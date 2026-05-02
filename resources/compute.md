# Resource picture

Captured 2026-05-02. Update when changes.

## Local machine

- OS: Windows 11 Pro (10.0.26200)
- Python: 3.11.2
- pip: 23.0.1
- GPU: NVIDIA GeForce GTX 1650 (4 GB VRAM, driver 535.98, CUDA 12.2)
- RAM: TBD (probe failed with WMIC; can re-probe with `Get-CimInstance` if needed)

## Implications

4 GB VRAM is the binding constraint for deep learning. Reasonable regimes:

- Classical ML on engineered features (sklearn, xgboost) — comfortable.
- Small CNNs / MLPs / shallow transformers (≤ ~30 M params) — feasible with mixed-precision and small batches.
- Fine-tuning small heads on **pretrained** backbones (frozen feature extraction) — feasible.
- Pretraining or full fine-tuning of foundation models — **out of scope** locally.

## Free / public compute that may be in scope

- Colab free tier (T4 16 GB, time-limited) — feasible for moderate training jobs.
- Kaggle notebooks (P100 / T4, 30 GB RAM, 9 hr) — feasible for moderate jobs and dataset access.
- HuggingFace Spaces (CPU free, GPU paid).

Use these *only* if a project-relevant experiment justifies the data egress / setup cost. Default to local.

## Time horizon

To be scoped at start of methodology layer (layer 20). Default suggestion: 2–4 weeks of focused effort to a first honest result, with explicit kill criteria.
