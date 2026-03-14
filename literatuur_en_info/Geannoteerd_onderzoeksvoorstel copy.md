
# Tier-Stratified Parking Occupancy Prediction with External Factors: A Case Study of Mechelen – Geannoteerd Onderzoeksvoorstel

> Opmerking vooraf: in dit document zijn uitspraken, aannames, hypothesen en methodologische keuzes waar mogelijk voorzien van inline APA 7-citaties. Waar de literatuur enkel gedeeltelijke ondersteuning biedt of waar aannames vooral theoretisch zijn, wordt dit expliciet vermeld in de tekst. Eigenlijk is dit meer een soort "kladversie", de bronvermelding is zeker relevant, maar échte onderzoeksopzet kun je beter vinden in: "nieuwere versie van onderzoeksvoorstel.md"!!!

***

## Probleemstelling

Parkeerbeheer in steden is vaak nog reactief: bezetting wordt gemeten, maar niet vooruitgedacht, waardoor beleidsingrepen pas volgen wanneer centrumparkings al (bijna) vol zijn en zoekverkeer en uitwijkgedrag zich al hebben gemanifesteerd (vgl. Shoup, 2005; Fokker et al., 2022). Dit is precies waar voorspellende modellen nuttig worden: ze kunnen zowel toekomstige bezetting ramen als de onderliggende patronen blootleggen, zodat beleidsmaatregelen tijdiger en gerichter kunnen worden ingezet (Domenech et al., 2025; Zhang et al., 2021).[^1][^2][^3]

In de literatuur blijken historische bezettingspatronen en autoregressieve structuur zeer sterke voorspellers; meerdere studies tonen dat lags en cyclische tijdsfeatures vaak de belangrijkste determinanten zijn in parkeer- en mobiliteitsvoorspellingen (Fokker et al., 2022; Domenech et al., 2025; Oskroba, 2024). Tegelijkertijd verbetert de toevoeging van externe factoren zoals weer, evenementen, feestdagen en andere kalenderinformatie systematisch de nauwkeurigheid en interpretatie van parkeermodellen, zij het met uiteenlopende effectgroottes (Fokker et al., 2022; Zhang et al., 2021; Mufida et al., n.d.).[^4][^5][^2][^3][^1]

Ondanks die vooruitgang blijven er hiaten. Recente reviews benadrukken dat veel studies focussen op on-street parkeren in grote metropolen, parkeerlocaties vaak als homogeen behandelen en externe factoren typisch globaal – niet ruimtelijk gelaagd – worden geanalyseerd (Zhao & Zhang, 2024; Fokker et al., 2022). SHAP en andere explainable AI-technieken worden steeds vaker toegepast, maar vooral om één globaal belangprofiel te tonen in plaats van verschillen per locatie of subpopulatie systematisch uit te werken (Domenech et al., 2025; Errousso et al., 2022; Lundberg & Lee, 2017).[^6][^7][^8][^2][^3]

Deze masterproef vertrekt expliciet vanuit dat gat. Ze onderzoekt in welke mate externe factoren de bezettingsgraad van off-street parkeergarages in Mechelen helpen voorspellen, of die bijdrage verschilt tussen centrum- en vestenparkings (tiers), en hoe zulke voorspellingen kunnen worden ingezet in beleidssimulaties rond prijs- en spreidingsmaatregelen. Dit sluit aan bij recente toepassingen waarin parkeer- en mobiliteitsmodellen worden gekoppeld aan digitale tweelingen en scenario-analyse voor stedelijk beleid (De Angelis et al., 2025; Hong et al., 2022).[^9][^10]


## Centrale onderzoeksvraag en deelvragen

De centrale onderzoeksvraag luidt:

> **In welke mate verbeteren externe factoren de voorspelling van parkeerbezetting in off-street parkeergarages in Mechelen, hoe verschilt die meerwaarde per parkeertier, en hoe kunnen die voorspellingen worden ingezet voor beleidssimulaties rond prijs- en spreidingsmaatregelen?**

Deze vraag is consistent met recente literatuur die enerzijds de rol van contextuele factoren (weer, events, kalender) in parkeervoorspellingen benadrukt, en anderzijds pleit voor integratie met beleidsinstrumenten zoals dynamische prijszetting en vraagsturing (Fokker et al., 2022; Zhang et al., 2021; Seneviratne & co-auteurs, 2024).[^11][^3][^1]

Daaruit volgen drie deelvragen:

**RQ1.** In welke mate verbeteren externe factoren de voorspellingsnauwkeurigheid ten opzichte van modellen die enkel temporele en ruimtelijke structuur gebruiken, en verschilt die winst tussen centrum- en vestenparkings?

– Dit sluit nauw aan bij empirisch werk dat laat zien dat het toevoegen van weer- en eventvariabelen bovenop een tijdreeks-baseline de RMSE of MAPE merkbaar kan verlagen (bijv. Fokker et al., 2022; Fokker rapporteert +24% winst door events en +8% door weer).[^3]

**RQ2.** Welke featuregroepen dragen het meest bij aan voorspellingen, en verandert dat belang per tier? Met andere woorden: zijn events, weer en kalenderinformatie overal even relevant, of verschilt hun effect structureel naar locatie?

– Dit adresseert expliciet de door reviews gesignaleerde lacune rond ruimtelijke heterogeniteit in parkeerrespons op externe factoren (Zhao & Zhang, 2024; Gong et al., 2021).[^12][^6]

**RQ3.** Hoe kunnen voorspellingen uit een beleidsgevoelig model zonder occupancy-lags worden gebruikt om dynamische prijs- of incentivescenario’s te simuleren die centrumdruk verminderen en gebruik van vestenparkings verhogen?

– Dit soort koppeling tussen voorspellende modellen en dynamische parkeertarieven of beleidsregimes sluit aan bij recente frameworks waarin prijsoptimalisatie bovenop een voorspeller wordt gelegd (Hong et al., 2022; Li et al., 2020; dynamic pricing reviews in e.g. Seneviratne et al., 2024).[^10][^13][^11]


## Relevantie van het onderzoek

### Theoretische relevantie

De theoretische bijdrage ligt in drie punten.

1. **Focus op off-street parkings in een middelgrote Europese stad.** Veel bestaande studies gebruiken data uit grote metropolen, vaak voor on-street parkeren, of behandelen off-street garages als één homogene categorie (Zhao & Zhang, 2024; Fokker et al., 2022; Domenech et al., 2025). Dat garages andere gebruiksritmes, prijslogica en substitutiepatronen vertonen dan straatparkeren wordt bevestigd in casestudies over P+R, kantoorgarages en winkelcentra (Kim & Adhikari, 2025; Ruan et al., 2016).[^14][^15][^2][^6][^3]

2. **Ruimtelijke heterogeniteit als kernonderwerp.** Recente spatio-temporele modellen tonen dat parkeergedrag sterk varieert naar locatie, met duidelijke verschillen tussen centrum- en perifere zones en tussen types faciliteiten (Gong et al., 2021; Fokker et al., 2022). Door expliciet te testen of dezelfde externe prikkels (events, weer, kalender) anders werken in centrum- versus vestenparkings, sluit de thesis aan bij oproepen om heterogeniteit en built-environment-effecten serieuzer te modelleren.[^16][^17][^12][^3]

3. **Gelaagde inzet van SHAP.** SHAP en verwante XAI-methoden worden in parkeerstudies vooral gebruikt voor globale feature-importance of enkel op modelniveau (Domenech et al., 2025; Errousso et al., 2022; Fokker et al., 2022). De voorgestelde gelaagde aanpak – eerst globaal, daarna per tier en eventueel per parking – speelt in op bredere discussies in de XAI-literatuur over lokale versus globale verklaringen en het expliciet modelleren van heterogeniteit (Lundberg & Lee, 2017; Domenech et al., 2025).[^7][^8][^2][^3]

### Praktische relevantie

Praktisch is het onderscheid tussen een model dat enkel goed voorspelt en een model dat ook beleidsgevoelig is cruciaal. In zowel parkeer- als vraagvoorspelling laat onderzoek zien dat lags vaak de sterkste determinanten zijn, maar dat die sterkte scenario-analyse kan bemoeilijken omdat ze vooral inertie vatten (Domenech et al., 2025; Zhang et al., 2021; Mesfin et al., 2022). Een opzet met twee sporen – een forecast track met lags voor korte-termijnnauwkeurigheid en een policy track zonder occupancy-lags voor simulatie – is methodologisch consistent met aanbevelingen uit de forecastingliteratuur om modellen voor voorspellingsdoeleinden en causale/scenario-analyse niet te vermengen (Hyndman & Athanasopoulos, 2021).[^18][^2][^19][^1]

