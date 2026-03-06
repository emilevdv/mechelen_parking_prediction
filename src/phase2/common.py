from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_train_mask(
    df: pd.DataFrame,
    min_year: int = 2020,
    excluded_years: tuple[int, ...] = (2025,),
    require_quality_flags: bool = True,
) -> pd.Series:
    required = {"year", "low_data_coverage", "system_blackout", "partial_year"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns for train mask: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    mask = df["year"] >= min_year
    if excluded_years:
        mask &= ~df["year"].isin(excluded_years)
    if require_quality_flags:
        mask &= df["low_data_coverage"].eq(0)
        mask &= df["system_blackout"].eq(0)
        mask &= df["partial_year"].eq(0)
    return mask


def apply_train_filter(
    df: pd.DataFrame,
    min_year: int = 2020,
    excluded_years: tuple[int, ...] = (2025,),
    require_quality_flags: bool = True,
) -> pd.DataFrame:
    mask = build_train_mask(
        df,
        min_year=min_year,
        excluded_years=excluded_years,
        require_quality_flags=require_quality_flags,
    )
    return df.loc[mask].copy()


def add_tier_column(
    df: pd.DataFrame,
    source_col: str = "parking_location_category",
    target_col: str = "tier",
) -> pd.DataFrame:
    if source_col not in df.columns:
        raise ValueError(f"Column '{source_col}' not found.")

    out = df.copy()
    out[target_col] = (
        out[source_col]
        .astype(str)
        .replace({"rand": "vesten_of_rand", "vesten": "vesten_of_rand"})
    )
    return out


def add_day_type_3(
    df: pd.DataFrame,
    weekday_col: str = "weekday_int",
    holiday_col: str = "is_national_holiday",
    target_col: str = "day_type_3",
) -> pd.DataFrame:
    required = {weekday_col, holiday_col}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns for day_type_3: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    out = df.copy()
    out[target_col] = "weekday"
    out.loc[out[weekday_col] == 5, target_col] = "saturday"
    out.loc[(out[weekday_col] == 6) | (out[holiday_col] == 1), target_col] = "sunday_holiday"
    return out


def add_season_column(
    df: pd.DataFrame,
    month_col: str = "month",
    target_col: str = "season",
) -> pd.DataFrame:
    if month_col not in df.columns:
        raise ValueError(f"Column '{month_col}' not found.")

    season_map = {
        12: "winter",
        1: "winter",
        2: "winter",
        3: "lente",
        4: "lente",
        5: "lente",
        6: "zomer",
        7: "zomer",
        8: "zomer",
        9: "herfst",
        10: "herfst",
        11: "herfst",
    }
    out = df.copy()
    out[target_col] = out[month_col].map(season_map)
    return out


def get_eda_figure_dir(paths, notebook_code: str) -> Path:
    out = paths.figures / "eda" / notebook_code
    out.mkdir(parents=True, exist_ok=True)
    return out
