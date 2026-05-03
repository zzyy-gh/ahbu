> **Spec:** `20-plan/ecg-ppg-realworld/{approach,risk-register,protocol-lock,unlock-note-2026-05-03,pilots-README}.md` (under review) + `10-pain-point/ecg-ppg-realworld/admission.md` (the spec layer 20 received) + `30-implement/ecg-ppg-realworld/runs/pilot_p1_*.json` (three P-1 runs)

# Critic pass -- ecg-ppg-realworld methodology (v2, CinC 2017 re-pass) -- 2026-05-03

## Verdict

**pass-with-fixes**

The dataset pivot rationale is sound and the CinC 2017 protocol is substantially well-formed. Pre-registration is complete, held-out discipline is upheld, and the unlock note correctly characterises the P-1 finding. Four findings require action before layer 30 proceeds: one critical, two major, one minor carry-forward. The critical finding is the pilots-README.md stale state -- it describes a PTB-XL / strat_fold workflow throughout and was not updated when the dataset was switched. No finding blocks the scientific design; all are correctable in the current design phase.

---

## Findings

### Critical

**C-1 -- pilots-README.md is entirely PTB-XL-specific and was not updated after the dataset pivot**

Where: `20-plan/ecg-ppg-realworld/pilots-README.md`, all sections P-1 through P-7.

The file describes PTB-XL strat_fold semantics throughout: P-1 checks PTB-XL ptbxl_database.csv + scp_statements.csv, P-2 uses strat_fold 1-8, P-3 uses a strat_fold 1 subset, P-4 and P-5 use strat_fold 9, P-6 checks strat_fold 9 vs strat_fold 10 site overlap. Only P-7 mentions CinC 2017, and there as a cross-dataset probe against a PTB-XL-trained model -- the inverse of the new design. None of the pilot procedures describe CinC 2017 download, CinC 2017 record loading, or CinC 2017 partition creation.

The approach.md and protocol-lock.md correctly describe CinC 2017 as the primary dataset. pilots-README.md is now a contradictory planning document: it specifies pilot procedures for a dataset that has been abandoned. An implementer arriving at layer 30 with pilots-README.md as the operational guide will run PTB-XL pilots against a CinC 2017 protocol.

What to do: rewrite pilots-README.md for CinC 2017. At minimum: replace P-1 with a CinC 2017 download and class-count verification pilot (confirm 771 AF records, 8,528 total, ODC-BY licence check); update P-2 through P-5 to reference CinC 2017 records and the 80/20 dev/test split (not strat_fold); replace P-6 with the CinC 2017 record-level partition audit (validate_partition() on record IDs); retain P-7 as an optional cross-dataset probe on CinC 2020. The P-3 VRAM probe can be retained in substance but must reference CinC 2017 input shape (1,1,9000) not PTB-XL (12,1000). Marked critical because it is the implementer operational guide and currently contradicts every other layer-20 artifact.

---

### Major

**M-1 -- VRAM extrapolation is 9x out-of-distribution; a CinC 2017-specific VRAM pilot has not been run**

Where: `20-plan/ecg-ppg-realworld/approach.md` section Feasibility check (4 GB VRAM envelope); `20-plan/ecg-ppg-realworld/risk-register.md` R-2.

The approach asserts xresnet1d50 at batch=8 float32 with 9,000 samples is estimated at ~1.5-2.0 GB VRAM based on linear scaling from the P-3 measurement. The P-3 pilot (`30-implement/ecg-ppg-realworld/runs/pilot_p3_1777729895.json`) ran with seq_len=1000 (not 9,000) at batch=32, reporting 0.62 GB. The extrapolation scales from (batch=32, seq_len=1000) to (batch=8, seq_len=9000). Going from seq_len=1000 to seq_len=9000 is 9x longer input; going from batch=32 to batch=8 is 0.25x. Net factor ~2.25x gives an estimate of ~1.4 GB. The stated ~1.5-2.0 GB is plausible but the approach says no re-probe needed -- seq_len=1000 is not comparable to seq_len=9000.

The 3.2 GB kill threshold and ~1.4 GB estimate provide probably adequate headroom, but this is unverified. Activation memory before global average pooling scales with sequence length in ways that can exceed the linear approximation for early ResNet blocks.

