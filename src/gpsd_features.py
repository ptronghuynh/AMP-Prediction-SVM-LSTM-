"""GPSD feature utilities.

The released `features.csv` already contains the selected 126 GPSD descriptor
columns. This module provides helpers for selecting those columns consistently.
"""

from __future__ import annotations

import pandas as pd


NON_FEATURE_COLUMNS = {"ID", "Label", "Sequence", "y"}


def gpsd_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return descriptor columns from a loaded feature table."""
    return [col for col in df.columns if col not in NON_FEATURE_COLUMNS]


def split_features_labels(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split a prepared table into GPSD features and binary labels."""
    if "y" not in df.columns:
        raise ValueError("Expected a binary label column named `y`.")
    return df[gpsd_feature_columns(df)], df["y"]

