"""
Spec: 30-implement/shared/eval/abstention.py

Selective classification (abstention) curve utility.

Originating consumer: ecg-ppg-realworld P-4 (3-epoch xresnet1d50
abstention threshold sweep on CinC 2017 dev).
Expected second consumer: any track requiring confidence-threshold
abstention with a coverage / PPV / accuracy trade-off (sleep-staging
confidence stratification, affective-state abstention).

Public API: selective_classification_curve(confidences, correct, coverages)
returns a dict with one entry per requested coverage point: the
threshold that achieves (at least) that coverage and the accuracy on
the committed (non-abstained) subset.
"""

from __future__ import annotations

import numpy as np


def selective_classification_curve(
    confidences: np.ndarray,
    correct: np.ndarray,
    coverages: list[float],
) -> dict:
    """Compute the selective-classification (coverage / accuracy) curve.

    Parameters
    ----------
    confidences : (N,) array of float
        Per-record confidence scores (e.g. max-softmax). Higher = more
        confident.
    correct : (N,) array of bool / {0,1}
        Whether the prediction at that record is correct.
    coverages : list of float
        Target coverages in (0, 1]. For each target, return the highest
        threshold T s.t. fraction(confidence >= T) >= target_coverage,
        and accuracy on the committed subset.

    Returns
    -------
    dict with keys:
        - "n_total": int, number of records.
        - "auc_correctness": float | None, AUROC of confidence vs
          correctness (None if `correct` is constant).
        - "points": list of per-coverage dicts:
            - "target_coverage": float
            - "achieved_coverage": float
            - "threshold": float
            - "n_committed": int
            - "accuracy_on_committed": float | None
        - "coverage_full": dict, coverage=1.0 reference (no abstention).
    """
    confidences = np.asarray(confidences, dtype=float).ravel()
    correct = np.asarray(correct).ravel().astype(bool)
    if confidences.shape[0] != correct.shape[0]:
        raise ValueError(
            f"confidences ({confidences.shape[0]}) and correct ({correct.shape[0]}) "
            "must have matching length."
        )
    n = int(confidences.shape[0])
    if n == 0:
        return {
            "n_total": 0,
            "auc_correctness": None,
            "points": [],
            "coverage_full": None,
        }

    # AUROC of confidence as predictor of correctness.
    try:
        from sklearn.metrics import roc_auc_score

        if correct.any() and not correct.all():
            auc_correctness = float(roc_auc_score(correct.astype(int), confidences))
        else:
            auc_correctness = None
    except ImportError:
        auc_correctness = None

    # Sort confidences descending; for each target coverage, take the
    # smallest k s.t. k/n >= target_coverage and pick the threshold = the
    # k-th largest confidence (inclusive).
    order = np.argsort(-confidences, kind="stable")
    conf_sorted = confidences[order]
    correct_sorted = correct[order]

    coverage_full_acc = float(correct.mean()) if n > 0 else None

    points = []
    for target in coverages:
        if target <= 0.0 or target > 1.0:
            points.append(
                {
                    "target_coverage": float(target),
                    "achieved_coverage": None,
                    "threshold": None,
                    "n_committed": 0,
                    "accuracy_on_committed": None,
                    "error": "target_coverage must be in (0, 1]",
                }
            )
            continue

        # Number of records to keep so coverage >= target.
        k = int(np.ceil(target * n))
        k = max(1, min(n, k))
        threshold = float(conf_sorted[k - 1])
        # Inclusive: anything with confidence >= threshold is committed.
        committed_mask = confidences >= threshold
        n_committed = int(committed_mask.sum())
        achieved_coverage = float(n_committed / n)
        if n_committed > 0:
            acc_committed = float(correct[committed_mask].mean())
        else:
            acc_committed = None

        points.append(
            {
                "target_coverage": float(target),
                "achieved_coverage": achieved_coverage,
                "threshold": threshold,
                "n_committed": n_committed,
                "accuracy_on_committed": acc_committed,
            }
        )

    coverage_full = {
        "target_coverage": 1.0,
        "achieved_coverage": 1.0,
        "threshold": float(conf_sorted[-1]) if n > 0 else None,
        "n_committed": n,
        "accuracy_on_committed": coverage_full_acc,
    }

    return {
        "n_total": n,
        "auc_correctness": auc_correctness,
        "points": points,
        "coverage_full": coverage_full,
    }
