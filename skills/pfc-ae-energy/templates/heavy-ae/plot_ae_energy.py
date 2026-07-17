from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd

from config import MODEL_TO_MM, case_dir, case_title


plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.fonttype"] = 42


def read_numeric_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column in df.columns:
        if column not in {"mode_label"}:
            converted = pd.to_numeric(df[column], errors="coerce")
            if not converted.isna().all():
                df[column] = converted
    return df


def cumulative_trapezoid(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    out = np.zeros_like(x, dtype=float)
    if x.size < 2:
        return out
    dx = np.diff(x)
    avg = 0.5 * (y[1:] + y[:-1])
    out[1:] = np.cumsum(dx * avg)
    return out


def rolling_mean(values: np.ndarray, window: int = 7) -> np.ndarray:
    if values.size == 0 or window <= 1:
        return values
    window = max(1, min(window, values.size))
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(values, kernel, mode="same")


def derivative_vs_strain(strain: np.ndarray, values: np.ndarray) -> np.ndarray:
    if strain.size < 2:
        return np.zeros_like(strain, dtype=float)
    rate = np.zeros_like(values, dtype=float)
    delta_strain = np.diff(strain)
    delta_values = np.diff(values)
    local = np.divide(delta_values, delta_strain, out=np.zeros_like(delta_values, dtype=float), where=np.abs(delta_strain) > 1.0e-12)
    rate[1:] = local
    rate[0] = rate[1] if rate.size > 1 else 0.0
    return rolling_mean(rate, window=9)


def fit_elastic_modulus(strain: np.ndarray, stress_mpa: np.ndarray) -> float:
    if strain.size < 5:
        return float("nan")
    peak_idx = int(np.argmax(stress_mpa))
    ascending_strain = strain[: peak_idx + 1]
    ascending_stress = stress_mpa[: peak_idx + 1]
    peak_stress = float(np.max(ascending_stress))
    mask = (ascending_stress >= peak_stress * 0.10) & (ascending_stress <= peak_stress * 0.40) & (ascending_strain > 0.0)
    if np.count_nonzero(mask) < 5:
        mask = (ascending_stress >= peak_stress * 0.05) & (ascending_stress <= peak_stress * 0.50) & (ascending_strain > 0.0)
    if np.count_nonzero(mask) < 3:
        return float("nan")
    slope, _ = np.polyfit(ascending_strain[mask], ascending_stress[mask], 1)
    return float(slope)


def parse_stage_strains(case_path: Path) -> dict[str, float]:
    text = (case_path / "3load.dat").read_text(encoding="utf-8", errors="ignore")
    matches = re.findall(r"\[(stage_[a-d]_strain)\s*=\s*([0-9.eE+-]+)\]", text)
    return {name: float(value) for name, value in matches}


def event_stage_label(strain_value: float, stage_strains: dict[str, float], peak_strain: float) -> str:
    a = stage_strains.get("stage_a_strain", np.nan)
    b = stage_strains.get("stage_b_strain", np.nan)
    c = stage_strains.get("stage_c_strain", np.nan)
    d = stage_strains.get("stage_d_strain", np.nan)
    if strain_value < a:
        return "O-A"
    if strain_value < b:
        return "A-B"
    if strain_value < c:
        return "B-C"
    if strain_value < d:
        return "C-D"
    if strain_value < peak_strain:
        return "D-Peak"
    return "Post-Peak"


def cluster_hits_to_events(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()

    ordered = events.sort_values(["time", "strain"]).reset_index(drop=True).copy()
    time_values = ordered["time"].to_numpy(dtype=float)
    radius_mm = ordered["radius_mm"].to_numpy(dtype=float)
    x_mm = ordered["x_mm"].to_numpy(dtype=float)
    y_mm = ordered["y_mm"].to_numpy(dtype=float)

    valid_dt = np.diff(time_values)
    valid_dt = valid_dt[valid_dt > 0]
    base_dt = float(np.median(valid_dt)) if valid_dt.size else 0.0
    time_gap_limit = max(base_dt * 10.0, 2.5e-4)
    radius_ref = float(np.median(radius_mm[radius_mm > 0])) if np.any(radius_mm > 0) else 0.35
    overlap_slack_mm = max(radius_ref * 4.0, 1.2)

    rows: list[dict[str, float | int | str]] = []
    start = 0
    cluster_id = 0
    while start < len(ordered):
        end = start + 1
        center_x = float(x_mm[start])
        center_y = float(y_mm[start])
        reach = max(float(radius_mm[start]), radius_ref)
        while end < len(ordered):
            dt = float(time_values[end] - time_values[end - 1])
            dx = float(x_mm[end] - center_x)
            dy = float(y_mm[end] - center_y)
            dist = float(np.hypot(dx, dy))
            local_reach = max(reach, float(radius_mm[end]), radius_ref) + overlap_slack_mm
            if dt > time_gap_limit or dist > local_reach:
                break
            current = ordered.iloc[start : end + 1]
            center_x = float(current["x_mm"].mean())
            center_y = float(current["y_mm"].mean())
            reach = float(
                np.max(
                    np.hypot(current["x_mm"] - center_x, current["y_mm"] - center_y)
                    + current["radius_mm"].clip(lower=radius_ref)
                )
            )
            end += 1

        cluster = ordered.iloc[start:end].copy()
        cluster_id += 1
        tension_hits = int((cluster["mode_label"] == "tension").sum())
        shear_hits = int((cluster["mode_label"] == "shear").sum())
        hit_count = int(len(cluster))
        dominant_mode = "mixed"
        if tension_hits > shear_hits:
            dominant_mode = "tension"
        elif shear_hits > tension_hits:
            dominant_mode = "shear"
        mt_xx = float(cluster["mt_xx"].sum())
        mt_yy = float(cluster["mt_yy"].sum())
        mt_zz = float(cluster["mt_zz"].sum())
        mt_xy = float(cluster["mt_xy"].sum())
        mt_xz = float(cluster["mt_xz"].sum())
        mt_yz = float(cluster["mt_yz"].sum())
        size_proxy = float((cluster["stress_mpa"] * (cluster["radius_mm"].clip(lower=0.05) ** 2)).sum())
        magnitude_proxy = float(np.log10(max(size_proxy, 1.0e-6)))
        rows.append(
            {
                "event_id": cluster_id,
                "hit_count": hit_count,
                "tension_hits": tension_hits,
                "shear_hits": shear_hits,
                "dominant_mode": dominant_mode,
                "time_start": float(cluster["time"].iloc[0]),
                "time_end": float(cluster["time"].iloc[-1]),
                "duration": float(cluster["time"].iloc[-1] - cluster["time"].iloc[0]),
                "strain_start": float(cluster["strain"].iloc[0]),
                "strain_end": float(cluster["strain"].iloc[-1]),
                "stress_peak_mpa": float(cluster["stress_mpa"].max()),
                "stress_mean_mpa": float(cluster["stress_mpa"].mean()),
                "center_x_mm": float(cluster["x_mm"].mean()),
                "center_y_mm": float(cluster["y_mm"].mean()),
                "radius_extent_mm": float(
                    np.max(
                        np.hypot(cluster["x_mm"] - cluster["x_mm"].mean(), cluster["y_mm"] - cluster["y_mm"].mean())
                        + cluster["radius_mm"].clip(lower=radius_ref)
                    )
                ),
                "break_energy_sum": float(cluster["pbstrain_energy"].sum()),
                "break_strength_mean": float(cluster["break_strength"].mean()),
                "mt_xx": mt_xx,
                "mt_yy": mt_yy,
                "mt_zz": mt_zz,
                "mt_xy": mt_xy,
                "mt_xz": mt_xz,
                "mt_yz": mt_yz,
                "size_proxy": size_proxy,
                "magnitude_proxy": magnitude_proxy,
            }
        )
        start = end
    return pd.DataFrame(rows)


def classify_tk_source(t_value: float, k_value: float) -> str:
    if np.isnan(t_value) or np.isnan(k_value):
        return "undefined"
    if -1.0 <= t_value <= -0.4 and 0.2 <= k_value <= 0.4:
        return "linear_tensile"
    if 0.4 <= t_value <= 1.0 and -0.4 <= k_value <= -0.2:
        return "linear_shear"
    if -0.2 <= t_value <= 0.2 and -0.2 <= k_value <= 0.2:
        return "double_couple"
    return "mixed"


def tensor_metrics_from_components(mxx: float, myy: float, mzz: float, mxy: float, mxz: float, myz: float) -> dict[str, float | str]:
    tensor = np.array(
        [
            [mxx, mxy, mxz],
            [mxy, myy, myz],
            [mxz, myz, mzz],
        ],
        dtype=float,
    )
    tensor = 0.5 * (tensor + tensor.T)
    eigvals, eigvecs = np.linalg.eigh(tensor)
    eigvals = np.sort(eigvals)[::-1]
    m1, m2, m3 = (float(value) for value in eigvals)
    trace = float(np.trace(tensor))
    m_iso = trace / 3.0
    dev = eigvals - m_iso
    dev0, dev1, dev2 = (float(value) for value in dev)
    dev_scale = max(abs(dev0), abs(dev2))
    denom_k = abs(m_iso) + dev_scale
    t_value = float(2.0 * dev1 / dev_scale) if dev_scale > 1.0e-20 else 0.0
    k_value = float(m_iso / denom_k) if denom_k > 1.0e-20 else 0.0
    scalar_moment = float(np.sqrt(max((m1 * m1 + m2 * m2 + m3 * m3) / 2.0, 0.0)))
    magnitude = float((2.0 / 3.0) * np.log10(scalar_moment) - 6.0) if scalar_moment > 0.0 else np.nan
    r_denom = abs(trace) + abs(dev0) + abs(dev1) + abs(dev2)
    r_value = float(100.0 * trace / r_denom) if r_denom > 1.0e-20 else 0.0
    dev_abs = np.abs(dev)
    dev_abs_max = float(np.max(dev_abs))
    dev_abs_min = float(np.min(dev_abs))
    epsilon = float(-dev_abs_min / dev_abs_max) if dev_abs_max > 1.0e-20 else np.nan
    p_dc = float(max(0.0, 1.0 - 2.0 * abs(epsilon))) if np.isfinite(epsilon) else np.nan
    source_type = classify_tk_source(t_value, k_value)
    hudson_u, hudson_v = hudson_uv_from_principal(m1, m2, m3)
    return {
        "mt_principal_1": m1,
        "mt_principal_2": m2,
        "mt_principal_3": m3,
        "mt_trace": trace,
        "mt_iso": float(m_iso),
        "mt_dev_1": dev0,
        "mt_dev_2": dev1,
        "mt_dev_3": dev2,
        "scalar_moment": scalar_moment,
        "moment_magnitude": magnitude,
        "tk_t": t_value,
        "tk_k": k_value,
        "hudson_u": hudson_u,
        "hudson_v": hudson_v,
        "r_value": r_value,
        "epsilon": epsilon,
        "p_dc": p_dc,
        "source_type_tk": source_type,
    }


def decorate_cluster_tensors(clusters: pd.DataFrame) -> pd.DataFrame:
    if clusters.empty:
        return clusters
    metrics = [
        tensor_metrics_from_components(
            float(row.mt_xx),
            float(row.mt_yy),
            float(row.mt_zz),
            float(row.mt_xy),
            float(row.mt_xz),
            float(row.mt_yz),
        )
        for row in clusters.itertuples(index=False)
    ]
    return pd.concat([clusters.reset_index(drop=True), pd.DataFrame(metrics)], axis=1)


def chinese_font_properties() -> fm.FontProperties:
    candidates = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "Arial Unicode MS",
    ]
    available = {item.name for item in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return fm.FontProperties(family=name)
    return fm.FontProperties()


def hudson_uv_from_principal(m1: float, m2: float, m3: float) -> tuple[float, float]:
    eig = np.array([m1, m2, m3], dtype=float)
    scale = float(np.max(np.abs(eig)))
    if scale <= 1.0e-20:
        return 0.0, 0.0
    a1, a2, a3 = eig / scale
    u = -2.0 / 3.0 * (a1 + a3 - 2.0 * a2)
    v = 1.0 / 3.0 * (a1 + a2 + a3)
    return float(u), float(v)


def tk_to_uv(t_values: np.ndarray, k_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(t_values, dtype=float)
    k = np.clip(np.asarray(k_values, dtype=float), -0.999999, 0.999999)
    d0 = np.where(t <= 0.0, 1.0, 1.0 - t / 2.0)
    d1 = t / 2.0
    d2 = np.where(t <= 0.0, -1.0 - t / 2.0, -1.0)
    m_iso = k / (1.0 - np.abs(k))
    e1, e2, e3 = d0 + m_iso, d1 + m_iso, d2 + m_iso
    scale = np.maximum.reduce([np.abs(e1), np.abs(e2), np.abs(e3)])
    scale = np.where(scale <= 1.0e-20, 1.0, scale)
    a1, a2, a3 = e1 / scale, e2 / scale, e3 / scale
    u = -2.0 / 3.0 * (a1 + a3 - 2.0 * a2)
    v = 1.0 / 3.0 * (a1 + a2 + a3)
    return u, v


def tk_to_hudson_coords(t_values: np.ndarray, k_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return tk_to_uv(t_values, k_values)


def tk_to_diamond_coords(t_values: np.ndarray, k_values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return tk_to_hudson_coords(t_values, k_values)


edge_literal_points = {(2.0 / 3.0, 2.0 / 3.0), (-2.0 / 3.0, -2.0 / 3.0)}


def special_point_uv(t_value: float, k_value: float) -> tuple[float, float]:
    if (t_value, k_value) in edge_literal_points:
        return float(t_value), float(k_value)
    pu, pv = tk_to_uv(np.array([t_value]), np.array([k_value]))
    return float(pu[0]), float(pv[0])


def plot_tk_diamond_chinese(case_path: Path, case_name: str, clusters: pd.DataFrame) -> None:
    del case_name
    font_prop = chinese_font_properties()
    fig, ax = plt.subplots(figsize=(7.2, 6.3))

    palette = {
        "boundary": "#4D4D4D",
        "grid": "#D6D6D6",
        "guide_warm": "#D97B2D",
        "guide_cool": "#4F81BD",
        "guide_neutral": "#8A8A8A",
        "linear_tensile": "#D55E00",
        "linear_shear": "#4C78A8",
        "double_couple": "#2A9D8F",
        "mixed": "#9C6ADE",
        "undefined": "#8F8F8F",
    }

    ax.plot(
        [-4.0 / 3.0, 0.0, 4.0 / 3.0, 0.0, -4.0 / 3.0],
        [-1.0 / 3.0, -1.0, 1.0 / 3.0, 1.0, -1.0 / 3.0],
        color=palette["boundary"],
        linewidth=1.5,
        zorder=2,
    )

    t_dense = np.linspace(-1.0, 1.0, 241)
    for k_value in np.linspace(-0.9, 0.9, 19):
        gu, gv = tk_to_uv(t_dense, np.full_like(t_dense, k_value))
        ax.plot(gu, gv, color=palette["grid"], linewidth=0.5, zorder=0)

    k_dense = np.linspace(-0.97, 0.97, 241)
    for t_value in np.linspace(-1.0, 1.0, 19):
        gu, gv = tk_to_uv(np.full_like(k_dense, t_value), k_dense)
        ax.plot(gu, gv, color=palette["grid"], linewidth=0.5, zorder=0)

    ax.plot([-1.0, 1.0], [0.0, 0.0], color=palette["guide_neutral"], linewidth=1.0, zorder=1)
    ax.plot([0.0, 0.0], [-1.0, 1.0], color=palette["guide_neutral"], linewidth=1.0, zorder=1)
    ax.plot(
        [-4.0 / 3.0, 4.0 / 3.0],
        [-1.0 / 3.0, 1.0 / 3.0],
        color=palette["guide_neutral"],
        linewidth=1.0,
        linestyle=(0, (4, 3)),
        alpha=0.95,
        zorder=1,
    )

    guide_line_specs = [
        ([-1.0, 1.0], [1.0 / 3.0, -1.0 / 3.0], palette["guide_neutral"], (0, (4, 3)), 1.0),
        ([-2.0 / 3.0, 1.0], [-2.0 / 3.0, -1.0 / 3.0], palette["guide_cool"], (0, (4, 3)), 1.0),
        ([2.0 / 3.0, -1.0], [2.0 / 3.0, 1.0 / 3.0], palette["guide_cool"], (0, (4, 3)), 1.0),
        ([-1.0, 1.0], [5.0 / 9.0, -1.0 / 3.0], palette["guide_warm"], (0, (5, 3)), 1.0),
    ]
    for t_pair, k_pair, color, line_style, line_width in guide_line_specs:
        u0, v0 = special_point_uv(t_pair[0], k_pair[0])
        u1, v1 = special_point_uv(t_pair[1], k_pair[1])
        ax.plot([u0, u1], [v0, v1], color=color, linewidth=line_width, linestyle=line_style, alpha=0.95, zorder=1)

    color_map = {
        "linear_tensile": palette["linear_tensile"],
        "linear_shear": palette["linear_shear"],
        "double_couple": palette["double_couple"],
        "mixed": palette["mixed"],
        "undefined": palette["undefined"],
    }
    marker_map = {
        "linear_tensile": "o",
        "linear_shear": "D",
        "double_couple": "s",
        "mixed": "h",
        "undefined": "x",
    }

    if not clusters.empty:
        for source_type, color in color_map.items():
            chunk = clusters[clusters["source_type_tk"] == source_type]
            if chunk.empty:
                continue
            chunk_sizes = np.clip(np.nan_to_num(chunk["scalar_moment"].to_numpy(dtype=float), nan=0.0) * 9.0e5, 10.0, 38.0)
            ax.scatter(
                chunk["hudson_u"].to_numpy(dtype=float),
                chunk["hudson_v"].to_numpy(dtype=float),
                s=chunk_sizes,
                c=color,
                marker=marker_map[source_type],
                alpha=0.72,
                edgecolors="white",
                linewidths=0.28,
                zorder=3,
            )
        source_df = clusters.loc[:, ["event_id", "tk_t", "tk_k", "hudson_u", "hudson_v", "scalar_moment", "moment_magnitude", "source_type_tk"]].copy()
        source_df.to_csv(case_path / "ae_tk_diamond_cn_source_data.csv", index=False, encoding="utf-8-sig")

    annotation_specs = [
        ("\u5747\u5300\u81a8\u80c0 k=+1.0", 0.0, 1.0, 0.00, 0.08, "center", "bottom"),
        ("\u5747\u5300\u538b\u7f29 k=-1.0", 0.0, -1.0, 0.00, -0.09, "center", "top"),
        ("CLVD T=-1.0", -1.0, 0.0, -0.06, 0.02, "right", "bottom"),
        ("-CLVD T=+1.0", 1.0, 0.0, 0.06, 0.02, "left", "bottom"),
        ("\u53cc\u529b\u5076\u526a\u5207 T=0, k=0", 0.0, 0.0, -0.10, -0.09, "right", "top"),
        ("\u5f20\u62c9\u7834\u88c2 (-1, 5/9)", -1.0, 5.0 / 9.0, -0.08, 0.05, "right", "bottom"),
        ("\u538b\u7f29\u7834\u88c2 (1, -5/9)", 1.0, -5.0 / 9.0, 0.08, -0.05, "left", "top"),
        ("\u7ebf\u6027\u77e2\u91cf\u5076\u6781(\u6b63) (-1, 1/3)", -1.0, 1.0 / 3.0, -0.09, 0.02, "right", "center"),
        ("\u7ebf\u6027\u77e2\u91cf\u5076\u6781(\u8d1f) (1, -1/3)", 1.0, -1.0 / 3.0, 0.09, -0.02, "left", "center"),
        ("(-1, -1/5)", -1.0, -1.0 / 5.0, -0.05, -0.02, "right", "top"),
        ("(1, 1/5)", 1.0, 1.0 / 5.0, 0.06, 0.00, "left", "center"),
        ("(-2/3, -2/3)", -2.0 / 3.0, -2.0 / 3.0, -0.04, -0.06, "right", "top"),
        ("(2/3, 2/3)", 2.0 / 3.0, 2.0 / 3.0, 0.04, 0.02, "left", "bottom"),
    ]
    for label, t_value, k_value, dx, dy, ha, va in annotation_specs:
        u_point, v_point = special_point_uv(t_value, k_value)
        x_value, y_value = np.array([u_point]), np.array([v_point])
        point_color = palette["boundary"]
        if (t_value, k_value) in [(-1.0, -1.0 / 5.0), (1.0, 1.0 / 5.0), (-2.0 / 3.0, -2.0 / 3.0), (2.0 / 3.0, 2.0 / 3.0)]:
            point_color = palette["guide_cool"]
        elif (t_value, k_value) in [(-1.0, 5.0 / 9.0), (1.0, -5.0 / 9.0)]:
            point_color = palette["guide_warm"]
        ax.scatter(x_value, y_value, s=24.0, c=point_color, zorder=4)
        ax.text(
            float(x_value[0] + dx),
            float(y_value[0] + dy),
            label,
            fontproperties=font_prop,
            fontsize=9.1,
            ha=ha,
            va=va,
            color="#222222",
        )

    ax.set_xlim(-4.0 / 3.0 - 0.18, 4.0 / 3.0 + 0.18)
    ax.set_ylim(-1.18, 1.18)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("\u58f0\u53d1\u5c04\u4e8b\u4ef6\u77e9\u5f20\u91cf T-k \u673a\u5236\u5206\u5e03", fontproperties=font_prop, fontsize=12.5, pad=10)
    fig.tight_layout()
    fig.savefig(case_path / "ae_tk_diamond_cn.png", dpi=320, bbox_inches="tight")
    fig.savefig(case_path / "ae_tk_diamond_cn.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_tk_diamond_cn.pdf", bbox_inches="tight")
    fig.savefig(case_path / "ae_tk_diamond_cn.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)


def tensor_matrix_from_row(row: pd.Series) -> np.ndarray:
    return np.array(
        [
            [float(row["mt_xx"]), float(row["mt_xy"]), float(row["mt_xz"])],
            [float(row["mt_xy"]), float(row["mt_yy"]), float(row["mt_yz"])],
            [float(row["mt_xz"]), float(row["mt_yz"]), float(row["mt_zz"])],
        ],
        dtype=float,
    )


def principal_axis_vectors(row: pd.Series) -> tuple[np.ndarray, np.ndarray] | tuple[None, None]:
    matrix = tensor_matrix_from_row(row)
    if not np.isfinite(matrix).all():
        return None, None
    values, vectors = np.linalg.eigh(matrix)
    order = np.argsort(values)[::-1]
    vectors = vectors[:, order]
    return vectors[:, 0], vectors[:, -1]


def axis_azimuth_rad(vector: np.ndarray) -> float:
    """Return compass azimuth in radians for an undirected principal axis."""
    x_value, y_value = float(vector[0]), float(vector[1])
    if abs(x_value) < 1.0e-20 and abs(y_value) < 1.0e-20:
        return float("nan")
    angle = np.arctan2(x_value, y_value)
    # Principal axes are bidirectional; fold to 0-pi to avoid arbitrary sign flips.
    return float(angle % np.pi)


def lower_hemisphere_equal_area(vector: np.ndarray) -> tuple[float, float]:
    """Schmidt equal-area projection for 3D tensors; 2D tensors plot on the rim."""
    vec = np.asarray(vector, dtype=float)
    norm = float(np.linalg.norm(vec))
    if norm <= 0.0:
        return float("nan"), float("nan")
    vec = vec / norm
    if vec[2] > 0.0:
        vec = -vec
    theta = np.arccos(np.clip(-vec[2], -1.0, 1.0))
    radius = np.sin(theta / 2.0)
    azimuth = np.arctan2(vec[0], vec[1])
    return float(radius * np.sin(azimuth)), float(radius * np.cos(azimuth))


def draw_orientation_frame(ax: plt.Axes, title: str) -> None:
    ink = "#272727"
    grid = "#D7D7D7"
    inner_grid = "#EAEAEA"
    ax.set_facecolor("white")
    ax.add_patch(plt.Circle((0.0, 0.0), 1.0, edgecolor=ink, facecolor="none", linewidth=0.95, zorder=3))
    for radius in (0.25, 0.50, 0.75):
        ax.add_patch(plt.Circle((0.0, 0.0), radius, edgecolor=inner_grid, facecolor="none", linewidth=0.45, zorder=0))
    for angle_deg in range(0, 180, 30):
        angle = np.radians(angle_deg)
        x_value = np.sin(angle)
        y_value = np.cos(angle)
        ax.plot([-x_value, x_value], [-y_value, y_value], color=grid, linewidth=0.48, zorder=0)
    ax.plot([-1.0, 1.0], [0.0, 0.0], color="#BDBDBD", linewidth=0.68, zorder=1)
    ax.plot([0.0, 0.0], [-1.0, 1.0], color="#BDBDBD", linewidth=0.68, zorder=1)
    ax.scatter([0.0], [0.0], s=10.0, c=ink, marker="o", linewidths=0.0, zorder=5)
    ax.text(0.0, 0.045, "O", ha="center", va="bottom", fontsize=8.2, color=ink)
    label_kw = dict(fontsize=10.8, color=ink, family="sans-serif")
    ax.text(0.0, 1.055, "N", ha="center", va="bottom", **label_kw)
    ax.text(1.055, 0.0, "E", ha="left", va="center", **label_kw)
    ax.text(0.0, -1.055, "S", ha="center", va="top", **label_kw)
    ax.text(-1.055, 0.0, "W", ha="right", va="center", **label_kw)
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-1.12, 1.12)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9.0, fontweight="bold", color=ink, pad=8)


def plot_ae_orientation(case_path: Path, case_name: str, clusters: pd.DataFrame) -> None:
    if clusters.empty:
        return
    required = {"mt_xx", "mt_yy", "mt_zz", "mt_xy", "mt_xz", "mt_yz", "scalar_moment"}
    if not required.issubset(clusters.columns):
        return

    rows: list[dict[str, float | str | int]] = []
    for _, row in clusters.iterrows():
        t_axis, p_axis = principal_axis_vectors(row)
        if t_axis is None or p_axis is None:
            continue
        scalar = float(row.get("scalar_moment", np.nan))
        source_type = str(row.get("source_type_tk", "undefined"))
        for axis_name, axis_vector in (("T", t_axis), ("P", p_axis)):
            sx, sy = lower_hemisphere_equal_area(axis_vector)
            azimuth = axis_azimuth_rad(axis_vector)
            if not np.isfinite(azimuth):
                continue
            rows.append(
                {
                    "event_id": int(row.get("event_id", len(rows) + 1)),
                    "axis": axis_name,
                    "azimuth_deg": float(np.degrees(azimuth)),
                    "stereonet_x": sx,
                    "stereonet_y": sy,
                    "scalar_moment": scalar,
                    "moment_magnitude": float(row.get("moment_magnitude", np.nan)),
                    "source_type_tk": source_type,
                    "stage_label": str(row.get("stage_label", "")),
                }
            )

    axes_df = pd.DataFrame(rows)
    if axes_df.empty:
        return
    axes_df.to_csv(case_path / "ae_orientation_axes.csv", index=False, encoding="utf-8-sig")

    color_map = {
        "linear_tensile": "#B64342",
        "linear_shear": "#0F4D92",
        "double_couple": "#42949E",
        "mixed": "#9A4D8E",
        "undefined": "#767676",
    }

    fig, ax = plt.subplots(figsize=(3.54, 3.54))
    draw_orientation_frame(ax, case_title(case_name) + "  AE tensor principal axes")
    for axis_name, marker, size, alpha in (("T", ".", 18.0, 0.52), ("P", "+", 42.0, 0.72)):
        chunk = axes_df[axes_df["axis"] == axis_name]
        if chunk.empty:
            continue
        ax.scatter(
            chunk["stereonet_x"],
            chunk["stereonet_y"],
            s=size,
            c="#272727" if axis_name == "P" else "#767676",
            marker=marker,
            alpha=alpha,
            linewidths=0.7 if axis_name == "P" else 0.0,
            label=f"{axis_name} axis",
        )
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.095), ncol=2, frameon=False, fontsize=6.8, handletextpad=0.35, columnspacing=0.9)
    fig.tight_layout(pad=0.25)
    fig.savefig(case_path / "ae_orientation_stereonet.png", dpi=600, bbox_inches="tight")
    fig.savefig(case_path / "ae_orientation_stereonet.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_orientation_stereonet.pdf", bbox_inches="tight")
    fig.savefig(case_path / "ae_orientation_stereonet.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)

    moment = np.nan_to_num(axes_df["scalar_moment"].to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    positive = moment[moment > 0.0]
    ref = float(np.nanpercentile(positive, 95)) if positive.size else 1.0
    ref = max(ref, 1.0e-20)
    axes_df["radial_moment"] = np.clip(np.sqrt(np.maximum(axes_df["scalar_moment"].astype(float), 0.0) / ref), 0.08, 1.0)

    fig, ax = plt.subplots(figsize=(3.54, 3.54))
    draw_orientation_frame(ax, case_title(case_name) + "  AE orientation by moment")
    for source_type, color in color_map.items():
        chunk = axes_df[(axes_df["axis"] == "T") & (axes_df["source_type_tk"] == source_type)]
        if chunk.empty:
            continue
        azimuth = np.radians(chunk["azimuth_deg"].to_numpy(dtype=float))
        radial = chunk["radial_moment"].to_numpy(dtype=float)
        # Plot antipodal points because a principal axis has no arrow direction.
        x_values = np.concatenate([radial * np.sin(azimuth), -radial * np.sin(azimuth)])
        y_values = np.concatenate([radial * np.cos(azimuth), -radial * np.cos(azimuth)])
        ax.scatter(x_values, y_values, s=14.0, c=color, marker=".", alpha=0.62, label=source_type)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False, fontsize=6.4, handletextpad=0.35, columnspacing=0.8)
    fig.tight_layout(pad=0.25)
    fig.savefig(case_path / "ae_orientation_moment_polar.png", dpi=600, bbox_inches="tight")
    fig.savefig(case_path / "ae_orientation_moment_polar.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_orientation_moment_polar.pdf", bbox_inches="tight")
    fig.savefig(case_path / "ae_orientation_moment_polar.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)

def build_stage_count_table(events: pd.DataFrame, stage_strains: dict[str, float], peak_strain: float) -> pd.DataFrame:
    bounds = [
        ("O-A", 0.0, stage_strains.get("stage_a_strain", np.nan)),
        ("A-B", stage_strains.get("stage_a_strain", np.nan), stage_strains.get("stage_b_strain", np.nan)),
        ("B-C", stage_strains.get("stage_b_strain", np.nan), stage_strains.get("stage_c_strain", np.nan)),
        ("C-D", stage_strains.get("stage_c_strain", np.nan), stage_strains.get("stage_d_strain", np.nan)),
        ("D-Peak", stage_strains.get("stage_d_strain", np.nan), peak_strain),
        ("Post-Peak", peak_strain, np.inf),
    ]
    rows: list[dict[str, float | str]] = []
    for label, lower, upper in bounds:
        if np.isnan(lower) or np.isnan(upper):
            continue
        mask = (events["strain"] >= lower) & (events["strain"] < upper)
        chunk = events.loc[mask]
        rows.append(
            {
                "stage": label,
                "total_hits": int(len(chunk)),
                "tension_hits": int((chunk["mode_label"] == "tension").sum()),
                "shear_hits": int((chunk["mode_label"] == "shear").sum()),
                "lower_strain": float(lower),
                "upper_strain": float(upper),
            }
        )
    return pd.DataFrame(rows)


def plot_case(case_name: str) -> None:
    case_path = case_dir(case_name)
    stress_path = case_path / "stress_strain.csv"
    events_path = case_path / "ae_events.csv"
    if not stress_path.exists():
        raise FileNotFoundError(f"Missing {stress_path}")
    if not events_path.exists():
        raise FileNotFoundError(f"Missing {events_path}")

    curve = read_numeric_csv(stress_path).copy()
    events = read_numeric_csv(events_path).copy()
    required_curve = {"strain", "stress_mpa", "crack_num"}
    required_events = {
        "strain",
        "stress_mpa",
        "x",
        "y",
        "mode_label",
        "pbstrain_energy",
        "break_strength",
        "mt_xx",
        "mt_yy",
        "mt_zz",
        "mt_xy",
        "mt_xz",
        "mt_yz",
    }
    if not required_curve.issubset(curve.columns):
        raise ValueError(f"stress_strain.csv missing columns: {sorted(required_curve - set(curve.columns))}")
    if not required_events.issubset(events.columns):
        raise ValueError(f"ae_events.csv missing columns: {sorted(required_events - set(events.columns))}")

    curve = curve.dropna(subset=["strain", "stress_mpa", "crack_num"]).copy()
    curve["strain"] = curve["strain"].abs().astype(float)
    curve["stress_mpa"] = curve["stress_mpa"].abs().astype(float)
    curve["crack_num"] = curve["crack_num"].astype(float)
    curve["crack_tension_num"] = pd.to_numeric(curve.get("crack_tension_num"), errors="coerce").fillna(0.0)
    curve["crack_shear_num"] = pd.to_numeric(curve.get("crack_shear_num"), errors="coerce").fillna(0.0)
    curve = curve.sort_values("strain").drop_duplicates(subset=["strain"], keep="last").reset_index(drop=True)

    events = events.dropna(subset=["strain", "stress_mpa", "x", "y"]).copy()
    events["strain"] = events["strain"].abs().astype(float)
    events["stress_mpa"] = events["stress_mpa"].abs().astype(float)
    events["x_mm"] = events["x"].astype(float) * MODEL_TO_MM
    events["y_mm"] = events["y"].astype(float) * MODEL_TO_MM
    events["radius_mm"] = pd.to_numeric(events.get("radius_model"), errors="coerce").fillna(0.0) * MODEL_TO_MM
    events["mode_label"] = events["mode_label"].astype(str).str.lower()
    for tensor_name in ("pbstrain_energy", "break_strength", "mt_xx", "mt_yy", "mt_zz", "mt_xy", "mt_xz", "mt_yz"):
        events[tensor_name] = pd.to_numeric(events[tensor_name], errors="coerce").fillna(0.0)

    strain = curve["strain"].to_numpy(dtype=float)
    stress_mpa = curve["stress_mpa"].to_numpy(dtype=float)
    total_hits = curve["crack_num"].to_numpy(dtype=float)
    tension_hits = curve["crack_tension_num"].to_numpy(dtype=float)
    shear_hits = curve["crack_shear_num"].to_numpy(dtype=float)

    rate_total = derivative_vs_strain(strain, total_hits)
    rate_tension = derivative_vs_strain(strain, tension_hits)
    rate_shear = derivative_vs_strain(strain, shear_hits)

    energy_input = cumulative_trapezoid(strain, stress_mpa)
    elastic_modulus = fit_elastic_modulus(strain, stress_mpa)
    energy_elastic = np.zeros_like(energy_input)
    if np.isfinite(elastic_modulus) and elastic_modulus > 0.0:
        energy_elastic = (stress_mpa ** 2) / (2.0 * elastic_modulus)
    energy_dissipated = np.maximum(energy_input - energy_elastic, 0.0)

    peak_idx = int(np.argmax(stress_mpa))
    peak_strain = float(strain[peak_idx])
    peak_stress = float(stress_mpa[peak_idx])
    peak_rate_idx = int(np.argmax(rate_total))
    stage_strains = parse_stage_strains(case_path)
    stage_table = build_stage_count_table(events, stage_strains, peak_strain)
    clusters = decorate_cluster_tensors(cluster_hits_to_events(events))
    if not clusters.empty:
        clusters["stage_label"] = clusters["strain_start"].apply(lambda value: event_stage_label(float(value), stage_strains, peak_strain))
        cluster_stage = (
            clusters.groupby(["stage_label", "source_type_tk"], dropna=False)
            .agg(
                event_count=("event_id", "count"),
                total_hits=("hit_count", "sum"),
                mean_hits_per_event=("hit_count", "mean"),
                max_moment_magnitude=("moment_magnitude", "max"),
            )
            .reset_index()
        )
    else:
        cluster_stage = pd.DataFrame(columns=["stage_label", "source_type_tk", "event_count", "total_hits", "mean_hits_per_event", "max_moment_magnitude"])

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    ax = axes[0, 0]
    ax.plot(strain, stress_mpa, color="#1f77b4", linewidth=2.2, label="Stress")
    ax.set_xlabel("Axial Strain")
    ax.set_ylabel("Axial Stress (MPa)")
    ax.set_title("Stress and Cumulative AE")
    twin = ax.twinx()
    twin.plot(strain, total_hits, color="#c0392b", linewidth=1.8, label="AE Hits")
    twin.plot(strain, tension_hits, color="#f39c12", linewidth=1.2, linestyle="--", label="Tension")
    twin.plot(strain, shear_hits, color="#7f8c8d", linewidth=1.2, linestyle=":", label="Shear")
    twin.set_ylabel("Cumulative Hits")
    for stage_name in ("stage_a_strain", "stage_b_strain", "stage_c_strain", "stage_d_strain"):
        stage_value = stage_strains.get(stage_name)
        if stage_value is not None:
            ax.axvline(stage_value, color="#bbbbbb", linewidth=0.8, linestyle="--")
    ax.axvline(peak_strain, color="#2c3e50", linewidth=1.0, linestyle="-.", alpha=0.7)
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = twin.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc="upper left", fontsize=8)

    ax = axes[0, 1]
    ax.plot(strain, rate_total, color="#c0392b", linewidth=1.8, label="Total")
    ax.plot(strain, rate_tension, color="#f39c12", linewidth=1.2, linestyle="--", label="Tension")
    ax.plot(strain, rate_shear, color="#7f8c8d", linewidth=1.2, linestyle=":", label="Shear")
    ax.axvline(peak_strain, color="#2c3e50", linewidth=1.0, linestyle="-.", alpha=0.7)
    ax.set_xlabel("Axial Strain")
    ax.set_ylabel("AE Hit Rate (per strain)")
    ax.set_title("AE Hit Rate")
    ax.legend(loc="upper left", fontsize=8)

    ax = axes[1, 0]
    ax.plot(strain, energy_input, color="#1f77b4", linewidth=2.0, label="Input")
    ax.plot(strain, energy_elastic, color="#27ae60", linewidth=1.5, linestyle="--", label="Elastic")
    ax.plot(strain, energy_dissipated, color="#8e44ad", linewidth=1.5, linestyle="-.", label="Dissipated")
    ax.axvline(peak_strain, color="#2c3e50", linewidth=1.0, linestyle="-.", alpha=0.7)
    ax.set_xlabel("Axial Strain")
    ax.set_ylabel("Energy Density (MJ/m^3)")
    ax.set_title("Macro Energy Density")
    ax.legend(loc="upper left", fontsize=8)

    ax = axes[1, 1]
    tension = events[events["mode_label"] == "tension"]
    shear = events[events["mode_label"] == "shear"]
    size_tension = np.clip(tension["radius_mm"].to_numpy(dtype=float) * 140.0, 12.0, 80.0) if not tension.empty else []
    size_shear = np.clip(shear["radius_mm"].to_numpy(dtype=float) * 140.0, 12.0, 80.0) if not shear.empty else []
    if not tension.empty:
        ax.scatter(tension["x_mm"], tension["y_mm"], s=size_tension, c=tension["stress_mpa"], cmap="YlOrRd", alpha=0.7, edgecolors="none", label="Tension")
    if not shear.empty:
        ax.scatter(shear["x_mm"], shear["y_mm"], s=size_shear, c=shear["stress_mpa"], cmap="Blues", alpha=0.7, marker="s", edgecolors="none", label="Shear")
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("AE Event Map")
    ax.legend(loc="best", fontsize=8)

    fig.suptitle(case_title(case_name) + "  AE and Energy Overview", fontsize=13)
    fig.tight_layout()
    fig.savefig(case_path / "ae_energy_overview.png", dpi=300, bbox_inches="tight")
    fig.savefig(case_path / "ae_energy_overview.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_energy_overview.pdf", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 6.0))
    scatter = None
    if not events.empty:
        colors = events["stress_mpa"].to_numpy(dtype=float)
        markers = {"tension": "o", "shear": "s"}
        for mode_label, marker in markers.items():
            chunk = events[events["mode_label"] == mode_label]
            if chunk.empty:
                continue
            size = np.clip(chunk["radius_mm"].to_numpy(dtype=float) * 150.0, 14.0, 90.0)
            scatter = ax.scatter(
                chunk["x_mm"],
                chunk["y_mm"],
                s=size,
                c=chunk["stress_mpa"],
                cmap="viridis",
                alpha=0.78,
                marker=marker,
                edgecolors="none",
                label=mode_label.title(),
            )
        if scatter is not None:
            cbar = fig.colorbar(scatter, ax=ax, fraction=0.046, pad=0.03)
            cbar.set_label("Stress at event (MPa)")
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(case_title(case_name) + "  AE Event Distribution")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(case_path / "ae_event_map.png", dpi=300, bbox_inches="tight")
    fig.savefig(case_path / "ae_event_map.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_event_map.pdf", bbox_inches="tight")
    plt.close(fig)

    marker_map = {
        "linear_tensile": "o",
        "linear_shear": "D",
        "double_couple": "s",
        "mixed": "h",
        "undefined": "x",
    }
    color_map = {
        "linear_tensile": "#B64342",
        "linear_shear": "#0F4D92",
        "double_couple": "#42949E",
        "mixed": "#9A4D8E",
        "undefined": "#767676",
    }

    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    if not clusters.empty:
        for source_type, marker in marker_map.items():
            chunk = clusters[clusters["source_type_tk"] == source_type]
            if chunk.empty:
                continue
            size = np.clip(np.nan_to_num(chunk["scalar_moment"].to_numpy(dtype=float), nan=0.0) * 1.0e6, 20.0, 180.0)
            ax.scatter(
                chunk["center_x_mm"],
                chunk["center_y_mm"],
                s=size,
                c=color_map[source_type],
                marker=marker,
                alpha=0.78,
                edgecolors="none",
                label=source_type,
            )
    ax.set_aspect("equal")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(case_title(case_name) + "  AE Source Mechanism Map")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(case_path / "ae_source_event_map.png", dpi=300, bbox_inches="tight")
    fig.savefig(case_path / "ae_source_event_map.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_source_event_map.pdf", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.0, 5.2))
    if not clusters.empty:
        for source_type, marker in marker_map.items():
            chunk = clusters[clusters["source_type_tk"] == source_type]
            if chunk.empty:
                continue
            size = np.clip(np.nan_to_num(chunk["scalar_moment"].to_numpy(dtype=float), nan=0.0) * 1.0e6, 22.0, 160.0)
            ax.scatter(
                chunk["tk_t"],
                chunk["tk_k"],
                s=size,
                c=color_map[source_type],
                marker=marker,
                alpha=0.8,
                edgecolors="none",
                label=source_type,
            )
    ax.axhline(0.0, color="#bbbbbb", linewidth=0.8)
    ax.axvline(0.0, color="#bbbbbb", linewidth=0.8)
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel("T")
    ax.set_ylabel("k")
    ax.set_title("T-k Source Mechanism")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(case_path / "ae_tk_source_map.png", dpi=300, bbox_inches="tight")
    fig.savefig(case_path / "ae_tk_source_map.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_tk_source_map.pdf", bbox_inches="tight")
    plt.close(fig)
    plot_tk_diamond_chinese(case_path, case_name, clusters)
    plot_ae_orientation(case_path, case_name, clusters)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    ax = axes[0]
    if not clusters.empty:
        order = ["O-A", "A-B", "B-C", "C-D", "D-Peak", "Post-Peak"]
        counts = (
            cluster_stage.pivot(index="stage_label", columns="source_type_tk", values="event_count")
            .reindex(order)
            .fillna(0.0)
        )
        cumulative = np.zeros(len(counts), dtype=float)
        for source_type in ("linear_tensile", "linear_shear", "double_couple", "mixed", "undefined"):
            if source_type in counts.columns:
                values = counts[source_type].to_numpy(dtype=float)
                ax.bar(counts.index, values, bottom=cumulative, color=color_map[source_type], label=source_type)
                cumulative = cumulative + values
        twin = ax.twinx()
        total_hits_by_stage = (
            cluster_stage.groupby("stage_label", dropna=False)["total_hits"].sum().reindex(order).fillna(0.0)
        )
        twin.plot(total_hits_by_stage.index, total_hits_by_stage.to_numpy(dtype=float), color="#111111", marker="o", linewidth=1.4, label="Hits")
        twin.set_ylabel("Total Hits")
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = twin.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc="upper left", fontsize=8)
    ax.set_ylabel("Event Count")
    ax.set_title("Stage-wise AE Mechanisms")
    ax.tick_params(axis="x", rotation=25)

    ax = axes[1]
    if not clusters.empty:
        for source_type, marker in marker_map.items():
            chunk = clusters[clusters["source_type_tk"] == source_type]
            if chunk.empty:
                continue
            size = np.clip(np.nan_to_num(chunk["scalar_moment"].to_numpy(dtype=float), nan=0.0) * 1.0e6, 24.0, 170.0)
            ax.scatter(
                chunk["strain_start"],
                chunk["moment_magnitude"],
                s=size,
                c=color_map[source_type],
                marker=marker,
                alpha=0.82,
                edgecolors="none",
                label=source_type,
            )
    ax.axvline(peak_strain, color="#2c3e50", linewidth=1.0, linestyle="-.", alpha=0.7)
    ax.set_xlabel("Axial Strain")
    ax.set_ylabel("Moment Magnitude")
    ax.set_title("Event Moment Evolution")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(case_path / "ae_event_evolution.png", dpi=300, bbox_inches="tight")
    fig.savefig(case_path / "ae_event_evolution.svg", bbox_inches="tight")
    fig.savefig(case_path / "ae_event_evolution.pdf", bbox_inches="tight")
    plt.close(fig)

    summary = pd.DataFrame(
        [
            {"metric": "total_hits", "value": float(total_hits[-1])},
            {"metric": "tension_hits", "value": float(tension_hits[-1])},
            {"metric": "shear_hits", "value": float(shear_hits[-1])},
            {"metric": "clustered_event_count", "value": float(len(clusters))},
            {"metric": "mean_hits_per_event", "value": float(clusters["hit_count"].mean()) if not clusters.empty else np.nan},
            {"metric": "max_event_hits", "value": float(clusters["hit_count"].max()) if not clusters.empty else np.nan},
            {"metric": "max_scalar_moment", "value": float(clusters["scalar_moment"].max()) if not clusters.empty else np.nan},
            {"metric": "max_moment_magnitude", "value": float(clusters["moment_magnitude"].max()) if not clusters.empty else np.nan},
            {"metric": "total_break_energy", "value": float(events["pbstrain_energy"].sum()) if not events.empty else np.nan},
            {"metric": "first_hit_strain", "value": float(events["strain"].min()) if not events.empty else np.nan},
            {"metric": "first_hit_stress_mpa", "value": float(events.loc[events["strain"].idxmin(), "stress_mpa"]) if not events.empty else np.nan},
            {"metric": "peak_stress_mpa", "value": peak_stress},
            {"metric": "peak_stress_strain", "value": peak_strain},
            {"metric": "peak_ae_rate", "value": float(rate_total[peak_rate_idx])},
            {"metric": "peak_ae_rate_strain", "value": float(strain[peak_rate_idx])},
            {"metric": "elastic_modulus_mpa", "value": elastic_modulus},
            {"metric": "peak_input_energy_mj_m3", "value": float(energy_input[peak_idx])},
            {"metric": "peak_dissipated_energy_mj_m3", "value": float(energy_dissipated[peak_idx])},
            {"metric": "final_input_energy_mj_m3", "value": float(energy_input[-1])},
            {"metric": "final_dissipated_energy_mj_m3", "value": float(energy_dissipated[-1])},
        ]
    )

    with pd.ExcelWriter(case_path / "ae_energy_metrics.xlsx") as writer:
        summary.to_excel(writer, index=False, sheet_name="summary")
        stage_table.to_excel(writer, index=False, sheet_name="stage_counts")
        cluster_stage.to_excel(writer, index=False, sheet_name="cluster_stage")
        clusters.to_excel(writer, index=False, sheet_name="clustered_events")
        events.to_excel(writer, index=False, sheet_name="events")
    clusters.to_csv(case_path / "ae_clustered_events.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot AE and energy diagnostics for one PFC case.")
    parser.add_argument("case", help="Case name, for example b30_d20")
    args = parser.parse_args()
    plot_case(args.case)


if __name__ == "__main__":
    main()
