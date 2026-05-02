# Admission record — sleep-staging

- **Date:** 2026-05-02
- **Slug:** `sleep-staging`
- **Rubric version:** v2 (real-pain only at layer 10; feasibility / quality bar enforced at layers 20 / 30)
- **Verdict:** **admitted** (pass-with-fixes — Stone→Chinoy and Bakker→Choo author-name fixes applied in candidate.md)
- **Track dirs:** `20-plan/sleep-staging/` (next), `30-implement/sleep-staging/` (later)

## Pain statement (one paragraph)

Sleep staging at clinical and consumer scale is rate-limited by inter-rater disagreement (κ ≈ 0.76 overall, N1 κ ≈ 0.24), automated-stager performance collapse on edge populations (Korkalainen 2020 OSA-severity degradation 84.5 % → 76.5 %; pediatric bias), AASM v3 hypopnea-rule disputes that change scoring outcomes, and consumer wearable misclassification (30–50 % of REM and deep sleep wrong on common devices). Sleep technologists spend ~70 minutes per PSG manually scoring at $23–72/hr; clinicians manage downstream confusion when wearable stage estimates disagree with PSG. Constituencies feel this in time, money, and clinical decision quality.

## Real-pain evidence (admission gate)

≥ 2 independent evidence classes per sub-pain, all confirmed by critic pass with two author-name fixes applied:

1. **Inter-rater ceiling.** Lee et al. 2022 meta-analysis — overall κ = 0.76; N1 κ = 0.24 (verified).
2. **Automated stager edge-case collapse.** Korkalainen 2020 — 84.5 % → 76.5 % accuracy as OSA severity increases (verified). Plus van Gorp 2023 + U-Sleep peds 2024 (pediatric bias).
3. **AASM v3 dispute.** Rosen & Auckley 2024 (JCSM commentary on hypopnea rule); Malhotra 2024 (PMC11063699, letter, separate paper); AASM v3 summary PDF.
4. **Wearable misclassification — multi-device PSG validation.** Chinoy et al., Sleep 2021 (PMC8120339) — most devices misclassify 30–50 % of REM and deep sleep (verified; previously misattributed to "Stone et al.", fixed 2026-05-02).
5. **Wearable misclassification — multicenter benchmark.** JMIR mHealth 2023 (PMC10654909) — best macro-F1 0.69, worst 0.26 across 349 k epochs (verified).
6. **Consumer device studies.** Chee et al., Sleep Med 2024 (Oura Gen3 + OSSA 2.0 multi-night); Oura systematic review 2025 (PMC12602993).
7. **Sleep-tech burden — timed observation.** Choo et al., Frontiers in Neurology 2023 (PMC9981786) — 4,243 s manual vs 42.7 s autoscore per PSG; 0.25 FTE savings at 750 patients/year (verified; previously misattributed to "Bakker et al.", fixed 2026-05-02).
8. **Sleep-tech burden — independent.** Holm et al., J Sleep Research 2026 (PMC12856104) — manual scoring "up to 2 h" per 8-h PSG; 14 % staging disagreement, 34.6 % respiratory-event disagreement, OSA severity differs in 66 % of cases by scorer (verified).
9. **Patient voice.** Baron 2017 case-series patient quotes (verified verbatim).
10. **Pediatric scoring difficulty.** Kevat / JCSM 2025 pediatric κ figures (verified).

Independence threshold (≥ 2 sources per sub-claim) comfortably exceeded across all 5 sub-pains.

## Constituency

Sleep technologists (paid $23–72/hr per BLS), pediatric / geriatric sleep researchers, sleep clinicians (AASM v3 cohort), wearable users + their downstream clinicians. **Reachable** via AASM Learning Center, AAST workforce surveys, Sleep-EDF / NSRR / Dreem-DOD dataset maintainers, paper-author emails.

## Critic pass

`real-pain-critic.md` — verdict `pass-with-fixes`. Two major (Stone→Chinoy and Bakker→Choo author-name corrections — both fixed in candidate file 2026-05-02; underlying data confirmed accurate). Two minor (Rosen & Auckley DOI 10.5664/jcsm.10944 not independently verifiable due to TLS error — sub-pain still supported by Malhotra; AAST 2023 workforce-survey full-data inaccessible — Choo/Holm timed observation independently meets threshold). Neither minor blocks admission.

## Advisory annotations (NOT gating — input to layer 20 / 30)

**From gap-closing pass (researcher a922da):**
- Dreem-DOD-H/-O access path documented; CC-BY-4.0 license, registration friction confirmed but ≤ 1 week.
- Sleep-tech workforce burden quantified primary-source (Choo 2023, Holm 2026, AAST attrition).
- Pediatric scoring difficulty quantified primary-source (Kevat 2025).
- Direct named-technologist interview NOT obtained — inferential evidence (paid training market) cited; close in track life if reviewer needs voice.

**From defensibility critic (a52506) — historical, advisory:**
- sleep-staging scope (a) clinical-population stratified eval of pretrained stagers: fragile-null on DUA-free data (Dreem-DOD-O n=55, 3–7× underpowered for OSA stratification). RECOVERY: NSRR DUA submitted day-one with 4-week kill criterion → defensible-null.
- sleep-staging scope (b) HRV-only EEG-less staging: defensible-null on HMC PSG (151 subjects) for ≥ 17 pp EEG-vs-HRV gap.

**From reuse sketch (methodologist a6dd95):**
- Promotion candidates: `30-implement/shared/data/cohort_stratifier.py` (per-cohort eval splits), `30-implement/shared/data/hrv_features.py` (HRV pipeline — UNIQUE to this track), `30-implement/shared/eval/calibration.py` (overlaps ecg-ppg-realworld). Plausible 2nd consumers = ecg-ppg-realworld + cross-subject-eeg (calibration + cohort stratifier).

## Open items to close in early track life

- Confirm Rosen & Auckley DOI 10.5664/jcsm.10944 (currently TLS-error-blocked)
- AAST 2023 workforce survey full data (currently 404 — qualify as institutional position statement)
- Direct named-technologist or named-clinician individual-voice quote on scoring burden
- NSRR DUA submission on day one of methodology — gates the OSA-stratified scope feasibility

## Human checkpoint

- [x] Lead reviewed critic verdict and evidence — 2026-05-02
- [ ] Human approval to instantiate `20-plan/sleep-staging/`

When human approves, instantiate `20-plan/sleep-staging/`, update `10-pain-point/shared/portfolio.md`, tag `v2-sleep-staging-admitted`.
