> **Spec:** `20-plan/ecg-ppg-realworld/approach.md`

# ecg-ppg-realworld — implementation

Code, environment, run instructions for the ecg-ppg-realworld track.

**Spec:** see `20-plan/ecg-ppg-realworld/{approach,risk-register,protocol-lock,pilots-README}.md`. Locked protocol: do not modify from here.

## Layout

```
code/
  README.md                       # this file
  requirements.txt                # pinned deps
  pilots/                         # pilot scripts (dev-only; results in ../runs/)
    p1_cinc2017_load.py           # CRITICAL — CinC 2017 download + class count
    p2_classical_baseline.py      # NeuroKit2 + LR sanity AUROC
    p3_xresnet_vram_cinc.py       # CRITICAL — VRAM probe at (1, 1, 9000)
    p4_abstention_sweep.py
    p5_calibration_baseline.py
    p6_partition_audit.py         # builds canonical runs/partition.json
  headline/                       # post-pilots: locked-protocol scripts
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
| CinC 2017 v1.0.0 | https://physionet.org/content/challenge-2017/1.0.0/ | ODC-BY (open, no credentialing) | 8,528 single-lead ECGs, 300 Hz, REFERENCE-v3.csv labels (N / A / O / ~). |

PTB-XL was the prior primary; it was retired in v2 unlock (2026-05-03)
after pilot P-1 found only 8 AFIB records in strat_fold 10 (need >= 87
for power). See `20-plan/ecg-ppg-realworld/unlock-note-2026-05-03.md`.

## Running pilots

```powershell
python pilots/p1_cinc2017_load.py --cinc-dir $HOME/physionet_data/challenge-2017-1.0.0
python pilots/p6_partition_audit.py --cinc-dir $HOME/physionet_data/challenge-2017-1.0.0
python pilots/p3_xresnet_vram_cinc.py        # synthetic input ok for VRAM portion
# etc.
```

## Headline run

Only after pilots clear and `protocol-lock.md` unmodified. Touches the
20 % held-out test partition (per `runs/partition.json`) exactly once.
Pre-run-checklist required at `runs/pre-run-checklist.txt`.

## Cancel-back

Per risk-register triggers — most likely failures are R-2 (xresnet
VRAM > envelope at 9 k seq_len, P-3 substitution path xresnet1d50 →
xresnet1d18 pre-authorised) and R-7 (protocol violation). Both
retire-cancel.
