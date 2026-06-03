"""Preprocessing helpers for AMP prediction experiments."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"ID", "Label", "Sequence"}


def load_feature_table(path: str | Path) -> pd.DataFrame:
    """Load a feature CSV and validate the minimum manuscript columns."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def label_to_binary(label: str) -> int:
    """Map manuscript labels to binary AMP class labels."""
    normalized = str(label).strip().lower()
    if normalized == "amp":
        return 1
    if normalized in {"namp", "non-amp", "non_amp"}:
        return 0
    raise ValueError(f"Unknown label: {label!r}")


def add_binary_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a `y` column where AMP=1 and nAMP=0."""
    out = df.copy()
    out["y"] = out["Label"].map(label_to_binary)
    return out

