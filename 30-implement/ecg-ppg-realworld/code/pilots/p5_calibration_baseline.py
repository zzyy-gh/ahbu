"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-5

P-5 — Calibration baseline: Brier and ECE before vs after temperature
scaling, on the CinC 2017 within-dev validation hold-out.

Procedure:
  1. Load the trained 3-epoch model + fitted temperature T saved by P-4.
  2. Reconstruct the same within-dev validation hold-out (seed=42,
     stratified, 20% of dev).
  3. Compute Brier score and ECE (15 bins) with and without temperature
     scaling.
  4. Plot reliability diagrams side-by-side; save PNG.

Success criteria (per pilots-README §P-5):
  - ECE(calibrated) < ECE(uncalibrated).
  - Reliability diagram shows smaller deviation from diagonal post-scale.
  - T in [1.0, 5.0]. T > 5.0 is a flag (not a fail) — surfaces severe
    overconfidence in the early model that's expected to ease with full
    50-epoch training.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
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


def latest_artifact(runs_dir: Path, pattern: str):
    cands = sorted(runs_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
    return cands[-1] if cands else None


def compute_ece(probs, y_true, n_bins: int = 15) -> float:
    """Multi-class ECE: bin by max-confidence; per-bin gap = |acc - conf|."""
    import numpy as np

    pred = probs.argmax(axis=1)
    conf = probs.max(axis=1)
    correct = (pred == y_true).astype(float)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y_true)
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        # Last bin closed on right.
        if i == n_bins - 1:
            mask = (conf >= lo) & (conf <= hi)
        else:
            mask = (conf >= lo) & (conf < hi)
        if mask.sum() == 0:
            continue
        acc_bin = float(correct[mask].mean())
        conf_bin = float(conf[mask].mean())
        ece += (mask.sum() / n) * abs(acc_bin - conf_bin)
    return float(ece)


def reliability_bins(probs, y_true, n_bins: int = 15):
    import numpy as np

    pred = probs.argmax(axis=1)
    conf = probs.max(axis=1)
    correct = (pred == y_true).astype(float)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_acc = []
    bin_conf = []
    bin_count = []
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        if i == n_bins - 1:
            mask = (conf >= lo) & (conf <= hi)
        else:
            mask = (conf >= lo) & (conf < hi)
        n_in = int(mask.sum())
        bin_count.append(n_in)
        if n_in == 0:
            bin_acc.append(None)
            bin_conf.append(None)
        else:
            bin_acc.append(float(correct[mask].mean()))
            bin_conf.append(float(conf[mask].mean()))
    return bins, bin_acc, bin_conf, bin_count


