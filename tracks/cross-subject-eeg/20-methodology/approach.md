# Approach — cross-subject-eeg

**Track:** cross-subject-eeg
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

---

## Scope statement

Honest evaluation-diagnostic study on cross-subject EEG decoding.
Contribution is the evaluation program, not a new architecture.
The five-part program from candidate §6 fills gaps that EEG-FM-Bench
(arXiv:2508.17742) and the Critical Review (arXiv:2507.11783) name but do
not operationalize:

(a) Subject + dataset + hardware-disjoint held-out splits simultaneously.
(b) 0/1/5/20-shot calibration curves per subject, not aggregate only.
(c) Per-subject performance distributions, not mean ± SD only.
(d) Pre-training-overlap audit for every FM checkpoint evaluated.
(e) Riemannian and classical-ML baselines under the same disjoint splits.

No FM pre-training. No new architecture. Cancel-back authority exercised
below in §Compute-feasibility check; the conclusion is: feasible.

---

## Shared substrate

### Scan result

`shared/README.md` read end-to-end. `shared/data/`, `shared/eval/`,
`shared/models/` do not exist. `shared/` contains only its root README.
**This track is the first promoter.** There is nothing to consume;
everything described below is a net-new contribution to `shared/`.

### Consume

None. (Shared substrate is empty.)

### Promote on completion

The following four artifacts will be built in
`tracks/cross-subject-eeg/30-experiments/code/` and promoted to `shared/`
once ≥1 plausible second consumer exists. Plausible second consumers are
noted for each; they satisfy the shared/README.md promotion rule.

**1. `shared/eval/leakage_audit.py`**

Purpose: given lists of dataset IDs and subject IDs used in FM
pre-training and a proposed evaluation set, detect any intersection and
produce a structured report. The pre-training-overlap audit is the
highest-novelty evaluation utility in this portfolio — nothing equivalent
exists anywhere in shared/ and no other candidate naturally builds it.

Interface:

```python
def check_subject_overlap(
    pretrain_subject_ids: list[str],
    eval_subject_ids: list[str],
) -> dict:
    """
    Returns {"overlap_count": int, "overlap_ids": list[str],
             "overlap_fraction": float, "clean": bool}.
    """

def check_dataset_overlap(
    pretrain_dataset_names: list[str],
    eval_dataset_names: list[str],
) -> dict:
    """
    Returns {"overlap_datasets": list[str], "clean": bool}.
    """

def report_leakage_summary(
    subject_result: dict,
    dataset_result: dict,
    fm_name: str,
    eval_set_name: str,
) -> str:
    """
    Returns a human-readable, log-safe summary string.
    """
```

Plausible 2nd consumers: affective-state (Brookshire 2024
trial-level leakage framing); sleep-staging (pre-training overlap
check for any FM-pretrained stager evaluated on NSRR / HMC PSG).

**2. `shared/eval/fewshot_curve.py`**

Purpose: given a model with a `fit(X, y)` / `predict(X)` interface,
support sets of labeled examples, and query sets, compute accuracy at
each shot level and return a tidy DataFrame with 95 % bootstrap CIs.
Plotting utility included.

Interface:

```python
def fewshot_accuracy_curve(
    model,                              # sklearn-compatible or adapter
    support_sets: dict[int, tuple],     # {shot: (X_support, y_support)}
    query_X: np.ndarray,
    query_y: np.ndarray,
    shot_levels: list[int] = [0, 1, 5, 20],
    n_bootstrap: int = 2000,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Returns DataFrame with columns:
    [shot, accuracy_mean, ci_low, ci_high, n_query].
    shot=0 uses model without fitting (zero-shot).
    """

def plot_fewshot_curve(
    df: pd.DataFrame,
    title: str = "",
    save_path: str | None = None,
) -> None:
    """
    Plots mean accuracy + shaded 95 % CI across shot levels.
    """
```

Plausible 2nd consumers: sleep-staging (U-Sleep calibration-cost
curve — how many labeled subject records close the gap on a new
cohort); ecg-ppg-realworld (per-patient labeled-example curve for
abstention-threshold stabilization).

**3. `shared/eval/partition.py`**

Purpose: subject-disjoint train / dev / test splitting with optional
dataset-disjoint constraint. Reproducible via seed.

Interface:

