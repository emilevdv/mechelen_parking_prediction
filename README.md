# Mechelen Parking

Notebook-based data and model pipeline for the thesis:
**"Spatiotemporal Prediction and Optimization of Car Parking in Mechelen"**.

## Inhoud
- [Mechelen Parking](#mechelen-parking)
  - [Inhoud](#inhoud)
  - [1. Doel en scope](#1-doel-en-scope)
  - [2. Snelle start](#2-snelle-start)
  - [3. Repository structuur (actueel)](#3-repository-structuur-actueel)
  - [4. Pipeline volgorde (actueel)](#4-pipeline-volgorde-actueel)
    - [Phase 1 - Data Prep](#phase-1---data-prep)
    - [Phase 2 - EDA](#phase-2---eda)
    - [Phase 3 - Feature Engineering](#phase-3---feature-engineering)
  - [Phase 4 - Modelling](#phase-4---modelling)
  - [5. Figures output structuur](#5-figures-output-structuur)
  - [6. Src modules](#6-src-modules)
  - [7. Dataflow en kerncontracten](#7-dataflow-en-kerncontracten)

## 1. Doel en scope
- Opbouw van robuuste parkeerbezettingsdatasets (short-term en long-term).
- Phase 1 levert gevalideerde intermediate data + MAD-tabellen.
- Phase 2 levert EDA-inzichten, tabellen/figuren en train/holdout split.
- Latere fases behandelen feature engineering en modellering.

## 2. Snelle start
```bash
cd /Users/emilevandevoorde/Documents/mechelen_parking
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

## 3. Repository structuur (actueel)
```text
mechelen_parking/
├── configs/
├── data_raw/
├── data_intermediate/
├── data_processed/
├── data_models/
├── data_results/
├── figures/
│   ├── phase1/
│   │   └── nb03/
│   └── eda/
│       ├── nb06/
│       ├── nb07/
│       ├── nb08/
│       └── nb08b/
├── notebooks/
│   ├── phase1/
│   ├── phase2/
│   ├── 08_ft_ngr.ipynb
│   ├── 09_baseline_models.ipynb
│   ├── 10_global_models.ipynb
│   ├── FASE01_Recap.ipynb
│   ├── FASE02_Recap.ipynb
│   └── FASE03_Recap.ipynb
├── src/
│   ├── project_config.py
│   ├── io/
│   ├── phase1/
│   └── phase2/
├── tests/
├── README.md
└── STRUCTUUR.md
```

Voor detailafspraken over pipeline en contracts: zie `STRUCTUUR.md`.

## 4. Pipeline volgorde (actueel)

### Phase 1 - Data Prep
1. `notebooks/phase1/01_calendar_integration.ipynb`
- Input: feestdagen + schoolvakanties in `data_raw/`
- Output: `calendar_holidays_daily.parquet`, `calendar_schoolvac_daily.parquet`, `calendar_master.parquet` in `data_intermediate/`

2. `notebooks/phase1/02_data_quality_check.ipynb`
- Input: `parking_location.parquet`, `timeseries_shortterm.parquet`, `timeseries_longterm.parquet`
- Output: `shortterm_cleaned.parquet`, `longterm_cleaned.parquet`, `quality_report.csv` in `data_intermediate/`

3. `notebooks/phase1/03_weather_cleaning.ipynb`
- Input: `aws_1hour-5.csv`
- Output: `weather_cleaned.parquet` in `data_intermediate/`

4. `notebooks/phase1/04_event_assembly.ipynb`
- Input: eventbronnen + configuraties
- Output: `events_master.parquet` in `data_intermediate/`

5. `notebooks/phase1/05_mad_assembly.ipynb`
- Input: phase1 outputs + locatiedata
- Output: `MAD_shortterm.parquet`, `MAD_longterm.parquet` in `data_processed/`, plus `parking_location_clean.parquet` in `data_intermediate/`

### Phase 2 - EDA
6. `notebooks/phase2/06_eda_temporal.ipynb`
7. `notebooks/phase2/07_eda_spatio.ipynb`
8. `notebooks/phase2/08_eda_external_factors.ipynb`
9. `notebooks/phase2/08b_eda_LT.ipynb`
10. `notebooks/phase2/08c_train_test_split.ipynb`
    ├── Input  → data_processed/MAD_shortterm.parquet
    └── Output → data_processed/train.parquet     (2020/2023/2024)
                data_processed/holdout.parquet    (2025)

- Belangrijkste output: `data_processed/train.parquet`, `data_processed/holdout.parquet`

### Phase 3 - Feature Engineering
[PHASE 3 — FEATURE ENGINEERING (FREEZE POINT)]  notebooks/phase3/08c_feature_engineering.ipynb
├── Input  → data_processed/train.parquet
│            data_processed/holdout.parquet
├── Processing (fit on train only, transform both)
│     ├── T: time structure (sin/cos, calendar, holidays)
│     ├── S: spatial identity (encoding, tier, clusters, capacity)
│     ├── E: external (weather, events, interactions, cascade)
│     └── L: lags (occ_lag_1h/24h/168h; time-aware)
└── Output (IMMUTABLE DATASET FOR ALL MODELS)
      → data_features/train_features.parquet
      → data_features/holdout_features.parquet
      → data_features/feature_schema.json
      (+ optional transformers/)

## Phase 4 - Modelling

[PHASE 4 — MODELLING & EVALUATION]  notebooks/phase4/
├── 09_baselines.ipynb   (BENCHMARKS; no hyperparameter search)
│   Input  → data_features/train_features.parquet
│            data_features/holdout_features.parquet
│   Output → results/metrics/baselines_metrics.csv
│   Benchmarks:
│     ├── Forecast baselines (with L):
│     │    - persistence (lag1)
│     │    - daily naive (lag24)
│     │    - weekly naive (lag168)
│     └── Policy baselines (no L):
│          - seasonal profile mean (parking × hour × day_type_3)
│          - ridge (T + S + E)
│
├── 10_global_models.ipynb   (ML + ABLATIONS = RQ1 CORE)
│   Input  → data_features/train_features.parquet
│            data_features/holdout_features.parquet
│   Output → results/metrics/model_metrics.csv
│            results/predictions/predictions_2025.parquet
│            models/selected/best_forecast_model.pkl
│            models/selected/best_policy_model.pkl
│   Models:
│     - linear (ridge/elasticnet)
│     - random forest
│     - xgboost OR lightgbm
│   CV:
│     - rolling TimeSeriesSplit inside train (2020/2023/2024)
│   Ablations (feature configs):
│     - TS, TSE, TSL, TSEL, SE, TSE_noEvents
│
├── 11_tier_analysis.ipynb   (RQ1: tier differences in performance)
│   Input  → results/predictions/predictions_2025.parquet
│            data_features/holdout_features.parquet (metadata join)
│   Output → results/metrics/tier_performance_metrics.csv
│   Analysis:
│     - errors per tier_admin (centrum vs vesten)
│     - errors per parking
│     - error distributions + event vs non-event slices
│
├── 12_interpretability.ipynb
│   Input  → models/selected/best_forecast_model.pkl
│            models/selected/best_policy_model.pkl
│            data_features/holdout_features.parquet
│   Output → results/interpretability/feature_importance.csv
│            figures/shap_plots/
│   Analysis:
│     - SHAP / permutation importance (overall + per tier)
│     - PDP/ICE for key drivers (events, holidays, tier interactions)
│
├── 13_robustness_checks.ipynb   (OPTIONAL; supports RQ3)
│   Input  → data_features/*_features.parquet
│            model configs
│   Output → results/metrics/robustness_results.csv
│   Tests:
│     - remove wind_strong / cascade / target encoding
│     - alternative bins / thresholds
│     - stability of conclusions
│
└── 14_scenario_simulation.ipynb  (RQ2; POLICY APPLICATION)
    Input  → models/selected/best_policy_model.pkl      (NO-LAG preferred)
             data_features/holdout_features.parquet     (or scenario input grid)
             configs/simulation/scenarios.yaml          (pricing/incentives)
    Output → results/simulation/scenario_simulations.csv
             figures/scenario_plots/
    Goal:
      - simulate interventions to shift occupancy from centrum → vesten
      - report tier-level redistribution under scenarios

## 5. Figures output structuur
- Phase 1 weerdiagnostiek:
  - `figures/phase1/nb03/humidity_qc_diagnose.png`
  - `figures/phase1/nb03/dst_timezone_verificatie.png`
- Phase 2 EDA outputs:
  - `figures/eda/nb06/` voor notebook 06
  - `figures/eda/nb07/` voor notebook 07
  - `figures/eda/nb08/` voor notebook 08
  - `figures/eda/nb08b/` voor notebook 08b

## 6. Src modules
- Core:
  - `src/project_config.py`: centrale paden en defaults
  - `src/io/paths.py`: `@data/...` alias-resolutie

- IO readers:
  - `src/io/calendar_readers.py`
  - `src/io/parking_readers.py`
  - `src/io/weather_readers.py`
  - `src/io/phase2_readers.py`

- Phase 1:
  - `src/phase1/calendar.py`
  - `src/phase1/quality.py`
  - `src/phase1/weather.py`
  - `src/phase1/events.py`
  - `src/phase1/assembly.py`

- Phase 2:
  - `src/phase2/common.py`
  - `src/phase2/constants.py`
  - `src/phase2/stats.py`
  - `src/phase2/temporal.py`
  - `src/phase2/spatio.py`
  - `src/phase2/external_factors.py`
  - `src/phase2/longterm.py`
  - `src/phase2/split.py`

## 7. Dataflow en kerncontracten
Dataflow:
`data_raw -> data_intermediate -> data_processed -> data_models + data_results`

MAD-contract:
- Unieke sleutel: `(parking_id, rounded_hour)`
- Eventkolommen zitten direct in MAD (geen aparte post-hoc merge-stap)

Train/holdout-contract (phase2 split):
- `train.parquet`: jaren `2020, 2023, 2024`
- `holdout.parquet`: jaar `2025`
- Geen overlap op sleutel `(parking_id, rounded_hour)`
