from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.io.parking_readers import read_longterm_timeseries, read_parking_location, read_shortterm_timeseries
from src.io.paths import resolve_data_path
from src.io.weather_readers import read_weather_cleaned
from src.phase1.events import merge_events_into_mad


def load_mad_inputs(
    paths=None, project_root: Path | None = None, include_events: bool = True
) -> dict[str, pd.DataFrame]:
    root = project_root if project_root is not None else (paths.root if paths is not None else None)
    data = {
        "shortterm": pd.read_parquet(
            resolve_data_path("@data/intermediate/shortterm_cleaned.parquet", root)
        ),
        "longterm": pd.read_parquet(
            resolve_data_path("@data/intermediate/longterm_cleaned.parquet", root)
        ),
        "weather": read_weather_cleaned(root),
        "calendar": pd.read_parquet(
            resolve_data_path("@data/intermediate/calendar_master.parquet", root)
        ),
        "location": read_parking_location(root),
    }
    if include_events:
        events_path = resolve_data_path("@data/intermediate/events_master.parquet", root)
        if events_path.exists():
            data["events"] = pd.read_parquet(events_path)
    return data


def normalize_time_columns(df_st: pd.DataFrame, df_lt: pd.DataFrame, df_w: pd.DataFrame) -> None:
    df_st["rounded_hour"] = pd.to_datetime(df_st["rounded_hour"])
    df_lt["rounded_hour"] = pd.to_datetime(df_lt["rounded_hour"])
    df_w["timestamp"] = pd.to_datetime(df_w["timestamp"])
    df_st["date_only"] = pd.to_datetime(df_st["date_only"]).dt.normalize()
    df_lt["date_only"] = pd.to_datetime(df_lt["date_only"]).dt.normalize()


def prepare_calendar_for_merge(df_cal: pd.DataFrame) -> pd.DataFrame:
    out = df_cal.copy()
    out["date"] = pd.to_datetime(out["date"]).dt.normalize()
    # Keep semantic calendar features; avoid duplicating base temporal columns.
    out = out.drop(columns=["year", "month", "weekday", "is_weekend"], errors="ignore")
    return out


def prepare_location_for_merge(df_loc: pd.DataFrame) -> pd.DataFrame:
    out = df_loc.drop(columns=["created_at"], errors="ignore").copy()
    out = out[out["parking_location_category"].notna()].copy()
    return out


def build_mad_table(
    base_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    calendar_df: pd.DataFrame,
    location_df: pd.DataFrame,
    events_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    out = base_df.merge(
        weather_df.rename(columns={"timestamp": "rounded_hour"}),
        on="rounded_hour",
        how="left",
        validate="many_to_one",
    )
    out = out.merge(
        calendar_df.rename(columns={"date": "date_only"}),
        on="date_only",
        how="left",
        validate="many_to_one",
    )
    out = out.merge(location_df, on="parking_id", how="left", validate="many_to_one")
    if events_df is not None:
        out = merge_events_into_mad(out, events_df, date_col="date_only")
    return out


def add_coverage_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    low_coverage_years = {2018, 2021, 2022}
    out["low_data_coverage"] = out["year"].isin(low_coverage_years).astype("int8")

    blackout_start = pd.Timestamp("2021-06-01")
    blackout_end = pd.Timestamp("2022-07-01")
    out["system_blackout"] = (
        (out["rounded_hour"] >= blackout_start) & (out["rounded_hour"] < blackout_end)
    ).astype("int8")
    out["partial_year"] = (out["year"] == 2026).astype("int8")
    return out


def drop_admin_columns(df: pd.DataFrame) -> pd.DataFrame:
    drop_admin = ["publication_time", "created_at", "date_with_day"]
    return df.drop(columns=drop_admin, errors="ignore")


def merge_quality_report(df: pd.DataFrame, name: str) -> None:
    n_rows = len(df)
    n_nan_occ = int(df["occupancy_rate"].isna().sum()) if "occupancy_rate" in df.columns else -1
    n_nan_loc = (
        int(df["parking_location_category"].isna().sum())
        if "parking_location_category" in df.columns
        else -1
    )
    print(f"MERGE-KWALITEITSRAPPORT — {name}")
    print(f"  rows                     : {n_rows:,}")
    print(f"  NaN occupancy_rate       : {n_nan_occ:,}")
    print(f"  NaN parking_location_cat : {n_nan_loc:,}")


def export_mad_outputs(paths, df_loc_clean: pd.DataFrame, mad_st: pd.DataFrame, mad_lt: pd.DataFrame):
    loc_out = resolve_data_path("@data/intermediate/parking_location_clean.parquet", paths.root)
    out_st = resolve_data_path("@data/processed/MAD_shortterm.parquet", paths.root)
    out_lt = resolve_data_path("@data/processed/MAD_longterm.parquet", paths.root)
    df_loc_clean.to_parquet(loc_out, index=False)
    mad_st.to_parquet(out_st, index=False)
    mad_lt.to_parquet(out_lt, index=False)
    return {"location": loc_out, "mad_shortterm": out_st, "mad_longterm": out_lt}
