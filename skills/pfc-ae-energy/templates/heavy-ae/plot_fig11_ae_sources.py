from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, ConnectionPatch, FancyArrowPatch
from matplotlib.collections import PatchCollection

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
plt.rcParams["svg.fonttype"] = "none"

# Fig.11 "AE sources of different fracture types".
# Required:  ae_clustered_events.csv (event_id, center_x_mm, center_y_mm,
#            moment_magnitude, r_value, tension_hits, shear_hits, hit_count, mt_xx, mt_yy, mt_xy)
# Optional (real microstructure; falls back to a schematic disk if absent):
#   plotdata_ball_fields_final.csv or plotdata_ball_fields_peak.csv : PFC ball field (x, y, radius in metres)
#   ae_events.csv                 : individual micro-cracks (x, y in metres, mode_label, radius_model)
# Source type is decided by R = isotropic/deviatoric ratio (paper Fig.11 metric):
#   R > +thr -> Explosion (tensile),  R < -thr -> Implosion (compressive),  |R| <= thr -> Shear.

MM = 1000.0  # metres -> millimetres

PALETTE = {
    "tension": "#B64342",   # micro-tension crack (red)
    "shear": "#0F4D92",     # micro-shear crack (blue)
    "green": "#3CB371",     # AE event circle
    "blue_dash": "#2F8EFF", # dashed boundary
    "ball": "#1E88FF",      # particle field
    "ball_edge": "#0B5FCC",
    "disk": "#D7DEE8",      # inset fallback interior
    "black": "#1A1A1A",
    "white": "#FFFFFF",
}

R_VALUE_COLUMNS = ("r_value", "R", "iso_dev_ratio")


def apply_publication_style(font_size: float = 10.5, axes_linewidth: float = 1.2) -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["font.size"] = font_size
    plt.rcParams["axes.linewidth"] = axes_linewidth
    plt.rcParams["legend.frameon"] = False


def finalize_figure(fig: plt.Figure, output_prefix: Path, dpi: int = 600) -> None:
    fig.savefig(output_prefix.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".png"), dpi=dpi, bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def r_series(events: pd.DataFrame) -> pd.Series:
    for col in R_VALUE_COLUMNS:
        if col in events.columns:
            return pd.to_numeric(events[col], errors="coerce").fillna(0.0)
    raise KeyError("No R / r_value column found in events.")


def classify_r(r_value: float, threshold: float) -> str:
    if r_value > threshold:
        return "Explosion"
    if r_value < -threshold:
        return "Implosion"
    return "Shear"


def load_microstructure(case_dir: Path) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    balls = hits = None
    # Prefer the explicitly named final-state export; fall back to peak or legacy final names.
    ball_candidates = [
        case_dir / "plotdata_ball_fields_final.csv",
        case_dir / "plotdata_ball_fields_peak.csv",
        case_dir / "plotdata_ball_fields.csv",
    ]
    hp = case_dir / "ae_events.csv"
    bp = next((p for p in ball_candidates if p.exists()), None)
    if bp is not None:
        balls = pd.read_csv(bp)
        balls[["x", "y", "radius"]] = balls[["x", "y", "radius"]] * MM
    if hp.exists():
        hits = pd.read_csv(hp)
        hits[["x", "y"]] = hits[["x", "y"]] * MM
        if "radius_model" in hits.columns:
            hits["radius_model"] = hits["radius_model"] * MM
    return balls, hits


def _is_tension(series: pd.Series) -> pd.Series:
    return series.astype(str).str.contains("tens", case=False, na=False)


