> **Spec:** `10-pain-point/cross-subject-eeg/admission.md`

# Protocol lock — cross-subject-eeg

**Track:** cross-subject-eeg
**Locked:** 2026-05-02
**Locked by:** methodologist agent
**Status:** LOCKED — pre-registered before any headline experiment

This document defines the frozen evaluation protocol for the headline
experiment. It is locked before any experiment code is run against the
held-out test split. Changes require an explicit unlock note with a
documented reason and a new critic pass before re-locking.

---

## 0. Pre-registration statement

This protocol is written and committed before any headline experiment
is run. The held-out test partition defined in §3 has not been examined,
summarized, or used for any model selection decision as of this lock
date. The dev split may be used freely for pilots, ablations, and
preliminary analysis; the test split may be accessed exactly once, for
the single authorized evaluation run described in §6.

This pre-registration satisfies the condition imposed by the
defensibility-critic advisory (10-pain-point/
critic-defensibility.md §5) and the admission record advisory annotation.

---

## 1. The five-part evaluation program (pre-registered)

The headline experiment delivers exactly these five contributions.
If any component cannot be delivered, the specific component is marked
"not delivered" in results.md with a documented reason.

**(a) Subject + dataset + hardware-disjoint splits simultaneously.**
Train and dev data comes from a different dataset, different subject
pool, and different recording hardware than the held-out test data.
Specific split defined in §3.

**(b) 0/1/5/20-shot calibration curves per subject.**
For each model, at each shot level k ∈ {0, 1, 5, 20}, report:
mean accuracy across subjects, 95 % bootstrap CI, and the full
per-subject distribution. Shot examples drawn by 50 independent
random draws per (subject, k); mean and CI reported across draws.

**(c) Per-subject performance distributions.**
For each model × shot level, report the full distribution of
per-subject accuracy (not mean alone). Report TWO illiteracy
fractions side-by-side (m-3 fix):
- **At-or-below chance** (25 % for 4-class, 50 % for 2-class) — the
  truly-no-signal subjects.
- **At-or-below 70 % usability threshold** (Saha & Baumert 2020 /
  BCI-IV-2a convention) — the subjects who would not derive practical
  value from a deployed BCI at this scope.
The 70 % figure is directly comparable to the cited 15–30 %
illiteracy literature; the 25 % figure is the formal chance baseline.
The illiteracy characterization is a primary output, not supplementary.

**(d) Pre-training-overlap audit.**
Before touching the test split, run leakage_audit.py against the
published pre-training dataset lists for every FM checkpoint evaluated.
Report the audit result in the headline results table. If overlap is
found, the overlapping dataset is removed from the FM evaluation arm
per risk-register R-2. The audit result is reported regardless of
direction.

**Ablation-2 elevation (m-4 fix):** the LaBraM pre-training corpus
documented in §2 includes BCICIV_2a (BNCI2014_001) and BCICIV_2b —
both of which are dev-set datasets in this protocol. Ablation 2
(overlap-removed FM, defined in `approach.md`) is therefore expected
to trigger on the dev set. When triggered, the overlap-removed FM
result is elevated to a required headline component and reported in
the main results table alongside the pre-training-overlap audit, not
relegated to ablation appendix.

**(e) Riemannian + classical-ML baselines under the same splits.**
Riemannian MDM and FBCSP + LDA are evaluated under identical split
conditions as the FM probe. No baseline-favorable adjustments to the
split or preprocessing are permitted after this lock.

---

## 2. FM checkpoints evaluated (pre-registered)

**Primary FM:** LaBraM-Base (arXiv:2405.18765, ICLR 2024 spotlight).
Checkpoint: the official release at https://github.com/935963004/LaBraM.
Usage: frozen encoder, linear head (logistic regression) fitted on
k-shot support examples per target subject.

Pre-training corpus (per arXiv:2405.18765 §3.1, reproduced here for
audit purposes): TUAB, TUEV, SEED, SEED-IV, SEED-V, FACED, BCICIV_2a,
BCICIV_2b, DEAP, MAHNOB, HCI, plus additional datasets listed in the
paper. The exact list is reproduced in
`30-implement/cross-subject-eeg/code/labram_pretrain_datasets.txt` at environment setup,
for use by leakage_audit.py.

