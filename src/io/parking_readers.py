from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.io.paths import resolve_data_path


PARKING_LOCATION_COLUMNS = {
    "parking_id",
    "longitude",
    "latitude",
    "created_at",
    "total_capacity",
    "parking_location_category",
}

TIMESERIES_COLUMNS = {
    "parking_id",
    "parking_id_hash",
    "parking_type",
    "kind",
    "publication_time",
    "created_at",
    "year",
    "month",
    "date_only",
    "date_with_day",
    "rounded_hour",
    "hour",
    "weekday_int",
    "weekday_name",
    "day_type",
    "number_of_spaces_override",
    "number_of_occupied_spaces",
    "occupancy_rate",
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


def read_parking_location(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path("@data/raw/parking_location.parquet", project_root=project_root)
    return _read_parquet_with_schema(path, PARKING_LOCATION_COLUMNS)


def read_shortterm_timeseries(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path(
        "@data/raw/timeseries_shortterm.parquet", project_root=project_root
    )
    return _read_parquet_with_schema(path, TIMESERIES_COLUMNS)


def read_longterm_timeseries(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path(
        "@data/raw/timeseries_longterm.parquet", project_root=project_root
    )
    return _read_parquet_with_schema(path, TIMESERIES_COLUMNS)

