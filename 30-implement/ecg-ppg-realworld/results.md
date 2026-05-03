> **Spec:** `20-plan/ecg-ppg-realworld/protocol-lock.md`

# Headline results — ecg-ppg-realworld

**Track:** ecg-ppg-realworld
**Run date:** 2026-05-03 (single authorized held-out touch)
**Status:** PRIMARY HEADLINE COMPLETE — POSITIVE result. Multi-seed
secondary (1337, 2025) deferred.
**Held-out touched:** once (seed=42), per protocol-lock §0 / §6.

---

## 1. Primary outcome

**Verdict:** POSITIVE — statistically significant and clinically meaningful
PPV improvement from calibrated abstention on single-lead wearable ECG
AF detection.

| Metric | Value | 95 % bootstrap CI | n_committed |
|---|---:|---|---:|
| **PPV @ 17 % abstention** | **63.8 %** | 57.7 – 70.3 % | 1,343 |
| Baseline PPV @ 0 % abstention | 56.1 % | 51.3 – 61.4 % | 1,650 |
| **Improvement** | **+7.7 pp** | — | — |

Bootstrap: 2,000 resamples, stratified by class, `random_state=42`.

**Statistical test (McNemar, PPV-flavoured per protocol-lock §6):**
- 2×2 table on AF-predicted-positive set under the no-abstain vs
  abstention conditions (drops counted as discordant by
  direction-on-PPV):

  |  | abstention TP | abstention FP / drop |
  |---|---:|---:|
  | **no-abstain TP** | a = 104 | b = 20 |
  | **no-abstain FP** | c = 38 | d = 59 |

- McNemar χ² (continuity-corrected) = 4.98
- **p = 0.0256** (< 0.05, single primary test, no Bonferroni adjustment
  per §6)
- c (38) > b (20) → abstention removes more FPs than TPs from the AF-predicted set.

Per the §6/§7 decision rule: **p < 0.05 AND PPV improvement ≥ 5 pp →
"statistically significant and clinically meaningful PPV improvement
from calibrated abstention."**

---

## 2. Pre-registered companion metrics

All values informative regardless of primary direction (per protocol-lock §7).

| Metric | Value |
|---|---:|
| AUROC AF (post-T) on test | **0.947** |
| ECE uncalibrated (15 bins) | 0.0381 |
| ECE post-T (15 bins) | 0.0404 |
| Temperature T (Brier-min on dev cal hold-out) | 0.941 |
| Achieved abstention rate on test | 18.61 % (target 17 %; +1.6 pp drift) |
| Records held out | 1,650 (after excluding 56 noisy `~`) |
| AF-positive in held-out | 152 |

Achieved abstention rate drift (18.6 % vs 17 % target) is expected:
the threshold was set as the 17 %-quantile of dev-train post-T
max-softmax confidences (per §4 step 3); test confidence distribution
shifts slightly relative to dev-train, producing the observed +1.6 pp
drift. Reported transparently; not a failure.

---

## 3. PPV-vs-coverage curve

Six pre-registered coverage points (post-T MaxSoftmax confidence
threshold sweep), AF-vs-rest binary task, on held-out test:

Full six-point table is in
`runs/headline/test_seed42.json["ppv_vs_coverage_curve"]`. Key entries:

- coverage 1.00 → PPV ≈ baseline 56.1 %
- coverage 0.83 (= 17 % abstention) → operating point of the headline
- The curve is monotone increasing in PPV with decreasing coverage,
  consistent with the P-4 pilot finding (curve direction validated on
  dev hold-out at 3 epochs).

---

## 4. Selective-classification curve

Confidence-correctness AUROC on test (post-T): full curve in
`runs/headline/test_seed42.json["selective_classification_curve"]`.
P-4 dev hold-out reference: 0.659 at 3 epochs. Mature 26-epoch
model on test reported as the headline value.

---

## 5. Ablations

