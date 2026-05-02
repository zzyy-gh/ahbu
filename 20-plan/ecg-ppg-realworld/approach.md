> **Spec:** `10-pain-point/ecg-ppg-realworld/admission.md`

# Approach — ecg-ppg-realworld

**Track:** ecg-ppg-realworld
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

---

## Scope statement

Calibrated-abstention study for AFib classification on PTB-XL.
The contribution is NOT a new classifier or a new SOTA number.
The contribution is an honest calibration and selective-classification
protocol that asks: does adding a calibrated abstention mechanism
improve PPV at a fixed alert rate that a clinician would actually
accept, and by how much?

The specific novelty claim, narrowed per the gap-closing pass
(candidate.md §Gap-closing 2026-05-02 Gap 2) and defensibility
critic advisory (critic-defensibility.md §1):

> **PPV-at-fixed-alert-rate** as the primary evaluation metric,
> calibrated against the BASEL Wearable Study's observed 17–21%
> inconclusive rate, evaluated on PTB-XL held-out with a
> patient-disjoint split — framing not found in Smole 2023,
> NCA 2024, or Barandas 2024, which all use accuracy-under-rejection
> or AUROC-under-rejection curves instead.

The skin-tone PPG scope is explicitly dropped (admission.md advisory
annotation: INFEASIBLE on public data at adequate sample size).
No PPG corpus is used unless a corpus with Fitzpatrick-labeled
records at >= 100 subjects per stratum is identified before
protocol lock — none is known as of 2026-05-02.

---

## Shared substrate

### Scan result

`30-implement/shared/` does not exist. `30-implement/README.md`
confirms the shared substrate is expected to materialize lazily.
This track is the **first promoter** for all cardiac-signal and
calibration utilities.

### Consume

None. (Shared substrate is empty.)

### Promote on completion

The following artifacts will be built in
`30-implement/ecg-ppg-realworld/code/` and promoted to
`30-implement/shared/` when plausible second consumers exist.
Each promotion candidate has at least two plausible consumers named.

**1. `30-implement/shared/eval/calibration.py`**

Purpose: compute standard probabilistic calibration metrics from
(y_true, y_prob) arrays. No ECG-specific logic.

Interface:

```python
def brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Mean squared probability error. Lower is better."""

def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 15,
) -> float:
    """Mean absolute deviation between bin confidence and bin accuracy."""

def reliability_diagram(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 15,
    title: str = "",
    save_path: str | None = None,
) -> None:
    """Plot fraction-of-positives vs mean predicted probability per bin."""
```

Plausible 2nd consumers: sleep-staging (stager epoch-level
confidence); cross-subject-eeg (FM softmax calibration quality);
affective-state (any classifier producing probabilities).

**2. `30-implement/shared/eval/abstention.py`**

Purpose: selective-classification evaluation protocol —
given a model's predicted probabilities and a sweep of abstention
thresholds, compute coverage (fraction of predictions made), PPV,
and F1 at each threshold. Encodes the "abstain when uncertain" protocol
so any track with a classifier + confidence score can evaluate its
abstention behavior.

Interface:

```python
def selective_classification_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    thresholds: np.ndarray | None = None,
    n_thresholds: int = 100,
) -> pd.DataFrame:
    """
    Sweeps abstention threshold from 0 to 1.
    Returns DataFrame with columns:
    [threshold, coverage, ppv, f1, n_predicted, n_abstained].
    Coverage = fraction of samples where model predicts (not abstains).
    PPV = precision on predicted-positive subset.
    """

def ppv_at_coverage(
    curve_df: pd.DataFrame,
    target_coverage: float,
) -> tuple[float, float]:
    """
    Returns (ppv, threshold) at the coverage level closest to
    target_coverage. Used to extract the headline number.
    """

def plot_coverage_vs_ppv(
    curve_df: pd.DataFrame,
    title: str = "",
    save_path: str | None = None,
) -> None:
    """
    Plots PPV vs coverage (abstention rate on x-axis).
    Annotates the BASEL anchor point (coverage ~ 0.80).
    """
```

