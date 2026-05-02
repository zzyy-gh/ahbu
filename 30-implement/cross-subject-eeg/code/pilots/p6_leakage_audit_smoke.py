"""
P-6 — leakage_audit.py smoke test.

Question: does leakage_audit.py correctly detect known overlap in a
synthetic test case?

Spec: 20-plan/cross-subject-eeg/pilots-README.md §P-6.

Success criterion: both assertions pass. Unit test, not a scientific result.

Inlines a minimal `check_dataset_overlap` here. The promotable version
will live at `30-implement/shared/eval/leakage_audit.py` once the
promotion gate is met (≥ 1 plausible second consumer).
"""

import argparse
import json
import sys
import time
from pathlib import Path


def check_dataset_overlap(pretrain_list, eval_list):
    pretrain_set = {s.lower() for s in pretrain_list}
    eval_set = {s.lower() for s in eval_list}
    overlap = sorted(pretrain_set & eval_set)
    return {
        "overlap_datasets": overlap,
        "clean": len(overlap) == 0,
        "n_pretrain": len(pretrain_set),
        "n_eval": len(eval_set),
    }


def probe() -> dict:
    cases = []

    r1 = check_dataset_overlap(
        ["BNCI2014_001", "TUAB"], ["BNCI2014_001", "PhysionetMI"]
    )
    case1_ok = r1["overlap_datasets"] == ["bnci2014_001"] and r1["clean"] is False
    cases.append(
        {
            "case": "known overlap",
            "expected_overlap": ["bnci2014_001"],
            "expected_clean": False,
            "got": r1,
            "ok": case1_ok,
        }
    )

    r2 = check_dataset_overlap(["TUAB", "TUEV"], ["PhysionetMI", "HBN_R9"])
    case2_ok = r2["overlap_datasets"] == [] and r2["clean"] is True
    cases.append(
        {
            "case": "no overlap",
            "expected_overlap": [],
            "expected_clean": True,
            "got": r2,
            "ok": case2_ok,
        }
    )

    return {
        "status": "pass" if all(c["ok"] for c in cases) else "fail",
        "cases": cases,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-6 leakage_audit smoke test")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe()
    result["pilot"] = "P-6"
    result["spec"] = "20-plan/cross-subject-eeg/pilots-README.md#P-6"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p6_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
