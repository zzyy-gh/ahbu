"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-2

P-2 — Classical baseline pipeline speed + sanity AUROC.

Question: how long does NeuroKit2 feature extraction + LR take on a
1000-record sample from PTB-XL strat_fold 1-8? Is AUROC > 0.75?

Success criteria:
  (a) extraction time < 10 s/record (target < 3)
  (b) AUROC > 0.75 on 200-record held-out
  (c) AFIB records have visually higher RR-interval CV than non-AFIB
"""

import argparse
import ast
import json
import sys
import time
from pathlib import Path


def probe(ptbxl_dir: Path, n_sample: int, sampling_rate: int) -> dict:
    if not ptbxl_dir.exists():
        return {"status": "fail", "reason": f"PTB-XL dir not found at {ptbxl_dir}"}

    try:
        import numpy as np
        import pandas as pd
        import wfdb
        import neurokit2 as nk
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import roc_auc_score
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    metadata_csv = ptbxl_dir / "ptbxl_database.csv"
    df = pd.read_csv(metadata_csv, index_col="ecg_id")
    df["scp_codes_dict"] = df["scp_codes"].apply(lambda s: ast.literal_eval(s) if isinstance(s, str) else {})
    df["is_afib"] = df["scp_codes_dict"].apply(lambda d: d.get("AFIB", 0.0) >= 100.0)

    dev = df[df["strat_fold"].isin(range(1, 9))]
    afib = dev[dev["is_afib"]].sample(n=min(n_sample // 2, dev["is_afib"].sum()), random_state=42)
    non_afib = dev[~dev["is_afib"]].sample(n=min(n_sample - len(afib), len(dev[~dev["is_afib"]])), random_state=42)
    sample = pd.concat([afib, non_afib]).sample(frac=1.0, random_state=42)

    feature_cols = ["MeanNN", "SDNN", "RMSSD", "pNN50", "CVnn", "MeanHR",
                    "SDHR", "MinHR", "MaxHR", "HRV_LF", "HRV_HF", "HRV_LFHF"]
    X_rows = []
    y_rows = []
    extraction_times = []

    record_path_col = "filename_lr" if sampling_rate == 100 else "filename_hr"
    for ecg_id, row in sample.iterrows():
        record_path = ptbxl_dir / row[record_path_col]
        try:
            t0 = time.perf_counter()
            sig, fields = wfdb.rdsamp(str(record_path).replace(".dat", ""))
            lead_ii = sig[:, 1]
            ecg_signals, info = nk.ecg_process(lead_ii, sampling_rate=sampling_rate)
            features_df = nk.ecg_intervalrelated(ecg_signals, sampling_rate=sampling_rate)
            extraction_times.append(time.perf_counter() - t0)

            row_features = {}
            for c in feature_cols:
                matching = [col for col in features_df.columns if c.lower() in col.lower()]
                row_features[c] = float(features_df[matching[0]].iloc[0]) if matching else float("nan")
            X_rows.append(row_features)
            y_rows.append(int(row["is_afib"]))
        except Exception as e:  # noqa: BLE001
            extraction_times.append(0.0)
            X_rows.append({c: float("nan") for c in feature_cols})
            y_rows.append(int(row["is_afib"]))

    X = pd.DataFrame(X_rows)
    y = np.array(y_rows)

    valid_mask = ~X.isna().any(axis=1)
    X_valid = X[valid_mask]
    y_valid = y[valid_mask]

    n_train = int(0.8 * len(X_valid))
    X_train, X_test = X_valid.iloc[:n_train], X_valid.iloc[n_train:]
    y_train, y_test = y_valid[:n_train], y_valid[n_train:]

    clf = LogisticRegression(C=1.0, max_iter=2000, random_state=42)
    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:, 1]
    auroc = float(roc_auc_score(y_test, proba)) if len(set(y_test)) > 1 else float("nan")

    cv_afib = float(X_valid.loc[y_valid == 1, "CVnn"].mean()) if "CVnn" in X_valid.columns else float("nan")
    cv_non = float(X_valid.loc[y_valid == 0, "CVnn"].mean()) if "CVnn" in X_valid.columns else float("nan")

    mean_extract = float(np.mean(extraction_times))
    passed = (
        mean_extract < 10.0
        and not np.isnan(auroc)
        and auroc > 0.75
        and (np.isnan(cv_afib) or cv_afib > cv_non)
    )

    return {
        "status": "pass" if passed else "fail",
        "n_sample_loaded": int(len(X_rows)),
        "n_valid_after_extraction": int(valid_mask.sum()),
        "mean_extract_time_s": round(mean_extract, 3),
        "median_extract_time_s": round(float(np.median(extraction_times)), 3),
        "max_extract_time_s": round(float(np.max(extraction_times)), 3),
        "auroc_held_out_200": round(auroc, 4) if not np.isnan(auroc) else None,
        "cv_rrinterval_afib_mean": round(cv_afib, 4) if not np.isnan(cv_afib) else None,
        "cv_rrinterval_non_afib_mean": round(cv_non, 4) if not np.isnan(cv_non) else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-2 classical baseline speed + AUROC")
    ap.add_argument(
        "--ptbxl-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "ptb-xl-1.0.3",
    )
    ap.add_argument("--n-sample", type=int, default=1000)
    ap.add_argument("--sampling-rate", type=int, default=100)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.ptbxl_dir, args.n_sample, args.sampling_rate)
    result["pilot"] = "P-2"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-2"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p2_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