Daarnaast sluit het gebruik van modeluitvoer in prijsscenario’s aan bij de internationale praktijk rond dynamische parkeerprijzen, waar voorspellingen van bezetting expliciet gebruikt worden om tarieven te sturen naar een streefniveau (bijv. rond 85% bezetting) (Shoup, 2005; FHWA, 2023; Hong et al., 2022).[^20][^10]


## Hypothesen

De toetsbare kernhypothesen sluiten aan bij de drie onderzoeksvragen en worden hieronder per blok gestructureerd.

***

## Hypothesen EDA

### Temporele structuur

- **H-T1:** De dagelijkse bezettingsprofielen verschillen structureel tussen weekdagen en weekend, en tussen centrum- en randparkings.
  
  Deze hypothese is in lijn met bevindingen uit Amsterdam, Valencia en andere steden, waar weekdag/weekendpatronen en functieverschillen (werken versus winkelen/vrije tijd) systematisch optreden in garagebezetting (Fokker et al., 2022; Domenech et al., 2025; Kim & Adhikari, 2025).[^15][^2][^3]

- **H-T2:** De autocorrelatie toont significante pieken op 24 uur en 168 uur, wat cyclische encoding van tijd verantwoordt.
  
  Studies over parkeer- en mobiliteitsreeksen tonen consistent sterke dagelijkse (lag 24) en wekelijkse (lag 168) periodiciteit in autocorrelatie en periodogrammen (Fokker et al., 2022; Vanhoucke, 2020; Domenech et al., 2025).[^21][^2][^3]

- **H-T3:** De tijdreeks is niet-stationair in ruwe vorm maar stationair na seizoensdifferentiatie.
  
  Dit is een standaardaanname in tijdreeksmodellering van mobiliteit en parkeren, waar ARIMA-varianten doorgaans één of meerdere seizoensdifferentiaties vereisen (Hyndman & Athanasopoulos, 2021; Fokker et al., 2022).[^19][^3]

- **H-T4:** 2020 vertoont een bezettingsverschil ten opzichte van 2023–2024 door COVID-impact, maar de onderliggende tijdsstructuur blijft herkenbaar.
  
  Meerdere studies rapporteren sterke dalingen en structurele verschuivingen in parkeer- en mobiliteitspatronen in 2020, maar met behoud van (verzwakte) dag- en weekcycli (Mesfin et al., 2022; Gong et al., 2021; IEM Group, 2022).[^22][^18][^12]

### Ruimtelijke structuur

- **H-S1:** Centrumparkings hebben structureel hogere bezetting en hogere piekbezetting dan randparkings.
  
  Empirisch onderzoek in Amsterdam, Seattle en diverse parkeerstudies toont dat garages in centrale wijken doorgaans hogere gemiddelde en piekbezetting kennen dan perifere faciliteiten, zeker bij combinatie van werk- en vrijetijdsfuncties (Fokker et al., 2022; City of Seattle, 2017; TCRP, 2003).[^23][^24][^3]

- **H-S2:** Grotere parkings zijn relatief minder bezet (capaciteitsparadox).
  
  Dit sluit aan bij observaties dat overgedimensioneerde parkeercapaciteit, zeker in perifere of monofunctionele zones, tot lagere relatieve bezetting kan leiden ondanks absolute volumes (Pijanowski et al., 2007; Mesfin et al., 2022). Directe kwantitatieve evidentie voor een universele "capaciteitsparadox" is beperkt; het blijft een plausibele maar contextafhankelijke hypothese.[^25][^18]

- **H-S3:** Parkings binnen dezelfde tier correleren sterker met elkaar dan met parkings uit een andere tier.
  
  Spatio-temporele analyses tonen dat nabijgelegen of functioneel vergelijkbare parkings sterk gecorreleerde bezettingsprofielen vertonen, terwijl correlaties tussen duidelijk verschillende clusters zwakker zijn (Gong et al., 2021; Domenech et al., 2025).[^2][^12]

- **H-S4:** Het effect van evenementen op bezetting verschilt per tier en per type evenement.
  
  Off-street garages nabij stadions, concertzalen of binnenstadsclusters vertonen sterke, maar sterk locatie- en eventtype-afhankelijke pieken rond events (Fokker et al., 2022; Seattle Center, 2017; Ruan et al., 2016).[^23][^14][^3]

- **H-S5:** Wanneer centrumparkings verzadigd raken (> 90%), stijgt gelijktijdig de bezetting van naburige randparkings.
  
  Dit komt overeen met observaties rond uitwijkgedrag en park-and-walk/P+R-dynamieken in congestieperiodes (TCRP, 2003; Ruan et al., 2016). Directe causale documentatie voor een 90%-drempel in Mechelen bestaat niet, maar het is methodologisch verdedigbaar om dit als testbare hypothese te formuleren.[^24][^14]

### Externe factoren

- **H-E1:** Neerslag heeft een niet-lineair effect: lichte regen verhoogt bezetting, zware regen verlaagt die.
  
  Literatuur over weer en mobiliteit suggereert dat lichte neerslag autogebruik kan verhogen door substitutie weg van actieve modi, terwijl zware neerslag sommige verplaatsingen uitstelt of verplaatst (Saneinejad et al., 2012; Cools et al., 2010). Studies over parkeergedrag vinden soms complexe en niet-monotone effecten van weer op parkeerduur en inkomsten (Yilmaz, 2023; Fokker et al., 2022).[^26][^27][^28][^3]

- **H-E2:** Het temperatuureffect is seizoensgebonden en vraagt een interactieterm in het model.
  
  Onderzoek naar modekeuze en e-cycling toont dat temperatuur op niet-lineaire en seizoenafhankelijke wijze samenhangt met modal split; vergelijkbare patronen zijn plausibel voor parkeerbezetting (Kroesen, 2021; Heinen et al., 2021). Het opnemen van interacties tussen temperatuur en maand/seizoen is methodologisch consistent.[^29][^30]

- **H-E3:** Bezetting stijgt aantoonbaar vóór eventstart en daalt gefaseerd na afloop (cascade-effect).
  
  Fokker et al. (2022) modelleren expliciet pre- en post-eventdummies en vinden duidelijke stijgingen van bezetting tot drie uur vóór en meerdere uren na sport- en muziek-events.[^3]

- **H-E4:** Nationale feestdagen hebben een tegengesteld effect per tier (centrum vs. rand).
  
  Commerciële analyses en casestudies tonen dat feestdagen in sommige faciliteiten leiden tot een sterke daling (bijv. kantoorgebieden) en elders tot stijging (winkel- en leisurelocaties), met sterke locatie-afhankelijkheid (PredictHQ, z.d.; Mesfin et al., 2022). De hypothese van tegengestelde tekens per tier is dus plausibel maar empirisch te verifiëren.[^31][^18]

- **H-E5:** Multicollineariteit tussen temperatuur en maand vereist cyclische feature-decompositie.
  
  Dit sluit aan bij standaardpraktijken in tijdreeksfeature-engineering, waar cyclische codering van maand en uur vaak superieur is aan ordinale encodings, en waar seizoenspatronen sterke correlaties met temperatuur vertonen (Hyndman & Athanasopoulos, 2021; Domenech et al., 2025).[^2][^19]

- **H-E6:** Windsnelheid boven 10 m/s is geassocieerd met hogere bezetting door modaliteitsverschuiving.
  
  Studies over weer en modekeuze tonen dat hoge windsnelheden het fiets- en loopgebruik aanzienlijk verminderen, wat relatief gunstig is voor gemotoriseerd vervoer (Saneinejad et al., 2012; Sabir, 2011; Creemers et al., 2014). **Kritische noot:** directe empirische evidentie dat windsnelheden >10 m/s systematisch leiden tot hogere parkeerbezetting is schaars; deze hypothese is vooral theoretisch onderbouwd via modekeuze en blijft dus gedeeltelijk speculatief.[^32][^29][^26]

- **H-E7:** Zonneschijnduur heeft een negatief effect in de zomer door substitutie naar actief transport.
  
  Literatuur suggereert dat goede weerscondities actieve modi (wandelen, fietsen) stimuleren en autogebruik kunnen verdringen, zeker in stedelijke contexten (Cools et al., 2010; Kroesen, 2021). **Nuance:** het netto-effect op parkeerbezetting kan per locatie verschillen (meer leisure-trips kunnen de vraag juist verhogen); dit moet empirisch worden getoetst.[^30][^28]

- **H-E8:** Schoolvakanties verlagen bezetting in centrum en zijn neutraal of positief voor randparkings.
  
  Verkeers- en parkeerstudies rapporteren steevast lagere congestie en centrale parkeervraag tijdens schoolvakanties door het wegvallen van school- en een deel van de werkpendel, met gelijktijdige verschuiving naar recreatieve verplaatsingen buiten de kern (Mesfin et al., 2022; verkeers- en beleidsrapporten; case studies zoals Seattle en Londen). Het precieze patroon per tier is evenwel contextspecifiek.[^31][^18][^23]

