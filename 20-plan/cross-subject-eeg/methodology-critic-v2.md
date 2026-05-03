> **Spec:** `20-plan/cross-subject-eeg/{approach,risk-register,protocol-lock,unlock-note-2026-05-03}.md` (under review) + `10-pain-point/cross-subject-eeg/admission.md` (the spec layer 20 received)

# Critic pass -- cross-subject-eeg methodology v2 (unlock + revised protocol) -- 2026-05-03

## Verdict

**pass-with-fixes**

The unlock is legitimate: the held-out split was not touched before the protocol change, the substitution path was pre-specified in R-2 and protocol-lock section 4, and the split-arm design is an honest response to the contamination finding. Two major findings and one minor finding must be fixed before re-locking. None are fatal.

---

## Findings

### Critical

None.

### Major

**M-1 -- risk-register.md R-5 mitigation step 2 names Cho2017 as a dataset that can be added to the MOABB dev set, but Cho2017 is now the FM arm test set.**

Location: `risk-register.md` R-5 Mitigation, step 2.

The text reads: if N < 62, add Cho2017 (52 subjects) to the MOABB dev set and expand the dev-to-test ratio so the combined test set clears N=62.

This is a copy-paste leftover from v1. In v2, Cho2017 is frozen as the FM arm held-out test dataset (protocol-lock section 3, approach.md Dataset section). Using Cho2017 as dev would violate the protocol immediately. As written, R-5 tells the practitioner to resolve the power problem by doing exactly the thing R-9 would retire-cancel the track for (pre-test-set access). The mitigation step is wrong and dangerous -- it points at the wrong dataset.

Fix: replace R-5 mitigation step 2 with a corrected path. If FM arm effective N falls below 62 after artifact rejection, the permissible response is: add Lee2019 test subjects or another audited-clean MOABB MI dataset to the FM arm test set, provided no test data has been touched and the change is documented as a pre-experiment design adjustment before any test data is accessed. Cho2017 may not be added to dev.

**M-2 -- approach.md compute budget table names PhysionetMI as the target of LaBraM feature extraction; LaBraM may not run on PhysionetMI.**

Location: `approach.md` compute budget table, row: LaBraM feature extraction (PhysionetMI) | GTX 1650 | 1-2 hr.

Protocol-lock section 3 and approach.md Held-out partition both state explicitly that LaBraM is NOT evaluated on PhysionetMI (contamination). The compute table was not updated to reflect the v2 substitution. The headline FM feature extraction runs on Cho2017 (52 subjects), not PhysionetMI (109 subjects). The time estimate is off by roughly 2x (109 vs 52 subjects). A future auditor or replicator would see a direct contradiction between the data-flow narrative and the compute table.

Fix: update the row to: LaBraM feature extraction (Cho2017, 52 subjects) | GTX 1650 | ~30-60 min, and confirm the time estimate.

### Minor

**m-1 -- Unlock note section 3 power claim is internally inconsistent.**

Location: `unlock-note-2026-05-03.md` section 3, first bullet.

The text states N=52 is adequate for Wilcoxon at the effect sizes expected, without qualification, but the same paragraph parenthetical correctly acknowledges Cho2017 is below the N=62 illiteracy-rate threshold. The note simultaneously asserts N=52 is adequate (unqualified) and that illiteracy-rate precision is reduced (qualified). The Wilcoxon FM-vs-MDM comparison does have adequate power at N=52 for moderate effect sizes (paired signed-rank; N=35 suffices for d=0.5, alpha=0.05 corrected, power=0.80). But the note does not separate the two sub-claims, leaving the reader to infer which is which. Risk-register R-5 correctly separates them, so this is a documentation inconsistency, not a substantive design error.

Fix: rewrite the parenthetical to separate the two claims: N=52 is adequate for the FM-vs-MDM Wilcoxon comparison (paired test, power sufficient at moderate effect sizes); it falls below the N=62 threshold for the illiteracy-rate characterization, which is reported with reduced-precision caveat per R-5.

---

## Specific checks performed (as requested)

**Check 1 -- Cho2017 clean in labram_pretrain_datasets.txt (leakage_audit logic):**

`30-implement/cross-subject-eeg/code/headline/labram_pretrain_datasets.txt` contains exactly 20 entries, consistent with `leakage_audit_result.json` n_pretrain=20. Grepped for all plausible aliases for Cho2017: cho, biosemi, gigadb, 2017, left.hand, right.hand. Zero matches. The entry PhysioNet-Motor-Movement is present (confirming PhysionetMI). Cho2017 is NOT in the pretrain list under any variant checkable from this file. The contamination status is correctly stated.

