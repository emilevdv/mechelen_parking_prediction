# Reproducible Runbook

This runbook makes the notebook workflow easier to repeat in VSCode/Jupyter.

## 1) Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Configure paths (optional but recommended)

Default behavior uses your current working directory as project root.

```bash
export MECH_PARKING_PROJECT_ROOT="$(pwd)"
export MECH_PARKING_DATA_PROCESSED="$(pwd)/data_processed"
export MECH_PARKING_FIGURES="$(pwd)/figures"
```

## 3) Verify shared config

```bash
PYTHONPATH=src python scripts/notebook_bootstrap.py
```

## 4) Notebook execution order

Run notebooks in this order for reproducible outputs:

1. `01_calendar_integration.ipynb`
2. `02_data_quality_check.ipynb`
3. `03_weather_cleaning.ipynb`
4. `04_mad_assembly.ipynb`
5. `04b_event_assembly.ipynb`
6. `05_eda_temporal.ipynb`
7. `06_eda_spatio.ipynb`
8. `07_eda_external_factors.ipynb`
9. `07b_eda_LT.ipynb`
10. `07c_train_test_split.ipynb`
11. `08_ft_ngr.ipynb`
12. `09_baseline_models.ipynb`

## 5) VSCode workflow (safe + reversible)

- Work in a feature branch per cleanup step:
  - `git switch -c chore/notebook-cleanup-step1`
- Commit after each notebook or module change:
  - `git add -p`
  - `git commit -m "refactor: extract common notebook utility"`
- If a change is bad, undo quickly:
  - discard file: `git restore path/to/file`
  - undo commit keep changes: `git reset --soft HEAD~1`
  - hard rollback: `git reset --hard <commit>`

## 6) Recommended notebook import pattern

At the top of each notebook, use:

```python
from mechelen_parking import get_default_paths, get_train_mask, standardize_columns

PATHS = get_default_paths()
```

This removes path duplication and keeps the training filter consistent across notebooks.
