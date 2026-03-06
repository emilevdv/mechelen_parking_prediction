from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss


def run_stationarity_tests(series, name: str = "series") -> dict[str, object]:
    series = pd.Series(series).dropna()

    adf_res = adfuller(series, autolag="AIC", regression="ct")
    adf_stat, adf_p, adf_lags = adf_res[0], adf_res[1], adf_res[2]

    kpss_res = kpss(series, regression="ct", nlags="auto")
    kpss_stat, kpss_p, kpss_lags = kpss_res[0], kpss_res[1], kpss_res[2]

    adf_reject = adf_p < 0.05
    kpss_reject = kpss_p < 0.05

    if adf_reject and not kpss_reject:
        conclusion = "STATIONAIR"
    elif not adf_reject and kpss_reject:
        conclusion = "NIET-STATIONAIR"
    elif adf_reject and kpss_reject:
        conclusion = "TREND-STATIONAIR (differentiatie aanbevolen)"
    else:
        conclusion = "ONDUIDELIJK (meer diagnostiek vereist)"

    return {
        "name": name,
        "n_obs": len(series),
        "adf_stat": round(adf_stat, 4),
        "adf_p": round(adf_p, 4),
        "adf_lags": adf_lags,
        "adf_reject_h0": adf_reject,
        "kpss_stat": round(kpss_stat, 4),
        "kpss_p": round(kpss_p, 4),
        "kpss_lags": kpss_lags,
        "kpss_reject_h0": kpss_reject,
        "conclusion": conclusion,
    }


def detect_bimodality(tier: str, df: pd.DataFrame) -> dict[str, object]:
    prof = (
        df[(df["tier"] == tier) & (df["day_type_3"] == "weekday")]
        .groupby("hour")["occupancy_rate"]
        .mean()
        .reindex(range(24))
    )
    window = prof.iloc[6:21]
    local_maxima = [
        h
        for i, h in enumerate(window.index[1:-1], start=1)
        if window.iloc[i] > window.iloc[i - 1] and window.iloc[i] > window.iloc[i + 1]
    ]
    peak_values = [(h, round(prof[h], 4)) for h in local_maxima]
    n_peaks = len(local_maxima)

    prof_we = (
        df[(df["tier"] == tier) & (df["day_type_3"].isin(["saturday", "sunday_holiday"]))]
        .groupby("hour")["occupancy_rate"]
        .mean()
        .reindex(range(24))
    )
    window_we = prof_we.iloc[6:21]
    local_maxima_we = [
        h
        for i, h in enumerate(window_we.index[1:-1], start=1)
        if window_we.iloc[i] > window_we.iloc[i - 1] and window_we.iloc[i] > window_we.iloc[i + 1]
    ]

    weekday_bimodal = n_peaks >= 2
    weekend_unimodal = len(local_maxima_we) <= 1

    return {
        "tier": tier,
        "n_weekday_peaks": n_peaks,
        "weekday_peak_hours": peak_values,
        "n_weekend_peaks": len(local_maxima_we),
        "weekend_unimodal": weekend_unimodal,
        "H_T1_weekday_bimodal": weekday_bimodal,
        "H_T1_confirmed": weekday_bimodal and weekend_unimodal,
    }


def evaluate_ht2(tier: str, acf_dict: dict, df: pd.DataFrame) -> dict[str, object]:
    n_obs = len(
        df[(df["tier"] == tier) & (df["year"].isin([2023, 2024]))]
        .groupby("rounded_hour")["occupancy_rate"]
        .mean()
    )
    sig_band = 1.96 / np.sqrt(max(n_obs, 1))

    acf_vals = acf_dict[tier]["acf"]

    lag24_val = float(acf_vals[24]) if len(acf_vals) > 24 else np.nan
    lag48_val = float(acf_vals[48]) if len(acf_vals) > 48 else np.nan
    lag168_val = float(acf_vals[168]) if len(acf_vals) > 168 else np.nan

    lag24_sig = abs(lag24_val) > sig_band if not np.isnan(lag24_val) else False
    lag168_sig = abs(lag168_val) > sig_band if not np.isnan(lag168_val) else False

    return {
        "tier": tier,
        "n_obs": n_obs,
        "sig_band_95": round(sig_band, 4),
        "acf_lag1": round(float(acf_vals[1]), 4) if len(acf_vals) > 1 else np.nan,
        "acf_lag24": round(lag24_val, 4),
        "acf_lag48": round(lag48_val, 4),
        "acf_lag168": round(lag168_val, 4),
        "lag24_significant": lag24_sig,
        "lag168_significant": lag168_sig,
        "sincos_encoding_justified": lag24_sig and lag168_sig,
        "H_T2_confirmed": lag24_sig and lag168_sig,
    }


