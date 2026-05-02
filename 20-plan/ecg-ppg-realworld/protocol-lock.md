> **Spec:** `10-pain-point/ecg-ppg-realworld/admission.md`

# Protocol lock — ecg-ppg-realworld

**Track:** ecg-ppg-realworld
**Locked:** 2026-05-02
**Locked by:** methodologist agent
**Status:** LOCKED — pre-registered before any headline experiment

This document defines the frozen evaluation protocol for the headline
experiment. It is locked before any experiment code is run against
strat_fold 10. Changes require an explicit unlock note with a documented
reason and a new critic pass before re-locking.

---

## 0. Pre-registration statement

This protocol is written and committed before any headline experiment
is run. The held-out test partition defined in §3 (PTB-XL strat_fold 10)
has not been examined, summarized, or used for any model selection
decision as of this lock date.

The dev partition (strat_fold 1–8) and validation partition (strat_fold 9)
may be used freely for pilots, ablations, temperature scaling fit, and
threshold selection. The test partition (strat_fold 10) is accessed
exactly once, for the single authorized evaluation run described in §6.

This pre-registration satisfies the condition imposed by the
defensibility-critic advisory (10-pain-point/shared/critic-defensibility.md §1):
"Pre-register: scope and primary metric (PPV@20%-abstain-rate) locked
before touching the held-out split."

The scope (b) — skin-tone PPG evaluation — is explicitly excluded from
this protocol per the admission record advisory and the gap-closing pass.
No PPG corpus is used.

---

## 1. Headline contribution (pre-registered)

One contribution, evaluated exactly once on the held-out test partition.

> **Does calibrated abstention improve PPV at a fixed alert rate on
> PTB-XL? Specifically: does a temperature-scaled xresnet1d50
> abstaining on its 20% least-confident records produce meaningfully
> higher PPV than the same model evaluated without abstention, on
> PTB-XL strat_fold 10, patient-disjoint held-out partition?**

No secondary contributions are part of the pre-registered headline.
The cross-dataset CinC 2017 probe, conformal prediction arm, and
per-subgroup analyses are all exploratory and are not evaluated on
a frozen held-out partition.

---

## 2. Model evaluated (pre-registered)

**Primary model:** xresnet1d50 trained on PTB-XL strat_fold 1–8, binary
AFIB label at likelihood_threshold = 100.0, post-hoc calibrated by
temperature scaling (T fitted on strat_fold 9 by Brier minimization).

**Primary abstention mechanism:** Confidence-threshold abstention.
Abstain when max(P_afib, 1 - P_afib) < tau. Primary operating point:
coverage = 0.80, corresponding to abstaining on the 20% of strat_fold 10
records with the lowest max-confidence score.

**Seed selection:** Three training seeds evaluated on strat_fold 9
(Brier score). The seed with the lowest strat_fold 9 Brier score is
selected. This selection is made and logged BEFORE touching strat_fold 10.
The selected seed is recorded in `30-implement/ecg-ppg-realworld/runs/seed_selection.txt`.

**Fallback model (if xresnet1d50 training fails, per R-5):**
Logistic regression on the 12-feature hand-crafted feature vector,
with Platt scaling for calibration. If the fallback is used, document
it as a pre-headline design change in `runs/model_selection.txt`.
The headline metric and statistical test are unchanged.

If both xresnet1d50 and logistic regression fail (AUROC < 0.60 on
strat_fold 9), the track retires-cancelled per risk-register R-5.

---

## 3. Held-out partition definition (FROZEN)

**Test partition:** PTB-XL v1.0.3, strat_fold 10.
- PhysioNet path: https://physionet.org/content/ptb-xl/1.0.3/
- Strat_fold 10 is defined by the `strat_fold` column in
  `ptbxl_database.csv`. No manual re-selection of records is permitted.
- Expected approximate record count: ~2,179 total, ~303 AFIB-labeled
  at likelihood_threshold=100.0.
- Patient disjointness: guaranteed by PTB-XL's fold construction.
  Verified by `partition.py:validate_partition()` before the headline run.
  Pass/fail logged in `30-implement/ecg-ppg-realworld/runs/partition_audit.txt`.

