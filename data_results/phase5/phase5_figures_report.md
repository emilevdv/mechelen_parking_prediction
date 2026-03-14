# Phase 5 Figure Report (Intuitive + Academic)

Datum: 2026-03-14

## 1. Scope
- Primary interpretatiemodellen: P4 (policy) en F3 (forecast).
- Benchmarkcontrast: P0 en F0.
- Basis: bestaande Phase 5 artefacts; geen nieuwe tuning.

## 2. Figuuroverzicht
- Figure 1: holdout top-15 SHAP features per primary model.
- Figure 2: relatieve SHAP-massa per featurefamilie (T/S/E/L).
- Figure 3: fold-rank heatmaps voor top holdout features.
- Figure 4: stabiliteitslandschap (mean rank, std rank, top10 frequency).
- Figure 5: tier-delta forest plots met 95% CI en significantie.
- Figure 6: dependence-zoom voor geselecteerde topfeatures.
- Figure 7: holdout accuracy trade-off (primary vs baseline).
- Figure 8: baseline-stage decompositie op holdout.
- Figure 9: additiviteitsdiagnostiek van SHAP.

## 3. Intuitieve kernbevindingen
- Policy P4 top-10 wordt gedomineerd door: t_season__zomer, s_parking_id__p_maarten, t_hour_cos, s_parking_id__p_hoogstraat, e_int_temp_x_season__zomer, e_n_concurrent_events_capped, t_hour_sin, s_parking_id__p_tinel, e_int_temp_x_season__lente, t_season__lente.
- Forecast F3 top-10 wordt gedomineerd door: l_occ_lag_1h, l_occ_lag_168h, l_occ_lag_24h, t_hour_sin, t_hour_cos, s_capacity_bucket__medium, l_occ_lag_delta_1h_24h, t_weekday_cos, e_sun_intensity_log1p, t_weekday_sin.
- Policy holdout MAE-gap (P4 - P0): 0.0105 (P0 beter).
- Forecast holdout MAE-gap (F3 - F0): 0.0015 (F0 beter op full holdout).

## 4. Academische interpretatie
### 4.1 Stabiliteit
- Iteratieve stabiliteitsregel activeerde rerun: top10_jaccard=0.5018 < 0.60.
- Dit ondersteunt methodologische strengheid: claims steunen op gehercalculeerde SHAP-structuur.

### 4.2 Tier-heterogeniteit
- Significantie-aandeel tier-deltas: P4=20.7%, F3=79.3%.
- Conclusie: forecast vertoont sterkere, consistenter meetbare tierverschillen dan policy in deze opzet.

### 4.3 Trade-off versus benchmark
- Benchmark-beter-regel geactiveerd: True.
- Thesisclaim moet expliciet scheiden: predictieve minimumfout vs methodologisch interpreteerbare modelkeuze.

### 4.4 Additiviteitscontrole
- Figure 9 toont lage additiviteitsfouten over contexten, wat de numerieke consistentie van SHAP-decomposities ondersteunt.

## 5. Beperkingen
- SHAP-interpretatie blijft associatief en niet causaal.
- Per-tier conclusies moeten beperkt blijven tot features met CI- en permutation-ondersteuning.
- Benchmarksuperioriteit op holdout-MAE blijft een expliciete randvoorwaarde in de discussie.

## 6. Praktische thesis-aanbeveling
- Gebruik Figure 1-2 om globale verhaalstructuur te introduceren.
- Gebruik Figure 3-5 voor methodologische robuustheid en heterogeniteit.
- Gebruik Figure 7-8 om het primaire trade-off argument expliciet te maken.
- Verwijs Figure 6 als intuitieve verdieping; positioneer dit als exploratief.