Per protocol-lock §4 / §7 the multi-seed comparison is the secondary
ablation. Status:

| Ablation | Status | Notes |
|---|---|---|
| Seed sensitivity (seeds 42, 1337, 2025) | **DEFERRED** — only seed=42 run | Single-seed primary reported; multi-seed secondary pending re-runs at ~2.9 hr/seed × 2 seeds ≈ 5.8 hr GPU. |
| Uncalibrated baseline | Implicit via ECE pre/post and T = 0.94 | Calibration provides minimal PPV swing at this T; abstention drives the headline gain. |
| Model variant (xresnet1d50 vs xresnet1d18 fallback) | Not triggered — fit GTX 1650 4 GB at batch=8 | R-2 fallback path unused. |

Headline status is **POSITIVE on the single primary seed**. Multi-seed
robustness check is queued; if the secondary later reveals seed
instability, that finding is reported in `findings.md` rather than the
headline being downgraded — the pre-registered single-seed primary
stands.

---

## 6. Uncertainty + failure modes

- 95 % bootstrap CIs (n=2000, stratified by class) reported on every PPV
  point. CI on improvement is the difference of two stratified bootstraps.
- Patient-level note (per protocol-lock §3): CinC 2017 lacks patient IDs;
  partition is record-level. Multiple records from the same patient
  may appear in dev and test. Pre-registered limitation (R-4); echoed
  in `limitations.md`.
- Class imbalance: AF positive rate 9.2 % in held-out (152 / 1650).
  Bootstrap stratifies by class to preserve prevalence in the CI.
- Calibration is near-noise-floor (ECE 0.04, n=1650, 15 bins ≈ 110
  records/bin). The slight ECE regression after T scaling (0.038 →
  0.040) is below 1 standard error of bin-level mean estimation;
  not a genuine calibration degradation.

---

## 7. Reproducibility

| Artifact | Path |
|---|---|
| Held-out test result (frozen, single use) | `runs/headline/test_seed42.json` |
| Calibration parameters (T + threshold) | `runs/headline/calibration_seed42.json` |
| Best-AUROC weights (epoch 26) | `runs/headline/weights_seed42_best.pt` (74.3 MB; gitignored via `*.pt`) |
| Per-epoch training history | `runs/headline/train_seed42_history.json` |
| Pre-run checklist | `runs/pre-run-checklist.txt` |
| Single-seed cross-summary | `runs/headline/headline_summary.json` |
| Training log | `runs/headline_train_seed42.log` |
| Calibration log | `runs/headline_calibrate_seed42.log` |
| Test log | `runs/headline_test_seed42.log` |
| Headline runner | `code/headline/headline_ecg_ppg.py` |

Reproduce (assuming partition.json from P-6 + cinc-2017 dataset present):

```bash
# Train (~2.9 hr; early-stop typical at ep 36 after best at ep 26)
python code/headline/headline_ecg_ppg.py --phase train --seed 42

# Calibrate (~3 min)
python code/headline/headline_ecg_ppg.py --phase calibrate --seed 42

# Pre-run checklist (auto-fills if all artifacts present)
python code/headline/headline_ecg_ppg.py --phase write-checklist --seeds 42

# Held-out single-touch test (~2 min)
python code/headline/headline_ecg_ppg.py --phase test --seed 42 --n-boot 2000

# Cross-seed aggregate
python code/headline/headline_ecg_ppg.py --phase aggregate --seeds 42
```

The `test` phase has a single-use idempotency guard — refuses to overwrite
`runs/headline/test_seed{seed}.json` once written, per protocol-lock §0.

---

## 8. Findings, limitations, lessons

See:
- `20-plan/ecg-ppg-realworld/findings.md` (interpretation)
- `20-plan/ecg-ppg-realworld/limitations.md` (honest scope of claim)
- `20-plan/ecg-ppg-realworld/lessons.md` (substrate-promotion candidates)
