> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Approach — sleep-staging

**Track:** sleep-staging
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

---

## Scope decision

Two scopes were evaluated by the defensibility critic prior to admission:

**(a) Clinical-population stratified evaluation of pretrained stagers.**
Fragile-null on DUA-free data alone (Dreem-DOD-O n=55, 3–7x underpowered
for OSA stratification per the defensibility-critic power analysis).
Recoverable to defensible-null only if NSRR DUA is submitted on day one
of this layer and arrives within 4 weeks.

**(b) HRV-only EEG-less staging.**
Defensible-null at HMC PSG scale (154 subjects). Independently feasible
with no administrative dependency. Both EEG-parity (supports wearable
deployment) and EEG-superiority (defines performance ceiling) are
informative outcomes.

**Decision: pursue BOTH scopes in parallel sub-arms.** Scope (b) is
the primary arm — it is self-contained, has no external dependencies,
and fits inside the compute envelope trivially. Scope (a) is a
conditional stretch arm: the NSRR DUA is submitted on day one per the
defensibility critic's required action, and scope (a) work begins only
in week 4 after the DUA arrives; if the DUA does not arrive within
4 weeks of submission, scope (a) is dropped and scope (b) stands alone
as the track headline. This parallel structure ensures the track always
has a defensible primary result regardless of DUA timing.

**Justification for not choosing scope (a) alone:** If the DUA does not
arrive in time, a scope-(a)-only track has no defensible headline.
Scope (b) guarantees a result.

**Justification for not dropping scope (a) entirely:** The clinical-
population stratification question is the higher-impact contribution;
if the DUA arrives in time, executing scope (a) on SHHS/MESA elevates
the track's reach substantially. The marginal cost of submitting the
DUA and beginning conditional scope-(a) preparation is low.

---

## Shared substrate

### Scan result

`30-implement/shared/` does not exist. The cross-subject-eeg track
is ahead of sleep-staging and has declared four promotion candidates
(`leakage_audit.py`, `fewshot_curve.py`, `partition.py`,
`riemannian_baseline.py`) but has not yet materialized them in shared/.
This track is the first to materialize HRV-specific substrate.

The cross-subject-eeg `approach.md` also declares `partition.py`
(`subject_disjoint_split` + `validate_partition`). This track will
consume that interface once it is promoted; in the meantime the
sleep-staging track implements its own subject-disjoint split locally
with the same signature so that promotion is a drop-in.

### Consume

**From `30-implement/shared/eval/partition.py`** (to be promoted by
cross-subject-eeg or by this track, whichever runs first):
`subject_disjoint_split` and `validate_partition`. If the shared
module exists at implementation time, import it. If not, implement
locally and promote from sleep-staging.

**No other shared substrate to consume.** The cross-subject-eeg eval
utilities (leakage_audit, fewshot_curve, riemannian_baseline) are not
needed by this track. The calibration and cohort-stratifier utilities
do not yet exist in shared/ — this track builds them.

### Promote on completion

**1. `30-implement/shared/data/hrv_features.py`**

HRV feature extraction from R-R interval sequences. UNIQUE to this
track — no other current track builds this naturally. Consumed by
ecg-ppg-realworld (HRV validity sub-scope), affective-state (cardiac
feature arm), cross-subject-eeg (if an ECG-based sleep arm is added).

```python
def extract_hrv_features(
    rr_ms: np.ndarray,          # R-R intervals in milliseconds
    window_sec: float = 300.0,  # analysis window length
    step_sec: float = 30.0,     # step between windows
    fs_hr: float = 4.0,         # resampling rate for spectral analysis
    epoch_label: str | None = None,
) -> pd.DataFrame:
    """
    Returns DataFrame with one row per window. Columns:
    time-domain: mean_rr, sdnn, rmssd, pnn50
    spectral: lf_power, hf_power, lf_hf_ratio, vlf_power, tp_power
    nonlinear: sd1, sd2 (Poincare)
    Index: window_start_sec.
    Requires: neurokit2 >= 0.2.0 or scipy + numpy fallback.
    """

def align_hrv_to_epochs(
    hrv_df: pd.DataFrame,       # output of extract_hrv_features
    epoch_starts_sec: np.ndarray,
    epoch_dur_sec: float = 30.0,
) -> pd.DataFrame:
    """
    Returns one row per sleep epoch (30 s) with HRV features interpolated
    or aggregated from the enclosing or nearest HRV window.
    Allows direct concatenation with stage labels for classifier input.
    """
```

