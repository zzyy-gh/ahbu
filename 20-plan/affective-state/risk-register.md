> **Spec:** `10-pain-point/affective-state/admission.md`

# Risk register — affective-state

**Track:** affective-state
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

Each risk has: description, probability estimate (H/M/L), impact
(H/M/L), mitigation, and a concrete kill criterion. Kill criteria are
checked at the milestone they apply to; hitting one stops that risk's
affected path immediately. "Retire-cancel" means the track itself is
retired; otherwise only the affected arm is cancelled.

---

## R-1 — DEAP or MAHNOB-HCI form approval delayed or denied

**Description:** DEAP (http://www.eecs.qmul.ac.uk/mmv/datasets/deap/)
and MAHNOB-HCI (https://mahnob-db.eu/hci-tagging/) require academic
request forms. Approval may take days to weeks, or be denied. WESAD
(PhysioNet CC-BY) requires no form.

**Probability:** M for delay (academic forms routinely take 1–10 business
days); L for denial (both are standard academic datasets with permissive
academic-use policies and long publication histories).

**Impact for delay:** M — delays headline by 1–2 weeks but does not
change the science. WESAD can be preprocessed and piloted in the interim.

**Impact for denial:** H — losing DEAP removes the largest dataset with
comparable arousal label format to MAHNOB-HCI; losing MAHNOB-HCI removes
the third dataset. Either denial narrows the cross-dataset claim.

**Mitigation:**
1. Submit both forms on day 1 of track life. Log submission date in
   `30-implement/affective-state/runs/dataset_access_log.txt`.
2. While waiting, run full pipeline on WESAD (no form needed). Confirm
   feature extraction and correlation code works.
3. If DEAP is denied: promote DREAMER as the second dataset (also
   requires a request form; submit in parallel on day 1). DREAMER
   (23 subjects, ECG + EDA) is the documented backup (see approach.md
   §Dataset, "Why DREAMER not included by default").
4. If MAHNOB-HCI is denied: use AMIGOS or DREAMER as the third dataset,
   subject to their access status. Document the substitution as a
   pre-headline design adjustment (before touching any headline data).

**Kill criterion:** If both DEAP AND MAHNOB-HCI forms are denied AND
DREAMER access is also denied, the track cannot assemble three datasets
with both arousal ratings and cardiac/EDA signals. In that case:
WESAD-only analysis (N=1 dataset) is not a cross-dataset reproducibility
study — it is an underpowered single-dataset correlation. **Retire-cancel
with documented access failure.** If exactly one substitute is available
(DREAMER), proceed with WESAD + DREAMER as a two-dataset version; document
the reduced claim (reproducibility across 2 datasets, not 3).

---

## R-2 — NeuroKit2 version produces different feature values than arXiv:2508.10561

**Description:** arXiv:2508.10561 used a specific (potentially older)
version of NeuroKit2 or an entirely different toolchain. Different
NeuroKit2 versions compute HRV features differently (e.g., RMSSD
formula, default HRV frequency bands, EDA decomposition parameters).
If our NeuroKit2 version computes materially different values for the
2 reproducible EDA features from the original paper, we cannot claim
partial replication.

**Probability:** M — NeuroKit2 has documented breaking changes between
minor versions (0.1.x vs 0.2.x feature naming and computation).

**Impact:** M — reduces the "partial replication" claim but does not
invalidate the new cardiac contribution. The headline binomial test
on our feature set is still valid regardless.

**Mitigation:**
1. Pin NeuroKit2 at a specific version (0.2.x at the time of environment
   setup; record exact version in requirements.txt).
2. Run a cross-check computation of RMSSD and SCL_mean on a short
   synthetic signal against known ground-truth values (unit test in
   `30-implement/affective-state/code/tests/`).
3. If the original paper specifies the toolchain version, use it.
   arXiv:2508.10561 is a preprint; check its GitHub / supplementary for
   toolchain specifics. If no version is specified, document that
   NeuroKit2 defaults at version X.Y.Z were used.
4. Report BioSPPy cross-check R-peak counts: if BioSPPy and NeuroKit2
   agree on R-peak detection for > 90% of windows, the downstream HRV
   features are consistent.

**Kill criterion:** None — a version mismatch with the original paper
narrows the replication claim but does not stop the track. Document
honestly: "our EDA features were computed with NeuroKit2 X.Y.Z;
arXiv:2508.10561 did not specify their toolchain version; direct
comparison of EDA feature values is therefore imprecise." The cardiac
extension stands regardless of this mismatch.

---

## R-3 — cvxEDA fails on one or more datasets (numerical instability)

**Description:** cvxEDA (the EDA decomposition method chosen as primary)
can fail with numerical errors on short segments, extreme noise, or
signal ranges outside its expected domain. WESAD chest EDA at 700 Hz
downsampled to 4 Hz may have edge cases. MAHNOB-HCI EDA quality is
variable.

**Probability:** M for at least one failure per dataset (edge cases in
low-quality windows). L for wholesale failure on a dataset.

**Impact:** L–M — per-window failures produce NaN features (handled
gracefully); wholesale failure on a dataset shifts all EDA decomposition
to the high-pass fallback, which changes feature values.

**Mitigation:**
1. Implement cvxEDA fallback to `nk.eda_phasic(method="highpass")`
   within the feature extractor. Log which windows used which method.
2. Report the fraction of windows that fell back per dataset.
3. Ablation A-2 explicitly tests cvxEDA vs high-pass; if they agree
   on reproducibility count, the choice does not affect the headline.

**Kill criterion:** None — the fallback handles this. If > 50% of
windows in a dataset required the fallback, note it in the results and
interpret the EDA reproducibility claim for that dataset with caution.

---

## R-4 — NeuroKit2 HRV feature schema changes between versions (breaking)

**Description:** NeuroKit2 has renamed or removed HRV features between
releases (e.g., column name changes in `nk.hrv()` output, removal of
some nonlinear features). If the environment is set up with one version
and then upgraded, the feature schema changes and the 164-feature count
changes, invalidating the pre-registered schema.

**Probability:** H if version is not pinned; L if pinned at environment
setup.

**Impact:** H — changes the N in the binomial test; invalidates the
pre-registered feature list.

**Mitigation:**
1. Pin NeuroKit2 to exact patch version in requirements.txt BEFORE
   running any feature extraction.
2. Write the feature schema YAML (`feature_schema_v1.yaml`) at first
   successful extraction run (before correlation analysis). The YAML
   is committed to the repo.
3. Do NOT upgrade NeuroKit2 during the experiment. If a bug requires
   upgrading, treat this as a protocol change: unlock note required,
   new feature schema YAML required.

**Kill criterion:** If NeuroKit2 is upgraded (accidentally or
necessarily) and the feature schema changes AFTER the headline
correlation analysis has begun (even partial), the correlation results
are invalid. **Retire-cancel the headline; start from a fresh pinned
environment.** This is preventable with discipline; include it as a
reminder.

---

## R-5 — Arousal label quality is insufficient for meaningful correlation

**Description:** DEAP and MAHNOB-HCI use post-hoc retrospective
self-report arousal ratings collected after each 1-minute stimulus clip.
These ratings may have very low intra-subject reliability (subjects
cannot reliably distinguish arousal levels across similar video clips).
If arousal labels are essentially random within a subject, the
Spearman rho for all features will be near zero regardless of the
underlying physiology — confirming the 2/164 finding for the wrong
reason (weak labels, not unstable features).

**Probability:** H that this is partially true. The construct-validity
critique (Lindquist & Barrett, candidate.md §3) specifically names this
problem.

**Impact:** M — a finding of near-zero rho for all features with near-
zero label variance would be the honest finding. It is informative
(confirms the label-validity critique) but prevents distinguishing
"features don't carry arousal" from "labels don't carry arousal."

**Mitigation:**
1. Before the headline, compute arousal label variance per subject
   per dataset. If mean per-subject variance in arousal ratings is
   < 0.5 (on a 1–9 scale, equivalent to less than half a point of
   typical variation), flag this as a "weak label" dataset.
2. Compute inter-rater reliability proxy: within each subject, split
   40 DEAP clips into two groups by clip number and compute
   split-half Spearman rho of arousal ratings. If split-half rho
   near zero, label reliability is low.
3. Report arousal label statistics (mean, std, variance per subject)
   as a dataset characterization section in results.md. This is
   honest provenance, not cherry-picking.
4. If labels are weak: the finding "we cannot test feature-stability
   because labels are unreliable" is itself a finding — consistent
   with the admission record's construct-validity evidence.

**Kill criterion (m-5 fix per methodology-critic — added numeric downgrade trigger):**
- Soft trigger: if at pilot P-3 ≥ 1 dataset has mean per-subject arousal-label variance < 0.5 OR split-half rho < 0.2, FLAG that dataset as "weak labels" and report results separately for "weak vs strong label" subsets.
- Hard kill: if ≥ 2 of 3 datasets fail BOTH variance and split-half thresholds, the headline is **demoted** to a single-dataset finding (whichever surviving dataset). The "three-dataset audit" framing is dropped; results are reported as "single-dataset feature audit on dataset X". This prevents the WESAD-only-finding-misrepresented-as-three-dataset failure mode flagged by the critic.
- If ALL three datasets fail: report "arousal label quality insufficient to test feature stability in these datasets; label quality is itself the bottleneck." Valid pre-characterized outcome (see defensibility critic §6).

---

## R-6 — BioSPPy R-peak cross-check reveals systematic ECG signal quality problem

**Description:** BioSPPy R-peak detector returns substantially different
counts from NeuroKit2 for a dataset (> 10% discrepancy rate across
windows). This would indicate ECG signal quality issues (noise, artifacts,
lead-off) that could corrupt all cardiac features.

**Probability:** M for MAHNOB-HCI (peripheral ECG, lab setting, but
varied electrode placement across subjects).

**Impact:** M — corrupted cardiac features in one dataset reduce the
cross-dataset reproducibility test to effectively 2 datasets for cardiac
features. EDA features are unaffected.

**Mitigation:**
1. Flag all windows with > 10% R-peak discrepancy between NeuroKit2
   and BioSPPy as low-quality. Exclude them from the headline
   correlation (document exclusion rate per dataset).
2. If > 30% of windows in a dataset are flagged low-quality for ECG:
   exclude that dataset's cardiac features from the cardiac reproducibility
   count. EDA features from that dataset remain usable.
3. Report per-dataset ECG quality statistics in results.md.

**Kill criterion:** If all three datasets have > 30% low-quality ECG
windows: cardiac feature reproducibility cannot be tested. Report as
"cardiac feature extraction infeasible at acceptable quality threshold;
EDA-only reproducibility reported." This narrows the claim (EDA only)
but is still informative as an EDA replication study.

---

## R-7 — Arousal operationalization choice drives reproducibility results

**Description:** The choice of how to operationalize arousal — binary
median split vs fixed threshold vs continuous — may itself determine
whether features appear reproducible. This is a design choice made
before the headline, but if it were changed post-hoc based on seeing
the results, the finding would be circular.

**Probability:** H that operationalization affects results (this is
documented in the admission record: "post-hoc binarization thresholds
varying arbitrarily across papers"). Low probability of post-hoc
manipulation if pre-registered.

**Impact:** H on scientific validity if not pre-registered.

**Mitigation:**
1. Pre-register the arousal operationalization per dataset in
   protocol-lock.md BEFORE running any feature extraction.
2. Ablation A-4 (WESAD amusement included) probes sensitivity to the
   operationalization choice, but it is framed as an ablation, not
   a headline result.
3. The headline uses the pre-registered operationalization regardless
   of whether a different choice might have yielded more interesting
   results.

**Kill criterion:** None — the operationalization is pre-registered
and cannot be changed post-hoc. If a post-hoc operationalization
change is made AFTER seeing any feature-level results, the headline
is invalidated. Treat the same as R-9 in the cross-subject-eeg
risk-register (protocol violation). Retire-cancel headline;
redesign with clean pre-registration.

---

## R-8 — arXiv:2508.10561 reproduces its EDA finding before we publish (priority risk)

**Description:** arXiv:2508.10561 is a preprint (2025). An expanded
follow-up or independent replication may be published by another group
before this track's results are available, including cardiac features.
This reduces the novelty of the AHBU contribution.

**Probability:** M (the preprint has existed since August 2025; the
AHBU track will run in May–June 2026; concurrent work is plausible).

**Impact:** M — reduces novelty of the cardiac extension; the shared-
substrate contribution (feature_stability.py) and the dataset combination
remain novel regardless. A pre-empted publication does not invalidate the
results; it reframes them as independent confirmation.

**Mitigation:**
1. Monitor arXiv:2508.10561's citation page and related searches once
   per week during the track run.
2. If a paper extending the EDA finding to cardiac features is published
   mid-run: evaluate whether AHBU's specific dataset combination (DEAP
   + WESAD + MAHNOB-HCI) is distinct from the new paper's corpus. If
   distinct, the contribution stands as an independent replication.
   If not distinct: evaluate whether the shared-substrate angle
   (feature_stability.py) is sufficient justification to complete.
3. Do not stop or slow down because of a potentially competing paper —
   run the analysis as pre-registered. Framing adjustments (independent
   replication rather than first-mover) are made at findings.md time.

**Kill criterion:** None — a competing publication does not stop the
track. The evaluation can still produce an honest findings.md that
characterizes what is and is not novel in light of the new paper.

---

## R-9 — Feature-correlation analysis run prematurely (protocol violation)

**Description:** The binomial test / Spearman correlation analysis is
run before the protocol-lock.md is committed, or is run multiple times
with result-based adjustments to the operationalization or feature list.
This would convert a pre-registered test into an exploratory one.

**Probability:** L if discipline is maintained; M if "just a quick
check" temptation is acted on.

**Impact:** H on scientific validity. The entire point of the
reproducibility audit is that it is pre-registered.

**Mitigation:**
1. The feature extraction pipeline (producing per-window feature
   DataFrames) can be run and verified for correctness without
   running the correlation analysis. Verify extraction correctness
   on dev data only (pilot probes P-1, P-2, P-3).
2. The correlation table and binomial test are run ONCE, after
   protocol-lock.md is committed and after the feature schema YAML
   is written and committed.
3. If any exploratory correlation is computed during development
   (e.g., to check that the pipeline produces non-NaN outputs), it
   must be documented as "exploratory, not pre-registered" in
   `30-implement/affective-state/runs/exploratory_log.txt`. It does not
   count as a headline result.

**Kill criterion:** If the correlation analysis was run before
protocol-lock.md was committed AND the result influenced any
operationalization or feature-list choice: **retire-cancel the
headline.** Write a clean pre-registration and re-run on fresh
data (if a different dataset combination is available) or retire
with a documented explanation that pre-registration was violated.

---

## Summary table

| ID | Risk | P | I | Kill criterion |
|---|---|---|---|---|
| R-1 | Dataset form delayed / denied | M delay, L denial | H for denial | Both DEAP + MAHNOB denied AND DREAMER denied → retire-cancel |
| R-2 | NeuroKit2 version mismatch with source paper | M | M | None — narrows replication claim; document |
| R-3 | cvxEDA numerical failure | M per window | L–M | None — high-pass fallback; flag if > 50% of windows |
| R-4 | NeuroKit2 feature schema breaks mid-run | L if pinned | H | Version upgraded after headline correlation began → retire-cancel headline |
| R-5 | Arousal labels too weak for correlation | H (partial) | M | None — weak labels IS a finding; document as primary finding if all 3 datasets affected |
| R-6 | ECG quality failures | M for MAHNOB | M | All 3 datasets > 30% low-quality ECG → cardiac-only arm dropped; EDA arm continues |
| R-7 | Operationalization choice drives results | H if not pre-registered | H | Post-hoc operationalization change after seeing results → retire-cancel headline |
| R-8 | Competing paper published mid-run | M | M | None — complete as independent replication |
| R-9 | Correlation analysis run before protocol lock | M (temptation) | H | Result influenced operationalization choice → retire-cancel headline |

---

## Retire-cancel triggers (track level)

The track retires-cancelled (not just an arm) if:

1. **Dataset access blocker (R-1 extended):** Both DEAP and MAHNOB-HCI
   access are denied AND no substitute (DREAMER, AMIGOS) is accessible.
   A one-dataset study (WESAD only) is not a cross-dataset reproducibility
   study; it does not address the pain point.

2. **Protocol violation (R-7 or R-9 severe case):** The feature list,
   operationalization, or datasets were adjusted after seeing any
   feature-level results, and the change cannot be documented as a
   protocol-locked ablation. The scientific contribution requires
   honest pre-registration; without it, the track contributes nothing
   not already in arXiv:2508.10561.

3. **NeuroKit2 wholesale failure (R-4 extreme):** NeuroKit2 is upgraded
   during the run, the feature schema changes, and the schema YAML
   committed before the headline is no longer reproducible from the
   environment used. If re-running from scratch with a fresh environment
   is feasible, do that; if not (data no longer accessible, time elapsed),
   retire-cancel with documented reason.

In any retire-cancel: write a retire-cancel note in
`10-pain-point/affective-state/admission.md` with the specific triggering
condition, update `10-pain-point/shared/portfolio.md`, and tag
`v5-affective-state-retired-cancelled`.

A retire-cancel does NOT prevent promoting `feature_stability.py` to
`30-implement/shared/eval/` if it was built before the cancel trigger.
Shared-substrate contributions survive track cancellation.
