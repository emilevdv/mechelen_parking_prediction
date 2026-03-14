Hieronder staat een **herschreven, geoptimaliseerde en uitgebreidere versie** voor je onderzoeksvoorstel, in een **academische maar heldere stijl**, met:
- **Onderzoeksvraag**
- **Deelvragen**
- **Hypothesen**
- **Relevantie van het onderzoek**
- **Methodologische flow**
- **Data en datamanipulatie**
- **Methoden en modellen**

---





# Onderzoeksvraag

Deze thesis zal onderzoeken in welke mate externe factoren de modellering van parkeerbezetting in off-street parkings in Mechelen kunnen verrijken, hoe die meerwaarde verschilt tussen centrum- en vesten-/randparkings, en in welke mate zulke modellen bruikbaar kunnen zijn als verkennende basis voor operationele en beleidsmatige scenarioanalyse rond parkeerspreiding.

De centrale focus zal dus niet uitsluitend liggen op het maximaliseren van voorspellingsnauwkeurigheid, maar op het combineren van drie doelstellingen:  
(1) nagaan of externe contextinformatie daadwerkelijk bijkomende informatiewaarde levert,  
(2) onderzoeken of die meerwaarde verschilt tussen parkeertiers met een verschillende ruimtelijke en beleidsmatige functie, en  
(3) beoordelen in welke mate een beleidsgevoeliger model, zonder afhankelijkheid van historische bezettingslags, bruikbaar kan zijn als verkennende basis voor scenario’s die een verschuiving van parkeergedrag van centrum- naar vesten- of randparkings kunnen ondersteunen.

Daarbij zal expliciet een onderscheid worden gemaakt tussen twee modelsporen. Enerzijds zal een **forecast-spoor** worden opgebouwd, waarin occupancy-lags worden toegelaten om de maximale voorspellende performantie te benaderen, onder meer vanuit operationele relevantie voor parkeerbeheerders. Anderzijds zal een **policy-spoor** worden uitgewerkt, waarin dergelijke lags bewust worden uitgesloten, zodat de rol van externe, interpreteerbare en potentieel beïnvloedbare factoren beter zichtbaar wordt voor beleidsmatige reflectie.

---

# Deelvragen

**RQ1.** In welke mate leveren externe factoren een bijkomende bijdrage aan de modellering van parkeerbezetting bovenop temporele en ruimtelijke structuur, en verschilt die bijdrage tussen centrum- en vesten-/randparkings?

**RQ2.** Welke externe factorengroepen blijken het meest informatief voor parkeerbezetting, en in welke mate verschillen hun relatieve bijdrage en dynamiek tussen de onderscheiden parkeertiers?

**RQ3.** In welke mate verschilt de bruikbaarheid van een forecast-model met occupancy-lags en een policy-model zonder occupancy-lags voor respectievelijk operationele voorspelling en beleidsgerichte scenarioanalyse?

**RQ4.** Hoe kunnen inzichten uit een lag-vrij policy-model worden vertaald naar verkennende scenario’s rond prijs- of andere spreidingsmaatregelen die de druk in centrumparkings helpen verminderen en het gebruik van vesten- of randparkings kunnen stimuleren?

---

# Hypothesen

Aangezien deze thesis deels exploratief van aard zal zijn, zullen de hypothesen niet worden opgevat als rigide verwachtingen die per se bevestigd moeten worden, maar als richtinggevende werkhypothesen die empirisch getoetst zullen worden.

**H1.** Modellen die externe factoren opnemen zullen parkeerbezetting beter modelleren dan modellen die uitsluitend op temporele en ruimtelijke basisstructuur steunen.

**H2.** De meerwaarde van externe factoren zal niet homogeen zijn, maar zal verschillen tussen centrum- en vesten-/randparkings.

**H3.** Event-, kalender- en weerinformatie zullen niet overal dezelfde informatiewaarde hebben, maar zullen per tier en context verschillend bijdragen aan de modellering van parkeerbezetting.

**H4.** Een forecast-model met occupancy-lags zal naar verwachting hogere voorspellingsprestaties leveren dan een policy-model zonder occupancy-lags, maar het policy-model zal inhoudelijk beter geschikt zijn om beleidsrelevante en interpreteerbare relaties zichtbaar te maken.

**H5.** Een lag-vrij policy-model zal voldoende signaal bevatten om verkennende scenarioanalyse rond parkeerspreiding mogelijk te maken, ook al zal het geen harde causale uitspraken toelaten.