Plausible 2nd consumers: ecg-ppg-realworld (HRV-validity probe on
PTB-XL / WESAD), affective-state (cardiac feature extraction for
DEAP/WESAD arousal study), cross-subject-eeg (any ECG-based sub-scope).

**2. `30-implement/shared/eval/calibration.py`**

Calibration metrics and reliability diagrams. The reuse sketch
identified this as overlapping with ecg-ppg-realworld's planned
contribution. Whichever track runs first promotes it.

```python
def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
    strategy: str = "uniform",   # "uniform" or "quantile"
) -> float:
    """
    Scalar ECE (Expected Calibration Error) for a single class.
    y_prob: predicted probability for the positive class.
    """

def multiclass_ece(
    y_true: np.ndarray,         # integer class labels
    y_prob: np.ndarray,         # shape (n_samples, n_classes)
    n_bins: int = 10,
) -> dict:
    """
    Returns {"macro_ece": float, "per_class_ece": dict[str, float]}.
    Macro ECE = mean of per-class ECE using one-vs-rest decomposition.
    """

def reliability_diagram(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
    class_name: str = "",
    save_path: str | None = None,
) -> None:
    """
    Plots fraction-of-positives vs mean-predicted-probability with
    perfect-calibration diagonal. Saves if save_path is provided.
    """
```

Plausible 2nd consumers: ecg-ppg-realworld (calibration of AFib
abstention threshold), cross-subject-eeg (any future probability-output
variant), affective-state (arousal prediction confidence).

**3. `30-implement/shared/eval/cohort_stratifier.py`**

Per-stratum evaluation. The reuse sketch called this `cohort_stratifier.py`.
Any track with subgroup evaluation needs this utility.

```python
def stratified_report(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray | None,  # shape (n_samples, n_classes), optional
    stratum_col: np.ndarray,    # stratum label per sample
    stratum_vals: list | None = None,  # if None, use unique values
    stage_names: list[str] | None = None,
    n_bootstrap: int = 2000,
    random_state: int = 42,
) -> dict:
    """
    Returns per-stratum dict with keys:
    {"stratum_value": {
        "n_epochs": int,
        "per_stage_f1": dict[str, float],
        "macro_f1": float,
        "macro_f1_ci": (float, float),
        "confusion": np.ndarray,
        "ece": float | None,          # None if y_prob not provided
    }}
    Strata are AHI band, age decile, cohort site, or any categorical.
    Bootstrap CI computed over subjects (not epochs).
    """
```

Plausible 2nd consumers: ecg-ppg-realworld (site-stratified PTB-XL
eval), cross-subject-eeg (paradigm- or hardware-stratified eval),
affective-state (cross-dataset feature stability).

**4. `30-implement/shared/eval/partition.py`** (co-promotion with
cross-subject-eeg — if cross-subject-eeg promotes first, consume;
if sleep-staging reaches implementation first, promote from here).

Same interface as declared in cross-subject-eeg approach.md.

### Track-specific (not promoted)

- Sleep-EDF loader (epoch-based PSG format; useful only for PSG tracks).
- HMC PSG loader (same reason).
- Dreem-DOD loader (same reason).
- Stage-label mapping utilities (AASM 5-class, 3-class, Wake/NREM/REM).
- R-peak detection wrapper around NeuroKit2 `ecg_peaks` (single-use).

---

## Dataset

### Primary: HMC PSG (scope b — primary arm)

