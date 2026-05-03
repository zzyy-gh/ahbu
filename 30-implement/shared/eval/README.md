> **Spec:** originating-track promotion event (ecg-ppg-realworld P-4) + expected second-consumer (sleep-staging or affective-state confidence stratification).

# `shared/eval/` — selective classification utilities

This is the **first promotion** to `30-implement/shared/`. Per the
CLAUDE.md "promote eagerly once >=1 plausible second consumer exists"
discipline.

## Promotion event

- **Originating track / consumer:** `ecg-ppg-realworld` pilot P-4
  (3-epoch xresnet1d50 + temperature scaling + abstention sweep on
  CinC 2017 dev validation hold-out). The `pilots-README.md#P-4`
  spec calls this utility out by name as
  `30-implement/shared/eval/abstention.py:selective_classification_curve()`,
  so the abstraction is established at design time, not opportunistically.
- **Expected second consumer:** any track that surfaces a
  PPV-vs-coverage or selective-classification figure. Concrete near-term
  candidates:
  - `sleep-staging` — confidence stratification on epoch-level stage
    predictions (a candidate finding from that track's protocol-lock).
  - `affective-state` — abstention on uncertain emotion classifications
    (mentioned in that track's risk register).
- **Headline consumer (this track):** `ecg-ppg-realworld` headline
  also calls this utility through `code/headline/` to compute the
  PPV-at-coverage curve for the AF-vs-rest binary task.

## Files

- `abstention.py` — `selective_classification_curve(confidences,
  correct, coverages)` returning per-coverage threshold,
  achieved coverage, n_committed, and accuracy on the committed
  subset. Also returns the AUROC of confidence vs correctness as a
  summary statistic (the "confidence-correctness AUC" in P-4 success
  criteria).
- `ppv_at_coverage.py` — `ppv_at_coverage(y_true, y_pred,
  confidences, coverages, bootstrap_n=2000, bootstrap_seed=42)`
  returning per-coverage PPV with stratified bootstrap 95% CI. PPV is
  computed on the predicted-positive subset within the committed set.
- `__init__.py` — re-exports both functions.

## Usage

```python
from shared.eval import selective_classification_curve, ppv_at_coverage

# Confidence vs correctness (per-record max-softmax; binary correct flag).
sc = selective_classification_curve(
    confidences=conf_array,            # shape (N,)
    correct=correct_array,             # shape (N,)
    coverages=[1.00, 0.95, 0.90, 0.85, 0.83, 0.79],
)
print(sc["auc_correctness"])           # confidence-correctness AUROC
for p in sc["points"]:
    print(p["target_coverage"], p["accuracy_on_committed"])

# PPV at coverage, with stratified bootstrap CI.
ppv = ppv_at_coverage(
    y_true=y_true_binary,
    y_pred=y_pred_binary,
    confidences=conf_array,
    coverages=[1.00, 0.95, 0.83],
)
for p in ppv["points"]:
    print(p["target_coverage"], p["ppv"], p["ppv_ci95_lo"], p["ppv_ci95_hi"])
```

## Conventions

- All inputs are `np.ndarray` shape `(N,)`.
- "Confidence" is convention-free: any score where higher = more
  confident works. For softmax classifiers the typical choice is
  `max(softmax(logits / T))` where T is a fitted temperature.
- "Correct" is `(y_pred == y_true)` (multi-class) or `(y_pred ==
  y_true)` over the binary projection — the caller decides the
  binarisation upstream.
- For PPV, the predicted-positive subset is determined by the
  caller's `y_pred`, not by the confidence ranking. Confidence is
  used only to set the coverage threshold.
- Bootstrap is stratified by `y_true` to preserve prevalence in the
  CI; this matches the protocol-lock §5 convention for
  ecg-ppg-realworld.
