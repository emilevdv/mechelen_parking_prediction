from __future__ import annotations

import numpy as np
import pandas as pd


def compute_daily_cv(df: pd.DataFrame, label: str) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["rounded_hour"]).dt.date
    cv = (
        out.groupby(["parking_id", "date"])["occupancy_rate"]
        .agg(lambda x: x.std() / x.mean() if x.mean() > 0.01 else np.nan)
        .dropna()
        .reset_index()
        .rename(columns={"occupancy_rate": f"cv_{label}"})
    )
    return cv


def section(title: str, sep: str = "═" * 78) -> None:
    print(f"\n{sep}\n  {title}\n{sep}")


def sub(title: str, sep: str = "─" * 78) -> None:
    print(f"\n  {sep}\n  {title}\n  {sep}")
