> **Spec:** `20-plan/affective-state/{approach,risk-register,protocol-lock}.md` (under review) + `10-pain-point/affective-state/admission.md` (the spec layer 20 received)

# Critic pass — affective-state methodology (v2, re-lock review) — 2026-05-03

## Verdict

pass-with-fixes

---

## Findings

### Critical

None.

### Major

**M-1 — Power at N=126 is borderline and the protocol acknowledges it without resolving it**

Location: `protocol-lock.md` §2D and §5; `unlock-note-2026-05-03.md` §Path X rationale.

The Poisson approximation in `protocol-lock.md` §2D states P(X<=2 | n=126, p=0.05) ≈ 0.050 "at the boundary." The unlock note explicitly designed up to N=126 to restore adequate power, but 0.050 is not a comfortable margin — it is exactly at the threshold, and the approximation used (Poisson) is an approximation. The exact binomial value for P(X<=2 | n=126, p=0.05) should be computed and stated explicitly rather than approximated. The Poisson lambda = n*p = 6.3 approximation is valid but gives P ≈ 0.050; the exact binomial may be slightly above or below. If it is above 0.050 the protocol's own adequacy claim is false before any data is seen.

More concretely: the protocol states "if the final YAML count is < 120, the binomial test is under-powered and the CI-led headline is the sole primary presentation." This fallback is acceptable, but the trigger should be stated in terms of the exact binomial threshold, not a round-number approximation. At N=125 the exact P(X<=2 | p=0.05) is different from N=126; the protocol should cite the minimum N at which the exact binomial P(X<=2) < 0.05.

What to do: replace the Poisson approximation with an exact binomial calculation (scipy.stats.binom.cdf(2, 126, 0.05) — run it once). State the exact value and the minimum N that satisfies P<0.05 exactly. If exact P(X<=2 | n=126) >= 0.05, the fallback trigger should move to N >= whichever value passes. This is a one-line code check; it does not require re-locking unless the answer changes the fallback threshold materially.

**M-2 — P-2 EDA success claim is incomplete: `eda_scl_mean` is null in the pass record**

Location: `30-implement/affective-state/runs/pilot_p2_1777731646.json` (the "pass" run); `risk-register.md` R-2; `approach.md` §EDA preprocessing pipeline.

The approach.md and risk-register.md both cite P-2 as confirming "the highpass pipeline is fully functional." However `pilot_p2_1777731646.json` does not contain `eda_scl_mean`; the field is absent from the pass record (it was null in the fail record and simply not present in the pass record). The success criterion in `pilots-README.md` P-2 is: "EDA pipeline: cvxEDA completes without numerical error; SCL_mean is a positive finite float." The pass run confirms `eda_pass: true` and lists 6 EDA columns present, but the SCL_mean numeric value is not recorded. The confirmation that "highpass pipeline is fully functional" therefore rests on `eda_pass: true` (a boolean logged by the pilot script) without the numeric sanity check being surfaced in the JSON. This is a bookkeeping gap, not necessarily a pipeline failure — the pilot passed and the columns are confirmed present. But the cited pilot does not provide full traceability on the EDA numeric output.

What to do: note this gap in the limitations or results.md when it is written; do not treat `eda_pass: true` as equivalent to a verified numeric output. If time permits, re-run the P-2 EDA section with SCL_mean logged. This is minor if the EDA processing runs cleanly on WESAD at full scale, but should be documented honestly.

**M-3 — "Band-power features were already pre-registered" claim in unlock-note is overstated**

Location: `unlock-note-2026-05-03.md` §Path X rationale, point 1.

The unlock note argues that the band-power features "were ALREADY PRE-REGISTERED in protocol-lock.md §2, bullet 3" and therefore adding them "is not a protocol change." This argument is used to justify the full 34-feature supplementary EDA expansion. However, the original protocol-lock.md §2 bullet 3 cited in the unlock note is not visible in the current re-locked document — only the re-locked version is present. The critic cannot verify that bullet 3 of the original 2026-05-02 lock actually contained the enumerated band-power feature list. The unlock note self-certifies the pre-registration retrospectively. The SCL and SCR features (26 of 34 supplementary EDA features) are explicitly acknowledged as "additions that require explicit lock" in the unlock note's own critic note section.

This means the supplementary EDA features are a genuine post-pilot addition to the feature set — which is acceptable given no correlation has been computed — but the framing that it was "completing the protocol as written" is partially inaccurate and should not be used to minimize the significance of the re-lock. The re-lock is appropriate and necessary; understating it introduces a future defensibility risk.

