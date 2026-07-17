from __future__ import annotations

import argparse
from pathlib import Path

from _campaign_common import default_n_init, load_config, parameter_defs, sample_lhs, workspace_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an LHS design for an auto-calibration campaign.")
    parser.add_argument("config", help="Path to calibration_campaign.yaml")
    parser.add_argument("--n-samples", type=int, default=None, help="Override initial LHS sample count")
    parser.add_argument("--seed", type=int, default=None, help="Override random seed")
    parser.add_argument("--output", default=None, help="Output CSV path; defaults to workspace/lhs_samples.csv")
    args = parser.parse_args()

    cfg = load_config(args.config)
    params = parameter_defs(cfg)
    seed = int(args.seed if args.seed is not None else cfg.get("random_seed", 42))
    n_samples = int(args.n_samples if args.n_samples is not None else default_n_init(cfg, len(params)))
    lhs = sample_lhs(params, n_samples=n_samples, seed=seed)

    output = Path(args.output) if args.output else workspace_dir(cfg) / "lhs_samples.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    lhs.to_csv(output, index=False)
    print(f"generated {len(lhs)} samples -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