```python
def subject_disjoint_split(
    subject_ids: list[str],
    dataset_labels: list[str] | None = None,
    test_fraction: float = 0.20,
    dev_fraction: float = 0.10,
    random_state: int = 42,
    dataset_disjoint: bool = False,
) -> dict[str, list[str]]:
    """
    Returns {"train": [...], "dev": [...], "test": [...]}.
    If dataset_disjoint=True, datasets (not subjects) are split at
    the top level; subjects within each split remain non-overlapping.
    """

def validate_partition(partition: dict[str, list[str]]) -> None:
    """
    Raises ValueError if any subject appears in more than one split.
    """
```

Plausible 2nd consumers: all EEG-facing tracks (sleep-staging,
affective-state). The utility is paradigm-agnostic.

**4. `shared/models/riemannian_baseline.py`**

Purpose: sklearn-compatible MDM (Minimum Distance to Mean on
Riemannian covariance manifold) wrapper via pyRiemann, with a
consistent fit/predict/score interface. Strong fast EEG baseline any
EEG-facing track can call without reimplementing.

Interface:

```python
def fit_mdm(
    X_train: np.ndarray,    # shape (n_trials, n_channels, n_samples)
    y_train: np.ndarray,
    metric: str = "riemann",
) -> object:
    """
    Returns a fitted pyRiemann MDM model (sklearn-compatible).
    """

def predict_mdm(
    model: object,
    X_test: np.ndarray,
) -> np.ndarray:
    """
    Returns predicted class labels.
    """

def score_mdm(
    model: object,
    X_test: np.ndarray,
    y_test: np.ndarray,
) -> float:
    """
    Returns accuracy.
    """
```

Plausible 2nd consumers: sleep-staging (covariance-based epoch
features on HMC PSG); affective-state (Riemannian features on
DEAP/WESAD, if an EEG-arm is included).

### Track-specific (not promoted)

- MOABB dataset loading scripts (paradigm-specific; unlikely to
  generalize to non-EEG tracks without heavy parameterization).
- LaBraM feature-extraction adapter (FM-checkpoint-specific).
- Per-experiment analysis notebooks.

---

## Dataset

### Primary datasets

**MOABB motor-imagery collection**

- Access: `pip install moabb` (version 1.1.x, pinned). All datasets
  downloaded on first use via MOABB's paradigm API.
- License: varies per dataset; all MOABB MI datasets are freely
  accessible for research. Key datasets and licenses:
  - BNCI2014_001 (BCI Competition IV-2a): 9 subjects, 4-class MI,
    publicly available, research use. This is the canonical LOSO
    benchmark. Available via MOABB.
  - BNCI2014_004 (BCI Competition IV-2b): 9 subjects, 2-class MI.
    Publicly available.
  - Zhou2016: 4 subjects (pilot value only; too few for held-out
    testing). Use dev split only.
  - PhysionetMI (GigaDB / PhysioNet): 109 subjects, 4-class MI,
    CC0. Largest single-dataset subject pool available via MOABB.
    Primary source of statistical power for per-subject distributions.
  - At least one additional MOABB MI dataset to be selected from
    Cho2017 (52 subjects) or Lee2019 (54 subjects) for dataset-
    disjoint held-out arm. Selection frozen at protocol-lock.

- Version pin: MOABB 1.1.x. Exact version recorded in
  `30-experiments/code/requirements.txt` at environment setup.
- Paradigm: `MotorImagery` via `moabb.paradigms`. Band-pass 8–35 Hz,
  epoch window [0.5 s, 2.5 s] relative to cue onset, baseline
  removed. These parameters are standard across the literature and
  consistent with BCI-IV-2a protocol.

**EEG Foundation Challenge dataset (HBN Releases 1–11)**

- Access: CC-BY-SA-4.0, no DUA, no registration. AWS S3 path
  `s3://nmdatasets/NeurIPS2025/` or NEMAR (nemar.org). Direct
  download confirmed in gap-closing pass 2026-05-02.
- Subjects: approximately 2,600, ages 5–21, 128-channel EEG, 6 tasks.
- Role: complementary dataset for the cross-task generalization arm
  of the FM probe. NOT a drop-in for the MI LOSO headline — pediatric
  population, different paradigm. Used to characterize FM behavior on
  a maximally different distribution from MOABB.
- Version: use HBN Releases 1–11 as retrieved at experiment start.
  Release 12 is not yet public (confirmed May 2026); do not wait
  for it.

### Held-out partition

Defined precisely in `protocol-lock.md`. Summary here:

- MOABB arm: PhysionetMI (109 subjects) is the held-out test dataset.
  No subject from PhysionetMI appears in any FM pre-training corpus
  known at time of locking (to be confirmed by leakage_audit.py).
  Remaining MOABB datasets (BNCI2014_001 + one additional) used for
  dev (parameter selection, pilot probes).
