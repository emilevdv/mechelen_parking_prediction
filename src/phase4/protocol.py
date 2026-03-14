from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import math
import re
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


DEFAULT_SEED = 20260313
DAY_CLASS_LEVELS = ["weekday_regular", "weekend_regular", "school_vacation", "holiday", "event_day"]
SEASON_LEVELS = ["winter", "lente", "zomer", "herfst"]
SEASON_MAP = {
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

BASE_COLUMNS = [
    "parking_id",
    "rounded_hour",
    "year",
    "occupancy_rate",
    "operational_split",
    "hour",
    "weekday_int",
]


@dataclass(frozen=True)
class Phase4Paths:
    project_root: Path
    split_dir: Path
    phase3_core_tse_dir: Path
    phase3_forecast_l_dir: Path
    phase4_feature_set_dir: Path
    results_dir: Path
    internal_dir: Path
    notebooks_phase4_dir: Path


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "data_processed").exists() and (candidate / "notebooks").exists():
            return candidate
    raise FileNotFoundError("Project root not found")


def get_phase4_paths(project_root: Path | None = None) -> Phase4Paths:
    root = (project_root or find_project_root()).resolve()
    results_dir = root / "data_results" / "phase4"
    internal_dir = results_dir / "internal"
    notebooks_phase4_dir = root / "notebooks" / "phase4"
    results_dir.mkdir(parents=True, exist_ok=True)
    internal_dir.mkdir(parents=True, exist_ok=True)
    notebooks_phase4_dir.mkdir(parents=True, exist_ok=True)
    return Phase4Paths(
        project_root=root,
        split_dir=root / "data_processed" / "phase3_splits",
        phase3_core_tse_dir=root / "data_processed" / "phase3_features" / "core_tse",
        phase3_forecast_l_dir=root / "data_processed" / "phase3_features" / "forecast_l",
        phase4_feature_set_dir=root / "data_processed" / "phase4_feature_sets",
        results_dir=results_dir,
        internal_dir=internal_dir,
        notebooks_phase4_dir=notebooks_phase4_dir,
    )


def ensure_datetime(df: pd.DataFrame, col: str) -> None:
    df[col] = pd.to_datetime(df[col], errors="coerce")


