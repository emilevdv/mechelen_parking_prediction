# Phase 5 Protocol (Interpretatie SHAP + Per-Tier)

Datum: 2026-03-13

## Scope-lock
- Primaire interpretatiemodellen: `P4_ridge_a1_0` (policy) en `F3_rf_90_d12_l2` (forecast).
- Benchmarkcontrast: `P0_profile_baseline` en `F0_persistence_baseline`.
- Claimbasis: fold-stability + finale holdout-interpretatie 2025.
- Primair tier-niveau: centrum vs vesten/rand.

## Methodologische guardrails
1. Geen modelherselectie in Phase 5.
2. Geen hyperparametertuning in Phase 5.
3. Geen holdout-gebruik voor modelkeuze.
4. Policy/forecast trackscheiding blijft intact.
5. SHAP is verplicht voor primaire interpretatie.

## Dependency status
- shap beschikbaar: YES