If LaBraM-Base is unavailable (risk-register R-1), the fallback FM is
BENDR (https://github.com/SPOClab-ca/BENDR). The fallback must be
documented as a pre-experiment substitution in results.md before the
test split is touched.

No other FM checkpoints are evaluated in the headline. Additional FM
probes (BENDR, BIOT) are pilot/exploratory only and do not contribute
to the headline metric.

---

## 3. Held-out partition definition (FROZEN)

### MOABB arm (headline FM-vs-Riemannian comparison)

**Test dataset:** PhysionetMI (GigaDB / PhysioNet, 109 subjects,
4-class MI, CC0 license, available via MOABB as `PhysionetMI`).

**Dev datasets:** BNCI2014_001 (BCI Competition IV-2a, 9 subjects) +
one additional dataset, chosen as either Cho2017 (52 subjects) or
Lee2019 (54 subjects). The additional dev dataset is selected during
week 1 based on download success; this selection is recorded in
`30-implement/cross-subject-eeg/runs/dev_dataset_selection.txt` before any dev-split
results are computed. The test dataset is not affected by this choice.

**Hardware-disjoint rationale (primary pair only):** PhysionetMI was
recorded using a BCI2000 system with 64 channels. BNCI2014_001 was
recorded using a g.USBamp 22-channel system. These are distinct
hardware manufacturers with distinct amplifier characteristics and
electrode counts — the hardware-disjoint criterion is satisfied for
the BNCI2014_001-vs-PhysionetMI dev/test pair.

The secondary dev dataset (Cho2017 or Lee2019) recording hardware is
not yet verified. At dev-dataset selection time (week 1), the
recording hardware of the chosen dataset is documented in
`30-implement/cross-subject-eeg/runs/dev_dataset_selection.txt`. The "hardware-disjoint"
property is asserted only for the primary pair and qualified for the
secondary pair according to what selection reveals. m-2.

**Subject-disjoint verification:** `partition.py:validate_partition()`
is run on the (dev_subject_ids, test_subject_ids) pair before the
headline run. Pass/fail logged in `30-implement/cross-subject-eeg/runs/partition_audit.txt`.

### HBN arm (complementary cross-task FM probe)

**Test subjects:** HBN Releases 9–11 (approximately 300 subjects from
three cohort releases, ages 5–21, 128-channel EEG, 6 tasks).

**Dev subjects:** HBN Releases 1–8 (approximately 2,300 subjects).

**Subject-disjoint:** HBN releases are distinct cohort sweeps;
no subject appears in more than one release per the HBN data
documentation. Verified programmatically by subject-ID uniqueness
check at preprocessing time.

**Note on HBN arm scope:** The HBN arm evaluates cross-task
generalization of the FM, not cross-subject MI decoding. It is
a secondary analysis. If the HBN arm cannot be run (risk-register
R-6), the headline remains MOABB-only and the HBN arm is dropped.
This does not affect the primary metric.

### What counts as "touching the held-out split"

The held-out split is touched when any of the following occurs:
- Test-set raw data is loaded into memory.
- Test-set features or predictions are computed.
- Test-set results are read, even for debugging.

Checking that test-set files exist on disk (e.g., `os.path.exists`)
does not count as touching.

The single authorized evaluation run must be preceded by:
1. A written confirmation in `30-implement/cross-subject-eeg/runs/pre-run-checklist.txt`
   that all model selection decisions have been made on the dev split.
2. The leakage audit result (§4) confirming the test split is clean
   for the FM arm.
3. `partition.py:validate_partition()` passing.

---

## 4. Pre-training-overlap audit procedure (pre-registered)

Run before the headline evaluation. Results stored in
`30-implement/cross-subject-eeg/runs/leakage_audit_result.json`.

Steps:
1. Load `labram_pretrain_datasets.txt` (dataset-name list).
2. Call `leakage_audit.check_dataset_overlap(pretrain_list, ["PhysionetMI"])`.
3. Call `leakage_audit.check_dataset_overlap(pretrain_list, ["HBN_R9", "HBN_R10", "HBN_R11"])`.
4. **Dev-dataset coverage (M-2 fix):** also call
   `leakage_audit.check_dataset_overlap(pretrain_list, ["BNCI2014_001", "Cho2017", "Lee2019"])`
   before any FM evaluation on the dev split begins. The result is
   logged in `30-implement/cross-subject-eeg/runs/leakage_audit_result.json` alongside
   the test-split audit. The known LaBraM corpus already includes
   BCICIV_2a (BNCI2014_001) and BCICIV_2b — the dev-set audit therefore
   nearly certainly returns a hit, which triggers Ablation 2 as a
   required headline component (see §1(d)).
5. If PhysionetMI is in pretrain_list: substitute with Lee2019 or
   Cho2017 for the FM arm (subject to those datasets also passing
   the test-split audit). Document the substitution.
6. If all MOABB candidate test datasets are in pretrain_list:
   FM cross-subject generalization claim is cancelled (see R-2).
   Leakage audit result is the FM-arm headline.

---

## 5. Primary metric (pre-registered)

**Primary metric:** Mean LOSO accuracy, macro-averaged across
datasets (MOABB arm), at each shot level k ∈ {0, 1, 5, 20},
with 95 % bootstrap CI (n=2000 resamples, stratified by subject,
random_state=42).

Unit: percentage points (0–100). Reported as "XX.X % (95 % CI:
YY.Y–ZZ.Z %, N=N_subjects)".

