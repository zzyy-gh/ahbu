> **Spec:** `10-pain-point/affective-state/admission.md`

# Protocol lock — affective-state
**Track:** affective-state
**Originally locked:** 2026-05-02
**Unlocked:** 2026-05-03 (unlock-note-2026-05-03.md)
**Re-locked:** 2026-05-03
**Locked by:** methodologist agent (re-pass)
**Status:** LOCKED — re-locked after pilot-driven EDA pipeline revision

This document defines the frozen evaluation protocol for the headline
experiment. Changes after this re-lock require a new unlock note.

This re-lock supersedes the 2026-05-02 version. The unlock note
(`unlock-note-2026-05-03.md`) documents the two changes: (1) EDA
decomposition method changed from cvxEDA-primary to highpass-only, and
(2) EDA feature list expanded from 6 (nk.eda_features output only) to
~42 (nk.eda_features + explicitly enumerated SCL, SCR, band-power, and
derived features). Total N_features revised from 92 to 126 (pre-committed),
exact count locked in feature_schema_v2.yaml at first successful extraction.

---

## 0. Pre-registration statement

This protocol is re-locked before any headline feature extraction or
correlation analysis runs. The correlation table has not been computed.
No feature-level result has been seen from real data. Pilots P-1 through
P-3 and P-6 used (a) synthetic data only, (b) WESAD subject s2 pipeline
verification without per-feature correlation, and (c) WESAD window-count
checks without any feature-arousal computation. DEAP and MAHNOB-HCI have
not been downloaded as of this re-lock date.

The three items required by the defensibility-critic advisory remain
explicitly locked below: (1) feature list, (2) dataset selection,
(3) arousal operationalization.

---

## 1. Dataset selection (FROZEN)

The headline uses exactly these three datasets. Unchanged from 2026-05-02.

**Dataset A: WESAD**
- Source: PhysioNet, CC-BY 4.0. No registration required.
- Version: PhysioNet release 1.0.0 (DOI 10.13026/C2088N).
- Signals used: chest-worn ECG (700 Hz) and EDA (700 Hz). Wrist-worn
  signals not used.
- Subjects: all 15 subjects (s2 through s17; s1 excluded per official
  WESAD documentation as a test subject).
- Status: confirmed available and pipeline-verified (P-2, P-3).

**Dataset B: DEAP**
- Source: request form at http://www.eecs.qmul.ac.uk/mmv/datasets/deap/
  (academic use, non-commercial).
- Version: data_preprocessed_matlab.zip (32 subjects, 128 Hz peripheral).
- Signals used: ECG channel and GSR (EDA) channel. Arousal labels: column
  index 1 of the labels array.
- Status: access form submitted; approval pending as of 2026-05-03.
- Fallback: if DEAP access is denied, substitute DREAMER (23 subjects,
  ECG + EDA). Fallback must be documented before processing begins.

**Dataset C: MAHNOB-HCI**
- Source: request form at https://mahnob-db.eu/hci-tagging/ (academic).
- Version: HCI-Tagging subset, 27 subjects.
- Signals used: ECG and EDA. Labels: feltArsl (1-9 scale).
- Status: access form submitted; approval pending as of 2026-05-03.
- Fallback: DREAMER (if DEAP fallback not already used). Two-dataset
  (WESAD + DREAMER) version accepted if both B and C denied.

**No other datasets enter the headline.**

---

## 2. Feature list (FROZEN — revised 2026-05-03)

The pre-registered feature list is the union of:
(A) all columns returned by the NeuroKit2 cardiac functions below,
(B) all columns returned by nk.eda_features below, and
(C) the explicitly enumerated supplementary EDA features below.

All features are extracted from 60-second non-overlapping windows at the
NeuroKit2 version pinned in requirements.txt (0.2.13).

The exact feature names are written to
`30-implement/affective-state/runs/feature_schema_v2.yaml` at the first
successful extraction on real data. feature_schema_v2.yaml is committed
before the headline correlation analysis runs.

### 2A. Cardiac features (86 confirmed by P-1)

Extracted from ECG signal only.

**Time-domain HRV — nk.hrv_time(rpeaks, sampling_rate=fs):**
All returned columns. Confirmed 25 features at NK 0.2.13:
HRV_MeanNN, HRV_SDNN, HRV_SDANN1, HRV_SDNNI1, HRV_SDANN2, HRV_SDNNI2,
HRV_SDANN5, HRV_SDNNI5, HRV_RMSSD, HRV_SDSD, HRV_CVNN, HRV_CVSD,
HRV_MedianNN, HRV_MadNN, HRV_MCVNN, HRV_IQRNN, HRV_SDRMSSD,
HRV_Prc20NN, HRV_Prc80NN, HRV_pNN50, HRV_pNN20, HRV_MinNN, HRV_MaxNN,
HRV_HTI, HRV_TINN.

