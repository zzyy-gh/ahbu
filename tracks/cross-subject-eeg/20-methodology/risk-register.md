# Risk register — cross-subject-eeg

**Track:** cross-subject-eeg
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

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
   `30-experiments/code/requirements.txt` alongside URL.
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

**Description:** The leakage audit (leakage_audit.py) finds that
PhysionetMI or HBN Releases 9–11 were included in LaBraM's
pre-training corpus (published in arXiv:2405.18765 §3.1). This would
invalidate the FM probe's cross-subject generalization claim for those
datasets.

**Probability:** M (LaBraM pre-training corpus includes BCICIV_2a and
BCICIV_2b, which are MOABB dev datasets; PhysionetMI is not listed in
the published corpus but the list may be incomplete).

**Impact:** M (affects interpretation, not the methodology; the
Riemannian arm is unaffected).

**Mitigation:**
1. Run leakage_audit.py before touching the test split, using the
   published pre-training corpus list from arXiv:2405.18765 §3.1.
2. If PhysionetMI overlaps: remove PhysionetMI from the FM arm's
   headline evaluation. Substitute Lee2019 or Cho2017 as the test
   dataset for the FM arm, if those are not in the pre-training corpus.
3. Report the audit result explicitly in the headline results table.
   The audit finding itself is a contribution regardless of direction.

**Kill criterion:** If the leakage audit finds that ALL candidate
held-out test datasets are in the FM pre-training corpus, and no
alternative dataset can be confirmed clean, cancel the FM cross-subject
generalization claim entirely. The headline becomes:
(1) Riemannian LOSO numbers, and
(2) leakage audit documenting that LaBraM cannot be honestly evaluated
    cross-subject at this time.
This is a publishable finding per the defensibility-critic verdict
(Null B: overlap found is itself informative).

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

**Kill criterion:** If preprocessing fails for PhysionetMI specifically
(the primary test dataset) and cannot be fixed within 3 days, substitute
Lee2019 or Cho2017 as the test dataset (subject to leakage audit passing
for that dataset). If no alternative test dataset can be preprocessed,
retire-cancel with a documented environment-failure reason.

---

## R-5 — PhysionetMI subject count is insufficient for planned statistical test

**Description:** PhysionetMI nominally has 109 subjects. After
artifact rejection and epoch filtering, the usable subject count may
drop below the N=62 threshold required to detect a 30 % vs 10 %
BCI illiteracy rate at 80 % power (per defensibility-critic power
analysis, §5 cross-subject-eeg).

**Probability:** L–M (artifact rejection on a well-curated publicly
available dataset typically retains > 80 % of subjects).
**Impact:** M (weakens the illiteracy-rate characterization claim; does
not affect the FM-vs-MDM comparison which only needs paired samples).

**Mitigation:**
1. Compute post-rejection subject count during week 1 preprocessing.
   Report it explicitly.
2. If N < 62: add Cho2017 (52 subjects) to the MOABB dev set and
   expand the dev-to-test ratio so the combined test set clears N=62.
   (This change must be flagged as a pre-experiment design adjustment,
   documented before touching any test data.)

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

**Description:** Any analysis, even "just a look," is performed on the
held-out test split (PhysionetMI, HBN Releases 9–11) before the single
authorized evaluation run.

**Probability:** L–M (inadvertent; easy to do when debugging code on
"the full dataset").
**Impact:** H (invalidates the honest-evaluation claim; the core
scientific contribution is the honest protocol).

**Mitigation:**
1. Store test-set file paths in a separate config key (`test_paths`).
   During dev and pilot phases, only `dev_paths` is loaded.
2. Code review: before running the headline experiment, manually
   verify that no prior result file in `30-experiments/runs/` was
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
| R-2 | LaBraM pre-training overlaps test split | M | M | All test datasets in pre-training corpus → FM headline cancelled; leakage audit IS the result |
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

1. **Preprocessing blocker:** MOABB preprocessing fails for all
   test-set candidates and cannot be fixed within 3 days (R-4
   extended to all datasets).

2. **Protocol violation:** The held-out partition was used for
   model selection before the single authorized evaluation run (R-9
   severe case).

3. **No baseline computable:** pyRiemann MDM fails to run on
   BNCI2014_001 (the simplest 9-subject dataset). If the most
   basic baseline is broken, the evaluation infrastructure is broken
   and the compute envelope claim is false.

In any retire-cancel scenario, write a concise retire-cancel note in
`tracks/cross-subject-eeg/README.md` with the specific triggering
condition, update `layers/10-pain-point-validation/portfolio.md`,
and tag `v2-cross-subject-eeg-retired-cancelled`.

A retire-cancel due to R-3 (FM compute infeasibility) is narrow:
only the FM arm is cancelled. The Riemannian-only headline is still
a valid track outcome — contributions (b), (c), (e) of the five-part
program do not require a FM.
