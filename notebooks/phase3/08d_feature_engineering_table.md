Ik heb de kolommen zo gekozen dat ze **methodologisch nuttig blijven voor later (nb09–nb14)** en tegelijk **interpretatiegericht** zijn voor je thesis.

### Kolommen:

1️ huidige naam (of _nieuwe feature_)  
2️ betekenis volgens huidige nb08 logica  
3️ voorgestelde definitieve naam  
4️ featurecategorie (T/S/E/L)  
5️ gebruik (forecast / policy / beide)  
6️ interpretatie-notitie  
7️ literatuur / conceptuele fundering  
8️ kritische opmerking / risico

---

## TLDR Feature Matrix — NB08 (Final Design)
| Huidige naam              | Betekenis volgens huidige notebook                                               | Definitieve naam         | Categorie         | Gebruik  | Interpretatie-notitie                                    | Conceptuele fundering                            | Kritische opmerking                 |
| ------------------------- | -------------------------------------------------------------------------------- | ------------------------ | ----------------- | -------- | -------------------------------------------------------- | ------------------------------------------------ | ----------------------------------- |
| hour_sin                  | sinus-transformatie van uur van de dag om circulaire tijdstructuur te modelleren | hour_sin                 | Temporal (T)      | beide    | piek tijdens kantooruren en shoppingmomenten             | standaard in time-series ML voor cyclic features | essentieel; nooit verwijderen       |
| hour_cos                  | cosinus-component van uur van de dag                                             | hour_cos                 | Temporal (T)      | beide    | samen met sin vormt dit een circulaire tijdrepresentatie | cyclic encoding (Hyndman & Athanasopoulos)       | geen                                |
| weekday_sin               | sinus-transformatie van weekday index                                            | weekday_sin              | Temporal (T)      | beide    | vangt verschillen tussen weekdagen                       | weekly mobility cycles                           | kan minder belangrijk zijn dan hour |
| weekday_cos               | cosinus-component weekday                                                        | weekday_cos              | Temporal (T)      | beide    | complementair aan weekday_sin                            | cyclic encoding                                  | geen                                |
| month_sin                 | sinus-transformatie maand                                                        | month_sin                | Temporal (T)      | beide    | seizoenseffecten in stadsgebruik                         | seasonal mobility patterns                       | mogelijk zwakker effect             |
| month_cos                 | cosinus maand                                                                    | month_cos                | Temporal (T)      | beide    | seizoenscyclus                                           | seasonal time-series encoding                    | geen                                |
| day_type_3                | categorie: werkdag / zaterdag / zondag+feestdag                                  | day_type_3               | Temporal/Calendar | beide    | vangt weekend shopping en recreatie                      | urban mobility studies                           | essentieel                          |
| year_2020                 | indicatorvariabele voor COVID-jaar                                               | covid_year_indicator     | Calendar          | beide    | structurele afwijking in mobiliteit                      | COVID mobility research                          | kan later irrelevant worden         |
| is_school_vacation        | indicator dat Belgische scholen vakantie hebben                                  | school_vacation_flag     | Calendar          | beide    | minder pendelverkeer maar meer leisure                   | travel demand studies                            | sterk plausibel                     |
| precip_mm → bin           | regenhoeveelheid gediscretiseerd in categorieën                                  | precipitation_intensity  | Weather (E)       | beide    | regen verhoogt autogebruik                               | weather-mobility interaction                     | bins correct valideren              |
| sun_duration_scaled       | geschaalde zonduur                                                               | sunshine_scaled          | Weather (E)       | beide    | goed weer verhoogt stadsbezoek                           | tourism & mobility                               | vaak zwakker dan regen              |
| wind_speed threshold      | indicator sterke wind                                                            | strong_wind_flag         | Weather (E)       | test     | mogelijk effect op comfort                               | micro-weather mobility                           | extreem zeldzaam                    |
| is_football_day           | indicator dat voetbalmatch plaatsvindt                                           | event_football           | Events (E)        | beide    | stadionevents genereren piekparking                      | event demand literature                          | sterk context-specifiek             |
| is_festival_day           | indicator festival                                                               | event_festival           | Events (E)        | beide    | grote bezoekersstromen                                   | event mobility studies                           | behouden                            |
| is_kermis_day             | indicator kermis                                                                 | event_kermis             | Events (E)        | beide    | lokale eventimpact                                       | event-driven demand                              | klein effect mogelijk               |
| is_carnival_day           | indicator carnaval                                                               | event_carnival           | Events (E)        | beide    | seizoensgebonden piek                                    | urban event research                             | zeldzaam                            |
| is_procession_day         | indicator religieuze processie                                                   | event_procession         | Events (E)        | beide    | lokale mobiliteitseffecten                               | niche events                                     | lage frequentie                     |
| nieuwe feature            | aantal gelijktijdige events                                                      | concurrent_event_count   | Events (E)        | beide    | cumulatief effect van meerdere events                    | demand aggregation                               | afhankelijk van eventdata kwaliteit |
| hours_since_last_event    | uren sinds vorige event                                                          | hours_since_event        | Event dynamics    | beide    | post-event afname in bezetting                           | event decay concept                              | sentinel nodig                      |
| hours_to_next_event       | uren tot volgende event                                                          | hours_to_event           | Event dynamics    | beide    | anticipatiegedrag                                        | anticipatory travel behaviour                    | sentinel nodig                      |
| nieuwe feature            | indicator dat geen vorige event bestaat                                          | no_previous_event_flag   | Event dynamics    | beide    | interpreteert sentinel                                   | missingness indicator                            | noodzakelijk                        |
| nieuwe feature            | indicator dat geen volgende event bestaat                                        | no_next_event_flag       | Event dynamics    | beide    | interpreteert sentinel                                   | missingness indicator                            | noodzakelijk                        |
| tier_admin                | categorische parkingtier (centrum / vesten)                                      | parking_tier             | Spatial (S)       | beide    | beleidsvariabele                                         | parking management literature                    | cruciaal                            |
| total_capacity            | aantal parkeerplaatsen                                                           | log_capacity             | Spatial (S)       | beide    | grotere parkings vullen trager                           | capacity effects                                 | log transform aanbevolen            |
| behavioral_cluster        | cluster op basis van LT gebruikspatronen                                         | parking_behavior_cluster | Spatial (S)       | beide    | type parking (shopping vs commuter)                      | clustering mobility behaviour                    | interpreteerbaarheid check          |
| high_lt_pressure          | indicator structurele vraagdruk                                                  | high_longterm_pressure   | Spatial (S)       | beide    | structurele populariteit                                 | demand persistence                               | overlap met lags                    |
| parking_id                | identifier parking                                                               | parking_id_onehot        | Spatial (S)       | beide    | parking-specifieke intercept                             | fixed-effects modelling                          | vervangt target encoder             |
| occ_lag_1h                | occupancy 1 uur geleden                                                          | occ_lag_1h               | Lag (L)           | forecast | inertia in bezetting                                     | autoregressive demand                            | alleen bij correct lag              |
| occ_lag_24h               | occupancy 24 uur geleden                                                         | occ_lag_24h              | Lag (L)           | forecast | dagelijkse cyclus                                        | seasonal AR                                      | correct berekenen                   |
| occ_lag_168h              | occupancy week geleden                                                           | occ_lag_168h             | Lag (L)           | forecast | weekly cycle                                             | weekly seasonality                               | idem                                |
| is_any_holiday            | indicator voor elke feestdag                                                     | verwijderd               | —                 | —        | redundant met day_type_3                                 | feature redundancy                               | verwijderen                         |
| parking_id_target_encoded | target encoding parking                                                          | verwijderd               | —                 | —        | leakage risico                                           | CV leakage in time-series                        | vervangen door one-hot              |





