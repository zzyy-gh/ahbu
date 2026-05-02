> **Spec:** `10-pain-point/affective-state/admission.md`

# Protocol lock — affective-state

**Track:** affective-state
**Locked:** 2026-05-02
**Locked by:** methodologist agent
**Status:** LOCKED — pre-registered before any headline experiment

This document defines the frozen evaluation protocol for the headline
experiment. It is locked before any feature extraction or correlation
analysis runs against the pre-registered datasets. Changes require an
explicit unlock note with a documented reason and a new critic pass
before re-locking.

This pre-registration satisfies the condition imposed by the
defensibility-critic advisory (`10-pain-point/shared/critic-defensibility.md` §6):
"Pre-reg required: feature list, dataset selection, arousal operationalization —
all locked before headline runs."

---

## 0. Pre-registration statement

This protocol is written and committed before any headline feature
extraction or correlation analysis runs. The correlation table has not
been computed. No feature-level result has been seen as of this lock
date. Pilot probes (P-1 through P-5 in pilots-README.md) use dev-
accessible data for pipeline verification only; no per-feature correlation
with arousal is computed in any pilot.

The three items required by the defensibility-critic advisory are
explicitly locked below: (1) feature list, (2) dataset selection,
(3) arousal operationalization.

---

## 1. Dataset selection (FROZEN)

The headline uses exactly these three datasets:

**Dataset A: WESAD**
- Source: PhysioNet, CC-BY 4.0. No registration required.
- Version: PhysioNet release 1.0.0 (DOI 10.13026/C2088N).
- Signals used: chest-worn ECG (700 Hz) and EDA (700 Hz). Wrist-worn
  signals not used (BVP and wrist EDA from E4 are a separate modality;
  not part of the pre-registered feature set).
- Subjects: all 15 subjects (s2 through s17, with s1 excluded per
  official WESAD documentation as a test subject).
- Sessions: one session per subject.

**Dataset B: DEAP**
- Source: request form at http://www.eecs.qmul.ac.uk/mmv/datasets/deap/
  (academic use, non-commercial).
- Version: the `data_preprocessed_matlab.zip` release (32 subjects,
  preprocessed to 128 Hz, peripheral channels included).
- Signals used: ECG (channel labeled "ECG") and EDA/GSR (channel labeled
  "GSR" in DEAP terminology). Labels: the `labels_valence_arousal_dominance_liking`
  array, using the arousal column (column index 1).
- Subjects: all 32 subjects.
- Fallback: if DEAP access is denied, substitute DREAMER (23 subjects,
  ECG + EDA; access via a similar academic form). The fallback must be
  documented as a pre-headline design adjustment BEFORE any data is
  processed; it is not a post-hoc substitution.

**Dataset C: MAHNOB-HCI**
- Source: request form at https://mahnob-db.eu/hci-tagging/ (academic use).
- Version: "HCI-Tagging" subset (27 subjects with valid physiological
  recordings; 3 of the original 30 subjects excluded per official release).
- Signals used: ECG (100 Hz or 256 Hz depending on recording configuration;
  use whichever is documented for each subject) and EDA (100 Hz or 256 Hz).
  Labels: `feltArsl` (felt arousal) column from the annotation file,
  on a 1–9 scale.
- Subjects: all 27 subjects with valid recordings.
- Fallback: if MAHNOB-HCI access is denied, substitute DREAMER (if not
  already used as Dataset B fallback). If both DEAP and MAHNOB-HCI are
  denied and DREAMER is the only substitute, proceed with WESAD + DREAMER
  (2-dataset version); document the reduced claim explicitly.

**No other datasets enter the headline.** DREAMER, AMIGOS, SEED-IV,
and others are pilot/exploratory only.

---

## 2. Feature list (FROZEN)

The pre-registered feature list is the output of the NeuroKit2 functions
below, applied to 60-second non-overlapping windows, at the pinned library
version recorded at environment setup.

The exact feature names are written to
`30-implement/affective-state/runs/feature_schema_v1.yaml` at the first
successful feature extraction run. This YAML is committed before the
headline correlation analysis runs.

