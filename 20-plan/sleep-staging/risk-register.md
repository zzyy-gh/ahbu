> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Risk register — sleep-staging

**Track:** sleep-staging
**Date:** 2026-05-02 (initial); revised 2026-05-03
**Author:** methodologist agent
**Status:** revised — see unlock-note-2026-05-03.md

Each risk: description, probability (H/M/L), impact (H/M/L), mitigation, kill criterion.
Kill criteria are threshold-triggered: hitting one stops the affected arm immediately.

The track has two arms — (b) HRV-only primary and (a) pretrained-stager (now co-primary).

---

## R-1 — NSRR DUA not submitted or not received in time (scope a)

**Status: RESOLVED — 2026-05-03**

**Resolution:** NSRR API token is available in the project environment as `NSRR_TOKEN`
in `.env` (gitignored). Token issuance by NSRR confirms that the DUA has been approved.
SHHS and MESA are immediately accessible. The 4-week kill criterion no longer applies.

**What to do at implementation start:** Validate token with a test request (P-7 pilot).
Log token validity confirmation in `30-implement/sleep-staging/runs/nsrr_token_validation.txt`.

**Kill criterion: REMOVED.** The 4-week clock and scope (a) conditional-cancel are
no longer in effect. Scope (a) begins in week 1.

**Residual risk (R-1a, new): NSRR token expires or is invalidated.**
Probability: L. Impact: H for scope (a). Mitigation: validate token at start of every
session that downloads NSRR data. If token is rejected, re-login to sleepdata.org to
renew. Kill criterion: if token cannot be renewed within 3 business days and no MESA data
has been downloaded, defer scope (a) and fall back to scope (b) standalone (same outcome
as the original kill criterion).

---

## R-2 — HMC PSG access requires multi-week DUA or is unavailable

**Status: TRIGGERED and RESOLVED via substitution specification — 2026-05-03**

**Trigger:** User reports uncertainty about credentialed-access timeline.

**Resolution from verification:** HMC Sleep Staging Database is CC BY 4.0 open access.
The PhysioNet page explicitly states "Anyone can access the files … Creative Commons
Attribution 4.0 International Public License." There is no DUA and no multi-week wait.
The original R-2 probability was based on conservative uncertainty about the dataset's
tier; that uncertainty is now resolved.

**Despite resolution, full CAP Sleep substitute specification is included here** because:
(a) the user reported a real access concern in practice, (b) access barriers can arise
from institutional network configurations or PhysioNet account issues independent of
license tier, and (c) having a fully specified substitute eliminates operational delay
if a barrier materializes.

**Updated probability:** L (HMC is open access confirmed; barrier now requires some
local/institutional factor).
**Impact:** H for scope (b).

**Mitigation:**

1. Run P-1 (HMC access check) as the first action in week 1. Record access confirmation
   in `30-implement/sleep-staging/runs/hmc_access_tier.txt`.

2. **If HMC PSG is inaccessible** for any reason after P-1:
   Activate CAP Sleep substitute. CAP Sleep Database at
   https://physionet.org/content/capslpdb/1.0.0/ is ODC-BY open access (confirmed
   2026-05-03). 108 subjects, ECG present in all recordings.

   **CAP-specific preprocessing requirement:** R&K stage labels. Apply standard mapping:
   W→W, S1→N1, S2→N2, {S3, S4}→N3, REM→REM. Implement in a dedicated
   `rk_to_aasm_map()` utility in the track-specific loader. Verify the mapping is
   applied consistently in both training and evaluation.

   **CAP pathology caveat:** Only 4 of 108 CAP subjects have sleep-disordered breathing.
   AHI-band stratification is not feasible. If CAP is activated, the AHI-stratified
   secondary analysis is dropped. Pathology-category stratification (healthy / NFLE /
   RBD / PLM / insomnia / other) replaces it.

   **CAP partition:** 54 dev / 54 test, stratified by pathology category, seed=42.
   Re-freeze protocol-lock.md §3 with CAP-specific partition before any training.

