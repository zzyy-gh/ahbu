"""
Spec: 30-implement/shared/eval/ppv_at_coverage.py

PPV-at-coverage utility (binary class).

Originating consumer: ecg-ppg-realworld P-4 / headline (AF PPV at
calibrated abstention coverage on CinC 2017).
Expected second consumer: any binary-screening track that needs PPV
reported at multiple coverage operating points with bootstrap CIs.

Public API: ppv_at_coverage(y_true, y_pred, confidences, coverages,
bootstrap_n=2000, bootstrap_seed=42).
"""

from __future__ import annotations

import numpy as np


def _ppv_on_subset(y_true: np.ndarray, y_pred: np.ndarray) -> float | None:
    """PPV = TP / (TP + FP) restricted to predicted-positive records."""
    pos_mask = y_pred == 1
    n_pos = int(pos_mask.sum())
    if n_pos == 0:
        return None
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    return float(tp / n_pos)


def ppv_at_coverage(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    confidences: np.ndarray,
    coverages: list[float],
    bootstrap_n: int = 2000,
    bootstrap_seed: int = 42,
) -> dict:
    """Compute PPV at each requested coverage with a 95% bootstrap CI.

    Coverage is enforced by keeping the top-k highest-confidence
    records (k = ceil(coverage * N)). PPV is computed on the
    predicted-positive subset within those committed records.

    Bootstrap: stratified resample (by y_true) of the committed
    subset, recomputing PPV per resample.

    Returns dict with:
      - "n_total": int
      - "n_positive_true": int
      - "points": list of per-coverage dicts:
          - "target_coverage": float
          - "achieved_coverage": float
          - "threshold": float
          - "n_committed": int
          - "n_predicted_positive": int (within committed)
          - "ppv": float | None
          - "ppv_ci95_lo": float | None
          - "ppv_ci95_hi": float | None
          - "bootstrap_n": int
    """
    y_true = np.asarray(y_true).ravel().astype(int)
    y_pred = np.asarray(y_pred).ravel().astype(int)
    confidences = np.asarray(confidences, dtype=float).ravel()

    if not (y_true.shape == y_pred.shape == confidences.shape):
        raise ValueError(
            "y_true, y_pred, confidences must all have the same shape; got "
            f"{y_true.shape}, {y_pred.shape}, {confidences.shape}"
        )
    n = int(y_true.shape[0])
    if n == 0:
        return {"n_total": 0, "n_positive_true": 0, "points": []}

    rng = np.random.default_rng(bootstrap_seed)
    order = np.argsort(-confidences, kind="stable")
    conf_sorted = confidences[order]

    n_positive_true = int((y_true == 1).sum())

    points = []
    for target in coverages:
        if target <= 0.0 or target > 1.0:
            points.append(
                {
                    "target_coverage": float(target),
                    "error": "target_coverage must be in (0, 1]",
                }
            )
            continue
        k = int(np.ceil(target * n))
        k = max(1, min(n, k))
        threshold = float(conf_sorted[k - 1])
        committed_mask = confidences >= threshold
        n_committed = int(committed_mask.sum())
        achieved_coverage = float(n_committed / n)

        y_true_c = y_true[committed_mask]
        y_pred_c = y_pred[committed_mask]
        n_pred_pos = int((y_pred_c == 1).sum())

        ppv = _ppv_on_subset(y_true_c, y_pred_c)

        if ppv is None or n_committed == 0 or bootstrap_n <= 0:
            ppv_lo = ppv_hi = None
        else:
            # Stratified-by-y_true bootstrap: resample positives and
            # negatives separately to preserve prevalence in CI.
            pos_idx = np.where(y_true_c == 1)[0]
            neg_idx = np.where(y_true_c == 0)[0]
            ppvs: list[float] = []
            for _ in range(int(bootstrap_n)):
                if len(pos_idx) > 0:
                    rs_pos = rng.choice(pos_idx, size=len(pos_idx), replace=True)
                else:
                    rs_pos = pos_idx
                if len(neg_idx) > 0:
                    rs_neg = rng.choice(neg_idx, size=len(neg_idx), replace=True)
                else:
                    rs_neg = neg_idx
                rs = np.concatenate([rs_pos, rs_neg])
                ppv_b = _ppv_on_subset(y_true_c[rs], y_pred_c[rs])
                if ppv_b is not None:
                    ppvs.append(ppv_b)
            if ppvs:
                ppv_lo = float(np.percentile(ppvs, 2.5))
                ppv_hi = float(np.percentile(ppvs, 97.5))
            else:
                ppv_lo = ppv_hi = None

        points.append(
            {
                "target_coverage": float(target),
                "achieved_coverage": achieved_coverage,
                "threshold": threshold,
                "n_committed": n_committed,
                "n_predicted_positive": n_pred_pos,
                "ppv": ppv,
                "ppv_ci95_lo": ppv_lo,
                "ppv_ci95_hi": ppv_hi,
                "bootstrap_n": int(bootstrap_n),
            }
        )

    return {
        "n_total": n,
        "n_positive_true": n_positive_true,
        "points": points,
    }
