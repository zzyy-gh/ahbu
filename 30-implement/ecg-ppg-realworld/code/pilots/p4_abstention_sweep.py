"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-4

P-4 — Abstention threshold sweep on CinC 2017 dev validation hold-out.

Procedure:
  1. Load CinC 2017 dev split (from runs/partition.json — built by P-6).
  2. Internally split dev into 80% training / 20% validation hold-out
     (seed=42, stratified by class). Validation hold-out is the
     within-dev probe surface; the headline test split is NOT touched.
  3. Train xresnet1d50 (single-lead, 4-class) for 3 epochs at batch=8,
     fp32, Adam lr=1e-3. Inputs are 9000-sample (30 s × 300 Hz)
     pre-processed waveforms (notch + highpass + clip + z-score per
     p2_classical_baseline.preprocess()).
  4. On the validation hold-out: extract logits, compute softmax probs,
     fit temperature parameter T by Brier-score minimization
     (scipy.optimize.minimize_scalar over T in [0.5, 10]).
  5. Compute coverage-vs-PPV curve via shared.eval.selective_classification_curve()
     (binary AF-vs-rest), at coverages [1.00, 0.95, 0.90, 0.85, 0.83, 0.79].
  6. Compute confidence-correctness AUC (label = correct, score =
     post-temperature max-softmax) via sklearn.metrics.roc_auc_score.

Success criteria (per pilots-README §P-4):
  - Confidence-correctness AUC >= 0.55 (R-3 kill threshold).
  - PPV at coverage=0.83 > PPV at coverage=1.00 on the 3-epoch model.

Side-effects (saved for P-5):
  - runs/p4_xresnet1d50_3ep_<ts>.pt — model state_dict.
  - runs/p4_temperature_<ts>.json — temperature T value + metadata.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

# Ensure shared/ is importable.
_THIS = Path(__file__).resolve()
_REPO_ROOT = _THIS.parents[4]  # ahbu/
_SHARED_PARENT = _REPO_ROOT / "30-implement"
if str(_SHARED_PARENT) not in sys.path:
    sys.path.insert(0, str(_SHARED_PARENT))

# Vendored from p2_classical_baseline.preprocess() to avoid a relative-
# import dance (p2 is a sibling pilot script with no package structure).
def preprocess(signal, fs: int):
    import numpy as np
    from scipy.signal import butter, filtfilt, iirnotch

    sos_b, sos_a = butter(4, 0.5 / (fs / 2), btype="highpass")
    signal = filtfilt(sos_b, sos_a, signal)
    notch_b, notch_a = iirnotch(50.0 / (fs / 2), Q=30)
    signal = filtfilt(notch_b, notch_a, signal)
    signal = np.clip(signal, -5.0, 5.0)
    mu = float(signal.mean())
    sigma = float(signal.std())
    if sigma > 1e-9:
        signal = (signal - mu) / sigma
    return signal


def find_reference_csv(cinc_dir: Path):
    for cand in ("REFERENCE-v3.csv", "REFERENCE.csv", "training2017/REFERENCE-v3.csv", "training2017/REFERENCE.csv"):
        p = cinc_dir / cand
        if p.exists():
            return p
    return None


def build_xresnet1d50(in_channels: int = 1, n_out: int = 4):
    """Same construction pattern as p3_xresnet_vram_cinc.py."""
    from fastai.vision.models.xresnet import ResBlock, XResNet

    return XResNet(
        ResBlock,
        expansion=4,
        layers=[3, 4, 6, 3],
        c_in=in_channels,
        n_out=n_out,
        ndim=1,
        ks=5,
    )


def pad_or_crop(signal, target_len: int):
    import numpy as np

    n = len(signal)
    if n == target_len:
        return signal.astype(np.float32)
    if n > target_len:
        # Center crop.
        start = (n - target_len) // 2
        return signal[start : start + target_len].astype(np.float32)
    out = np.zeros(target_len, dtype=np.float32)
    out[:n] = signal.astype(np.float32)
    return out


def load_record_signal(rec_path, target_len: int, fs: int):
    import wfdb

    r = wfdb.rdrecord(str(rec_path))
    sig = r.p_signal[:, 0]
    sig = preprocess(sig, fs)
    sig = pad_or_crop(sig, target_len)
    return sig