# Thesis “Projectverhaal” — TL;DR briefing (contextkader voor nb08→nb14)

### 0) Doel van de thesis

**Tier-Stratified Parking Occupancy Prediction with External Factors (Mechelen).**  
We bouwen een voorspel- en interpretatiekader dat:

1. **RQ1** beantwoordt: _wat is de meerwaarde van externe factoren t.o.v. puur temporele patronen, en verschilt dit per parkeertier?_
    
2. **RQ2** ondersteunt: _hoe gebruik je voorspellingen voor dynamische prijs-/beleidssimulaties om centrumdruk te verlagen en vesten te verhogen?_  
    (Optioneel) **RQ3**: overdraagbaarheid.
    

### 1) Fundamentele ontwerpkeuzes (niet meer van afwijken)

- **Train:** 2020 + 2023 + 2024
    
- **Holdout test:** 2025 (strict out-of-sample; **no tuning**)
    
- **Validatie binnen train:** rolling time-series CV (TimeSeriesSplit / rolling origin).
    
- **Dataset “freeze”:** na nb08 worden **geen features meer aangepast** (geen renames, geen “late additions”, geen nieuwe kolommen).
    
- **Twee modeldoelen naast elkaar (essentieel voor beleidsrelevantie):**
    
    - **Forecast track (korte termijn nauwkeurig):** _mag lags bevatten_.
        
    - **Policy track (beleidsgevoelig/structureel):** _geen occupancy-lags_ (vermijdt “past predicts future” als dominante driver; beter voor scenario’s).
        

