> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Risk register — sleep-staging

**Track:** sleep-staging
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

Each risk has: description, probability (H/M/L), impact (H/M/L),
mitigation, and a concrete kill criterion. Kill criteria are threshold-
triggered: hitting one stops the affected arm immediately.
"Retire-cancel" means the whole track exits; otherwise only the
affected arm is cancelled.

The track has two arms — (b) HRV-only primary and (a) pretrained-
stager conditional. Kill criteria that affect only arm (a) do NOT
cancel the track; arm (b) is the safety net.

---

## R-1 — NSRR DUA not submitted or not received in time (scope a)

**Description:** The NSRR DUA for SHHS and MESA is not submitted on
day one of this layer, or is submitted but not approved within 4 weeks
of submission. Without SHHS or MESA, scope (a) OSA-stratification
headline is powered only by Dreem-DOD-O (n=55), which is 3–7x
underpowered for the primary claim (defensibility critic finding,
10-pain-point/shared/critic-defensibility.md §3).

**Probability (non-submission):** L (flagged as required action;
tracked explicitly).
**Probability (submission but late approval):** M (NSRR documented
approval lag 1–4 weeks; can extend to 8 weeks if institutional sign-off
is required).
**Impact:** H for scope (a); zero for scope (b) — scope (b) is DUA-free.

**Required first action (day one):**
Submit the NSRR DUA for SHHS and MESA immediately on the first day of
this layer. Log submission confirmation (email confirmation or NSRR
account DUA-status page screenshot) in
`30-implement/sleep-staging/runs/nsrr_dua_submission.txt`.

**Mitigation:**
1. Submit DUA day one. Use institution email for fastest processing.
2. While waiting: execute all scope (b) work (weeks 1–4) and scope (a)
   pilot work on Dreem-DOD-O (n=55) with honest CI widths.
3. If DUA arrives by week 4: begin NSRR preprocessing; scope (a)
   headline runs weeks 6–8.
4. If DUA does not arrive by week 4 after submission: scope (a) is
   cancelled per the kill criterion below. Scope (b) headline proceeds
   as the sole track result.

**Kill criterion:** If the NSRR DUA is NOT approved within 4 calendar
weeks of the confirmed submission date, cancel scope (a) OSA-
stratification headline. Scope (b) HRV-only headline proceeds
unaffected. Document the DUA timeline in results.md. The 4-week
clock starts from the date recorded in
`30-implement/sleep-staging/runs/nsrr_dua_submission.txt`.

Note (m-4 fix): "4 weeks" is **4 calendar weeks from the confirmed
submission date** logged in `30-implement/sleep-staging/runs/nsrr_dua_submission.txt`,
regardless of when in the layer that date falls. No proportional
adjustment.

---

## R-2 — HMC PSG access requires multi-week DUA or is unavailable

**Description:** The HMC Sleep Staging Database (Hassan et al. 2023, doi:10.13026/533e-0n28)
is described as requiring PhysioNet credentialed access. At implementation
start, the actual access tier may be more restrictive than expected —
requiring a multi-week institutional DUA rather than a same-session
account creation.

**Probability:** M (PhysioNet credentialed access is typically quick,
but specific datasets may have additional requirements not apparent from
the landing page).
**Impact:** H for scope (b) — HMC PSG is the primary scope (b) dataset.
If access is blocked, the primary arm has no data.

**Mitigation:**
1. Verify HMC PSG access tier in week 1 before any downstream
   dependencies are built.
2. If multi-week DUA required: substitute with CAP Sleep database
   (PhysioNet, ~108 subjects with various pathologies including sleep
   apnea; similar PhysioNet access tier). The CAP dataset has ECG
   channels for HRV extraction.
3. If CAP Sleep also requires DUA: use Dreem-DOD-H (25 subjects) for
   a smaller-scale scope (b) pilot and re-evaluate feasibility.
   At n=25, the scope (b) headline is underpowered — see kill criterion.

**Kill criterion:** If HMC PSG access requires a DUA that will not be
approved within 2 weeks, AND no substitute dataset with ≥ 75 subjects
with ECG channels is available DUA-free, retire-cancel the scope (b)
primary arm and retire-cancel the entire track unless scope (a) NSRR
data has already arrived. If scope (a) NSRR data is available, the
track may pivot to scope (a) only. Document the substitution attempt
in the retire-cancel note.

---

## R-3 — ECG channel absent or unusable in HMC PSG subjects

**Description:** HMC PSG includes ECG, but individual recordings may
have ECG channels with severe noise, flat-line segments, or electrode
dropout that makes R-peak detection unreliable. Excessive ECG quality
exclusions may reduce the usable subject count below the 76-subject
test threshold.

