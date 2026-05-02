# Reuse sketch — ecg-ppg-realworld (pre-admission aid)

Author: methodologist agent
Date: 2026-05-02
Status: admission-aid sketch only — not a locked methodology

---

## 1. Working scope

Narrowed per shortlist and critic: calibrated abstention for AFib classification
on PTB-XL with patient- and site-disjoint held-out evaluation. Skin-tone
stratification is deferred unless an operative PPG corpus with
Fitzpatrick-or-equivalent labels is identified before admission (critic §critical-2
and §critical-3 block this framing otherwise). The deliverable is an honest
calibration + abstention study, not a new SOTA classifier.

---

## 2. Approach in three bullets

- **Data.** PTB-XL v1.0.3 (PhysioNet, ODC-BY, 21,799 ECGs, 18,869 patients).
  Train/val on strat-II sites; test on held-out site(s) chosen once and
  frozen. Optional second dataset: PhysioNet/CinC 2017 (AF single-lead, MIT
  license) as a cross-cohort probe. No PPG corpus unless skin-tone labels
  confirmed.

- **Model family.** Primary: 1D-ResNet-34 or xresnet1d101 (both trained in
  prior PTB-XL work, param count 3–11 M, fit 4 GB with batch=32 and mixed
  precision). Baseline: logistic regression on hand-crafted RR-interval +
  morphology features via NeuroKit2. Abstention layer: temperature scaling +
  selective-classification threshold swept on a val partition. No FM
  pretraining. No end-to-end transformer training.

- **Eval skeleton.** Primary metric: PPV at a fixed-alert-rate matching
  BASEL inconclusive rate (~19%). Secondary: Brier score, ECE (15-bin
  reliability diagram), AUROC. Report with 95% bootstrap CI over patients.
  Ablation: model with vs without abstention; report abstention rate and
  PPV-at-abstention-rate jointly so the reader sees the trade-off curve.

---

## 3. Shared substrate — promotion side

shared/ is currently empty; no existing components to consume. Promotion
candidates this track would contribute on success:

- **`30-implement/shared/eval/calibration.py`** — functions `brier_score(y_true, y_prob)`,
  `expected_calibration_error(y_true, y_prob, n_bins)`, `reliability_diagram(...)`.
  Interface: numpy arrays in, scalar or figure out. Self-contained; no
  track-specific logic.

- **`30-implement/shared/eval/abstention.py`** — `selective_classification_curve(y_true,
  y_prob, thresholds)` returning (coverage, PPV, F1) triples; `plot_coverage_vs_ppv(...)`.
  Encodes the "abstain when uncertain" protocol so any track with a classifier
  + confidence score can evaluate its abstention behavior without reimplementing.

- **`30-implement/shared/eval/partition.py`** — `patient_disjoint_split(df, id_col,
  site_col, test_frac, seed)` that enforces no patient or site leaks across
  splits. Validates itself by asserting intersection of patient-id sets is
  empty. Reusable by any track with tabular metadata + a patient identifier.

- **`30-implement/shared/data/ptbxl_loader.py`** — thin wrapper around PTB-XL waveform
  files + metadata CSV; returns `(signals, labels, metadata)` in a consistent
  format. Promotes the dataset-access pattern as a reference for other cardiac
  loaders.

---

## 4. Plausible 2nd consumer

**sleep-staging.** The calibration utilities (`calibration.py`,
`abstention.py`) are directly applicable to evaluating a pretrained sleep
stager's epoch-level confidence: ECE per stage, reliability diagrams,
abstention curves where the stager hedges on N1. The partition utility
(`patient_disjoint_split`) applies to any track with subject metadata.

**cross-subject-eeg.** The abstention protocol generalizes to selective
classification in BCI contexts (abstain when the few-shot decoder is
uncertain). Calibration metrics apply to FM-probing experiments where the
EEG model outputs a softmax probability.

**affective-state (if admitted in feature-stability sub-scope).** The
calibration and abstention utilities apply directly to any cross-subject
classification evaluation.

All three other candidates have plausible reasons to consume at least one
promoted utility. The partition utility alone is universally needed.

---

## 5. Cross-track leverage rating

**High.**

The calibration, abstention, and partition utilities are domain-agnostic
once written for PTB-XL and would be consumed by every other candidate track.
The ecg-ppg-realworld track is the most natural first track to build these
because its admitted scope is precisely calibration + abstention, so the
promotion cost is marginal relative to what gets built anyway.
