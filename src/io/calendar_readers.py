from __future__ import annotations

from pathlib import Path

import pandas as pd


_HOLIDAY_REQUIRED_COLUMNS = {"Feestdag", "Datum"}
_VACATION_REQUIRED_COLUMNS = {"Vakantie", "Type", "Startdatum", "Einddatum"}


def _validate_columns(df: pd.DataFrame, required: set[str], file_hint: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns in '{file_hint}': {missing}. "
            f"Found columns: {list(df.columns)}"
        )


def list_holiday_files(data_raw_dir: Path) -> tuple[list[Path], list[Path]]:
    """Return sorted lists of national and other holiday CSV files."""
    national_files = sorted(data_raw_dir.glob("*national_fd.csv"))
    other_files = sorted(data_raw_dir.glob("*other_fd.csv"))

    if not national_files:
        raise FileNotFoundError(
            f"No files matched '*national_fd.csv' in '{data_raw_dir}'."
        )
    if not other_files:
        raise FileNotFoundError(f"No files matched '*other_fd.csv' in '{data_raw_dir}'.")

    return national_files, other_files


def read_holiday_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    _validate_columns(df, _HOLIDAY_REQUIRED_COLUMNS, str(path))
    return df


def read_school_vacations_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    _validate_columns(df, _VACATION_REQUIRED_COLUMNS, str(path))
    return df

