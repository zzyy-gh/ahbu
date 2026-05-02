> **Spec:** `20-plan/ecg-ppg-realworld/approach.md`

# Pilot probes — ecg-ppg-realworld

**Status:** Not pre-registered. Pilots use dev/validation split ONLY
(strat_fold 1–9). They do not touch the held-out test partition
(strat_fold 10). Results here may inform final design choices but do
not constitute headline results.

Run pilots in priority order. Each result must be recorded in the
"Result field." If a pilot reveals a fatal design flaw, update
approach.md and risk-register.md — do not silently discard the result.

---

## P-1 — PTB-XL load and AFIB record count verification (CRITICAL, week 1)

**Question:** Does PTB-XL v1.0.3 download cleanly, and how many
AFIB-labeled records exist in each strat_fold at likelihood_threshold=100.0?

**Dataset/split:** All folds (strat_fold 1–10 metadata only; strat_fold 10
waveforms NOT loaded). Read only `ptbxl_database.csv` and `scp_statements.csv`.

**Procedure:**
1. Download PTB-XL v1.0.3 from PhysioNet.
2. Load `ptbxl_database.csv` with pandas.
3. Parse `scp_codes` column; count records with AFIB likelihood >= 100.0
   per strat_fold.
4. Verify total record count = 21,799.
5. Verify that no patient_id appears in both strat_fold 1–9 and
   strat_fold 10 (run `partition.py:validate_partition()` on patient IDs).
6. Sample-read 10 WFDB records from strat_fold 1 using `wfdb.rdrecord()`.
   Confirm no parse errors.

**Success criterion:**
- strat_fold 10 AFIB count >= 87 (power threshold per risk-register R-2).
- validate_partition() passes with zero overlap.
- 10 WFDB sample records load without error.

**Estimated time:** 1–2 hours (including download).

**Result field:** [FILL AFTER RUN]
Expected: strat_fold 10 AFIB count ~ 151 (= ~1,514 / 10).
If count < 87: trigger R-2 mitigation before any further work.

---

## P-2 — Classical baseline pipeline speed and sanity check (week 1)

**Question:** How long does the classical baseline pipeline take
(NeuroKit2 feature extraction + logistic regression) on a 1,000-record
subset of strat_fold 1–8? Are extracted features sensible?

**Dataset/split:** Random 1,000-record sample from strat_fold 1–8
(balanced 500 AFIB, 500 non-AFIB where available; otherwise all AFIB
plus matched non-AFIB sample).

**Procedure:**
1. Load 1,000 records at 100 Hz using `wfdb.rdrecord()`.
2. Apply preprocessing pipeline (baseline wander, notch, clip, normalize).
3. Extract 12 features via NeuroKit2 `ecg_process()` + `ecg_intervalrelated()`
   on Lead II. Time the extraction per record.
4. Fit logistic regression (sklearn, C=1.0) on 800 records, evaluate on 200.
5. Report AUROC on the 200-record held-out subset.
6. Inspect feature distributions: do AFIB records have higher RR-interval
   CV than non-AFIB? (Sanity check — this should be obvious.)

**Success criterion:**
- Feature extraction < 10 seconds per record (10,000 records would take
  < 30 hours; target is < 3 s/record to complete in < 10 hours).
- AUROC on 200-record subset > 0.75 (AFIB is highly distinguishable
  by RR-interval features; AUC < 0.75 suggests a preprocessing error).
- AFIB records have visually higher RR-interval CV than non-AFIB.

**Estimated time:** 2–3 hours.

**Result field:** [FILL AFTER RUN]
If extraction time > 10 s/record: investigate parallelization with
joblib or reduce to fewer features. If AUROC < 0.75: debug
preprocessing (normalization, lead selection, Pan-Tompkins R-peak
detection on noisy records).

---

## P-3 — xresnet1d50 VRAM probe and one-epoch convergence check (CRITICAL, week 2)

**Question:** How much VRAM does xresnet1d50 use at training batch=32,
12 leads × 1,000 samples? Does the loss decrease in the first epoch?

**Dataset/split:** 500-record subset of strat_fold 1 (250 AFIB, 250
non-AFIB if available; oversample AFIB to balance).

**Procedure:**
1. Instantiate xresnet1d50 from the PTB-XL benchmarking repository.
2. Run one training epoch at batch=32, float32.
3. Log `torch.cuda.max_memory_allocated() / 1e9` (GB) at peak.
4. Confirm loss decreases from epoch start to epoch end.
5. Repeat at float16 mixed precision (torch.cuda.amp.autocast()).

**Success criterion:**
- Peak VRAM <= 3 GB at float32, OR <= 2.5 GB at float16.
  Documents R-8 risk status.
- Loss at end of epoch < loss at start (convergence check passes).

**Estimated time:** 1 hour.

**Result field:** [FILL AFTER RUN]
If VRAM > 3 GB float32 and > 2.5 GB float16: reduce batch to 16.
If loss does not decrease: check preprocessing and label extraction
before committing to full training.

---

## P-4 — Abstention threshold sweep on validation set (week 2)

**Question:** On strat_fold 9, does confidence-threshold abstention
produce a meaningful PPV-vs-coverage trade-off? Is the confidence-
correctness AUC above 0.55 (the kill-trigger threshold from risk-register R-3)?

**Dataset/split:** strat_fold 9 only (validation partition).

**Procedure:**
1. Train xresnet1d50 for 3 epochs on strat_fold 1 (quick sanity training —
   NOT the full 50-epoch training, which belongs in week 2).
2. Apply temperature scaling on strat_fold 9 (fit T on strat_fold 9
   Brier score).
