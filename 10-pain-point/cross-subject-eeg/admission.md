> **Spec:** `00-vision/README.md` (hard constraint #1: pain real and validated) + `10-pain-point/README.md` (validation rubric)

# Admission record — cross-subject-eeg

- **Date:** 2026-05-02
- **Slug:** `cross-subject-eeg`
- **Rubric version:** v2 (real-pain only at layer 10; feasibility / quality bar enforced at layers 20 / 30 / 40)
- **Verdict:** **admitted** (pass-with-fixes — citation fix applied)
- **Track dir:** `30-implement/cross-subject-eeg/`

## Pain statement (one paragraph)

EEG-based decoders for motor imagery, P300, SSVEP, affective state, and related paradigms generalize poorly across subjects. Practitioners pay a recurring 20–30-minute calibration tax per new user per session, and a non-trivial fraction of users (15–30 % "BCI illiterate") cannot be calibrated to acceptable accuracy at all. Recent self-supervised "foundation" models claim to narrow the gap, but independent benchmark and review work suggests the universality and robustness have not been convincingly demonstrated.

## Real-pain evidence (admission gate)

≥ 2 independent evidence classes confirmed by critic pass:

1. **BCI-illiteracy figures, peer-reviewed.** Saha & Baumert, *Frontiers in Computational Neuroscience* 2020 — "Around 15–30 % users are inherently unable…" (verbatim quote confirmed).
2. **Foundation-model critical review.** arXiv:2507.11783v3 — "the universality and robustness of EEG-FMs have not been convincingly demonstrated" (verified).
3. **Vendor admission of pain.** Neurable FAQ — three quoted statements about cross-user generalization friction (verified).
4. **Calibration-cost narrative, peer-reviewed.** Huang et al., *Frontiers in Neuroscience* 2021 (PMC8417074) — paraphrased on tedious per-subject calibration. 20–30-min figure is well-known across BCI reviews (Lotte 2018; BCI Competition IV-2a protocol) but was not pinned to a single citation in this pass; qualitative pain established.
5. **Practitioner-facing forum.** OpenBCI forum thread — practitioner-flagged calibration / impedance friction.
6. **Field-aggregator stance.** MOABB explicitly punts on cross-subject generalization in its scope.

## Constituency

BCI labs, EEG foundation-model authors, neurotechnology vendors (Neurable, Emotiv), the EEG Foundation Challenge 2025 community. **Reachable** via MOABB / braindecode / LaBraM GitHub repos, EEG Foundation Challenge contacts, OpenBCI forum, and direct paper-author emails.

## Critic pass

`admission/cross-subject-eeg.critic.md` — verdict `pass-with-fixes`. One major (citation attribution error in §3a — fixed in candidate file 2026-05-02). Two minor (OpenBCI thread description slightly over-stated — leave as-is, accurate directionally; r/BCI first-person practitioner quote gap — close in early track life).

## Advisory annotations (NOT gating — input to layer 20 / 30 / 40)

**From gap-closing pass (researcher a714e0):**
- EEG-FM-Bench (arXiv:2508.17742) delivers 0/5 of the candidate's §6 evaluation-diagnostic program. Ample headroom for the proposed work.
- NeurIPS 2025 EEG Foundation Challenge train/val data (HBN R1–11) freely accessible (CC-BY-SA-4.0, no DUA, NEMAR + AWS S3). Test set (R12) not yet released.
- HBN dataset = pediatric/adolescent (5–21) with psychopathology targets — not a drop-in for canonical motor-imagery benchmarks. Treat as complementary.

**From defensibility critic (a52506):**
- Verdict: **defensible-null**. All three plausible null scenarios (FM loses to Riemannian, overlap audit clean, illiteracy lower than prior) are informative.
- Condition: **pre-register** the five-part evaluation program in `20-plan/cross-subject-eeg/protocol-lock.md` before any headline experiment runs.

**From reuse sketch (methodologist a6dd95):**
- Highest-novelty shared artifact in the portfolio: `30-implement/shared/eval/leakage_audit.py` (pre-training overlap audit). Promotable independently of result direction.
- Other promotion candidates: `30-implement/shared/eval/fewshot_curve.py`, `30-implement/shared/eval/partition.py`, `30-implement/shared/models/riemannian_baseline.py`. Plausible 2nd consumers exist across affective-state, sleep-staging, ecg-ppg-realworld.

## Open items to close in early track life (not blocking)

- Direct first-person r/BCI / r/neurotechnology practitioner quote on calibration tax (carry-over from candidate §7).
- Pin the 20–30-min calibration figure to a specific protocol citation (Lotte 2018 review or BCI Competition IV-2a protocol).
- Read OpenBCI forum thread end-to-end to confirm specific friction modes (impedance vs hair vs electrode reliability).

## Human checkpoint

- [x] Lead reviewed critic verdict and evidence — 2026-05-02
- [ ] Human approval to instantiate `30-implement/cross-subject-eeg/`

When the human checkpoint completes, instantiate `20-plan/cross-subject-eeg/` (and later `30-implement/cross-subject-eeg/` once methodology pre-reg locks), update `10-pain-point/shared/portfolio.md`, tag `v2-cross-subject-eeg-admitted`.
