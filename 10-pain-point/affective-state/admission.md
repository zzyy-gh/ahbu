> **Spec:** `00-vision/README.md` (hard constraint #1: pain real and validated) + `10-pain-point/README.md` (validation rubric)

# Admission record — affective-state

- **Date:** 2026-05-02
- **Slug:** `affective-state`
- **Rubric version:** v2 (real-pain only at layer 10; feasibility / quality bar enforced at layers 20 / 30)
- **Verdict:** **admitted** (pass-with-fixes — DEAP-label inversion + WESAD-figure misattribution fixed in candidate.md)
- **Track dirs:** `20-plan/affective-state/` (next), `30-implement/affective-state/` (later)

## Pain statement (one paragraph)

Models that infer affective or mental states (emotion category, valence/arousal, stress, drowsiness, cognitive load, pain) from physiological signals (EEG, ECG/HRV, EDA, fNIRS, fusion) routinely report 80–98 % accuracy on public benchmarks (DEAP, SEED, WESAD) but fail to generalize to new subjects, new sessions, new contexts, and new labs. Reported numbers are inflated by trial-level and subject-level data leakage, by within-subject evaluation that masks the hard problem, and by features whose reproducibility across datasets is near-zero (2 of 164 cardiac + EDA features replicate). Downstream constituencies that try to deploy these models in field conditions either get unusable results or build elaborate per-subject calibration pipelines that defeat the purpose; in some application classes (workplace / education emotion AI), the EU regulator has explicitly banned deployment.

## Real-pain evidence (admission gate)

≥ 4 independent evidence classes (well above the 2-source threshold) confirmed by critic pass:

1. **Cross-subject generalization gap — systematic review.** Apicella et al., Neurocomputing 2024 (arXiv:2212.08744) — 50–70 % LOSO ceiling on emotion classification (verified).
2. **Leakage-inflated published numbers.** Brookshire et al., Frontiers in Neuroscience 2024 (PMC11099244) — only 27 % of reviewed DNN-EEG studies used proper subject-based holdout; "most published DNN-EEG studies may dramatically overestimate" (verified).
3. **Feature stability near-zero.** arXiv:2508.10561 — 2 electrodermal-derived features out of 164 cardiac + EDA features showed reproducible association with arousal (verified).
4. **Clinical-deployment evidence — anesthesia.** Ledowski 2019 BJA (PMC6676047) — verbatim quote on no firm evidence for clinically relevant influence of nociception monitors (verified).
5. **Regulatory evidence.** EU AI Act Article 5(1)(f) — workplace / education emotion-AI prohibited, in-force 2 February 2025 (verified).
6. **Construct validity.** Lindquist & Barrett 2012 BBS meta-analysis (consistent with known literature; full-text 403, attribution verified).
7. **Person-specific vs generic gap (wearable stress).** Schmidt 2018 baseline 93.1 % LDA + Li 2024 (via PMC12685819) ~95 % person-specific vs ~67 % generic — verified after WESAD figure fix.

Independence threshold (≥ 2) comfortably exceeded.

## Constituency

**Operative constituency at admission:** academic EEG/affective-computing community (DEAP / SEED / MAHNOB-HCI users) + wearable stress-detection vendors and quantified-self users (WESAD follow-ups). Both are clearly reachable: GitHub for affective benchmarks, paper-author emails, MOABB community.

**Adjacent (harder to reach, not the operative scope):** clinical anesthesia (Ledowski/Hajat/Shanker BJA cohort), fleet-safety operators, regulatory bodies (EU AI Office). These are valid pain-bearers but layer 20 should not commit to serving them at this scale.

## Critic pass

`real-pain-critic.md` — verdict `pass-with-fixes`. One critical (DEAP labels mischaracterized as stimulus-class — fixed in candidate file 2026-05-02). One major (WESAD 98.9/83.9 figures unverified in cited source — replaced with Li 2024 ~95/67 figures via PMC12685819). Four minor (2 EDA precision, operative constituency, three paywall-blocked sources) — all addressed in admission record (operative constituency named) or carried into track life.

## Advisory annotations (NOT gating — input to layer 20 / 30)

**From historical critic-shortlist (v1 rubric):**
- Shortlist deferred this candidate on "redundancy" grounds (Brookshire 2024 + Apicella 2024 already named the leakage gap). v1 critic disputed: feature-reproducibility angle (2/164) is non-redundant.
- The strongest framing for layer 20 is the **feature-stability audit sub-scope** per arXiv:2508.10561.

**From defensibility critic (v1, advisory):**
- affective-state feature-stability audit: defensible-null. Binomial test at N=164 well-powered (P(X≤2 | p=0.05) = 0.01).
- Pre-reg required: feature list, dataset selection, arousal operationalization — all locked before headline runs.

**From reuse sketch (methodologist a6dd95):**
- Promotion candidate: `30-implement/shared/eval/feature_stability.py` (UNIQUE to this track among the four). Plausible 2nd consumer = ecg-ppg-realworld + sleep-staging if they adopt a pre-model feature-audit discipline.
- Note: leverage rating MEDIUM (lower than the other three) because consumers must opt into a feature-audit-first methodology, not inherent to their own scope.

## Open items to close in early track life

- 98.9 / 83.9 WESAD figures: trace original source (Schmidt 2018 PDF or arXiv:2203.09663) or accept the Li 2024 reframe permanently
- Verify Lindquist & Barrett 2012 BBS quote when paywall accessible
- Verify Shanker BJA 2023 specifics
- CEUR-WS Vol-4115 paper7 trial-level leakage findings (binary PDF blocked)
- Consider whether to acquire a clinical-anesthesia outreach attempt (currently the candidate's strongest pain-bearer is named but not directly engaged)

## Human checkpoint

- [x] Lead reviewed critic verdict and evidence — 2026-05-02
- [ ] Human approval to instantiate `20-plan/affective-state/`

When human approves, instantiate `20-plan/affective-state/`, update `10-pain-point/shared/portfolio.md`, tag `v2-affective-state-admitted`.
