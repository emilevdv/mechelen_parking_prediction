# Phase 4 Protocol (Definitief)

Datum: 2026-03-13

## Harde methodologische regels

1. `2025` blijft volledig locked holdout.
2. Strikte trackscheiding: `policy = T+S+E`, `forecast = T+S+E+L`.
3. Geen kwaliteitsflags of target-proxies als predictors.
4. Fold-safe CV is primair: alle `requires_fit=True` stappen per fold op fold-train fitten.
5. Fixed-export CV mag alleen als sensitivity-referentie, nooit als hoofdclaim.

## Evaluatie- en selectieregels

1. Primaire metric: MAE (tie-breakers: RMSE, daarna MAPE).
2. Rapportering verplicht: overall, per tier (centrum vs vesten/rand), event vs non-event.
3. Forecast rapporteert zowel full-set als strict lag-valid subsets.
4. Policy met en zonder `parking_id` wordt parallel gerapporteerd.

## Go/No-Go criteria

- Go: fold-safe runs + volledige ablaties + event-contract compleet.
- No-Go: modelkeuze op fixed-export zonder fold-safe hoofdresultaten.
- No-Go: policyrapportering enkel met `parking_id`.
