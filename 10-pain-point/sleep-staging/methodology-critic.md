> **Spec:** 10-pain-point/sleep-staging/admission.md

# Critic pass - sleep-staging methodology (layer 20 to layer 30) - 2026-05-02

## Verdict

pass-with-fixes

The methodology is substantially sound. The primary arm (scope b, HRV-only RF on HMC PSG) is well-designed, honestly pre-registered, and the held-out discipline is among the clearest reviewed at this stage. Three issues require fixes before layer-30 work begins; none are fatal to the track.

---

## Findings

### CRITICAL

None.

---

### MAJOR

**1. (major) pilots-README.md spec pointer is wrong.**
Location: pilots-README.md line 1.
The file opens with spec pointer 20-plan/sleep-staging/approach.md. Per CLAUDE.md every layer-20 output file must open with spec 10-pain-point/sleep-staging/admission.md. One layer-20 artifact cannot be the spec of another layer-20 artifact without an explicit sub-layering decision (none exists here).
Fix: change line 1 of pilots-README.md to the admission record path.

**2. (major) HMC PSG dataset identity mismatch.**
Location: approach.md lines 222-235, protocol-lock.md lines 88-118, risk-register.md R-2, pilots-README.md P-1.
approach.md names the primary dataset HMC PSG and defines it as the PhysioNet 2018 CinC Challenge dataset (challenge-2018/1.0.0). These are different datasets. HMC PSG (Hassan et al.) is at physionet.org/content/hmc-sleep-staging/1.0.0/ (115 subjects, 2023 release, DOI 10.13026/533e-0n28). The PhysioNet 2018 CinC Challenge (challenge-2018/1.0.0) concerns apnea/arousal detection (994 training records; staging is not the primary annotation). The 151-subject figure does not match the CinC 2018 training count of 994. This is a correctness issue, not a naming issue: if the intended dataset is HMC Sleep Staging (Hassan 2023), update all four methodology files with the correct URL, DOI, and subject count. If the intended dataset is genuinely the CinC 2018 set, confirm that stage labels for exactly 151 subjects exist in that release and resolve the 994-vs-151 discrepancy before any implementation begins.

**3. (major) Power analysis inconsistency makes the N=76 adequacy claim unsupported.**
Location: approach.md lines 253-259 and 529-534, risk-register.md R-3 lines 127-134.
approach.md states N required = 105 for the 17 pp gap at 80% power, then immediately claims N=76 test subjects is adequate for that same claim. N=105 is not met by N=76. The R-3 kill criterion only triggers at N=40, far below either figure. The methodology must either: (a) show the arithmetic that justifies N=76 being adequate for a paired Wilcoxon (required N for a paired test may differ from a two-sample proportion test; state and cite explicitly), or (b) acknowledge the design is modestly underpowered at N=76 and adjust the headline claim framing, CI-width criterion, and R-3 kill threshold accordingly.

---

### MINOR

**4. (minor) NSRR DUA kill-criterion clock wording is ambiguous.**
Location: risk-register.md R-1 lines 60-65.
The note that the criterion is adjusted proportionally if submission is delayed is not a concrete rule. Clarify: the kill criterion is 4 calendar weeks from confirmed submission date, regardless of when in the layer that date falls. Delete the proportionality note or replace it with a concrete date formula.

**5. (minor) U-Sleep training-data overlap check is not on the pre-run checklist.**
Location: approach.md lines 477-483, protocol-lock.md section 6 lines 215-228.
approach.md recommends confirming HMC PSG is not in U-Sleep training data before the headline run, but this check does not appear as a required checkbox in protocol-lock.md section 6. If HMC PSG test subjects appear in U-Sleep training data, the EEG-vs-HRV comparison is compromised. Add the overlap audit as a required gating checkbox before this protocol is used for implementation.

**6. (minor) Calibration-head dev set for scope (a) has an unacknowledged distribution shift.**
Location: approach.md scope (a) Stage 5 lines 439-445.
Temperature scaling is fit on Dreem-DOD-H (25 healthy subjects) and applied to NSRR (SHHS/MESA) test subjects. Different acquisition systems, demographics, and pathology mixes. The calibration may be ineffective on NSRR data. This risk is not mentioned in approach.md or risk-register.md. Either acknowledge it as a limitation in approach.md, or plan to re-fit the calibration head on an NSRR dev subset once the DUA arrives.

**7. (minor) Novelty claim for the paired EEG-vs-HRV comparison is over-broad.**
Location: approach.md Novelty section lines 715-728.
Fonseca 2017 and Radha 2019, both cited in approach.md, ran HRV-only staging on PSG datasets that also contain EEG, making an implicit same-population comparison available. The novel element is the explicit same-harness pre-registered paired test, not the absence of any prior modality comparison. Narrow the claim to: an explicit same-harness pre-registered paired comparison, rather than implying the wearable literature universally conflates modality and device effects.

---

## What I checked

- Read all four methodology artifacts in full (approach.md, risk-register.md, protocol-lock.md, pilots-README.md).
- Read admission.md and critic-defensibility.md in full.
- Verified spec-convention compliance on all four artifact headers.
- Verified scope (b) is primary and DUA-free; scope (a) is conditional, matching the admission advisory from the defensibility critic.
- Verified NSRR DUA day-one requirement appears in both approach.md lines 317-320 and risk-register.md R-1 lines 38-45.
- Verified held-out partition: 76 test subjects, subject-disjoint, touched exactly once, subject-ID lists committed to git before training. All present in protocol-lock.md sections 3 and 6.
- Verified primary metric (3-class macro-F1), CI method (bootstrap at subject level), statistical test (paired Wilcoxon one-sided), four pre-specified interpretation cases. All present in protocol-lock.md sections 4-5.
- Verified all four ablations are restricted to the dev split.
- Verified exploratory pilots (LSTM P-5, within-subject ceiling P-4) are labeled non-pre-registered and dev-only.
- Cross-checked the 151-subject figure against the stated PhysioNet URL challenge-2018/1.0.0 and identified the dataset identity mismatch.
- Checked compute table: scope (b) RF uses no GPU; U-Sleep VRAM claim (< 1 GB at batch=32) contingent on P-3 pilot passing.
- Checked all eleven risk-register kill criteria for concreteness.
- Checked the power arithmetic inconsistency between N=76 actual and N=105 required.

## What I could not check

- Could not independently verify whether challenge-2018/1.0.0 contains stage labels for 151 subjects vs arousal-only annotations for 994 records. Requires a human with PhysioNet access to resolve.
- Could not verify the U-Sleep training corpus manifest to determine whether the HMC Sleep Staging dataset is in U-Sleep training data.
- Could not verify whether Fonseca 2017 or Radha 2019 performed an explicit same-harness paired EEG-vs-HRV comparison.
- Could not confirm whether CAP Sleep (named in R-2, R-3) has ECG channels for all subjects.
- Could not confirm whether Dreem-DOD-O Zenodo record 15900394 includes AHI values per subject (required for P-6 AHI-band stratification).
