> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Protocol lock — sleep-staging

**Track:** sleep-staging
**Originally locked:** 2026-05-02
**Re-locked:** 2026-05-03
**Re-locked by:** methodologist agent
**Unlock note:** `20-plan/sleep-staging/unlock-note-2026-05-03.md`
**Status:** LOCKED — revised pre-registration. Scope (b) held-out partition unchanged.
Scope (a) added as co-primary headline.

This document defines the frozen evaluation protocol for both headline experiments.
It is locked before any experiment code is run against either held-out test partition.
Changes require an explicit unlock note with a documented reason and a new critic pass
before re-locking.

---

## 0. Pre-registration statement

This revised protocol is written and committed on 2026-05-03 before any headline
experiment is run on either the scope (b) HMC PSG test partition or the scope (a)
MESA test partition. Neither held-out partition has been examined, summarized, or
used for any model selection decision as of this lock date.

The dev split may be used freely for pilot probes, ablations, and preliminary analysis.
Held-out test partitions may be accessed exactly once each, for the single authorized
evaluation run described in §6 for each scope.

---

## 1. Headline experiments (pre-registered)

### Scope (b) — HEADLINE-B: paired HRV-only vs EEG staging comparison on HMC PSG

The headline question: does HRV-only staging (Random Forest on 11 HRV features) perform
detectably differently from EEG-based staging (U-Sleep frozen inference) when evaluated
cross-subject on a mixed clinical-population PSG dataset?

- Arm B1: HRV-only RF, trained on 77 dev subjects, tested on 77 held-out test subjects.
- Arm B2: U-Sleep pretrained EEG stager (frozen), evaluated on the same 77 held-out test
  subjects (no re-training on HMC PSG).

Both arms produce a 3-class prediction (Wake / NREM / REM) per 30-second epoch.
Macro-F1 is computed per subject; subjects are the unit of statistical analysis.

### Scope (a) — HEADLINE-A: clinical-population stratified evaluation of pretrained stager on MESA

The headline question: does a pretrained EEG stager (U-Sleep) exhibit a systematic
performance gap across OSA severity strata (none / mild / moderate / severe) when applied
to MESA PSG data — a large multi-ethnic cohort not in U-Sleep's training corpus?

- Single arm: U-Sleep frozen inference on MESA test subjects, stratified by AHI band.
- No HRV-only comparison in scope (a). Scope (a) is purely evaluation of U-Sleep on
  a powered clinical cohort.

MESA is the primary NSRR dataset for scope (a) because:
- 2,056 subjects with ECG (enables HRV for scope b replication if desired).
- Multi-ethnic (AHA-defined strata).
- AASM v2 labels (same coding era as HMC PSG).
- AHI available per subject.

SHHS (~5,800 subjects, R&K labels, older scoring era) is a secondary confirmatory
dataset for scope (a) if time and storage allow. SHHS results are secondary, not primary.

**Token access:** NSRR API token is available in the environment as `os.environ['NSRR_TOKEN']`.
The token lives in `.env` (gitignored). Never print or commit the value. Use it as:
```python
import os
token = os.environ['NSRR_TOKEN']
```
Pass to nsrr download commands or direct HTTPS requests as the authentication bearer.
The token's presence confirms DUA approval for both SHHS and MESA.

---

## 2. Models evaluated (pre-registered)

### Scope (b) models

**Primary model:** Random Forest (sklearn RandomForestClassifier,
n_estimators=200, class_weight="balanced", random_state=42) trained on all 77 dev
subjects' epoch-level HRV features. (N dev updated from 75 to 77 — see §3.)

**Comparison model:** U-Sleep pretrained checkpoint
(https://github.com/perslev/U-Sleep, exact version recorded at implementation start
in `30-implement/sleep-staging/code/requirements.txt`). Used as frozen inference —
no re-training on HMC PSG.