**Probability:** M (clinical PSG recordings routinely have ECG quality
issues; the exclusion rate in published HRV studies on PSG data is
typically 5–20 %).
**Impact:** M — reduces effective sample size.

**Mitigation:**
1. Apply SQI threshold (> 30 % low-quality windows → exclude subject)
   as specified in preprocessing §Stage 1.
2. Report the exclusion count explicitly.
3. If exclusion reduces the test split below N=60 subjects: the
   power for the 17 pp gap test drops to ~75 % (from 80 %). Report
   the actual achieved power.
4. If exclusion reduces test split below N=40: the 17 pp gap claim is
   no longer adequately powered.

**Kill criterion:** If ECG quality exclusions leave fewer than 40
usable test subjects, the primary scope (b) headline metric (3-class
macro-F1 EEG-vs-HRV comparison) is underpowered to detect the 17 pp
gap. In that case, either (a) substitute the CAP Sleep dataset to
supplement the subject count, or (b) report the available result with
an explicit underpowered caveat and reduce the claim scope accordingly.
This does not automatically trigger retire-cancel but the results
interpretation must be downgraded.

---

## R-4 — U-Sleep checkpoint unavailable or license-incompatible

**Description:** The U-Sleep pretrained checkpoint (Perslev et al.
2021, https://github.com/perslev/U-Sleep) is unavailable, requires
login, or carries a license that prohibits usage on Dreem-DOD or
NSRR data.

**Probability:** L–M (U-Sleep has a research license that permits
non-commercial use; the checkpoint is available via GitHub; however,
the original paper was trained on NSRR data among others, which may
create license conflicts for evaluation on NSRR data specifically).
**Impact:** H for scope (a) — U-Sleep is the primary pretrained stager.
Impact L for scope (b) — U-Sleep is only the EEG comparison model.

**Mitigation:**
1. Download and verify U-Sleep checkpoint at implementation start.
   Record SHA-256 hash.
2. Verify license against Dreem-DOD and HMC PSG data agreements.
3. If U-Sleep is unavailable: substitute with DeepSleepNet (Supratak
   et al. 2017; weights available at https://github.com/akaraspt/deepsleepnet)
   or SleepTransformer (Phan et al. 2022; weights available via
   corresponding author on request or via HuggingFace). Document the
   substitution.
4. For scope (b) EEG comparison specifically: a simpler CNN baseline
   (1D-ResNet trained on Sleep-EDF dev split and tested on HMC PSG
   test split) can substitute U-Sleep. This is a weaker EEG baseline
   but avoids the pretrained-checkpoint dependency entirely.

**Kill criterion:** If no pretrained EEG stager checkpoint can be
obtained with a compatible license, cancel the pretrained-stager
comparison from scope (a). Scope (b) EEG comparison falls back to
a dev-trained 1D-ResNet baseline — see approach.md for the fallback.
If the 1D-ResNet fallback also cannot be trained within the compute
envelope (R-5), retire-cancel scope (a) and proceed with scope (b)
alone.

---

## R-5 — U-Sleep inference exceeds 4 GB VRAM on GTX 1650

**Description:** U-Sleep processes multi-channel EEG at 100 Hz in
30-second epochs. At batch=32, the activation memory may exceed the
3 GB safe threshold (leaving headroom for OS/CUDA).

**Probability:** M (U-Sleep architecture is not trivially small;
the original implementation used A100 GPUs, though inference is
lighter than training).
**Impact:** M — would require batch-size reduction or Kaggle fallback.

**Mitigation:**
1. Run U-Sleep VRAM probe (pilot P-1) on a single batch before any
   large-scale inference. Measure `torch.cuda.max_memory_allocated()`.
2. If VRAM > 3 GB at batch=32: reduce to batch=8 or batch=1 and
   re-check. Inference speed decreases linearly with batch size
   but remains feasible.
3. If VRAM > 3 GB even at batch=1: move U-Sleep inference to Kaggle
   T4 (16 GB VRAM, 9 hr/week). Extract features (probabilities) in
   a Kaggle notebook, download the probability arrays locally for
   evaluation.

**Kill criterion:** If U-Sleep inference cannot be run locally at any
batch size, AND Kaggle T4 inference fails (quota exhausted or
environment conflict unfixable within 2 days), cancel the U-Sleep EEG
comparison from scope (a) and scope (b). The scope (b) EEG comparison
falls back to the dev-trained 1D-ResNet baseline (R-4 fallback). If
that also fails, scope (b) reports HRV-only RF results without a
direct EEG comparison, noting the gap claim cannot be quantified at
this resource level. This does not retire-cancel the track but
narrows the headline claim.

---

## R-6 — Dreem-DOD download too large for local storage

**Description:** dodh.zip (21.9 GB) + dodo.zip (36.2 GB) = 58.1 GB.
Local storage may be insufficient.

**Probability:** M (depends on disk; not verified at methodology lock).
**Impact:** M — affects scope (a) OOD probe; does not affect scope (b)
primary arm.

**Mitigation:**
1. Check available local disk space before scheduling Dreem-DOD download.
2. If insufficient: use Kaggle Datasets to mount Dreem-DOD via the
   Zenodo URL in a notebook. Extract features (probability arrays)
   in the notebook; download only feature matrices locally (~MB scale).
3. If scope (a) OOD probe cannot run: drop it from the track work plan.
   Scope (b) is unaffected.

**Kill criterion:** If Dreem-DOD is inaccessible both locally and via
Kaggle within week 2, drop the Dreem-DOD OOD probe from scope (a).
This does not trigger retire-cancel; scope (b) headline is unaffected.
Document the access failure.

---

## R-7 — HRV features are insufficient to discriminate N1 from N2

**Description:** N1 is the hardest stage for both human raters (κ=0.24)
and EEG-based automated stagers (F1 ~0.40–0.53). HRV-only features
may completely fail to discriminate N1 from N2, producing N1 F1
near zero. This is an expected outcome, not a model failure — but it
must be reported, not hidden.

**Probability:** H (N1 is characterized primarily by EEG vertex sharp
waves and slow eye movements, not by distinctive HRV dynamics; N1 HRV
is similar to light NREM in most subjects).
**Impact:** L — this is a valid informative result, not a fatal outcome.

**Mitigation:**
1. Report N1 F1 explicitly in 5-class results. Do not collapse N1
   into a success metric.
2. Compare HRV-only N1 F1 to human-rater N1 κ = 0.24 explicitly.
   A result near κ=0.24 in F1-equivalent terms shows HRV-only is at
   the human rater ceiling for N1 — which is itself interesting.
3. If 5-class HRV-only N1 F1 < 0.10: note that N1 discrimination is
   essentially chance-level without EEG, and the 3-class collapse
   (N1+N2+N3 → NREM) is scientifically motivated, not a post-hoc fix.

**Kill criterion:** None. N1 failure is a pre-specified expected outcome.
It does not trigger a cancel.

---

## R-8 — HRV-only staging matches EEG (scope b null result)

**Description:** The Wilcoxon test finds no significant difference
between HRV-RF and U-Sleep-EEG macro-F1 on the 77 test subjects.
This is the "wearables don't need EEG" finding.

**Probability:** L (published literature reports ~17 pp gap; at
HMC PSG this may be larger or smaller depending on pathology mix).
**Impact:** L — this is a pre-specified defensible-null outcome per
the defensibility critic. Both directions are informative.

**Mitigation:**
1. Report the full result including CIs. A null result with narrow CIs
   is more informative than a positive result with wide CIs.
2. If null: frame as "HRV-only staging is not detectably inferior to
   EEG-based staging at this sample size and pathology mix; this has
   implications for EEG-less wearable deployment."
3. Ensure ablations are complete so the null cannot be attributed to
   a weak EEG baseline (compare U-Sleep vs other EEG baselines as
   a dev-split probe).

**Kill criterion:** None. The null outcome does not trigger a cancel.

---

## R-9 — Held-out partition touched prematurely (protocol violation)

**Description:** Any analysis — including "just looking" at summary
statistics — is performed on the 76-subject test split before the
single authorized evaluation run.

**Probability:** L–M (easy to trigger inadvertently when debugging
code on a "full" dataset).
**Impact:** H — invalidates the honest-evaluation claim.

**Mitigation:**
1. Store test-subject IDs in a separate config variable (`test_subjects`)
   distinct from dev subjects. During dev and pilot phases, only
   dev_subjects is loaded.
2. Before the headline run, manually verify that no prior result file
   in `30-implement/sleep-staging/runs/` contains metrics computed
   on test-split subjects.
3. If a test-split subject's data was inadvertently loaded: document
   the violation in results.md immediately. Assess whether any model
   selection decision was influenced by test-split information.

**Kill criterion:** If a model selection decision (choice of feature set,
choice of HRV window length, choice of RF hyperparameters) was made
after seeing test-split performance, retire-cancel the headline
experiment. The evaluation is no longer honest. This is a hard cancel
with no recovery path. Document transparently.

---

## R-10 — Stage label quality in HMC PSG (single-rater labels)

**Description:** HMC PSG (PhysioNet 2018 CinC) staging labels were
produced by a single clinical site. Single-rater labels have inherent
noise (human kappa for overall sleep staging ~0.76; N1 kappa ~0.24).
A model trained on single-rater labels and evaluated on the same
label set may appear to perform better than it actually does, because
both training and testing share the same rater's systematic errors.

**Probability:** H (single-rater is the norm for CinC challenge data).
**Impact:** M — inflates apparent accuracy by unknown amount, but the
paired EEG-vs-HRV comparison remains valid because both models share
the same label source.

**Mitigation:**
1. Acknowledge single-rater label limitation explicitly in approach
   and results.
2. The primary claim (EEG-vs-HRV gap) is not affected by single-rater
   bias because both models are evaluated against the same labels;
   the gap reflects modality difference, not label quality.
3. Optionally cross-reference a small subset of HMC PSG labels against
   Dreem-DOD multi-rater labels for orientation (this is a dev-only
   probe, not a headline).

**Kill criterion:** None. This is a documented limitation, not a
fatal flaw. It constrains the absolute-accuracy claim but not the
comparative gap claim.

---

## R-11 — Dreem-DOD multi-rater consensus labels — version compatibility

**Description:** Dreem-DOD was released in 2020 with a specific label
format (JSON per subject, 5-rater consensus). The Zenodo 2025 re-release
(record 15900394) may have different file formats or label encoding
than the benchmark repo's code expects.

**Probability:** M (re-releases sometimes change packaging).
**Impact:** M — delays preprocessing; fixable but takes time.

**Mitigation:**
1. Download Dreem-DOD and run a label-format smoke test in week 2
   (pilot P-2) before building the full scope (a) eval pipeline.
2. If format changed: adapt the loader to the new format. The benchmark
   repo (github.com/Dreem-Organization/dreem-learning-open) has data
   loading utilities that can serve as reference.

**Kill criterion:** If Dreem-DOD labels cannot be loaded within 2 days
of discovery, drop the Dreem-DOD OOD probe. Scope (b) unaffected.

---

## Summary table

| ID | Risk | Arm | P | I | Kill criterion |
|---|---|---|---|---|---|
| R-1 | NSRR DUA not received in 4 weeks | (a) | M | H | Cancel scope (a) headline |
| R-2 | HMC PSG DUA required / inaccessible | (b) primary | M | H | Retire-cancel track if no substitute ≥75-subject DUA-free dataset exists |
| R-3 | ECG quality exclusions reduce N < 40 | (b) | M | M | Downgrade claim scope; may substitute CAP dataset |
| R-4 | U-Sleep checkpoint unavailable | (a)/(b) | L–M | H | Cancel pretrained-stager comparison; fall back to dev-trained 1D-ResNet for EEG comparison |
| R-5 | U-Sleep VRAM > 3 GB on GTX 1650 | (a)/(b) | M | M | Move to Kaggle T4; if T4 also fails, cancel EEG comparison, narrow scope (b) claim |
| R-6 | Dreem-DOD download impractical locally | (a) | M | M | Use Kaggle; if inaccessible, drop Dreem-DOD OOD probe |
| R-7 | HRV N1 F1 near zero | (b) | H | L | None — valid pre-specified outcome |
| R-8 | HRV-only matches EEG (null result) | (b) | L | L | None — valid pre-specified outcome |
| R-9 | Held-out partition touched prematurely | both | L–M | H | Retire-cancel headline experiment |
| R-10 | Single-rater HMC PSG labels | (b) | H | M | None — documented limitation; comparative gap claim unaffected |
| R-11 | Dreem-DOD format mismatch on re-release | (a) | M | M | Drop Dreem-DOD OOD probe if unfixable in 2 days |

---

## Retire-cancel triggers (track level)

The entire track retires-cancelled (not just an arm) if:

1. **Primary data inaccessible:** HMC PSG and all substitute datasets
   (CAP Sleep, Dreem-DOD-H) cannot be accessed within 2 weeks of
   layer start, leaving no DUA-free dataset with ≥ 40 ECG-enabled
   subjects. Without primary data, neither scope can be executed.

2. **Protocol violation:** The held-out partition was used for model
   selection (R-9 severe case). Hard cancel, no recovery.

3. **ECG entirely absent from all accessible datasets:** R-peak
   detection is impossible across all available datasets, making
   HRV feature extraction infeasible. This would require pivoting
   the entire scope — in that case retire-cancel with documented
   reason.

In any retire-cancel scenario: write a concise retire-cancel note in
`10-pain-point/sleep-staging/admission.md`, update
`10-pain-point/shared/portfolio.md`, and tag
`v2-sleep-staging-retired-cancelled`. Still promote any reusable
substrate (hrv_features.py, calibration.py, cohort_stratifier.py)
that was built before cancellation, if ≥1 plausible second consumer
exists.
