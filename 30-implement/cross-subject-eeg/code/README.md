> **Spec:** `20-plan/cross-subject-eeg/approach.md`

# cross-subject-eeg — implementation

Code, environment, run instructions for the cross-subject-eeg track.

**Spec:** see `20-plan/cross-subject-eeg/{approach,risk-register,protocol-lock,pilots-README}.md`. Do not modify the locked protocol from here — changes require an unlock note + critic re-pass at layer 20.

## Layout

```
code/
  README.md             ← this file
  requirements.txt      ← pinned deps for the env
  pilots/               ← pilot scripts (dev-only; results in ../runs/)
    p1_labram_vram_probe.py
    p2_mdm_speed_probe.py
    ...
  headline/             ← (created when pilots clear) locked-protocol scripts
runs/
  pilot_p1_<timestamp>.json
  ...
```

## Environment setup

GTX 1650 4 GB host; Python 3.11.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

LaBraM weights are not on PyPI. Download separately:

```powershell
# Clone the repo, follow its README to fetch the LaBraM-Base checkpoint
git clone https://github.com/935963004/LaBraM external/LaBraM
# Place the checkpoint at: external/LaBraM/checkpoints/labram-base.pth
```

## Running pilots

Pilots run against the dev split only (BNCI2014_001 + secondary dev dataset to be selected at week 1). They do NOT touch PhysionetMI or HBN R9–R11.

```powershell
python pilots/p1_labram_vram_probe.py --checkpoint external/LaBraM/checkpoints/labram-base.pth --dtype float32
```

Results land in `../runs/pilot_p1_<timestamp>.json`. Re-run with `--dtype float16` if float32 exceeds 3 GB per pilot success criterion.

## Headline run

Only after pilots clear and `protocol-lock.md` is unmodified. Script under `headline/` (not yet written). The headline touches the held-out partition exactly once and writes to `runs/headline_<date>.json` + appends to `../results.md`.

Pre-run checklist required by `protocol-lock.md` §3.6 — see `runs/pre-run-checklist.txt` (created at headline time).

## Cancel-back

If a pilot fails its success criterion (e.g., LaBraM > 3 GB at float16 on Kaggle T4 too — R-3 kill), follow the risk-register's mitigation steps. If no path recovers, escalate to layer 20 for re-design or layer 10 for retire-cancel.