- **Full name:** St. Vincent's University Hospital / University College
  Dublin Sleep Apnea Database — also distributed as the PhysioNet 2018
  CinC Challenge dataset ("An open-access database for the evaluation
  of cardiorespiratory signals in sleep apnea").
- **Access:** PhysioNet. https://physionet.org/content/hmc-sleep-staging/1.0.0/
  License: PhysioNet Credentialed Health Data License 1.5.0 (free
  registration; no multi-week DUA process; account creation is same-
  session). The training set is fully labeled (PSG + staging + apnea
  annotations). Confirm at implementation start that credentialed
  access is current and the 154-subject set is available.
  Note: PhysioNet 2018 CinC challenge data is sometimes described as
  "no DUA" in secondary sources; the exact access tier must be confirmed
  at implementation start. If a multi-week DUA is required, substitute
  the CAP Sleep database (PhysioNet, ~108 subjects, various pathologies,
  similar open access tier) for scope (b) piloting, and proceed with
  Dreem-DOD-H (25 healthy, 25 GB, MIT license, Zenodo direct download)
  for scope (a) dev work. Either substitution is pre-authorized here.
- **Size:** 154 subjects (HMC Sleep Staging Database, Hassan 2023).
- **Modalities:** EEG (C3-A2, C4-A1), EOG (left/right), chin EMG,
  ECG single-lead (or ABD/CHEST respiratory effort; ECG required for
  HRV). Confirm ECG availability per subject at preprocessing time.
- **Stage labels:** 5-class AASM (W, N1, N2, N3, REM). 30-second
  epochs.
- **Pathology:** mixed — includes healthy subjects and subjects with
  suspected sleep-disordered breathing (the challenge concerned apnea
  detection). AHI values documented in challenge metadata where
  available.
- **Intended split:**
  - Subject-disjoint: 75 subjects dev / 76 subjects test (50/50).
    Stratified by AHI category at split time to ensure both halves
    have similar pathology distribution.
  - The 50/50 split (rather than 80/20) gives N=77 test subjects.
    Honest power note (m-3 fix per methodology-critic): a two-sample
    proportion power calc requires N≈105 per stratum to detect a
    17 pp accuracy gap at 80 % power, so N=77 is **modestly
    underpowered** for the headline gap test under that assumption.
    A paired Wilcoxon may have higher effective power (within-subject
    variance < between-subject), but the exact paired-design power is
    not pre-computed here. The headline framing therefore leads with
    **CI width on the EEG-vs-HRV macro-F1 difference** as the primary
    informative quantity; the Wilcoxon p-value is reported but
    secondary. A null at this N is interpretable as "the EEG-vs-HRV
    gap is not larger than ~17 pp at 95 % CI width" — itself a
    useful constraint on field claims.
  - The 77-subject test split is the held-out partition. Touched once,
    for the headline run only.
- **Version:** HMC Sleep Staging Database (Hassan 2023) data as retrieved at
  implementation start. Record exact retrieval date and file hashes
  in `30-implement/sleep-staging/code/requirements.txt`.

### Secondary dev dataset: Sleep-EDF Cassette v1

- **Access:** PhysioNet ODC-BY license. No registration required.
  https://physionet.org/content/sleep-edfx/1.0.0/
- **Size:** 78 recording pairs (39 subjects × 2 nights for 20 subjects;
  single-night for the rest), healthy adults 21–35 yr.
- **Modalities:** EEG Fpz-Cz, EEG Pz-Oz, EOG horizontal, oro-nasal
  thermistor, EMG submental. No ECG channel — HRV cannot be extracted.
- **Role:** Dev-only pipeline test for EEG preprocessing and stager
  inference. NOT used for any headline result. Its demographic
  homogeneity (young healthy adults) makes it inappropriate for
  clinical-population claims.
- **Split:** Use all 78 recordings for dev (no held-out split needed;
  it is dev-only by design).

### Out-of-distribution probe: Dreem-DOD-H and Dreem-DOD-O

- **Access:** Zenodo https://zenodo.org/records/15900394 (MIT license,
  open, no registration, confirmed in gap-closing pass 2026-05-02).
  DOD-H: 25 healthy adults (dodh.zip, 21.9 GB).
  DOD-O: 55 OSA patients (dodo.zip, 36.2 GB).
- **Modalities:** EEG (multiple channels), EOG, EMG, accelerometer.
  No ECG — HRV cannot be extracted from Dreem-DOD. This dataset is
  therefore scope (a) only (stager eval), not scope (b) (HRV-only).
- **Stage labels:** 5-class AASM scored by 5 expert raters (Dreem
  proprietary + 4 independent sleep centers). Majority-vote consensus
  label available. This multi-rater setup is a strength — confusion
  in Dreem-DOD labels reflects genuine human disagreement, not a
  single-rater artifact.
- **Role:** Out-of-distribution test for scope (a): evaluate a
  pretrained stager (U-Sleep or DeepSleepNet checkpoint) on Dreem-DOD-O
  (55 OSA subjects) and Dreem-DOD-H (25 healthy) to document
  performance by AHI band. This is pilot-scale work until NSRR DUA
  arrives; the power is insufficient (n=55) for a defensible OSA-
  stratification headline but is enough for honest CI-documented
  estimates that frame what NSRR will test.
