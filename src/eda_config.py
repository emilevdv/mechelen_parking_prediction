# ── eda_config.py ─────────────────────────────────────────────────────────────
from pathlib import Path
import pandas as pd

# Paden
ROOT      = Path("/Users/emilevandevoorde/Documents/mechelen_parking")
DATA_PROC = ROOT / "data_processed"
FIGS      = ROOT / "figures" / "eda"
for nb in ["nb05", "nb06", "nb07"]:
    (FIGS / nb).mkdir(parents=True, exist_ok=True)

# Trainingsfilter — ALTIJD dezelfde mask, nooit afwijken
def get_train_mask(df):
    return (
        (df["low_data_coverage"]  == 0) &
        (df["system_blackout"]    == 0) &
        (df["partial_year"]       == 0) &
        (df["year"]               >= 2020) &
        (df["year"]               != 2025)
    )

# Tier-indeling
TIER_ORDER  = ["centrum", "vesten", "rand"]
TIER_COLORS = {"centrum": "#2563EB", "vesten": "#16A34A", "rand": "#DC2626"}

# Parking-kleuren (10 parkings)
PARKING_COLORS = {
    "P1":  "#1E3A5F", "P2":  "#2563EB", "P3":  "#60A5FA",  # centrum
    "P4":  "#14532D", "P5":  "#16A34A", "P6":  "#86EFAC",  # vesten
    "P7":  "#7F1D1D", "P8":  "#DC2626", "P9":  "#FCA5A5",  # rand
    "P10": "#78716C",
}

# Plotstijl
FIGSIZE_WIDE   = (14, 5)
FIGSIZE_SQUARE = (8, 8)
FIGSIZE_GRID   = (16, 10)
ALPHA          = 0.75
FONTSIZE       = 11