def plot_reliability(bins, acc_uncal, conf_uncal, count_uncal, acc_cal, conf_cal, count_cal, T, out_path: Path, ece_uncal: float, ece_cal: float):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    centers = (bins[:-1] + bins[1:]) / 2.0

    for ax, acc, conf, count, title, ece in (
        (axes[0], acc_uncal, conf_uncal, count_uncal, "uncalibrated", ece_uncal),
        (axes[1], acc_cal, conf_cal, count_cal, f"calibrated (T={T:.2f})", ece_cal),
    ):
        ax.plot([0, 1], [0, 1], "k--", linewidth=1, alpha=0.6)
        # Bars: x = bin center, height = bin acc.
        widths = 1.0 / len(centers)
        heights = [a if a is not None else 0.0 for a in acc]
        ax.bar(centers, heights, width=widths * 0.9, alpha=0.7, edgecolor="black", label="accuracy")
        # Overlay confidence as small markers.
        for c_x, c_y in zip(centers, conf):
            if c_y is not None:
                ax.plot(c_x, c_y, "rx", markersize=8)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("confidence")
        ax.set_ylabel("accuracy")
        ax.set_title(f"{title} — ECE={ece:.4f}")
        ax.grid(True, alpha=0.3)

    fig.suptitle("Reliability diagrams — P-5 calibration baseline (CinC 2017 dev hold-out)")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def probe(
    cinc_dir: Path,
    partition_json: Path,
    runs_dir: Path,
    model_path: Path | None,
    temperature_path: Path | None,
    target_len: int,
    fs: int,
    n_bins: int,
):
    if not cinc_dir.exists():
        return {"status": "fail", "reason": f"CinC 2017 dir not found at {cinc_dir}"}
    if not partition_json.exists():
        return {"status": "fail", "reason": f"partition.json not found at {partition_json}"}

    reference_csv = find_reference_csv(cinc_dir)
    if reference_csv is None:
        return {"status": "fail", "reason": f"REFERENCE csv not found under {cinc_dir}"}

    try:
        import numpy as np
        import pandas as pd
        import torch
        from scipy.special import softmax
        from sklearn.model_selection import StratifiedShuffleSplit
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    if not torch.cuda.is_available():
        return {"status": "fail", "reason": "torch.cuda unavailable; P-5 requires GPU."}

    # Auto-resolve P-4 artifacts.
    if model_path is None:
        model_path = latest_artifact(runs_dir, "p4_xresnet1d50_3ep_*.pt")
    if temperature_path is None:
        temperature_path = latest_artifact(runs_dir, "p4_temperature_*.json")
    if model_path is None or not Path(model_path).exists():
        return {"status": "fail", "reason": f"P-4 model artifact not found in {runs_dir}"}
    if temperature_path is None or not Path(temperature_path).exists():
        return {"status": "fail", "reason": f"P-4 temperature artifact not found in {runs_dir}"}

    print(f"[P-5] using model: {model_path}", flush=True)
    print(f"[P-5] using temperature file: {temperature_path}", flush=True)

    temp_meta = json.loads(Path(temperature_path).read_text())
    T = float(temp_meta["T"])

    # Reconstruct hold-out exactly as in P-4.
    waveform_dir = reference_csv.parent
    df = pd.read_csv(reference_csv, header=None, names=["record_id", "label"])
    partition = json.loads(partition_json.read_text())
    dev_ids = set(partition["dev_record_ids"])
    df_dev = df[df["record_id"].isin(dev_ids)].copy()
    df_dev = df_dev[df_dev["label"] != "~"].reset_index(drop=True)

    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    split_iter = list(sss.split(df_dev["record_id"].values, df_dev["label"].values))
    _, holdout_idx = split_iter[0]
    holdout_records = df_dev.iloc[holdout_idx].copy().reset_index(drop=True)

    label_map = {"N": 0, "A": 1, "O": 2, "~": 3}
    n_classes = 4

    print(f"[P-5] hold-out records: {len(holdout_records)} (T={T:.3f})", flush=True)
    device = "cuda:0"
    model = build_xresnet1d50(in_channels=1, n_out=n_classes).to(device)
    state = torch.load(str(model_path), map_location=device, weights_only=False)
    if isinstance(state, dict) and "state_dict" in state:
        model.load_state_dict(state["state_dict"])
    else:
        model.load_state_dict(state)
    model.eval()

    # Load + infer in batches without staging the full dataset in RAM
    # twice (P-4 already paid the load cost; we re-load here so P-5 is
    # standalone-runnable for re-checks).
    batch_size = 16
    all_logits = []
    all_y = []
    buf_x = []
    buf_y = []
    print("[P-5] loading hold-out + inference...", flush=True)
    t0 = time.perf_counter()
    n_failed = 0
    for i, (rid, lbl) in enumerate(zip(holdout_records["record_id"], holdout_records["label"])):
        try:
            sig = load_record_signal(waveform_dir / rid, target_len, fs)
        except Exception:
            n_failed += 1
            continue
        buf_x.append(sig)
        buf_y.append(label_map[lbl])
        if len(buf_x) == batch_size or i == len(holdout_records) - 1:
            x = torch.from_numpy(np.stack(buf_x).astype(np.float32)).unsqueeze(1).to(device)
            with torch.no_grad():
                logits = model(x)
            all_logits.append(logits.cpu().numpy())
            all_y.extend(buf_y)
            buf_x = []
            buf_y = []
        if (i + 1) % 200 == 0:
            print(f"  [infer] {i+1}/{len(holdout_records)}", flush=True)
    elapsed = time.perf_counter() - t0
    print(f"[P-5] inference complete in {elapsed:.1f}s (failed={n_failed})", flush=True)

    logits = np.concatenate(all_logits, axis=0)
    y_holdout = np.asarray(all_y, dtype=np.int64)

    probs_uncal = softmax(logits, axis=1)
    probs_cal = softmax(logits / max(T, 1e-3), axis=1)

    # Brier scores (multi-class one-hot).
    y_onehot = np.zeros((len(y_holdout), n_classes), dtype=np.float32)
    y_onehot[np.arange(len(y_holdout)), y_holdout] = 1.0
    brier_uncal = float(((probs_uncal - y_onehot) ** 2).sum(axis=1).mean())
    brier_cal = float(((probs_cal - y_onehot) ** 2).sum(axis=1).mean())

    # ECE.
    ece_uncal = compute_ece(probs_uncal, y_holdout, n_bins=n_bins)
    ece_cal = compute_ece(probs_cal, y_holdout, n_bins=n_bins)

    # Reliability diagrams.
    bins_u, acc_u, conf_u, count_u = reliability_bins(probs_uncal, y_holdout, n_bins=n_bins)
    bins_c, acc_c, conf_c, count_c = reliability_bins(probs_cal, y_holdout, n_bins=n_bins)

    ts = int(time.time())
    runs_dir.mkdir(parents=True, exist_ok=True)
    png_path = runs_dir / f"p5_reliability_{ts}.png"
    plot_reliability(
        bins_u, acc_u, conf_u, count_u, acc_c, conf_c, count_c, T, png_path, ece_uncal, ece_cal
    )
    print(f"[P-5] saved reliability diagram -> {png_path}", flush=True)

    # Success criteria.
    ece_improved = ece_cal < ece_uncal
    t_in_range = 1.0 <= T <= 5.0
    t_high_flag = T > 5.0
    # Reliability "closer to diagonal" measured via mean abs (acc - conf) over non-empty bins.
    def _mean_gap(acc, conf, count):
        gaps = []
        for a, c, n in zip(acc, conf, count):
            if a is not None and c is not None and n > 0:
                gaps.append(abs(a - c))
        return float(sum(gaps) / max(len(gaps), 1)) if gaps else None

    gap_uncal = _mean_gap(acc_u, conf_u, count_u)
    gap_cal = _mean_gap(acc_c, conf_c, count_c)
    diagram_improved = (
        gap_uncal is not None and gap_cal is not None and gap_cal <= gap_uncal
    )

    # PASS = ECE improves AND diagram improves AND T in [1,5] (T>5 is a
    # FLAG not a FAIL per the spec).
    status = "pass" if (ece_improved and diagram_improved and (t_in_range or t_high_flag)) else "fail"

    return {
        "status": status,
        "n_holdout": int(len(y_holdout)),
        "n_failed_load": int(n_failed),
        "model_path": str(model_path),
        "temperature_path": str(temperature_path),
        "T": round(T, 4),
        "T_in_range_1_5": t_in_range,
        "T_high_flag_gt_5": t_high_flag,
        "brier_uncalibrated": round(brier_uncal, 5),
        "brier_calibrated": round(brier_cal, 5),
        "ece_uncalibrated": round(ece_uncal, 5),
        "ece_calibrated": round(ece_cal, 5),
        "ece_improved": ece_improved,
        "mean_reliability_gap_uncalibrated": (
            round(gap_uncal, 5) if gap_uncal is not None else None
        ),
        "mean_reliability_gap_calibrated": (
            round(gap_cal, 5) if gap_cal is not None else None
        ),
        "diagram_improved": diagram_improved,
        "reliability_png": str(png_path),
        "n_bins": n_bins,
        "reliability_uncalibrated": {
            "bin_edges": list(map(float, bins_u)),
            "accuracy": acc_u,
            "confidence": conf_u,
            "count": count_u,
        },
        "reliability_calibrated": {
            "bin_edges": list(map(float, bins_c)),
            "accuracy": acc_c,
            "confidence": conf_c,
            "count": count_c,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-5 calibration baseline (reuses P-4 model)")
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
    ap.add_argument("--model-path", type=Path, default=None)
    ap.add_argument("--temperature-path", type=Path, default=None)
    ap.add_argument("--target-len", type=int, default=9000)
    ap.add_argument("--fs", type=int, default=300)
    ap.add_argument("--n-bins", type=int, default=15)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    try:
        result = probe(
            args.cinc_dir,
            args.partition_json,
            args.runs_dir,
            args.model_path,
            args.temperature_path,
            args.target_len,
            args.fs,
            args.n_bins,
        )
    except Exception as e:  # noqa: BLE001
        result = {
            "status": "fail",
            "reason": f"unhandled exception: {e}",
            "traceback": traceback.format_exc(),
        }

    result["pilot"] = "P-5"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-5"

    out_path = args.out or (
        args.runs_dir / f"pilot_p5_calibration_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    summary_keys = [
        "status",
        "n_holdout",
        "n_failed_load",
        "T",
        "T_in_range_1_5",
        "T_high_flag_gt_5",
        "brier_uncalibrated",
        "brier_calibrated",
        "ece_uncalibrated",
        "ece_calibrated",
        "ece_improved",
        "mean_reliability_gap_uncalibrated",
        "mean_reliability_gap_calibrated",
        "diagram_improved",
        "reliability_png",
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