- **Split (scope a):** Dreem-DOD is entirely a test/evaluation dataset
  for the pretrained stager — no training occurs on it. All 55 OSA
  subjects are used for scope (a) OOD evaluation. Subject-disjoint
  from HMC PSG trivially (different sites, different acquisition
  systems).

### Conditional stretch dataset: SHHS + MESA via NSRR DUA (scope a, week 4+)

- **Access:** NSRR (sleepdata.org). Free credentialed access with
  institution email + DUA submission. Documented typical processing
  time: 1–4 weeks.
  - SHHS (Sleep Heart Health Study): ~5,800 subjects, older adults,
    AHI available, ECG available (R-R interval derivable), multi-ethnic.
    Scored with R&K and AASM; mixed-scoring era is a caveat.
  - MESA (Multi-Ethnic Study of Atherosclerosis Sleep Study): ~2,000
    subjects, multi-ethnic, EEG + ECG + actigraphy, AASM v2 scoring.
    Both EEG and ECG available — enables both scope (a) and scope (b)
    replication on a larger, more diverse cohort.
- **DUA action:** SUBMIT ON DAY ONE of this layer (see risk register
  R-1). Confirmation of submission logged in
  `30-implement/sleep-staging/runs/nsrr_dua_submission.txt`.
- **Role:** Scope (a) primary dataset if DUA arrives in time; scope (b)
  replication cohort for HRV-only staging at larger N. SHHS and MESA
  together provide the N > 384 required for a properly powered OSA-
  stratification headline.
- **Intended split (if used):** 80 % train + dev / 20 % test,
  subject-disjoint, stratified by AHI band (none/mild/moderate/severe)
  and ethnicity (MESA). Exact split frozen in protocol-lock when DUA
  data arrives; a revised protocol-lock addendum is required before
  the NSRR headline run.

---

## Preprocessing

### Scope (b) — HRV feature pipeline (primary arm)

This pipeline operates on the ECG channel of HMC PSG.

**Stage 1: ECG loading and quality check**

Software: MNE-Python 1.6.x, NeuroKit2 >= 0.2.0.

1. Load the ECG channel from each subject's EDF file using
   `mne.io.read_raw_edf(preload=True)`.
2. Check sampling rate: HMC PSG ECG is nominally sampled at >= 256 Hz.
   If < 200 Hz, flag the recording and report the fraction flagged.
3. Compute signal-quality index (SQI): using NeuroKit2
   `nk.ecg_quality()`, flag 30-second windows with SQI < 0.5.
   Report the fraction of flagged windows per subject.
4. Subjects with > 30 % of windows flagged are excluded from scope (b)
   analysis (quality-exclusion criterion; logged, not hidden).

**Stage 2: R-peak detection**

1. `nk.ecg_peaks(ecg_cleaned, sampling_rate=fs)` using the "pantompkins"
   method as default. Record detector type.
2. Compute R-R interval sequence in milliseconds.
3. Apply ectopic-beat correction: `nk.hrv_sanitize()` or equivalent
   outlier removal (R-R intervals outside [300, 2000] ms flagged as
   ectopic, replaced by linear interpolation). Report ectopic fraction.

**Stage 3: HRV feature extraction**

Call `hrv_features.extract_hrv_features(rr_ms, window_sec=300,
step_sec=30)` per subject. The 300-second (5-minute) window is the
standard for spectral HRV analysis (Task Force 1996; gives frequency
resolution sufficient for LF/HF decomposition). Step size = 30 seconds
= epoch length.

Features per 30-second epoch:
- Time-domain: mean_rr, sdnn, rmssd, pnn50
- Spectral (after cubic spline resampling at 4 Hz):
  lf_power (0.04–0.15 Hz), hf_power (0.15–0.40 Hz), lf_hf_ratio,
  vlf_power (0.003–0.04 Hz), total_power
- Nonlinear: sd1, sd2 (Poincare plot axes)
Total: 11 features per epoch.

Rationale for 11 features: sufficient to capture the autonomic HRV
dynamics known to differentiate wake/NREM/REM (HF power increases
in NREM; LF/HF increases in REM; mean HR decreases in NREM, rises
in REM). Keeping the feature set small avoids overfitting on 75 dev
subjects.

**Stage 4: Epoch alignment**

