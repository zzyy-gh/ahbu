> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Protocol lock — sleep-staging

**Track:** sleep-staging
**Locked:** 2026-05-02
**Locked by:** methodologist agent
**Status:** LOCKED — pre-registered before any headline experiment

This document defines the frozen evaluation protocol for the headline
experiment (scope b: HRV-only vs EEG staging on HMC PSG). It is locked
before any experiment code is run against the held-out test split.
Changes require an explicit unlock note with a documented reason and a
new critic pass before re-locking.

---

## 0. Pre-registration statement

This protocol is written and committed before any headline experiment
is run. The held-out test partition defined in §3 has not been examined,
summarized, or used for any model selection decision as of this lock
date (2026-05-02).

The dev split may be used freely for pilot probes, ablations, and
preliminary analysis. The held-out test split may be accessed exactly
once, for the single authorized evaluation run described in §6.

This pre-registration satisfies the condition imposed by the
defensibility-critic advisory (10-pain-point/shared/critic-defensibility.md
§4) for scope (b): named dataset (HMC PSG), named primary metric
(3-class macro-F1), pre-registered before any test-split contact.

---

## 1. Headline experiment (pre-registered)

**Scope b: paired HRV-only vs EEG staging comparison on HMC PSG.**

The headline experiment answers: does HRV-only staging (Random Forest
on 11 HRV features) perform detectably differently from EEG-based
staging (U-Sleep frozen inference) when evaluated cross-subject on
the same population?

This is a two-arm evaluation:
- Arm 1: HRV-only RF, trained on 75 dev subjects, tested on 76 held-out
  test subjects.
- Arm 2: U-Sleep pretrained EEG stager (frozen), evaluated on the same
  76 held-out test subjects (no re-training on HMC PSG).

Both arms produce a 3-class prediction (Wake / NREM / REM) for each
30-second epoch. Macro-F1 is computed per subject; subjects are the
unit of statistical analysis.

Scope (a) (OSA-stratified eval on NSRR data) is NOT part of this
locked headline. If the NSRR DUA arrives and scope (a) runs, it
receives a separate protocol-lock addendum before the scope (a)
headline run. The scope (b) headline is independent of scope (a).

---

## 2. Models evaluated (pre-registered)

**Primary model:** Random Forest (sklearn RandomForestClassifier,
n_estimators=200, class_weight="balanced", random_state=42) trained
on all 75 dev subjects' epoch-level HRV features.

**Comparison model:** U-Sleep pretrained checkpoint
(https://github.com/perslev/U-Sleep, exact version recorded at
implementation start in `30-implement/sleep-staging/code/requirements.txt`).
Used as frozen inference — no re-training on HMC PSG.

If U-Sleep is unavailable per risk-register R-4, the fallback EEG
baseline is a 1D-ResNet trained on the dev split and tested on the
test split. The fallback must be documented as a pre-experiment
substitution in results.md before the test split is touched.

**Majority-class baseline:** Predict NREM for all epochs (no model,
lower bound). Included in results for calibration.

No other models are evaluated in the headline. Additional models
(LSTM on HRV, temperature-scaled U-Sleep) are dev-only probes and
do not contribute to the headline metric.

---

## 3. Held-out partition definition (FROZEN)

### Dataset

**HMC PSG (HMC Sleep Staging Database (Hassan 2023) dataset),**
as accessed at implementation start. Exact URL:
https://physionet.org/content/hmc-sleep-staging/1.0.0/
The labeled training set (154 subjects with PSG + stage annotations)
is used.

### Subject split

- **Dev subjects:** 75 subjects, selected by stratified random split
  (stratified by AHI category: none / mild / moderate / severe OSA,
  based on available metadata; if AHI is unavailable for all subjects,
  stratify by epoch count quartile as a proxy for recording quality).
- **Test subjects:** 77 subjects (the remaining 154 - 78), selected
  by the same stratified split.
- **Split seed:** random_state=42.
- **Split procedure:** `subject_disjoint_split(all_subjects, test_fraction=0.50,
  stratify_col=ahi_band, random_state=42)` (from partition.py or
  local implementation with same interface).
- **Split validation:** `validate_partition({"dev": dev_subjects,
  "test": test_subjects})` must pass (no subject overlap) before
  any experiment runs. Logged in
  `30-implement/sleep-staging/runs/partition_audit.txt`.

The exact subject-ID lists for dev and test splits are recorded in
`30-implement/sleep-staging/runs/partition_definition.json` at the time
of split creation, before any model training or inference begins.
This file is committed to git before week 1 experiments start.

### Stage labels

5-class AASM (W, N1, N2, N3, REM) from HMC PSG annotation files.
For the headline metric, map to 3-class: W=Wake, {N1, N2, N3}=NREM,
REM=REM.

### What counts as "touching the held-out split"

The held-out split is touched when any of the following occurs:
- Test-subject file paths are passed to any data-loading function.
- Test-subject ECG or EEG data is read into memory.
- Test-subject epoch features or predictions are computed.
- Test-split metrics are computed or viewed.

Checking that test-subject files exist on disk does NOT count.

The single authorized evaluation run must be preceded by the
pre-run checklist (§6).

---

## 4. Primary metric (pre-registered)

**Primary metric:** 3-class macro-F1 (Wake / NREM / REM) on
76 held-out test subjects, computed as follows:

1. For each test subject s, compute per-epoch predictions from
   both HRV-RF and U-Sleep.
