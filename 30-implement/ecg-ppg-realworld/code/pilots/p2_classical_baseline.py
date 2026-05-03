"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-2

P-2 — Classical baseline pipeline speed and sanity check on CinC 2017.

Tests:
  (a) NeuroKit2 ecg_process() + ecg_intervalrelated() feature extraction
      throughput on a stratified 1,000-record dev sample.
  (b) Logistic regression AF-vs-rest AUROC on a within-pilot 800/200
      train/holdout split of the same 1,000 records.
  (c) Sanity: AFIB records have higher RR-interval CV than non-AFIB.

Dataset/split: stratified 1,000-record sample of CinC 2017 dev (the
80 % partition produced by P-6 → runs/partition.json). Within-pilot
holdout is for sanity only — does NOT touch the 20 % headline test
partition.

Success criteria (per pilots-README §P-2):
  - Mean feature extraction time < 10 s/record (target < 3 s/record).
  - LR AUROC on 200-record within-pilot holdout > 0.75.
  - AFIB CV(RR) median > non-AFIB CV(RR) median.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from pathlib import Path
from typing import Any


def find_reference_csv(cinc_dir: Path) -> Path | None:
    for cand in ("REFERENCE-v3.csv", "REFERENCE.csv", "training2017/REFERENCE-v3.csv", "training2017/REFERENCE.csv"):
        p = cinc_dir / cand
        if p.exists():
            return p
    return None


def preprocess(signal, fs: int):
    import numpy as np
    from scipy.signal import iirnotch, butter, filtfilt

    # Baseline-wander highpass (0.5 Hz)
    sos_b, sos_a = butter(4, 0.5 / (fs / 2), btype="highpass")
    signal = filtfilt(sos_b, sos_a, signal)

    # Notch (50 Hz; CinC 2017 was collected mostly outside US grid)
    notch_b, notch_a = iirnotch(50.0 / (fs / 2), Q=30)
    signal = filtfilt(notch_b, notch_a, signal)

    # Clip ±5 mV (assuming the unit is mV; if raw integer ADC scale was
    # used, the clipping is a no-op for typical values)
    signal = np.clip(signal, -5.0, 5.0)

    # Per-record z-score
    mu = float(signal.mean())
    sigma = float(signal.std())
    if sigma > 1e-9:
        signal = (signal - mu) / sigma
    return signal


def extract_features(signal, fs: int) -> dict[str, float] | None:
    import neurokit2 as nk
    import numpy as np

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            signals_df, info = nk.ecg_process(signal, sampling_rate=fs)
            agg = nk.ecg_intervalrelated(signals_df, sampling_rate=fs)
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}

    out: dict[str, float] = {}
    if hasattr(agg, "iloc") and len(agg) > 0:
        row = agg.iloc[0]
        for k, v in row.items():
            # NeuroKit2 0.2.13 returns most HRV columns as [[value]] 2D arrays;
            # flatten to scalar via np.asarray().flatten()[0] if the cell is
            # array-wrapped, else try float() directly.
            try:
                arr = np.asarray(v)
                if arr.size == 1:
                    fv = float(arr.flatten()[0])
                else:
                    continue
                if not (np.isnan(fv) or np.isinf(fv)):
                    out[str(k)] = fv
            except (ValueError, TypeError):
                continue
    return out if out else None


