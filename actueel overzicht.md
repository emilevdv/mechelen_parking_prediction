# Actueel Overzicht

Laatst geupdate: 2026-03-13  
Project: *Spatiotemporal Prediction and Optimization of Car Parking in Mechelen*

## 1. Telegram-stijl samenvatting

- `DOEL`: betrouwbare parkeerbezettingsmodellen bouwen die tegelijk voorspelkracht en beleidsrelevantie hebben.
- `STATUS`: Phase 1, 2, 3 en 4 zijn uitgevoerd; modelling-protocol en evaluaties zijn operationeel afgerond.
- `KERNOPZET`: 2 strikt gescheiden tracks blijven leidend.
- `SPOOR 1`: `policy = T + S + E` (zonder occupancy-lags; beleidsgerichte interpretatie).
- `SPOOR 2`: `forecast = T + S + E + L` (met autoregressieve lags; forecasting-doel).
- `SPLIT LOCK`: train = `2020, 2023, 2024`; holdout = `2025`; `2019` uitgesloten.
- `LEAKAGE-BELEID`: train-only fitting, fold-safe CV, causale features, geen kwaliteitsflags/proxies als predictor.
- `PHASE 4 STATUS`: audit PASS, fold-safe CV + fixed-export sensitivity uitgevoerd, holdout 2025 geëvalueerd, selectie-memo opgeleverd.
- `GO/NO-GO`: huidige status = `GO` volgens vastgelegde criteria in phase4-modelselectiememo.

## 2. Pipeline in ASCII

```text
RAW SOURCES
  |
  v
[PHASE 1] Cleaning + harmonisatie + assembly (MAD)
  Output: MAD_shortterm / MAD_longterm
  |
  v
[PHASE 2] EDA (temporal + spatial + external + interacties + bridge)
  Output: FE-beslissingen + split-advies + leakage guardrails
  |
  v
[PHASE 3] Feature Engineering
  |
  +--> fe_00: FE design lock
  |      - split hard vast
  |      - scope + protocol + registry-template
  |
  +--> fe_01: core TSE build
  |      - T (time), S (spatial), E (external)
  |      - gedeelde laag voor beide tracks
  |
  +--> fe_02: forecast-only L build
  |      - causale lags per parking/tijd
  |      - policy strikt zonder L
  |
  +--> fe_03: finalize + immutable export
         - policy_final (TSE)
         - forecast_final (TSE+L)
         - manifests, dictionaries, schema snapshots
  |
  v
[PHASE 4] Modelling & evaluatie (UITGEVOERD)
  |
  +--> p4_00: protocol + pre-modelling audit
  |      - checksum/schema/track contracts
  |      - event availability contract
  |
  +--> p4_01: fold-safe FE engine
  |      - per fold train-only fit parameters
  |      - fold logs + interne datasets
  |
  +--> p4_02: ablation CV runs
  |      - fold-safe primary
  |      - fixed-export sensitivity
  |
  +--> p4_03: iterative critique + refine
  |      - variabiliteitscheck
  |      - F4 retain/reject rule
  |      - shortlist
  |
  +--> p4_04: holdout + selectie memo
         - finale 2025 evaluatie
         - DM-test (optioneel) + GO/NO-GO
  |
  v
[PHASE 5] Interpretatie (SHAP/per-tier)  <-- next
  |
  v
[PHASE 6] Simulatie (policy what-if)      <-- daarna
```

## 3. Wat is al gedaan (uitgebreid stap-voor-stap)

1. `Phase 1`: data opgeschoond, geharmoniseerd en samengevoegd tot MAD-datasets.  
Waarom: consistente en reproduceerbare basis.

2. `Phase 2`: EDA uitgevoerd op temporal/spatial/external patronen + interacties + bridge naar FE.  
Waarom: featurekeuzes inhoudelijk funderen in plaats van ad hoc engineering.

3. `fe_00_design_and_split_lock.ipynb`: FE-scope, split-lock en leakageguardrails formeel vastgezet.  
Waarom: methodologisch contract vóór featurebuild.

4. `fe_01_build_core_features_TSE.ipynb`: gedeelde `T+S+E` laag gebouwd voor beide tracks.  
Waarom: één stabiele kernlaag, zodat policy en forecast vergelijkbaar blijven.

5. `fe_02_build_forecast_lag_features_L.ipynb`: forecast-only `L` features causaal toegevoegd.  
Waarom: forecasting-prestatie verhogen zonder policy-track te contamineren.

6. `fe_03_finalize_feature_sets_and_export.ipynb`: finale immutable exports + manifests + schema’s opgeleverd.  
Waarom: plug-and-play overdracht naar modellingfase.

7. `p4_00_protocol_and_pre_modelling_audit.ipynb`: Phase 4-protocol, checksums, contracts en event-availability contract gemaakt.  
Waarom: vooraf valideren dat modelling op correcte artefacts draait.

8. `p4_01_fold_safe_fe_engine.ipynb`: fold-safe FE per rolling fold opgebouwd, met fit-parameters per fold gelogd.  
Waarom: P0-risico (fold-leakage) expliciet afdekken.

9. `p4_02_ablation_cv_runs.ipynb`: ablations uitgevoerd met twee evaluatiemodi.  
Waarom: primaire claims op fold-safe CV, met fixed-export enkel als sensitivity-reference.

10. `p4_03_iterative_critique_and_refine.ipynb`: variabiliteitsregels toegepast, beperkte gerichte reruns uitgevoerd, shortlist vastgesteld.  
Waarom: kritische kwaliteitscontrole zonder model-zoo-explosie.

