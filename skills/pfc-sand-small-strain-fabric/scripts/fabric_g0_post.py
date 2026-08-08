"""Post-process G0, contact fabric and mechanical coordination.

CSV inputs:
  loop.csv: strain,stress[,volume_strain,mean_pressure]
  contacts.csv: nx,ny,nz,grain1,grain2
Use physical grain/clump IDs, not pebble IDs, for coordination.
"""
import csv
import math
import numpy as np


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def loop_metrics(rows):
    strain = np.array([float(r["strain"]) for r in rows])
    stress = np.array([float(r["stress"]) for r in rows])
    de = 0.5 * (strain.max() - strain.min())
    ds = 0.5 * (stress.max() - stress.min())
    g0 = ds / de
    # Polygon integral: energy dissipated per unit volume in one loop.
    area = abs(np.trapz(stress, strain))
    return {"strain_half_amplitude": de, "stress_half_amplitude": ds,
            "G0": g0, "loop_area": area}


def fabric_metrics(rows):
    normals = np.array([[float(r[k]) for k in ("nx", "ny", "nz")]
                        for r in rows], dtype=float)
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    rij = np.einsum("ni,nj->ij", normals, normals) / len(normals)
    aij = 7.5 * (rij - np.eye(3) / 3.0)
    ad = math.sqrt(1.5 * float(np.sum(aij * aij)))
    eigval, eigvec = np.linalg.eigh(rij)
    principal = eigvec[:, np.argmax(eigval)]
    return {"Rij": rij, "aij": aij, "ad": ad,
            "principal_direction": principal}


def mechanical_coordination(rows):
    neighbours = {}
    for r in rows:
        a, b = r["grain1"], r["grain2"]
        neighbours.setdefault(a, set()).add(b)
        neighbours.setdefault(b, set()).add(a)
    degree = np.array([len(v) for v in neighbours.values()], dtype=int)
    npart = len(degree)
    n0 = int(np.sum(degree == 0))
    n1 = int(np.sum(degree == 1))
    nc = int(degree.sum() // 2)
    den = npart - n1 - n0
    return (2 * nc - n1) / den if den else float("nan")


def fit_g0_void_ratio(void_ratio, g0):
    """Fit G0=A*exp(-a*e) at one pressure; returns A, a, R2."""
    e = np.asarray(void_ratio, dtype=float)
    y = np.log(np.asarray(g0, dtype=float))
    slope, intercept = np.polyfit(e, y, 1)
    pred = intercept + slope * e
    r2 = 1.0 - np.sum((y-pred)**2) / np.sum((y-y.mean())**2)
    return {"A": math.exp(intercept), "a": -slope, "R2_log": r2}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--loop", required=True)
    p.add_argument("--contacts", required=True)
    args = p.parse_args()
    loop = read_csv(args.loop)
    contacts = read_csv(args.contacts)
    print(loop_metrics(loop))
    fm = fabric_metrics(contacts)
    print("ad=", fm["ad"], "principal=", fm["principal_direction"])
    print("Zm=", mechanical_coordination(contacts))
