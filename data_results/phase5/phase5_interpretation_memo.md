# Phase 5 Interpretation Memo (SHAP + Per-Tier)

Datum: 2026-03-13

## Scope and protocol adherence
- Primary models interpreted: `P4_ridge_a1_0` (policy) and `F3_rf_90_d12_l2` (forecast).
- Benchmarks for contrast: `P0_profile_baseline` and `F0_persistence_baseline`.
- Claim basis: fold-stability + holdout context.
- Tier scope: centrum vs vesten/rand (parking detail only as appendix-level context).

## Primary feature dominance (holdout SHAP)
- Policy P4 top features: t_season__zomer, s_parking_id__p_maarten, t_hour_cos, s_parking_id__p_hoogstraat, e_int_temp_x_season__zomer, e_n_concurrent_events_capped, t_hour_sin, s_parking_id__p_tinel, e_int_temp_x_season__lente, t_season__lente.
- Forecast F3 top features: l_occ_lag_1h, l_occ_lag_168h, l_occ_lag_24h, t_hour_sin, t_hour_cos, s_capacity_bucket__medium, l_occ_lag_delta_1h_24h, t_weekday_cos, e_sun_intensity_log1p, t_weekday_sin.

## Per-tier robustness
- F3_rf_90_d12_l2: significant tier-delta share = 79.3%.
- P4_ridge_a1_0: significant tier-delta share = 20.7%.

## Baseline contrast and critical interpretation
- Policy holdout MAE: P0=0.2064 vs P4=0.2169 (benchmark better=True).
- Forecast holdout MAE: F0=0.0635 vs F3=0.0650 (benchmark better=True).
- Therefore, thesis framing must distinguish predictive minimum-error claims from methodological/interpretability claims.

## Stability and claim strength policy
- Directional claims downgraded: False
- Hard tier claims restricted: True
- Trade-off paragraph required: True

## Strong conclusions
- Fold-safe interpretation workflow is reproducible and track-consistent.
- Feature importance structure is extractable for both tracks without changing Phase 4 model selection.
- Benchmark-vs-primary mismatch is explicit and must remain explicit in thesis reporting.

## Weaker / conditional conclusions
- Directionality of policy effects should be treated as associative where fold sign consistency is limited.
- Tier contrasts are only claimable as hard differences when CI and permutation test both support them.

## Required thesis wording implications
- Report prediction quality and interpretability as two non-identical objectives.
- Explicitly mention lag-valid context for forecast primary interpretation.
- Keep benchmark results visible in the same tables as primary interpretations.