"""Radial crack density, 5-degree dip bins, and tensile/shear statistics.
CSV columns: x,y,z,nx,ny,nz,mode[,cycle]. Coordinates are metres.
"""
import csv
import math

H_MM = 100.0
R_MM = 25.0
DR_MM = 5.0
DA_DEG = 5.0


def load_csv(path):
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            out.append({
                "pos": tuple(float(r[k]) for k in ("x", "y", "z")),
                "normal": tuple(float(r[k]) for k in ("nx", "ny", "nz")),
                "mode": r["mode"].strip().lower(),
            })
    return out


def radial_density(cracks, height_mm=H_MM, radius_mm=R_MM, band_mm=DR_MM):
    """Eqs. 5-6: rho_c=N/V; V=pi*H*((R+dR)^2-R^2)."""
    nb = int(math.ceil(radius_mm / band_mm))
    counts = [0] * nb
    for c in cracks:
        x, y, _ = c["pos"]
        r_mm = 1000.0 * math.hypot(x, y)
        counts[min(int(r_mm / band_mm), nb - 1)] += 1
    rows = []
    for i, n in enumerate(counts):
        r0, r1 = i * band_mm, min((i + 1) * band_mm, radius_mm)
        v_m3 = math.pi * height_mm * (r1*r1-r0*r0) * 1e-9
        rows.append((r0, r1, n, n / v_m3))
    return rows


def dip_bins(cracks, width=DA_DEG):
    """Angle of crack plane to specimen axis, folded to 0-90 degrees."""
    nb = int(90 / width)
    counts = [0] * nb
    for c in cracks:
        nx, ny, nz = c["normal"]
        norm = math.sqrt(nx*nx + ny*ny + nz*nz)
        if norm == 0:
            continue
        angle = math.degrees(math.asin(min(1.0, abs(nz) / norm)))
        counts[min(int(angle / width), nb - 1)] += 1
    total = sum(counts) or 1
    return [(i*width, (i+1)*width, n, n/total) for i, n in enumerate(counts)]


def failure_modes(cracks):
    total = len(cracks)
    tensile = sum(c["mode"].startswith("ten") for c in cracks)
    shear = total - tensile
    den = total or 1
    return tensile, shear, tensile/den, shear/den


def report(cracks):
    print("radial density (cracks/m3)")
    for a, b, n, rho in radial_density(cracks):
        print(f"{a:4.0f}-{b:4.0f} mm  N={n:6d}  rho={rho:.3e}")
    print("dip-angle distribution")
    for a, b, n, p in dip_bins(cracks):
        print(f"{a:3.0f}-{b:3.0f} deg  N={n:6d}  {100*p:6.2f}%")
    nt, ns, pt, ps = failure_modes(cracks)
    print(f"tensile={nt} ({100*pt:.2f}%), shear={ns} ({100*ps:.2f}%)")


if __name__ == "__main__":
    import sys
    report(load_csv(sys.argv[1]))
