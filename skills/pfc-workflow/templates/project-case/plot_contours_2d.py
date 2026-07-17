"""Generate rose diagram and contour plots from PFC 5plot.dat exported CSVs.

Compatible with PFC 6.0 FISH API.

Usage - from cases_2d directory:
    python plot_contours_2d.py Intact final
    python plot_contours_2d.py Intact peak
    python plot_contours_2d.py Intact all
    python plot_contours_2d.py all final

Generated plots (per stage):
    - plot_rose_diagram.png         : fracture orientation rose diagram
    - plot_displacement_{stage}.png : displacement contours (X / Y / magnitude)
    - plot_velocity_{stage}.png     : velocity contours (X / Y / magnitude)
    - plot_stress_{stage}.png       : stress contours (measurement-based sigma_xx/yy/xy/von Mises)
    - plot_porosity_{stage}.png     : porosity & coordination number contours
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np
import pandas as pd
from matplotlib import rcParams
from matplotlib.ticker import FuncFormatter, ScalarFormatter
from scipy.interpolate import griddata

from config import MODEL_TO_MM, SPECIMEN_EXTENT_MODEL, specimen_extent_mm

try:
    import cupy as cp

    GPU_AVAILABLE = False
    if cp.cuda.runtime.getDeviceCount() > 0:
        try:
            _probe = cp.asarray([1.0], dtype=cp.float64)
            _probe = cp.sqrt(_probe)
            cp.asnumpy(_probe)
            GPU_AVAILABLE = True
        except Exception:
            GPU_AVAILABLE = False
except Exception:
    cp = None
    GPU_AVAILABLE = False

rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 7,
    'svg.fonttype': 'none',
    'pdf.fonttype': 42,
    'axes.linewidth': 0.4,
    'axes.spines.right': False,
    'axes.spines.top': False,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.width': 0.35,
    'ytick.major.width': 0.35,
    'xtick.major.size': 2,
    'ytick.major.size': 2,
    'legend.frameon': False,
})

CASES_DIR = Path(__file__).resolve().parent
SPECIMEN_EXTENT = SPECIMEN_EXTENT_MODEL
SPECIMEN_EXTENT_MM = specimen_extent_mm()
GRID_RESOLUTION = 200
PLOT_DPI = 300
COLORMAP = 'viridis'
COLORMAP_STRESS = 'RdBu_r'

STAGE_LABELS = {
    'peak': 'Peak',
    'final': 'Post-peak',
}


def _fmt_mpa(x, _pos=None):
    return f'{x / 1e6:.1f}'


def _fmt_mm(x, _pos=None):
    return f'{x:.1f}'


def _fmt_um(x, _pos=None):
    return f'{x * 1e6:.1f}'


def _fmt_percent(x, _pos=None):
    return f'{x * 100:.0f}'


def _fmt_vel(x, _pos=None):
    return f'{x:.4f}'


def existing_case_names() -> list[str]:
    names = []
    for path in CASES_DIR.iterdir():
        if not path.is_dir():
            continue
        if (path / '3load.dat').exists():
            names.append(path.name)
    return sorted(names)


def case_sort_key(name: str) -> tuple[int, int, int]:
    if name == 'Intact':
        return (0, -1, -1)
    if name.startswith('b') and '_d' in name:
        beta_text, d_text = name[1:].split('_d', maxsplit=1)
        if beta_text.isdigit() and d_text.isdigit():
            return (1, int(beta_text), int(d_text))
    return (2, 999, 999)


def case_title(case_name: str) -> str:
    if case_name == 'Intact':
        return 'Intact 2D'
    parts = case_name.replace('b', '').split('_d')
    if len(parts) == 2:
        return f'2D  β={parts[0]}°  d={parts[1]} mm'
    return case_name


def load_fracture_orientations(case_dir: Path) -> pd.DataFrame | None:
    path = case_dir / 'plotdata_fracture_orientations.csv'
    if not path.exists():
        return None
    df = pd.read_csv(path)
    df['angle_deg'] = pd.to_numeric(df['angle_deg'], errors='coerce')
    df = df.dropna(subset=['angle_deg'])
    return df if not df.empty else None


def load_ball_fields(case_dir: Path, stage: str) -> pd.DataFrame | None:
    suffix = '_peak' if stage == 'peak' else ''
    path = case_dir / f'plotdata_ball_fields{suffix}.csv'
    if not path.exists():
        return None
    df = pd.read_csv(path)
    for col in ['x', 'y', 'disp_x', 'disp_y', 'vel_x', 'vel_y', 'radius']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df.dropna(subset=['x', 'y']) if not df.empty else None


def load_measure_data(case_dir: Path, prefix: str, stage: str) -> pd.DataFrame | None:
    """Load measurement data: prefix = 'porosity' or 'stress'."""
    suffix = '_peak' if stage == 'peak' else ''
    path = case_dir / f'plotdata_{prefix}{suffix}.csv'
    if not path.exists():
        return None
    df = pd.read_csv(path)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=['x', 'y'])
    return df if not df.empty else None


def to_device_array(values) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if GPU_AVAILABLE:
        return cp.asarray(array)
    return array


def to_numpy_array(values) -> np.ndarray:
    if GPU_AVAILABLE and isinstance(values, cp.ndarray):
        return cp.asnumpy(values)
    return np.asarray(values, dtype=float)


def vector_magnitude(x, y) -> np.ndarray:
    xp = cp if GPU_AVAILABLE else np
    x_arr = to_device_array(x)
    y_arr = to_device_array(y)
    return to_numpy_array(xp.sqrt(x_arr ** 2 + y_arr ** 2))


def stress_von_mises(sxx, syy, sxy) -> np.ndarray:
    xp = cp if GPU_AVAILABLE else np
    sxx_arr = to_device_array(sxx)
    syy_arr = to_device_array(syy)
    sxy_arr = to_device_array(sxy)
    values = xp.sqrt(sxx_arr ** 2 + syy_arr ** 2 - sxx_arr * syy_arr + 3 * sxy_arr ** 2)
    return to_numpy_array(values)


def angle_histogram(angles_deg, bins_deg) -> np.ndarray:
    xp = cp if GPU_AVAILABLE else np
    angle_arr = to_device_array(angles_deg)
    bin_arr = to_device_array(np.deg2rad(bins_deg))
    counts, _ = xp.histogram(xp.deg2rad(angle_arr), bins=bin_arr)
    return to_numpy_array(counts)


def _tricontour_from_scatter(
    ax, x, y, values, levels=20, cmap=COLORMAP, label=None, fmt=None
):
    """Create filled contour from scattered points via triangulation."""
    t = tri.Triangulation(x, y)
    if np.any(t.triangles < 0):
        mask = tri.TriAnalyzer(t).get_flat_tri_mask(min_circle_ratio=0.01)
        t.set_mask(mask)
    cnt = ax.tricontourf(t, values, levels=levels, cmap=cmap, extend='both')
    ax.tricontour(t, values, levels=levels, colors='k', linewidths=0.15, alpha=0.4)
    cbar = plt.colorbar(cnt, ax=ax, shrink=0.85, pad=0.02)
    if fmt:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(fmt))
    if label:
        cbar.set_label(label, fontsize=10)
    return cnt


def _grid_contour(ax, x, y, values, levels=20, cmap=COLORMAP, label=None, fmt=None):
    """Create filled contour from gridded measurement data."""
    xi = np.linspace(SPECIMEN_EXTENT[0], SPECIMEN_EXTENT[1], GRID_RESOLUTION)
    yi = np.linspace(SPECIMEN_EXTENT[0], SPECIMEN_EXTENT[1], GRID_RESOLUTION)
    Xi, Yi = np.meshgrid(xi, yi)
    Zi = griddata((x, y), values, (Xi, Yi), method='cubic')
    Zi = np.ma.masked_invalid(Zi)
    cnt = ax.contourf(Xi, Yi, Zi, levels=levels, cmap=cmap, extend='both')
    ax.contour(Xi, Yi, Zi, levels=levels, colors='k', linewidths=0.15, alpha=0.4)
    cbar = plt.colorbar(cnt, ax=ax, shrink=0.85, pad=0.02)
    if fmt:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(fmt))
    if label:
        cbar.set_label(label, fontsize=10)
    return cnt


def _setup_contour_axes(ax, title, specimen_extent=SPECIMEN_EXTENT):
    ax.set_xlim(*specimen_extent)
    ax.set_ylim(*specimen_extent)
    ax.set_aspect('equal')
    ax.set_xlabel('x (mm)')
    ax.set_ylabel('y (mm)')
    ax.set_title(title)
    ax.xaxis.set_major_formatter(FuncFormatter(_fmt_mm))
    ax.yaxis.set_major_formatter(FuncFormatter(_fmt_mm))
    ax.spines['left'].set_linewidth(0.4)
    ax.spines['bottom'].set_linewidth(0.4)


def _style_cartesian_axes(ax, labelsize: float) -> None:
    ax.tick_params(labelsize=labelsize, width=0.35, length=2)
    ax.spines['left'].set_linewidth(0.4)
    ax.spines['bottom'].set_linewidth(0.4)


# ---- Rose Diagram (Nature-figure style) ----
def plot_rose_diagram(case_dir: Path, case_name: str, save: bool = True):
    df = load_fracture_orientations(case_dir)
    if df is None:
        print(f'  [skip] No fracture orientation data for {case_name}')
        return

    tensile = df[df['type'] == 'tension']
    shear = df[df['type'] == 'shear']
    N = len(df)
    bins_deg = np.linspace(0, 180, 19)
    bin_centers = (bins_deg[:-1] + bins_deg[1:]) / 2
    bin_width = bins_deg[1] - bins_deg[0]

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'},
                           figsize=(75 / 25.4, 75 / 25.4))  # 75×75 mm

    # Low-saturation Nature palette
    counts_all = angle_histogram(df['angle_deg'].to_numpy(dtype=float), bins_deg)
    ax.bar(np.deg2rad(bin_centers), counts_all, width=np.deg2rad(bin_width),
           color='#6baed6', edgecolor='#2171b5', linewidth=0.4, alpha=0.85,
           label=f'All ({N})')
    if not tensile.empty:
        counts_t = angle_histogram(tensile['angle_deg'].to_numpy(dtype=float), bins_deg)
        ax.bar(np.deg2rad(bin_centers), counts_t, width=np.deg2rad(bin_width),
               color='#fc9272', edgecolor='#cb181d', linewidth=0.3, alpha=0.7,
               label=f'Tension ({len(tensile)})')
    if not shear.empty:
        counts_s = angle_histogram(shear['angle_deg'].to_numpy(dtype=float), bins_deg)
        ax.bar(np.deg2rad(bin_centers), counts_s, width=np.deg2rad(bin_width),
               color='#a1d99b', edgecolor='#31a354', linewidth=0.3, alpha=0.7,
               label=f'Shear ({len(shear)})')

    ax.set_theta_zero_location('E')
    ax.set_theta_direction('counterclockwise')
    ax.set_thetagrids([0, 30, 60, 90, 120, 150],
                      labels=['0°', '30°', '60°', '90°', '120°', '150°'],
                      fontsize=6)
    ax.tick_params(axis='y', labelsize=5.5, pad=0)
    ax.grid(linewidth=0.4, alpha=0.5)
    ax.spines['polar'].set_linewidth(0.4)

    ax.set_title(f'{case_title(case_name)} — Fracture Rose Diagram',
                 pad=10, fontsize=8, fontweight='bold')
    ax.legend(loc='upper right', bbox_to_anchor=(1.32, 1.05),
              fontsize=5.5, handlelength=1.2, handletextpad=0.4,
              borderpad=0.3, labelspacing=0.3)
    fig.tight_layout()
    if save:
        stem = case_dir / 'plot_rose_diagram'
        fig.savefig(f'{stem}.png', dpi=600, bbox_inches='tight')
        fig.savefig(f'{stem}.svg', bbox_inches='tight')
        fig.savefig(f'{stem}.pdf', bbox_inches='tight')
        print(f'  saved: plot_rose_diagram (.png/.svg/.pdf)')
    plt.close(fig)


# ---- Displacement Contour (Nature-figure style) ----
def plot_displacement_contour(case_dir: Path, case_name: str, stage: str, save: bool = True):
    df = load_ball_fields(case_dir, stage)
    if df is None:
        print(f'  [skip] No ball field data for {case_name} ({stage})')
        return

    # Convert all to mm
    x_mm = df['x'].values * MODEL_TO_MM
    y_mm = df['y'].values * MODEL_TO_MM
    dx_mm = df['disp_x'].values * MODEL_TO_MM
    dy_mm = df['disp_y'].values * MODEL_TO_MM
    dmag_mm = vector_magnitude(df['disp_x'].to_numpy(dtype=float),
                               df['disp_y'].to_numpy(dtype=float)) * MODEL_TO_MM

    stage_label = STAGE_LABELS.get(stage, stage)
    title_base = f'{case_title(case_name)} — {stage_label}'
    extent_mm = SPECIMEN_EXTENT_MM

    # Determine scale factor: if max disp < 0.1 mm, show as ×10⁻³
    max_abs = max(np.abs(dx_mm).max(), np.abs(dy_mm).max(), dmag_mm.max())
    if max_abs < 0.1:
        scale = 1e3
        cbar_label = r'Displacement ($\times 10^{-3}$ mm)'
    else:
        scale = 1.0
        cbar_label = 'Displacement (mm)'

    fig, axes = plt.subplots(1, 3, figsize=(183 / 25.4, 55 / 25.4))  # 183×55 mm
    panel_labels = ['a', 'b', 'c']
    datasets = [dx_mm * scale, dy_mm * scale, dmag_mm * scale]
    subtitles = [r'$u_x$', r'$u_y$', r'$|\mathbf{u}|$']
    cmaps = ['RdBu_r', 'RdBu_r', 'plasma']

    for i, (ax, data, stitle, cm) in enumerate(zip(axes, datasets, subtitles, cmaps)):
        # Triangulation contour
        t = tri.Triangulation(x_mm, y_mm)
        cnt = ax.tricontourf(t, data, levels=20, cmap=cm, extend='both')
        ax.tricontour(t, data, levels=20, colors='k', linewidths=0.15, alpha=0.3)

        # Colorbar
        cbar = plt.colorbar(cnt, ax=ax, shrink=0.88, pad=0.03, aspect=20)
        cbar.ax.tick_params(labelsize=6, width=0.35, length=2)
        cbar.outline.set_linewidth(0.4)
        cbar.set_label(cbar_label, fontsize=6.5)

        # Axes setup
        ax.set_xlim(*extent_mm)
        ax.set_ylim(*extent_mm)
        ax.set_aspect('equal')
        ax.set_xlabel('x (mm)', fontsize=7)
        ax.set_ylabel('y (mm)', fontsize=7)
        _style_cartesian_axes(ax, 6)

        # Panel label (Nature bold letter)
        ax.text(-0.12, 1.05, panel_labels[i], transform=ax.transAxes,
                fontsize=8, fontweight='bold', va='bottom', ha='left')
        # Subtitle
        ax.set_title(stitle, fontsize=7, pad=4)

    fig.suptitle(f'{title_base} — Displacement Contours',
                 fontsize=8, fontweight='bold', y=1.02)
    fig.tight_layout(w_pad=1.8)
    if save:
        stem = case_dir / f'plot_displacement_{stage}'
        fig.savefig(f'{stem}.png', dpi=600, bbox_inches='tight')
        fig.savefig(f'{stem}.svg', bbox_inches='tight')
        fig.savefig(f'{stem}.pdf', bbox_inches='tight')
        print(f'  saved: plot_displacement_{stage} (.png/.svg/.pdf)')
    plt.close(fig)


# ---- Velocity Contour (Nature-figure style) ----
def plot_velocity_contour(case_dir: Path, case_name: str, stage: str, save: bool = True):
    df = load_ball_fields(case_dir, stage)
    if df is None:
        print(f'  [skip] No ball field data for {case_name} ({stage})')
        return

    df['vel_mag'] = vector_magnitude(df['vel_x'].to_numpy(dtype=float), df['vel_y'].to_numpy(dtype=float))

    max_vel = df['vel_mag'].max()
    if max_vel < 1e-12:
        print(f'  [skip] Velocity near-zero for {case_name} ({stage}), max={max_vel:.2e}')
        return

    # Convert to mm
    x_mm = df['x'].values * MODEL_TO_MM
    y_mm = df['y'].values * MODEL_TO_MM
    extent_mm = SPECIMEN_EXTENT_MM

    # Velocity follows the same length convention as the specimen: mm/s.
    vx = df['vel_x'].values * MODEL_TO_MM
    vy = df['vel_y'].values * MODEL_TO_MM
    vmag = df['vel_mag'].values * MODEL_TO_MM
    max_abs_vel = max(np.abs(vx).max(), np.abs(vy).max(), vmag.max())
    if max_abs_vel < 1.0:
        vel_scale = 1e3
        cbar_unit = 'um/s'
    else:
        vel_scale = 1.0
        cbar_unit = 'mm/s'

    stage_label = STAGE_LABELS.get(stage, stage)
    title_base = f'{case_title(case_name)} — {stage_label}'

    fig, axes = plt.subplots(1, 3, figsize=(183 / 25.4, 55 / 25.4))  # 183×55 mm
    panel_labels = ['a', 'b', 'c']
    datasets = [vx * vel_scale, vy * vel_scale, vmag * vel_scale]
    subtitles = [r'$v_x$', r'$v_y$', r'$|\mathbf{v}|$']
    cmaps = ['RdBu_r', 'RdBu_r', 'plasma']

    for i, (ax, data, stitle, cm) in enumerate(zip(axes, datasets, subtitles, cmaps)):
        t = tri.Triangulation(x_mm, y_mm)
        cnt = ax.tricontourf(t, data, levels=20, cmap=cm, extend='both')
        ax.tricontour(t, data, levels=20, colors='k', linewidths=0.15, alpha=0.3)

        cbar = plt.colorbar(cnt, ax=ax, shrink=0.88, pad=0.03, aspect=20)
        cbar.ax.tick_params(labelsize=6, width=0.35, length=2)
        cbar.outline.set_linewidth(0.4)
        cbar.set_label(f'Velocity ({cbar_unit})', fontsize=6.5)

        ax.set_xlim(*extent_mm)
        ax.set_ylim(*extent_mm)
        ax.set_aspect('equal')
        ax.set_xlabel('x (mm)', fontsize=7)
        ax.set_ylabel('y (mm)', fontsize=7)
        _style_cartesian_axes(ax, 6)

        ax.text(-0.12, 1.05, panel_labels[i], transform=ax.transAxes,
                fontsize=8, fontweight='bold', va='bottom', ha='left')
        ax.set_title(stitle, fontsize=7, pad=4)

    fig.suptitle(f'{title_base} — Velocity Contours',
                 fontsize=8, fontweight='bold', y=1.02)
    fig.tight_layout(w_pad=1.8)
    if save:
        stem = case_dir / f'plot_velocity_{stage}'
        fig.savefig(f'{stem}.png', dpi=600, bbox_inches='tight')
        fig.savefig(f'{stem}.svg', bbox_inches='tight')
        fig.savefig(f'{stem}.pdf', bbox_inches='tight')
        print(f'  saved: plot_velocity_{stage} (.png/.svg/.pdf)')
    plt.close(fig)


# ---- Stress Contour (Nature-figure style) ----
def plot_stress_contour(case_dir: Path, case_name: str, stage: str, save: bool = True):
    df = load_measure_data(case_dir, 'stress', stage)
    if df is None:
        print(f'  [skip] No measure stress data for {case_name} ({stage})')
        return

    df['von_mises'] = stress_von_mises(
        df['sxx'].to_numpy(dtype=float),
        df['syy'].to_numpy(dtype=float),
        df['sxy'].to_numpy(dtype=float),
    )

    # Convert to mm
    x_mm = df['x'].values * MODEL_TO_MM
    y_mm = df['y'].values * MODEL_TO_MM
    extent_mm = SPECIMEN_EXTENT_MM

    # Determine stress unit: if max |stress| < 1e4 Pa → show kPa; else MPa
    all_stress = np.concatenate([df['sxx'].values, df['syy'].values,
                                 df['sxy'].values, df['von_mises'].values])
    max_abs_stress = np.nanmax(np.abs(all_stress))
    if max_abs_stress < 1e4:  # < 10 kPa
        stress_scale = 1e-3
        cbar_unit = 'kPa'
    else:
        stress_scale = 1e-6
        cbar_unit = 'MPa'

    stage_label = STAGE_LABELS.get(stage, stage)
    title_base = f'{case_title(case_name)} — {stage_label}'

    fig, axes = plt.subplots(2, 2, figsize=(130 / 25.4, 110 / 25.4))  # 130×110 mm
    axes_flat = axes.flatten()
    panel_labels = ['a', 'b', 'c', 'd']
    cols = ['sxx', 'syy', 'sxy', 'von_mises']
    subtitles = [r'$\sigma_{xx}$', r'$\sigma_{yy}$', r'$\sigma_{xy}$',
                 r'$\sigma_\mathrm{vM}$']
    cmaps_stress = ['RdBu_r', 'RdBu_r', 'RdBu_r', 'plasma']

    xi = np.linspace(extent_mm[0], extent_mm[1], GRID_RESOLUTION)
    yi = np.linspace(extent_mm[0], extent_mm[1], GRID_RESOLUTION)
    Xi, Yi = np.meshgrid(xi, yi)

    for i, (ax, col, stitle, cm) in enumerate(
        zip(axes_flat, cols, subtitles, cmaps_stress)
    ):
        data_scaled = df[col].values * stress_scale
        Zi = griddata((x_mm, y_mm), data_scaled, (Xi, Yi), method='cubic')
        Zi = np.ma.masked_invalid(Zi)
        cnt = ax.contourf(Xi, Yi, Zi, levels=20, cmap=cm, extend='both')
        ax.contour(Xi, Yi, Zi, levels=20, colors='k', linewidths=0.15, alpha=0.3)

        cbar = plt.colorbar(cnt, ax=ax, shrink=0.88, pad=0.03, aspect=20)
        cbar.ax.tick_params(labelsize=5.5, width=0.35, length=2)
        cbar.outline.set_linewidth(0.4)
        cbar.set_label(f'Stress ({cbar_unit})', fontsize=6)

        ax.set_xlim(*extent_mm)
        ax.set_ylim(*extent_mm)
        ax.set_aspect('equal')
        ax.set_xlabel('x (mm)', fontsize=6.5)
        ax.set_ylabel('y (mm)', fontsize=6.5)
        _style_cartesian_axes(ax, 5.5)

        ax.text(-0.14, 1.08, panel_labels[i], transform=ax.transAxes,
                fontsize=8, fontweight='bold', va='bottom', ha='left')
        ax.set_title(stitle, fontsize=7, pad=4)

    fig.suptitle(f'{title_base} — Stress Contours',
                 fontsize=8, fontweight='bold', y=1.01)
    fig.tight_layout(w_pad=1.5, h_pad=2.0)
    if save:
        stem = case_dir / f'plot_stress_{stage}'
        fig.savefig(f'{stem}.png', dpi=600, bbox_inches='tight')
        fig.savefig(f'{stem}.svg', bbox_inches='tight')
        fig.savefig(f'{stem}.pdf', bbox_inches='tight')
        print(f'  saved: plot_stress_{stage} (.png/.svg/.pdf)')
    plt.close(fig)


# ---- Porosity Contour (Nature-figure style) ----
def plot_porosity_contour(case_dir: Path, case_name: str, stage: str, save: bool = True):
    df = load_measure_data(case_dir, 'porosity', stage)
    if df is None:
        print(f'  [skip] No measure porosity data for {case_name} ({stage})')
        return

    # Convert to mm
    x_mm = df['x'].values * MODEL_TO_MM
    y_mm = df['y'].values * MODEL_TO_MM
    porosity_pct = df['porosity'].values * 100.0  # fraction → %
    coord_num = df['coord_num'].values
    extent_mm = SPECIMEN_EXTENT_MM

    stage_label = STAGE_LABELS.get(stage, stage)
    title_base = f'{case_title(case_name)} — {stage_label}'

    fig, axes = plt.subplots(1, 2, figsize=(130 / 25.4, 55 / 25.4))  # 130×55 mm
    panel_labels = ['a', 'b']
    datasets = [porosity_pct, coord_num]
    subtitles = ['Porosity', 'Coordination number']
    cbar_labels = ['Porosity (%)', 'Coordination number']
    cmaps = ['cividis_r', 'viridis']

    xi = np.linspace(extent_mm[0], extent_mm[1], GRID_RESOLUTION)
    yi = np.linspace(extent_mm[0], extent_mm[1], GRID_RESOLUTION)
    Xi, Yi = np.meshgrid(xi, yi)

    for i, (ax, data, stitle, clab, cm) in enumerate(
        zip(axes, datasets, subtitles, cbar_labels, cmaps)
    ):
        Zi = griddata((x_mm, y_mm), data, (Xi, Yi), method='cubic')
        Zi = np.ma.masked_invalid(Zi)
        cnt = ax.contourf(Xi, Yi, Zi, levels=20, cmap=cm, extend='both')
        ax.contour(Xi, Yi, Zi, levels=20, colors='k', linewidths=0.15, alpha=0.3)

        cbar = plt.colorbar(cnt, ax=ax, shrink=0.88, pad=0.03, aspect=20)
        cbar.ax.tick_params(labelsize=6, width=0.35, length=2)
        cbar.outline.set_linewidth(0.4)
        cbar.set_label(clab, fontsize=6.5)

        ax.set_xlim(*extent_mm)
        ax.set_ylim(*extent_mm)
        ax.set_aspect('equal')
        ax.set_xlabel('x (mm)', fontsize=7)
        ax.set_ylabel('y (mm)', fontsize=7)
        _style_cartesian_axes(ax, 6)

        ax.text(-0.14, 1.05, panel_labels[i], transform=ax.transAxes,
                fontsize=8, fontweight='bold', va='bottom', ha='left')
        ax.set_title(stitle, fontsize=7, pad=4)

    fig.suptitle(f'{title_base} — Porosity & Coordination',
                 fontsize=8, fontweight='bold', y=1.02)
    fig.tight_layout(w_pad=2.0)
    if save:
        stem = case_dir / f'plot_porosity_{stage}'
        fig.savefig(f'{stem}.png', dpi=600, bbox_inches='tight')
        fig.savefig(f'{stem}.svg', bbox_inches='tight')
        fig.savefig(f'{stem}.pdf', bbox_inches='tight')
        print(f'  saved: plot_porosity_{stage} (.png/.svg/.pdf)')
    plt.close(fig)


# ---- All plots for one case + stage ----
def plot_case_contours(case_name: str, stage: str, save: bool = True):
    case_dir = CASES_DIR / case_name
    if not case_dir.is_dir():
        print(f'Case directory not found: {case_dir}')
        return

    print(f'\n=== {case_title(case_name)} [{stage}] ===')

    plot_rose_diagram(case_dir, case_name, save=save)
    plot_displacement_contour(case_dir, case_name, stage, save=save)
    plot_velocity_contour(case_dir, case_name, stage, save=save)
    plot_stress_contour(case_dir, case_name, stage, save=save)
    plot_porosity_contour(case_dir, case_name, stage, save=save)


# ---- Main CLI ----
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate PFC contour and rose-diagram plots from 5plot.dat exports.'
    )
    parser.add_argument(
        'target',
        help='Case name (Intact, b0_d14, ...) or "all" for every case',
    )
    parser.add_argument(
        'stage',
        nargs='?',
        default='all',
        choices=['final', 'peak', 'all'],
        help='Simulation stage: peak, final, or all (default: all)',
    )
    args = parser.parse_args()

    if args.target.lower() == 'all':
        cases = existing_case_names()
    else:
        cases = [args.target]

    for case in sorted(cases, key=case_sort_key):
        if args.stage == 'all':
            for s in ['peak', 'final']:
                plot_case_contours(case, s)
        else:
            plot_case_contours(case, args.stage)

    print('\nDone.')