**U-Sleep fallback (if unavailable per R-4):** 1D-ResNet trained on dev split, tested
on test split. Must be documented as pre-experiment substitution in results.md before
test split is touched.

**Majority-class baseline:** Predict NREM for all epochs. Lower bound; always reported.

No other models are evaluated in HEADLINE-B.

### Scope (a) models

**Primary model:** U-Sleep frozen inference on MESA test subjects. Same checkpoint as
scope (b). No training on MESA.

**Calibration head:** Temperature scaling fit on a MESA dev subset (10 % of MESA
subjects, subject-disjoint from MESA test partition). Fit on this MESA-native dev set
corrects for distribution shift vs Dreem-DOD-H (see approach.md). ECE reported
before and after temperature scaling.

No HRV-only model in scope (a).

---

## 3. Held-out partition definitions (FROZEN)

### Scope (b) — HMC PSG held-out partition

**Dataset:** HMC Sleep Staging Database (Hassan 2023), v1.0.0.
URL: https://physionet.org/content/hmc-sleep-staging/1.0.0/
License: Creative Commons Attribution 4.0 International (open access; no DUA required).
The labeled set (154 subjects) with PSG + stage annotations is used.

**Subject split:**
- Dev subjects: 77 subjects.
- Test subjects: 77 subjects (154 - 77).
- Split seed: random_state=42.
- Stratified by AHI category (none: AHI<5 / mild: 5≤AHI<15 / moderate: 15≤AHI<30 /
  severe: AHI≥30) **if AHI metadata is present in HMC PSG headers** (confirmed at
  P-1 success criterion).
- **If AHI metadata is absent from HMC PSG:** split is stratified by sex (M/F) and
  age-decade (40s / 50s / 60s / 70s+). The AHI-stratified secondary analysis of
  scope (a) is unaffected (MESA carries its own AHI metadata); only the HMC PSG
  stratification variable changes. This is a pre-specified conditional, not a
  post-hoc choice.
- Procedure: `subject_disjoint_split(all_subjects, test_fraction=0.50, stratify_col=ahi_band,
  random_state=42)`.

Note: the original lock used 75 dev / 77 test (rounding 154 × 0.50 = 77). This revision
uses a symmetric 77/77 split. The held-out partition size is unchanged at 77 test subjects.

**Stage labels:** 5-class AASM (W, N1, N2, N3, REM). Headline metric uses 3-class mapping:
W=Wake, {N1, N2, N3}=NREM, REM=REM.

**CAP Sleep substitute (activated only if HMC PSG is inaccessible after P-1 attempt):**
If P-1 confirms HMC PSG is blocked (unlikely given open-access confirmation, but possible
due to local/institutional factors), substitute CAP Sleep Database (PhysioNet ODC-BY open;
108 subjects; ECG present in all recordings). Partition: 54 dev / 54 test, stratified by
pathology category (healthy / neurological / respiratory / other). Label mapping: R&K
S1→N1, S2→N2, {S3, S4}→N3, REM→REM, W→W (standard AASM-equivalent mapping). Subject
count and partition seed are re-frozen here: test_fraction=0.50, random_state=42.
If substitute is activated: write a substitute-activation note in
`30-implement/sleep-staging/runs/cap_substitute_activation.txt` before any training.

**What counts as touching the held-out split:** Any loading of test-subject file paths,
reading of ECG/EEG data for test subjects, computation of epoch features or predictions
for test subjects, or viewing of test-split metrics. Checking file existence does not count.

### Scope (a) — MESA held-out partition

**Dataset:** MESA Sleep (Multi-Ethnic Study of Atherosclerosis — Sleep Exam).
Access: via NSRR API token (`os.environ['NSRR_TOKEN']`), DUA approved.
URL: https://sleepdata.org/datasets/mesa
Subjects with PSG data: 2,056.

**Subject split:**
- Dev subjects: 10 % (approximately 206 subjects), stratified by AHI band and
  self-reported race/ethnicity. Used for calibration head fitting only.
