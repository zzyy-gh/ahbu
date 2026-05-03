> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Approach — sleep-staging

**Track:** sleep-staging
**Date:** 2026-05-02 (initial); revised 2026-05-03
**Author:** methodologist agent
**Status:** revised — unlock-note-2026-05-03.md; pending critic gate before layer 30 headline

---

## Scope decision (revised 2026-05-03)

Two scopes evaluated by the defensibility critic prior to admission:

**(a) Clinical-population stratified evaluation of pretrained stagers.**
Originally framed as fragile unless NSRR DUA arrived within 4 weeks.

**Revision (2026-05-03):** NSRR API token is now available in `.env` as `NSRR_TOKEN`
(gitignored; never printed or committed). Token issuance by NSRR confirms DUA approval.
SHHS and MESA are immediately accessible. Scope (a) is elevated from "conditional stretch
arm" to **co-primary headline** alongside scope (b).

**(b) HRV-only EEG-less staging.**
Defensible-null at HMC PSG scale (154 subjects). Independently feasible with no
administrative dependency.

**HMC PSG access clarification (2026-05-03):** Fetching the dataset page directly confirms
HMC Sleep Staging Database is released under Creative Commons Attribution 4.0 International
— open access, no DUA or credentialed sign-up required. The original R-2 risk description
was conservative. Scope (b) proceeds on HMC PSG as planned.

**Decision: pursue BOTH scopes as co-primary arms.** Scope (b) remains the primary arm for
the EEG-vs-HRV gap question. Scope (a) is now an equally funded headline arm for the
clinical-population OSA-stratification question. Both can run in week 1 without administrative
gates. The two headline experiments are independent (different datasets, different held-out
partitions, different primary metrics).

---

## Shared substrate

### Scan result

`30-implement/shared/` does not exist. The cross-subject-eeg track is ahead of sleep-staging
and has declared four promotion candidates (`leakage_audit.py`, `fewshot_curve.py`,
`partition.py`, `riemannian_baseline.py`) but has not yet materialized them in shared/.
This track is the first to materialize HRV-specific substrate.

The cross-subject-eeg `approach.md` also declares `partition.py` (`subject_disjoint_split`
+ `validate_partition`). This track will consume that interface once it is promoted; in the
meantime the sleep-staging track implements its own subject-disjoint split locally with the
same signature so that promotion is a drop-in.

### Consume

**From `30-implement/shared/eval/partition.py`** (to be promoted by cross-subject-eeg or by
this track, whichever runs first): `subject_disjoint_split` and `validate_partition`. If the
shared module exists at implementation time, import it. If not, implement locally and promote
from sleep-staging.

**No other shared substrate to consume.** The calibration and cohort-stratifier utilities do
not yet exist in shared/ — this track builds them.

### Promote on completion

**1. `30-implement/shared/data/hrv_features.py`**

HRV feature extraction from R-R interval sequences. UNIQUE to this track. Consumed by
ecg-ppg-realworld (HRV validity sub-scope), affective-state (cardiac feature arm),
cross-subject-eeg (if an ECG-based sleep arm is added).

```python
def extract_hrv_features(
    rr_ms: np.ndarray,          # R-R intervals in milliseconds
    window_sec: float = 300.0,  # analysis window length
    step_sec: float = 30.0,     # step between windows
    fs_hr: float = 4.0,         # resampling rate for spectral analysis
    epoch_label: str | None = None,
) -> pd.DataFrame:
    """
    Returns DataFrame with one row per window.
    Columns: mean_rr, sdnn, rmssd, pnn50, lf_power, hf_power,
    lf_hf_ratio, vlf_power, tp_power, sd1, sd2.
    Requires: neurokit2 >= 0.2.0 or scipy + numpy fallback.
    """

def align_hrv_to_epochs(
    hrv_df: pd.DataFrame,
    epoch_starts_sec: np.ndarray,
    epoch_dur_sec: float = 30.0,
) -> pd.DataFrame:
    """
    Returns one row per sleep epoch (30 s) with HRV features
    interpolated or aggregated from the nearest HRV window.
    """
```

**2. `30-implement/shared/eval/calibration.py`**