def as_bool_flag(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype(float).gt(0)


def as_int_flag(series: pd.Series) -> pd.Series:
    return as_bool_flag(series).astype(np.int8)


def cyclical_encode(series: pd.Series, period: int) -> tuple[np.ndarray, np.ndarray]:
    vals = pd.to_numeric(series, errors="coerce").astype(float)
    angle = 2.0 * np.pi * (vals % period) / period
    return np.sin(angle), np.cos(angle)


def slugify(value: str) -> str:
    s = str(value).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "unknown"


def qcut_with_fallback(series: pd.Series, q: int, labels: list[str]) -> tuple[pd.Series, np.ndarray]:
    ser = pd.to_numeric(series, errors="coerce")
    try:
        binned, edges = pd.qcut(ser, q=q, labels=labels, retbins=True, duplicates="drop")
    except ValueError:
        edges = np.array([ser.min(), ser.max()], dtype=float)
        binned = pd.cut(ser, bins=edges, labels=labels[:1], include_lowest=True)
    return binned, edges


def cut_using_edges(series: pd.Series, edges: np.ndarray, labels: list[str]) -> pd.Series:
    ser = pd.to_numeric(series, errors="coerce")
    edges_adj = np.array(edges, dtype=float)
    edges_adj = np.unique(edges_adj)
    if len(edges_adj) < 2:
        min_v = float(ser.min()) if pd.notna(ser.min()) else 0.0
        max_v = float(ser.max()) if pd.notna(ser.max()) else min_v + 1.0
        if max_v <= min_v:
            max_v = min_v + 1.0
        edges_adj = np.array([min_v, max_v], dtype=float)
    if len(labels) != len(edges_adj) - 1:
        labels = labels[: len(edges_adj) - 1]
    return pd.cut(ser, bins=edges_adj, labels=labels, include_lowest=True)


def compute_event_cascade_features(
    timestamp_series: pd.Series,
    event_series: pd.Series,
    clip_hours: int = 72,
) -> pd.DataFrame:
    timeline = (
        pd.DataFrame(
            {
                "rounded_hour": pd.to_datetime(timestamp_series, errors="coerce"),
                "event_flag": as_int_flag(event_series),
            }
        )
        .dropna(subset=["rounded_hour"])
        .groupby("rounded_hour", as_index=False)["event_flag"]
        .max()
        .sort_values("rounded_hour")
        .reset_index(drop=True)
    )

    sentinel = clip_hours + 1

    if timeline.empty or timeline["event_flag"].sum() == 0:
        return pd.DataFrame(
            {
                "rounded_hour": timeline["rounded_hour"],
                "e_hours_to_event_clip": sentinel,
                "e_hours_since_event_clip": sentinel,
                "e_event_proximity_clip": sentinel,
                "e_event_window_pre_24h": 0,
                "e_event_window_post_24h": 0,
            }
        )

    ts = timeline["rounded_hour"].values.astype("datetime64[h]").astype("int64")
    event_ts = timeline.loc[timeline["event_flag"].eq(1), "rounded_hour"].values.astype("datetime64[h]").astype("int64")

    idx_next = np.searchsorted(event_ts, ts, side="left")
    idx_prev = np.searchsorted(event_ts, ts, side="right") - 1

    to_hours = np.full(len(ts), np.inf, dtype=float)
    valid_next = idx_next < len(event_ts)
    to_hours[valid_next] = event_ts[idx_next[valid_next]] - ts[valid_next]

    since_hours = np.full(len(ts), np.inf, dtype=float)
    valid_prev = idx_prev >= 0
    since_hours[valid_prev] = ts[valid_prev] - event_ts[idx_prev[valid_prev]]

    to_clip = np.where(np.isfinite(to_hours), np.minimum(to_hours, clip_hours), sentinel)
    since_clip = np.where(np.isfinite(since_hours), np.minimum(since_hours, clip_hours), sentinel)
    prox_clip = np.minimum(to_clip, since_clip)

    return pd.DataFrame(
        {
            "rounded_hour": timeline["rounded_hour"],
            "e_hours_to_event_clip": to_clip.astype(int),
            "e_hours_since_event_clip": since_clip.astype(int),
            "e_event_proximity_clip": prox_clip.astype(int),
            "e_event_window_pre_24h": ((to_clip <= 24) & (timeline["event_flag"].eq(0))).astype(np.int8),
            "e_event_window_post_24h": ((since_clip <= 24) & (timeline["event_flag"].eq(0))).astype(np.int8),
        }
    )


def add_time_features(df: pd.DataFrame, day_class_levels: list[str]) -> pd.DataFrame:
    out = df.copy()

    hour_sin, hour_cos = cyclical_encode(out["hour"], period=24)
    wd_sin, wd_cos = cyclical_encode(out["weekday_int"], period=7)
    month_sin, month_cos = cyclical_encode(out["month"], period=12)

    out["t_hour_sin"] = hour_sin
    out["t_hour_cos"] = hour_cos
    out["t_weekday_sin"] = wd_sin
    out["t_weekday_cos"] = wd_cos
    out["t_month_sin"] = month_sin
    out["t_month_cos"] = month_cos

    out["t_is_weekend"] = as_int_flag(out["weekday_int"].isin([5, 6]))
    out["t_is_national_holiday"] = as_int_flag(out["is_national_holiday"])
    out["t_is_other_holiday"] = as_int_flag(out["is_other_holiday"])
    out["t_is_any_holiday"] = as_int_flag(out["is_any_holiday"])
    out["t_is_school_vacation"] = as_int_flag(out["is_school_vacation"])
    out["t_is_2020_regime"] = pd.to_numeric(out["year"], errors="coerce").eq(2020).astype(np.int8)

    out["t_season"] = pd.to_numeric(out["month"], errors="coerce").map(SEASON_MAP).fillna("unknown")

    dayclass = np.select(
        [
            as_bool_flag(out["is_event_day"]),
            as_bool_flag(out["is_any_holiday"]),
            as_bool_flag(out["is_school_vacation"]),
            out["weekday_int"].isin([5, 6]),
        ],
        ["event_day", "holiday", "school_vacation", "weekend_regular"],
        default="weekday_regular",
    )
    out["t_day_class_5"] = pd.Categorical(dayclass, categories=day_class_levels)

    for level in day_class_levels:
        out[f"t_day_class_5__{slugify(level)}"] = out["t_day_class_5"].eq(level).astype(np.int8)

    for season in SEASON_LEVELS:
        out[f"t_season__{season}"] = out["t_season"].eq(season).astype(np.int8)

    return out


def add_spatial_features(df: pd.DataFrame, parking_levels: list[str]) -> pd.DataFrame:
    out = df.copy()

    out["s_tier_is_centrum"] = out["parking_location_category"].astype(str).str.lower().eq("centrum").astype(np.int8)
    out["s_tier_is_vesten"] = out["parking_location_category"].astype(str).str.lower().eq("vesten").astype(np.int8)
    out["s_tier_is_rand"] = out["parking_location_category"].astype(str).str.lower().eq("rand").astype(np.int8)

    cap_numeric = pd.to_numeric(out["total_capacity"], errors="coerce")
    out["s_log_total_capacity"] = np.log1p(cap_numeric)

    for level in ["small", "medium", "large"]:
        out[f"s_capacity_bucket__{level}"] = out["s_capacity_bucket"].eq(level).astype(np.int8)

    out["s_parking_id"] = pd.Categorical(out["parking_id"].astype(str), categories=parking_levels)
    for pid in parking_levels:
        out[f"s_parking_id__{slugify(pid)}"] = out["s_parking_id"].eq(pid).astype(np.int8)

    return out


def fit_external_params(train_df: pd.DataFrame) -> dict[str, float | int]:
    precip_positive = pd.to_numeric(train_df["precip_mm"], errors="coerce")
    precip_positive = precip_positive[precip_positive > 0]
    if len(precip_positive) > 0:
        precip_q50 = float(precip_positive.quantile(0.50))
        precip_q90 = float(precip_positive.quantile(0.90))
    else:
        precip_q50, precip_q90 = 0.1, 1.0

    wind_speed_high_thr = float(pd.to_numeric(train_df["wind_speed_ms"], errors="coerce").quantile(0.90))
    wind_gust_high_thr = float(pd.to_numeric(train_df["wind_gusts_ms"], errors="coerce").quantile(0.90))

    n_concurrent_cap = int(pd.to_numeric(train_df["n_concurrent_events"], errors="coerce").quantile(0.95))
    if n_concurrent_cap < 1:
        n_concurrent_cap = 1

    return {
        "precip_positive_q50": precip_q50,
        "precip_positive_q90": precip_q90,
        "wind_speed_high_thr_q90": wind_speed_high_thr,
        "wind_gust_high_thr_q90": wind_gust_high_thr,
        "n_concurrent_events_cap_q95": n_concurrent_cap,
    }


def add_external_features(df: pd.DataFrame, fit_params: dict[str, float | int]) -> pd.DataFrame:
    out = df.copy()

    temp = pd.to_numeric(out["temp_c"], errors="coerce")
    precip = pd.to_numeric(out["precip_mm"], errors="coerce")
    wind = pd.to_numeric(out["wind_speed_ms"], errors="coerce")
    gust = pd.to_numeric(out["wind_gusts_ms"], errors="coerce")
    sun_duration = pd.to_numeric(out["sun_duration_min"], errors="coerce")
    sun_intensity = pd.to_numeric(out["sun_intensity_wm2"], errors="coerce")

    out["e_temp_c"] = temp
    out["e_temp_c_sq"] = np.square(temp)

    out["e_precip_mm"] = precip
    p50 = float(fit_params["precip_positive_q50"])
    p90 = float(fit_params["precip_positive_q90"])
    out["e_precip_bin"] = np.select(
        [
            precip.eq(0),
            (precip > 0) & (precip <= p50),
            (precip > p50) & (precip <= p90),
            precip > p90,
        ],
        ["dry", "light", "moderate", "heavy"],
        default="unknown",
    )
    for lvl in ["dry", "light", "moderate", "heavy"]:
        out[f"e_precip_bin__{lvl}"] = pd.Series(out["e_precip_bin"]).eq(lvl).astype(np.int8)

    out["e_wind_speed_ms"] = wind
    out["e_wind_gusts_ms"] = gust
    out["e_is_high_wind_speed"] = wind.ge(float(fit_params["wind_speed_high_thr_q90"])).fillna(False).astype(np.int8)
    out["e_is_high_wind_gust"] = gust.ge(float(fit_params["wind_gust_high_thr_q90"])).fillna(False).astype(np.int8)

    out["e_sun_duration_ratio"] = (sun_duration / 60.0).clip(lower=0, upper=1)
    out["e_sun_intensity_log1p"] = np.log1p(sun_intensity.clip(lower=0))

    out["e_is_event_day"] = as_int_flag(out["is_event_day"])
    for col in [
        "is_football_day",
        "is_sport_day",
        "is_festival_day",
        "is_procession_day",
        "is_kermis_day",
        "is_markt_day",
        "is_carnival_day",
        "is_other_day",
    ]:
        out[f"e_{col}"] = as_int_flag(out[col])

    out["e_event_scale_max"] = pd.to_numeric(out["event_scale_max"], errors="coerce").fillna(0).astype(int)
    out["e_event_scale_is_large"] = out["e_event_scale_max"].ge(2).astype(np.int8)

    out["e_n_concurrent_events"] = pd.to_numeric(out["n_concurrent_events"], errors="coerce").fillna(0)
    out["e_n_concurrent_events_capped"] = out["e_n_concurrent_events"].clip(upper=int(fit_params["n_concurrent_events_cap_q95"]))

    kickoff = pd.to_numeric(out["football_kickoff_hour"], errors="coerce")
    out["e_has_football_kickoff"] = kickoff.notna().astype(np.int8)
    kickoff_sin, kickoff_cos = cyclical_encode(kickoff.fillna(0), period=24)
    out["e_football_kickoff_hour_sin"] = kickoff_sin
    out["e_football_kickoff_hour_cos"] = kickoff_cos

    return out


def add_external_interactions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["e_int_event_x_tier_centrum"] = out["e_is_event_day"] * out["s_tier_is_centrum"]
    out["e_int_holiday_x_tier_centrum"] = out["t_is_any_holiday"] * out["s_tier_is_centrum"]
    out["e_int_vacation_x_tier_centrum"] = out["t_is_school_vacation"] * out["s_tier_is_centrum"]

    for season in SEASON_LEVELS:
        season_col = f"t_season__{season}"
        out[f"e_int_temp_x_season__{season}"] = out["e_temp_c"] * out[season_col]
        out[f"e_int_precip_x_season__{season}"] = out["e_precip_mm"] * out[season_col]
        out[f"e_int_wind_x_season__{season}"] = out["e_wind_speed_ms"] * out[season_col]

    return out


def add_time_aware_lag(
    df: pd.DataFrame,
    lag_hours: int,
    value_col: str = "occupancy_rate",
    id_col: str = "parking_id",
    time_col: str = "rounded_hour",
) -> pd.DataFrame:
    lag_col = f"l_occ_lag_{lag_hours}h"
    lookup = df[[id_col, time_col, value_col]].rename(columns={value_col: lag_col}).copy()
    lookup[time_col] = lookup[time_col] + pd.Timedelta(hours=lag_hours)
    return df.merge(lookup, on=[id_col, time_col], how="left")


def add_strict_contiguous_rolling_features(
    df: pd.DataFrame,
    id_col: str = "parking_id",
    time_col: str = "rounded_hour",
    value_col: str = "occupancy_rate",
) -> pd.DataFrame:
    out = df.sort_values([id_col, time_col]).copy()

    prev_time = out.groupby(id_col)[time_col].shift(1)
    is_step_1h = prev_time.notna() & ((out[time_col] - prev_time) == pd.Timedelta(hours=1))
    out["_contig_break"] = ~is_step_1h
    out["_contig_id"] = out.groupby(id_col)["_contig_break"].cumsum()

    out["l_occ_rollmean_24h_strict"] = (
        out.groupby([id_col, "_contig_id"])[value_col]
        .transform(lambda s: s.shift(1).rolling(window=24, min_periods=24).mean())
    )

    out["l_occ_rollstd_24h_strict"] = (
        out.groupby([id_col, "_contig_id"])[value_col]
        .transform(lambda s: s.shift(1).rolling(window=24, min_periods=24).std(ddof=0))
    )

    return out.drop(columns=["_contig_break", "_contig_id"])


def add_lag_validity_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["l_valid_lag_1h"] = out["l_occ_lag_1h"].notna().astype(np.int8)
    out["l_valid_lag_24h"] = out["l_occ_lag_24h"].notna().astype(np.int8)
    out["l_valid_lag_168h"] = out["l_occ_lag_168h"].notna().astype(np.int8)
    out["l_valid_all_core"] = (
        (out["l_valid_lag_1h"] == 1)
        & (out["l_valid_lag_24h"] == 1)
        & (out["l_valid_lag_168h"] == 1)
    ).astype(np.int8)
    out["l_valid_roll24_strict"] = (
        out["l_occ_rollmean_24h_strict"].notna() & out["l_occ_rollstd_24h_strict"].notna()
    ).astype(np.int8)
    out["l_valid_core_plus_roll24"] = (
        (out["l_valid_all_core"] == 1) & (out["l_valid_roll24_strict"] == 1)
    ).astype(np.int8)
    return out


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _load_phase_inputs(paths: Phase4Paths) -> dict[str, Any]:
    train_raw = pd.read_parquet(paths.split_dir / "MAD_shortterm_train_2020_2023_2024.parquet")
    holdout_raw = pd.read_parquet(paths.split_dir / "MAD_shortterm_holdout_2025.parquet")
    for df in [train_raw, holdout_raw]:
        ensure_datetime(df, "rounded_hour")
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    cv_plan = pd.read_csv(paths.split_dir / "shortterm_train_rolling_cv_plan.csv")
    for col in ["train_end_before", "valid_start", "valid_end"]:
        cv_plan[col] = pd.to_datetime(cv_plan[col], errors="coerce")

    policy_manifest = _load_json(paths.phase4_feature_set_dir / "feature_manifest_policy.json")
    forecast_manifest = _load_json(paths.phase4_feature_set_dir / "feature_manifest_forecast.json")
    feature_registry = pd.read_csv(paths.phase4_feature_set_dir / "feature_registry.csv")

    return {
        "train_raw": train_raw,
        "holdout_raw": holdout_raw,
        "cv_plan": cv_plan,
        "policy_manifest": policy_manifest,
        "forecast_manifest": forecast_manifest,
        "feature_registry": feature_registry,
    }


def _build_tse_for_train_apply(
    train_df: pd.DataFrame,
    apply_df: pd.DataFrame,
    policy_columns: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    train = train_df.copy()
    apply = apply_df.copy()
    for df in [train, apply]:
        ensure_datetime(df, "rounded_hour")

    train_t = add_time_features(train, day_class_levels=DAY_CLASS_LEVELS)
    apply_t = add_time_features(apply, day_class_levels=DAY_CLASS_LEVELS)

    cap_labels = ["small", "medium", "large"]
    train_cap_bucket, cap_edges = qcut_with_fallback(train_t["total_capacity"], q=3, labels=cap_labels)
    train_t["s_capacity_bucket"] = train_cap_bucket.astype(str)
    apply_t["s_capacity_bucket"] = cut_using_edges(apply_t["total_capacity"], edges=cap_edges, labels=cap_labels).astype(str)

    parking_levels = sorted(train_t["parking_id"].astype(str).unique().tolist())
    train_s = add_spatial_features(train_t, parking_levels=parking_levels)
    apply_s = add_spatial_features(apply_t, parking_levels=parking_levels)

    external_fit_params = fit_external_params(train_s)
    train_e = add_external_features(train_s, fit_params=external_fit_params)
    apply_e = add_external_features(apply_s, fit_params=external_fit_params)

    train_int = add_external_interactions(train_e)
    apply_int = add_external_interactions(apply_e)

    combined_timeline = pd.concat(
        [
            train_int[["rounded_hour", "is_event_day"]],
            apply_int[["rounded_hour", "is_event_day"]],
        ],
        axis=0,
        ignore_index=True,
    )
    cascade = compute_event_cascade_features(
        timestamp_series=combined_timeline["rounded_hour"],
        event_series=combined_timeline["is_event_day"],
        clip_hours=72,
    )

    train_final = train_int.merge(cascade, on="rounded_hour", how="left")
    apply_final = apply_int.merge(cascade, on="rounded_hour", how="left")

    for col in [
        "e_hours_to_event_clip",
        "e_hours_since_event_clip",
        "e_event_proximity_clip",
        "e_event_window_pre_24h",
        "e_event_window_post_24h",
    ]:
        train_final[col] = pd.to_numeric(train_final[col], errors="coerce").fillna(73).astype(int)
        apply_final[col] = pd.to_numeric(apply_final[col], errors="coerce").fillna(73).astype(int)

    cols = BASE_COLUMNS + policy_columns
    for col in cols:
        if col not in train_final.columns:
            train_final[col] = 0
        if col not in apply_final.columns:
            apply_final[col] = 0
    train_out = train_final[cols].copy()
    apply_out = apply_final[cols].copy()

    fit_payload = {
        "capacity_bin_edges": [float(x) for x in np.array(cap_edges).tolist()],
        "parking_levels": parking_levels,
        "day_class_levels": DAY_CLASS_LEVELS,
        "external_fit_params": external_fit_params,
        "event_cascade": {"clip_hours": 72, "sentinel": 73},
    }
    return train_out, apply_out, fit_payload


def _add_forecast_l_for_train_apply(
    train_tse: pd.DataFrame,
    apply_tse: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    combined = pd.concat([train_tse, apply_tse], axis=0, ignore_index=True)
    combined = combined.sort_values(["parking_id", "rounded_hour"]).reset_index(drop=True)

    for lag_h in [1, 24, 168]:
        combined = add_time_aware_lag(combined, lag_hours=lag_h)

    combined = add_strict_contiguous_rolling_features(combined)
    combined["l_occ_lag_delta_1h_24h"] = combined["l_occ_lag_1h"] - combined["l_occ_lag_24h"]
    combined["l_occ_lag_delta_24h_168h"] = combined["l_occ_lag_24h"] - combined["l_occ_lag_168h"]
    combined = add_lag_validity_flags(combined)

    train_out = combined.iloc[: len(train_tse)].copy()
    apply_out = combined.iloc[len(train_tse) :].copy()
    return train_out, apply_out


def _build_fold_feature_layers(
    fold_train_raw: pd.DataFrame,
    fold_valid_raw: pd.DataFrame,
    policy_columns: list[str],
    forecast_columns: list[str],
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    train_policy, valid_policy, fit_payload = _build_tse_for_train_apply(
        train_df=fold_train_raw,
        apply_df=fold_valid_raw,
        policy_columns=policy_columns,
    )

    train_forecast_all, valid_forecast_all = _add_forecast_l_for_train_apply(
        train_tse=train_policy,
        apply_tse=valid_policy,
    )

    forecast_core_cols = BASE_COLUMNS + sorted(
        set(forecast_columns)
        | {
            "l_occ_rollmean_24h_strict",
            "l_occ_rollstd_24h_strict",
            "l_valid_lag_1h",
            "l_valid_lag_24h",
            "l_valid_lag_168h",
            "l_valid_all_core",
            "l_valid_roll24_strict",
            "l_valid_core_plus_roll24",
        }
    )

    layers = {
        "policy_train": train_policy,
        "policy_valid": valid_policy,
        "forecast_train": train_forecast_all[forecast_core_cols].copy(),
        "forecast_valid": valid_forecast_all[forecast_core_cols].copy(),
    }

    return layers, fit_payload


def _hash_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _classify_event_feature(name: str) -> tuple[str, str]:
    lower = name.lower()
    uncertain_tokens = ["hours_to", "hours_since", "proximity", "window"]
    probable_tokens = [
        "kickoff",
        "event_scale",
        "n_concurrent",
        "is_event_day",
        "is_football",
        "is_sport",
        "is_festival",
        "is_procession",
        "is_kermis",
        "is_markt",
        "is_carnival",
        "is_other_day",
        "event_x",
    ]

    if any(tok in lower for tok in uncertain_tokens):
        return (
            "ex_post_or_uncertain",
            "Conservative strict rule: timing-proximity style event feature is uncertain ex-ante.",
        )
    if any(tok in lower for tok in probable_tokens):
        return (
            "ex_ante_probable",
            "Event calendar/type signal is usually known in advance but operational certainty can vary.",
        )
    return (
        "ex_ante_guaranteed",
        "Calendar-derived feature with deterministic construction under project assumptions.",
    )


def _build_event_contract(feature_registry: pd.DataFrame) -> pd.DataFrame:
    event_rows = []
    for _, row in feature_registry.iterrows():
        feature_name = str(row["feature_name"])
        if not feature_name.startswith("e_"):
            continue

        is_event_related = any(
            token in feature_name.lower()
            for token in ["event", "football", "festival", "kermis", "markt", "carnival", "procession", "sport"]
        )
        if not is_event_related:
            continue

        label, rationale = _classify_event_feature(feature_name)
        include_primary = label != "ex_post_or_uncertain"
        event_rows.append(
            {
                "feature_name": feature_name,
                "track_allowed": row.get("track_allowed", "policy|forecast"),
                "availability_label": label,
                "rationale": rationale,
                "evidence_source": "phase4_feature_sets/feature_registry.csv + conservative strict rule",
                "included_primary_policy": bool(include_primary),
                "included_primary_forecast": bool(include_primary),
            }
        )

    return pd.DataFrame(event_rows).sort_values("feature_name").reset_index(drop=True)


def _model_grid() -> dict[str, dict[str, Any]]:
    return {
        "ridge_a1_0": {"model_family": "ridge", "alpha": 1.0},
        "rf_90_d12_l2": {
            "model_family": "random_forest",
            "n_estimators": 90,
            "max_depth": 12,
            "min_samples_leaf": 2,
            "n_jobs": -1,
        },
        "xgb_80_d4_lr006": {
            "model_family": "xgboost",
            "n_estimators": 80,
            "max_depth": 4,
            "learning_rate": 0.06,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
        },
    }


def _build_ablation_run_specs(seed: int = DEFAULT_SEED) -> list[dict[str, Any]]:
    model_keys = list(_model_grid().keys())
    specs: list[dict[str, Any]] = []

    specs.append(
        {
            "run_id": "P0_profile_baseline",
            "track": "policy",
            "variant": "P0",
            "model_family": "baseline",
            "model_key": "profile_baseline",
            "feature_set_id": "baseline_profile",
            "row_filter": "none",
            "seed": seed,
            "primary_metric": "mae",
        }
    )

    for variant, fs_id in [
        ("P1", "policy_ts"),
        ("P2", "policy_tse_no_parking_id"),
        ("P3", "policy_tse_full"),
        ("P4", "policy_tse_exante_strict"),
    ]:
        for mk in model_keys:
            specs.append(
                {
                    "run_id": f"{variant}_{mk}",
                    "track": "policy",
                    "variant": variant,
                    "model_family": _model_grid()[mk]["model_family"],
                    "model_key": mk,
                    "feature_set_id": fs_id,
                    "row_filter": "none",
                    "seed": seed,
                    "primary_metric": "mae",
                }
            )

    specs.append(
        {
            "run_id": "F0_persistence_baseline",
            "track": "forecast",
            "variant": "F0",
            "model_family": "baseline",
            "model_key": "persistence_baseline",
            "feature_set_id": "baseline_persistence",
            "row_filter": "none",
            "seed": seed,
            "primary_metric": "mae",
        }
    )

    for variant, fs_id, row_filter in [
        ("F1", "forecast_tse", "none"),
        ("F2", "forecast_tsel_core", "none"),
        ("F3", "forecast_tsel_core_strict_lagvalid", "l_valid_all_core==1"),
        ("F4", "forecast_tsel_plus_roll_strict", "l_valid_core_plus_roll24==1"),
    ]:
        for mk in model_keys:
            specs.append(
                {
                    "run_id": f"{variant}_{mk}",
                    "track": "forecast",
                    "variant": variant,
                    "model_family": _model_grid()[mk]["model_family"],
                    "model_key": mk,
                    "feature_set_id": fs_id,
                    "row_filter": row_filter,
                    "seed": seed,
                    "primary_metric": "mae",
                }
            )

    return specs


def _get_variant_features(
    track: str,
    variant: str,
    policy_inputs: list[str],
    forecast_inputs: list[str],
    uncertain_event_features: set[str],
) -> list[str]:
    if track == "policy":
        if variant == "P0":
            return []
        if variant == "P1":
            return [c for c in policy_inputs if c.startswith("t_") or c.startswith("s_")]
        if variant == "P2":
            return [c for c in policy_inputs if not c.startswith("s_parking_id__")]
        if variant == "P3":
            return list(policy_inputs)
        if variant == "P4":
            return [c for c in policy_inputs if c not in uncertain_event_features]

    if track == "forecast":
        if variant == "F0":
            return []
        if variant == "F1":
            return list(policy_inputs)
        if variant in {"F2", "F3"}:
            return list(forecast_inputs)
        if variant == "F4":
            return list(forecast_inputs) + ["l_occ_rollmean_24h_strict", "l_occ_rollstd_24h_strict"]

    raise ValueError(f"Unknown track/variant combination: {track}/{variant}")


def _safe_mape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-6) -> float:
    denom = np.maximum(np.abs(y_true), eps)
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


def _metric_bundle(df: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    err = np.abs(y_true - y_pred)

    def _masked_mae(mask: np.ndarray) -> float:
        if mask.sum() == 0:
            return float("nan")
        return float(np.mean(err[mask]))

    mask_centrum = df["s_tier_is_centrum"].to_numpy(dtype=float) == 1.0
    mask_vr = ~mask_centrum
    mask_event = df["e_is_event_day"].to_numpy(dtype=float) == 1.0
    mask_non_event = ~mask_event

    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(math.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": _safe_mape(y_true, y_pred),
        "mae_tier_centrum": _masked_mae(mask_centrum),
        "mae_tier_vesten_rand": _masked_mae(mask_vr),
        "mae_event": _masked_mae(mask_event),
        "mae_non_event": _masked_mae(mask_non_event),
    }


def _make_regressor(model_key: str, seed: int) -> Pipeline:
    cfg = _model_grid()[model_key]
    fam = cfg["model_family"]

    if fam == "ridge":
        model = Ridge(alpha=float(cfg["alpha"]))
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", model),
            ]
        )

    if fam == "random_forest":
        model = RandomForestRegressor(
            n_estimators=int(cfg["n_estimators"]),
            max_depth=cfg["max_depth"],
            min_samples_leaf=int(cfg["min_samples_leaf"]),
            random_state=seed,
            n_jobs=int(cfg["n_jobs"]),
        )
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", model),
            ]
        )

    if fam == "xgboost":
        model = XGBRegressor(
            objective="reg:squarederror",
            n_estimators=int(cfg["n_estimators"]),
            max_depth=int(cfg["max_depth"]),
            learning_rate=float(cfg["learning_rate"]),
            subsample=float(cfg["subsample"]),
            colsample_bytree=float(cfg["colsample_bytree"]),
            random_state=seed,
            tree_method="hist",
            n_jobs=4,
            eval_metric="rmse",
            reg_lambda=1.0,
        )
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", model),
            ]
        )

    raise ValueError(f"Unsupported model key: {model_key}")


