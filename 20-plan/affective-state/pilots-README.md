> **Spec:** `20-plan/affective-state/approach.md`

# Pilot probes — affective-state

**Status:** Not pre-registered. Pilots use dev-accessible data ONLY.
They do not contribute to the headline pre-registration. No pilot
computes per-feature Spearman correlation with arousal (that step is
reserved for the post-protocol-lock headline run).

Each probe has: question, dataset/split, procedure, success criterion,
estimated time, and a result field.

Run pilots in order. P-1 and P-2 can run in parallel.

---

## P-1 — NeuroKit2 feature schema smoke test

**Question:** Does `nk.hrv()`, `nk.hrv_frequency()`, and `nk.hrv_nonlinear()`
produce a non-empty, non-NaN output DataFrame for a 60-second synthetic
RR-interval series at 128 Hz? Confirm the exact column names produced by
the pinned NeuroKit2 version. This output defines the cardiac arm of the
feature schema YAML.

**Dataset/split:** No real data. Use a synthetic RR-interval series:
800 ± 50 ms intervals (normal sinus rhythm simulation), 60 seconds at
128 Hz, generated via `np.random.normal(800, 50, 75)` with seed=42.

**Procedure:**
1. Install NeuroKit2 at pinned version. Record exact version with
   `import neurokit2; print(neurokit2.__version__)`.
2. Generate synthetic R-peaks from synthetic RR intervals.
3. Call `nk.hrv_time(rpeaks, sampling_rate=128)`,
   `nk.hrv_frequency(rpeaks, sampling_rate=128)`,
   `nk.hrv_nonlinear(rpeaks, sampling_rate=128)`.
4. Assert no all-NaN columns and no empty DataFrame.
5. Print column names and count. This is the cardiac feature list.

**Success criterion:** All three function calls return DataFrames with
> 15 columns each and < 10% NaN values on this clean synthetic signal.
Record exact column count and names for `feature_schema_v1.yaml`.

**Estimated time:** 30 minutes (including environment setup).

**Result field:** [FILL AFTER RUN]

---

## P-2 — WESAD download and EDA extraction test

**Question:** Can WESAD be downloaded from PhysioNet, parsed (the native
.pkl format), and processed through the EDA extraction pipeline without
error? This confirms the data-loading code works before waiting for DEAP
and MAHNOB-HCI form approval.

**Dataset/split:** WESAD, subject s2 only (the first subject alphabetically).
Dev data; no arousal correlation is computed.

**Procedure:**
1. Download WESAD from PhysioNet (DOI 10.13026/C2088N) via
   `wget https://physionet.org/static/published-data/wesad/1.0.0/WESAD.zip`.
2. Unzip. Locate S2/S2.pkl.
3. Load with `pickle.load(open("S2.pkl", "rb"))`.
4. Extract chest ECG (700 Hz) and EDA (700 Hz) for the "stress"
   and "baseline" condition epochs.
5. Run the ECG preprocessing pipeline (bandpass, R-peak detection,
   NeuroKit2 HRV features) on one 60-second window.
6. Run the EDA preprocessing pipeline (resample to 4 Hz, clean, cvxEDA,
   EDA features) on one 60-second window.
7. Assert output DataFrames are non-empty and match expected column
   names from P-1.

**Success criterion:**
- ECG pipeline: R-peak detection returns > 50 and < 100 peaks for a
  60-second window at resting HR (normal resting = 60–100 bpm).
- EDA pipeline: cvxEDA completes without numerical error; SCL_mean is
  a positive finite float.
- BioSPPy cross-check: R-peak count from BioSPPy within 10% of
  NeuroKit2 count.

**Pre-pilot environment smoke test (m-6 fix per methodology-critic):** before downloading data, verify `pip install cvxpy` succeeds on Windows 11 + Python 3.11.2 + the pinned scipy/numpy versions. cvxpy has historically been Windows-fragile; if install fails, document and switch the EDA pipeline to `nk.eda_phasic(method="highpass")` as the primary (not fallback) method, document the swap, and proceed.

**Estimated time:** 1.5 hours (including download, ~4 GB).

**Result field:** [FILL AFTER RUN]

---

## P-3 — Arousal label distribution check (WESAD and DEAP if available)

**Question:** What is the distribution of arousal labels per subject?
Are there subjects with near-zero arousal variance (per the R-5 concern
in risk-register)? Does the median-split rule produce balanced classes?

**Dataset/split:** WESAD (all 15 subjects); DEAP (all 32 subjects, if
form approved by pilot time). Dev data only; no per-feature correlation.

**Procedure:**
1. For WESAD: count 60-second windows per condition per subject. Confirm
   stress and baseline conditions are both available for all 15 subjects.
   Report mean number of windows per condition.
2. For DEAP: load arousal ratings (40 ratings per subject, column index 1
   from the labels array). Compute per-subject mean, std, median. Report
   the distribution of per-subject std across 32 subjects.
3. Apply median split to DEAP arousal. Report mean high-arousal fraction
   (should be near 0.50 by construction of median split).
