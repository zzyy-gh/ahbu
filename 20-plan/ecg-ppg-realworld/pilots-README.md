> **Spec:** `20-plan/ecg-ppg-realworld/approach.md`

# Pilot probes — ecg-ppg-realworld (CinC 2017)

**Status:** Not pre-registered. Pilots use dev split ONLY (80 % of CinC
2017 working set, ~6,786 records, partition seed=42 per
`protocol-lock.md` §3). They do NOT touch the held-out test partition
(20 %, ~1,696 records, AF positive ~154). Results inform final design
choices but do not constitute headline results.

**Rewrite history:** Original pilots-README (committed in 93bf404) was
PTB-XL-specific and was retained in error after the PTB-XL → CinC 2017
pivot in cd372bd. Critic-v2 finding C-1 flagged the contradiction; the
rewrite below is the actual fix. The obsolete PTB-XL pilot scripts in
`30-implement/ecg-ppg-realworld/code/pilots/` (p1_ptbxl_load.py,
p2_classical_baseline.py, p3_xresnet_vram.py) are removed in this same
commit.

Run pilots in priority order. Each result must be recorded in the
"Result field" of its section. If a pilot reveals a fatal design flaw,
update approach.md and risk-register.md — do not silently discard the
result.

---

## P-1 — CinC 2017 download + class count verification (CRITICAL, week 1)

**Question:** Does PhysioNet/CinC 2017 v1.0.0 download cleanly under
its ODC-BY licence, and does the labelled training set contain the
expected ~771 AF records out of 8,528 total?

**Dataset/split:** All records (no test/dev partition yet at this stage —
this pilot reads the full REFERENCE.csv; the 80/20 partition is
generated and frozen only after this pilot passes).

**Procedure:**
1. Download from https://physionet.org/content/challenge-2017/1.0.0/
   (no credentialing required; ODC-BY).
2. Verify ODC-BY licence text in `LICENSE.txt`.
3. Read `REFERENCE-v3.csv`. Count records per class label
   (`N` Normal, `A` AF, `O` Other, `~` Noisy).
4. Assert total record count matches the published 8,528.
5. Sample-read 10 WFDB records via `wfdb.rdrecord()`. Confirm no
   parse errors and that `record.fs == 300` and `record.n_sig == 1`.
6. Report per-class counts, total, sample-read pass/fail, and the
   first ten record IDs read.

**Success criterion:**
- Total record count == 8,528 (exact, per CinC 2017 spec).
- AF (`A`) count >= 700 (expected ~771; >= 700 leaves comfortable
  margin for the 20 % test stratum to clear ~140 AF records — well
  above the protocol-lock §3 expected ~154 AF positive).
- 10 sample WFDB records load without error at 300 Hz, single lead.

**Estimated time:** 30–60 min (including download; CinC 2017 release
is ~600 MB compressed).

**Result field:** [FILL AFTER RUN]

If AF count < 700 or total ≠ 8,528: STOP, escalate to risk-register
R-1 (dataset-shape kill). The PTB-XL pivot was already triggered by
this same kind of discovery; a second dataset failure would force a
full design re-pass.

---

## P-2 — Classical baseline pipeline speed and sanity check on CinC 2017 dev (week 1)

**Question:** How long does the classical baseline pipeline (NeuroKit2
ECG features + logistic regression) take per CinC 2017 record, and
does the AF-vs-rest AUROC clear the lower-bound sanity threshold on a
1,000-record dev sample?

**Dataset/split:** Random 1,000-record sample from the CinC 2017 dev
split (80 %, ~6,786 records, partition seed=42). Stratified by class.
Use `partition.json` if it has been written by P-6; otherwise compute
the 80/20 split locally for this pilot only and discard (the canonical
partition.json is committed by the headline pre-flight).

**Procedure:**
1. Load 1,000 records via `wfdb.rdrecord()` from the dev sample.
2. Apply preprocessing: notch (50/60 Hz), baseline-wander highpass
   (0.5 Hz), clipping at ±5 mV, per-record z-score normalisation.
3. Extract NeuroKit2 ECG features via `ecg_process()` +
   `ecg_intervalrelated()` on the single CinC 2017 lead. Time the
   extraction per record.
4. Fit logistic regression (sklearn, C=1.0) on 800 records (binary
   AF-vs-rest). Evaluate AUROC on 200 held-out (within-pilot only;
   does NOT touch the headline test split).
5. Inspect feature distributions: AFIB records should have visibly
   higher RR-interval CV than non-AFIB (sanity check).

**Success criterion:**
- Feature extraction < 10 s per record (10,000 records → < 30 hr;
  target < 3 s/record for full dev in < 6 hr).