---

## 2) Dataflow per notebook (input/output contract)

### NB08 — Feature Engineering (FINAL pipeline)

**Doel:** één reproduceerbare feature-matrix voor alle latere notebooks; leakage-proof.  
**Input:** `train.parquet` (2020/2023/2024), `holdout.parquet` (2025).  
**Output (immutable artifacts):**

- `train_features.parquet`
    
- `holdout_features.parquet`
    
- `feature_schema.json` (kolomnamen + dtypes + featuregroepen + versie)
    
- (optioneel) `transformers/` (scalers, target encoder)
    

**Belangrijk: nb08 bouwt 2 expliciete feature-sets in dezelfde parquet:**

- **Full feature universe** = alle kolommen die later nodig zijn
    
- Maar nb09/nb10 selecteren subsets via vaste lijsten.
    

**Featuregroepen (frozen, single source of truth):**

- **T (time structure):** sin/cos hour/weekday/month + day_type_3 + year_2020 + holiday/vacation.
    
- **S (spatial identity):** mean_occ_by_parking (target encoding), tier_num, behavioral_cluster, high_lt_pressure, log_capacity.
    
- **E (external):** weather (precip_bin, wind_strong, sun_scaled), events (type dummies + n_concurrent_events), interacties (event×tier), cascade (hours_to/since + sentinel/clip).
    
- **L (autoregressive):** occ_lag_1h/24h/168h **time-aware** (gaten → NaN correct).
    

**Data quality policy:**

- Lag-NaN’s zijn verwacht; nb09/nb10 droppen met **één conservatieve mask**: `occ_lag_168h.notna()` (wie 168h heeft, heeft 24h en 1h doorgaans ook).
    
- Cascade NaN’s worden **niet gedropt**; sentinel=999 + clip.
    

**Waarom dit nuttig is:** nb08 maakt alle latere analyses consistent; voorkomt “feature drift” en leakage.

---

### NB09 — Baselines (benchmarks, geen model zoo)

**Doel:** referentieprestaties vastleggen voor beide tracks (forecast + policy).  
**Input:** `train_features.parquet`, `holdout_features.parquet`  
**Output:** `outputs/baselines_metrics.csv` + 1–2 figuren (error per tier/parking).

**Baseline-set (max 5, bewust beperkt):**

**Forecast baselines (met lags; pure regels, geen sklearn):**

1. **Persistence:** ŷ=occ_lag_1h
    
2. **Daily seasonal naive:** ŷ=occ_lag_24h
    
3. **Weekly seasonal naive:** ŷ=occ_lag_168h
    

**Policy baselines (zonder occupancy-lags; beleidsrelevant):**  
4) **Seasonal profile mean (no-lag):** gemiddelde per _(parking × hour × day_type_3)_ uit train → predict holdout  
5) **Ridge (no-lag, fixed):** ridge-regressie op **T+S+E zonder L** (geen tuning of minimaal; dit is baseline-ML)

**Metrics (altijd):** MAE, RMSE, MAPE + per tier_admin (centrum vs vesten) + per parking (optioneel).  
**Waarom nuttig:** geeft ondergrens voor “forecasting” én ondergrens voor “policy without lags”.

---

### NB10 — Global models (kern van RQ1 via ablations)

**Doel:** echte ML-modellen trainen + **ablatie-experimenten** uitvoeren om bijdrage van externe factoren en lags te kwantificeren (overall + per tier).  
**Input:** features (frozen) uit nb08  
**Output:**

- `outputs/models_metrics.csv` (alle configs × metrics)
    
- `outputs/best_forecast_model.pkl`
    
- `outputs/best_policy_model.pkl`
    
- `outputs/predictions_2025.parquet` (met metadata voor nb11–nb12)
    

**Modelkeuze (max 3, thesis-proof):**

