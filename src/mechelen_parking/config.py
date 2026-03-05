from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ProjectPaths:
    """Centralized project paths with env-var overrides.

    Environment variables:
    - MECH_PARKING_PROJECT_ROOT: repository root (defaults to current working directory)
    - MECH_PARKING_DATA_PROCESSED: processed dataset folder
    - MECH_PARKING_FIGURES: base figures folder
    """

    root: Path
    data_processed: Path
    figures: Path

    @classmethod
    def from_env(cls) -> "ProjectPaths":
        root = Path(os.getenv("MECH_PARKING_PROJECT_ROOT", Path.cwd())).resolve()
        data_processed = Path(
            os.getenv("MECH_PARKING_DATA_PROCESSED", root / "data_processed")
        ).resolve()
        figures = Path(os.getenv("MECH_PARKING_FIGURES", root / "figures")).resolve()
        return cls(root=root, data_processed=data_processed, figures=figures)

    def ensure_eda_dirs(self, notebooks: Iterable[str] = ("nb05", "nb06", "nb07")) -> None:
        for nb in notebooks:
            (self.figures / "eda" / nb).mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class EDAStyle:
    tier_order: tuple[str, ...] = ("centrum", "vesten", "rand")
    tier_colors: dict[str, str] = None
    parking_colors: dict[str, str] = None
    figsize_wide: tuple[int, int] = (14, 5)
    figsize_square: tuple[int, int] = (8, 8)
    figsize_grid: tuple[int, int] = (16, 10)
    alpha: float = 0.75
    fontsize: int = 11

    def __post_init__(self) -> None:
        if self.tier_colors is None:
            object.__setattr__(
                self,
                "tier_colors",
                {"centrum": "#2563EB", "vesten": "#16A34A", "rand": "#DC2626"},
            )
        if self.parking_colors is None:
            object.__setattr__(
                self,
                "parking_colors",
                {
                    "P1": "#1E3A5F",
                    "P2": "#2563EB",
                    "P3": "#60A5FA",
                    "P4": "#14532D",
                    "P5": "#16A34A",
                    "P6": "#86EFAC",
                    "P7": "#7F1D1D",
                    "P8": "#DC2626",
                    "P9": "#FCA5A5",
                    "P10": "#78716C",
                },
            )


def get_default_paths() -> ProjectPaths:
    paths = ProjectPaths.from_env()
    paths.ensure_eda_dirs()
    return paths
