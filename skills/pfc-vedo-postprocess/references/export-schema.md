# PFC Export Schema for vedo

Preferred snapshot format: one `.npz` per time step, for example `pfc_step000.npz`.

## Particle arrays

- `pos`: `(N, 3)` float, particle center coordinates. For PFC2D, use `z=0`.
- `rad`: `(N,)` float, particle radius.
- `disp`: `(N, 3)` float, displacement vector.
- `vel`: `(N, 3)` float, velocity vector.
- `grp`: `(N,)` string or integer, material/group label.

## Contact arrays

- `c_p1`: `(M, 3)` float, endpoint 1 or ball-center 1.
- `c_p2`: `(M, 3)` float, endpoint 2 or ball-center 2.
- `c_fn`: `(M,)` float, signed normal force. Confirm sign convention before labeling compression/tension.
- `c_bonded`: `(M,)` integer/bool, whether the contact is bonded.

## Crack arrays

- `cr_pos`: `(K, 3)` float, crack center.
- `cr_nrm`: `(K, 3)` float, crack-plane normal. Normalize before rendering.
- `cr_size`: `(K,)` float, representative crack diameter or radius depending on export convention.
- `cr_type`: `(K,)` integer/string, recommended `0=tensile`, `1=shear`.

## Defensive loading

Scripts should tolerate missing optional arrays and empty contacts/cracks:

```python
import numpy as np

d = np.load(path, allow_pickle=True)
pos = d['pos']
if pos.shape[1] == 2:
    pos = np.c_[pos, np.zeros(len(pos))]
rad = d.get('rad', np.full(len(pos), 1.0))
```