- Test subjects: 90 % (approximately 1,850 subjects), stratified by same columns.
- Split seed: random_state=42.
- Procedure: `subject_disjoint_split(mesa_subjects, test_fraction=0.90,
  stratify_col=ahi_band, random_state=42)`.

Rationale for 90/10 split (vs 50/50 for scope b): scope (a) requires no model training
on MESA. The dev subset is used only for calibration (temperature scaling, ~200 subjects
is ample). The large test partition (N~1,850) gives well-powered OSA-stratification
analysis.

**Scope (a) power story:** With N~1,850 test subjects and expected AHI-band distribution
(none ~40 %, mild ~25 %, moderate ~20 %, severe ~15 %; figures from Dean et al. 2015,
J Clin Sleep Med, MESA Sleep cohort baseline characteristics — to be confirmed against
the actual MESA covariates file in P-7), the smallest stratum is severe OSA (~280 subjects).
A two-sample proportion test comparing severe-OSA macro-F1 to no-OSA macro-F1 with
expected 10 pp gap, 80 % power, alpha=0.05 requires N~170 per stratum. N~280 meets
this threshold comfortably. (The §5 multiplicity policy applies to the two top-level
co-primary headline Wilcoxon tests; it does not apply to this within-scope secondary
stratum comparison.) **Conditional kill:**
if P-7 reveals the severe-OSA fraction in the MESA sample is < 10 % (smallest stratum
< ~185 subjects after the 90/10 split), the power story is revisited and HEADLINE-A
must be re-locked before any test access.

**Stage labels:** AASM v2 scoring (5-class). Same 3-class mapping as scope (b) for
cross-scope comparability.

**SHHS secondary dataset (if pursued):** SHHS has R&K labels (8-class: W, S1–S4, REM,
movement, unscored). R&K-to-AASM mapping required. SHHS is confirmatory only; it does
NOT replace MESA as the primary scope (a) dataset. SHHS headline metrics are secondary
in results.md.

---

## 4. Primary metrics (pre-registered)

### Scope (b) primary metric

**3-class macro-F1 (Wake / NREM / REM)** on 77 held-out HMC PSG test subjects.

Computation:
1. For each test subject s, compute per-epoch predictions from both HRV-RF and U-Sleep.
2. Map 5-class predictions to 3-class (N1, N2, N3 → NREM).
3. Compute macro-F1 per subject (unweighted mean of Wake-F1, NREM-F1, REM-F1).
4. Report mean across subjects with 95 % bootstrap CI (n=2000, subject-level resampling,
   random_state=42).

Reported as: "macro-F1 = X.XX (95 % CI: Y.YY–Z.ZZ, N=77 test subjects)".

**Primary comparison metric (scope b):** EEG-vs-HRV gap = U-Sleep-macro-F1 minus
HRV-RF-macro-F1, paired by subject. This delta is the scope (b) headline quantity.

### Scope (a) primary metric

**AHI-stratified 3-class macro-F1** for U-Sleep on MESA test subjects.

Reported as: per-stratum mean macro-F1 ± 95 % bootstrap CI for each of four AHI strata
(none: AHI < 5; mild: 5 ≤ AHI < 15; moderate: 15 ≤ AHI < 30; severe: AHI ≥ 30).

Primary estimand: the macro-F1 difference between the no-OSA stratum and the severe-OSA
stratum (OSA performance degradation). Reported as a point estimate with 95 % CI.

### Secondary metrics (both scopes, reported but not primary)

- 5-class per-stage F1 (W, N1, N2, N3, REM) with 95 % CI for each model.
- 5-class confusion matrix per model.
- RF feature importance (scope b): top HRV features per class.
- ECE (scope a): multiclass_ece() before and after temperature scaling.
- Majority-class baseline macro-F1.
- SHHS confirmatory OSA-stratification results (scope a, secondary).

---

## 5. Statistical tests (pre-registered)

### Multiplicity policy across the two co-primary headlines

