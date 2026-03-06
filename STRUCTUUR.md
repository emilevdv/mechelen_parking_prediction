# Repositorystructuur en Pipeline (actueel na phase2 refactor)

Dit document is de referentie voor de huidige projectstructuur, uitvoervolgorde en datacontracten.

## 1. Ontwerpprincipes
- Notebook-first voor exploratie en rapportage.
- Herbruikbare logica in `src/`.
- Duidelijke fasegrenzen en stabiele output-contracten.
- Expliciete inputs/outputs per stap.
- Lineaire dataflow: `raw -> intermediate -> processed -> modeling/results`.

## 2. Actuele top-level structuur

```text
mechelen_parking/
├── README.md
├── STRUCTUUR.md
├── requirements.txt
├── .gitignore
│
├── configs/
│   └── README.md
│
├── data_raw/
├── data_intermediate/
├── data_processed/
├── data_models/
├── data_results/
│
├── figures/
│   ├── phase1/
│   │   └── nb03/
│   │       ├── humidity_qc_diagnose.png
│   │       └── dst_timezone_verificatie.png
│   └── eda/
│       ├── nb06/
│       ├── nb07/
│       ├── nb08/
│       └── nb08b/
│
├── notebooks/
│   ├── phase1/
│   │   ├── 01_calendar_integration.ipynb
│   │   ├── 02_data_quality_check.ipynb
│   │   ├── 03_weather_cleaning.ipynb
│   │   ├── 04_event_assembly.ipynb
│   │   └── 05_mad_assembly.ipynb
│   ├── phase2/
│   │   ├── 06_eda_temporal.ipynb
│   │   ├── 07_eda_spatio.ipynb
│   │   ├── 08_eda_external_factors.ipynb
│   │   ├── 08b_eda_LT.ipynb
│   │   └── 08c_train_test_split.ipynb
│   ├── phase3/
│   │   ├── 08d_feature_engineering_final.ipynb
│   │   ├── 08d_feature_engineering_table.md
│   ├── 09_baseline_models.ipynb              # <-- 09, 10, 11, ... phase4 meoten ofwel nog verplaatst worden  / gemaakt worden
│   ├── 10_global_models.ipynb
│   ├── FASE01_Recap.ipynb
│   ├── FASE02_Recap.ipynb
│   ├── FASE03_Recap.ipynb
│   └── mechelen_events_2020_2026.csv
│
├── src/
│   ├── __init__.py
│   ├── project_config.py
│   ├── io/
│   │   ├── __init__.py
│   │   ├── paths.py
│   │   ├── calendar_readers.py
│   │   ├── parking_readers.py
│   │   ├── weather_readers.py
│   │   └── phase2_readers.py
│   ├── phase1/
│   │   ├── __init__.py
│   │   ├── calendar.py
│   │   ├── quality.py
│   │   ├── weather.py
│   │   ├── events.py
│   │   └── assembly.py
│   └── phase2/
│       ├── __init__.py
│       ├── common.py
│       ├── constants.py
│       ├── stats.py
│       ├── temporal.py
│       ├── spatio.py
│       ├── external_factors.py
│       ├── longterm.py
│       └── split.py
│
├── tests/
└── scripts/
```

## 3. Data-pipeline flow (actueel)

```text
PHASE 1 — DATA PREP
01_calendar_integration
  -> calendar_holidays_daily.parquet
  -> calendar_schoolvac_daily.parquet
  -> calendar_master.parquet

02_data_quality_check
  -> shortterm_cleaned.parquet
  -> longterm_cleaned.parquet
  -> quality_report.csv

03_weather_cleaning
  -> weather_cleaned.parquet
  -> figures/phase1/nb03/*.png

04_event_assembly
  -> events_master.parquet

05_mad_assembly
  Input: shortterm_cleaned + longterm_cleaned + weather_cleaned + calendar_master + events_master + parking_location
  -> MAD_shortterm.parquet
  -> MAD_longterm.parquet
  -> parking_location_clean.parquet

PHASE 2 — EDA
06_eda_temporal
  -> figures/eda/nb06/*
07_eda_spatio
  -> figures/eda/nb07/*
08_eda_external_factors
  -> figures/eda/nb08/*
08b_eda_LT
  -> figures/eda/nb08b/*
08c_train_test_split
  -> data_processed/train.parquet
  -> data_processed/holdout.parquet

PHASE 3 — FEATURE ENGINEERING (huidige notebooknaam)
08_ft_ngr
  -> train_features.parquet / holdout_features.parquet (verwacht)

PHASE 4 — MODELLING (huidige notebooknamen)
09_baseline_models
10_global_models
```

## 4. Fasegrenzen en verantwoordelijkheden
- `04_event_assembly`: bouwt enkel `events_master`.
- `05_mad_assembly`: doet alle joins (weather/calendar/location/events) in een stap.
- Event-merge gebeurt niet langer als post-hoc update op MAD.
- `08c_train_test_split`: levert het enige officiele train/holdout contract voor huidige pipeline.

## 5. Datacontracten (kernoutputs)
- `data_intermediate/events_master.parquet`:
  - 1 rij per dag binnen projectbereik.
  - Flags: `is_event_day`, `is_football_day`, `is_festival_day`, `is_procession_day`, `is_kermis_day`, `is_carnival_day`.
- `data_processed/MAD_shortterm.parquet` en `data_processed/MAD_longterm.parquet`:
  - primaire sleutel: `(parking_id, rounded_hour)` uniek.
  - bevat eventkolommen direct in MAD.
- `data_processed/train.parquet` en `data_processed/holdout.parquet`:
  - train: jaren `2020, 2023, 2024`
  - holdout: jaar `2025`
  - geen overlap op `(parking_id, rounded_hour)`.

## 6. Uitvoeringsregel
Bij volledige run deze volgorde aanhouden:
1. Phase 1 notebooks `01` t/m `05`.
2. Phase 2 notebooks `06`, `07`, `08`, `08b`, `08c`.
3. Daarna feature engineering en modeling.

## 7. Migratie-roadmap (nog niet volledig toegepast)
Deze mapping blijft de doelchronologie voor toekomstige notebook-hernoeming buiten phase2:
- `08_ft_ngr.ipynb` -> `phase3/09_feature_engineering.ipynb`
- `09_baseline_models.ipynb` -> `phase4/10_baseline_models.ipynb`
- `10_global_models.ipynb` -> `phase4/11_global_models.ipynb`
