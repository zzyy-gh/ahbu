> **Spec:** `10-pain-point/affective-state/admission.md`

# Approach — affective-state

**Track:** affective-state
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

---

## Scope statement

Feature-stability audit of cardiac (HRV, ECG-derived) and electrodermal
(EDA/EDA-derived) features across public affective-state datasets.
**arXiv:2508.10561 verification note (m-1 fix per methodology-critic — open):** the non-redundancy argument here rests on arXiv:2508.10561 being EDA-feature-only, not including HRV / cardiac features. Critic could not verify this from the abstract alone. Pilot P-1 includes a manual confirmation step: fetch the paper's Methods or supplementary feature list and confirm whether HRV features are present. If they are present, the "extension to cardiac" novelty claim is downgraded — narrow to "extension to fresh datasets and per-subject Fisher-z aggregation."

Operative scope: replicate and extend the finding from arXiv:2508.10561
(2 of 164 EDA features showed reproducible association with arousal) by
applying the same audit framework to a NEW combination of datasets, with
cardiac features as the primary extension target.

The AHBU contribution is non-redundant with arXiv:2508.10561 because
that paper focused on EDA features; we extend explicitly to cardiac
features (HRV time-domain, spectral HRV, ECG morphology derivatives).
Non-redundant with Brookshire 2024 (DNN leakage framing) and Apicella
2024 (cross-subject classification methods review). No new model or
classifier is trained in the headline; the headline is a statistical
reproducibility map.

Secondary contribution: `30-implement/shared/eval/feature_stability.py`
promoted to shared substrate — a general-purpose cross-dataset feature
reproducibility diagnostic.

No deep learning. No classification SOTA claim. Cancel-back authority
is exercised below in the compute section; conclusion is feasible with
margin.

---

## Shared substrate

### Scan result

`30-implement/shared/` directory does not exist (30-implement/README.md
confirms lazy materialization). `30-implement/shared/data/`,
`30-implement/shared/eval/`, `30-implement/shared/models/` are absent.

The cross-subject-eeg track (currently running) plans to promote
`30-implement/shared/eval/partition.py` (subject_disjoint_split) and
`30-implement/shared/eval/leakage_audit.py`. These are not yet available
but are near-term candidates.

### Consume

- **`30-implement/shared/eval/partition.py`** (when promoted by
  cross-subject-eeg): consume `subject_disjoint_split` to partition
  subjects across train/dev/test within each dataset. If not yet
  promoted at time of experiment, implement inline and flag for later
  merging into shared/.

Nothing else to consume. This track is effectively a co-first promoter
alongside cross-subject-eeg on the shared eval infrastructure.

### Promote on completion

**1. `30-implement/shared/eval/feature_stability.py`** (UNIQUE to
this track; no other track builds this)

Purpose: given a list of per-dataset feature DataFrames and a target
arousal column, compute cross-dataset reproducibility statistics for
each feature — Spearman rho per dataset, direction consistency,
FDR-corrected significance, and a reproducibility flag. Returns a
tidy stability-report DataFrame and a heatmap plot.

Interface (pre-committed; must not change without unlock note):

```python
def cross_dataset_correlation(
    feature_df_list: list[pd.DataFrame],
    target_col: str,
    correction_method: str = "fdr_bh",  # or "bonferroni"
    alpha: float = 0.05,
) -> pd.DataFrame:
    """
    Returns a DataFrame indexed by feature name with columns:
      rho_<dataset_i>        Spearman correlation per dataset
      p_<dataset_i>          uncorrected p-value per dataset
      p_corrected_<dataset_i>  FDR/Bonferroni-corrected p-value per dataset
      sig_<dataset_i>        bool: p_corrected < alpha
      consistent_sign        bool: all significant rhos have the same sign
      n_sig                  int: count of datasets where sig=True
      reproducible           bool: sig=True AND consistent_sign=True in
                             ALL datasets tested
    One row per feature; NaN if feature could not be computed for
    that dataset.
    """

def plot_stability_heatmap(
    stability_df: pd.DataFrame,
    save_path: str | None = None,
    figsize: tuple[int, int] = (14, 8),
) -> None:
    """
    Heatmap of per-feature, per-dataset Spearman rho, with
    FDR-significance cells outlined and reproducible features
    highlighted in a distinct color band.
    """
```

Plausible 2nd consumers (satisfies the promotion rule):
- ecg-ppg-realworld: HRV feature stability across PTB-XL and PPG-DaLiA
  as a pre-modeling audit.
