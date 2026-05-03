> **Spec:** `10-pain-point/cross-subject-eeg/admission.md`

# Risk register — cross-subject-eeg

**Track:** cross-subject-eeg
**Date:** 2026-05-02 (updated 2026-05-03)
**Author:** methodologist agent
**Status:** draft — R-2 updated to reflect confirmed contamination + split-arm design; pending critic gate before layer 30

Each risk has: description, probability estimate (H/M/L), impact
(H/M/L), mitigation, and a concrete kill criterion (numeric or yes/no).
Kill criteria are checked at the milestone they apply to; hitting one
stops that risk's affected path immediately. "Retire-cancel" means the
track itself is retired; otherwise only the affected arm is cancelled.

---

## R-1 — LaBraM checkpoint unavailable or corrupted

**Description:** The LaBraM-Base weights at
https://github.com/935963004/LaBraM become unavailable (repo taken
down, file corrupted, license changed) between methodology lock and
experiment start.

**Probability:** L (repo is public, ICLR 2024 spotlight, active).
**Impact:** H (FM probe arm loses its primary model).

**Mitigation:**
1. Download and archive the checkpoint locally at environment-setup
   time (week 1), before any experiments begin.
2. Record SHA-256 hash of downloaded file in
   `30-implement/cross-subject-eeg/code/requirements.txt` alongside URL.
