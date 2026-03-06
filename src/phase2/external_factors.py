from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant


def assign_precip_bin(x):
    if pd.isna(x):
        return np.nan
    if x == 0:
        return "droog"
    if x <= 2:
        return "licht"
    if x <= 10:
        return "matig"
    return "zwaar"


def assign_temp_bin(x):
    if pd.isna(x):
        return np.nan
    if x < 5:
        return "koud (<5°C)"
    if x < 15:
        return "koel (5-15°C)"
    if x < 25:
        return "warm (15-25°C)"
    return "heet (≥25°C)"


def scale_to_num(val):
    if pd.isna(val):
        return 2
    if isinstance(val, (int, float)):
        num = int(val)
        return num if num in (1, 2, 3) else 2

    text = str(val).strip().lower()
    mapping = {
        "klein": 1,
        "small": 1,
        "1": 1,
        "medium": 2,
        "middle": 2,
        "2": 2,
        "groot": 3,
        "large": 3,
        "big": 3,
        "3": 3,
    }
    return mapping.get(text, 2)


def cyclic_encode(series, max_val):
    return (np.sin(2 * np.pi * series / max_val), np.cos(2 * np.pi * series / max_val))


def compute_vif(df_input: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    available = [
        c for c in feature_cols if c in df_input.columns and df_input[c].notna().sum() > 100
    ]
    df_feat = df_input[available].dropna()

    if len(df_feat) == 0 or len(available) < 2:
        return pd.DataFrame()

    np.random.seed(42)
    n_sample = min(20000, len(df_feat))
    df_feat = df_feat.sample(n_sample, random_state=42)

    X = add_constant(df_feat.values, has_constant="add")
    col_names = ["const"] + available

    rows: list[dict[str, object]] = []
    for i, col in enumerate(col_names):
        if col == "const":
            continue
        try:
            vif_val = variance_inflation_factor(X, i)
        except Exception:
            vif_val = np.nan
        rows.append(
            {
                "feature": col,
                "vif": round(float(vif_val), 3),
                "status": (
                    "🔴 ernstig"
                    if vif_val > 10
                    else "🟡 zorgwekkend"
                    if vif_val > 5
                    else "✅ acceptabel"
                ),
            }
        )

    return pd.DataFrame(rows).sort_values("vif", ascending=False)


def build_delta_profile(
    df_train: pd.DataFrame,
    baseline: pd.DataFrame,
    tier_order: list[str],
    lag_range: list[int],
    event_col: str,
    anchor_col: str | None,
    default_hour: int,
    confidence_filter: str | None = None,
):
    if event_col not in df_train.columns:
        return {}, pd.DataFrame()

    df_ev = df_train[df_train[event_col] == 1].copy()

    if confidence_filter is not None and "data_confidence" in df_ev.columns:
        df_ev = df_ev[df_ev["data_confidence"] == confidence_filter].copy()

    if len(df_ev) == 0:
        return {}, pd.DataFrame()

    if anchor_col and anchor_col in df_ev.columns:
        df_ev["anchor_hour"] = df_ev[anchor_col].fillna(default_hour).astype(float).astype(int)
    else:
        df_ev["anchor_hour"] = int(default_hour)

    df_ev["lag_t"] = df_ev["hour"].astype(int) - df_ev["anchor_hour"].astype(int)

    df_ev = df_ev.merge(
        baseline,
        on=["tier", "weekday_int", "hour", "season"],
        how="left",
    )
    df_ev["delta"] = df_ev["occupancy_rate"] - df_ev["baseline_occ"]
    df_ev = df_ev[df_ev["lag_t"].between(min(lag_range), max(lag_range))]

    profiles = {}
    for tier in tier_order:
        df_tier = df_ev[df_ev["tier"] == tier]
        lag_profile = []

        for lag in lag_range:
            deltas = df_tier[df_tier["lag_t"] == lag]["delta"].dropna().values
            if len(deltas) < 3:
                lag_profile.append(
                    {
                        "lag": lag,
                        "mean_delta": np.nan,
                        "ci_lo": np.nan,
                        "ci_hi": np.nan,
                        "n": len(deltas),
                    }
                )
                continue

            np.random.seed(42)
            boot_means = [
                np.mean(np.random.choice(deltas, size=len(deltas), replace=True))
                for _ in range(1000)
            ]
            lag_profile.append(
                {
                    "lag": lag,
                    "mean_delta": round(float(np.mean(deltas)), 4),
                    "ci_lo": round(float(np.percentile(boot_means, 2.5)), 4),
                    "ci_hi": round(float(np.percentile(boot_means, 97.5)), 4),
                    "n": len(deltas),
                }
            )
        profiles[tier] = lag_profile

    return profiles, df_ev
