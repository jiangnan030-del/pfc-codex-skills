#!/usr/bin/env python3
"""Extract mineral phase fractions from a grayscale/RGB image.

This is a lightweight template. It prefers scikit-image when available and falls
back to quantile thresholds so the script remains readable on minimal systems.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def read_image(path: Path) -> np.ndarray:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Install Pillow to read images: python -m pip install pillow") from exc
    image = Image.open(path).convert("RGB")
    arr = np.asarray(image, dtype=float)
    return 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]


def thresholds_otsu(gray: np.ndarray, classes: int) -> np.ndarray:
    try:
        from skimage.filters import threshold_multiotsu
    except ImportError:
        return np.quantile(gray[np.isfinite(gray)], np.linspace(0, 1, classes + 1)[1:-1])
    return threshold_multiotsu(gray.astype(np.uint8), classes=classes)


def phase_fractions(gray: np.ndarray, thresholds: np.ndarray, names: list[str]) -> dict[str, float]:
    labels = np.digitize(gray, thresholds, right=False)
    total = float(labels.size)
    return {name: float(np.count_nonzero(labels == i) / total) for i, name in enumerate(names)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate mineral phase fractions from an image.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--classes", type=int, default=3)
    parser.add_argument("--names", default="mica,quartz,feldspar")
    parser.add_argument("--out", type=Path, default=Path("mineral_phase_fractions.json"))
    args = parser.parse_args()

    names = [x.strip() for x in args.names.split(",") if x.strip()]
    if len(names) != args.classes:
        raise SystemExit("--names count must match --classes")

    gray = read_image(args.image)
    thresholds = thresholds_otsu(gray, args.classes)
    fractions = phase_fractions(gray, thresholds, names)
    payload = {"thresholds": [float(x) for x in thresholds], "fractions": fractions}
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
