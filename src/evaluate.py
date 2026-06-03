"""Evaluation helpers for AMP prediction outputs."""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score


def summarize_predictions(y_true, y_pred, y_score=None) -> dict[str, object]:
    """Return standard binary classification metrics."""
    summary: dict[str, object] = {
        "accuracy": accuracy_score(y_true, y_pred),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, output_dict=True),
    }
    if y_score is not None:
        summary["auc_roc"] = roc_auc_score(y_true, y_score)
    return summary


def load_prediction_csv(path: str) -> pd.DataFrame:
    """Load a paired prediction file with the expected raw-prediction schema."""
    df = pd.read_csv(path)
    required = {"sample_id", "true_label", "pred_label", "pred_score"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    return df