**Training partition:** strat_fold 1–8.
**Validation partition (calibration fitting + seed selection by Brier + threshold selection):** strat_fold 9 (M-2 fix per methodology-critic — full permitted uses listed).

No records from strat_fold 10 are used for any purpose other than the
single authorized evaluation run.

### What counts as "touching the held-out split"

The held-out split is touched when any of the following occurs:
- strat_fold 10 record data is loaded into memory.
- strat_fold 10 features, predictions, or labels are computed.
- strat_fold 10 performance is read, even for debugging.

Checking that strat_fold 10 files exist on disk does not count as touching.

The single authorized evaluation run must be preceded by all steps in §6.

---

## 4. Primary metric (pre-registered)

**PPV at coverage = 0.80**

Definition: PPV computed over the predicted-AFIB subset of the 80% of
strat_fold 10 records retained after `max(P_afib, 1 - P_afib)` abstention.

**Two-denominator clarification (M-1 fix per methodology-critic):**
Coverage and PPV use different denominators.
- Coverage denominator = ALL retained records (both high-confidence
  AFIB-predicted AND high-confidence not-AFIB-predicted together).
- PPV denominator = ONLY the predicted-AFIB subset of those retained
  records.
A record with P_afib=0.05 (max-confidence=0.95, predicted not-AFIB) is
retained in the top 80% (counted in coverage) but contributes neither TP
nor FP to PPV.

Formally:
- Sort strat_fold 10 records by max(P_afib, 1 - P_afib) descending.
- Take the top 80% (highest confidence) → this is the retained set.
- Within the retained set, identify predicted-AFIB records (P_afib > 0.5).
- PPV = TP / (TP + FP), where TP = AFIB records predicted as AFIB
  inside the retained set, FP = non-AFIB records predicted as AFIB
  inside the retained set.

Operating point anchor: 80% coverage = 20% abstention rate, matching
the BASEL Wearable Study's 17–21% inconclusive rate (Mannhart et al.
JACC Clin Electrophysiol 2023). This is a clinically motivated anchor,
not a post-hoc optimal point.

**Comparison (headline test):** PPV(coverage=0.80, with abstention)
vs PPV(coverage=1.00, no abstention). Both computed on strat_fold 10.
The abstention benefit = PPV(0.80) - PPV(1.00).

---

## 5. Secondary metrics (pre-registered, reported alongside primary)

These are computed on strat_fold 10 in the same single evaluation run.
They do not determine headline-positive vs. headline-null; they are
reported regardless of direction.

- PPV at coverage = {0.70, 0.75, 0.85, 0.90, 1.00} — to show the
  full PPV-vs-coverage trade-off curve.
- AUC of the coverage-vs-PPV curve from coverage=0.50 to 1.00.
- Brier score (temperature-scaled vs. uncalibrated model, for context).
- ECE at 15 bins.
- AUROC (for comparison with the existing PTB-XL benchmark literature).
- Abstention rate at the primary operating point (should be ~20% by
  construction, but the actual rate may differ slightly depending on
  the confidence distribution).
- Count of AFIB records in strat_fold 10 at likelihood_threshold=100.0
  (actual N, used in all CI computations).

---

## 6. Pre-run checklist (required before touching strat_fold 10)

All items must be checked and logged in
`30-implement/ecg-ppg-realworld/runs/pre-run-checklist.txt` before the
headline evaluation code is executed.

- [ ] partition.py:validate_partition() passes on (strat_fold 1–8,
      strat_fold 9, strat_fold 10) patient-ID sets.
- [ ] AFIB record count in strat_fold 10 verified at likelihood_threshold=100.0.
      Count recorded. Count >= 87 (power threshold from R-2 mitigation).
- [ ] Seed selection completed: three seeds evaluated on strat_fold 9,
      winning seed recorded in `runs/seed_selection.txt`.
- [ ] Temperature scaling T parameter fitted on strat_fold 9 and recorded.
- [ ] Ablation 1 on strat_fold 9 confirms confidence-correctness AUC
      >= 0.55 (R-3 kill check passed).
