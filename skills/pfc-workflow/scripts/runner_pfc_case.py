from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml


def replace_pattern(text: str, pattern: str, replacement: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"Pattern not found or not unique: {pattern}")
    return new_text


def update_2bond(case_dir: Path, params: dict[str, float]) -> None:
    bond_path = case_dir / "2bond.dat"
    backup_path = case_dir / "2bond.dat.autocalib.bak"
    if not backup_path.exists():
        shutil.copy2(bond_path, backup_path)
    text = bond_path.read_text(encoding="utf-8-sig")

    if "bond_gap" in params:
        text = replace_pattern(
            text,
            r"contact method bond gap [0-9eE\+\-\.]+",
            f"contact method bond gap {float(params['bond_gap']):.6e}",
        )
    if "emod" in params:
        emod = float(params["emod"])
        text = replace_pattern(
            text,
            r"contact method deform emod [0-9eE\+\-\.]+ krat",
            f"contact method deform emod {emod:.6e} krat",
        )
        text = replace_pattern(
            text,
            r"contact method pb_deform emod [0-9eE\+\-\.]+ krat",
            f"contact method pb_deform emod {emod:.6e} krat",
        )
    if any(key in params for key in ("pb_ten", "pb_coh", "pb_fa")):
        current = bond_path.read_text(encoding="utf-8-sig")
        line_match = re.search(
            r"contact property pb_ten ([0-9eE\+\-\.]+) pb_coh ([0-9eE\+\-\.]+) pb_fa ([0-9eE\+\-\.]+)",
            text,
        )
        if not line_match:
            raise ValueError("Could not find pb_ten/pb_coh/pb_fa line in 2bond.dat")
        pb_ten = float(params.get("pb_ten", line_match.group(1)))
        pb_coh = float(params.get("pb_coh", line_match.group(2)))
        pb_fa = float(params.get("pb_fa", line_match.group(3)))
        text = replace_pattern(
            text,
            r"contact property pb_ten [0-9eE\+\-\.]+ pb_coh [0-9eE\+\-\.]+ pb_fa [0-9eE\+\-\.]+",
            f"contact property pb_ten {pb_ten:.6e} pb_coh {pb_coh:.6e} pb_fa {pb_fa:.6f}",
        )
    if "fric" in params:
        text = replace_pattern(
            text,
            r"contact property fric [0-9eE\+\-\.]+ range contact type 'ball-ball'",
            f"contact property fric {float(params['fric']):.6f} range contact type 'ball-ball'",
        )

    bond_path.write_text(text, encoding="utf-8")


def extract_metrics(case_dir: Path) -> dict[str, float]:
    stress_csv = case_dir / "stress_strain.csv"
    if not stress_csv.exists():
        raise FileNotFoundError(f"Missing stress_strain.csv in {case_dir}")
    df = pd.read_csv(stress_csv)
    peak_idx = df["stress_mpa"].idxmax()
    metrics = {
        "ucs": float(df.loc[peak_idx, "stress_mpa"]),
        "peak_strain": float(abs(df.loc[peak_idx, "strain"])),
    }
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Update a PFC case 2bond.dat, run solve-only, and export macro metrics.")
    parser.add_argument("--params-file", required=True, help="Input YAML of candidate parameters")
    parser.add_argument("--metrics-file", required=True, help="Output JSON of macro metrics")
    parser.add_argument("--case-dir", required=True, help="Target PFC case directory")
    parser.add_argument("--case-name", required=True, help="Case name for run_case.py")
    parser.add_argument("--run-case-script", default="pfc_2d\\run_case.py", help="Path to run_case.py")
    parser.add_argument("--timeout-sec", type=int, default=420, help="Solve timeout in seconds")
    args = parser.parse_args()

    with Path(args.params_file).open("r", encoding="utf-8") as handle:
        params = yaml.safe_load(handle) or {}
    if not isinstance(params, dict):
        raise ValueError("params-file must contain a mapping")

    case_dir = Path(args.case_dir)
    update_2bond(case_dir, params)

    command = [sys.executable, args.run_case_script, args.case_name, "--solve-only"]
    completed = subprocess.run(
        command,
        cwd=str(case_dir.parents[1]),
        timeout=args.timeout_sec,
        check=True,
        capture_output=True,
        text=True,
    )

    metrics = extract_metrics(case_dir)
    metrics["stdout_tail_len"] = len((completed.stdout or "").splitlines())
    output = Path(args.metrics_file)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