def _profile_baseline_predict(train_df: pd.DataFrame, valid_df: pd.DataFrame) -> np.ndarray:
    prof = (
        train_df.groupby(["parking_id", "hour", "weekday_int"], as_index=False)["occupancy_rate"].mean().rename(columns={"occupancy_rate": "pred"})
    )
    p_h = train_df.groupby(["parking_id", "hour"], as_index=False)["occupancy_rate"].mean().rename(columns={"occupancy_rate": "pred_ph"})
    p = train_df.groupby("parking_id", as_index=False)["occupancy_rate"].mean().rename(columns={"occupancy_rate": "pred_p"})
    global_mean = float(train_df["occupancy_rate"].mean())

    pred_df = valid_df[["parking_id", "hour", "weekday_int"]].copy()
    pred_df = pred_df.merge(prof, on=["parking_id", "hour", "weekday_int"], how="left")
    pred_df = pred_df.merge(p_h, on=["parking_id", "hour"], how="left")
    pred_df = pred_df.merge(p, on=["parking_id"], how="left")

    pred = pred_df["pred"]
    pred = pred.fillna(pred_df["pred_ph"]).fillna(pred_df["pred_p"]).fillna(global_mean)
    return pred.to_numpy(dtype=float)


def _persistence_baseline_predict(train_df: pd.DataFrame, valid_df: pd.DataFrame) -> np.ndarray:
    fallback = _profile_baseline_predict(train_df, valid_df)
    pred = valid_df["l_occ_lag_1h"].copy()
    pred = pred.fillna(valid_df["l_occ_lag_24h"])
    pred = pred.fillna(pd.Series(fallback, index=valid_df.index))
    return pred.to_numpy(dtype=float)


