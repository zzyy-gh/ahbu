> **Spec:** `10-pain-point/ecg-ppg-realworld/admission.md`

# Risk register — ecg-ppg-realworld

**Track:** ecg-ppg-realworld
**Date:** 2026-05-03
**Author:** methodologist agent (re-pass)
**Status:** draft — pending critic gate before layer 30

Kill criterion notation: a kill criterion is a specific threshold that, if hit, means stop that component and document why. Stopping a component is not retiring the track unless R-10 is triggered.

---

## R-1 — PTB-XL AFIB label counts insufficient (RESOLVED by dataset pivot)

**Status: RESOLVED.** Pilot P-1 confirmed 48 AFIB-positive records in PTB-XL (fold-10: 8 records), approximately 10x below the N = 87 required for 80 % power. Dataset switched to PhysioNet/CinC 2017 (771 AFIB positives). See `unlock-note-2026-05-03.md` for full rationale.

**Evidence from pilot:** PTB-XL `ptbxl_database.csv` + `scp_statements.csv` enumerated directly. Records with AFIB SCP likelihood > 0: 48. Records with AFIB or AFLT: 104. fold-10 AFIB: 8.

**Why this risk is listed:** it was the original design flaw. Recording it prevents future confusion about why PTB-XL was dropped.

**Residual concern:** CinC 2017 AFIB prevalence is 9.0 % (771 / 8528). In the 20 % test split (~1706 records), expected AFIB count ~154. This is well above N = 87. Power is adequate. The residual concern is that the class imbalance (9 % AF vs 91 % non-AF) may require class-weighting in training. Mitigation: use class-weighted cross-entropy (weight inversely proportional to class frequency). Log class weights in `30-implement/ecg-ppg-realworld/runs/`.

---

## R-2 — xresnet1d50 VRAM exceeds 3.2 GB on CinC 2017 input

**Probability:** low. Cross-subject-eeg P-3 confirmed 0.62 GB at batch=32 on shorter input. Scaling estimate for batch=8, input=(8,1,9000) is ~1.5-2.0 GB.

**Impact:** would require batch reduction or float16 switch.

**Mitigation:**
1. Pilot P-1 (ecg-ppg-realworld): run xresnet1d50 forward pass with input shape (8, 1, 9000), float32, log `torch.cuda.max_memory_allocated() / 1e9`.
2. If > 3.2 GB at batch=8: reduce to batch=4. Re-measure. Estimated ~1.0 GB.
3. If > 3.2 GB at batch=4: switch to float16. Re-measure.
4. If > 3.2 GB at float16 batch=4: use xresnet1d18 as primary model (smaller architecture).

**Kill criterion for deep model:** if xresnet1d18 float16 batch=4 exceeds 3.2 GB VRAM, cancel xresnet family. Fall back to LR-HCF as primary model (headline becomes LR-HCF + abstention only). Document in results.md as a compute-imposed limitation.

---

## R-3 — Calibration method does not improve PPV (null result on primary metric)

**Probability:** moderate. The theoretical motivation is sound, but empirical calibration improvements are dataset-dependent and may be small.

**Impact:** null result on primary metric. This is a valid scientific outcome, not a failure.

**Mitigation:**
- Ablations 1-4 on dev split will characterize the PPV-coverage curve shape before the headline run. If the dev-split curve is flat (no PPV improvement with abstention), the headline will likely be null.
- A flat dev-split curve is informative: it means the model's confidence scores are poorly calibrated relative to the PPV-precision trade-off, and abstention thresholding on softmax alone is not sufficient.
- If dev-split shows null: proceed to headline anyway. A confirmed null is the contribution ("calibrated abstention does not improve PPV for wearable-grade AFib detection at the BASEL coverage budget"). This is defensible per admission.

