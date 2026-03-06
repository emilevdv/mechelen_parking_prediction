from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd


QC_MAP = {
    "precip_quantity": "PRECIP_QUANTITY",
    "temp_dry_shelter_avg": "TEMP_DRY_SHELTER_AVG",
    "wind_speed_10m": "WIND_SPEED_10M",
    "wind_gusts_speed": "WIND_GUSTS_SPEED",
    "humidity_rel_shelter_avg": "HUMIDITY_REL_SHELTER_AVG",
    "pressure": "PRESSURE",
    "sun_duration": "SUN_DURATION",
    "short_wave_from_sky_avg": "SHORT_WAVE_FROM_SKY_AVG",
    "sun_int_avg": "SUN_INT_AVG",
}

LOW_INVALID_COLS = [
    "precip_quantity",
    "temp_dry_shelter_avg",
    "wind_speed_10m",
    "wind_gusts_speed",
    "pressure",
]

SOLAR_COLS_RAW = ["short_wave_from_sky_avg", "sun_int_avg"]
SOLAR_COLS_CLEAN = ["sun_duration_min", "shortwave_wm2", "sun_intensity_wm2"]

SOLAR_MAX_WM2 = 1400
SOLAR_MIN_WM2 = -5
WMO_THRESHOLD_WM2 = 120

SLOW_VARS = {
    "temp_c": 6,
    "wind_speed_ms": 3,
    "humidity_pct": 3,
    "pressure_hpa": 6,
}

RENAME_MAP = {
    "timestamp": "timestamp",
    "temp_dry_shelter_avg": "temp_c",
    "precip_quantity": "precip_mm",
    "wind_speed_10m": "wind_speed_ms",
    "wind_gusts_speed": "wind_gusts_ms",
    "humidity_rel_shelter_avg": "humidity_pct",
    "pressure": "pressure_hpa",
    "sun_duration": "sun_duration_min",
    "short_wave_from_sky_avg": "shortwave_wm2",
    "sun_int_avg": "sun_intensity_wm2",
    "qc_temp_dry_shelter_avg": "qc_temp",
    "qc_precip_quantity": "qc_precip",
    "qc_wind_speed_10m": "qc_wind_speed",
    "qc_wind_gusts_speed": "qc_wind_gusts",
    "qc_humidity_rel_shelter_avg": "qc_humidity",
    "qc_pressure": "qc_pressure",
    "humidity_suspect": "humidity_suspect",
    "sun_duration_inconsistent": "sun_duration_inconsistent",
}

WEATHER_EXPORT_COL_ORDER = [
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
]

NIGHT_HOURS_BY_MONTH = {
    1: list(range(0, 8)) + list(range(17, 24)),
    2: list(range(0, 8)) + list(range(18, 24)),
    3: list(range(0, 7)) + list(range(19, 24)),
    4: list(range(0, 6)) + list(range(21, 24)),
    5: list(range(0, 5)) + list(range(21, 24)),
    6: list(range(0, 5)) + list(range(22, 24)),
    7: list(range(0, 5)) + list(range(22, 24)),
    8: list(range(0, 6)) + list(range(21, 24)),
    9: list(range(0, 7)) + list(range(20, 24)),
    10: list(range(0, 7)) + list(range(18, 24)),
    11: list(range(0, 8)) + list(range(17, 24)),
    12: list(range(0, 8)) + list(range(16, 24)),
}

DST_SPRING = ["2020-03-29", "2021-03-28", "2022-03-27", "2023-03-26", "2024-03-31", "2025-03-30"]
DST_AUTUMN = ["2020-10-25", "2021-10-31", "2022-10-30", "2023-10-29", "2024-10-27", "2025-10-26"]

FEATURE_COLS_CHECK = [
    "temp_c",
    "precip_mm",
    "wind_speed_ms",
    "wind_gusts_ms",
    "humidity_pct",
    "pressure_hpa",
    "sun_duration_min",
    "shortwave_wm2",
    "sun_intensity_wm2",
]


def parse_qc_flags(qc_str: str) -> dict[str, Any]:
    try:
        return json.loads(qc_str).get("validated", {})
    except (json.JSONDecodeError, TypeError, AttributeError):
        return {}


