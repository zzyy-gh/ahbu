> **Spec:** `10-pain-point/cross-subject-eeg/admission.md`

# Protocol lock — cross-subject-eeg

**Track:** cross-subject-eeg
**Originally locked:** 2026-05-02
**Re-locked:** 2026-05-03
**Re-locked by:** methodologist agent (leakage_audit re-pass)
**Status:** LOCKED (v2) — revised pre-registration; held-out split not yet touched

Unlock note: `20-plan/cross-subject-eeg/unlock-note-2026-05-03.md`

This document defines the frozen evaluation protocol for the headline
experiment. It is locked before any experiment code is run against the
held-out test splits. Changes require an explicit unlock note with a
documented reason and a new critic pass before re-locking.

---

## 0. Pre-registration statement

This protocol is written and committed before any headline experiment
is run. The held-out test partitions defined in §3 have not been
examined, summarized, or used for any model selection decision as of
the re-lock date 2026-05-03. The dev split may be used freely for
pilots, ablations, and preliminary analysis; the test splits may each
be accessed exactly once, for the single authorized evaluation run
described in §6.

This pre-registration satisfies the condition imposed by the
defensibility-critic advisory (10-pain-point/critic-defensibility.md
§5) and the admission record advisory annotation.

**Change from v1 (2026-05-02):** PhysionetMI was confirmed in
LaBraM's pre-training corpus (arXiv:2405.18765 §3.1; see
`unlock-note-2026-05-03.md` §2 for full corpus map). Per the
pre-registered substitution procedure (risk-register R-2 + prior
protocol §4 step 5), the FM arm test dataset is substituted to
Cho2017. PhysionetMI is retained as the Riemannian/classical arm
test dataset. The asymmetry is documented and reported as a headline
audit finding, not buried.

---

## 1. The five-part evaluation program (pre-registered)

The headline experiment delivers exactly these five contributions.
If any component cannot be delivered, the specific component is marked
"not delivered" in results.md with a documented reason.

**(a) Subject + dataset + hardware-disjoint splits simultaneously.**
Train and dev data comes from different datasets, different subject
pools, and different recording hardware than each held-out test set.
Specific splits defined in §3, per arm.

**(b) 0/1/5/20-shot calibration curves per subject.**
For each model, at each shot level k ∈ {0, 1, 5, 20}, report:
mean accuracy across subjects, 95 % bootstrap CI, and the full
per-subject distribution. Shot examples drawn by 50 independent
random draws per (subject, k); mean and CI reported across draws.

**(c) Per-subject performance distributions.**
For each model × shot level, report the full distribution of
per-subject accuracy (not mean alone). Report TWO illiteracy
fractions side-by-side:
- **At-or-below chance** (25 % for 4-class, 50 % for 2-class) — the
  truly-no-signal subjects.
- **At-or-below 70 % usability threshold** (Saha & Baumert 2020 /
  BCI-IV-2a convention) — the subjects who would not derive practical
  value from a deployed BCI at this calibration scope.
The 70 % figure is directly comparable to the cited 15–30 %
illiteracy literature; the 25 % figure is the formal chance baseline.
The illiteracy characterization is a primary output, not supplementary.