def _apply_row_filter(df: pd.DataFrame, row_filter: str) -> pd.DataFrame:
    if row_filter == "none":
        return df.copy()
    if row_filter == "l_valid_all_core==1":
        return df.loc[df["l_valid_all_core"] == 1].copy()
    if row_filter == "l_valid_core_plus_roll24==1":
        return df.loc[df["l_valid_core_plus_roll24"] == 1].copy()
    raise ValueError(f"Unknown row filter: {row_filter}")


def _join_helper_time_cols(df: pd.DataFrame, raw_lookup: pd.DataFrame) -> pd.DataFrame:
    if "hour" in df.columns and "weekday_int" in df.columns:
        return df
    merged = df.merge(raw_lookup, on=["parking_id", "rounded_hour"], how="left")
    merged["hour"] = pd.to_numeric(merged["hour"], errors="coerce")
    merged["weekday_int"] = pd.to_numeric(merged["weekday_int"], errors="coerce")
    return merged


def _prepare_fixed_export_layers(paths: Phase4Paths, raw_train: pd.DataFrame) -> dict[str, pd.DataFrame]:
    policy_train = pd.read_parquet(paths.phase4_feature_set_dir / "policy_train.parquet")
    forecast_train = pd.read_parquet(paths.phase4_feature_set_dir / "forecast_train.parquet")

    for df in [policy_train, forecast_train]:
        ensure_datetime(df, "rounded_hour")

    raw_lookup = raw_train[["parking_id", "rounded_hour", "hour", "weekday_int"]].drop_duplicates()

    policy_train = _join_helper_time_cols(policy_train, raw_lookup)
    forecast_train = _join_helper_time_cols(forecast_train, raw_lookup)

    forecast_train = add_strict_contiguous_rolling_features(forecast_train)
    forecast_train = add_lag_validity_flags(forecast_train)

    return {
        "policy_train": policy_train,
        "forecast_train": forecast_train,
    }