3. Log substitution activation in `30-implement/sleep-staging/runs/cap_substitute_activation.txt`
   before any model training if CAP is activated.

**Kill criterion (unchanged in structure):** If HMC PSG access requires a DUA that will
not be approved within 2 weeks, AND CAP Sleep is also inaccessible (e.g., PhysioNet
entirely down), AND no other substitute dataset with ≥ 54 subjects with ECG channels
is available open-access, retire-cancel scope (b) primary arm. The track may pivot to
scope (a) only if MESA access is confirmed. Document the substitution attempt.

---

## R-3 — ECG channel absent or unusable in HMC PSG subjects

Unchanged from original risk register. SQI threshold > 30 % low-quality windows → exclude.
Exclusion count reported explicitly.

**Supplement for CAP Sleep (if substitute active):** CAP Sleep ECG channels are present
per the dataset description but quality is not documented at per-subject granularity.
Apply the same SQI pipeline. If exclusion reduces usable subjects below 40 in the test
split, downgrade the claim scope as per the original kill criterion.

**Kill criterion (original):** Unchanged. If ECG quality exclusions leave fewer than 40
usable test subjects, either (a) supplement with CAP Sleep data, or (b) report with
explicit underpowered caveat. Does not auto-trigger retire-cancel.

---

## R-4 — U-Sleep checkpoint unavailable or license-incompatible

Unchanged from original risk register.

**Additional note (2026-05-03):** U-Sleep's training corpus (Perslev et al. 2021
supplementary, 16 studies, 15,660 PSGs) must be checked against MESA. If MESA is in
U-Sleep's training data, scope (a) EEG evaluation on MESA is contaminated (the model
saw these subjects during training). This check is required in the pre-run checklist
for scope (a) (protocol-lock.md §6 HEADLINE-A checklist).

**Kill criterion (unchanged):** If no pretrained EEG stager checkpoint can be obtained,
cancel the pretrained-stager comparison from scope (a) and fall back to 1D-ResNet for
scope (b) EEG comparison. If the 1D-ResNet fallback also fails, retire-cancel scope (a)
and proceed with scope (b) alone.

---

## R-5 — U-Sleep inference exceeds 4 GB VRAM on GTX 1650

Unchanged from original risk register. P-3 pilot verifies at batch=32. If > 3 GB:
reduce batch size. If > 3 GB at batch=1: move to Kaggle T4.

**Additional note for MESA-scale inference:** MESA involves ~1,850 test subjects
(~1.85 M epochs). Even at batch=32, this is a multi-day job on GTX 1650. If Kaggle T4
is used for MESA inference, probability arrays (soft predictions per epoch) are
extracted in Kaggle and downloaded locally (~50 MB per subject at 5-class float32
× 1000 epochs = 20 KB; total ~100 MB — download feasible). The headline run is then
the evaluation/statistics step, which runs locally on CPU.

**Kill criterion (unchanged):** If inference fails at all batch sizes locally AND Kaggle
T4 fails within 2 days, cancel the U-Sleep EEG comparison from scope (a) and scope (b).
Scope (b) reports HRV-only RF results without direct EEG comparison, noting the gap
claim cannot be quantified at this resource level.

---

## R-6 — Dreem-DOD download too large for local storage

Unchanged from original risk register. Dreem-DOD (58 GB) is for P-6 framing probe only
— optional given MESA is now available. If local storage is insufficient, Dreem-DOD is
deprioritized; MESA via NSRR is the primary scope (a) dataset regardless.

**Kill criterion (unchanged):** Drop Dreem-DOD OOD probe if inaccessible both locally
and via Kaggle within week 2. Scope (b) and scope (a) MESA are unaffected.

---

## R-7 — HRV features are insufficient to discriminate N1 from N2

Unchanged from original risk register. Expected pre-specified outcome; N1 F1 near zero
is valid and informative. No kill criterion.

---