- **ElasticNet/Ridge** (interpretabele lineaire referentie)
    
- **RandomForest** (sterk tabular, robuust)
    
- **XGBoost of LightGBM** (kies één; SOTA tabular)  
    _(Niet uitbreiden tenzij je een sterke motivatie hebt; helderheid > modelzoo.)_
    

**Validatie/tuning:**

- Binnen train: rolling TimeSeriesSplit (k=5) voor hyperparams (alleen RF + XGB/LGB).
    
- Holdout 2025: 1x finale evaluatie.
    

---

## 3) Perfect experiment design (RQ1 “informatiebronnen” i.p.v. modelzoo)

### Kern: ablaties op featuregroepen

Gebruik vaste blokken (T,S,E,L) en test minimaal deze configs:

1. **TS (structure-only):** T + S
    
2. **TSE (structure + extern):** T + S + E _(test externe meerwaarde vs structure)_
    
3. **TSL (structure + lags):** T + S + L _(test autoregressieve dominantie)_
    
4. **TSEL (full):** T + S + E + L _(best forecasting accuracy verwacht)_
    
5. **SE (extern+spatial, no time):** S + E _(sanity check)_
    
6. **TSE_noEvents:** T + S + (E zonder events/cascade) _(isoleer eventbijdrage)_
    

### Wat je rapporteert (altijd)

- MAE/RMSE/MAPE overall (2025)
    
- dezelfde metrics **per tier_admin**
    
- optioneel: “event days vs non-event days” error
    
- modelranking en delta’s:
    
    - **Δ(TSE − TS)** = bijdrage externe factoren
        
    - **Δ(TSEL − TSE)** = extra winst door lags
        
    - **per tier**: dezelfde delta’s → “tier-stratified importance”
        

### Thesis-interpretatie (verwachte patronen)

- Lags geven meestal grootste winst voor korte termijn (forecast track).
    
- Externe factoren leveren meetbare winst bovenop T+S, vooral rond events/vakanties.
    
- Policy track (zonder L) is minder accuraat maar **beleidsrelevant** en geschikt voor simulaties.
    

---

## 4) Logische keten nb09 → nb14 (waarom elk notebook bestaat)

- **nb09 Baselines:** benchmarks (forecast + policy no-lag).
    
- **nb10 Global models + ablations:** RQ1 bewijs (extern vs lags vs structure), kiest 2 “kampioen”-modellen:
    
    - **best_forecast_model** (met L)
        
    - **best_policy_model** (zonder L)
        
- **nb11 Tier-stratified evaluation:** performance & fouten per tier/parking; check waar model faalt; vertaalt naar beleidscontext.
    
- **nb12 Interpretability:** SHAP/permutation importance, **per tier**; identificeert drivers (events, vakantie, interacties).
    
- **nb13 Robustness / Transferability (optioneel):** sensitivity checks; welke componenten blijven stabiel (RQ3).
    
- **nb14 Scenario simulation:** gebruik **best_policy_model** (zonder L) voor dynamische prijs-/beleidssimulaties; doel = verschuiving bezetting centrum→vesten.
    

**Cruciale nuance:**  
Simulaties (nb14) met lag-occupancy zijn riskant omdat je beleidsinterventie “wegdrukt” door inertie/feedback; daarom policy model zonder L.

---

## 5) Scopebewaking (om “all over the place” te vermijden)

**Strikte regels:**

- nb08 = laatste notebook waar features veranderen.
    
- nb09 = alleen benchmarks (max 5). Geen hyperparam search.
    
- nb10 = alleen ML + ablations. Geen feature engineering. Geen renames.
    
- Elke notebook schrijft 1–2 artifacts weg die de volgende notebook consumeert.
    
- Eén centrale `config.py`/`constants.py` of `feature_schema.json` bepaalt featuregroepen.
    

---

## 6) Wat “succes” betekent (jury-gericht)

- Je kan helder aantonen:
    
    - _Externe factoren voegen X% foutreductie toe vs TS_ (RQ1)
        
    - _Die bijdrage verschilt per tier_ (RQ1)
        
    - _Policy-simulaties gebaseerd op policy model tonen verschuiving centrum→vesten_ (RQ2)
        
- Je maakt een volwassen onderscheid tussen “accuracy” en “policy relevance”.
    

Dit is het referentiekader dat je (of een ander model) telkens kan gebruiken om beslissingen in nb08–nb14 consistent te houden.