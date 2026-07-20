"""Command-line entry point for transactional CPB2D project generation."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from cpb2d_scaffold import ConfigError, create_project, load_intake, project_warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a reproducible CPB2D UCS project scaffold"
    )
    parser.add_argument("--from-intake", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    return parser


def _print_result(case_order: list[str], warnings: list[str]) -> None:
    print(f"enabled case order: {', '.join(case_order)}")
    for warning in warnings:
        print(f"warning: {warning}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.validate_only:
            config = load_intake(args.from_intake)
            order = [case.name for case in config.cases if case.enabled]
            warnings = project_warnings(config, args.output_dir)
            print("validate-only preflight for proposed output directory")
            _print_result(order, warnings)
            return 0

        result = create_project(
            args.from_intake,
            args.output_dir,
            force=args.force,
        )
        _print_result(result.case_order, result.warnings)
        print(f"created project: {result.root}")
        return 0
    except (ConfigError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