This protocol declares two co-primary headline tests: HEADLINE-A
(scope a, MESA, two-sample Wilcoxon on no-OSA vs severe-OSA macro-F1)
and HEADLINE-B (scope b, HMC PSG, paired Wilcoxon on U-Sleep vs HRV-RF
macro-F1). The two tests use **different datasets** (MESA vs HMC PSG),
**different model families** (single U-Sleep stratum-comparison vs
U-Sleep-vs-RF paired comparison), and **different estimands**
(within-model OSA-severity degradation vs between-model EEG-vs-HRV gap).

**Policy (pre-registered, option (b) per critic-v2 M-1):** the two
headlines test independent estimands on independent datasets and are
each individually interpretable. No family-wise error rate correction
is applied; each headline is tested at its declared alpha = 0.05.
Both headlines are reported, regardless of direction, per their own
case-rule tables below. This rationale is locked here pre-experiment;
it cannot be characterized as post-hoc.

**Conservative fallback:** if a reviewer or the analysis sign-off
critic deems the independence argument insufficient, the published
report adds Bonferroni-corrected p-values (alpha = 0.025 per test)
as a sensitivity column alongside the primary alpha = 0.05 result;
the case-rule labels do not change.

### Scope (b) statistical test

**Paired Wilcoxon signed-rank test, one-sided.**
H1: U-Sleep (EEG) macro-F1 > HRV-RF macro-F1, per subject.
Significance threshold: p < 0.05.
Effect size: Cohen's d (paired).

**Interpretation rule (applied at analysis time):**

Case A: p < 0.05 AND d >= 0.5:
"EEG significantly and substantially outperforms HRV-only staging (p < 0.05, d >= 0.5).
EEG provides substantial additional information beyond autonomic HRV dynamics for sleep
staging at this population."

Case B: p < 0.05 AND 0.2 <= d < 0.5:
"EEG statistically outperforms HRV-only staging (p < 0.05) but the effect size is
moderate (d = X.X). The absolute performance gap is small enough that HRV-only may be
adequate for low-precision wearable applications."

Case C: p < 0.05 AND d < 0.2:
"EEG outperforms HRV-only by a statistically significant but practically negligible
margin. HRV-only staging is effectively at EEG parity for practical purposes."

Case D: p >= 0.05:
"No statistically significant difference between EEG-based and HRV-only staging at
N=77 (p = X.XX). This is a defensible-null result: the gap is below the detection
threshold at this sample size."

All four cases are pre-specified. Case is determined by the test result; no post-hoc
framing.

### Scope (a) statistical test

**Two-sample Wilcoxon test (unpaired), one-sided.**
H1: U-Sleep macro-F1 in no-OSA stratum > U-Sleep macro-F1 in severe-OSA stratum.
Significance threshold: p < 0.05 (single primary test).
Effect size: rank-biserial correlation r.

**Interpretation rule:**

Case A: p < 0.05 AND r >= 0.3:
"U-Sleep performance degrades significantly and substantially as OSA severity increases
(p < 0.05, r >= 0.3). Pretrained stagers are not reliable for severe-OSA populations
without OSA-specific fine-tuning."

Case B: p < 0.05 AND r < 0.3:
"U-Sleep shows a statistically significant but modest degradation with OSA severity.
The clinical magnitude may not warrant OSA-specific retraining for typical deployments."

Case C: p >= 0.05:
"U-Sleep shows no statistically significant performance difference across OSA severity
strata at N~1,850. Pretrained stager is OSA-robust at this statistical threshold."

All three cases are pre-specified.

---

## 6. Decision rule: what counts as the headline result (pre-registered)

### Pre-run checklist — scope (b) HEADLINE-B

All must be true before touching the HMC PSG test split:

- [ ] `partition_definition_hmcpsg.json` committed to git with dev/test subject lists
      before any model training.
