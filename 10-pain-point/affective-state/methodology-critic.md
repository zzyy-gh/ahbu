> **Spec:** `10-pain-point/affective-state/admission.md`

# Critic pass — affective-state methodology — 2026-05-02

**Artifacts reviewed:**
- `20-plan/affective-state/approach.md`
- `20-plan/affective-state/risk-register.md`
- `20-plan/affective-state/protocol-lock.md`
- `20-plan/affective-state/pilots-README.md`

**Spec consulted:**
- `10-pain-point/affective-state/admission.md`
- `10-pain-point/shared/critic-defensibility.md` §6 (advisory)
- `20-plan/README.md`
- `30-implement/compute.md`

---

## Verdict

**pass-with-fixes**

The methodology is well-designed: the feature-stability framing answers the admission record directly, pre-registration items are all present, compute is CPU-only and comfortably inside the envelope, kill criteria are mostly concrete, DEAP labels are correctly characterized as participant self-reports (not stimulus-class labels), and pilot held-out discipline is enforced. Two findings require fixes before layer-30 begins: one critical (internal inconsistency in how Spearman rho is computed across the two files) and one major (feature-count ambiguity that may invalidate the binomial-test power basis). Six minor items follow.

---

## Findings

### CRITICAL

**C-1 — Internal inconsistency: subject-pooled vs Fisher-z-of-per-subject Spearman rho**

Location: `approach.md` §Evaluation vs `protocol-lock.md` §3 and §6.

The two files prescribe different statistical procedures for computing the dataset-level Spearman rho.

- `approach.md` §Evaluation (line ~577): "the correlation is computed across all subjects (subject-pooled)."
- `approach.md` §Preprocessing / WESAD: "Per-subject Spearman rho is computed first ... dataset-level Spearman rho is the Fisher-z-transformed mean across subjects."
- `protocol-lock.md` §3 WESAD (lines 146-149): "per-subject Spearman rho ... Dataset-level rho = Fisher-z-transformed mean of per-subject rhos."
- `protocol-lock.md` §3 DEAP (lines 160-162): same Fisher-z procedure.
- `protocol-lock.md` §6 statistical test (lines 227-229): "Compute Spearman rho ... using the dataset-level aggregated (subject, window) pairs (subject-pooled correlation; see approach.md §Evaluation for rationale)."

These are two materially different estimators. Subject-pooled Spearman treats all (subject x window) pairs as i.i.d., inflating effective N and producing liberal p-values because windows from the same subject are correlated. Fisher-z of per-subject rhos respects subject independence. The two estimators can disagree in sign for features dominated by between-subject variance. Since the headline binomial test counts features that pass FDR-corrected significance within each dataset, the discrepancy can change N_reproducible materially.

**What to do:** Resolve before layer 30. Pick one procedure, write it into `protocol-lock.md` §6 with an explicit unlock note, and eliminate the contradictory passage in `approach.md` §Evaluation. The Fisher-z-of-per-subject approach is more statistically defensible (subjects are the natural exchangeable unit). The subject-pooled approach is simpler and directly analogous to a correlation study over paired observations. Either is acceptable if stated consistently in both files.

---

### MAJOR

**M-1 — Feature count ambiguity: approach.md invokes N=164 but expects approximately 100 features**

Location: `approach.md` §"The 164 features" section heading and multiple binomial-test passages.

The section heading reads "The 164 features" and multiple passages use 164 as the binomial-test denominator (lines ~279, 291, 489, 497, 686, compute-budget table). The body of the same section reveals the expected actual total is approximately 100: cardiac ~60 + EDA ~35-40. `protocol-lock.md` §2 correctly defers to the actual count from `feature_schema_v1.yaml`, but `approach.md` does not update its prose accordingly.

This matters for the defensibility-critic power assessment. At N=164: P(X<=2 | n=164, p=0.05) = 0.010 (informative null). At N=100: P(X<=2 | n=100, p=0.05) is approximately 0.119 (not significant at alpha=0.05). The "well-powered" claim in the defensibility advisory was made at N=164. If the actual schema produces approximately 100 features, the binomial null result would not be significant at the 5% threshold and the defensibility framing changes meaningfully.