**Kill criterion for abstention study:** if PPV-at-coverage curve on dev split is not monotonically increasing as coverage decreases (i.e., abstaining on uncertain inputs does not improve PPV even on dev set), add a diagnosis pass to understand why (miscalibration? class overlap? label noise?) and document findings in the headline. Do NOT redesign the metric; report the null with its diagnosis.

---

## R-4 — No patient-level IDs in CinC 2017 public release (label leakage risk)

**Probability:** confirmed. The CinC 2017 training set does not include patient identifiers in the public release. Multiple recordings from the same patient may appear in both dev and test splits under a record-level random split.

**Impact:** if a patient contributes records to both train and test, the model has seen that patient's rhythm pattern during training. This could inflate test-set performance, particularly for rare or unusual rhythm presentations.

**Mitigation:**
- Document this as a limitation in `limitations.md` post-headline.
- Estimate the magnitude: the training set has 8,528 records but ~unknown patients. The CinC 2017 challenge paper notes "all were unique patients" for the test set — this suggests some patient-deduplication was done for the test set by the organizers, but this is not guaranteed to apply to the training set.
- A record-level 80/20 split is standard practice for CinC 2017 (used by the majority of papers that train on this dataset). The limitation is inherited from the dataset, not introduced by this protocol.
- If patient-level identifiers become available (e.g., via challenge organizer contact or a derived dataset), update the split at pilot time. Do not change the split after any dev-split results have been computed.

**Kill criterion:** this risk does not trigger a kill criterion. It is a documentation obligation only. The headline proceeds with record-level split and the limitation is stated explicitly.

---

## R-5 — CinC 2017 label quality uncertainty (cardiologist annotation variability)

**Probability:** low-moderate. The labels were assigned by a panel of cardiologists, but inter-rater agreement for the "Other" class is known to be lower than for Normal and AF. The 46 "Too noisy" records are excluded; but some "Normal" or "Other" records may contain brief AF episodes not captured by the recording-level label.

**Impact:** label noise dilutes the apparent PPV improvement from abstention. The model may abstain on records where label noise is high, which would inflate observed PPV without clinical meaning.

**Mitigation:**
- Exclude the "Too noisy" class from all training and evaluation (done in preprocessing).
- Analyze abstained records on dev split: do abstained records have higher entropy in their cardiologist label (if multiple annotations exist)? CinC 2017 does not provide multiple cardiologist annotations publicly; this check is aspirational.
- Report that label noise is an inherited limitation and cannot be resolved with available data.

**Kill criterion:** none. Label quality is a known dataset property; it does not trigger cancellation.

---

## R-6 — xresnet1d50 does not outperform LR-HCF on AUROC (model-quality concern)

**Probability:** low-moderate on a single-lead binary task with 771 positives.

**Impact:** if LR-HCF achieves comparable AUROC, the deep model's abstention curves may not be more discriminative. The ablation comparison (Ablation 4) would show LR-HCF + calibrated abstention is sufficient.

**Mitigation:**
- Report both models fully. If LR-HCF matches xresnet1d50 on PPV-at-coverage, the contribution is: "a simple calibrated logistic regressor achieves BASEL-parity PPV with a 17 % abstention budget on wearable-grade ECG."
- This is a valid and publishable result. Do not chase xresnet1d50 performance improvements at the cost of held-out integrity.

**Kill criterion:** none. If LR-HCF beats xresnet1d50, report it. Do not suppress.

---

## R-7 — Bootstrap CI too wide to distinguish abstention benefit

**Probability:** moderate at N_committed = ~128 (154 test AFIB positives × 0.83 coverage = ~128 committed AFIB positives at 17 % abstention).

**Impact:** if 95 % CI on PPV difference spans both positive and negative values, the McNemar's test may not reject H0, and the headline is null with wide uncertainty.