Calibration metrics and reliability diagrams. See signatures in original approach.md;
unchanged. Promotes from whichever track runs first (sleep-staging or ecg-ppg-realworld).

**3. `30-implement/shared/eval/cohort_stratifier.py`**

Per-stratum evaluation. See signature in original approach.md; unchanged.

**4. `30-implement/shared/eval/partition.py`**

Co-promotion with cross-subject-eeg. Same interface as declared in cross-subject-eeg
approach.md. If cross-subject-eeg promotes first, consume; if sleep-staging reaches
implementation first, promote from here.

### Track-specific (not promoted)

- Sleep-EDF loader (PSG format; PSG-track-only).
- HMC PSG loader (same).
- CAP Sleep loader (only used if substitute is activated).
- MESA/SHHS NSRR loaders (clinical-track-only at this stage).
- Stage-label mapping utilities (AASM 5-class, 3-class, R&K-to-AASM).
- R-peak detection wrapper around NeuroKit2 `ecg_peaks`.

---

## Dataset

### Primary scope (b): HMC PSG

- **Full name:** Haaglanden Medisch Centrum Sleep Staging Database (Hassan 2023).
- **Access:** Open access. URL: https://physionet.org/content/hmc-sleep-staging/1.0.0/
  License: Creative Commons Attribution 4.0 International. No DUA, no credentialed
  sign-up. Direct download after accepting CC-BY terms (same-session).
  **Confirmation (2026-05-03):** PhysioNet dataset page explicitly states "Anyone can
  access the files … Creative Commons Attribution 4.0 International Public License."
- **Size:** 154 subjects (88 M, 66 F; mean age 53.8 ± 15.4 yr).
- **Modalities:** EEG (F4/M1, C4/M1, O2/M1, C3/M2), EOG ×2, chin EMG, ECG single
  modified lead II. All channels at 256 Hz.
- **Stage labels:** 5-class AASM (W, N1, N2, N3, REM), 30-second epochs.
- **Pathology:** Mixed — includes healthy and subjects with suspected sleep-disordered
  breathing. AHI metadata availability to be confirmed at implementation start.
- **Intended split:** 77 dev / 77 test (50/50), stratified by AHI band, seed=42.
  See protocol-lock.md §3.
- **Power note (unchanged from prior pass, m-3 fix):** N=77 test subjects is modestly
  underpowered for the 17 pp gap test under the two-sample proportion assumption
  (required N ≈ 105). The headline framing leads with CI width on the EEG-vs-HRV
  macro-F1 difference as the primary informative quantity. The paired Wilcoxon
  p-value is secondary. A null at N=77 bounds the gap to < ~17 pp at 80 % power
  — itself a useful constraint.

### Scope (b) substitute if HMC access blocked: CAP Sleep Database

Activated only if P-1 confirms HMC PSG is inaccessible (see pilots-README.md P-1).

- **Full name:** CAP Sleep Database.
- **Access:** PhysioNet, Open Data Commons Attribution License (ODC-BY). Open access,
  no DUA. URL: https://physionet.org/content/capslpdb/1.0.0/
  Confirmed (2026-05-03): "Anyone can access the files."
- **Size:** 108 subjects (16 healthy controls + 92 with various pathologies).
- **Modalities:** EEG (3 or more channels), EOG, chin and tibial EMG, airflow,
  respiratory effort, SaO2, ECG. ECG is present in all recordings.
- **Stage labels:** R&K classification (W, S1, S2, S3, S4, REM). NOT AASM.
  **Label mapping required:** W→W, S1→N1, S2→N2, {S3, S4}→N3, REM→REM.
  This is the standard AASM-equivalent conversion; see R-12.
- **Pathology mix:** 16 healthy, 40 NFLE (nocturnal frontal lobe epilepsy), 22 RBD,
  10 PLM, 9 insomnia, 5 narcolepsy, 4 SDB (sleep-disordered breathing), 2 bruxism.
  **Critical caveat:** CAP Sleep has only 4 SDB subjects. AHI-band stratification
  (one of the secondary analyses from scope b) is not feasible on CAP Sleep as a
  substitute. If CAP is activated, the AHI-stratified analysis is dropped and the
  headline is narrowed to the EEG-vs-HRV gap question only (not the OSA-severity
  decomposition). Pathology-stratified analysis by CAP category (NFLE vs RBD vs
  healthy vs other) replaces AHI stratification as a secondary metric.