4. Check for ties at median (clips where arousal exactly equals the
   subject's median). Report fraction of ties. Ties are handled by
   excluding them from binary label (label = NaN for tie clips). Report
   tie rate.

**Success criterion:**
- WESAD: >= 10 stress windows and >= 10 baseline windows per subject
  (confirming 60-second windowing produces adequate sample size per
  condition for all subjects).
- DEAP: per-subject arousal std > 1.0 for at least 25 of 32 subjects.
  If fewer than 25 subjects show std > 1.0, flag R-5 as high probability.
- Median split: tie rate < 10% across subjects (low enough that exclusion
  does not materially reduce sample size).

**Estimated time:** 1 hour (WESAD portion; DEAP portion if available adds
30 min).

**Result field:** [FILL AFTER RUN]

---

## P-4 — cvxEDA vs high-pass fallback comparison (single dataset)

**Status (2026-05-03):** SUPERSEDED by `unlock-note-2026-05-03.md`.
cvxEDA is unavailable on the project environment (cvxpy/cvxopt install
fails per P-2 fail run). The cvxEDA-vs-highpass comparison cannot run.
Ablation A-2 in approach.md is replaced by A-2′ (highpass NaN-rate
characterization). This pilot is retired.

**Question:** For WESAD subject s2 (60-second windows), how often does
cvxEDA fail, and do the EDA features from cvxEDA and the high-pass fallback
agree in rank order across windows? This informs Ablation A-2 before it
runs at full scale.

**Dataset/split:** WESAD subject s2, all 60-second windows in stress and
baseline conditions. Dev data; no arousal correlation.

**Procedure:**
1. Run EDA decomposition with `method="cvxeda"` for all windows.
   Count failures (numerical errors).
2. Run EDA decomposition with `method="highpass"` for all windows.
3. For windows where cvxEDA succeeded: compute Spearman rho between
   the two methods' SCL_mean and SCR_rate values across windows.
4. Report: failure rate, rho(cvxEDA_SCL_mean, highpass_SCL_mean),
   rho(cvxEDA_SCR_rate, highpass_SCR_rate).

**Success criterion:**
- cvxEDA failure rate < 20% on clean WESAD windows.
- rho(cvxEDA, highpass) > 0.80 for SCL_mean (high correlation means
  the two methods agree on which windows have high tonic EDA).
- If failure rate >= 20% or rho < 0.80: flag in risk-register as R-3
  elevated and document which method to prefer.

**Estimated time:** 30 minutes (using data from P-2).

**Result field:** [FILL AFTER RUN]

---

## P-5 — DREAMER access probe (backup dataset)

**Status (2026-05-03):** PENDING — to be run alongside DEAP / MAHNOB-HCI
access form submissions (R-1). Not gating; backup if a primary dataset
fails access. No result expected before primary access decisions land.


**Question:** Can DREAMER (23 subjects, ECG + EDA + EEG, academic request
form) be accessed and loaded? This confirms the R-1 fallback path is viable
before DEAP or MAHNOB-HCI approval is needed.

**Dataset/split:** DREAMER, one subject, no analysis. Availability check only.

**Procedure:**
1. Submit DREAMER access request form (https://zenodo.org/record/546113
   or the official DREAMER repository) on day 1 alongside DEAP and
   MAHNOB-HCI forms.
2. Once access is granted: download DREAMER.mat (~500 MB).
3. Load with scipy.io.loadmat. Confirm ECG and EDA channels are present.
4. Confirm arousal ratings are present (1–5 scale in DREAMER, not 1–9
   like DEAP/MAHNOB-HCI). Note that the scale differs; if DREAMER is used
   as a substitute, the median-split rule still applies but the 1–5 range
   requires documenting.

**Success criterion:**
- DREAMER access granted within 2 weeks of submission.
- ECG and EDA channels loadable with scipy.io.
- Arousal column present and non-degenerate (std > 0.5 across clips).

**Note:** DREAMER does NOT enter the headline unless DEAP or MAHNOB-HCI
access fails (R-1 trigger). This probe confirms only that the fallback
path is viable.

**Estimated time:** 30 minutes of active work; 1–14 days of waiting for
form approval.

**Result field:** [FILL AFTER RUN]

---

## P-6 — Feature stability module unit test (shared substrate smoke test)

**Question:** Does the `cross_dataset_correlation` function from
`feature_stability.py` (the shared-substrate contribution) return correct
results on a synthetic input where the ground truth is known?

**Dataset/split:** Synthetic DataFrames only. No real data.

**Procedure:**
1. Create three synthetic feature DataFrames (simulating 3 datasets), each
   with 50 rows (simulated subjects × windows) and 10 features.
2. Set feature "F1" to perfectly correlate with arousal (rho = 1.0) in all
   three DataFrames.
3. Set feature "F2" to be uncorrelated with arousal (rho = 0.0) in all
   three DataFrames.
4. Set feature "F3" to have rho = +0.5 in 2 datasets and rho = -0.5 in
   the third (inconsistent sign; should NOT be classified as reproducible).
5. Call `cross_dataset_correlation([df1, df2, df3], target_col="arousal")`.
6. Assert: F1 has `reproducible=True`, F2 has `reproducible=False`,
   F3 has `reproducible=False` (inconsistent sign blocks it).
7. Assert: the function returns a DataFrame with N_features rows and the
   expected columns (rho_D1, rho_D2, rho_D3, consistent_sign, n_sig,
   reproducible).

**Success criterion:** All assertions pass. This is a unit test, not a
scientific result. The test is committed to
`30-implement/affective-state/code/tests/test_feature_stability.py`.

**Estimated time:** 45 minutes (including writing the test).

**Result field:** [FILL AFTER RUN]

---

## Notes on pilots

- Pilots may run in any order after their prerequisite data is available.
- P-1, P-6 have no data dependency and can run immediately.
- P-2 requires WESAD download (~4 GB, ~1 hour).
- P-3, P-4 require WESAD; P-3 also uses DEAP if available.
- P-5 runs in parallel with dataset form submissions.
- No pilot result constitutes a headline result.
- No pilot computes per-feature Spearman correlation with arousal against
  the full dataset. Pilots only verify pipeline correctness.
- If a pilot reveals a fatal design flaw, update approach.md and
  risk-register.md. Do not silently drop the pilot result.
- Pilot scripts live in `30-implement/affective-state/code/pilots/` when written.
