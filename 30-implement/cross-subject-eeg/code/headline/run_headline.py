"""
Spec: 20-plan/cross-subject-eeg/protocol-lock.md

Headline experiment for cross-subject-eeg.
Runs the 5-part evaluation-diagnostic program on the locked PhysionetMI
held-out test partition. Touches the held-out partition exactly once.

Components:
  1. Pre-run checklist (gates execution; aborts on any fail)
  2. Leakage audit (test + dev datasets vs LaBraM corpus)
  3. Per-subject k-shot evaluation: k in {0, 1, 5, 20}
     - LaBraM-Base frozen + linear head (FM probe)
     - Riemannian MDM (primary baseline)
     - FBCSP + LDA (secondary baseline)
  4. Per-subject distribution + illiteracy fractions (chance + 70 %)
  5. Statistical test: paired one-sided Wilcoxon FM > MDM at k=20,
     Bonferroni adjusted threshold p < 0.0125 across 4 shot levels

Output:
  runs/headline_<timestamp>.json   — full results
  ../results.md                    — appended headline summary

Hard rule: this script writes a marker file `runs/.headline_started`
on launch. If that file already exists, the script REFUSES TO RUN
without an explicit `--force-rerun` flag (which violates the
touched-once discipline and requires a protocol-lock unlock note).
"""

import argparse
import json
import sys
import time
from pathlib import Path


def pre_run_checklist(runs_dir: Path) -> dict:
    """Per protocol-lock §6 (and approach.md §Touched-once)."""
    checklist = {
        "partition_definition_committed": (runs_dir / "partition_definition.json").exists(),
        "partition_audit_passed": (runs_dir / "partition_audit.txt").exists(),
        "leakage_audit_complete": (runs_dir / "leakage_audit_result.json").exists(),
        "labram_pretrain_corpus_pinned": (Path(__file__).parent / "labram_pretrain_datasets.txt").exists(),
        "no_prior_test_split_touch": not (runs_dir / ".headline_started").exists(),
    }
    return checklist


def load_labram(checkpoint_path: Path):
    here = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(here / "external" / "LaBraM"))
    from modeling_finetune import labram_base_patch200_200  # type: ignore

    import torch
    model = labram_base_patch200_200(EEG_size=200, init_values=0.1)
    state = torch.load(checkpoint_path, map_location="cuda")
    if isinstance(state, dict) and "model" in state:
        state = state["model"]
    model.load_state_dict(state, strict=False)
    model.to("cuda").eval()
    return model


def labram_embeddings(model, X, n_channels, n_patches, input_chans):
    import numpy as np
    import torch

    embs = []
    with torch.no_grad():
        for i in range(X.shape[0]):
            x = torch.tensor(
                X[i : i + 1].reshape(1, n_channels, n_patches, 200),
                device="cuda",
                dtype=torch.float32,
            )
            embs.append(model.forward_features(x, input_chans=input_chans).cpu().numpy().flatten())
    return np.array(embs)


def fewshot_eval_subject(model_name, X_dev, y_dev, X_target, y_target, k, model_state, rng):
    """Evaluate one subject at one shot level. model_state is the loaded model
    or fitted classifier per arm. Returns accuracy."""
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    if model_name == "LaBraM":
        model, n_channels, n_patches, input_chans = model_state
        emb_dev = labram_embeddings(model, X_dev, n_channels, n_patches, input_chans)
        emb_target_all = labram_embeddings(model, X_target, n_channels, n_patches, input_chans)
        if k == 0:
            classes = np.unique(y_dev)
            centroids = np.array([emb_dev[y_dev == c].mean(axis=0) for c in classes])
            preds = []
            for e in emb_target_all:
                preds.append(classes[int(np.argmin(np.linalg.norm(centroids - e, axis=1)))])
            return float(np.mean(np.array(preds) == y_target))
        else:
            shot_idx = rng.choice(len(emb_target_all), size=k * len(np.unique(y_target)), replace=False)
            X_train = np.vstack([emb_dev, emb_target_all[shot_idx]])
            y_train_combined = np.concatenate([y_dev, y_target[shot_idx]])
            mask = np.ones(len(emb_target_all), dtype=bool)
            mask[shot_idx] = False
            clf = LogisticRegression(max_iter=2000, random_state=42)
            clf.fit(X_train, y_train_combined)
            return float(np.mean(clf.predict(emb_target_all[mask]) == y_target[mask]))

    elif model_name == "MDM":
        from pyriemann.classification import MDM
        from pyriemann.estimation import Covariances

        cov_dev = Covariances(estimator="oas").transform(X_dev)
        cov_target = Covariances(estimator="oas").transform(X_target)
        if k == 0:
            mdm = MDM(metric="riemann")
            mdm.fit(cov_dev, y_dev)
            return float(np.mean(mdm.predict(cov_target) == y_target))
        else:
            shot_idx = rng.choice(len(cov_target), size=k * len(np.unique(y_target)), replace=False)
            cov_train = np.concatenate([cov_dev, cov_target[shot_idx]])
            y_train_combined = np.concatenate([y_dev, y_target[shot_idx]])
            mask = np.ones(len(cov_target), dtype=bool)
            mask[shot_idx] = False
            mdm = MDM(metric="riemann")
            mdm.fit(cov_train, y_train_combined)
            return float(np.mean(mdm.predict(cov_target[mask]) == y_target[mask]))

    raise ValueError(f"unknown model {model_name}")


def headline_run(args) -> dict:
    """Per protocol-lock — touched-once on PhysionetMI held-out subjects."""
    raise NotImplementedError(
        "STUB: headline_run wires together: load PhysionetMI test subjects + "
        "BNCI2014_001 dev subjects + (selected secondary dev) via MOABB; loops "
        "over (subject, shot, model) calling fewshot_eval_subject; aggregates "
        "per-subject accuracies; runs Wilcoxon (scipy.stats.wilcoxon, "
        "alternative='greater') comparing FM vs MDM at k=20 with Bonferroni "
        "correction (p < 0.0125 across 4 shot levels). Writes JSON. "
        "Implement when user is ready to commit GPU time (estimated 5-15 hours "
        "for full run on GTX 1650). Existing pilot scripts P-1..P-4 cover the "
        "primitives this calls."
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="cross-subject-eeg headline run")
    ap.add_argument(
        "--checkpoint",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "external" / "LaBraM" / "checkpoints" / "labram-base.pth",
    )
    ap.add_argument("--shot-levels", nargs="+", type=int, default=[0, 1, 5, 20])
    ap.add_argument("--n-shot-draws", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force-rerun", action="store_true",
                    help="DANGER: bypass the headline-once gate. Requires unlock note.")
    args = ap.parse_args()

    runs_dir = Path(__file__).resolve().parents[2] / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    started_marker = runs_dir / ".headline_started"
    if started_marker.exists() and not args.force_rerun:
        print(f"REFUSING: {started_marker} exists. Headline already started or completed.")
        print("Touched-once discipline. Use --force-rerun ONLY with an unlock note.")
        return 3

    checklist = pre_run_checklist(runs_dir)
    print("Pre-run checklist:")
    for k, v in checklist.items():
        print(f"  [{'x' if v else ' '}] {k}")
    if not all(checklist.values()):
        print("\nFAIL: pre-run checklist incomplete. Aborting.")
        return 1

    started_marker.write_text(f"started at {time.time()}\n")

    try:
        result = headline_run(args)
    except NotImplementedError as e:
        print(f"\nNOTE: {e}")
        started_marker.unlink()
        return 4

    out_path = runs_dir / f"headline_{int(time.time())}.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
