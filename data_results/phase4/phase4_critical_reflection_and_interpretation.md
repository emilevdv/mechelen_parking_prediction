# Phase 4 Kritische Reflectie en Interpretatie

Datum: 2026-03-13  
Project: *Spatiotemporal Prediction and Optimization of Car Parking in Mechelen*

## 1. Doel en scope van deze reflectie

Dit document rapporteert wat methodologisch en empirisch geconcludeerd kan worden uit de volledige uitvoering van Phase 4.  
De focus ligt op:

- methodologische geldigheid (fold-safety, trackscheiding, holdout-discipline),
- interpretatie van ablaties en modelgedrag,
- kritische beoordeling van resterende risico's,
- implicaties voor verdere onderzoeksfasen.

Alle conclusies hieronder zijn gebaseerd op de effectieve artefacts in `data_results/phase4/`.

## 2. Bewijsbasis (artefacts)

Kernbestanden gebruikt voor deze reflectie:

- `phase4_protocol.md`
- `phase4_contract_checks.csv`
- `phase4_immutable_checksum_audit.csv`
- `phase4_fold_safety_log.csv`
- `event_feature_availability_contract.csv`
- `phase4_ablation_plan.csv`
- `phase4_cv_results.csv`
- `phase4_cv_summary.csv`
- `phase4_iterative_critique_log.csv`
- `phase4_model_selection_shortlist.csv`
- `phase4_holdout_results_2025.csv`
- `phase4_dm_tests.csv`
- `phase4_model_selection_memo.md`

## 2.1 Wat effectief is uitgevoerd in Phase 4 (notebook-first)

1. `p4_00_protocol_and_pre_modelling_audit.ipynb`
- Methodologische spelregels vastgezet.
- Artefact-audit uitgevoerd op schema/checksum/track-separatie.
- Event availability contract opgesteld met conservatieve labeling.

2. `p4_01_fold_safe_fe_engine.ipynb`
- Fold-safe FE-rebuild per CV-fold gebouwd vanaf splitdata.
- Train-only fitting afgedwongen voor fit-afhankelijke transformaties.
- Causale lagconstructies en validity-flags opnieuw berekend.
- Fold safety log met fit-parameters per fold geëxporteerd.

3. `p4_02_ablation_cv_runs.ipynb`
- Volledige ablation map uitgevoerd: policy `P0..P4`, forecast `F0..F4`.
- Beperkte modelset toegepast (baseline, ridge, RF, XGBoost).
- Zowel `fold_safe` als `fixed_export` CV-mode gerund.

4. `p4_03_iterative_critique_and_refine.ipynb`
- Iteratieve zelfkritiek toegepast op ronde-1 resultaten.
- Bijsturing alleen gedaan waar variabiliteitsdrempel werd overschreden.
- Beperkte reruns toegevoegd, zonder model-zoo-uitbreiding.

5. `p4_04_holdout_and_selection_memo.ipynb`
- Shortlist op basis van fold-safe CV vastgelegd.
- Eenmalige holdout-evaluatie op 2025 uitgevoerd.
- Modelselectiememo, holdoutresultaten en optionele DM-tests opgeleverd.

## 3. Methodologische beoordeling

### 3.1 Wat aantoonbaar correct is uitgevoerd

1. Holdout-lock discipline is gerespecteerd.
- Protocol expliciteert dat 2025 locked blijft tot finale selectie.
- Holdout-evaluatie is pas gerapporteerd na CV-gedreven shortlist.

2. Trackscheiding is technisch afgedwongen.
- `policy_has_no_l_columns = PASS`.
- `forecast_has_exact_5_selected_l_columns = PASS`.
- `forecast_excludes_l_validity_flags_from_model_inputs = PASS`.

3. Artefact-integriteit is gecontroleerd.
- Immutable checksums: 11/11 correct (`checksum_ok=True`).

4. Fold-safe evaluatie is primair gebruikt.
- Protocol: fold-safe scores zijn hoofdclaim; fixed-export alleen sensitivity.
- In resultaten en memo is dit onderscheid behouden.

5. Per-fold fit-discipline is expliciet gelogd.
- `phase4_fold_safety_log.csv` bevat per fold de gefitte parameters (o.a. thresholds, caps, bins) en bevestigt train-only fit-scope.

### 3.2 Wat methodologisch sterk is

- Er is een expliciete scheiding tussen een methodologisch correcte evaluatielijn (`fold_safe`) en een gevoeligheidslijn (`fixed_export`).
- De event-availability problematiek is niet genegeerd maar geformaliseerd in een contractbestand.
- De ablation map is volledig uitgevoerd voor beide tracks (P0..P4 en F0..F4).

