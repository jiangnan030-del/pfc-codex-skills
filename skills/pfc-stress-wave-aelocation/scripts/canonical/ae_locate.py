#!/usr/bin/env python3
"""Velocity-free 2D AE source localization with cross-correlation delays."""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Iterable

import numpy as np


def xcorr_delay(x: np.ndarray, y: np.ndarray, dt: float, normalize: bool = True) -> tuple[float, float]:
    x = np.asarray(x, dtype=float) - np.nanmean(x)
    y = np.asarray(y, dtype=float) - np.nanmean(y)
    if normalize:
        sx = np.nanstd(x) or 1.0
        sy = np.nanstd(y) or 1.0
        x = x / sx
        y = y / sy
    corr = np.correlate(y, x, mode="full")
    lags = np.arange(-len(x) + 1, len(x))
    i = int(np.nanargmax(corr))
    delta = 0.0
    if 0 < i < len(corr) - 1:
        denom = corr[i - 1] - 2.0 * corr[i] + corr[i + 1]
        if abs(denom) > 1.0e-20:
            delta = 0.5 * (corr[i - 1] - corr[i + 1]) / denom
    lag = (lags[i] + delta) * dt
    peak = float(corr[i] / max(len(x), 1))
    return float(lag), peak


def bearing_from_triangle(ref: Iterable[float], s2: Iterable[float], s3: Iterable[float], t21: float, t31: float) -> float:
    ref = np.array(ref, dtype=float)
    v2 = np.array(s2, dtype=float) - ref
    v3 = np.array(s3, dtype=float) - ref
    a = float(np.linalg.norm(v2))
    b = float(np.linalg.norm(v3))
    alpha = float(np.arctan2(v2[1], v2[0]))
    beta = float(np.arctan2(v3[1], v3[0]))
    num = b * t21 * np.cos(beta) - a * t31 * np.cos(alpha)
    den = a * t31 * np.sin(alpha) - b * t21 * np.sin(beta)
    return float(np.arctan2(num, den))


def intersect_rays(p1: Iterable[float], theta1: float, p2: Iterable[float], theta2: float, tol: float = 1e-8) -> tuple[np.ndarray | None, float]:
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    d1 = np.array([np.cos(theta1), np.sin(theta1)])
    d2 = np.array([np.cos(theta2), np.sin(theta2)])
    cross = float(d1[0] * d2[1] - d1[1] * d2[0])
    if abs(cross) < tol:
        return None, abs(cross)
    mat = np.column_stack([d1, -d2])
    st = np.linalg.solve(mat, p2 - p1)
    return p1 + st[0] * d1, abs(cross)


def locate_from_clusters(clusters: list[dict], min_cross: float = 1e-3) -> dict:
    bearings = []
    for c in clusters:
        theta = bearing_from_triangle(c["ref"], c["s2"], c["s3"], c["t21"], c["t31"])
        bearings.append({"name": c.get("name", f"C{len(bearings)+1}"), "ref": c["ref"], "theta": theta})
    estimates = []
    for a, b in combinations(bearings, 2):
        point, quality = intersect_rays(a["ref"], a["theta"], b["ref"], b["theta"], tol=min_cross)
        if point is not None:
            estimates.append({"clusters": [a["name"], b["name"]], "x": float(point[0]), "y": float(point[1]), "quality": quality})
    if estimates:
        pts = np.array([[e["x"], e["y"]] for e in estimates])
        final = np.median(pts, axis=0)
    else:
        final = np.array([np.nan, np.nan])
    return {"bearings": bearings, "estimates": estimates, "final": {"x": float(final[0]), "y": float(final[1])}}


def main() -> None:
    parser = argparse.ArgumentParser(description="Velocity-free AE source localization from cluster time delays.")
    parser.add_argument("--clusters", type=Path, required=True, help="JSON file with cluster refs, sensors, and t21/t31 delays.")
    parser.add_argument("--out", type=Path, default=Path("ae_location_result.json"))
    args = parser.parse_args()
    clusters = json.loads(args.clusters.read_text(encoding="utf-8"))["clusters"]
    result = locate_from_clusters(clusters)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
