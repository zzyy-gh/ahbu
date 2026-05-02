# Reuse sketch — cross-subject-eeg (pre-admission aid)

Author: methodologist agent
Date: 2026-05-02
Status: admission-aid sketch only — not a locked methodology

---

## 1. Working scope

Narrowed per critic's un-deferral: evaluation-diagnostic study on
cross-subject motor-imagery decoding with subject-, dataset-, and ideally
hardware-disjoint splits. The primary contribution is a leakage-clean
benchmarking protocol on MOABB + a foundation-model probe (e.g., LaBraM
frozen features) compared against a strong Riemannian baseline (MDM),
with 0/1/5/20-shot calibration curves and per-subject distributions. No FM
pretraining. Not a new architecture — the contribution is the honest
evaluation program described in §6 of the candidate file.

---

## 2. Approach in three bullets

- **Data.** MOABB motor-imagery datasets (BCI Competition IV-2a, BNCI2014_001,
  and >=1 additional paradigm; all MOABB-accessible, most CC-licensed or
  publicly downloadable). MOABB version pinned. Datasets split so no subject
  appears in both train and test; pre-training corpus of any FM checkpoint
  must not overlap with the test set (pre-training overlap audit required per
  candidate §6 and EEG-FM-Bench finding).

- **Model family.** Baseline A: Riemannian MDM (Minimum Distance to Mean
  on covariance matrices via pyRiemann) — this is MOABB's strongest
  within-session learner and a demanding cross-subject baseline. Baseline B:
  subject-adversarial FBCSP (Filter Bank CSP, the canonical MI feature).
  Primary: LaBraM frozen encoder (open weights, ICLR 2024) as a feature
  extractor with a linear head fitted on k-shot examples per target subject.
  All three fit GTX 1650 with room to spare.

- **Eval skeleton.** Primary metric: mean LOSO accuracy across datasets, at
  each shot level (0, 1, 5, 20) with 95% bootstrap CI. Secondary: per-subject
  accuracy distribution (to expose BCI-illiteracy bimodality), Riemannian
  baseline delta (FM minus MDM). Ablation: with vs without electrode-dropout
  (montage mismatch robustness), pre-training-overlap-removed vs full FM
  checkpoint (tests whether FM gains are genuine or leakage-driven).

---

## 3. Shared substrate — promotion side

shared/ is currently empty; no existing components to consume. Promotion
candidates this track would contribute on success:

- **`30-implement/shared/eval/leakage_audit.py`** — `check_subject_overlap(train_ids,
  test_ids)`, `check_dataset_overlap(pretrain_datasets, eval_datasets)`,
  `report_leakage_summary(...)`. The pre-training-overlap audit is a
  reusable diagnostic: given a list of dataset names or subject IDs used
  in FM pretraining and a proposed evaluation set, flag any intersection.
  This is the most distinctive evaluation utility this track produces —
  nothing equivalent exists in shared/ yet and no other candidate
  naturally builds it.

- **`30-implement/shared/eval/fewshot_curve.py`** — `fewshot_accuracy_curve(model,
  support_sets, query_sets, shot_levels=[0,1,5,10,20])` returning a
  DataFrame of (shot, accuracy, ci_low, ci_high) per subject; `plot_fewshot_curve(...)`.
  Generalizes beyond EEG: any track evaluating calibration or performance
  as a function of labeled examples per new subject/patient can use this.

- **`30-implement/shared/eval/partition.py`** — `subject_disjoint_split(...)` as in
  the other sketches. If already promoted by an earlier track, this track
  consumes it; if cross-subject-eeg is first, it promotes the implementation.

- **`30-implement/shared/models/riemannian_baseline.py`** — `fit_mdm(X_train, y_train)`,
  `predict_mdm(model, X_test)` wrapping pyRiemann MDM with a consistent
  sklearn-compatible interface. A strong, fast EEG baseline that any
  EEG-facing track (sleep-staging, affective-state) can use without
  reimplementing.

---

## 4. Plausible 2nd consumer

**affective-state (if admitted in feature-stability sub-scope).** The
leakage_audit module directly targets the affective-state leakage problem
(Brookshire 2024, trial-level leakage). The fewshot_curve module applies
to calibration-cost reporting in affective-state cross-subject eval. The
Riemannian baseline is applicable to EEG-based arousal classification.

**sleep-staging.** The fewshot_curve module applies to U-Sleep calibration
evaluation: how much per-subject data closes the gap on a new clinical cohort.
The leakage_audit applies to pre-training overlap checks if any FM-pretrained
stager is evaluated. The Riemannian baseline is not directly applicable
(epoch-based not trial-based) but the partition utility is.

**ecg-ppg-realworld.** The fewshot_curve module is re-expressible as a
calibration-cost curve: how many labeled patient examples are needed for the
abstention threshold to stabilize. The leakage_audit concept (patient-overlap
check) is a specialization of the subject-overlap check.

The leakage_audit is the unique and most broadly applicable contribution of
this track — it addresses the pre-training/eval overlap problem that
EEG-FM-Bench named but did not operationalize as a reusable tool.

---

## 5. Cross-track leverage rating

**High.**

The leakage audit and few-shot curve utilities are the most distinctive
reusable contributions across the four candidates, and both are consumed by
multiple other tracks. The Riemannian baseline is a universally applicable
EEG strong-baseline that would otherwise be re-implemented in every
EEG-facing track. The main leverage risk is that the admitted scope is
"honest evaluation of existing FMs," which, if it yields a purely null
result (FMs not better than Riemannian cross-subject), is itself a finding
— and the evaluation tooling still promotes regardless of result direction.
