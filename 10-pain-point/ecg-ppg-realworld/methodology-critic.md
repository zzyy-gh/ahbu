> **Spec:** `10-pain-point/ecg-ppg-realworld/admission.md` (spec layer 20 received) + `20-plan/ecg-ppg-realworld/{approach,risk-register,protocol-lock}.md` (artifacts under review)

# Critic pass -- ecg-ppg-realworld methodology -- 2026-05-02

## Verdict

**pass-with-fixes**

The four artifacts are coherent, honest, and substantially well-designed. Pre-registration is genuinely complete and held-out discipline is the strongest in the portfolio. Five findings require action before layer 30 proceeds: two major, three minor. No finding rises to block.

---

## Findings

### Major

**M-1 -- PPV metric definition ambiguous: coverage denominator and PPV denominator are different objects, not reconciled in the text**

Where: approach.md section Primary metric; protocol-lock.md section 4.

The protocol defines coverage as the fraction of all strat_fold 10 records retained -- the top 80% by max(P_afib, 1-P_afib). PPV is defined as TP/(TP+FP) among AFIB-predicted records in the retained set. These denominators are different.

Coverage denominator = all retained records regardless of predicted class (high-confidence AFIB-predicted + high-confidence not-AFIB-predicted).
PPV denominator = only AFIB-predicted records within the retained set.

A record with P_afib=0.05 (max-confidence=0.95, predicted not-AFIB) is retained in the top 80% and counted toward coverage, but contributes neither TP nor FP. This is correct behavior. The problem is that approach.md section Primary metric says "among the records the model CHOOSES TO PREDICT AS AFIB ... what fraction are true AFIB" -- which implies coverage and PPV share the same denominator (AFIB-predicted records only). They do not.

At roughly 14% AFIB prevalence in strat_fold 10 (~303 AFIB / ~2,179 total), the 80% retained set contains approximately 303 AFIB and 1,440 non-AFIB records. Of the non-AFIB retained records, some are predicted AFIB (false positives) and some predicted not-AFIB (true negatives). PPV is computed over TP+FP only. The two-denominator structure is not made explicit in the text.

The clinical BASEL anchor (17-21% inconclusive rate) maps correctly to the max(P_afib, 1-P_afib) abstention criterion. The operationalization is correct; the exposition needs one clarifying sentence.

What to do: in approach.md section Primary metric and protocol-lock.md section 4, add: "Coverage = fraction of all strat_fold 10 records on which the model renders any prediction (AFIB or not-AFIB); PPV is computed only over the predicted-AFIB subset of those retained records. High-confidence not-AFIB predictions are retained (counted in coverage) but do not affect PPV."

---

**M-2 -- approach.md labels strat_fold 9 as calibration-only, but protocol-lock.md also uses it for seed selection -- inconsistency on permitted uses of strat_fold 9**

Where: approach.md section Split definition; protocol-lock.md section 2; pilots-README.md section P-4.

approach.md section Split definition says: "Validation partition (calibration fitting, threshold selection): strat_fold 9." Seed selection is not listed.

protocol-lock.md section 2 says: "Three training seeds evaluated on strat_fold 9 (Brier score). The seed with the lowest strat_fold 9 Brier score is selected." This is model selection, not only calibration fitting.

P-4 also runs temperature scaling on strat_fold 9 during the pilot phase. None of this is a protocol violation -- strat_fold 9 is the designated calibration and model-selection partition, not a held-out. The issue is that the description in approach.md is incomplete relative to protocol-lock.md, which may cause a future implementer to treat the seed-selection step as an undocumented use.

What to do: (a) Update approach.md section Split definition to read "Validation partition (calibration fitting, seed selection by Brier score, threshold selection): strat_fold 9." (b) Add one sentence in pilots-README.md P-4: "Strat_fold 9 is the designated calibration and model-selection partition; it is used for both P-4 temperature scaling and the headline seed selection in protocol-lock section 2 -- this is intended design."

---

### Minor

**m-1 -- Forward reference to non-existent `20-plan/cross-subject-eeg/approach.md`**

Where: approach.md, section Promote on completion, partition.py note.

approach.md notes that cross-subject-eeg is building a subject_disjoint_split with a compatible interface and references cross-subject-eeg/approach.md section Promote. As of this critic pass, that file does not exist in the worktree.

What to do: replace the forward reference with: "When cross-subject-eeg reaches layer 20, the two partition utilities should be compared for interface compatibility and merged or aliased. Whichever track promotes first owns the initial file."

---

**m-2 -- Headline-null definition does not name the wide-CI inconclusive case**

Where: protocol-lock.md section 8.

The decision rule defines headline-positive, headline-null, and partial positive. The case p >= 0.05 AND 95% CI upper bound >= 10 pp falls through all three categories: not headline-null (CI does not rule out a large effect) and not partial positive (p >= 0.05). This is the underpowered or high-variance inconclusive case and it should be named.

What to do: add one sentence to the headline-null definition: "If p >= 0.05 and the 95% CI upper bound >= 10 pp, the result is inconclusive -- findings.md must state this explicitly and report the realized CI width and the actual AFIB N in strat_fold 10."

---

**m-3 -- Human checkpoint box unchecked despite `20-plan/ecg-ppg-realworld/` existing**