Call `hrv_features.align_hrv_to_epochs(hrv_df, epoch_starts_sec)`
using the stage annotation file's epoch boundary timestamps. Produces
one feature vector per 30-second sleep epoch, aligned with stage label.

**Stage 5: Class balance check**

Per subject: report epoch counts per stage (W, N1, N2, N3, REM).
Expected class distribution in mixed-pathology dataset: N2 ~50 %,
N1 ~5 %, N3 ~15 %, REM ~20 %, W ~10 %. If any subject has 0 epochs
for a given stage, note it; do not impute. Report class balance per
split.

### Scope (a) — pretrained stager inference pipeline (conditional)

This pipeline requires EEG. Used on Sleep-EDF (dev), Dreem-DOD (OOD
probe), and NSRR data (headline, if DUA arrives).

**Stage 1: EEG loading**

1. Load EEG channels (C3-A2 or equivalent) via MNE-Python.
2. For Sleep-EDF: Fpz-Cz as single EEG channel (matches U-Sleep
   single-channel mode).
3. For Dreem-DOD: use the channel mapping provided in the Dreem
   benchmark repo (github.com/Dreem-Organization/dreem-learning-open).
4. Sampling rate: resample to 100 Hz (U-Sleep's required input rate)
   using MNE anti-aliasing filter.

**Stage 2: Epoch extraction**

30-second epochs as required by AASM staging protocol. Label source:
annotation files (Sleep-EDF: EDF+ annotation channel; Dreem-DOD:
JSON annotation files per subject).

**Stage 3: Normalization**

Normalize each epoch: subtract channel mean, divide by channel SD.
U-Sleep expects normalized input.

**Stage 4: Pretrained stager inference**

Primary: U-Sleep checkpoint (Perslev et al. 2021). The U-Sleep
inference API accepts a numpy array of normalized EEG epochs and
returns per-epoch probability distributions over 5 stages.
See https://github.com/perslev/U-Sleep for API.

Compute: frozen inference on GTX 1650 is feasible for ~150 subjects
× ~1,000 epochs = ~150,000 epochs. At batch=32, each forward pass
is approximately 0.1 s. Total: ~500 s / ~8 minutes per subject
dataset. Full Dreem-DOD: ~10 hours on GPU. Feasible; see compute
budget below.

**Stage 5: Calibration head (scope a only)**

Temperature scaling on a held-out dev subset (Dreem-DOD-H, 25 subjects
— these subjects are NOT in the test set for scope (a)).
Fit a single temperature parameter T on the dev subset logits using
NLL minimization. Then report ECE before and after temperature scaling
to quantify calibration improvement. This uses
`calibration.multiclass_ece()` and `calibration.reliability_diagram()`.

**Distribution-shift caveat (m-6 fix per methodology-critic):** Dreem-DOD-H
is 25 healthy subjects with the Dreem headband acquisition system; NSRR
SHHS / MESA are clinical-population PSGs with different acquisition
hardware, demographics, and pathology mix. Temperature scaling fit on
Dreem-DOD-H may be ineffective on NSRR test data (calibration is itself
non-transportable across distributions). Acknowledged limitation; if the
NSRR DUA arrives, RE-FIT the calibration head on a small NSRR dev subset
before applying to NSRR test (carve out ~10 % of NSRR for this).

---

## Model family

### Scope (b) — HRV-only classifier (primary arm)

**Model A (primary): Random Forest on 11 HRV features**

- Library: scikit-learn RandomForestClassifier.
- Hyperparameters: n_estimators=200, max_depth=None (let trees grow),
  class_weight="balanced" (to handle N1 class imbalance).
- Rationale: Random Forest is the canonical HRV-based sleep staging
  classifier (Fonseca et al. 2017; Radha et al. 2019 on 4-class HRV
  staging). It is interpretable via feature importance (which HRV
  features matter per stage), robust to the small-N regime (75 dev
  subjects), and does not require GPU. Feature importance is a
  secondary output of scientific interest.
- Training: fit once on the 75 dev subjects' epoch-level feature
  vectors and stage labels. No per-subject retraining — this is a
  population-level model.
- Test: evaluate on the 76 held-out test subjects, subject-disjoint.

**Model B (primary comparison — EEG baseline for gap quantification):**

EEG-based stager on HMC PSG — required to quantify the EEG-vs-HRV
performance gap (the primary scientific question).

Option: U-Sleep frozen inference on the HMC PSG EEG channels.
The U-Sleep model was trained on 15,660 PSGs from 16 studies. HMC PSG
is not in U-Sleep's declared training corpus (per the published
supplementary). Confirm this via a dataset-overlap check before the
headline run (using the `partition.py` / manual audit; leakage_audit.py
from cross-subject-eeg can be adapted here).