3. If unavailable: fall back to BENDR (open weights, confirmed
   available at https://github.com/SPOClab-ca/BENDR) or BIOT as
   the FM probe model. Run leakage audit for the substitute model.

**Kill criterion:** If no open-weight EEG FM checkpoint can be
downloaded, verified (hash), and loaded without error by end of week 1,
cancel the FM probe arm. The headline becomes Riemannian-only (MDM vs
FBCSP). This is a valid outcome — the Riemannian arm alone delivers
evaluation contributions (b), (c), (e) of the five-part program.

---

## R-2 — LaBraM pre-training corpus overlaps held-out test split

**Status (2026-05-03): TRIGGERED AND RESOLVED.** PhysionetMI confirmed
in LaBraM corpus. Substitution to Cho2017 (FM arm test set) executed.
Protocol-lock v2 reflects the split-arm design. See
unlock-note-2026-05-03.md for full record.

**Description:** The leakage audit confirmed that PhysionetMI ("EEG
Motor Movement/Imagery Dataset") is in LaBraM's pre-training corpus
(arXiv:2405.18765 §3.1). PhysionetMI may not serve as the FM arm test
set. HBN Releases 9-11 status: no explicit HBN entry found in the
published corpus list; treated as clean pending any corpus errata.

**Prior probability:** M → CONFIRMED hit for PhysionetMI.
**Impact:** M (Riemannian arm unaffected; FM arm test set substituted).

**Mitigation (executed):**
1. Leakage audit run prior to re-lock (2026-05-03).
   Result: PhysionetMI contaminated; Cho2017 clean; Lee2019 clean.
2. PhysionetMI removed from FM arm. Cho2017 substituted as FM test.
   Lee2019 assigned as secondary dev (frozen). PhysionetMI retained
   for Riemannian/classical arm (MDM has no pre-training corpus).
3. Audit result is a headline contribution and will appear in the
   results.md audit column.

**Residual risk:** If Cho2017 is later discovered to be in the LaBraM
corpus (corpus update or paper errata), re-run the audit and substitute
Lee2019 (confirmed clean as of this date). If both are contaminated,
fall to the kill criterion.

**Kill criterion:** If ALL MOABB MI candidate test datasets
(PhysionetMI, Cho2017, Lee2019, and any further candidates audited)
are confirmed in the FM pre-training corpus, cancel the FM arm.
The headline becomes: (1) Riemannian LOSO on PhysionetMI, and
(2) leakage audit documenting that LaBraM cannot be honestly evaluated
cross-subject on any available MOABB MI dataset at this time.
This is a publishable finding per the defensibility-critic verdict.

---

## R-3 — LaBraM-Base exceeds 4 GB VRAM at inference time

**Description:** LaBraM-Base, when loaded into PyTorch on the GTX 1650
in inference mode (batch=1, float32, sequence length corresponding to
a 2-second 22-channel epoch), consumes more than 3 GB VRAM. (3 GB
rather than 4 GB to leave headroom for OS, Python, and CUDA overhead.)

**Probability:** L (LaBraM-Base has ~5 M parameters; at float32,
weights alone are ~20 MB; input activations for a 22×200 epoch are
negligible). However, if LaBraM expects a large token sequence (e.g.,
whole-session context), this could spike.

**Impact:** H (would require moving to cloud or cancelling FM arm).

**Mitigation:**
1. As first pilot probe (week 1), run a single-epoch inference and
   log `torch.cuda.max_memory_allocated()`. Record in
   `pilots/README.md`.
2. If 3 GB < VRAM usage <= 4 GB: switch to float16 (half precision)
   for inference. Retest.
3. If still > 3 GB in float16: move FM feature extraction to
   Kaggle GPU notebook (T4 16 GB, 9 hr/week, sufficient for
   PhysionetMI 109 subjects). Store extracted features locally.
   This is not a compute-infeasible path.

**Kill criterion:** If LaBraM-Base at batch=1, float16, on Kaggle T4
fails to run (environment conflict, quota exhausted, or sequence-length
error not fixable within 2 days of debugging), cancel the FM probe arm.
Headline becomes Riemannian-only. Document the failure mode.

---

## R-4 — MOABB download or API changes break preprocessing pipeline

**Description:** MOABB 1.1.x API or a dataset download endpoint changes
between methodology lock and experiment start, breaking the preprocessing
pipeline.

**Probability:** M (MOABB is actively maintained; minor API churn between
minor versions is common).
**Impact:** M (delays, not a blocker if caught early).

**Mitigation:**
1. Pin MOABB version: `moabb==1.1.x` (exact patch version recorded at
   install time). Do not upgrade during the experiment.
2. Download all dev-split datasets in week 1 and cache locally.
   Do not re-download after caching.
3. If a specific dataset's download endpoint is broken: file a
   MOABB GitHub issue and use a direct download from the original
   source (BCI Competition IV, PhysioNet). MOABB datasets are all
   independently downloadable.

**Kill criterion (updated 2026-05-03):** If preprocessing fails for
PhysionetMI (Riemannian arm test) and cannot be fixed within 3 days,
the Riemannian arm may fall back to Cho2017 as its test set (shared
with FM arm; acceptable under the split-arm design). If preprocessing
also fails for Cho2017, retire-cancel with a documented failure reason.
Failure in only one arm does not retire-cancel the other arm.

---

## R-5 — PhysionetMI subject count is insufficient for planned statistical test

**Description (updated 2026-05-03 — split-arm design):**
Riemannian arm: PhysionetMI nominally has 109 subjects; the N=62
threshold for the illiteracy-rate power analysis is met with headroom.
FM arm: Cho2017 has 52 subjects — below the N=62 threshold. The FM
arm illiteracy-rate characterization is reported with a reduced-
precision caveat and stated as a limitation in results.md.

**Probability:** L–M (artifact rejection on a well-curated publicly
available dataset typically retains > 80 % of subjects).
**Impact:** M (weakens the illiteracy-rate characterization claim; does
not affect the FM-vs-MDM comparison which only needs paired samples).

**Mitigation:**
1. Compute post-rejection subject count during week 1 preprocessing.
   Report it explicitly.
2. **(M-1 fix per methodology-critic-v2 — corrected path):** If FM arm effective N falls below 62 after artifact rejection, add **Lee2019 test subjects** (or another audited-clean MOABB MI dataset NOT already in any frozen role) to the FM arm test set. Cho2017 may NOT be added to the dev set — it is the FM arm test set per protocol-lock §3 and would violate the touched-once partition. Any such addition must be flagged as a pre-experiment design adjustment, documented before touching any test data, and the new dataset audited via leakage_audit before inclusion.

**Kill criterion:** If the combined usable subject count across all
available MOABB test datasets falls below N=30 after artifact rejection,
the per-subject distribution analysis is underpowered to detect the
illiteracy signal. In that case, drop the illiteracy-rate claim from
the headline; retain the FM-vs-MDM comparison and the shot-curve
contributions.

---

## R-6 — HBN data download is too large for local storage / bandwidth

**Description:** HBN Releases 1–11 is approximately 50 GB. Local disk
space or download bandwidth may make this impractical.

**Probability:** M (depends on local disk, not verified at methodology
lock).
**Impact:** M (affects the HBN arm; does not affect the primary MOABB
headline).

**Mitigation:**
1. Check available local disk space before scheduling the HBN download.
2. If local space is insufficient: use Kaggle Datasets to mount the
   HBN data in a notebook (NEMAR AWS S3 path is publicly accessible
   from Kaggle). Extract features in the notebook and download only
   the feature matrices locally.
3. The MOABB arm alone is sufficient for the headline FM-vs-MDM claim.
   The HBN arm is a complementary dataset for cross-task analysis.

**Kill criterion:** If HBN data is inaccessible both locally and via
Kaggle within week 3, drop the HBN arm entirely. The headline is
MOABB-only. Document the access failure.

---

## R-7 — LaBraM-Base zero-shot (k=0) performance is at chance on all datasets

**Description:** With no target-subject calibration examples, the
nearest-centroid zero-shot classifier in LaBraM embedding space
performs at chance (25 % for 4-class, 50 % for 2-class). This would
mean the FM embedding has no cross-subject MI signal in the zero-shot
regime.

**Probability:** M (zero-shot cross-subject MI is genuinely hard; the
TCPL curve starts at 65.3 % at 1-shot, suggesting some cross-subject
signal, but zero-shot is even harder).
**Impact:** L (this is an informative result, not a fatal outcome;
chance performance at k=0 is a valid finding and expected by the
defensibility critic; the k>0 curves are more informative).

**Mitigation:**
1. Report the full k=0 result regardless of direction.
2. Provide a chance-level baseline in all plots (horizontal dashed
   line at 1/n_classes).
3. If k=0 is at chance for all FMs: frame the finding as "zero-shot
   cross-subject transfer does not exceed chance for LaBraM-Base;
   meaningful performance requires ≥1 calibration example" — this
   is consistent with the TCPL curve and is an honest, informative
   result.

**Kill criterion:** None. A null at k=0 is a valid, pre-specified
outcome. It does not trigger a cancel.

---

## R-8 — MDM beats FM at all shot levels (Null A)

**Description:** Riemannian MDM outperforms LaBraM-Base + linear head
at all shot levels k ∈ {0, 1, 5, 20} on the held-out test set.

**Probability:** H (EEG-FM-Bench explicitly finds compact domain-
specific architectures consistently outperform larger FMs; MDM has
strong inductive bias for MI covariance structure).
**Impact:** L (this IS the contribution: the defensibility critic
classified it as "defensible-null"; the result is informative
regardless of direction).

**Mitigation:**
1. This risk is pre-characterized by the defensibility critic.
   The protocol is designed to make a null result maximally
   informative: leakage-clean splits, per-subject distributions,
   shot curves.
2. If MDM beats FM: report with full statistical testing and CI.
   Frame as: "under leakage-clean evaluation conditions, Riemannian
   MDM remains the practical cross-subject baseline; LaBraM-Base
   does not demonstrate added value at any calibration budget."
3. Ensure the ablations (especially ablation 2, overlap-removed FM)
   are complete so that the null result cannot be attributed to
   inadvertent leakage favoring MDM.

**Kill criterion:** None. This outcome does not trigger a cancel.
It triggers a different framing of the results section.

---

## R-9 — Held-out partition touched prematurely (protocol violation)

**Description:** Any analysis, even "just a look," is performed on any
held-out test split (PhysionetMI for Riemannian arm, Cho2017 for FM arm,
or HBN Releases 9-11 for HBN arm) before the single authorized
evaluation run for that arm.

**Probability:** L–M (inadvertent; easy to do when debugging code on
"the full dataset").
**Impact:** H (invalidates the honest-evaluation claim; the core
scientific contribution is the honest protocol).

**Mitigation:**
1. Store test-set file paths in a separate config key (`test_paths`).
   During dev and pilot phases, only `dev_paths` is loaded.
2. Code review: before running the headline experiment, manually
   verify that no prior result file in `30-implement/cross-subject-eeg/runs/` was
   generated using test-set subjects.
3. If a test-set subject's data was inadvertently loaded during
   dev phase: document the violation explicitly in `results.md`.
   Do not hide it. Consider whether the violation is minor (data
   loaded but no model selection decision depended on it) or major
   (test-set performance influenced model or hyperparameter choice).

**Kill criterion:** If a model selection decision (choice of FM,
choice of k, choice of MDM metric) was made after seeing test-set
performance, retire-cancel the headline experiment. The evaluation
is no longer honest. Document transparently. This is a hard cancel
with no recovery path.

---

## R-10 — MOABB subject overlap across datasets (same subject recorded twice)

**Description:** Some subjects in MOABB datasets may be the same
physical person recorded under different paradigm protocols (e.g., a
lab that contributed to multiple datasets). This would violate the
subject-disjoint split assumption.

**Probability:** L (most MOABB datasets are from independent labs with
distinct subject pools; no known cross-dataset subject overlap in the
published literature).
**Impact:** M (would inflate cross-subject generalization estimates if
the overlapping subject appears in both train and test partitions
across datasets).

**Mitigation:**
1. Run `partition.py:validate_partition()` after constructing splits.
   This catches within-dataset overlap but not cross-dataset.
2. Document that cross-dataset subject identity cannot be verified
   programmatically from MOABB metadata. Acknowledge this as a
   limitation in results.md.
3. Limit the cross-dataset evaluation to datasets from demonstrably
   different labs (BNCI2014_001 is Graz; PhysionetMI is BCI2000
   labs — distinct subject pools with high confidence).

**Kill criterion:** None. If cross-dataset subject overlap is
suspected for a specific dataset pair, exclude that pair from the
cross-dataset generalization claim and document the exclusion.

---

## Summary table

| ID | Risk | P | I | Kill criterion |
|---|---|---|---|---|
| R-1 | FM checkpoint unavailable | L | H | No open-weight FM loadable by end of week 1 → FM arm cancelled |
| R-2 | LaBraM pre-training overlaps test split | TRIGGERED+RESOLVED | M | RESOLVED: Cho2017 substituted for FM arm; kill only if ALL candidates contaminated |
| R-3 | LaBraM-Base > 3 GB VRAM at inference | L | H | Fails on Kaggle T4 float16 → FM arm cancelled |
| R-4 | MOABB API / download breaks | M | M | PhysionetMI preprocessing fails, no substitute cleanable in 3 days → retire-cancel |
| R-5 | PhysionetMI N < 62 usable subjects | L–M | M | Combined test N < 30 after artifact rejection → drop illiteracy-rate claim from headline |
| R-6 | HBN data download impractical | M | M | Inaccessible locally and via Kaggle by week 3 → drop HBN arm |
| R-7 | FM zero-shot at chance | M | L | None — valid informative result |
| R-8 | MDM beats FM at all shot levels | H | L | None — valid informative result (defensible-null) |
| R-9 | Test split touched prematurely | L–M | H | Model selection depended on test-set performance → retire-cancel headline |
| R-10 | Cross-dataset subject overlap | L | M | None — document as limitation; exclude affected dataset pair |

---

## Retire-cancel triggers (track level)

The track retires-cancelled (not just an arm) if:

1. **Preprocessing blocker:** MOABB preprocessing fails for BOTH
   PhysionetMI AND Cho2017 (both arm test sets) and cannot be fixed
   within 3 days (R-4 extended to both). Single-arm failure cancels
   that arm only; the other arm continues.

2. **Protocol violation:** The held-out partition was used for
   model selection before the single authorized evaluation run (R-9
   severe case).

3. **No baseline computable:** pyRiemann MDM fails to run on
   BNCI2014_001 (the simplest 9-subject dataset). If the most
   basic baseline is broken, the evaluation infrastructure is broken
   and the compute envelope claim is false.

In any retire-cancel scenario, write a concise retire-cancel note in
`10-pain-point/cross-subject-eeg/admission.md` with the specific triggering
condition, update `10-pain-point/shared/portfolio.md`,
and tag `v2-cross-subject-eeg-retired-cancelled`.

A retire-cancel due to R-3 (FM compute infeasibility) is narrow:
only the FM arm is cancelled. The Riemannian-only headline is still
a valid track outcome — contributions (b), (c), (e) of the five-part
program do not require a FM.