Where: 10-pain-point/ecg-ppg-realworld/admission.md, section Human checkpoint.

The second checkbox (Human approval to instantiate 20-plan/ecg-ppg-realworld/) is unchecked. The directory and all four methodology artifacts exist. Either the human approved and the box was not updated, or the directory was instantiated without the checkpoint.

What to do: confirm human approval and check the box with the date.

---

### What passes cleanly

- **Spec drift:** None. All four artifacts answer the admission record exactly. Skin-tone PPG scope explicitly dropped with correct citation to the advisory. No scope creep or premature narrowing.

- **Novelty claim:** Correctly scoped and accurately distinguished from prior work. PPV-at-fixed-alert-rate calibrated to BASEL 17-21% inconclusive rate is not the framing in Smole 2023, NCA 2024, or Barandas 2024 (which use accuracy-under-rejection or AUROC-under-rejection curves). Standard components labeled as intentionally standard in approach.md section Novelty.

- **Pre-registration completeness:** Held-out partition (PTB-XL v1.0.3 strat_fold 10) named. Primary metric (PPV at coverage=0.80) named. Statistical test (paired bootstrap n=2000, seed=42) named. H0/H1 stated. Decision rule with numeric thresholds stated (5 pp effect size minimum, CI lower bound >= 5 pp for positive). Pre-run checklist complete with seven items. Satisfies all three defensibility conditions: well-powered (N=~303 vs threshold N=87), comprehensive (full PPV-vs-coverage curve), pre-registered.

- **Compute envelope coherence:** xresnet1d50 ~1.4 M parameters at batch=32, 12-lead, 1000 samples float32 estimated ~0.8 GB VRAM. Consistent with Strodthoff et al. 2020. Temperature scaling and classical baseline CPU-only. No Kaggle fallback claimed or needed for this track. Fallback chain documented in R-8 with kill criterion if all fallbacks fail.

- **Kill criteria concrete:** All risk items have numeric or yes/no kill criteria. R-1: >5% unreadable OR >2% in strat_fold 10. R-2: combined fold 9+10 AFIB < 87 at threshold=75.0. R-3: both neural AND classical confidence-correctness AUC < 0.55. R-5: AUROC < 0.60 for both models. R-7: model selection influenced by strat_fold 10 (hard retire-cancel, no recovery). R-4, R-6, R-9, R-10 explicitly have no kill criterion with documented rationale.

- **Held-out discipline:** R-7 is a hard retire-cancel with no recovery path. P-6 correctly identifies strat_fold 10 site metadata as administrative and non-contaminating per protocol-lock section 3. P-1 explicitly loads metadata CSV only. HEADLINE_RUN guard function enforces the boundary programmatically.

- **Ablations on load-bearing choices:** Five ablations cover all load-bearing design choices: abstention vs none, temperature scaling vs no calibration, MC-Dropout vs temperature scaling, classical vs deep, AFIB likelihood threshold sensitivity. Each has a hypothesis and numeric or directional threshold. No load-bearing choice is unablated.

- **Spec line on every file:** All four files compliant with CLAUDE.md per-file spec-convention table. approach.md, risk-register.md, and protocol-lock.md point to admission.md; pilots-README.md points to approach.md.

- **Dataset licensing:** PTB-XL v1.0.3 (PhysioNet ODC-BY, open, no registration). CinC 2017 (PhysioNet CC-BY 4.0, open). No PPG corpus. No DUA required.

---

## What I checked

- Read all four methodology artifacts end to end.
- Read admission record and defensibility critic advisory (section 1).
- Read 20-plan/README.md for layer mandate and spec-convention table.
- Read 30-implement/compute.md for the binding compute constraint.
- Checked spec drift against admission record scope and advisory annotations.
- Checked pre-registration completeness against all three defensibility conditions.
- Checked compute envelope coherence for every step in approach.md section Compute budget.
- Checked kill criteria for numeric or yes/no triggers in every risk-register entry.
- Checked held-out discipline across all pilots for which folds they access.
- Checked ablation coverage against all load-bearing design choices.
- Checked novelty claim against the three cited prior works.
- Checked spec line presence and correctness on all four files against CLAUDE.md table.
- Checked protocol-lock.md section 8 decision rule for completeness of cases.
- Checked PPV metric definition for internal consistency between approach.md and protocol-lock.md.
- Checked pilot P-4 for calibration partition documentation consistency.
- Checked forward references to other track artifacts; confirmed `20-plan/cross-subject-eeg/approach.md` does not exist.
- Checked admission.md human checkpoint status.

## What I could not check

- Did not empirically query PTB-XL to verify ~303 AFIB in strat_fold 10. Pilot P-1 is the empirical check.
- Did not independently fetch Smole 2023, NCA 2024, or Barandas 2024 to verify novelty claim. Claim is consistent with the papers as described in the artifacts.
- Did not verify the xresnet1d50 VRAM estimate empirically. Pilot P-3 is the empirical check.
- Did not verify the BASEL 17-21% inconclusive figure against Mannhart et al. 2023 directly.
- Did not check NeuroKit2 >= 0.2.9 compatibility with Python 3.11.2 on Windows 11. No known incompatibility but a practical week-1 risk.
- Did not survey conformal-prediction-on-ECG literature for papers after the gap-closing pass. Relevant only to the exploratory arm.