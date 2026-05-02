"""
P-2 — MDM speed probe on BNCI2014_001.

Question: how long does a full 9-subject LOSO with pyRiemann MDM take on
BNCI2014_001?

Spec: 20-plan/cross-subject-eeg/pilots-README.md §P-2.

Success criterion: completes in < 10 minutes on CPU.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np


def probe(verbose: bool) -> dict:
    try:
        from moabb.datasets import BNCI2014_001
        from moabb.paradigms import MotorImagery
        from pyriemann.classification import MDM
        from pyriemann.estimation import Covariances
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    paradigm = MotorImagery(n_classes=4)
    dataset = BNCI2014_001()
    subjects = dataset.subject_list

    t0 = time.perf_counter()
    X, y, meta = paradigm.get_data(dataset=dataset, subjects=subjects)
    t_load = time.perf_counter() - t0

    cov = Covariances(estimator="oas").transform(X)

    per_subject = []
    t1 = time.perf_counter()
    for held_out in subjects:
        train_mask = meta["subject"].values != held_out
        test_mask = ~train_mask
        clf = MDM(metric="riemann")
        clf.fit(cov[train_mask], y[train_mask])
        acc = float(np.mean(clf.predict(cov[test_mask]) == y[test_mask]))
        per_subject.append({"held_out": int(held_out), "accuracy": round(acc, 4)})
        if verbose:
            print(f"S{held_out}: acc={acc:.3f}")
    t_loso = time.perf_counter() - t1

    mean_acc = float(np.mean([s["accuracy"] for s in per_subject]))
    threshold_s = 600.0
    passed = t_loso <= threshold_s

    return {
        "status": "pass" if passed else "fail",
        "n_subjects": len(subjects),
        "n_epochs_total": int(X.shape[0]),
        "n_channels": int(X.shape[1]),
        "data_load_time_s": round(t_load, 2),
        "loso_time_s": round(t_loso, 2),
        "threshold_s": threshold_s,
        "mean_loso_accuracy": round(mean_acc, 4),
        "per_subject": per_subject,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-2 MDM speed probe on BNCI2014_001")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.verbose)
    result["pilot"] = "P-2"
    result["spec"] = "20-plan/cross-subject-eeg/pilots-README.md#P-2"

    out_path = args.out or (
        Path(__file__).resolve().parents[2]
        / "runs"
        / f"pilot_p2_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
