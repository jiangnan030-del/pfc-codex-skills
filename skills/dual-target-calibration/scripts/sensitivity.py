#!/usr/bin/env python3
"""Estimate X sensitivity from a pair that keeps Y approximately fixed."""

from __future__ import annotations

import argparse
import sys

from dual_target_common import CalibrationError, load_config, nearest_controlled_pair, read_trials


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CHECKPOINT 4 helper: controlled dual-target sensitivity")
    parser.add_argument("trials_csv")
    parser.add_argument("config", nargs="?", default="config.yaml")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        data = read_trials(args.trials_csv)
        max_y_change = float(config["thresholds"].get("sensitivity_max_relative_y_change", 0.02))
        i, j = nearest_controlled_pair(data, max_y_change)
        dx = data[j, 0] - data[i, 0]
        derivative_a = (data[j, 2] - data[i, 2]) / dx
        derivative_b = (data[j, 3] - data[i, 3]) / dx
        ratio = abs(derivative_a) / abs(derivative_b) if derivative_b else float("inf")
        target_b = float(config["targets"]["B"]["value"])
        jump = abs(data[j, 3] / target_b - data[i, 3] / target_b)
        basin = config["thresholds"]["basin_jump"]
        normalized_jump = jump / abs(dx) * float(basin["per_dX"])
        if normalized_jump > float(basin["dErrB"]):
            raise CalibrationError(
                f"basin jump {normalized_jump:.2%} exceeds {float(basin['dErrB']):.2%}"
            )
    except CalibrationError as exc:
        print(f"CHECKPOINT failed: {exc}", file=sys.stderr)
        return 2
    recommendation = "tune X" if ratio > 3 else ("tune Y or stop" if ratio < 2 else "prefer a small X step")
    print(
        f"rows={i + 1},{j + 1}\ndA_dX={derivative_a:.12g}\ndB_dX={derivative_b:.12g}\n"
        f"sensitivity_ratio={ratio:.6g}\nrecommendation={recommendation}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
