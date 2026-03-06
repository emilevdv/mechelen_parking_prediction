from __future__ import annotations

import numpy as np
import pandas as pd

from src.phase2.constants import PARKING_TIER_MAP, TIER_COLORS
from src.phase2.stats import fisher_z, status


def build_parking_color_map(parking_order: list[str]) -> dict[str, str]:
    return {
        parking_id: (
            TIER_COLORS["centrum"]
            if PARKING_TIER_MAP.get(parking_id) == "centrum"
            else TIER_COLORS["vesten_of_rand"]
        )
        for parking_id in parking_order
    }


def split_intra_inter_correlations(
    corr_matrix: pd.DataFrame,
    parking_tier_map: dict[str, str] | None = None,
) -> tuple[list[float], list[float]]:
    tier_map = parking_tier_map or PARKING_TIER_MAP
    columns = list(corr_matrix.columns)

    intra_r: list[float] = []
    inter_r: list[float] = []

    for i, p1 in enumerate(columns):
        for j, p2 in enumerate(columns):
            if j <= i:
                continue
            r_val = float(corr_matrix.loc[p1, p2])
            if tier_map.get(p1) == tier_map.get(p2):
                intra_r.append(r_val)
            else:
                inter_r.append(r_val)

    return intra_r, inter_r


def fisher_z_lists(values: list[float]) -> list[float]:
    return [fisher_z(v) for v in values]


__all__ = [
    "build_parking_color_map",
    "split_intra_inter_correlations",
    "fisher_z",
    "fisher_z_lists",
    "status",
]
