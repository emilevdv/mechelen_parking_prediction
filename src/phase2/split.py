from __future__ import annotations

import pandas as pd

from src.io.paths import resolve_data_path


QUALITY_FILTER_COLUMNS = ("low_data_coverage", "system_blackout", "partial_year")


def apply_quality_filter(df: pd.DataFrame) -> pd.DataFrame:
    missing = sorted(set(QUALITY_FILTER_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required quality columns: {missing}. Found columns: {list(df.columns)}"
        )

    quality_mask = (
        (df["low_data_coverage"] == 0)
        & (df["system_blackout"] == 0)
        & (df["partial_year"] == 0)
    )
    return df.loc[quality_mask].copy()


def split_train_holdout(
    df: pd.DataFrame,
    train_years: tuple[int, ...] = (2020, 2023, 2024),
    holdout_year: int = 2025,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if "year" not in df.columns:
        raise ValueError("Missing required column 'year'.")

    train = df[df["year"].isin(train_years)].copy()
    holdout = df[df["year"] == holdout_year].copy()
    return train, holdout


def overlap_count(train: pd.DataFrame, holdout: pd.DataFrame) -> int:
    if not {"parking_id", "rounded_hour"}.issubset(train.columns) or not {
        "parking_id",
        "rounded_hour",
    }.issubset(holdout.columns):
        return len(set(train.index) & set(holdout.index))

    train_keys = set(zip(train["parking_id"], pd.to_datetime(train["rounded_hour"])))
    holdout_keys = set(zip(holdout["parking_id"], pd.to_datetime(holdout["rounded_hour"])))
    return len(train_keys & holdout_keys)


def export_split_outputs(
    train: pd.DataFrame,
    holdout: pd.DataFrame,
    project_root=None,
) -> dict[str, object]:
    out_train = resolve_data_path("@data/processed/train.parquet", project_root)
    out_holdout = resolve_data_path("@data/processed/holdout.parquet", project_root)

    train.to_parquet(out_train, index=False)
    holdout.to_parquet(out_holdout, index=False)
    return {"train": out_train, "holdout": out_holdout}
