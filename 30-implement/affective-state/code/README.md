> **Spec:** `20-plan/affective-state/approach.md`

# affective-state — implementation

Code, environment, run instructions for the affective-state feature-stability audit.

**Spec:** see `20-plan/affective-state/{approach,risk-register,protocol-lock,pilots-README}.md`. Pure CPU work; no GPU required.

## Layout

```
code/
  README.md                  # this file
  requirements.txt           # pinned deps (NeuroKit2 is the load-bearing one)
  pilots/                    # pilot scripts (dev-only; results in ../runs/)
    p1_neurokit2_schema.py   # extract feature schema, count N_features (locks YAML)
    p2_wesad_eda_smoke.py    # WESAD download + EDA pipeline; cvxpy install smoke first
    p3_arousal_distribution.py
    p4_cvxeda_vs_highpass.py
    p5_dreamer_access.py     # backup dataset probe
    p6_feature_stability_unit.py  # smoke test for shared promotion candidate
  headline/                  # post-pilots: locked-protocol scripts
runs/
  feature_schema_v1.yaml     # locked at P-1
results.md
```

## Environment setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Pre-pilot smoke (per pilots-README P-2 m-6 fix):
pip install cvxpy
# If cvxpy install fails, swap EDA primary to nk.eda_phasic(method="highpass")
# and document.
```

## Data access

| Dataset | Source | Tier | Notes |
|---|---|---|---|
| WESAD | https://physionet.org/content/wesad/1.0.0/ | open (CC-BY) | 15 subj, ECG/EDA/EMG/RESP/ACC, stress vs amusement vs baseline |
| DEAP | http://www.eecs.qmul.ac.uk/mmv/datasets/deap/ | request form | 32 subj, EEG + peripheral, 40 video clips with arousal/valence self-report |
| MAHNOB-HCI | https://mahnob-db.eu/hci-tagging/ | request form | 27 subj, EEG + ECG + EDA + video, felt arousal self-report |
| DREAMER (backup) | request | request form | 23 subj — fallback if DEAP/MAHNOB-HCI denied |

## Running pilots

```powershell
python pilots/p1_neurokit2_schema.py            # locks feature_schema_v1.yaml
python pilots/p2_wesad_eda_smoke.py             # gates on cvxpy install
# ...
```

## Headline run

Only after pilots clear AND `protocol-lock.md` + `feature_schema_v1.yaml` are committed. The correlation analysis is run **once** on the frozen feature matrices. Pre-run checklist required at `runs/pre-run-checklist.txt`.

## Cancel-back

Per risk-register: R-1 (dataset access — both DEAP and MAHNOB-HCI denied AND DREAMER denied → retire-cancel), R-5 demotion (≥ 2/3 datasets fail label-quality → drop "three-dataset audit" framing).
