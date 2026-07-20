"""Project adapter template for checking one completed dual-target trial."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml


def check(trial_id: str, workdir: str = ".", config: str = "config.yaml") -> dict[str, float]:
    config_path = Path(config)
    settings: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    target_a = settings["targets"]["A"]["value"]
    target_b = settings["targets"]["B"]["value"]
    if target_a in (None, 0) or target_b in (None, 0):
        raise ValueError("confirm and write both non-zero targets before checking trials")

    trial_dir = Path(workdir) / f"trial_{trial_id}"
    result_path = trial_dir / "result.csv"
    params_path = trial_dir / "params.json"
    if not result_path.is_file():
        raise FileNotFoundError(f"trial output is not ready: {result_path}")
    if not params_path.is_file():
        raise FileNotFoundError(f"trial parameters are missing: {params_path}")
    with result_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 1 or not {"A", "B"}.issubset(rows[0]):
        raise ValueError("result.csv must contain exactly one row with A and B")
    value_a = float(rows[0]["A"])
    value_b = float(rows[0]["B"])
    params = json.loads(params_path.read_text(encoding="utf-8"))
    x_name = settings["levers"]["X"]["name"]
    y_name = settings["levers"]["Y"]["name"]
    if x_name not in params or y_name not in params:
        raise ValueError("params.json does not contain both configured lever names")

    ledger = Path(workdir) / "trials.csv"
    existing: list[dict[str, str]] = []
    if ledger.exists():
        with ledger.open("r", encoding="utf-8-sig", newline="") as stream:
            existing = list(csv.DictReader(stream))
        if any(row.get("trial") == trial_id for row in existing):
            raise ValueError(f"trial already recorded: {trial_id}")
    with ledger.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        if not existing:
            writer.writerow(["trial", "X", "Y", "A", "B"])
        writer.writerow([trial_id, params[x_name], params[y_name], value_a, value_b])
    return {
        "A": value_a,
        "B": value_b,
        "err_A": (value_a - float(target_a)) / float(target_a),
        "err_B": (value_b - float(target_b)) / float(target_b),
    }
