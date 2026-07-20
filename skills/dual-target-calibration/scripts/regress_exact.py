#!/usr/bin/env python3
"""Solve a selected three-trial local two-target response surface."""

from __future__ import annotations

import argparse
import sys

import numpy as np

from dual_target_common import (
    CalibrationError,
    exact_solution,
    load_config,
    read_trials,
    require_bounds,
    require_mixed_signs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CHECKPOINT 1/2: exact 2x2 dual-target calibration solve")
    parser.add_argument("trials_csv")
    parser.add_argument("config", nargs="?", default="config.yaml")
    parser.add_argument("--rows", nargs=3, type=int, metavar=("I", "J", "K"), help="1-based data-row indices; default: last three")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        all_data = read_trials(args.trials_csv)
        indices = [index - 1 for index in args.rows] if args.rows else list(range(len(all_data) - 3, len(all_data)))
        if len(all_data) < 3 or any(index < 0 or index >= len(all_data) for index in indices):
            raise CalibrationError("select three valid trial rows")
        data = all_data[indices]
        target_a = float(config["targets"]["A"]["value"])
        target_b = float(config["targets"]["B"]["value"])
        error_a = data[:, 2] / target_a - 1.0
        error_b = data[:, 3] / target_b - 1.0
        require_mixed_signs(error_a, "A")
        require_mixed_signs(error_b, "B")
        basin_limit = float(config["thresholds"].get("exact_basin_error_span", 0.20))
        if np.ptp(error_b) > basin_limit:
            raise CalibrationError(f"B error span exceeds {basin_limit:.1%}; use basin recovery")
        x_opt, y_opt = exact_solution(data, target_a, target_b)
        require_bounds(config, x_opt, y_opt)
    except (CalibrationError, np.linalg.LinAlgError) as exc:
        print(f"CHECKPOINT failed: {exc}", file=sys.stderr)
        return 2
    print(f"X_opt={x_opt:.12g}\nY_opt={y_opt:.12g}\nCHECKPOINT 1/2 passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