## R-8 — HRV-only staging matches EEG (scope b null result)

Unchanged from original risk register. Pre-specified defensible-null. No kill criterion.

---

## R-9 — Held-out partition touched prematurely (protocol violation)

Unchanged from original risk register.

**Additional note (2026-05-03):** There are now TWO held-out partitions (HMC PSG test
split for scope b; MESA test partition for scope a). Both are governed by separate
pre-run checklists. The isolation requirement applies to each independently. Subject-ID
lists for each partition are stored in separate files:
- `30-implement/sleep-staging/runs/partition_definition_hmcpsg.json`
- `30-implement/sleep-staging/runs/partition_definition_mesa.json`

**Kill criterion (unchanged):** If a model selection decision was made after seeing
test-split performance for either partition, retire-cancel the corresponding headline.
Applies independently to each scope.

---

## R-10 — Stage label quality in HMC PSG (single-rater labels)

Unchanged from original risk register. Documented limitation; does not affect the paired
EEG-vs-HRV gap claim. No kill criterion.

---

## R-11 — Dreem-DOD multi-rater consensus labels — version compatibility

Unchanged from original risk register. Lower priority now that MESA is available.
Kill criterion: drop Dreem-DOD OOD probe if format incompatibility unfixable in 2 days.

---

## R-12 — CAP Sleep R&K-to-AASM label mapping error (NEW — 2026-05-03)

**Description:** CAP Sleep uses R&K staging (W, S1, S2, S3, S4, REM, plus "MT" for
body movements). If the standard AASM-equivalent mapping (S1→N1, S2→N2, {S3,S4}→N3)
is applied inconsistently between the training set label encoding and the evaluation
label encoding, the classifier will be evaluated on a different label space than it
was trained on, producing artificially degraded results.

**Applies to:** Scope (b) only, and only if CAP Sleep substitute is activated.

**Probability:** M (only if substitute is activated; the mapping itself is well-defined
and standardized, but implementation errors are easy to make in the split of 6 R&K
classes to 5 AASM classes, especially for the body-movement "MT" label).
**Impact:** M — if inconsistent, results are invalid and training must be restarted.

**Mitigation:**
1. Implement `rk_to_aasm_map(stage_label)` as a standalone function with an explicit
   lookup table and a test: `{W→W, S1→N1, S2→N2, S3→N3, S4→N3, REM→REM, MT→None}`.
   MT (body movements) → None means that epoch is excluded from both training and
   evaluation. Document the exclusion fraction.
2. Apply the mapping once, at load time, before any train/test split. Verify the
   label distribution after mapping matches expected proportions (no S3, S4, MT in
   the output).
3. Add an assertion in the training script: `assert set(labels).issubset({'W','N1','N2','N3','REM'})`.

**Kill criterion:** If the R&K-to-AASM mapping produces a label distribution inconsistent
with expected sleep staging proportions (e.g., NREM > 70 % of epochs, or REM < 5 %),
flag as a mapping error and halt before any training. Investigate the loader before
proceeding.

---

## R-13 — MESA storage and download bottleneck (NEW — 2026-05-03)

**Description:** MESA PSG EDF files total approximately 165 GB (2,056 subjects × ~80 MB).
Local disk may not accommodate the full dataset simultaneously. NSRR bandwidth throttling
may also make bulk download impractical in the week-1 timeline.

**Probability:** M (165 GB is a significant local storage requirement; bandwidth to NSRR
servers is unknown).
**Impact:** M — delays scope (a) headline by 1–2 weeks if download is slow.

**Mitigation:**
1. Check local disk space before initiating MESA bulk download. 200 GB free required.
2. If insufficient local storage: download in subject batches. Process each batch
   (ECG/EEG extraction → probability arrays via U-Sleep), save probability arrays
   (~20 KB per subject), delete EDFs. The probability arrays (~40 MB total for 2,056
   subjects) are the only artifact needed for evaluation.
