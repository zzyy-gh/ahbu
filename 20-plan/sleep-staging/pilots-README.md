> **Spec:** `10-pain-point/sleep-staging/admission.md`

# Pilot probes — sleep-staging

**Status:** Not pre-registered. Pilots use dev split ONLY.
They do not touch the held-out test partitions (77 HMC PSG test subjects for scope b,
~1,850 MESA test subjects for scope a, as defined in protocol-lock.md §3).
Results here may inform final design choices but do not constitute headline results.

Pilot numbering is track-local (P-1 through P-N); does not share the cross-subject-eeg
pilot numbering.

Run pilots in priority order. P-1 is critical-path for scope (b). P-7 is critical-path
for scope (a) and can run in parallel with P-1.

**Revision 2026-05-03:** P-1 updated to reflect HMC PSG open-access confirmation and
revised failure path. P-7 added for NSRR token validation.

---

## P-1 — HMC PSG access confirmation + ECG channel quality check (CRITICAL for scope b, week 1)

**Question:** (a) Is HMC PSG accessible without credential barriers (expected: yes,
open CC-BY access confirmed 2026-05-03)? If it is blocked for any local/institutional
reason, is CAP Sleep accessible as substitute? (b) Of a 10-subject sample, how many
have ECG SQI >= 0.5 on > 70 % of 30-second windows?

**Why this is still run despite open-access confirmation:** Open-access license does not
guarantee that the download will work in the user's environment (network filtering,
PhysioNet account configuration, incomplete download). P-1 confirms the full pipeline
from download to ECG channel extraction before committing to HMC PSG as the primary
dataset.

**Dataset/split:**
Primary attempt: HMC PSG, all 154 subjects available for download. Sample 10 subjects
(first 10 alphabetically by subject ID) for the ECG quality check.
Fallback attempt (P-1b, only if primary fails): CAP Sleep, 10-subject sample from the
108 subjects.

**Procedure — primary (HMC PSG):**
1. Download the first 10 subject EDF files from https://physionet.org/content/hmc-sleep-staging/1.0.0/.
2. Confirm the access tier (CC-BY download should complete without credential prompts).
   Record in `30-implement/sleep-staging/runs/hmc_access_tier.txt`.
3. Load ECG channel (channel name "ECG" or "EKG" per header) via MNE `read_raw_edf()`.
4. Compute SQI: `nk.ecg_quality()` on each 30-second window. Compute fraction above 0.5.
5. Report per-subject ECG presence, SQI fraction, sampling rate.

**Procedure — fallback P-1b (CAP Sleep, only if HMC access fails):**
1. Download 10 subject EDF files from https://physionet.org/content/capslpdb/1.0.0/.
2. Load ECG channel; apply same SQI computation.
3. Load the hypnogram annotation file; apply R&K-to-AASM mapping
   `{S1→N1, S2→N2, S3→N3, S4→N3, MT→None}`. Verify label distribution is plausible.
4. Report per-subject results.
5. If CAP passes P-1b success criterion: activate R-2 substitution path (write
   `runs/cap_substitute_activation.txt`). Update partition freeze per protocol-lock.md §3.

**Success criteria:**
(a) Primary: HMC access completes within 1 hour; >= 8/10 subjects have > 70 % ECG windows
    above SQI threshold. This is the expected outcome given open-access confirmation.
(b) Fallback: CAP access completes within 1 hour; >= 8/10 subjects have ECG; R&K label
    distribution after mapping is plausible (N2 dominant, < 15 % W, > 10 % REM).

**Script:** `30-implement/sleep-staging/code/pilots/p1_hmc_access_check.py` (existing;
script is compatible with both HMC PSG and CAP Sleep — pass `--dataset cap` flag if
running fallback). Update script to add `--dataset` argument if not already present.

**Estimated time:** 2 hours (including download of 10-subject sample for primary;
additional 1 hour for fallback if triggered).

**Result field:** [FILL AFTER RUN]

---

## P-2 — Dreem-DOD label loading smoke test (week 2)

Unchanged from original pilots-README.md. Lower priority now that MESA is available
as scope (a) primary dataset. Still run in week 2 to confirm Dreem-DOD-O is usable
for P-6 framing probe.

**Dataset/split:** Dreem-DOD-O, 3-subject sample. Dev use only.

**Procedure:** Load JSON annotation file. Check epoch count, consensus label field,
stage distribution. Align with EEG timestamps. Repeat for 3 subjects.

**Success criterion:** All 3 subjects have loadable annotations with valid consensus
label and correct epoch count. Zero NaN labels.

**Estimated time:** 1.5 hours.

**Result field:** [FILL AFTER RUN]

---

## P-3 — U-Sleep VRAM probe and inference correctness check (week 2)

Unchanged from original pilots-README.md. Critical for both scopes (U-Sleep is the
EEG model for scope b and the only model for scope a).

**Dataset/split:** Sleep-EDF Cassette, 2-subject sample. Dev use only.

