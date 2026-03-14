from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import itertools
import json
import math
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.phase4.protocol import (
    DEFAULT_SEED as PHASE4_SEED,
    _apply_row_filter,
    _get_variant_features,
    _load_phase_inputs,
    _make_regressor,
    _metric_bundle,
    get_phase4_paths,
)


DEFAULT_SEED = PHASE4_SEED
PHASE5_PRIMARY_RUNS = {
    "policy": "P4_ridge_a1_0",
    "forecast": "F3_rf_90_d12_l2",
}
PHASE5_BENCHMARK_RUNS = {
    "policy": "P0_profile_baseline",
    "forecast": "F0_persistence_baseline",
}


@dataclass(frozen=True)
class Phase5Paths:
    project_root: Path
    phase4_results_dir: Path
    phase4_internal_dir: Path
    phase4_feature_set_dir: Path
    phase5_results_dir: Path
    notebooks_phase5_dir: Path


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "data_processed").exists() and (candidate / "notebooks").exists():
            return candidate
    raise FileNotFoundError("Project root not found")


def get_phase5_paths(project_root: Path | None = None) -> Phase5Paths:
    root = (project_root or find_project_root()).resolve()
    phase4_results_dir = root / "data_results" / "phase4"
    phase4_internal_dir = phase4_results_dir / "internal"
    phase4_feature_set_dir = root / "data_processed" / "phase4_feature_sets"
    phase5_results_dir = root / "data_results" / "phase5"
    notebooks_phase5_dir = root / "notebooks" / "phase5"

    phase5_results_dir.mkdir(parents=True, exist_ok=True)
    notebooks_phase5_dir.mkdir(parents=True, exist_ok=True)

    return Phase5Paths(
        project_root=root,
        phase4_results_dir=phase4_results_dir,
        phase4_internal_dir=phase4_internal_dir,
        phase4_feature_set_dir=phase4_feature_set_dir,
        phase5_results_dir=phase5_results_dir,
        notebooks_phase5_dir=notebooks_phase5_dir,
    )


def _ensure_datetime(df: pd.DataFrame, col: str) -> None:
    df[col] = pd.to_datetime(df[col], errors="coerce")


def _require_shap() -> Any:
    try:
        import shap  # noqa: PLC0415

        return shap
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("`shap` is required for Phase 5. Install via `.venv/bin/python -m pip install shap`.") from exc


def _load_event_contract(paths: Phase5Paths) -> pd.DataFrame:
    p = paths.phase4_results_dir / "event_feature_availability_contract.csv"
    if not p.exists():
        raise FileNotFoundError(f"Missing event contract: {p}")
    return pd.read_csv(p)


def _load_phase4_shortlist(paths: Phase5Paths) -> pd.DataFrame:
    p = paths.phase4_results_dir / "phase4_model_selection_shortlist.csv"
    if not p.exists():
        raise FileNotFoundError(f"Missing Phase 4 shortlist: {p}")
    return pd.read_csv(p)


def _load_phase4_holdout_results(paths: Phase5Paths) -> pd.DataFrame:
    p = paths.phase4_results_dir / "phase4_holdout_results_2025.csv"
    if not p.exists():
        raise FileNotFoundError(f"Missing Phase 4 holdout results: {p}")
    return pd.read_csv(p)


def _daypart_from_hour(hour: pd.Series) -> pd.Series:
    h = pd.to_numeric(hour, errors="coerce").fillna(0).astype(int)
    return pd.Series(
        np.select(
            [
                h.between(0, 5),
                h.between(6, 11),
                h.between(12, 17),
                h.between(18, 23),
            ],
            ["night", "morning", "afternoon", "evening"],
            default="unknown",
        ),
        index=hour.index,
    )


def _tier_group(df: pd.DataFrame) -> pd.Series:
    is_centrum = pd.to_numeric(df.get("s_tier_is_centrum", 0), errors="coerce").fillna(0).astype(float) > 0
    return pd.Series(np.where(is_centrum, "centrum", "vesten_rand"), index=df.index)


def _event_flag(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df.get("e_is_event_day", 0), errors="coerce").fillna(0).astype(float).gt(0)


def _build_strata(df: pd.DataFrame) -> pd.Series:
    tier = _tier_group(df)
    event = _event_flag(df).map({True: "event", False: "non_event"})
    daypart = _daypart_from_hour(df.get("hour", pd.Series(0, index=df.index)))
    return tier.astype(str) + "|" + event.astype(str) + "|" + daypart.astype(str)


def _stratified_sample(df: pd.DataFrame, n_max: int, seed: int) -> pd.DataFrame:
    if len(df) <= n_max:
        return df.copy()

    rng = np.random.default_rng(seed)
    strata = _build_strata(df)
    tmp = df.copy()
    tmp["_strata"] = strata

    counts = tmp["_strata"].value_counts().sort_index()
    total = int(counts.sum())
    target = int(n_max)

    frac = counts / total
    alloc = np.floor(frac * target).astype(int)
    alloc = alloc.clip(lower=1)

    # Reduce if overflow after minimum-1 guard
    overflow = int(alloc.sum() - target)
    if overflow > 0:
        for key in alloc.sort_values(ascending=False).index:
            if overflow == 0:
                break
            if alloc.loc[key] > 1:
                drop = min(int(alloc.loc[key] - 1), overflow)
                alloc.loc[key] -= drop
                overflow -= drop

    # Distribute leftovers
    leftover = int(target - alloc.sum())
    if leftover > 0:
        remainders = (frac * target - np.floor(frac * target)).sort_values(ascending=False)
        keys = list(remainders.index)
        for i in range(leftover):
            alloc.loc[keys[i % len(keys)]] += 1

    sampled_idx: list[int] = []
    for key, n_take in alloc.items():
        grp_idx = tmp.index[tmp["_strata"] == key].to_numpy()
        n_take = int(min(n_take, len(grp_idx)))
        if n_take <= 0:
            continue
        pick = rng.choice(grp_idx, size=n_take, replace=False)
        sampled_idx.extend(pick.tolist())

    out = tmp.loc[sorted(set(sampled_idx))].drop(columns=["_strata"])
    if len(out) > n_max:
        out = out.sample(n=n_max, random_state=seed)
    return out.sort_index()


def _safe_mape(y_true: np.ndarray, y_pred: np.ndarray, eps: float = 1e-6) -> float:
    denom = np.maximum(np.abs(y_true), eps)
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