### 3.3 Kritische nuance

- Fold-safe correctheid is aangetoond op procesniveau, maar blijft afhankelijk van correcte implementatie van alle FE-stappen in de fold-engine. De log ondersteunt dat sterk, maar is geen formeel bewijs van afwezigheid van alle mogelijke implementatiedetailsfouten.
- De methodologische kwaliteit is hoog; de inhoudelijke waarde van sommige featureblokken blijft echter een empirische vraag (zie secties 4 en 5).

## 4. Empirische resultaten en interpretatie

## 4.1 Fold-safe versus fixed-export: impact op claims

Belangrijkste observatie:

- In de forecast-track is fixed-export systematisch optimistischer dan fold-safe.
- Gemiddelde MAE-verschuiving (`fold_safe - fixed_export`) in forecast: `+0.01095`.
- Voor top-forecastmodellen ligt de relatieve kloof vaak rond `~18%` tot `~25%` van de fold-safe MAE.

Interpretatie:

- Dit bevestigt de oorspronkelijke zorg rond fold-safety als reëel en substantieel.
- Hoofdclaims op fixed-export zouden methodologisch overschat zijn.
- De keuze om fold-safe als primair te nemen is dus niet alleen theoretisch, maar empirisch noodzakelijk.

Nuance:

- In de policy-track is het verschil bijna nul (gemiddeld licht negatief, praktisch verwaarloosbaar).
- Dat komt waarschijnlijk doordat policy-features minder afhankelijk zijn van agressieve historiek-gebaseerde filtering/lag-constructies.

## 4.2 Forecast-track (T+S+E+L): wat leren de ablaties echt?

Fold-safe best per variant (MAE):

- `F0` persistence baseline: `0.08843`
- `F2` TSEL-core RF: `0.06784`
- `F3` TSEL-core + strict lag-valid subset RF: `0.06536`
- `F4` TSEL + strict rolling RF: `0.06048`

Kerninterpretatie:

1. L-features voegen duidelijk waarde toe t.o.v. naïeve persistence binnen CV.
- `F2` vs `F0`: `-23.28%` MAE (fold-safe).

2. Striktere lag-valid filtering helpt in CV, maar met samplekost.
- `F3` verbetert MAE t.o.v. `F2` met `-3.66%`.
- Gemiddelde valid-rijen daalt van `14767` (`F2`) naar `11660` (`F3`).

3. `F4` presteert het best op CV-MAE, maar werd terecht niet primair gekozen.
- `F4` vs `F2`: `-10.85%` MAE, maar retention slechts `21.42%`.
- Deze trade-off is methodologisch terecht als "te duur" beoordeeld en expliciet verworpen volgens vooraf vastgelegde regel.

Holdout-nuance (2025):

- `F0` baseline heeft laagste holdout-MAE (`0.06347`) op volledige set (`n=87600`).
- Geselecteerde `F3` heeft iets slechtere MAE (`0.06497`) maar betere RMSE (`0.09954` vs `0.11144`) op kleinere geldige subset (`n=78017`).

Interpretatie:

- Forecastconclusies moeten genuanceerd zijn: de geavanceerde lagmodellen leveren duidelijke CV-meerwaarde en lagere foutspreiding in hogere fouten (RMSE), maar niet automatisch betere holdout-MAE op de volledige populatie.
- De keuze voor `F3` blijft verdedigbaar als "forecast op strikt valide autoregressieve context", maar niet als universeel beste model voor alle operationele settings.

## 4.3 Policy-track (T+S+E): wat leren de ablaties echt?

Fold-safe best per variant (MAE):

- `P0` profielbaseline: `0.20721` (beste)
- `P4` ridge, ex-ante strict events: `0.22194`
- `P3` xgboost, full TSE met parking_id: `0.22226`
- `P2` xgboost, zonder parking_id: `0.22739`

Empirische interpretatie:

1. De profielbaseline domineert op pure foutmaat.
- `P4` is `+7.11%` slechter dan `P0` in fold-safe MAE.
- `P3` en `P2` zijn nog zwakker.

2. `parking_id` helpt wel, maar niet genoeg om baseline te kloppen.
- `P3` (met parking_id) beter dan `P2` (zonder), maar beide blijven onder `P0`.