What to do: in `approach.md` or `protocol-lock.md`, replace the claim that supplementary EDA features were pre-registered with an honest statement: "Band-power features were described in the original §2; SCL/SCR/derived features were designed before the lock but not enumerated; all 40 EDA features are now explicitly locked in this re-locked protocol (2026-05-03), before any correlation analysis." The re-lock is sufficient. The retrospective pre-registration claim is not needed.

### Minor

**m-1 — arXiv:2508.10561 HRV inclusion still unverified: carried forward but not documented as a formal open item in the re-locked files**

Location: `approach.md` §Scope statement (arXiv verification note); `risk-register.md` R-2; `feature_schema_v1.yaml` field `arxiv_2508_10561_includes_hrv_FILL_MANUALLY`.

The YAML field remains `[unverified]`. The approach.md carries a note, and R-2 lists it as a residual mitigation item. This is acceptable — it does not stop the track. However the open item is not listed in any formal checklist; it could silently persist into the results phase. Minor because it only affects the novelty framing, not the scientific validity of the headline.

What to do: add this to admission.md §Open items or a new open-items section in approach.md with a concrete trigger ("verify before results.md is written, not merely before correlation runs").

**m-2 — P-3 DEAP portion was skipped; the claim "P-3 WESAD PASS" is accurate but the admission record's arousal-label concern (R-5) for DEAP is still fully open**

Location: `30-implement/affective-state/runs/pilot_p3_1777731781.json` (deap status: skipped); `risk-register.md` R-5.

This is not a design flaw — DEAP access is pending. But approach.md and the unlock note cite "P-3 PASS" in contexts where the reader might infer it covers both WESAD and DEAP. The P-3 pass covers WESAD only; the DEAP label-quality check has not run. R-5 correctly marks this as "Active (DEAP/MAHNOB not accessed)." The risk is registered. This is a communication accuracy issue.

What to do: wherever "P-3 PASS" is cited, ensure it reads "P-3 PASS (WESAD only; DEAP and MAHNOB-HCI pending access)."

**m-3 — P-4 (cvxEDA vs highpass comparison) and P-5 (DREAMER access probe) are not marked retired in pilots-README.md**

Location: `20-plan/affective-state/pilots-README.md` P-4 and P-5; `unlock-note-2026-05-03.md`.

P-4 is now irrelevant (cvxEDA is unavailable; the comparison cannot run). P-5 is a contingency probe that should run in parallel with form submissions. Neither pilot is marked with a status update reflecting the 2026-05-03 unlock. A reader scanning pilots-README.md cannot tell which pilots are still active and which are superseded.

What to do: add result annotations to P-4 ("Superseded by unlock-note-2026-05-03.md: cvxEDA unavailable on project environment; comparison cannot run. Replaced by A-2' in approach.md.") and confirm P-5 status (either "submitted alongside DEAP/MAHNOB forms" or "pending").

**m-4 — Protocol-lock §2D total count says 126 but protocol header text says "~128-132"**

Location: `protocol-lock.md` header (line 19) vs §2D table (line 218).

The header says "Total N_features revised from 92 to ~128-132, exact count locked in feature_schema_v2.yaml." The §2D table sums to exactly 126 and is stated as "N_features = 126 (pre-committed)." These are inconsistent. The header range (~128-132) is from an earlier draft that the re-lock superseded. The pre-committed count is 126.

What to do: correct the header text to "~126, exact count locked in feature_schema_v2.yaml" to match §2D.

**m-5 — Spec convention not fully adhered to in unlock-note-2026-05-03.md**

Location: `unlock-note-2026-05-03.md` line 1.

The spec line reads `> **Spec:** 10-pain-point/affective-state/admission.md` — this points to the admission record. By CLAUDE.md convention the unlock note is an artifact that serves the approach/protocol-lock files it modifies; the spec should point to those (e.g., `20-plan/affective-state/protocol-lock.md` as the document being unlocked). This is a minor traceability issue with no scientific consequence.

What to do: update the spec line to `> **Spec:** 20-plan/affective-state/protocol-lock.md` (the document being unlocked).

---

## What I checked

