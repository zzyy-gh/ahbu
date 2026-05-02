"""
Spec: 20-plan/cross-subject-eeg/protocol-lock.md#4

Pre-training overlap audit. Run BEFORE the headline touches the
held-out test partition.

Reads labram_pretrain_datasets.txt and audits both:
  - Test datasets (PhysionetMI + HBN R9-R11 if used)
  - Dev datasets (BNCI2014_001, Cho2017, Lee2019) — added per critic M-2 fix

Writes 30-implement/cross-subject-eeg/runs/leakage_audit_result.json.
Exits non-zero if any test-set overlap is found AND no substitution path
is documented.
"""

import argparse
import json
import sys
from pathlib import Path


DATASET_ALIASES = {
    "bnci2014001": "bciciv2a",
    "bnci2014_001": "bciciv2a",
    "bnci2014002": "bciciv2b",
    "bnci2014_002": "bciciv2b",
    "bcicompetitionivdataset2a": "bciciv2a",
    "bcicompetitionivdataset2b": "bciciv2b",
    "physionetmotormovement": "physionetmotormovement",
    "physionetmi": "physionetmotormovement",
    "hbn": "hbn",
    "hbnr9": "hbn",
    "hbnr10": "hbn",
    "hbnr11": "hbn",
    "healthybrainnetwork": "hbn",
    "hmcpsg": "hmcpsg",
    "hmcsleepstaging": "hmcpsg",
}


def normalize(name: str) -> str:
    base = name.lower().replace("_", "").replace("-", "").replace(" ", "")
    return DATASET_ALIASES.get(base, base)


def check_dataset_overlap(pretrain_list, eval_list):
    pretrain_norm = {normalize(s) for s in pretrain_list}
    eval_norm = {normalize(s): s for s in eval_list}
    overlap = sorted([orig for n, orig in eval_norm.items() if n in pretrain_norm])
    return {
        "overlap_datasets": overlap,
        "clean": len(overlap) == 0,
        "n_pretrain": len(pretrain_norm),
        "n_eval": len(eval_norm),
    }


def report_leakage_summary(test_result, dev_result, fm_name, eval_set_name):
    return {
        "fm_name": fm_name,
        "eval_set_name": eval_set_name,
        "test_audit": test_result,
        "dev_audit": dev_result,
        "test_clean": test_result["clean"],
        "dev_clean": dev_result["clean"],
        "ablation_2_will_trigger": not dev_result["clean"],
        "headline_can_proceed": test_result["clean"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-training overlap audit")
    ap.add_argument(
        "--pretrain-list",
        type=Path,
        default=Path(__file__).parent / "labram_pretrain_datasets.txt",
    )
    ap.add_argument(
        "--test-datasets",
        nargs="+",
        default=["PhysionetMI", "HBN_R9", "HBN_R10", "HBN_R11"],
    )
    ap.add_argument(
        "--dev-datasets",
        nargs="+",
        default=["BNCI2014_001", "Cho2017", "Lee2019"],
    )
    ap.add_argument("--fm-name", default="LaBraM-Base")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "runs" / "leakage_audit_result.json",
    )
    args = ap.parse_args()

    if not args.pretrain_list.exists():
        print(f"FAIL: pretrain list not found at {args.pretrain_list}", file=sys.stderr)
        return 2
    pretrain_list = [
        line.strip()
        for line in args.pretrain_list.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    test_result = check_dataset_overlap(pretrain_list, args.test_datasets)
    dev_result = check_dataset_overlap(pretrain_list, args.dev_datasets)
    summary = report_leakage_summary(test_result, dev_result, args.fm_name, "headline-eval")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"\nWrote {args.out}")

    if not test_result["clean"]:
        print("\nWARNING: test-set overlap detected. Per protocol-lock §4 step 5,")
        print("substitute affected datasets or cancel the FM arm. Headline blocked.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
