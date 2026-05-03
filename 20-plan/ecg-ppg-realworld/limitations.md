> **Spec:** `30-implement/ecg-ppg-realworld/results.md` + `20-plan/ecg-ppg-realworld/protocol-lock.md`

# Limitations — ecg-ppg-realworld (post-headline)

These are honest scope limitations of the headline claim. Each was
either pre-registered (carried forward from the protocol-lock and
risk-register) or surfaced during execution. Listed in roughly
descending order of how much each constrains downstream readers.

---

## 1. Single seed for primary metric (multi-seed deferred)

**Status:** pre-registered (protocol-lock §4 / §7); secondary deferred
due to GPU time budget.

The pre-registered primary uses seed=42. Multi-seed mean ± std across
seeds {42, 1337, 2025} is the §5 secondary metric and was **not run**
in the headline session — would need ~5.8 hr GPU at the current rate
on the GTX 1650 4 GB envelope (compute.md).

What this means:
- The reported PPV @ 17 % abstention (63.8 %) is a single-seed point
  estimate, not a seed-mean.
- The CI on PPV is the bootstrap CI over **records** at that single
  seed, not over **seeds** + records.
- A single-seed result is consistent with §5 / §7 and the headline
  verdict stands per the pre-registered decision rule.

Mitigation: the secondary multi-seed run is queued and will be
appended to `findings.md` §6 when complete.

## 2. Record-level (not patient-level) partition

**Status:** pre-registered (protocol-lock §3, R-4); inherent to the
CinC 2017 public release.

CinC 2017 v1.0.0 does not include patient identifiers. The dev/test
partition is record-level stratified (`StratifiedShuffleSplit`,
`random_state=42`). Multiple records from the same patient may appear
in both splits.

Effect: a small upward bias on AUROC and PPV vs a true patient-level
test set. Magnitude is bounded by the record-per-patient ratio in
the unobservable patient distribution; CinC 2017 community practice
treats this as a known small effect (~1–3 pp AUROC inflation in
informal comparisons) and not a fatal flaw — but it is a real
limitation of the public release, not a methodology choice.

Mitigation: a patient-IDed re-release would tighten the claim. None
exists at the time of this headline.

## 3. AliveCor Kardia ≠ free-living wrist PPG/ECG

**Status:** scope of dataset; the claim is bounded to AliveCor
Kardia-class devices.

CinC 2017 is "wearable-grade" in the AliveCor Kardia sense:
30-second 300 Hz single-lead recordings collected by a smartphone-
attached pad, with users prompted to take the recording. This is
not the same as continuous Apple Watch / Fitbit PPG-then-ECG flow.
The data has lower motion artifact than wrist-worn continuous PPG.

Effect: the headline claim "calibrated abstention improves PPV in
wearable AF detection" is properly scoped to **single-lead 30s
prompted ECG**. Extension to continuous wrist PPG/PPG-derived ECG
is not tested. The Apple Heart Study and Fitbit Heart Study cited
in protocol-lock §6 use different waveforms and the comparison there
is to *PPV burden*, which is a downstream property; the upstream
abstention mechanism's transferability across waveform-class is an
open question.

## 4. CinC 2017 prevalence ≠ deployed prevalence

**Status:** noted but not pre-registered.

AF positive rate in CinC 2017 working set: 9.1 % overall, 9.2 % in
held-out (152 / 1,650). Deployed wearable AF screening cohorts have
much lower prevalence (Apple Heart Study: 0.5 % among notified;
Fitbit: similar order). PPV at fixed sensitivity falls with falling
prevalence (Bayes' rule).

Effect: the absolute PPV at 17 % abstention (63.8 %) is **specific
to a 9 %-AF-prevalence test set**. The relative-improvement claim
(+7.7 pp) translates to deployment more directly than the absolute
PPV — but neither is a guarantee at deployment prevalence. PPV would
have to be re-measured on a representative deployment cohort.

Mitigation: report relative (Δ pp) alongside absolute PPV; readers
informed about the prevalence gap.

## 5. Achieved abstention rate drift on test (+1.6 pp)

**Status:** documented in `results.md` §2 + `findings.md` §4.

Threshold quantile-fit on dev-train confidences yields 17.0 %
abstention there; same threshold on test gives 18.6 %. Within the
BASEL 17–21 % window, but a transparent +1.6 pp drift.

This means: any reader interpreting the headline as "exactly 17 %
abstention" should mentally adjust to "approximately 17 % ± 2 %
abstention." For PPV-improvement direction, the drift is benign
(more abstention → at-least-as-good PPV per the monotone curve). For
absolute "operate at 17 %" deployment claims, a deployment threshold
would need re-fitting on deployment-distribution data.

## 6. Calibration is near noise-floor on this dev cal hold-out

**Status:** documented in `findings.md` §3.

T = 0.94, ECE 0.038 → 0.040. The model is near-calibrated even
without T-scaling. This *strengthens* the headline (the lift is from
abstention, not from calibration) but it also means the
*temperature-scaling component of the pipeline cannot be empirically
validated on this dev hold-out* — it has nothing to fit. Any future
deployment with substantially different distribution would need its
own calibration check.

## 7. McNemar table semantics

**Status:** explicitly pre-registered (§6 M-2 fix).

The 2×2 table counts AF-predicted records under no-abstain vs
abstention, with **drops counted as discordant cells by direction-on-
PPV** (a no-abstain TP that abstention drops counts as a TP→FP-shaped
discordant cell; a no-abstain FP that abstention drops counts as
FP→TP-shaped discordant).

This deviates from a textbook accuracy-comparing McNemar in a way
that is appropriate for testing a PPV-improvement question. A reader
expecting an accuracy-comparing McNemar will misread the result.
The protocol-lock language is precise but readers should reach for
the formal definition in §6 before re-using the p-value at
face-value.

## 8. CinC 2017 ground truth has known label noise

**Status:** dataset-level limitation; not enumerated in
protocol-lock.

Per the CinC 2017 challenge documentation, the labels are clinician-
adjudicated but rates of disagreement on Other-vs-Normal and
Other-vs-AF in particular are not zero. Label noise propagates into
PPV at a small but non-zero rate. The 7.7 pp PPV improvement is
above this noise floor, but precise calibration of how much of the
gain is "real signal" vs "abstention disproportionately drops
mislabeled records" is not separable here.

## 9. xresnet1d50 is a chosen architecture, not a comparison study

**Status:** pre-registered (§4).

The headline claim is about *calibrated abstention's effect on PPV*,
not about *xresnet1d50's superiority among 1D architectures*. We did
not compare against EEGNet-1D, transformer-based ECG models, or
recent self-supervised baselines. The single-architecture choice was
locked at protocol-lock time and the comparison is not part of this
headline's contract.

A reader interested in "does this work with model X" must run
their own follow-up.

## 10. Patient-disjoint generalization untested

**Status:** consequence of §2 above.

Without patient IDs, we cannot construct a patient-disjoint test
partition to test cross-patient generalization. The within-CinC-2017
record-level held-out test gives a within-distribution generalization
estimate but does not test whether the abstention mechanism's PPV
improvement holds across genuinely unseen patients. The
cross-subject-eeg track holds the cross-subject angle for the AHBU
portfolio; this track tests the calibration / abstention angle.
