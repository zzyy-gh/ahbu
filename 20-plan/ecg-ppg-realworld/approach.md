> **Spec:** `10-pain-point/ecg-ppg-realworld/admission.md`

# Approach — ecg-ppg-realworld

**Track:** ecg-ppg-realworld
**Date:** 2026-05-03
**Author:** methodologist agent (re-pass after P-1 underpowering finding)
**Status:** draft — pending critic gate before layer 30

**Dataset pivot note:** PTB-XL was the original target. Pilot P-1 found only 48 AFIB-positive records in PTB-XL (fold-10: 8), approximately 10x below the N = 87 required for 80 % power. Dataset switched to PhysioNet/CinC 2017 (771 AFIB positives, single-lead wearable-grade). Full rationale in `unlock-note-2026-05-03.md`.

---

## Scope statement

Evaluation-diagnostic study on calibrated abstention for wearable-grade AFib classification. The contribution is not a new architecture. It is a disciplined evaluation of whether selective classification (abstention on uncertain inputs) can improve PPV at a clinically motivated fixed alert rate, using a model family that fits in 4 GB VRAM, on a dataset with adequate AFIB-positive counts.

**Headline question:** On wearable-grade single-lead ECG, does calibrated abstention (withholding predictions on uncertain inputs) increase PPV for AFib detection at a fixed coverage rate, relative to a baseline classifier that commits on all inputs?

**Why this matters:** Consumer wearables (Apple Watch, Fitbit) produce AFib alerts with PPVs as low as 32-34 % (Fitbit Heart Study) in general populations. The BASEL Wearable Study found 17-21 % of tracings were inconclusive. A classifier that abstains on the 17-21 % most uncertain inputs and commits on the rest — mirroring the BASEL inconclusive budget — should achieve higher PPV on the committed predictions. Whether this holds, and by how much, is the empirical question.

---

## Shared substrate

### Scan result

`30-implement/shared/` directory does not exist in this worktree. The cross-subject-eeg track defined four promotion candidates (`leakage_audit.py`, `fewshot_curve.py`, `partition.py`, `riemannian_baseline.py`) as future shared artifacts, but they have not been promoted to `shared/` yet (they live in `30-implement/cross-subject-eeg/code/`).

### Consume

- `30-implement/cross-subject-eeg/code/pilots/` VRAM probe methodology: xresnet1d50 confirmed at 0.62 GB VRAM peak on GTX 1650 — but at seq_len=1000, batch=32 (cross-subject-eeg input shape). **CinC 2017 headline uses seq_len=9000 (30 s × 300 Hz, 9× longer)**, so a re-probe on the actual headline input shape is required as P-3 of THIS track before training begins (M-1 fix per critic-v2). Linear extrapolation suggests ~1.4–2.0 GB at batch=8 float32; conservative but unverified.

### Track-specific (not promoted on first pass)

- CinC 2017 loader / preprocessing pipeline.
- Abstention wrappers (temperature scaling + MaxSoftmax + conformal prediction set size).
- PPV-at-coverage curve implementation.

### Promote on completion (plausible 2nd consumer annotated)

- `30-implement/shared/eval/ppv_at_coverage.py` — PPV-at-coverage curve with bootstrap CI. Plausible 2nd consumer: any cardiac classification track (sleep-staging if it evaluates on imbalanced rhythm labels).
- `30-implement/shared/eval/calibration.py` — Brier score, expected calibration error (ECE), reliability-diagram generator. Plausible 2nd consumer: cross-subject-eeg (confidence calibration for FM predictions); sleep-staging.
- `30-implement/shared/eval/abstention.py` — selective-classification abstention wrapper: given a scoring function and a coverage target, returns a threshold and the PPV/sensitivity/abstention-rate on a held-out split. Plausible 2nd consumer: cross-subject-eeg (BCI illiteracy abstention); any track with imbalanced binary classification.

Promotion is deferred until at least one second consumer is confirmed active. These are candidates, not commitments.

---

## Dataset

### Primary dataset

