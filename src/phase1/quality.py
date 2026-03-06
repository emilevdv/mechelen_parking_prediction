from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


KNOWN_CAPACITIES = {
    "P Grote Markt": 155,
    "P Hoogstraat": 109,
    "P Kathedraal": 130,
    "P Lamot": 255,
    "P Veemarkt": 129,
    "P Bruul": 350,
    "P Komet": 124,
    "P Maarten": 189,
    "P Tinel": 124,
    "P Zandpoortvest": 622,
    "P Keerdok": 516,
}

DST_TRANSITIONS_2019_2026 = [
    ("2019-03-31", "zomer->"),
    ("2019-10-27", "<-winter"),
    ("2020-03-29", "zomer->"),
    ("2020-10-25", "<-winter"),
    ("2021-03-28", "zomer->"),
    ("2021-10-31", "<-winter"),
    ("2022-03-27", "zomer->"),
    ("2022-10-30", "<-winter"),
    ("2023-03-26", "zomer->"),
    ("2023-10-29", "<-winter"),
    ("2024-03-31", "zomer->"),
    ("2024-10-27", "<-winter"),
    ("2025-03-30", "zomer->"),
    ("2025-10-26", "<-winter"),
    ("2026-03-29", "zomer->"),
    ("2026-10-25", "<-winter"),
]

FREEZE_THRESHOLD = 4
DISCREPANCY_THRESHOLD = 0.01


@dataclass
class QualityLogger:
    rows: list[dict[str, object]] = field(default_factory=list)

    def log(
        self, check_name: str, dataset: str, result: str, n_affected: int, action: str
    ) -> None:
        self.rows.append(
            {
                "check": check_name,
                "dataset": dataset,
                "result": result,
                "n_affected": int(n_affected),
                "action": action,
            }
        )

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows, columns=["check", "dataset", "result", "n_affected", "action"])


def evaluate_parking_location(
    df_loc: pd.DataFrame,
    expected_n_parkings: int = 15,
    known_capacities: dict[str, int] | None = None,
) -> tuple[int, pd.Series, pd.DataFrame]:
    n_parkings = int(df_loc["parking_id"].nunique())
    if n_parkings != expected_n_parkings:
        raise AssertionError(
            f"Verwacht {expected_n_parkings} parkings, gevonden: {n_parkings}"
        )

    categories = df_loc["parking_location_category"].value_counts(dropna=False)
    capacities = known_capacities or KNOWN_CAPACITIES

    rows: list[dict[str, object]] = []
    for parking_id, expected in capacities.items():
        match = df_loc.loc[df_loc["parking_id"] == parking_id, "total_capacity"]
        if match.empty:
            rows.append(
                {
                    "parking_id": parking_id,
                    "status": "MISSING",
                    "expected_capacity": expected,
                    "actual_capacity": np.nan,
                }
            )
        else:
            actual = int(match.iloc[0])
            rows.append(
                {
                    "parking_id": parking_id,
                    "status": "OK" if actual == expected else "MISMATCH",
                    "expected_capacity": expected,
                    "actual_capacity": actual,
                }
            )

    return n_parkings, categories, pd.DataFrame(rows)


def compute_shortterm_completeness(df_st: pd.DataFrame) -> pd.DataFrame:
    comp = (
        df_st.groupby(["parking_id", "year"], as_index=False)
        .agg(
            n_days=("date_only", "nunique"),
            actual_obs=("rounded_hour", "size"),
        )
        .sort_values(["parking_id", "year"])
        .reset_index(drop=True)
    )
    comp["expected_obs"] = comp["n_days"] * 24
    comp["missing_obs"] = comp["expected_obs"] - comp["actual_obs"]
    comp["completeness"] = (comp["actual_obs"] / comp["expected_obs"]).round(4)
    return comp[
        ["parking_id", "year", "n_days", "expected_obs", "actual_obs", "missing_obs", "completeness"]
    ]


