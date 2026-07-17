from __future__ import annotations

import argparse
import csv

from config import case_dir


def to_float(value: str) -> float:
    return float(value.strip())


def find_column(fieldnames: list[str], candidates: tuple[str, ...], fallback_index: int) -> str:
    normalized = {name.strip().lower(): name for name in fieldnames}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in normalized:
            return normalized[key]
    return fieldnames[fallback_index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize stress_strain.csv for one case.")
    parser.add_argument("case", help="Case name, for example Intact or b60_d20")
    args = parser.parse_args()

    csv_path = case_dir(args.case) / "stress_strain.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows: list[tuple[float, float, float]] = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV file has no header: {csv_path}")
        fieldnames = reader.fieldnames
        strain_col = find_column(fieldnames, ("strain", "axial_strain"), 0)
        stress_col = find_column(fieldnames, ("stress_mpa", "stress", "axial_stress"), 1)
        crack_col = find_column(fieldnames, ("crack_num", "crack_number", "cracks"), len(fieldnames) - 1)
        for row in reader:
            try:
                rows.append((to_float(row[strain_col]), to_float(row[stress_col]), to_float(row[crack_col])))
            except (KeyError, TypeError, ValueError):
                continue

    if not rows:
        raise ValueError(f"No valid numeric rows found in: {csv_path}")

    peak = max(rows, key=lambda item: abs(item[1]))
    last = rows[-1]
    print("stress_strain.csv summary")
    print("=" * 32)
    print(f"rows: {len(rows)}")
    print(f"peak_strain: {peak[0]:.8g}")
    print(f"peak_stress_mpa: {peak[1]:.8g}")
    print(f"peak_crack_num: {peak[2]:.8g}")
    print(f"last_strain: {last[0]:.8g}")
    print(f"last_stress_mpa: {last[1]:.8g}")
    print(f"last_crack_num: {last[2]:.8g}")


if __name__ == "__main__":
    main()
