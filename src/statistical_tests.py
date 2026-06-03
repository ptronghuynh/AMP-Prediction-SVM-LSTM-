"""Paired statistical tests for model comparison."""

from __future__ import annotations

import numpy as np
from scipy.stats import chi2


def mcnemar_from_predictions(y_true, pred_a, pred_b) -> dict[str, float]:
    """Compute McNemar's test with continuity correction."""
    y_true = np.asarray(y_true)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    a_correct = pred_a == y_true
    b_correct = pred_b == y_true
    n01 = int(np.sum(a_correct & ~b_correct))
    n10 = int(np.sum(~a_correct & b_correct))
    statistic = (abs(n01 - n10) - 1) ** 2 / (n01 + n10) if (n01 + n10) else 0.0
    p_value = float(1 - chi2.cdf(statistic, df=1))
    return {"n01": n01, "n10": n10, "statistic": float(statistic), "p_value": p_value}


def delong_auc_test_placeholder() -> None:
    """Placeholder for DeLong AUC comparison.

    Use fixed-order raw scores for both models before implementing this test.
    """
    raise NotImplementedError("DeLong test requires paired raw scores from identical sample ordering.")