def add_qc_columns(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    qc_parsed = df_raw["qc_flags"].map(parse_qc_flags)
    df = df_raw.copy()

    stats_rows: list[dict[str, Any]] = []
    for col, qc_key in QC_MAP.items():
        if col not in df.columns:
            continue
        qc_col = f"qc_{col}"
        df[qc_col] = qc_parsed.map(lambda d, k=qc_key: d.get(k, None))
        total = int(df[qc_col].notna().sum())
        valid = int((df[qc_col] == True).sum())  # noqa: E712
        invalid = int((df[qc_col] == False).sum())  # noqa: E712
        stats_rows.append(
            {
                "variable": col,
                "n_total": total,
                "n_valid": valid,
                "n_invalid": invalid,
                "pct_valid": (valid / total * 100) if total else 0.0,
                "pct_invalid": (invalid / total * 100) if total else 0.0,
            }
        )

    stats_df = pd.DataFrame(stats_rows).sort_values("variable").reset_index(drop=True)
    return df, stats_df


def clean_low_invalid_group(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, int]]]:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    stats: dict[str, dict[str, int]] = {}

    for col in LOW_INVALID_COLS:
        qc_col = f"qc_{col}"
        if qc_col not in out.columns:
            continue
        mask = out[qc_col] == False  # noqa: E712
        n_set_nan = int(mask.sum())
        out.loc[mask, col] = np.nan
        stats[col] = {"set_nan": n_set_nan}

    out = out.set_index("timestamp")
    for col in LOW_INVALID_COLS:
        if col not in out.columns:
            continue
        before = int(out[col].isna().sum())
        out[col] = out[col].interpolate(method="time", limit=2, limit_direction="forward")
        after = int(out[col].isna().sum())
        stats.setdefault(col, {})
        stats[col]["interpolated"] = before - after
        stats[col]["remaining_nan"] = after

    return out.reset_index(), stats