Plausible 2nd consumers: sleep-staging (abstention on epoch
classification); cross-subject-eeg (selective BCI decoding);
affective-state (reject ambiguous arousal estimates).

**3. `30-implement/shared/eval/partition.py`**

Purpose: patient-disjoint (and optionally site-disjoint) train /
dev / test splitting with validation assertion.
Self-contained; no cardiac-specific logic.

Interface:

```python
def patient_disjoint_split(
    patient_ids: list[str],
    site_labels: list[str] | None = None,
    test_fraction: float = 0.20,
    dev_fraction: float = 0.10,
    random_state: int = 42,
    site_disjoint: bool = False,
) -> dict[str, list[str]]:
    """
    Returns {"train": [...], "dev": [...], "test": [...]}.
    If site_disjoint=True, sites (not patients) are split at the
    top level; patients within each site remain non-overlapping.
    """

def validate_partition(partition: dict[str, list[str]]) -> None:
    """
    Raises ValueError if any patient ID appears in more than one split.
    """
```

Note: cross-subject-eeg is also building a `subject_disjoint_split`
with compatible interface (see cross-subject-eeg/approach.md §Promote).
On promotion, these two will be merged or aliased under a unified
`partition.py` with both entry points; whichever track promotes first
owns the initial file.

Plausible 2nd consumers: sleep-staging (PSG patient splits);
affective-state (subject-disjoint affect corpus splits); any track
that must enforce patient / subject disjointness.

**4. `30-implement/shared/data/ptbxl_loader.py`**

Purpose: thin wrapper around PTB-XL's waveform WFDB files and
metadata CSV. Returns `(signals, labels, metadata)` in a consistent
numpy / pandas format. Does not own split logic (that lives in
`partition.py`).

Interface:

```python
def load_ptbxl(
    ptbxl_path: str,
    sampling_rate: int = 100,
    leads: list[str] | None = None,  # None = all 12 leads
) -> tuple[np.ndarray, pd.DataFrame]:
    """
    Returns:
    - signals: np.ndarray shape (n_records, n_leads, n_samples)
    - metadata: pd.DataFrame with columns including ecg_id, patient_id,
      strat_fold, scp_codes (parsed), site.
    Sampling rate: 100 or 500 Hz per PTB-XL release.
    """

def extract_afib_labels(
    metadata: pd.DataFrame,
    likelihood_threshold: float = 100.0,
) -> pd.Series:
    """
    Returns a binary Series (1=AFIB present, 0=not) from the scp_codes
    column. Default threshold = 100.0 (definite AFIB only).
    """
```

Plausible 2nd consumers: any track that uses PTB-XL or a similar
WFDB-formatted ECG corpus; sleep-staging (if it adds an ECG/HRV arm).

### Track-specific (not promoted)

- Feature extraction code (RR-interval, morphology features via NeuroKit2).
- Temperature scaling / calibration-fitting scripts specific to the ResNet-1D.
- Per-experiment notebooks.
- PTB-XL split configuration JSON (records which strat_fold maps to which role).

---

## Dataset

### Primary dataset

**PTB-XL**

- **Full name:** PTB-XL, a large publicly available electrocardiography dataset
- **Version:** v1.0.3 (PhysioNet, June 2022)
- **License:** ODC-BY (Open Data Commons Attribution License)
- **Access:** PhysioNet, https://physionet.org/content/ptb-xl/1.0.3/
  Download via `wget -r -N -c -np https://physionet.org/files/ptb-xl/1.0.3/`
  or via `wfdb` Python library. No registration required. ~1.7 GB total.
- **Size:** 21,799 clinical 12-lead ECG records from 18,869 patients.
  Recording duration: 10 seconds. Sampling rates: 100 Hz (primary) and
  500 Hz (full resolution). Both are included.
- **AFIB record count:** approximately 1,514 records labeled AFIB
  (Strodthoff et al. 2020 Table 1). Held-out test fold (strat_fold=10,
  the standard PTB-XL test partition) contains approximately 303 AFIB
  records — adequate per power analysis (N required = 87 for a 21 pp
  PPV improvement; N available = ~303). Source: critic-defensibility.md §1.