**Frequency-domain HRV — nk.hrv_frequency(rpeaks, sampling_rate=fs):**
All returned columns. Confirmed 10 features at NK 0.2.13:
HRV_ULF, HRV_VLF, HRV_LF, HRV_HF, HRV_VHF, HRV_TP, HRV_LFHF,
HRV_LFn, HRV_HFn, HRV_LnHF.

**Non-linear HRV — nk.hrv_nonlinear(rpeaks, sampling_rate=fs):**
All returned columns. Confirmed 51 features at NK 0.2.13:
HRV_SD1, HRV_SD2, HRV_SD1SD2, HRV_S, HRV_CSI, HRV_CVI, HRV_CSI_Modified,
HRV_PIP, HRV_IALS, HRV_PSS, HRV_PAS, HRV_GI, HRV_SI, HRV_AI, HRV_PI,
HRV_C1d, HRV_C1a, HRV_SD1d, HRV_SD1a, HRV_C2d, HRV_C2a, HRV_SD2d,
HRV_SD2a, HRV_Cd, HRV_Ca, HRV_SDNNd, HRV_SDNNa, HRV_DFA_alpha1,
HRV_MFDFA_alpha1_Width, HRV_MFDFA_alpha1_Peak, HRV_MFDFA_alpha1_Mean,
HRV_MFDFA_alpha1_Max, HRV_MFDFA_alpha1_Delta, HRV_MFDFA_alpha1_Asymmetry,
HRV_MFDFA_alpha1_Fluctuation, HRV_MFDFA_alpha1_Increment,
HRV_ApEn, HRV_SampEn, HRV_ShanEn, HRV_FuzzyEn, HRV_MSEn, HRV_CMSEn,
HRV_RCMSEn, HRV_CD, HRV_HFD, HRV_KFD, HRV_LZC,
HRV_Symbolic_EqualProb4_0V, HRV_Symbolic_EqualProb4_1V,
HRV_Symbolic_EqualProb4_2LV, HRV_Symbolic_EqualProb4_2UV.

**Cardiac subtotal: 86 features (confirmed P-1).**

### 2B. EDA features from nk.eda_features (6 confirmed by P-1)

Extracted from the cleaned EDA signal (highpass decomposition).
Decomposition: `nk.eda_phasic(eda_cleaned, sampling_rate=4, method="highpass")`.
**cvxEDA is not used.** Installation of cvxpy/cvxopt fails on the project
environment (Windows 11 + Python 3.11.2); confirmed by P-2. highpass is
the primary and only method.

nk.eda_features output at NK 0.2.13 (6 confirmed features):
EDA_NK_SCR_Peaks_N, EDA_NK_SCR_Peaks_Amplitude_Mean,
EDA_NK_EDA_Tonic_SD, EDA_NK_EDA_Sympathetic,
EDA_NK_EDA_SympatheticN, EDA_NK_EDA_Autocorrelation.

(Column names prefixed EDA_NK_ in feature_schema_v2.yaml to distinguish
from the supplementary features in §2C.)

**EDA-nk subtotal: 6 features (confirmed P-1).**

### 2C. Supplementary EDA features (enumerated, newly locked 2026-05-03)

All extracted from the highpass-decomposed tonic (SCL) and phasic
components for each 60-second window. All computed in Python using
scipy.signal and numpy. No additional library dependencies.

**SCL tonic features (10):**
Computed from the tonic component array (length = window_samples at 4 Hz):
- EDA_SCL_Mean: mean of tonic signal
- EDA_SCL_Std: standard deviation of tonic signal
- EDA_SCL_Slope: linear regression slope (scipy.stats.linregress, seconds as x)
- EDA_SCL_Median: median of tonic signal
- EDA_SCL_Max: maximum value
- EDA_SCL_Min: minimum value
- EDA_SCL_Range: max - min
- EDA_SCL_IQR: 75th - 25th percentile (numpy.percentile)
- EDA_SCL_Skewness: scipy.stats.skew of tonic signal
- EDA_SCL_Kurtosis: scipy.stats.kurtosis of tonic signal (excess kurtosis)