def deduplicate_shortterm(df_st: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    n_exact_dupes = int(df_st.duplicated().sum())
    n_func_dupes = int(df_st.duplicated(subset=["parking_id", "rounded_hour"]).sum())

    out = df_st
    if n_exact_dupes > 0:
        out = out.drop_duplicates()

    if n_func_dupes > 0:
        out = (
            out.sort_values("publication_time", ascending=False)
            .drop_duplicates(subset=["parking_id", "rounded_hour"])
            .sort_values(["parking_id", "rounded_hour"])
            .reset_index(drop=True)
        )

    return out, n_exact_dupes, n_func_dupes


def apply_shortterm_quality_flags(
    df_st: pd.DataFrame, discrepancy_threshold: float = DISCREPANCY_THRESHOLD
) -> tuple[pd.DataFrame, int, int, int]:
    out = df_st.copy()
    out["occ_rate_calculated"] = (
        out["number_of_occupied_spaces"] / out["number_of_spaces_override"]
    ).replace([np.inf, -np.inf], np.nan)
    out["occ_rate_discrepancy"] = (out["occupancy_rate"] - out["occ_rate_calculated"]).abs()

    n_inconsistent = int((out["occ_rate_discrepancy"] > discrepancy_threshold).sum())
    out["flag_occ_inconsistent"] = (out["occ_rate_discrepancy"] > discrepancy_threshold).astype(
        int
    )

    n_overcapacity = int(
        (out["number_of_occupied_spaces"] > out["number_of_spaces_override"]).sum()
    )
    out["flag_overcapacity"] = (
        out["number_of_occupied_spaces"] > out["number_of_spaces_override"]
    ).astype(int)

    n_negative = int((out["number_of_occupied_spaces"] < 0).sum())
    out = out.drop(columns=["occ_rate_calculated", "occ_rate_discrepancy"])

    return out, n_inconsistent, n_overcapacity, n_negative


def add_frozen_sensor_flag(
    df: pd.DataFrame, freeze_threshold: int = FREEZE_THRESHOLD
) -> tuple[pd.DataFrame, int]:
    out = df.sort_values(["parking_id", "rounded_hour"]).reset_index(drop=True).copy()
    out["prev_occupied"] = out.groupby("parking_id")["number_of_occupied_spaces"].shift(1)
    out["is_same_as_prev"] = (out["number_of_occupied_spaces"] == out["prev_occupied"]).astype(
        int
    )
    streak_group = (
        out["is_same_as_prev"]
        != out.groupby("parking_id")["is_same_as_prev"].shift(1, fill_value=0)
    ).cumsum()
    out["freeze_streak"] = out.groupby(["parking_id", streak_group])["is_same_as_prev"].cumsum()
    out["flag_frozen_sensor"] = (out["freeze_streak"] >= freeze_threshold).astype(int)
    n_frozen = int(out["flag_frozen_sensor"].sum())
    out = out.drop(columns=["prev_occupied", "is_same_as_prev", "freeze_streak"])
    return out, n_frozen


def check_dst_hour_anomalies(
    df_st: pd.DataFrame, dst_transitions: list[tuple[str, str]] | None = None
) -> tuple[pd.DataFrame, int]:
    transitions = dst_transitions or DST_TRANSITIONS_2019_2026
    dst_dates = [pd.Timestamp(d[0]).date() for d in transitions]
    hours_per_day = (
        df_st.groupby(["parking_id", "date_only"])["hour"]
        .nunique()
        .reset_index(name="n_unique_hours")
    )
    dst_check = hours_per_day[hours_per_day["date_only"].isin(dst_dates)].copy()
    n_dst_anom = int((dst_check["n_unique_hours"] != 24).sum()) if not dst_check.empty else 0
    return dst_check, n_dst_anom


def process_longterm_quality(
    df_lt: pd.DataFrame,
    freeze_threshold: int = FREEZE_THRESHOLD,
    discrepancy_threshold: float = DISCREPANCY_THRESHOLD,
) -> tuple[pd.DataFrame, dict[str, int]]:
    out = df_lt.copy()
    n_null_occ = int(out["occupancy_rate"].isnull().sum())
    out["occupancy_rate"] = out["occupancy_rate"].fillna(
        out["number_of_occupied_spaces"] / out["number_of_spaces_override"]
    )

    out["occ_calc"] = out["number_of_occupied_spaces"] / out["number_of_spaces_override"]
    n_incons_lt = int(((out["occupancy_rate"] - out["occ_calc"]).abs() > discrepancy_threshold).sum())
    out["flag_occ_inconsistent"] = (
        (out["occupancy_rate"] - out["occ_calc"]).abs() > discrepancy_threshold
    ).astype(int)
    out = out.drop(columns=["occ_calc"])

    out, n_frozen_lt = add_frozen_sensor_flag(out, freeze_threshold=freeze_threshold)

    n_dupes_lt = int(out.duplicated(subset=["parking_id", "rounded_hour"]).sum())
    if n_dupes_lt > 0:
        out = (
            out.sort_values("publication_time", ascending=False)
            .drop_duplicates(subset=["parking_id", "rounded_hour"])
            .sort_values(["parking_id", "rounded_hour"])
            .reset_index(drop=True)
        )

    stats = {
        "n_null_occ": n_null_occ,
        "n_incons_lt": n_incons_lt,
        "n_frozen_lt": n_frozen_lt,
        "n_dupes_lt": n_dupes_lt,
    }
    return out, stats


def crosscheck_override_capacity(
    df_st: pd.DataFrame, df_loc: pd.DataFrame
) -> tuple[pd.DataFrame, int]:
    max_override_st = (
        df_st.groupby("parking_id")["number_of_spaces_override"]
        .max()
        .reset_index(name="max_override")
    )
    cap_check = max_override_st.merge(
        df_loc[["parking_id", "total_capacity"]], on="parking_id", how="left"
    )
    cap_check["override_exceeds_capacity"] = (
        cap_check["max_override"] > cap_check["total_capacity"]
    )
    n_exceeds = int(cap_check["override_exceeds_capacity"].sum())
    return cap_check, n_exceeds


def recompute_occupancy_for_inconsistent(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    out = df.copy()
    mask = out["flag_occ_inconsistent"] == 1
    n_fixed = int(mask.sum())
    if n_fixed > 0:
        out.loc[mask, "occupancy_rate"] = (
            out.loc[mask, "number_of_occupied_spaces"]
            / out.loc[mask, "number_of_spaces_override"]
        )
    return out, n_fixed