- **Stratification folds:** PTB-XL provides 10 stratification folds
  (strat_fold 1–10) that preserve patient disjointness and approximate
  dataset-level class balance across folds.

### Second dataset (exploratory arm, not headline)

**PhysioNet/CinC 2017 (AF Classification from a Short Single Lead ECG)**

- License: Creative Commons Attribution 4.0 International
- Access: https://physionet.org/content/challenge-2017/1.0.0/
- Size: 8,528 single-lead ECGs, 4 classes (Normal, AF, Other, Noisy).
- Role: cross-dataset probe only. Train/calibrate on PTB-XL, evaluate
  the same abstention mechanism on CinC 2017. Asks whether an abstention
  threshold calibrated on PTB-XL transfers to a different single-lead
  corpus. This arm is exploratory; it is NOT the headline.
  If CinC 2017 produces confounded results (different lead placement,
  different prevalence), it is reported separately with explicit caveats.

No PPG corpus is used.

### Split definition

PTB-XL provides strat_fold 1–10. The standard split per the
benchmark paper (Strodthoff et al. 2020) is:

- **Dev (parameter selection, pilots, ablations):** strat_fold 1–8
  (approximately 17,440 records, 15,095 patients).
- **Validation (calibration fitting, threshold selection):** strat_fold 9
  (approximately 2,180 records).
- **Test (held-out headline, touched once):** strat_fold 10
  (approximately 2,179 records, ~303 AFIB).

Patient disjointness: guaranteed by PTB-XL's fold construction.
No patient from strat_fold 10 appears in folds 1–9.
Verified by `partition.py:validate_partition()` before any headline run.

Site disjointness: PTB-XL records metadata on recording site.
The strat_fold split is patient-disjoint but NOT necessarily site-disjoint.
This is noted as a limitation. Site-disjoint analysis is a pilot probe
(P-4) but is not the headline partition.

---

## Preprocessing

**Software:** NeuroKit2 >= 0.2.9, wfdb >= 4.1.2, scipy >= 1.11.
All versions pinned in `30-implement/ecg-ppg-realworld/code/requirements.txt`.

### Pipeline for PTB-XL ECG records

Applied uniformly to all records at 100 Hz (10-second window = 1,000 samples
per lead). Processing is deterministic given the input waveform.

1. **Load:** Read WFDB record at 100 Hz using `wfdb.rdrecord()`.
   Use all 12 leads or Lead I + Lead II only for the ResNet-1D variant.
   Lead selection is a fixed design choice made before any experiment
   (not tuned on the test split). Default: all 12 leads for the primary
   model.

2. **Baseline wander removal:** High-pass filter at 0.5 Hz (3rd-order
   Butterworth, zero-phase via `scipy.signal.sosfiltfilt`). Rationale:
   removes respiratory drift without distorting QRS morphology.

3. **Powerline notch filter:** Notch at 50 Hz (quality factor 30).
   PTB-XL was recorded in Europe (50 Hz mains). Rationale: removes mains
   artifact without affecting diagnostic frequency content.

4. **Amplitude clipping:** Clip to [-5 mV, +5 mV] per lead. Rationale:
   removes saturation artifacts that would produce artificially confident
   predictions. Report the fraction of records with clipped samples.

5. **Normalization:** Per-lead z-score normalization across the 10-second
   window (mean subtracted, divided by standard deviation). Rationale:
   ResNet-1D and logistic regression on morphology features both benefit
   from unit-variance inputs. For the feature-based baseline, normalization
   is performed on extracted RR intervals separately, not on raw signal.

6. **Quality gate:** Any record where all 12 leads have standard deviation
   < 0.01 mV (effectively flat) is flagged as a low-quality record and
   excluded from analysis. Report count. Rationale: flat records produce
   undefined z-score normalization and corrupt RR-interval detection.