- **Intended split (if activated):** 54 dev / 54 test, stratified by pathology category,
  seed=42. Frozen in protocol-lock.md §3.

### Primary scope (a): MESA via NSRR

- **Full name:** Multi-Ethnic Study of Atherosclerosis — Sleep Exam (MESA Sleep).
- **Access:** NSRR (sleepdata.org). DUA approved; access via API token.
  The token is stored in `.env` as `NSRR_TOKEN` (gitignored). In code:
  ```python
  import os
  token = os.environ['NSRR_TOKEN']
  ```
  Use with nsrr-gem (`nsrr download mesa --token <token>`) or direct HTTPS requests
  with `Authorization: Bearer <token>` header. Never print or commit the token value.
- **Size:** 2,056 subjects with PSG data, from the 2010–2012 MESA Sleep Exam.
- **Modalities:** EEG (C4-M1, Oz-Cz, Fz-Cz), EOG bilateral, chin EMG, thoracic and
  abdominal RIP, airflow, ECG single lead, leg movements, SpO2.
- **Stage labels:** AASM v2 scoring (5-class W, N1, N2, N3, REM), 30-second epochs.
  Scored at Brigham and Women's Hospital reading center.
- **Pathology / cohort:** Multi-ethnic (White, Black, Hispanic, Chinese-American).
  AHI available per subject.
- **Intended split:** 90 % test (~1,850 subjects) / 10 % dev (~206 subjects), stratified
  by AHI band and race/ethnicity, seed=42. See protocol-lock.md §3.
- **Scope (a) power story:** Smallest AHI stratum at test time (severe OSA, AHI ≥ 30) is
  approximately 15 % of 1,850 = ~280 subjects. A two-sample proportion test for a 10 pp
  degradation at 80 % power requires N ≈ 170 per stratum. N~280 meets this threshold
  with margin. The analysis is properly powered.

### Secondary dev dataset: Sleep-EDF Cassette v1

Unchanged from original approach.md. Used for EEG preprocessing pipeline testing and
U-Sleep sanity check (P-3). Dev-only. No ECG, no HRV. Not used for any headline.

### Out-of-distribution probe: Dreem-DOD-H and Dreem-DOD-O

Unchanged from original approach.md. Used for U-Sleep OOD calibration framing (P-6).
No ECG — scope (a) only, not scope (b). N=55 OSA subjects remains underpowered for
a scope (a) OSA-stratification headline. Now that MESA is available, Dreem-DOD-O is
a framing pilot (P-6) that contextualizes what MESA will test, not a substitute.

### NSRR SHHS (secondary confirmatory, scope a)

- **Access:** NSRR, same token. URL: https://sleepdata.org/datasets/shhs
- **Size:** ~5,800 subjects (SHHS1 + SHHS2 combined; SHHS1 ~5,800 subject-nights, visit 1).
- **Stage labels:** Rechtschaffen & Kales (8-class). R&K-to-AASM mapping required
  before SHHS can be evaluated with U-Sleep. Mapping: W→W, S1→N1, S2→N2,
  {S3, S4}→N3, REM→REM; Movement, Unscored → excluded.
- **Role:** Confirmatory OSA-stratification replication after MESA headline. Secondary
  only. If SHHS results diverge materially from MESA results, investigate scoring-era
  differences (R&K vs AASM v2).

---

## Preprocessing

### Scope (b) — HRV feature pipeline (primary arm)

Unchanged from original approach.md. Operates on the ECG channel of HMC PSG (or
CAP Sleep if substitute activated). Stages 1–5 as originally specified.

Key parameters: ECG SQI threshold 0.5, exclusion at > 30 % low-quality windows,
ectopic correction via `nk.hrv_sanitize()`, 300-second HRV analysis window, 30-second
step, 11 HRV features per epoch.

### Scope (a) — pretrained stager inference pipeline

