from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.lines import Line2D
from PIL import Image

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"


PALETTE = {
    "blue_main": "#0F4D92",
    "green_3": "#8BCF8B",
    "red_strong": "#B64342",
    "neutral_dark": "#4D4D4D",
    "neutral_black": "#272727",
    "white": "#FFFFFF",
}


def apply_publication_style(font_size: float = 8, axes_linewidth: float = 1.0) -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["font.size"] = font_size
    plt.rcParams["axes.linewidth"] = axes_linewidth
    plt.rcParams["legend.frameon"] = False
    plt.rcParams["axes.spines.top"] = True
    plt.rcParams["axes.spines.right"] = True


def finalize_figure(fig: plt.Figure, output_prefix: Path, dpi: int = 600) -> None:
    fig.savefig(output_prefix.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def _read_image(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(path)
    with Image.open(path) as img:
        return np.asarray(img.convert("RGB"))


def _crop_white_margin(img: np.ndarray, tolerance: int = 248, pad: int = 8) -> np.ndarray:
    mask = np.any(img < tolerance, axis=2)
    if not np.any(mask):
        return img
    ys, xs = np.where(mask)
    y0 = max(int(ys.min()) - pad, 0)
    y1 = min(int(ys.max()) + pad + 1, img.shape[0])
    x0 = max(int(xs.min()) - pad, 0)
    x1 = min(int(xs.max()) + pad + 1, img.shape[1])
    return img[y0:y1, x0:x1]


def _stage_targets(case_dir: Path) -> dict[str, float]:
    source = pd.read_csv(case_dir / "ae_multiaxis_step_source.csv")
    x = source["step_load_1e4"].to_numpy(float)
    stress = source["stress_plot_mpa"].to_numpy(float)
    strain = source["strain_abs"].to_numpy(float)
    x_max = float(np.nanmax(x))
    peak_i = int(np.nanargmax(stress))
    targets: dict[str, float] = {}
    for label, rel in {"A": 0.30, "B": 0.48, "C": 0.66, "D": 0.82}.items():
        idx = int(np.nanargmin(np.abs(x - rel * x_max)))
        targets[label] = float(strain[idx])
    targets["E"] = float(strain[peak_i])
    post = np.arange(peak_i + 1, len(source))
    candidates = post[stress[post] <= 0.75 * stress[peak_i]] if len(post) else []
    f_i = int(candidates[0]) if len(candidates) else len(source) - 1
    targets["F"] = float(strain[f_i])
    return targets


def _classify_source_types(events: pd.DataFrame, iso_threshold: float) -> tuple[pd.Series, pd.Series, bool]:
    required = {"mt_iso", "mt_dev_1", "mt_dev_2", "mt_dev_3"}
    if required.issubset(events.columns):
        mt_iso = events["mt_iso"].astype(float)
        mt_dev_max = events[["mt_dev_1", "mt_dev_2", "mt_dev_3"]].abs().max(axis=1).astype(float)
        denominator = mt_iso.abs() + mt_dev_max
        source_iso = mt_iso.divide(denominator.where(denominator > 0.0, np.nan)).fillna(0.0)
        source_class = pd.Series("Shear", index=events.index, dtype="object")
        source_class[source_iso > iso_threshold] = "Explosion"
        source_class[source_iso < -iso_threshold] = "Implosion"
        return source_class, source_iso, True

    if "source_type_tk" not in events.columns:
        raise ValueError("Need mt_iso/mt_dev_1/2/3 or source_type_tk to classify AE source types.")
    text = events["source_type_tk"].astype(str).str.lower()
    source_class = pd.Series("Explosion", index=events.index, dtype="object")
    source_class[text.str.contains("shear|double", regex=True, na=False)] = "Shear"
    source_class[text.str.contains("implosion|compress|implosive", regex=True, na=False)] = "Implosion"
    return source_class, pd.Series(np.nan, index=events.index, dtype="float"), False


def _marker_sizes(magnitude: pd.Series, min_size: float = 13.0, max_size: float = 88.0) -> np.ndarray:
    mag = magnitude.to_numpy(float)
    if len(mag) == 0:
        return np.array([])
    m0 = float(np.nanmin(mag))
    m1 = float(np.nanmax(mag))
    if not np.isfinite(m0) or not np.isfinite(m1) or abs(m1 - m0) < 1e-12:
        return np.full_like(mag, (min_size + max_size) / 2.0, dtype=float)
    norm = np.clip((mag - m0) / (m1 - m0), 0.0, 1.0)
    return min_size + (norm ** 1.55) * (max_size - min_size)


def _style_panel(ax: plt.Axes, linewidth: float = 1.0) -> None:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(linewidth)
        spine.set_edgecolor(PALETTE["neutral_dark"])


def _plot_ae_stage(ax: plt.Axes, events: pd.DataFrame, stage: str, targets: dict[str, float], extent: tuple[float, float, float, float]) -> dict[str, int]:
    subset = events[events["strain_start"].abs() <= targets[stage]].copy()
    colors = {
        "Explosion": PALETTE["red_strong"],
        "Shear": PALETTE["green_3"],
        "Implosion": PALETTE["blue_main"],
    }
    for source_class in ["Explosion", "Shear", "Implosion"]:
        part = subset[subset["source_class"] == source_class]
        if part.empty:
            continue
        ax.scatter(
            part["center_x_mm"],
            part["center_y_mm"],
            s=_marker_sizes(part["moment_magnitude"]),
            facecolors="none",
            edgecolors=colors[source_class],
            linewidths=0.85,
            alpha=0.92,
            zorder=3,
        )
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.set_aspect("equal", adjustable="box")
    ax.set_facecolor("white")
    _style_panel(ax, linewidth=1.0)
    return {
        "stage": stage,
        "target_strain_abs": targets[stage],
        "ae_events": int(len(subset)),
        "explosion": int((subset.get("source_class") == "Explosion").sum()),
        "shear": int((subset.get("source_class") == "Shear").sum()),
        "implosion": int((subset.get("source_class") == "Implosion").sum()),
        "iso_min": float(subset["source_iso"].min()) if "source_iso" in subset and len(subset) else np.nan,
        "iso_max": float(subset["source_iso"].max()) if "source_iso" in subset and len(subset) else np.nan,
    }


def build_figure(case_dir: Path, output_prefix: str, crop_top: bool, iso_threshold: float, hide_top: bool = False) -> None:
    apply_publication_style(font_size=8, axes_linewidth=1.0)
    stages = list("ABCDEF")
    targets = _stage_targets(case_dir)
    events = pd.read_csv(case_dir / "ae_clustered_events.csv")
    events["source_class"], events["source_iso"], used_tensor_classification = _classify_source_types(events, iso_threshold)
    extent = (-20.0, 20.0, -20.0, 20.0)

    counts = events["source_class"].value_counts().reindex(["Explosion", "Shear", "Implosion"], fill_value=0)
    print(f"[diagnostic] ae_clustered_events.csv columns: {', '.join(events.columns)}")
    print(f"[diagnostic] tensor_iso_classification: {used_tensor_classification}; iso_threshold={iso_threshold:.3f}")
    print("[diagnostic] source counts: " + ", ".join(f"{name}={int(counts[name])}" for name in counts.index))

    if hide_top:
        fig = plt.figure(figsize=(14.0, 3.0), facecolor="white")
        gs = gridspec.GridSpec(
            2,
            6,
            height_ratios=[1.0, 0.28],
            left=0.035,
            right=0.985,
            bottom=0.18,
            top=0.84,
            wspace=0.18,
            hspace=0.18,
        )
    else:
        fig = plt.figure(figsize=(14.0, 5.0), facecolor="white")
        gs = gridspec.GridSpec(
            3,
            6,
            height_ratios=[1.0, 1.0, 0.22],
            left=0.025,
            right=0.985,
            bottom=0.12,
            top=0.91,
            wspace=0.035,
            hspace=0.12,
        )

    summary_rows = []
    for col, stage in enumerate(stages):
        if not hide_top:
            ax_top = fig.add_subplot(gs[0, col])
            clean_path = case_dir / f"fig9_clean_{stage}_balls_fractures.png"
            img_path = clean_path if clean_path.exists() else case_dir / f"fig9_{stage}_balls_fractures.png"
            img = _read_image(img_path)
            if crop_top and not clean_path.exists():
                img = _crop_white_margin(img)
            ax_top.imshow(img)
            _style_panel(ax_top, linewidth=1.0)
            ax_top.set_aspect("equal")
            ax_top.text(
                0.5,
                -0.075,
                stage,
                transform=ax_top.transAxes,
                ha="center",
                va="top",
                fontsize=9.5,
                fontweight="bold",
                color=PALETTE["neutral_black"],
            )

        ax_bottom = fig.add_subplot(gs[0 if hide_top else 1, col])
        summary_rows.append(_plot_ae_stage(ax_bottom, events, stage, targets, extent))
        ax_bottom.text(
            0.5,
            -0.075,
            stage,
            transform=ax_bottom.transAxes,
            ha="center",
            va="top",
            fontsize=9.5,
            fontweight="bold",
            color=PALETTE["neutral_black"],
        )

    # Row labels are placed beneath each row, matching the reference figure layout.
    if hide_top:
        fig.text(0.5, 0.155, "(b)", ha="center", va="center", fontsize=10.5, fontweight="bold")
        legend_ax = fig.add_subplot(gs[1, :])
    else:
        fig.text(0.5, 0.505, "(a)", ha="center", va="center", fontsize=10.5, fontweight="bold")
        fig.text(0.5, 0.118, "(b)", ha="center", va="center", fontsize=10.5, fontweight="bold")
        legend_ax = fig.add_subplot(gs[2, :])
    legend_ax.axis("off")
    ae_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=PALETTE["red_strong"], markersize=7, label="Explosion"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=PALETTE["green_3"], markersize=7, label="Shear"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=PALETTE["blue_main"], markersize=7, label="Implosion"),
    ]
    if hide_top:
        legend_ax.legend(handles=ae_handles, loc="center", bbox_to_anchor=(0.5, 0.55), ncol=3, handletextpad=0.45, columnspacing=1.15, fontsize=8.2)
        caption = "Simulation results of AE location, source fracture types and magnitude."
        subcaption = ""
    else:
        crack_handles = [
            Line2D([0], [0], marker="^", color="none", markerfacecolor=PALETTE["blue_main"], markeredgecolor=PALETTE["blue_main"], markersize=7, label="Micro-shear crack"),
            Line2D([0], [0], marker="^", color="none", markerfacecolor=PALETTE["red_strong"], markeredgecolor=PALETTE["red_strong"], markersize=7, label="Micro-tension crack"),
        ]
        leg1 = legend_ax.legend(handles=crack_handles, loc="center", bbox_to_anchor=(0.31, 0.55), ncol=2, handletextpad=0.45, columnspacing=1.15, fontsize=8.2)
        legend_ax.add_artist(leg1)
        legend_ax.legend(handles=ae_handles, loc="center", bbox_to_anchor=(0.72, 0.55), ncol=3, handletextpad=0.45, columnspacing=1.15, fontsize=8.2)
        caption = "Microscopic mechanism of the process of macro cracks."
        subcaption = "(a) DFN obtained by PFC. (b) Simulation results of AE location, source fracture types and magnitude."
    fig.text(0.5, 0.965, caption, ha="center", va="top", fontsize=10.5, fontweight="bold", color=PALETTE["neutral_black"])
    if subcaption:
        fig.text(0.5, 0.935, subcaption, ha="center", va="top", fontsize=8.5, color=PALETTE["neutral_black"])

    output = case_dir / output_prefix
    finalize_figure(fig, output, dpi=600)
    pd.DataFrame(summary_rows).to_csv(case_dir / f"{output_prefix}_summary.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Nature-style Fig.9 2x6 macro-crack mechanism panel figure.")
    parser.add_argument("case_dir", nargs="?", default="b45_d14", type=Path)
    parser.add_argument("--output-prefix", default="fig9_macrocrack_mechanism")
    parser.add_argument("--no-crop-top", action="store_true", help="Do not crop white margins from PFC GUI exports.")
    parser.add_argument("--iso-threshold", type=float, default=0.3, help="Feignier-Young ISO threshold for Explosion/Implosion classification.")
    parser.add_argument("--hide-top", action="store_true", help="Temporarily omit the PFC screenshot row and draw only the AE row.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_figure(args.case_dir, args.output_prefix, crop_top=not args.no_crop_top, iso_threshold=args.iso_threshold, hide_top=args.hide_top)


if __name__ == "__main__":
    main()
