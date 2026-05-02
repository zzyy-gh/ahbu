> **Spec:** `00-vision/README.md` (hard constraint #1: pain real and validated) + `10-pain-point/README.md` (validation rubric)

# Admission record — ecg-ppg-realworld

- **Date:** 2026-05-02
- **Slug:** `ecg-ppg-realworld`
- **Rubric version:** v2 (real-pain only at layer 10; feasibility / quality bar enforced at layers 20 / 30)
- **Verdict:** **admitted** (pass-with-fixes — JMIR 2024 misattributed-numbers fix applied in candidate.md §3c)
- **Track dirs:** `20-plan/ecg-ppg-realworld/` (next), `30-implement/ecg-ppg-realworld/` (later)

## Pain statement (one paragraph)

Consumer wearables and clinical ECG/PPG pipelines produce alerts and stage estimates that are often inaccurate or non-actionable in the wild: AFib false-positive cascades that drive avoidable visits, motion / electrode-displacement artifacts that wreck rhythm classification, demographic generalization gaps (skin tone, age, comorbidities) that bias outputs, Holter / patch-monitor review burden, HRV over-interpretation by consumer apps, and ML benchmarks that drop ~10 % when moved off-distribution. Constituencies that feel this include patients living with false-alert anxiety, GPs and cardiac techs absorbing the workflow cost, athletes interpreting noisy HRV, and ML developers shipping into deployment.

## Real-pain evidence (admission gate)

≥ 2 independent evidence classes per sub-pain, all confirmed by critic pass with one major fix applied:

1. **AFib false-positive burden — clinical cohort.** JAHA 2024 doi:10.1161/JAHA.123.033750 — wearable users 2.04 vs non-users 1.33 AF-specific outpatient visits (P=0.02); 1.84 vs 1.00 rhythm-related procedures (P=0.004); 20 % "always contacted doctors" on irregular-rhythm notifications.
2. **AFib false-positive burden — population/regulatory.** Apple Heart Study (NEJM 2019); FDA De Novo DEN180042; BASEL Wearable Study (Mannhart et al., JACC Clinical Electrophysiology 9(2), 2023, 17–21 % inconclusive).
3. **Skin-tone disparity — meta-analysis.** Singh et al., JMIR 2024 — pooled SpO₂ bias 1.27 % (dark, 95 % CI 0.58–1.95) vs 0.70 % (light, 95 % CI 0.17–1.22); both exceed FDA accuracy thresholds. (Earlier-draft 60–70 % saturation specifics were misattributed; removed and replaced with verified pooled figures per critic 2026-05-02.)
4. **Skin-tone calibration gap — secondary.** MDPI Sensors review on PPG calibration bias.
5. **Practitioner pain — clinician voice.** STAT News 2019 (Dr. Venkatesh Murthy on false-alarm burden, verified verbatim).
6. **OSS ecosystem pain.** NeuroKit2 issue #1115 — practitioner-flagged PPG amplitude artifact pain, real workflow detail.
7. **ML benchmark — domain-shift evidence.** PhysioNet/CinC 2020 — ~10 % drop on hidden test data.
8. **HRV over-claim — academic.** JMIR Human Factors 2022 HRV validity study; PMC9707930 (Smole et al. 2023 selective classification on ECG).

Independence threshold (≥ 2 sources per sub-claim) comfortably exceeded.

## Constituency

Wearable users (consumer + patient), GPs, cardiac techs, athletes, dark-skin users, ML researchers shipping into deployment. **Reachable** via Apple/Garmin/Fitbit support forums, NeuroKit2 / BioSPPy / py-ecg-detectors GitHub, PhysioNet challenge organizers, paper-author emails.

## Critic pass

`real-pain-critic.md` — verdict `pass-with-fixes`. One major (misattributed JMIR figures in §3c — fixed in candidate file 2026-05-02). Three minor (BASEL venue label, PMC7085621 quotation marks, STAT cardiologist quote framing — all carry into early track life as advisories, none blocking).

## Advisory annotations (NOT gating — input to layer 20 / 30)

**From gap-closing pass (researcher a83811):**
- Skin-tone Fitzpatrick-stratified PPG eval at adequate sample size = INFEASIBLE on public data (only MIMIC PERform Ethnicity has any race split — binary B/W, n=100/100 ICU PPG). Layer 20 should drop the skin-tone scope or narrow drastically.
- Calibrated-abstention novelty PARTIALLY refuted (Smole 2023, NCA 2024, Barandas 2024 already do ECG abstention). Genuine novelty remains in PTB-XL + PPV-at-fixed-alert-rate, cross-dataset abstention, or conformal coverage on single-lead wearable.

**From defensibility critic (a52506) — historical, advisory:**
- ecg-ppg-realworld scope (a) calibrated abstention for AFib alerts on PTB-XL: defensible-null. PTB-XL ~303 AFIB records adequate for 21 pp PPV improvement (N required = 87).
- ecg-ppg-realworld scope (b) skin-tone PPG: fragile-null at BUT-PPG n=48 (3–13× underpowered for known effects).

**From reuse sketch (methodologist a6dd95):**
- Promotion candidates: `30-implement/shared/eval/calibration.py` (Brier, ECE, reliability), `abstention.py` (selective-classification protocol), `30-implement/shared/data/patient_disjoint_split.py`. Plausible 2nd consumer = sleep-staging (calibration utilities).

## Open items to close in early track life

- BASEL venue / DOI confirmation
- PMC7085621 quotation marks (verbatim or paraphrase)
- Trace or remove the [JCSM 2020] bracket appended in §3h (potential conflation)
- Identify alternative source for the 60–70 % saturation specifics if the figures were drawn from a paper outside Singh et al. 2024 (e.g., Sjoding et al. NEJM 2020 ICU pulse-ox)

## Human checkpoint

- [x] Lead reviewed critic verdict and evidence — 2026-05-02
- [ ] Human approval to instantiate `20-plan/ecg-ppg-realworld/`

When human approves, instantiate `20-plan/ecg-ppg-realworld/`, update `10-pain-point/shared/portfolio.md`, tag `v2-ecg-ppg-realworld-admitted`.