**PhysioNet / Computing in Cardiology Challenge 2017 (CinC 2017)**

- Full name: "AF Classification from a Short Single Lead ECG Recording: The PhysioNet/Computing in Cardiology Challenge 2017"
- PhysioNet DOI: https://physionet.org/content/challenge-2017/1.0.0/
- Version: 1.0.0 (the canonical training set; test set labels were not publicly released)
- License: Open Data Commons Attribution License v1.0 (ODC-BY). No data-use agreement required. Freely downloadable.
- Access: `wget -r -N -c -np https://physionet.org/files/challenge-2017/1.0.0/` or via the PhysioNet web interface. Training set ~150 MB.
- Content: 8,528 single-lead ECG recordings, 9-61 seconds, sampled at 300 Hz. Labels assigned by expert cardiologists.
- Class distribution (training set):

  | Class | N | Fraction |
  |---|---|---|
  | Normal sinus rhythm | 5,154 | 60.4 % |
  | Atrial fibrillation | 771 | 9.0 % |
  | Other rhythm | 2,557 | 30.0 % |
  | Too noisy | 46 | 0.5 % |
  | **Total** | **8,528** | |

- Recording device: AliveCor Kardia single-lead handheld ECG monitor. This is directly comparable to wearable / consumer-grade ECG (Apple Watch single-lead ECG uses a comparable 1-lead surface ECG recording principle).
- Signal characteristics: 300 Hz, 16-bit, variable length 9-61 s. Mean length approximately 30 s.

### Why CinC 2017 replaces PTB-XL

PTB-XL AFIB-positive counts (pilot P-1): 48 total records across all 21,799 ECGs (fold-10: 8 records). Required N = 87 for 80 % power at the design effect. Underpowered by ~10x. Full explanation in `unlock-note-2026-05-03.md`. CinC 2017 provides 771 AFIB-positive records, adequate for the power requirement. The single-lead modality is more representative of the consumer-wearable constituency than 12-lead clinical ECG.

### Held-out partition

CinC 2017 training set (8,528 records) is the only labeled data available (test-set labels were never released). The partition is defined in `protocol-lock.md` §3.

**Planned split:**
- Dev split (80 % of training set, stratified by class): 6,822 records, approximately 617 AFIB positives.
- Held-out test split (20 % of training set, stratified by class): 1,696 records, approximately 154 AFIB positives. (Minor partition-size fix per critic-v2 m: 20 % of 8,482 = 1,696.4, not 1,706.)

**Stratification:** split is stratified by the four-class label to preserve AFIB prevalence in both splits. Random seed = 42. `partition.py:subject_disjoint_split()` called on record IDs (CinC 2017 does not provide patient-level IDs in the public release, so record-level stratification is used; this is documented as a limitation — see risk register R-4).

**Held-out discipline:** the 20 % test split is defined at partition time and not examined until the single authorized headline run. All model selection, threshold tuning, calibration fitting, and ablations run on the dev split.

### Secondary dataset (cross-dataset abstention probe, pilot only)

**CinC 2020 single-lead subset (PTB-XL physionet)**

For a pilot probe only (not headline): train calibrated abstainer on CinC 2017 dev; evaluate abstention and PPV on CinC 2020 single-lead recordings (the CinC 2020 training data includes single-lead ECGs from multiple sites alongside 12-lead). This is a cross-dataset domain-generalization probe. Results from this probe are preliminary only and labeled as such. The headline is CinC 2017 test split only.

---

## Preprocessing

**Pipeline (CinC 2017 single-lead ECG)**

All recordings at 300 Hz. No resampling required. Pipeline implemented in `30-implement/ecg-ppg-realworld/code/preprocess.py`.

