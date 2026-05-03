> **Spec:** `10-pain-point/affective-state/admission.md`

# Approach — affective-state

**Track:** affective-state
**Date:** 2026-05-02 (revised 2026-05-03 — pilot P-1/P-2 findings)
**Author:** methodologist agent
**Status:** revised — EDA pipeline updated per unlock-note-2026-05-03.md

---

## Scope statement

Feature-stability audit of cardiac (HRV) and electrodermal (EDA) features
across public affective-state datasets. Operative scope: replicate and
extend the finding from arXiv:2508.10561 (2 of 164 features showed
reproducible association with arousal) by applying the same audit framework
to a NEW combination of datasets (DEAP + WESAD + MAHNOB-HCI), with HRV
cardiac features as the primary extension target and EDA as a secondary
arm tested with the features computable from highpass decomposition.

**arXiv:2508.10561 verification note (m-1 fix — updated):** The non-redundancy
argument rests on arXiv:2508.10561 focusing on EDA features rather than HRV
cardiac features. The YAML field `arxiv_2508_10561_includes_hrv_FILL_MANUALLY`
in feature_schema_v1.yaml remains unverified from the paper's Methods. If
the original paper did include HRV features, the cardiac novelty claim
narrows to "extension to fresh datasets and per-subject Fisher-z aggregation."
This open item is carried forward to the headline phase.

**EDA pipeline update (2026-05-03):** cvxEDA is unavailable on the project
environment (cvxpy/cvxopt fails on Windows 11 + Python 3.11.2; confirmed P-2).
highpass decomposition is the primary and only EDA decomposition method.
The EDA feature set is expanded from 6 (nk.eda_features output only) to
~42 explicitly enumerated features using scipy.signal and numpy operations
on the highpass-decomposed tonic and phasic components. Full feature list
in protocol-lock.md §2. Total N_features = 126. No classifier-level
consequences — EDA features are still tested in the same correlation pipeline.

The AHBU contribution is non-redundant with arXiv:2508.10561 (EDA-only,
different datasets), Brookshire 2024 (DNN leakage framing), and Apicella
2024 (cross-subject classification review). No new model is trained in the
headline; the headline is a statistical reproducibility map.

Secondary contribution: `30-implement/shared/eval/feature_stability.py`
promoted to shared substrate.

No deep learning. No classification SOTA claim. CPU-only.

---

## Shared substrate

### Scan result

`30-implement/shared/` directory does not exist (lazy materialization).
`30-implement/shared/data/`, `30-implement/shared/eval/`,
`30-implement/shared/models/` are absent.

The cross-subject-eeg track plans to promote `30-implement/shared/eval/
partition.py` (subject_disjoint_split) and `leakage_audit.py`. Not yet
available.

### Consume

- **`30-implement/shared/eval/partition.py`** (when promoted by
  cross-subject-eeg): consume `subject_disjoint_split` for secondary
  classifier ablation. If not promoted by experiment time, implement inline
  and flag for merging.

### Promote on completion

**1. `30-implement/shared/eval/feature_stability.py`** (UNIQUE to this track)

Purpose: given per-dataset feature DataFrames and a target column, compute
cross-dataset reproducibility statistics — per-subject Fisher-z Spearman
rho, FDR-corrected significance, direction consistency, reproducibility
flag. Returns a tidy stability-report DataFrame and a heatmap plot.

Interface (locked in protocol-lock.md §2 and P-6 test; must not change
without unlock note):

```python
def cross_dataset_correlation(
    feature_df_list: list[pd.DataFrame],
    target_col: str,
    correction_method: str = "fdr_bh",
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Returns DataFrame indexed by feature name with columns:
      rho_<dataset_i>          per-subject Fisher-z Spearman rho per dataset
      p_<dataset_i>            uncorrected p-value (t-test on Fisher-z values)
      p_corrected_<dataset_i>  FDR/Bonferroni-corrected p-value
      sig_<dataset_i>          bool: p_corrected < alpha
      consistent_sign          bool: all significant rhos share same sign
      n_sig                    int: count of datasets where sig=True
      reproducible             bool: sig=True AND consistent_sign=True in all
    """

def plot_stability_heatmap(
    stability_df: pd.DataFrame,
    save_path: str | None = None,
    figsize: tuple[int, int] = (14, 8),
) -> None:
    """Heatmap of per-feature, per-dataset Spearman rho with FDR outlining."""
```