Additionally, the admission record pain statement uses the phrase "2 of 164 cardiac + EDA features," which implies the source paper may have included HRV features, not EDA-only (see also m-1).

**What to do:** (a) Run pilot P-1 first to determine actual N_features from the pinned NeuroKit2 version. (b) Re-state the binomial power calculation in `approach.md` at actual N. (c) Update all "N=164" references in `approach.md` to "N=N_features (locked in `feature_schema_v1.yaml`; expected ~100; binomial test power re-stated at actual N)." `protocol-lock.md` §2 is already correct and needs no change.

---

### MINOR

**m-1 — arXiv:2508.10561 "EDA-only" claim not verified against the paper's feature table**

Location: `approach.md` §Scope, §Novelty.

The non-redundancy argument rests on arXiv:2508.10561 not having tested cardiac HRV features. This is asserted without citing a specific table or section. The admission record own pain-statement uses "2 of 164 cardiac + EDA features," which implies the paper may have included cardiac features in its denominator. If it did, the "cardiac extension" framing is not novel; the contribution would be the new dataset combination instead — a weaker but still valid claim.

**What to do:** Open arXiv:2508.10561 and check Table 1 or Methods for feature composition. Record the finding in `approach.md` §Novelty. If HRV features were included in the original 164, revise the novelty framing to the new-dataset-combination angle rather than the cardiac-extension angle.

**m-2 — WESAD arousal-label construct validity: condition label as arousal proxy is assumed, not verified in the headline**

Location: `approach.md` §Dataset / WESAD.

WESAD stress condition is mapped to "high arousal" by experimental design intent. The SAM arousal questionnaire (administered post-condition) is used only in ablation A-4. The headline labels are therefore construct-level assumptions. A meaningful fraction of subjects showing low SAM arousal under stress (a known heterogeneity in stress research) would introduce undetected label noise in the headline run.

**What to do:** No redesign needed, but add a limitation note in `approach.md` §Dataset / WESAD. Include a SAM arousal variance check in pilot P-3 to catch degenerate cases before the headline runs.

**m-3 — Median-split tie-handling rule absent from `protocol-lock.md` §3**

Location: `protocol-lock.md` §3 DEAP and MAHNOB-HCI.

`approach.md` pilot P-3 states that clips where arousal exactly equals the per-subject median are assigned label = NaN and excluded. This rule does not appear in `protocol-lock.md` §3. Tie rate is estimated at 5-10% of clips; exclusions at this rate affect the effective sample size and the correlation.

**What to do:** Add one sentence to `protocol-lock.md` §3 under both DEAP and MAHNOB-HCI: "Clips where arousal = per-subject median are assigned label = NaN and excluded from the correlation analysis." This requires an unlock note since the protocol is marked LOCKED.

**m-4 — Secondary classifier on WESAD is severely underpowered but not flagged**

Location: `approach.md` §Model family (secondary analysis).

A 70/10/20 subject-level split on WESAD (15 subjects) yields approximately 3 test subjects. LOSO AUC from 3 subjects has extreme variance; a 95% bootstrap CI will span most of the [0,1] range. The result is labeled secondary, which partially mitigates the concern, but presenting it alongside DEAP (32 subjects) and MAHNOB-HCI (27 subjects) without a caveat could mislead readers.

**What to do:** Add a note in `approach.md` that WESAD secondary classifier results are pilot-quality due to N_test approximately 3 and will be reported with a wide CI caveat or omitted from the secondary-results table with a text note.

**m-5 — R-5 kill criterion (weak arousal labels) is too permissive for a three-dataset claim**

Location: `risk-register.md` §R-5.

R-5 states kill criterion = None: weak labels produce an informative null. This is correct in principle but too permissive. If only WESAD condition labels are strong and both DEAP and MAHNOB-HCI show near-zero arousal variance, the headline effectively becomes a WESAD-centered result with two uninformative comparisons, which would be misrepresented as a three-dataset cross-dataset audit.

