> **Spec:** `10-pain-point/ecg-ppg-realworld/admission.md`

# Risk register — ecg-ppg-realworld

**Track:** ecg-ppg-realworld
**Date:** 2026-05-02
**Author:** methodologist agent
**Status:** draft — pending critic gate before layer 30

Each risk has: description, probability estimate (H/M/L), impact
(H/M/L), mitigation, and a concrete kill criterion (numeric or yes/no).
Kill criteria are checked at the milestone they apply to. "Retire-cancel"
means the track itself is retired; otherwise only the affected arm is
cancelled.

---

## R-1 — PTB-XL access fails or waveform files are corrupted

**Description:** PhysioNet is inaccessible (outage, DNS failure) or the
downloaded PTB-XL waveform archive is corrupted such that wfdb cannot
read a significant fraction of records.

**Probability:** L (PhysioNet is stable; PTB-XL v1.0.3 is a frozen,
widely-used release).
**Impact:** H (no dataset = no track).

**Mitigation:**
1. Download and verify at week 1. Run wfdb.rdrecord() on a 100-record
   sample and confirm no parse errors. Log pass/fail.
2. Verify total record count matches 21,799 (per the database header).
3. If PhysioNet is temporarily unavailable: wait up to 72 hours (outages
   are rare and brief). Alternative: download via the wfdb Python library
   which caches locally.
4. If waveform files are partially corrupted: document the corrupted record
   IDs, exclude them from analysis, and report the exclusion rate.

**Kill criterion:** If more than 5% of PTB-XL records are unreadable
after download, or if strat_fold 10 (the held-out test partition) has
more than 2% unreadable records, retire-cancel the track. Rationale: a
5% data loss is manageable; a loss concentrated in the test partition
would bias held-out evaluation and cannot be corrected without touching
the test split.

---

## R-2 — AFIB record count in strat_fold 10 is below the power threshold

**Description:** The actual AFIB-labeled record count in strat_fold 10
is materially below the ~303 figure cited in the defensibility critic
advisory (from Strodthoff et al. 2020 Table 1). This would reduce
statistical power below the N=87 threshold for detecting a 21 pp PPV
improvement.

**Probability:** L (the ~1,514 total and ~303 held-out figures come from
the published PTB-XL benchmark paper and are verified).
**Impact:** M (a count below ~87 AFIB records in strat_fold 10 would
require a power re-analysis before the headline run).

**Mitigation:**
1. Count AFIB-labeled records in each strat_fold during week 1
   preprocessing (using likelihood_threshold=100.0). Log the count.
2. If strat_fold 10 has 87–150 AFIB records (lower than expected but
   above threshold): power analysis is still met; report the actual N.
3. If strat_fold 10 has fewer than 87 AFIB records: expand the test
   partition to include strat_fold 9 + 10 combined (total ~600 records,
   ~60 AFIB expected at minimum in fold 9). This design change must be
   documented before touching any data in strat_fold 9 or 10 for
   non-calibration purposes.

**Kill criterion:** If the combined strat_fold 9+10 AFIB count is below
87 records at likelihood_threshold=100.0, lower the threshold to 75.0
and recount. If the count remains below 87 even at threshold=75.0,
retire-cancel the headline PPV claim with a documented reason. A Brier
score / calibration study can still proceed, but the PPV power claim
cannot be made honestly.

---

## R-3 — Abstention mechanism is uninformative (Ablation 1 kill trigger)

**Description:** After temperature scaling, the model's confidence
ordering is uninformative: abstaining on the lowest-confidence records
does not remove more false positives than true positives. PPV at
coverage=0.80 is not materially higher than PPV at coverage=1.00 on
the validation set (strat_fold 9).

**Probability:** M (the model may be well-calibrated but not well-ranked;
or the prevalence in PTB-XL strat_fold 9 may differ from what the
power analysis assumed).
**Impact:** H (the primary contribution of this track depends on
abstention being informative).

