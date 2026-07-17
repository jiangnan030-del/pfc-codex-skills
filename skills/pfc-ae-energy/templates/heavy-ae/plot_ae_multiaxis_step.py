#!/usr/bin/env python3
"""Plot a Step/1e4 multi-axis stress, AE, and crack-count figure for a PFC case."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def _read_inputs(case_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    step_path = case_dir / "stress_strain_step.csv"
    event_path = case_dir / "ae_clustered_events.csv"
    if not step_path.exists():
        raise FileNotFoundError(f"Missing {step_path}; rerun PFC export with Step history enabled.")
    if not event_path.exists():
        raise FileNotFoundError(f"Missing {event_path}; run AE clustering/post-processing first.")
    return pd.read_csv(step_path), pd.read_csv(event_path)


def _map_events_to_step(step_df: pd.DataFrame, events_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Map AE event strain positions to raw and load-relative Step/1e4."""
    step_raw = step_df["step_1e4"].to_numpy(dtype=float)
    step_load = (step_df["step"].to_numpy(dtype=float) - float(step_df["step"].iloc[0])) / 10000.0
    strain_abs = np.abs(step_df["strain"].to_numpy(dtype=float))

    order = np.argsort(strain_abs)
    event_strain = events_df["strain_start"].to_numpy(dtype=float)
    event_load_x = np.interp(event_strain, strain_abs[order], step_load[order])
    event_raw_x = np.interp(event_strain, strain_abs[order], step_raw[order])
    return event_load_x, event_raw_x


def plot_case(case_dir: Path, bins: int = 45, output_prefix: str = "ae_multiaxis_step") -> None:
    step_df, events_df = _read_inputs(case_dir)
    event_load_x, event_raw_x = _map_events_to_step(step_df, events_df)

    step_raw = step_df["step_1e4"].to_numpy(dtype=float)
    step_load = (step_df["step"].to_numpy(dtype=float) - float(step_df["step"].iloc[0])) / 10000.0
    stress_raw = step_df["stress_mpa"].to_numpy(dtype=float)
    stress = _prepare_stress_for_plot(step_load, stress_raw)
    crack = step_df["crack_num"].to_numpy(dtype=float)
    strain_abs = np.abs(step_df["strain"].to_numpy(dtype=float))

    x_max = max(0.24, float(np.nanmax(step_load)) * 1.05)
    bar_edges = np.linspace(0.0, x_max, bins + 1)
    counts, _ = np.histogram(event_load_x, bins=bar_edges)
    bar_centers = 0.5 * (bar_edges[:-1] + bar_edges[1:])
    bar_width = np.diff(bar_edges)
    ae_ratio = counts / len(events_df) * 100.0 if len(events_df) else counts.astype(float)

    order = np.argsort(event_load_x)
    ae_cum_x = event_load_x[order]
    ae_cum = np.arange(1, len(ae_cum_x) + 1)

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "axes.linewidth": 1.25,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    fig, ax1 = plt.subplots(figsize=(7.3, 6.4), dpi=260)
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax4 = ax1.twinx()
    ax3.spines["right"].set_position(("axes", 1.15))
    ax4.spines["right"].set_position(("axes", 1.30))
    for ax, color in [(ax2, "red"), (ax3, "blue"), (ax4, "lime")]:
        ax.spines["right"].set_visible(True)
        ax.spines["right"].set_color(color)
        ax.spines["right"].set_linewidth(1.25)
        ax.tick_params(axis="y", colors=color, width=1.15, length=4)

    ax1.plot(step_load, stress, color="black", lw=1.65, label="Stress", zorder=4)
    ax2.bar(
        bar_centers,
        ae_ratio,
        width=bar_width * 0.86,
        color="red",
        edgecolor="red",
        linewidth=0.2,
        alpha=0.86,
        label="AE ratio",
        zorder=1,
    )
    ax3.plot(ae_cum_x, ae_cum, color="blue", lw=1.65, label="AE Count", zorder=3)
    ax4.plot(step_load, crack, color="lime", lw=1.55, label="Total crack number", zorder=2)

    _annotate_feature_points(ax1, step_load, stress, x_max)

    ax1.set_xlim(0, x_max)
    ax1.set_ylim(0, max(0.085, float(np.nanmax(stress)) * 1.10))
    ax2.set_ylim(0, max(2.0, float(np.nanmax(ae_ratio)) * 1.15 if len(ae_ratio) else 2.0))
    ax3.set_ylim(0, _nice_axis_limit(len(events_df) * 1.08))
    ax4.set_ylim(0, _nice_axis_limit(float(np.nanmax(crack)) * 1.08))
    ax3.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax4.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    ax2.spines["right"].set_bounds(*ax2.get_ylim())
    ax3.spines["right"].set_bounds(*ax3.get_ylim())
    ax4.spines["right"].set_bounds(*ax4.get_ylim())

    ax1.set_xlabel(r"Step/$10^4$", fontsize=12.5, fontweight="bold")
    ax1.set_ylabel("Stress/MPa", fontsize=12.5, fontweight="bold")
    ax2.set_ylabel("AE ratio/%", fontsize=12.5, color="red", fontweight="bold", labelpad=8)
    ax3.set_ylabel("AE Count", fontsize=12.5, color="blue", fontweight="bold", labelpad=16)
    ax4.set_ylabel("Total crack number", fontsize=12.5, color="lime", fontweight="bold", labelpad=20)
    ax1.tick_params(axis="both", width=1.15, length=4)
    ax1.minorticks_on()
    ax2.minorticks_on()
    ax3.minorticks_on()
    ax4.minorticks_on()

    handles = [
        plt.Line2D([0], [0], color="lime", lw=1.6, label="Total crack number"),
        plt.Line2D([0], [0], color="black", lw=1.6, label="Stress"),
        plt.Rectangle((0, 0), 1, 1, color="red", label="AE ratio"),
        plt.Line2D([0], [0], color="blue", lw=1.6, label="AE Count"),
    ]
    ax1.legend(
        handles=handles,
        loc="upper left",
        frameon=False,
        fontsize=10.5,
        bbox_to_anchor=(0.045, 0.985),
        handlelength=2.55,
        handletextpad=0.45,
    )
    fig.tight_layout()
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(case_dir / f"{output_prefix}.{ext}", bbox_inches="tight")
    plt.close(fig)

    _write_source_data(
        case_dir,
        output_prefix,
        step_df,
        step_raw,
        step_load,
        strain_abs,
        stress_raw,
        stress,
        crack,
        bar_centers,
        counts,
        ae_ratio,
        events_df,
        event_load_x,
        event_raw_x,
    )