3. Ex-ante strengere eventkeuze (P4) is methodologisch sterker, niet nauwkeuriger.
- `P4` en `P3` liggen dicht bij elkaar, met licht voordeel van `P4` op MAE in CV.
- Op holdout is `P4` en `P3` quasi gelijk in MAE.

Holdout-nuance:

- `P0` blijft beste holdout-MAE (`0.20640`).
- Geselecteerde `P4` scoort `0.21691`.

Interpretatie:

- Voor policy-doeleinden ontstaat een klassieke spanning: best voorspellende baseline vs methodologisch/causaal-strengere variant.
- `P4` is verdedigbaar als primaire policy-kandidaat voor interpretatie en ex-ante bruikbaarheid, maar niet als "accuraatste" policy-model.

## 4.4 Lag-validity en sample-selectie

Per-fold lag-valid rates:

- Train: `76.26%`, `79.41%`, `83.62%`
- Valid: `74.00%`, `75.20%`, `83.38%`
- Gemiddelde valid lag-valid: `77.52%`

Implicaties:

- Forecastmodellen met strikte lagregels leren/evalueren op een geselecteerde subpopulatie.
- F3/F4-resultaten zijn dus conditioneel op "lag-valid" observaties en niet direct generaliseerbaar naar alle timestamps.

Belangrijke nuance:

- De vroegere zorg "sterke asymmetrie train vs holdout" is deels geadresseerd: foldlogs tonen consistente maar niet identieke validiteitspercentages over tijd.
- Er blijft wel een structureel sample-selectiemechanisme dat in thesisrapportering expliciet moet blijven.

## 4.5 Event-features: ex-ante bruikbaarheid

Event-contract telling:

- `ex_ante_probable`: `16`
- `ex_post_or_uncertain`: `5`
- `ex_ante_guaranteed`: `0`

Interpretatie:

- De conservatieve contractregel is methodologisch prudent en reduceert risico op pseudo-ex-ante informatie.
- Tegelijk toont dit dat volledige ex-ante garantie operationeel nog niet hard is aangetoond voor eventinformatie.
- Daardoor is het correct dat onzekere proximity/window/since/to-features niet in de primaire set zijn opgenomen.

## 4.6 Iteratieve kritiek en statistische vergelijking

Iteratieve bijsturing (`phase4_iterative_critique_log.csv`):

- `10` runs overschreden de variabiliteitsdrempel (`std(MAE)/mean(MAE) > 0.15`).
- Er zijn `4` gerichte refinement-runs toegevoegd.
- Dit ondersteunt dat iteratie doelgericht en begrensd bleef (geen opportunistische brede hertuning).

DM-tests op holdout (`phase4_dm_tests.csv`):

- Policy: `P0_profile_baseline` vs `P4_ridge_a1_0`, `DM=-17.4471`, `p=0.0000`.
- Forecast: `F0_persistence_baseline` vs `F3_rf_90_d12_l2`, `DM=-10.6421`, `p=0.0000`.

Interpretatie:

- Er is statistisch sterk bewijs dat foutreeksen tussen de vergeleken modellen verschillen.
- In combinatie met holdout-MAE suggereert dit in beide tracks een voordeel voor de baseline-run binnen de geteste vergelijking.
- De keuze voor `P4` en `F3` moet daarom expliciet als methodologisch-gedreven keuze worden gepositioneerd, niet als eenduidige foutminimum-keuze op holdout.

## 5. Segmentanalyse (inhoudelijke robuustheid)

Op holdout (geselecteerde en baseline runs) zien we systematisch:

1. Centrum is moeilijker dan vesten/rand.
- Forecast `F3`: centrum-MAE `0.07299` vs vesten/rand `0.05639`.
- Policy `P4`: centrum-MAE `0.25468` vs vesten/rand `0.17914`.

2. Event-uren zijn iets moeilijker dan non-event, maar verschil is klein.
- Forecast `F3`: event-non-event delta `~+0.0010` MAE.
- Policy `P4`: event-non-event delta `~+0.0074` MAE.

Interpretatie:

- Ruimtelijke heterogeniteit (centrum vs rand) blijft een grotere foutdriver dan eventstatus op aggregate niveau.
- Dit ondersteunt verdere tier- of locatiegerichte modeldiagnostiek in vervolgonderzoek.

## 6. Metriekkeuze en rapporteringskwaliteit

MAPE-waarden zijn extreem groot in meerdere runs. Dat is inhoudelijk verklaarbaar:

- Doelvariabele `occupancy_rate` bevat veel (bijna-)nulwaarden.
- In holdout is `share_zero` ongeveer `5.2%` tot `5.4%`.

