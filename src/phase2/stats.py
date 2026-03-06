from __future__ import annotations

import numpy as np
from scipy import stats


def bootstrap_ci(series, n_boot: int = 1000, ci: float = 0.95, random_state: int = 42):
    values = np.asarray(series.dropna() if hasattr(series, "dropna") else series)
    values = values[np.isfinite(values)]
    if len(values) < 5:
        return np.nan, np.nan

    rng = np.random.default_rng(random_state)
    boot_idx = rng.integers(0, len(values), size=(n_boot, len(values)))
    means = values[boot_idx].mean(axis=1)
    lo = np.percentile(means, (1 - ci) / 2 * 100)
    hi = np.percentile(means, (1 + ci) / 2 * 100)
    return float(lo), float(hi)


def fisher_z(r: float) -> float:
    clipped = float(np.clip(r, -0.9999, 0.9999))
    return float(0.5 * np.log((1 + clipped) / (1 - clipped)))


def fisher_z_test(r1: float, r2: float, n1: int, n2: int) -> tuple[float, float]:
    if n1 <= 3 or n2 <= 3:
        raise ValueError("n1 and n2 must be > 3 for Fisher z-test.")
    z1 = np.arctanh(np.clip(r1, -0.9999, 0.9999))
    z2 = np.arctanh(np.clip(r2, -0.9999, 0.9999))
    se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
    z = (z1 - z2) / se
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return float(z), float(p)


def status_icon(confirmed):
    if confirmed is True:
        return "✅ BEVESTIGD"
    if confirmed is False:
        return "❌ VERWORPEN"
    return "⚠ GEDEELTELIJK"


def status(condition):
    if condition is True:
        return "✅ BEVESTIGD"
    if condition is False:
        return "❌ VERWORPEN"
    return "⚠  GEDEELTELIJK / ONZEKER"


def fmt_float(val, decimals: int = 3, prefix: str = "") -> str:
    try:
        if val is None or np.isnan(float(val)):
            return "N/A"
        fmt = f"+.{decimals}f" if prefix == "+" else f".{decimals}f"
        return format(float(val), fmt)
    except (TypeError, ValueError):
        return "N/A"


def fmt_p(val) -> str:
    try:
        if val is None or np.isnan(float(val)):
            return "N/A"
        return format(float(val), ".4f")
    except (TypeError, ValueError):
        return "N/A"