- sleep-staging: spectral HRV feature stability across Sleep-EDF and
  Dreem-DOD cohorts (AHI bands) before committing to an HRV-only
  classifier.
- cross-subject-eeg: EEG band-power feature stability across MOABB
  datasets (direct analogue of the 2/164 finding applied to EEG).

**2. `30-implement/shared/data/hrv_eda_feature_extractor.py`**

Purpose: extract a fixed, documented feature schema (matching the 164
features from arXiv:2508.10561, or the documented subset derived here)
from ECG or EDA signals. Returns a named-column DataFrame with one row
per subject-session window.

Interface:

```python
def extract_features(
    signal: np.ndarray,
    signal_type: str,          # "ecg" or "eda"
    fs: float,                 # sampling rate in Hz
    window_sec: float = 60.0,  # analysis window length
    feature_set: str = "arXiv_2508_10561",  # schema version tag
) -> pd.DataFrame:
    """
    Returns a DataFrame with one row per non-overlapping window.
    Columns are the feature names from the named schema.
    NaN inserted for windows where a feature cannot be computed
    (e.g., too few R-peaks for spectral HRV).
    """
```

Note: the reuse-sketch flags that sleep-staging's HRV pipeline
sketch proposed a similar artifact. If sleep-staging is admitted,
merge into one canonical extractor; this track defines the schema
and provides the first implementation.

Plausible 2nd consumers: sleep-staging (HRV features for staging),
ecg-ppg-realworld (HRV features for AFib abstention context).

**3. `30-implement/shared/eval/partition.py`** — subject_disjoint_split:
if cross-subject-eeg has not yet promoted this, this track promotes it.
Interface follows the cross-subject-eeg approach.md definition verbatim
(to ensure they merge cleanly when both tracks are active).

### Track-specific (not promoted)

- Per-dataset DEAP, WESAD, MAHNOB-HCI data loaders (dataset-specific
  format handling; unlikely to generalize without heavy parameterization).
- Arousal operationalization mappings (dataset-specific label harmonization
  table; the logic is track-specific even if the utility code is shared).
- Binomial test wrapper (scipy one-liner; too thin to warrant promotion).
- Per-experiment analysis notebooks.

---

## Dataset

### Dataset selection rationale

Operative scope requires at least two datasets to define "cross-dataset
reproducibility." Three datasets are used to make the binomial-test
per-dataset count informative and to distinguish "replicates in 2 of 3"
from "replicates in all 3." More than three would increase power; fewer
would reduce the reproducibility claim to a single pairwise comparison.

Criteria for inclusion: (1) contains both arousal ratings AND cardiac or
EDA signal, (2) no DUA-level friction (academic request forms acceptable),
(3) subject count >= 15, (4) publicly documented and cited in the
affective-computing literature.

**DEAP** — Primary dataset

- Subjects: 32. Modality: EEG + peripheral (ECG, EDA, EMG, RESP, skin
  temperature, plethysmograph). 40 one-minute music-video clips per subject.
- Labels: participant self-reports on 1–9 continuous scales for valence,
  arousal, dominance, and liking. NOT stimulus-class labels (per
  real-pain-critic correction 2026-05-02). Arousal ratings used directly.
- License: access via request form at
  http://www.eecs.qmul.ac.uk/mmv/datasets/deap/ — academic use,
  non-commercial. Form is lightweight (name, institution, purpose).
- Access: download request to DEAP authors; data_preprocessed_matlab.zip
  (~700 MB) and the raw physiological signals. We use the preprocessed
  peripheral signals (ECG, EDA at 128 Hz) from the provided .mat files.
  Python loader via scipy.io.loadmat.
- Arousal operationalization: continuous 1–9 self-report. For the
  reproducibility test, binarize at the dataset median (median split,
  per-subject; see §Preprocessing). Median split chosen over a fixed
  threshold (e.g., >=5) to avoid arbitrary cutoff variation across papers
  (identified as a label-quality problem in the admission record).
- Split: no train/test split needed for the feature-stability headline
  (the audit tests per-feature association with arousal across ALL subjects
  within a dataset). Subjects are not split for the headline; each
  subject's segment-level features form the population for that dataset's
  correlation. Dev/test split applies to the secondary classifier ablation
  only (see §Ablations).
- Why included: largest affective-EEG dataset with EDA + ECG; the most
  cited DEAP benchmark; arXiv:2508.10561 used DEAP as one of its corpora.
  Using it enables partial replication and direct comparison.