**Mitigation:**
1. Run Ablation 1 on strat_fold 9 before the headline run.
2. If PPV improvement at coverage=0.80 is < 2 pp on strat_fold 9:
   a. Check whether AUC of (confidence score vs correctness) is > 0.55.
      If AUC < 0.55, the confidence is uncorrelated with correctness —
      the mechanism is broken.
   b. If confidence ordering is fine but PPV improvement is small:
      the AFIB prevalence in the test set may be so low that abstention
      provides minimal gain. Report this as a finding, not a failure.
   c. Try MC-Dropout abstention (Model B) as an alternative — if
      MC-Dropout confidence is better correlated with correctness,
      switch to MC-Dropout as the primary abstention mechanism before
      the headline. This switch must be documented as a pre-headline
      design change.
3. If both temperature scaling and MC-Dropout show < 2 pp improvement on
   strat_fold 9 and confidence-correctness AUC < 0.55: this is a genuine
   null — the ResNet-1D on PTB-XL does not produce informative uncertainty
   estimates. Proceed to headline to confirm on strat_fold 10. The null
   is the finding.

**Kill criterion:** If Ablation 1 on strat_fold 9 shows that BOTH
temperature scaling AND MC-Dropout produce confidence-correctness AUC
< 0.55, the abstention mechanism is fundamentally broken on this model.
Before proceeding to headline, run the classical logistic regression
baseline abstention. If the classical baseline also shows AUC < 0.55,
retire-cancel the headline. If only the neural model fails but the
classical baseline works, report both results honestly — the headline
becomes "classical abstention works; neural abstention does not on
PTB-XL at 4 GB."

---

## R-4 — Novelty contention: a paper is published mid-run that uses PPV-at-coverage on PTB-XL

**Description:** A peer-reviewed paper is published between methodology
lock and headline evaluation that explicitly uses PPV at a fixed alert
rate as the primary metric for ECG abstention on PTB-XL, directly
matching our novelty claim.

**Probability:** L–M (the gap-closing pass found no such paper as of
2026-05-02; the framing is unusual enough that rapid duplication is
unlikely but possible given the active ECG-ML literature).
**Impact:** M (reduces novelty of the headline; does not invalidate the
honest evaluation infrastructure or the shared substrate contributions).

**Mitigation:**
1. Conduct a final literature check at the start of the headline
   evaluation run (week 4) before touching strat_fold 10. Search for:
   "PTB-XL abstention PPV alert rate" and equivalents.
2. If a matching paper is found:
   a. Read it carefully. Check whether the held-out split is
      patient-disjoint (many published PTB-XL studies are not).
   b. If our protocol is more rigorous (patient-disjoint + temperature
      scaling + multi-seed + bootstrap CI), proceed and explicitly compare.
      The rigor difference is itself a contribution.
   c. If the paper uses identical methods with identical rigor: downgrade
      the novelty claim. The shared-substrate contributions (calibration.py,
      abstention.py, partition.py) remain valuable regardless.
3. Do NOT halt the headline run for novelty reasons alone. A rigorous
   replication with honest uncertainty quantification is valuable.

**Kill criterion:** None for this risk alone. Novelty contention does
not trigger a retire-cancel. It triggers a re-framing of the contribution.
If the track's ONLY contribution would have been the PPV-at-coverage
framing, and a pre-print shows it already, escalate to human checkpoint
before spending the headline run token.

---

## R-5 — Model training fails to converge or produces degenerate outputs

**Description:** xresnet1d50 trained on PTB-XL strat_fold 1–8 fails
to converge (loss stays at cross-entropy baseline), or produces
degenerate predictions (all predictions the same class, or all
confidence values near 0.5).

**Probability:** L (xresnet1d50 on PTB-XL is a known-working
configuration from Strodthoff et al. 2020; exact hyperparameters are
documented in the benchmark paper and publicly available implementation).
**Impact:** H (no trained model = no headline).

