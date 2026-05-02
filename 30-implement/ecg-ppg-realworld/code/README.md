> **Spec:** `20-plan/ecg-ppg-realworld/approach.md`

# ecg-ppg-realworld — implementation

Code, environment, run instructions for the ecg-ppg-realworld track.

**Spec:** see `20-plan/ecg-ppg-realworld/{approach,risk-register,protocol-lock,pilots-README}.md`. Locked protocol: do not modify from here.

## Layout

```
code/
  README.md                # this file
  requirements.txt         # pinned deps
  pilots/                  # pilot scripts (dev-only; results in ../runs/)
    p1_ptbxl_load.py       # CRITICAL — verify PTB-XL loads + AFIB count >= 87
    p2_classical_baseline.py
    p3_xresnet_vram.py     # CRITICAL — VRAM probe at GTX 1650
    p4_abstention_sweep.py
    p5_calibration_baseline.py
    p6_site_overlap.py     # optional
    p7_cinc2017_compat.py  # exploratory
  headline/                # post-pilots: locked-protocol scripts
runs/
results.md
```

## Environment setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Data access

| Dataset | Source | Tier | Notes |
|---|---|---|---|
| PTB-XL v1.0.3 | https://physionet.org/content/ptb-xl/1.0.3/ | open | ~21k 12-lead ECGs, AFIB labels via `scp_codes`, strat_folds 1–10 |
| CinC 2017 (P-7 only) | https://physionet.org/content/challenge-2017/1.0.0/ | open | single-lead AF challenge data; exploratory cross-dataset probe |

## Running pilots

```powershell
python pilots/p1_ptbxl_load.py --ptbxl-dir $HOME/physionet_data/ptb-xl-1.0.3
python pilots/p3_xresnet_vram.py
# etc.
```

## Headline run

Only after pilots clear and `protocol-lock.md` unmodified. Touches strat_fold 10 exactly once. Pre-run-checklist required at `runs/pre-run-checklist.txt`.

## Cancel-back

Per risk-register triggers — most likely failures are R-3 (xresnet VRAM > envelope) and R-7 (protocol violation). Both retire-cancel.