def choose_events(events: pd.DataFrame, threshold: float, event_ids: list[int] | None, n_select: int = 6) -> pd.DataFrame:
    df = events.copy()
    df["source_class"] = r_series(df).map(lambda r: classify_r(float(r), threshold))
    if event_ids:
        chosen = df[df["event_id"].isin(event_ids)].copy()
        missing = sorted(set(event_ids) - set(chosen["event_id"].tolist()))
        if missing:
            raise ValueError(f"Requested event ids not found: {missing}")
        return chosen.set_index("event_id").loc[event_ids].reset_index()
    df["ncracks"] = df.get("hit_count", pd.Series(1, index=df.index)).astype(float)
    selected: list[pd.Series] = []
    used: set[int] = set()
    for cls in ["Explosion", "Implosion", "Shear"]:
        sub = df[(df["source_class"] == cls) & (~df["event_id"].isin(used))].copy()
        if sub.empty:
            continue
        sub["score"] = sub["ncracks"] * 2.0 + r_series(sub).abs() * 0.05
        pick = sub.sort_values("score", ascending=False).iloc[0]
        selected.append(pick)
        used.add(int(pick["event_id"]))
    while len(selected) < n_select:
        remaining = df[~df["event_id"].isin(used)].copy()
        if remaining.empty:
            break
        coords = np.array([[float(r["center_x_mm"]), float(r["center_y_mm"])] for r in selected]) if selected else None
        cand = remaining[["center_x_mm", "center_y_mm"]].to_numpy(float)
        spread = (np.min(np.sqrt(((cand[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2)), axis=1)
                  if coords is not None else np.ones(len(remaining)))
        remaining["score"] = remaining["ncracks"] * 1.6 + spread * 0.15 + r_series(remaining).abs() * 0.03
        pick = remaining.sort_values("score", ascending=False).iloc[0]
        selected.append(pick)
        used.add(int(pick["event_id"]))
    return pd.DataFrame(selected).head(n_select).reset_index(drop=True)


def principal_axes(row: pd.Series) -> list[tuple[np.ndarray, float]]:
    # In-plane moment tensor [[xx, xy], [xy, yy]] -> principal directions + relative magnitudes.
    mat = np.array([[float(row.get("mt_xx", 0.0)), float(row.get("mt_xy", 0.0))],
                    [float(row.get("mt_xy", 0.0)), float(row.get("mt_yy", 0.0))]], dtype=float)
    if not np.any(mat):
        return []
    vals, vecs = np.linalg.eigh(mat)
    order = np.argsort(np.abs(vals))[::-1]
    vals, vecs = vals[order], vecs[:, order]
    vmax = np.max(np.abs(vals)) or 1.0
    out = []
    for i in range(2):
        v = vecs[:, i]
        if np.linalg.norm(v) == 0:
            continue
        out.append((v / np.linalg.norm(v), float(vals[i]) / vmax))
    return out


def draw_balls(ax: plt.Axes, balls: pd.DataFrame, edge_lw: float = 0.15, clip=None) -> None:
    patches = [Circle((float(bx), float(by)), float(br)) for bx, by, br in
               zip(balls["x"], balls["y"], balls["radius"])]
    pc = PatchCollection(patches, facecolor=PALETTE["ball"], edgecolor=PALETTE["ball_edge"], linewidths=edge_lw, zorder=1)
    if clip is not None:
        pc.set_clip_path(clip)
    ax.add_collection(pc)


def draw_cracks(ax: plt.Axes, hits: pd.DataFrame, s_scale: float, clip=None) -> None:
    if hits.empty:
        return
    t = hits[_is_tension(hits["mode_label"])]
    s = hits[~_is_tension(hits["mode_label"])]
    for sub, color in ((t, PALETTE["tension"]), (s, PALETTE["shear"])):
        if sub.empty:
            continue
        if "radius_model" in sub.columns:
            size = np.clip(sub["radius_model"].to_numpy(float) * s_scale, 6, 120)
        else:
            size = 18
        sc = ax.scatter(sub["x"], sub["y"], s=size, marker="^", facecolors=color, edgecolors=color, linewidths=0.2, zorder=5)
        if clip is not None:
            sc.set_clip_path(clip)


def draw_inset(ax: plt.Axes, row: pd.Series, balls: pd.DataFrame | None, hits: pd.DataFrame | None,
               idx: int, window_half: float = 2.3) -> None:
    cx, cy = float(row["center_x_mm"]), float(row["center_y_mm"])
    ax.set_xlim(cx - window_half, cx + window_half)
    ax.set_ylim(cy - window_half, cy + window_half)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    ring = window_half * 0.92
    clip = Circle((cx, cy), ring, transform=ax.transData)

    if balls is not None and len(balls):
        win = balls[(balls["x"].between(cx - window_half, cx + window_half)) &
                    (balls["y"].between(cy - window_half, cy + window_half))]
        if len(win):
            draw_balls(ax, win, edge_lw=0.3, clip=clip)
    else:
        ax.add_patch(Circle((cx, cy), ring, facecolor=PALETTE["disk"], edgecolor="none", zorder=0))

    if hits is not None and len(hits):
        win = hits[(hits["x"].between(cx - window_half, cx + window_half)) &
                   (hits["y"].between(cy - window_half, cy + window_half))]
        draw_cracks(ax, win, s_scale=4.0e4, clip=clip)
    else:
        n_t = int(row.get("tension_hits", 0) or 0) or 1
        n_s = int(row.get("shear_hits", 0) or 0)
        total = n_t + n_s
        rng = np.random.default_rng(int(row["event_id"]))
        base = rng.uniform(0, 2 * np.pi)
        rad = 0.0 if total == 1 else window_half * 0.34
        marks = [PALETTE["tension"]] * n_t + [PALETTE["shear"]] * n_s
        for k, color in enumerate(marks):
            ang = base + 2 * np.pi * k / total
            ax.scatter([cx + rad * np.cos(ang)], [cy + rad * np.sin(ang)], s=150, marker="^",
                       facecolors=color, edgecolors=color, zorder=6)

    # green solid + blue dashed boundary, AE-event green circle, white principal-axis arrows
    ax.add_patch(Circle((cx, cy), ring, facecolor="none", edgecolor=PALETTE["green"], linewidth=1.6, zorder=4))
    ax.add_patch(Circle((cx, cy), window_half * 1.06, facecolor="none", edgecolor=PALETTE["blue_dash"],
                        linewidth=1.3, linestyle=(0, (5, 4)), zorder=4))
    ax.scatter([cx], [cy], s=210, facecolors="none", edgecolors=PALETTE["green"], linewidths=1.8, zorder=7)
    for vec, rel in principal_axes(row):
        length = window_half * (0.42 + 0.42 * abs(rel))
        dx, dy = float(vec[0]) * length, float(vec[1]) * length
        for sgn in (1, -1):
            ax.add_patch(FancyArrowPatch((cx, cy), (cx + sgn * dx, cy + sgn * dy), arrowstyle="-|>",
                                         mutation_scale=11, linewidth=1.7, color=PALETTE["white"], zorder=8))

    ax.text(0.02, 0.99, f"M= {float(row['moment_magnitude']):.2f}\nR= {float(row['r_value']):.2f}",
            transform=ax.transAxes, ha="left", va="top", fontsize=9.3, color=PALETTE["black"])
    ax.text(0.92, 1.0, str(idx + 1), transform=ax.transAxes, ha="center", va="bottom",
            fontsize=13, fontweight="bold", color=PALETTE["black"])


def build_figure(case_dir: Path, output_prefix: str, r_threshold: float, event_ids: list[int] | None) -> None:
    apply_publication_style()
    events = pd.read_csv(case_dir / "ae_clustered_events.csv")
    events["source_class"] = r_series(events).map(lambda r: classify_r(float(r), r_threshold))
    balls, hits = load_microstructure(case_dir)
    selected = choose_events(events, r_threshold, event_ids, n_select=6)

    print("[diagnostic] total events:", len(events),
          "| balls:", 0 if balls is None else len(balls),
          "| hits:", 0 if hits is None else len(hits))
    print("[diagnostic] class counts (R +/-%.0f):" % r_threshold)
    print(events["source_class"].value_counts().to_string())
    print("[diagnostic] selected events:")
    for i, row in selected.iterrows():
        print(f"  {i+1}: id={int(row['event_id'])} class={row['source_class']} M={float(row['moment_magnitude']):.2f} "
              f"R={float(row['r_value']):.2f} t={int(row.get('tension_hits',0))} s={int(row.get('shear_hits',0))}")

    fig = plt.figure(figsize=(10.5, 9.6), facecolor="white")

    # ---- central specimen map: real particle field + micro-cracks ----
    ax_c = fig.add_axes([0.30, 0.26, 0.40, 0.40])
    if balls is not None and len(balls):
        xmin, xmax = balls["x"].min(), balls["x"].max()
        ymin, ymax = balls["y"].min(), balls["y"].max()
        draw_balls(ax_c, balls, edge_lw=0.12)
    else:
        xmin, xmax = events["center_x_mm"].min(), events["center_x_mm"].max()
        ymin, ymax = events["center_y_mm"].min(), events["center_y_mm"].max()
        ax_c.set_facecolor(PALETTE["ball"])
    ax_c.set_xlim(xmin, xmax)
    ax_c.set_ylim(ymin, ymax)
    ax_c.set_aspect("equal", adjustable="box")
    ax_c.set_xticks([]); ax_c.set_yticks([])
    for sp in ax_c.spines.values():
        sp.set_visible(True); sp.set_linewidth(1.0); sp.set_color(PALETTE["black"])
    if hits is not None and len(hits):
        draw_cracks(ax_c, hits, s_scale=8.0e3)
    else:
        mode = events.get("dominant_mode", pd.Series("tension", index=events.index)).astype(str)
        ax_c.scatter(events[_is_tension(mode)]["center_x_mm"], events[_is_tension(mode)]["center_y_mm"],
                     s=14, c=PALETTE["tension"], edgecolors="none", zorder=4)

    for i, row in selected.iterrows():
        ax_c.add_patch(Circle((float(row["center_x_mm"]), float(row["center_y_mm"])), 0.9, facecolor="none",
                              edgecolor=PALETTE["black"], linewidth=2.0, zorder=8))
        ax_c.text(float(row["center_x_mm"]) + 1.4, float(row["center_y_mm"]) + 0.4, str(i + 1),
                  fontsize=12, fontweight="bold", color=PALETTE["black"], zorder=9)

    # ---- six insets ----
    inset_positions = [
        [0.15, 0.66, 0.22, 0.22],
        [0.59, 0.66, 0.22, 0.22],
        [0.02, 0.39, 0.22, 0.22],
        [0.76, 0.40, 0.22, 0.22],
        [0.11, 0.06, 0.22, 0.22],
        [0.57, 0.05, 0.22, 0.22],
    ]
    for idx, (pos, (_, row)) in enumerate(zip(inset_positions, selected.iterrows())):
        ax = fig.add_axes(pos)
        draw_inset(ax, row, balls, hits, idx)
        con = ConnectionPatch(
            xyA=(float(row["center_x_mm"]), float(row["center_y_mm"])), coordsA=ax_c.transData,
            xyB=(float(row["center_x_mm"]), float(row["center_y_mm"])), coordsB=ax.transData,
            arrowstyle="-", lw=1.0, linestyle=(0, (5, 4)), color=PALETTE["blue_dash"], zorder=1,
        )
        fig.add_artist(con)

    # ---- legend + caption ----
    handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor="none", markeredgecolor=PALETTE["green"],
                   markeredgewidth=1.6, markersize=10, label="AE event"),
        plt.Line2D([0], [0], marker="^", color="none", markerfacecolor=PALETTE["tension"], markeredgecolor=PALETTE["tension"],
                   markersize=10, label="micro-tension crack"),
        plt.Line2D([0], [0], marker="^", color="none", markerfacecolor=PALETTE["shear"], markeredgecolor=PALETTE["shear"],
                   markersize=10, label="micro-shear crack"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=3, frameon=False,
               columnspacing=1.6, handletextpad=0.5, fontsize=10)


    selected[["event_id", "center_x_mm", "center_y_mm", "moment_magnitude", "r_value", "source_class"]].to_csv(
        case_dir / f"{output_prefix}_selected_events.csv", index=False)
    finalize_figure(fig, case_dir / output_prefix, dpi=600)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fig.11 AE sources of different fracture types.")
    parser.add_argument("case_dir", nargs="?", default=".", type=Path)
    parser.add_argument("--output-prefix", default="fig11_ae_sources")
    parser.add_argument("--r-threshold", type=float, default=30.0,
                        help="|R| boundary: R>+thr Explosion, R<-thr Implosion, else Shear.")
    parser.add_argument("--event-ids", default="", help="Comma-separated event_id list to force the six insets.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    event_ids = [int(x) for x in args.event_ids.split(",") if x.strip()] if args.event_ids else None
    build_figure(args.case_dir, args.output_prefix, args.r_threshold, event_ids)


if __name__ == "__main__":
    main()