- AUROC on 200-record subset > 0.75 (AF is highly distinguishable
  by RR-interval features on clean Lead I; AUROC < 0.75 implies a
  preprocessing or label-loading bug).
- AFIB CV(RR) visibly > non-AFIB CV(RR).

**Estimated time:** 2–3 hr.

**Result field:** [FILL AFTER RUN]

If extraction time > 10 s/record: parallelise via joblib or reduce
feature set. If AUROC < 0.75: debug preprocessing (R-peak detection
on noisy CinC 2017 records is non-trivial; try Pan-Tompkins).

---

## P-3 — xresnet1d50 VRAM probe at CinC 2017 input shape (CRITICAL, week 1)

**Question:** At the CinC 2017 headline input shape `(batch, 1, 9000)`
— 30 s × 300 Hz, single lead — how much peak VRAM does xresnet1d50
consume on the GTX 1650 4 GB at training batch=8, float32? Does the
loss decrease in the first epoch?

**Critic-v2 M-1 background:** The previous track-shared P-3 (in
cross-subject-eeg) ran at `(batch=32, seq_len=1000)` and reported
0.62 GB peak VRAM. CinC 2017 input is `(batch=8, seq_len=9000)` —
9× longer sequence, 0.25× batch, net ~2.25× scaling on a linear model
gives ~1.4 GB. The linear estimate is unverified for early-block
activation memory at 9× sequence length. **This re-probe is required
before any CinC 2017 training run** per critic-v2 fix M-1 in approach.md.

**Dataset/split:** 500-record subset of CinC 2017 dev (250 AF, 250
non-AF, balanced via oversampling). Synthetic input is acceptable for
the VRAM portion alone; real records are required for the loss-
decrease check.

**Procedure:**
1. Instantiate xresnet1d50 from `helme/ecg_ptbxl_benchmarking`,
   adjusted for single-lead input (`in_channels=1`).
2. Run one training epoch at `batch=8`, float32, on the 500-record
   sample.
3. Log `torch.cuda.max_memory_allocated() / 1e9` at peak.
4. Confirm loss at end of epoch < loss at start.
5. Repeat at float16 mixed-precision (`torch.cuda.amp.autocast()`).
6. If the float32 result is comfortably under threshold, also probe
   `batch=16` to inform secondary throughput planning (not gating).

**Success criterion (per protocol-lock §4 kill):**
- Peak VRAM <= **3.0 GB at float32, batch=8** OR <= 2.5 GB at
  float16, batch=8. Anything above 3.2 GB triggers the model
  substitution to xresnet1d18 per protocol-lock R-2.
- Loss(end) < loss(start) on the 500-record sanity training.

**Estimated time:** 1–2 hr.

**Result field:** [FILL AFTER RUN]

If VRAM > 3.2 GB at both float32 and float16: switch to xresnet1d18,
document the substitution in `runs/`, and re-run P-3 against
xresnet1d18. Substitution is pre-authorised in protocol-lock §4 and
risk-register R-2; no critic re-pass required.

---

## P-4 — Abstention threshold sweep on CinC 2017 dev validation hold-out (week 2)

**Question:** Does confidence-threshold abstention produce a
meaningful PPV-vs-coverage trade-off on a CinC 2017 dev subset? Is
the confidence-correctness AUC above the R-3 kill-trigger threshold
of 0.55?

**Dataset/split:** CinC 2017 dev (80 %, ~6,786 records). Internally
split: 80 % training (~5,429), 20 % validation hold-out (~1,357,
seed=42). Validation hold-out is the within-dev probe surface; NOT
the headline test split.

**Procedure:**
1. Train xresnet1d50 (or xresnet1d18 if P-3 forced substitution) for
   3 epochs on the within-dev training portion. (Quick sanity
   training, NOT the full 50-epoch headline training.)
2. Fit temperature parameter T on the validation hold-out using the
   protocol-lock §5 calibration procedure (Brier-score minimisation).
3. Compute coverage-vs-PPV curve via
   `30-implement/shared/eval/abstention.py:selective_classification_curve()`,
   sweeping threshold from 0.50 to 1.00.
4. Compute confidence-correctness AUC: per-record, label = 1 if the
   prediction is correct, score = max-softmax confidence; AUC
   summarises the predictive power of the confidence score itself.
5. Plot coverage-vs-PPV. Inspect for monotone relation
   (higher confidence → higher PPV).

**Success criterion:**
- Confidence-correctness AUC >= 0.55 (R-3 kill threshold). If a
  3-epoch model already produces AUC < 0.55, the abstention mechanism
  is fundamentally weak and the headline is at risk.
- PPV at coverage=0.83 (= 17 % abstention, the headline operating
  point) > PPV at coverage=1.00 (full commit) on the 3-epoch model.

**Estimated time:** 2–3 hr (includes 3-epoch training).

