from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.io.paths import resolve_data_path


CONFIDENCE_RANK = {"verified": 0, "estimated": 1, "covid_modified": 2}


def date_range_list(start_date: str, end_date: str) -> list[str]:
    dates = pd.date_range(pd.Timestamp(start_date), pd.Timestamp(end_date), freq="D")
    return [d.strftime("%Y-%m-%d") for d in dates]


def make_event_records(
    dates: list[str],
    event_name: str,
    event_type: str,
    event_scale: int,
    expected_attendance: float | int,
    data_confidence: str,
    is_multiday_event: int,
    football_kickoff_hour: float | None = None,
) -> pd.DataFrame:
    kickoff = np.nan if football_kickoff_hour is None else float(football_kickoff_hour)
    rows = []
    for d in dates:
        rows.append(
            {
                "date": pd.Timestamp(d).normalize(),
                "event_name": event_name,
                "event_type": event_type,
                "event_scale": int(event_scale),
                "expected_attendance": float(expected_attendance),
                "football_kickoff_hour": kickoff,
                "data_confidence": data_confidence,
                "is_multiday_event": int(is_multiday_event),
            }
        )
    return pd.DataFrame(rows)


def extract_kvm_home_matches_wikipedia(season_start_year: int) -> pd.DataFrame:
    url = (
        f"https://en.wikipedia.org/wiki/"
        f"{season_start_year}%E2%80%93{str(season_start_year + 1)[-2:]}"
        f"_K.V._Mechelen_season"
    )

    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return pd.DataFrame()

        soup = BeautifulSoup(resp.text, "html.parser")
        date_pattern = re.compile(
            r"(\d{1,2}\s+(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)\s+\d{4})"
        )
        score_pattern = re.compile(r"\d+\s*[–-]\s*\d+")

        records: list[dict[str, object]] = []
        for row in soup.find_all("tr"):
            cells = row.find_all(["td", "th"])
            row_text = " ".join(c.get_text(strip=True) for c in cells)
            date_match = date_pattern.search(row_text)
            if not date_match:
                continue
            score_match = score_pattern.search(row_text)
            if not score_match:
                continue
            mech_pos = row_text.find("Mechelen")
            if mech_pos < 0:
                continue
            is_home = mech_pos < score_match.start()
            if not is_home:
                continue

            try:
                match_date = pd.to_datetime(date_match.group(1), format="%d %B %Y")
            except Exception:
                continue

            time_match = re.search(r"(\d{2}):(\d{2})", row_text)
            if time_match:
                kickoff = int(time_match.group(1)) + int(time_match.group(2)) / 60
            else:
                kickoff = 18.0 if match_date.dayofweek in [5, 6] else 20.75

            records.append(
                {
                    "date": match_date.normalize(),
                    "event_name": "KVM thuiswedstrijd",
                    "event_type": "football",
                    "event_scale": 2,
                    "expected_attendance": 11000.0,
                    "football_kickoff_hour": kickoff,
                    "data_confidence": "verified",
                    "is_multiday_event": 0,
                }
            )

        return pd.DataFrame(records).drop_duplicates(subset=["date"])
    except Exception:
        return pd.DataFrame()


def _worst_confidence(series: pd.Series) -> str:
    ranked = series.map(CONFIDENCE_RANK)
    worst = ranked.max()
    reverse_rank = {v: k for k, v in CONFIDENCE_RANK.items()}
    return reverse_rank[int(worst)]


def aggregate_events_daily(
    df_events_raw: pd.DataFrame, event_types: dict[str, str]
) -> pd.DataFrame:
    events_agg = (
        df_events_raw.groupby("date")
        .agg(
            event_scale_max=("event_scale", "max"),
            n_concurrent_events=("event_type", "nunique"),
            football_kickoff_hour=(
                "football_kickoff_hour",
                lambda x: x.dropna().iloc[0] if x.notna().any() else np.nan,
            ),
            data_confidence=("data_confidence", _worst_confidence),
            event_names_combined=("event_name", lambda x: " | ".join(sorted(x.unique()))),
        )
        .reset_index()
    )

    for flag_col, event_type in event_types.items():
        type_dates = set(df_events_raw.loc[df_events_raw["event_type"] == event_type, "date"])
        events_agg[flag_col] = events_agg["date"].isin(type_dates).astype("int8")

    events_agg["is_event_day"] = 1
    return events_agg


def build_events_master(
    events_agg: pd.DataFrame,
    event_flag_columns: list[str],
    project_start: str,
    project_end: str,
) -> pd.DataFrame:
    all_days = pd.DataFrame(
        {"date": pd.date_range(pd.Timestamp(project_start), pd.Timestamp(project_end), freq="D")}
    )
    out = all_days.merge(events_agg, on="date", how="left")
    out["event_scale_max"] = out["event_scale_max"].fillna(0).astype("int8")
    out["n_concurrent_events"] = out["n_concurrent_events"].fillna(0).astype("int8")
    out["is_event_day"] = out["is_event_day"].fillna(0).astype("int8")
    out["data_confidence"] = out["data_confidence"].fillna("verified")
    out["event_names_combined"] = out["event_names_combined"].fillna("")

    for col in event_flag_columns:
        out[col] = out[col].fillna(0).astype("int8")
    return out


def merge_events_into_mad(
    mad_df: pd.DataFrame, events_master: pd.DataFrame, date_col: str = "date_only"
) -> pd.DataFrame:
    events = events_master.rename(columns={"date": date_col}).copy()
    out = mad_df.copy()
    out[date_col] = pd.to_datetime(out[date_col]).dt.normalize()
    out = out.merge(events, on=date_col, how="left", validate="many_to_one")

    # Fill all day-level event flags present in events_master, including future additions
    # such as is_sport_day / is_markt_day, to keep MAD merge forward-compatible.
    dynamic_day_flags = [c for c in out.columns if c.startswith("is_") and c.endswith("_day")]
    for col in dynamic_day_flags:
        out[col] = out[col].fillna(0).astype("int8")

    for col in ["event_scale_max", "n_concurrent_events"]:
        if col in out.columns:
            out[col] = out[col].fillna(0).astype("int8")
    if "data_confidence" in out.columns:
        out["data_confidence"] = out["data_confidence"].fillna("verified")
    if "event_names_combined" in out.columns:
        out["event_names_combined"] = out["event_names_combined"].fillna("")
    return out


def export_events_master(events_master: pd.DataFrame, project_root: Path | None = None) -> Path:
    out_path = resolve_data_path("@data/intermediate/events_master.parquet", project_root)
    events_master.to_parquet(out_path, index=False)
    return out_path