P-6 confirmed: all 3 unit-test cases pass (all-reproducible, none-reproducible,
sign-inconsistent). The function is correct.

Plausible 2nd consumers: ecg-ppg-realworld (HRV feature stability across
PPG-DaLiA), sleep-staging (HRV feature stability across Sleep-EDF cohorts),
cross-subject-eeg (EEG band-power stability across MOABB datasets).

**2. `30-implement/shared/data/hrv_eda_feature_extractor.py`**

Purpose: extract a fixed, documented feature schema (matching the 126-feature
list from protocol-lock.md §2) from ECG or EDA signals.

Interface:

```python
def extract_features(
    signal: np.ndarray,
    signal_type: str,          # "ecg" or "eda"
    fs: float,
    window_sec: float = 60.0,
    feature_set: str = "ahbu_affective_v2",
) -> pd.DataFrame:
    """
    Returns DataFrame with one row per non-overlapping window.
    Columns = feature names from feature_schema_v2.yaml.
    NaN inserted where a feature cannot be computed.
    """
```

Plausible 2nd consumers: sleep-staging (HRV), ecg-ppg-realworld (HRV).

**3. `30-implement/shared/eval/partition.py`** — subject_disjoint_split:
promote if cross-subject-eeg has not done so by experiment time.

### Track-specific (not promoted)

- Per-dataset DEAP, WESAD, MAHNOB-HCI data loaders.
- Arousal operationalization label-harmonization table.
- Binomial test wrapper.
- Per-experiment analysis notebooks.

---

## Dataset

### Dataset selection rationale

Three datasets required: at least two for cross-dataset reproducibility;
three makes "replicates in all 3" distinguishable from "replicates in 2 of 3."
All must contain arousal ratings AND cardiac + EDA signals. See admission
record §Constituency for the operative constituency (academic affective-
computing + wearable stress-detection). Dataset selection unchanged from
2026-05-02 version.

**DEAP** — Primary dataset
- 32 subjects. ECG + GSR/EDA at 128 Hz (preprocessed). 40 one-minute
  clips per subject. Arousal self-report 1-9 per clip.
- License: academic request form, non-commercial.
- Access: pending form approval as of 2026-05-03.
- Arousal operationalization: binarize at per-subject median (median split);
  ties excluded (NaN). Locked in §3 of protocol-lock.
- Why included: largest affective-EEG dataset with paired ECG + EDA;
  most-cited DEAP benchmark; enables comparison with arXiv:2508.10561.

**WESAD** — Second dataset
- 15 subjects. Chest ECG + EDA at 700 Hz. Three conditions: stress,
  amusement, baseline.
- License: PhysioNet CC-BY 4.0. No registration.
- Access: downloaded and pipeline-verified (P-2, P-3). All 15 subjects
  confirmed with >=10 stress and >=10 baseline 60-second windows.
- Arousal operationalization: stress=1, baseline=0, amusement excluded.
- Why included: primary wearable-stress dataset for operative constituency.
  arXiv:2508.10561 uses WESAD; our cardiac extension on WESAD is the
  primary novel contribution.

**MAHNOB-HCI** — Third dataset
- 27 subjects. ECG + EDA at 100-256 Hz. 20 film clips per subject.
  Arousal self-report 1-9 per clip.
- License: academic request form.
- Access: pending form approval as of 2026-05-03.
- Arousal operationalization: binarize at per-subject median; same rule
  as DEAP.
- Why included: provides a third dataset with both ECG and EDA, with
  self-report arousal matching DEAP format. Three-dataset claim is
  substantially stronger than two-dataset.

**No train/test split for the headline reproducibility map.** All subjects
in all datasets contribute to the Spearman correlations. The unit of
inference is the feature, not the subject. The subject-level split
(70/10/20 by subject) is used only for the secondary classifier ablation
(A-3); it is explicitly labeled secondary and does not feed the headline.

---

## Preprocessing

### General principles

- Extract cardiac (ECG) and EDA features only. EEG channels ignored.
- All signal processing via NeuroKit2 0.2.13 (pinned; confirmed P-1/P-2).
- CPU-only. No GPU required.
- Random seed: 42, fixed throughout.

### ECG preprocessing pipeline (unchanged from 2026-05-02)

1. Load ECG at native sampling rate (DEAP: 128 Hz; WESAD: 700 Hz;
   MAHNOB-HCI: 100-256 Hz).