Residual caveat (cannot be closed from this file alone): the pretrain list is a best-effort transcription from arXiv:2405.18765 section 3.1 HTML. The file header itself notes this. If the LaBraM authors used Cho2017 under an informal name not captured in the transcription, the clean verdict would be wrong. The risk register flags this as a lower-bound concern in R-2 residual risk. The caveat is already stated and adequate.

**Check 2 -- Cross-arm absolute-accuracy comparison prohibition:**

`protocol-lock.md` section 3 FM arm states: Cross-arm comparisons of absolute accuracy are NOT made; each arm is interpreted on its own test set. Section 5 Reporting note repeats: cross-arm accuracy comparisons are NOT made. The prohibition is explicit, stated twice, in the frozen pre-registration document. Satisfied.

**Check 3 -- Power on Cho2017 (52 subjects, 2-class MI) for illiteracy-rate analysis:**

The N=62 threshold in R-5 is the original design threshold for the illiteracy-rate characterization, derived from the PhysionetMI 4-class context. Cho2017 is 2-class MI, chance at 50%. At N=52 with artifact rejection retaining >80% of subjects (expected per R-5), effective N is approximately 42-52. For the Wilcoxon FM-vs-MDM paired comparison, N=52 is comfortably powered at moderate effect sizes (paired signed-rank; N=35 suffices for d=0.5, alpha=0.05 corrected, power=0.80). For the illiteracy-rate proportion test, N=52 gives a 95% CI half-width of approximately +-14 percentage points (Wilson interval), vs +-12.5 pp at N=62. The precision difference is real but not dramatic. The protocol correctly documents this as a limitation and does not suppress it. The power situation is adequately handled provided the limitation appears in results.md, which is pre-specified in R-5 and protocol-lock section 1(c).

**Check 4 -- Spec line present in all four artifacts:**

All four artifacts carry the spec line pointing to 10-pain-point/cross-subject-eeg/admission.md as their first line. Satisfied.

**Check 5 -- Touched-once discipline preserved across both test sets:**

`protocol-lock.md` section 3 defines the single authorized evaluation run per arm. Pre-run checklist, partition audit, and leakage audit result are all required preconditions before either arm test split is accessed. The unlock note section 6 confirms the held-out split has not been touched as of 2026-05-03. What counts as touching the held-out split is defined operationally in section 3. R-9 provides a retire-cancel kill criterion if this is violated. Discipline is structurally sound.

---

## What I checked

- `leakage_audit_result.json`: n_pretrain=20 consistent with 20-line labram_pretrain_datasets.txt; PhysionetMI flagged contaminated; Cho2017 absent from corpus file under all checked aliases.
- `labram_pretrain_datasets.txt` (full): grepped for cho, biosemi, gigadb, 2017, left.hand, right.hand -- zero matches; PhysioNet-Motor-Movement present confirming PhysionetMI match.
- `unlock-note-2026-05-03.md`: trigger, corpus re-examination table, path choice rationale, change table, what-does-not-change list, critic-pass requirement.
- `protocol-lock.md` v2: pre-registration statement, five-part program, FM checkpoint, held-out partition definition (split-arm design), audit status, primary metrics, statistical test, decision rule, unlock procedure, unlock history.
- `approach.md` v2: scope, shared substrate, dataset section, preprocessing, model family, evaluation protocol, ablations, uncertainty reporting, compute budget, novelty notes.
- `risk-register.md` v2: all 10 risks and retire-cancel triggers; focus on R-2 (resolved), R-5 (source of M-1), R-9 (test-split discipline).
- `admission.md`: spec, advisory annotations, human checkpoint status.
- Cross-arm prohibition: checked section 3 and section 5 of protocol-lock -- prohibition stated explicitly twice.
- Spec line: all four artifacts carry the correct spec line.
- Touch-once: pre-run checklist preconditions, R-9 kill criterion, section 8 unlock procedure.
- Compute table in approach.md: found M-2.
- R-5 mitigation step 2: found M-1.
- Consistency of power claim in unlock note vs risk register: found m-1.
- Prior critic pass (methodology-critic.md v1): confirmed M-2 (dev dataset leakage audit gap) and m-4 (Ablation 2 elevation) from that pass are resolved in v2.

## What I could not check

- Whether the LaBraM authors used Cho2017 under an informal or translated name not captured in the best-effort pretrain transcription. Known lower-bound risk; already documented in R-2 residual risk.
- Whether the LaBraM arXiv:2405.18765 corpus list has been updated since initial posting via errata or supplementary appendix. Audit result is valid only against the version transcribed when the audit was run.
- Cho2017 and Lee2019 recording hardware confirmation against MOABB documentation (m-2 from prior pass: dev_dataset_selection.txt is the designated resolution artifact, not yet created).
- Whether PhysionetMI artifact rejection retains substantially all 109 subjects (pilot P-2 from prior pass, not yet run).
- Kaggle account and T4 quota (M-1 from prior pass, not yet verified at environment setup).