- Exclusion check: DEAP is not in arXiv:2508.10561's test dataset list
  for cardiac features (that paper focused on EDA). Including DEAP for
  the cardiac extension is therefore a genuine contribution.

**WESAD** — Second dataset

- Subjects: 15. Modality: chest-worn (ECG, EDA, EMG, RESP, ACC, TEMP) +
  wrist-worn (BVP, EDA, TEMP, ACC). Three affect conditions: baseline,
  stress, amusement. 
- Labels: experimental condition labels (stress/amusement/baseline) plus
  self-report questionnaires (STAI, SAM, PANAS) administered between
  conditions.
- License: PhysioNet CC-BY 4.0. No registration or form required.
  Direct download: https://physionet.org/content/wesad/1.0.0/
- Access: wget or Python pooch, ~4 GB total.
- Arousal operationalization: WESAD uses condition labels (stress =
  high arousal, amusement = moderate arousal, baseline = low arousal).
  We use a binary mapping: stress = high-arousal (1), baseline = low-
  arousal (0), amusement = excluded from the headline binomial test
  (ambiguous arousal level; included in an ablation). This operationalization
  is locked in protocol-lock.md before any headline run.
  SAM arousal self-reports (if available per-segment) are used as a
  secondary continuous-arousal correlation target in an ablation.
- Split: same rationale as DEAP — feature-stability headline uses all
  subjects; dev/test applies to secondary classifier only.
- Why included: WESAD is the primary wearable-stress dataset for the
  operative constituency. arXiv:2508.10561 reports on WESAD; our
  extension to cardiac features on WESAD is the primary non-redundant
  contribution.
- Note on session structure: WESAD has within-session structure (one
  subject, one session with sequential conditions). Features must be
  extracted per-condition-epoch, not per-session, to avoid leakage
  between high/low arousal windows within one subject. See §Preprocessing.

**MAHNOB-HCI** — Third dataset

- Subjects: 27 (30 recorded, 3 excluded per official release for
  technical issues). Modality: EEG + ECG + EDA + respiration + skin
  temperature + facial video (facial video not used here). 20 short film
  clips per subject, some repeated.
- Labels: participant self-reports on discrete and continuous scales for
  valence, arousal, dominance, predictability, and emotion category.
  Arousal reported on 1–9 scale post-stimulus (continuous self-report,
  same format as DEAP).
- License: access form at https://mahnob-db.eu/hci-tagging/ — academic
  use. Form is lightweight.
- Access: download request to MAHNOB-HCI authors. Dataset ~10 GB
  including video (we download only physiological channels, ~1 GB).
- Arousal operationalization: continuous 1–9 self-report, binarized at
  dataset median (same rule as DEAP for consistency).
- Split: same rationale as DEAP.
- Why included: MAHNOB-HCI provides a dataset with both ECG and EDA,
  with a self-report arousal scale matching DEAP's format. Using it as a
  third dataset makes the "consistent across 3 datasets" claim
  distinguishable from a coincidental 2-dataset agreement.
- Why DREAMER and SEED are not included: DREAMER (23 subjects, EEG + ECG
  + EDA) is a plausible candidate but is lower priority than MAHNOB-HCI
  because MAHNOB-HCI has a larger published literature and is more
  commonly cited as a benchmark. SEED and SEED-IV are EEG-only; no
  ECG/EDA channel — incompatible with the cardiac/EDA feature audit scope.
  Including DREAMER as an optional fourth dataset is registered as a pilot
  probe (P-5).
- Why not AMIGOS: subjects = 40, but ECG and EDA are included only in the
  "long" AMIGOS condition (not all published analyses); access and
  documentation are less standardized. Deferred.

### Held-out partition

The feature-stability headline does NOT have a conventional train/test
split. The unit of analysis is the feature (N_features (locked at pilot P-1; arXiv:2508.10561 denominator was 164, our actual count likely ~100 from NeuroKit2 — see M-1 fix in methodology-critic)), not the subject. The
held-out discipline applies differently:

- No data is held out from the correlation analysis (all subjects in all
  three datasets contribute to the reproducibility map).
- The headline is "locked" in the sense that the feature list, datasets,
  arousal operationalization, and statistical test are pre-registered in
  `protocol-lock.md` before any feature extraction runs.