Gevolg:

- MAPE is hier instabiel en moeilijk interpreteerbaar als primaire metric.
- De keuze `MAE-first` met RMSE tie-break is methodologisch correct voor deze data-eigenschap.

## 7. Kritische beoordeling van modelselectie in Phase 4

### 7.1 Wat sterk is

- Selectieregels werden vooraf vastgelegd en nadien consequent toegepast.
- F4 is niet opportunistisch gekozen ondanks betere CV-MAE, vanwege expliciete retention-grens.
- Policy met en zonder `parking_id` is daadwerkelijk naast elkaar gerapporteerd.

### 7.2 Wat inhoudelijk kwetsbaar blijft

1. Forecast-keuze blijft contextafhankelijk.
- `F3` is sterk binnen lag-valid context, maar verliest op holdout-MAE tegen simpele baseline op volledige set.
- Zonder duidelijke operationele definitie van "voorspellingsscope" (alle uren vs lag-valid uren) kan dit fout geïnterpreteerd worden.

2. Policy-keuze vraagt expliciete framing in thesis.
- `P4` is niet foutmatig best.
- Keuze voor `P4` moet dus geframed worden als methodologische/beleidsmatige preferentie, niet als pure accuraatheidswinst.

3. Ex-ante eventclaim is voorzichtig, maar nog niet maximaal hard.
- "ex_ante_probable" is geen formele garantie.
- Voor sterk causale beleidsclaims blijft extern operationeel bewijs wenselijk.

## 8. Wat we met hoge, middelmatige en lage zekerheid kunnen claimen

### Hoge zekerheid

- Fold-safe evaluatie is cruciaal; fixed-export overschat vooral forecastprestaties.
- Trackscheiding policy/forecast is correct geïmplementeerd.
- L-features leveren duidelijke CV-meerwaarde binnen forecast.
- F4 is methodologisch terecht afgewezen door sample-retentiecriterium.

### Middelmatige zekerheid

- `F3` is een goede forecast-kandidaat voor lag-valide operationele settings.
- `P4` is een verdedigbare policy-kandidaat als ex-ante voorzichtigheid en interpretatie prioriteit krijgen.

### Lage zekerheid / nog open

- Dat `F3` universeel beter is dan eenvoudige persistence op alle operationele scenario's.
- Dat eventfeatures in productiecontext consequent ex-ante beschikbaar zijn zonder extra governance.
- Dat huidige policy-modellen voldoende beleidsgevoeligheid tonen buiten sterke statische profielen.

## 9. Aanbevolen vervolgstappen (academisch en operationeel)

1. Rapporteer duale forecast-evaluatie expliciet.
- Altijd apart: full-populatie en strict-lag-valid populatie.
- Voeg beslisregel toe voor wanneer welk model operationeel gebruikt wordt.

2. Maak policy-framing expliciet in methodesectie.
- Benoem dat `P4` gekozen is op methodologische robuustheid, niet op laagste MAE.
- Behoud `P0` als sterke benchmark in alle tabellen.

3. Versterk event-governance.
- Documenteer per eventbron of timing effectief vooraf gekend is in real-time planning.
- Converteer waar mogelijk `ex_ante_probable` naar harde operationele SLA-criteria.

4. Voeg foutdiagnostiek toe op piekmomenten.
- Apart analyseren van top-deciel occupancy-uren en extreme eventdagen.
- Dit is relevant omdat RMSE-verschillen suggereren dat foutenverdeling verschuift tussen modellen.

## 10. Eindconclusie

Phase 4 is methodologisch sterk uitgevoerd en levert een reproduceerbare, kritisch getoetste modelselectiebasis op.  
De belangrijkste winst is niet alleen modelperformantie, maar vooral de kwaliteitscontrole van de evaluatielogica: fold-safe boven fixed-export, expliciete trackscheiding, contractuele event-interpretatie en transparante ablaties.

De resultaten vragen tegelijk een genuanceerde lezing:

- in forecast is er duidelijke CV-winst door autoregressieve features, maar met sample-selectie en zonder automatische dominantie op holdout-MAE;
- in policy blijft de sterkste pure foutbenchmark een eenvoudige profielbaseline, waardoor keuze voor een striktere TSE-variant expliciet normatief en methodologisch gemotiveerd moet worden.

Daarmee is de fase academisch verdedigbaar afgerond, op voorwaarde dat deze nuance volledig wordt meegenomen in de thesis-rapportering en in de operationele vertaling van de modelkeuze.
