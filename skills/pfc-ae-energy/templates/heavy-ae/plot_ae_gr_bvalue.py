#!/usr/bin/env python3
"""Nature-style AE magnitude-frequency and Gutenberg-Richter b-value plot."""
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
    "blue_main": "#0F4D92",
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
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["axes.linewidth"] = axes_linewidth
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"


def finalize_figure(fig: plt.Figure, output_base: Path, dpi: int = 300) -> None:
    """Save SVG as the primary editable output and PNG as a raster preview."""
    fig.tight_layout(pad=1.5)
    fig.savefig(output_base.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _nice_bins(values: np.ndarray, bin_width: float) -> np.ndarray:
    lo = np.floor(np.nanmin(values) / bin_width) * bin_width
    hi = np.ceil(np.nanmax(values) / bin_width) * bin_width
    return np.arange(lo, hi + bin_width * 1.5, bin_width)


def _fit_gr(mag: np.ndarray, logn: np.ndarray, freq: np.ndarray, min_points: int = 4) -> dict[str, float]:
    """Fit logN = a - bM on the post-peak descending branch."""
    valid = np.isfinite(mag) & np.isfinite(logn) & (freq > 0)
    if valid.sum() < min_points:
        raise ValueError("Not enough non-empty magnitude bins for Gutenberg-Richter fit.")

    mag_v = mag[valid]
    logn_v = logn[valid]
    freq_v = freq[valid]
    peak_local = int(np.argmax(freq_v))

    fit_mask_v = np.zeros_like(mag_v, dtype=bool)
    fit_mask_v[peak_local:] = True
    fit_mask_v &= np.isfinite(logn_v) & (logn_v > 0)

    tail_ok = fit_mask_v & (10 ** logn_v >= 2)
    if tail_ok.sum() >= min_points:
        fit_mask_v = tail_ok

    if fit_mask_v.sum() < min_points:
        start = max(0, len(mag_v) // 2)
        fit_mask_v[:] = False
        fit_mask_v[start:] = True
        fit_mask_v &= np.isfinite(logn_v) & (logn_v > 0)

    if fit_mask_v.sum() < 2:
        raise ValueError("Not enough points in the selected fitting branch.")

    x = mag_v[fit_mask_v]
    y = logn_v[fit_mask_v]
    slope, intercept = np.polyfit(x, y, 1)
    y_hat = slope * x + intercept
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    return {
        "a": float(intercept),
        "b": float(-slope),
        "slope": float(slope),
        "r2": float(r2),
        "fit_min_magnitude": float(np.min(x)),
        "fit_max_magnitude": float(np.max(x)),
        "fit_points": int(len(x)),
        "peak_magnitude": float(mag_v[peak_local]),
    }


def _export_tables(
    case_dir: Path,
    output_prefix: str,
    centers: np.ndarray,
    edges: np.ndarray,
    freq: np.ndarray,
    cumulative_n: np.ndarray,
    logn: np.ndarray,
    fit: dict[str, float],
) -> None:
    source = pd.DataFrame(
        {
            "magnitude_bin_center": centers,
            "magnitude_bin_left": edges[:-1],
            "magnitude_bin_right": edges[1:],
            "frequency": freq,
            "cumulative_N": cumulative_n.astype(int),
            "logN": logn,
        }
    )
    source.to_csv(case_dir / f"{output_prefix}_source.csv", index=False)
    pd.DataFrame([fit]).to_csv(case_dir / f"{output_prefix}_fit.csv", index=False)


def plot_case(
    case_dir: Path,
    magnitude_col: str = "moment_magnitude",
    bin_width: float = 0.10,
    output_prefix: str = "ae_gr_bvalue",
) -> None:
    event_path = case_dir / "ae_clustered_events.csv"
    if not event_path.exists():
        raise FileNotFoundError(f"Missing {event_path}; run AE clustering first.")

    events = pd.read_csv(event_path)
    if magnitude_col not in events.columns:
        raise KeyError(f"Column {magnitude_col!r} not found in {event_path}.")

    magnitudes = pd.to_numeric(events[magnitude_col], errors="coerce").dropna().to_numpy(dtype=float)
    if len(magnitudes) < 5:
        raise ValueError("Not enough AE events with valid magnitudes.")

    bins = _nice_bins(magnitudes, bin_width)
    freq, edges = np.histogram(magnitudes, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    cumulative_n = np.array([(magnitudes >= c).sum() for c in centers], dtype=float)
    logn = np.full_like(cumulative_n, np.nan, dtype=float)
    positive = cumulative_n > 0
    logn[positive] = np.log10(cumulative_n[positive])

    fit = _fit_gr(centers, logn, freq)
    fit_x = np.linspace(fit["fit_min_magnitude"], fit["fit_max_magnitude"], 200)
    fit_y = fit["slope"] * fit_x + fit["a"]
    _export_tables(case_dir, output_prefix, centers, edges, freq, cumulative_n, logn, fit)

    apply_publication_style(font_size=15, axes_linewidth=2.0)
    fig, ax1 = plt.subplots(figsize=(7.2, 5.2), dpi=300)
    ax2 = ax1.twinx()

    ax1.set_zorder(ax2.get_zorder() + 1)
    ax1.patch.set_visible(False)

    bars = ax2.bar(
        centers,
        freq,
        width=bin_width * 0.86,
        color=PALETTE["blue_secondary"],
        edgecolor=PALETTE["neutral_dark"],
        linewidth=1.1,
        alpha=0.88,
        label="Frequency",
        zorder=1,
    )
    scatter = ax1.scatter(
        centers,
        logn,
        marker="s",
        s=48,
        facecolors="none",
        edgecolors=PALETTE["neutral_black"],
        linewidths=1.5,
        label="logN",
        zorder=4,
    )
    line, = ax1.plot(
        fit_x,
        fit_y,
        color=PALETTE["red_strong"],
        lw=2.6,
        label="Fitting curve",
        zorder=5,
    )

    for spine in ["left", "bottom"]:
        ax1.spines[spine].set_color(PALETTE["neutral_black"])
        ax1.spines[spine].set_linewidth(2.0)
    ax1.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_color(PALETTE["blue_main"])
    ax2.spines["right"].set_linewidth(2.0)

    ax1.set_xlabel("Magnitude", fontweight="bold")
    ax1.set_ylabel("logN", fontweight="bold")
    ax2.set_ylabel("Frequency", color=PALETTE["blue_main"], fontweight="bold")
    ax1.tick_params(axis="both", width=2.0, length=6, colors=PALETTE["neutral_black"])
    ax2.tick_params(axis="y", width=2.0, length=6, colors=PALETTE["blue_main"])

    ax1.grid(False)
    ax2.grid(False)
    ax1.set_xlim(edges[0] - bin_width * 0.75, edges[-1] + bin_width * 0.75)
    ax1.set_ylim(0, np.nanmax(logn) * 1.12)
    ax2.set_ylim(0, max(1, float(freq.max()) * 1.18))
    ax1.yaxis.set_major_locator(MaxNLocator(nbins=5))
    ax2.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=6))

    eq_text = f"logN = {fit['slope']:.2f}M {fit['a']:+.2f}"
    stats_text = f"$R^2$ = {fit['r2']:.3f}\nb = {fit['b']:.2f}"
    ax1.text(
        0.97,
        0.95,
        eq_text + "\n" + stats_text,
        transform=ax1.transAxes,
        ha="right",
        va="top",
        color=PALETTE["neutral_black"],
        fontsize=14,
    )

    ax1.legend(
        [scatter, bars, line],
        ["logN", "Frequency", "Fitting curve"],
        loc="upper left",
        frameon=False,
        bbox_to_anchor=(0.04, 0.94),
        handlelength=2.0,
        handletextpad=0.5,
    )
    ax1.set_title("Relationship between number and magnitude of AE event", fontweight="bold", pad=12)

    finalize_figure(fig, case_dir / output_prefix)

    print(f"Saved {case_dir / (output_prefix + '.svg')}")
    print(
        f"Magnitude range {magnitudes.min():.4f} to {magnitudes.max():.4f}; "
        f"bin_width={bin_width}; a={fit['a']:.4f}; b={fit['b']:.4f}; R2={fit['r2']:.4f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="PFC case directory, e.g. b45_d14")
    parser.add_argument("--magnitude-col", default="moment_magnitude", help="Magnitude column in ae_clustered_events.csv")
    parser.add_argument("--bin-width", type=float, default=0.10, help="Magnitude histogram bin width")
    parser.add_argument("--output-prefix", default="ae_gr_bvalue", help="Output file prefix")
    args = parser.parse_args()
    plot_case(args.case, magnitude_col=args.magnitude_col, bin_width=args.bin_width, output_prefix=args.output_prefix)


if __name__ == "__main__":
    main()