**SCR phasic features (14):**
Computed from the phasic component array and peak detection
(scipy.signal.find_peaks on the phasic signal, prominence >= 0.01 uS,
distance >= 4 samples at 4 Hz = 1 s minimum inter-peak interval):
- EDA_SCR_Rate: SCR peaks per 60 seconds (peak count / window_sec * 60)
- EDA_SCR_Amplitude_Mean: mean peak amplitude (prominence values)
- EDA_SCR_Amplitude_Std: std of peak amplitudes
- EDA_SCR_Amplitude_Max: maximum peak amplitude
- EDA_SCR_Amplitude_Median: median peak amplitude
- EDA_SCR_Risetime_Mean: mean rise time in seconds (sample-to-peak from onset)
  Onset = the sample at which the phasic signal begins rising before the peak
  (computed as the preceding local minimum).
- EDA_SCR_Risetime_Std: std of rise times
- EDA_SCR_HalfRec_Mean: mean half-recovery time in seconds (time for phasic
  to decay to 50% of peak amplitude after the peak).
  If end of window is reached before 50% recovery, use window-end time.
- EDA_SCR_HalfRec_Std: std of half-recovery times
- EDA_SCR_Latency_Mean: mean latency from window start to first peak (seconds).
  NaN if no peaks in window.
- EDA_SCR_IPI_Mean: mean inter-peak interval in seconds (time between
  consecutive peak indices). NaN if fewer than 2 peaks.
- EDA_SCR_IPI_Std: std of inter-peak intervals. NaN if fewer than 3 peaks.
- EDA_Phasic_Variance: variance of the phasic component signal
- EDA_Phasic_Skewness: scipy.stats.skew of phasic component

**EDA band-power features (6) — pre-registered in original §2 bullet 3:**
Computed via scipy.signal.welch on the cleaned (pre-decomposition) EDA
signal at 4 Hz, nperseg=64 (16 seconds), noverlap=32:
- EDA_LF_Power: band power 0.01–0.08 Hz (integrated PSD)
- EDA_MF_Power: band power 0.08–0.25 Hz
- EDA_HF_Power: band power 0.25–1.0 Hz
- EDA_LFMF_Ratio: EDA_LF_Power / (EDA_MF_Power + 1e-12)
- EDA_LF_Percent: EDA_LF_Power / (EDA_LF_Power + EDA_MF_Power + EDA_HF_Power + 1e-12)
- EDA_HF_Percent: EDA_HF_Power / (EDA_LF_Power + EDA_MF_Power + EDA_HF_Power + 1e-12)

**Derived EDA features (4):**
- EDA_Sympathetic_Index: EDA_SCR_Rate * EDA_SCL_Mean
  (combines tonic and phasic into a compound sympathetic activity index)
- EDA_SCR_Active_Proportion: fraction of window samples in the phasic
  signal that are within a rise or recovery segment of an SCR event.
  (SCR is active from onset to offset = half-recovery endpoint.)
  NaN if no peaks.
- EDA_SCL_Recovery_Rate: EDA_SCL_Slope computed only on the second half
  of the window (seconds 31-60). A proxy for tonic recovery trajectory.
- EDA_Phasic_Mean: mean of phasic component signal.

**Supplementary EDA subtotal: 10 + 14 + 6 + 4 = 34 features.**

### 2D. Total feature count

| Group | Count |
|---|---|
| Cardiac (§2A) | 86 |
| EDA from nk.eda_features (§2B) | 6 |
| SCL tonic features (§2C) | 10 |
| SCR phasic features (§2C) | 14 |
| EDA band-power (§2C) | 6 |
| Derived EDA (§2C) | 4 |
| **Total N_features** | **126** |

**N_features = 126 (pre-committed).**
Exact column count is confirmed and written to
`30-implement/affective-state/runs/feature_schema_v2.yaml` at first
successful extraction on real data and committed before the headline
correlation runs. If the exact count differs from 126 due to library
version edge cases, the YAML count governs and the discrepancy is
documented. The binomial test uses the YAML count, not this estimate.

**Power at N=126 (exact binomial, scipy.stats.binom.cdf):**
P(X<=2 | n=126, p=0.05) = **0.04594** — adequate, margin small but real.

