from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def get_train_mask(df):
    """Canonical train mask used across EDA/modeling notebooks."""
    return (
        (df["low_data_coverage"] == 0)
        & (df["system_blackout"] == 0)
        & (df["partial_year"] == 0)
        & (df["year"] >= 2020)
        & (df["year"] != 2025)
    )


def apply_train_mask(df):
    """Return a filtered copy using the canonical train mask."""
    return df.loc[get_train_mask(df)].copy()


def standardize_columns(df):
    """Normalize column names for notebook interoperability."""
    out = df.copy()
    out.columns = [c.strip().lower().replace(" ", "_") for c in out.columns]
    return out
