# Feature Shortlist nb07 — input voor nb08

_Automatisch gegenereerd door nb07 cel 12_

| Feature | Prioriteit | Encoding | Basis | Referentie |
|---|---|---|---|---|
| hour_sin + hour_cos | 🔴 HOOG | sin/cos(2π·hour/24) | Sterkste temporele predictor (nb05 cel 02) | Cerqueira et al. (2023) |
| weekday_sin + weekday_cos | 🔴 HOOG | sin/cos(2π·weekday/7) | Weekdag-variantie > 25% (nb05 cel 03) | Channamallu et al. (2024) |
| month_sin + month_cos | 🔴 HOOG | sin/cos(2π·month/12) — NIET month raw (H-E5) | H-E5: VIF probleem opgelost via cyclische decomp. | James et al. (2021); Cerqueira et al. (2023) |
| day_type_3 | 🔴 HOOG | One-hot: weekday / saturday / sunday_holiday | KW p<0.001 weekdag vs. weekend (nb05) | Zhang et al. (2024) |
| tier | 🔴 HOOG | Aparte modellen per tier OF one-hot | H-S3: intra > inter-tier correlatie (nb06 cel 06) | Yang et al. (2019) |
| parking_id | 🔴 HOOG | One-hot (10 parkings) of target encoding | H-S1/S2: sterke parking-heterogeniteit (nb06 cel 02) | Wang & Li (2024) |
| total_capacity | 🟡 MEDIUM | log(total_capacity) | Spearman ρ capaciteit × bezetting (nb06 cel 05) | Sun et al. (2023) |
| temp_c | 🟡 MEDIUM | Gestandaardiseerd + interactie temp_c × seizoen | H-E2: effect aanwezig | Balmer et al. (2021) |
| precip_mm | 🔴 HOOG | Bins droog/licht/matig/zwaar OF log(precip+1) | H-E1: niet-lineair → binning aanbevolen | Oz (2023); Correia et al. (2020) |
| wind_speed_ms | 🟡 MEDIUM | Drempel-dummy (>10 m/s) OF continu | H-E6: drempeleffect bevestigd bij 10 m/s | Böcker et al. (2013) |
| sun_duration_min | 🟢 LAAG | Gestandaardiseerd + interactie sun × zomer_dummy | H-E7: effect niet bevestigd | Oz (2023); Balmer et al. (2021) |
| is_national_holiday | 🟡 MEDIUM | Binair + interactie tier × is_national_holiday | H-E4: effect aanwezig | Zhang et al. (2024) |
| is_school_vacation | 🔴 HOOG | Binair + interactie tier × is_school_vacation | H-E8: centrum↓ vesten neutraal/↑ bevestigd | Zhang et al. (2024) |
| is_event_day + event_type_dummies | 🔴 HOOG | Apart voor football/festival/procession/kermis/carnaval | H-E3/H-S4: cascade-effect + tier-specifiek | Fokker et al. (2021) |
| tier × is_event_day (interactie) | 🔴 HOOG | tier-dummy × event-dummy product | H-S4 + H-E3: eventeffect groter voor centrum | Wang & Li (2024) |
| year_dummy | 🟡 MEDIUM | Ordinaal (2020=0, 2023=1, 2024=2) | Jaar-trend aanwezig (nb05 cel 03) | Niu et al. (2023) |
