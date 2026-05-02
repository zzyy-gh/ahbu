# Portfolio registry

The active state of the AHBU pain-point portfolio. Each candidate has a status; transitions are dated and reasoned.

**Status values:** `candidate` (under investigation) · `admitted` (track active) · `deferred` (failed admission gate, conditions for re-eval listed) · `retired` (track completed).

## Active

| Slug | Status | Track dir | Admitted | Notes |
|------|--------|-----------|----------|-------|
| `cross-subject-eeg` | admitted | `30-implement/cross-subject-eeg/` | 2026-05-02 | First admission under v2 rubric. Critic `pass-with-fixes` (citation fix applied). Pre-reg required at layer-20 protocol-lock. |

## Candidates under investigation

| Slug | Status | Date | Real-pain critic verdict | Notes (advisory, not gating) |
|------|--------|------|--------------------------|------------------------------|
| `ecg-ppg-realworld` | candidate | 2026-05-02 | pending — real-pain evidence strong (FDA flag, JAHA 2024 clinician burden, JMIR meta-analysis) | Layer-20 input: skin-tone-stratified scope blocked at Fitzpatrick granularity (BUT-PPG n=48, MIMIC-PERform-Ethnicity binary B/W n=100/group only); abstention scope still feasible if narrowed to PTB-XL + PPV-at-fixed-alert-rate or single-lead conformal. |
| `sleep-staging` | candidate | 2026-05-02 | pending — real-pain evidence strong (sleep-tech burden, AASM v3, wearable misclassification) | Layer-20 input: OSA-stratified scope underpowered on DUA-free data (Dreem-DOD-O n=55); recoverable via NSRR DUA submitted day-one with 4-wk kill criterion. HRV-only scope independently feasible. |
| `affective-state` | candidate | 2026-05-02 | pending — real-pain mixed (academic emotion contested, safety/clinical angle stronger) | Layer-20 input: feature-stability sub-scope (2/164 reproducibility per arXiv:2508.10561) is the strongest framing; pre-reg feature list + dataset + arousal operationalization. |

## Deferred

_None yet — admission decisions still pending first round._

## Retired

_None yet._

---

## How to update

- New candidate: add row to "Candidates under investigation" + drop a `10-pain-point/<slug>/candidate.md` file.
- Admission: move row to "Active", write `<slug>/admission.md` + `<slug>/real-pain-critic.md`, instantiate `20-plan/<slug>/`, append to `validation-log.md`.
- Deferral: move row to "Deferred", record reason + re-eval conditions.
- Retirement: move row to "Retired" once `20-plan/<slug>/lessons.md` is signed off; surface lessons to the appropriate layer's `shared/` or to `lessons.md`.