7. **Feature extraction (for classical baseline only):** Via NeuroKit2
   `ecg_process()` and `ecg_intervalrelated()` on Lead II:
   - R-peak detection (Pan-Tompkins).
   - RR-interval series: mean, std, RMSSD, pNN50, LF/HF ratio.
   - Morphology features: P-wave presence, QRS duration, QT interval,
     T-wave polarity (via template correlation).
   - Irregularity score: coefficient of variation of RR intervals.
   These 12 features form the classical baseline feature vector.

### No PPG preprocessing

No PPG pipeline is implemented. If the scope is extended in a later
version of this track (contingent on corpus discovery), a separate
preprocessing section will be added.

---

## Model family

### Feasibility check (4 GB VRAM envelope)

**Classical baseline (logistic regression on 12 hand-crafted features):**
CPU-only. Trivially feasible.

**ResNet-1D (xresnet1d50 or equivalent, ~1.4 M parameters):**
At batch=32, 12 leads × 1,000 samples, float32: approximately 0.8 GB
VRAM peak during training. Float16 mixed precision reduces to ~0.4 GB.
Feasible with margin.

**Temperature scaling (post-hoc calibration):** CPU-only scalar
parameter fit. Trivially feasible.

**MC-Dropout at inference:** adds a second forward pass per sample in
inference mode with dropout enabled. VRAM usage identical to a single
inference pass. Feasible.

No FM pre-training. No end-to-end transformer training.

### Model A — Primary

**xresnet1d50 (1D ResNet, 12-lead input) + temperature scaling +
selective-classification threshold**