U-Sleep inference is run on the same 77 test subjects, same epochs.
This gives a paired comparison: for each test subject, both HRV-only-RF
accuracy and U-Sleep-EEG accuracy are available. The gap is the primary
metric.

**Model C (baseline lower bound): Majority-class classifier**

Predict N2 for all epochs (majority class, ~50 % of epochs).
This is the naive baseline. Any model that does not beat majority-class
on macro-F1 is not doing useful work.

**Model D (exploratory, dev-split only): LSTM on HRV sequence**

A small LSTM (1 layer, 64 hidden units, input = 11 HRV features per
epoch, sequence = 30 consecutive epochs) trained on dev subjects.
This tests whether temporal context (sleep cycles) improves HRV-only
staging beyond the epoch-wise Random Forest. On 75 dev subjects at
~1,000 epochs each = 75,000 training examples: a 1-layer LSTM with
64 units has ~37,000 parameters, training in minutes on CPU. This is
a pilot probe (P-5), not a pre-registered model.

### Scope (a) — pretrained stager evaluation (conditional)

No new model is trained. Scope (a) contributes:
1. U-Sleep inference on Dreem-DOD and (if DUA arrives) SHHS/MESA.
2. Calibration head (temperature scaling) fit on dev.
3. Per-AHI-band, per-stage F1 evaluation using `cohort_stratifier.py`.

### Summary table

| Model | Arm | GPU? | VRAM | Role |
|---|---|---|---|---|
| Random Forest (11 HRV features) | (b) | no | 0 | primary scope (b) |
| U-Sleep frozen inference (EEG) | (b) comparison / (a) | yes | ~1–2 GB | EEG gap baseline + scope (a) eval |
| Majority-class classifier | (b) | no | 0 | lower bound |
| LSTM on HRV sequence | (b) exploratory | CPU/GPU | < 0.5 GB | dev-only pilot |

---

## Evaluation protocol

### Structure

Subject-disjoint throughout. Each subject appears in exactly one split
(dev or test). Within each split, evaluation is at the epoch level
(30-second windows), but statistical tests are performed at the subject
level (averaging over epochs per subject first, then comparing subjects).

**3-class vs 5-class decision:**
Primary scope (b) evaluation uses 3-class labels (Wake / NREM / REM)
for power reasons (N=77 test subjects provides adequate power for a
17 pp 3-class accuracy gap; 5-class is reported secondarily with honest
CI widths). The 5-class result is informative but the headline claim is
anchored to 3-class macro-F1.

Rationale: NREM consolidation (N1+N2+N3 → NREM) reflects how HRV
signals actually vary — the HRV signature of N1 vs N2 is subtle;
the HRV signature of NREM vs REM is strong. 5-class precision captures
the N1/N2/N3 detail but is not the primary axis of the HRV question.

**Cross-subject evaluation (not cross-session):**
One model trained on dev subjects, evaluated on test subjects. This is
cross-subject generalization, which is the relevant question for
deployment (a wearable algorithm must work without per-user training).

### Metrics

**Primary metric (scope b):**
3-class macro-F1 (Wake / NREM / REM) on 76 held-out test subjects.
Reported as: "macro-F1 = X.XX (95 % CI: Y.YY–Z.ZZ, N=77 subjects)".

**Primary comparison metric (scope b):**
EEG-vs-HRV gap = U-Sleep macro-F1 minus HRV-RF macro-F1 on the same
77 test subjects. This is a paired comparison.

**Secondary metrics:**
- 5-class per-stage F1 (W, N1, N2, N3, REM) with 95 % CI — reported,
  not used for headline claim.
- 5-class confusion matrix — reported per model.
- AHI-stratified 3-class macro-F1 (none / mild / moderate / severe)
  — reported via `cohort_stratifier.stratified_report()`. For scope (b)
  this characterizes whether HRV-only staging degrades more for OSA
  patients (expected: yes, because OSA disrupts HRV dynamics).
- Per-stage feature importance (RF) — top HRV features per stage class.
- ECE per stage for U-Sleep (scope a) — using `calibration.multiclass_ece()`.

### Cross-subject vs within-subject

