from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal command-runner template for pfc-workflow campaigns.")
    parser.add_argument("--params-file", required=True, help="Input YAML of candidate parameters")
    parser.add_argument("--metrics-file", required=True, help="Output JSON of macro metrics")
    args = parser.parse_args()

    with Path(args.params_file).open("r", encoding="utf-8") as handle:
        params = yaml.safe_load(handle)

    # Replace this block with your real PFC wrapper logic.
    emod = float(params.get("emod", 3.0e6))
    pb_ten = float(params.get("pb_ten", 2.0e5))
    pb_coh = float(params.get("pb_coh", 3.0e5))
    pb_fa = float(params.get("pb_fa", 10.0))
    metrics = {
        "elastic_modulus": 1.0 + emod / 4.0e6,
        "ucs": 0.10 + pb_ten / 2.0e6 + pb_coh / 3.5e6,
        "peak_strain": 0.08 - pb_fa / 1000.0,
    }

    output = Path(args.metrics_file)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
