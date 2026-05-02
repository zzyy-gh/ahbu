# Reuse sketch — affective-state / feature-stability sub-scope (pre-admission aid)

Author: methodologist agent
Date: 2026-05-02
Status: admission-aid sketch only — not a locked methodology

---

## 1. Working scope

Narrowed per critic's rescue of the candidate: physiological feature
stability audit across affective-state datasets. Specifically: replicate
and extend the arXiv:2508.10561 finding (2 of 164 features reproducible
across cardiac + EDA signals on arousal) across DEAP, WESAD, and DREAMER
using consistent preprocessing, subject-disjoint splits, and statistical
correction. Deliverable: a reproducibility map of cardiac + EDA features
for arousal, with honest effect-size bounds. This scope is not covered by
Brookshire 2024 (DNN leakage) or Apicella 2024 (cross-subject review).

---

## 2. Approach in three bullets

- **Data.** WESAD (15 subjects, ECG + EDA + EMG + RESP + ACC, PhysioNet
  CC-BY), DEAP (32 subjects, EEG + peripheral; available on request,
  academic use), DREAMER (23 subjects, EEG + ECG + EDA, available on
  request). All three are small, public, and well-documented. No
  registration or DUA required for WESAD; DEAP and DREAMER require
  brief request forms (academic standard, not DUA-level friction). EEG
  channels de-emphasized — the audit focuses on cardiac (ECG-derived
  RR intervals, HRV spectral) and EDA features, where the 2-of-164
  finding is most dramatic and most consequential for construct validity.

- **Model family.** Not a classification task. The primary analysis is
  a cross-dataset feature-stability audit: for each of the 164 candidate
  features (time-domain HRV, spectral HRV, EDA SCR rate, SCL baseline,
  etc.), compute Spearman correlation with arousal ratings in each dataset
  independently, apply Bonferroni or FDR correction, and report which
  features replicate. Secondary: a logistic regression / SVM classifier
  using only the reproducible feature subset vs the full feature set
  (measures whether stable features retain any predictive signal). No
  deep learning. Compute budget: negligible — sklearn + NeuroKit2 on CPU.

- **Eval skeleton.** Primary metric: number of features with statistically
  significant (alpha=0.05 FDR-corrected) consistent-direction association
  with arousal across all three datasets (replication rate). Secondary:
  cross-subject LOSO AUC of the reproducible-feature classifier vs full
  feature set, with bootstrap CI. Ablation: Bonferroni vs BH correction;
  correlation threshold sweep. Expected finding: replication rate is very
  low (consistent with arXiv:2508.10561); this is the contribution — a
  multi-dataset confirmation with methodology exposed.

---

## 3. Shared substrate — promotion side

shared/ is currently empty; no existing components to consume. Promotion
candidates this track would contribute on success:

- **`30-implement/shared/data/hrv_eda_feature_extractor.py`** — `extract_features(signal,
  signal_type, fs, window_sec)` where `signal_type` in {"ecg", "eda",
  "ppg"}. Returns a named feature DataFrame with a fixed, documented
  feature schema (the same 164-feature schema from arXiv:2508.10561,
  or a documented subset). Reusable by any track that needs HRV or EDA
  features. Note: overlaps with `30-implement/shared/models/hrv_feature_pipeline.py`
  proposed by sleep-staging sketch — these should be merged into one
  canonical extractor if both tracks are admitted.

- **`30-implement/shared/eval/feature_stability.py`** — `cross_dataset_correlation(
  feature_df_list, target_col, correction_method)` returning a stability
  report DataFrame with per-feature (rho, p_corrected, consistent_sign)
  across datasets. `plot_stability_heatmap(...)`. This is a general-purpose
  feature-reproducibility diagnostic, applicable to any track that wants to
  audit whether its hand-crafted features are stable across cohorts before
  committing to a model.

- **`30-implement/shared/eval/partition.py`** — subject_disjoint_split as above; this
  track would consume it if already promoted, or promote if first.

The feature_stability module is the most unique contribution of this track
to shared/ — no other candidate builds this, and it is not domain-specific
to affective state.

---

## 4. Plausible 2nd consumer

**ecg-ppg-realworld.** A feature-stability audit of RR-interval and HRV
features across PTB-XL and PPG-DaLiA cohorts is an honest pre-modeling check:
are the features that survive across the training-domain also stable in the
test-domain? The `cross_dataset_correlation` module directly enables this.

**sleep-staging.** HRV feature stability across Sleep-EDF and Dreem-DOD
(healthy vs OSA cohorts) is a legitimate methodological question: which
spectral HRV features are stable across AHI bands before being used in an
HRV-only staging classifier?

**cross-subject-eeg (EEG arm, not HRV arm).** The feature_stability module
is transferable to EEG band-power features: how stable are alpha/beta/theta
band powers across subjects and datasets before being used in a motor-imagery
classifier? This is a direct analogue of the 2-of-164 HRV/EDA finding,
applied to EEG.

Multiple plausible 2nd consumers exist. However, the use cases are somewhat
more indirect than for ecg-ppg-realworld's calibration tools or
cross-subject-eeg's leakage audit — they require the downstream track to
actively choose to run a feature stability pre-check, which may or may not
be part of their methodology plan.

---

## 5. Cross-track leverage rating

**Medium.**

The feature_stability module is a genuine, unique contribution not produced
by any other candidate, and it has plausible consumers in all three other
tracks. However, its leverage is contingent: it is most valuable if other
tracks adopt a "feature audit before model" discipline, which is not
mandated by their own pain-point scope. The HRV/EDA extractor overlaps with
sleep-staging's HRV pipeline — the net new contribution is the
feature_stability auditor itself. The admitted scope (arousal-only, cardiac
+ EDA, three small datasets) is narrow enough that the track's own scientific
contribution is modest; most of its admission case rests on the
sub-scope-is-non-redundant argument, which the critic supports but the
shortlist flagged as carry-high-redundancy-risk. This track is lower
admission priority than the other three unless the feature-stability
contribution is confirmed non-redundant with arXiv:2508.10561 before
admission.
