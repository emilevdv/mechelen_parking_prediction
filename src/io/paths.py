from __future__ import annotations

from pathlib import Path

from src.project_config import get_project_paths


_DATA_ALIAS_PREFIX = "@data/"
_ALIAS_TO_DIRNAME = {
    "raw": "data_raw",
    "intermediate": "data_intermediate",
    "processed": "data_processed",
    "models": "data_models",
    "results": "data_results",
}


def resolve_data_path(alias: str, project_root: Path | None = None) -> Path:
    """
    Resolve an @data alias to an absolute path in the project tree.

    Examples:
    - @data/raw/2020national_fd.csv
    - @data/intermediate/calendar_master.parquet
    """
    if not alias.startswith(_DATA_ALIAS_PREFIX):
        raise ValueError(
            f"Invalid alias '{alias}'. Expected format '@data/<bucket>/...'."
        )

    relative = alias[len(_DATA_ALIAS_PREFIX) :]
    bucket, sep, tail = relative.partition("/")
    if not bucket or not sep:
        raise ValueError(
            f"Invalid alias '{alias}'. Expected format '@data/<bucket>/...'."
        )

    mapped_dirname = _ALIAS_TO_DIRNAME.get(bucket)
    if mapped_dirname is None:
        valid_buckets = ", ".join(sorted(_ALIAS_TO_DIRNAME))
        raise ValueError(
            f"Unknown @data bucket '{bucket}'. Expected one of: {valid_buckets}."
        )

    root = get_project_paths(project_root).root
    return (root / mapped_dirname / tail).resolve()

