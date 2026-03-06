import pandas as pd

from src.phase2.common import apply_train_filter, build_train_mask


def test_build_train_mask_default_rules():
    df = pd.DataFrame(
        {
            "year": [2019, 2020, 2023, 2024, 2025],
            "low_data_coverage": [0, 0, 1, 0, 0],
            "system_blackout": [0, 0, 0, 1, 0],
            "partial_year": [0, 0, 0, 0, 0],
        }
    )

    mask = build_train_mask(df)
    assert mask.tolist() == [False, True, False, False, False]


def test_apply_train_filter_custom_years_without_quality_flags():
    df = pd.DataFrame(
        {
            "year": [2020, 2021, 2022],
            "low_data_coverage": [1, 1, 1],
            "system_blackout": [1, 1, 1],
            "partial_year": [1, 1, 1],
            "value": [10, 20, 30],
        }
    )

    out = apply_train_filter(
        df,
        min_year=2021,
        excluded_years=(2022,),
        require_quality_flags=False,
    )
    assert out["year"].tolist() == [2021]
    assert out["value"].tolist() == [20]
