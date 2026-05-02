# Portfolio registry

The active state of the AHBU pain-point portfolio. Each candidate has a status; transitions are dated and reasoned.

**Status values:** `candidate` (under investigation) · `admitted` (track active) · `deferred` (failed admission gate, conditions for re-eval listed) · `retired` (track completed).

## Active

| Slug | Status | Track dir | Admitted | Notes |
|------|--------|-----------|----------|-------|
| _none yet_ | | | | |

## Candidates under investigation

| Slug | Status | Date | Critic verdict | Open issues |
|------|--------|------|----------------|-------------|
| `cross-subject-eeg` | candidate | 2026-05-02 | pending (critic-shortlist found premature deferral) | candidate's §6 evaluation-diagnostic program not yet checked against EEG-FM-Bench scope |
| `ecg-ppg-realworld` | candidate | 2026-05-02 | shortlist promotes; critic flags skin-tone feasibility + abstention novelty unchecked | scope narrowing required (AFib abstention vs skin-tone), constituency outreach not yet attempted |
| `sleep-staging` | candidate | 2026-05-02 | shortlist promotes; critic flags Dreem-DOD registration friction + clinician interviews missing | scope narrowing (clinical-population eval vs HRV-only EEG-less staging), DUA timeline for SHHS/MESA |
| `affective-state` | candidate | 2026-05-02 | shortlist defers on redundancy; critic disputes — feature-reproducibility angle (2/164) is not redundant | scope = "honest evaluation tooling" or "arousal-only reframing"; construct-validity risk acknowledged |

## Deferred

_None yet — admission decisions still pending first round._

## Retired

_None yet._

---

## How to update

- New candidate: add row to "Candidates under investigation" + drop a `candidates/<slug>.md` file.
- Admission: move row to "Active", write `admission/<slug>.md` (critic notes + human approval), instantiate `tracks/<slug>/` from `tracks/_template/`, append to `validation-log.md`.
- Deferral: move row to "Deferred", record reason + re-eval conditions.
- Retirement: move row to "Retired" once track's `40-analysis/` is signed off; surface lessons to `shared/` or `tracks/<slug>/lessons.md`.
