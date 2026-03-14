# Mechelen Parking

Notebook-based data and model pipeline for the thesis:
**"Spatiotemporal Prediction and Optimization of Car Parking in Mechelen"**.

## 1. Doel en scope

Mijn project zou er zo moeten uitzien: 
Phase1: data cleaning en consolidatie 
Phase2: EDA 
Phase3: Feature Engineering 
Phase4: MODELLING & EVALUATION 
Phase5: Interpretatie 
Phase6: Simulatie

Meer uitleg vind je in bron: 'geannoteerde onderzoeksvoorstel' !!!


##  Notebook-structuur voor phase 2
eda_00_protocol_and_data_audit.ipynb
eda_01_global_descriptives.ipynb
eda_02_temporal_patterns.ipynb
eda_03_spatial_patterns.ipynb
eda_04_external_factors.ipynb
eda_05_shortterm_vs_longterm.ipynb
eda_06_interactions_and_hypothesis_synthesis.ipynb
eda_07_feature_engineering_bridge.ipynb
Dit sluit goed aan bij het onderzoeksvoorstel: temporal, spatial, external, plus expliciete aandacht voor ST vs LT en een afsluitende brug naar phase 3. 


##  Aanbevolen notebook-structuur voor phase 3 Feature Engineering
Ik zou phase 3 opdelen in deze FE-notebookstructuur:
fe_00_design_and_split_lock.ipynb
fe_01_build_core_features_TSE.ipynb
fe_02_build_forecast_lag_features_L.ipynb
fe_03_finalize_feature_sets_and_export.ipynb


## . Repository structuur
```text
mp_mechelen_parking_v2/
├── ...
├── configs/
├── data_raw/
├── data_intermediate/
├── data_processed/
├── data_models/
├── data_results/
├── figures/
│   ├── phase1/
│   │   └── .../
│   └── eda/
│       ├ ...
├── notebooks/
│   ├── phase1/
│   ├── phase2/
│   ├─- phase3/
│   ├─- phase4/
│   ├─- phase5/
│   ├─- phase/
├── src/
│   ├── project_config.py
│   ├── io/
│   ├── phase1/
│   ├── phase2/
│   ├── ...
│   └── phase6/
├── tests/
├── README.md
└── STRUCTUUR.md <-- nog aan te maken, actueel te maken
```

Voor detailafspraken over pipeline en contracts: zie `STRUCTUUR.md`. <-- nog aan te maken, actueel te maken