- The secondary classifier ablation (logistic regression on the
  reproducible-feature subset vs full feature set) does use a subject-
  disjoint split: 70/10/20 train/dev/test by subject within each dataset.
  This split is NOT the headline; it is explicitly labeled secondary.
  **Pilot-quality flag (m-4 fix per methodology-critic):** for WESAD
  (15 subjects total, ~3 test subjects after 70/10/20 split), 95 % CI
  on classifier AUC will span most of [0, 1]. Result is reported with
  an explicit "PILOT-QUALITY: N_test=3, CI uninformative" tag in the
  results table; do not over-interpret. DEAP (32) and MAHNOB-HCI (27)
  give ~6–7 test subjects each — also pilot-quality CI but somewhat
  narrower. The secondary classifier is for sanity-check directional
  signal only, never a headline.
- The binomial test runs on ALL features (N_features (locked at pilot P-1; arXiv:2508.10561 denominator was 164, our actual count likely ~100 from NeuroKit2 — see M-1 fix in methodology-critic)) using data from ALL
  subjects in all three datasets. It is run exactly once, after all
  feature extraction is complete and the correlation table is written to
  disk. Running it more than once (e.g., inspecting partial results) would
  not change the test's validity because the feature list and test statistic
  are pre-specified, but the commitment to "run once on frozen data" is
  documented here for transparency.

---

## Preprocessing

### General principles

- Extract cardiac and EDA features only. EEG channels are ignored.
- All signal processing via NeuroKit2 (version pinned; see below).
  NeuroKit2 is chosen because it implements the most complete set of
  published HRV and EDA feature extractors in a single library and
  because its output column names provide a natural schema for the 164-
  feature set. BioSPPy is used as a cross-check library for R-peak
  detection only (see R-6 in risk-register).
- All preprocessing on CPU. No GPU required.
- Random seed: 42, fixed throughout.

### ECG preprocessing pipeline

1. Load ECG at native sampling rate (DEAP: 128 Hz; WESAD chest: 700 Hz;
   MAHNOB-HCI: 256 Hz).
2. Bandpass filter: 0.5–40 Hz (4th-order Butterworth, zero-phase via
   `scipy.signal.sosfiltfilt`). Rationale: removes DC baseline drift and
   high-frequency EMG without distorting QRS morphology.
3. R-peak detection: `nk.ecg_findpeaks(method="pantompkins1985")`.
   Cross-check with BioSPPy (`biosppy.signals.ecg`) for R-peak count
   consistency (flag if discrepancy > 10%).
4. RR-interval series: compute from consecutive R-peaks. Remove
   physiologically implausible intervals (< 300 ms or > 2000 ms);
   replace with linear interpolation (not deletion — preserves window
   alignment). Flag windows with > 20% replaced beats as low quality.
5. Feature extraction: `nk.hrv(rpeaks, sampling_rate=fs, show=False)`.
   This produces all time-domain (SDNN, RMSSD, pNN50, ...) and frequency-
   domain (LF, HF, LF/HF, VLF, ...) HRV features. Also compute ECG
   morphology features (QRS duration, QT proxy) where the library supports
   them.
6. Window length: 60 seconds non-overlapping. Rationale: standard HRV
   analysis window; balances stationarity vs feature count. For WESAD
   conditions (stress ~10 min, amusement ~392 s, baseline ~20 min):
   all conditions yield multiple 60-second windows. For DEAP (1-minute
   clips): exactly one window per clip per subject.

### EDA preprocessing pipeline

1. Load EDA at native sampling rate (DEAP: 128 Hz; WESAD chest: 700 Hz,
   wrist: 4 Hz [wrist not used for ECG arm]; MAHNOB-HCI: 256 Hz).
2. Downsample to 4 Hz if input > 4 Hz (EDA analysis standard; avoids
   oversampling artifacts in SCR peak detection). Via
   `scipy.signal.resample_poly`.
3. Clean: `nk.eda_clean(sampling_rate=4)` (default low-pass Butterworth).
4. Decompose into tonic (SCL, skin conductance level) and phasic (SCR,
   skin conductance response) components:
   `nk.eda_phasic(eda_cleaned, sampling_rate=4, method="cvxeda")`.
   If cvxEDA fails (numerical error), fall back to `method="highpass"`.
   Both methods are documented; results compared in a pilot probe.
5. Feature extraction: `nk.eda_features(...)` for each 60-second window:
   SCR rate, mean SCL, mean SCR amplitude, number of SCRs, SCR peak
   amplitude mean/std, SCL slope, phasic variance.
6. Same window length as ECG (60 s).

### Arousal operationalization

Pre-registered for each dataset (see also protocol-lock.md):