Unchanged from original approach.md. EEG loading via MNE, 100 Hz resampling,
epoch extraction, per-epoch normalization, U-Sleep frozen inference.

**Calibration head revision (2026-05-03):** Temperature scaling is NOW fit on a MESA
dev subset (~206 MESA subjects, 10 % carved out before the test partition), not on
Dreem-DOD-H. This corrects the distribution-shift limitation identified by the
methodology critic (m-6 fix). Dreem-DOD-H is used only in P-6 as a framing probe
(which ECE does U-Sleep achieve out-of-the-box on a small OSA cohort before any
calibration). The MESA-calibrated temperature parameter T is the one applied to
the MESA test partition for scope (a) headline.

---

## Model family

### Scope (b) — HRV-only classifier

Unchanged: Random Forest (primary), U-Sleep frozen EEG (comparison), majority-class
(lower bound), LSTM dev-only probe (P-5). See original approach.md for parameters.

### Scope (a) — pretrained stager evaluation

U-Sleep frozen inference on MESA. Temperature scaling calibration head fit on
MESA dev subset. Cohort-stratifier on 4 AHI bands. No new model training.

### Summary table (revised)

| Model | Arm | GPU? | VRAM | Role |
|---|---|---|---|---|
| Random Forest (11 HRV features) | (b) primary | no | 0 | scope (b) headline |
| U-Sleep frozen inference (EEG) | (b) comparison + (a) | yes | ~1–2 GB | EEG gap baseline + scope (a) eval |
| Majority-class classifier | (b) | no | 0 | lower bound |
| LSTM on HRV sequence | (b) dev-only | CPU | < 0.5 GB | P-5 pilot |

---

## Evaluation protocol

Unchanged from original approach.md: subject-disjoint, 3-class primary (scope b),
5-class secondary, bootstrap CI at subject level, cross-subject evaluation only.

### Scope (a) evaluation addition

- Unit of analysis: MESA test subjects (~1,850).
- Stratification: AHI band (none / mild / moderate / severe), race/ethnicity.
- Primary estimand: macro-F1 difference between no-OSA and severe-OSA strata.
- `cohort_stratifier.stratified_report()` applied with stratum_col=ahi_band.
- Bootstrap CI: n=2000 resamples at the subject level, random_state=42.

---

## Ablations

Ablations 1–4 unchanged (run on HMC PSG dev split). See original approach.md.

**Ablation 5 (scope a, new): MESA dev calibration benefit**

Hypothesis: temperature scaling fit on MESA dev subjects substantially reduces ECE on
MESA test subjects; temperature scaling fit on Dreem-DOD-H does not (distribution shift).
This ablation directly tests whether the in-distribution calibration approach (MESA dev)
is worth the extra 10 % subject cost compared to using an out-of-distribution calibration
(Dreem-DOD-H).

Procedure: run U-Sleep on MESA test with (a) no calibration, (b) Dreem-DOD-H temperature
T, (c) MESA-dev temperature T. Compare ECE for all three. Run on dev split only before
the headline test run.

---

## Uncertainty reporting

Unchanged from original approach.md: bootstrap CI at subject level, multi-seed RF check
on dev, CI width as evidence, "X.XX (95 % CI: Y.YY–Z.ZZ, N=…)" format for all headline
numbers.

---

## Compute budget (revised)

| Task | Hardware | Estimated time |
|---|---|---|
| HMC PSG download (~2 GB compressed) | local | 30 min |
| Sleep-EDF download (~1 GB) | local | 15 min |
| Dreem-DOD download (58 GB) | local | 4–8 hr |
| MESA download via NSRR token (~165 GB for EDF files) | local | 12–24 hr (bandwidth-limited) |
| ECG preprocessing + R-peak detection (HMC PSG, 154 subj) | CPU | 2–3 hr |
| HRV feature extraction (154 subj × ~1000 epochs) | CPU | 1–2 hr |
| RF training on 77 dev subjects | CPU | < 5 min |
| RF ablations (4 configs × dev LOSO) | CPU | 30 min |
| U-Sleep inference on HMC PSG (154 subj) | GTX 1650 | 6–10 hr |
| U-Sleep inference on MESA test (~1850 subj) | GTX 1650 | 60–100 hr |
| U-Sleep inference on Dreem-DOD (80 subj) | GTX 1650 | 4–6 hr |
| MESA calibration head fitting (dev subset ~206 subj) | CPU | < 30 min |
| Bootstrap CI scope (b) | CPU | < 30 min |
| Bootstrap CI scope (a) MESA | CPU | 1–2 hr |
| Ablation 5 (calibration comparison) | CPU | < 30 min |
| **HEADLINE-B total** | CPU | **~1 hr** |
| **HEADLINE-A total (MESA inference)** | GTX 1650 | **~80 hr** |