1. **Load WFDB record:** `wfdb.rdrecord()`. Extract single-lead voltage trace.
2. **Bandpass filter:** 0.5-40 Hz, 4th-order Butterworth zero-phase. Removes DC drift (below 0.5 Hz) and high-frequency noise / EMG (above 40 Hz). AFib discriminative features (P-wave absence, irregular RR) live in 0.5-30 Hz; extending to 40 Hz preserves beat morphology without EMG contamination.
3. **Normalize:** z-score per recording (subtract mean, divide by std). Handles inter-recording amplitude variation from the AliveCor device (variable skin contact, lead placement).
4. **Fixed-length window extraction:** split each recording into non-overlapping 30-second windows (9,000 samples at 300 Hz). Shorter recordings padded with zeros to 9,000 samples; recordings shorter than 9 s (2,700 samples) are flagged and excluded. Rationale: 30 s is the minimum window used in clinical AFib detection practice; it captures multiple AF episodes and several RR-interval variation cycles.
5. **Label assignment:** each window inherits the recording-level label. This is a simplification — within a 30-second window, label quality is constrained by the recording-level ground truth. Documented as a limitation (a recording labeled "Other rhythm" may contain a brief AF episode).
6. **Noisy-record exclusion:** the 46 "Too noisy" recordings are excluded from all training and evaluation. They are not included in the dev or test splits. This reduces confounding between classification failure and noise-driven abstention.

**Software:** wfdb (Python), scipy (filtering), numpy. Versions pinned in `30-implement/ecg-ppg-realworld/code/requirements.txt`.

**Why not segment by R-peaks / beat-level:** beat-level segmentation requires a reliable QRS detector, which itself fails on AF (irregular rhythm). Window-level segmentation avoids this circularity. Recording-level models on fixed-length windows are standard in CinC 2017 entries.

---

## Model family

### Feasibility check (4 GB VRAM envelope)

**xresnet1d50:** cross-subject-eeg pilot P-3 confirmed 0.62 GB VRAM peak on GTX 1650 at batch=32, float32. This was with a comparable 1D input (EEG epoch ~2 s). CinC 2017 input is 9,000 samples (30 s at 300 Hz), single channel. Memory scales with input length; at batch=8 float32 with 9,000 samples, estimated VRAM ~1.5-2.0 GB (linear scaling from the P-3 measurement). Feasible.

**Temperature scaling + MaxSoftmax abstainer:** post-hoc calibration. No additional VRAM (runs on logits in CPU after inference). Trivially feasible.

**Conformal prediction (RAPS / APS):** post-hoc, no additional VRAM. Feasible.

Kill criterion: if xresnet1d50 at batch=8 float32 exceeds 3.2 GB VRAM on CinC 2017 input, reduce to batch=4 or switch to float16. If neither fits, cancel deep model and fall back to logistic regression on hand-crafted features (LR-HCF). LR-HCF is the kill-criterion fallback, not a planned baseline (see risk register R-3).

### Model A — Primary

**xresnet1d50 (1D ResNet variant, Strodthoff et al. 2021 implementation)**