3. If NSRR throttles download to < 5 MB/s: use the nsrr-gem parallel download flag
   or break into batches of 200 subjects/session (each batch ~16 GB, ~1 hr at 5 MB/s).
4. Kaggle fallback: mount NSRR files in a Kaggle notebook (nsrr-gem supports Kaggle
   environments with token injection), extract probabilities in notebook, download
   results. Only if local storage is genuinely insufficient.

**Kill criterion:** If MESA download cannot complete within 2 weeks of week 1 start,
scope (a) headline is delayed but not cancelled. If after 4 weeks only a subset of
MESA subjects has been downloaded and the subset is < 500 subjects, re-evaluate whether
a reduced-N scope (a) analysis (N=500) is adequate for the OSA-stratification claim
(smallest stratum at N=500 × 15 % = ~75 severe OSA subjects — borderline for 10 pp
gap at 80 % power). If N is borderline, report with explicit underpowered caveat.

---

## Summary table (revised)

| ID | Risk | Arm | P | I | Status | Kill criterion |
|---|---|---|---|---|---|---|
| R-1 | NSRR DUA not received | (a) | — | — | **RESOLVED** | Kill removed; residual R-1a (token renewal) |
| R-1a | NSRR token expired/invalid | (a) | L | H | Open | Defer scope (a) if unresolvable in 3 days |
| R-2 | HMC PSG access blocked | (b) primary | L | H | **RESOLVED** (confirmed open); substitute fully specified | Retire-cancel scope (b) if no DUA-free substitute ≥54 subj |
| R-3 | ECG quality exclusions | (b) | M | M | Open | Downgrade claim; supplement with CAP if < 40 test subj |
| R-4 | U-Sleep checkpoint unavailable | (a)/(b) | L–M | H | Open | Fall back to 1D-ResNet; if that fails, cancel EEG comparison |
| R-5 | U-Sleep VRAM > 3 GB | (a)/(b) | M | M | Open | Move to Kaggle T4; if T4 fails, cancel EEG comparison |
| R-6 | Dreem-DOD download impractical | (a) | M | L | Open (lower priority) | Drop Dreem-DOD probe; MESA unaffected |
| R-7 | HRV N1 F1 near zero | (b) | H | L | Open | None — valid pre-specified outcome |
| R-8 | HRV-only matches EEG | (b) | L | L | Open | None — valid pre-specified outcome |
| R-9 | Held-out partition touched prematurely | both | L–M | H | Open | Retire-cancel the affected scope's headline |
| R-10 | Single-rater HMC PSG labels | (b) | H | M | Open | None — documented limitation |
| R-11 | Dreem-DOD format mismatch | (a) | M | L | Open (lower priority) | Drop Dreem-DOD probe if unfixable in 2 days |
| R-12 | CAP R&K-to-AASM mapping error | (b) if substitute active | M | M | **NEW** | Halt training if label distribution implausible |
| R-13 | MESA storage / download bottleneck | (a) | M | M | **NEW** | Delay headline; reduce to N≥500 with caveat if 4 wks elapse |

---

## Retire-cancel triggers (track level)

The entire track retires-cancelled if:

1. **Primary data inaccessible:** HMC PSG and CAP Sleep both inaccessible within 2 weeks,
   AND MESA/SHHS scope (a) data has not been downloaded, leaving no executable scope.

2. **Protocol violation (R-9 severe case):** The held-out partition for any scope was used
   for model selection. Hard cancel for that scope, no recovery.

3. **ECG entirely absent from all accessible datasets:** HRV feature extraction infeasible
   across all datasets. Retire-cancel with documented reason.

In any retire-cancel scenario: write retire-cancel note in `10-pain-point/sleep-staging/admission.md`,
update `10-pain-point/shared/portfolio.md`, tag `v2-sleep-staging-retired-cancelled`. Promote
any reusable substrate (hrv_features.py, calibration.py, cohort_stratifier.py) built before
cancellation if ≥1 plausible second consumer exists.