**Additional scope-a check:** After confirming correctness on Sleep-EDF, run on 1 MESA
sample subject (downloaded in P-7) to verify U-Sleep handles MESA channel configuration
(C4-M1 as primary EEG channel; confirm this is in U-Sleep's supported channel list or
select an appropriate substitute channel from MESA's montage).

**Success criteria:**
(a) Peak VRAM <= 3 GB at batch=32.
(b) Per-epoch probabilities valid.
(c) Sanity-check macro-F1 > 0.60 on Sleep-EDF 2-subject sample.
(d) MESA channel compatibility confirmed (no channel-not-found errors).

**Estimated time:** 2.5 hours (0.5 hr additional for MESA channel check).

**Result field:** [FILL AFTER RUN]

---

## P-4 — Within-subject RF ceiling vs cross-subject RF gap (week 3)

Unchanged from original pilots-README.md. Operates on HMC PSG dev subjects (77).
Temporal within-subject split 80/20. Compare within-subject macro-F1 vs cross-subject
LOSO macro-F1 on dev split.

**Estimated time:** 1 hour.

**Result field:** [FILL AFTER RUN]

---

## P-5 — LSTM on HRV sequence (temporal context probe, week 3)

Unchanged from original pilots-README.md. Operates on HMC PSG dev subjects. LOSO on
dev split. Compare LSTM macro-F1 to RF macro-F1 on dev.

If LSTM macro-F1 > RF + 3 pp: document "temporal context is beneficial" and consider
unlock note to add LSTM as a pre-registered arm. If gap < 3 pp: RF is sufficient.

**Estimated time:** 3 hours.

**Result field:** [FILL AFTER RUN]

---

## P-6 — Scope (a) framing probe: U-Sleep on Dreem-DOD-O with CI (week 4)

Unchanged from original pilots-README.md, with one revision: this is now explicitly
a framing/calibration probe for MESA, not a substitute for MESA.

**Question:** For Dreem-DOD-O (n=55 OSA subjects), what are U-Sleep per-stage F1
values by AHI band, and what are the 95 % CI widths? This frames the expected MESA
results and surfaces any unexpected U-Sleep failure modes before the large MESA run.

**Revised framing (2026-05-03):** With MESA available, the P-6 result is contextualized
as: "This is what U-Sleep achieves on a small (n=55), underpowered OSA cohort. The MESA
headline will answer the same question at N~1,850." Do not report P-6 results as
headline findings.

**Dataset/split:** Dreem-DOD-O, all 55 subjects. OOD evaluation of frozen U-Sleep.

**Success criterion:** Honesty. CI widths are wide for small strata, reported as such.
The pilot report does not claim powered findings.

**Estimated time:** 3 hours (after P-3 confirms U-Sleep is running).

**Result field:** [FILL AFTER RUN]

---

## P-7 — NSRR token validation + MESA sample download (CRITICAL for scope a, week 1)

**Question:** (a) Is the NSRR API token valid and does it grant access to MESA?
(b) Can a sample MESA subject be downloaded successfully? (c) Does the MESA EDF
contain the expected channels (C4-M1 EEG, ECG, stage annotations)?

**NSRR token security:** The token lives in `.env` as `NSRR_TOKEN` (gitignored). In code:
```python
import os
token = os.environ['NSRR_TOKEN']
```
Never print the token value. Log only the validation result (success/fail), not the
token itself, in `30-implement/sleep-staging/runs/nsrr_token_validation.txt`.

**Procedure:**
1. Load `NSRR_TOKEN` from environment. Confirm it is non-empty.
2. Run a token-test request: `GET https://sleepdata.org/api/v1/me.json?auth_token=<token>`.
   Expected response: 200 OK with JSON containing `authenticated: true` and a username.
   Log `authenticated: true/false` (not the token) to `runs/nsrr_token_validation.txt`.
3. Download 1 MESA subject's EDF file using nsrr-gem:
   `nsrr download mesa/polysomnography/edfs/mesa-sleep-0001.edf --token <token>`
   or equivalent Python requests call. Confirm download completes.
4. Load the EDF via MNE. Confirm: (a) C4-M1 EEG channel present; (b) ECG channel
   present; (c) sampling rate >= 256 Hz for EEG.
5. Load the MESA staging annotation (XML file for the same subject). Confirm 5-class
   AASM labels are parseable and epoch count is ~900–1200.
6. Record channel names, sampling rates, epoch count in `runs/mesa_sample_check.txt`.

**Success criteria:**
(a) Token validation returns `authenticated: true`.
(b) EDF download completes without 403 error.
(c) C4-M1 and ECG channels present. EEG sampling rate >= 256 Hz.
(d) Annotation file parseable; labels are valid AASM stage codes.

If (a) fails: token is invalid or expired. Re-login to sleepdata.org to renew.
Trigger R-1a mitigation immediately.
If (c) fails: MESA channel configuration differs from expected. Examine available EEG
channels and identify the appropriate U-Sleep-compatible channel (U-Sleep requires
a central EEG channel, e.g. C4-M1 or C3-M2). Document the fallback channel in the
approach if needed. This does not halt scope (a) — it adjusts the channel selection.

**Script:** `30-implement/sleep-staging/code/pilots/p7_nsrr_token_validation.py` (new).

**Estimated time:** 1 hour.

**Result field:** [FILL AFTER RUN]

---

## Notes on pilots

- Run P-1 and P-7 in parallel in week 1 — they are independent and both critical-path.
- All pilot results are labeled "dev-split / preliminary" in any logs.
- No pilot result constitutes a headline result.
- If P-1 finds HMC PSG blocked: activate R-2 substitute path; re-freeze protocol-lock.md §3
  with CAP partition; write cap_substitute_activation.txt. Requires unlock note.
- If P-7 finds token invalid: invoke R-1a; attempt token renewal before escalating.
- If P-3 reveals MESA channel incompatibility: update channel selection in approach.md
  (minor change; no unlock note required unless the primary metric definition changes).
- Pilot scripts live in `30-implement/sleep-staging/code/pilots/` when written; each
  script's module docstring references this file's P-N entry.
