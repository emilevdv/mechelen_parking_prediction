# Mechelen Parking Prediction

Notebook-first project for parking occupancy/prediction analysis in Mechelen.

## Repository structure

- `notebooks/`: full analytical flow from data integration to baseline models.
- `src/mechelen_parking/`: shared reusable utilities (config + data-prep).
- `src/eda_config.py`: backward-compatible shim used by existing notebooks.
- `figures/`: generated charts/tables from EDA notebooks.
- `data_models/`: serialized baseline model artifacts.
- `docs/RUNBOOK.md`: reproducible setup + execution guide.

## Why this refactor

The project originally relied mostly on notebook-local logic and machine-specific paths.
This repository now includes:

1. **Parameterized paths/config** via environment variables.
2. **Shared modules** for repeated notebook logic (train mask, column normalization).
3. **A reproducible runbook** for setup, execution order, and rollback strategy.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python scripts/notebook_bootstrap.py
```

Then follow `docs/RUNBOOK.md`.

## Git helper scripts

- `update_auto_push_github.sh`: interactive add/commit/push.
- `push_to_github.sh`: force-pushes local state to remote main (**use carefully**).