What to do: (a) Update approach.md to state P-3 ran at seq_len=1000; CinC 2017 requires seq_len=9000. A CinC 2017-specific VRAM probe is required as the first pilot step before committing the training configuration. (b) Update pilots-README.md (as part of C-1 fix) to mark this as a critical-priority pilot. (c) Update risk-register R-2 to note that the P-3 result is indicative only.

---

**M-2 -- McNemar test construction does not specify which records populate the 2x2 table; the framing tests accuracy change on committed records, not PPV change**

Where: `20-plan/ecg-ppg-realworld/protocol-lock.md` section 6; `20-plan/ecg-ppg-realworld/approach.md` section Statistical test.

Protocol-lock section 6 describes the McNemar table as built from committed records on which both conditions make a prediction. McNemar on those records checks whether the two classifiers produce different predictions -- this tests overall accuracy change on the committed set, not PPV change. PPV is TP/(TP+FP), computed only on the predicted-positive (predicted-AF) subset.

The stated H1 is abstention improves PPV. The operationalised test checks accuracy change. These coincide only if the abstainer exclusively removes false positives from the committed set, which is the hoped-for mechanism but not guaranteed. The R-7 power calculation (80 discordant pairs from 128 committed AF positives) implies the table is built on committed AF-relevant records, but the protocol text does not state this explicitly.

What to do: add two sentences to protocol-lock.md section 6 specifying the exact table construction: The 2x2 table is built on all committed test-split records. Each record is labelled correct or incorrect under each condition. McNemar tests whether the abstainer changes prediction outcomes on committed records. PPV is separately computed as TP/(TP+FP) on the predicted-AF subset of committed records and reported with bootstrap CI. The primary hypothesis is assessed by both statistics together; neither alone is sufficient.

---

### Minor

**m-1 -- Partition size discrepancy: approach.md says 1,706 test records; protocol-lock.md says ~1,696**

Where: `20-plan/ecg-ppg-realworld/approach.md` section Held-out partition; `20-plan/ecg-ppg-realworld/protocol-lock.md` section 3.

20 pct of 8,482 working-set records is 1,696.4, rounding to 1,696. protocol-lock.md says ~1,696. approach.md says 1,706. The discrepancy is 10 records and does not affect power, but two different numbers in two locked documents will cause confusion during the partition audit.

What to do: align both documents to the protocol-lock figure (~1,696 records). Correct approach.md section Held-out partition.

---

### Minor carry-forward from v1

**m-2 -- Unnamed wide-CI inconclusive case in protocol-lock section 7 decision rule**

Where: `20-plan/ecg-ppg-realworld/protocol-lock.md` section 7.

The decision rule defines positive, partial positive, and null. The case p >= 0.05 AND 95% CI upper bound >= 10 pp is underpowered-inconclusive and falls through all three categories. This is a real possibility given R-7.

What to do: add one sentence to the null definition: If p >= 0.05 and the 95% CI upper bound >= 10 pp, the result is inconclusive (underpowered); findings.md must state this explicitly and report the realized CI width and the actual AF N in the test split.

---

## What passes cleanly

**Spec drift:** None. All four revised artifacts answer the admission record exactly. The pivot to CinC 2017 single-lead is more faithful to the stated constituency (Apple Watch / AliveCor wearable users) than the original PTB-XL 12-lead design. The scope narrowing is honest and documented.

**Unlock note completeness:** unlock-note-2026-05-03.md correctly states the root cause (PTB-XL AFIB/RHYTHM vs diagnostic-superclass label namespace conflation), enumerates all four paths with reasons for rejecting A, B, and D, and selects C with justification. The pivot occurred before any held-out data was touched.

**CinC 2017 license and access:** ODC-BY v1.0, freely downloadable, no data-use agreement required. Verified against PhysioNet directly. Class counts (Normal 5154 / AF 771 / Other 2557 / Noisy 46, total 8528) match approach.md and protocol-lock.md exactly.

**Single-lead constituency alignment:** AliveCor Kardia is a single-lead handheld ECG device. Apple Watch ECG and Fitbit ECG are also single-lead. CinC 2017 data comes from AliveCor Kardia recordings. The constituency framing is more honest to the device class than PTB-XL 12-lead was. This is a genuine improvement.