This study uses **cross-subject** evaluation exclusively. The population-
level model (RF trained on 75 dev subjects) is evaluated on 76 unseen
test subjects. Within-subject performance is not reported as a headline
because it is not the deployment-relevant scenario. Within-subject RF
(fit per subject using 80 % of that subject's epochs) is a dev-only
probe (P-4) to establish the within-subject ceiling.

### Statistical testing

**Paired test for EEG-vs-HRV gap:**
Paired Wilcoxon signed-rank test (one-sided: H1 = EEG accuracy > HRV
accuracy), across 77 test subjects. Each subject yields one accuracy
score per model; pairing controls for subject-level difficulty variation.
Significance threshold: p < 0.05 (single test, no multiplicity
correction needed for the primary comparison).
Effect size: Cohen's d (paired).

**Interpretation rule:**
- p < 0.05 AND d >= 0.5: "EEG significantly and substantially
  outperforms HRV-only; EEG is necessary for clinical-grade staging."
- p < 0.05 AND d < 0.5: "EEG statistically outperforms HRV-only but
  the gap is modest; HRV-only may be adequate for some use cases."
- p >= 0.05: "No statistically significant difference between EEG
  and HRV-only; HRV-only is not detectably worse than EEG at this
  sample size."

All three outcomes are pre-specified and informative per the
defensibility-critic analysis.

---

## Ablations

All ablations run on the dev split only.

**Ablation 1: Feature subset ablation (time-domain only vs spectral only vs all)**

Hypothesis: spectral features (LF/HF) carry the majority of
discriminative information for REM vs NREM. If accuracy with spectral-
only features is within 3 pp of full feature accuracy, and accuracy
with time-domain-only features drops > 10 pp, the spectral features
are the load-bearing HRV signal. This ablation directly addresses
"which HRV features matter" — a clinically meaningful sub-question
about wearable signal requirements.

Procedure: train RF with (a) all 11 features, (b) 4 time-domain only,
(c) 5 spectral only, (d) 2 nonlinear only. Evaluate on dev split LOSO.

**Ablation 2: Window length sensitivity (60 s vs 150 s vs 300 s)**

Hypothesis: HRV spectral features require a minimum window of ~5 minutes
for reliable LF/HF estimation. Shorter windows (60–150 s) will
degrade spectral feature quality and reduce staging accuracy.
This tests whether the standard 5-minute spectral HRV window is
load-bearing or whether a 60-second window (lower latency, more
practical for wearables) is adequate.

Procedure: compute HRV features at window lengths 60, 150, 300 s;
train separate RFs; compare macro-F1 on dev split.

**Ablation 3: Ectopic correction on/off**

Hypothesis: ectopic R-R intervals inflated RMSSD and pNN50 values
degrade classifier performance, particularly in OSA subjects where
ectopic beats are more common. Ectopic correction is load-bearing for
OSA subjects.

Procedure: train one RF with ectopic correction and one without.
Compare accuracy stratified by AHI band on the dev split.

**Ablation 4: 3-class vs 5-class target (scope b)**

Hypothesis: HRV-only staging achieves reasonable performance on 3-class
(Wake/NREM/REM) but fails on N1 specifically. This would replicate the
N1 difficulty seen in EEG-based models (N1 F1 ~0.35–0.40 in literature)
and establish that N1 is hard regardless of modality.

Procedure: train RF on 5-class labels; compare 5-class per-stage F1
to 3-class macro-F1 and to the human-rater kappa ceiling (N1 κ=0.24).

---

## Uncertainty reporting

- **Bootstrap CI:** All macro-F1 means reported with 95 % bootstrap CI
  (n=2000 resamples, sampling with replacement at the subject level,
  fixed random_state=42). Subject-level resampling is correct because
  epochs within a subject are not exchangeable.
- **Multi-seed:** Random Forest uses random_state=42 for reproducibility.
  Report RF performance with 5 additional random seeds (43–47) on the
  dev set to confirm training-run variance is negligible (< 0.5 pp
  across seeds). Do not report multi-seed on the test split.
- **Reporting format:** "X.XX (95 % CI: Y.YY–Z.ZZ, N=77 test subjects)"
  for all headline numbers. Never report a point estimate without CI.
- **CI width as evidence:** If the CI width is > 15 pp, the result is
  inconclusive at this sample size and must be stated as such, not
  framed as a finding.

---

## Compute budget

| Task | Hardware | Estimated time |
|---|---|---|
| HMC PSG download (~10 GB) | local | 1–2 hr |
| Sleep-EDF download (~1 GB) | local | 15 min |
| Dreem-DOD download (58 GB) | local | 4–8 hr (bandwidth-limited) |
| ECG preprocessing + R-peak detection (HMC PSG, 154 subj) | CPU | 2–3 hr |
| HRV feature extraction (154 subj × ~1000 epochs) | CPU | 1–2 hr |
| RF training on 75 dev subjects | CPU | < 5 min |
| RF ablations (4 configurations × dev LOSO) | CPU | 30 min |
| U-Sleep inference on HMC PSG (154 subj, batch=32) | GTX 1650 | 6–10 hr |
| U-Sleep inference on Dreem-DOD (80 subj) | GTX 1650 | 4–6 hr |
| Bootstrap CI computation (n=2000) | CPU | < 30 min |
| Calibration head fitting + ECE (scope a dev) | CPU | < 10 min |
| **Total headline run (scope b test split)** | CPU | **~1 hr** |
| **Total scope (a) OOD probe (Dreem-DOD)** | GTX 1650 | **~5 hr** |

Total GPU budget: approximately 10–15 GPU-hours (GTX 1650). Fits the
4 GB VRAM envelope — U-Sleep inference at batch=32 on 30-second 1-channel
epochs uses < 1 GB VRAM. Verify at implementation start (P-1 pilot).

**Fits 4 GB envelope:** yes, with margin. The HRV-only scope (b) primary
arm uses zero GPU. Scope (a) U-Sleep inference is the only GPU load.

### Time to first honest result

- Week 1: NSRR DUA submission. HMC PSG access confirmation. ECG
  preprocessing pipeline. HRV feature extraction (dev subjects). RF
  baseline on dev LOSO. Preliminary accuracy estimate (labeled
  preliminary, not headline).
- Week 2: U-Sleep inference on Sleep-EDF (dev) and 5 Dreem-DOD-H
  subjects (pilot). Ablations 1–3 on dev split. Per-stage F1 patterns
  established. Pilot probes completed.
- Week 3: Headline RF training on 75 dev subjects. Dev-split multi-seed
  check. Protocol-lock review. Pre-run checklist preparation.
- Week 4: Headline test-split evaluation (scope b). Single authorized
  run. Bootstrap CI computation. Results written.
  If NSRR DUA arrived: begin scope (a) NSRR preprocessing.

**First honest result (scope b): week 4.**
**First honest result (scope a, conditional): week 6–8 if DUA arrives week 4.**

---

## Novelty and exploration notes

**What is genuinely novel:**
- An **explicit, pre-registered, same-harness** paired EEG-vs-HRV staging
  comparison on HMC PSG (m-7 fix per methodology-critic — narrowed claim).
  Fonseca 2017 and Radha 2019 both ran HRV-only staging on PSG datasets
  that also contain EEG, so an implicit modality comparison was available
  in those works; the novel element here is the explicit same-harness
  pre-registered paired test with CI-width-led headline framing — not
  the absence of any prior modality comparison.
- Calibration evaluation on a pretrained stager (U-Sleep) applied to
  out-of-distribution data (Dreem-DOD OSA cohort). U-Sleep calibration
  on clinical-edge populations is not reported in the published U-Sleep
  papers.
- The AHI-stratified HRV staging accuracy decomposition: does HRV-only
  staging degrade more steeply than EEG-based staging as OSA severity
  increases? The defensibility critic identifies this as the informative
  sub-question that can be answered even at n=55 (Dreem-DOD-O) with
  honest CI widths.

**What is standard and intentionally so:**
- Random Forest on HRV features: the canonical HRV sleep staging
  baseline (Fonseca 2017, Radha 2019). Using it is disciplined.
- U-Sleep as the EEG baseline: the best publicly available pretrained
  stager with open weights.
- Bootstrap CI at the subject level: correct uncertainty quantification
  for this design.
- 30-second epochs: AASM standard.

**What is exploratory (pilot probes, not pre-registered):**
- LSTM on HRV sequence (P-5): tests temporal context benefit.
- U-Sleep temperature calibration improvement magnitude (P-3).
- Within-subject RF ceiling vs cross-subject RF gap (P-4).
- Scope (a) Dreem-DOD AHI-stratified ECE curves (P-2): framing
  exercise for the NSRR headline.