**H6.** De analyse zal niet alleen inhoudelijke inzichten opleveren over parkeerbezetting, maar ook zichtbaar maken welke bijkomende data in toekomstig onderzoek nodig zullen zijn om sterkere beleids- of causaliteitsclaims te kunnen ondersteunen.

---

# Relevantie van het onderzoek

Dit onderzoek zal relevant zijn op zowel praktisch, inhoudelijk als methodologisch niveau.

Op **praktisch niveau** zal de thesis aansluiten bij de beleidscontext van Mechelen, waar een betere spreiding van parkeerdruk een relevante doelstelling vormt. In die context is het wenselijk dat automobilisten minder in centrumparkings en meer in vesten- of randparkings parkeren. Deze thesis zal niet pretenderen om het effect van concrete beleidsmaatregelen causaal te bewijzen, maar zal wel onderzoeken in welke mate voorspellende modellen, verrijkt met externe contextinformatie, kunnen helpen om verschillen in parkeerdruk beter te begrijpen en om verkennende scenario’s rond prijs- of andere spreidingsmaatregelen te onderbouwen.

Op **inhoudelijk niveau** zal de thesis bijdragen aan de literatuur over parkeerbezetting door expliciet aandacht te besteden aan heterogeniteit tussen parkeertiers. Veel bestaand werk richt zich in sterke mate op algemene voorspellingsnauwkeurigheid, terwijl minder duidelijk is of externe factoren overal dezelfde informatiewaarde hebben. Deze thesis zal daarom niet alleen onderzoeken óf externe data meerwaarde hebben, maar ook **waar**, **voor welke types parkings** en **onder welke contexten** die meerwaarde het duidelijkst naar voren komt.

Op **methodologisch niveau** zal het onderzoek expliciteren dat voorspellende bruikbaarheid en beleidsmatige bruikbaarheid niet noodzakelijk samenvallen. Door een forecast-spoor en een policy-spoor naast elkaar te plaatsen, zal de thesis zichtbaar maken dat sommige variabelen nuttig kunnen zijn voor pure voorspelling, maar minder relevant zijn wanneer de focus verschuift naar beïnvloedbare of beleidsmatig interpreteerbare factoren. Daarmee zal het onderzoek niet alleen modellen vergelijken, maar ook duidelijk maken welk type modelinformatie bruikbaar is voor operationeel beheer en welk type informatie eerder kan dienen als verkennende basis voor beleidsreflectie.

Ten slotte zal deze thesis ook relevant zijn omdat ze de **grenzen van de beschikbare data** expliciet zal meenemen. De bedoeling zal niet zijn om op basis van één casestudy definitieve uitspraken te doen, maar om op een systematische manier te tonen welke inzichten reeds mogelijk zijn, waar de beperkingen liggen, en welke bijkomende data of analysekaders in toekomstig onderzoek het meest waardevol zouden zijn.

---

# Methodologische flow

De methodologische opbouw van deze thesis zal verlopen in zes opeenvolgende fasen.

## Fase 1 — Probleemafbakening en data-integratie

In een eerste fase zal de onderzoeksvraag worden geconcretiseerd binnen de beleids- en operationele context van Mechelen. Tegelijk zullen de relevante databronnen worden verzameld, opgeschoond en geïntegreerd tot één analyseerbare dataset op het niveau van parking en tijdseenheid.

## Fase 2 — Exploratieve data-analyse

Vervolgens zal een uitgebreide exploratieve data-analyse worden uitgevoerd om patronen in parkeerbezetting zichtbaar te maken, met bijzondere aandacht voor:

- temporele structuur,
    
- verschillen tussen parkings en tiers,
    
- de aanwezigheid van event-, kalender- en weersinvloeden,
    
- datakwaliteit en ontbrekende waarden.
    

Deze fase zal dienen om te bepalen welke featurefamilies inhoudelijk en empirisch verantwoord zijn voor verdere modellering.

## Fase 3 — Feature engineering

In de derde fase zal de analyse worden vertaald naar een gestructureerde featurelaag. Daarbij zal een onderscheid worden gemaakt tussen:

- **time features**,
    
- **spatial/entity features**,
    
- **event- en kalenderfeatures**,
    
- **weerfeatures**,
    
- en, enkel voor het forecast-spoor, **autoregressieve lagfeatures**.
    

De feature engineering zal bewust twee sporen ondersteunen:

- een **forecast-spoor**, gericht op voorspellingskracht,
    
- en een **policy-spoor**, gericht op interpreteerbaarheid en beleidsrelevantie.
    

## Fase 4 — Modelling en evaluatie

