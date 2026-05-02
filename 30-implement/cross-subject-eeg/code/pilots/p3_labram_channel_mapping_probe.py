"""
Spec: 20-plan/cross-subject-eeg/pilots-README.md#P-3
P-3 — LaBraM channel-mapping probe.

Question: can LaBraM-Base process BNCI2014_001's 22-channel montage without
error?

Spec: 20-plan/cross-subject-eeg/pilots-README.md §P-3.

Success criterion: non-degenerate embedding output for > 90% of test epochs.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def probe(checkpoint_path: Path, n_subjects: int) -> dict:
    try:
        import numpy as np
        import torch
        from moabb.datasets import BNCI2014_001
        from moabb.paradigms import MotorImagery
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    if not checkpoint_path.exists():
        return {"status": "fail", "reason": f"Checkpoint not found at {checkpoint_path}."}

    if not torch.cuda.is_available():
        return {"status": "fail", "reason": "CUDA not available"}

    here = Path(__file__).resolve().parents[1]
    labram_root = here / "external" / "LaBraM"
    if labram_root.exists():
        sys.path.insert(0, str(labram_root))
    else:
        return {
            "status": "fail",
            "reason": "external/LaBraM not found. Run: git clone https://github.com/935963004/LaBraM external/LaBraM",
        }

    try:
        from modeling_finetune import labram_base_patch200_200  # type: ignore
    except ImportError as e:
        return {"status": "fail", "reason": f"LaBraM import failed: {e}"}

    device = torch.device("cuda")

    paradigm = MotorImagery(n_classes=4)
    dataset = BNCI2014_001()
    subjects = dataset.subject_list[:n_subjects]
    X, y, meta = paradigm.get_data(dataset=dataset, subjects=subjects)

    n_channels = int(X.shape[1])
    n_patches = max(int(X.shape[2]) // 200, 1)
    truncated_samples = n_patches * 200
    X = X[:, :, :truncated_samples]

    model = labram_base_patch200_200(EEG_size=truncated_samples, init_values=0.1)
    state = torch.load(checkpoint_path, map_location=device)
    if isinstance(state, dict) and "model" in state:
        state = state["model"]
    model.load_state_dict(state, strict=False)
    model.to(device).eval()

    input_chans = list(range(n_channels + 1))

    n_total = X.shape[0]
    n_nondegenerate = 0
    failure_modes = {"nan": 0, "all_zero": 0, "constant": 0}

    with torch.no_grad():
        for i in range(n_total):
            x_np = X[i : i + 1].reshape(1, n_channels, n_patches, 200)
            x = torch.tensor(x_np, device=device, dtype=torch.float32)
            try:
                out = model.forward_features(x, input_chans=input_chans)
                emb = out.detach().cpu().numpy().flatten()
                if np.any(np.isnan(emb)):
                    failure_modes["nan"] += 1
                elif np.allclose(emb, 0):
                    failure_modes["all_zero"] += 1
                elif np.std(emb) < 1e-6:
                    failure_modes["constant"] += 1
                else:
                    n_nondegenerate += 1
            except Exception as e:  # noqa: BLE001
                return {"status": "fail", "reason": f"forward pass error on epoch {i}: {e}"}

    fraction_ok = n_nondegenerate / max(n_total, 1)
    threshold = 0.90
    return {
        "status": "pass" if fraction_ok > threshold else "fail",
        "n_subjects": len(subjects),
        "n_epochs_total": int(n_total),
        "n_nondegenerate": n_nondegenerate,
        "fraction_nondegenerate": round(fraction_ok, 4),
        "threshold": threshold,
        "failure_modes": failure_modes,
        "n_channels": int(X.shape[1]),
        "n_samples": int(X.shape[2]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-3 LaBraM channel-mapping probe")
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--n-subjects", type=int, default=5)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.checkpoint, args.n_subjects)
    result["pilot"] = "P-3"
    result["spec"] = "20-plan/cross-subject-eeg/pilots-README.md#P-3"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p3_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