Reference values for nearby N (computed 2026-05-03 with
scipy.stats.binom.cdf(2, n, 0.05)):
- N=120: P=0.05751 (under-powered)
- N=124: P=0.04953 (minimum N at which P<0.05 exactly)
- N=125: P=0.04770
- N=126: P=0.04594 (this protocol's pre-committed N)
- N=128: P=0.04260
- N=132: P=0.03658

If the final YAML count is **< 124**: the binomial test is under-powered
at the exact-binomial threshold; the CI-led headline (§5) becomes the
sole primary presentation and the binomial test is demoted to
informational. The CI-led headline is in any case the primary
presentation; the binomial test is confirmatory.

**EDA decomposition for headline:** highpass only. No cvxEDA.
All features in §2B and §2C are computable from highpass decomposition.

**No features are added or removed from this list after feature_schema_v2
is committed.** Any change requires a new unlock note.

**Audit dominance note:** The feature set is cardiac-dominant (86/126 = 68%
cardiac). This is an honest characterization of what NeuroKit2 0.2.13
exposes from its HRV pipeline. The EDA contribution (40/126 = 32%) is
sufficient to maintain the "cardiac + EDA" framing and to allow partial
comparison with arXiv:2508.10561's EDA-only finding. The audit headline
is stated as "HRV-dominant cardiac + EDA feature-stability audit" to
reflect the actual balance.

---

## 3. Arousal operationalization (FROZEN)

Unchanged from 2026-05-02. Reproduced here for completeness.

**WESAD:**
- Binary mapping: stress=1, baseline=0. Amusement excluded from headline.
- Unit: 60-second non-overlapping windows within condition epochs.
- Aggregate: per-subject Fisher-z Spearman rho, then dataset-level mean.
- Construct-validity caveat: condition label, not SAM arousal rating.
  SAM check in Ablation A-4.

**DEAP:**
- Arousal proxy: self-report 1-9 arousal scale, per 1-minute clip.
- Binarize at per-subject median. Tie rule: ties excluded (label=NaN).
- Aggregate: per-subject Fisher-z Spearman rho across 40 clips.

**MAHNOB-HCI:**
- Arousal proxy: feltArsl, 1-9 scale, per stimulus clip.
- Binarize at per-subject median. Same tie rule as DEAP.
- Aggregate: same as DEAP.

**No sign-flipping needed across datasets.** High arousal = 1 in all three.

---

## 4. Feature extraction procedure (FROZEN)

1. For each dataset, for each subject, segment signals into 60-second
   non-overlapping windows within each valid epoch.
2. ECG: bandpass 0.5-40 Hz (4th-order Butterworth, zero-phase,
   scipy.signal.sosfiltfilt), R-peak detection via
   nk.ecg_findpeaks(method="pantompkins1985"), extract cardiac features.
3. EDA: resample to 4 Hz (scipy.signal.resample_poly), clean with
   nk.eda_clean(sampling_rate=4), decompose with
   nk.eda_phasic(method="highpass"), extract nk.eda_features + all
   supplementary features from §2C.
4. Windows with >20% interpolated RR-intervals: flagged low-quality;
   features computed but excluded from correlation analysis.
5. Windows where any EDA feature is NaN due to phasic component being
   all-zero (e.g., no EDA signal in the channel): EDA features set to NaN
   for that window; cardiac features computed normally.
6. Assemble one feature matrix per dataset: rows = (subject, window_index)
   pairs; columns = all features from feature_schema_v2.yaml.
7. Write feature matrices to
   `30-implement/affective-state/runs/features_{dataset}.parquet`
   before running any correlation. These files are not re-run after
   the correlation analysis starts.

---

## 5. Primary metric (FROZEN — power note revised 2026-05-03)

**Primary metric:** N_reproducible — the count of features with
FDR-corrected p < 0.05 Spearman correlation with arousal in ALL three
datasets AND consistent sign across all three.

**Headline presentation (CI-led):**
"N_reproducible = k out of N_features (reproducibility rate = k/N_features;
95% Clopper-Pearson CI: [a, b]; binomial test p = X.XXX)."

The 95% Clopper-Pearson CI on the rate is the primary presentation.
The binomial test p-value is a secondary confirmation.

**Power at N_features = 126 (exact binomial):**
P(X<=2 | n=126, p=0.05) = **0.04594** — adequate (under 0.05, margin small).
The test confirms near-zero reproducibility if k<=2 is observed.
Minimum N at which P(X<=2 | p=0.05) < 0.05 exactly is N=124 (P=0.04953).
If feature_schema_v2.yaml confirms N_features >= 128, margin improves to
P(X<=2) = 0.04260.

**EDA-feature-count caveat:** The EDA portion of the feature set
(40 features, 32% of total) is computed from highpass decomposition.
cvxEDA is unavailable on the project environment. Results for EDA features
are reported with an explicit note: "EDA features computed from highpass
decomposition (cvxEDA unavailable); comparison with arXiv:2508.10561
EDA finding is approximate."

**Secondary metrics (reported, not primary):**
- N features significant in exactly 2 of 3 datasets (consistent sign).
- N features significant in exactly 1 dataset.
- N features significant in 0 datasets.
- Per-feature rho values and 95% bootstrap CI for each dataset.
- Comparison to arXiv:2508.10561 EDA finding (2/164).
- Secondary classifier LOSO AUC on reproducible-feature subset vs full set.