11. `p4_04_holdout_and_selection_memo.ipynb`: holdout 2025-run + finale memo + DM-tests + GO/NO-GO.  
Waarom: formele afsluiting van Phase 4 en voorbereiding op interpretatie/simulatie.

## 4. Kerncijfers en actuele resultaten

### 4.1 Data en featurebasis

- Train rows: `129,837`
- Holdout 2025 rows: `87,600`
- Policy modelinputs: `87` features (`T+S+E`)
- Forecast modelinputs: `92` features (`T+S+E+L`)

### 4.2 Pre-run audit (p4_00)

Alle hoofdchecks zijn `PASS`:
- policy bevat geen `l_` kolommen;
- forecast bevat exact 5 toegelaten `L`-features;
- forecast-modelinputs bevatten geen `l_valid_*` flags;
- immutable checksums kloppen.

### 4.3 Fold-safe FE logs (p4_01)

Per fold werd train-only fitting toegepast en gelogd:
- `cv_fold_1`: lag-valid rate train `76.26%`, valid `74.00%`
- `cv_fold_2`: lag-valid rate train `79.41%`, valid `75.20%`
- `cv_fold_3`: lag-valid rate train `83.62%`, valid `83.38%`

### 4.4 CV-run dekking (p4_02 + p4_03)

- `phase4_cv_results.csv`: `168` rijen
- `fit_status`: `ok` voor alle rijen
- varianten aanwezig in fold-safe én fixed-export: `P0..P4` en `F0..F4`
- modelfamilies: `baseline`, `ridge`, `random_forest`, `xgboost`

### 4.5 Iteratieve critique-uitkomst

- high-variability trigger geactiveerd: `10` runs boven drempel `std(MAE)/mean(MAE) > 0.15`
- gerichte extra runs toegevoegd: `4`
- F4-retain regel: `niet behouden` als primaire keuze voor selectiepad, omdat sample-retentie slechts `21.42%` was (ondanks MAE-winst)

### 4.6 Holdout 2025 (p4_04)

Geselecteerde primaire kandidaten:
- Forecast: `F3_rf_90_d12_l2` (selected)
- Policy: `P4_ridge_a1_0` (selected)

Belangrijke nuance:
- Forecast baseline `F0_persistence_baseline` heeft lagere holdout-MAE dan de geselecteerde `F3`, maar `F3` behoudt betere structurele forecast-opzet met stricte lag-valid context en betere foutstructuur op subset.
- Policy baseline `P0_profile_baseline` blijft een sterke benchmark en presteert qua MAE beter dan de policy-modelvarianten; dit moet expliciet mee in interpretatiehoofdstuk (geen overselling).

## 5. Niet-onderhandelbare methodologische keuzes (actueel bevestigd)

- Holdout `2025` bleef locked tot finale selectie-evaluatie.
- Fold-safe CV is primaire evaluatiebasis; fixed-export enkel sensitivity.
- Policy/forecast tracks blijven strikt gescheiden qua `L`-gebruik.
- Geen kwaliteitsflags of target-proxies als predictors.
- Event availability contract expliciet gekoppeld aan featurekeuzes.

## 6. Finale artefacts per fase

### 6.1 Feature-engineering artefacts (Phase 3)

Locatie: `data_processed/phase4_feature_sets/`
- `policy_train.parquet`
- `policy_holdout_2025.parquet`
- `forecast_train.parquet`
- `forecast_holdout_2025.parquet`
- `feature_registry.csv`
- `feature_manifest_policy.json`
- `feature_manifest_forecast.json`
- `schema_policy_snapshot.json`
- `schema_forecast_snapshot.json`
- `data_dictionary_policy.csv`
- `data_dictionary_forecast.csv`
- `immutable_export_manifest.csv`

### 6.2 Modelling artefacts (Phase 4)

Locatie: `data_results/phase4/`
- `phase4_protocol.md`
- `event_feature_availability_contract.csv`
- `phase4_ablation_plan.csv`
- `phase4_cv_results.csv`
- `phase4_cv_summary.csv`
- `phase4_fold_safety_log.csv`
- `phase4_iterative_critique_log.csv`
- `phase4_model_selection_shortlist.csv`
- `phase4_holdout_results_2025.csv`
- `phase4_dm_tests.csv`
- `phase4_model_selection_memo.md`

## 7. Methodologische interpretatie van huidige status

1. Fold-safety kritiek is operationeel geadresseerd.  
Er is nu een expliciete fold-safe FE-engine met per-fold logs.

2. Event ex-ante risico is geformaliseerd.  
Eventfeatures kregen availability-labels en werden conservatief geclassificeerd.

3. Policy met/zonder parking-effecten is expliciet zichtbaar gemaakt.  
Trade-off (nauwkeurigheid vs policy-sensitiviteit) is gerapporteerd i.p.v. verborgen.

4. Lag-validity impact is expliciet gemeten.  
Forecast-keuzes houden rekening met sample-retentie en validiteitsfilters.

## 8. Richting vanaf nu (Phase 5 en 6)

1. Start Phase 5 met interpretatie op geselecteerde modellen + relevante baselines.
2. Rapporteer interpretatie altijd met methodologische context:
   - fold-safe primair;
   - baselinevergelijking expliciet;
   - policy vs forecast-doeldoel verschillend.
3. Start daarna Phase 6-simulatie op policy-track varianten die inhoudelijk verdedigbaar blijven voor scenarioanalyse.

## 9. Korte conclusie

Projectstatus is nu: **FE + modelling protocol + holdout evaluatie operationeel afgerond en methodologisch gedocumenteerd**.  
Volgende stap is niet meer “bouwen”, maar **kritisch interpreteren en scenario-vertalen** zonder de vastgelegde guardrails te schenden.
