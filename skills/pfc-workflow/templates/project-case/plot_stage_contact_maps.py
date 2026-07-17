from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import rcParams
from matplotlib.collections import LineCollection
from matplotlib.ticker import FuncFormatter
from scipy.interpolate import griddata

from config import CONTACT_STAGES, MODEL_TO_MM, SPECIMEN_EXTENT_MODEL, case_dir, specimen_extent_mm

rcParams["font.family"] = "Times New Roman"
rcParams["font.size"] = 11
rcParams["axes.linewidth"] = 1.0
rcParams["xtick.direction"] = "in"
rcParams["ytick.direction"] = "in"

SPECIMEN_EXTENT = SPECIMEN_EXTENT_MODEL
SPECIMEN_EXTENT_MM = specimen_extent_mm()
GRID_RESOLUTION = 200
PLOT_DPI = 300
FORCE_QUANTILE = 0.82
BASE_FORCECHAIN_COLOR = "#2d7ff9"
BASE_FORCECHAIN_ALPHA = 0.85
BASE_FORCECHAIN_WIDTH = 0.18


def fmt_mm(value, _pos=None):
    return f"{value:.1f}"


def load_contacts(case_path: Path, stage: str) -> pd.DataFrame | None:
    path = case_path / f"plotdata_contacts_stage_{stage}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    for col in ["x", "y", "x1", "y1", "x2", "y2", "fx", "fy", "fmag"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["x1", "y1", "x2", "y2", "fmag"])
    return df if not df.empty else None


def load_measures(case_path: Path, stage: str) -> pd.DataFrame | None:
    path = case_path / f"plotdata_measures_stage_{stage}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    for col in ["x", "y", "porosity", "coord_num"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["x", "y", "coord_num"])
    return df if not df.empty else None


def setup_axes(ax, title: str) -> None:
    ax.set_xlim(*SPECIMEN_EXTENT_MM)
    ax.set_ylim(*SPECIMEN_EXTENT_MM)
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(title)
    ax.xaxis.set_major_formatter(FuncFormatter(fmt_mm))
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_mm))


def segments_from_df(df: pd.DataFrame) -> np.ndarray:
    values = np.stack([df[["x1", "y1"]].to_numpy(dtype=float), df[["x2", "y2"]].to_numpy(dtype=float)], axis=1)
    return values * MODEL_TO_MM


def plot_forcechain(case_path: Path, stage: str) -> None:
    df = load_contacts(case_path, stage)
    if df is None:
        print(f"skip forcechain {stage}")
        return
    threshold = df["fmag"].quantile(FORCE_QUANTILE)
    strong = df[df["fmag"] >= threshold].copy()
    if strong.empty:
        print(f"skip forcechain {stage}: threshold empty")
        return

    base_segments = segments_from_df(df)
    segments = segments_from_df(strong)
    values = strong["fmag"].to_numpy(dtype=float)
    vmin = values.min()
    vmax = values.max()
    widths = np.full_like(values, 1.35, dtype=float) if vmax <= vmin else 0.45 + 1.55 * (values - vmin) / (vmax - vmin)

    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    ax.add_collection(
        LineCollection(
            base_segments,
            colors=BASE_FORCECHAIN_COLOR,
            linewidths=BASE_FORCECHAIN_WIDTH,
            alpha=BASE_FORCECHAIN_ALPHA,
            zorder=1,
        )
    )
    collection = LineCollection(segments, cmap="turbo", linewidths=widths)
    collection.set_array(values)
    collection.set_alpha(0.98)
    collection.set_zorder(2)
    ax.add_collection(collection)
    setup_axes(ax, f"Stage {stage} Force Chains")
    cbar = plt.colorbar(collection, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("contact force magnitude")
    fig.tight_layout()
    fig.savefig(case_path / f"stage_{stage}_contact_forcechain_filtered.png", dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)


def plot_coordination(case_path: Path, stage: str) -> None:
    df = load_measures(case_path, stage)
    if df is None:
        print(f"skip coordination {stage}")
        return
    xi = np.linspace(SPECIMEN_EXTENT_MM[0], SPECIMEN_EXTENT_MM[1], GRID_RESOLUTION)
    yi = np.linspace(SPECIMEN_EXTENT_MM[0], SPECIMEN_EXTENT_MM[1], GRID_RESOLUTION)
    grid_x, grid_y = np.meshgrid(xi, yi)
    grid_z = griddata((df["x"] * MODEL_TO_MM, df["y"] * MODEL_TO_MM), df["coord_num"], (grid_x, grid_y), method="cubic")
    grid_z = np.ma.masked_invalid(grid_z)
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    contour = ax.contourf(grid_x, grid_y, grid_z, levels=20, cmap="viridis", extend="both")
    ax.contour(grid_x, grid_y, grid_z, levels=20, colors="k", linewidths=0.15, alpha=0.35)
    setup_axes(ax, f"Stage {stage} Coordination Number")
    cbar = plt.colorbar(contour, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label("coordination number")
    fig.tight_layout()
    fig.savefig(case_path / f"stage_{stage}_contact_coordination.png", dpi=PLOT_DPI, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot stage contact maps for one case.")
    parser.add_argument("case", help="Case name, for example Intact or b60_d20")
    args = parser.parse_args()

    case_path = case_dir(args.case)
    for stage in CONTACT_STAGES:
        plot_forcechain(case_path, stage)
        plot_coordination(case_path, stage)


if __name__ == "__main__":
    main()
