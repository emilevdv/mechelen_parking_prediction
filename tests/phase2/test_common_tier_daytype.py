import pandas as pd

from src.phase2.common import add_day_type_3, add_tier_column


def test_add_tier_column_merges_rand_and_vesten():
    df = pd.DataFrame({"parking_location_category": ["centrum", "vesten", "rand", "foo"]})
    out = add_tier_column(df)
    assert out["tier"].tolist() == ["centrum", "vesten_of_rand", "vesten_of_rand", "foo"]


def test_add_day_type_3_weekday_saturday_sunday_holiday():
    df = pd.DataFrame(
        {
            "weekday_int": [0, 5, 6, 2],
            "is_national_holiday": [0, 0, 0, 1],
        }
    )
    out = add_day_type_3(df)
    assert out["day_type_3"].tolist() == ["weekday", "saturday", "sunday_holiday", "sunday_holiday"]
