# Selection shortlist (post-broad-survey)

Built 2026-05-02 by lead from `candidates/{cross-subject-eeg, ecg-ppg-realworld, sleep-staging, affective-state}.md`.

This document is **not** the selection. It is the shortlist + comparison the next phase debates.

## Convergent finding across candidates

Three of four candidates (cross-subject EEG, sleep staging, affective state) independently surfaced **evaluation hygiene** — leakage, cohort-disjoint splits, calibration metrics, abstention, per-subject distributions — as the contribution that fits a single-GPU lab and is currently under-tooled. The pattern is:

- A new SOTA contribution requires multi-GPU training and is contested by foundation-model races.
- An honest-evaluation / diagnostic contribution requires modest compute, is what the field is actively asking for, and matches the AHBU quality-bar mandate.

This shapes how each candidate is realistically scoped at our resources.

## Comparison

| Axis | cross-subject-eeg | ecg-ppg-realworld | sleep-staging | affective-state |
|---|---|---|---|---|
| Pain real (evidence strength) | High — 20–30 min calibration, 15–30 % BCI illiteracy, MOABB punts on cross-subject | High — FDA flag, BASEL 17–21 % inconclusive, JMIR skin-tone meta-analysis, CinC 2020 ~10 % drop | High — N1 κ=0.24 ceiling, 30–50 % wearable misclassification of REM/deep, AASM v3 ethics pain | Mixed — gap real (50–70 % LOSO), but partly field reckoning with oversell rather than starved external constituency |
| Named constituencies | BCI labs, sleep teams, Emotiv/Neurable, FM authors, EEG Foundation Challenge 2025 | Wearable users, GPs, cardiac techs, athletes, dark-skin users, ML researchers | Sleep techs ($23–72/hr), pediatric/geriatric researchers, sleep clinicians (AASM v3), wearable users | Affective-EEG academics, fleet-safety, anesthesiologists, neuroergo — strongest pain in clinical / safety, weakest in academic emotion |
| Feasibility @ GTX 1650 | Med — fine-tune existing FM checkpoints (LaBraM/EEGPT/BENDR), Riemannian baselines easy; no FM pretraining | High — PTB-XL public, classical ML on features, abstention work compute-light; PPG corpora available | Med — pretrained U-Sleep fine-tune feasible; HRV-only classical ML easy; **NSRR DUA admin lag (weeks)** for SHHS/MESA | High — DEAP/SEED/WESAD all small + open; classical ML + leakage diagnostics fit |
| Data access friction | Low (MOABB, BCI Comp IV, public FMs) | Low (PhysioNet PTB-XL, CinC challenges public) | **Medium-high** — Sleep-EDF free but narrow; SHHS/MESA require DUA; pediatric data harder | Low (DEAP/SEED on request, WESAD/MAHNOB public) |
| Quality-bar implication | Subject- + dataset- + hardware-disjoint splits; 0/1/5/20-shot curves; per-subject distributions | Patient- + site-disjoint; calibration (Brier, ECE, PPV@alert-rate); skin-tone stratification; abstention | Subject- + cohort-disjoint; per-stage F1 + confusion; AHI/age stratification; reliability diagrams; multi-rater consensus targets | Subject-disjoint headline; trial-level leakage check; calibration-curve vs N calibration examples; trivial-baseline ablation |
| Risk of redundancy | Crowded (FM space) — but evaluation diagnostic angle still open | Modest — calibration + skin-tone disparity work less crowded; abstention angle distinctive | Med — well-trodden field; clinical-population stratification + uncertainty less so | **High** — Brookshire 2024 + Apicella 2024 already named the leakage gap; further leakage-only contribution may be incremental |
| Distinctive contribution available at our scale | Cross-paradigm cross-subject diagnostic on MOABB + foundation-model probe under leakage-clean splits | Calibrated abstention for AFib alerts on PTB-XL + cross-cohort eval; skin-tone where labels exist | Pretrained-stager calibration + cohort-stratified eval on a clinical population; OR HRV-only EEG-less staging | Honest evaluation framework + arousal-only reframing (per Barrett); risk: low novelty |
| Time-to-first-honest-result | 4–8 weeks | 3–6 weeks | 4–10 weeks (DUA-dependent) | 3–6 weeks |
| Verification gaps flagged by researcher | r/BCI direct quote not found; arXiv:2602.01019 venue unverified | Reddit threads couldn't access; clinician-burden quantification missing; NeuroKit2 issues unread | Pediatric primary-source clinician interviews missing; consumer-pain-vs-vendor-claim disambiguation | Need ≥1 named practitioner who would adopt better evaluation |

## Cross-cutting observation

**EEG cross-subject generalization** and **affective-state inference** share the same root pain (subject transfer + leakage). They differ on whether the labels are clinically grounded (sleep stages, motor imagery class) vs construct-contested (discrete emotions). For the AHBU quality bar, label-grounded variants are stronger.

## Recommendation for selection debate

Top two for selection-phase scrutiny:

1. **`ecg-ppg-realworld`, narrowed.** Strongest external constituency (clinicians + consumers) with a quantified deployment cost, lowest data-access friction, and a distinctive contribution angle (calibrated abstention + stratified eval) that fits compute. Risk: pain is broad, must narrow before methodology — likely to **AFib alert PPV / abstention on PTB-XL + a PPG corpus** OR **skin-tone-stratified PPG eval** specifically.
2. **`sleep-staging`, narrowed.** Strong constituency (sleep techs, pediatric/geriatric clinicians), label is clinically grounded, well-instrumented field with N1 / clinical-degradation gaps the field has already named. Risk: NSRR DUA admin lag; mitigation = start with Sleep-EDF + Dreem-DOD + HMC PSG (no DUA) and pursue SHHS/MESA in parallel.

`cross-subject-eeg` deferred: feasible but most crowded; unique angle is "evaluation diagnostic on foundation models" which is valuable but narrow and already partly addressed by EEG-FM-Bench (arXiv:2508.17742).

`affective-state` deferred: redundancy risk is real (Brookshire 2024 + Apicella 2024) and construct validity (Barrett) makes any positive claim fragile.

Selection debate must:

- Ask each top candidate: what would this look like as a **2-page approach.md** that the methodologist could lock?
- Run **critic pass** against shortlist before committing.
- Verify the constituency is **reachable for feedback** (not just citable).
- Check the chosen scope is **defensible if results are negative** — a negative skin-tone-disparity result, or a negative abstention-improvement result, still has to be a valuable contribution.

## What this shortlist deliberately does not yet do

- Pick. Selection is a separate step (`selection.md`) gated by critic pass + human checkpoint.
- Resolve verification gaps. Each candidate has open items; selection-phase deep-dive should close gaps for the top 1–2 only, not all four.
- Commit to a methodology. That's layer 20.