---

## 6. Statistical test (FROZEN)

**Per-dataset Spearman test (unchanged from 2026-05-02):**
- For each feature × subject: compute Spearman rho(feature, binary_arousal)
  across that subject's windows.
- Aggregate: Fisher-z transform per subject rho; mean across subjects;
  back-transform to dataset-level rho.
- p-value: one-sample t-test on Fisher-z values against 0
  (scipy.stats.ttest_1samp). For N_subjects < 15: permutation test
  (n_permutations=5000, seed=42).
- FDR correction: Benjamini-Hochberg across ALL N_features within each
  dataset independently (statsmodels.stats.multitest.fdrcorrection).
- Significance threshold: FDR-corrected p < 0.05.

**Cross-dataset reproducibility:**
A feature is "reproducible" if FDR-corrected sig=True in ALL THREE
datasets AND rho sign is consistent across all three.

**Primary binomial test:**
scipy.stats.binomtest(k=N_reproducible, n=N_features, p=0.05,
alternative="two-sided").
95% Clopper-Pearson CI: scipy.stats.binom.interval(0.95, N_features,
N_reproducible/N_features).

**Power claim (revised 2026-05-03; exact binomial via scipy.stats.binom.cdf):**
At N_features = 126: P(X<=2 | p=0.05) = **0.04594** (adequate, margin small).
At N_features = 128: P(X<=2 | p=0.05) = 0.04260.
Minimum N satisfying P(X<=2) < 0.05 exactly: **N=124** (P=0.04953).
Both N=126 and N=128 are adequate to confirm near-zero reproducibility at
alpha=0.05 if k<=2 is observed. If exact N from feature_schema_v2.yaml is
**below 124**, the binomial test is under-powered and the CI-led headline
is the sole primary presentation; the binomial test is demoted to
informational.

**No post-hoc threshold adjustment.** alpha=0.05 FDR threshold and
p0=0.05 binomial null are locked.

---

## 7. Decision rule: what counts as the headline result (FROZEN)

The headline result is valid ("the result is real") if:

1. protocol-lock.md (this re-locked version, 2026-05-03) was committed
   before feature matrices (features_{dataset}.parquet) were written.
2. feature_schema_v2.yaml was committed before the correlation table
   was computed.
3. The correlation table was computed ONCE from the frozen feature
   matrices, using the frozen arousal operationalization.
4. The binomial test was run once on the frozen correlation table.
5. No operationalization, feature, or dataset substitution was made
   after step 3 without a new unlock note.

**What counts as headline-positive:**
Binomial test rejects H0 (p < 0.05, two-sided) in the direction of MORE
reproducibility than expected (observed rate > 0.05). Some features are
more stable than the arXiv:2508.10561 EDA finding predicts.

**What counts as headline-null:**
Binomial test does not reject H0 (p >= 0.05), or rejects in the direction
of FEWER reproducible features than 5%. Both null outcomes are informative:
- Null A (rate ~ 0%): cardiac + EDA features are as unstable as the
  original EDA-only finding. Confirms universal feature instability
  across modalities.
- Null B (rate < 5%): even more extreme instability. Features are
  systematically anti-correlated with arousal, or arousal labels are weak.

**What counts as informative regardless of direction:**
- The reproducibility map (per-feature, per-dataset rho table).
- The comparison to arXiv:2508.10561.
- feature_schema_v2.yaml and the extraction code (promoted to shared/).

---

## 8. Unlock procedure

Same as original §8. For the avoidance of doubt: this re-locked
document (2026-05-03) is now the locked protocol. Any further changes
require a new dated unlock note.

---

*(Unlock note 2026-05-03 appended below this line.)*

## Unlock note — 2026-05-03

See `20-plan/affective-state/unlock-note-2026-05-03.md` for the full
rationale. Summary:
- Pilot P-1: N_features = 92 (86 cardiac + 6 EDA from nk.eda_features).
- Pilot P-2: cvxpy/cvxopt installation fails; highpass is primary EDA
  decomposition (no fallback needed or available).
- Path chosen: X — expand EDA feature set to N_total = 126 using
  explicitly enumerated SCL/SCR/band-power/derived features computable
  from highpass decomposition.
- Power restored (exact binomial): P(X<=2 | n=126, p=0.05) = 0.04594
  (adequate; min N for P<0.05 exact = 124).
- DEAP and MAHNOB-HCI access still pending. P-3 PASS covers WESAD only;
  DEAP and MAHNOB-HCI label-quality / arousal-operationalization checks
  have NOT run (gated on dataset access).
- Critic re-pass requested before headline feature extraction runs.
