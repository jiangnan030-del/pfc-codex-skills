#!/usr/bin/env python3
"""Plot exported PFC waveforms or sensor histories."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot time-series waveforms from a whitespace/CSV table.")
    parser.add_argument("table", type=Path)
    parser.add_argument("--delimiter", default=None)
    parser.add_argument("--time-col", type=int, default=0)
    parser.add_argument("--cols", default="1", help="Comma-separated signal column indices.")
    parser.add_argument("--out", type=Path, default=Path("waveforms.png"))
    args = parser.parse_args()

    data = np.genfromtxt(args.table, delimiter=args.delimiter)
    if data.ndim == 1:
        data = data.reshape(-1, data.shape[0])
    time = data[:, args.time_col]
    cols = [int(c.strip()) for c in args.cols.split(",") if c.strip()]

    fig, ax = plt.subplots(figsize=(6.5, 3.2), constrained_layout=True)
    for col in cols:
        ax.plot(time, data[:, col], lw=1.1, label=f"col {col}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Signal")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    fig.savefig(args.out, dpi=300)
    print(args.out)


if __name__ == "__main__":
    main()