2. Bandpass filter: 0.5-40 Hz (4th-order Butterworth, zero-phase,
   scipy.signal.sosfiltfilt).
3. R-peak detection: nk.ecg_findpeaks(method="pantompkins1985").
   BioSPPy cross-check for R-peak count consistency (flag if >10%
   discrepancy).
4. RR intervals: physiologically implausible (<300 ms or >2000 ms)
   replaced with linear interpolation. Windows with >20% replaced beats
   flagged low-quality and excluded from correlation.
5. Feature extraction: nk.hrv_time, nk.hrv_frequency, nk.hrv_nonlinear
   (all columns). 86 features confirmed (P-1 / feature_schema_v1.yaml).
6. Window: 60 s non-overlapping.

### EDA preprocessing pipeline (revised 2026-05-03)

**Change from 2026-05-02:** cvxEDA removed; highpass is primary and only
decomposition method. The pipeline is simpler and fully deterministic —
no numerical failures, no per-window method logging.

1. Load EDA at native sampling rate.
2. Downsample to 4 Hz: scipy.signal.resample_poly.
3. Clean: nk.eda_clean(sampling_rate=4) (default Butterworth lowpass).
4. Decompose: nk.eda_phasic(eda_cleaned, sampling_rate=4,
   method="highpass"). Returns tonic (SCL) and phasic components.
5. Extract nk.eda_features(eda_signals, sampling_rate=4) — 6 columns
   confirmed (P-1): SCR_Peaks_N, SCR_Peaks_Amplitude_Mean,
   EDA_Tonic_SD, EDA_Sympathetic, EDA_SympatheticN, EDA_Autocorrelation.
6. Extract supplementary SCL features: 10 features (mean, std, slope,
   median, max, min, range, IQR, skewness, kurtosis) from tonic array.
7. Extract supplementary SCR features: 14 features from scipy.signal
   peak detection on phasic array (SCR_Rate, amplitudes, rise times,
   half-recovery times, latency, inter-peak intervals, phasic variance/
   skewness). Peak detection: scipy.signal.find_peaks, prominence>=0.01
   uS, min inter-peak distance=4 samples (1 s at 4 Hz).
8. Extract EDA band-power: scipy.signal.welch on cleaned EDA at 4 Hz
   (nperseg=64, noverlap=32). Integrate PSD over three bands (LF, MF, HF)
   and compute 6 band-power features.
9. Compute 4 derived features: Sympathetic_Index, SCR_Active_Proportion,
   SCL_Recovery_Rate, Phasic_Mean.
10. Same 60-s window as ECG.