def _metric_bundle_simple(df: pd.DataFrame, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    err = np.abs(y_true - y_pred)

    def _masked_mae(mask: np.ndarray) -> float:
        if mask.sum() == 0:
            return float("nan")
        return float(np.mean(err[mask]))

    mask_centrum = _tier_group(df).to_numpy() == "centrum"
    mask_vr = ~mask_centrum
    mask_event = _event_flag(df).to_numpy()
    mask_non_event = ~mask_event

    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(math.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": _safe_mape(y_true, y_pred),
        "mae_tier_centrum": _masked_mae(mask_centrum),
        "mae_tier_vesten_rand": _masked_mae(mask_vr),
        "mae_event": _masked_mae(mask_event),
        "mae_non_event": _masked_mae(mask_non_event),
    }


def _profile_baseline_predict_with_stage(train_df: pd.DataFrame, valid_df: pd.DataFrame) -> tuple[np.ndarray, pd.Series]:
    prof = (
        train_df.groupby(["parking_id", "hour", "weekday_int"], as_index=False)["occupancy_rate"]
        .mean()
        .rename(columns={"occupancy_rate": "pred"})
    )
    p_h = (
        train_df.groupby(["parking_id", "hour"], as_index=False)["occupancy_rate"]
        .mean()
        .rename(columns={"occupancy_rate": "pred_ph"})
    )
    p = train_df.groupby("parking_id", as_index=False)["occupancy_rate"].mean().rename(columns={"occupancy_rate": "pred_p"})
    global_mean = float(train_df["occupancy_rate"].mean())

    pred_df = valid_df[["parking_id", "hour", "weekday_int"]].copy()
    pred_df = pred_df.merge(prof, on=["parking_id", "hour", "weekday_int"], how="left")
    pred_df = pred_df.merge(p_h, on=["parking_id", "hour"], how="left")
    pred_df = pred_df.merge(p, on=["parking_id"], how="left")

    stage = pd.Series("global", index=pred_df.index)
    stage[pred_df["pred_p"].notna()] = "parking"
    stage[pred_df["pred_ph"].notna()] = "parking_hour"
    stage[pred_df["pred"].notna()] = "parking_hour_weekday"

    pred = pred_df["pred"].copy()
    pred = pred.fillna(pred_df["pred_ph"]).fillna(pred_df["pred_p"]).fillna(global_mean)
    return pred.to_numpy(dtype=float), stage


def _persistence_baseline_predict_with_stage(train_df: pd.DataFrame, valid_df: pd.DataFrame) -> tuple[np.ndarray, pd.Series]:
    fallback_pred, _fallback_stage = _profile_baseline_predict_with_stage(train_df, valid_df)
    lag1 = pd.to_numeric(valid_df.get("l_occ_lag_1h"), errors="coerce")
    lag24 = pd.to_numeric(valid_df.get("l_occ_lag_24h"), errors="coerce")

    stage = pd.Series("fallback_profile", index=valid_df.index)
    stage[lag24.notna()] = "lag24"
    stage[lag1.notna()] = "lag1"

    pred = lag1.copy()
    pred = pred.fillna(lag24)
    pred = pred.fillna(pd.Series(fallback_pred, index=valid_df.index))
    return pred.to_numpy(dtype=float), stage


def _pairwise_jaccard(sets: list[set[str]]) -> float:
    if len(sets) < 2:
        return float("nan")
    vals = []
    for a, b in itertools.combinations(sets, 2):
        if not a and not b:
            vals.append(1.0)
            continue
        denom = len(a | b)
        vals.append((len(a & b) / denom) if denom else 0.0)
    return float(np.mean(vals)) if vals else float("nan")


def _bootstrap_delta_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_boot: int,
    alpha: float,
    seed: int,
) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    deltas = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        xb = x[rng.integers(0, len(x), len(x))]
        yb = y[rng.integers(0, len(y), len(y))]
        deltas[i] = float(xb.mean() - yb.mean())
    lo = float(np.quantile(deltas, alpha / 2.0))
    hi = float(np.quantile(deltas, 1.0 - alpha / 2.0))
    return float(deltas.mean()), lo, hi


def _permutation_pvalue(
    x: np.ndarray,
    y: np.ndarray,
    n_perm: int,
    seed: int,
) -> float:
    rng = np.random.default_rng(seed)
    obs = float(x.mean() - y.mean())
    pool = np.concatenate([x, y])
    n_x = len(x)
    if n_x == 0 or len(y) == 0:
        return float("nan")

    stats = np.empty(n_perm, dtype=float)
    for i in range(n_perm):
        perm = rng.permutation(pool)
        stats[i] = float(perm[:n_x].mean() - perm[n_x:].mean())
    p = float((np.abs(stats) >= abs(obs)).mean())
    return max(p, 1.0 / n_perm)


def _build_phase5_protocol_markdown(shap_available: bool) -> str:
    return "\n".join(
        [
            "# Phase 5 Protocol (Interpretatie SHAP + Per-Tier)",
            "",
            "Datum: 2026-03-13",
            "",
            "## Scope-lock",
            "- Primaire interpretatiemodellen: `P4_ridge_a1_0` (policy) en `F3_rf_90_d12_l2` (forecast).",
            "- Benchmarkcontrast: `P0_profile_baseline` en `F0_persistence_baseline`.",
            "- Claimbasis: fold-stability + finale holdout-interpretatie 2025.",
            "- Primair tier-niveau: centrum vs vesten/rand.",
            "",
            "## Methodologische guardrails",
            "1. Geen modelherselectie in Phase 5.",
            "2. Geen hyperparametertuning in Phase 5.",
            "3. Geen holdout-gebruik voor modelkeuze.",
            "4. Policy/forecast trackscheiding blijft intact.",
            "5. SHAP is verplicht voor primaire interpretatie.",
            "",
            "## Dependency status",
            f"- shap beschikbaar: {'YES' if shap_available else 'NO'}",
        ]
    )


