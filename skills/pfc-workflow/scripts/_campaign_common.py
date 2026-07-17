from __future__ import annotations

import json
import math
import pickle
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from scipy.stats import norm, qmc
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

try:
    import optuna
except ImportError:  # optional
    optuna = None

STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
DEFAULT_FAILURE_PENALTY = 1.0e6


@dataclass
class ParameterDef:
    name: str
    lower: float
    upper: float
    scale: str = "linear"
    integer: bool = False


@dataclass
class TargetDef:
    name: str
    value: float
    tolerance: float
    weight: float = 1.0
    direction: str = "match"


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8-sig") as handle:
        cfg = yaml.safe_load(handle)
    if not isinstance(cfg, dict):
        raise ValueError("Config must be a mapping.")
    cfg["_config_path"] = str(config_path.resolve())
    cfg.setdefault("campaign_name", config_path.stem)
    cfg.setdefault(
        "workspace_dir",
        str((config_path.parent / "campaign_outputs" / cfg["campaign_name"]).resolve()),
    )
    cfg.setdefault("random_seed", 42)
    cfg.setdefault("budget", {})
    cfg.setdefault("optimizer", {})
    cfg.setdefault("runner", {})
    return cfg


def workspace_dir(cfg: dict[str, Any]) -> Path:
    path = Path(cfg["workspace_dir"]).resolve()
    path.mkdir(parents=True, exist_ok=True)
    (path / "artifacts").mkdir(parents=True, exist_ok=True)
    (path / "models").mkdir(parents=True, exist_ok=True)
    (path / "plots").mkdir(parents=True, exist_ok=True)
    return path


def parameter_defs(cfg: dict[str, Any]) -> list[ParameterDef]:
    items = cfg.get("parameters", [])
    if not items:
        raise ValueError("Config must define parameters.")
    result = []
    for item in items:
        result.append(
            ParameterDef(
                name=item["name"],
                lower=float(item["lower"]),
                upper=float(item["upper"]),
                scale=str(item.get("scale", "linear")).lower(),
                integer=bool(item.get("integer", False)),
            )
        )
    return result


def target_defs(cfg: dict[str, Any]) -> list[TargetDef]:
    items = cfg.get("targets", [])
    if not items:
        raise ValueError("Config must define targets.")
    result = []
    for item in items:
        result.append(
            TargetDef(
                name=item["name"],
                value=float(item["value"]),
                tolerance=float(item["tolerance"]),
                weight=float(item.get("weight", 1.0)),
                direction=str(item.get("direction", "match")).lower(),
            )
        )
    return result


def default_n_init(cfg: dict[str, Any], d: int) -> int:
    return int(cfg.get("budget", {}).get("n_init", max(24, 8 * d)))


def default_n_iter(cfg: dict[str, Any]) -> int:
    return int(cfg.get("budget", {}).get("n_iter", 12))


def stop_objective(cfg: dict[str, Any]) -> float | None:
    value = cfg.get("budget", {}).get("stop_objective")
    return None if value is None else float(value)


def sample_lhs(
    params: list[ParameterDef],
    n_samples: int,
    seed: int,
    optimization: str = "random-cd",
) -> pd.DataFrame:
    sampler = qmc.LatinHypercube(d=len(params), seed=seed, optimization=optimization)
    unit = sampler.random(n=n_samples)
    rows: list[dict[str, Any]] = []
    for idx, u in enumerate(unit, start=1):
        row: dict[str, Any] = {"sample_id": f"lhs_{idx:04d}", "phase": "lhs"}
        for param, raw in zip(params, u):
            if param.scale == "log":
                lo = math.log10(param.lower)
                hi = math.log10(param.upper)
                value = 10 ** (lo + raw * (hi - lo))
            else:
                value = param.lower + raw * (param.upper - param.lower)
            if param.integer:
                value = int(round(value))
                value = min(max(value, int(math.ceil(param.lower))), int(math.floor(param.upper)))
            row[param.name] = float(value) if not param.integer else int(value)
        rows.append(row)
    return pd.DataFrame(rows)


