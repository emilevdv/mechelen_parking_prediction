# ── eda_config.py ─────────────────────────────────────────────────────────────
"""Backward-compatible config shim for notebooks.

Prefer importing from `mechelen_parking` in new notebooks/scripts.
"""

from mechelen_parking.config import EDAStyle, get_default_paths
from mechelen_parking.data_prep import get_train_mask

# Paths
PATHS = get_default_paths()
ROOT = PATHS.root
DATA_PROC = PATHS.data_processed
FIGS = PATHS.figures / "eda"

# Visual style constants
STYLE = EDAStyle()
TIER_ORDER = list(STYLE.tier_order)
TIER_COLORS = STYLE.tier_colors
PARKING_COLORS = STYLE.parking_colors
FIGSIZE_WIDE = STYLE.figsize_wide
FIGSIZE_SQUARE = STYLE.figsize_square
FIGSIZE_GRID = STYLE.figsize_grid
ALPHA = STYLE.alpha
FONTSIZE = STYLE.fontsize