**Power adequacy:** 154 test-split AF positives. At 17% abstention budget, committed AF positives ~128. At a realistic discordant-pair fraction of ~60% (~77 pairs), McNemar at alpha=0.05 is adequate for ~80% power at ~10 pp effect size. R-7 correctly characterises this as boundary-adequate and provides a kill criterion (N_committed_AF < 50 triggers a power warning).

**Pre-registration completeness:** held-out partition (CinC 2017 20% stratified by class, random_state=42, record IDs frozen to partition.json) named. Primary metric (PPV at 17% abstention) named. Statistical test (McNemar one-sided, p < 0.05) named. H0/H1 stated. Decision rule with numeric thresholds stated. Pre-run checklist with six items. Held-out touched exactly once.

**Novelty claim:** correctly scoped. PPV-at-fixed-alert-rate calibrated to the BASEL 17-21% inconclusive rate is not the framing in Smole 2023, NCA 2024, or Barandas 2024 (which use accuracy-under-rejection or AUROC-under-rejection). Standard components labelled as intentionally standard.

**Spec line on every file:** all four revised artifacts carry the spec line as the first line. Compliant with CLAUDE.md convention.

**Ablations on load-bearing choices:** three abstention mechanisms compared within the primary model, deep vs LR-HCF comparison, window-length sensitivity. All load-bearing choices are ablated on dev split only.

---

## v1 findings disposition

**M-1** (PPV/coverage denominator ambiguity): partially addressed in the rewrite. Residual McNemar construction ambiguity re-raised as M-2 in this pass.

**M-2** (strat_fold 9 calibration vs seed-selection inconsistency): gone. CinC 2017 design uses a single 80/20 split; no strat_fold ambiguity exists.

**m-1** (forward reference to non-existent cross-subject-eeg/approach.md): resolved in the rewrite.

**m-2** (unnamed wide-CI inconclusive case): not fixed in the rewrite. Carries forward as m-2 in this pass.

**m-3** (admission.md human checkpoint unchecked): not re-examined in this pass. Advisory carry-forward.

---

## What I checked

- Read all four revised methodology artifacts end to end.
- Read the original admission record including advisory annotations.
- Read methodology-critic.md (v1) and tracked all five finding dispositions.
- Read all three P-1 pilot JSON results; verified AFIB counts match the unlock-note table exactly.
- Read the P-3 pilot JSON result; identified seq_len=1000 vs seq_len=9000 discrepancy underlying M-1.
- Read pilots-README.md end to end; confirmed none of P-1 through P-6 references CinC 2017 as primary dataset, underlying C-1.
- Verified CinC 2017 license (ODC-BY), record count (8,528), and class distribution against PhysioNet directly -- all match artifacts exactly.
- Verified power arithmetic: 154 test-split AF positives, ~128 committed at 17% abstention, ~77 discordant pairs at 60% fraction, adequate for 80% power at ~10 pp effect size.
- Checked McNemar test construction against stated null/alternative and identified the accuracy-vs-PPV framing gap (M-2).
- Identified 10-record partition size discrepancy between approach.md (1,706) and protocol-lock.md (1,696) -- raised as m-1.
- Checked spec-line presence and format on all four revised artifacts.
- Checked novelty claim framing against prior work citations.
- Checked held-out discipline across protocol-lock section 7 pre-run checklist.
- Verified AliveCor Kardia and Apple Watch ECG are single-lead devices, confirming constituency alignment for Path C.

## What I could not check

- Did not run a VRAM probe at seq_len=9000 empirically. The M-1 concern is analytical; the actual value requires a pilot run.
- Did not independently verify Smole 2023, NCA 2024, or Barandas 2024 to confirm none uses PPV-at-coverage as a primary metric. Accepted approach.md characterisation as stated.
- Did not verify whether CinC 2017 training set guarantees unique patients across records. R-4 limitation documentation is appropriate given this uncertainty.
- Did not verify the BASEL 17-21% inconclusive rate against Mannhart et al. 2023 directly. The figure was accepted from the admission record where it passed layer-10 critic scrutiny.
- Did not check conformal prediction library compatibility (crepes, nonconformist) with the project pinned Python/PyTorch version -- a practical dependency risk not currently covered in the risk register.