**Cardiac features (from ECG):**

- `nk.hrv_time(rpeaks, sampling_rate=fs)` — all returned columns
  (expected: MeanNN, SDNN, SDANN, RMSSD, pNN20, pNN50, SDSD, HRV_triangularindex,
  TINN, HTI, LnRMSSD, MadNN, IQRnn, CVnn, CVrmssd, MedianNN, MeanHR,
  MinHR, MaxHR, SDHR, and any others returned by this function at the
  pinned version).
- `nk.hrv_frequency(rpeaks, sampling_rate=fs)` — all returned columns
  (expected: LF_power, HF_power, VLF_power, LF_peak, HF_peak, VLF_peak,
  LFHF, LFn, HFn, LF_percent, HF_percent, total_power).
- `nk.hrv_nonlinear(rpeaks, sampling_rate=fs)` — all returned columns
  (expected: SD1, SD2, SD1SD2, S, CSI, CVI, GI, SI, AI, PI, DFA_alpha1,
  DFA_alpha2, SampEn, ApEn, CD, HFD, KFD, and others at pinned version).

**EDA features (from EDA signal):**

- Decompose using `nk.eda_phasic(eda_cleaned, sampling_rate=4, method="cvxeda")`.
  If cvxEDA raises a numerical error for a specific window, fall back to
  `method="highpass"` for that window (log per-window method used).
- `nk.eda_features(...)` — all returned columns (expected: SCR_rate,
  SCL_mean, SCL_std, SCR_amplitude_mean, SCR_amplitude_std, SCR_count,
  SCR_risetime_mean, phasic_variance, tonic_slope, and others at pinned
  version).
- Supplementary EDA band-power features:
  EDA_LF_power (0.01–0.08 Hz), EDA_MF_power (0.08–0.25 Hz),
  EDA_HF_power (0.25–1.0 Hz), LFMF_ratio, LF_percent, HF_percent
  (computed via scipy.signal.welch on the cleaned EDA signal at 4 Hz).

**N_features:** the exact count is determined by NeuroKit2's output at
the pinned version and committed in `feature_schema_v1.yaml`. The
binomial test is run at the actual N_features from that YAML, not at
an assumed 164. If N_features deviates from 164 (the arXiv:2508.10561
denominator), the deviation is documented and the comparison to the
original paper is qualified accordingly.

**Power note (M-1 fix per methodology-critic):** the defensibility-critic verdict ("well-powered binomial test at N=164") was computed at N=164. Pilot P-1 likely yields N_features closer to ~100 (cardiac ~60 + EDA ~35–40 from NeuroKit2 actual outputs). At N=100, P(X ≤ 2 | p=0.05) ≈ 0.119 — NOT significant at α=0.05. The headline framing therefore depends on N_features being verified at P-1; if N_features < ~150, the binomial test is underpowered for detecting the 2/164-rate finding directionally, and the headline must lead with the **count + 95 % Clopper-Pearson CI** rather than the binomial p-value. This is acknowledged as a CI-led headline at low N.

**No features are added or removed from this list after the YAML is
committed.** Any change requires an unlock note.

---

## 3. Arousal operationalization (FROZEN)

**WESAD:**
- Arousal proxy: experimental condition label.
- Binary mapping: `stress` condition = 1 (high arousal),
  `baseline` condition = 0 (low arousal).
- `amusement` condition: EXCLUDED from the headline binary correlation
  (included in Ablation A-4 as an exploratory item).
- Unit of analysis: 60-second non-overlapping windows within each
  condition epoch. Label = the condition's binary arousal value.
- Subject-level computation: per-subject Spearman rho(feature, arousal)
  computed across all windows from that subject (pooling stress and
  baseline windows). Dataset-level rho = Fisher-z-transformed mean
  of per-subject rhos.
- **Construct-validity caveat (m-2 fix per methodology-critic):**
  WESAD arousal label is the experimental condition (stress vs baseline)
  by design intent — not the SAM arousal questionnaire response. The
  SAM arousal-response check is only run in Ablation A-4 (exploratory).
  This is a known limitation: a feature stable on WESAD may reflect
  condition-evoked physiological response (sympathetic activation
  during stress task) rather than self-reported arousal per se.
  Documented as a limitation in `findings.md` post-headline.

