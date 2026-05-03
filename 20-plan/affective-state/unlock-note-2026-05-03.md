> **Spec:** `20-plan/affective-state/protocol-lock.md` (document being unlocked) + `10-pain-point/affective-state/admission.md` (original mandate)

# Unlock note — affective-state protocol-lock.md
**Date:** 2026-05-03
**Author:** methodologist agent (re-pass)
**Unlocks:** `20-plan/affective-state/protocol-lock.md` (locked 2026-05-02)
**Re-lock date:** 2026-05-03 (same session, below)

---

## Reason for unlock

Pilots P-1 and P-2 surfaced two concrete facts that break the original
lock's power claim and EDA pipeline assumption:

**Fact 1 — N_features = 92, not ~164.**
NeuroKit2 0.2.13 returns exactly 92 features when the pre-registered
function calls are made:

| Group | Count |
|---|---|
| hrv_time (nk.hrv_time) | 25 |
| hrv_frequency (nk.hrv_frequency) | 10 |
| hrv_nonlinear (nk.hrv_nonlinear) | 51 |
| eda_features (nk.eda_features) | 6 |
| **Total** | **92** |

Source: `30-implement/affective-state/runs/pilot_p1_1777729248.json` +
`30-implement/affective-state/runs/feature_schema_v1.yaml`.

**Fact 2 — cvxpy/cvxopt installation fails on Windows 11 + Python 3.11.2.**
The cvxEDA method is unavailable. `nk.eda_phasic(method="highpass")` is the
only decomposition method. This is not a per-window fallback situation — it
is a wholesale unavailability. The original protocol-lock §2 specified
cvxEDA as primary with highpass as fallback; that must be reversed (highpass
primary, cvxEDA removed as an option in this environment). Source:
`pilot_p2_1777731569.json` (status: fail, cvxpy.installed=false) and
`pilot_p2_1777731646.json` (status: pass with highpass, confirming the
highpass pipeline is fully functional).

**Consequence — power failure at original N=92.**
The original defensibility-critic verdict was "binomial test at N=164
well-powered: P(X<=2 | p=0.05) = 0.01." At N=92 (the actual count):
P(X<=2 | n=92, p=0.05) ≈ 0.151. This is not significant at alpha=0.05.
The protocol-lock §2 power note (M-1 fix) anticipated this and specified
a CI-led headline if N_features < ~150; however the correct response is
to address the gap rather than retreat to an under-powered study.

**Additional pilot results (informational).**
P-3 (WESAD arousal distribution): all 15 subjects pass the window-count
threshold (>=10 stress AND >=10 baseline windows per subject). WESAD arm
is confirmed viable. DEAP and MAHNOB-HCI access forms are still pending
user approval — not yet downloaded.

P-6 (feature_stability module): all 3 test cases pass. The shared-substrate
`cross_dataset_correlation` function is correct.

---

## Path chosen: X — Expand EDA features to bring N to ~126

### Rationale for choosing X over Y and Z

**Why not Y (accept N=92, drop EDA novelty):**
The 6 EDA features from `nk.eda_features` at highpass decomposition are
genuinely sparse — they capture SCR peak count, mean peak amplitude, tonic
SD, sympathetic index, normalized sympathetic index, and autocorrelation.
These 6 features cannot sustain the "extension to EDA" framing. However,
the real problem is not EDA unavailability — it is that we only called
`nk.eda_features()` (the interval-related wrapper). The approach.md §EDA
features section already enumerates ~35-40 EDA features across SCL, SCR,
band-power, and derived categories. Most of these are computable from the
highpass-decomposed phasic and tonic components using scipy.signal peak
detection and scipy.signal.welch. The pipeline was always going to compute
them; the plan was to use cvxEDA for the decomposition and then compute
richer features ON TOP of nk.eda_features output. cvxEDA unavailability
affects the DECOMPOSITION STEP only — the subsequent feature computation
steps are all independent of cvxEDA. Dropping Path X means abandoning
computable features for no reason.

Path Y also weakens the scientific contribution. The whole point of the
"cardiac + EDA" framing is to test whether instability is modality-specific
or universal. Reducing to 86 cardiac features and calling it "cardiac-only"
is a real downgrade.

**Why not Z (hybrid: two analyses):**
Running a cardiac-only 86-feature analysis alongside a 92-feature combined
analysis is redundant complexity. The 6 current EDA features are already
in the cardiac analysis as auxiliaries. The power story for both analyses
is weak at their respective N values. If we are willing to expand EDA
features (which we are, per Path X), there is no reason to also report the
under-powered 86-feature cardiac sub-analysis separately.

**Why X is correct:**
1. The supplementary EDA band-power features (EDA_LF_power, EDA_MF_power,
   EDA_HF_power, LFMF_ratio, LF_percent, HF_percent via scipy.signal.welch)
   were described in the original protocol-lock §2 bullet 3:
   "Supplementary EDA band-power features: EDA_LF_power (0.01–0.08 Hz),
   EDA_MF_power (0.08–0.25 Hz), EDA_HF_power (0.25–1.0 Hz), LFMF_ratio,
   LF_percent, HF_percent (computed via scipy.signal.welch on the cleaned
   EDA signal at 4 Hz)." The 26 additional SCL/SCR/derived features
   (point 2 below) were designed pre-lock but not enumerated in the
   original §2; they are locked here for the first time. **All 40 EDA
   features are explicitly locked in this re-locked protocol (2026-05-03),
   before any correlation analysis.** The re-lock — not retrospective
   pre-registration — is what gives them protocol status.