**Window NaN policy:** Windows where phasic component is all-zero or all
SCR features are NaN (e.g., channel noise or flat EDA signal): EDA features
set to NaN for that window. Cardiac features computed normally. The NaN
rate per EDA feature per dataset is reported in results.md (see A-2').

### Arousal operationalization

Per protocol-lock §3. Pre-registered per dataset.

### Preprocessing software

- NeuroKit2 0.2.13 (pinned; confirmed P-1/P-2).
- BioSPPy 0.8.x (R-peak cross-check only; pinned).
- scipy 1.12.x (signal processing, peak detection, Welch PSD; pinned).
- pandas 2.2.x (feature DataFrames; pinned).
- statsmodels 0.14.x (FDR correction; pinned).
- numpy 1.26.x (pinned).
- cvxpy: NOT used (installation failed on project environment).

---

## Feature schema (N_features = 126)

Full enumeration in protocol-lock.md §2. Summary:

| Group | Count | Source |
|---|---|---|
| HRV time-domain | 25 | nk.hrv_time |
| HRV frequency-domain | 10 | nk.hrv_frequency |
| HRV non-linear | 51 | nk.hrv_nonlinear |
| EDA (nk.eda_features) | 6 | nk.eda_features |
| EDA SCL tonic | 10 | scipy/numpy from tonic component |
| EDA SCR phasic | 14 | scipy.signal.find_peaks on phasic |
| EDA band-power | 6 | scipy.signal.welch on cleaned EDA |
| EDA derived | 4 | composite formulas |
| **Total** | **126** | |

Cardiac: 86 (68%). EDA: 40 (32%).
Schema written to feature_schema_v2.yaml before headline run.

---

## Model family

This track has no primary classifier model. The headline is a statistical
reproducibility test. The secondary classifier uses Logistic Regression only.

### Primary analysis — feature-stability correlation

For each feature f and dataset D:
1. Per-subject: Spearman rho(f, binary_arousal) across that subject's windows.
2. Fisher-z aggregate to dataset-level rho.
3. p-value: one-sample t-test on Fisher-z values (permutation test if
   N_subjects < 15).
4. FDR-BH correction across all N_features within each dataset.
5. Reproducible if: FDR p < 0.05 AND consistent sign across all 3 datasets.
6. Binomial test on N_reproducible at N_features, p0=0.05, two-sided.

### Secondary analysis — classifier on reproducible subset

Secondary, not headline. Dev split only.

- Model A: Logistic Regression (sklearn, liblinear, C=1.0) on reproducible
  features.
- Model B: Logistic Regression on full 126-feature set.
- Model C: Majority-class baseline.

Evaluation: subject-disjoint LOSO AUC, 95% bootstrap CI (n=2000, seed=42).
Rationale: LR is the simplest interpretable model. No SVM/RF complexity.

---

## Evaluation protocol

### Primary (reproducibility map)

Unit of analysis: the feature (N=126).

Per feature: compute (rho, p_raw, p_corrected, sig, sign) independently
in each of the three datasets. Mark feature reproducible if sig=True in
all three AND consistent sign.

Primary metric: N_reproducible / N_total with 95% Clopper-Pearson CI.

Report separately:
- Reproducible in all 3 datasets.
- Reproducible in exactly 2 of 3 (consistent sign).
- Reproducible in 1 dataset only.
- Reproducible in 0 datasets.

Statistical test: scipy.stats.binomtest(k, n=N_features, p=0.05,
alternative="two-sided").

### Held-out discipline

Correlation analysis uses ALL subjects in all datasets (no train/test
split for the headline). The secondary classifier ablation uses a
70/10/20 subject-level split. The classifier result is labeled secondary.

### Cross-dataset reproducibility note

The reproducibility claim is cross-DATASET: does feature X associate with
arousal in dataset A AND in B AND in C? Within each dataset the correlation
is subject-pooled via Fisher-z (not single-subject). Limitation:
subject-pooled rho may reflect between-subject physiological variation
more than within-subject arousal variation. Ablation A-5 tests this.

---

## Ablations

All ablations use the same per-dataset feature matrices computed once
at headline time (no re-extraction). No ablation touches a separate
held-out split beyond the secondary classifier split.

**A-1: FDR vs Bonferroni correction**
Hypothesis: reproducibility count is sensitive to correction choice.
Procedure: rerun correlation table with correction_method="bonferroni".
Report count under both.

**A-2': EDA feature NaN-rate check (replaces A-2 cvxEDA vs highpass)**
Hypothesis: EDA features computed from highpass decomposition may have
high NaN rates on datasets with noisy or low-amplitude EDA signals.
If >30% of windows for an EDA feature in a dataset produce NaN, that
feature is unreliable in that dataset.
Procedure: report per-EDA-feature NaN rate per dataset from the feature
matrices. If any EDA feature has >30% NaN in a dataset, exclude it from
the reproducibility test for that dataset (EDA-feature-level exclusion,
not dataset-level). Document the exclusion list.
Kill criterion: if >50% of EDA features (>20 of 40) are excluded from
all three datasets due to NaN rate, demote EDA features to auxiliary
and report the cardiac-only reproducibility count as the primary finding.

**A-3: Reproducible-feature subset classifier vs full feature set**
Hypothesis: stable features retain predictive value even though the set
is smaller.
Procedure: LOSO LR AUC on reproducible subset vs full 126 features vs
majority-class baseline, 70/10/20 split within each dataset.

**A-4: WESAD amusement condition included**
Hypothesis: excluding amusement sharpens contrast; including it may
change the WESAD correlation pattern.
Procedure: 3-class ordinal encoding (stress=2, amusement=1, baseline=0),
Spearman rho on ordinal. Compare reproducibility count.

**A-5: Per-subject correlation vs subject-pooled Fisher-z**
Hypothesis: subject-pooled rho may be dominated by between-subject
physiological variation rather than arousal-driven variation.
Procedure: compute Spearman rho separately per subject (within-session).
Report median per-subject rho and sign consistency across subjects.

---

## Uncertainty reporting

- **Primary reproducibility count:** 95% Clopper-Pearson CI on
  N_reproducible / N_features.
- **Per-feature rho estimates:** 95% bootstrap CI (n=2000, seed=42) on
  the dataset-level rho.
- **Secondary classifier AUC:** 95% bootstrap CI (n=2000) on LOSO AUC.
- **Format:** "N_reproducible = k (95% CI: [a, b], Clopper-Pearson;
  N_features = 126; binomial p = X.XXX)."