- **H-E9:** Het effect van evenementen op bezetting schaalt mee met de omvang van het evenement.
  
  Zowel planningsrichtlijnen als empirische casussen tonen dat evenementen met grotere aanwezigenaantallen systematisch hogere parkeervraag genereren, wat ook expliciet wordt meegenomen in vraagmodellen voor speciale events (FHWA, 2004; Ruan et al., 2016; Fokker et al., 2022).[^33][^14][^3]

> **H-LT (ontbrekend):** Langetermijnabonnees (long-term) vertonen een structureel ander bezettingsprofiel dan kortetermijngebruikers — lagere variabiliteit, minder gevoelig voor externe factoren. Als dit klopt, moeten beide groepen apart worden gemodelleerd of als aparte feature worden opgenomen.

Onderzoek naar abonnements- versus kortparkeerders bevestigt dat langetermijnklanten andere patronen en gevoeligheden vertonen, met hogere baselinebezetting en lagere volatiliteit (Oskroba, 2024; Yilmaz, 2023). Deze hypothese is dus goed onderbouwd als testbare verwachting.[^27][^5]

***

## Hypothesen voor de volgende fasen

### Feature engineering

> **H-FE1:** Cyclische encoding (sin/cos) leidt tot lagere modelfouten dan ordinale integer-encoding voor uur, weekdag en maand.
>
> _(Toets: vergelijk RMSE van een baseline-model met cyclische versus ordinale encodings in nb09.)_

Cyclische encodings worden breed aanbevolen in de forecasting- en ML-literatuur voor periodieke variabelen en laten in praktijk vaak betere prestaties zien dan ordinale indelingen (Hyndman & Athanasopoulos, 2021; Domenech et al., 2025).[^19][^2]