2. Map 5-class predictions to 3-class (N1, N2, N3 → NREM).
3. Compute macro-F1 per subject (macro = unweighted mean of
   per-class F1 over Wake, NREM, REM).
4. Report the mean across subjects with 95 % bootstrap CI
   (n=2000 resamples at the subject level, random_state=42).

Unit: F1 score (0.0–1.0). Reported as: "macro-F1 = X.XX
(95 % CI: Y.YY–Z.ZZ, N=77 test subjects)".

**Primary comparison metric:** EEG-vs-HRV gap =
U-Sleep-macro-F1 minus HRV-RF-macro-F1, paired by subject.
This delta is the headline quantity.

**Secondary metrics (reported but not primary):**
- 5-class per-stage F1 (W, N1, N2, N3, REM) with 95 % CI.
- 5-class confusion matrix per model.
- AHI-stratified 3-class macro-F1 (if AHI data is available for
  sufficient subjects) via `cohort_stratifier.stratified_report()`.
- RF feature importance (top HRV features per class).
- Majority-class baseline macro-F1 (lower bound).

---

## 5. Statistical test (pre-registered)

**Test:** Paired Wilcoxon signed-rank test, one-sided.
H1: U-Sleep (EEG) macro-F1 > HRV-RF macro-F1, per subject.

**Significance threshold:** p < 0.05 (single primary test;
no multiplicity correction — only one pre-registered comparison).

**Effect size:** Cohen's d (paired).

**Interpretation rule (applied at analysis time):**

Case A: p < 0.05 AND d >= 0.5:
"EEG significantly and substantially outperforms HRV-only staging
(p < 0.05, d >= 0.5). EEG provides substantial additional information
beyond autonomic HRV dynamics for sleep staging at this population."

Case B: p < 0.05 AND 0.2 <= d < 0.5:
"EEG statistically outperforms HRV-only staging (p < 0.05) but the
effect size is moderate (d = X.X). The absolute performance gap is
small enough that HRV-only may be adequate for low-precision wearable
applications."

Case C: p < 0.05 AND d < 0.2:
"EEG outperforms HRV-only by a statistically significant but
practically negligible margin. HRV-only staging is effectively at
EEG parity for practical purposes at this population and threshold."

Case D: p >= 0.05:
"No statistically significant difference between EEG-based and
HRV-only staging at N=77 (p = X.XX). This is a defensible-null
result: either the true gap is below the detection threshold at this
sample size, or HRV-only staging is genuinely at EEG parity in this
population."

All four cases are pre-specified. The case label is determined by the
test result; no cherry-picking of framing post-hoc.

---

## 6. Decision rule: what counts as the headline result (pre-registered)

The headline result is the full set of evaluation outputs on the
held-out test split, evaluated exactly once. It is "real" if:

**Pre-run checklist (all must be true before touching the test split):**
- [ ] `partition_definition.json` committed to git with dev/test
      subject lists before any model training.
- [ ] `partition_audit.txt` shows `validate_partition()` passed.
- [ ] RF trained on dev subjects only (training confirmed by code
      inspection before headline run).
- [ ] U-Sleep checkpoint version recorded in requirements.txt.
- [ ] **U-Sleep training-data overlap audit run** (m-5 fix): confirm
      HMC Sleep Staging Database is NOT in U-Sleep's documented
      pre-training corpus (Perslev et al. — 16 studies, 15,660 PSGs;
      check the published list). If HMC is in pretrain, the EEG-vs-HRV
      paired comparison is contaminated and the headline must redesign
      (e.g., evaluate on a held-out cohort confirmed absent from
      U-Sleep training, or substitute a different EEG stager).
      Audit result logged in `30-implement/sleep-staging/runs/usleep_overlap_audit.txt`.
- [ ] No test-split subject data was loaded for any prior experiment.
- [ ] All ablations and pilot probes have been run on dev split only.
- [ ] Pre-run checklist written to
      `30-implement/sleep-staging/runs/pre-run-checklist.txt` before
      executing the headline script.

**Headline-positive:** The Wilcoxon test rejects H0 (p < 0.05)
for the EEG-vs-HRV comparison. Positive result characterizes the
EEG advantage; the effect size determines clinical relevance framing
(Cases A–C above).

**Headline-null:** The Wilcoxon test does not reject H0 (p >= 0.05).
Null result means the gap is below the detection threshold at N=77.
Per the defensibility-critic analysis: this is an informative null
because it bounds the EEG-HRV gap to < ~17 pp at 80 % power (the
detection threshold). It directly informs wearable deployment
decisions.

**Informative regardless of direction:**
- The 3-class macro-F1 absolute values for both models (establishes
  the performance floor for this population).
- The 5-class per-stage F1 (characterizes where HRV fails: N1, N2, or
  across all NREM).
- The AHI-stratified breakdown (does HRV degrade more than EEG as
  OSA severity increases?).

---

## 7. Unlock procedure

If this protocol must be changed after locking:

1. Write an unlock note in this file immediately below §7, with:
   - Date
   - Author
   - Specific change proposed
   - Reason the change is necessary
   - Whether the change affects the held-out partition definition
     or the primary metric
2. If the change affects the held-out partition definition or primary
   metric: a critic re-pass is required before re-locking.
3. If the held-out split has already been touched (the single
   authorized evaluation run has begun): no protocol change is
   permitted. The evaluation proceeds as locked.

---

*(No unlock notes below this line as of 2026-05-02.)*