- **No bare point estimates.** Every metric gets a CI.

---

## Compute budget

| Task | Hardware | Estimated time |
|---|---|---|
| Dataset download WESAD (~4 GB, done) | local | complete |
| DEAP form + download (~700 MB, pending) | local | 1-10 business days wait + 30 min download |
| MAHNOB-HCI form + download (~1 GB phys signals, pending) | local | 1-10 business days wait + 30 min |
| WESAD preprocessing (15 subjects × conditions) | CPU | 10-20 min |
| DEAP preprocessing (32 subjects × 40 clips) | CPU | 15-30 min |
| MAHNOB-HCI preprocessing (27 subjects × 20 clips) | CPU | 20-30 min |
| EDA supplementary feature extraction (scipy per window) | CPU | add 15-30 min vs nk-only |
| Correlation table + FDR + binomial test | CPU | <5 min |
| Bootstrap CIs (n=2000, 126 features, 3 datasets) | CPU | 30-60 min |
| Ablations A-1, A-2', A-3, A-4, A-5 | CPU | 1-2 hr total |
| Secondary classifier LOSO LR | CPU | 15-30 min |
| Plots + report | CPU | 1-2 hr |
| **Total headline** | **CPU** | **~5-7 hr active** |

GPU requirement: zero. 4 GB VRAM constraint not binding. CPU-only.

### Time to first honest result

- Day 1-2 (now): WESAD full-pipeline run with expanded EDA features.
  First result = WESAD dev-check (pipeline correctness; no arousal
  correlation computed).
- Day 2-5: await DEAP and MAHNOB-HCI form approval. Continue
  WESAD preprocessing and ablation scaffolding.
- Day 5-10: full feature extraction on all three datasets once access
  confirmed. feature_schema_v2.yaml committed.
- Day 10-14: headline correlation table, binomial test, CIs, ablations.
- **First honest result: end of week 2.**

---

## Novelty and exploration notes

### What is genuinely novel

- Extension of arXiv:2508.10561 from EDA-only to HRV cardiac + EDA
  features across three datasets simultaneously. No prior paper has
  computed cross-dataset per-subject Fisher-z Spearman rho for HRV
  features on arousal with FDR correction and a binomial reproducibility
  test on this dataset combination.
- Dataset combination DEAP + WESAD + MAHNOB-HCI not used together in
  arXiv:2508.10561.
- `feature_stability.py` — shared substrate, not built by any other track.
- Honest EDA comparison: our highpass-only EDA features vs arXiv:2508.10561
  EDA finding (partial independent replication).

### What is standard and intentionally so

- Spearman correlation, FDR correction, binomial test: established
  psychophysiology statistical tools. Interpretable; matches the
  reference paper.
- Logistic regression for secondary classifier.

### EDA scope clarification (2026-05-03)

The EDA pipeline uses highpass decomposition because cvxEDA is unavailable.
This is acknowledged as a limitation: the highpass method is a simpler linear
separation of tonic/phasic components vs the model-based cvxEDA approach.
Features derived from highpass decomposition may differ in absolute value from
cvxEDA-derived features. The arXiv:2508.10561 comparison is therefore
approximate for EDA features.

The EDA feature set (40 features) covers tonic and phasic aspects of EDA.
The audit is characterized as "HRV-dominant (86/126) with EDA supplement
(40/126)" — not "balanced cardiac + EDA." This framing is honest and does
not oversell the EDA contribution. A-2' (EDA NaN rate check) will determine
whether all 40 EDA features are usable across all three datasets.

### Redundancy acknowledgment

The shortlist tagged affective-state as high-redundancy-risk. The rebuttal
is unchanged: arXiv:2508.10561 did not test HRV cardiac features; Brookshire
2024 tested DNN leakage; Apicella 2024 reviewed methods. AHBU extends the
feature-stability audit to cardiac features on a new dataset combination.
We do not claim to supersede arXiv:2508.10561 — we replicate its EDA finding
(in approximate form, highpass vs their method) and extend to HRV cardiac.
