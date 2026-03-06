from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.io.paths import resolve_data_path


_MAD_REQUIRED_COLUMNS = {
    "parking_id",
    "rounded_hour",
    "occupancy_rate",
    "low_data_coverage",
    "system_blackout",
    "partial_year",
    "year",
    "month",
    "hour",
    "weekday_int",
    "parking_location_category",
}

_LOCATION_CLEAN_REQUIRED_COLUMNS = {
    "parking_id",
    "total_capacity",
}


def _read_parquet_with_schema(path: Path, required_columns: set[str]) -> pd.DataFrame:
    df = pd.read_parquet(path)
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns in '{path}': {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    return df


def read_mad_shortterm(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path("@data/processed/MAD_shortterm.parquet", project_root=project_root)
    return _read_parquet_with_schema(path, _MAD_REQUIRED_COLUMNS)


def read_mad_longterm(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path("@data/processed/MAD_longterm.parquet", project_root=project_root)
    return _read_parquet_with_schema(path, _MAD_REQUIRED_COLUMNS)


def read_parking_location_clean(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path(
        "@data/intermediate/parking_location_clean.parquet", project_root=project_root
    )
    return _read_parquet_with_schema(path, _LOCATION_CLEAN_REQUIRED_COLUMNS)


def read_stationarity_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"name", "adf_p", "kpss_p", "adf_reject_h0", "kpss_reject_h0", "conclusion"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns in '{path}': {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    return df