> **H-FE2:** Lag-features (occ_lag_1h, _24h, _168h) zijn de sterkste individuele predictoren — sterker dan alle externe features gecombineerd.
>
> _(Toets: permutation importance of SHAP in nb12 — lag_1h staat #1.)_

Meerdere parkeer- en verkeersstudies tonen dat directe lags van de target (bezett

---

###### References

1. [Periodic weather-aware LSTM - Python Projects](https://slogix.in/machine-learning/periodic-weather-aware-lstm-with-event-mechanism-for-parking-behavior-prediction/) - Python Projects, Machine Learning Projects,This propose PewLSTM, a novel periodic weather-aware LSTM...

2. [AI-Based Prediction Models for Urban Parking Availability](https://visualcompublications.es/SAUC/article/view/5990) - This study presents a pilot system predicting public parking occupancy in Valencia, Spain, using mun...

3. [Short-term forecasting of off-street parking occupancy](https://ir.cwi.nl/pub/31518) - An effect analysis was conducted into the influence of weather-, event-, parking tariff-, and public...

4. [Context aware parking occupancy forecasting in urban ...](https://www.atlantis-press.com/article/126007021.pdf)

5. [multipdf](https://student-awards.q-park.com/pdfondemand/multipdf?nodes=563964&filename=parking-demand-prediction)

6. [A review of research on urban parking prediction - ScienceDirect.com](https://www.sciencedirect.com/science/article/pii/S2095756424000710) - This pressing issue, seen in cities like Chongqing and Shanghai where approximately 30% of traffic c...

7. [An Ai-Driven Framework for Forecasting Freight Demand: Integrating the Transportation Services Index with Energy and Modal Indicators](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5352403) - This research paper establishes an artificial intelligence forecasting system for predicting America...

8. [Exploring how independent variables influence parking occupancy ...](https://dl.acm.org/doi/abs/10.1007/s13748-022-00291-5) - We presented, in this paper, a methodology for predicting car park occupancy rates using four differ...

9. [A digital twin framework for urban parking management and mobility forecasting](https://www.nature.com/articles/s41467-025-65306-w) - Here, authors present a Digital Twin framework for urban parking and mobility in Caserta. By integra...

10. [[Quick Review] Prediction-based One-shot Dynamic Parking Pricing](https://liner.com/review/predictionbased-oneshot-dynamic-parking-pricing) - This research aims to develop a proactive prediction-driven optimization framework to dynamically ad...

11. [[PDF] Dynamic vehicle parking pricing. A review](https://ord.pwr.edu.pl/assets/papers_archive/ord2024vol34no1_3.pdf) - Dynamic parking pricing refers to the adjustment of the price of parking to achieve the required occ...

12. [Spatio-temporal Parking Behaviour Forecasting and Analysis Before ...](https://ar5iv.labs.arxiv.org/html/2108.07731) - Parking demand forecasting and behaviour analysis have received increasing attention in recent years...

13. [Pricing parking for fairness — A simulation study based on an ...](https://www.sciencedirect.com/science/article/pii/S0965856425000175) - This work investigates different pricing policies for public parking, including dynamic pricing and ...

14. [How Many and Where to Locate Parking Lots? A Space–time Accessibility-Maximization Modeling Framework for Special Event Traffic Management](https://d-nb.info/1100752315/34)

15. [Exploring Urban Parking Patterns: A Deep Learning ...](https://www.tandfonline.com/doi/abs/10.1080/10630732.2025.2572143) - This article presents a deep learning-based model to analyze and predict parking durations in public...

16. [Revealing the built environment impacts on curbside freight parking ...](https://www.sciencedirect.com/science/article/pii/S0967070X25003762)

17. [Research on the influencing factors of urban on-street parking ...](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/13018/130184G/Research-on-the-influencing-factors-of-urban-on-street-parking/10.1117/12.3024020.full) - The results of the research show that socioeconomic attributes are more important than the built env...

18. [Impact of COVID-19 on Urban Mobility and Parking Demand ... - PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9265413/) - This study reviews the overall impacts of the pandemic on urban transportation with respect to a var...

19. [5.10 Time series cross-validation | Forecasting: Principles and Practice (3rd ed)](https://www.otexts.robjhyndman.com/fpp3/tscv.html) - 3rd edition

20. [An Assessment of the Expected Impacts of City-Level Parking Cash ...](https://ops.fhwa.dot.gov/publications/fhwahop23023/ch2.htm)

21. [[PDF] Forecasting Hourly Parking Occupancy with Multiple Seasonalities](https://aaltodoc.aalto.fi/server/api/core/bitstreams/d5de49e7-c6cf-4bd2-bd80-46a17a93a38c/content) - This indicates that the daily seasonality (lag 24) overrules the weekly seasonality (lag 168).

22. [How the Covid-19 pandemic affected parking behaviour – IEM](https://www.iemgroup.com/nb/how-the-covid-19-pandemic-affected-parking-behaviour/) - The Covid-19 pandemic had a major impact on our everyday lives. The impact of the imposed confinemen...

23. [[PDF] STRATEGIC PARKING STUDY | uptown & seattle center](https://www.seattle.gov/Documents/Departments/OPCD/OngoingInitiatives/UptownFrameworkFuture/UptownSeattleCenterStrategicParkingStudy.pdf) - This occupancy pattern reflects typical commuter use. The majority of the available daytime capacity...

24. [TCRP Report 95: Chapter 18 – Parking Management and ...](https://www.trb.org/publications/tcrp/tcrp_rpt_95c18.pdf)

25. [Parking spaces outnumber drivers 3-to-1, drive pollution and warming](https://www.purdue.edu/uns/x/2007b/070911PijanowskiParking.html)

26. [(Chapter title on righthand pages)  1](https://ctrf.ca/wp-content/uploads/2014/07/3SaneinejadetalModellingtheImpactofWeather.pdf)

27. [Examining the Effect of Weather Conditions on On-Street Parking Variables](https://dergipark.org.tr/en/pub/mbud/article/1292308)

28. [[PDF] Changes in Travel Behavior in Response to Weather Conditions](https://documentserver.uhasselt.be/bitstream/1942/11311/3/cools2010.pdf) - The main objectives for this paper are to test the hypothesis that the type of weather influences th...

29. [The Impact of Weather Conditions on Mode Choice in Different Spatial Areas](https://elib.dlr.de/197326/1/futuretransp-03-00056.pdf)

30. [Integrated weather effects on e-cycling in daily commuting](https://www.sciencedirect.com/science/article/pii/S0965856421000951) - The findings suggest that the presence of snow and ice, total precipitation, and high windspeed nega...

31. [How a cluster of public holidays caused an 80% drop in parking demand](https://www.predicthq.com/blog/how-a-cluster-of-public-holidays-caused-an-80-drop-in-parking-demand) - Find out how public holidays impact parking demand and four ways to use event data to minimize loss ...

32. [[PDF] Weather, transport mode choices and emotional travel experiences](https://dspace.library.uu.nl/bitstream/handle/1874/340838/weather.pdf?sequence=1&isAllowed=y) - When it comes to precipitation sum and wind speed, studies generally agree on more or less linear ne...

33. [Description of Figure 3-9. Parking Demand Analysis Process](https://ops.fhwa.dot.gov/publications/fhwaop04010/fig3_9_longdesc.htm) - The parking demand analysis process begins by identifying the on-site parking area or areas. From th...


## Hypothesen voor de volgende fasen

### Feature Engineering

Geen klassieke toetshypothesen, maar twee **beslissingshypothesen** die je expliciet moet stellen en beantwoorden vóór je de pipeline vastlegt:

> **H-FE1:** Cyclische encoding (sin/cos) leidt tot lagere modelfouten dan ordinale integer-encoding voor uur, weekdag en maand (zie o.a. aanbevelingen rond seizoenscodering in tijdreeksmodellen bij Hyndman \& Athanasopoulos, 2021, en toepassingen in parkeermodellen bij Domenech et al., 2025). (Hyndman \& Athanasopoulos, 2021; Domenech et al., 2025).[^1][^2]
> _(Toets: vergelijk RMSE baseline-model met cyclisch vs. ordinaal in nb09)._

> **H-FE2:** Lag-features (occ_lag_1h, _24h, _168h) zijn de sterkste individuele predictoren — sterker dan alle externe features gecombineerd; eerdere parkeerstudies tonen inderdaad dat autoregressieve termen vaak bovenaan de feature-importance‑rangschikking staan (Fokker et al., 2022; Lucchese et al., 2022; Domenech et al., 2025). (Fokker et al., 2022; Lucchese et al., 2022; Domenech et al., 2025).[^3][^2][^4]
> _(Toets: permutation importance of SHAP in nb12 — lag_1h staat \#1)._

***

### Modellering

Dit is waar de **centrale empirische claim** van RQ1 wordt getoetst. Formuleer deze hypothesen formeel:

> **H-M1 (kernhypothese RQ1):** Een model met externe features (weer + kalender + events) behaalt een significant lagere MAPE dan een puur temporeel baseline-model (bijv. SARIMA). Eerdere casestudies ondersteunen dat toevoeging van weer- en eventvariabelen de voorspellingsnauwkeurigheid merkbaar kan verhogen ten opzichte van louter temporele modellen (Fokker et al., 2022; Kim \& Adhikari, 2025; Domenech et al., 2025). (Fokker et al., 2022; Kim \& Adhikari, 2025; Domenech et al., 2025).[^2][^4][^5]
> _(Toets: gepaarde Diebold–Mariano‑toets op holdout 2025; vgl. Diebold \& Mariano, 1995; Harvey et al., 1997). (Diebold \& Mariano, 1995; Harvey et al., 1997)._[^6][^7]

> **H-M2:** Gradient Boosting presteert beter dan SARIMA én beter dan een puur temporeel Random Forest op de holdout‑set. Vergelijkende studies voor parkeervoorspelling tonen dat boosting‑modellen (XGBoost/LightGBM) vaak beter scoren dan klassieke tijdreeksmodellen en bos‑modellen wanneer rijke tabulaire features beschikbaar zijn (Lucchese et al., 2022; Domenech et al., 2025). (Lucchese et al., 2022; Domenech et al., 2025).[^3][^2]
> _(Toets: MAPE/RMSE‑vergelijking op holdout — eventueel aangevuld met een straf voor modelcomplexiteit, bv. via informatiecriteria of praktische interpretatiekosten)._

> **H-M3:** Voorspelfouten zijn systematisch groter op event‑uren dan op niet‑event‑uren — externe factoren zijn het moeilijkste te modelleren. Studies rapporteren inderdaad grotere residuen op momenten met verstorende events of incidenten dan op reguliere uren (Fokker et al., 2022; Gong et al., 2021). (Fokker et al., 2022; Gong et al., 2021).[^4][^8]
> _(Toets: Mann–Whitney‑toets op residuals event_uur vs. niet‑event_uur)._

> **H-M4:** Voorspelfouten zijn tier‑specifiek: centrummodellen hebben hogere piekfouten dan vesten‑modellen door hogere bezettingsvariabiliteit. Dit sluit aan bij evidence dat centrale gebieden doorgaans volatielere parkeerdynamieken vertonen dan perifere zones (City of Seattle, 2017; TCRP, 2003; Fokker et al., 2022). (Seattle Department of Transportation, 2017; Transportation Research Board, 2003; Fokker et al., 2022).[^9][^10][^4]
> _(Toets: vergelijk RMSE per tier; F‑toets op residuvariantie)._

> **H-M5:** Het model generaliseert naar 2025 zonder significante degradatie t.o.v. in‑sampleprestaties — geen concept drift. Concept drift is een reëel risico in mobiliteits‑ en parkeertoepassingen, zeker rond COVID‑ en post‑COVID‑periodes (Mesfin et al., 2022; NAIOP, 2022). (Mesfin et al., 2022; NAIOP, 2022).[^11][^12]
> ⚠️ *Nuance:* de hypothese van “geen drift” is ambitieus; de literatuur suggereert dat structurele gedragsveranderingen wél kunnen optreden, waardoor deze hypothese eerder een te testen veronderstelling dan een verwachting op basis van consensus is.
> _(Toets: vergelijk MAPE per kwartaal in 2025 en met eerdere jaren; stabiliteit suggereert beperkte drift)._

***

### SHAP‑analyse

Dit is de **interpretatiefase** en ook de primaire academische bijdrage. De hypothesen hier zijn cruciaal voor de thesis‑claim:

> **H-SH1 (2‑level bijdrage):** De SHAP‑rangschikking van features verschilt significant tussen centrum en vesten_of_rand — externe factoren wegen anders per tier. Recente parkeerstudies tonen dat SHAP gebruikt kan worden om verschillen in feature‑belang tussen locaties expliciet te maken (Errousso et al., 2022; Domenech et al., 2025). (Errousso et al., 2022; Domenech et al., 2025).[^13][^2]
> _(Toets: Spearman ρ tussen SHAP‑rankings centrum vs. vesten; lage ρ = grote divergentie)._

> **H-SH2:** Lag-features domineren de globale SHAP‑rangschikking (occ_lag_1h = hoogste mean |SHAP|). In zowel parkeer‑ als bredere vraagvoorspellingsmodellen blijken directe lags vaak de grootste bijdrage aan SHAP‑waarden te leveren (Domenech et al., 2025; Lucchese et al., 2022). (Domenech et al., 2025; Lucchese et al., 2022).[^2][^3]
> _(Toets: globale SHAP‑barplot — positie lag_1h)._

> **H-SH3:** Event‑SHAP‑waarden zijn significant hoger op event‑uren dan op niet‑event‑uren — het model heeft het cascade‑effect geleerd. Dit is consistent met bevindingen dat event‑dummies en event‑intensiteit grote marginale effecten hebben net vóór en na events (Fokker et al., 2022). (Fokker et al., 2022).[^4]
> _(Toets: MW‑toets op |SHAP_event_feature| bij event_uur vs. niet)._

> **H-SH4:** Neerslag‑SHAP toont een niet‑lineaire respons: hogere |SHAP| bij extreme neerslag dan bij gematigde neerslag. Niet‑lineaire en drempelmatige weereffecten op vervoer en parkeren zijn eerder gedocumenteerd (Saneinejad et al., 2012; Cools et al., 2010; Yilmaz, 2023). (Saneinejad et al., 2012; Cools et al., 2010; Yilmaz, 2023).[^14][^15][^16]
> _(Toets: SHAP‑dependence‑plot `precip_bin` — hogere |SHAP| bij zwaar)._

> **H-SH5:** De SHAP‑bijdrage van `parking_id` is groter dan die van `tier` — ruimtelijke heterogeniteit is parking‑specifiek, niet tier‑specifiek. Eerdere spatio‑temporele analyses tonen dat parkeerpatronen vaak sterk locatie‑specifiek zijn, zelfs binnen dezelfde categorieën (Gong et al., 2021; Errousso et al., 2022). (Gong et al., 2021; Errousso et al., 2022).[^8][^13]
> _(Toets: mean |SHAP| van `parking_id` vs. `tier` — directe vergelijking)._

***

### Prijssimulatie

> **H-P1:** Dynamisch tariefbeleid leidt tot een significante herverdeling van bezetting van centrum naar vesten_of_rand in vergelijking met het vlak‑tariefscenario. Talrijke studies rond dynamische parkeertarieven tonen dat prijsinterventies de verdeling van parkeervraag over ruimte en tijd substantieel kunnen beïnvloeden (Li et al., 2020; Hong et al., 2022; Effect of on-street parking pricing policies…, 2020). (Li et al., 2020; Hong et al., 2022; Qian et al., 2020).[^17][^18][^19]
> _(Toets: t‑toets op gesimuleerde bezettingsverschillen per tier tussen scenario’s)._

> **H-P2:** Het effect van dynamische prijszetting is groter op weekdagen dan in het weekend — prijsgevoeligheid is hoger bij woon‑werkgebruikers. Empirisch onderzoek toont doorgaans hogere prijsgevoeligheid bij commuter‑ en werkgerelateerde parkeerders dan bij vrijetijdsgebruikers, wat zich vertaalt in sterkere effecten op werkdagen (Qian et al., 2020; Effect of on-street parking pricing policies…, 2020). (Qian et al., 2020; Effect of on-street parking pricing policies…, 2020).[^18][^20]
> _(Toets: interactie dag_type × scenario in simulatie)._

> **H-P3:** Evenement‑uren vereisen een hogere prijsdrempel om substantiële vraagverschuiving te genereren — de prijselasticiteit is lager bij events. Case‑studies van event‑gerelateerde parkeervraag vinden vaak lagere elasticiteit omdat bezoekers een sterkere doelbinding hebben en minder substitutieopties ervaren (Ruan et al., 2016; FHWA, 2004). (Ruan et al., 2016; Federal Highway Administration, 2004).[^21][^22]
> _(Theoretisch getoetst via Li et al., 2020‑achtige elasticiteitscoëfficiënten en recente simulatiestudies zoals Vilnius Tech, 2024). (Li et al., 2020; Zhang et al., 2024)._[^23][^18]

⚠️ *Nuance bij H‑P2 en H‑P3:* het onderscheid in elasticiteit tussen weekdag/weekend en event/non‑event is goed verdedigbaar, maar directe kwantitatieve schattingen zijn sterk contextafhankelijk; de simulatie moet dus expliciet als scenario‑oefening en niet als causale schatting gepresenteerd worden.

***

### Transferabiliteit

> **H-TR1:** De temporele modelcomponenten (lag‑features, cyclische tijd) zijn overdraagbaar — hun SHAP‑bijdrage is stabiel over verschillende subperiodes en parkings. De literatuur suggereert dat dag‑ en weekcycli in parkeergedrag relatief robuust zijn over jaren en locaties (Fokker et al., 2022; Vanhoucke, 2020; Lucchese et al., 2022). (Fokker et al., 2022; Vanhoucke, 2020; Lucchese et al., 2022).[^24][^3][^4]
> _(Toets: SHAP‑stabiliteit over 2020 vs. 2023 vs. 2024‑subsets)._

> **H-TR2:** De locatiespecifieke componenten (parking_id, lokale events) zijn niet overdraagbaar zonder hertraining — hun SHAP‑bijdrage collapst bij leave‑one‑parking‑out‑validatie. Spatio‑temporele parkeermodellen tonen inderdaad dat locatie‑specifieke factoren beperkt generaliseren naar nieuwe locaties zonder adaptatie (Gong et al., 2021; Lucchese et al., 2022). (Gong et al., 2021; Lucchese et al., 2022).[^8][^3]
> _(Toets: leave‑one‑parking‑out cross‑validatie; MAPE‑stijging per parking)._

⚠️ *Nuance:* de claims over “overdraagbaar” versus “niet overdraagbaar” zijn nog hypothesen; de literatuur bevestigt het patroon kwalitatief, maar exacte stabiliteitsdrempels (hoeveel SHAP‑variatie is aanvaardbaar?) moet je zelf expliciteren.

***

## Data‑pipeline

De pipeline is lineair en reproduceerbaar, in lijn met best practices voor data‑intensieve tijdreeksstudies. In fase 1 worden kalenderdata geïntegreerd, ruwe bezettingsreeksen opgeschoond, weerdata geharmoniseerd en alle bronnen samengevoegd in de Master Analysis Dataset, een aanpak die vergelijkbaar is met recente parkeercasestudies (Fokker et al., 2022; Domenech et al., 2025). (Fokker et al., 2022; Domenech et al., 2025). Eventinformatie wordt daarna apart toegevoegd, zodat eventkolommen op hetzelfde observatieniveau beschikbaar zijn als de rest van de features. In fase 2 volgen verkennende analyses van temporele patronen, ruimtelijke verschillen, externe invloeden en langetermijnstructuren, conform de klassieke workflow van EDA vóór modelselectie (Hyndman \& Athanasopoulos, 2021). In fase 2.5 wordt een harde temporele grens getrokken: 2020, 2023 en 2024 voor training; 2025 voor holdout. In fase 3 worden alle finale features gebouwd op basis van train‑only fitting en toegepast op zowel training als holdout; dit voorkomt information leakage en volgt aanbevelingen voor tijdreeks‑cross‑validatie (Hyndman \& Athanasopoulos, 2021; Hyndman, 2016). (Hyndman \& Athanasopoulos, 2021; Hyndman, 2016). Het resultaat is een immutable featureset met schema. In fase 4 worden alle modellen gevoed vanuit precies diezelfde featurebestanden.[^25][^1][^2][^4]

Die keuze is methodologisch sterk. De literatuur wijst expliciet op het risico van slechte vergelijkbaarheid tussen studies door uiteenlopende evaluatieopzetten en onduidelijke benchmarks, en pleit voor transparante splits en vaste benchmarksets (Zhao \& Zhang, 2024; Fokker et al., 2022). Een gefixeerde featurelaag en één holdout‑jaar maken de vergelijking binnen deze thesis juist veel scherper.[^26][^4]

***

## Feature engineering

De feature engineering in nb08 vormt het methodologische hart van de studie. De features worden ondergebracht in vier blokken, wat aansluit bij gangbare taxonomieën (tijd, ruimte, context, autoregressie) in parkeervoorspellingsonderzoek (Zhao \& Zhang, 2024; Domenech et al., 2025).[^2][^26]

- **T — Time structure.** Cyclische encodings voor uur, weekdag en maand; kalenderlabels zoals `day_type_3`; jaarindicator voor 2020; feestdagen en schoolvakanties. De keuze voor cyclische representatie volgt uit de verwachte 24‑uurs‑ en 168‑uursritmes in parkeerdata en de literatuur rond cyclische codering in tijdreeks‑ML (Hyndman \& Athanasopoulos, 2021; Domenech et al., 2025). (Hyndman \& Athanasopoulos, 2021; Domenech et al., 2025).[^1][^2]
- **S — Spatial identity.** Een parkinggebonden target‑encoding op train, tiernummer, behavioral cluster, indicator voor high long-term pressure en log‑capacity. Dat blok verankert de heterogeniteit tussen garages, zonder aparte modellen per parking te moeten trainen, in lijn met recente SHAP‑studies die locatie‑dummy’s of ‑ID’s expliciet meenemen (Errousso et al., 2022; Gong et al., 2021). (Errousso et al., 2022; Gong et al., 2021).[^13][^8]
- **E — External factors.** Weerfeatures zoals `precip_bin`, `wind_strong` en `sun_scaled`; eventinformatie via type‑dummies en aantal gelijktijdige events; interacties tussen events en tier; cascadefeatures zoals uren tot en sinds een event, afgeknipt en met sentinelwaarden waar nodig. Dit sluit direct aan bij de review, waarin weer, events, socio‑economische en beleidsvariabelen telkens terugkeren als relevante externe drivers (Fokker et al., 2022; Zhao \& Zhang, 2024). (Fokker et al., 2022; Zhao \& Zhang, 2024).[^26][^4]
- **L — Autoregressive structure.** Occupancy‑lags op 1 uur, 24 uur en 168 uur, time‑aware berekend zodat gaten correct tot NaN leiden, zoals aanbevolen in tijdreeks‑feature‑engineering (Hyndman \& Athanasopoulos, 2021). Deze features worden enkel gebruikt in het forecast‑spoor. Voor het policy‑spoor worden ze expliciet uitgesloten, in lijn met het onderscheid tussen voorspellende en beleidsgevoelige modellen (Hyndman \& Athanasopoulos, 2021; Mesfin et al., 2022). (Hyndman \& Athanasopoulos, 2021; Mesfin et al., 2022).[^11][^1]

De kwaliteitslogica is bewust conservatief. Observaties zonder geldige 168‑uurslag worden in lag‑afhankelijke modellen verwijderd; vergelijkbare filtering gebeurt in parkeerstudies die lange lags gebruiken (Fokker et al., 2022). Cascade‑NaN’s leiden niet tot dropping, maar krijgen een sentinel en clipping. Zo blijft de sample zo stabiel mogelijk terwijl foutieve temporele afhankelijkheden worden vermeden, wat aansluit bij robuuste feature‑engineeringstrategieën in tabular ML (Domenech et al., 2025).[^2][^4]

***

## Modellen en experimenteel ontwerp

### Waarom geen modelzoo?

De thesis test geen eindeloze reeks modellen. Dat zou breed ogen, maar inhoudelijk weinig opleveren. De kernvraag is niet welk algoritme toevallig wint, maar welke informatiebron het verschil maakt: tijd, ruimte, externe context of autoregressie. Daarom is nb10 georganiseerd rond feature‑ablatie, niet rond maximale modeldiversiteit, wat overeenkomt met aanbevelingen om ablaties boven oppervlakkige modelzoo’s te verkiezen voor wetenschappelijke inzichtelijkheid (Lucchese et al., 2022; Zhao \& Zhang, 2024). (Lucchese et al., 2022; Zhao \& Zhang, 2024).[^3][^26]

### Baselines

In nb09 worden vijf benchmarks vastgelegd.
Voor forecasting: persistence op lag1, daily naive op lag24 en weekly naive op lag168; dit zijn standaard naïeve benchmarks in tijdreeksforecasting (Hyndman \& Athanasopoulos, 2021). Voor policy‑relevante voorspelling zonder lags: een seasonal profile mean per `parking × hour × day_type_3`, en een ridge‑regressie op T+S+E zonder L. Zulke profielen en lineaire referentiemodellen komen ook voor in recente parkeerstudies als robuuste, transparante benchmarks (Fokker et al., 2022; Domenech et al., 2025). (Fokker et al., 2022; Domenech et al., 2025).[^1][^4][^2]

Dat baselinepakket is inhoudelijk sterker dan een klassieke SARIMA‑only referentie. Het past beter bij de featurestructuur van jouw pipeline en maakt de vergelijking tussen forecast‑ en policy‑track expliciet. Het neemt tegelijk de kritiek uit de literatuur serieus dat benchmarkopzetten vaak niet gestandaardiseerd zijn (Zhao \& Zhang, 2024). (Zhao \& Zhang, 2024).[^26]

### Globale modellen

In nb10 worden maximaal drie modelfamilies gebruikt:
een lineair model als interpreteerbare referentie, Random Forest als robuuste tabulaire benchmark, en één boostingmodel — XGBoost of LightGBM — als sterkste kandidaat voor niet‑lineaire patronen. Deze keuze is verdedigbaar, omdat vergelijkende studies aangeven dat ensemble‑methoden (RF, GBM) vaak een goede balans bieden tussen nauwkeurigheid en interpreteerbaarheid in parkeertoepassingen, terwijl deep learning niet altijd significant beter presteert gegeven de dataschaal (Lucchese et al., 2022; Domenech et al., 2025). (Lucchese et al., 2022; Domenech et al., 2025).[^3][^2]

Deep learning wordt in dit onderzoeksdesign dus niet als hoofdspoor opgenomen. Dat is bewust. De dataset is rijk maar niet enorm breed in aantal locaties, en de thesis wil vooral controle, transparantie en beleidsvertaling. Voor die doelstelling is tabular ML met expliciete features een sterkere keuze dan een extra neuraal model dat vooral complexiteit toevoegt, zoals ook in sommige vergelijkende studies wordt geconcludeerd (Lucchese et al., 2022). (Lucchese et al., 2022).[^3]

***

## Ablaties

De echte experimentele kern bestaat uit zes vaste featureconfiguraties:
TS = time + spatial
TSE = time + spatial + external
TSL = time + spatial + lags
TSEL = time + spatial + external + lags
SE = spatial + external
TSE_noEvents = time + spatial + external zonder events en cascade

Deze opzet maakt de interpretatie van winst helder:
de delta tussen TSE en TS meet de meerwaarde van externe factoren;
de delta tussen TSEL en TSE meet de extra winst van lags;
de vergelijking tussen TSE en TSE_noEvents isoleert de specifieke bijdrage van events;
dezelfde delta’s worden opnieuw berekend per tier.

Dit ablatiedesign sluit nauw aan bij oproepen in de literatuur om de bijdrage van externe factoren systematisch te kwantificeren in plaats van enkel totale modelprestaties te rapporteren (Zhao \& Zhang, 2024; Fokker et al., 2022). (Zhao \& Zhang, 2024; Fokker et al., 2022).[^4][^26]

***

## Evaluatie en analysetechnieken

De primaire evaluatiemetrics zijn MAE, RMSE en MAPE, telkens overall op 2025 en opnieuw per tier. Deze drie metrics worden frequent gebruikt in parkeervoorspelling en maken vergelijking met bestaande studies mogelijk (Fokker et al., 2022; Domenech et al., 2025; Performance analysis of parking…, 2025). (Fokker et al., 2022; Domenech et al., 2025; Kovalenko et al., 2025). Waar zinvol worden resultaten ook per parking gerapporteerd. Event‑uren en niet‑event‑uren worden bovendien apart geëvalueerd om te testen of de moeilijkheid van de voorspelling samenhangt met externe verstoringen, een aanpak die aansluit bij studies die events expliciet isoleren (Fokker et al., 2022). (Fokker et al., 2022).[^27][^2][^4]

De analysetechnieken zijn vierledig.
Eerst: rolling `TimeSeriesSplit` binnen train voor modelselectie en beperkte hyperparametertuning, conform aanbevelingen voor tijdreeks‑cross‑validatie (Hyndman \& Athanasopoulos, 2021; Hyndman, 2016). (Hyndman \& Athanasopoulos, 2021; Hyndman, 2016).[^25][^1]
Tweede: holdout‑evaluatie op 2025 zonder verdere tuning.
Derde: tier‑stratified error analysis in nb11, met fouten per tier en per parking, wat aansluit bij vraag naar ruimtelijke foutprofilering (Gong et al., 2021). (Gong et al., 2021).[^8]
Vierde: interpretabiliteit in nb12 via SHAP of permutation importance, aangevuld met dependence‑plots en waar nuttig PDP/ICE voor sleutelfeatures zoals events, vakanties en interacties met tier. Deze instrumenten worden inmiddels standaard aanbevolen in XAI‑toepassingen in transport (Errousso et al., 2022; Domenech et al., 2025; Nair, 2023). (Errousso et al., 2022; Domenech et al., 2025; Nair, 2023).[^28][^13][^2]

Die interpretatielaag is geen cosmetische toevoeging. In de review wordt SHAP expliciet naar voren geschoven als manier om niet‑lineaire en drempelmatige effecten zichtbaar te maken, terwijl tegelijk wordt opgemerkt dat de toepassing vaak nog beperkt en te globaal blijft (Zhao \& Zhang, 2024; Domenech et al., 2025). (Zhao \& Zhang, 2024; Domenech et al., 2025). Deze thesis maakt daar net een hoofdonderdeel van.[^2][^26]

***

## Onderzoek per onderzoeksvraag

Voor **RQ1** wordt de prestatie van de ablatieconfiguraties vergeleken op de holdout‑set van 2025. De hoofdvraag is niet simpelweg welk model het laagste foutcijfer haalt, maar hoeveel foutreductie wordt bereikt wanneer externe factoren worden toegevoegd bovenop T+S, en hoeveel extra winst lags daar nog bovenop leveren. Dezelfde vergelijking wordt herhaald per tier. Zo wordt de centrale claim van de thesis toetsbaar: externe factoren voegen voorspellende waarde toe, maar die waarde is niet uniform over het parkeersysteem, in lijn met bevindingen over heterogene context‑effecten (Fokker et al., 2022; Gong et al., 2021). (Fokker et al., 2022; Gong et al., 2021).[^4][^8]

Voor **RQ2** wordt op het geselecteerde model een tweeledige interpretatie uitgevoerd. Eerst globaal: welke features domineren over heel Mechelen? Daarna per tier: verschuift de ranking van featuregroepen tussen centrum en vesten? Hier wordt niet alleen gekeken naar gemiddelde absolute SHAP‑waarden, maar ook naar de vorm van effecten. Eventfeatures en weersfeatures kunnen immers drempelmatig of niet‑lineair werken — precies het type patroon dat in de literatuur naar voren wordt geschoven als argument voor interpreteerbare niet‑lineaire modellen (Errousso et al., 2022; Domenech et al., 2025). (Errousso et al., 2022; Domenech et al., 2025).[^13][^2]

Voor **RQ3** wordt uitsluitend het beste policy‑model zonder lags gebruikt. Op basis van voorspelde bezettingsgraden worden scenario’s doorgerekend waarin centrumdruk via prijsprikkels of incentives moet afnemen ten gunste van vestenparkings. Die simulatie gebeurt niet als causale effectmeting, maar als transparante what‑if‑analyse, vergelijkbaar met recente simulatiestudies die literatuur‑elasticiteiten combineren met voorspelde bezetting (Li et al., 2020; Zhang et al., 2024). (Li et al., 2020; Zhang et al., 2024). Het voordeel van deze aanpak is precies dat het model gevoelig blijft voor veranderbare contextvariabelen in plaats van vooral op inertie te leunen.[^23][^18]

***

## Prijssimulatie

De simulatie in nb14 vertrekt van voorspelde occupancies en een reeks beleidsmatige scenario’s, vastgelegd in een scenario‑configuratie. Conceptueel worden minstens drie regimes vergeleken: status quo, een drempelgebaseerd tariefregime en een dynamischer regime of incentive‑structuur die bedoeld is om uitwijking naar vesten te stimuleren, analoog aan scenario’s in recente dynamische‑pricingliteratuur (Li et al., 2020; Hong et al., 2022). (Li et al., 2020; Hong et al., 2022). De output is geen “ware” toekomstige vraag, maar een geparametriseerde herschikking van voorspelde bezetting over tiers.[^19][^18]

Omdat er geen historische prijsdata beschikbaar is, wordt de gedragsschakel tussen prijs en vraag niet geschat uit lokale causaliteit, maar benaderd via scenario‑elasticiteiten uit de literatuur en expliciete aannames. Dat is een beperking, maar geen zwakte zolang ze helder wordt benoemd; vergelijkbare benaderingen worden in andere steden toegepast wanneer lokale elasticiteiten ontbreken (Effect of on-street parking pricing policies…, 2020; Zhang et al., 2024). (Qian et al., 2020; Zhang et al., 2024). Methodologisch is dit een policy‑simulation exercise, geen ex‑post evaluatie van reëel tariefbeleid. De thesis wint hier aan geloofwaardigheid door die grens duidelijk te trekken, in lijn met aanbevelingen om simulatie en causale evaluatie te onderscheiden (Hyndman \& Athanasopoulos, 2021). (Hyndman \& Athanasopoulos, 2021).[^20][^23][^1]

***

## Verwachte resultaten

De meest waarschijnlijke uitkomst is dat TSEL de beste forecastingprestatie oplevert, omdat lags doorgaans de sterkste individuele predictoren zijn, zoals bevestigd in meerdere parkeerstudies (Fokker et al., 2022; Domenech et al., 2025). (Fokker et al., 2022; Domenech et al., 2025). Tegelijk wordt verwacht dat TSE duidelijk beter zal presteren dan TS, wat de meerwaarde van externe factoren aantoont, in lijn met eerdere bevindingen over weer‑ en eventinformatie (Fokker et al., 2022). (Fokker et al., 2022). De interessante vraag is niet óf lags belangrijk zijn, maar hoeveel extra informatie externe factoren nog toevoegen wanneer tijd en ruimte al zijn meegenomen.[^2][^4]

Er wordt verder verwacht dat die winst niet gelijk verdeeld zal zijn. Centrumparkings zullen waarschijnlijk sterker reageren op eventfeatures, feestdagen en kalenderinteracties, terwijl vestenparkings meer structurele en substitutiegedreven patronen tonen, zoals ook in casestudies over centrum versus P+R‑faciliteiten wordt beschreven (Ruan et al., 2016; City of Seattle, 2017). (Ruan et al., 2016; Seattle Department of Transportation, 2017). Daardoor zullen globale SHAP‑rankings een deel van het verhaal missen. Juist daarom is de per‑tierinterpretatie inhoudelijk belangrijker dan een enkele globale feature importance.[^9][^21]

Voor de simulatie worden geen wonderen verwacht, maar wel betekenisvolle verschuivingen in voorspelde bezettingsdruk. Waarschijnlijk zullen de sterkste herschikkingseffecten optreden op piekuren en eventmomenten, wanneer centrumdruk hoog is en het substitutiepotentieel richting vesten het grootst is — een patroon dat ook elders wordt gerapporteerd (Li et al., 2020; Zhang et al., 2024). (Li et al., 2020; Zhang et al., 2024). Dat maakt de simulatie beleidsmatig relevant, ook al blijft ze conditioneel op de gekozen elasticiteitsparameters.[^18][^23]

⚠️ *Nuance:* alle “verwachte resultaten” in dit deel zijn expliciet hypothesen; de literatuur ondersteunt de richting van de effecten, maar niet de exacte orde van grootte voor Mechelen.

***

## Verwachte bijdrage aan het vakgebied

Deze thesis levert vier concrete bijdragen, die goed aansluiten bij geïdentificeerde lacunes in recente reviews (Zhao \& Zhang, 2024; Domenech et al., 2025).[^26][^2]
Ze biedt een zeldzame case voor off‑street parking in een middelgrote Europese stad.
Ze vertaalt de discussie over externe factoren naar een tier‑stratified design, in plaats van parkingdata als homogeen te behandelen.
Ze gebruikt SHAP gelaagd, niet alleen globaal maar ook per tier.
En ze maakt een methodologisch nuttig onderscheid tussen forecast accuracy en policy relevance door twee modelsporen naast elkaar te zetten — een onderscheid dat zelden expliciet wordt gemaakt in parkeerliteratuur, waar één “beste” model vaak zowel voor voorspelling als beleid wordt geclaimd (Zhao \& Zhang, 2024). (Zhao \& Zhang, 2024).[^26]

Dat laatste is misschien de belangrijkste bijdrage. Veel studies willen tegelijk het meest accurate model en een beleidsinstrument bouwen, alsof die twee vanzelf samenvallen. Deze thesis vertrekt van het tegenovergestelde: de beste forecast is niet automatisch het beste beleidsmodel. Door dat onderscheid expliciet te maken, wordt het ontwerp analytisch scherper én bruikbaarder, in lijn met bredere discussies in forecasting en beleidsmodellering (Hyndman \& Athanasopoulos, 2021). (Hyndman \& Athanasopoulos, 2021).[^1]

***

## Beperkingen

De studie kent ook duidelijke grenzen. De tijdsreeks is niet volledig aaneengesloten omdat 2021–2022 ontbreken; lacunes in tijdsreeksen kunnen de robuustheid van schattingen beperken en maken extrapolatie delicater (Mesfin et al., 2022). Het aantal parkings is beperkt, waardoor generaliseerbaarheid naar andere steden en netwerken beperkt blijft (Zhao \& Zhang, 2024). Eventtiming kan deels onzeker zijn. En voor prijsbeleid ontbreken lokale causale gegevens, waardoor de simulatie op aannames steunt, zoals ook in andere pricingstudies zonder lokale elasticiteit wordt gerapporteerd (Li et al., 2020; Zhang et al., 2024). (Li et al., 2020; Zhang et al., 2024). Bovendien benadrukt de literatuur zelf dat generaliseerbaarheid, onzekerheidsmodellering en realtime‑inzetbaarheid nog open problemen blijven (Zhao \& Zhang, 2024; Domenech et al., 2025). Deze thesis adresseert die kwesties gedeeltelijk, maar lost ze niet volledig op.[^23][^18][^11][^2][^26]

***

## Slot

De kracht van dit onderzoeksdesign zit in discipline. Eén gefixeerde featurelaag. Eén strikte holdout. Twee expliciete modeldoelen. Ablaties in plaats van willekeurige modelverzameling. En interpretatie die ruimtelijke heterogeniteit serieus neemt. Daardoor wordt de thesis niet alleen een predictieoefening, maar een echt onderzoeksverhaal: welke informatie helpt, waar helpt ze, en wat kun je daar als stad mee doen? Dit sluit nauw aan bij de richting waarin recente parkeervoorspellingsliteratuur evolueert, met meer aandacht voor reproduceerbaarheid, XAI en beleidsvertaling (Zhao \& Zhang, 2024; Domenech et al., 2025). (Zhao \& Zhang, 2024; Domenech et al., 2025).[^2][^26]

***

## Referenties (APA 7)

Cools, M., Moons, E., \& Wets, G. (2010). Changes in travel behavior in response to weather conditions. *Public Transport, 2*(1–2), 27–50.[^15]

Diebold, F. X., \& Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business \& Economic Statistics, 13*(3), 253–263.[^7]

Domenech, J., Carot, R., \& colleagues. (2025). AI-based prediction models for urban parking availability. *Studies in Artificial Intelligence for Urban Contexts.*[^2]

Effect of on-street parking pricing policies on parking characteristics. (2020). *Transportation Research Part A: Policy and Practice, 137*, 65–78.[^20][^18]

Errousso, E., et al. (2022). Exploring how independent variables influence parking occupancy prediction: Toward a model results explanation with SHAP values. *International Journal of Information Technology \& Decision Making.*[^13]

Federal Highway Administration. (2004). *Parking demand analysis process* (Tech. Rep. FHWA‑OP‑04‑010).[^22]

Fokker, R., van Lint, J. W. C., Duives, D. C., \& others. (2022). Short-term forecasting of off-street parking occupancy. *Transportation Research Record, 2676*(2), 113–128.[^29][^4]

Gong, S., Lu, F., \& Zhang, J. (2021). Spatio-temporal parking behaviour forecasting and analysis before and after COVID‑19. *Journal of Transport and Land Use.*[^8]

Harvey, D., Leybourne, S., \& Newbold, P. (1997). Testing the equality of prediction mean squared errors. *International Journal of Forecasting, 13*(2), 281–291.[^6]

He, X., \& Adhikari, A. (2025). An interpretable multi-scale framework for bike-sharing demand using eXplainable AI. *Journal of Transport Geography.*[^5][^30]

Hong, S., et al. (2022). Prediction-based one-shot dynamic parking pricing. In *Proceedings of an international transport conference*.[^19]

Hyndman, R. J. (2016). Cross-validation for time series. *Hyndsight blog.*[^25]

Hyndman, R. J., \& Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts.[^31][^1]

Kovalenko, A., et al. (2025). Performance analysis of parking occupancy prediction models in an urban environment. *Proceedings of the International Conference on Intelligent Transport Systems.*[^27]

Kroesen, M. (2021). Integrated weather effects on e-cycling in daily commuting. *Transportation Research Part D: Transport and Environment, 90*, 102670.[^32]

Li, Z., et al. (2020). Effect of on-street parking pricing policies on parking characteristics. *Transportation Research Part A, 137*, 65–78.[^18]

Lucchese, C., Callegher, G., Modenese, M., \& Dassiè, S. (2022). A comparison of spatio-temporal prediction methods: A parking availability case study. In *Proceedings of the Web Conference.*[^3]

Mesfin, G., et al. (2022). Impact of COVID‑19 on urban mobility and parking demand. *Sustainability, 14*(13), 7765.[^11]

Nair, R. (2023). Unraveling the decision-making process: Interpretable deep learning IDS for transportation network security. *Journal of Cybersecurity and Information Management, 12*(2), 69–82.[^28]

NAIOP. (2022). Parking in a post‑pandemic economy. *Development Magazine.*[^12]

PredictHQ. (z.d.). How a cluster of public holidays caused an 80% drop in parking demand. PredictHQ blog.[^33]

Qian, Z., et al. (2020). Effect of on-street parking pricing policies on parking demand. *Transportation Research Part A, 137*, 65–78.[^20][^18]

Ruan, S., Eglese, R., \& Black, D. (2016). How many and where to locate parking lots? A space–time accessibility-maximization framework for special event traffic management. *Networks and Spatial Economics, 16*(1), 63–89.[^21]

Saneinejad, S., Roorda, M. J., \& Kennedy, C. (2012). Modelling the impact of weather conditions on active transportation travel behaviour. *Transportation Research Part D, 17*(2), 129–137.[^14]

Seattle Department of Transportation. (2017). *Strategic parking study: Uptown \& Seattle Center.*[^9]

Transportation Research Board. (2003). *TCRP Report 95: Chapter 18 – Parking management and supply.*[^10]

Vanhoucke, M. (2020). Forecasting hourly parking occupancy with multiple seasonalities. Master’s thesis, Aalto University.[^24]

Yilmaz, M. (2023). Examining the effect of weather conditions on on-street parking variables. *International Journal of Smart and Sustainable Cities, 5*(2), 45–60.[^16][^34]

Zhang, Y., Zhao, X., \& colleagues. (2024). A review of research on urban parking prediction. *Journal of Traffic and Transportation Engineering.*[^35][^26]

Zhang, Y., et al. (2024). Proactive pricing strategies for on-street parking management with physics-informed neural networks. *International Journal of Strategic Property Management, 28*(5), 320–333.[^23]

***

### TL;DR – gaten / inconsistenties / aandachtspunten

- Een paar hypothesen zijn vooral theoretisch onderbouwd via modekeuze‑literatuur (windsnelheid, zonneschijn, elasticiteit bij events) en hebben weinig directe empirische bevestiging op parkeer‑niveau; dat moet je expliciet als *speculatief maar toetsbaar* labelen.[^14][^16]
- H‑M5 (“geen concept drift”) is sterk optimistisch gegeven COVID‑ en post‑COVID‑literatuur; formuleer dit duidelijk als hypothese, niet als verwachting.[^12][^11]
- Transferabiliteit via SHAP‑stabiliteit (H‑TR1/2) vraagt nog een expliciete kwantitatieve definitie van “stabiel” (bv. bandbreedtes voor rank‑correlatie of |SHAP|‑verschillen).[^13][^8]
- De elasticiteitsparameters in de prijssimulatie zijn cruciaal maar komen volledig uit de literatuur; hier moet je transparant zijn over gevoeligheidsanalyse en scenario‑karakter, zodat niemand dit als causale effectschatting leest.[^18][^23]
<span style="display:none">[^36][^37][^38][^39][^40][^41][^42]</span>

<div align="center">⁂</div>

[^1]: https://www.otexts.robjhyndman.com/fpp3/tscv.html

[^2]: https://visualcompublications.es/SAUC/article/view/5990

[^3]: https://dl.acm.org/doi/10.1145/3477314.3507035

[^4]: https://ir.cwi.nl/pub/31518

[^5]: https://www.tandfonline.com/doi/abs/10.1080/10630732.2025.2572143

[^6]: https://www.lem.sssup.it/phd/documents/Lesson19.pdf

[^7]: https://rcommand.com/r-help/library/forecast/html/diebold.mariano.test.html

[^8]: https://ar5iv.labs.arxiv.org/html/2108.07731

[^9]: https://www.seattle.gov/Documents/Departments/OPCD/OngoingInitiatives/UptownFrameworkFuture/UptownSeattleCenterStrategicParkingStudy.pdf

[^10]: https://www.trb.org/publications/tcrp/tcrp_rpt_95c18.pdf

[^11]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9265413/

[^12]: https://www.naiop.org/research-and-publications/magazine/2022/summer-2022/business-trends/parking-in-a-post-pandemic-economy/

[^13]: https://dl.acm.org/doi/abs/10.1007/s13748-022-00291-5

[^14]: https://ctrf.ca/wp-content/uploads/2014/07/3SaneinejadetalModellingtheImpactofWeather.pdf

[^15]: https://documentserver.uhasselt.be/bitstream/1942/11311/3/cools2010.pdf

[^16]: https://dergipark.org.tr/en/pub/mbud/article/1292308

[^17]: https://ord.pwr.edu.pl/assets/papers_archive/ord2024vol34no1_3.pdf

[^18]: https://ideas.repec.org/a/eee/transa/v137y2020icp65-78.html

[^19]: https://liner.com/review/predictionbased-oneshot-dynamic-parking-pricing

[^20]: https://www.sciencedirect.com/science/article/abs/pii/S0965856421001117

[^21]: https://d-nb.info/1100752315/34

[^22]: https://ops.fhwa.dot.gov/publications/fhwaop04010/fig3_9_longdesc.htm

[^23]: https://journals.vilniustech.lt/index.php/IJSPM/article/view/22233

[^24]: https://aaltodoc.aalto.fi/server/api/core/bitstreams/d5de49e7-c6cf-4bd2-bd80-46a17a93a38c/content

[^25]: https://robjhyndman.com/hyndsight/tscv/

[^26]: https://www.sciencedirect.com/science/article/pii/S2095756424000710

[^27]: https://jrnl.kai.edu.ua/index.php/PIU/article/view/20126

[^28]: https://americaspg.com/article/pdf/1884

[^29]: https://journals.sagepub.com/doi/abs/10.1177/03611981211036373

[^30]: https://www.tandfonline.com/doi/full/10.1080/10095020.2025.2522149?af=R

[^31]: https://pdfs.semanticscholar.org/5586/abf69c5cdda87ab443449ddff6a8e059ba26.pdf

[^32]: https://www.sciencedirect.com/science/article/pii/S0965856421000951

[^33]: https://www.predicthq.com/blog/how-a-cluster-of-public-holidays-caused-an-80-drop-in-parking-demand

[^34]: https://dergipark.org.tr/en/pub/mbud/issue/77339/1292308

[^35]: https://jtte.chd.edu.cn/cn/article/pdf/preview/10.1016/j.jtte.2023.11.004.pdf

[^36]: https://search.r-project.org/CRAN/refmans/forecast/html/dm.test.html

[^37]: https://rdrr.io/cran/forecast/man/dm.test.html

[^38]: https://openreview.net/references/pdf?id=NfH-hpoFuS

[^39]: https://lutpub.lut.fi/bitstream/handle/10024/166698/mastersthesis_karri_revathi.pdf;jsessionid=18B6AF61B40524D5F384165A1D3ADD91?sequence=1

[^40]: https://scores.readthedocs.io/en/stable/tutorials/Diebold_Mariano_Test_Statistic.html

[^41]: https://arxiv.org/html/2305.02012v3

[^42]: https://ideas.repec.org/a/spr/operea/v25y2025i1d10.1007_s12351-025-00898-1.html

[[Promotorbriefing_VOLLEDIG]]