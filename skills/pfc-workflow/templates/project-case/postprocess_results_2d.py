import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import rcParams

from config import case_dir, case_sort_key, case_title, existing_case_names, map_case_to_experiment_file

rcParams['font.family'] = 'Times New Roman'
rcParams['font.size'] = 12
rcParams['axes.linewidth'] = 1.1
rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'

CASES_DIR = Path(__file__).resolve().parent
PREPEAK_RATIO = 0.92
PEAK_FRACTION = 0.60
ELASTIC_LOWER_RATIO = 0.10
ELASTIC_UPPER_RATIO = 0.40
ELASTIC_FALLBACK_LOWER_RATIO = 0.05
ELASTIC_FALLBACK_UPPER_RATIO = 0.50
MIN_ELASTIC_POINTS = 5


def normalize_case_name(case_name: str) -> str:
    return case_name.strip()


def find_experimental_file(case_name: str) -> Path | None:
    path = map_case_to_experiment_file(case_name)
    if path.exists() and not path.name.startswith('~$'):
        return path
    return None


def find_simulation_file(case_path: Path) -> Path | None:
    preferred = [
        case_path / 'stress_strain.csv',
        case_path / 'stress_strain.his',
        case_path / 'stress_strain.dat',
    ]
    for path in preferred:
        if path.exists():
            return path
    for pattern in ('*.csv', '*.his', '*.dat'):
        matches = sorted(case_path.glob(pattern))
        if matches:
            return matches[0]
    return None


def read_experimental_curve(case_name: str) -> pd.DataFrame | None:
    xlsx_path = find_experimental_file(case_name)
    if xlsx_path is None:
        return None
    df = pd.read_excel(xlsx_path)
    columns = {str(col).strip().lower(): col for col in df.columns}
    strain_col = columns.get('strain')
    stress_col = columns.get('stress')
    if strain_col is None or stress_col is None:
        return None
    out = pd.DataFrame({
        'strain': pd.to_numeric(df[strain_col], errors='coerce'),
        'stress_mpa': pd.to_numeric(df[stress_col], errors='coerce'),
        'crack_num': np.nan,
    }).dropna(subset=['strain', 'stress_mpa'])
    out = out[out['strain'] >= 0].reset_index(drop=True)
    return out if not out.empty else None


def read_simulation_raw_table(csv_path: Path) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(csv_path)
        if not df.empty and df.shape[1] >= 2:
            return df
    except Exception:
        pass

    try:
        df = pd.read_csv(csv_path, sep=r'[\s,]+', engine='python', header=None, comment=';')
    except Exception:
        return None

    if df.empty or df.shape[1] < 2:
        return None
    return df


def read_simulation_curve(case_path: Path) -> pd.DataFrame | None:
    csv_path = find_simulation_file(case_path)
    if csv_path is None:
        return None
    df = read_simulation_raw_table(csv_path)
    if df is None or df.empty or df.shape[1] < 2:
        return None

    if all(isinstance(col, int) for col in df.columns):
        columns = ['strain', 'stress_raw']
        if df.shape[1] >= 3:
            columns.append('crack_num')
        df = df.iloc[:, :len(columns)].copy()
        df.columns = columns

    lower_columns = {str(col).strip().lower(): col for col in df.columns}
    strain_col = lower_columns.get('strain', df.columns[0])
    stress_col = lower_columns.get('stress_mpa') or lower_columns.get('stress_pa') or lower_columns.get('stress') or df.columns[1]
    crack_col = lower_columns.get('crack_num')
    if crack_col is None and df.shape[1] >= 3:
        crack_col = df.columns[2]

    out = pd.DataFrame({
        'strain': pd.to_numeric(df[strain_col], errors='coerce'),
        'stress_raw': pd.to_numeric(df[stress_col], errors='coerce'),
        'crack_num': pd.to_numeric(df[crack_col], errors='coerce') if crack_col is not None else np.nan,
    }).dropna(subset=['strain', 'stress_raw']).reset_index(drop=True)
    if out.empty:
        return None

    stress_max = out['stress_raw'].abs().max()
    if lower_columns.get('stress_mpa') is not None:
        out['stress_mpa'] = out['stress_raw'].abs()
    else:
        out['stress_mpa'] = out['stress_raw'].abs() / 1e6 if stress_max > 1000 else out['stress_raw'].abs()
    out['strain'] = out['strain'].abs()
    return out[['strain', 'stress_mpa', 'crack_num']]


