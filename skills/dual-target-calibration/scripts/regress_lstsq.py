#!/usr/bin/env python3
"""Fit cross-basin least-squares surfaces with CHECKPOINT 3 guards."""

from __future__ import annotations

import argparse
import sys

import numpy as np

from dual_target_common import (
    CalibrationError,
    fit_response_surfaces,
    load_config,
    read_trials,
    require_bounds,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CHECKPOINT 3: least-squares dual-target basin recovery")
    parser.add_argument("trials_csv")
    parser.add_argument("config", nargs="?", default="config.yaml")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        data = read_trials(args.trials_csv)
        target_a = float(config["targets"]["A"]["value"])
        target_b = float(config["targets"]["B"]["value"])
        fit = fit_response_surfaces(data, target_a, target_b)
        minimum = float(config["thresholds"]["regression_r2"])
        if fit["r2_a"] < minimum or fit["r2_b"] < minimum:
            raise CalibrationError(
                f"R2 below {minimum:.3f}: A={fit['r2_a']:.4f}, B={fit['r2_b']:.4f}"
            )
        require_bounds(config, fit["x_opt"], fit["y_opt"])
    except (CalibrationError, np.linalg.LinAlgError) as exc:
        print(f"CHECKPOINT failed: {exc}", file=sys.stderr)
        return 2
    print(
        f"R2_A={fit['r2_a']:.6f}\nR2_B={fit['r2_b']:.6f}\n"
        f"X_opt={fit['x_opt']:.12g}\nY_opt={fit['y_opt']:.12g}\nCHECKPOINT 3 passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
