> **Spec:** `10-pain-point/affective-state/admission.md`

# Risk register — affective-state

**Track:** affective-state
**Date:** 2026-05-02 (revised 2026-05-03 — pilot findings incorporated)
**Author:** methodologist agent
**Status:** revised — R-2 and R-3 updated per unlock-note-2026-05-03.md

---

## R-1 — DEAP or MAHNOB-HCI form approval delayed or denied

**Description:** DEAP and MAHNOB-HCI require academic request forms. WESAD
(PhysioNet CC-BY) requires no form.

**Probability:** M for delay (1-10 business days typical); L for denial.

**Impact for delay:** M — delays headline by 1-2 weeks; WESAD can be
processed in the interim.

**Impact for denial:** H — losing DEAP removes the largest dataset with
matched arousal label format; losing MAHNOB-HCI removes the third dataset.

**Mitigation:**
1. Submit both forms on day 1 of track life. Log submission dates.
2. Run full pipeline on WESAD in the interim.
3. If DEAP denied: promote DREAMER (23 subjects, ECG + EDA, academic form;
   submit in parallel on day 1) as the second dataset.
4. If MAHNOB-HCI denied: use DREAMER or AMIGOS as third dataset.
   Document as pre-headline design adjustment BEFORE processing any data.

**Kill criterion:** Both DEAP AND MAHNOB-HCI denied AND DREAMER denied.
WESAD-only (N=1 dataset) is not a cross-dataset reproducibility study.
Retire-cancel with documented access failure. If one substitute available
(DREAMER), proceed with two-dataset version; document reduced claim.

---

## R-2 — NeuroKit2 feature count and EDA pipeline confirmed (updated 2026-05-03)

**Updated description:** Pilots P-1 and P-2 have resolved the main
uncertainty in this risk. The confirmed facts are:

- **N_features confirmed at 92** from the nk-only calls as coded in the
  original protocol: 86 cardiac (25 time-domain + 10 freq + 51 nonlinear)
  + 6 from nk.eda_features. Source: pilot_p1_1777729248.json and
  feature_schema_v1.yaml.

- **cvxpy/cvxopt installation fails** on Windows 11 + Python 3.11.2.
  Confirmed: pilot_p2_1777731569.json (status=fail, cvxpy.installed=false).
  Mitigation enacted: highpass is now the primary and only EDA decomposition
  method (unlock-note-2026-05-03.md). cvxEDA is removed from the pipeline.

- **Power gap at N=92 confirmed and addressed.** At N=92,
  P(X<=2 | p=0.05) = 0.151 — not significant. Mitigation: expand EDA
  feature set to N_total = 126 using explicitly enumerated SCL/SCR/band-
  power/derived features computable from highpass decomposition. At N=126,
  P(X<=2 | p=0.05) ≈ 0.050 — at the threshold. At N=128,
  P(X<=2 | p=0.05) ≈ 0.046 — adequate. Feature_schema_v2.yaml will lock
  the exact count before the headline run.

- **NeuroKit2 vs arXiv:2508.10561 toolchain mismatch:** still partially
  open. The paper's Methods section has not been verified for whether it
  includes HRV features. The `arxiv_2508_10561_includes_hrv_FILL_MANUALLY`
  field in feature_schema_v1.yaml remains unverified. If the original paper
  did include HRV features, the novelty claim narrows (see approach.md
  scope note). This does not stop the track; the headline test is valid
  regardless.

**Probability:** L (the major uncertainties resolved; only the paper-Methods
verification is open).

**Impact:** L-M — paper-Methods verification affects novelty claim framing
but not the headline test validity.

**Mitigation (residual):**
1. Fetch arXiv:2508.10561 Methods section or supplementary to verify
   whether their "164 features" include HRV cardiac features or EDA only.
   If HRV included: reframe novelty as "independent replication on fresh
   dataset combination with per-subject Fisher-z aggregation."
2. Pin NeuroKit2 at 0.2.13 throughout; do not upgrade.
3. Cross-check RMSSD and SCL_mean on synthetic signal (unit test, already
   in P-1 scope).

**Kill criterion:** None — version or toolchain mismatch narrows the
replication claim but does not stop the track. Document honestly.

---

## R-3 — EDA feature NaN rates under highpass decomposition (updated 2026-05-03)

**Updated description:** cvxEDA is no longer in the pipeline (R-2 update).
The residual EDA risk is: highpass decomposition may produce near-zero
phasic components on datasets with low EDA amplitude (especially MAHNOB-HCI
lab recordings where EDA electrode quality varies). Near-zero phasic
components yield NaN or degenerate values for SCR features (no detectable
peaks).