def prepare_curve_for_display(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or df.empty:
        return df

    out = df.copy().reset_index(drop=True)
    peak_idx = int(out['stress_mpa'].idxmax())
    peak_stress = float(out.loc[peak_idx, 'stress_mpa'])
    peak_strain = float(out.loc[peak_idx, 'strain'])
    strain0 = max(0.0, float(out.loc[0, 'strain']))
    stress0 = max(0.0, float(out.loc[0, 'stress_mpa']))

    if strain0 > 0 and peak_strain > strain0:
        strain_values = np.clip(out['strain'].to_numpy(dtype=float) - strain0, 0.0, None)
        strain_scale = peak_strain / max(peak_strain - strain0, 1.0e-12)
        out['strain'] = strain_values * strain_scale

    if stress0 > 0 and peak_stress > stress0:
        stress_values = np.clip(out['stress_mpa'].to_numpy(dtype=float) - stress0, 0.0, None)
        stress_scale = peak_stress / max(peak_stress - stress0, 1.0e-12)
        out['stress_mpa'] = stress_values * stress_scale

    early_limit = peak_stress * 0.12
    early_mask = out['stress_mpa'].to_numpy(dtype=float) <= early_limit
    if np.any(early_mask):
        early_end = int(np.argmax(~early_mask)) if np.any(~early_mask) else len(out)
        if early_end <= 1:
            early_end = min(len(out), 12)
        early_end = max(2, early_end)
        anchor = float(out.loc[early_end - 1, 'stress_mpa'])
        out.loc[:early_end - 1, 'stress_mpa'] = np.linspace(0.0, anchor, early_end)

    origin = pd.DataFrame([{
        'strain': 0.0,
        'stress_mpa': 0.0,
        'crack_num': float(out.loc[0, 'crack_num']) if 'crack_num' in out.columns and pd.notna(out.loc[0, 'crack_num']) else np.nan,
    }])
    out = pd.concat([origin, out], ignore_index=True)
    out = out.sort_values('strain').drop_duplicates(subset=['strain'], keep='first').reset_index(drop=True)
    return out


def fit_line(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    if x.size < 2 or y.size < 2 or np.allclose(x, x[0]):
        return np.nan, np.nan, np.nan
    slope, intercept = np.polyfit(x, y, 1)
    y_hat = slope * x + intercept
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = np.nan if ss_tot <= 0 else 1.0 - ss_res / ss_tot
    return float(slope), float(intercept), float(r2)


def select_elastic_window(
    df: pd.DataFrame,
    lower_ratio: float = ELASTIC_LOWER_RATIO,
    upper_ratio: float = ELASTIC_UPPER_RATIO,
    min_points: int = MIN_ELASTIC_POINTS,
) -> pd.DataFrame:
    if df.empty:
        return df.iloc[0:0].copy()

    peak_idx = int(df['stress_mpa'].idxmax())
    ascending = df.iloc[:peak_idx + 1].copy()
    ascending = ascending[(ascending['strain'] > 0) & (ascending['stress_mpa'] > 0)].reset_index(drop=True)
    if ascending.empty:
        return ascending

    peak_stress = float(ascending['stress_mpa'].max())
    window = ascending[
        (ascending['stress_mpa'] >= peak_stress * lower_ratio)
        & (ascending['stress_mpa'] <= peak_stress * upper_ratio)
    ].copy()

    if len(window) < min_points:
        window = ascending[
            (ascending['stress_mpa'] >= peak_stress * ELASTIC_FALLBACK_LOWER_RATIO)
            & (ascending['stress_mpa'] <= peak_stress * ELASTIC_FALLBACK_UPPER_RATIO)
        ].copy()

    if len(window) < min_points and len(ascending) >= 3:
        start = max(1, math.floor(len(ascending) * 0.08))
        end = max(start + 3, math.ceil(len(ascending) * 0.45))
        window = ascending.iloc[start:end].copy()

    return window.reset_index(drop=True)


def calculate_elastic_modulus_metrics(df: pd.DataFrame | None) -> dict:
    empty = {
        'elastic_lower_ratio': ELASTIC_LOWER_RATIO,
        'elastic_upper_ratio': ELASTIC_UPPER_RATIO,
        'elastic_window_start_strain': np.nan,
        'elastic_window_end_strain': np.nan,
        'elastic_window_start_stress_mpa': np.nan,
        'elastic_window_end_stress_mpa': np.nan,
        'elastic_window_point_count': 0,
        'secant_modulus_mpa': np.nan,
        'tangent_modulus_mpa': np.nan,
        'regression_modulus_mpa': np.nan,
        'regression_intercept_mpa': np.nan,
        'regression_r2': np.nan,
    }
    if df is None or df.empty:
        return empty

    window = select_elastic_window(df)
    if len(window) < 2:
        return empty

    x = window['strain'].to_numpy(dtype=float)
    y = window['stress_mpa'].to_numpy(dtype=float)
    dx = float(x[-1] - x[0])
    secant_modulus = np.nan if abs(dx) <= 0 else float((y[-1] - y[0]) / dx)

    local_radius = max(1, min(2, len(window) // 4))
    center = len(window) // 2
    local_start = max(0, center - local_radius)
    local_end = min(len(window), center + local_radius + 1)
    tangent_x = x[local_start:local_end]
    tangent_y = y[local_start:local_end]
    tangent_modulus, _, _ = fit_line(tangent_x, tangent_y)
    regression_modulus, regression_intercept, regression_r2 = fit_line(x, y)

    return {
        'elastic_lower_ratio': ELASTIC_LOWER_RATIO,
        'elastic_upper_ratio': ELASTIC_UPPER_RATIO,
        'elastic_window_start_strain': float(x[0]),
        'elastic_window_end_strain': float(x[-1]),
        'elastic_window_start_stress_mpa': float(y[0]),
        'elastic_window_end_stress_mpa': float(y[-1]),
        'elastic_window_point_count': int(len(window)),
        'secant_modulus_mpa': secant_modulus,
        'tangent_modulus_mpa': tangent_modulus,
        'regression_modulus_mpa': regression_modulus,
        'regression_intercept_mpa': regression_intercept,
        'regression_r2': regression_r2,
    }


def identify_stage_points(df: pd.DataFrame, prepeak_ratio: float = PREPEAK_RATIO, peak_fraction: float = PEAK_FRACTION) -> dict:
    if df.empty:
        return {}

    peak_idx = int(df['stress_mpa'].idxmax())
    peak_stress = float(df.loc[peak_idx, 'stress_mpa'])
    peak_strain = float(df.loc[peak_idx, 'strain'])

    ascending = df.iloc[:peak_idx + 1]
    prepeak_target = peak_stress * prepeak_ratio
    prepeak_idx = int((ascending['stress_mpa'] - prepeak_target).abs().idxmin())
    prepeak_stress = float(df.loc[prepeak_idx, 'stress_mpa'])
    prepeak_strain = float(df.loc[prepeak_idx, 'strain'])

    tail_n = min(len(df), max(10, math.ceil(len(df) * 0.05)))
    post_peak_start = min(peak_idx + 1, len(df) - 1)
    tail_start = max(post_peak_start, len(df) - tail_n)
    residual_window = df.iloc[tail_start:].copy()
    if residual_window.empty:
        residual_window = df.iloc[max(0, len(df) - tail_n):].copy()
    residual = float(residual_window['stress_mpa'].mean())
    residual_idx = int((residual_window['stress_mpa'] - residual).abs().idxmin())
    residual_strain = float(df.loc[residual_idx, 'strain'])

    threshold_stress = peak_stress * peak_fraction
    post_peak = df.iloc[peak_idx:].copy()
    below_threshold = post_peak[post_peak['stress_mpa'] <= threshold_stress]
    threshold_strain = float(below_threshold.iloc[0]['strain']) if not below_threshold.empty else np.nan

    crack_series = pd.to_numeric(df.get('crack_num'), errors='coerce') if 'crack_num' in df.columns else pd.Series(dtype=float)
    peak_crack_num = float(crack_series.loc[peak_idx]) if not crack_series.empty and pd.notna(crack_series.loc[peak_idx]) else np.nan
    final_crack_num = float(crack_series.iloc[-1]) if not crack_series.empty and pd.notna(crack_series.iloc[-1]) else np.nan
    max_crack_num = float(crack_series.max()) if not crack_series.empty and crack_series.notna().any() else np.nan

    return {
        'prepeak_ratio': prepeak_ratio,
        'prepeak_target_stress_mpa': prepeak_target,
        'prepeak_stress_mpa': prepeak_stress,
        'prepeak_strain': prepeak_strain,
        'peak_stress_mpa': peak_stress,
        'peak_strain': peak_strain,
        'peak_fraction': peak_fraction,
        'peak_fraction_stress_mpa': threshold_stress,
        'peak_fraction_strain': threshold_strain,
        'residual_stress_mpa': residual,
        'residual_strain': residual_strain,
        'residual_ratio': residual / peak_stress if peak_stress else np.nan,
        'peak_crack_num': peak_crack_num,
        'final_crack_num': final_crack_num,
        'max_crack_num': max_crack_num,
        'point_count': int(len(df)),
    }


def summarize_curve(df: pd.DataFrame | None, label: str) -> dict | None:
    if df is None or df.empty:
        return None
    return {
        'source': label,
        **identify_stage_points(df),
        **calculate_elastic_modulus_metrics(df),
    }


def plot_case(case_name: str, save: bool = True) -> pd.DataFrame:
    case_name = normalize_case_name(case_name)
    case_path = case_dir(case_name)
    exp_df = read_experimental_curve(case_name)
    sim_df = read_simulation_curve(case_path)
    if exp_df is None and sim_df is None:
        raise FileNotFoundError(f'No experimental or simulation curve found for {case_name}')

    exp_metrics = summarize_curve(exp_df, 'experimental') if exp_df is not None else None
    sim_metrics = summarize_curve(sim_df, 'simulation') if sim_df is not None else None
    sim_plot_df = prepare_curve_for_display(sim_df)

    fig, ax = plt.subplots(figsize=(8, 6))
    crack_ax = None
    rows = []

    if exp_df is not None:
        ax.plot(exp_df['strain'], exp_df['stress_mpa'], color='#f39c12', linewidth=2.0, linestyle='--', label='Experimental')
        rows.append({'case': case_name, **exp_metrics})
    if sim_plot_df is not None:
        ax.plot(sim_plot_df['strain'], sim_plot_df['stress_mpa'], color='#1f77b4', linewidth=2.2, label='Simulation')
        rows.append({'case': case_name, **sim_metrics})
        if sim_plot_df['crack_num'].notna().any():
            crack_ax = ax.twinx()
            crack_ax.plot(sim_plot_df['strain'], sim_plot_df['crack_num'], color='#c0392b', linewidth=1.4, alpha=0.8, label='Crack Number')
            crack_ax.set_ylabel('Crack Number')
            crack_ax.tick_params(direction='in')

    ax.set_xlabel('Axial Strain')
    ax.set_ylabel('Axial Stress (MPa)')
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_title(case_title(case_name))

    handles, labels = ax.get_legend_handles_labels()
    if crack_ax is not None:
        crack_handles, crack_labels = crack_ax.get_legend_handles_labels()
        handles += crack_handles
        labels += crack_labels
    if handles:
        ax.legend(handles, labels, loc='best')

    plt.tight_layout()
    if save:
        fig.savefig(case_path / 'curve_compare_2d.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

    result = pd.DataFrame(rows)
    if save:
        result.to_excel(case_path / 'curve_metrics_2d.xlsx', index=False)
    return result


def plot_all(save: bool = True) -> pd.DataFrame:
    records = []
    for case_name in existing_case_names():
        try:
            case_result = plot_case(case_name, save=save)
            if not case_result.empty:
                records.append(case_result)
        except FileNotFoundError:
            continue

    if not records:
        raise FileNotFoundError('No usable 2D curves found for postprocessing.')

    summary = pd.concat(records, ignore_index=True)
    if save:
        summary.to_excel(CASES_DIR / 'curve_metrics_summary_2d.xlsx', index=False)

    sim_summary = summary[summary['source'] == 'simulation'].copy()
    if not sim_summary.empty:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        ordered = sim_summary.sort_values('case', key=lambda s: s.map(case_sort_key))
        axes[0].bar(ordered['case'], ordered['peak_stress_mpa'], color='#1f77b4')
        axes[0].set_title('2D Simulation Peak Axial Stress')
        axes[0].tick_params(axis='x', rotation=60)
        axes[0].set_ylabel('MPa')

        axes[1].bar(ordered['case'], ordered['final_crack_num'], color='#c0392b')
        axes[1].set_title('2D Final Crack Number')
        axes[1].tick_params(axis='x', rotation=60)
        axes[1].set_ylabel('Count')

        plt.tight_layout()
        if save:
            fig.savefig(CASES_DIR / 'summary_2d.png', dpi=300, bbox_inches='tight')
        plt.close(fig)

    exp_summary = summary[summary['source'] == 'experimental'].copy()
    paired = exp_summary.merge(sim_summary, on='case', suffixes=('_exp', '_sim'))
    if not paired.empty:
        paired['peak_error_pct'] = (paired['peak_stress_mpa_sim'] - paired['peak_stress_mpa_exp']) / paired['peak_stress_mpa_exp'] * 100.0
        paired['residual_error_pct'] = (paired['residual_stress_mpa_sim'] - paired['residual_stress_mpa_exp']) / paired['residual_stress_mpa_exp'] * 100.0
        paired['secant_modulus_error_pct'] = (paired['secant_modulus_mpa_sim'] - paired['secant_modulus_mpa_exp']) / paired['secant_modulus_mpa_exp'] * 100.0
        paired['tangent_modulus_error_pct'] = (paired['tangent_modulus_mpa_sim'] - paired['tangent_modulus_mpa_exp']) / paired['tangent_modulus_mpa_exp'] * 100.0
        paired['regression_modulus_error_pct'] = (paired['regression_modulus_mpa_sim'] - paired['regression_modulus_mpa_exp']) / paired['regression_modulus_mpa_exp'] * 100.0
        if save:
            paired.sort_values('case', key=lambda s: s.map(case_sort_key)).to_excel(CASES_DIR / 'experiment_simulation_comparison_2d.xlsx', index=False)

    return summary


def print_case_metrics(case_name: str) -> None:
    result = plot_case(case_name, save=True)
    print(result.to_string(index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='2D case name, for example Intact, b0_d14, or all')
    args = parser.parse_args()

    if args.target.lower() == 'all':
        summary = plot_all(save=True)
        print(summary.to_string(index=False))
    else:
        print_case_metrics(args.target)
