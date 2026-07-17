#!/usr/bin/env python3
"""Nature-style AE magnitude versus micro-crack count relation with envelope power fit."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"

PALETTE = {
    "red_strong": "#B64342",
    "neutral_black": "#272727",
}


def apply_publication_style(font_size: int = 15, axes_linewidth: float = 2.0) -> None:
    """Apply Nature-style rcParams before creating figures."""
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["font.size"] = font_size
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["axes.linewidth"] = axes_linewidth
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"


def finalize_figure(fig: plt.Figure, output_base: Path, dpi: int = 300) -> None:
    """Save editable SVG first, then PNG preview and PDF."""
    fig.tight_layout(pad=1.5)
    fig.savefig(output_base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _r2(y: np.ndarray, y_hat: np.ndarray) -> float:
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan


def _load_events(case_dir: Path, magnitude_col: str, count_col: str) -> pd.DataFrame:
    event_path = case_dir / "ae_clustered_events.csv"
    if not event_path.exists():
        raise FileNotFoundError(f"Missing {event_path}; run AE clustering first.")
    events = pd.read_csv(event_path)
    missing = [col for col in [magnitude_col, count_col] if col not in events.columns]
    if missing:
        raise KeyError(f"Missing columns in {event_path}: {missing}")
    data = pd.DataFrame(
        {
            "magnitude": pd.to_numeric(events[magnitude_col], errors="coerce"),
            "microcrack_count": pd.to_numeric(events[count_col], errors="coerce"),
        }
    ).dropna()
    data = data[data["microcrack_count"] > 0].copy()
    if data.empty:
        raise ValueError("No valid AE events after filtering magnitude and count columns.")
    return data


def _binned_envelope(magnitude: np.ndarray, count: np.ndarray, bin_width: float) -> pd.DataFrame:
    lo = np.floor(np.nanmin(magnitude) / bin_width) * bin_width
    hi = np.ceil(np.nanmax(magnitude) / bin_width) * bin_width
    edges = np.arange(lo, hi + bin_width * 1.5, bin_width)
    idx = np.digitize(magnitude, edges) - 1
    rows: list[dict[str, float]] = []
    for i in range(len(edges) - 1):
        mask = idx == i
        if not np.any(mask):
            continue
        rows.append(
            {
                "magnitude_bin_center": 0.5 * (edges[i] + edges[i + 1]),
                "magnitude_bin_left": edges[i],
                "magnitude_bin_right": edges[i + 1],
                "mean_microcrack_count": float(np.mean(count[mask])),
                "median_microcrack_count": float(np.median(count[mask])),
                "max_microcrack_count": float(np.max(count[mask])),
                "event_count": int(mask.sum()),
            }
        )
    binned = pd.DataFrame(rows)
    binned["envelope_microcrack_count"] = binned["max_microcrack_count"].cummax()
    return binned


def _predict_envelope_power(x: np.ndarray, baseline: float, amp: float, m0: float, power: float) -> np.ndarray:
    return baseline + amp * np.maximum(x - m0, 0.0) ** power


def _fit_envelope_power(
    binned: pd.DataFrame,
    baseline: float,
    m0_steps: int = 181,
    power_min: float = 2.0,
    power_max: float = 4.0,
    power_steps: int = 161,
) -> dict[str, float | str | int]:
    x = binned["magnitude_bin_center"].to_numpy(dtype=float)
    y = binned["envelope_microcrack_count"].to_numpy(dtype=float)
    # Search breakpoints from the interior of the magnitude range so the low branch
    # stays horizontal and only the terminal envelope bends upward.
    m0_grid = np.linspace(np.quantile(x, 0.35), np.quantile(x, 0.90), m0_steps)
    power_grid = np.linspace(power_min, power_max, power_steps)
    best: dict[str, float | str | int] | None = None
    for m0 in m0_grid:
        dx = np.maximum(x - m0, 0.0)
        if np.count_nonzero(dx) < 2:
            continue
        for power in power_grid:
            basis = dx**power
            denom = float(np.dot(basis, basis))
            if denom <= 0:
                continue
            amp = max(0.0, float(np.dot(basis, y - baseline) / denom))
            y_hat = baseline + amp * basis
            score = _r2(y, y_hat)
            if best is None or score > float(best["r2"]):
                best = {
                    "model": "baseline_power_envelope",
                    "target": "binned_envelope",
                    "baseline": float(baseline),
                    "amp": float(amp),
                    "M0": float(m0),
                    "power": float(power),
                    "r2": float(score),
                    "fit_points": int(len(x)),
                    "magnitude_min": float(np.min(x)),
                    "magnitude_max": float(np.max(x)),
                }
    if best is None:
        raise ValueError("Envelope power fit failed.")
    return best


def plot_case(
    case_dir: Path,
    magnitude_col: str = "moment_magnitude",
    count_col: str = "hit_count",
    bin_width: float = 0.10,
    output_prefix: str = "ae_magnitude_microcrack_relation",
    jitter: float = 0.06,
    seed: int = 7,
    y_max: float | None = None,
) -> None:
    data = _load_events(case_dir, magnitude_col, count_col)
    magnitude = data["magnitude"].to_numpy(dtype=float)
    count = data["microcrack_count"].to_numpy(dtype=float)
    baseline = float(np.nanmin(count))
    binned = _binned_envelope(magnitude, count, bin_width)
    fit = _fit_envelope_power(binned, baseline=baseline)

    rng = np.random.default_rng(seed)
    data["microcrack_count_display"] = count + rng.uniform(-jitter, jitter, size=len(count))
    data["fit_prediction"] = _predict_envelope_power(
        magnitude,
        float(fit["baseline"]),
        float(fit["amp"]),
        float(fit["M0"]),
        float(fit["power"]),
    )
    data.to_csv(case_dir / f"{output_prefix}_source.csv", index=False)

    binned["fit_prediction"] = _predict_envelope_power(
        binned["magnitude_bin_center"].to_numpy(dtype=float),
        float(fit["baseline"]),
        float(fit["amp"]),
        float(fit["M0"]),
        float(fit["power"]),
    )
    binned.to_csv(case_dir / f"{output_prefix}_binned_source.csv", index=False)
    pd.DataFrame([fit]).to_csv(case_dir / f"{output_prefix}_fit.csv", index=False)

    x_curve = np.linspace(float(np.min(magnitude)), float(np.max(magnitude)), 500)
    y_curve = _predict_envelope_power(
        x_curve,
        float(fit["baseline"]),
        float(fit["amp"]),
        float(fit["M0"]),
        float(fit["power"]),
    )

    apply_publication_style(font_size=15, axes_linewidth=2.0)
    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=300)
    scatter = ax.scatter(
        magnitude,
        data["microcrack_count_display"],
        marker="o",
        s=42,
        facecolors="none",
        edgecolors=PALETTE["neutral_black"],
        linewidths=1.5,
        alpha=0.82,
        label="aenum",
        zorder=2,
    )
    line, = ax.plot(
        x_curve,
        y_curve,
        color=PALETTE["red_strong"],
        linewidth=2.5,
        label="Fitting curve",
        zorder=3,
    )

    m0 = float(fit["M0"])
    equation = f"N = {baseline:.2f} + {float(fit['amp']):.2f} * max(M{(-m0):+.2f}, 0)^{float(fit['power']):.2f}"
    ax.text(
        0.97,
        0.95,
        equation + f"\n$R^2$ = {float(fit['r2']):.3f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        color=PALETTE["neutral_black"],
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 2.0},
    )

    x_pad = max((float(np.max(magnitude)) - float(np.min(magnitude))) * 0.06, 0.05)
    y_upper = y_max if y_max is not None else max(6.0, float(np.max(count)) * 1.35, float(np.max(y_curve)) * 1.10)
    ax.set_xlim(float(np.min(magnitude)) - x_pad, float(np.max(magnitude)) + x_pad)
    ax.set_ylim(0, y_upper)
    ax.set_xlabel("Magnitude", fontweight="bold")
    ax.set_ylabel("number of microcracks", fontweight="bold")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    ax.tick_params(axis="both", width=2.0, length=6, colors=PALETTE["neutral_black"])
    ax.spines["left"].set_color(PALETTE["neutral_black"])
    ax.spines["bottom"].set_color(PALETTE["neutral_black"])
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_linewidth(2.0)
    ax.grid(False)
    ax.legend(
        [scatter, line],
        ["aenum", "Fitting curve"],
        loc="lower left",
        bbox_to_anchor=(0.00, 1.01),
        ncol=2,
        frameon=False,
        handlelength=2.0,
        handletextpad=0.5,
        columnspacing=1.2,
    )

    finalize_figure(fig, case_dir / output_prefix)
    print(f"Saved {case_dir / (output_prefix + '.svg')}")
    print(
        f"model={fit['model']}; baseline={fit['baseline']:.4f}; amp={fit['amp']:.4f}; "
        f"M0={fit['M0']:.4f}; power={fit['power']:.4f}; R2={fit['r2']:.4f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="PFC case directory, e.g. b45_d14")
    parser.add_argument("--magnitude-col", default="moment_magnitude", help="AE event magnitude column")
    parser.add_argument("--count-col", default="hit_count", help="AE event micro-crack count column")
    parser.add_argument("--bin-width", type=float, default=0.10, help="Magnitude bin width for envelope fitting")
    parser.add_argument("--output-prefix", default="ae_magnitude_microcrack_relation", help="Output file prefix")
    parser.add_argument("--jitter", type=float, default=0.06, help="Vertical display jitter for overlapping integer counts")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for reproducible display jitter")
    parser.add_argument("--y-max", type=float, default=None, help="Optional fixed y-axis maximum")
    args = parser.parse_args()
    plot_case(
        args.case,
        magnitude_col=args.magnitude_col,
        count_col=args.count_col,
        bin_width=args.bin_width,
        output_prefix=args.output_prefix,
        jitter=args.jitter,
        seed=args.seed,
        y_max=args.y_max,
    )


if __name__ == "__main__":
    main()