def _build_fold_cache(paths: Phase4Paths, cv_plan: pd.DataFrame, raw_train: pd.DataFrame) -> dict[str, Any]:
    fold_cache: dict[str, Any] = {"fold_safe": {}, "fixed_export": {}}

    for _, row in cv_plan.iterrows():
        fold_id = str(row["fold"])
        fold_dir = paths.internal_dir / "fold_safe" / fold_id
        fold_cache["fold_safe"][fold_id] = {
            "policy_train": pd.read_parquet(fold_dir / "policy_train.parquet"),
            "policy_valid": pd.read_parquet(fold_dir / "policy_valid.parquet"),
            "forecast_train": pd.read_parquet(fold_dir / "forecast_train.parquet"),
            "forecast_valid": pd.read_parquet(fold_dir / "forecast_valid.parquet"),
        }

    fixed = _prepare_fixed_export_layers(paths, raw_train=raw_train)
    fx_policy = fixed["policy_train"]
    fx_forecast = fixed["forecast_train"]

    for _, row in cv_plan.iterrows():
        fold_id = str(row["fold"])
        train_end_before = pd.to_datetime(row["train_end_before"])
        valid_start = pd.to_datetime(row["valid_start"])
        valid_end = pd.to_datetime(row["valid_end"])

        p_train = fx_policy.loc[fx_policy["rounded_hour"] < train_end_before].copy()
        p_valid = fx_policy.loc[(fx_policy["rounded_hour"] >= valid_start) & (fx_policy["rounded_hour"] <= valid_end)].copy()

        f_train = fx_forecast.loc[fx_forecast["rounded_hour"] < train_end_before].copy()
        f_valid = fx_forecast.loc[(fx_forecast["rounded_hour"] >= valid_start) & (fx_forecast["rounded_hour"] <= valid_end)].copy()

        fold_cache["fixed_export"][fold_id] = {
            "policy_train": p_train,
            "policy_valid": p_valid,
            "forecast_train": f_train,
            "forecast_valid": f_valid,
        }

    return fold_cache


def _execute_cv_plan_rows(
    plan_rows: pd.DataFrame,
    cv_plan: pd.DataFrame,
    fold_cache: dict[str, Any],
    policy_inputs: list[str],
    forecast_inputs: list[str],
    uncertain_event_features: set[str],
) -> pd.DataFrame:
    results: list[dict[str, Any]] = []

    for _, plan_row in plan_rows.iterrows():
        run_id = str(plan_row["run_id"])
        track = str(plan_row["track"])
        variant = str(plan_row["variant"])
        model_family = str(plan_row["model_family"])
        model_key = str(plan_row["model_key"])
        row_filter = str(plan_row["row_filter"])
        cv_mode = str(plan_row["cv_mode"])
        seed = int(plan_row["seed"])

        feature_cols = _get_variant_features(
            track=track,
            variant=variant,
            policy_inputs=policy_inputs,
            forecast_inputs=forecast_inputs,
            uncertain_event_features=uncertain_event_features,
        )

        for _, fold in cv_plan.iterrows():
            fold_id = str(fold["fold"])
            cache = fold_cache[cv_mode][fold_id]
            train_df = cache[f"{track}_train"].copy()
            valid_df = cache[f"{track}_valid"].copy()

            train_df = _apply_row_filter(train_df, row_filter=row_filter)
            valid_df = _apply_row_filter(valid_df, row_filter=row_filter)

            train_df = train_df.dropna(subset=["occupancy_rate"]).copy()
            valid_df = valid_df.dropna(subset=["occupancy_rate"]).copy()

            n_train = int(len(train_df))
            n_valid = int(len(valid_df))

            if n_train == 0 or n_valid == 0:
                results.append(
                    {
                        "run_id": run_id,
                        "cv_mode": cv_mode,
                        "fold_id": fold_id,
                        "track": track,
                        "variant": variant,
                        "model_family": model_family,
                        "model_key": model_key,
                        "n_train": n_train,
                        "n_valid": n_valid,
                        "mae": float("nan"),
                        "rmse": float("nan"),
                        "mape": float("nan"),
                        "mae_tier_centrum": float("nan"),
                        "mae_tier_vesten_rand": float("nan"),
                        "mae_event": float("nan"),
                        "mae_non_event": float("nan"),
                        "fit_status": "empty_after_filter",
                    }
                )
                continue

            y_train = train_df["occupancy_rate"].to_numpy(dtype=float)
            y_valid = valid_df["occupancy_rate"].to_numpy(dtype=float)

            try:
                if model_family == "baseline" and model_key == "profile_baseline":
                    y_pred = _profile_baseline_predict(train_df, valid_df)
                elif model_family == "baseline" and model_key == "persistence_baseline":
                    y_pred = _persistence_baseline_predict(train_df, valid_df)
                else:
                    X_train = train_df[feature_cols]
                    X_valid = valid_df[feature_cols]
                    model = _make_regressor(model_key=model_key, seed=seed)
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_valid).astype(float)

                metrics = _metric_bundle(valid_df, y_valid, y_pred)
                results.append(
                    {
                        "run_id": run_id,
                        "cv_mode": cv_mode,
                        "fold_id": fold_id,
                        "track": track,
                        "variant": variant,
                        "model_family": model_family,
                        "model_key": model_key,
                        "n_train": n_train,
                        "n_valid": n_valid,
                        **metrics,
                        "fit_status": "ok",
                    }
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    {
                        "run_id": run_id,
                        "cv_mode": cv_mode,
                        "fold_id": fold_id,
                        "track": track,
                        "variant": variant,
                        "model_family": model_family,
                        "model_key": model_key,
                        "n_train": n_train,
                        "n_valid": n_valid,
                        "mae": float("nan"),
                        "rmse": float("nan"),
                        "mape": float("nan"),
                        "mae_tier_centrum": float("nan"),
                        "mae_tier_vesten_rand": float("nan"),
                        "mae_event": float("nan"),
                        "mae_non_event": float("nan"),
                        "fit_status": f"error: {exc}",
                    }
                )

    return pd.DataFrame(results)


def _aggregate_cv_results(cv_results: pd.DataFrame) -> pd.DataFrame:
    ok = cv_results.loc[cv_results["fit_status"] == "ok"].copy()
    if ok.empty:
        return pd.DataFrame()

    grouped = (
        ok.groupby(["run_id", "cv_mode", "track", "variant", "model_family", "model_key"], as_index=False)
        .agg(
            folds=("fold_id", "nunique"),
            mean_mae=("mae", "mean"),
            std_mae=("mae", "std"),
            mean_rmse=("rmse", "mean"),
            mean_mape=("mape", "mean"),
            mean_n_valid=("n_valid", "mean"),
        )
        .sort_values(["track", "cv_mode", "mean_mae", "mean_rmse", "mean_mape"])
    )
    grouped["std_mae"] = grouped["std_mae"].fillna(0.0)
    grouped["cv_variability_ratio"] = grouped["std_mae"] / grouped["mean_mae"].replace(0, np.nan)
    return grouped


def _build_phase4_protocol_markdown() -> str:
    return """# Phase 4 Protocol (Definitief)

Datum: 2026-03-13

## Harde methodologische regels

1. `2025` blijft volledig locked holdout.
2. Strikte trackscheiding: `policy = T+S+E`, `forecast = T+S+E+L`.
3. Geen kwaliteitsflags of target-proxies als predictors.
4. Fold-safe CV is primair: alle `requires_fit=True` stappen per fold op fold-train fitten.
5. Fixed-export CV mag alleen als sensitivity-referentie, nooit als hoofdclaim.

## Evaluatie- en selectieregels

1. Primaire metric: MAE (tie-breakers: RMSE, daarna MAPE).
2. Rapportering verplicht: overall, per tier (centrum vs vesten/rand), event vs non-event.
3. Forecast rapporteert zowel full-set als strict lag-valid subsets.
4. Policy met en zonder `parking_id` wordt parallel gerapporteerd.

## Go/No-Go criteria

- Go: fold-safe runs + volledige ablaties + event-contract compleet.
- No-Go: modelkeuze op fixed-export zonder fold-safe hoofdresultaten.
- No-Go: policyrapportering enkel met `parking_id`.
"""