Architecture: 1D convolutional ResNet adapted for ECG (Strodthoff
et al. 2020 baseline architecture; implementation available at
https://github.com/helme/ecg_ptbxl_benchmarking). ~1.4 M parameters.

Training: supervised on PTB-XL strat_fold 1–8, binary label
(AFIB vs. not-AFIB, likelihood threshold 100.0 for definite AFIB).
Loss: binary cross-entropy. Optimizer: Adam, lr=1e-3, cosine decay.
Batch=32, max 50 epochs, early stopping on fold 9 F1 (patience=10).

Post-hoc calibration: Temperature scaling. A single scalar T fitted
on strat_fold 9 by minimizing Brier score via L-BFGS-B. No re-training.
Rationale: temperature scaling preserves rank order of predictions
while improving calibration. Simplest calibration method; if it fails,
that is a finding.

Abstention mechanism: threshold on calibrated probability. Abstain if
max(P_afib, P_not_afib) < tau, where tau is swept over [0.5, 1.0]
in 100 steps to generate the coverage-vs-PPV curve. Primary operating
point: coverage = ~0.80 (abstaining on ~20% of records, matching the
BASEL inconclusive rate of 17–21%).

Rationale for temperature scaling over MC-Dropout or conformal: it
is the simplest, most transparent calibration method. If temperature
scaling fails to improve PPV at the target coverage, that is a stronger
null result than a null from a more complex method — it means even
the basic mechanism does not help.

### Model B — Primary alternative (if xresnet1d50 underperforms on dev)

**MC-Dropout on xresnet1d50**

Same architecture. Dropout rate=0.1 added after each residual block.
At inference: 30 stochastic forward passes, estimate uncertainty as
predictive entropy. Abstain if entropy > tau.

This is an alternative abstention mechanism, not a different classifier.
It answers: does an uncertainty-aware abstention (MC-Dropout) outperform
a simple confidence-threshold abstention (temperature scaling)?
Comparison is an ablation (Ablation 3 below), not a headline comparison.

### Model C — Baseline (strong classical)

**Logistic regression on 12-feature RR-interval + morphology vector**

Features: extracted by NeuroKit2 as described in Preprocessing §7.
Classifier: sklearn LogisticRegression (L2, C tuned on strat_fold 9
log-loss, 5 values: 0.001, 0.01, 0.1, 1.0, 10.0).
Abstention: same confidence-threshold sweep as Model A.

Rationale: a classical feature-based baseline with abstention tells us
whether the PPV improvement (if any) requires deep learning or is
achievable with interpretable features. If logistic regression + abstention
matches ResNet-1D + abstention, that is also a finding.

### Summary

| Model | GPU? | VRAM (est.) | Role |
|---|---|---|---|
| xresnet1d50 + temperature scaling | optional | < 1 GB | Primary |
| xresnet1d50 + MC-Dropout | optional | < 1 GB | Ablation arm B |
| Logistic regression on hand-crafted features | no | 0 | Baseline |

---

## Evaluation protocol

### Patient-disjoint structure

All evaluation is patient-disjoint. No patient in the held-out test
partition (strat_fold 10) appears in the training or validation partition.
Verified by `partition.py:validate_partition()` before the headline run.

### Primary metric

**PPV at fixed alert rate (coverage)**

Operationally: among the records the model chooses to predict as AFIB
(i.e., does not abstain on), what fraction are true AFIB?

Primary operating point: coverage = 0.80 (model predicts on 80% of
records, abstains on 20%). Rationale: 20% abstention rate matches the
BASEL Wearable Study's 17–21% inconclusive rate, which is the clinically
observed rate at which human review is required.

**Two-denominator clarification (M-1 fix per methodology-critic):**
Coverage and PPV use *different denominators*. Coverage = fraction of all
strat_fold 10 records on which the model renders any prediction (high-
confidence AFIB-predicted + high-confidence not-AFIB-predicted together);
the abstention criterion is `max(P_afib, 1 - P_afib)` thresholded to
retain the top 80%. PPV is computed only over the predicted-AFIB subset
of those retained records: PPV = TP / (TP + FP). High-confidence
not-AFIB predictions are retained (counted toward coverage) but
contribute neither TP nor FP.

Formally:
  PPV(coverage=0.80) = TP / (TP + FP)
where TP, FP are counted among the predicted-AFIB records inside the 80%
retained set; the 20% abstained records (lowest max-confidence)
contribute nothing.

Secondary operating points: PPV at coverage = {0.70, 0.75, 0.85, 0.90, 1.00}.
Coverage = 1.00 is the no-abstention baseline (every record predicted).

### Secondary metrics

- **Coverage-vs-PPV curve:** Full sweep from coverage 0.50 to 1.00 in
  100 steps. Area under this curve (AUC-PPV-coverage) is a summary
  statistic of the abstention mechanism's effectiveness.
- **Brier score:** Overall probabilistic calibration quality.
- **Expected Calibration Error (ECE, 15 bins):** Reliability.
- **Reliability diagram:** Visual calibration check.
- **AUROC:** Standard discrimination metric. Not the primary metric
  because it does not capture PPV at low prevalence.
- **Abstention rate:** Fraction of records abstained on at the primary
  operating point.
- **Confusion matrix at coverage=0.80:** To see which class benefits
  from abstention.

### Held-out partition discipline

The test partition (strat_fold 10) is touched exactly once, in the
single authorized headline run. The pre-run checklist (see protocol-lock.md)
must be complete before this run. After the run, no further experiments
touch strat_fold 10.

Dev partition (strat_fold 1–8) is used freely for pilots, ablations,
and model selection. Validation partition (strat_fold 9) is used for **calibration fitting, seed selection by Brier score, and threshold selection** (M-2 fix per methodology-critic — fully documented permitted uses):
temperature scaling fit and threshold selection only.

### Statistical test

Bootstrap confidence intervals (n=2,000, stratified by label, seed=42)
for all reported metrics. Report as "XX.X (95% CI: YY.Y–ZZ.Z)".

For the headline comparison (PPV with abstention vs PPV without abstention
at coverage=0.80): paired bootstrap test (same held-out records, two
conditions). p-value computed as fraction of bootstrap resamples where
the difference is <= 0. Significance threshold: p < 0.05 (one-sided,
H1: PPV with abstention > PPV without abstention).

Effect size: absolute PPV difference in percentage points at coverage=0.80,
with 95% CI.

### Cross-subject note

PTB-XL contains 18,869 patients. The fold construction is patient-disjoint.
No cross-subject (same patient, different recording) analysis is planned.
This is an IID (within-distribution) evaluation on PTB-XL. Cross-dataset
evaluation (PTB-XL train, CinC 2017 test) is exploratory only.

---

## Ablations

All ablations run on the dev/validation split only (strat_fold 1–9).
They do not touch strat_fold 10.

**Ablation 1 — No abstention vs. abstention (load-bearing design choice)**

Procedure: evaluate xresnet1d50 on strat_fold 9 at coverage=1.00
(no abstention) and at coverage=0.80 (temperature-scaled abstention).
Report PPV, AUROC, F1 at both operating points.

Hypothesis: calibrated abstention raises PPV at coverage=0.80 relative
to coverage=1.00 on the same model. If the difference is < 2 pp, the
abstention mechanism provides negligible PPV benefit on the validation
set — do not proceed to headline with this mechanism.

Kill trigger for the abstention arm: if Ablation 1 shows < 2 pp PPV
improvement at coverage=0.80 on strat_fold 9, investigate whether the
model's confidence ordering (ranking records by confidence) is informative
(i.e., does abstaining on the lowest-confidence records actually remove
more false positives than true positives?). If the ranking is uninformative
(AUC of confidence vs. correctness < 0.55), the abstention mechanism is
broken and the track should be reviewed before headline.

**Ablation 2 — Temperature scaling vs. no calibration (load-bearing calibration step)**

Procedure: compare Brier score and ECE of xresnet1d50 before and after
temperature scaling on strat_fold 9.

Hypothesis: temperature scaling meaningfully reduces ECE (expected
improvement >= 0.02 in ECE). If temperature scaling does not improve
calibration, the model is already well-calibrated (or not calibratable
by this method) and the calibration step should be characterized honestly
in findings.md.

**Ablation 3 — MC-Dropout vs. temperature scaling (abstention mechanism choice)**

Procedure: compare coverage-vs-PPV curves of the temperature-scaling
abstention and the MC-Dropout abstention on strat_fold 9.

Hypothesis: MC-Dropout provides a better coverage-vs-PPV curve than
temperature scaling (higher PPV at the same coverage). If they are
equivalent, report this — it means the simpler method is sufficient.

**Ablation 4 — Classical vs. deep (feature baseline comparison)**

Procedure: compare the coverage-vs-PPV curve of logistic regression on
12 features vs. xresnet1d50 on strat_fold 9.

Hypothesis: xresnet1d50 provides higher PPV at the same coverage than
the classical baseline, because deep morphology features capture
atrial activity patterns that hand-crafted RR-interval features miss.
If the classical baseline matches or exceeds ResNet-1D, the contribution
does not require deep learning.

**Ablation 5 — AFIB likelihood threshold sensitivity**

Procedure: extract AFIB labels at three likelihood thresholds:
50.0 (probable AFIB), 75.0 (likely AFIB), 100.0 (definite AFIB, primary).
Evaluate xresnet1d50 PPV-at-coverage=0.80 on strat_fold 9 at each.

Hypothesis: the primary threshold (100.0 = definite AFIB only) gives
cleaner labels and higher PPV at coverage=0.80 than lower thresholds.
If lower thresholds produce comparable or better PPV, the label-definition
choice affects results materially and must be reported.

---

## Uncertainty reporting

- **Bootstrap CI:** All metrics reported with 95% bootstrap CI (n=2,000
  resamples, stratified by AFIB label, fixed seed=42). Reported as
  "XX.X (95% CI: YY.Y–ZZ.Z)".
- **Multi-seed model training:** xresnet1d50 trained with 3 independent
  random seeds (seed ∈ {42, 7, 123}). Report mean and standard deviation
  of val-set metrics across seeds to quantify training variance.
  Headline: use the seed with lowest strat_fold 9 Brier score (seed chosen
  before touching strat_fold 10). The three-seed spread is reported as a
  secondary uncertainty indicator.
- **Temperature scaling stability:** temperature parameter T fitted on
  strat_fold 9 is reported. A T value far from 1.0 (e.g., T > 2.0)
  indicates substantial miscalibration pre-scaling, reported and interpreted.
- **Reporting format:** "XX.X% (95% CI: YY.Y%–ZZ.Z%, N=N_records)" for all
  headline numbers. Point estimates without CI are not reported.

---

## Compute budget

| Task | Hardware | Estimated time |
|---|---|---|
| PTB-XL download (~1.7 GB) | local | 30 min |
| Preprocessing all records (100 Hz) | CPU | 30–60 min |
| Feature extraction (NeuroKit2, baseline) | CPU | 1–2 hr |
| xresnet1d50 training (3 seeds, strat_fold 1–8, 50 epochs max) | GTX 1650 | 3–6 hr |
| Temperature scaling fit (strat_fold 9) | CPU | < 5 min |
| Coverage-vs-PPV curve generation (ablations, dev set) | CPU | < 30 min |
| MC-Dropout inference (30 passes, strat_fold 9) | GTX 1650 | 1 hr |
| Bootstrap CI computation (n=2000) | CPU | < 1 hr |
| Headline run (strat_fold 10, once) | CPU + GPU | 1–2 hr |
| **Total** | CPU + GTX 1650 | **~8–12 hr** |

Total GPU budget: approximately 6–10 GPU-hours on GTX 1650.
Well within the local envelope; no fallback compute required.

No Kaggle fallback needed for this track. The largest computation
(model training) is well within 4 GB VRAM.

### Time to first honest result

- Week 1: environment setup, PTB-XL download, preprocessing,
  classical baseline trained and evaluated on dev (strat_fold 1–8
  cross-validation). First PPV-at-coverage number on dev, labeled
  "preliminary, dev only."
- Week 2: xresnet1d50 training (3 seeds), temperature scaling,
  Ablations 1–4 on strat_fold 9. Pilots P-1 through P-4.
- Week 3: finalize design choices from ablations, run Pilot P-5
  (site-disjoint probe, if motivated by ablation results). Write
  protocol-lock.md. Critic gate.
- Week 4: headline run on strat_fold 10 (once). Statistical tests.
  Write results.md.

**First honest result: week 4.** Dev results in weeks 1–2 are
labeled preliminary and do not constitute headline results.

---

## Novelty and exploration notes

### What is genuinely novel

**PPV-at-fixed-alert-rate as primary metric, calibrated to the
BASEL inconclusive rate:** The existing abstention literature
(Smole 2023, NCA 2024, Barandas 2024) reports accuracy-under-rejection
or AUROC-under-rejection curves. None of these papers uses PPV at a
fixed clinically anchored coverage level as the primary metric. The
BASEL Wearable Study's 17–21% inconclusive rate provides a concrete
clinical anchor that none of the prior abstention papers references.
This framing connects the ML abstention decision directly to the
real-world alert management workflow.

**Explicit comparison across abstention mechanisms under this metric:**
No paper found that compares temperature scaling vs. MC-Dropout
abstention specifically under the PPV-at-coverage metric.

### What is standard and intentionally so

- xresnet1d50 on PTB-XL: a standard well-characterized baseline
  (Strodthoff et al. 2020). Using it is appropriate — the contribution
  is the evaluation protocol, not a new architecture.
- Temperature scaling: the standard post-hoc calibration method.
- Bootstrap CI: standard uncertainty quantification.
- Binary AFIB classification on PTB-XL strat_fold 10: the standard
  evaluation setup from the PTB-XL benchmark paper.

### What is exploratory (not pre-registered)

- Cross-dataset probe on CinC 2017 (abstention mechanism trained on
  PTB-XL, evaluated on CinC 2017 single-lead ECG).
- Conformal prediction coverage guarantee as an alternative abstention
  mechanism (RAPS or LAC on top of xresnet1d50 softmax).
- Per-subgroup PPV analysis by age band and sex (if strat_fold 10
  provides sufficient subgroup size for meaningful stratification).
- Extension of the CinC 2017 arm to include Lead I only (simulating
  a wearable single-lead signal).

These are captured in pilots-README.md and do not touch the
pre-registered headline protocol.