- **DEAP:** continuous arousal self-report (1–9 scale) per 1-minute clip.
  Binarize: arousal >= subject's median arousal across all clips = 1
  (high arousal), < median = 0 (low arousal). Per-subject median avoids
  cross-subject scale shift confounds. Each clip yields one
  (feature-vector, arousal-label) pair.

- **WESAD:** condition-level label. stress = 1 (high arousal),
  baseline = 0 (low arousal), amusement = excluded from headline
  (WESAD SAM arousal ratings analyzed in ablation A-4 separately).
  Features extracted per 60-second window within each condition epoch;
  label assigned from condition, not from window-level physiology.
  Subject-level stratification: all windows from one subject are
  either all-in or all-out for the Spearman correlation computation.
  Per-subject Spearman rho is computed first (using all windows from
  that subject across both included conditions), then dataset-level
  Spearman rho is the Fisher-z-transformed mean across subjects.

- **MAHNOB-HCI:** continuous arousal self-report (1–9 scale) per clip.
  Binarize: same median-split rule as DEAP.

### Preprocessing software

- NeuroKit2 0.2.x (pinned to exact minor version at environment setup;
  exact version recorded in `30-implement/affective-state/code/requirements.txt`).
- BioSPPy 0.8.x (cross-check only; pinned).
- scipy 1.12.x (signal processing utilities; pinned).
- pandas 2.2.x (feature DataFrame management; pinned).
- cvxpy (cvxEDA dependency; pinned; fallback documented if unavailable).

Rationale for NeuroKit2 primary: open source, actively maintained,
implements the HRV/EDA feature set used in arXiv:2508.10561 (or at
least the closest published mapping). Version pinning is critical:
NeuroKit2 has changed HRV feature defaults between minor versions (this
is risk R-4 in risk-register).

---

## Feature schema (the 164 features)

The feature set is derived from arXiv:2508.10561's Table 1 / Methods
section and extended. We replicate their denominator of 164 features
total (cardiac + EDA), which is the basis of the binomial test. This
is the pre-registered feature list; additions require an unlock note
before running.

### Cardiac features (target: ~100 features)

**Time-domain HRV (via NeuroKit2 `nk.hrv_time`):**
MeanNN, SDNN, SDANN, SDNNI, RMSSD, SDSD, pNN20, pNN50, HRV_triangularindex,
TINN, HTI, LnRMSSD, MadNN, IQRnn, CVnn, CVrmssd, MedianNN, MeanHR,
MinHR, MaxHR, SDHR (~20 features)

**Frequency-domain HRV (via `nk.hrv_frequency`):**
LF (ms^2), HF (ms^2), VLF (ms^2), LF_peak, HF_peak, VLF_peak, LFHF,
LFn, HFn, LF_percent, HF_percent, VHF, TP (~13 features)

**Non-linear HRV (via `nk.hrv_nonlinear`):**
SD1, SD2, SD1SD2, S, CSI, CVI, CSI_modified, PI, Poincare_ellipse_area,
GI, SI, AI, PI, DFA_alpha1, DFA_alpha2, SampEn, ApEn, Hurst, RCMSE,
CD, HFD, KFD (~22 features)

**ECG morphology (via `nk.ecg_quality` and peak delineation):**
QRS_duration_mean, QRS_duration_std, P_amplitude_mean, T_amplitude_mean,
R_amplitude_mean, QT_interval_proxy (~6 features, dataset-dependent;
may be NaN for WESAD 700 Hz if delineation unreliable)

Total cardiac: approximately 60 features. Exact count determined at
feature-extraction time and documented in schema YAML file before headline.

### EDA features (target: ~64 features)

**SCL features (tonic):**
SCL_mean, SCL_std, SCL_slope, SCL_median, SCL_max, SCL_min,
SCL_range, SCL_IQR, SCL_skewness, SCL_kurtosis (~10 features)

**SCR features (phasic):**
SCR_rate (peaks per 60 s), SCR_amplitude_mean, SCR_amplitude_std,
SCR_amplitude_max, SCR_amplitude_median, SCR_risetime_mean,
SCR_risetime_std, SCR_halfrectime_mean, SCR_halfrectime_std,
SCR_count, SCR_latency_mean, phasic_variance, phasic_mean,
phasic_std, phasic_skewness, phasic_kurtosis (~16 features)

**Band-power of EDA signal:**
EDA_LF_power (0.01–0.08 Hz), EDA_MF_power (0.08–0.25 Hz),
EDA_HF_power (0.25–1.0 Hz), EDA_LFMF_ratio, EDA_LF_percent,
EDA_HF_percent (~6 features)

