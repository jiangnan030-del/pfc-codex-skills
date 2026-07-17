#!/usr/bin/env python3
"""Extract calibration metrics from exported PFC stress-strain histories.

Expected compression CSV columns can be customized, but defaults assume axial
strain, axial stress, radial strain, and volumetric strain are present.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load_table(path: Path) -> np.ndarray:
    data = np.genfromtxt(path, comments="#", delimiter=None)
    if data.ndim == 1:
        data = data.reshape(-1, data.shape[0])
    return data


def interp_at(x: np.ndarray, y: np.ndarray, target: float) -> float:
    order = np.argsort(x)
    return float(np.interp(target, x[order], y[order]))


def secant_modulus(strain: np.ndarray, stress: np.ndarray, e1: float, e2: float) -> float:
    s1 = interp_at(strain, stress, e1)
    s2 = interp_at(strain, stress, e2)
    return (s2 - s1) / (e2 - e1)


def extract_compression(path: Path, strain_col: int, stress_col: int, radial_col: int | None, vol_col: int | None) -> dict[str, float]:
    data = load_table(path)
    strain = np.abs(data[:, strain_col])
    stress = np.abs(data[:, stress_col])
    result = {
        "UCS": float(np.nanmax(stress)),
        "E_secant_0p05_0p15": float(secant_modulus(strain, stress, 0.0005, 0.0015)),
    }
    if radial_col is not None:
        radial = data[:, radial_col]
        nu_curve = -radial / np.where(data[:, strain_col] == 0, np.nan, data[:, strain_col])
        nu1 = interp_at(strain, nu_curve, 0.001)
        nu2 = interp_at(strain, nu_curve, 0.002)
        result["nu_avg_0p1_0p2"] = float((nu1 + nu2) / 2.0)
    if vol_col is not None:
        vol = data[:, vol_col]
        grad = np.gradient(vol, strain)
        idx = int(np.nanargmax(grad)) if len(grad) else 0
        result["sigma_cd_estimate"] = float(stress[idx])
        result["sigma_cd_over_UCS"] = float(stress[idx] / result["UCS"]) if result["UCS"] else float("nan")
    return result


def extract_tension(path: Path, stress_col: int) -> dict[str, float]:
    data = load_table(path)
    stress = np.abs(data[:, stress_col])
    return {"UTS": float(np.nanmax(stress))}


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract macro metrics from PFC exported histories.")
    parser.add_argument("--compression", type=Path)
    parser.add_argument("--tension", type=Path)
    parser.add_argument("--out", type=Path, default=Path("metrics.json"))
    parser.add_argument("--strain-col", type=int, default=0)
    parser.add_argument("--stress-col", type=int, default=1)
    parser.add_argument("--radial-col", type=int, default=2)
    parser.add_argument("--vol-col", type=int, default=3)
    parser.add_argument("--tension-stress-col", type=int, default=1)
    args = parser.parse_args()

    metrics: dict[str, float] = {}
    if args.compression:
        metrics.update(extract_compression(args.compression, args.strain_col, args.stress_col, args.radial_col, args.vol_col))
    if args.tension:
        metrics.update(extract_tension(args.tension, args.tension_stress_col))
    if "UCS" in metrics and "UTS" in metrics and metrics["UTS"]:
        metrics["UCS_over_UTS"] = metrics["UCS"] / metrics["UTS"]
    args.out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