def run_phase5_scope_lock(paths: Phase5Paths | None = None) -> dict[str, Any]:
    p = paths or get_phase5_paths()

    checks: list[dict[str, Any]] = []

    try:
        shap_mod = _require_shap()
        shap_ok = True
        shap_version = str(shap_mod.__version__)
    except Exception:  # noqa: BLE001
        shap_ok = False
        shap_version = "missing"

    checks.append({"check": "shap_available", "result": "PASS" if shap_ok else "FAIL", "detail": f"version={shap_version}"})

    required_files = [
        p.phase4_results_dir / "phase4_model_selection_shortlist.csv",
        p.phase4_results_dir / "phase4_holdout_results_2025.csv",
        p.phase4_results_dir / "phase4_fold_safety_log.csv",
        p.phase4_results_dir / "event_feature_availability_contract.csv",
        p.phase4_feature_set_dir / "feature_manifest_policy.json",
        p.phase4_feature_set_dir / "feature_manifest_forecast.json",
    ]
    for req in required_files:
        checks.append(
            {
                "check": f"exists::{req.name}",
                "result": "PASS" if req.exists() else "FAIL",
                "detail": str(req),
            }
        )

    shortlist = _load_phase4_shortlist(p)
    for run_id in [*PHASE5_PRIMARY_RUNS.values(), *PHASE5_BENCHMARK_RUNS.values()]:
        checks.append(
            {
                "check": f"shortlist_has::{run_id}",
                "result": "PASS" if run_id in set(shortlist["run_id"].astype(str)) else "FAIL",
                "detail": "present in phase4_model_selection_shortlist",
            }
        )

    scope_rows = [
        {
            "track": "policy",
            "role": "primary",
            "run_id": "P4_ridge_a1_0",
            "model_family": "ridge",
            "feature_set_id": "policy_tse_exante_strict",
            "row_filter": "none",
            "claim_scope": "fold_plus_holdout",
        },
        {
            "track": "forecast",
            "role": "primary",
            "run_id": "F3_rf_90_d12_l2",
            "model_family": "random_forest",
            "feature_set_id": "forecast_tsel_core_strict_lagvalid",
            "row_filter": "l_valid_all_core==1",
            "claim_scope": "fold_plus_holdout",
        },
        {
            "track": "policy",
            "role": "benchmark",
            "run_id": "P0_profile_baseline",
            "model_family": "baseline",
            "feature_set_id": "baseline_profile",
            "row_filter": "none",
            "claim_scope": "benchmark_contrast",
        },
        {
            "track": "forecast",
            "role": "benchmark",
            "run_id": "F0_persistence_baseline",
            "model_family": "baseline",
            "feature_set_id": "baseline_persistence",
            "row_filter": "none",
            "claim_scope": "benchmark_contrast",
        },
    ]
    scope_df = pd.DataFrame(scope_rows)

    protocol_md = _build_phase5_protocol_markdown(shap_available=shap_ok)
    checks_df = pd.DataFrame(checks)

    (p.phase5_results_dir / "phase5_protocol.md").write_text(protocol_md)
    scope_df.to_csv(p.phase5_results_dir / "phase5_model_scope.csv", index=False)
    checks_df.to_csv(p.phase5_results_dir / "phase5_scope_checks.csv", index=False)

    return {
        "scope": scope_df,
        "checks": checks_df,
        "paths": {
            "phase5_protocol_md": str(p.phase5_results_dir / "phase5_protocol.md"),
            "phase5_model_scope_csv": str(p.phase5_results_dir / "phase5_model_scope.csv"),
            "phase5_scope_checks_csv": str(p.phase5_results_dir / "phase5_scope_checks.csv"),
        },
    }


