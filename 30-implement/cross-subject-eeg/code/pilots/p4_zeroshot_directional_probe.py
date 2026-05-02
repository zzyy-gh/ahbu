"""
Spec: 20-plan/cross-subject-eeg/pilots-README.md#P-4
P-4 — Zero-shot accuracy on 5 BNCI2014_001 subjects.

Question: directional zero-shot cross-subject accuracy of LaBraM-Base
nearest-centroid vs MDM on BNCI2014_001 dev split.

Spec: 20-plan/cross-subject-eeg/pilots-README.md §P-4.

NOT a pass/fail. Documents the FM-minus-MDM delta at k=0 for the
risk-register and approach.md sanity check.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def labram_zeroshot(model, device, X_train, y_train, X_test):
    import numpy as np
    import torch

    with torch.no_grad():
        emb_train = []
        for i in range(X_train.shape[0]):
            x = torch.tensor(X_train[i : i + 1], device=device, dtype=torch.float32)
            emb_train.append(model(x).detach().cpu().numpy().flatten())
        emb_train = np.array(emb_train)

        classes = np.unique(y_train)
        centroids = np.array([emb_train[y_train == c].mean(axis=0) for c in classes])

        preds = []
        for i in range(X_test.shape[0]):
            x = torch.tensor(X_test[i : i + 1], device=device, dtype=torch.float32)
            emb = model(x).detach().cpu().numpy().flatten()
            dists = np.linalg.norm(centroids - emb, axis=1)
            preds.append(classes[int(np.argmin(dists))])
    return np.array(preds)


def probe(checkpoint_path: Path, n_subjects: int) -> dict:
    try:
        import numpy as np
        import torch
        from moabb.datasets import BNCI2014_001
        from moabb.paradigms import MotorImagery
        from pyriemann.classification import MDM
        from pyriemann.estimation import Covariances
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    if not checkpoint_path.exists():
        return {"status": "fail", "reason": f"Checkpoint not found at {checkpoint_path}."}

    if not torch.cuda.is_available():
        return {"status": "fail", "reason": "CUDA not available"}

    try:
        from labram import LaBraMBase  # type: ignore
    except ImportError:
        return {"status": "fail", "reason": "labram package not importable."}

    device = torch.device("cuda")

    paradigm = MotorImagery(n_classes=4)
    dataset = BNCI2014_001()
    subjects = dataset.subject_list[:n_subjects]
    X, y, meta = paradigm.get_data(dataset=dataset, subjects=subjects)
    cov = Covariances(estimator="oas").transform(X)

    state = torch.load(checkpoint_path, map_location=device)
    model = LaBraMBase()
    model.load_state_dict(state, strict=False)
    model.to(device).eval()

    per_subject = []
    for held_out in subjects:
        train_mask = meta["subject"].values != held_out
        test_mask = ~train_mask

        mdm = MDM(metric="riemann")
        mdm.fit(cov[train_mask], y[train_mask])
        acc_mdm = float(np.mean(mdm.predict(cov[test_mask]) == y[test_mask]))

        preds_fm = labram_zeroshot(model, device, X[train_mask], y[train_mask], X[test_mask])
        acc_fm = float(np.mean(preds_fm == y[test_mask]))

        per_subject.append(
            {
                "held_out": int(held_out),
                "mdm_acc": round(acc_mdm, 4),
                "labram_zeroshot_acc": round(acc_fm, 4),
                "delta_fm_minus_mdm_pp": round((acc_fm - acc_mdm) * 100, 2),
            }
        )

    mean_mdm = float(np.mean([s["mdm_acc"] for s in per_subject]))
    mean_fm = float(np.mean([s["labram_zeroshot_acc"] for s in per_subject]))
    delta_pp = (mean_fm - mean_mdm) * 100

    return {
        "status": "directional",
        "n_subjects": len(subjects),
        "mean_mdm_acc": round(mean_mdm, 4),
        "mean_labram_zeroshot_acc": round(mean_fm, 4),
        "mean_delta_fm_minus_mdm_pp": round(delta_pp, 2),
        "approach_md_consistency": (
            "fm_below_mdm_as_expected"
            if delta_pp < -10
            else "fm_competitive_or_better_revisit_approach"
        ),
        "per_subject": per_subject,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-4 zero-shot directional probe")
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--n-subjects", type=int, default=5)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.checkpoint, args.n_subjects)
    result["pilot"] = "P-4"
    result["spec"] = "20-plan/cross-subject-eeg/pilots-README.md#P-4"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p4_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
