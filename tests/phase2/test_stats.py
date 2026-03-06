import numpy as np
import pandas as pd

from src.phase2.stats import bootstrap_ci, fisher_z, fisher_z_test


def test_bootstrap_ci_returns_ordered_interval():
    s = pd.Series(np.linspace(0.1, 0.9, 50))
    lo, hi = bootstrap_ci(s, n_boot=200, random_state=42)
    assert np.isfinite(lo)
    assert np.isfinite(hi)
    assert lo <= hi


def test_fisher_z_clips_extremes():
    z_hi = fisher_z(1.0)
    z_lo = fisher_z(-1.0)
    assert np.isfinite(z_hi)
    assert np.isfinite(z_lo)
    assert z_hi > 0
    assert z_lo < 0


def test_fisher_z_test_returns_valid_p():
    z, p = fisher_z_test(0.6, 0.2, 100, 100)
    assert np.isfinite(z)
    assert 0 <= p <= 1
