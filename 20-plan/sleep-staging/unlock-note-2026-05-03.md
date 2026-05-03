> **Spec:** `20-plan/sleep-staging/protocol-lock.md` (document being unlocked) + `10-pain-point/sleep-staging/admission.md` (original mandate)

# Protocol unlock note — sleep-staging — 2026-05-03

**Unlock date:** 2026-05-03
**Author:** methodologist agent (re-pass)
**Status:** UNLOCK — revisions in progress; re-lock follows in protocol-lock.md

---

## Why this unlock is triggered

Two independent triggers arrived simultaneously:

### Trigger 1 — HMC PSG credentialed access uncertain in timeline

The user reports that PhysioNet credentialed access to HMC Sleep Staging Database
may require a DUA-equivalent signup whose approval timeline is uncertain. Risk-register
R-2 was already present and named CAP Sleep as the pre-authorized substitute.

**What verification found:** Fetching https://physionet.org/content/hmc-sleep-staging/1.0.0/
directly returns "Anyone can access the files … Creative Commons Attribution 4.0
International Public License." HMC PSG is open access, not credentialed. The
original R-2 risk description was conservative. As of 2026-05-03 there is no DUA
or credentialed-sign-up barrier.

**Practical consequence:** HMC PSG remains the primary scope (b) dataset. However,
because the user has reported uncertainty from their own access attempt, the CAP Sleep
substitution path is fully evaluated here (rather than left as a one-line mention in
the risk register) so that the protocol is robust if access issues arise in practice.
CAP Sleep is promoted from "named fallback" to "fully specified substitute" in case
any local or institutional barrier materializes.

### Trigger 2 — NSRR API token obtained

The user has obtained an NSRR API token (stored in `.env` as `NSRR_TOKEN`, gitignored;
accessed in code via `os.environ['NSRR_TOKEN']`). Per NSRR's stated policy, the token
is issued only after DUA approval. Token in hand means the DUA has been approved.
SHHS and MESA are therefore immediately accessible.

**What this changes:** R-1 (NSRR DUA not received in 4 weeks) is resolved. The 4-week
kill criterion that made scope (a) conditional is gone. Scope (a) — clinical-population
stratified evaluation of pretrained stagers on NSRR SHHS/MESA — can begin immediately
in week 1. Scope (a) is elevated from "conditional stretch" to "co-primary headline."

---

## Summary of changes flowing from these triggers

| File | Change |
|---|---|
| `protocol-lock.md` | Held-out partition: scope (b) stays HMC PSG 77-subject split (unchanged). Scope (a) added as co-primary headline with MESA as primary NSRR dataset; SHHS as supplemental. NSRR token path documented. |
| `approach.md` | Scope (a) elevated to co-primary; NSRR access via token described; CAP Sleep fully specified as scope (b) substitute with label-format and pathology-mix caveats; power story updated for MESA 2056 subjects. |
| `risk-register.md` | R-1 marked RESOLVED (token obtained). R-2 updated: HMC access confirmed open, but substitute path fully specified for any residual barrier. New R-12 added for R&K-to-AASM label mapping if CAP substitute is activated. |
| `pilots-README.md` | P-1 description updated: primary target remains HMC PSG; if P-1 (a) fails, P-1b runs CAP Sleep access and label check instead. New P-7 added for NSRR token validation and MESA sample download. |

---

## What does NOT change

- Primary metric for scope (b): 3-class macro-F1 on the HMC PSG 77-subject held-out partition.
- Scope (b) model: Random Forest on 11 HRV features vs U-Sleep EEG baseline.
- Statistical test: paired Wilcoxon, one-sided.
- All four interpretation cases (A through D).
- Held-out split: HMC PSG, N=77 test subjects, stratified by AHI band, seed=42. (If CAP
  substitute is activated, the CAP partition definition replaces this — see approach.md.)
- Quality bar: bootstrap CI at subject level, held-out touched once.

---

## Critic re-pass requirement

These changes affect the held-out partition definition only conditionally (CAP substitute).
The primary scope (b) partition is unchanged. Scope (a) adds a new headline arm with its
own protocol-lock section. A full critic re-pass is required before any headline experiment
runs on scope (a). The scope (b) headline on HMC PSG may proceed under the original locked
protocol if HMC access is confirmed — no critic re-pass needed for scope (b) alone.