- Unlock trigger: both triggering facts (N_features = 92 from P-1 JSON; cvxEDA failure from P-2 JSON) are independently evidenced in the pilot run files. The unlock is justified.
- Held-out partition: pre-registration statement (protocol-lock §0) asserts no correlation table has been computed and DEAP/MAHNOB-HCI have not been downloaded. P-3 confirms DEAP was not accessed. P-1, P-2 use synthetic data or a single WESAD subject without correlation. P-6 uses synthetic data. No evidence of held-out contamination.
- Feature list frozen: §2 of the re-locked protocol-lock.md enumerates all 126 features by name (86 cardiac confirmed by P-1 YAML; 40 EDA enumerated in §2B and §2C). The exact count is explicitly pre-committed. The YAML count governs if it differs.
- Fisher-z primary analysis: the procedure (per-subject Spearman → Fisher-z → t-test → FDR-BH) is standard psychophysiology methodology. Per-subject Fisher-z is appropriate for aggregating within-subject correlations across subjects; the t-test on Fisher-z values is well-known and correctly specified. The permutation fallback for N_subjects < 15 (WESAD has exactly 15; DEAP has 32; MAHNOB-HCI has 27) is a sensible safeguard. The statistical approach is sound.
- CI-led headline consistency: §5 explicitly demotes the binomial test to "confirmatory" and makes the 95% Clopper-Pearson CI the primary presentation. This is correctly aligned with the borderline power at N=126. The framing is honest and consistent with the pre-registration.
- Binomial test framing: stated as "two-sided, secondary confirmation" with the null p0=0.05 matching the FDR threshold used to define reproducibility. This is defensible — the null hypothesis is "features reproduce at the base FDR rate of 5%," which is the appropriate null for a reproducibility audit. The two-sided test is conservative and correct.
- Pilot evidence supports design choices: P-1 confirms the 86-feature cardiac schema. P-2 confirms cvxEDA failure and highpass pipeline functionality for ECG and EDA columns. P-3 confirms WESAD window counts (all 15 subjects pass the >=10 windows threshold). P-6 confirms the `cross_dataset_correlation` function logic on synthetic data. No pilot is being used to support a claim beyond its scope.
- Risk-register consistency: R-2 and R-3 are correctly updated to reflect the pilot findings. The cvxEDA risk is retired and replaced by the EDA NaN rate risk (R-3 revised). R-1 (dataset access), R-5 (arousal labels), R-6 (ECG quality) are appropriately marked active with quantified kill criteria. No stale v1 entries detected.
- Compute consistency: the compute table in approach.md is CPU-only; the affective-state track does not use GPU at any stage. The compute table does not include any GPU line. This is consistent with the 4 GB VRAM envelope (not binding for this track).
- Spec convention: approach.md, protocol-lock.md, risk-register.md all carry `> **Spec:** 10-pain-point/affective-state/admission.md`. Correct.
- Secondary classifier scope: correctly labeled secondary throughout; uses dev split only; does not feed the headline. No conflation with the headline analysis.
- Failure modes: R-5 (weak labels), R-3 (EDA NaN rates), R-6 (ECG quality) all have numeric kill criteria and demote-not-retire paths. Ablation A-2' quantifies the NaN risk before the conclusion is written. Failure modes are characterized, not buried.

## What I could not check

- Exact binomial value for P(X<=2 | n=126, p=0.05): I did not run scipy.stats.binom.cdf(2, 126, 0.05). The Poisson approximation in the protocol may be slightly over or under the exact value. This is M-1 above.
- Original 2026-05-02 protocol-lock.md: the current file shows only the re-locked version. I cannot independently verify whether "band-power features were pre-registered in the original §2 bullet 3" as claimed in the unlock note. The git history would resolve this; I did not run a git diff.
- arXiv:2508.10561 Methods section: I could not verify whether the paper includes HRV features. The FILL_MANUALLY flag in feature_schema_v1.yaml is unresolved. This is m-1 above.
- DEAP and MAHNOB-HCI data: not downloaded; label quality and ECG/EDA signal quality for these datasets are entirely unverified. R-5 and R-6 correctly characterize this as open.
- NeuroKit2 0.2.13 behavior on 60-second windows with short RR series (e.g., DEAP at 128 Hz may have low beat counts if clips are exactly 60 s): the HRV_ULF and very-long-term HRV features may produce NaN on short windows. This is a potential source of cardiac feature NaN rates not covered by R-3 (which focuses on EDA). Not a block — results.md will surface it — but worth tracking.
- feature_schema_v2.yaml: does not exist yet (will be created at first extraction on real data). The exact final N cannot be confirmed until then.
