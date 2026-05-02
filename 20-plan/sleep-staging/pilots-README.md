> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Pilot probes — sleep-staging

**Status:** Not pre-registered. Pilots use dev split ONLY.
They do not touch the held-out test partition (76 HMC PSG test subjects
as defined in protocol-lock.md §3). Results here may inform final
design choices but do not constitute headline results.

Pilot numbering is track-local (P-1 through P-N); does not share the
cross-subject-eeg pilot numbering.

Run pilots in priority order. P-1 is critical-path — blocks P-2 and P-5.

---

## P-1 — HMC PSG access tier and ECG channel check (CRITICAL, week 1)

**Question:** (a) Is HMC PSG accessible at the PhysioNet credentialed
level (same-session account creation) or does it require a multi-week
DUA? (b) How many subjects have a usable ECG channel with SQI >= 0.5
on > 70 % of epochs?

**Dataset/split:** Attempt HMC PSG access for all 154 subjects.
Load ECG channels for a 10-subject sample.

**Procedure:**
1. Create PhysioNet account (if not already done). Navigate to
   https://physionet.org/content/hmc-sleep-staging/1.0.0/.
   Note the access tier displayed. Record in
   `30-implement/sleep-staging/runs/hmc_access_tier.txt`.
2. Download 10 subject files (the first 10 alphabetically by subject
   ID as a convenience sample, not a random sample).
3. Load ECG channel using MNE `read_raw_edf()`. Compute SQI via
   `nk.ecg_quality()` for each 30-second window.
4. Compute fraction of windows with SQI >= 0.5 per subject.
   Report count and fraction above threshold.

**Success criterion:**
(a) Access granted within 1 hour of account creation (credentialed-
    access tier, not multi-week DUA).
(b) >= 8 of 10 sampled subjects have > 70 % of ECG windows with SQI
    >= 0.5.

If (a) fails: invoke risk-register R-2 — begin CAP Sleep access
procedure immediately.
If (b) fails on > 5 of 10 subjects: the ECG quality exclusion
rate may be higher than expected; adjust the exclusion threshold
and re-examine (or invoke R-3 kill criterion assessment).

**Estimated time:** 2 hours (including download of 10-subject sample).

**Result field:** [FILL AFTER RUN]

---

## P-2 — Dreem-DOD label loading smoke test (week 2)

**Question:** Can the Dreem-DOD-O label files (JSON format, Zenodo
2025 re-release) be loaded correctly, and do the stage annotations
align with the expected epoch boundaries?

**Dataset/split:** Dreem-DOD-O, 3-subject sample (subjects 0, 1, 2
from the alphabetically sorted list). Dev use only.

**Procedure:**
1. Download Dreem-DOD-O (or a 3-subject subset from Zenodo).
2. Load JSON annotation file for subject 0. Check:
   - Number of epochs (expected: ~1,000 per 8-hour recording).
   - Stage label distribution (expected: W < 20 %, N2 ~40 %, REM
     ~20 %, N1 + N3 remainder).
   - Consensus label field is present (vs per-rater-only labels).
3. Align epoch start times with the EEG channel timestamps.
   Confirm the first epoch start matches the annotation.
4. Repeat for subjects 1 and 2.

**Success criterion:** All 3 subjects have loadable annotations with
a valid consensus label field and correct epoch count. Zero NaN or
out-of-bounds labels.

If consensus field absent: check benchmark repo (dreem-learning-open)
for the consensus construction code; apply it to get majority-vote
labels from per-rater fields.

**Estimated time:** 1.5 hours.

**Result field:** [FILL AFTER RUN]

---

## P-3 — U-Sleep VRAM probe and inference correctness check (week 2)

**Question:** (a) How much VRAM does U-Sleep inference consume on
GTX 1650 at batch=32, single EEG channel, 30-second epochs at 100 Hz?
(b) Do the output probability distributions look valid (not uniform,
not all-zero, sums to 1)?

**Dataset/split:** Sleep-EDF Cassette, 2-subject sample (dev use only).

**Procedure:**
1. Install U-Sleep (pip install usleep or from GitHub).
2. Load 2 subjects from Sleep-EDF Cassette. Preprocess to 100 Hz,
   normalize per-epoch.
3. Run U-Sleep inference at batch=32 on a single subject's epochs
   (~900 epochs). Log peak VRAM: `torch.cuda.max_memory_allocated() / 1e9`.
4. Inspect per-epoch probability distributions: compute mean entropy
   per epoch across 5 classes. Expected: high entropy (near log(5))
   for N1; low entropy for W and REM.
5. Compute per-subject macro-F1 on the 2-subject sample against the
   Sleep-EDF annotations (this is a sanity check, not a result).
   Expected: Sleep-EDF is in-distribution for U-Sleep (or close to
   it); macro-F1 should be > 0.65 for a sanity pass.

**Success criterion:**
(a) Peak VRAM <= 3 GB at batch=32. If > 3 GB: re-run at batch=8
    and record result. If > 3 GB at batch=8: invoke R-5 mitigation.
(b) Per-epoch probabilities are valid (sum to 1 within 1e-5; entropy
    varies plausibly across epoch types).
(c) Sanity-check macro-F1 > 0.60 on the 2-subject Sleep-EDF sample.

**Estimated time:** 2 hours.

**Result field:** [FILL AFTER RUN]

---

## P-4 — Within-subject RF ceiling vs cross-subject RF gap (week 3)