def run_pre_modelling_audit(paths: Phase4Paths | None = None, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    p = paths or get_phase4_paths()
    data = _load_phase_inputs(p)

    immutable_manifest = pd.read_csv(p.phase4_feature_set_dir / "immutable_export_manifest.csv")
    checksum_rows = []
    for _, row in immutable_manifest.iterrows():
        file_path = Path(str(row["path"]))
        expected = str(row["sha256"])
        observed = _hash_file(file_path)
        checksum_rows.append(
            {
                "artifact": row["artifact"],
                "path": str(file_path),
                "expected_sha256": expected,
                "observed_sha256": observed,
                "checksum_ok": observed == expected,
            }
        )
    checksum_df = pd.DataFrame(checksum_rows)

    policy_inputs = list(data["policy_manifest"]["model_input_columns"])
    forecast_inputs = list(data["forecast_manifest"]["model_input_columns"])

    contract_checks = pd.DataFrame(
        [
            {
                "check": "policy_has_no_l_columns",
                "result": "PASS" if len([c for c in policy_inputs if c.startswith("l_")]) == 0 else "FAIL",
                "detail": f"n_l_columns={len([c for c in policy_inputs if c.startswith('l_')])}",
            },
            {
                "check": "forecast_has_exact_5_selected_l_columns",
                "result": "PASS" if len([c for c in forecast_inputs if c.startswith("l_")]) == 5 else "FAIL",
                "detail": f"n_l_columns={len([c for c in forecast_inputs if c.startswith('l_')])}",
            },
            {
                "check": "forecast_excludes_l_validity_flags_from_model_inputs",
                "result": "PASS"
                if len([c for c in forecast_inputs if c.startswith("l_valid")]) == 0
                else "FAIL",
                "detail": f"n_l_valid_in_inputs={len([c for c in forecast_inputs if c.startswith('l_valid')])}",
            },
            {
                "check": "immutable_manifest_checksums",
                "result": "PASS" if checksum_df["checksum_ok"].all() else "FAIL",
                "detail": f"n_checked={len(checksum_df)}",
            },
        ]
    )

    event_contract = _build_event_contract(data["feature_registry"])

    run_specs = _build_ablation_run_specs(seed=seed)
    ablation_plan = pd.DataFrame(
        [
            {
                **spec,
                "cv_mode": cv_mode,
            }
            for spec in run_specs
            for cv_mode in ["fold_safe", "fixed_export"]
        ]
    )

    protocol_md = _build_phase4_protocol_markdown()
    (p.results_dir / "phase4_protocol.md").write_text(protocol_md)
    event_contract.to_csv(p.results_dir / "event_feature_availability_contract.csv", index=False)
    ablation_plan.to_csv(p.results_dir / "phase4_ablation_plan.csv", index=False)
    checksum_df.to_csv(p.results_dir / "phase4_immutable_checksum_audit.csv", index=False)
    contract_checks.to_csv(p.results_dir / "phase4_contract_checks.csv", index=False)

    return {
        "checksum_df": checksum_df,
        "contract_checks": contract_checks,
        "event_contract": event_contract,
        "ablation_plan": ablation_plan,
        "paths": {
            "phase4_protocol_md": str(p.results_dir / "phase4_protocol.md"),
            "event_contract_csv": str(p.results_dir / "event_feature_availability_contract.csv"),
            "ablation_plan_csv": str(p.results_dir / "phase4_ablation_plan.csv"),
            "checksum_audit_csv": str(p.results_dir / "phase4_immutable_checksum_audit.csv"),
            "contract_checks_csv": str(p.results_dir / "phase4_contract_checks.csv"),
        },
    }


def run_fold_safe_fe_engine(paths: Phase4Paths | None = None) -> dict[str, Any]:
    p = paths or get_phase4_paths()
    data = _load_phase_inputs(p)

    train_raw = data["train_raw"].copy()
    cv_plan = data["cv_plan"].copy()
    policy_inputs = list(data["policy_manifest"]["model_input_columns"])
    forecast_inputs = list(data["forecast_manifest"]["model_input_columns"])

    fold_safe_dir = p.internal_dir / "fold_safe"
    fold_safe_dir.mkdir(parents=True, exist_ok=True)

    log_rows = []

    for _, fold in cv_plan.iterrows():
        fold_id = str(fold["fold"])
        train_end_before = pd.to_datetime(fold["train_end_before"])
        valid_start = pd.to_datetime(fold["valid_start"])
        valid_end = pd.to_datetime(fold["valid_end"])

        fold_train_raw = train_raw.loc[train_raw["rounded_hour"] < train_end_before].copy()
        fold_valid_raw = train_raw.loc[
            (train_raw["rounded_hour"] >= valid_start) & (train_raw["rounded_hour"] <= valid_end)
        ].copy()

        layers, fit_payload = _build_fold_feature_layers(
            fold_train_raw=fold_train_raw,
            fold_valid_raw=fold_valid_raw,
            policy_columns=policy_inputs,
            forecast_columns=forecast_inputs,
        )

        fold_dir = fold_safe_dir / fold_id
        fold_dir.mkdir(parents=True, exist_ok=True)

        layers["policy_train"].to_parquet(fold_dir / "policy_train.parquet", index=False)
        layers["policy_valid"].to_parquet(fold_dir / "policy_valid.parquet", index=False)
        layers["forecast_train"].to_parquet(fold_dir / "forecast_train.parquet", index=False)
        layers["forecast_valid"].to_parquet(fold_dir / "forecast_valid.parquet", index=False)
        (fold_dir / "fit_params.json").write_text(json.dumps(fit_payload, indent=2))

        lag_valid_train = float((layers["forecast_train"]["l_valid_all_core"] == 1).mean() * 100)
        lag_valid_valid = float((layers["forecast_valid"]["l_valid_all_core"] == 1).mean() * 100)

        log_rows.append(
            {
                "fold": fold_id,
                "train_end_before": train_end_before,
                "valid_start": valid_start,
                "valid_end": valid_end,
                "n_train_raw": len(fold_train_raw),
                "n_valid_raw": len(fold_valid_raw),
                "n_train_policy": len(layers["policy_train"]),
                "n_valid_policy": len(layers["policy_valid"]),
                "n_train_forecast": len(layers["forecast_train"]),
                "n_valid_forecast": len(layers["forecast_valid"]),
                "lag_valid_rate_train_pct": lag_valid_train,
                "lag_valid_rate_valid_pct": lag_valid_valid,
                "capacity_bin_edges": json.dumps(fit_payload["capacity_bin_edges"]),
                "parking_levels_n": len(fit_payload["parking_levels"]),
                "external_fit_params": json.dumps(fit_payload["external_fit_params"]),
                "event_cascade": json.dumps(fit_payload["event_cascade"]),
                "fit_scope_assertion": "train-only fit parameters applied to fold-valid",
            }
        )

    log_df = pd.DataFrame(log_rows)
    log_df.to_csv(p.results_dir / "phase4_fold_safety_log.csv", index=False)

    return {
        "fold_safety_log": log_df,
        "fold_safe_dir": str(fold_safe_dir),
        "fold_safety_log_csv": str(p.results_dir / "phase4_fold_safety_log.csv"),
    }


def run_ablation_cv(paths: Phase4Paths | None = None) -> dict[str, Any]:
    p = paths or get_phase4_paths()
    data = _load_phase_inputs(p)

    plan_path = p.results_dir / "phase4_ablation_plan.csv"
    if not plan_path.exists():
        run_pre_modelling_audit(paths=p)

    plan_df = pd.read_csv(plan_path)
    cv_plan = data["cv_plan"].copy()

    event_contract_path = p.results_dir / "event_feature_availability_contract.csv"
    event_contract = pd.read_csv(event_contract_path)
    uncertain = set(
        event_contract.loc[event_contract["availability_label"].eq("ex_post_or_uncertain"), "feature_name"].astype(str).tolist()
    )

    fold_cache = _build_fold_cache(paths=p, cv_plan=cv_plan, raw_train=data["train_raw"])

    policy_inputs = list(data["policy_manifest"]["model_input_columns"])
    forecast_inputs = list(data["forecast_manifest"]["model_input_columns"])

    cv_results = _execute_cv_plan_rows(
        plan_rows=plan_df,
        cv_plan=cv_plan,
        fold_cache=fold_cache,
        policy_inputs=policy_inputs,
        forecast_inputs=forecast_inputs,
        uncertain_event_features=uncertain,
    )

    cv_results.to_csv(p.results_dir / "phase4_cv_results.csv", index=False)

    cv_summary = _aggregate_cv_results(cv_results)
    cv_summary.to_csv(p.results_dir / "phase4_cv_summary.csv", index=False)

    return {
        "cv_results": cv_results,
        "cv_summary": cv_summary,
        "cv_results_csv": str(p.results_dir / "phase4_cv_results.csv"),
        "cv_summary_csv": str(p.results_dir / "phase4_cv_summary.csv"),
    }


def _build_refinement_specs(high_var_rows: pd.DataFrame, seed: int = DEFAULT_SEED) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    available_keys = set(_model_grid().keys())
    for _, row in high_var_rows.head(4).iterrows():
        track = str(row["track"])
        variant = str(row["variant"])
        model_family = str(row["model_family"])

        if model_family == "ridge":
            model_key = "ridge_a1_0"
        elif model_family == "random_forest":
            model_key = "rf_90_d12_l2"
        else:
            model_key = "xgb_80_d4_lr006"

        if model_key not in available_keys:
            continue

        specs.append(
            {
                "run_id": f"R1_{variant}_{model_key}",
                "track": track,
                "variant": variant,
                "model_family": _model_grid()[model_key]["model_family"],
                "model_key": model_key,
                "feature_set_id": f"refine_{variant}",
                "row_filter": "l_valid_all_core==1" if variant == "F3" else ("l_valid_core_plus_roll24==1" if variant == "F4" else "none"),
                "seed": seed,
                "primary_metric": "mae",
                "cv_mode": "fold_safe",
            }
        )

    return specs


def run_iterative_critique_and_refine(paths: Phase4Paths | None = None) -> dict[str, Any]:
    p = paths or get_phase4_paths()
    data = _load_phase_inputs(p)

    cv_results_path = p.results_dir / "phase4_cv_results.csv"
    if not cv_results_path.exists():
        run_ablation_cv(paths=p)

    cv_results = pd.read_csv(cv_results_path)
    cv_summary = _aggregate_cv_results(cv_results)

    high_var = cv_summary.loc[
        (cv_summary["cv_mode"] == "fold_safe")
        & (cv_summary["variant"].isin(["P1", "P2", "P3", "P4", "F1", "F2", "F3", "F4"]))
        & (cv_summary["cv_variability_ratio"] > 0.15)
    ].copy()

    refinement_specs = _build_refinement_specs(high_var)

    if refinement_specs:
        fold_cache = _build_fold_cache(paths=p, cv_plan=data["cv_plan"], raw_train=data["train_raw"])
        event_contract = pd.read_csv(p.results_dir / "event_feature_availability_contract.csv")
        uncertain = set(
            event_contract.loc[event_contract["availability_label"].eq("ex_post_or_uncertain"), "feature_name"].astype(str).tolist()
        )
        refined_results = _execute_cv_plan_rows(
            plan_rows=pd.DataFrame(refinement_specs),
            cv_plan=data["cv_plan"],
            fold_cache=fold_cache,
            policy_inputs=list(data["policy_manifest"]["model_input_columns"]),
            forecast_inputs=list(data["forecast_manifest"]["model_input_columns"]),
            uncertain_event_features=uncertain,
        )
        cv_results = pd.concat([cv_results, refined_results], axis=0, ignore_index=True)
        cv_results.to_csv(cv_results_path, index=False)
        cv_summary = _aggregate_cv_results(cv_results)
        cv_summary.to_csv(p.results_dir / "phase4_cv_summary.csv", index=False)

    fold_safe_summary = cv_summary.loc[cv_summary["cv_mode"] == "fold_safe"].copy()

    best_per_variant = (
        fold_safe_summary.sort_values(["track", "variant", "mean_mae", "mean_rmse", "mean_mape"]).groupby(["track", "variant"], as_index=False).first()
    )

    f2_best = best_per_variant.loc[(best_per_variant["track"] == "forecast") & (best_per_variant["variant"] == "F2")]
    f4_best = best_per_variant.loc[(best_per_variant["track"] == "forecast") & (best_per_variant["variant"] == "F4")]

    f4_keep = False
    f4_rule_note = "F4 not available"
    if not f2_best.empty and not f4_best.empty:
        mae_f2 = float(f2_best.iloc[0]["mean_mae"])
        mae_f4 = float(f4_best.iloc[0]["mean_mae"])
        n_f2 = float(f2_best.iloc[0]["mean_n_valid"])
        n_f4 = float(f4_best.iloc[0]["mean_n_valid"])
        gain_pct = ((mae_f2 - mae_f4) / mae_f2) * 100.0 if mae_f2 > 0 else 0.0
        retention_pct = (n_f4 / n_f2) * 100.0 if n_f2 > 0 else 0.0
        f4_keep = gain_pct >= 1.0 and retention_pct >= 80.0
        f4_rule_note = f"F4 gain={gain_pct:.3f}% vs F2; retention={retention_pct:.3f}%"

    shortlist_rows = []
    for _, row in best_per_variant.iterrows():
        track = str(row["track"])
        variant = str(row["variant"])
        status = "candidate"
        selected_for_holdout = False

        if track == "policy":
            if variant in {"P2", "P3", "P4", "P0", "P1"}:
                selected_for_holdout = variant in {"P0", "P2", "P3", "P4"}
        else:
            if variant == "F4" and not f4_keep:
                status = "rejected_by_f4_rule"
                selected_for_holdout = False
            else:
                selected_for_holdout = variant in {"F0", "F1", "F2", "F3", "F4"}

        shortlist_rows.append(
            {
                **row.to_dict(),
                "status": status,
                "selected_for_holdout": selected_for_holdout,
            }
        )

    shortlist = pd.DataFrame(shortlist_rows)

    def _pick_primary(track: str, allowed_variants: set[str]) -> str | None:
        cand = shortlist.loc[
            (shortlist["track"] == track)
            & (shortlist["status"] == "candidate")
            & (shortlist["variant"].isin(allowed_variants))
        ].sort_values(["mean_mae", "mean_rmse", "mean_mape"])
        if cand.empty:
            return None
        return str(cand.iloc[0]["run_id"])

    primary_policy = _pick_primary("policy", {"P2", "P3", "P4"})
    primary_forecast = _pick_primary("forecast", {"F2", "F3", "F4", "F1"})

    shortlist["is_primary_candidate"] = shortlist["run_id"].isin(
        [x for x in [primary_policy, primary_forecast] if x is not None]
    )
    shortlist["selection_note"] = ""
    shortlist.loc[shortlist["variant"] == "F4", "selection_note"] = f4_rule_note

    shortlist.to_csv(p.results_dir / "phase4_model_selection_shortlist.csv", index=False)

    critique_rows = [
        {
            "rule": "high_variability_trigger",
            "value": int(len(high_var)),
            "detail": "count of fold-safe runs with std(MAE)/mean(MAE) > 0.15",
        },
        {
            "rule": "refinement_runs_added",
            "value": int(len(refinement_specs)),
            "detail": "limited targeted reruns added only when variability exceeded threshold",
        },
        {
            "rule": "f4_keep_rule",
            "value": int(f4_keep),
            "detail": f4_rule_note,
        },
    ]
    critique_df = pd.DataFrame(critique_rows)
    critique_df.to_csv(p.results_dir / "phase4_iterative_critique_log.csv", index=False)

    return {
        "cv_results": cv_results,
        "cv_summary": cv_summary,
        "shortlist": shortlist,
        "iterative_log": critique_df,
        "shortlist_csv": str(p.results_dir / "phase4_model_selection_shortlist.csv"),
    }


def _diebold_mariano_abs_loss(e1: np.ndarray, e2: np.ndarray, lag: int = 24) -> dict[str, float]:
    d = np.abs(e1) - np.abs(e2)
    T = len(d)
    if T < 10:
        return {"dm_stat": float("nan"), "p_value": float("nan"), "n": float(T)}

    d_bar = float(np.mean(d))
    gamma0 = float(np.var(d, ddof=1))

    s = gamma0
    for k in range(1, min(lag, T - 1) + 1):
        cov = float(np.cov(d[k:], d[:-k], ddof=1)[0, 1])
        s += 2.0 * (1.0 - k / (lag + 1.0)) * cov

    if s <= 0:
        return {"dm_stat": float("nan"), "p_value": float("nan"), "n": float(T)}

    dm_stat = d_bar / math.sqrt(s / T)
    p_val = float(2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(dm_stat) / math.sqrt(2.0)))))
    return {"dm_stat": float(dm_stat), "p_value": p_val, "n": float(T)}