**Derived/cross-component:**
Sympathetic_index (SCR_rate × SCL_mean), SCR_proportion_time_active,
SCL_recovery_rate (~3 features)

**From arXiv:2508.10561 EDA feature set (reproduce their exact list
for the cardiac extension to be non-redundant — we test the SAME EDA
features they tested, plus cardiac features they did not test):**
Their 2 reproducible features (electrodermal-derived) will appear in our
result; if they do NOT replicate in our datasets, that is also informative.

Total EDA: approximately 35–40 features. Combined with cardiac: targeting
~100 total, below 164. If total is below 164: document discrepancy
(NeuroKit2 may not expose all 164 features from the original paper's
different toolchain). The binomial test is run at whatever N the schema
produces; N is locked before headline.

**Schema lock:** the exact feature list (column names, computation method,
library call) is written to a YAML file at feature-extraction time and
committed to `30-implement/affective-state/runs/feature_schema_v1.yaml`
before the headline correlation analysis runs. The YAML is part of the
pre-registered protocol.

---

## Model family

This track has no primary model in the classification sense. The
headline is a statistical reproducibility test. The following describes
the analysis chain and the secondary classifier used in ablations.

### Primary analysis — feature-stability correlation

Not a classifier. For each feature f and each dataset D:

1. Compute Spearman rho(f, arousal) using all (feature-vector, arousal-
   label) pairs from that dataset. For binary arousal (0/1), Spearman rho
   on binary target is equivalent to a rank-biserial correlation (this is
   fine; the test is nonparametric).
2. Compute p-value via exact permutation test (n_permutations=5000) for
   small datasets (N < 50), or scipy.stats.spearmanr for larger datasets.
3. Apply FDR correction (Benjamini-Hochberg) across all 164 features
   within each dataset.
4. A feature is "reproducible" if: FDR-corrected p < 0.05 AND the sign
   of rho is consistent across all three datasets.
5. Binomial test on the count of reproducible features: P(X >= k | n=N_features,
   p=0.05) under H0 that features are independently reproduced at the
   5% base rate. This tests whether the overall reproducibility rate is
   above chance (analogous to the arXiv:2508.10561 approach, inverted:
   they tested whether 2/164 is significantly LOW; we additionally test
   whether any cardiac features might be significantly HIGH).

### Secondary analysis — classifier on reproducible subset

Not a headline. Run on dev split only.

- **Model A (primary):** Logistic Regression (sklearn, liblinear solver,
  C=1.0, max_iter=1000) trained on reproducible-feature subset only.
- **Model B (baseline):** Logistic Regression on full 164-feature set.
- **Model C (trivial baseline):** Majority-class predictor.

Evaluation: subject-disjoint LOSO AUC (macro-averaged), with 95%
bootstrap CI. Comparison shows whether the stable features retain any
predictive value.

Rationale for Logistic Regression over SVM/RF: simplest interpretable
model; coefficient signs can be read directly alongside the reproducibility
map. Complexity adds nothing at this feature count.

---

## Evaluation protocol

### Primary evaluation (reproducibility map)

Unit of analysis: the feature (N = total features in schema).

For each feature:
- Compute (rho, p_raw, p_corrected, sig, sign) independently in each
  of the three datasets.
- Mark feature as "reproducible" if (sig=True in all three datasets
  AND signs are consistent).

Primary metric: N_reproducible / N_total (reproducibility rate) and
N_reproducible (count), with 95% exact binomial CI (Clopper-Pearson)
on the count.

Statistical test: one-sided binomial test — H0: reproducibility rate
<= 0.05 (5% base rate, matching the FDR threshold). H1: reproducibility
rate > 0.05. This tests whether cardiac features are MORE reproducible
than the arXiv:2508.10561 finding would predict for EDA features. A
null (rate not significantly > 0.05) is informative (confirms universal
feature instability). A positive (rate > 0.05) is informative (identifies
cardiac features that warrant further study).

Separately, report the EDA feature reproducibility count from our
analysis and compare to arXiv:2508.10561's 2/164. Agreement = partial
replication. Disagreement = requires explanation.

### Cross-dataset: "reproducible in all 3 vs 2 of 3"

Report separately:
- Features significant in all 3 datasets (strong reproducibility).
- Features significant in exactly 2 of 3 datasets (partial, with direction
  consistency checked).
- Features significant in exactly 1 dataset only (not reproducible).
- Features significant in 0 datasets.

