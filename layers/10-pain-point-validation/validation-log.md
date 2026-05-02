# Pain-point validation log

Chronological log of validation activities. Append entries; don't rewrite history.

## 2026-05-02

- Repo scaffolded. Layers 00–40 defined per Layered Endeavor Framework.
- Resource picture captured: GTX 1650 4 GB; classical ML / small DL / pretrained-feature regimes feasible.
- Next: broad survey of candidate pain points (target ≥ 5 candidates from independent angles before narrowing).
- Candidate added: `candidates/ecg-ppg-realworld.md` — ECG/PPG real-world interpretation pain (AFib false alerts, PPG motion/skin-tone, Holter review burden, HRV over-claim, ML domain-shift); ≥2 independent sources per sub-claim; verification gaps noted (Reddit threads, NeuroKit2 issue tracker, quantified clinician burden).
- 2026-05-02 — cross-subject EEG investigated by researcher agent — N candidates of evidence found — see candidates/cross-subject-eeg.md
- 2026-05-02 — sleep staging & event detection investigated by pain-point-researcher — evidence: Lee 2022 inter-rater meta-analysis (κ=0.76 overall, N1 κ=0.24); U-Sleep / DeepSleepNet / SleepTransformer benchmarks vs human ceiling; Korkalainen 2020 OSA-severity degradation (84.5%→76.5%); pediatric & elderly age-bias (van Gorp 2023, U-Sleep peds 2024); AASM v3 hypopnea-scoring ethics dispute (Rosen & Auckley 2024); Oura/Whoop/Fitbit/Apple Watch validation studies (Stone 2021, Chee 2024, Sleep Adv 2025); Garmin/Apple consumer forum threads on REM mis-detection; Sleep-EDF dataset caveats — see candidates/sleep-staging.md
- 2026-05-02 — affective / mental-state inference investigated by pain-point-researcher — evidence: Apicella 2024 cross-subject systematic review (50–70% LOSO ceiling); Brookshire 2024 Frontiers Neurosci data-leakage paper ("most published DNN-EEG studies may dramatically overestimate"); CEUR-WS Vol-4115 trial-leakage on emotion benchmarks; LibEER 2024 + arXiv:2505.18175 evaluation review; reproducible-features arXiv:2508.10561 (2 of 164 features replicate); Lindquist/Barrett 2012 BBS meta-analysis (no consistent emotion-region mapping) and Barrett ANS-specificity work; WESAD person-specific 98.9 % vs generic 83.9 %; BIS/NoL/ANI clinical limitations (Hajat 2017, Shanker BJA 2023, Ledowski BJA 2019, ASRA 2024, APSF); EU AI Act Article 5(1)(f) workplace/education emotion-AI ban Feb 2025; MOABB reproducibility framework (covers MI/P300/SSVEP, not affective). Candor: subfield is epistemically weak; recommended angle is honest-evaluation / leakage-diagnostic, not new-SOTA — see candidates/affective-state.md
- 2026-05-02 — broad survey (4 candidates) consolidated into `selection-shortlist.md`. Top two for selection-phase scrutiny: `ecg-ppg-realworld` (narrowed) and `sleep-staging` (narrowed). `cross-subject-eeg` and `affective-state` deferred with reasons.
