# Phase 4 Model Selection Memo

Datum: 2026-03-13

## Finale feature sets
- Policy track: T+S+E (met expliciete vergelijking P2/P3/P4).
- Forecast track: T+S+E+L (met lag-valid sensitivities).

## Fold-safe CV (primary)
- forecast: best `F4_rf_90_d12_l2` met MAE=0.0605, RMSE=0.0879, MAPE=41188.604.
- policy: best `P0_profile_baseline` met MAE=0.2072, RMSE=0.2622, MAPE=252497.864.

## Fixed-export sensitivity (reference only)
- forecast: best `F4_rf_90_d12_l2` met MAE=0.0453, RMSE=0.0684, MAPE=37328.083.
- policy: best `P0_profile_baseline` met MAE=0.2072, RMSE=0.2622, MAPE=252497.864.

## Holdout 2025 resultaten
- forecast F0_persistence_baseline: MAE=0.0635, RMSE=0.1114, MAPE=43069.543, n=87600.
- forecast F3_rf_90_d12_l2 (selected): MAE=0.0650, RMSE=0.0995, MAPE=218074.298, n=78017.
- forecast F2_rf_90_d12_l2: MAE=0.0725, RMSE=0.1162, MAPE=207200.992, n=87600.
- forecast F1_xgb_80_d4_lr006: MAE=0.2584, RMSE=0.3197, MAPE=2140669.734, n=87600.
- policy P0_profile_baseline: MAE=0.2064, RMSE=0.2563, MAPE=753126.287, n=87600.
- policy P4_ridge_a1_0 (selected): MAE=0.2169, RMSE=0.2657, MAPE=883126.177, n=87600.
- policy P3_xgb_80_d4_lr006: MAE=0.2169, RMSE=0.2681, MAPE=1010900.673, n=87600.
- policy P2_xgb_80_d4_lr006: MAE=0.2197, RMSE=0.2694, MAPE=1071823.068, n=87600.

## DM-test (optioneel)
- policy: `P0_profile_baseline` vs `P4_ridge_a1_0` -> DM=-17.4471, p=0.0000, n=87600.
- forecast: `F0_persistence_baseline` vs `F3_rf_90_d12_l2` -> DM=-10.6421, p=0.0000, n=78017.

## Go / No-Go checks
- pre_run_audit_pass: PASS
- fold_safety_log_complete: PASS
- all_variants_present_fold_safe: PASS
- policy_tradeoff_reported: PASS
- selection_not_fixed_export_only: PASS

## Eindstatus: GO

## Feature engineering choices that must not be violated later
- Geen holdout-gedreven tuning.
- Fold-safe refit blijft primaire evaluatiebasis.
- Policy en forecast blijven strikt gescheiden qua L-features.

## Recommended modelling ablation map
- Policy: P0, P1, P2, P3, P4
- Forecast: F0, F1, F2, F3, F4