- [ ] No file in `30-implement/ecg-ppg-realworld/runs/` contains results
      from strat_fold 10 records.
- [ ] Final literature check completed (R-4 mitigation): no paper found
      that pre-empts the PPV-at-coverage framing on PTB-XL strat_fold 10.
      Result of check recorded in `runs/pre-run-checklist.txt`.

If any checklist item fails, do not proceed. Address the failure per
the risk register.

---

## 7. Statistical test for the headline claim (pre-registered)

**Test:** Paired bootstrap test (n=2,000 resamples, stratified by AFIB
label, seed=42).

**H0:** PPV(coverage=0.80) - PPV(coverage=1.00) = 0.

**H1 (one-sided):** PPV(coverage=0.80) > PPV(coverage=1.00).

**p-value:** Fraction of bootstrap resamples where the difference
PPV(0.80) - PPV(1.00) <= 0.

**Significance threshold:** p < 0.05 (one-sided).

**Effect size:** Absolute PPV difference in percentage points
at coverage=0.80, with 95% bootstrap CI.

No multiple-comparison correction is needed — there is exactly one
primary comparison.

---

## 8. Decision rule: what counts as headline-positive vs. headline-null

**Headline-positive:**
PPV(coverage=0.80) - PPV(coverage=1.00) is statistically significant
(p < 0.05, one-sided) AND the effect size is >= 5 percentage points
(95% CI lower bound >= 5 pp).

Rationale for 5 pp threshold: below 5 pp PPV improvement at 20%
abstention, the clinical benefit is likely too small to justify asking
a physician to review the abstained records, given that the BASEL
inconclusive rate was already 17–21% with no ML abstention. The
clinical cost of a 20% inconclusive rate must be worth at least a
5 pp PPV improvement to be actionable.

**Headline-null (informative):**
PPV(coverage=0.80) - PPV(coverage=1.00) is not statistically significant
(p >= 0.05), AND the 95% CI upper bound < 10 pp.

A headline-null is informative given:
(i) Adequate power: N >= 87 AFIB records confirmed in pre-run checklist.
(ii) Comprehensive reporting: full PPV-vs-coverage curve reported, not
     only the primary operating point.
(iii) Pre-registered: this protocol was committed before touching
      strat_fold 10.

The null establishes the performance ceiling for standard temperature-scaled
selective classification on PTB-XL under 4 GB compute, and advises
practitioners that this approach does not fix the low-PPV problem.

**Headline-inconclusive (m-2 fix per methodology-critic):**
p >= 0.05 AND 95% CI upper bound >= 10 pp — i.e., the test is not
significant but the CI is too wide to rule out a meaningful effect.
This case is treated as **NEITHER positive NOR null**: the headline
result is reported as "underpowered to discriminate; CI too wide".
Action: report all secondary metrics, characterize the wide-CI
direction (positive-leaning vs neutral vs negative-leaning), and
flag in `findings.md` that a larger replication run would resolve.
Do not retire-cancel the track on inconclusive — that is an
analysis-layer interpretation, not a layer-30 cancel trigger.

**Partial positive (report separately):**
If p < 0.05 but effect size < 5 pp: "statistically significant but
clinically small improvement." Report the full curve; let the reader
judge clinical relevance.

**What the result is NOT:**
Regardless of direction, the result does NOT establish that a more
powerful abstention method (conformal, ensemble) would or would not
help. The headline is scoped to temperature-scaling abstention only.
Claims beyond this scope require additional experiments.

---

## 9. Unlock procedure

If this protocol must be changed after locking:

1. Write an unlock note below §9, with:
   - Date
   - Author
   - Specific change proposed
   - Reason the change is necessary
   - Whether the change affects the held-out partition (§3) or
     primary metric (§4)
2. If the change affects the held-out partition or primary metric:
   a critic re-pass is required before re-locking.
3. If strat_fold 10 has already been accessed (the single authorized
   evaluation run has begun), no protocol change is permitted.
   The evaluation proceeds as locked.

---

*(No unlock notes below this line as of 2026-05-02.)*