**DEAP:**
- Arousal proxy: participant self-report on the 1–9 arousal scale,
  provided per 1-minute video clip.
- Label construction: arousal binarized at the per-subject median
  across all 40 clips. Clips with arousal >= median = 1 (high);
  clips with arousal < median = 0 (low). Per-subject median is used
  to normalize for between-subject scale differences.
- **Tie rule (m-3 fix per methodology-critic):** clips where arousal
  exactly equals the per-subject median are EXCLUDED from the binary
  label (label = NaN). They contribute neither to the per-subject
  Spearman computation nor to the count. Tie rate per subject is
  reported in `findings.md`. Same rule applies to MAHNOB-HCI below.
- One (feature-vector, label) pair per clip per subject (no windowing
  needed; each clip is already one minute).
- Subject-level computation: Spearman rho(feature, binary_arousal)
  across 40 clips per subject. Dataset-level rho = Fisher-z-transformed
  mean of per-subject rhos.

**MAHNOB-HCI:**
- Arousal proxy: `feltArsl` (felt arousal, 1–9 scale), provided per
  stimulus clip, one rating per subject per clip.
- Label construction: binarized at per-subject median across all clips
  per subject (same rule as DEAP).
- One (feature-vector, label) pair per clip per subject.
- Subject-level computation: same as DEAP.

**Consistent direction of "arousal" across datasets:**
High arousal = 1 in all three datasets. WESAD stress = 1 is consistent
with "high sympathetic activation = high arousal" — the same construct
that DEAP and MAHNOB-HCI self-reports capture when rating high.
No dataset requires sign-flipping.

---

## 4. Feature extraction procedure (FROZEN)

1. For each dataset, for each subject, segment signals into 60-second
   non-overlapping windows within each valid epoch (WESAD: per-condition;
   DEAP and MAHNOB-HCI: per-stimulus-clip, with the clip treated as one
   window).
2. For each window: preprocess ECG (bandpass 0.5–40 Hz, R-peak detection
   via NeuroKit2 `pantompkins1985`), then extract all cardiac features.
   Preprocess EDA (resample to 4 Hz, `nk.eda_clean`, decompose, extract
   EDA features).
3. Windows with > 20% interpolated RR-intervals (per approach.md §Preprocessing)
   are flagged low-quality. Their features are computed but flagged;
   they are excluded from the correlation analysis.
4. Windows where cvxEDA raises a numerical error AND the high-pass
   fallback also fails: EDA features set to NaN for that window.
5. Assemble one feature matrix per dataset: rows = (subject, window)
   pairs; columns = all features from schema YAML.
6. Write feature matrices to
   `30-implement/affective-state/runs/features_{dataset}.parquet` before
   running any correlation. These files are NOT re-run after the
   correlation analysis starts.

---

## 5. Primary metric (FROZEN)

**Primary metric:** N_reproducible — the count of features with
statistically significant (FDR-corrected p < 0.05) Spearman correlation
with arousal in ALL three datasets, with consistent sign across all three.

Reported as: "N_reproducible = k out of N_features (reproducibility rate
= k/N_features; 95% Clopper-Pearson CI: [a, b]; binomial test p = X.XXX)."

**Secondary metrics (reported, not primary):**
- N features significant in exactly 2 of 3 datasets (consistent sign).
- N features significant in exactly 1 dataset.
- N features significant in 0 datasets.
- Per-feature rho values and 95% bootstrap CI for each dataset.
- Comparison to arXiv:2508.10561 EDA reproducibility finding (2/164).
- Secondary classifier LOSO AUC (reproducible-feature subset vs full
  feature set, subject-disjoint split within each dataset).

---

## 6. Statistical test (FROZEN)