- HBN arm: Releases 9–11 (~300 subjects) are the held-out test arm
  for the cross-task FM probe. Releases 1–8 are the dev pool.
- Hardware-disjoint rationale: PhysionetMI was recorded with
  a BCI2000 / 64-channel system; BNCI2014_001 used a g.USBamp
  system. Different hardware manufacturers, different amplifier
  characteristics — hardware-disjoint at the dev-vs-test level is
  satisfied by this split.

### Splits

- Dev split (parameter selection, pilots, preliminary analysis):
  BNCI2014_001 + one additional MOABB MI dataset, HBN Releases 1–8.
- Held-out test split (headline experiment, touched once):
  PhysionetMI + HBN Releases 9–11.
- `partition.py:validate_partition()` run before any experiment
  to confirm no subject-ID overlap across splits.

---

## Preprocessing

**Pipeline for MOABB MI datasets**

All preprocessing via MOABB paradigm API (`moabb.paradigms.MotorImagery`)
which wraps MNE-Python. MOABB handles per-dataset normalization
differences internally.

1. Band-pass filter: 8–35 Hz (4th-order Butterworth, zero-phase).
   Rationale: captures mu and beta rhythms that carry MI signal;
   excludes low-frequency drift and high-frequency EMG.
2. Epoch extraction: [0.5 s, 2.5 s] post-cue. 2-second window is
   the standard MI epoch length across all cited benchmarks.
3. Baseline removal: subtract mean of [-0.2 s, 0 s] pre-cue window.
4. Channel selection: use MOABB paradigm default (dataset-native).
   Cross-dataset channel alignment handled by MOABB's
   `MotorImagery` interface for covariance-based methods.
   For LaBraM: map to LaBraM's expected montage using MNE's
   `mne.set_montage` + nearest-neighbor interpolation for missing
   channels (standard practice, no invented signal).
5. Artifact rejection: threshold-based (peak-to-peak > 100 µV per
   epoch flagged; channel > 5 SD flagged). Do not drop channels
   globally — per-epoch rejection only. Report rejection rate
   per dataset.
6. No further normalization before covariance computation.
   For LaBraM: normalize to [-1, 1] per channel per epoch as
   specified in the LaBraM paper.

**Software:** MNE-Python 1.6.x, MOABB 1.1.x, pyRiemann 0.6.x.
All versions pinned in `requirements.txt`.

**Pipeline for HBN (EEG Foundation Challenge)**

1. Load preprocessed EEG from HBN release files (EEGLAB format
   via MNE-Python `read_raw_eeglab`).
2. Band-pass 1–40 Hz (broader band than MI, captures passive
   paradigm content).
3. Epoch extraction: task-specific windows as defined in the
   challenge protocol (arXiv:2506.19141).
4. Artifact rejection: same threshold as MOABB arm.

---

## Model family

### Feasibility check (4 GB VRAM envelope)

**Riemannian MDM (pyRiemann):** CPU-only. Covariance matrix
computation on 2-second, 22-channel epochs (BNCI2014_001): matrix
is 22×22. Trivially fast. No GPU required. Confirmed feasible.

**FBCSP + LDA (baseline B):** CPU-only. Filter bank + CSP features
+ LDA classifier. No GPU required. Confirmed feasible.

**LaBraM frozen feature extractor + linear head:**
LaBraM-Base (arXiv:2405.18765, ICLR 2024 spotlight). Model weights
available at https://github.com/935963004/LaBraM.
- LaBraM-Base has approximately 5 M parameters.
- At batch=1, float32, sequence length ~200 tokens (2 s at 100 Hz
  after patching): peak VRAM is well under 1 GB in inference mode.
  No gradient computation (frozen). 4 GB envelope is not at risk.
- LaBraM-Large (approximately 350 M parameters) would require
  checking; see risk-register R-3 for the kill criterion.
- Default: use LaBraM-Base. Large variant is a pilot probe only.

Kill criterion for FM compute: if LaBraM-Base inference on a
single epoch with batch=1 exceeds 3 GB VRAM (leaving headroom for
OS and Python), the FM probe arm is cancelled and the headline
becomes Riemannian-only. (See risk-register R-3.)

### Model A — Primary (FM probe arm)

**LaBraM-Base frozen encoder + linear head (logistic regression)**

