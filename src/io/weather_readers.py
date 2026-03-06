from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.io.paths import resolve_data_path


WEATHER_RAW_REQUIRED_COLUMNS = {
    "timestamp",
    "qc_flags",
    "precip_quantity",
    "temp_dry_shelter_avg",
    "wind_speed_10m",
    "wind_gusts_speed",
    "humidity_rel_shelter_avg",
    "pressure",
    "sun_duration",
    "short_wave_from_sky_avg",
    "sun_int_avg",
}

WEATHER_CLEAN_REQUIRED_COLUMNS = {
    "timestamp",
    "temp_c",
    "precip_mm",
    "wind_speed_ms",
    "wind_gusts_ms",
    "humidity_pct",
    "pressure_hpa",
    "sun_duration_min",
    "shortwave_wm2",
    "sun_intensity_wm2",
    "qc_temp",
    "qc_precip",
    "qc_wind_speed",
    "qc_wind_gusts",
    "qc_humidity",
    "qc_pressure",
    "humidity_suspect",
    "sun_duration_inconsistent",
    "precip_imputed",
}


def _read_csv_with_schema(path: Path, required_columns: set[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns in '{path}': {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    return df


def _read_parquet_with_schema(path: Path, required_columns: set[str]) -> pd.DataFrame:
    df = pd.read_parquet(path)
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns in '{path}': {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    return df


def read_weather_raw(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path("@data/raw/aws_1hour-5.csv", project_root=project_root)
    return _read_csv_with_schema(path, WEATHER_RAW_REQUIRED_COLUMNS)


def read_weather_cleaned(project_root: Path | None = None) -> pd.DataFrame:
    path = resolve_data_path(
        "@data/intermediate/weather_cleaned.parquet", project_root=project_root
    )
    return _read_parquet_with_schema(path, WEATHER_CLEAN_REQUIRED_COLUMNS)

