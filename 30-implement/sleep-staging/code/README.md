> **Spec:** `20-plan/sleep-staging/approach.md`

# sleep-staging — implementation

Code, environment, run instructions for the sleep-staging track.

**Spec:** see `20-plan/sleep-staging/{approach,risk-register,protocol-lock,pilots-README}.md`. Do not modify the locked protocol from here — changes require an unlock note + critic re-pass at layer 20.

## Layout

```
code/
  README.md             ← this file
  requirements.txt      ← pinned deps
  pilots/               ← pilot scripts (dev-only; results in ../runs/)
    p1_hmc_access_check.py
    p2_dreem_dod_label_check.py
    p3_usleep_vram_probe.py
    p4_within_subject_rf_ceiling.py
    p5_lstm_temporal_probe.py
    p6_dreem_dod_o_framing.py
  headline/             ← (created when pilots clear) locked-protocol scripts
runs/
  pilot_p<N>_<timestamp>.json
```

## Environment setup

GTX 1650 4 GB host; Python 3.11. CPU-bound for primary scope (b);
U-Sleep inference is the only GPU step.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Data access

| Dataset | Source | Tier | Notes |
|---|---|---|---|
| HMC Sleep Staging Database | https://physionet.org/content/hmc-sleep-staging/1.0.0/ | credentialed | PhysioNet account + signed DUA-equivalent (~same-session). 154 subj, ECG + EEG + AASM stages. |
| Dreem-DOD-O | Zenodo 15900394 | open | OSA cohort, 55 subjects, JSON consensus labels |
| Sleep-EDF Cassette | https://physionet.org/content/sleep-edfx/1.0.0/ | open | for U-Sleep sanity check (P-3) |
| NSRR (SHHS / MESA) | sleepdata.org | DUA, ~4 wk | scope (a) only; submit day 1 |

LaBraM is NOT used in this track.

## Running pilots

```powershell
python pilots/p1_hmc_access_check.py --subjects 10
python pilots/p2_dreem_dod_label_check.py
python pilots/p3_usleep_vram_probe.py
# ... etc.
```

Each writes `../runs/pilot_p<N>_<timestamp>.json`.

## Headline run

Only after pilots clear and `protocol-lock.md` is unmodified. Script under `headline/` (not yet written). Headline touches the held-out partition (HMC PSG 77 test subjects) exactly once and writes to `runs/headline_<date>.json` + appends to `../results.md`.

Pre-run checklist required by `protocol-lock.md` §6 — see `runs/pre-run-checklist.txt` (created at headline time). Includes the U-Sleep training-overlap audit per critic m-5 fix.

## Cancel-back

If a pilot fails its success criterion (e.g., P-1 finds HMC PSG DUA-blocked → R-2 substitute path), follow the risk-register's mitigation steps. If no path recovers, escalate to layer 20 (re-design) or layer 10 (retire-cancel).
