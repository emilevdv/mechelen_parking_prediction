from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.io.calendar_readers import read_holiday_csv


def load_holiday_files(files: list[Path], holiday_type: str) -> pd.DataFrame:
    """Load holiday CSV files and normalize to a daily holiday table."""
    if holiday_type not in {"national", "other"}:
        raise ValueError("holiday_type must be either 'national' or 'other'.")
    if not files:
        raise ValueError("Expected at least one holiday file.")

    frames: list[pd.DataFrame] = []
    for path in files:
        df = read_holiday_csv(path).rename(
            columns={"Feestdag": "holiday_name", "Datum": "date"}
        )
        df["date"] = pd.to_datetime(df["date"], format="%d %b %Y", errors="raise")
        df["holiday_type"] = holiday_type
        df["year"] = df["date"].dt.year.astype("int64")
        frames.append(df[["holiday_name", "date", "holiday_type", "year"]])

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.drop_duplicates(subset=["date", "holiday_type"])
    merged = merged.sort_values("date").reset_index(drop=True)
    return merged


def prepare_school_vacations(df_vac_raw: pd.DataFrame) -> pd.DataFrame:
    """Expand vacation periods to daily rows."""
    required = {"Vakantie", "Type", "Startdatum", "Einddatum"}
    missing = sorted(required - set(df_vac_raw.columns))
    if missing:
        raise ValueError(
            f"Missing required vacation columns: {missing}. "
            f"Found columns: {list(df_vac_raw.columns)}"
        )

    df = df_vac_raw.rename(
        columns={
            "Vakantie": "vacation_name",
            "Type": "vacation_type",
            "Startdatum": "start_date",
            "Einddatum": "end_date",
        }
    ).copy()
    df["start_date"] = pd.to_datetime(df["start_date"], errors="raise")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="raise")

    expanded_frames: list[pd.DataFrame] = []
    for row in df.itertuples(index=False):
        if row.end_date < row.start_date:
            raise ValueError(
                f"Vacation '{row.vacation_name}' has end_date before start_date."
            )
        days = pd.date_range(start=row.start_date, end=row.end_date, freq="D")
        expanded_frames.append(
            pd.DataFrame(
                {
                    "date": days,
                    "vacation_name": row.vacation_name,
                    "vacation_type": row.vacation_type,
                }
            )
        )

    if not expanded_frames:
        return pd.DataFrame(columns=["date", "vacation_name", "vacation_type"])

    daily = pd.concat(expanded_frames, ignore_index=True)
    daily = daily.drop_duplicates(subset=["date", "vacation_name", "vacation_type"])
    daily = daily.sort_values("date").reset_index(drop=True)
    return daily


def build_calendar_master(
    df_holidays: pd.DataFrame,
    df_vac_daily: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Build a daily master calendar table with holiday and vacation flags."""
    base = pd.DataFrame(
        {"date": pd.date_range(start=pd.Timestamp(start_date), end=pd.Timestamp(end_date))}
    )

    holidays = df_holidays.copy()
    holidays["date"] = pd.to_datetime(holidays["date"], errors="raise")

    nat = (
        holidays.loc[holidays["holiday_type"] == "national", ["date", "holiday_name"]]
        .drop_duplicates(subset=["date"])
        .rename(columns={"holiday_name": "national_holiday_name"})
    )
    oth = (
        holidays.loc[holidays["holiday_type"] == "other", ["date", "holiday_name"]]
        .drop_duplicates(subset=["date"])
        .rename(columns={"holiday_name": "other_holiday_name"})
    )

    vac = df_vac_daily[["date", "vacation_name", "vacation_type"]].copy()
    vac["date"] = pd.to_datetime(vac["date"], errors="raise")
    vac = vac.drop_duplicates(subset=["date"])

    df = base.merge(nat, on="date", how="left")
    df = df.merge(oth, on="date", how="left")
    df = df.merge(vac, on="date", how="left")

    df["is_national_holiday"] = df["national_holiday_name"].notna().astype("int8")
    df["is_other_holiday"] = df["other_holiday_name"].notna().astype("int8")
    df["is_any_holiday"] = (
        (df["is_national_holiday"] == 1) | (df["is_other_holiday"] == 1)
    ).astype("int8")
    df["is_school_vacation"] = df["vacation_name"].notna().astype("int8")
    df["weekday"] = df["date"].dt.weekday.astype("int8")
    df["is_weekend"] = (df["weekday"] >= 5).astype("int8")
    df["year"] = df["date"].dt.year.astype("int16")
    df["month"] = df["date"].dt.month.astype("int8")

    conditions = [
        df["is_national_holiday"] == 1,
        df["is_other_holiday"] == 1,
        df["is_school_vacation"] == 1,
        df["is_weekend"] == 1,
    ]
    labels = ["national_holiday", "other_holiday", "school_vacation", "weekend"]
    df["calendar_day_class"] = np.select(conditions, labels, default="regular_day")

    ordered_cols = [
        "date",
        "national_holiday_name",
        "other_holiday_name",
        "vacation_name",
        "vacation_type",
        "is_national_holiday",
        "is_other_holiday",
        "is_any_holiday",
        "is_school_vacation",
        "calendar_day_class",
        "year",
        "month",
        "weekday",
        "is_weekend",
    ]
    return df[ordered_cols].sort_values("date").reset_index(drop=True)