class CincDataset:
    """Lightweight in-memory cache → torch Dataset.

    8528 records × 9000 float32 = ~289 MB; comfortable in RAM. Avoids
    repeated WFDB I/O across 3 training epochs.
    """

    def __init__(self, record_ids, labels, waveform_dir: Path, target_len: int, fs: int, label_map: dict, log_every: int = 500):
        import numpy as np

        self.record_ids = list(record_ids)
        self.labels = list(labels)
        self.label_map = label_map
        self.target_len = target_len
        self.fs = fs
        self.signals = np.zeros((len(self.record_ids), target_len), dtype=np.float32)
        self.y = np.zeros(len(self.record_ids), dtype=np.int64)
        n_failed = 0
        for i, (rid, lbl) in enumerate(zip(self.record_ids, self.labels)):
            try:
                sig = load_record_signal(waveform_dir / rid, target_len, fs)
                self.signals[i] = sig
            except Exception:  # noqa: BLE001
                n_failed += 1
            self.y[i] = label_map[lbl]
            if (i + 1) % log_every == 0:
                print(f"  [load] {i+1}/{len(self.record_ids)} (failed={n_failed})", flush=True)
        self.n_failed = n_failed

    def __len__(self):
        return len(self.record_ids)


def make_loader(dataset, indices, batch_size: int, shuffle: bool, generator=None):
    import numpy as np
    import torch
    from torch.utils.data import DataLoader, Dataset, Subset

    class _Wrap(Dataset):
        def __init__(self, ds):
            self.ds = ds

        def __len__(self):
            return len(self.ds)

        def __getitem__(self, idx):
            x = self.ds.signals[idx]
            y = self.ds.y[idx]
            return torch.from_numpy(x).unsqueeze(0), torch.tensor(y, dtype=torch.long)

    sub = Subset(_Wrap(dataset), indices)
    return DataLoader(
        sub,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0,
        pin_memory=True,
        generator=generator,
        drop_last=False,
    )


def fit_temperature_brier(probs_uncalibrated, y_true_onehot):
    """Fit T by minimizing Brier score on probabilities derived from
    softmax(logits / T). The optimization is over T directly; we
    recompute probs from the underlying logits each evaluation.

    Caller passes logits (not probs). We expose the wrapper below.
    """
    raise NotImplementedError("Use fit_temperature_brier_from_logits")


def fit_temperature_brier_from_logits(logits, y_true: "np.ndarray", n_classes: int):
    """Fit T by Brier score min over T in [0.5, 10]. Returns (T, brier_pre, brier_post)."""
    import numpy as np
    from scipy.optimize import minimize_scalar
    from scipy.special import softmax

    y_onehot = np.zeros((len(y_true), n_classes), dtype=np.float32)
    y_onehot[np.arange(len(y_true)), y_true] = 1.0

    def brier(T):
        probs = softmax(logits / max(T, 1e-3), axis=1)
        return float(((probs - y_onehot) ** 2).sum(axis=1).mean())

    res = minimize_scalar(brier, bounds=(0.5, 10.0), method="bounded", options={"xatol": 1e-3})
    T = float(res.x)
    return T, brier(1.0), brier(T)