- Architecture: 1D ResNet-50 variant adapted for ECG (xresnet1d50 from the PTB-XL benchmark codebase, https://github.com/helme/ecg_ptbxl_benchmarking).
- Input: (batch, 1, 9000) — one channel, 9,000 samples.
- Output: 4-class softmax logits (Normal / AF / Other / Noisy). Noisy class is excluded from test evaluation (see preprocessing §6), but retaining it in training prevents the model from being forced to classify noisy inputs as one of the three meaningful classes.
- Training: cross-entropy loss, Adam optimizer (lr=1e-3, cosine decay), batch=8, 50 epochs with early stopping (patience=10, monitored on dev-split AUROC for the AF class). Epochs that change the held-out split are not allowed.
- Calibration: temperature scaling (Guo et al. 2017) fitted on dev split AF-vs-rest binary calibration.

Rationale: xresnet1d50 is the leading architecture in the PTB-XL multi-label benchmark (Strodthoff 2021). It is the standard 1D ECG CNN baseline in the community. Using it is disciplined; it provides a credible model for the abstention study without requiring novel architecture work.

### Model B — Baseline

**Logistic regression on hand-crafted ECG features (LR-HCF)**

- Features: HRV-derived features from RR intervals (mean RR, SDNN, RMSSD, pNN50), plus frequency-domain features (LF/HF ratio, spectral entropy), plus morphological features (P-wave presence proxy via autocorrelation peak in expected P-wave window, QRS duration estimated via WFDB XQRS). Total ~20 features per 30-second window.
- Classifier: scikit-learn LogisticRegression with L2 regularization (C tuned on dev split via 5-fold CV).
- Calibration: Platt scaling (logistic calibration) on dev split.
- Rationale: strong interpretable baseline. If xresnet1d50 abstainer does not outperform a calibrated LR-HCF abstainer, the deep model adds no value beyond feature engineering for this use case. HCF baseline is also compute-trivial and runs fully on CPU.

### Model C — Abstention mechanism variants (within primary model)

Three abstention mechanisms applied to xresnet1d50 outputs:

1. **MaxSoftmax threshold:** abstain if max(softmax(logits)) < threshold. Threshold tuned on dev split to achieve the target coverage rate (17-21 % abstention budget matching BASEL inconclusive rate).
2. **Temperature-scaled MaxSoftmax:** same as above but softmax applied to logits / T where T is the temperature-scaling parameter fitted on dev split. Calibration improves threshold stability.
3. **Conformal prediction (RAPS):** Regularized Adaptive Prediction Sets (Angelopoulos et al. 2021). Calibrated on dev split; abstain if |prediction set| > 1 (multi-class uncertainty). Coverage guarantee: empirical miscoverage <= alpha (alpha tuned to achieve 17-21 % abstention budget).

These three mechanisms are compared within the same base model. The comparison is an ablation, not a three-way primary metric competition. The primary metric is computed for each mechanism; the comparison answers "does calibration or conformal coverage improve PPV over naive MaxSoftmax?"

---

## Evaluation protocol

### Primary framing

**AF vs non-AF binary classification.** The four-class model is evaluated in binary mode: AF positive vs (Normal + Other) negative. The "Too noisy" class is excluded from evaluation (see preprocessing §6). This binary framing directly addresses the consumer-wearable use case (alert / no-alert).

### Selective classification (abstention) evaluation

For each abstention mechanism:

1. Compute the abstention threshold on the dev split that achieves the target coverage rate (1 - target_abstention_rate). Target abstention rates: 0 % (baseline, no abstention), 10 %, 17 %, 21 %. The 17 % and 21 % thresholds match the lower and upper bounds of the BASEL inconclusive rate.
2. On the held-out test split, apply the threshold fitted on the dev split (no further threshold adjustment). Report:
   - PPV on committed predictions (the primary metric).
   - Sensitivity on committed predictions.
   - Abstention rate (fraction of test records on which the model abstains).
   - Coverage (1 - abstention_rate).
   - F1 on committed predictions.
3. **PPV-at-coverage curve:** for both xresnet1d50 and LR-HCF, compute PPV at coverage values {1.0, 0.95, 0.90, 0.85, 0.83, 0.79} (corresponding to abstention rates 0, 5, 10, 15, 17, 21 %). Plot curve with 95 % bootstrap CI at each coverage point.

### Held-out partition discipline

The held-out 20 % test split is touched exactly once, for the single authorized headline run. All threshold tuning, calibration fitting, temperature scaling, conformal calibration set construction — all of these use the dev split only.

**What "touching the held-out split" means:**
- Loading test-split raw data into memory.
- Computing predictions or probabilities on test-split records.
- Reading any test-split statistic.

Checking file existence does not count. The single authorized run is preceded by the pre-run checklist defined in `protocol-lock.md` §5.

### Metrics

**Primary metric:** PPV of the AF class at 17 % abstention (the lower BASEL bound), on the held-out test split, for the temperature-scaled MaxSoftmax abstainer applied to xresnet1d50.

Reported as: "XX.X % (95 % CI: YY.Y–ZZ.Z %, N_committed = N)"

**Secondary metrics (reported, not primary):**
- PPV at 0 % abstention (baseline — model commits on all inputs).
- PPV at 21 % abstention (upper BASEL bound).
- Sensitivity at 17 % abstention.
- Area under the PPV-coverage curve (AUPC) for xresnet1d50 and LR-HCF.
- Brier score on full test set (calibration quality).
- Expected calibration error (ECE) before and after temperature scaling.
- AUROC for AF detection (standard discrimination metric, reported for comparability with published CinC 2017 results).

**Reporting format:** "XX.X % (95 % CI: YY.Y–ZZ.Z %, N=N)" on every number. Never a point estimate without CI.

### Cross-subject structure

CinC 2017 does not provide patient IDs in the public release. All splits are record-level stratified. "Cross-subject" cannot be tested strictly. This is documented as a limitation in `risk-register.md` R-4 and in `limitations.md` post-headline. The record-level held-out split is not equivalent to a patient-disjoint held-out; if multiple records from the same patient appear in both splits, there is potential label leakage (same patient's rhythm in both train and test). Mitigation: record-level random split at fixed seed is standard for CinC 2017; this limitation is inherited from the dataset, not introduced by this protocol.

### Statistical test

One-sided test for primary hypothesis: PPV at 17 % abstention > PPV at 0 % abstention.

**Test:** McNemar's test on the paired committed-prediction confusion matrices (comparing the classifier-with-abstention vs classifier-without-abstention on the same test records that both make a prediction). One-sided, H1: abstention improves PPV.

**Significance threshold:** p < 0.05 (single test on primary metric; no correction needed).

**Effect size:** absolute PPV improvement in percentage points.

**Interpretation rule:**
- p < 0.05 AND PPV improvement >= 5 pp: "statistically significant and clinically meaningful improvement from abstention."
- p < 0.05 AND PPV improvement < 5 pp: "statistically significant but small improvement."
- p >= 0.05: "no statistically significant PPV improvement from abstention at 17 % coverage rate."

A null result is informative: it means calibrated abstention does not reliably improve PPV for wearable-grade AFib detection at this coverage budget, which is itself a contribution given the clinical motivation.

---

## Ablations

All ablations run on the dev split only. None touch the held-out test partition.

**Ablation 1: Abstention mechanism comparison**

Procedure: compare MaxSoftmax (uncalibrated), temperature-scaled MaxSoftmax, and conformal RAPS at identical coverage targets on the dev split. Report PPV-at-coverage curve for all three.
Hypothesis: temperature scaling improves the PPV-coverage curve relative to uncalibrated MaxSoftmax; conformal RAPS achieves similar or better PPV but with a coverage guarantee. If MaxSoftmax already achieves near-optimal PPV, calibration adds no value.

**Ablation 2: Model depth (xresnet1d50 vs xresnet1d18)**

Procedure: repeat primary training with xresnet1d18 (smaller architecture, ~6 M params vs ~25 M params). Compare PPV-at-coverage curves.
Hypothesis: the smaller model performs comparably or better on this relatively simple binary classification task with moderate data size (6,822 dev records). If xresnet1d18 matches xresnet1d50, the lighter model is preferred for deployment.

**Ablation 3: Window length sensitivity**

Procedure: repeat primary evaluation with 10-second windows (3,000 samples) and 60-second windows (padded/truncated). Compare PPV-at-coverage curves.
Hypothesis: longer windows improve AFib detection confidence (more RR-interval variation captured), leading to better calibration and higher PPV at a given abstention rate. If 10-second windows perform comparably, shorter windows (closer to Apple Watch Episode recording length) are sufficient.

**Ablation 4: Feature-engineered abstainer vs deep abstainer**

Procedure: apply all three abstention mechanisms to LR-HCF (logistic regression baseline) and compare PPV-at-coverage curves with xresnet1d50 + same abstention mechanisms.
Hypothesis: if the deep model's better discrimination also produces better-calibrated confidence scores, xresnet1d50 + temperature-scaled MaxSoftmax achieves higher PPV at the 17 % abstention budget than LR-HCF + any abstention mechanism. If not, the deep model's calibration advantage is spurious.

---

## Uncertainty reporting

- **Bootstrap CI:** All PPV, sensitivity, and F1 values reported with 95 % bootstrap CI (n=2000 resamples, stratified by class, random_state=42).
- **PPV-coverage curve:** CI at each coverage point computed independently via bootstrap.
- **Reporting format:** "XX.X % (95 % CI: YY.Y–ZZ.Z %, N=N)" on all primary and secondary metrics.
- **Multi-seed training:** three independent training runs with random seeds {42, 1337, 2025}; report mean and std of primary metric across seeds. If std > 2 pp, investigate instability.

---

## Compute budget

| Task | Hardware | Estimated time |
|---|---|---|
| CinC 2017 data download (~150 MB) | local | 5 min |
| Preprocessing (bandpass, windowing, split) | CPU | 15 min |
| LR-HCF feature extraction (dev set) | CPU | 30 min |
| LR-HCF cross-validation + calibration (dev) | CPU | 30 min |
| xresnet1d50 training, 50 epochs, batch=8 | GTX 1650 | 2-3 hr per seed |
| Temperature scaling calibration (dev) | CPU | < 5 min |
| Conformal RAPS calibration (dev) | CPU | < 5 min |
| Ablations 1-4 (dev split only) | CPU + GPU | 4-6 hr |
| Headline run (test split, one-time) | CPU + GPU | < 1 hr |
| Bootstrap CI computation (n=2000) | CPU | 30 min |
| **Total (3 training seeds + ablations + headline)** | CPU + GPU | **~14-18 GPU-hours** |

Total GPU budget: approximately 15 GPU-hours (GTX 1650). Feasible locally; no external compute required.

**Fits 4 GB envelope:** yes. xresnet1d50 at batch=8 float32, input=(8,1,9000) estimated ~1.5-2.0 GB VRAM (based on cross-subject-eeg P-3 scaling from batch=32, shorter input, 0.62 GB). If batch=8 exceeds 3.2 GB, reduce to batch=4 (estimated ~1.0 GB VRAM, 2x training time).

### Time to first honest result

- Week 1: data download, preprocessing, LR-HCF baseline, pilot VRAM probe for xresnet1d50 on CinC 2017 input. First dev-split PPV-at-0%-abstention from LR-HCF.
- Week 2: xresnet1d50 training (3 seeds), temperature scaling. Dev-split PPV-at-coverage curve for primary model. Ablations 1 and 2.
- Week 3: Ablations 3 and 4. Conformal RAPS. Cross-dataset pilot probe (CinC 2020). Finalize threshold from dev split. Write pre-run checklist.
- Week 4: single authorized headline run on test split. Statistical test. Results to `30-implement/ecg-ppg-realworld/results.md`.

**First honest result: week 4.**

---

## Novelty

**What is genuinely novel:**

The specific combination of (a) wearable-grade single-lead ECG (CinC 2017 AliveCor recordings), (b) PPV-at-fixed-alert-rate as the primary metric (calibrated to the BASEL 17-21 % inconclusive-rate budget), and (c) comparative evaluation of calibration methods (uncalibrated MaxSoftmax vs temperature scaling vs conformal RAPS) under a held-out design that touches the test split exactly once.

Prior work (Smole 2023, NCA 2024, Barandas 2024) evaluates abstention on ECG as accuracy-under-rejection. None uses PPV-at-coverage as the primary metric, and none is scoped to the consumer-wearable AFib false-positive problem. The BASEL 17-21 % inconclusive-rate anchor for the coverage budget is this track's specific clinical grounding.

**What is standard and intentionally so:**

xresnet1d50: the PTB-XL benchmark standard architecture. Using it is disciplined. Temperature scaling: the canonical post-hoc calibration method. CinC 2017: a well-characterized public dataset. AUROC: reported for comparability with published results.

**What is exploratory (pilot only, not pre-registered):**

Cross-dataset abstention probe (CinC 2020 single-lead subset). Longer fine-tuning schedules. ECG-FM frozen encoder as an alternative feature extractor (if a suitable wearable-grade pre-trained model exists and fits in 4 GB).