**MESA inference compute note:** 1,850 subjects × ~1,000 epochs = 1.85 M epochs at
batch=32 ≈ 57,800 forward passes. At 0.1 s/batch: ~1.6 hr per 100 subjects, ~29 hr
total on GTX 1650. With overhead and I/O: ~60–100 hr. This is the single largest
compute item. It can be split across multiple sessions; intermediate probability
arrays are saved per-subject.

**MESA storage note:** MESA PSG EDF files are approximately 80 MB per subject × 2,056 =
~165 GB. If local storage is insufficient, use Kaggle (100 GB per dataset) or process
in batches: download, extract U-Sleep probabilities, delete EDF, repeat.

**Fits 4 GB envelope:** estimated yes. U-Sleep inference at batch=32 is
**estimated** at < 2 GB VRAM; **to be confirmed by P-3 before any full
inference run**. P-3 has not yet run (`30-implement/sleep-staging/runs/`
empty as of 2026-05-03). HEADLINE-A and HEADLINE-B inference are gated
on P-3 PASS (success criterion: peak VRAM <= 3 GB at batch=32) per
`protocol-lock.md` §6 pre-run checklists. Verify for MESA channel
configuration as part of P-3 (U-Sleep single-channel mode, same as
HMC PSG).

### Time to first honest result

- Week 1: MESA NSRR token validation (P-7). HMC PSG download + access confirmation.
  ECG preprocessing dev pipeline. HRV feature extraction (dev subjects). RF baseline
  on dev LOSO. MESA sample download (10 subjects for P-7).
- Week 2: U-Sleep inference on Sleep-EDF (P-3), Dreem-DOD-H (P-6 start). MESA bulk
  download begins in background. Ablations 1–3 on HMC dev split.
- Week 3: Headline RF training on 77 HMC dev subjects. Dev multi-seed check.
  MESA dev-subset calibration head fitting (Ablation 5). U-Sleep inference on MESA
  test begins (long-running background job).
- Week 4: HEADLINE-B: single test-split run (HMC PSG, ~1 hr). Bootstrap CIs. Results.
  MESA inference continues.
- Week 5–6: HEADLINE-A: MESA inference completes. Stratified report. Bootstrap CIs.
  Results.

**First honest result (scope b, HEADLINE-B): week 4.**
**First honest result (scope a, HEADLINE-A): week 5–6.**

---

## Novelty and exploration notes

**What is genuinely novel (revised 2026-05-03):**

1. An explicit, pre-registered, same-harness paired EEG-vs-HRV staging comparison on
   HMC PSG (m-7 fix from original — narrowed claim). The novel element is the explicit
   pre-registered paired test with CI-width-led framing; not absence of all prior
   modality comparisons.

2. U-Sleep calibration on a powered clinical cohort (MESA, N~1,850) stratified by
   AHI band and race/ethnicity. U-Sleep calibration on clinical-edge populations is
   not reported in the published U-Sleep papers, and the multi-ethnic component
   (MESA's explicit design feature) adds a dimension absent from most prior PSG studies.

3. The AHI-stratified HRV staging accuracy decomposition (scope b): does HRV-only
   staging degrade more steeply than EEG-based staging as OSA severity increases?
   Pre-registered, honest CI widths.

**What is standard and intentionally so:**
Random Forest on HRV features, U-Sleep, bootstrap CI, 30-second epochs.

**What is exploratory:**
LSTM on HRV (P-5), within-subject ceiling (P-4), Dreem-DOD framing probe (P-6),
MESA calibration ablation (Ablation 5 on dev split).