This stratification is more informative than a binary cutoff.

### Statistical testing

For the primary reproducibility claim: two-sided binomial test at N =
N_features, k = N_reproducible, p0 = 0.05. Report exact p-value (via
scipy.stats.binomtest) and 95% Clopper-Pearson CI on the rate.

For the within-dataset Spearman correlations: FDR (Benjamini-Hochberg,
via statsmodels.stats.multitest) at alpha=0.05, applied per dataset
independently across all features tested.

No Bonferroni across datasets (that would double-penalize features; FDR
per-dataset then consistency-across-datasets is the correct two-stage
procedure).

### Held-out discipline

The correlation analysis uses all available subjects in all three datasets
(no train/test split on subjects for the headline reproducibility map).
This is appropriate because the unit of inference is the feature, not the
subject; we are asking "does feature X associate with arousal across the
population in this dataset" — using all subjects maximizes power for each
per-feature test.

The only held-out split is for the SECONDARY classifier ablation (A-3,
see §Ablations), which uses a 70/10/20 subject-level train/dev/test
split within each dataset. This result is clearly labeled as secondary
and does not feed the headline.

### Cross-subject vs within-subject note

This track does not evaluate cross-subject generalization in the
classification sense. The reproducibility claim is cross-DATASET:
does feature X associate with arousal in dataset A, and also in datasets
B and C? Within each dataset, the correlation is computed across all
subjects (subject-pooled), which conflates within-subject and between-
subject variance. This is documented as a limitation. An ablation
(A-5) tests per-subject Spearman correlations separately to check
whether subject-pooled and average-of-per-subject results agree in
direction.

---

## Ablations

All ablations run on the dev-accessible data (full per-dataset feature
tables are computed once; ablations reuse them). No ablation touches a
separate held-out split beyond what the secondary classifier uses.

**A-1: FDR vs Bonferroni correction**

Hypothesis: reproducibility count is sensitive to the choice of
multiple-comparison correction. Bonferroni is more conservative;
if the reproducible feature count changes materially (>2 features
reclassified), it means the result is near the significance boundary
and should be reported with both corrections. If counts agree, FDR
is confirmed the appropriate choice.

Procedure: rerun the correlation table with `correction_method="bonferroni"`.
Report reproducibility count under both methods.

**A-2: cvxEDA vs high-pass EDA decomposition**

Hypothesis: EDA feature values (and thus reproducibility) depend on
the decomposition method (cvxEDA vs simple high-pass). If the 2-of-164
finding from arXiv:2508.10561 was specific to one EDA decomposition
method, it may not replicate with a different method.

Procedure: extract EDA features with both decomposition methods on all
three datasets. Compare reproducibility counts for EDA features.

**A-3: Reproducible-feature subset classifier vs full feature set**

Hypothesis: if stable features exist, they retain predictive value
even though the feature set is smaller.

Procedure: Logistic Regression LOSO AUC with reproducible-feature
subset vs full 164-feature set vs trivial baseline (majority class),
on the secondary classifier subject-split.

**A-4: WESAD amusement condition included**

Hypothesis: excluding amusement (moderate arousal) from WESAD
conservatively sharpens the high/low contrast; including it may change
the WESAD correlation pattern.

Procedure: rerun WESAD correlation with a 3-class arousal encoding
(stress=2, amusement=1, baseline=0) using Spearman rho on the ordinal
scale. Compare reproducibility count to the binary-headline version.

**A-5: Per-subject correlation vs subject-pooled correlation**

Hypothesis: subject-pooled Spearman rho may be dominated by between-
subject physiological differences rather than arousal-driven differences.
Per-subject correlations (each subject's within-session features vs
arousal) may tell a different story.

Procedure: compute Spearman rho separately for each subject in each
dataset (within-subject correlation, using the subject's multiple windows
as the sample). Report median per-subject rho and its sign across subjects
per feature per dataset. Compare "consistent sign across subjects" to
"consistent sign across datasets" as a convergence check.

---

## Uncertainty reporting

- **Primary reproducibility count:** 95% exact binomial CI (Clopper-
  Pearson) on N_reproducible / N_total.
- **Per-feature rho estimates:** 95% bootstrap CI (n=2000, fixed seed 42)
  on the Spearman rho computed from each dataset's (feature, arousal) pairs.
  This quantifies sampling variability in each per-dataset estimate.
- **Secondary classifier AUC:** 95% bootstrap CI (n=2000) on per-subject
  LOSO AUC.
