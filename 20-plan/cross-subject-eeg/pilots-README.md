# Pilot probes — cross-subject-eeg

**Status:** Not pre-registered. Pilots use dev split ONLY.
They do not touch the held-out test partition (PhysionetMI,
HBN Releases 9–11). Results here may inform final design choices
but do not constitute headline results.

Each probe has: question, dataset/split, procedure, success criterion,
and estimated time. Run pilots in order of priority.

---

## P-1 — LaBraM-Base VRAM probe (CRITICAL, week 1)

**Question:** How much VRAM does a single LaBraM-Base forward pass
consume on the GTX 1650 at batch=1?

**Dataset/split:** None required. Use a synthetic input tensor of the
appropriate shape (n_channels x n_samples for BNCI2014_001: 22 x 200).

**Procedure:**
1. Install PyTorch + LaBraM dependencies.
2. Load LaBraM-Base weights: `torch.load(checkpoint_path, map_location="cuda")`.
3. Set model to `eval()`, `torch.no_grad()`.
4. Run one forward pass with a random input of shape (1, 22, 200).
5. Log `torch.cuda.max_memory_allocated() / 1e9` (GB).
6. Repeat at float16 if float32 exceeds 3 GB.

**Success criterion:** Peak VRAM <= 3 GB at float32 OR <= 2.5 GB at
float16. Documents the compute margin for risk-register R-3.

**Estimated time:** 30 minutes (including environment setup).

**Result field:** [FILL AFTER RUN]

---

## P-2 — MDM speed probe on BNCI2014_001 (week 1)

**Question:** How long does a full 9-subject LOSO with pyRiemann MDM
take on BNCI2014_001 (the smallest MOABB dataset)?

**Dataset/split:** BNCI2014_001 dev split (all 9 subjects).

**Procedure:**
1. Load BNCI2014_001 via MOABB `MotorImagery` paradigm.
2. Run LOSO with MDM (pyRiemann, metric="riemann").
3. Time the full LOSO loop.

**Success criterion:** Completes in < 10 minutes on CPU. If > 30 min,
investigate vectorization; MDM on 9 subjects × ~288 trials × 22 channels
should be fast.

**Estimated time:** 1 hour (including data download).

**Result field:** [FILL AFTER RUN]

---

## P-3 — LaBraM channel-mapping probe (week 2)

**Question:** Can LaBraM-Base process BNCI2014_001's 22-channel montage
(C3, Cz, C4, etc.) without error? LaBraM was pre-trained on datasets
with varying channel counts; the model must accept a non-standard montage.

**Dataset/split:** BNCI2014_001 dev split (5 subjects).

**Procedure:**
1. Preprocess BNCI2014_001 with MNE, extract 22-channel epochs.
2. Map electrode names to LaBraM's expected token IDs.
3. For missing LaBraM channels: use nearest-neighbor interpolation
   or zero-padding (whichever LaBraM's channel-ID scheme supports).
4. Run forward pass. Confirm output embedding is not NaN or all-zero.

**Success criterion:** Non-degenerate embedding output for > 90 % of
test epochs. Documents the channel-mismatch handling strategy for
approach.md preprocessing §5.

**Estimated time:** 2 hours.

**Result field:** [FILL AFTER RUN]

---

## P-4 — Zero-shot accuracy on 5 BNCI2014_001 subjects (week 2)

**Question:** What is the approximate zero-shot cross-subject accuracy
of LaBraM-Base nearest-centroid vs MDM on BNCI2014_001 (dev)?
This gives a directional estimate before committing to the full
PhysionetMI headline.

**Dataset/split:** BNCI2014_001 dev split (5-subject subset; the
other 4 subjects are held for the dev LOSO baseline).

**Procedure:**
1. Run LOSO on 5 subjects using MDM (baseline).
2. Run LOSO on 5 subjects using LaBraM nearest-centroid (zero-shot).
3. Compute accuracy per subject. Note: BNCI2014_001 is a dev dataset;
   this result is preliminary and labeled as such.

**Success criterion:** Not a pass/fail — this is purely directional.
Document the delta (FM minus MDM) and its sign. If FM is > 10 pp
below MDM at k=0 on 5 subjects, make sure approach.md's
characterization of k=0 as "expected to be at or near chance" is
accurate.

**Estimated time:** 3 hours.

**Result field:** [FILL AFTER RUN]

---

## P-5 — LaBraM-Large VRAM probe (week 2, optional)

**Question:** Does LaBraM-Large fit on GTX 1650 at float16?

**Dataset/split:** Synthetic input (same as P-1).

**Condition:** Only run if LaBraM-Large weights are available at
the same repo. If not available, skip.

**Procedure:** Same as P-1, using LaBraM-Large checkpoint.

**Success criterion:** Peak VRAM <= 3.5 GB at float16. If yes,
add LaBraM-Large as a scaling probe in the dev-split analysis
(not headline — Large is exploratory).

**Estimated time:** 30 minutes.

**Result field:** [FILL AFTER RUN]

---

## P-6 — leakage_audit.py smoke test (week 3)

**Question:** Does leakage_audit.py correctly detect known overlap
in a synthetic test case?

**Dataset/split:** No real data. Use synthetic lists.

**Procedure:**
1. Create a synthetic pretrain list: `["BNCI2014_001", "TUAB"]`.
2. Create a synthetic eval list: `["BNCI2014_001", "PhysionetMI"]`.
3. Call `check_dataset_overlap(pretrain_list, eval_list)`.
4. Assert: `overlap_datasets == ["BNCI2014_001"]`, `clean == False`.
5. Create non-overlapping lists; assert `clean == True`.

**Success criterion:** Both assertions pass. This is a unit test,
not a scientific result.

**Estimated time:** 20 minutes.

**Result field:** [FILL AFTER RUN]

---

## Notes on pilots

- Pilots may be run in any order after their prerequisite week.
- All pilot results are labeled as "dev-split / preliminary" in any
  notes or logs.
- No pilot result constitutes a headline result.
- If a pilot reveals a fatal design flaw, update approach.md and
  risk-register.md; do not silently drop the pilot result.
- Pilot scripts live in `30-implement/cross-subject-eeg/code/pilots/` when written.
