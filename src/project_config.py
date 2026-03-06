from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_PROJECT_START = "2019-01-01"
DEFAULT_PROJECT_END = "2026-12-31"
DEFAULT_EVENTS_END = DEFAULT_PROJECT_END


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    data_raw: Path
    data_intermediate: Path
    data_processed: Path
    data_models: Path
    data_results: Path
    figures: Path
    notebooks: Path
    configs: Path


def find_project_root(start: Path | None = None) -> Path:
    """Resolve repository root by walking upward from a starting directory."""
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    sentinels = ("data_raw", "notebooks")

    for candidate in (current, *current.parents):
        if all((candidate / sentinel).exists() for sentinel in sentinels):
            return candidate

    raise FileNotFoundError(
        f"Unable to locate project root from '{current}'. "
        "Expected a parent directory containing 'data_raw/' and 'notebooks/'."
    )


def get_project_paths(project_root: Path | None = None) -> ProjectPaths:
    root = find_project_root(project_root)
    return ProjectPaths(
        root=root,
        data_raw=root / "data_raw",
        data_intermediate=root / "data_intermediate",
        data_processed=root / "data_processed",
        data_models=root / "data_models",
        data_results=root / "data_results",
        figures=root / "figures",
        notebooks=root / "notebooks",
        configs=root / "configs",
    )