The per-shot-level accuracy values are four numbers, not one.
The headline comparison is the FM-vs-MDM delta at k=20 (the "best
available calibration budget" scenario) AND at k=0 (zero-shot).
Both directions matter; neither is cherry-picked.

**Secondary metrics** (reported, not primary):
- Per-subject accuracy distribution (violin plots + illiteracy-rate
  fraction below threshold).
- FM minus MDM delta at each shot level with CI.
- Leakage audit result (structured report).
- Per-class accuracy for 4-class datasets.
- FBCSP + LDA accuracy at each shot level (lower-bound baseline).

---

## 6. Statistical test for FM-vs-Riemannian comparison (pre-registered)

**Test:** Paired Wilcoxon signed-rank test, one-sided
(H1: FM accuracy > MDM accuracy, per subject, at each shot level).

**Correction:** Bonferroni across four shot levels (k = 0, 1, 5, 20);
adjusted significance threshold p < 0.0125.

**Effect size:** Cohen's d (paired, per shot level).

**Interpretation rule:**
- p < 0.0125 AND d >= 0.2: "statistically significant and practically
  meaningful improvement of FM over MDM."
- p < 0.0125 AND d < 0.2: "statistically significant but practically
  small improvement."
- p >= 0.0125: "no statistically significant improvement of FM over
  MDM at this shot level."

All four shot levels are reported. Cherry-picking a single shot level
post-hoc is a protocol violation.

---

## 7. Decision rule: what counts as the headline result (pre-registered)

The headline result is the full set of five-part evaluation outputs
on the held-out test split, evaluated exactly once. It is "real" if:

- The pre-run checklist (§3) is complete and logged.
- The leakage audit was run before the evaluation (§4).
- `validate_partition()` passed (§3).
- The evaluation was not re-run after seeing the results.

**What counts as null:** The primary metric is null (FM does not beat
MDM) if the Wilcoxon signed-rank test fails to reject H0 at the
corrected threshold (p >= 0.0125) at k=20. A null at k=20 but a
positive result at k=5 is a partial positive, reported as such.

**What counts as positive:** FM accuracy is statistically significantly
(p < 0.0125) and practically meaningfully (d >= 0.2) higher than MDM
at k=20 on the MOABB held-out test datasets, under leakage-clean splits.

**What counts as informative regardless of FM-vs-MDM direction:**
- The leakage audit result.
- The per-subject distribution (illiteracy-rate characterization).
- The shot curves (0/1/5/20 accuracy with CI).
These are pre-specified contributions that are informative in all
directions, as documented by the defensibility critic.

---

## 8. Unlock procedure

If this protocol must be changed after locking:

1. Write an unlock note in this file, below this section, with:
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

*(No unlock notes below this line as of 2026-05-02.)*