In de vierde fase zullen verschillende modellen worden getraind en vergeleken. Eerst zal worden onderzocht in welke mate externe factoren bijkomende voorspellende waarde leveren bovenop een basis van temporele en ruimtelijke structuur. Daarna zal worden nagegaan in welke mate deze meerwaarde verschilt tussen tiers en tussen forecast- en policy-opzetten.

De evaluatie zal verlopen via een duidelijke temporele train/holdout-opzet, met rolling of blocked validatie binnen de trainingsperiode en een finale toets op een afgeschermde holdout.

## Fase 5 — Interpretatie

Na de selectie van de best presterende modellen zal de focus verschuiven naar interpretatie. Daarbij zal worden onderzocht:

- welke featuregroepen het belangrijkst zijn,
    
- hoe hun belang verschilt per tier,
    
- en welke relaties beleidsmatig het meest relevant of interessant lijken.
    

Deze interpretatiefase zal niet bedoeld zijn om causale claims te maken, maar om de richting van relevante mechanismen en mogelijke beleidshefbomen zichtbaar te maken.

## Fase 6 — Verkennende scenarioanalyse

In een laatste fase zal het best geschikte policy-model worden gebruikt als basis voor een verkennende scenarioanalyse. Daarbij zal worden nagegaan hoe prijs- of andere spreidingsmaatregelen conceptueel kunnen worden doorgedacht in relatie tot centrum- versus vesten-/randparkings. Deze fase zal uitdrukkelijk verkennend blijven en niet worden voorgesteld als causale evaluatie van reëel beleid.

---

# Data

De analyse zal steunen op een geïntegreerde dataset rond off-street parkings in Mechelen. De kern van de data zal bestaan uit bezettingsinformatie op tijdstip- en parkingniveau. Deze data zullen worden verrijkt met externe databronnen die inhoudelijk relevant worden geacht voor parkeerbezetting.

De voornaamste databronnen zullen bestaan uit:

- **bezettingsdata** van de betrokken parkings;
    
- **tijds- en kalenderinformatie**, zoals uur, weekdag, maand, vakantie- en feestdagindicatoren;
    
- **eventdata**, voor zover beschikbaar en voldoende betrouwbaar;
    
- **weerdata**, zoals temperatuur, neerslag, wind en andere relevante meteorologische kenmerken;
    
- **ruimtelijke of parking-specifieke metadata**, zoals parkingtype, capaciteit en tierindeling.
    

Tiers zullen daarbij niet louter als een technische categorisatie worden opgevat, maar als een combinatie van **ruimtelijke ligging** en **beleidsmatige functie**, waarbij centrumparkings en vesten-/randparkings een verschillende rol kunnen spelen binnen een bredere visie op parkeerspreiding.

---

# Datamanipulatie en featureconstructie

De ruwe data zullen worden opgeschoond, geharmoniseerd en omgezet naar een analyseerbaar featureschema.

De belangrijkste datamanipulaties zullen omvatten:

- het uniformeren van tijdstempels en analyse-eenheden;
    
- het controleren en verwerken van ontbrekende waarden;
    
- het koppelen van externe databronnen aan de bezettingsdata;
    
- het construeren van tijdsfeatures, zoals cyclische representaties van uur, weekdag en maand;
    
- het afleiden van kalender- en eventfeatures;
    
- het opbouwen van weerfeatures, inclusief eventuele niet-lineaire representaties indien inhoudelijk verantwoord;
    
- het coderen van spatial/entity-kenmerken;
    
- en, in het forecast-spoor, het opbouwen van strikt causale lagfeatures en rolling indicators.
    

De featureconstructie zal niet louter technisch gebeuren, maar zal expliciet gestuurd worden door de resultaten uit de exploratieve data-analyse. Features zullen dus enkel worden behouden wanneer ze inhoudelijk relevant, methodologisch verdedigbaar en bruikbaar zijn binnen het onderscheid tussen forecast en policy.

Bijzondere aandacht zal gaan naar leakage-preventie. Alle transformaties die fitting vereisen zullen uitsluitend op trainingsdata worden geleerd. Voor het policy-spoor zullen occupancy-lags bewust worden uitgesloten, omdat deze wel nuttig kunnen zijn voor operationele voorspelling, maar minder betekenisvol zijn voor beleidsvragen die gericht zijn op factoren die daadwerkelijk beïnvloedbaar zijn.

---

# Methoden en modellen

De empirische analyse zal bestaan uit een combinatie van beschrijvende, voorspellende en interpreteerbare modellering.

## 1. Basismodellen en vergelijkingslogica

De modellen zullen in eerste instantie worden opgebouwd volgens een oplopende informatiestructuur. Daarbij zal stapsgewijs worden vergeleken wat de bijdrage is van verschillende featuregroepen:

- modellen met enkel **temporele structuur**;
    
- modellen met **temporele + ruimtelijke** informatie;
    
- modellen met **temporele + ruimtelijke + externe factoren**;
    
- en, voor het forecast-spoor, modellen waarin ook **autoregressieve informatie** wordt toegevoegd.
    

Deze opbouw zal toelaten om de marginale meerwaarde van externe factoren systematisch te beoordelen.

## 2. Modelklassen

Er zal gebruik worden gemaakt van meerdere modeltypes, zodat zowel eenvoudige als meer flexibele relaties kunnen worden onderzocht. Afhankelijk van datakwaliteit, schaal en performantie zullen onder meer volgende modelklassen worden overwogen:

- lineaire of geregulariseerde regressiemodellen;
    
- boomgebaseerde modellen;
    
- eventueel ensemblemodellen, indien methodologisch verantwoord en praktisch haalbaar.
    

De bedoeling zal niet zijn om een zo breed mogelijk arsenaal aan algoritmes te testen, maar om een evenwicht te vinden tussen performantie, robuustheid en interpreteerbaarheid.

## 3. Forecast- en policy-spoor

De modellering zal expliciet twee sporen volgen.

In het **forecast-spoor** zullen historische bezettingslags worden opgenomen om de maximaal haalbare voorspellingsprestatie te benaderen. Dit spoor zal vooral relevant zijn vanuit operationeel oogpunt, bijvoorbeeld voor parkeerbeheerders die kortetermijninschattingen willen ondersteunen.

In het **policy-spoor** zullen dergelijke lags bewust worden uitgesloten. Hierdoor zal de aandacht verschuiven naar factoren zoals tijdsstructuur, ruimtelijke kenmerken, events, kalenderinformatie en weer. Dit spoor zal methodologisch beter aansluiten bij vragen rond beleidsrelevantie, omdat het sterker focust op factoren die observeerbaar, interpreteerbaar en ten minste in bredere zin beleidsmatig relevant kunnen zijn.

## 4. Evaluatie

De modellen zullen worden geëvalueerd via een temporeel consistente opzet, met een trainingsperiode en een volledig afgeschermde holdout-periode. Binnen de trainingsperiode zal gebruik worden gemaakt van rolling of blocked validatie om modelkeuzes te ondersteunen.

De prestaties zullen worden vergeleken op basis van standaardmaten voor regressie of voorspelling, en waar relevant ook uitgesplitst per tier. Op die manier zal niet alleen worden gekeken welk model gemiddeld het best presteert, maar ook of de prestaties en meerwaarde van externe factoren verschillen naargelang de ruimtelijke en beleidsmatige positie van de parking.

## 5. Interpretatie

De best geselecteerde modellen zullen vervolgens worden geïnterpreteerd met behulp van geschikte interpretatiemethoden, zoals feature importance-analyses en, waar zinvol, SHAP-gebaseerde interpretatie. Het doel zal daarbij zijn om te begrijpen welke factorengroepen het meest informatief zijn en hoe die informatiewaarde verschilt tussen tiers en contexten.

De interpretatie zal voorzichtig gebeuren. Resultaten zullen worden gelezen als aanwijzingen over voorspellend relevante patronen en beleidsmatig interessante richtingen, niet als hard bewijs van causale effecten.

## 6. Scenarioanalyse

Op basis van het best presterende policy-model zal ten slotte een verkennende scenarioanalyse worden opgezet. Daarbij zal worden nagegaan hoe prijs- of andere spreidingsmaatregelen conceptueel kunnen doorwerken in de richting van lagere centrumdruk en een hoger gebruik van vesten- of randparkings.

Deze analyse zal expliciet worden gepresenteerd als een verkennende toepassing van een policy-gevoelig model, en niet als een sluitende evaluatie van het werkelijke effect van toekomstig beleid.

---

# Korte samenvattende positionering

Samengevat zal deze thesis geen puur technische forecasting-oefening zijn, maar een beleidsgerichte case study die voorspellende modellering inzet om drie vragen te onderzoeken:  
(1) of externe factoren extra informatiewaarde leveren voor parkeerbezetting,  
(2) of die waarde verschilt tussen centrum- en vesten-/randparkings,  
en (3) of lag-vrije, beleidsgevoeliger modellen bruikbaar kunnen zijn als verkennende basis voor scenario’s rond parkeerspreiding in Mechelen.

---

Als je wilt, kan ik dit nu nog **strakker omzetten naar de stijl van een echt onderzoeksvoorstel**, dus minder uitleggerig en meer alsof het rechtstreeks in je document geplakt kan worden.