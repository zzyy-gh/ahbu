# Portfolio registry

The active state of the AHBU pain-point portfolio. Each candidate has a status; transitions are dated and reasoned.

**Status values:** `candidate` (under investigation) · `admitted` (track active) · `deferred` (failed admission gate, conditions for re-eval listed) · `retired` (track completed).

## Active

| Slug | Status | Track dir | Admitted | Layer-20 status | Layer-30 status | Notes |
|------|--------|-----------|----------|-----------------|-----------------|-------|
| `cross-subject-eeg` | admitted | `30-implement/cross-subject-eeg/` | 2026-05-02 | protocol-lock v2 (2026-05-03), critic-v2 pass-with-fixes applied | pilots P-1..P-6 + leakage_audit done | HYBRID: MDM on PhysionetMI + LaBraM on Cho2017 after PhysionetMI contamination found. Headline not yet run. |
| `affective-state` | admitted | `30-implement/affective-state/` | 2026-05-02 | protocol-lock v2 (2026-05-03), critic-v2 pass-with-fixes applied | pilots P-1, P-2, P-3 (WESAD only), P-6 done | Path X: EDA expanded 6→40 features; N_total=126 (exact-binom power 0.04594). DEAP/MAHNOB-HCI access pending. Headline not yet run. |
| `ecg-ppg-realworld` | admitted | `30-implement/ecg-ppg-realworld/` | 2026-05-02 | protocol-lock v2 (2026-05-03), critic-v2 pass-with-fixes applied | CinC 2017 P-1, P-2, P-3, P-4 PASS; P-6 PASS; P-5 informative-fail (T~1.03 → no overconf to scale; re-run on 50-ep headline) | Path C: pivoted PTB-XL → CinC 2017. All pilots done; ready for headline. Headline not yet run. |
| `sleep-staging` | admitted | `30-implement/sleep-staging/` | 2026-05-02 | protocol-lock v2 (2026-05-03), critic-v2 pass-with-fixes applied; **R-1 RE-OPENED 2026-05-03 PM** | P-7 FAIL: MESA DAR not approved (token tier insufficient); HMC bulk DL in progress | **R-1 re-opened.** Pivot to HEADLINE-B (HMC PSG, CC-BY) first; DAR submitted in parallel; if not approved by 2026-05-31, demote HEADLINE-A. P-1/P-3 next. |

## Candidates under investigation

_None — all 4 candidates admitted as of 2026-05-02._

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