**Mitigation:**
- Pre-compute required sample size: for 10 pp PPV improvement from 35 % to 45 %, McNemar's test at alpha=0.05, 80 % power, requires approximately 60-80 discordant pairs. With ~128 committed AFIB positives and a realistic discordant-pair fraction of ~60 %, we expect ~77 discordant pairs. This is on the boundary of adequate power.
- If CinC 2017 test split has fewer than 100 committed AF positives at 17 % abstention, note the power limitation explicitly.
- Do not compensate by loosening the abstention threshold to include more records. The threshold is fixed at dev-split tuning.

**Kill criterion for power:** if expected N_committed_AF < 50 at 17 % abstention on the test split, note "underpowered at this coverage level" in results.md and also report the 0 % abstention (baseline) result with full CI. The study is still informative on the PPV-at-coverage curve shape.

---

## R-8 — Temperature scaling overfit to dev split

**Probability:** low if dev split is large enough. Dev split has ~617 AF positives.

**Impact:** temperature parameter T optimized on dev split may not generalize to test split, producing worse calibration on the test split than the uncalibrated baseline.

**Mitigation:**
- Fit temperature scaling on a calibration held-out within the dev split (use 20 % of dev as calibration set, 80 % as training set). This is the standard Guo et al. 2017 procedure.
- Report ECE on both the calibration-held-out (dev) and the test split. If ECE worsens after temperature scaling on the test split, report this finding.

**Kill criterion:** none. Temperature scaling miscalibration on test split is a finding to report, not a reason to stop.

---

## R-9 — Conformal RAPS implementation error

**Probability:** low if a standard library is used.

**Impact:** incorrect prediction sets lead to incorrect abstention decisions and invalid coverage guarantees.

**Mitigation:**
- Use an established implementation: `crepes` (Linusson & Johansson, PyPI) or `nonconformist` (PyPI). Do not implement RAPS from scratch.
- Verify coverage guarantee on dev split: if target coverage = 83 % (17 % abstention), empirical coverage on dev split must be >= 83 %. If not, the implementation is incorrect.
- Log empirical coverage in `30-implement/ecg-ppg-realworld/runs/`.

**Kill criterion:** if empirical coverage on dev split is < target coverage - 2 pp, the RAPS implementation is incorrect. Re-implement or switch libraries before using conformal abstention results in any report.

---

## R-10 — Track retire-cancel trigger (project-level)

**Condition:** the headline result is null AND the failure mode cannot be characterized. That is, PPV improvement at 17 % abstention is not statistically significant, AND the PPV-coverage curve does not show a monotonic trend even on the dev split, AND there is no diagnosable cause (not label noise, not class imbalance, not calibration failure — all checked via ablations).

**Action:** if R-10 triggers, write `20-plan/ecg-ppg-realworld/findings.md` documenting the null, `limitations.md` documenting why characterization was not possible, and `lessons.md` with lessons for future abstention tracks. Tag `v5-ecg-ppg-realworld-retired`. The pain is real; the solution failed. That is itself a contribution.

---

## Risk summary

| ID | Risk | Probability | Impact | Status |
|---|---|---|---|---|
| R-1 | PTB-XL AFIB underpowering | confirmed | fatal | RESOLVED by dataset pivot |
| R-2 | xresnet1d50 VRAM overflow | low | medium | pilot P-1 (ecg-ppg-realworld) |
| R-3 | Null result on primary metric | moderate | low (valid finding) | ablation 1-4 on dev |
| R-4 | No patient IDs in CinC 2017 | confirmed | medium | documented limitation |
| R-5 | CinC 2017 label noise | low-moderate | low | documented limitation |
| R-6 | LR-HCF matches xresnet1d50 | low-moderate | low (valid finding) | ablation 4 |
| R-7 | Bootstrap CI too wide | moderate | medium | check N_committed pre-headline |
| R-8 | Temperature scaling overfit | low | low | calibration-held-out in dev |
| R-9 | RAPS implementation error | low | medium | coverage-guarantee check on dev |
| R-10 | Track retire-cancel | unlikely | high | diagnostic pass before retiring |
