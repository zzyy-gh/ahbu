> **Historical note (post-rubric-loosening, 2026-05-02):** Written under v1 rubric. Recommendations to defer based on feasibility / scope / redundancy are no longer blocking — admission gates on real-pain only. Use the comparison + reasoning here as advisory input to layer 20 methodology, not as portfolio-admission decisions.

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

## Recommendation for portfolio admission debate

Project model: portfolio. Each candidate that passes the admission gate (real · feasible · honest evaluation, plus reuse expectations) enters the portfolio as its own track. Sequencing — which is admitted first, which run in parallel — is a downstream operational call, not a selection.

Initial admission ordering, ranked by gap-closing cost + reuse leverage:

1. **`ecg-ppg-realworld`, narrowed.** Strongest external constituency (clinicians + consumers) with quantified deployment cost, lowest data-access friction. Distinctive contribution angle (calibrated abstention + stratified eval) fits compute. Reuse leverage: abstention/calibration utilities promote naturally to `30-implement/shared/eval/`. Risk: pain is broad, must narrow before methodology — likely **AFib alert PPV / abstention on PTB-XL + a PPG corpus** OR **skin-tone-stratified PPG eval** specifically. Critic flagged: skin-tone framing feasibility-blocked unless operative dataset has Fitzpatrick-or-equivalent labels.
2. **`sleep-staging`, narrowed.** Strong constituency (sleep techs, pediatric/geriatric clinicians), clinically-grounded labels, well-instrumented field. Reuse leverage: cohort-stratified eval + uncertainty wrappers promote to `30-implement/shared/eval/`; HRV-only EEG-less staging shares feature/loader code with cardiac tracks. Risk: NSRR DUA admin lag; mitigation = start with Sleep-EDF + Dreem-DOD + HMC PSG (no DUA, modulo Dreem registration friction) and pursue SHHS/MESA in parallel.
3. **`cross-subject-eeg`, undeferred per critic.** Critic showed deferral was premature — candidate's §6 evaluation-diagnostic program (subject + dataset + hardware-disjoint splits, 0/1/5/20-shot curves, pre-training-overlap audit) is not what EEG-FM-Bench delivered. Reuse leverage: leakage-clean splits + few-shot calibration curves promote to `30-implement/shared/eval/` and are likely the highest cross-track payoff of any candidate.
4. **`affective-state`, sub-scope only.** Discrete-emotion classification is construct-contested (Barrett) and redundant on leakage-only framings. The 2/164 feature-reproducibility finding (arXiv:2508.10561) supports a **feature-stability audit** sub-scope that is *not* redundant with Brookshire/Apicella. Admit only if scoped this way; otherwise defer.

Each ranked candidate must independently pass the admission gate. Ranking is preference, not entitlement.

## Admission debate must (per candidate)

- Sketch what `20-plan/<slug>/approach.md` would say as a 2-page draft, including the **Shared substrate** section (what consumes from / promotes to `shared/`).
- Run a critic pass on the candidate's admission against the layer-10 rubric.
- Verify constituency is **reachable for feedback** (not just citable). Log at least one outreach attempt.
- Show the scope is **defensible if results are negative** — a null skin-tone disparity, a null abstention improvement, a null feature-reproducibility finding all need to be valid contributions.

## What this shortlist deliberately does not do

- Admit. Admission is a separate step per candidate (`admission/<slug>.md`) gated by critic-pass + human checkpoint.
- Pick a single winner. Portfolio model — multiple admissions are expected.
- Resolve verification gaps for all four. Gap-closing is per-candidate at admission time.
- Commit to a methodology. That's the track's `20-plan/cross-subject-eeg/` layer.