- Encoder: LaBraM-Base, weights frozen, used as feature extractor.
  Output: per-epoch embedding vector.
- Head: scikit-learn LogisticRegression fitted on k-shot support
  examples from the target subject (k ∈ {0, 1, 5, 20}).
  For k=0 (zero-shot): nearest-centroid classifier in embedding
  space, one centroid per class from dev-set subjects.
- Rationale: frozen backbone + linear head is the standard "honest"
  FM evaluation protocol. Full fine-tuning would require per-subject
  data and would not be a fair cross-subject test; it also risks
  4 GB overflow.
- Pre-training-overlap audit: before running headline, run
  `leakage_audit.py` against the known LaBraM pre-training dataset
  list (published in arXiv:2405.18765 §3.1: TUAB, TUEV, SEED, SEED-IV,
  SEED-V, FACED, BCICIV_2a, BCICIV_2b, etc.) vs the held-out test
  sets. Any overlap triggers removal of the overlapping dataset from
  the FM evaluation arm (not from the Riemannian arm). Result
  reported in the audit column of the headline results table.

### Model B — Baseline (strong classical)

**Riemannian MDM (Minimum Distance to Mean)**

- Features: spatial covariance matrix computed per epoch.
- Classification: MDM on the SPD manifold (pyRiemann).
- LOSO protocol: fit MDM on all subjects except one; test on
  left-out subject. No subject-specific adaptation.
  For k-shot: re-fit MDM including k examples from target subject
  in the training set. This is the standard Riemannian adaptation
  protocol and a demanding baseline (it had access to the target
  subject's covariance structure at test time at k>0).
- Rationale: MDM is the strongest within-session learner in the
  MOABB benchmark (Chevallier et al. 2024). If FM does not beat
  MDM cross-subject, that is the headline result.

### Model C — Second baseline (canonical MI)

**FBCSP + LDA**

- Features: Filter Bank CSP (5 bands × 4 spatial filters), LDA
  classifier.
- LOSO protocol: same as MDM.
- Rationale: canonical MI feature pipeline, widely reported in
  the literature, provides a lower bound (MDM should beat FBCSP
  cross-subject; if it doesn't, that's also informative).

### Summary table

| Model | GPU? | VRAM (est.) | Role |
|---|---|---|---|
| LaBraM-Base + linear head | optional | < 1 GB | primary FM probe |
| Riemannian MDM | no (CPU) | 0 | baseline A |
| FBCSP + LDA | no (CPU) | 0 | baseline B |

---

## Evaluation protocol

### LOSO structure

Leave-one-subject-out (LOSO) on each dataset independently:
for each subject s in dataset D, train on all subjects in D except s,
evaluate on s. Report mean accuracy ± 95 % bootstrap CI across
subjects within each dataset, then macro-average across datasets.

### Shot-level evaluation

At each shot level k ∈ {0, 1, 5, 20}:
- k=0: no target-subject data at test time (true zero-shot).
- k>0: k labeled epochs per class from the target subject are given
  to the model before evaluating on the remaining target-subject
  epochs. For FM: re-fit linear head on k examples. For MDM: add
  k examples to training pool and re-fit.
- Shot examples drawn randomly from the target subject's available
  trials; 50 random draws per (subject, k) pair; report mean
  accuracy and 95 % CI across draws.
- `fewshot_curve.py:fewshot_accuracy_curve()` implements this
  uniformly across all models.

**k=0 protocol symmetry note (m-1):** at k=0 both arms are
zero-target-subject-data in the same sense, but information types
differ. LaBraM k=0 = nearest-centroid in embedding space, with one
class centroid per dev-set subject's labels (uses dev-set class
labels). MDM k=0 = LOSO fit on dev-set training subjects' covariances
(uses dev-set covariance geometry + class labels). Performance gaps
at k=0 reflect both model quality AND the asymmetry between
embedding-space prototype matching vs SPD-manifold class centers;
the comparison is meaningful but not solely a model-quality test.

### Per-subject distributions

For each dataset × model × shot level:
- Report the full distribution of per-subject accuracy (violin or
  boxplot, and a cumulative distribution).
- Report TWO illiteracy fractions side-by-side (m-3 fix):
  - **At-or-below chance** — 25 % accuracy for balanced 4-class MI,
    50 % for 2-class. Subjects in this band have no measurable signal
    above chance.
  - **At-or-below the 70 % usability threshold** — Saha & Baumert 2020
    and the BCI-IV-2a protocol commonly use 70 % on 4-class MI as the
    practical-usability cutoff. Subjects below 70 % would not derive
    practical value from a deployed BCI even if their decoder is
    above chance.
  The 70 % figure is directly comparable to the cited 15–30 %
  illiteracy literature; the chance-level figure is the formal
  no-signal baseline.