**Per-dataset Spearman test (C-1 fix per methodology-critic — picked per-subject Fisher-z, removed subject-pooled inconsistency):**
- For each feature × subject pair, compute Spearman rho(feature, binary_arousal) across that subject's windows. This yields one rho per (feature, subject).
- Aggregate to dataset-level rho via Fisher-z transform: `r_z = arctanh(rho)` per subject; mean across subjects; back-transform: `rho_dataset = tanh(mean(r_z))`. This matches the per-subject convention specified in §3 for all three datasets and is robust to between-subject variance.
- Compute p-value: pool all per-subject rho values for the feature; one-sample t-test on Fisher-z values against 0 (`scipy.stats.ttest_1samp`). For N_subjects < 15, use permutation test (n_permutations=5000, seed=42) on Fisher-z values.
- Apply FDR correction (Benjamini-Hochberg, `statsmodels.stats.multitest.fdrcorrection`)
  across ALL features within each dataset independently.
- Significance threshold: FDR-corrected p < 0.05.
- The subject-pooled correlation is computed as a **secondary** report only (Ablation A-5 in approach.md compares the two estimators); the headline uses per-subject Fisher-z exclusively.

**Cross-dataset reproducibility test:**
- A feature is "reproducible" if: FDR-corrected sig=True in ALL THREE
  datasets AND rho sign is consistent (same sign in all three).
- Count N_reproducible.

**Primary binomial test:**
- `scipy.stats.binomtest(k=N_reproducible, n=N_features, p=0.05,
  alternative="two-sided")`.
- Two-sided test: we report both whether the reproducibility rate is
  significantly above 5% (cardiac features more stable than predicted)
  and whether it is significantly BELOW 5% (confirming near-zero
  reproducibility). Both directions are informative per the defensibility
  critic.
- 95% Clopper-Pearson CI: `scipy.stats.binom.interval(0.95, N_features,
  N_reproducible/N_features)` (or equivalent).

**No post-hoc threshold adjustment.** The alpha=0.05 FDR threshold and
the p0=0.05 binomial null are locked. If a more conservative threshold
were applied post-hoc based on seeing near-significant features, it would
invalidate the test.

---

## 7. Decision rule: what counts as the headline result (FROZEN)

The headline result is valid ("the result is real") if:

1. Protocol-lock.md was committed before feature matrices
   (`features_{dataset}.parquet`) were written.
2. The feature schema YAML was committed before the correlation table
   was computed.
3. The correlation table was computed ONCE from the frozen feature
   matrices, using the frozen arousal operationalization.
4. The binomial test was run once on the frozen correlation table.
5. No operationalization, feature, or dataset substitution was made
   after step 3 without an unlock note.

**What counts as headline-positive:**
The binomial test rejects H0 (p < 0.05, two-sided) in the direction of
MORE reproducibility than expected (observed rate > 0.05). This means
some features (specifically, cardiac features) are more stable across
datasets than the arXiv:2508.10561 EDA finding would predict.

**What counts as headline-null:**
The binomial test does not reject H0 (p >= 0.05), or rejects it in the
direction of FEWER reproducible features than 5% (confirming near-zero
stability for cardiac features as well). Both null outcomes are
informative:
- Null A (rate ~ 0): cardiac features are as unstable as EDA features.
  Confirms universal feature instability. Supports the "don't use these
  features" advisory.
- Null B (rate significantly < 0.05): even more extreme instability than
  expected by chance, indicating systematic feature–arousal dissociation.

**What counts as informative regardless of direction:**
- The reproducibility map (per-feature, per-dataset rho table) is
  informative in all directions.
- The comparison to arXiv:2508.10561 EDA finding.
- The feature schema YAML and extraction code (promoted to shared/).

---

## 8. Unlock procedure

If this protocol must be changed after locking:

1. Write an unlock note below this section with:
   - Date
   - Author
   - Specific change proposed
   - Reason the change is necessary
   - Whether the change affects the feature list, dataset selection,
     or arousal operationalization (the three pre-registration items)
2. If the change affects any of the three pre-registration items:
   a critic re-pass is required before re-locking.
3. If the correlation table has already been computed (step 3 of
   the decision rule has occurred): no protocol change is permitted
   for the primary metric. A changed operationalization would produce
   a separate exploratory analysis, not the headline.

---

*(No unlock notes below this line as of 2026-05-02.)*