**Mitigation:**
1. Use the public benchmark implementation as starting point
   (https://github.com/helme/ecg_ptbxl_benchmarking). Do not
   reimplement from scratch.
2. Verify convergence after epoch 5 (loss should decrease materially
   from baseline). If not: check data loading and normalization.
3. If convergence fails: fall back to a smaller model (xresnet1d34 or
   a single-lead version). Document the fallback.
4. Always have the logistic regression baseline as a no-GPU fallback.
   The baseline can produce calibration and abstention results even if
   the neural model fails.

**Kill criterion:** If neither xresnet1d50 nor the logistic regression
baseline produces above-chance predictions (AUROC > 0.60) on strat_fold 9,
retire-cancel. The problem cannot be modeled with our approach — either
the preprocessing is broken or the label extraction is wrong.

---

## R-6 — Temperature scaling fails to improve calibration

**Description:** After temperature scaling on strat_fold 9, the ECE
is not materially lower than before scaling (< 0.01 ECE improvement).
This is possible if the model is already well-calibrated or if the
validation set is too small to fit T reliably.

**Probability:** L–M (modern ResNet-1D models on imbalanced datasets
are typically overconfident; temperature scaling usually helps).
**Impact:** L (this is a finding, not a fatal outcome; the track can
report it honestly and proceed to the abstention evaluation regardless).

**Mitigation:**
1. Report Brier score and ECE before and after temperature scaling.
2. If ECE improvement < 0.01: try Platt scaling (logistic regression
   on logits) as an alternative calibration method.
3. Report whichever calibration method produces the lower ECE on
   strat_fold 9. Document the comparison.

**Kill criterion:** None. A failure of temperature scaling is a finding.
Proceed to headline with the best-calibrated model regardless.

---

## R-7 — Held-out partition touched prematurely (protocol violation)

**Description:** Any analysis, even "just a look," is performed on
strat_fold 10 before the single authorized evaluation run.

**Probability:** L–M (easy to do accidentally when loading the full
PTB-XL dataset and computing aggregate statistics).
**Impact:** H (invalidates the honest-evaluation claim — the primary
epistemic contribution of this track).

**Mitigation:**
1. Store strat_fold 10 record IDs in a separate config key
   (`test_record_ids`). During dev and pilot phases, only records
   from strat_fold 1–9 are loaded via code.
2. Implement a guard function in ptbxl_loader.py: if the caller
   requests strat_fold 10 records, and a global flag `HEADLINE_RUN`
   is not set to True, raise a RuntimeError.
3. Before the headline run, manually confirm in the pre-run checklist
   that no file in `30-implement/ecg-ppg-realworld/runs/` contains results
   derived from strat_fold 10 records.

**Kill criterion:** If a model selection decision (choice of model,
choice of abstention mechanism, choice of AFIB likelihood threshold)
was made after seeing strat_fold 10 performance, retire-cancel the
headline. The evaluation is no longer honest. Document transparently.
This is a hard cancel with no recovery path.

---

## R-8 — xresnet1d50 exceeds 4 GB VRAM during training

**Description:** Training xresnet1d50 at batch=32, 12 leads × 1,000
samples, float32 uses more than 4 GB VRAM on the GTX 1650.

**Probability:** L (estimated ~0.8 GB at batch=32 float32; 4 GB envelope
has significant margin).
**Impact:** M (would require batch size reduction or mixed precision;
adds debugging time but not a blocker).

**Mitigation:**
1. Run Pilot P-1 (VRAM probe) before the full training run.
2. If > 3 GB at batch=32 float32: switch to float16 mixed precision
   (`torch.cuda.amp.autocast()`). Retest.
3. If > 3 GB at batch=32 float16: reduce batch size to 16. Retest.
4. If > 3 GB at batch=4 float16: the model does not fit locally.
   Move training to Kaggle T4 (16 GB). Store trained weights locally
   for inference and calibration (inference is trivially local).

**Kill criterion:** If xresnet1d50 cannot complete a training epoch
on GTX 1650 AND Kaggle T4 is unavailable, fall back to the logistic
regression baseline only. The headline becomes classical-only. This
is a valid outcome — document it.

---

## R-9 — Classical baseline matches or exceeds neural model at coverage=0.80

**Description:** Logistic regression on 12 hand-crafted features
achieves PPV at coverage=0.80 equal to or higher than xresnet1d50
on strat_fold 9.

**Probability:** L–M (RR-interval irregularity is highly diagnostic
for AFib; a classical feature that captures RR irregularity may be
nearly sufficient for this task).
**Impact:** L (this is a finding, not a fatal outcome; it suggests the
deep model does not add value beyond the classical signal for abstention).

**Mitigation:**
None needed. This is a pre-characterized informative outcome.
If the classical baseline matches the neural model, report it as the
primary finding: "For calibrated AFib abstention on PTB-XL, a classical
12-feature logistic regression provides equivalent PPV-at-coverage to a
ResNet-1D, suggesting the abstention signal is captured by RR-interval
irregularity alone."

**Kill criterion:** None. This outcome does not trigger a cancel.

---

## R-10 — Bootstrap CI is so wide that the headline result is uninformative

**Description:** At N=~303 AFIB records in strat_fold 10, the bootstrap
95% CI on the PPV difference (abstention minus no-abstention at
coverage=0.80) is wider than 20 pp, making the result consistent with
both a large positive effect and a null.

**Probability:** L (power analysis indicates N=87 required to detect
a 21 pp difference; N=303 is 3.5× the required N, so CIs should be
manageable).
**Impact:** M (if the CI is wide despite adequate N, the AFIB prevalence
in strat_fold 10 may be lower than expected, reducing effective sample
size for PPV computation).

**Mitigation:**
1. Verify AFIB count in strat_fold 10 during week 1 (R-2 mitigation).
2. Report the CI regardless of width. A wide CI is itself informative
   about the stability of the metric.
3. If the CI is very wide (> 20 pp) despite N > 87: investigate whether
   the PPV variability is driven by a small number of high-confidence
   borderline records. Report the sensitivity analysis.

**Kill criterion:** None. A wide CI is a finding, not a failure.
Report it honestly.

---

## Summary table

| ID | Risk | P | I | Kill criterion |
|---|---|---|---|---|
| R-1 | PTB-XL access/corruption | L | H | > 5% records unreadable, OR > 2% in strat_fold 10 → retire-cancel |
| R-2 | AFIB count below power threshold | L | M | Combined fold 9+10 AFIB < 87 at threshold=75.0 → retire PPV headline |
| R-3 | Abstention mechanism uninformative | M | H | Both temperature scaling AND MC-Dropout confidence-correctness AUC < 0.55, AND classical baseline also < 0.55 → retire-cancel |
| R-4 | Novelty contention mid-run | L–M | M | None — re-frame contribution; human checkpoint if framing collapses |
| R-5 | Model fails to converge | L | H | AUROC < 0.60 on strat_fold 9 for both neural AND classical models → retire-cancel |
| R-6 | Temperature scaling fails | L–M | L | None — finding, not failure |
| R-7 | Test split touched prematurely | L–M | H | Model selection depended on strat_fold 10 → retire-cancel headline (hard) |
| R-8 | VRAM exceeded during training | L | M | No training possible locally AND Kaggle unavailable → fall back to classical-only headline |
| R-9 | Classical baseline matches neural | L–M | L | None — informative finding |
| R-10 | Bootstrap CI too wide | L | M | None — report as finding |

---

## Retire-cancel triggers (track level)

The track retires-cancelled (not just an arm) if ANY of the following:

1. **Data blocker:** PTB-XL strat_fold 10 has > 2% unreadable records
   after download verification (R-1).

2. **Power failure:** AFIB record count in the test partition is below
   the N=87 power threshold even after expanding to fold 9+10 and
   lowering the likelihood threshold to 75.0 (R-2).

3. **Mechanism failure:** Both neural and classical abstention mechanisms
   show confidence-correctness AUC < 0.55 on the validation set (R-3).
   A mechanism that cannot distinguish correct from incorrect predictions
   cannot produce an informative abstention result.

4. **Modeling failure:** Neither xresnet1d50 nor logistic regression
   achieves AUROC > 0.60 on strat_fold 9 (R-5). The problem is not
   being modeled.

5. **Protocol violation:** The held-out partition influenced model
   selection before the single authorized evaluation run (R-7).

In any retire-cancel scenario: write a concise retire-cancel note in
`10-pain-point/ecg-ppg-realworld/admission.md`, update
`10-pain-point/shared/portfolio.md`, and tag
`v2-ecg-ppg-realworld-retired-cancelled`.

The shared-substrate promotion candidates (calibration.py, abstention.py,
partition.py, ptbxl_loader.py) are still worth promoting if partially
built, even in a retire-cancel — they have value for other tracks.