def probe(
    cinc_dir: Path,
    partition_json: Path,
    runs_dir: Path,
    epochs: int,
    batch_size: int,
    lr: float,
    seed: int,
    target_len: int,
    fs: int,
    auc_threshold: float,
):
    if not cinc_dir.exists():
        return {"status": "fail", "reason": f"CinC 2017 dir not found at {cinc_dir}"}
    if not partition_json.exists():
        return {"status": "fail", "reason": f"partition.json not found at {partition_json} — run P-6 first"}

    reference_csv = find_reference_csv(cinc_dir)
    if reference_csv is None:
        return {"status": "fail", "reason": f"REFERENCE csv not found under {cinc_dir}"}

    try:
        import numpy as np
        import pandas as pd
        import torch
        from scipy.special import softmax
        from sklearn.metrics import roc_auc_score
        from sklearn.model_selection import StratifiedShuffleSplit
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    try:
        from shared.eval import ppv_at_coverage, selective_classification_curve
    except ImportError as e:
        return {"status": "fail", "reason": f"could not import shared.eval: {e}"}

    if not torch.cuda.is_available():
        return {"status": "fail", "reason": "torch.cuda unavailable; P-4 requires GPU."}

    waveform_dir = reference_csv.parent
    df = pd.read_csv(reference_csv, header=None, names=["record_id", "label"])
    partition = json.loads(partition_json.read_text())
    dev_ids = set(partition["dev_record_ids"])
    df_dev = df[df["record_id"].isin(dev_ids)].copy()

    # Drop noisy records ('~') per protocol-lock §2; we still train as
    # 4-class to match approach.md / the headline model. The 4-class
    # head is preserved; we just don't expect any '~' in the working
    # set after this exclusion.
    n_before = len(df_dev)
    df_dev = df_dev[df_dev["label"] != "~"].reset_index(drop=True)
    n_after = len(df_dev)
    n_excluded_noisy = n_before - n_after

    # 80/20 within-dev stratified split, seed=42.
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    split_iter = list(sss.split(df_dev["record_id"].values, df_dev["label"].values))
    train_idx, holdout_idx = split_iter[0]
    train_records = df_dev.iloc[train_idx].copy().reset_index(drop=True)
    holdout_records = df_dev.iloc[holdout_idx].copy().reset_index(drop=True)

    print(
        f"[P-4] dev={len(df_dev)} (excluded {n_excluded_noisy} noisy '~'); "
        f"train={len(train_records)} holdout={len(holdout_records)}",
        flush=True,
    )

    label_map = {"N": 0, "A": 1, "O": 2, "~": 3}
    n_classes = 4

    print("[P-4] loading + preprocessing waveforms (this is the slow step)...", flush=True)
    t_load0 = time.perf_counter()
    train_ds = CincDataset(
        train_records["record_id"].tolist(),
        train_records["label"].tolist(),
        waveform_dir,
        target_len,
        fs,
        label_map,
    )
    holdout_ds = CincDataset(
        holdout_records["record_id"].tolist(),
        holdout_records["label"].tolist(),
        waveform_dir,
        target_len,
        fs,
        label_map,
    )
    load_elapsed = time.perf_counter() - t_load0
    print(
        f"[P-4] load complete in {load_elapsed:.1f}s "
        f"(train_failed={train_ds.n_failed}, holdout_failed={holdout_ds.n_failed})",
        flush=True,
    )

    # Reproducibility.
    torch.manual_seed(seed)
    np.random.seed(seed)
    g_cpu = torch.Generator()
    g_cpu.manual_seed(seed)

    device = "cuda:0"
    model = build_xresnet1d50(in_channels=1, n_out=n_classes).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = torch.nn.CrossEntropyLoss()

    # Training loader = all train indices.
    train_loader = make_loader(
        train_ds, indices=list(range(len(train_ds))), batch_size=batch_size, shuffle=True, generator=g_cpu
    )
    holdout_loader = make_loader(
        holdout_ds, indices=list(range(len(holdout_ds))), batch_size=batch_size * 2, shuffle=False
    )

    print(f"[P-4] training xresnet1d50: epochs={epochs}, batch={batch_size}, fp32, Adam lr={lr}", flush=True)
    train_loss_history = []
    train_t0 = time.perf_counter()
    for epoch in range(epochs):
        model.train()
        running = 0.0
        n_batches = 0
        epoch_t0 = time.perf_counter()
        for x, y in train_loader:
            x = x.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)
            optimizer.zero_grad()
            logits = model(x)
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()
            running += float(loss.item())
            n_batches += 1
            if n_batches % 100 == 0:
                el = time.perf_counter() - epoch_t0
                print(
                    f"  [epoch {epoch+1}/{epochs}] step {n_batches}/{len(train_loader)} "
                    f"running_loss={running / n_batches:.4f} elapsed={el:.0f}s",
                    flush=True,
                )
        epoch_loss = running / max(n_batches, 1)
        epoch_elapsed = time.perf_counter() - epoch_t0
        train_loss_history.append({"epoch": epoch + 1, "loss": epoch_loss, "elapsed_s": epoch_elapsed})
        print(
            f"[P-4] epoch {epoch+1}/{epochs} done: train_loss={epoch_loss:.4f} elapsed={epoch_elapsed:.1f}s",
            flush=True,
        )
    train_elapsed = time.perf_counter() - train_t0
    print(f"[P-4] training complete in {train_elapsed:.1f}s", flush=True)

    # Inference on holdout.
    print("[P-4] running inference on validation hold-out...", flush=True)
    model.eval()
    all_logits = []
    all_y = []
    with torch.no_grad():
        for x, y in holdout_loader:
            x = x.to(device, non_blocking=True)
            logits = model(x)
            all_logits.append(logits.detach().cpu().numpy())
            all_y.append(y.numpy())
    logits = np.concatenate(all_logits, axis=0)
    y_holdout = np.concatenate(all_y, axis=0).astype(np.int64)

    # Sanity: train AUROC from a forward over train (subset, fast).
    # Skip full pass to save time; use holdout AUROC only.
    probs_uncal = softmax(logits, axis=1)
    af_idx = label_map["A"]
    auroc_af_uncal = float(
        roc_auc_score((y_holdout == af_idx).astype(int), probs_uncal[:, af_idx])
    )
    print(f"[P-4] holdout AF-vs-rest AUROC (uncalibrated) = {auroc_af_uncal:.4f}", flush=True)

    # Fit temperature on validation hold-out via Brier minimization.
    T, brier_pre, brier_post = fit_temperature_brier_from_logits(logits, y_holdout, n_classes)
    print(f"[P-4] fitted T={T:.3f}; Brier pre={brier_pre:.4f} post={brier_post:.4f}", flush=True)

    # Calibrated probs.
    probs_cal = softmax(logits / max(T, 1e-3), axis=1)
    # AUROC of AF probability after T scaling (T is monotonic so AUROC
    # of the AF column should be invariant; we recompute as a sanity).
    auroc_af_cal = float(
        roc_auc_score((y_holdout == af_idx).astype(int), probs_cal[:, af_idx])
    )

    # Per-record predictions and confidences (post-T).
    pred = probs_cal.argmax(axis=1)
    confidence = probs_cal.max(axis=1)
    correct = (pred == y_holdout).astype(int)

    # Confidence-correctness AUC.
    if correct.sum() == 0 or correct.sum() == len(correct):
        conf_correct_auc = None
    else:
        conf_correct_auc = float(roc_auc_score(correct, confidence))
    print(f"[P-4] confidence-correctness AUC = {conf_correct_auc}", flush=True)

    # Coverage points per pilots-README §P-4.
    coverages = [1.00, 0.95, 0.90, 0.85, 0.83, 0.79]

    # Selective-classification (correctness) curve.
    sc = selective_classification_curve(confidence, correct.astype(bool), coverages)

    # PPV at coverage on AF-vs-rest binary projection.
    y_true_bin = (y_holdout == af_idx).astype(int)
    y_pred_bin = (pred == af_idx).astype(int)
    ppv_curve = ppv_at_coverage(
        y_true=y_true_bin,
        y_pred=y_pred_bin,
        confidences=confidence,
        coverages=coverages,
        bootstrap_n=2000,
        bootstrap_seed=42,
    )

    # Resolve PPV @ 0.83 vs @ 1.00 for the success criterion.
    def _find_ppv(target):
        for p in ppv_curve["points"]:
            if abs(p.get("target_coverage", -1) - target) < 1e-9:
                return p.get("ppv")
        return None

    ppv_at_1_00 = _find_ppv(1.00)
    ppv_at_0_83 = _find_ppv(0.83)
    ppv_improvement_pp = (
        round((ppv_at_0_83 - ppv_at_1_00) * 100, 3)
        if (ppv_at_0_83 is not None and ppv_at_1_00 is not None)
        else None
    )

    # Success criteria.
    auc_pass = (conf_correct_auc is not None) and (conf_correct_auc >= auc_threshold)
    ppv_pass = (
        ppv_at_0_83 is not None
        and ppv_at_1_00 is not None
        and ppv_at_0_83 > ppv_at_1_00
    )
    status = "pass" if (auc_pass and ppv_pass) else "fail"

    # Save model + temperature for P-5 reuse.
    ts = int(time.time())
    runs_dir.mkdir(parents=True, exist_ok=True)
    model_path = runs_dir / f"p4_xresnet1d50_3ep_{ts}.pt"
    temp_path = runs_dir / f"p4_temperature_{ts}.json"
    torch.save(
        {
            "state_dict": model.state_dict(),
            "in_channels": 1,
            "n_out": n_classes,
            "epochs": epochs,
            "batch_size": batch_size,
            "lr": lr,
            "seed": seed,
            "target_len": target_len,
            "fs": fs,
            "label_map": label_map,
        },
        model_path,
    )
    temp_path.write_text(
        json.dumps(
            {
                "T": T,
                "brier_pre": brier_pre,
                "brier_post": brier_post,
                "fitted_on": "validation_holdout (within-dev 20% seed=42)",
                "n_holdout": int(len(y_holdout)),
                "model_state_dict": str(model_path),
                "spec": "20-plan/ecg-ppg-realworld/pilots-README.md#P-4 + protocol-lock §5",
            },
            indent=2,
        )
    )
    print(f"[P-4] saved model -> {model_path}", flush=True)
    print(f"[P-4] saved temperature -> {temp_path}", flush=True)

    return {
        "status": status,
        "n_train": int(len(train_ds)),
        "n_holdout": int(len(holdout_ds)),
        "n_excluded_noisy": int(n_excluded_noisy),
        "load_elapsed_s": round(load_elapsed, 1),
        "train_elapsed_s": round(train_elapsed, 1),
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "seed": seed,
        "input_shape": [1, target_len],
        "train_loss_history": train_loss_history,
        "holdout_auroc_af_uncalibrated": round(auroc_af_uncal, 4),
        "holdout_auroc_af_calibrated": round(auroc_af_cal, 4),
        "temperature_T": round(T, 4),
        "brier_pre": round(brier_pre, 5),
        "brier_post": round(brier_post, 5),
        "confidence_correctness_auc": (
            round(conf_correct_auc, 4) if conf_correct_auc is not None else None
        ),
        "confidence_correctness_auc_threshold": auc_threshold,
        "confidence_correctness_auc_pass": auc_pass,
        "ppv_at_coverage": ppv_curve,
        "ppv_at_1_00": ppv_at_1_00,
        "ppv_at_0_83": ppv_at_0_83,
        "ppv_improvement_pp_at_0_83": ppv_improvement_pp,
        "ppv_pass": ppv_pass,
        "selective_classification_curve": sc,
        "model_path": str(model_path),
        "temperature_path": str(temp_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-4 abstention threshold sweep on CinC 2017")
    ap.add_argument(
        "--cinc-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "challenge-2017-1.0.0",
    )
    ap.add_argument(
        "--partition-json",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "runs" / "partition.json",
    )
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "runs",
    )
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--target-len", type=int, default=9000)
    ap.add_argument("--fs", type=int, default=300)
    ap.add_argument("--auc-threshold", type=float, default=0.55)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    try:
        result = probe(
            args.cinc_dir,
            args.partition_json,
            args.runs_dir,
            args.epochs,
            args.batch_size,
            args.lr,
            args.seed,
            args.target_len,
            args.fs,
            args.auc_threshold,
        )
    except Exception as e:  # noqa: BLE001
        result = {
            "status": "fail",
            "reason": f"unhandled exception: {e}",
            "traceback": traceback.format_exc(),
        }

    result["pilot"] = "P-4"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-4"

    out_path = args.out or (
        args.runs_dir / f"pilot_p4_abstention_sweep_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    # Print a trimmed summary, not the whole result (PPV bootstrap
    # bloats the output).
    summary_keys = [
        "status",
        "n_train",
        "n_holdout",
        "load_elapsed_s",
        "train_elapsed_s",
        "train_loss_history",
        "holdout_auroc_af_uncalibrated",
        "temperature_T",
        "brier_pre",
        "brier_post",
        "confidence_correctness_auc",
        "confidence_correctness_auc_pass",
        "ppv_at_1_00",
        "ppv_at_0_83",
        "ppv_improvement_pp_at_0_83",
        "ppv_pass",
        "model_path",
        "temperature_path",
        "reason",
    ]
    summary = {k: result.get(k) for k in summary_keys if k in result}
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