**(d) Pre-training-overlap audit.**
Run before touching any test split. Audit result is documented in
`unlock-note-2026-05-03.md` §2 (completed prior to re-lock):
- PhysionetMI: CONTAMINATED (in LaBraM corpus as "EEG Motor
  Movement/Imagery Dataset"). FM arm may NOT use PhysionetMI.
- Cho2017: CLEAN (not in corpus). FM arm test set.
- Lee2019: CLEAN (not in corpus). Dev dataset.
The audit result is reported in the headline results table regardless
of direction. The contamination finding is itself a contribution.

**Ablation-2 elevation:** The LaBraM pre-training corpus includes
BCICIV_2a (BNCI2014_001) and BCICIV_2b — both dev-set datasets in
this protocol. Ablation 2 (overlap-removed FM) is therefore expected
to trigger on the dev set. When triggered, the overlap-removed FM
result is elevated to a required headline component and reported in
the main results table alongside the pre-training-overlap audit, not
relegated to ablation appendix.

**(e) Riemannian + classical-ML baselines under the same splits.**
Riemannian MDM and FBCSP + LDA are evaluated under identical
split conditions as each arm. No baseline-favorable adjustments to
the split or preprocessing are permitted after this lock.

---

## 2. FM checkpoints evaluated (pre-registered)

**Primary FM:** LaBraM-Base (arXiv:2405.18765, ICLR 2024 spotlight).
Checkpoint: the official release at https://github.com/935963004/LaBraM.
Usage: frozen encoder, linear head (logistic regression) fitted on
k-shot support examples per target subject.

Pre-training corpus (per arXiv:2405.18765 §3.1, reproduced in
`unlock-note-2026-05-03.md` §2): includes PhysionetMI ("EEG Motor
Movement/Imagery Dataset"), BCICIV_2a, BCICIV_2b, SEED series,
TUAB/TUEV/TUSZ, and others. Does NOT include Cho2017 or Lee2019.

If LaBraM-Base is unavailable (risk-register R-1), the fallback FM is
BENDR (https://github.com/SPOClab-ca/BENDR). The fallback must
be documented as a pre-experiment substitution in results.md before
any test split is touched. The leakage audit must be run for the
fallback FM's corpus against Cho2017 before the fallback is confirmed.

No other FM checkpoints are evaluated in the headline. Additional FM
probes (BENDR, BIOT) are pilot/exploratory only and do not contribute
to the headline metric.

---

## 3. Held-out partition definition (FROZEN)

This protocol uses a **split-arm design** as a consequence of the
pre-training-overlap audit. The Riemannian/classical arm and the FM
arm use different test sets. The asymmetry is explicitly reported.

### MOABB Riemannian/classical arm

**Test dataset:** PhysionetMI (GigaDB / PhysioNet, 109 subjects,
4-class MI, CC0 license, available via MOABB as `PhysionetMI`).
No pre-training contamination concern (MDM and FBCSP+LDA have no
pre-training corpus). This is the primary large-N test set for
per-subject distribution analysis and illiteracy-rate characterization.

**Scope:** MDM (Riemannian baseline) and FBCSP+LDA are evaluated on
PhysionetMI. LaBraM is NOT evaluated on PhysionetMI (contamination).

### MOABB FM arm

**Test dataset:** Cho2017 (52 subjects, 2-class MI, 64-channel
Biosemi ActiveTwo, available via MOABB as `Cho2017`).
Confirmed clean per the pre-training-overlap audit documented in
`unlock-note-2026-05-03.md` §2.

**Scope:** LaBraM-Base frozen encoder + linear head is evaluated on
Cho2017. MDM and FBCSP+LDA are also evaluated on Cho2017 to provide
a within-dataset baseline for the FM-vs-Riemannian comparison.

**Note on 2-class vs 4-class:** Cho2017 is 2-class MI (left hand vs
right hand), while PhysionetMI is 4-class. The primary metric is
LOSO accuracy; chance is 50 % for Cho2017. The illiteracy threshold
(70 % usability, chance 50 %) is applied accordingly. Cross-arm
comparisons of absolute accuracy are NOT made; each arm is interpreted
on its own test set.

### MOABB dev datasets (FROZEN)

**Primary dev:** BNCI2014_001 (BCI Competition IV-2a, 9 subjects,
4-class MI).
**Secondary dev:** Lee2019 (54 subjects, 2-class MI). Selection
previously deferred to week 1 is now frozen as Lee2019.

Rationale: Cho2017 is now the FM arm test set and may not be used
for dev. Lee2019 is clean per the corpus audit and provides a
reasonable secondary dev pool with a similar 2-class structure to
Cho2017 (reduces confounding from paradigm mismatch at dev time).

Both BNCI2014_001 and Lee2019 are in (or similar to) the LaBraM
pre-training corpus (BNCI2014_001 = BCICIV_2a, confirmed in corpus).
Lee2019 is NOT confirmed in corpus. Ablation 2 (overlap-removed FM)
is expected to trigger on BNCI2014_001-based dev results.

**Hardware-disjoint (dev vs test):**

Riemannian arm: BNCI2014_001 (g.USBamp, 22-channel) vs PhysionetMI
(BCI2000, 64-channel) — different hardware manufacturers, hardware-
disjoint criterion satisfied. Verified.

FM arm: Lee2019 hardware is BrainProducts BrainAmp (32-channel); Cho2017
hardware is Biosemi ActiveTwo (64-channel) — different amplifier
systems, hardware-disjoint criterion satisfied for this pair. If
precise hardware specs are not confirmed by week 1, the claim is
narrowed to "different labs, different amplifier vendors" per MOABB
dataset documentation; this is documented at dev-dataset selection
time in `30-implement/cross-subject-eeg/runs/dev_dataset_selection.txt`.

### Subject-disjoint verification

`partition.py:validate_partition()` is run on (dev_subject_ids,
test_subject_ids) for each arm before the headline run.
Pass/fail logged in `30-implement/cross-subject-eeg/runs/partition_audit.txt`.

### HBN arm (complementary cross-task FM probe)

**Test subjects:** HBN Releases 9–11 (approximately 300 subjects,
ages 5–21, 128-channel EEG, 6 tasks).

**Dev subjects:** HBN Releases 1–8 (approximately 2,300 subjects).

**Subject-disjoint:** HBN releases are distinct cohort sweeps;
no subject appears in more than one release per the HBN data
documentation. Verified programmatically by subject-ID uniqueness
check at preprocessing time.

**Note on HBN arm scope:** The HBN arm evaluates cross-task
generalization of the FM, not cross-subject MI decoding. It is
a secondary analysis. If the HBN arm cannot be run (risk-register
R-6), the headline remains MOABB-only and the HBN arm is dropped.

### What counts as "touching the held-out split"

The held-out split is touched when any of the following occurs:
- Test-set raw data is loaded into memory.
- Test-set features or predictions are computed.
- Test-set results are read, even for debugging.

Checking that test-set files exist on disk (e.g., `os.path.exists`)
does not count as touching.

The single authorized evaluation run for each arm must be preceded by:
1. A written confirmation in
   `30-implement/cross-subject-eeg/runs/pre-run-checklist.txt` that all
   model selection decisions have been made on the dev split.
2. The leakage audit result (§4) confirmed as logged in the unlock
   note.
3. `partition.py:validate_partition()` passing for each arm.

---

## 4. Pre-training-overlap audit status (COMPLETED)

The audit was run as part of the leakage_audit pilot and confirmed
prior to this re-lock. Full findings in `unlock-note-2026-05-03.md` §2.

**Summary of audit results:**

| Dataset | FM arm role | Audit result |
|---|---|---|
| PhysionetMI | PREVIOUS test (v1) | CONTAMINATED — in LaBraM corpus |
| Cho2017 | FM arm test (v2) | CLEAN — not in LaBraM corpus |
| Lee2019 | Secondary dev (v2) | CLEAN — not in LaBraM corpus |
| BNCI2014_001 | Primary dev | CONTAMINATED (BCICIV_2a) — dev only; triggers Ablation 2 |
| HBN Releases 9–11 | HBN arm test | Not explicitly in corpus; no HBN-specific entry found in LaBraM corpus list |

The audit is complete. Steps 1–4 of the original §4 procedure have
been executed. The substitution (step 5) has been executed via this
unlock. Step 6 (FM arm cancellation) does not apply — Cho2017 is
available and clean.

---

## 5. Primary metric (pre-registered)

**Primary metrics (one per arm, reported separately):**

**Riemannian arm primary metric:** Mean LOSO accuracy on
PhysionetMI, macro-averaged across subjects, at each shot level
k ∈ {0, 1, 5, 20}, with 95 % bootstrap CI (n=2000 resamples,
stratified by subject, random_state=42).
Unit: percentage points (0–100). Reported as "XX.X % (95 % CI:
YY.Y–ZZ.Z %, N=N_subjects)".

**FM arm primary metric:** Mean LOSO accuracy on Cho2017,
macro-averaged across subjects, at each shot level k ∈ {0, 1, 5, 20},
with 95 % bootstrap CI (n=2000 resamples, stratified by subject,
random_state=42). FM (LaBraM-Base) vs MDM (Riemannian) comparison
on Cho2017.

The per-shot-level accuracy values are four numbers per arm per model,
not one. The headline FM-vs-MDM comparison is the delta at k=20 AND
at k=0 on Cho2017. Both directions matter; neither is cherry-picked.

**Secondary metrics** (reported, not primary):
- Per-subject accuracy distribution (violin plots + illiteracy-rate
  fraction below threshold), per arm.
- FM minus MDM delta at each shot level with CI (Cho2017 arm).
- Leakage audit result (structured report including PhysionetMI
  contamination finding).
- Per-class accuracy for 4-class PhysionetMI (Riemannian arm).
- FBCSP + LDA accuracy at each shot level (lower-bound baseline).

**Reporting note:** Because PhysionetMI and Cho2017 use different
numbers of classes (4 vs 2), cross-arm accuracy comparisons are NOT
made. Each arm's accuracy is interpreted relative to its own
chance level.

---

## 6. Statistical test for FM-vs-Riemannian comparison (pre-registered)

Applied to the FM arm (Cho2017) only, where both FM and MDM are
evaluated on the same test set.

**Test:** Paired Wilcoxon signed-rank test, one-sided
(H1: FM accuracy > MDM accuracy, per subject, at each shot level).

**Correction:** Bonferroni across four shot levels (k = 0, 1, 5, 20);
adjusted significance threshold p < 0.0125.

**Effect size:** Cohen's d (paired, per shot level).

**Interpretation rule:**
- p < 0.0125 AND d >= 0.2: "statistically significant and practically
  meaningful improvement of FM over MDM on Cho2017."
- p < 0.0125 AND d < 0.2: "statistically significant but practically
  small improvement."
- p >= 0.0125: "no statistically significant improvement of FM over
  MDM at this shot level on Cho2017."

All four shot levels are reported. Cherry-picking a single shot level
post-hoc is a protocol violation.

---

## 7. Decision rule: what counts as the headline result (pre-registered)

The headline result is the full set of five-part evaluation outputs
on the held-out test splits, evaluated exactly once per arm. It is
"real" if:

- The pre-run checklist (§3) is complete and logged.
- The leakage audit result is documented in the unlock note prior to
  any test-split access.
- `validate_partition()` passed for each arm (§3).
- Neither arm's evaluation was re-run after seeing the results.

**What counts as null (FM arm):** The primary metric is null if the
Wilcoxon signed-rank test fails to reject H0 at the corrected
threshold (p >= 0.0125) at k=20 on Cho2017. A null at k=20 but a
positive result at k=5 is a partial positive, reported as such.

**What counts as positive (FM arm):** FM accuracy is statistically
significantly (p < 0.0125) and practically meaningfully (d >= 0.2)
higher than MDM at k=20 on Cho2017 under leakage-clean splits.

**What counts as informative regardless of FM-vs-MDM direction:**
- The leakage audit result (including the PhysionetMI contamination
  finding — this is a standalone contribution regardless of FM
  performance on Cho2017).
- The per-subject distribution on both arms.
- The shot curves (0/1/5/20 accuracy with CI) on both arms.
- The Riemannian baseline on PhysionetMI (109 subjects) — the largest
  available MOABB MI subject pool.
These are pre-specified contributions that are informative in all
directions, as documented by the defensibility critic.

---

## 8. Unlock procedure

If this protocol must be changed after re-locking:

1. Write an unlock note in `20-plan/cross-subject-eeg/` with a new
   date, with:
   - Date
   - Author
   - Specific change proposed
   - Reason the change is necessary
   - Whether the change affects the held-out partition definition
     or the primary metric
2. If the change affects the held-out partition or primary metric:
   a critic re-pass is required before re-locking.
3. If the held-out split has already been touched (the single
   authorized evaluation run has begun), no protocol change is
   permitted. The evaluation proceeds as locked.

---

## Unlock history

| Date | Author | Summary | Partition affected? |
|---|---|---|---|
| 2026-05-03 | methodologist agent | PhysionetMI confirmed in LaBraM corpus; FM arm test set substituted to Cho2017; secondary dev frozen as Lee2019; split-arm design adopted | YES |

Full unlock note: `20-plan/cross-subject-eeg/unlock-note-2026-05-03.md`
