from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _campaign_common import load_config, load_runs, parameter_defs, target_defs, workspace_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot calibration campaign diagnostics.")
    parser.add_argument("config", help="Path to calibration campaign YAML")
    parser.add_argument("--runs", default=None, help="Path to runs.csv; defaults to workspace/runs.csv")
    parser.add_argument("--report", default=None, help="Path to surrogate report; defaults to workspace/surrogate_report.json")
    args = parser.parse_args()

    cfg = load_config(args.config)
    params = parameter_defs(cfg)
    targets = target_defs(cfg)
    wdir = workspace_dir(cfg)
    plots_dir = wdir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    runs_path = Path(args.runs) if args.runs else wdir / "runs.csv"
    report_path = Path(args.report) if args.report else wdir / "surrogate_report.json"
    runs = load_runs(runs_path, params, targets)
    good = runs[runs["status"] == "success"].copy().reset_index(drop=True)

    best_curve = good["objective"].cummin()
    plt.figure(figsize=(6, 4))
    plt.plot(np.arange(1, len(best_curve) + 1), best_curve, marker="o", linewidth=1.5)
    plt.xlabel("Successful evaluation count")
    plt.ylabel("Best objective so far")
    plt.title("Convergence curve")
    plt.tight_layout()
    plt.savefig(plots_dir / "convergence_curve.png", dpi=180)
    plt.close()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    model_names = list(report["model_reports"].keys())
    rmse = [report["model_reports"][name]["rmse"] for name in model_names]
    mae = [report["model_reports"][name]["mae"] for name in model_names]
    x = np.arange(len(model_names))
    width = 0.35
    plt.figure(figsize=(6, 4))
    plt.bar(x - width / 2, rmse, width=width, label="RMSE")
    plt.bar(x + width / 2, mae, width=width, label="MAE")
    plt.xticks(x, model_names)
    plt.ylabel("Error")
    plt.title("Surrogate CV error")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / "surrogate_cv_error.png", dpi=180)
    plt.close()

    importance = report.get("feature_importance") or {}
    if importance:
        items = sorted(importance.items(), key=lambda item: item[1], reverse=True)
        plt.figure(figsize=(6, 4))
        plt.bar([key for key, _ in items], [value for _, value in items])
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Importance")
        plt.title("Parameter importance")
        plt.tight_layout()
        plt.savefig(plots_dir / "parameter_importance.png", dpi=180)
        plt.close()

    if len(params) >= 2 and not good.empty:
        p1, p2 = params[0].name, params[1].name
        plt.figure(figsize=(6, 4))
        scatter = plt.scatter(good[f"param__{p1}"], good[f"param__{p2}"], c=good["objective"], cmap="viridis", s=35)
        plt.xlabel(p1)
        plt.ylabel(p2)
        plt.title("Sample coverage (first two parameters)")
        plt.colorbar(scatter, label="Objective")
        plt.tight_layout()
        plt.savefig(plots_dir / "sample_coverage_2d.png", dpi=180)
        plt.close()

    best = good.sort_values("objective").iloc[0]
    rows = []
    for target in targets:
        metric_name = f"metric__{target.name}"
        metric_value = float(best[metric_name])
        rows.append(
            {
                "target": target.name,
                "direction": target.direction,
                "goal": target.value,
                "tolerance": target.tolerance,
                "best_metric": metric_value,
                "abs_error": abs(metric_value - target.value),
            }
        )
    pd.DataFrame(rows).to_csv(wdir / "target_hit_summary.csv", index=False)
    print(f"diagnostics saved under {plots_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
