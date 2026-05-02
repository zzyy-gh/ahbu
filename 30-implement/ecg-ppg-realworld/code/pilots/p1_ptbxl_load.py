"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-1

P-1 — PTB-XL load + AFIB record count verification.

CRITICAL gating pilot. Verifies:
  (a) PTB-XL v1.0.3 is downloadable + loadable.
  (b) Strat_fold 10 has >= 87 AFIB records (per protocol-lock §4 power
      requirement: N_required = 87 for 21pp PPV improvement at 80%).

If (b) fails, R-1 triggers — methodology must redesign or retire-cancel.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def probe(ptbxl_dir: Path, likelihood_threshold: float, target_afib_count: int) -> dict:
    if not ptbxl_dir.exists():
        return {
            "status": "fail",
            "reason": f"PTB-XL dir not found at {ptbxl_dir}. Download per code/README.md.",
        }
    metadata_csv = ptbxl_dir / "ptbxl_database.csv"
    if not metadata_csv.exists():
        return {"status": "fail", "reason": f"ptbxl_database.csv not found at {metadata_csv}"}

    try:
        import ast
        import pandas as pd
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    df = pd.read_csv(metadata_csv, index_col="ecg_id")

    def parse_codes(s):
        try:
            return ast.literal_eval(s)
        except Exception:
            return {}

    df["scp_codes_dict"] = df["scp_codes"].apply(parse_codes)
    df["is_afib"] = df["scp_codes_dict"].apply(
        lambda d: d.get("AFIB", 0.0) >= likelihood_threshold
    )

    n_total = len(df)
    n_afib = int(df["is_afib"].sum())

    per_fold = {}
    for fold in sorted(df["strat_fold"].unique()):
        sub = df[df["strat_fold"] == fold]
        per_fold[int(fold)] = {
            "n_records": int(len(sub)),
            "n_afib": int(sub["is_afib"].sum()),
        }

    fold10_afib = per_fold.get(10, {}).get("n_afib", 0)
    passed = fold10_afib >= target_afib_count

    return {
        "status": "pass" if passed else "fail",
        "n_total": n_total,
        "n_afib_total": n_afib,
        "afib_likelihood_threshold": likelihood_threshold,
        "target_afib_count_strat_fold_10": target_afib_count,
        "fold10_afib_count": fold10_afib,
        "per_fold": per_fold,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-1 PTB-XL load + AFIB count")
    ap.add_argument(
        "--ptbxl-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "ptb-xl-1.0.3",
    )
    ap.add_argument("--likelihood-threshold", type=float, default=100.0)
    ap.add_argument("--target-afib-count", type=int, default=87)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.ptbxl_dir, args.likelihood_threshold, args.target_afib_count)
    result["pilot"] = "P-1"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-1"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p1_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