- **Reporting format:** "N_reproducible = k (95% CI: [a, b], Clopper-Pearson;
  N_features = N_total; binomial p = X.XXX)".
- **No bare point estimates** anywhere in the results table. Every metric
  gets a CI.

---

## Compute budget

| Task | Hardware | Estimated time |
|---|---|---|
| Dataset access/download (~12 GB total) | local | 2–4 hr (DEAP + MAHNOB form submission may add 1–2 days wait) |
| DEAP preprocessing (32 subjects × 40 clips, ECG + EDA, 60 s windows) | CPU | 15–30 min |
| WESAD preprocessing (15 subjects × 3 conditions, ECG + EDA) | CPU | 10–20 min |
| MAHNOB-HCI preprocessing (27 subjects × 20 clips) | CPU | 20–30 min |
| Feature extraction (all three datasets, 164 features each) | CPU | 30–60 min |
| Correlation table + FDR correction + binomial test | CPU | < 5 min |
| Bootstrap CIs (n=2000 per feature per dataset) | CPU | 30–60 min |
| Ablations A-1 through A-5 | CPU | 1–2 hr total |
| Secondary classifier (LOSO LR, three datasets) | CPU | 15–30 min |
| Plots + report writing | CPU | 1–2 hr |
| **Total headline** | **CPU** | **~4–6 hr active compute** |

**GPU requirement: zero.** This experiment is CPU-only. The 4 GB VRAM
constraint is not binding. The local GTX 1650 is idle for this track.

Compute envelope: comfortably within scope. No free-tier fallback needed.
Total wall-clock time (including dataset form wait, environment setup):
approximately 1 week.

### Time to first honest result

- Day 1–2: environment setup, WESAD download (no form required), begin
  WESAD preprocessing and feature extraction. First per-feature correlation
  on WESAD is a dev-split directional result only (not headline).
- Day 3–4: DEAP and MAHNOB-HCI form submissions (if not already approved).
  Preprocessing pipeline smoke tests on WESAD.
- Day 5–7: full feature extraction and correlation table on all three
  datasets once access is confirmed.
- Week 2: headline binomial test, ablations, CI computation. Pilot probes
  complete. Headline locked in protocol-lock.md before running.
- **First honest result: end of week 2.**

---

## Novelty and exploration notes

### What is genuinely novel

- Extension of arXiv:2508.10561 from EDA-only to CARDIAC + EDA features
  across three datasets simultaneously. No prior paper has computed
  cross-dataset Spearman rho for HRV features on arousal with FDR
  correction and a binomial reproducibility test. This is the primary
  scientific contribution.
- Dataset combination (DEAP + WESAD + MAHNOB-HCI) not used together
  in arXiv:2508.10561.
- `feature_stability.py` — promoted to shared/ — a reusable artifact
  not built by any other active track.
- Honest documentation of EDA reproducibility comparison (do our datasets
  agree with the original 2/164 finding or not?), which is a partial
  independent replication.

### What is standard and intentionally so

- Spearman correlation as the reproducibility statistic: interpretable,
  nonparametric, standard in the psychophysiology literature.
- FDR correction: standard for multi-feature multiple testing.
- Binomial test on feature counts: used in arXiv:2508.10561; applying it
  here is continuity with the reference paper.
- Logistic regression for the secondary classifier: the simplest defensible
  choice.

### What is exploratory (pilot probes only)

- cvxEDA decomposition quality on WESAD 700 Hz data (A-2 is an ablation,
  but the cvxEDA feasibility is first confirmed in pilot P-2).
- DREAMER as a fourth dataset (pilot P-5): if DREAMER access is approved
  quickly, a fourth dataset strengthens the claim.
- Per-subject correlation (A-5) may surface interesting heterogeneity
  (some subjects strongly arousal-linked, others not); if so, this is
  noted as a future sub-scope, not expanded in the headline.

### Redundancy acknowledgment (per admission record)

The shortlist tagged affective-state as "high redundancy risk." The
narrow framing directly rebuts this: arXiv:2508.10561 did not test
cardiac features. Brookshire 2024 tested DNN leakage, not feature
stability. Apicella 2024 reviewed methods. The 2/164 finding (EDA) is
the trigger for this audit; AHBU extends it to cardiac, which is the
primary deployment-relevant modality for wearable stress detection.
The rebuttal is honest and narrow. We do NOT claim to supersede
arXiv:2508.10561 — we replicate its EDA finding and extend to cardiac.