def run_holdout_and_selection(paths: Phase4Paths | None = None) -> dict[str, Any]:
    p = paths or get_phase4_paths()
    data = _load_phase_inputs(p)

    shortlist_path = p.results_dir / "phase4_model_selection_shortlist.csv"
    if not shortlist_path.exists():
        run_iterative_critique_and_refine(paths=p)

    shortlist = pd.read_csv(shortlist_path)
    shortlist_eval = shortlist.loc[shortlist["selected_for_holdout"] == True].copy()  # noqa: E712

    event_contract = pd.read_csv(p.results_dir / "event_feature_availability_contract.csv")
    uncertain = set(
        event_contract.loc[event_contract["availability_label"].eq("ex_post_or_uncertain"), "feature_name"].astype(str).tolist()
    )

    policy_inputs = list(data["policy_manifest"]["model_input_columns"])
    forecast_inputs = list(data["forecast_manifest"]["model_input_columns"])

    train_raw = data["train_raw"].copy()
    holdout_raw = data["holdout_raw"].copy()

    full_layers, full_fit_payload = _build_fold_feature_layers(
        fold_train_raw=train_raw,
        fold_valid_raw=holdout_raw,
        policy_columns=policy_inputs,
        forecast_columns=forecast_inputs,
    )

    full_dir = p.internal_dir / "full_train_holdout"
    full_dir.mkdir(parents=True, exist_ok=True)
    full_layers["policy_train"].to_parquet(full_dir / "policy_train.parquet", index=False)
    full_layers["policy_valid"].to_parquet(full_dir / "policy_holdout.parquet", index=False)
    full_layers["forecast_train"].to_parquet(full_dir / "forecast_train.parquet", index=False)
    full_layers["forecast_valid"].to_parquet(full_dir / "forecast_holdout.parquet", index=False)
    (full_dir / "fit_params.json").write_text(json.dumps(full_fit_payload, indent=2))

    holdout_rows = []
    pred_store: dict[str, pd.DataFrame] = {}

    for _, row in shortlist_eval.iterrows():
        run_id = str(row["run_id"])
        track = str(row["track"])
        variant = str(row["variant"])
        model_family = str(row["model_family"])
        model_key = str(row["model_key"])

        feature_cols = _get_variant_features(
            track=track,
            variant=variant,
            policy_inputs=policy_inputs,
            forecast_inputs=forecast_inputs,
            uncertain_event_features=uncertain,
        )

        if track == "policy":
            train_df = full_layers["policy_train"].copy()
            hold_df = full_layers["policy_valid"].copy()
        else:
            train_df = full_layers["forecast_train"].copy()
            hold_df = full_layers["forecast_valid"].copy()

        row_filter = "none"
        if variant == "F3":
            row_filter = "l_valid_all_core==1"
        elif variant == "F4":
            row_filter = "l_valid_core_plus_roll24==1"

        train_df = _apply_row_filter(train_df, row_filter)
        hold_df = _apply_row_filter(hold_df, row_filter)

        train_df = train_df.dropna(subset=["occupancy_rate"]).copy()
        hold_df = hold_df.dropna(subset=["occupancy_rate"]).copy()

        y_train = train_df["occupancy_rate"].to_numpy(dtype=float)
        y_hold = hold_df["occupancy_rate"].to_numpy(dtype=float)

        if model_family == "baseline" and model_key == "profile_baseline":
            y_pred = _profile_baseline_predict(train_df, hold_df)
        elif model_family == "baseline" and model_key == "persistence_baseline":
            y_pred = _persistence_baseline_predict(train_df, hold_df)
        else:
            model = _make_regressor(model_key=model_key, seed=DEFAULT_SEED)
            model.fit(train_df[feature_cols], y_train)
            y_pred = model.predict(hold_df[feature_cols]).astype(float)

        metrics = _metric_bundle(hold_df, y_hold, y_pred)

        holdout_rows.append(
            {
                "run_id": run_id,
                "track": track,
                "variant": variant,
                "selected": bool(row.get("is_primary_candidate", False)),
                **metrics,
                "n_rows": int(len(hold_df)),
            }
        )

        pred_store[run_id] = hold_df[["parking_id", "rounded_hour", "occupancy_rate"]].copy()
        pred_store[run_id]["y_pred"] = y_pred

    holdout_results = pd.DataFrame(holdout_rows).sort_values(["track", "mae", "rmse", "mape"])
    holdout_results.to_csv(p.results_dir / "phase4_holdout_results_2025.csv", index=False)

    dm_rows = []
    for track in ["policy", "forecast"]:
        track_rows = holdout_results.loc[holdout_results["track"] == track].sort_values("mae")
        if len(track_rows) < 2:
            continue
        r1 = str(track_rows.iloc[0]["run_id"])
        r2 = str(track_rows.iloc[1]["run_id"])

        a = pred_store[r1]
        b = pred_store[r2]
        m = a.merge(
            b,
            on=["parking_id", "rounded_hour"],
            suffixes=("_a", "_b"),
            how="inner",
        )
        if m.empty:
            continue

        e1 = (m["occupancy_rate_a"] - m["y_pred_a"]).to_numpy(dtype=float)
        e2 = (m["occupancy_rate_a"] - m["y_pred_b"]).to_numpy(dtype=float)
        dm = _diebold_mariano_abs_loss(e1=e1, e2=e2, lag=24)
        dm_rows.append(
            {
                "track": track,
                "best_run": r1,
                "second_run": r2,
                **dm,
            }
        )

    dm_df = pd.DataFrame(dm_rows)
    dm_path = p.results_dir / "phase4_dm_tests.csv"
    dm_df.to_csv(dm_path, index=False)

    cv_summary = pd.read_csv(p.results_dir / "phase4_cv_summary.csv")
    fold_safe_best = (
        cv_summary.loc[cv_summary["cv_mode"].eq("fold_safe")]
        .sort_values(["track", "mean_mae", "mean_rmse", "mean_mape"])
        .groupby("track", as_index=False)
        .first()
    )

    fixed_best = (
        cv_summary.loc[cv_summary["cv_mode"].eq("fixed_export")]
        .sort_values(["track", "mean_mae", "mean_rmse", "mean_mape"])
        .groupby("track", as_index=False)
        .first()
    )

    contract_checks = pd.read_csv(p.results_dir / "phase4_contract_checks.csv")
    fold_log = pd.read_csv(p.results_dir / "phase4_fold_safety_log.csv")

    go_checks = [
        ("pre_run_audit_pass", bool((contract_checks["result"] == "PASS").all())),
        (
            "fold_safety_log_complete",
            bool((fold_log["n_train_raw"] > 0).all() and (fold_log["n_valid_raw"] > 0).all()),
        ),
        (
            "all_variants_present_fold_safe",
            bool(
                set(
                    pd.read_csv(p.results_dir / "phase4_cv_results.csv")
                    .loc[lambda d: d["cv_mode"].eq("fold_safe")]
                    ["variant"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
                >= {"P0", "P1", "P2", "P3", "P4", "F0", "F1", "F2", "F3", "F4"}
            ),
        ),
        (
            "policy_tradeoff_reported",
            bool(set(holdout_results.loc[holdout_results["track"].eq("policy"), "variant"].astype(str)) >= {"P2", "P3", "P4"}),
        ),
        (
            "selection_not_fixed_export_only",
            bool(len(fold_safe_best) > 0),
        ),
    ]

    go_status = all(flag for _, flag in go_checks)

    memo_lines = [
        "# Phase 4 Model Selection Memo",
        "",
        "Datum: 2026-03-13",
        "",
        "## Finale feature sets",
        "- Policy track: T+S+E (met expliciete vergelijking P2/P3/P4).",
        "- Forecast track: T+S+E+L (met lag-valid sensitivities).",
        "",
        "## Fold-safe CV (primary)",
    ]

    for _, r in fold_safe_best.iterrows():
        memo_lines.append(
            f"- {r['track']}: best `{r['run_id']}` met MAE={r['mean_mae']:.4f}, RMSE={r['mean_rmse']:.4f}, MAPE={r['mean_mape']:.3f}."
        )

    memo_lines.append("")
    memo_lines.append("## Fixed-export sensitivity (reference only)")
    for _, r in fixed_best.iterrows():
        memo_lines.append(
            f"- {r['track']}: best `{r['run_id']}` met MAE={r['mean_mae']:.4f}, RMSE={r['mean_rmse']:.4f}, MAPE={r['mean_mape']:.3f}."
        )

    memo_lines.extend(
        [
            "",
            "## Holdout 2025 resultaten",
        ]
    )

    for _, r in holdout_results.iterrows():
        sel = " (selected)" if bool(r["selected"]) else ""
        memo_lines.append(
            f"- {r['track']} {r['run_id']}{sel}: MAE={r['mae']:.4f}, RMSE={r['rmse']:.4f}, MAPE={r['mape']:.3f}, n={int(r['n_rows'])}."
        )

    if not dm_df.empty:
        memo_lines.extend(["", "## DM-test (optioneel)"])
        for _, r in dm_df.iterrows():
            memo_lines.append(
                f"- {r['track']}: `{r['best_run']}` vs `{r['second_run']}` -> DM={r['dm_stat']:.4f}, p={r['p_value']:.4f}, n={int(r['n'])}."
            )

    memo_lines.extend(["", "## Go / No-Go checks"])
    for name, flag in go_checks:
        memo_lines.append(f"- {name}: {'PASS' if flag else 'FAIL'}")

    memo_lines.append("")
    memo_lines.append(f"## Eindstatus: {'GO' if go_status else 'NO-GO'}")

    memo_lines.extend(
        [
            "",
            "## Feature engineering choices that must not be violated later",
            "- Geen holdout-gedreven tuning.",
            "- Fold-safe refit blijft primaire evaluatiebasis.",
            "- Policy en forecast blijven strikt gescheiden qua L-features.",
            "",
            "## Recommended modelling ablation map",
            "- Policy: P0, P1, P2, P3, P4",
            "- Forecast: F0, F1, F2, F3, F4",
        ]
    )

    memo_path = p.results_dir / "phase4_model_selection_memo.md"
    memo_path.write_text("\n".join(memo_lines))

    return {
        "holdout_results": holdout_results,
        "dm_tests": dm_df,
        "memo_path": str(memo_path),
        "holdout_results_csv": str(p.results_dir / "phase4_holdout_results_2025.csv"),
    }
