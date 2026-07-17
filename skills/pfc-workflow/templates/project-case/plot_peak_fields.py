from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
from matplotlib.patches import Circle

from config import MODEL_TO_MM, case_dir


def read_csv_dict(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def filter_numeric_rows(rows: list[dict[str, str]], keys: tuple[str, ...]) -> list[dict[str, str]]:
    valid = []
    for row in rows:
        try:
            for key in keys:
                value = row.get(key)
                if value is None or str(value).strip() == "":
                    raise ValueError(key)
                float(value)
        except (TypeError, ValueError):
            continue
        valid.append(row)
    return valid


def to_float_array(rows: list[dict[str, str]], key: str) -> np.ndarray:
    return np.array([float(row[key]) for row in rows], dtype=float)


def plot_scalar_field(x: np.ndarray, y: np.ndarray, z: np.ndarray, out_path: Path, cbar_label: str, cmap: str) -> None:
    with mpl.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.linewidth": 0.8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    ):
        x_mm = x * MODEL_TO_MM
        y_mm = y * MODEL_TO_MM
        triang = mtri.Triangulation(x_mm, y_mm)
        fig, ax = plt.subplots(figsize=(5.5, 5.0))
        contour = ax.tricontourf(triang, z, levels=20, cmap=cmap)
        ax.set_aspect("equal")
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        cbar = fig.colorbar(contour, ax=ax, fraction=0.046, pad=0.03)
        cbar.set_label(cbar_label, fontsize=8)
        cbar.ax.tick_params(labelsize=7)
        fig.tight_layout()
        fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
        fig.savefig(out_path.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
        plt.close(fig)


def plot_porosity_field(x: np.ndarray, y: np.ndarray, porosity: np.ndarray, out_path: Path) -> None:
    with mpl.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.linewidth": 0.8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    ):
        x_mm = x * MODEL_TO_MM
        y_mm = y * MODEL_TO_MM
        unique_x = np.sort(np.unique(x_mm))
        unique_y = np.sort(np.unique(y_mm))
        nx = len(unique_x)
        ny = len(unique_y)
        dx = np.diff(unique_x).mean() if nx > 1 else 2.4
        dy = np.diff(unique_y).mean() if ny > 1 else 2.4

        grid = np.full((ny, nx), np.nan)
        x_index = {value: index for index, value in enumerate(unique_x)}
        y_index = {value: index for index, value in enumerate(unique_y)}
        for x_value, y_value, p_value in zip(x_mm, y_mm, porosity):
            x_round = min(unique_x, key=lambda value: abs(value - x_value))
            y_round = min(unique_y, key=lambda value: abs(value - y_value))
            grid[y_index[y_round], x_index[x_round]] = p_value

        x_edges = np.concatenate([unique_x - dx / 2, [unique_x[-1] + dx / 2]])
        y_edges = np.concatenate([unique_y - dy / 2, [unique_y[-1] + dy / 2]])

        fig, ax = plt.subplots(figsize=(5.5, 5.0))
        mesh = ax.pcolormesh(
            x_edges,
            y_edges,
            grid,
            cmap="YlOrRd",
            vmin=0.0,
            vmax=1.0,
            edgecolors="#cccccc",
            linewidths=0.3,
            shading="flat",
        )
        radius = dx / 2 * 0.9
        for x_value, y_value in zip(x_mm, y_mm):
            ax.add_patch(Circle((x_value, y_value), radius, fill=False, edgecolor="#555555", linewidth=0.25, alpha=0.4))
        ax.set_xlim(x_edges[0] - 0.5, x_edges[-1] + 0.5)
        ax.set_ylim(y_edges[0] - 0.5, y_edges[-1] + 0.5)
        ax.set_aspect("equal")
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        cbar = fig.colorbar(mesh, ax=ax, fraction=0.046, pad=0.03)
        cbar.set_label("Porosity", fontsize=8)
        cbar.ax.tick_params(labelsize=7)
        fig.tight_layout()
        fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
        fig.savefig(out_path.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
        plt.close(fig)


def plot_ball_field(x: np.ndarray, y: np.ndarray, dx: np.ndarray, dy: np.ndarray, radius: np.ndarray, out_path: Path) -> None:
    with mpl.rc_context(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 9,
            "axes.linewidth": 0.8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    ):
        disp_um = np.sqrt(dx ** 2 + dy ** 2) * MODEL_TO_MM * 1e3
        x_mm = x * MODEL_TO_MM
        y_mm = y * MODEL_TO_MM
        radius_mm = radius * MODEL_TO_MM
        patches = [Circle((x_value, y_value), r_value) for x_value, y_value, r_value in zip(x_mm, y_mm, radius_mm)]
        collection = PatchCollection(
            patches,
            array=disp_um,
            cmap="RdYlBu_r",
            norm=Normalize(vmin=0, vmax=np.ceil(disp_um.max()) if disp_um.size else 1.0),
            edgecolors="face",
            linewidths=0.1,
        )
        fig, ax = plt.subplots(figsize=(5.5, 5.0))
        ax.add_collection(collection)
        ax.set_xlim(x_mm.min() - 0.5, x_mm.max() + 0.5)
        ax.set_ylim(y_mm.min() - 0.5, y_mm.max() + 0.5)
        ax.set_aspect("equal")
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        cbar = fig.colorbar(collection, ax=ax, fraction=0.046, pad=0.03)
        cbar.set_label("Displacement magnitude (um)", fontsize=8)
        cbar.ax.tick_params(labelsize=7)
        fig.tight_layout()
        fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
        fig.savefig(out_path.with_suffix(".svg"), bbox_inches="tight", facecolor="white")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot peak stress, porosity, and ball fields for one case.")
    parser.add_argument("case", help="Case name, for example Intact or b60_d20")
    args = parser.parse_args()

    case_path = case_dir(args.case)
    stress_rows = filter_numeric_rows(read_csv_dict(case_path / "plotdata_stress_peak.csv"), ("x", "y", "syy"))
    porosity_rows = filter_numeric_rows(read_csv_dict(case_path / "plotdata_porosity_peak.csv"), ("x", "y", "porosity"))
    ball_rows = filter_numeric_rows(read_csv_dict(case_path / "plotdata_ball_fields_peak.csv"), ("x", "y", "disp_x", "disp_y", "radius"))

    plot_scalar_field(
        to_float_array(stress_rows, "x"),
        to_float_array(stress_rows, "y"),
        to_float_array(stress_rows, "syy"),
        case_path / "peak_stress_field.png",
        "syy",
        "RdBu_r",
    )
    plot_porosity_field(
        to_float_array(porosity_rows, "x"),
        to_float_array(porosity_rows, "y"),
        to_float_array(porosity_rows, "porosity"),
        case_path / "peak_porosity_field.png",
    )
    plot_ball_field(
        to_float_array(ball_rows, "x"),
        to_float_array(ball_rows, "y"),
        to_float_array(ball_rows, "disp_x"),
        to_float_array(ball_rows, "disp_y"),
        to_float_array(ball_rows, "radius"),
        case_path / "peak_ball_field.png",
    )


if __name__ == "__main__":
    main()