3. Compute coverage-vs-PPV curve using `abstention.py:selective_classification_curve()`
   on strat_fold 9. Sweep threshold from 0.50 to 1.00.
4. Compute confidence-correctness AUC: is a record's max-confidence
   score predictive of whether its prediction is correct? Compute
   AUC where label = 1 if prediction is correct, score = max-confidence.
5. Plot the coverage-vs-PPV curve. Visually inspect for a monotone
   relationship (higher confidence = higher PPV).

**Success criterion:**
- Confidence-correctness AUC >= 0.55 (above chance; the R-3 kill
  criterion threshold). If AUC < 0.55 even on a 3-epoch model, the
  mechanism may be fundamentally broken.
- PPV at coverage=0.80 >= PPV at coverage=1.00 (abstention helps in
  the right direction, even if modestly on a 3-epoch model).

**Estimated time:** 2–3 hours (including 3-epoch training run).

**Result field:** [FILL AFTER RUN]
Note: a 3-epoch model is expected to be weaker than the final 50-epoch
model. This pilot is a directional sanity check, not a headline-quality
result. A weak signal here is acceptable; a reversed signal (abstention
hurts PPV) warrants investigation.

---

## P-5 — Calibration baseline: Brier score and ECE before temperature scaling (week 2)

**Question:** How miscalibrated is the raw (pre-temperature-scaling)
xresnet1d50 on strat_fold 9? Does temperature scaling improve it?

**Dataset/split:** strat_fold 9 (validation partition).

**Procedure:**
1. Use the 3-epoch model from P-4 (acceptable for a calibration probe).
2. Compute Brier score and ECE (15 bins) on strat_fold 9 with and without
   temperature scaling.
3. Plot two reliability diagrams side by side (uncalibrated vs. calibrated).
4. Record temperature parameter T.

**Success criterion:**
- ECE(calibrated) < ECE(uncalibrated) — temperature scaling reduces
  miscalibration in the right direction.
- Reliability diagram shows smaller deviation from the diagonal after
  scaling.
- T value is between 1.0 and 5.0 (a T value > 5.0 indicates severe
  overconfidence in the early model; may improve with full training).

**Estimated time:** 30 minutes (reuses P-4 model).

**Result field:** [FILL AFTER RUN]
If ECE is not reduced by temperature scaling: investigate whether the
model is underconfident (T < 1.0) or whether Platt scaling is needed.

---

## P-6 — Site overlap probe: are strat_fold 9 and strat_fold 10 from the same recording sites? (week 3, optional)

**Question:** Does the standard PTB-XL strat_fold split produce a
site-disjoint dev/test partition, or do the same recording sites appear
in both strat_fold 9 and strat_fold 10?

**Dataset/split:** ptbxl_database.csv metadata only (no waveforms).
This probe reads the strat_fold 10 site metadata — but NOT strat_fold 10
labels or waveforms. Site labels are administrative, not a model output.
Reading site metadata does NOT count as "touching the held-out split"
per protocol-lock §3.

**Procedure:**
1. Load ptbxl_database.csv. Group by strat_fold and extract unique
   site identifiers (if present in metadata).
2. Check whether any site appears in both strat_fold 9 and strat_fold 10.
3. Document the site overlap status.

**Success criterion:**
- Determine: is the strat_fold 10 partition site-disjoint from strat_fold 1–9?
- Document for the headline results table (not a kill criterion, but
  a limitation note if overlap exists).

**Estimated time:** 30 minutes.

**Result field:** [FILL AFTER RUN]
If sites overlap between folds: document as a limitation in approach.md.
The headline evaluation proceeds regardless — site disjointness is not
required by the protocol-lock, only patient disjointness is.

---

## P-7 — Cross-dataset probe sketch: CinC 2017 compatibility check (week 3, exploratory)

**Question:** Can a PTB-XL-trained model be applied to CinC 2017
single-lead ECG records without preprocessing errors? What is the
approximate AUROC on the CinC 2017 normal-vs-AF subset using the
PTB-XL-trained model's Lead I output?

**Dataset/split:** CinC 2017 training set (8,528 records, public).
This is NOT the headline test partition. It is a separate corpus used
only for this exploratory probe.

**Procedure:**
1. Download CinC 2017 records.
2. Extract Lead I-equivalent from PTB-XL preprocessing pipeline.
3. Run the xresnet1d50 (Lead I only or single-lead adapter) on CinC 2017
   normal vs. AF subset (training labels are available).
4. Compute AUROC on the full CinC 2017 training set (this is dev-only,
   no held-out partitioning needed for this exploratory probe).
5. Document the AUROC and note any preprocessing incompatibilities
   (different duration, different sampling rate after resampling).

**Success criterion:**
- No preprocessing errors (records load and normalize without crash).
- AUROC > 0.65 (directionally better than chance; a lower value suggests
  severe domain shift that may make the cross-dataset arm uninformative).

**Estimated time:** 2–3 hours.

**Result field:** [FILL AFTER RUN]
This pilot is exploratory. Its result determines whether the CinC 2017
cross-dataset arm is worth pursuing as a post-headline extension (not
part of the pre-registered headline).

---

## Notes on pilots

- Pilots may be run in any order after their prerequisite week.
- All pilot results are labeled "dev/val-split / preliminary" in any
  notes or logs.
- No pilot result constitutes a headline result.
- Pilot scripts live in `30-implement/ecg-ppg-realworld/code/pilots/` when written.
  Each script's module docstring includes:
  `Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-N`
- P-6 is the only pilot that reads any strat_fold 10 data (site metadata
  only, not labels or waveforms). This is explicitly permitted per
  protocol-lock §3 because site labels are administrative and do not
  influence model selection.