def _prepare_stress_for_plot(step_load: np.ndarray, stress_raw: np.ndarray) -> np.ndarray:
    """Start the plotted stress at O=(0,0) without changing the peak value.

    The exported PFC history begins after specimen generation, so the first
    stress sample may contain residual wall force. For the visual O point, only
    the very short seating segment is redrawn as a smooth ramp into the raw
    curve; all later values, including UCS/peak stress, remain unchanged.
    """
    stress = stress_raw.copy()
    join_idx = int(np.searchsorted(step_load, 0.03, side="left"))
    join_idx = max(1, min(join_idx, len(stress) - 1))
    stress[: join_idx + 1] = np.linspace(0.0, stress_raw[join_idx], join_idx + 1)
    return stress


def _annotate_feature_points(ax: plt.Axes, step_load: np.ndarray, stress: np.ndarray, x_max: float) -> None:
    peak_i = int(np.nanargmax(stress))
    label_offset = float(np.nanmax(stress)) * 0.04
    rel_positions = {"O": 0.00, "A": 0.30, "B": 0.48, "C": 0.66, "D": 0.82, "E": step_load[peak_i] / x_max, "F": 0.98}
    for label, rel in rel_positions.items():
        x_val = np.clip(rel * x_max, float(step_load.min()), float(step_load.max()))
        if label == "E":
            x_val = step_load[peak_i]
        if label == "F":
            post = np.arange(peak_i + 1, len(stress))
            candidates = post[stress[post] <= 0.75 * stress[peak_i]] if len(post) else []
            x_val = step_load[int(candidates[0])] if len(candidates) else step_load[-1]
        y_val = np.interp(x_val, step_load, stress)
        ax.scatter([x_val], [y_val], s=25, color="blue", zorder=6)
        ax.text(x_val, y_val + label_offset, label, color="blue", fontsize=10.5, ha="center", va="bottom")


def _nice_axis_limit(value: float) -> float:
    """Return a compact rounded upper limit for count-style axes."""
    if not np.isfinite(value) or value <= 0:
        return 1.0
    if value <= 50:
        step = 5
    elif value <= 500:
        step = 50
    elif value <= 1000:
        step = 100
    else:
        step = 200
    return float(np.ceil(value / step) * step)


def _write_source_data(
    case_dir: Path,
    output_prefix: str,
    step_df: pd.DataFrame,
    step_raw: np.ndarray,
    step_load: np.ndarray,
    strain_abs: np.ndarray,
    stress_raw: np.ndarray,
    stress: np.ndarray,
    crack: np.ndarray,
    bar_centers: np.ndarray,
    counts: np.ndarray,
    ae_ratio: np.ndarray,
    events_df: pd.DataFrame,
    event_load_x: np.ndarray,
    event_raw_x: np.ndarray,
) -> None:
    source = pd.DataFrame(
        {
            "step_raw": step_df["step"],
            "step_raw_1e4": step_raw,
            "step_load_1e4": step_load,
            "strain_abs": strain_abs,
            "stress_raw_mpa": stress_raw,
            "stress_plot_mpa": stress,
            "crack_num": crack,
            "crack_tension_num": step_df["crack_tension_num"],
            "crack_shear_num": step_df["crack_shear_num"],
        }
    )
    source.to_csv(case_dir / f"{output_prefix}_source.csv", index=False)
    pd.DataFrame(
        {
            "step_load_1e4_bin_center": bar_centers,
            "ae_event_count": counts,
            "ae_ratio_percent": ae_ratio,
        }
    ).to_csv(case_dir / f"{output_prefix}_bar_source.csv", index=False)
    pd.DataFrame(
        {
            "event_id": events_df["event_id"],
            "event_step_load_1e4": event_load_x,
            "event_step_raw_1e4": event_raw_x,
            "strain_start": events_df["strain_start"],
        }
    ).to_csv(case_dir / f"{output_prefix}_event_source.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="PFC case directory, e.g. b45_d14")
    parser.add_argument("--bins", type=int, default=45, help="Number of AE-ratio bins")
    parser.add_argument("--output-prefix", default="ae_multiaxis_step", help="Output file prefix")
    args = parser.parse_args()
    plot_case(args.case, bins=args.bins, output_prefix=args.output_prefix)
    print(f"Saved {args.case / (args.output_prefix + '.png')}")


if __name__ == "__main__":
    main()
