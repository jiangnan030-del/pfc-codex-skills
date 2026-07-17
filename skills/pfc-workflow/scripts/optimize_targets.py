from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd
from scipy.optimize import differential_evolution

from _campaign_common import (
    default_n_init,
    default_n_iter,
    evaluate_case,
    fit_all_models,
    load_config,
    load_runs,
    maybe_optuna_tpe,
    parameter_defs,
    propose_bayes_candidate,
    propose_rsm_candidate,
    row_to_params,
    sample_lhs,
    save_model_bundle,
    save_runs,
    stop_objective,
    target_defs,
    workspace_dir,
)


def ensure_initial_runs(cfg: dict, runs: pd.DataFrame, runs_path: Path) -> pd.DataFrame:
    params = parameter_defs(cfg)
    if not runs.empty:
        return runs
    lhs = sample_lhs(params, n_samples=default_n_init(cfg, len(params)), seed=int(cfg.get("random_seed", 42)))
    for _, row in lhs.iterrows():
        record = evaluate_case(cfg, row_to_params(row, params), sample_id=str(row["sample_id"]), phase="lhs", runs_df=runs)
        runs = pd.concat([runs, pd.DataFrame([record])], ignore_index=True)
    save_runs(runs, runs_path)
    return runs


def append_record(runs: pd.DataFrame, record: dict, runs_path: Path) -> pd.DataFrame:
    runs = pd.concat([runs, pd.DataFrame([record])], ignore_index=True)
    save_runs(runs, runs_path)
    return runs


def run_bayes(cfg: dict, runs: pd.DataFrame, runs_path: Path) -> pd.DataFrame:
    n_iter = default_n_iter(cfg)
    stop_at = stop_objective(cfg)
    for iteration in range(1, n_iter + 1):
        engine = str(cfg.get("optimizer", {}).get("engine", "gp_ei")).lower()
        if engine == "optuna_tpe":
            candidate, meta = maybe_optuna_tpe(cfg, runs)
        else:
            candidate, meta = propose_bayes_candidate(cfg, runs, seed_offset=iteration)
        record = evaluate_case(cfg, candidate, sample_id=f"bayes_{iteration:04d}", phase="bayes", runs_df=runs)
        record["acquisition_score"] = meta.get("acquisition_score")
        runs = append_record(runs, record, runs_path)
        if stop_at is not None and float(record["objective"]) <= stop_at:
            break
    return runs


def run_rsm(cfg: dict, runs: pd.DataFrame, runs_path: Path) -> pd.DataFrame:
    n_iter = default_n_iter(cfg)
    stop_at = stop_objective(cfg)
    for iteration in range(1, n_iter + 1):
        candidate, meta = propose_rsm_candidate(cfg, runs)
        record = evaluate_case(cfg, candidate, sample_id=f"rsm_{iteration:04d}", phase="rsm", runs_df=runs)
        record["predicted_objective"] = meta.get("predicted_objective")
        runs = append_record(runs, record, runs_path)
        if stop_at is not None and float(record["objective"]) <= stop_at:
            break
    return runs


def run_de(cfg: dict, runs: pd.DataFrame, runs_path: Path) -> pd.DataFrame:
    params = parameter_defs(cfg)
    budget = cfg.get("budget", {})
    total_budget = int(budget.get("n_init", default_n_init(cfg, len(params))) + budget.get("n_iter", default_n_iter(cfg)))
    dim = len(params)
    requested_population = int(cfg.get("optimizer", {}).get("de_popsize", max(8, 4 * dim)))
    requested_population = max(requested_population, dim + 1)
    requested_population = min(requested_population, max(dim + 1, total_budget // 2))
    popsize = max(1, math.ceil(requested_population / max(dim, 1)))
    effective_population = popsize * dim
    maxiter = max(1, total_budget // max(effective_population, 1) - 1)
    bounds = [(param.lower, param.upper) for param in params]
    runs_box = [runs]

    def objective(vector) -> float:
        candidate = {}
        for value, param in zip(vector, params):
            candidate[param.name] = int(round(float(value))) if param.integer else float(value)
        record = evaluate_case(
            cfg,
            candidate,
            sample_id=f"de_{len(runs_box[0]) + 1:04d}",
            phase="de",
            runs_df=runs_box[0],
        )
        runs_box[0] = append_record(runs_box[0], record, runs_path)
        return float(record["objective"])

    differential_evolution(
        objective,
        bounds=bounds,
        seed=int(cfg.get("optimizer", {}).get("seed", cfg.get("random_seed", 42))),
        workers=1,
        updating="deferred",
        popsize=popsize,
        maxiter=maxiter,
        polish=False,
        init="latinhypercube",
        atol=0.0,
        tol=0.0,
    )
    return runs_box[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Optimize calibration targets with bayes, rsm, or de modes.")
    parser.add_argument("config", help="Path to calibration campaign YAML")
    parser.add_argument("--mode", choices=["bayes", "rsm", "de"], default=None, help="Override optimizer mode")
    parser.add_argument("--runs", default=None, help="Path to runs.csv; defaults to workspace/runs.csv")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.mode:
        cfg.setdefault("optimizer", {})["mode"] = args.mode
    mode = str(cfg.get("optimizer", {}).get("mode", "bayes")).lower()
    params = parameter_defs(cfg)
    targets = target_defs(cfg)
    wdir = workspace_dir(cfg)
    runs_path = Path(args.runs) if args.runs else wdir / "runs.csv"
    runs = load_runs(runs_path, params, targets)

    if mode in {"bayes", "rsm"}:
        runs = ensure_initial_runs(cfg, runs, runs_path)
    if mode == "bayes":
        runs = run_bayes(cfg, runs, runs_path)
    elif mode == "rsm":
        runs = run_rsm(cfg, runs, runs_path)
    elif mode == "de":
        runs = run_de(cfg, runs, runs_path)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    bundle = fit_all_models(cfg, runs)
    report_path, _ = save_model_bundle(bundle, cfg)
    best = runs.sort_values("objective").iloc[0].to_dict()
    summary = {
        "mode": mode,
        "n_runs": int(len(runs)),
        "best_objective": float(best["objective"]),
        "best_sample_id": best["sample_id"],
        "surrogate_report": str(report_path),
    }
    (wdir / "optimization_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