- [ ] `partition_audit_hmcpsg.txt` shows `validate_partition()` passed.
- [ ] RF trained on dev subjects only (confirmed by code inspection).
- [ ] U-Sleep checkpoint version recorded in requirements.txt.
- [ ] U-Sleep training-data overlap audit: confirmed HMC Sleep Staging Database is NOT
      in U-Sleep's documented pre-training corpus (Perslev et al. 16-study list).
      Audit result in `30-implement/sleep-staging/runs/usleep_overlap_audit.txt`.
- [ ] No test-split subject data loaded for any prior experiment.
- [ ] All ablations and pilots run on dev split only.
- [ ] **P-3 (U-Sleep VRAM probe) PASS** with peak VRAM <= 3 GB at batch=32 on
      a single-channel HMC PSG record. Result in
      `30-implement/sleep-staging/runs/pilot_p3_*.json`. Gating per critic-v2 C-1.
- [ ] Pre-run checklist written to `30-implement/sleep-staging/runs/pre-run-checklist-scopeb.txt`.

### Pre-run checklist — scope (a) HEADLINE-A

All must be true before touching the MESA test partition:

- [ ] `partition_definition_mesa.json` committed to git with dev/test subject lists.
- [ ] `partition_audit_mesa.txt` shows `validate_partition()` passed.
- [ ] Temperature scaling calibration head fit on MESA dev subset only (10 %).
- [ ] U-Sleep checkpoint version recorded (same checkpoint as scope b).
- [ ] U-Sleep overlap with MESA training corpus checked: MESA is not in U-Sleep's
      declared training set. Log in `30-implement/sleep-staging/runs/usleep_overlap_audit.txt`.
- [ ] NSRR token validity confirmed (test download of a single MESA EDF file before
      bulk download).
- [ ] No MESA test-split subject data loaded for any prior experiment.
- [ ] **P-3 (U-Sleep VRAM probe) PASS** with peak VRAM <= 3 GB at batch=32 on
      a single-channel MESA record (or HMC PSG, since both use single-channel
      U-Sleep mode). Result in `30-implement/sleep-staging/runs/pilot_p3_*.json`.
      Gating per critic-v2 C-1.
- [ ] **P-7 (MESA AHI distribution sanity)**: severe-OSA stratum size confirmed
      >= 185 subjects (in the 90 % test partition). Below this triggers the
      §3 conditional kill and a re-lock before any test access.
- [ ] Pre-run checklist written to `30-implement/sleep-staging/runs/pre-run-checklist-scopea.txt`.

### The result is "real" when

For HEADLINE-B: pre-run checklist complete, test split touched exactly once,
bootstrap CIs computed, Wilcoxon test run, case label (A/B/C/D) determined and recorded.

For HEADLINE-A: pre-run checklist complete, MESA test partition touched exactly once,
stratified_report() run for all four AHI strata, bootstrap CIs computed, Wilcoxon
test run, case label (A/B/C) determined and recorded.

Both headlines are informative regardless of direction per the pre-specified interpretation
rules above.

---

## 7. Unlock procedure

If this protocol must be changed after locking:

1. Write an unlock note in `20-plan/sleep-staging/unlock-note-<date>.md` with:
   - Date
   - Author
   - Specific change proposed
   - Reason the change is necessary
   - Whether the change affects a held-out partition definition or primary metric
2. If the change affects a held-out partition definition or primary metric: critic re-pass
   required before re-locking.
3. If a held-out split has already been touched (the single authorized evaluation run has
   begun for that scope): no protocol change is permitted for that scope. The evaluation
   proceeds as locked.

---

## 8. Unlock history

| Date | Author | Scope of change | Partition affected? | Notes |
|---|---|---|---|---|
| 2026-05-02 | methodologist agent | Initial lock | — | Scope (b) only; scope (a) conditional |
| 2026-05-03 | methodologist agent | Scope (a) elevated to co-primary; HMC access confirmed open; NSRR token path added | No (scope b unchanged; scope a partition added new) | See unlock-note-2026-05-03.md |