**Question:** What is the within-subject performance ceiling of the
HRV-only Random Forest on the dev split? This establishes the upper
bound that a per-subject trained model achieves and frames how much
of the EEG-vs-HRV gap is recoverable with subject-specific data.

**Dataset/split:** HMC PSG dev subjects (75 subjects). 80/20 within-
subject train/test split per subject. This does NOT use the held-out
test partition.

**Procedure:**
1. For each of the 75 dev subjects, split their epochs 80/20
   (temporal split — first 80 % for train, last 20 % for test;
   do not shuffle, to respect temporal dependence in sleep).
2. Fit a separate RF (n_estimators=200, class_weight="balanced",
   random_state=42) on the 80 % training epochs for each subject.
3. Evaluate on the 20 % test epochs. Compute per-subject 3-class
   macro-F1.
4. Compare to the cross-subject RF macro-F1 on the dev LOSO split.
   Report the within-subject-minus-cross-subject gap.

**Success criterion:** Within-subject macro-F1 >= cross-subject
macro-F1 + 5 pp. If the gap is < 5 pp, the cross-subject model
is nearly as good as within-subject for HRV — which would be a
strong result, but must be scrutinized for temporal leakage.

Note: if within-subject < cross-subject by more than 5 pp, this is
anomalous and suggests the cross-subject model may be overfitting to
dev-split noise. Investigate feature importance for anomalies.

**Estimated time:** 1 hour.

**Result field:** [FILL AFTER RUN]

---

## P-5 — LSTM on HRV sequence (temporal context probe, week 3)

**Question:** Does a small LSTM (1 layer, 64 hidden units) trained on
30-epoch windows of HRV features outperform the epoch-wise Random
Forest on the dev split? If so, temporal context (sleep cycles) is
informative beyond single-epoch HRV.

**Dataset/split:** HMC PSG dev subjects (75 subjects). Subject-disjoint
LOSO on dev split only.

**Procedure:**
1. Construct sequence inputs: for each subject, create overlapping
   windows of 30 consecutive epochs (30 × 11 feature matrix as input,
   predict the stage of the central epoch). Stride 1.
2. LSTM: 1 layer, 64 hidden units, linear output head (5 classes).
   Total parameters: ~37,000. Train on all dev subjects except one
   (LOSO). Optimizer: Adam, lr=1e-3, epochs=20, batch=64.
3. Evaluate macro-F1 on the left-out subject. Aggregate across dev
   subjects.
4. Compare to RF macro-F1 from the dev LOSO run.

**Success criterion:** Not a pass/fail — directional only. If LSTM
macro-F1 > RF macro-F1 + 3 pp on dev LOSO, document "temporal context
is beneficial" and add the LSTM as an additional arm in the next
protocol iteration (requires an unlock note). If the gap is < 3 pp,
RF is sufficient and LSTM adds no meaningful value at this scale.

**Compute:** LSTM training on 75 dev subjects × LOSO = 75 training
runs. Each run has ~74 × ~1000 = ~74,000 training examples, 20 epochs.
At batch=64: ~23,000 gradient steps per run × 75 runs = CPU feasible
in ~2–3 hours. No GPU required.

**Estimated time:** 3 hours.

**Result field:** [FILL AFTER RUN]

---

## P-6 — Scope (a) framing probe: U-Sleep on Dreem-DOD-O with CI (week 4)

**Question:** For the Dreem-DOD-O OSA subjects (n=55), what are the
U-Sleep per-stage F1 values by AHI band, and what are the 95 % CI
widths? This frames the underpowered scope (a) pilot result honestly
before the NSRR DUA outcome is known.

**Dataset/split:** Dreem-DOD-O, all 55 subjects. This is an OOD
evaluation of U-Sleep (no training). All 55 subjects treated as
"test" for this pilot (there is no training on Dreem-DOD — U-Sleep
is frozen). Labeled as pilot; not a pre-registered headline.

**Procedure:**
1. Run U-Sleep frozen inference on all 55 Dreem-DOD-O subjects.
   Map U-Sleep predictions to Dreem-DOD's 5-class labels.
2. Use Dreem-DOD consensus labels (majority vote across 5 raters)
   as ground truth.
3. Compute per-subject 5-class per-stage F1 and 3-class macro-F1.
4. Stratify by AHI band (none/mild/moderate/severe — AHI is
   documented in Dreem-DOD-O). Compute per-stratum mean F1 and
   95 % CI via `cohort_stratifier.stratified_report()`.
5. Report CI widths explicitly. Expected: CI width for severe-OSA
   stratum will be wide (estimated n=10–15 subjects in that stratum),
   demonstrating the underpowered state clearly.

**Success criterion:** This pilot is purely a framing exercise.
Success = the pilot report is honest: CI widths are wide for small
strata, reported as such, and the pilot document does not claim this
is a powered result. The pilot informs the NSRR scope (a) design.

**Estimated time:** 3 hours (after P-3 confirms U-Sleep is running).

**Result field:** [FILL AFTER RUN]

---

## Notes on pilots

- Pilots may be run in priority order; P-1 must complete before others
  depend on HMC PSG data.
- All pilot results are labeled "dev-split / preliminary" in any logs
  or notes.
- No pilot result constitutes a headline result.
- If a pilot reveals a fatal design flaw (e.g., P-1 finds HMC PSG is
  DUA-blocked): update approach.md, risk-register.md, and protocol-
  lock.md before proceeding to the headline. An unlock note is required
  if the partition definition changes.
- Pilot scripts live in `30-implement/sleep-staging/code/pilots/`
  when written; each script's module docstring references this file's
  P-N entry.