- Do NOT report only the mean. Per-subject distributions are a
  primary output, not supplementary.

### Pre-training-overlap audit

Before running the headline:
1. Collect the published pre-training dataset lists for each FM
   checkpoint evaluated (LaBraM from arXiv:2405.18765 §3.1).
2. Run `leakage_audit.py:check_dataset_overlap()` against the
   held-out test sets.
3. Run `leakage_audit.py:check_subject_overlap()` if subject-level
   metadata is available.
4. Report the audit result in the headline results table as a column:
   "overlap detected: yes/no; overlapping datasets: [list]".
5. If overlap is detected for the FM arm's test dataset:
   - Remove that dataset from the FM headline evaluation.
   - Keep it for the Riemannian baseline (MDM has no pre-training).
   - Document the removal in results.

### Held-out partition discipline

The held-out test split (PhysionetMI, HBN Releases 9–11) is touched
exactly once, only after all model selection decisions are made on
the dev split. This is enforced by the protocol-lock.md and tracked
manually. Any preliminary analysis of the test split prior to the
single evaluation run invalidates the headline result.

### Statistical test for FM vs Riemannian comparison

Paired Wilcoxon signed-rank test, one-sided (H1: FM > MDM),
across subjects at each shot level. Significance threshold: p < 0.05
with Bonferroni correction across shot levels (4 tests; adjusted
threshold p < 0.0125).

Rationale for paired test: each subject yields one accuracy score
for each model; the natural pairing is by subject, which controls
for subject-level difficulty variation. Wilcoxon is preferred over
paired t-test because per-subject accuracy distributions are bounded
and potentially non-normal (bimodal due to BCI illiteracy).

Effect size: Cohen's d (paired) reported alongside p-value. A
statistically significant result with |d| < 0.2 is noted as
"statistically significant but practically small."

### Metrics

Primary: mean LOSO accuracy (macro-averaged across datasets,
per shot level), with 95 % bootstrap CI (n=2000, stratified by
subject, random_state=42).

Secondary:
- Per-subject accuracy distribution (violin plots, illiteracy-rate
  fraction below threshold).
- FM minus MDM delta at each shot level (with CI).
- Leakage audit result (structured report, not a number).
- Per-class accuracy for 4-class MI datasets (to detect class-
  imbalanced failure modes).

Reported separately for dev split and held-out test split.
Dev split results are preliminary and labeled as such.

---

## Ablations

Ablations run on the dev split only. They do not touch the held-out
test partition.

**Ablation 1: Electrode dropout (montage mismatch robustness)**

Procedure: at inference time, randomly zero out k% of channels
(k ∈ {10 %, 25 %, 50 %}) before computing covariance / FM features.
Hypothesis: if FM cross-subject gains are robust to electrode loss,
the embedding learned from the full-channel pre-training corpus
captures distributed spatial information. If gains collapse at 25 %
dropout, the FM is brittle to montage mismatch — a concern for
real-world deployment where electrode configurations vary.

**Ablation 2: Pre-training-overlap-removed FM**

Procedure: if the leakage audit finds that the FM was pre-trained on
any dev-set dataset, construct a "clean" linear head by fitting only
on subjects from datasets NOT in the pre-training corpus. Compare
accuracy of full-dev-set-fitted head vs clean head.
Hypothesis: if accuracy drops materially (> 5 pp), the FM's
cross-subject gains on that dataset were at least partly leakage-
driven. If accuracy holds, the FM has genuinely generalizable
representations.

**Ablation 3: Random-feature baseline**

Procedure: replace the LaBraM embedding with a random projection of
the same input dimensionality (PCA retained to match LaBraM output
dim). Fit the same linear head on k-shot examples.
Hypothesis: if LaBraM + linear head does not meaningfully outperform
a random projection + linear head cross-subject, the FM's
representations add no value beyond dimensionality reduction. This
is an important sanity check for the FM probe arm.

**Ablation 4: Within-subject FM upper bound**

Procedure: for each subject, fit the LaBraM linear head using a 70/30
within-subject split instead of cross-subject support. Report accuracy.
This is not a fair cross-subject result — it is the upper bound on
what the frozen FM can achieve if given subject-specific data. It
quantifies how much of the cross-subject gap is head-related vs
encoder-related.

---