def evaluate_ht3(tier: str, df_stat: pd.DataFrame) -> dict[str, object]:
    results = {}
    for level_tag, label in [
        ("Ruw", "niveau_0"),
        ("Δ₁", "delta_1"),
        ("Δ₂₄", "delta_24"),
    ]:
        row = df_stat[
            df_stat["name"].str.contains(f"{tier}")
            & df_stat["name"].str.contains(level_tag)
        ]
        if row.empty:
            results[label] = {
                "conclusion": "DATA ONTBREEKT",
                "adf_p": np.nan,
                "kpss_p": np.nan,
            }
            continue

        r = row.iloc[0]
        results[label] = {
            "adf_p": round(r["adf_p"], 4),
            "kpss_p": round(r["kpss_p"], 4),
            "adf_reject": bool(r["adf_reject_h0"]),
            "kpss_reject": bool(r["kpss_reject_h0"]),
            "conclusion": r["conclusion"],
        }

    d24_concl = results.get("delta_24", {}).get("conclusion", "")
    ht3_confirmed = "STATIONAIR" in d24_concl

    raw_concl = results.get("niveau_0", {}).get("conclusion", "")
    differentiatie_needed = "STATIONAIR" not in raw_concl

    return {
        "tier": tier,
        **{f"{k}_{sub}": v2 for k, v in results.items() for sub, v2 in v.items()},
        "H_T3_confirmed": ht3_confirmed,
        "differentiatie_needed": differentiatie_needed,
        "recommended_diff": "Δ₂₄" if ht3_confirmed else "Δ₁ of hogere orde",
    }


def evaluate_ht4(tier: str, covid_res_list: list[dict[str, object]]) -> dict[str, object]:
    row = next((r for r in covid_res_list if r["tier"] == tier), None)
    if row is None:
        return {"tier": tier, "H_T4_confirmed": False, "note": "Geen data"}

    niveau_shift_sig = row.get("mw_p", 1.0) < 0.05
    niveau_lager_2020 = row.get("delta_abs", 0) > 0
    r_struct = row.get("pearson_r_hourly_structure", np.nan)
    struct_gelijk = r_struct > 0.95 if not np.isnan(r_struct) else False

    ht4_confirmed = niveau_shift_sig and niveau_lager_2020 and struct_gelijk

    year_feature_advice = (
        "year-dummy NOODZAKELIJK (categorisch, niet ordinaal)"
        if niveau_shift_sig
        else "year-dummy optioneel (geen significant niveauverschil)"
    )

    return {
        "tier": tier,
        "mean_occ_2020": round(row.get("mean_2020", np.nan), 4),
        "mean_occ_2023": round(row.get("mean_2023", np.nan), 4),
        "delta_2023_minus_2020": round(row.get("delta_abs", np.nan), 4),
        "mw_p_value": round(row.get("mw_p", 1.0), 6),
        "effect_size_r": round(row.get("effect_size_r", np.nan), 4),
        "effect_label": row.get("effect_label", "?"),
        "pearson_r_uurprofiel": round(r_struct, 4) if not np.isnan(r_struct) else np.nan,
        "structuur_gelijk": struct_gelijk,
        "niveau_shift_sig": niveau_shift_sig,
        "H_T4_confirmed": ht4_confirmed,
        "year_feature_advice": year_feature_advice,
    }