def add_humidity_suspect_flag(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()
    out["humidity_suspect"] = (out["qc_humidity_rel_shelter_avg"] == False).astype(int)  # noqa: E712
    run_id = (out["humidity_suspect"] != out["humidity_suspect"].shift()).cumsum()
    suspect_periods = (
        out.assign(run_group=run_id)
        .groupby("run_group")
        .agg(
            is_suspect=("humidity_suspect", "first"),
            start=("timestamp", "min"),
            end=("timestamp", "max"),
            n_uur=("humidity_suspect", "count"),
        )
        .query("is_suspect == 1")
        .drop(columns="is_suspect")
        .reset_index(drop=True)
    )
    suspect_periods["duur_dagen"] = (suspect_periods["n_uur"] / 24).round(1)
    return out, suspect_periods


def clean_solar_physical_range(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()
    rows: list[dict[str, int]] = []
    for col in SOLAR_COLS_RAW:
        if col not in out.columns:
            continue
        before_nan = int(out[col].isna().sum())
        invalid = (out[col] < SOLAR_MIN_WM2) | (out[col] > SOLAR_MAX_WM2)
        n_physical_fail = int(invalid.sum())
        out.loc[invalid, col] = np.nan
        out[col] = out[col].clip(lower=0)
        after_nan = int(out[col].isna().sum())
        rows.append(
            {
                "column": col,
                "n_physical_fail": n_physical_fail,
                "n_nan_before": before_nan,
                "n_nan_after": after_nan,
            }
        )
    return out, pd.DataFrame(rows)


def add_sun_duration_inconsistency_flag(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    out = df.copy()
    inconsistent_mask = (out["short_wave_from_sky_avg"] > WMO_THRESHOLD_WM2) & (
        out["sun_duration"] == 0
    )
    out["sun_duration_inconsistent"] = inconsistent_mask.astype(int)

    valid_solar = out[
        out["short_wave_from_sky_avg"].notna()
        & out["sun_duration"].notna()
        & (out["short_wave_from_sky_avg"] > 0)
    ]
    r = valid_solar["short_wave_from_sky_avg"].corr(valid_solar["sun_duration"])
    stats = {
        "pearson_r": float(r) if pd.notna(r) else float("nan"),
        "n_inconsistent": int(inconsistent_mask.sum()),
        "pct_inconsistent": float(inconsistent_mask.mean() * 100),
        "threshold_wm2": float(WMO_THRESHOLD_WM2),
    }
    return out, stats


def build_weather_clean_base(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    cols_present = [c for c in RENAME_MAP if c in df.columns]
    cols_missing = [c for c in RENAME_MAP if c not in df.columns]
    out = df[cols_present].rename(columns={k: RENAME_MAP[k] for k in cols_present}).copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    out = out.reset_index(drop=True)
    return out, cols_missing, cols_present


def impute_weather_features(df_clean: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df_clean.copy()
    out["precip_imputed"] = out["precip_mm"].isna().astype(int)
    stats_rows: list[dict[str, Any]] = []

    imp = out.set_index("timestamp").sort_index()
    night_mask_idx = imp.index.to_series().apply(
        lambda ts: ts.hour in NIGHT_HOURS_BY_MONTH.get(ts.month, [])
    )

    for col, limit in SLOW_VARS.items():
        before = int(imp[col].isna().sum())
        imp[col] = imp[col].interpolate(method="time", limit=limit, limit_direction="both")
        after = int(imp[col].isna().sum())
        stats_rows.append(
            {
                "column": col,
                "strategy": f"time_interp_limit_{limit}",
                "n_before": before,
                "n_after": after,
            }
        )

    before = int(imp["wind_gusts_ms"].isna().sum())
    imp["wind_gusts_ms"] = imp["wind_gusts_ms"].fillna(imp["wind_speed_ms"])
    after = int(imp["wind_gusts_ms"].isna().sum())
    stats_rows.append(
        {
            "column": "wind_gusts_ms",
            "strategy": "fillna_wind_speed_ms",
            "n_before": before,
            "n_after": after,
        }
    )

    before = int(imp["precip_mm"].isna().sum())
    imp["precip_mm"] = imp["precip_mm"].fillna(0.0)
    after = int(imp["precip_mm"].isna().sum())
    stats_rows.append(
        {"column": "precip_mm", "strategy": "fillna_0", "n_before": before, "n_after": after}
    )

    for col in SOLAR_COLS_CLEAN:
        before = int(imp[col].isna().sum())
        imp.loc[night_mask_idx & imp[col].isna(), col] = 0.0
        after_night = int(imp[col].isna().sum())
        imp[col] = imp[col].interpolate(method="time", limit=2, limit_direction="both")
        after = int(imp[col].isna().sum())
        stats_rows.append(
            {
                "column": col,
                "strategy": "night_to_0_then_time_interp_limit_2",
                "n_before": before,
                "n_after_night": after_night,
                "n_after": after,
            }
        )

    return imp.reset_index(), pd.DataFrame(stats_rows)


def check_weather_series_integrity(df_clean: pd.DataFrame) -> dict[str, Any]:
    full_index = pd.date_range(
        start=df_clean["timestamp"].min(), end=df_clean["timestamp"].max(), freq="h"
    )
    actual_set = set(df_clean["timestamp"])
    expected_set = set(full_index)
    missing_hours = sorted(expected_set - actual_set)
    surplus_hours = sorted(actual_set - expected_set)

    tmp = df_clean.copy()
    tmp["_date"] = tmp["timestamp"].dt.date
    dst_rows: list[dict[str, Any]] = []
    for d in DST_SPRING:
        n = int((tmp["_date"] == pd.Timestamp(d).date()).sum())
        dst_rows.append({"date": d, "type": "lente->zomer", "hours": n, "expected": 23, "ok": n == 23})
    for d in DST_AUTUMN:
        n = int((tmp["_date"] == pd.Timestamp(d).date()).sum())
        dst_rows.append({"date": d, "type": "zomer->winter", "hours": n, "expected": 25, "ok": n == 25})

    return {
        "expected_hours": len(full_index),
        "actual_hours": len(df_clean),
        "missing_hours": missing_hours,
        "surplus_hours": surplus_hours,
        "dst_check": pd.DataFrame(dst_rows),
    }


def to_weather_export_frame(df_clean: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    missing = [c for c in WEATHER_EXPORT_COL_ORDER if c not in df_clean.columns]
    extra = [c for c in df_clean.columns if c not in WEATHER_EXPORT_COL_ORDER]
    export_cols = [c for c in WEATHER_EXPORT_COL_ORDER if c in df_clean.columns]
    return df_clean[export_cols].copy(), missing, extra


def validate_export_no_nan(
    df_export: pd.DataFrame, feature_cols: list[str] | None = None
) -> pd.DataFrame:
    cols = feature_cols or list(df_export.columns)
    rows: list[dict[str, Any]] = []
    for col in cols:
        n_na = int(df_export[col].isna().sum())
        pct = float((n_na / len(df_export) * 100) if len(df_export) else 0.0)
        rows.append(
            {
                "column": col,
                "dtype": str(df_export[col].dtype),
                "n_nan": n_na,
                "pct_nan": pct,
                "status": "OK" if n_na == 0 else "HAS_NAN",
            }
        )
    return pd.DataFrame(rows)