def probe(cinc_dir: Path, partition_json: Path, n_sample: int, target_extraction_s_per_record: float, target_auc: float) -> dict[str, Any]:
    if not cinc_dir.exists():
        return {"status": "fail", "reason": f"CinC 2017 dir not found at {cinc_dir}"}

    reference_csv = find_reference_csv(cinc_dir)
    if reference_csv is None:
        return {"status": "fail", "reason": f"REFERENCE csv not found under {cinc_dir}"}
    if not partition_json.exists():
        return {"status": "fail", "reason": f"partition.json not found at {partition_json} — run P-6 first"}

    try:
        import numpy as np
        import pandas as pd
        import wfdb
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import roc_auc_score
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    waveform_dir = reference_csv.parent
    df = pd.read_csv(reference_csv, header=None, names=["record_id", "label"])
    partition = json.loads(partition_json.read_text())
    dev_ids = set(partition["dev_record_ids"])
    df_dev = df[df["record_id"].isin(dev_ids)].copy()

    # Stratified sample of n_sample records by label
    rng = np.random.default_rng(seed=42)
    sampled: list[pd.DataFrame] = []
    n_per_class = n_sample // 4
    for cls, group in df_dev.groupby("label"):
        take = min(len(group), n_per_class)
        idx = rng.choice(group.index.values, size=take, replace=False)
        sampled.append(group.loc[idx])
    df_sample = pd.concat(sampled, axis=0).sample(frac=1.0, random_state=42).reset_index(drop=True)

    fs = 300
    feature_rows: list[dict[str, float]] = []
    labels: list[str] = []
    extraction_times: list[float] = []
    extraction_errors: list[dict[str, str]] = []
    rr_cvs: dict[str, list[float]] = {"A": [], "N": [], "O": [], "~": []}

    for i, row in df_sample.iterrows():
        record_id = row["record_id"]
        label = row["label"]
        rec_path = waveform_dir / record_id
        try:
            r = wfdb.rdrecord(str(rec_path))
        except Exception as e:  # noqa: BLE001
            extraction_errors.append({"record_id": record_id, "stage": "load", "error": str(e)})
            continue

        signal = r.p_signal[:, 0]
        try:
            signal = preprocess(signal, fs)
        except Exception as e:  # noqa: BLE001
            extraction_errors.append({"record_id": record_id, "stage": "preprocess", "error": str(e)})
            continue

        t0 = time.perf_counter()
        feats = extract_features(signal, fs)
        elapsed = time.perf_counter() - t0
        extraction_times.append(elapsed)

        if not feats or "_error" in feats:
            extraction_errors.append({"record_id": record_id, "stage": "features", "error": (feats or {}).get("_error", "no features")})
            continue

        # Find an RR-CV-equivalent column. NeuroKit2 0.2.13 names them
        # HRV_CVNN / HRV_CVSD / HRV_RMSSD (no ECG_ prefix on the HRV
        # subset).
        rr_cv = None
        for k in ("HRV_CVNN", "HRV_CVSD", "HRV_RMSSD"):
            if k in feats:
                rr_cv = feats[k]
                break
        if rr_cv is not None:
            rr_cvs.setdefault(label, []).append(rr_cv)

        feature_rows.append(feats)
        labels.append(label)

        if (i + 1) % 100 == 0:
            print(f"...{i+1}/{len(df_sample)}: rolling mean extract {np.mean(extraction_times):.2f} s/record")

    n_extracted = len(feature_rows)
    if n_extracted < 200:
        return {
            "status": "fail",
            "reason": f"only {n_extracted} records had usable features; need >= 200 for AUROC eval",
            "n_sampled": len(df_sample),
            "n_extraction_errors": len(extraction_errors),
            "extraction_errors_sample": extraction_errors[:5],
        }

    feature_df = pd.DataFrame(feature_rows).fillna(0.0)
    feature_df = feature_df.replace([np.inf, -np.inf], 0.0)
    y = np.array([1 if lbl == "A" else 0 for lbl in labels])

    # Limit to numeric columns and drop any zero-variance ones
    feature_df = feature_df.loc[:, feature_df.std(axis=0) > 1e-9]

    X_train, X_test, y_train, y_test = train_test_split(
        feature_df.values, y, test_size=0.2, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    lr = LogisticRegression(C=1.0, max_iter=5000, class_weight="balanced")
    lr.fit(X_train_s, y_train)
    proba = lr.predict_proba(X_test_s)[:, 1]
    auroc = float(roc_auc_score(y_test, proba))

    rr_cv_a = float(np.median(rr_cvs.get("A", [0.0]))) if rr_cvs.get("A") else None
    rr_cv_n = float(np.median(rr_cvs.get("N", [0.0]))) if rr_cvs.get("N") else None
    rr_cv_sanity = (rr_cv_a is not None and rr_cv_n is not None and rr_cv_a > rr_cv_n)

    mean_extract = float(np.mean(extraction_times))
    extraction_speed_pass = mean_extract < target_extraction_s_per_record
    auroc_pass = auroc > target_auc
    status = "pass" if (extraction_speed_pass and auroc_pass and rr_cv_sanity) else "fail"

    return {
        "status": status,
        "n_sampled": len(df_sample),
        "n_extracted": n_extracted,
        "n_extraction_errors": len(extraction_errors),
        "mean_extraction_s_per_record": round(mean_extract, 3),
        "median_extraction_s_per_record": round(float(np.median(extraction_times)), 3),
        "extraction_speed_threshold_s": target_extraction_s_per_record,
        "extraction_speed_pass": extraction_speed_pass,
        "auroc_within_pilot_holdout": round(auroc, 4),
        "auroc_threshold": target_auc,
        "auroc_pass": auroc_pass,
        "n_features_used": int(feature_df.shape[1]),
        "rr_cv_median_afib": rr_cv_a,
        "rr_cv_median_nonafib": rr_cv_n,
        "rr_cv_sanity_pass": rr_cv_sanity,
        "n_train_holdout": int(len(y_test)),
        "extraction_errors_sample": extraction_errors[:5],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-2 CinC 2017 classical baseline")
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
    ap.add_argument("--n-sample", type=int, default=1000)
    ap.add_argument("--target-extraction-s", type=float, default=10.0)
    ap.add_argument("--target-auc", type=float, default=0.75)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.cinc_dir, args.partition_json, args.n_sample, args.target_extraction_s, args.target_auc)
    result["pilot"] = "P-2"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-2"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p2_classical_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