**What to do:** Strengthen the R-5 kill criterion to: "If two or more datasets show degenerate arousal labels (per-subject arousal std < 0.5 for DEAP and MAHNOB-HCI, confirmed at pilot P-3), the cross-dataset claim must be downgraded at headline time from three-dataset to two-dataset or one-dataset, with an unlock note documenting the reason."

**m-6 — cvxEDA / cvxpy Windows 11 + Python 3.11 installability not confirmed**

Location: `approach.md` §Preprocessing software.

cvxpy has had intermittent Windows build failures on recent Python versions. The per-window fallback to highpass handles numerical failures, but if cvxpy cannot be installed at all, the EDA primary decomposition arm cannot run. The pilots do not currently include a cvxpy installation smoke test.

**What to do:** Add to pilot P-2 success criterion: install cvxpy and confirm a single cvxEDA call completes on a synthetic EDA signal before any WESAD data processing begins. If installation fails, treat this as a whole-arm fallback trigger (use highpass as primary for all EDA windows) and update `approach.md` accordingly.

---

## What I checked

- Read all four artifacts end-to-end.
- Read the full admission record, defensibility-critic advisory §6, `20-plan/README.md`, and `30-implement/compute.md`.
- Verified spec-line presence and correctness on all four artifacts (all present; all match the CLAUDE.md spec-convention table).
- Cross-checked the three pre-registration items (feature list, dataset selection, arousal operationalization) between `approach.md` and `protocol-lock.md`. Found the subject-pooled vs Fisher-z inconsistency (C-1).
- Verified DEAP labels are correctly characterized as participant self-reports (NOT stimulus-class) in both `approach.md` §Dataset and `protocol-lock.md` §1. The real-pain-critic fix is correctly applied.
- Checked all pilot definitions for per-feature arousal correlation computation. None found; `pilots-README.md` explicitly prohibits this. Held-out discipline is intact (R-9 enforced).
- Verified compute envelope: all tasks listed as CPU-only; GPU requirement stated as zero; consistent with `30-implement/compute.md`.
- Checked kill criteria in all 9 risk-register entries for numeric or yes/no triggers. R-1, R-4, R-7, R-9 have explicit retire-cancel triggers. R-2, R-3, R-8 explicitly have no kill criterion with documented rationale. R-5 and R-6 have partial criteria; R-5 is the weakest (m-5 above).
- Checked novelty claim against admission record language: the admission record says "2 of 164 cardiac + EDA features" (not "EDA-only"), inconsistent with `approach.md` EDA-only characterization of arXiv:2508.10561 (m-1 above).
- Verified the feature-count arithmetic: cardiac ~60 + EDA ~35-40 is approximately 100, not 164. Computed binomial power at N=100: P(X<=2 | n=100, p=0.05) is approximately 0.119, not 0.010 (M-1 above).
- Verified `protocol-lock.md` §8 unlock procedure is present and complete.
- Verified `protocol-lock.md` §7 decision rule lists five sequential steps constituting a valid headline.
- Confirmed `approach.md` §Shared substrate documents reuse-scan result: shared/ does not yet exist; cross-subject-eeg is the co-first promoter candidate; promotion interface is pre-committed with defined function signatures.

## What I could not check

- Cannot verify whether arXiv:2508.10561 is EDA-only or includes HRV features without external network access to the preprint. This is the most material unverified assumption and directly bears on m-1 and M-1.
- Cannot verify exact NeuroKit2 0.2.x column names and counts for `nk.hrv_time`, `nk.hrv_frequency`, `nk.hrv_nonlinear` without running the library. The feature count uncertainty in M-1 depends on this; pilot P-1 resolves it.
- Cannot verify DEAP and MAHNOB-HCI form approval timelines (live administrative processes).
- Did not verify cvxpy installability on Python 3.11 / Windows 11 (m-6; pilot P-2 is the correct venue).
- Did not verify MAHNOB-HCI per-subject sampling rate variation (100 Hz vs 256 Hz) and the downstream effect on HRV spectral features requiring a minimum window length to resolve VLF components. Minor gap not elevated to a finding given the plan acknowledges the variation.
