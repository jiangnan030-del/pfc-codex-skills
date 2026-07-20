"""Reproducible CPB2D intact calibration adapter for PFC 6.0."""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import time
import uuid
from typing import Any

import yaml

from cpb2d_scaffold import create_project

BASELINE_PARAMETERS = {
    "linear_emod_pa": 2_200_000.0,
    "bond_emod_pa": 1_000_000.0,
    "pb_ten_pa": 50_000.0,
    "pb_coh_pa": 80_000.0,
}
FIXED_PARAMETERS = {"kratio": 1.5, "pb_fa_deg": 27.0, "friction": 0.8}
TARGET_FINAL_STRAIN = 0.175557485
BRIDGE_URL = "ws://localhost:9001"

TARGET_WEIGHTS = {
    "peak_stress_mpa": 2.0,
    "peak_strain": 1.5,
    "middle_secant_stiffness_mpa": 1.0,
    "late_secant_stiffness_mpa": 1.0,
    "final_peak_ratio": 0.5,
}
TARGET_RELATIVE_TOLERANCES = {
    "peak_stress_mpa": 0.05,
    "peak_strain": 0.08,
    "middle_secant_stiffness_mpa": 0.12,
    "late_secant_stiffness_mpa": 0.15,
    "final_peak_ratio": 0.08,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _interpolate(data: list[tuple[float, float]], x: float, end: int | None = None) -> float:
    limit = len(data) if end is None else end + 1
    if x <= data[0][0]:
        return data[0][1]
    previous = data[0]
    for current in data[1:limit]:
        if current[0] >= x:
            x0, y0 = previous
            x1, y1 = current
            return y1 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        previous = current
    return data[limit - 1][1]


def _secant(data: list[tuple[float, float]], peak_index: int, peak_strain: float, a: float, b: float) -> float:
    x0 = peak_strain * a
    x1 = peak_strain * b
    return (_interpolate(data, x1, peak_index) - _interpolate(data, x0, peak_index)) / (x1 - x0)


def extract_curve_metrics(curve_path: Path, target_final_strain: float = TARGET_FINAL_STRAIN) -> dict[str, float | int]:
    with curve_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not {"strain", "stress_mpa"}.issubset(rows[0]):
        raise ValueError("stress_strain.csv has no usable strain/stress_mpa rows")
    points: list[tuple[float, float, int]] = []
    for row in rows:
        strain = abs(float(row["strain"]))
        stress = float(row["stress_mpa"])
        crack = int(round(float(row.get("crack_num") or 0)))
        if math.isfinite(strain) and math.isfinite(stress):
            points.append((strain, stress, crack))
    if len(points) < 2:
        raise ValueError("stress_strain.csv has fewer than two finite rows")
    points.sort(key=lambda item: item[0])
    curve = [(item[0], item[1]) for item in points]
    peak_index = max(range(len(points)), key=lambda index: points[index][1])
    peak_strain, peak_stress, _ = points[peak_index]
    if peak_stress <= 0 or peak_strain <= 0:
        raise ValueError("curve has no positive peak")
    final_stress = _interpolate(curve, min(target_final_strain, curve[-1][0]))
    return {
        "peak_stress_mpa": peak_stress,
        "peak_strain": peak_strain,
        "early_secant_stiffness_mpa": _secant(curve, peak_index, peak_strain, 0.1, 0.4),
        "middle_secant_stiffness_mpa": _secant(curve, peak_index, peak_strain, 0.3, 0.7),
        "late_secant_stiffness_mpa": _secant(curve, peak_index, peak_strain, 0.4, 0.8),
        "final_peak_ratio": final_stress / peak_stress,
        "final_crack_count": points[-1][2],
        "curve_rows": len(points),
        "curve_final_strain": points[-1][0],
        "curve_final_stress_mpa": points[-1][1],
    }


def normalized_curve_rmse(simulation: Path, experiment: Path, n_points: int = 200) -> float:
    def read(path: Path) -> list[tuple[float, float]]:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            result = [(abs(float(row["strain"])), float(row["stress_mpa"])) for row in csv.DictReader(stream)]
        return sorted(result)

    sim = read(simulation)
    exp = read(experiment)
    max_strain = min(sim[-1][0], exp[-1][0])
    peak = max(value for _, value in exp)
    errors = []
    for index in range(n_points):
        strain = max_strain * index / (n_points - 1)
        errors.append((_interpolate(sim, strain) - _interpolate(exp, strain)) / peak)
    return math.sqrt(sum(value * value for value in errors) / len(errors))


def calibration_objective(metrics: dict[str, Any], targets: dict[str, float]) -> tuple[float, dict[str, float]]:
    total = 0.0
    details: dict[str, float] = {}
    for name, weight in TARGET_WEIGHTS.items():
        value = float(metrics[name])
        target = float(targets[name])
        tolerance = max(abs(target) * TARGET_RELATIVE_TOLERANCES[name], 1.0e-12)
        contribution = weight * ((value - target) / tolerance) ** 2
        details[name] = contribution
        total += contribution
    return total, details


def target_compliance(metrics: dict[str, Any], targets: dict[str, float]) -> dict[str, Any]:
    errors = {name: abs(float(metrics[name]) - value) / abs(value) for name, value in targets.items()}
    limits = TARGET_RELATIVE_TOLERANCES
    return {"relative_errors": errors, "limits": limits, "all_met": all(errors[name] <= limits[name] for name in limits)}


def _intake(params: dict[str, float]) -> dict[str, Any]:
    required = set(BASELINE_PARAMETERS)
    if set(params) != required:
        raise ValueError(f"params must contain exactly {sorted(required)}")
    return {
        "project": {"slug": "intact_3_calibration", "title": "intact-3 CPB2D calibration", "pfc_version": "6.0", "random_seed_base": 31000},
        "specimen": {"width_mm": 40.0, "height_mm": 40.0, "particle_radius_min_mm": 0.30, "particle_radius_max_mm": 0.50, "target_porosity": 0.15, "density_kg_m3": 1900.0, "damping": 0.70},
        "contact_model": {"family": "linearpbond", **params, **FIXED_PARAMETERS},
        "loading": {"wall_velocity_m_s": 0.10, "peak_drop_fraction": 0.80, "target_peak_strain_guess": 0.10, "stage_fractions": [0.25, 0.50, 0.75, 0.90], "history_interval": 10},
        "outputs": {"stress_strain": True, "crack_counts": True, "heavy_ae": False},
        "cases": [{"case_name": "intact", "family": "intact", "enabled": True, "experiment_file": "data/experimental/intact_3_stress_strain.csv", "crack_enabled": False}],
        "assumptions": ["Calibration candidate; fixed PFC6 seed and geometry.", "Only the intact case is enabled."],
    }


def materialize_case(params: dict[str, float], artifact_dir: Path) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    intake_path = artifact_dir / "intake.yaml"
    intake_path.write_text(yaml.safe_dump(_intake(params), sort_keys=False), encoding="utf-8")
    project = artifact_dir / "project"
    if project.exists():
        shutil.rmtree(project)
    create_project(intake_path, project)
    return project / "pfc_cases" / "intact"


async def _execute_bridge(code: str, timeout_sec: int) -> dict[str, Any]:
    import websockets

    wrapped = f"exec(compile({json.dumps(code)}, '<cpb2d-calibration>', 'exec'))"
    message = {"type": "execute_code", "request_id": str(uuid.uuid4()), "code": wrapped, "timeout_ms": timeout_sec * 1000}
    async with websockets.connect(BRIDGE_URL, compression=None, max_size=50 * 2**20, ping_interval=None, ping_timeout=None) as socket:
        await socket.send(json.dumps(message))
        return json.loads(await asyncio.wait_for(socket.recv(), timeout=timeout_sec + 60))


def run_case(case_dir: Path, timeout_sec: int = 900) -> dict[str, Any]:
    code = "\n".join(["import os", "import itasca", f"os.chdir(r'{case_dir.resolve().as_posix()}')", "itasca.command(\"program call 'run_all.dat'\")"])
    started = time.perf_counter()
    response = asyncio.run(_execute_bridge(code, timeout_sec))
    elapsed = time.perf_counter() - started
    if response.get("status") == "error":
        raise RuntimeError(json.dumps(response, ensure_ascii=False)[-4000:])
    return {"elapsed_sec": elapsed, "bridge_response": response}


def derive_runtime_status(case_dir: Path, metrics: dict[str, Any]) -> dict[str, Any]:
    peak_strain = float(metrics["peak_strain"])
    final_strain = float(metrics["curve_final_strain"])
    threshold_d = 0.10 * 0.90
    max_abs_strain = 0.20
    status = {
        "peak_confirmed": final_strain > peak_strain and float(metrics["curve_final_stress_mpa"]) < float(metrics["peak_stress_mpa"]) * 0.995,
        "safety_stop": final_strain >= max_abs_strain * 0.995,
        "stage_fallback": final_strain < threshold_d,
        "stage_d_threshold": threshold_d,
        "max_abs_strain": max_abs_strain,
    }
    (case_dir / "runtime_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    return status


def validate_runtime_outputs(case_dir: Path) -> dict[str, Any]:
    required = ["final.sav", "peak.sav", "stage_a.sav", "stage_b.sav", "stage_c.sav", "stage_d.sav", "stress_strain.csv"]
    for name in required:
        path = case_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"missing or empty runtime output: {name}")
    status_path = case_dir / "runtime_status.json"
    if not status_path.is_file():
        raise ValueError("missing runtime_status.json")
    status = json.loads(status_path.read_text(encoding="utf-8"))
    if not status.get("peak_confirmed"):
        raise ValueError("unconfirmed peak is not eligible for calibration")
    if status.get("safety_stop"):
        raise ValueError("maximum-strain safety stop is not eligible for calibration")
    if status.get("stage_fallback"):
        raise ValueError("stage fallback is not eligible for calibration")
    return status


def evaluate(params: dict[str, float], artifact_dir: Path, experiment_curve: Path, targets: dict[str, float], timeout_sec: int = 900) -> dict[str, Any]:
    case_dir = materialize_case(params, artifact_dir)
    run_info = run_case(case_dir, timeout_sec)
    metrics = extract_curve_metrics(case_dir / "stress_strain.csv")
    status = derive_runtime_status(case_dir, metrics)
    validate_runtime_outputs(case_dir)
    metrics["normalized_curve_rmse"] = normalized_curve_rmse(case_dir / "stress_strain.csv", experiment_curve)
    objective, contributions = calibration_objective(metrics, targets)
    compliance = target_compliance(metrics, targets)
    payload = {**metrics, "objective": objective, "contributions": contributions, "compliance": compliance, "runtime_status": status, "elapsed_sec": run_info["elapsed_sec"], "parameters": params, "curve_sha256": _sha256(case_dir / "stress_strain.csv")}
    (artifact_dir / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize and evaluate one CPB2D intact calibration candidate")
    parser.add_argument("--params-file", required=True, type=Path)
    parser.add_argument("--metrics-file", required=True, type=Path)
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--experiment-curve", required=True, type=Path)
    parser.add_argument("--targets-file", required=True, type=Path)
    parser.add_argument("--timeout-sec", type=int, default=900)
    parser.add_argument("--materialize-only", action="store_true")
    args = parser.parse_args()
    params = yaml.safe_load(args.params_file.read_text(encoding="utf-8"))
    targets_doc = json.loads(args.targets_file.read_text(encoding="utf-8"))
    targets = targets_doc.get("targets", targets_doc)
    if args.materialize_only:
        case_dir = materialize_case(params, args.artifact_dir)
        args.metrics_file.write_text(json.dumps({"case_dir": str(case_dir)}, indent=2), encoding="utf-8")
        return 0
    metrics = evaluate(params, args.artifact_dir, args.experiment_curve, targets, args.timeout_sec)
    args.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
