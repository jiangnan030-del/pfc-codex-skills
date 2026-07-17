"""Export a PFC state to a NumPy snapshot for vedo post-processing.

Run inside PFC's Python environment. PFC API names vary by version, so verify
contact force, bond, and crack accessors before using this in production.
"""
import numpy as np
import itasca as it


def _as_xyz(v):
    arr = np.asarray(v, dtype=float)
    if arr.shape[0] == 2:
        arr = np.r_[arr, 0.0]
    return arr


def export_state(tag="step000", out_prefix="pfc"):
    balls = list(it.ball.list())
    pos = np.array([_as_xyz(b.pos()) for b in balls])
    rad = np.array([b.radius() for b in balls], dtype=float)
    disp = np.array([_as_xyz(b.disp()) for b in balls])
    vel = np.array([_as_xyz(b.vel()) for b in balls])
    grp = np.array([b.group() for b in balls], dtype=object)

    c_p1, c_p2, c_fn, c_bonded = [], [], [], []
    for c in it.contact.list():
        if hasattr(c, "active") and not c.active():
            continue
        c_p1.append(_as_xyz(c.end1().pos()))
        c_p2.append(_as_xyz(c.end2().pos()))
        c_fn.append(c.normal_force())
        c_bonded.append(1 if getattr(c, "bonded", lambda: False)() else 0)

    cr_pos, cr_nrm, cr_size, cr_type = [], [], [], []
    if hasattr(it, "crack"):
        for ck in it.crack.list():
            cr_pos.append(_as_xyz(ck.pos()))
            n = _as_xyz(ck.normal())
            cr_nrm.append(n / (np.linalg.norm(n) + 1e-12))
            cr_size.append(ck.size())
            cr_type.append(0 if str(ck.type()).lower().startswith("tens") else 1)

    np.savez(
        f"{out_prefix}_{tag}.npz",
        pos=pos,
        rad=rad,
        disp=disp,
        vel=vel,
        grp=grp,
        c_p1=np.asarray(c_p1),
        c_p2=np.asarray(c_p2),
        c_fn=np.asarray(c_fn),
        c_bonded=np.asarray(c_bonded),
        cr_pos=np.asarray(cr_pos),
        cr_nrm=np.asarray(cr_nrm),
        cr_size=np.asarray(cr_size),
        cr_type=np.asarray(cr_type),
    )


if __name__ == "__main__":
    export_state()