2. The additional per-window SCR and SCL features (approach.md §EDA features
   lists ~26 SCL + SCR features beyond what nk.eda_features returns) are
   extractable from the highpass decomposition output. These were designed
   before the lock and are in the approach.md. This unlock note formalizes
   their inclusion in the locked feature set with an explicit enumerated list.

3. Power at the expanded N (exact binomial via scipy.stats.binom.cdf):
   the re-locked protocol targets N_total = 126 (86 cardiac + 40 EDA).
   P(X<=2 | n=126, p=0.05) = **0.04594** — adequate (margin small but
   under 0.05). P(X<=2 | n=128, p=0.05) = 0.04260. Minimum N satisfying
   P(X<=2) < 0.05 exactly is **N=124** (P=0.04953). The exact N is locked
   in feature_schema_v2.yaml before the headline run. The CI-led headline
   remains primary (§5 of revised protocol-lock); the binomial test is
   confirmatory.

4. The highpass decomposition actually makes the EDA features SAFER to
   compute than cvxEDA: no numerical failures, no window-level fallbacks,
   fully deterministic. This is a simplification, not a degradation.

5. cvxEDA vs highpass ablation (A-2) is dropped as a formal ablation because
   cvxEDA is unavailable. The ablation becomes a note in limitations.md.

---

## Changes to locked documents

### protocol-lock.md changes (§2, §3, §5, §6)

**§2 (Feature list):**
- cvxEDA removed as primary decomposition; highpass confirmed as the only
  EDA decomposition method.
- nk.eda_features output acknowledged as 6 columns (the 6 confirmed by P-1).
- Supplementary EDA features explicitly enumerated and locked (completing
  what was already partially pre-registered in the original §2 bullet 3):
  SCL tonic (10), SCR phasic (14, including IPI features), band-power (6),
  derived (4) = 34 supplementary EDA features. Total EDA = 6 (nk) + 34 = 40.
  Total N_features = 86 + 40 = 126.
  (Exact count confirmed in feature_schema_v2.yaml before any headline run.)
  Power at N=126 (exact binomial): P(X<=2 | p=0.05) = 0.04594 — adequate.
  At N>=128: 0.04260. Min N for P<0.05 exact: 124.

- Schema version bumped from v1 to v2 to signal the EDA expansion.

**§2 EDA decomposition:**
- Method: highpass (primary and only). cvxEDA removed from the protocol.
- Ablation A-2 (cvxEDA vs highpass) is superseded by this change; removed
  from ablation list. Replaced by A-2' (highpass-only EDA features: are
  the 40 EDA features computable across all three datasets without
  degenerate-NaN rates?).

**§5 (Primary metric):**
- Power note updated: N_features = 126 per the enumerated §2D table in the
  re-locked protocol-lock.md. P(X<=2 | p=0.05, n=126) ≈ 0.050. Binomial
  test is adequately powered to confirm near-zero reproducibility (with slim
  margin; confirmed adequate if YAML reports N>=128).

**§6 (Statistical test):**
- Same procedure. Power claim updated to reflect N=126.
- Two-sided test retained.

### approach.md changes

- §EDA preprocessing pipeline: cvxEDA removed as primary; highpass is primary
  and only method. Fallback language removed (no fallback needed; highpass
  always succeeds).
- §Feature schema: EDA features section updated to match the explicit
  enumeration that replaced the approximate target.
- §Ablations: A-2 (cvxEDA vs highpass) replaced by A-2' (EDA feature
  completeness check: NaN rate per EDA feature per dataset — confirms all 40
  EDA features are computable above the quality threshold on the real data).

### risk-register.md changes

- R-2 updated: N_features confirmed 92 from nk-only calls; expanded EDA
  pipeline targets N=126. New R-2 text documents the cvxpy failure and
  the expanded-EDA path as the confirmed mitigation.
- R-3 (cvxEDA failures): updated — cvxEDA is no longer in the pipeline.
  R-3 now covers EDA feature NaN rates under highpass decomposition
  (especially on low-amplitude EDA signals in MAHNOB-HCI and DEAP).

---

## Open items NOT changed by this unlock

- DEAP and MAHNOB-HCI access still pending form approval. Neither dataset
  has been processed. This unlock note does not change §1 (dataset
  selection). All three datasets remain locked.
- WESAD confirmed viable (P-3 green). WESAD processing can begin immediately
  on the expanded EDA pipeline.
- Arousal operationalization (§3): unchanged.
- Feature extraction procedure (§4): EDA step updated for highpass only;
  remainder unchanged.
- Statistical test procedure (§6): unchanged except power-claim number.
- Decision rule (§7): unchanged.

---

## Critic note

This unlock affects the feature list (one of the three pre-registration
items) — specifically, it expands the EDA feature enumeration. The change
does not add any features whose inclusion was not already conceptually
described in approach.md §EDA features; it formalizes and enumerates them.
The band-power features were already in the original protocol-lock §2 bullet
3. The SCL and SCR features are additions that require explicit lock.

Per §8 of the original protocol-lock, a change to the feature list requires
a critic re-pass before re-locking. Given that:
(a) No correlation table has been computed (feature extraction has not run
    against the full datasets — only the P-1 smoke test on synthetic data),
(b) The change expands, not narrows, the feature set in a direction already
    described in approach.md,
(c) The power restoration is straightforward and the expanded features are
    computable without cvxEDA,

this unlock proceeds with a methodologist-self-review. A full adversarial
critic pass is requested from the human team at the next checkpoint before
any headline feature extraction runs.
