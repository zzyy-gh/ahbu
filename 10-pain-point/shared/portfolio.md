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
| `affective-state` | admitted | `20-plan/affective-state/` (pending) | 2026-05-02 | Critic `pass-with-fixes` (DEAP-label inversion + WESAD figures fixed). Operative constituency = academic EEG / wearable-stress communities. Layer-20 advisory: feature-stability audit sub-scope (2/164 reproducibility per arXiv:2508.10561) is the strongest framing; pre-reg feature list + dataset + arousal operationalization. |

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
