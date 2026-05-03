> **Spec:** `10-pain-point/ecg-ppg-realworld/admission.md`

# Unlock note — ecg-ppg-realworld — 2026-05-03

**Date:** 2026-05-03
**Author:** methodologist agent (re-pass)
**Scope of change:** dataset pivot before first protocol lock. No headline experiment has run; held-out split has not been touched. This is a design-phase correction, not an unlock of a live pre-registration.

---

## What the pilot found

Pilot P-1 enumerated PTB-XL AFIB-positive records directly from `ptbxl_database.csv` and `scp_statements.csv` at three likelihood thresholds:

| threshold | AFIB records | fold-10 positives |
|---|---|---|
| > 0 | 48 | 8 |
| > 0 (AFIB or AFLT) | 104 | 12 |
| = 100 (definite) | 26 | ~4 |

The protocol planned for the headline required N >= 87 AFIB-positive records in the held-out fold for 80 % power to detect a 21 pp PPV improvement (the design effect derived from the BASEL 17-21 % inconclusive-rate anchor). The actual held-out count is 8 (AFIB only) or 12 (AFIB + AFLT). This is approximately 10x underpowered.

## Root cause

The original admission advisory (defensibility critic a52506) cited "~303 AFIB records adequate for 21 pp PPV improvement (N required = 87)." That figure came from the PTB-XL benchmark paper (Strodthoff 2020), which reported class counts under the `diagnostic_superclass` aggregation (NORM / MI / STTC / CD / HYP). AFIB is a RHYTHM label in the PTB-XL SCP-ECG hierarchy (scp_statements.csv: `rhythm=1.0`, `diagnostic_class=NaN`) and does not appear in the diagnostic-superclass counts. The two label namespaces were conflated.

## Four candidate paths and why Path C was chosen

**Path A — Widen to "any rhythm abnormality":** brings positive count to ~1000+ in PTB-XL. Retains dataset and model. Problem: loses the AFIB-specific clinical anchor. The BASEL 17-21 % inconclusive rate, the Fitbit Heart Study PPV of 32-34 %, and the entire consumer-wearable-AFib-alert constituency are AFIB-specific. Widening to "any rhythm abnormality" requires identifying a new clinical anchor for PPV-at-fixed-alert-rate. No adequate substitute anchor for "rhythm abnormality in general" was found in the literature with the same real-world PPV motivation. The constituency framing becomes significantly weaker.

**Path B — Switch to diagnostic_superclass (MI vs NORM):** label counts are abundant (~3000+ each). Problem: this is a scope change. The admitted pain is the AFib false-positive burden on wearable users. MI vs NORM is a different clinical problem with a different constituency. The defensibility critic's "N = 87" calculation was made for the AFib PPV claim, not a MI discrimination claim. A scope change to MI vs NORM would require returning to layer 10 for admission review. Not taken.

**Path D — Retire-cancel:** the pain is real (admission passed), and a suitable dataset exists. Retiring is premature.

**Path C — Switch dataset to PhysioNet/CinC 2017 (single-lead):** 8,528 training records, 771 AFIB-positive (class distribution: Normal 5154 / AF 771 / Other 2557 / Noisy 46). A candidate held-out fold of ~850 records contains approximately 77 AFIB positives at the training-set prevalence — within range of the N = 87 target with minor adjustment to the power calculation. More importantly, CinC 2017 is single-lead (12-second AliveCor / Kardia strip). This is wearable-grade ECG, directly analogous to Apple Watch's single-lead ECG recording. The original constituency (Apple Watch / Fitbit users receiving AFib alerts) is better served by single-lead evaluation than 12-lead clinical ECG. The BASEL inconclusive-rate anchor (17-21 %) applies to wearable-grade single-lead devices. The cross-dataset abstention novelty claim is strengthened: training on CinC 2017, evaluating abstention behaviour on a second wearable-grade corpus (CinC 2020 single-lead subset or a held-out CinC 2017 split), is closer to the real deployment scenario than PTB-XL ever was.

**Path C is chosen.**

## What changes

1. Primary dataset: PTB-XL removed. PhysioNet/CinC 2017 becomes the primary dataset.
2. Model family: xresnet1d50 already verified at 0.62 GB VRAM in cross-subject-eeg P-3 run. Retained as primary model. This is a 1D ResNet adapted for single-lead ECG, appropriate for CinC 2017 input (one channel, variable-length ~9-61 s, resampled to 300 Hz or 250 Hz standard).
3. Clinical anchor: retained. "PPV at a fixed alert rate matching the 17-21 % BASEL inconclusive-rate budget" applies to wearable-grade single-lead ECG (which CinC 2017 is).
4. Novelty claim: retained and sharpened. Calibrated abstention on wearable-grade single-lead AFib classification with PPV-at-fixed-alert-rate metric. The CinC 2017 label quality (hand-labeled by expert cardiologists) is higher than PTB-XL's SCP-ECG likelihood fields for rhythm labels.

## What does NOT change

- The core hypothesis: calibrated abstention can improve PPV in a wearable-grade AFib classifier without proportionally sacrificing coverage.
- The primary metric: PPV at a fixed abstention rate calibrated to the BASEL 17-21 % inconclusive budget.
- The held-out discipline: touched once, for the headline.
- The statistical test structure: one-sided test, pre-registered threshold.
- The constituency: Apple Watch / wearable-device AFib users and their clinicians.

## Critic re-pass requirement

This change does not alter the held-out partition beyond selecting a different dataset (CinC 2017 fold structure). However, because the primary dataset changes entirely, a brief critic acknowledgment is required before the protocol is locked. The critic pass is documented in `methodology-critic.md` (to be written after approach and risk-register are stable).
