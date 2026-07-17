from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from config import (
    CASE_CORE_FILES,
    CASE_NAMES,
    COMMON_CASE_FILES,
    COMMON_CASE_FILES_DIR,
    ROOT,
    case_dir,
)

def ensure_common_files() -> None:
    missing = [name for name in COMMON_CASE_FILES if not (COMMON_CASE_FILES_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing common case files: {', '.join(missing)}")


def write_case(case_name: str) -> Path:
    ensure_common_files()
    out_dir = case_dir(case_name)
    missing = [name for name in CASE_CORE_FILES if not (out_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing case files for {case_name}: {', '.join(missing)}")
    for name in COMMON_CASE_FILES:
        target = out_dir / name
        if not target.exists():
            shutil.copy2(COMMON_CASE_FILES_DIR / name, target)
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PFC 2D case skeletons from local reference seeds.")
    parser.add_argument("case", nargs="?", help="Optional single case name.")
    args = parser.parse_args()

    targets = [args.case] if args.case else CASE_NAMES
    for case_name in targets:
        if case_name not in CASE_NAMES:
            raise ValueError(f"Unknown case: {case_name}")
        out_dir = write_case(case_name)
        print(f"generated {out_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
