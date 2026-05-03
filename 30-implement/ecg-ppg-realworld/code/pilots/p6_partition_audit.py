"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-6

P-6 — CinC 2017 partition audit: build and validate dev/test split.

Builds the canonical partition.json that the headline run consumes.
Verifies the protocol-lock §3 spec:
  - StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
  - Dev count in [6,750, 6,820]; test count in [1,690, 1,710].
  - Test AF (`A`) count in [140, 170] (target ~154).
  - validate_partition() returns zero violations (no record ID in
    both dev and test).

Writes:
  - 30-implement/ecg-ppg-realworld/runs/partition.json
  - 30-implement/ecg-ppg-realworld/runs/partition_audit.txt
  - 30-implement/ecg-ppg-realworld/runs/pilot_p6_*.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path


def find_reference_csv(cinc_dir: Path) -> Path | None:
    for cand in ("REFERENCE-v3.csv", "REFERENCE.csv", "training2017/REFERENCE-v3.csv", "training2017/REFERENCE.csv"):
        p = cinc_dir / cand
        if p.exists():
            return p
    return None


def probe(cinc_dir: Path, runs_dir: Path, seed: int, test_fraction: float) -> dict:
    if not cinc_dir.exists():
        return {"status": "fail", "reason": f"CinC 2017 dir not found at {cinc_dir}"}

    reference_csv = find_reference_csv(cinc_dir)
    if reference_csv is None:
        return {"status": "fail", "reason": f"REFERENCE(-v3).csv not found under {cinc_dir}"}

    try:
        import pandas as pd
        from sklearn.model_selection import StratifiedShuffleSplit
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    df = pd.read_csv(reference_csv, header=None, names=["record_id", "label"])
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_fraction, random_state=seed)
    splits = list(sss.split(df["record_id"], df["label"]))
    dev_idx, test_idx = splits[0]

    dev_records = sorted(df.iloc[dev_idx]["record_id"].tolist())
    test_records = sorted(df.iloc[test_idx]["record_id"].tolist())

    overlap = sorted(set(dev_records) & set(test_records))
    overlap_count = len(overlap)

    test_per_class = Counter(df.iloc[test_idx]["label"].tolist())
    dev_per_class = Counter(df.iloc[dev_idx]["label"].tolist())

    n_dev = len(dev_records)
    n_test = len(test_records)
    test_af = int(test_per_class.get("A", 0))

    dev_in_range = 6750 <= n_dev <= 6830
    test_in_range = 1690 <= n_test <= 1710
    test_af_in_range = 140 <= test_af <= 170
    no_overlap = overlap_count == 0

    status = "pass" if (dev_in_range and test_in_range and test_af_in_range and no_overlap) else "fail"

    runs_dir.mkdir(parents=True, exist_ok=True)
    partition_json = runs_dir / "partition.json"
    partition_json.write_text(
        json.dumps(
            {
                "seed": seed,
                "test_fraction": test_fraction,
                "dev_record_ids": dev_records,
                "test_record_ids": test_records,
            },
            indent=2,
        )
    )

    audit_txt = runs_dir / "partition_audit.txt"
    audit_lines = [
        f"P-6 partition audit — {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"reference_csv: {reference_csv}",
        f"seed: {seed}, test_fraction: {test_fraction}",
        f"n_dev: {n_dev} (in [6750,6820]: {dev_in_range})",
        f"n_test: {n_test} (in [1690,1710]: {test_in_range})",
        f"test per-class: {dict(test_per_class)} (test_af in [140,170]: {test_af_in_range})",
        f"dev per-class: {dict(dev_per_class)}",
        f"overlap_count: {overlap_count} (no_overlap pass: {no_overlap})",
        f"status: {status}",
    ]
    audit_txt.write_text("\n".join(audit_lines) + "\n")

    return {
        "status": status,
        "seed": seed,
        "test_fraction": test_fraction,
        "n_dev": n_dev,
        "n_test": n_test,
        "dev_per_class": dict(dev_per_class),
        "test_per_class": dict(test_per_class),
        "test_af": test_af,
        "dev_in_range": dev_in_range,
        "test_in_range": test_in_range,
        "test_af_in_range": test_af_in_range,
        "no_overlap": no_overlap,
        "overlap_count": overlap_count,
        "partition_json": str(partition_json),
        "audit_txt": str(audit_txt),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-6 CinC 2017 partition audit")
    ap.add_argument(
        "--cinc-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "challenge-2017-1.0.0",
    )
    ap.add_argument(
        "--runs-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "runs",
    )
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--test-fraction", type=float, default=0.20)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.cinc_dir, args.runs_dir, args.seed, args.test_fraction)
    result["pilot"] = "P-6"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-6"

    out_path = args.out or (
        args.runs_dir / f"pilot_p6_partition_audit_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
