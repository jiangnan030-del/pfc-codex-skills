from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import AutoMinorLocator, MaxNLocator

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"


PALETTE = {
    "explosion": "#B64342",
    "shear": "#8BCF8B",
    "implosion": "#0F4D92",
    "stress": "#272727",
    "neutral_dark": "#4D4D4D",
    "neutral_black": "#272727",
    "white": "#FFFFFF",
}

ORDER = ["Implosion", "Shear", "Explosion"]
COLORS = {
    "Explosion": PALETTE["explosion"],
    "Shear": PALETTE["shear"],
    "Implosion": PALETTE["implosion"],
}


def apply_publication_style(font_size: float = 11.0, axes_linewidth: float = 1.35) -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["font.size"] = font_size
    plt.rcParams["axes.linewidth"] = axes_linewidth
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["xtick.direction"] = "in"
    plt.rcParams["ytick.direction"] = "in"
    plt.rcParams["xtick.major.width"] = axes_linewidth
    plt.rcParams["ytick.major.width"] = axes_linewidth
    plt.rcParams["xtick.minor.width"] = axes_linewidth * 0.75
    plt.rcParams["ytick.minor.width"] = axes_linewidth * 0.75


def finalize_figure(fig: plt.Figure, output_prefix: Path, dpi: int = 600) -> None:
    fig.tight_layout(pad=1.1, w_pad=2.3)
    fig.savefig(output_prefix.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _classify_iso(events: pd.DataFrame, iso_threshold: float) -> pd.DataFrame:
    required = {"mt_iso", "mt_dev_1", "mt_dev_2", "mt_dev_3"}
    if not required.issubset(events.columns):
        missing = sorted(required.difference(events.columns))
        raise ValueError(f"Missing tensor columns for ISO classification: {missing}")
    out = events.copy()
    mt_iso = out["mt_iso"].astype(float)
    mt_dev_max = out[["mt_dev_1", "mt_dev_2", "mt_dev_3"]].abs().max(axis=1).astype(float)
    denom = mt_iso.abs() + mt_dev_max
    out["source_iso"] = mt_iso.divide(denom.where(denom > 0.0, np.nan)).fillna(0.0)
    out["source_class"] = "Shear"
    out.loc[out["source_iso"] > iso_threshold, "source_class"] = "Explosion"
    out.loc[out["source_iso"] < -iso_threshold, "source_class"] = "Implosion"
    return out


def _stage_points(step_df: pd.DataFrame) -> dict[str, dict[str, float]]:
    step = step_df["step_load_1e4"].to_numpy(float)
    stress = step_df["stress_plot_mpa"].to_numpy(float)
    strain = step_df["strain_abs"].to_numpy(float)
    x_max = float(np.nanmax(step))
    peak_i = int(np.nanargmax(stress))
    points: dict[str, dict[str, float]] = {}
    for label, rel in {"O": 0.00, "A": 0.30, "B": 0.48, "C": 0.66, "D": 0.82}.items():
        idx = int(np.nanargmin(np.abs(step - rel * x_max)))
        points[label] = {"step": float(step[idx]), "stress": float(stress[idx]), "strain": float(strain[idx])}
    points["E"] = {"step": float(step[peak_i]), "stress": float(stress[peak_i]), "strain": float(strain[peak_i])}
    post = np.arange(peak_i + 1, len(step_df))
    candidates = post[stress[post] <= 0.75 * stress[peak_i]] if len(post) else []
    f_i = int(candidates[0]) if len(candidates) else len(step_df) - 1
    points["F"] = {"step": float(step[f_i]), "stress": float(stress[f_i]), "strain": float(strain[f_i])}
    return points


def _attach_event_step(events: pd.DataFrame, step_df: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()
    strain = step_df["strain_abs"].to_numpy(float)
    step = step_df["step_load_1e4"].to_numpy(float)
    stress = step_df["stress_plot_mpa"].to_numpy(float)
    order = np.argsort(strain)
    out["step_load_1e4"] = np.interp(out["strain_start"].abs().to_numpy(float), strain[order], step[order], left=step.min(), right=step.max())
    out["stress_interp_mpa"] = np.interp(out["strain_start"].abs().to_numpy(float), strain[order], stress[order], left=stress[0], right=stress[-1])
    return out


def _cumulative_source(events: pd.DataFrame, step_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    step_values = step_df["step_load_1e4"].to_numpy(float)
    for step_value in step_values:
        subset = events[events["step_load_1e4"] <= step_value]
        row = {"step_load_1e4": float(step_value)}
        for source_class in ["Explosion", "Shear", "Implosion"]:
            row[source_class.lower()] = int((subset["source_class"] == source_class).sum())
        rows.append(row)
    return pd.DataFrame(rows)


def _interval_counts(events: pd.DataFrame, points: dict[str, dict[str, float]]) -> pd.DataFrame:
    intervals = [
        ("BC", points["B"]["strain"], points["C"]["strain"]),
        ("CD", points["C"]["strain"], points["D"]["strain"]),
        ("DE", points["D"]["strain"], points["E"]["strain"]),
        ("EF", points["E"]["strain"], points["F"]["strain"]),
        ("OF", points["O"]["strain"], points["F"]["strain"]),
    ]
    rows = []
    strain_abs = events["strain_start"].abs()
    for label, start, end in intervals:
        if label == "OF":
            subset = events[(strain_abs >= start) & (strain_abs <= end)]
        else:
            subset = events[(strain_abs > start) & (strain_abs <= end)]
        counts = {source_class: int((subset["source_class"] == source_class).sum()) for source_class in ORDER}
        total = int(sum(counts.values()))
        row = {"stage": label, "total": total}
        for source_class in ORDER:
            row[source_class.lower()] = counts[source_class]
            row[f"{source_class.lower()}_percent"] = (counts[source_class] / total * 100.0) if total else 0.0
        rows.append(row)
    return pd.DataFrame(rows)


def _plot_stage_labels(ax: plt.Axes, points: dict[str, dict[str, float]], y_offset: float) -> None:
    for label in ["O", "A", "B", "C", "D", "E", "F"]:
        point = points[label]
        ax.scatter([point["step"]], [point["stress"]], s=28, color="blue", zorder=5)
        dy = y_offset
        if label == "F":
            dy = -1.25 * y_offset
        ax.text(point["step"], point["stress"] + dy, label, color="blue", fontsize=9.5, ha="center", va="bottom" if dy >= 0 else "top")


def build_figure(case_dir: Path, output_prefix: str, iso_threshold: float) -> None:
    apply_publication_style(font_size=11.0, axes_linewidth=1.35)
    events = pd.read_csv(case_dir / "ae_clustered_events.csv")
    step_df = pd.read_csv(case_dir / "ae_multiaxis_step_source.csv")
    events = _attach_event_step(_classify_iso(events, iso_threshold), step_df)
    points = _stage_points(step_df)
    cumulative = _cumulative_source(events, step_df)
    stage_percent = _interval_counts(events, points)

    counts = events["source_class"].value_counts().reindex(["Explosion", "Shear", "Implosion"], fill_value=0)
    print(f"[diagnostic] tensor_iso_classification: True; iso_threshold={iso_threshold:.3f}")
    print("[diagnostic] source counts: " + ", ".join(f"{name}={int(counts[name])}" for name in counts.index))
    print("[diagnostic] stage counts:")
    print(stage_percent[["stage", "total", "explosion", "shear", "implosion"]].to_string(index=False))

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(10.8, 5.4), gridspec_kw={"width_ratios": [1.05, 0.95]})

    step = step_df["step_load_1e4"].to_numpy(float)
    stress = step_df["stress_plot_mpa"].to_numpy(float)
    ax_a.plot(step, stress, color=PALETTE["stress"], lw=2.0, label="Stress", solid_capstyle="round")
    _plot_stage_labels(ax_a, points, y_offset=max(stress) * 0.06)
    ax_a.set_xlabel(r"Step/$10^4$", fontweight="bold")
    ax_a.set_ylabel("Stress/MPa", fontweight="bold")
    ax_a.set_xlim(float(step.min()), float(step.max()) * 1.03)
    ax_a.set_ylim(0.0, float(stress.max()) * 1.16)
    ax_a.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax_a.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax_a.tick_params(length=5, width=1.35)
    ax_a.tick_params(which="minor", length=3, width=1.0)

    ax_cum = ax_a.twinx()
    markevery = max(1, len(cumulative) // 18)
    for source_class in ["Implosion", "Shear", "Explosion"]:
        column = source_class.lower()
        ax_cum.plot(
            cumulative["step_load_1e4"],
            cumulative[column],
            color=COLORS[source_class],
            lw=1.9,
            marker="^",
            markevery=markevery,
            ms=5.2,
            mec=COLORS[source_class],
            mfc=COLORS[source_class],
            label=source_class if source_class != "Shear" else "shear",
        )
    cumulative_max = max(1, int(cumulative[["explosion", "shear", "implosion"]].max().max()))
    cum_limit = max(100, int(np.ceil(cumulative_max / 100.0) * 100))
    ax_cum.set_ylim(0, cum_limit)
    ax_cum.set_ylabel("Cumulative Number", color=PALETTE["explosion"], fontweight="bold")
    ax_cum.spines["right"].set_visible(True)
    ax_cum.spines["right"].set_color(PALETTE["explosion"])
    ax_cum.tick_params(axis="y", colors=PALETTE["explosion"], length=5, width=1.35)
    ax_cum.yaxis.set_major_locator(MaxNLocator(6, integer=True))
    ax_cum.yaxis.set_minor_locator(AutoMinorLocator(2))

    legend_handles = [Line2D([0], [0], color=PALETTE["stress"], lw=2.0, label="Stress")]
    legend_handles += [
        Line2D([0], [0], color=COLORS["Implosion"], lw=1.9, marker="^", ms=5.2, label="Implosion"),
        Line2D([0], [0], color=COLORS["Shear"], lw=1.9, marker="^", ms=5.2, label="shear"),
        Line2D([0], [0], color=COLORS["Explosion"], lw=1.9, marker="^", ms=5.2, label="Explosion"),
    ]
    ax_a.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(0.02, 0.91), handlelength=2.1, handletextpad=0.45, fontsize=9.4)

    stages = stage_percent["stage"].tolist()
    x = np.arange(len(stages))
    bottom = np.zeros(len(stages), dtype=float)
    for source_class in ORDER:
        values = stage_percent[f"{source_class.lower()}_percent"].to_numpy(float)
        ax_b.bar(x, values, bottom=bottom, color=COLORS[source_class], edgecolor="white", linewidth=0.7, width=0.82, label=source_class)
        for xi, low, val in zip(x, bottom, values):
            if val >= 6.0:
                text_color = "white" if source_class in {"Explosion", "Implosion"} else "black"
                ax_b.text(xi, low + val / 2.0, f"{val:.0f}%", ha="center", va="center", fontsize=9.0, color=text_color)
        bottom += values
    ax_b.set_ylim(0, 100)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(stages, fontweight="bold")
    ax_b.set_xlabel("Stage", fontweight="bold")
    ax_b.set_ylabel("%", fontweight="bold")
    ax_b.yaxis.set_major_locator(MaxNLocator(6))
    ax_b.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax_b.tick_params(length=5, width=1.35)
    ax_b.tick_params(which="minor", length=3, width=1.0)
    ax_b.legend(
        handles=[Patch(facecolor=COLORS["Explosion"], label="Explosion"), Patch(facecolor=COLORS["Shear"], label="Shear"), Patch(facecolor=COLORS["Implosion"], label="Implosion")],
        loc="upper center",
        bbox_to_anchor=(0.5, 1.12),
        ncol=3,
        columnspacing=1.3,
        handlelength=1.4,
        fontsize=9.4,
    )

    ax_a.text(0.5, -0.27, "(a)", transform=ax_a.transAxes, ha="center", va="top", fontsize=15)
    ax_b.text(0.5, -0.27, "(b)", transform=ax_b.transAxes, ha="center", va="top", fontsize=15)

    output = case_dir / output_prefix
    cumulative.to_csv(case_dir / f"{output_prefix}_cumulative.csv", index=False)
    stage_percent.to_csv(case_dir / f"{output_prefix}_stage_percent.csv", index=False)
    finalize_figure(fig, output, dpi=600)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Fig.10 AE source fracture type panels from tensor-decomposed AE events.")
    parser.add_argument("case_dir", nargs="?", default="b45_d14", type=Path)
    parser.add_argument("--output-prefix", default="fig10_ae_source_types")
    parser.add_argument("--iso-threshold", type=float, default=0.3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_figure(args.case_dir, args.output_prefix, args.iso_threshold)


if __name__ == "__main__":
    main()