**Probability:** M for at least some windows with NaN SCR features.
L for wholesale EDA NaN on a full dataset.

**Impact:** M — high per-feature NaN rates reduce the effective EDA
sample in the reproducibility test. If >50% of EDA features are excluded
from a dataset due to NaN, EDA reproducibility for that dataset is not
testable.

**Mitigation:**
1. Compute per-EDA-feature NaN rate per dataset from the feature matrices
   (Ablation A-2' in approach.md).
2. Exclusion rule: if an EDA feature has >30% NaN in a dataset, exclude
   that feature × dataset combination from the correlation test for that
   dataset. Document the exclusion list in results.md.
3. Report EDA feature usability summary: which features are computable
   in which datasets.

**Kill criterion (EDA arm only):** If >50% of EDA features (>20 of 40)
are excluded from all three datasets due to NaN rates, demote EDA features
to "auxiliary/informational" and report the cardiac-only (86-feature)
reproducibility count as the primary finding. The headline framing changes
to "cardiac HRV feature stability audit with auxiliary EDA." This is not
a track retire-cancel — the cardiac arm is unaffected.

---

## R-4 — NeuroKit2 HRV feature schema breaks if version changes mid-run

**Description:** NeuroKit2 has renamed or removed HRV features between
releases. If version changes, feature schema changes, invalidating the
pre-registered schema.

**Probability:** L (version is pinned at 0.2.13; confirmed P-1/P-2).

**Impact:** H if it occurs — invalidates the pre-registered feature list.

**Mitigation:**
1. NeuroKit2 pinned at 0.2.13 in requirements.txt.
2. feature_schema_v2.yaml committed before headline correlation.
3. No upgrades during the experiment.

**Kill criterion:** If NeuroKit2 is upgraded AND the feature schema
changes AFTER the headline correlation analysis has begun: retire-cancel
the headline; start from a fresh pinned environment.

---

## R-5 — Arousal label quality insufficient for meaningful correlation

**Description:** DEAP and MAHNOB-HCI use post-hoc retrospective self-report
arousal ratings. These may have near-zero within-subject variance.

**Probability:** H (partial) — label quality is a known problem
(admission record §3, Lindquist & Barrett evidence).

**Impact:** M — near-zero rho for all features may reflect weak labels,
not unstable features. Finding is still informative but interpretation
requires a label-quality caveat.

**Mitigation:**
1. Compute arousal label variance per subject per dataset before headline.
   Flag subjects with variance < 0.5 (on 1-9 scale) as "weak label."
2. Compute split-half reliability: within each DEAP/MAHNOB subject, split
   clips into two groups and compute split-half Spearman rho of arousal
   ratings.
3. Report arousal label statistics in results.md.
4. P-3 confirmed WESAD labels are valid (window counts adequate). DEAP
   and MAHNOB-HCI label quality to be assessed at download.

**Kill criterion (m-5 fix — numeric triggers):**
- Soft: if >=1 dataset has mean per-subject arousal variance <0.5 OR
  split-half rho <0.2, FLAG that dataset as "weak labels." Report
  results separately for weak vs strong label subsets.
- Hard: if >=2 of 3 datasets fail BOTH variance AND split-half thresholds:
  headline demoted to single-dataset finding. "Three-dataset audit"
  framing dropped; results reported as "single-dataset feature audit on
  dataset X."
- If all 3 fail: report "arousal label quality insufficient to test feature
  stability; label quality is itself the bottleneck." Valid pre-characterized
  outcome.

---

## R-6 — BioSPPy R-peak cross-check reveals ECG quality problem

**Description:** BioSPPy and NeuroKit2 R-peak detectors disagree by >10%
on a dataset, indicating ECG signal quality issues.

**Probability:** M for MAHNOB-HCI (varied electrode placement).

**P-2 confirmation:** On WESAD S2, BioSPPy returned 79 peaks vs NeuroKit2
81 (2.47% discrepancy, well within 10% threshold). WESAD ECG quality is
confirmed adequate. MAHNOB-HCI and DEAP not yet tested.

**Impact:** M — corrupted cardiac features in one dataset reduce the
cross-dataset test to effectively 2 datasets for cardiac features.

**Mitigation:**
1. Flag windows with >10% R-peak discrepancy as low-quality; exclude from
   headline correlation.
2. If >30% of windows in a dataset are flagged: exclude that dataset's
   cardiac features from the cardiac reproducibility count. EDA features
   from that dataset remain usable.
3. Report per-dataset ECG quality statistics in results.md.

**Kill criterion:** All three datasets have >30% low-quality ECG windows:
cardiac feature reproducibility cannot be tested. Report as "cardiac
feature extraction infeasible; EDA-only reproducibility reported." Narrows
claim but is still informative.

---

## R-7 — Operationalization choice drives reproducibility results

**Description:** Post-hoc operationalization changes (binarization threshold,
WESAD condition mapping) could drive the feature-level results.

**Probability:** H if not pre-registered; L given current pre-registration.

**Impact:** H on scientific validity if not pre-registered.

**Mitigation:**
1. Arousal operationalization locked in protocol-lock.md §3 before any
   feature extraction.
2. Ablation A-4 probes WESAD amusement inclusion as a registered ablation.

**Kill criterion:** If an operationalization change is made AFTER seeing
any feature-level results: retire-cancel headline; redesign.

---

## R-8 — Competing paper published mid-run

**Description:** An expanded or independent arXiv:2508.10561 follow-up
including cardiac features may be published before this track completes.

**Probability:** M (preprint from August 2025; AHBU track running May-June 2026).

**Impact:** M — reduces novelty; reframes as independent confirmation.

**Mitigation:**
1. Monitor arXiv:2508.10561 citations weekly during the run.
2. If a cardiac-extension paper is published: verify whether AHBU's dataset
   combination (DEAP+WESAD+MAHNOB-HCI) is distinct. If distinct: independent
   replication claim stands.
3. Do not slow down due to potential competing work.

**Kill criterion:** None.

---

## R-9 — Correlation analysis run prematurely (protocol violation)

**Description:** Spearman correlation or binomial test run before
protocol-lock.md is committed, or run multiple times with result-based
adjustments.

**Probability:** L with maintained discipline; M if "quick check" temptation
is acted on.

**Impact:** H — converts pre-registered test to exploratory.

**Mitigation:**
1. Feature extraction can be verified for pipeline correctness on dev data
   without running the correlation.
2. Correlation table and binomial test run ONCE after feature_schema_v2.yaml
   and this re-locked protocol-lock.md are both committed.
3. Any exploratory correlation during development documented in
   `30-implement/affective-state/runs/exploratory_log.txt`.

**Kill criterion:** Correlation run before protocol lock AND result
influenced any operationalization or feature-list choice:
retire-cancel headline; re-run with clean pre-registration.

---

## Summary table

| ID | Risk | P | I | Status | Kill criterion |
|---|---|---|---|---|---|
| R-1 | Dataset form delayed/denied | M delay, L denial | H | Open — forms submitted | Both DEAP+MAHNOB+DREAMER denied → retire-cancel |
| R-2 | NK2 count + cvxEDA failure | RESOLVED | — | Closed — N=92→126, highpass only | None (toolchain mismatch only; document) |
| R-3 | EDA NaN rates (highpass) | M per-feature | M | Active (real data not yet seen) | >50% EDA features NaN in all 3 → cardiac-only headline |
| R-4 | NK2 schema breaks if upgraded | L (pinned) | H | Controlled | Upgraded after correlation began → retire-cancel |
| R-5 | Arousal labels weak | H partial | M | Active (DEAP/MAHNOB not accessed) | >=2 datasets fail variance+split-half → single-dataset demotion |
| R-6 | ECG quality failure | M (MAHNOB) | M | Active (WESAD OK per P-2; others pending) | All 3 datasets >30% low-quality → cardiac arm dropped |
| R-7 | Operationalization not pre-registered | L (locked) | H | Controlled | Post-hoc change after seeing results → retire-cancel |
| R-8 | Competing paper mid-run | M | M | Monitor | None |
| R-9 | Correlation run before protocol lock | L | H | Controlled | Result influenced design → retire-cancel |

---

## Retire-cancel triggers (track level)

The track retires-cancelled if:

1. **Dataset access blocker (R-1 extended):** DEAP, MAHNOB-HCI, AND
   DREAMER all denied. WESAD-only is not a cross-dataset study.

2. **Protocol violation (R-7 or R-9 severe):** Feature list,
   operationalization, or datasets adjusted after seeing any feature-level
   result and the change cannot be documented as a pre-registered ablation.

3. **NK2 upgrade schema break (R-4 extreme):** Upgraded mid-run; schema
   changed; re-running from scratch infeasible (data inaccessible, time
   elapsed).

In any retire-cancel: write note in `10-pain-point/affective-state/
admission.md`, update portfolio.md, tag v5-affective-state-retired-cancelled.

A retire-cancel does NOT prevent promoting feature_stability.py to
`30-implement/shared/eval/` if built before the trigger.
