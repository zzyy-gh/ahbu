# Reuse sketch — sleep-staging (pre-admission aid)

Author: methodologist agent
Date: 2026-05-02
Status: admission-aid sketch only — not a locked methodology

---

## 1. Working scope

Narrowed per shortlist: calibration and cohort-stratified evaluation of a
pretrained sleep stager (U-Sleep or equivalent checkpoint) on a held-out
clinical population. Specifically: quantify ECE, per-stage reliability
diagrams, and per-AHI-band F1 on a dataset that is *not* in U-Sleep's
training set. HRV-only EEG-less staging on MESA is an optional second
experiment if NSRR DUA arrives. No retraining of U-Sleep from scratch.

---

## 2. Approach in three bullets

- **Data.** Primary: Sleep-EDF-Cassette v1 (PhysioNet ODC-BY, ~78 subjects
  healthy adults, 2-channel EEG) for pipeline development; Dreem-DOD-H/O
  (CC-BY 4.0 with Dreem registration, ~80 subjects healthy + OSA) as
  out-of-distribution clinical probe. SHHS/MESA (NSRR DUA) pursued in
  parallel as stretch goal — if DUA takes >4 weeks, the sketch remains valid
  on Dreem-DOD alone. HMC PSG 2018 (PhysioNet, no DUA) as additional
  cross-cohort site.

- **Model family.** Primary: frozen U-Sleep checkpoint (trained on 15,660
  PSGs; inference fits GTX 1650 easily — no backprop). Calibration head:
  temperature scaling fitted on a held-out validation subset of Dreem-DOD.
  Baseline: random forest on HRV + spectral features extracted via MNE-Python
  or NeuroKit2 (EEG-less or single-channel path). No foundation-model
  pretraining.

- **Eval skeleton.** Primary metric: per-stage macro-F1 on Dreem-DOD test
  partition, held-out subjects. Secondary: ECE per stage, reliability
  diagrams, performance stratified by AHI band (none / mild / moderate /
  severe), comparison against the human-rater kappa ceiling (0.76 overall,
  0.24 N1). Bootstrap CI over subjects. Ablation: uncalibrated vs
  temperature-scaled stager; with vs without the Dreem cohort as in-domain
  fine-tuning data (measures calibration transfer gap).

---

## 3. Shared substrate — promotion side

shared/ is currently empty; no existing components to consume. Promotion
candidates this track would contribute on success:

- **`30-implement/shared/eval/calibration.py`** — same module as ecg-ppg-realworld sketch
  proposes (`brier_score`, `expected_calibration_error`,
  `reliability_diagram`). If ecg-ppg-realworld is admitted first, this track
  consumes it; if sleep-staging is first, this track promotes it.

- **`30-implement/shared/eval/cohort_stratifier.py`** — `stratified_report(y_true,
  y_pred, y_prob, stratum_col, stratum_vals)` that produces per-stratum F1,
  ECE, and confusion matrix. Stratum column is arbitrary (AHI band, age
  decile, site, skin-tone proxy). Interface is domain-agnostic once the
  stratum metadata is provided. Any track with subgroup evaluation needs this.

- **`30-implement/shared/eval/partition.py`** — `subject_disjoint_split(df, subject_col,
  test_frac, stratify_col, seed)`. Same utility as ecg-ppg-realworld sketch
  proposes; if both are promoted by different tracks they should be merged
  into a single module.

- **`30-implement/shared/data/sleep_edf_loader.py`** — loader for Sleep-EDF-Cassette
  returning `(eeg_epochs, stage_labels, subject_metadata)` at 30-second
  granularity, compatible with MNE-Python Raw objects. Reference pattern for
  epoch-based biosignal datasets.

- **`30-implement/shared/models/hrv_feature_pipeline.py`** — `extract_hrv_features(rr_intervals,
  window_sec, step_sec)` returning a feature matrix of time-domain and
  spectral HRV features via NeuroKit2. Reusable by any track working with
  cardiac inter-beat intervals (ecg-ppg-realworld, affective-state
  arousal-only scope, cross-subject-eeg sleep-staging sub-scope).

---

## 4. Plausible 2nd consumer

**ecg-ppg-realworld.** The HRV feature pipeline (`hrv_feature_pipeline.py`)
is directly reusable for HRV-validity work on PTB-XL / PPG-DaLiA; the
calibration module is consumed as-is. The cohort stratifier applies to
site-stratified PTB-XL evaluation.

**cross-subject-eeg.** The subject_disjoint_split utility applies directly;
the cohort_stratifier could stratify by paradigm (MI vs P300 vs SSVEP) or
hardware condition, which mirrors its stratum-column design.

**affective-state (if admitted).** The HRV feature pipeline covers the
cardiac arm of affective-state feature extraction; the cohort stratifier
applies to cross-dataset evaluation.

Multiple plausible 2nd consumers exist. The HRV pipeline is the most valuable
unique contribution of this track to shared/ because it is not clearly
produced by any other candidate on their own terms.

---

## 5. Cross-track leverage rating

**High.**

The HRV feature pipeline is a unique contribution no other candidate produces
naturally, and it is consumed by at least three of the four tracks. The
calibration and cohort-stratifier utilities duplicate what ecg-ppg-realworld
would also produce — meaning the leverage depends partly on sequencing: if
sleep-staging is second, it consumes rather than builds those; if it is first,
it contributes them. Either way the net leverage is high. The one liability is
the NSRR DUA lag, which can delay first results by 4-8 weeks on the SHHS/MESA
stretch goal, but the core sketch (Dreem-DOD + Sleep-EDF) is DUA-free.