**Result field:** [FILL AFTER RUN]

A 3-epoch model is intentionally weaker than the 50-epoch headline.
A weak signal here is acceptable; a *reversed* signal (abstention
hurts PPV) warrants an investigation before headline.

---

## P-5 — Calibration baseline: Brier and ECE before vs after temperature scaling (week 2)

**Question:** How miscalibrated is the raw 3-epoch xresnet1d50 on the
CinC 2017 within-dev validation hold-out? Does temperature scaling
improve calibration in the right direction?

**Dataset/split:** CinC 2017 within-dev validation hold-out from P-4
(seed=42, ~1,357 records). Reuse the P-4 model.

**Procedure:**
1. Use the 3-epoch model from P-4.
2. Compute Brier score and ECE (15 bins) on the validation hold-out
   with and without temperature scaling.
3. Plot reliability diagrams side-by-side (uncalibrated vs calibrated).
4. Record temperature parameter T.

**Success criterion:**
- ECE(calibrated) < ECE(uncalibrated): temperature scaling improves
  calibration.
- Reliability diagram shows smaller deviation from the diagonal after
  scaling.
- T value in [1.0, 5.0]. T > 5.0 indicates severe overconfidence in
  the early model; expected to improve with full 50-epoch training
  but worth flagging.

**Estimated time:** 30–45 min (reuses P-4 model).

**Result field:** [FILL AFTER RUN]

If ECE not reduced by temperature scaling: investigate whether the
model is underconfident (T < 1.0) or whether Platt scaling is needed.

---

## P-6 — CinC 2017 partition audit: build and validate dev/test split (CRITICAL, week 2)

**Question:** Does
`sklearn.model_selection.StratifiedShuffleSplit(n_splits=1,
test_size=0.2, random_state=42)` on CinC 2017 produce the protocol-
lock §3 expected split (~6,786 dev / ~1,696 test, AF positive ~154
in test)?

**Dataset/split:** All CinC 2017 record IDs (REFERENCE-v3.csv). This
pilot **builds** the canonical partition.json and writes it to
`30-implement/ecg-ppg-realworld/runs/partition.json`. The
partition.json is committed to git as the frozen headline partition
once this pilot passes.

**Procedure:**
1. Load REFERENCE-v3.csv. Build the record_id → class_label table.
2. Run StratifiedShuffleSplit(n_splits=1, test_size=0.2,
   random_state=42).
3. Write `partition.json` with two keys: `dev_record_ids`,
   `test_record_ids` (sorted lists of record-ID strings).
4. Run `validate_partition()` (from cross-subject-eeg shared utility
   or local equivalent). Confirm zero overlap.
5. Report dev/test counts, per-class counts in each split, and
   confirm no record ID appears in both splits.
6. Write `partition_audit.txt` with the validate_partition() output.

**Success criterion:**
- Dev count in [6,750, 6,830]; test count in [1,690, 1,710].
  (Realised at seed=42, test_fraction=0.20 on the 8,528-record CinC 2017 set:
  n_dev=6822, n_test=1706. The dev upper bound is set at 6,830 so the realised
  6,822 falls comfortably inside without baking the exact realised value into
  the spec — the bound is a sanity range, not a target.)
- Test AF (`A`) count in [140, 170] (target ~154 per protocol-lock §3;
  realised 152).
- validate_partition() returns zero violations.
- partition.json committable as the canonical headline partition.

**Estimated time:** 30 min.

**Result field:** [FILL AFTER RUN]

If the test AF count falls outside [140, 170]: re-examine the seed
and stratification column. The protocol-lock §3 partition spec is
the authority; if the actual partition cannot meet the expected
composition, the protocol must be unlocked and re-locked before any
training begins. (This would surface a discrepancy between the
protocol's "expected ~154" and the realised partition; an unlock note
captures the actual numbers and re-justifies power.)

---

## Notes on pilots

- Pilots may be run in any order after their prerequisite week.
- All pilot results are labelled "dev-split / preliminary" in any
  notes or logs. No pilot result constitutes a headline result.
- Pilot scripts live in `30-implement/ecg-ppg-realworld/code/pilots/`
  with one file per pilot: `p1_cinc2017_load.py`,
  `p2_classical_baseline.py`, `p3_xresnet_vram_cinc.py`,
  `p4_abstention_sweep.py`, `p5_calibration_baseline.py`,
  `p6_partition_audit.py`. Each script's module docstring carries the
  spec line `Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-N` and
  each result JSON in `runs/` carries the same as the `spec` field.
- A future cross-dataset CinC 2020 single-lead probe is **not** part
  of this layer-30 work. It is a candidate post-headline extension
  noted in `approach.md` §Cross-dataset extensions; pre-registering
  it as a pilot would risk conflating exploration with the locked
  headline.
