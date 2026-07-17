import argparse
import numpy as np
from vedo import Spheres, Plotter


def xyz(a):
    a = np.asarray(a, dtype=float)
    return np.c_[a, np.zeros(len(a))] if a.ndim == 2 and a.shape[1] == 2 else a


def main():
    ap = argparse.ArgumentParser(description="Render PFC particles colored by displacement magnitude.")
    ap.add_argument("snapshot")
    ap.add_argument("--out", default="balls_disp.png")
    ap.add_argument("--sample", type=int, default=1)
    ap.add_argument("--res", type=int, default=12)
    args = ap.parse_args()

    d = np.load(args.snapshot, allow_pickle=True)
    sl = slice(None, None, max(args.sample, 1))
    pos = xyz(d["pos"])[sl]
    rad = d.get("rad", np.ones(len(d["pos"])))[sl]
    disp = xyz(d.get("disp", np.zeros_like(d["pos"])))[sl]
    dmag = np.linalg.norm(disp, axis=1)

    balls = Spheres(pos, r=rad, res=args.res)
    balls.cmap("viridis", dmag, on="points").add_scalarbar("|disp| (m)")
    plt = Plotter(axes=1, bg="white", title="PFC particles colored by displacement")
    plt.show(balls, viewup="z")
    plt.screenshot(args.out)
    plt.close()


if __name__ == "__main__":
    main()
