from __future__ import annotations

import argparse
from pathlib import Path

from _campaign_common import fit_all_models, load_config, load_runs, parameter_defs, save_model_bundle, target_defs, workspace_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit surrogate models from campaign runs.")
    parser.add_argument("config", help="Path to calibration campaign YAML")
    parser.add_argument("--runs", default=None, help="Path to runs.csv; defaults to workspace/runs.csv")
    parser.add_argument("--report-name", default="surrogate_report.json", help="Output report file name under workspace")
    args = parser.parse_args()

    cfg = load_config(args.config)
    params = parameter_defs(cfg)
    targets = target_defs(cfg)
    wdir = workspace_dir(cfg)
    runs_path = Path(args.runs) if args.runs else wdir / "runs.csv"
    runs = load_runs(runs_path, params, targets)

    bundle = fit_all_models(cfg, runs)
    report_path, model_path = save_model_bundle(bundle, cfg, report_name=args.report_name)
    print(f"surrogate report -> {report_path}")
    print(f"model bundle -> {model_path}")
    for name, stats in bundle["model_reports"].items():
        print(f"{name}: RMSE={stats['rmse']:.6f}, MAE={stats['mae']:.6f}, R2={stats['r2']:.6f}")
    print(f"selected_model={bundle['selected_model']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
