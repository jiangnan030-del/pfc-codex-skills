from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from _campaign_common import evaluate_case, load_config, load_runs, parameter_defs, row_to_params, save_runs, target_defs, workspace_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a batch of candidate points for an auto-calibration campaign.")
    parser.add_argument("config", help="Path to calibration campaign YAML")
    parser.add_argument("--samples", default=None, help="CSV of candidate points; defaults to workspace/lhs_samples.csv")
    parser.add_argument("--runs", default=None, help="Path to runs.csv; defaults to workspace/runs.csv")
    parser.add_argument("--phase", default="campaign", help="Phase label for appended runs")
    parser.add_argument("--limit", type=int, default=None, help="Evaluate only the first N unevaluated rows")
    parser.add_argument("--resume", action="store_true", help="Skip sample_id values already present in runs.csv")
    args = parser.parse_args()

    cfg = load_config(args.config)
    params = parameter_defs(cfg)
    targets = target_defs(cfg)
    wdir = workspace_dir(cfg)
    samples_path = Path(args.samples) if args.samples else wdir / "lhs_samples.csv"
    runs_path = Path(args.runs) if args.runs else wdir / "runs.csv"

    samples = pd.read_csv(samples_path)
    runs = load_runs(runs_path, params, targets)
    seen = set(runs["sample_id"].dropna().astype(str)) if args.resume else set()

    evaluated = 0
    for _, row in samples.iterrows():
        sample_id = str(row.get("sample_id") or f"{args.phase}_{evaluated + 1:04d}")
        if sample_id in seen:
            continue
        record = evaluate_case(cfg, row_to_params(row, params), sample_id=sample_id, phase=args.phase, runs_df=runs)
        runs = pd.concat([runs, pd.DataFrame([record])], ignore_index=True)
        evaluated += 1
        if args.limit is not None and evaluated >= args.limit:
            break
    save_runs(runs, runs_path)
    print(f"evaluated {evaluated} candidates -> {runs_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
