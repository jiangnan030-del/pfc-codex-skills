"""Project adapter contract: submit one expanded parameter set.

Copy this file into the calibration project and implement ``submit`` there.
The installed skill deliberately has no default engine side effect.
"""

from __future__ import annotations

import re
from typing import Any

_LINKED_RULE = re.compile(
    r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*$"
)


def expand_linked(params: dict[str, float], config: dict[str, Any]) -> dict[str, float]:
    """Expand safe ``factor * parameter`` rules from ``config.linked``."""
    expanded = {name: float(value) for name, value in params.items()}
    for name, expression in (config.get("linked") or {}).items():
        match = _LINKED_RULE.fullmatch(str(expression))
        if not match:
            raise ValueError(f"unsupported linked rule for {name}: {expression!r}")
        factor, reference = match.groups()
        if reference not in expanded:
            raise ValueError(f"linked rule for {name} references missing parameter: {reference}")
        expanded[name] = float(factor) * expanded[reference]
    return expanded


def submit(params: dict[str, float], workdir: str = ".") -> str:
    """Return a stable trial ID after project-specific submission."""
    raise NotImplementedError(
        "Copy adapters/submit.py into the project and connect it to the real PFC/MCP/queue runner. "
        "Do not add engine-specific paths to the public skill."
    )
