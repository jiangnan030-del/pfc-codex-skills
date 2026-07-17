from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml


def read_metrics_from_case(case_dir: Path) -> dict[str, float]:
    stress_csv = case_dir / "stress_strain.csv"
    if stress_csv.exists():
        df = pd.read_csv(stress_csv)
        peak_idx = df["stress_mpa"].idxmax()
        return {
            "ucs": float(df.loc[peak_idx, "stress_mpa"]),
            "peak_strain": float(abs(df.loc[peak_idx, "strain"])),
        }

    metrics_xlsx = case_dir / "curve_metrics_2d.xlsx"
    if not metrics_xlsx.exists():
        raise FileNotFoundError(f"No readable metrics source found under {case_dir}")
    df = pd.read_excel(metrics_xlsx)
    if "source" in df.columns:
        sim_rows = df[df["source"].astype(str).str.lower() == "simulation"]
        if not sim_rows.empty:
            row = sim_rows.iloc[0]
        else:
            row = df.iloc[0]
    else:
        row = df.iloc[0]
    metrics = {}
    if "peak_stress_mpa" in row:
        metrics["ucs"] = float(row["peak_stress_mpa"])
    if "peak_strain" in row:
        metrics["peak_strain"] = float(row["peak_strain"])
    if "regression_modulus_mpa" in row:
        metrics["elastic_modulus"] = float(row["regression_modulus_mpa"])
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Read macro metrics from an existing PFC case without modifying it.")
    parser.add_argument("--params-file", required=True, help="Campaign params YAML; accepted but ignored.")
    parser.add_argument("--metrics-file", required=True, help="Output JSON of macro metrics.")
    parser.add_argument("--case-dir", required=True, help="Existing solved or postprocessed case directory.")
    args = parser.parse_args()

    # Read the params file so the wrapper matches the standard contract.
    with Path(args.params_file).open("r", encoding="utf-8") as handle:
        yaml.safe_load(handle)

    metrics = read_metrics_from_case(Path(args.case_dir))
    output = Path(args.metrics_file)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
