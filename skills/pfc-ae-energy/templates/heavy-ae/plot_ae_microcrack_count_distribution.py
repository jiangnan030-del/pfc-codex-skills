#!/usr/bin/env python3
"""Nature-style AE event micro-crack count frequency distribution with decay fitting."""
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
    "blue_secondary": "#3775BA",
    "red_strong": "#B64342",
    "neutral_dark": "#4D4D4D",
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


def _fit_decay(x: np.ndarray, y: np.ndarray) -> dict[str, float | str]:
    """Fit power-law and exponential decays, then return the better R2 model."""
    positive = (x > 0) & (y > 0)
    x_fit = x[positive].astype(float)
    y_fit = y[positive].astype(float)
    if len(x_fit) < 2:
        raise ValueError("Need at least two non-zero frequency points for decay fitting.")

    log_y = np.log(y_fit)

    power_slope, power_intercept = np.polyfit(np.log(x_fit), log_y, 1)
    power_a = float(np.exp(power_intercept))
    power_b = float(-power_slope)
    power_pred = power_a * np.power(x_fit, -power_b)
    power_r2 = _r2(y_fit, power_pred)

    exp_slope, exp_intercept = np.polyfit(x_fit, log_y, 1)
    exp_a = float(np.exp(exp_intercept))
    exp_b = float(-exp_slope)
    exp_pred = exp_a * np.exp(-exp_b * x_fit)
    exp_r2 = _r2(y_fit, exp_pred)

    if power_r2 >= exp_r2:
        return {
            "model": "power",
            "a": power_a,
            "b": power_b,
            "r2": float(power_r2),
            "power_a": power_a,
            "power_b": power_b,
            "power_r2": float(power_r2),
            "exp_a": exp_a,
            "exp_b": exp_b,
            "exp_r2": float(exp_r2),
        }
    return {
        "model": "exponential",
        "a": exp_a,
        "b": exp_b,
        "r2": float(exp_r2),
        "power_a": power_a,
        "power_b": power_b,
        "power_r2": float(power_r2),
        "exp_a": exp_a,
        "exp_b": exp_b,
        "exp_r2": float(exp_r2),
    }


def _predict(model: str, a: float, b: float, x: np.ndarray) -> np.ndarray:
    if model == "power":
        return a * np.power(x, -b)
    return a * np.exp(-b * x)


def _load_counts(case_dir: Path, count_col: str, x_max: int | None) -> pd.DataFrame:
    event_path = case_dir / "ae_clustered_events.csv"
    if not event_path.exists():
        raise FileNotFoundError(f"Missing {event_path}; run AE clustering first.")
    events = pd.read_csv(event_path)
    if count_col not in events.columns:
        raise KeyError(f"Column {count_col!r} not found in {event_path}.")

    counts = pd.to_numeric(events[count_col], errors="coerce").dropna().astype(int)
    counts = counts[counts > 0]
    if counts.empty:
        raise ValueError(f"No positive integer values found in column {count_col!r}.")

    max_count = int(x_max) if x_max is not None else int(counts.max())
    x = np.arange(1, max_count + 1)
    freq = counts.value_counts().reindex(x, fill_value=0).sort_index().to_numpy(dtype=int)
    return pd.DataFrame({"microcrack_count": x, "frequency": freq})


def plot_case(
    case_dir: Path,
    count_col: str = "hit_count",
    output_prefix: str = "ae_microcrack_count_distribution",
    x_max: int | None = None,
) -> None:
    data = _load_counts(case_dir, count_col, x_max)
    x = data["microcrack_count"].to_numpy(dtype=float)
    y = data["frequency"].to_numpy(dtype=float)
    fit = _fit_decay(x, y)

    x_curve = np.linspace(float(x.min()), float(x.max()), 400)
    y_curve = _predict(str(fit["model"]), float(fit["a"]), float(fit["b"]), x_curve)
    data["fit_prediction"] = _predict(str(fit["model"]), float(fit["a"]), float(fit["b"]), x)
    data.to_csv(case_dir / f"{output_prefix}_source.csv", index=False)
    pd.DataFrame([fit]).to_csv(case_dir / f"{output_prefix}_fit.csv", index=False)

    apply_publication_style(font_size=15, axes_linewidth=2.0)
    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=300)

    bars = ax.bar(
        x,
        y,
        width=0.72,
        color=PALETTE["blue_secondary"],
        edgecolor=PALETTE["neutral_dark"],
        linewidth=1.2,
        label="Frequency",
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

    y_max = float(y.max())
    label_offset = max(y_max * 0.018, 1.0)
    for bar, value in zip(bars, y):
        if value <= 0:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + label_offset,
            f"{int(value)}",
            ha="center",
            va="bottom",
            fontsize=12,
            color=PALETTE["neutral_black"],
        )

    if fit["model"] == "power":
        equation = f"N = {float(fit['a']):.1f}x$^{{-{float(fit['b']):.2f}}}$"
    else:
        equation = f"N = {float(fit['a']):.1f}e$^{{-{float(fit['b']):.2f}x}}$"
    ax.text(
        0.97,
        0.68,
        equation + f"\n$R^2$ = {float(fit['r2']):.3f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=13,
        color=PALETTE["neutral_black"],
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 2.0},
    )

    ax.set_xlabel("Micro-crack number contained in an AE event", fontweight="bold")
    ax.set_ylabel("Frequency", fontweight="bold")
    ax.set_xlim(0.35, float(x.max()) + 0.65)
    ax.set_ylim(0, y_max * 1.18)
    ax.set_xticks(x.astype(int))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    ax.tick_params(axis="both", width=2.0, length=6, colors=PALETTE["neutral_black"])
    ax.spines["left"].set_color(PALETTE["neutral_black"])
    ax.spines["bottom"].set_color(PALETTE["neutral_black"])
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_linewidth(2.0)
    ax.grid(False)
    ax.legend([bars, line], ["Frequency", "Fitting curve"], loc="upper right", frameon=False)

    finalize_figure(fig, case_dir / output_prefix)
    print(f"Saved {case_dir / (output_prefix + '.svg')}")
    print(
        f"Counts 1-{int(x.max())}; model={fit['model']}; "
        f"a={float(fit['a']):.4f}; b={float(fit['b']):.4f}; R2={float(fit['r2']):.4f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="PFC case directory, e.g. b45_d14")
    parser.add_argument("--count-col", default="hit_count", help="AE event micro-crack count column")
    parser.add_argument("--output-prefix", default="ae_microcrack_count_distribution", help="Output file prefix")
    parser.add_argument("--x-max", type=int, default=None, help="Optional maximum integer x tick to show")
    args = parser.parse_args()
    plot_case(args.case, count_col=args.count_col, output_prefix=args.output_prefix, x_max=args.x_max)


if __name__ == "__main__":
    main()
