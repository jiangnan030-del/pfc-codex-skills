"""Project adapter contract for extracting two confirmed experimental targets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def write_targets(config_path: str | Path, target_a: float, target_b: float) -> dict[str, float]:
    """Persist confirmed target values into the project's single config source."""
    if target_a == 0 or target_b == 0:
        raise ValueError("relative-error targets must be non-zero")
    path = Path(config_path)
    config: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    config["targets"]["A"]["value"] = float(target_a)
    config["targets"]["B"]["value"] = float(target_b)
    path.write_text(
        yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return {"T_E": float(target_a) / float(target_b)}


def target(source: str, config: str = "config.yaml") -> tuple[float, float, dict[str, float]]:
    """Extract and confirm target A/B from a project-specific data source."""
    raise NotImplementedError(
        "Copy adapters/target.py into the project, parse the confirmed experiment contract, "
        "then call write_targets(config, target_a, target_b)."
    )