def row_to_params(row: pd.Series | dict[str, Any], params: list[ParameterDef]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for param in params:
        value = row[param.name]
        result[param.name] = int(round(float(value))) if param.integer else float(value)
    return result


def objective_from_metrics(
    metrics: dict[str, Any],
    targets: list[TargetDef],
    penalty: float = DEFAULT_FAILURE_PENALTY,
) -> tuple[float, dict[str, float], list[str]]:
    total = 0.0
    details: dict[str, float] = {}
    missing: list[str] = []
    for target in targets:
        if target.name not in metrics or metrics[target.name] is None:
            missing.append(target.name)
            total += penalty
            details[target.name] = float(penalty)
            continue
        metric_value = float(metrics[target.name])
        tol = max(abs(target.tolerance), 1.0e-12)
        if target.direction == "match":
            residual = (metric_value - target.value) / tol
        elif target.direction == "upper":
            residual = max(0.0, metric_value - target.value) / tol
        elif target.direction == "lower":
            residual = max(0.0, target.value - metric_value) / tol
        else:
            raise ValueError(f"Unsupported target direction: {target.direction}")
        contrib = target.weight * residual ** 2
        total += contrib
        details[target.name] = float(contrib)
    return float(total), details, missing


def ensure_runs_columns(
    df: pd.DataFrame,
    params: list[ParameterDef],
    targets: list[TargetDef],
) -> pd.DataFrame:
    expected = [
        "evaluation_id",
        "sample_id",
        "phase",
        "status",
        "elapsed_sec",
        "objective",
        "seed",
        "artifact_dir",
        "failure_reason",
    ]
    expected += [f"param__{param.name}" for param in params]
    expected += [f"metric__{target.name}" for target in targets]
    expected += [f"contrib__{target.name}" for target in targets]
    for column in expected:
        if column not in df.columns:
            df[column] = np.nan
    return df


def load_runs(path: Path, params: list[ParameterDef], targets: list[TargetDef]) -> pd.DataFrame:
    if not path.exists():
        return ensure_runs_columns(pd.DataFrame(), params, targets)
    return ensure_runs_columns(pd.read_csv(path), params, targets)


def save_runs(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def next_evaluation_id(runs_df: pd.DataFrame) -> int:
    if runs_df.empty or "evaluation_id" not in runs_df:
        return 1
    series = pd.to_numeric(runs_df["evaluation_id"], errors="coerce").dropna()
    return 1 if series.empty else int(series.max()) + 1


def write_params_yaml(params_dict: dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(params_dict, handle, sort_keys=False, allow_unicode=True)


def synthetic_metrics(function_name: str, params_dict: dict[str, Any]) -> dict[str, float]:
    if function_name == "sphere":
        x = np.array(list(params_dict.values()), dtype=float)
        return {"loss": float(np.sum(x ** 2))}
    if function_name == "branin":
        x1 = float(params_dict.get("x1"))
        x2 = float(params_dict.get("x2"))
        a = 1.0
        b = 5.1 / (4.0 * math.pi ** 2)
        c = 5.0 / math.pi
        r = 6.0
        s = 10.0
        t = 1.0 / (8.0 * math.pi)
        loss = a * (x2 - b * x1 ** 2 + c * x1 - r) ** 2 + s * (1.0 - t) * math.cos(x1) + s
        return {"loss": float(loss)}
    if function_name == "mock_pfc_calibration":
        emod = float(params_dict.get("emod", 3.2e6))
        pb_ten = float(params_dict.get("pb_ten", 2.2e5))
        pb_coh = float(params_dict.get("pb_coh", 3.2e5))
        pb_fa = float(params_dict.get("pb_fa", 12.0))
        elastic_modulus = 1.1 + 0.55 * math.log10(emod / 1.0e6) + 0.0000015 * (pb_coh - 2.8e5)
        ucs = 0.11 + 2.6e-7 * pb_ten + 2.1e-7 * pb_coh + 0.0012 * (pb_fa - 10.0)
        peak_strain = 0.085 - 0.0060 * math.log10(emod / 1.0e6) - 0.00006 * (pb_fa - 10.0) - 1.5e-8 * (pb_ten - 2.0e5)
        return {
            "elastic_modulus": float(elastic_modulus),
            "ucs": float(ucs),
            "peak_strain": float(peak_strain),
        }
    raise ValueError(f"Unsupported synthetic function: {function_name}")


def evaluate_case(
    cfg: dict[str, Any],
    params_dict: dict[str, Any],
    sample_id: str,
    phase: str,
    runs_df: pd.DataFrame,
) -> dict[str, Any]:
    params = parameter_defs(cfg)
    targets = target_defs(cfg)
    runner = cfg.get("runner", {})
    wdir = workspace_dir(cfg)
    eval_id = next_evaluation_id(runs_df)
    artifact_dir = wdir / "artifacts" / f"{eval_id:04d}_{sample_id}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    params_file = artifact_dir / "params.yaml"
    metrics_file = artifact_dir / "metrics.json"
    stdout_file = artifact_dir / "stdout.txt"
    stderr_file = artifact_dir / "stderr.txt"
    write_params_yaml(params_dict, params_file)

    start = time.perf_counter()
    status = STATUS_SUCCESS
    failure_reason = ""
    metrics: dict[str, Any] = {}
    try:
        if runner.get("kind", "synthetic") == "synthetic":
            metrics = synthetic_metrics(str(runner.get("function", "mock_pfc_calibration")), params_dict)
            metrics_file.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            template = runner.get("command_template")
            if not template:
                raise ValueError("runner.command_template is required for command runners.")
            format_map = {
                "params_file": str(params_file),
                "metrics_file": str(metrics_file),
                "artifact_dir": str(artifact_dir),
                "sample_id": sample_id,
                **params_dict,
            }
            command = template.format(**format_map)
            completed = subprocess.run(
                command,
                shell=True,
                cwd=runner.get("workdir") or None,
                timeout=float(runner.get("timeout_sec", 3600)),
                capture_output=True,
                text=True,
                check=False,
            )
            stdout_file.write_text(completed.stdout or "", encoding="utf-8")
            stderr_file.write_text(completed.stderr or "", encoding="utf-8")
            if completed.returncode != 0:
                raise RuntimeError(f"Command runner returned {completed.returncode}")
            if not metrics_file.exists():
                raise FileNotFoundError(f"Metrics file not produced: {metrics_file}")
            metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
            if not isinstance(metrics, dict):
                raise ValueError("Metrics file must contain a JSON object.")
    except Exception as exc:  # noqa: BLE001
        status = STATUS_FAILED
        failure_reason = str(exc)
        metrics = {}

    elapsed = time.perf_counter() - start
    objective, contributions, missing = objective_from_metrics(metrics, targets)
    if status == STATUS_FAILED:
        objective += DEFAULT_FAILURE_PENALTY
    if missing:
        suffix = "missing_metrics=" + ",".join(missing)
        failure_reason = f"{failure_reason}; {suffix}" if failure_reason else suffix

    record: dict[str, Any] = {
        "evaluation_id": eval_id,
        "sample_id": sample_id,
        "phase": phase,
        "status": status,
        "elapsed_sec": float(elapsed),
        "objective": float(objective),
        "seed": cfg.get("random_seed", 42),
        "artifact_dir": str(artifact_dir),
        "failure_reason": failure_reason,
    }
    for param in params:
        record[f"param__{param.name}"] = params_dict[param.name]
    for target in targets:
        record[f"metric__{target.name}"] = metrics.get(target.name)
        record[f"contrib__{target.name}"] = contributions.get(target.name)
    return record


def successful_runs(runs_df: pd.DataFrame) -> pd.DataFrame:
    if runs_df.empty:
        return runs_df.copy()
    return runs_df[runs_df["status"] == STATUS_SUCCESS].reset_index(drop=True)


def training_data(runs_df: pd.DataFrame, params: list[ParameterDef]) -> tuple[np.ndarray, np.ndarray]:
    clean = successful_runs(runs_df)
    if clean.empty:
        raise ValueError("No successful runs are available.")
    x = clean[[f"param__{param.name}" for param in params]].to_numpy(dtype=float)
    y = clean["objective"].to_numpy(dtype=float)
    return x, y


def build_models(seed: int) -> dict[str, Any]:
    kernel = ConstantKernel(1.0, (1.0e-3, 1.0e3)) * RBF(
        length_scale=1.0,
        length_scale_bounds=(1.0e-3, 1.0e3),
    ) + WhiteKernel(noise_level=1.0e-6, noise_level_bounds=(1.0e-10, 1.0))
    return {
        "gp": GaussianProcessRegressor(
            kernel=kernel,
            normalize_y=True,
            random_state=seed,
            n_restarts_optimizer=2,
        ),
        "rf": RandomForestRegressor(n_estimators=300, random_state=seed, n_jobs=1),
        "rsm": Pipeline(
            [
                ("poly", PolynomialFeatures(degree=2, include_bias=False)),
                ("linear", LinearRegression()),
            ]
        ),
    }


def cross_validate_model(model: Any, x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    if len(y) < 4:
        model.fit(x, y)
        pred = model.predict(x)
    else:
        cv = KFold(n_splits=min(5, len(y)), shuffle=True, random_state=42)
        pred = cross_val_predict(model, x, y, cv=cv)
    rmse = float(np.sqrt(mean_squared_error(y, pred)))
    mae = float(mean_absolute_error(y, pred))
    r2 = float(r2_score(y, pred)) if len(np.unique(y)) > 1 else float("nan")
    return {"rmse": rmse, "mae": mae, "r2": r2}


def fit_all_models(cfg: dict[str, Any], runs_df: pd.DataFrame) -> dict[str, Any]:
    params = parameter_defs(cfg)
    x, y = training_data(runs_df, params)
    seed = int(cfg.get("optimizer", {}).get("seed", cfg.get("random_seed", 42)))
    models = build_models(seed)
    reports: dict[str, Any] = {}
    fitted: dict[str, Any] = {}
    for name, model in models.items():
        reports[name] = cross_validate_model(model, x, y)
        model.fit(x, y)
        fitted[name] = model
    selected = "rf" if len(params) > 6 or len(y) > 120 else "gp"
    importances = getattr(fitted["rf"], "feature_importances_", None)
    feature_importance = {}
    if importances is not None:
        feature_importance = {
            param.name: float(value)
            for param, value in zip(params, importances)
        }
    return {
        "selected_model": selected,
        "model_reports": reports,
        "models": fitted,
        "feature_importance": feature_importance,
        "x": x,
        "y": y,
    }


def save_model_bundle(bundle: dict[str, Any], cfg: dict[str, Any], report_name: str = "surrogate_report.json") -> tuple[Path, Path]:
    wdir = workspace_dir(cfg)
    report_path = wdir / report_name
    model_path = wdir / "models" / "surrogate_models.pkl"
    payload = {
        "selected_model": bundle["selected_model"],
        "model_reports": bundle["model_reports"],
        "feature_importance": bundle["feature_importance"],
        "n_samples": int(len(bundle["y"])),
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    with model_path.open("wb") as handle:
        pickle.dump(bundle["models"], handle)
    return report_path, model_path


def random_candidate_matrix(params: list[ParameterDef], n_candidates: int, seed: int) -> np.ndarray:
    gen = np.random.default_rng(seed)
    rows = []
    for _ in range(n_candidates):
        row = []
        for param in params:
            raw = gen.random()
            if param.scale == "log":
                lo = math.log10(param.lower)
                hi = math.log10(param.upper)
                value = 10 ** (lo + raw * (hi - lo))
            else:
                value = param.lower + raw * (param.upper - param.lower)
            if param.integer:
                value = int(round(value))
                value = min(max(value, int(math.ceil(param.lower))), int(math.floor(param.upper)))
            row.append(float(value))
        rows.append(row)
    return np.asarray(rows, dtype=float)


def estimate_mean_std(model_name: str, model: Any, x_candidates: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if model_name == "gp":
        mean, std = model.predict(x_candidates, return_std=True)
        return np.asarray(mean, dtype=float), np.asarray(std, dtype=float)
    if model_name == "rf":
        tree_predictions = np.stack([tree.predict(x_candidates) for tree in model.estimators_], axis=0)
        return tree_predictions.mean(axis=0), tree_predictions.std(axis=0)
    mean = model.predict(x_candidates)
    std = np.full_like(mean, fill_value=max(np.std(mean), 1.0e-6), dtype=float)
    return np.asarray(mean, dtype=float), np.asarray(std, dtype=float)


def expected_improvement(y_best: float, mean: np.ndarray, std: np.ndarray, xi: float = 0.01) -> np.ndarray:
    std = np.maximum(std, 1.0e-9)
    improvement = y_best - mean - xi
    z = improvement / std
    return improvement * norm.cdf(z) + std * norm.pdf(z)


def candidate_dict(vector: np.ndarray, params: list[ParameterDef]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for value, param in zip(vector, params):
        result[param.name] = int(round(float(value))) if param.integer else float(value)
    return result


def propose_bayes_candidate(
    cfg: dict[str, Any],
    runs_df: pd.DataFrame,
    seed_offset: int = 0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    params = parameter_defs(cfg)
    bundle = fit_all_models(cfg, runs_df)
    selected_name = bundle["selected_model"]
    model = bundle["models"][selected_name]
    pool = int(cfg.get("optimizer", {}).get("candidate_pool", 5000))
    seed = int(cfg.get("optimizer", {}).get("seed", cfg.get("random_seed", 42))) + seed_offset
    candidates = random_candidate_matrix(params, pool, seed)
    mean, std = estimate_mean_std(selected_name, model, candidates)
    y_best = float(np.min(bundle["y"]))
    acquisition = str(cfg.get("optimizer", {}).get("acquisition", "ei")).lower()
    if acquisition != "ei":
        raise ValueError(f"Unsupported acquisition: {acquisition}")
    scores = expected_improvement(y_best, mean, std)
    best_idx = int(np.argmax(scores))
    return candidate_dict(candidates[best_idx], params), {
        "bundle": bundle,
        "acquisition_score": float(scores[best_idx]),
    }


def propose_rsm_candidate(cfg: dict[str, Any], runs_df: pd.DataFrame) -> tuple[dict[str, Any], dict[str, Any]]:
    from scipy.optimize import minimize

    params = parameter_defs(cfg)
    bundle = fit_all_models(cfg, runs_df)
    model = bundle["models"]["rsm"]
    clean = successful_runs(runs_df).sort_values("objective").reset_index(drop=True)
    starts = clean[[f"param__{param.name}" for param in params]].head(min(5, len(clean))).to_numpy(dtype=float)
    bounds = [(param.lower, param.upper) for param in params]
    best_x = starts[0]
    best_y = float("inf")

    def surrogate_objective(x: np.ndarray) -> float:
        return float(model.predict(np.asarray(x, dtype=float).reshape(1, -1))[0])

    for start in starts:
        result = minimize(surrogate_objective, x0=start, bounds=bounds, method="L-BFGS-B")
        if result.fun < best_y:
            best_y = float(result.fun)
            best_x = np.asarray(result.x, dtype=float)
    return candidate_dict(best_x, params), {"bundle": bundle, "predicted_objective": best_y}


def maybe_optuna_tpe(cfg: dict[str, Any], runs_df: pd.DataFrame) -> tuple[dict[str, Any], dict[str, Any]]:
    if optuna is None:
        raise RuntimeError("optuna is not installed. Install optuna or use engine=gp_ei.")
    params = parameter_defs(cfg)
    bundle = fit_all_models(cfg, runs_df)
    selected_name = "rf" if bundle["selected_model"] == "rf" else "gp"
    model = bundle["models"][selected_name]
    seed = int(cfg.get("optimizer", {}).get("seed", cfg.get("random_seed", 42)))

    def objective(trial: Any) -> float:
        values = []
        for param in params:
            if param.scale == "log":
                value = trial.suggest_float(param.name, param.lower, param.upper, log=True)
            elif param.integer:
                value = trial.suggest_int(param.name, int(math.ceil(param.lower)), int(math.floor(param.upper)))
            else:
                value = trial.suggest_float(param.name, param.lower, param.upper)
            values.append(float(value))
        return float(model.predict(np.asarray(values, dtype=float).reshape(1, -1))[0])

    study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=seed))
    study.optimize(objective, n_trials=256, show_progress_bar=False)
    vector = np.asarray([study.best_params[param.name] for param in params], dtype=float)
    return candidate_dict(vector, params), {
        "bundle": bundle,
        "optuna_best_value": float(study.best_value),
    }
