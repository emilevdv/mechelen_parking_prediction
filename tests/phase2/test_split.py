import pandas as pd

from src.phase2.split import apply_quality_filter, overlap_count, split_train_holdout


def _base_df():
    return pd.DataFrame(
        {
            "parking_id": ["A", "A", "A", "B"],
            "rounded_hour": pd.to_datetime(
                ["2020-01-01 00:00", "2023-01-01 00:00", "2025-01-01 00:00", "2025-01-01 01:00"]
            ),
            "year": [2020, 2023, 2025, 2025],
            "low_data_coverage": [0, 0, 0, 1],
            "system_blackout": [0, 0, 0, 0],
            "partial_year": [0, 0, 0, 0],
        }
    )


def test_quality_filter_removes_flagged_rows():
    out = apply_quality_filter(_base_df())
    assert len(out) == 3
    assert out["parking_id"].tolist() == ["A", "A", "A"]


def test_split_train_holdout_expected_years_and_zero_overlap():
    clean = apply_quality_filter(_base_df())
    train, holdout = split_train_holdout(clean)

    assert sorted(train["year"].unique().tolist()) == [2020, 2023]
    assert sorted(holdout["year"].unique().tolist()) == [2025]
    assert overlap_count(train, holdout) == 0
