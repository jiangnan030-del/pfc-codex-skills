#!/usr/bin/env python3
"""Reproduce a cross-correlation time-delay demonstration figure.

The figure mirrors the textbook-style example where two similar waveforms x(t)
and y(t) have their maximum cross-correlation at tau = -20 microseconds,
indicating a 20 microsecond inter-signal delay.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def ricker_like(t_us: np.ndarray, center_us: float, width_us: float = 8.0, amp: float = 0.11) -> np.ndarray:
    """A compact wavelet for visually similar AE waveforms."""
    z = (t_us - center_us) / width_us
    main = amp * (1.0 - z**2) * np.exp(-0.5 * z**2)
    tail = 0.035 * np.sin(0.18 * (t_us - center_us)) * np.exp(-((t_us - center_us - 35.0) / 35.0) ** 2)
    precursor = 0.008 * np.sin(0.08 * t_us) * np.exp(-((t_us - 35.0) / 35.0) ** 2)
    return main + tail + precursor


def normalized_xcorr(x: np.ndarray, y: np.ndarray, dt_us: float) -> tuple[np.ndarray, np.ndarray]:
    """Return normalized cross-correlation R_xy(tau) with tau in microseconds.

    The sign convention follows R_xy(tau)=int x(t)y(t+tau)dt. If y(t) lags
    x(t) by 20 us, the maximum appears near tau=-20 us.
    """
    x0 = x - np.mean(x)
    y0 = y - np.mean(y)
    corr = np.correlate(x0, y0, mode="full") * dt_us / len(x0)
    scale = np.sqrt(np.sum(x0**2) * np.sum(y0**2)) / len(x0)
    corr = corr / scale * 0.2  # scale to match the textbook-style vertical range
    lags = np.arange(-len(x0) + 1, len(x0)) * dt_us
    return lags, corr


def make_figure(out: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Microsoft YaHei",
                "SimHei",
                "SimSun",
                "Noto Sans CJK SC",
                "Arial Unicode MS",
                "DejaVu Sans",
            ],
            "mathtext.fontset": "stix",
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )

    dt_us = 0.5
    t = np.arange(0.0, 200.0 + dt_us, dt_us)
    delay_us = 20.0
    x = ricker_like(t, center_us=92.0)
    y = ricker_like(t, center_us=92.0 + delay_us)
    lags, corr = normalized_xcorr(x, y, dt_us)
    mask = (lags >= -120.0) & (lags <= 100.0)
    peak_idx = np.argmax(corr[mask])
    peak_lag = lags[mask][peak_idx]
    peak_val = corr[mask][peak_idx]

    fig, axes = plt.subplots(2, 1, figsize=(4.8, 6.2), constrained_layout=False)
    fig.subplots_adjust(left=0.18, right=0.96, top=0.96, bottom=0.12, hspace=0.55)

    ax = axes[0]
    ax.plot(t, x, color="0.20", lw=1.5, label=r"$x(t)$")
    ax.plot(t, y, color="0.35", lw=1.5, ls=(0, (3, 2)), label=r"$y(t)$")
    ax.axhline(0.0, color="0.0", lw=0.9)
    ax.set_xlim(-5, 200)
    ax.set_ylim(-0.10, 0.15)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.set_yticks([-0.10, -0.05, 0.0, 0.05, 0.10, 0.15])
    ax.set_ylabel("电压/V", fontsize=13)
    ax.set_xlabel(r"$T/\mu s$", fontsize=13)
    ax.text(84, 0.095, r"$x(t)$", fontsize=12)
    ax.text(114, 0.095, r"$y(t)$", fontsize=12)
    ax.text(0.5, -0.28, "(a) 相似波形信号", transform=ax.transAxes, ha="center", va="top", fontsize=13)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="in", length=4, width=0.9)

    ax = axes[1]
    ax.plot(lags[mask], corr[mask], color="0.05", lw=1.5)
    ax.axhline(0.0, color="0.0", lw=0.9)
    ax.plot([peak_lag], [peak_val], marker="o", ms=3.5, color="0.05")
    ax.annotate(
        "A(-20,0.2)",
        xy=(peak_lag, peak_val),
        xytext=(-5, 0.195),
        textcoords="data",
        arrowprops={"arrowstyle": "-", "lw": 0.8, "color": "0.15"},
        fontsize=12,
    )
    ax.set_xlim(-125, 100)
    ax.set_ylim(-0.20, 0.22)
    ax.set_xticks([-100, 0, 100])
    ax.set_yticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    ax.set_ylabel("CCR函数值", fontsize=13)
    ax.set_xlabel(r"$T/\mu s$", fontsize=13)
    ax.text(0.5, -0.28, "(b) 波形互相关处理结果", transform=ax.transAxes, ha="center", va="top", fontsize=13)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="in", length=4, width=0.9)

    fig.text(0.5, 0.02, "图 6.3.4  波形信号及互相关处理结果", ha="center", fontsize=13)
    fig.savefig(out, dpi=600)
    if out.suffix.lower() not in {".svg", ".pdf"}:
        fig.savefig(out.with_suffix(".svg"))
        fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Draw a cross-correlation time-delay demonstration figure.")
    parser.add_argument("--out", type=Path, default=Path("cross_correlation_delay_demo.png"))
    args = parser.parse_args()
    make_figure(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
