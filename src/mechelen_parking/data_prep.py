from __future__ import annotations


def get_quality_mask(df):
    """Canonical data-quality mask (no temporal inclusion/exclusion)."""
    return (
        (df["low_data_coverage"] == 0)
        & (df["system_blackout"] == 0)
        & (df["partial_year"] == 0)
    )


def get_train_mask(df):
    """Canonical train mask used across EDA/modeling notebooks."""
    return get_quality_mask(df) & (df["year"] >= 2020) & (df["year"] != 2025)


def apply_train_mask(df):
    """Return a filtered copy using the canonical train mask."""
    return df.loc[get_train_mask(df)].copy()


def standardize_columns(df):
    """Normalize column names for notebook interoperability."""
    out = df.copy()
    out.columns = [c.strip().lower().replace(" ", "_") for c in out.columns]
    return out


def add_tier_admin(df, source_col: str = "parking_location_category", target_col: str = "tier_admin"):
    """Add a merged admin tier column (`vesten` + `rand` -> `vesten_of_rand`)."""
    out = df.copy()
    out[target_col] = (
        out[source_col].astype(str).replace({"rand": "vesten_of_rand", "vesten": "vesten_of_rand"})
    )
    return out