## Uncertainty reporting

- **Bootstrap CI:** All accuracy means reported with 95 % bootstrap
  CI (n=2000 resamples, stratified by subject, fixed seed 42).
- **Multi-seed (shot sampling):** For k-shot evaluations, 50
  independent random draws of the support set per (subject, k).
  Report mean and CI across draws.
- **Cross-subject distribution:** In addition to mean ± CI, report
  the full per-subject distribution so readers can see spread and
  bimodality. Mean alone is insufficient for this problem domain.
- **Reporting format:** "XX.X % (95 % CI: YY.Y–ZZ.Z %, N=N_subjects)"
  for all headline numbers. Never report a point estimate without CI.

---

## Compute budget

| Task | Hardware | Estimated time |
|---|---|---|
| MOABB data download (~2 GB) | local | 1 hr |
| HBN data download (~50 GB, Releases 1–11) | local / Kaggle | 4–8 hr |
| Preprocessing (MOABB dev set) | CPU | 1–2 hr |
| Preprocessing (HBN dev set) | CPU | 4–6 hr |
| MDM LOSO on BNCI2014_001 (9 subj) | CPU | < 5 min |
| MDM LOSO on PhysionetMI (109 subj) | CPU | 30–60 min |
| FBCSP LOSO (PhysionetMI) | CPU | 30–60 min |
| LaBraM feature extraction (PhysionetMI) | GTX 1650 | 1–2 hr |
| Linear head fitting (all shot levels, 50 draws) | CPU | < 30 min |
| Bootstrap CI computation (n=2000) | CPU | < 1 hr |
| Ablations (dev split only) | CPU + GPU | 2–4 hr |
| **Total headline experiment (test split)** | CPU + GPU | **~4–6 hr** |

Total GPU budget: approximately 5–8 GPU-hours (GTX 1650). Well within
the local envelope. HBN download is the only significant I/O task; if
local storage is constrained, stream from Kaggle.

**Fits 4 GB envelope:** yes, with margin. LaBraM-Base inference
at batch=1 uses < 1 GB VRAM. Riemannian baselines are CPU-only.

### Time to first honest result

- Week 1: environment setup, MOABB dev data download, MDM LOSO on
  BNCI2014_001 (dev set result only, preliminary).
- Week 2: LaBraM feature extraction on dev set; linear head fitting;
  ablations 1 and 3 on dev split. Pilot probes (see pilots/).
- Week 3: HBN data download, preprocessing, leakage audit against
  LaBraM pre-training corpus.
- Week 4: headline experiment on test split (PhysionetMI + HBN 9–11),
  run once. Statistical tests. Write results.md.

**First honest result: week 4.** The dev-split preliminary result
(week 2) is labeled as such and not reported as the headline.

---

## Novelty and exploration notes

**What is genuinely novel:**
- The simultaneous application of all five quality-bar requirements
  from candidate §6 in a single study. EEG-FM-Bench (arXiv:2508.17742)
  enforces subject-independent splits but provides 0/5 of the other
  requirements. This track provides a protocol operationalizing all five.
- `leakage_audit.py` — a reusable pre-training-overlap audit
  tool. No equivalent exists in the EEG benchmark ecosystem.
- The fewshot_curve with per-subject distributions — the TCPL paper
  (arXiv:2506.19141 context) reports aggregate curves; per-subject
  distributions with explicit illiteracy-rate characterization are
  not reported in EEG-FM-Bench or the TCPL benchmark paper, which
  provide the direct comparison points (m-5 narrowing). MOABB and
  some LOSO papers do report per-subject tables, but not paired with
  the leakage-clean splits + few-shot curves + overlap audit
  combination this protocol delivers.

**What is standard and intentionally so:**
- LaBraM as FM probe: already the most-cited open-weight EEG FM.
- Riemannian MDM as baseline: the MOABB community's de facto strong
  baseline. Using it is disciplined, not uncreative.
- LOSO evaluation: the standard cross-subject protocol.
- Bootstrap CI: standard uncertainty quantification.

**What is exploratory (pilot probes, not pre-registered):**
- LaBraM-Large (if it fits in 4 GB) as a scaling probe.
- FgMDM (Riemannian with geodesic filtering) vs plain MDM.
- BENDR frozen encoder as a second FM probe (if its checkpoint is
  cleanly available and the leakage audit passes).
- K-nearest neighbor in Riemannian manifold for 1-shot adaptation.

These are captured in `pilots/README.md` and do not touch the
pre-registered headline protocol.