def _load_phase4_internal_layers(paths: Phase5Paths, track: str, fold_id: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    if fold_id is None:
        full_dir = paths.phase4_internal_dir / "full_train_holdout"
        if track == "policy":
            train_df = pd.read_parquet(full_dir / "policy_train.parquet")
            valid_df = pd.read_parquet(full_dir / "policy_holdout.parquet")
        else:
            train_df = pd.read_parquet(full_dir / "forecast_train.parquet")
            valid_df = pd.read_parquet(full_dir / "forecast_holdout.parquet")
    else:
        fold_dir = paths.phase4_internal_dir / "fold_safe" / str(fold_id)
        train_df = pd.read_parquet(fold_dir / f"{track}_train.parquet")
        valid_df = pd.read_parquet(fold_dir / f"{track}_valid.parquet")

    for df in [train_df, valid_df]:
        _ensure_datetime(df, "rounded_hour")

    return train_df, valid_df


def _resolve_run_spec(scope_row: pd.Series, shortlist: pd.DataFrame) -> dict[str, Any]:
    run_id = str(scope_row["run_id"])
    row = shortlist.loc[shortlist["run_id"].astype(str) == run_id]
    if row.empty:
        raise ValueError(f"run_id not found in shortlist: {run_id}")
    r = row.iloc[0]
    return {
        "run_id": run_id,
        "track": str(r["track"]),
        "variant": str(r["variant"]),
        "model_family": str(r["model_family"]),
        "model_key": str(r["model_key"]),
        "row_filter": str(scope_row["row_filter"]),
    }


def _compute_model_shap_values(
    model_family: str,
    model: Any,
    X_train: pd.DataFrame,
    X_sample: pd.DataFrame,
    feature_cols: list[str],
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    shap = _require_shap()

    preproc = model[:-1]
    est = model.named_steps["model"]

    X_train_proc = preproc.transform(X_train)
    X_sample_proc = preproc.transform(X_sample)

    if model_family == "ridge":
        explainer = shap.LinearExplainer(est, X_train_proc)
        exp = explainer(X_sample_proc)
        values = np.asarray(exp.values, dtype=float)
        base_values = np.asarray(exp.base_values, dtype=float)
    elif model_family == "random_forest":
        explainer = shap.TreeExplainer(est, data=X_train_proc, feature_perturbation="interventional")
        vals = explainer.shap_values(X_sample_proc, check_additivity=False)
        if isinstance(vals, list):
            vals = vals[0]
        values = np.asarray(vals, dtype=float)
        base = explainer.expected_value
        if isinstance(base, (list, np.ndarray)):
            base = float(np.asarray(base).reshape(-1)[0])
        base_values = np.full(X_sample_proc.shape[0], float(base), dtype=float)
    else:
        # robust fallback for unexpected family
        explainer = shap.Explainer(est, X_train_proc, seed=seed, feature_names=feature_cols)
        exp = explainer(X_sample_proc)
        values = np.asarray(exp.values, dtype=float)
        base_values = np.asarray(exp.base_values, dtype=float)

    if values.ndim != 2:
        values = values.reshape(values.shape[0], -1)

    pred = model.predict(X_sample).astype(float)
    return values, base_values.reshape(-1), pred


def _context_label(fold_id: str | None) -> str:
    return "holdout" if fold_id is None else f"fold_{fold_id}"


def _prepare_feature_columns(
    run_spec: dict[str, Any],
    policy_inputs: list[str],
    forecast_inputs: list[str],
    uncertain_event_features: set[str],
) -> list[str]:
    return _get_variant_features(
        track=run_spec["track"],
        variant=run_spec["variant"],
        policy_inputs=policy_inputs,
        forecast_inputs=forecast_inputs,
        uncertain_event_features=uncertain_event_features,
    )


def run_phase5_shap_core(
    paths: Phase5Paths | None = None,
    holdout_sample_max: int = 20000,
    fold_sample_max: int = 6000,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    p = paths or get_phase5_paths()
    _require_shap()

    scope_path = p.phase5_results_dir / "phase5_model_scope.csv"
    if not scope_path.exists():
        run_phase5_scope_lock(paths=p)

    scope = pd.read_csv(scope_path)
    shortlist = _load_phase4_shortlist(p)

    p4_paths = get_phase4_paths(project_root=p.project_root)
    phase_inputs = _load_phase_inputs(p4_paths)
    policy_inputs = list(phase_inputs["policy_manifest"]["model_input_columns"])
    forecast_inputs = list(phase_inputs["forecast_manifest"]["model_input_columns"])

    event_contract = _load_event_contract(p)
    uncertain = set(
        event_contract.loc[event_contract["availability_label"].eq("ex_post_or_uncertain"), "feature_name"].astype(str).tolist()
    )

    fold_log = pd.read_csv(p.phase4_results_dir / "phase4_fold_safety_log.csv")
    fold_ids = [str(x) for x in fold_log["fold"].astype(str).tolist()]

    rowlevel_frames: list[pd.DataFrame] = []
    global_rows: list[dict[str, Any]] = []
    tier_rows: list[dict[str, Any]] = []
    additivity_rows: list[dict[str, Any]] = []
    context_metric_rows: list[dict[str, Any]] = []

    prim_scope = scope.loc[scope["role"].eq("primary")].copy()
    for _, srow in prim_scope.iterrows():
        run_spec = _resolve_run_spec(srow, shortlist)
        run_id = str(run_spec["run_id"])
        track = str(run_spec["track"])
        variant = str(run_spec["variant"])
        model_key = str(run_spec["model_key"])
        model_family = str(run_spec["model_family"])
        row_filter = str(run_spec["row_filter"])

        feature_cols = _prepare_feature_columns(
            run_spec=run_spec,
            policy_inputs=policy_inputs,
            forecast_inputs=forecast_inputs,
            uncertain_event_features=uncertain,
        )

        contexts = [None, *fold_ids]
        for fold_id in contexts:
            context = _context_label(fold_id)
            context_seed = seed + (0 if fold_id is None else abs(hash(fold_id)) % 10000)

            train_df, valid_df = _load_phase4_internal_layers(paths=p, track=track, fold_id=fold_id)
            train_df = _apply_row_filter(train_df, row_filter=row_filter)
            valid_df = _apply_row_filter(valid_df, row_filter=row_filter)
            train_df = train_df.dropna(subset=["occupancy_rate"]).copy()
            valid_df = valid_df.dropna(subset=["occupancy_rate"]).copy()

            if train_df.empty or valid_df.empty:
                continue

            model = _make_regressor(model_key=model_key, seed=seed)
            X_train = train_df[feature_cols]
            y_train = train_df["occupancy_rate"].to_numpy(dtype=float)
            model.fit(X_train, y_train)

            # Context metrics on full valid subset (not just SHAP sample)
            y_valid = valid_df["occupancy_rate"].to_numpy(dtype=float)
            y_pred_full = model.predict(valid_df[feature_cols]).astype(float)
            metrics = _metric_bundle(valid_df, y_valid, y_pred_full)
            context_metric_rows.append(
                {
                    "run_id": run_id,
                    "track": track,
                    "variant": variant,
                    "context": context,
                    "fold_id": "holdout" if fold_id is None else str(fold_id),
                    "n_train": int(len(train_df)),
                    "n_valid": int(len(valid_df)),
                    **metrics,
                }
            )

            n_max = holdout_sample_max if fold_id is None else fold_sample_max
            sample_df = _stratified_sample(valid_df, n_max=n_max, seed=context_seed)

            X_sample = sample_df[feature_cols]
            shap_values, base_values, y_pred = _compute_model_shap_values(
                model_family=model_family,
                model=model,
                X_train=X_train,
                X_sample=X_sample,
                feature_cols=feature_cols,
                seed=context_seed,
            )

            # Additivity check
            shap_sum = base_values + shap_values.sum(axis=1)
            abs_err = np.abs(shap_sum - y_pred)
            additivity_rows.append(
                {
                    "run_id": run_id,
                    "context": context,
                    "fold_id": "holdout" if fold_id is None else str(fold_id),
                    "n_obs": int(len(sample_df)),
                    "mean_abs_error": float(np.mean(abs_err)),
                    "p95_abs_error": float(np.quantile(abs_err, 0.95)),
                    "max_abs_error": float(np.max(abs_err)),
                    "tol_1e-4_pass_rate": float((abs_err <= 1e-4).mean()),
                }
            )

            tier_grp = _tier_group(sample_df)
            event_flag = _event_flag(sample_df)
            daypart = _daypart_from_hour(sample_df.get("hour", pd.Series(0, index=sample_df.index)))

            # Row-level output
            row_df = sample_df[["parking_id", "rounded_hour", "occupancy_rate"]].copy()
            row_df.insert(0, "run_id", run_id)
            row_df.insert(1, "track", track)
            row_df.insert(2, "variant", variant)
            row_df.insert(3, "context", context)
            row_df.insert(4, "fold_id", "holdout" if fold_id is None else str(fold_id))
            row_df["tier_group"] = tier_grp.values
            row_df["event_flag"] = event_flag.astype(int).values
            row_df["daypart"] = daypart.values
            row_df["y_pred"] = y_pred
            row_df["base_value"] = base_values
            row_df["additivity_abs_error"] = abs_err

            for j, feat in enumerate(feature_cols):
                row_df[f"shap__{feat}"] = shap_values[:, j]

            rowlevel_frames.append(row_df)

            # Global importance
            mean_abs = np.abs(shap_values).mean(axis=0)
            mean_signed = shap_values.mean(axis=0)
            gdf = pd.DataFrame(
                {
                    "feature_name": feature_cols,
                    "mean_abs_shap": mean_abs,
                    "mean_signed_shap": mean_signed,
                }
            ).sort_values("mean_abs_shap", ascending=False)
            gdf["rank"] = np.arange(1, len(gdf) + 1)
            for _, r in gdf.iterrows():
                global_rows.append(
                    {
                        "run_id": run_id,
                        "track": track,
                        "context": context,
                        "fold_id": "holdout" if fold_id is None else str(fold_id),
                        "feature_name": str(r["feature_name"]),
                        "mean_abs_shap": float(r["mean_abs_shap"]),
                        "mean_signed_shap": float(r["mean_signed_shap"]),
                        "rank": int(r["rank"]),
                        "n_obs": int(len(sample_df)),
                    }
                )

            # Tier-specific importance
            for tier in ["centrum", "vesten_rand"]:
                mask = tier_grp.to_numpy() == tier
                if mask.sum() == 0:
                    continue
                t_abs = np.abs(shap_values[mask]).mean(axis=0)
                t_signed = shap_values[mask].mean(axis=0)
                tdf = pd.DataFrame(
                    {
                        "feature_name": feature_cols,
                        "mean_abs_shap": t_abs,
                        "mean_signed_shap": t_signed,
                    }
                ).sort_values("mean_abs_shap", ascending=False)
                tdf["rank"] = np.arange(1, len(tdf) + 1)
                for _, tr in tdf.iterrows():
                    tier_rows.append(
                        {
                            "run_id": run_id,
                            "track": track,
                            "context": context,
                            "fold_id": "holdout" if fold_id is None else str(fold_id),
                            "tier_group": tier,
                            "feature_name": str(tr["feature_name"]),
                            "mean_abs_shap": float(tr["mean_abs_shap"]),
                            "mean_signed_shap": float(tr["mean_signed_shap"]),
                            "rank": int(tr["rank"]),
                            "n_obs": int(mask.sum()),
                        }
                    )

    rowlevel = pd.concat(rowlevel_frames, axis=0, ignore_index=True) if rowlevel_frames else pd.DataFrame()
    global_imp = pd.DataFrame(global_rows)
    tier_imp = pd.DataFrame(tier_rows)
    additivity = pd.DataFrame(additivity_rows)
    context_metrics = pd.DataFrame(context_metric_rows)

    if not rowlevel.empty:
        rowlevel.to_parquet(p.phase5_results_dir / "phase5_shap_rowlevel_samples.parquet", index=False)
    global_imp.to_csv(p.phase5_results_dir / "phase5_shap_global_importance.csv", index=False)
    tier_imp.to_csv(p.phase5_results_dir / "phase5_shap_tier_importance.csv", index=False)
    additivity.to_csv(p.phase5_results_dir / "phase5_shap_additivity_checks.csv", index=False)
    context_metrics.to_csv(p.phase5_results_dir / "phase5_context_metrics.csv", index=False)

    return {
        "rowlevel": rowlevel,
        "global_importance": global_imp,
        "tier_importance": tier_imp,
        "additivity_checks": additivity,
        "context_metrics": context_metrics,
        "paths": {
            "phase5_shap_rowlevel_samples_parquet": str(p.phase5_results_dir / "phase5_shap_rowlevel_samples.parquet"),
            "phase5_shap_global_importance_csv": str(p.phase5_results_dir / "phase5_shap_global_importance.csv"),
            "phase5_shap_tier_importance_csv": str(p.phase5_results_dir / "phase5_shap_tier_importance.csv"),
            "phase5_shap_additivity_checks_csv": str(p.phase5_results_dir / "phase5_shap_additivity_checks.csv"),
            "phase5_context_metrics_csv": str(p.phase5_results_dir / "phase5_context_metrics.csv"),
        },
    }


def _compute_fold_stability(global_imp: pd.DataFrame) -> pd.DataFrame:
    fold_df = global_imp.loc[global_imp["context"].astype(str).str.startswith("fold_")].copy()
    if fold_df.empty:
        return pd.DataFrame(
            columns=["run_id", "feature_name", "mean_rank", "std_rank", "top10_freq", "sign_consistency"]
        )

    out_rows: list[dict[str, Any]] = []
    for (run_id, feat), grp in fold_df.groupby(["run_id", "feature_name"], as_index=False):
        ranks = pd.to_numeric(grp["rank"], errors="coerce").dropna().to_numpy(dtype=float)
        signs = np.sign(pd.to_numeric(grp["mean_signed_shap"], errors="coerce").fillna(0).to_numpy(dtype=float))
        pos = float((signs > 0).mean())
        neg = float((signs < 0).mean())
        sign_consistency = max(pos, neg)

        out_rows.append(
            {
                "run_id": str(run_id),
                "feature_name": str(feat),
                "mean_rank": float(np.mean(ranks)) if len(ranks) else float("nan"),
                "std_rank": float(np.std(ranks, ddof=0)) if len(ranks) else float("nan"),
                "top10_freq": float((ranks <= 10).mean()) if len(ranks) else float("nan"),
                "sign_consistency": float(sign_consistency),
            }
        )

    return pd.DataFrame(out_rows)


def _baseline_diagnostics(paths: Phase5Paths, scope: pd.DataFrame) -> pd.DataFrame:
    shortlist = _load_phase4_shortlist(paths)
    bench = scope.loc[scope["role"].eq("benchmark")].copy()

    fold_log = pd.read_csv(paths.phase4_results_dir / "phase4_fold_safety_log.csv")
    fold_ids = [str(x) for x in fold_log["fold"].astype(str).tolist()]

    rows: list[dict[str, Any]] = []

    for _, b in bench.iterrows():
        run_spec = _resolve_run_spec(b, shortlist)
        run_id = str(run_spec["run_id"])
        track = str(run_spec["track"])

        for fold_id in [None, *fold_ids]:
            context = _context_label(fold_id)
            train_df, valid_df = _load_phase4_internal_layers(paths, track=track, fold_id=fold_id)
            train_df = train_df.dropna(subset=["occupancy_rate"]).copy()
            valid_df = valid_df.dropna(subset=["occupancy_rate"]).copy()
            if train_df.empty or valid_df.empty:
                continue

            if run_id == "P0_profile_baseline":
                y_pred, stage = _profile_baseline_predict_with_stage(train_df, valid_df)
                stage_cols = {
                    "share_stage_parking_hour_weekday": float((stage == "parking_hour_weekday").mean()),
                    "share_stage_parking_hour": float((stage == "parking_hour").mean()),
                    "share_stage_parking": float((stage == "parking").mean()),
                    "share_stage_global": float((stage == "global").mean()),
                }
            elif run_id == "F0_persistence_baseline":
                y_pred, stage = _persistence_baseline_predict_with_stage(train_df, valid_df)
                stage_cols = {
                    "share_stage_lag1": float((stage == "lag1").mean()),
                    "share_stage_lag24": float((stage == "lag24").mean()),
                    "share_stage_fallback_profile": float((stage == "fallback_profile").mean()),
                }
            else:
                continue

            y_true = valid_df["occupancy_rate"].to_numpy(dtype=float)
            metrics = _metric_bundle_simple(valid_df, y_true, y_pred)
            rows.append(
                {
                    "run_id": run_id,
                    "track": track,
                    "context": context,
                    "fold_id": "holdout" if fold_id is None else str(fold_id),
                    "n_rows": int(len(valid_df)),
                    **metrics,
                    **stage_cols,
                }
            )

    return pd.DataFrame(rows)


def run_phase5_tier_contrast(
    paths: Phase5Paths | None = None,
    n_boot: int = 400,
    n_perm: int = 400,
    alpha: float = 0.05,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    p = paths or get_phase5_paths()

    if not (p.phase5_results_dir / "phase5_shap_global_importance.csv").exists():
        run_phase5_shap_core(paths=p)

    scope = pd.read_csv(p.phase5_results_dir / "phase5_model_scope.csv")
    global_imp = pd.read_csv(p.phase5_results_dir / "phase5_shap_global_importance.csv")
    tier_imp = pd.read_csv(p.phase5_results_dir / "phase5_shap_tier_importance.csv")
    rowlevel = pd.read_parquet(p.phase5_results_dir / "phase5_shap_rowlevel_samples.parquet")

    # Tier delta tests on holdout SHAP samples only (primary models)
    primary_runs = set(scope.loc[scope["role"].eq("primary"), "run_id"].astype(str).tolist())
    hold = rowlevel.loc[(rowlevel["run_id"].astype(str).isin(primary_runs)) & (rowlevel["context"].astype(str).eq("holdout"))].copy()

    shap_cols = [c for c in hold.columns if c.startswith("shap__")]
    delta_rows: list[dict[str, Any]] = []

    for run_id, g in hold.groupby("run_id", as_index=False):
        g = g.copy()
        mask_c = g["tier_group"].astype(str).eq("centrum").to_numpy()
        mask_v = g["tier_group"].astype(str).eq("vesten_rand").to_numpy()
        if mask_c.sum() == 0 or mask_v.sum() == 0:
            continue

        for sc in shap_cols:
            feat = sc.replace("shap__", "", 1)
            vals = np.abs(pd.to_numeric(g[sc], errors="coerce").fillna(0).to_numpy(dtype=float))
            x = vals[mask_c]
            y = vals[mask_v]
            if len(x) < 10 or len(y) < 10:
                continue

            delta = float(x.mean() - y.mean())
            boot_mean, ci_low, ci_high = _bootstrap_delta_ci(x=x, y=y, n_boot=n_boot, alpha=alpha, seed=seed)
            p_val = _permutation_pvalue(x=x, y=y, n_perm=n_perm, seed=seed)
            significant = bool((ci_low > 0 or ci_high < 0) and p_val < 0.05)

            delta_rows.append(
                {
                    "run_id": str(run_id),
                    "track": "policy" if str(run_id).startswith("P") else "forecast",
                    "context": "holdout",
                    "feature_name": feat,
                    "delta_mean_abs_shap": delta,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "p_value": p_val,
                    "significant": significant,
                    "n_centrum": int(len(x)),
                    "n_vesten_rand": int(len(y)),
                }
            )

    delta_tests = pd.DataFrame(delta_rows)

    fold_stability = _compute_fold_stability(global_imp)

    baseline_diag = _baseline_diagnostics(p, scope=scope)

    delta_tests.to_csv(p.phase5_results_dir / "phase5_shap_tier_delta_tests.csv", index=False)
    fold_stability.to_csv(p.phase5_results_dir / "phase5_shap_fold_stability.csv", index=False)
    baseline_diag.to_csv(p.phase5_results_dir / "phase5_baseline_diagnostics.csv", index=False)

    return {
        "global_importance": global_imp,
        "tier_importance": tier_imp,
        "tier_delta_tests": delta_tests,
        "fold_stability": fold_stability,
        "baseline_diagnostics": baseline_diag,
        "paths": {
            "phase5_shap_global_importance_csv": str(p.phase5_results_dir / "phase5_shap_global_importance.csv"),
            "phase5_shap_tier_importance_csv": str(p.phase5_results_dir / "phase5_shap_tier_importance.csv"),
            "phase5_shap_tier_delta_tests_csv": str(p.phase5_results_dir / "phase5_shap_tier_delta_tests.csv"),
            "phase5_shap_fold_stability_csv": str(p.phase5_results_dir / "phase5_shap_fold_stability.csv"),
            "phase5_baseline_diagnostics_csv": str(p.phase5_results_dir / "phase5_baseline_diagnostics.csv"),
        },
    }


def _mean_top10_jaccard(global_imp: pd.DataFrame, run_id: str) -> float:
    fold_df = global_imp.loc[(global_imp["run_id"].astype(str) == run_id) & (global_imp["context"].astype(str).str.startswith("fold_"))]
    if fold_df.empty:
        return float("nan")

    top_sets: list[set[str]] = []
    for _, grp in fold_df.groupby("context", as_index=False):
        top = grp.sort_values("rank").head(10)["feature_name"].astype(str).tolist()
        top_sets.append(set(top))
    return _pairwise_jaccard(top_sets)


def run_phase5_iterative_refine(
    paths: Phase5Paths | None = None,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    p = paths or get_phase5_paths()

    # Ensure upstream artefacts
    if not (p.phase5_results_dir / "phase5_shap_global_importance.csv").exists():
        run_phase5_shap_core(paths=p)
    if not (p.phase5_results_dir / "phase5_shap_tier_delta_tests.csv").exists():
        run_phase5_tier_contrast(paths=p)

    global_imp = pd.read_csv(p.phase5_results_dir / "phase5_shap_global_importance.csv")
    fold_stability = pd.read_csv(p.phase5_results_dir / "phase5_shap_fold_stability.csv")
    tier_tests = pd.read_csv(p.phase5_results_dir / "phase5_shap_tier_delta_tests.csv")
    baseline_diag = pd.read_csv(p.phase5_results_dir / "phase5_baseline_diagnostics.csv")

    critique_rows: list[dict[str, Any]] = []

    # Rule 1: Top-10 Jaccard over folds
    j_policy = _mean_top10_jaccard(global_imp, "P4_ridge_a1_0")
    j_forecast = _mean_top10_jaccard(global_imp, "F3_rf_90_d12_l2")
    j_min = float(np.nanmin([j_policy, j_forecast])) if not (math.isnan(j_policy) and math.isnan(j_forecast)) else float("nan")
    trigger_jaccard = (not math.isnan(j_min)) and j_min < 0.60

    critique_rows.append(
        {
            "rule": "top10_jaccard_threshold",
            "value": j_min,
            "threshold": 0.60,
            "triggered": bool(trigger_jaccard),
            "action": "rerun_shap_with_larger_samples" if trigger_jaccard else "none",
            "detail": f"policy={j_policy:.4f}, forecast={j_forecast:.4f}",
        }
    )

    if trigger_jaccard:
        run_phase5_shap_core(paths=p, holdout_sample_max=30000, fold_sample_max=10000, seed=seed + 77)
        run_phase5_tier_contrast(paths=p, seed=seed + 77)
        global_imp = pd.read_csv(p.phase5_results_dir / "phase5_shap_global_importance.csv")
        fold_stability = pd.read_csv(p.phase5_results_dir / "phase5_shap_fold_stability.csv")
        tier_tests = pd.read_csv(p.phase5_results_dir / "phase5_shap_tier_delta_tests.csv")

    # Rule 2: Linear direction consistency P4
    p4_stab = fold_stability.loc[fold_stability["run_id"].astype(str).eq("P4_ridge_a1_0")].copy()
    if p4_stab.empty:
        p4_dir_cons = float("nan")
    else:
        # Focus on top 20 most important (by mean rank)
        p4_dir_cons = float(p4_stab.sort_values("mean_rank").head(20)["sign_consistency"].mean())

    trigger_dir = (not math.isnan(p4_dir_cons)) and p4_dir_cons < 0.65
    critique_rows.append(
        {
            "rule": "p4_direction_consistency",
            "value": p4_dir_cons,
            "threshold": 0.65,
            "triggered": bool(trigger_dir),
            "action": "downgrade_directional_claims" if trigger_dir else "keep_directional_claims",
            "detail": "mean sign consistency over top-20 P4 features",
        }
    )

    # Rule 3: Tier-delta CI crossing 0
    if tier_tests.empty:
        crossing_rate = float("nan")
        trigger_tier = True
    else:
        crossing = (tier_tests["ci_low"] <= 0) & (tier_tests["ci_high"] >= 0)
        crossing_rate = float(crossing.mean())
        trigger_tier = bool(crossing.any())

    critique_rows.append(
        {
            "rule": "tier_delta_ci_crosses_zero",
            "value": crossing_rate,
            "threshold": 0.0,
            "triggered": bool(trigger_tier),
            "action": "suppress_hard_tier_claims_for_non_significant_features" if trigger_tier else "allow_hard_tier_claims",
            "detail": "share of features where 95% CI includes 0",
        }
    )

    # Rule 4: Benchmark better in same holdout evaluation scope
    holdout = _load_phase4_holdout_results(p)
    p0_mae = float(holdout.loc[holdout["run_id"].eq("P0_profile_baseline"), "mae"].iloc[0])
    p4_mae = float(holdout.loc[holdout["run_id"].eq("P4_ridge_a1_0"), "mae"].iloc[0])
    f0_mae = float(holdout.loc[holdout["run_id"].eq("F0_persistence_baseline"), "mae"].iloc[0])
    f3_mae = float(holdout.loc[holdout["run_id"].eq("F3_rf_90_d12_l2"), "mae"].iloc[0])

    bench_better_policy = p0_mae < p4_mae
    bench_better_forecast = f0_mae < f3_mae
    bench_better_any = bench_better_policy or bench_better_forecast

    critique_rows.append(
        {
            "rule": "benchmark_better_than_primary_holdout_mae",
            "value": float(int(bench_better_any)),
            "threshold": 0.0,
            "triggered": bool(bench_better_any),
            "action": "force_tradeoff_paragraph" if bench_better_any else "none",
            "detail": f"policy={bench_better_policy}, forecast={bench_better_forecast}",
        }
    )

    critique_df = pd.DataFrame(critique_rows)
    critique_df.to_csv(p.phase5_results_dir / "phase5_iterative_critique_log.csv", index=False)

    policy_flags = {
        "directional_claims_downgraded": bool(trigger_dir),
        "tier_hard_claims_restricted": bool(trigger_tier),
        "tradeoff_paragraph_required": bool(bench_better_any),
    }
    (p.phase5_results_dir / "phase5_claim_policy_flags.json").write_text(json.dumps(policy_flags, indent=2))

    return {
        "iterative_log": critique_df,
        "policy_flags": policy_flags,
        "paths": {
            "phase5_iterative_critique_log_csv": str(p.phase5_results_dir / "phase5_iterative_critique_log.csv"),
            "phase5_claim_policy_flags_json": str(p.phase5_results_dir / "phase5_claim_policy_flags.json"),
        },
    }


def _evidence_strength(top10_freq: float, sign_cons: float, tier_sig: bool) -> str:
    if (top10_freq >= 0.67) and (sign_cons >= 0.65) and tier_sig:
        return "strong"
    if (top10_freq >= 0.34) and (sign_cons >= 0.55):
        return "moderate"
    return "weak"


def run_phase5_memo(paths: Phase5Paths | None = None) -> dict[str, Any]:
    p = paths or get_phase5_paths()

    # Ensure upstream outputs
    if not (p.phase5_results_dir / "phase5_iterative_critique_log.csv").exists():
        run_phase5_iterative_refine(paths=p)

    scope = pd.read_csv(p.phase5_results_dir / "phase5_model_scope.csv")
    global_imp = pd.read_csv(p.phase5_results_dir / "phase5_shap_global_importance.csv")
    fold_stability = pd.read_csv(p.phase5_results_dir / "phase5_shap_fold_stability.csv")
    tier_tests = pd.read_csv(p.phase5_results_dir / "phase5_shap_tier_delta_tests.csv")
    baseline_diag = pd.read_csv(p.phase5_results_dir / "phase5_baseline_diagnostics.csv")
    critique_log = pd.read_csv(p.phase5_results_dir / "phase5_iterative_critique_log.csv")
    context_metrics = pd.read_csv(p.phase5_results_dir / "phase5_context_metrics.csv")
    holdout = _load_phase4_holdout_results(p)

    primary_runs = scope.loc[scope["role"].eq("primary"), "run_id"].astype(str).tolist()

    claim_rows: list[dict[str, Any]] = []
    claim_id = 1

    for run_id in primary_runs:
        track = "policy" if run_id.startswith("P") else "forecast"
        hold_top = (
            global_imp.loc[(global_imp["run_id"].astype(str).eq(run_id)) & (global_imp["context"].astype(str).eq("holdout"))]
            .sort_values("rank")
            .head(8)
        )

        for _, r in hold_top.iterrows():
            feat = str(r["feature_name"])
            stab = fold_stability.loc[
                (fold_stability["run_id"].astype(str).eq(run_id)) & (fold_stability["feature_name"].astype(str).eq(feat))
            ]
            top10_freq = float(stab["top10_freq"].iloc[0]) if not stab.empty else 0.0
            sign_cons = float(stab["sign_consistency"].iloc[0]) if not stab.empty else 0.0

            tt = tier_tests.loc[
                (tier_tests["run_id"].astype(str).eq(run_id)) & (tier_tests["feature_name"].astype(str).eq(feat))
            ]
            tier_sig = bool(tt["significant"].iloc[0]) if not tt.empty else False

            strength = _evidence_strength(top10_freq=top10_freq, sign_cons=sign_cons, tier_sig=tier_sig)
            caveat_parts = []
            if sign_cons < 0.65:
                caveat_parts.append("direction over folds is not highly stable")
            if not tier_sig:
                caveat_parts.append("tier contrast is not statistically robust")
            caveat = "; ".join(caveat_parts) if caveat_parts else "none"

            claim_rows.append(
                {
                    "claim_id": f"C{claim_id:03d}",
                    "track": track,
                    "claim_text": f"{feat} is among the dominant explanatory features for {run_id} in holdout SHAP ranking.",
                    "evidence_file": "phase5_shap_global_importance.csv; phase5_shap_fold_stability.csv; phase5_shap_tier_delta_tests.csv",
                    "evidence_strength": strength,
                    "caveat": caveat,
                }
            )
            claim_id += 1

    # Explicit benchmark-tradeoff claims
    p0_mae = float(holdout.loc[holdout["run_id"].eq("P0_profile_baseline"), "mae"].iloc[0])
    p4_mae = float(holdout.loc[holdout["run_id"].eq("P4_ridge_a1_0"), "mae"].iloc[0])
    f0_mae = float(holdout.loc[holdout["run_id"].eq("F0_persistence_baseline"), "mae"].iloc[0])
    f3_mae = float(holdout.loc[holdout["run_id"].eq("F3_rf_90_d12_l2"), "mae"].iloc[0])

    claim_rows.append(
        {
            "claim_id": f"C{claim_id:03d}",
            "track": "policy",
            "claim_text": "Policy benchmark P0 has lower holdout MAE than primary P4, so P4 must be framed as methodological/ex-ante strictness trade-off rather than pure accuracy gain.",
            "evidence_file": "phase4_holdout_results_2025.csv",
            "evidence_strength": "strong",
            "caveat": "accuracy-optimality and policy-interpretability are not aligned",
        }
    )
    claim_id += 1
    claim_rows.append(
        {
            "claim_id": f"C{claim_id:03d}",
            "track": "forecast",
            "claim_text": "Forecast benchmark F0 has slightly lower holdout MAE than primary F3 on full holdout scope, while F3 remains the lag-valid primary interpretative model.",
            "evidence_file": "phase4_holdout_results_2025.csv",
            "evidence_strength": "strong",
            "caveat": "scope mismatch (full-set baseline vs lag-valid primary) must be stated explicitly",
        }
    )

    claims_df = pd.DataFrame(claim_rows)
    claims_df.to_csv(p.phase5_results_dir / "phase5_interpretation_claims.csv", index=False)

    # Memo synthesis
    def _top_feats(run_id: str, n: int = 8) -> list[str]:
        sub = (
            global_imp.loc[(global_imp["run_id"].astype(str).eq(run_id)) & (global_imp["context"].astype(str).eq("holdout"))]
            .sort_values("rank")
            .head(n)
        )
        return sub["feature_name"].astype(str).tolist()

    p4_top = _top_feats("P4_ridge_a1_0", n=10)
    f3_top = _top_feats("F3_rf_90_d12_l2", n=10)

    sig_counts = (
        tier_tests.groupby("run_id", as_index=False)["significant"].mean().rename(columns={"significant": "sig_rate"})
        if not tier_tests.empty
        else pd.DataFrame(columns=["run_id", "sig_rate"])
    )

    flags_path = p.phase5_results_dir / "phase5_claim_policy_flags.json"
    flags = json.loads(flags_path.read_text()) if flags_path.exists() else {}

    memo_lines = [
        "# Phase 5 Interpretation Memo (SHAP + Per-Tier)",
        "",
        "Datum: 2026-03-13",
        "",
        "## Scope and protocol adherence",
        "- Primary models interpreted: `P4_ridge_a1_0` (policy) and `F3_rf_90_d12_l2` (forecast).",
        "- Benchmarks for contrast: `P0_profile_baseline` and `F0_persistence_baseline`.",
        "- Claim basis: fold-stability + holdout context.",
        "- Tier scope: centrum vs vesten/rand (parking detail only as appendix-level context).",
        "",
        "## Primary feature dominance (holdout SHAP)",
        f"- Policy P4 top features: {', '.join(p4_top[:10]) if p4_top else 'n/a'}.",
        f"- Forecast F3 top features: {', '.join(f3_top[:10]) if f3_top else 'n/a'}.",
        "",
        "## Per-tier robustness",
    ]

    if sig_counts.empty:
        memo_lines.append("- Tier-delta significance could not be computed (insufficient data).")
    else:
        for _, r in sig_counts.iterrows():
            memo_lines.append(f"- {r['run_id']}: significant tier-delta share = {float(r['sig_rate']) * 100:.1f}%.")

    memo_lines.extend(
        [
            "",
            "## Baseline contrast and critical interpretation",
            f"- Policy holdout MAE: P0={p0_mae:.4f} vs P4={p4_mae:.4f} (benchmark better={p0_mae < p4_mae}).",
            f"- Forecast holdout MAE: F0={f0_mae:.4f} vs F3={f3_mae:.4f} (benchmark better={f0_mae < f3_mae}).",
            "- Therefore, thesis framing must distinguish predictive minimum-error claims from methodological/interpretability claims.",
            "",
            "## Stability and claim strength policy",
            f"- Directional claims downgraded: {bool(flags.get('directional_claims_downgraded', False))}",
            f"- Hard tier claims restricted: {bool(flags.get('tier_hard_claims_restricted', False))}",
            f"- Trade-off paragraph required: {bool(flags.get('tradeoff_paragraph_required', False))}",
            "",
            "## Strong conclusions",
            "- Fold-safe interpretation workflow is reproducible and track-consistent.",
            "- Feature importance structure is extractable for both tracks without changing Phase 4 model selection.",
            "- Benchmark-vs-primary mismatch is explicit and must remain explicit in thesis reporting.",
            "",
            "## Weaker / conditional conclusions",
            "- Directionality of policy effects should be treated as associative where fold sign consistency is limited.",
            "- Tier contrasts are only claimable as hard differences when CI and permutation test both support them.",
            "",
            "## Required thesis wording implications",
            "- Report prediction quality and interpretability as two non-identical objectives.",
            "- Explicitly mention lag-valid context for forecast primary interpretation.",
            "- Keep benchmark results visible in the same tables as primary interpretations.",
        ]
    )

    memo_path = p.phase5_results_dir / "phase5_interpretation_memo.md"
    memo_path.write_text("\n".join(memo_lines))

    return {
        "claims": claims_df,
        "memo_path": str(memo_path),
        "paths": {
            "phase5_interpretation_claims_csv": str(p.phase5_results_dir / "phase5_interpretation_claims.csv"),
            "phase5_interpretation_memo_md": str(memo_path),
        },
    }
