"""Deterministic numerical helpers for two-lever, two-target calibration."""

from __future__ import annotations

import csv
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import yaml


class CalibrationError(ValueError):
    """Raised when a checkpoint makes a candidate unsafe to submit."""


def load_config(path: str | Path) -> dict[str, Any]:
    config = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise CalibrationError("config must contain a YAML mapping")
    for section in ("targets", "levers", "thresholds", "budget"):
        if section not in config:
            raise CalibrationError(f"config missing section: {section}")
    for target in ("A", "B"):
        value = config["targets"].get(target, {}).get("value")
        if value is None or not np.isfinite(float(value)) or float(value) == 0:
            raise CalibrationError(f"target {target} must be a finite non-zero value")
    return config


def read_trials(path: str | Path) -> np.ndarray:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    required = {"X", "Y", "A", "B"}
    if not rows or not required.issubset(rows[0]):
        raise CalibrationError("trials CSV must contain X,Y,A,B columns")
    try:
        data = np.asarray([[float(row[name]) for name in ("X", "Y", "A", "B")] for row in rows], dtype=float)
    except (TypeError, ValueError) as exc:
        raise CalibrationError(f"trials CSV contains non-numeric values: {exc}") from exc
    if not np.isfinite(data).all():
        raise CalibrationError("trials CSV contains non-finite values")
    return data


def require_mixed_signs(errors: np.ndarray, target_name: str) -> None:
    if not (np.any(errors <= 0) and np.any(errors >= 0)):
        raise CalibrationError(f"target {target_name} errors have the same sign")


def _design_matrix(data: np.ndarray, minimum_rows: int) -> np.ndarray:
    if data.ndim != 2 or data.shape[1] != 4 or len(data) < minimum_rows:
        raise CalibrationError(f"need at least {minimum_rows} rows with X,Y,A,B")
    design = np.column_stack([np.ones(len(data)), data[:, 0], data[:, 1]])
    if np.linalg.matrix_rank(design) < 3:
        raise CalibrationError("trial design matrix rank is below 3; choose non-collinear X/Y points")
    return design


def _solve_intersection(coeff_a: np.ndarray, coeff_b: np.ndarray, target_a: float, target_b: float) -> tuple[float, float]:
    response = np.asarray([[coeff_a[1], coeff_a[2]], [coeff_b[1], coeff_b[2]]], dtype=float)
    if np.linalg.matrix_rank(response) < 2:
        raise CalibrationError("response matrix rank is below 2; targets cannot be independently controlled")
    rhs = np.asarray([target_a - coeff_a[0], target_b - coeff_b[0]], dtype=float)
    solution = np.linalg.solve(response, rhs)
    return float(solution[0]), float(solution[1])


def exact_solution(data: np.ndarray, target_a: float, target_b: float) -> tuple[float, float]:
    if len(data) != 3:
        raise CalibrationError("exact solution requires exactly three selected trials")
    design = _design_matrix(data, 3)
    coeff_a = np.linalg.solve(design, data[:, 2])
    coeff_b = np.linalg.solve(design, data[:, 3])
    return _solve_intersection(coeff_a, coeff_b, target_a, target_b)


def r_squared(observed: np.ndarray, predicted: np.ndarray) -> float:
    residual = float(np.sum((observed - predicted) ** 2))
    total = float(np.sum((observed - np.mean(observed)) ** 2))
    return 1.0 if total == 0 and residual == 0 else (0.0 if total == 0 else 1.0 - residual / total)


def fit_response_surfaces(data: np.ndarray, target_a: float, target_b: float) -> dict[str, float]:
    design = _design_matrix(data, 4)
    coeff_a, *_ = np.linalg.lstsq(design, data[:, 2], rcond=None)
    coeff_b, *_ = np.linalg.lstsq(design, data[:, 3], rcond=None)
    x_opt, y_opt = _solve_intersection(coeff_a, coeff_b, target_a, target_b)
    return {
        "r2_a": r_squared(data[:, 2], design @ coeff_a),
        "r2_b": r_squared(data[:, 3], design @ coeff_b),
        "x_opt": x_opt,
        "y_opt": y_opt,
    }


def require_bounds(config: dict[str, Any], x_value: float, y_value: float) -> None:
    for name, value in (("X", x_value), ("Y", y_value)):
        lower, upper = map(float, config["levers"][name]["bounds"])
        if not lower < upper:
            raise CalibrationError(f"lever {name} bounds must be increasing")
        if not lower <= value <= upper:
            raise CalibrationError(f"{name}_opt={value:.6g} is outside [{lower:.6g}, {upper:.6g}]")


def nearest_controlled_pair(data: np.ndarray, max_relative_y_change: float) -> tuple[int, int]:
    candidates: list[tuple[float, int, int]] = []
    for i, j in combinations(range(len(data)), 2):
        dx = abs(data[j, 0] - data[i, 0])
        if dx == 0:
            continue
        scale = max(abs(data[i, 1]), abs(data[j, 1]), 1.0e-12)
        if abs(data[j, 1] - data[i, 1]) / scale <= max_relative_y_change:
            candidates.append((dx, i, j))
    if not candidates:
        raise CalibrationError("no controlled pair: vary X while holding Y approximately fixed")
    _, i, j = min(candidates)
    return i, j
