# pfc-sand-small-strain-fabric example

The PFC files are reference skeletons. Verify clump orientation, Hertz contact properties, wall reactions and callback syntax against the target PFC version before execution.

## Run order

1. Set the case in `../templates/params.yaml`.
2. Run `../scripts/make_ellipsoid_clumps.p3dat` and validate each clump template.
3. Load `../scripts/prepare_fabric.p3fis`, assign Ani I/II/III orientations, compact and calculate achieved fabric.
4. Consolidate to the configured pressure and save `consolidated`.
5. Rotate the specimen/loading axes to 0, 45 or 90 degrees and save `rotated_angle`.
6. Run `../scripts/cyclic_small_strain.p3fis` for one complete constant-volume loop.
7. Export loop/contact CSV files and run:

```bash
python ../scripts/fabric_g0_post.py --loop loop.csv --contacts contacts.csv
```

## Template checks

- Measured envelope aspect ratios are 1.0, 1.5, 2.0 and 2.5.
- Ellipsoid templates contain 5, 7 and 9 pebbles as configured.
- Shapes use the same equivalent-diameter distribution, not the same major-axis length.
- Volume, centroid and principal inertia direction are recorded.

## Fabric checks

Expected paper-style targets (`ad / Zm`):

| rm | Ani I | Ani II | Ani III |
|---:|---:|---:|---:|
| 1.5 | 0.0250 / 8.430 | 0.3166 / 8.392 | 0.4977 / 8.421 |
| 2.0 | 0.0294 / 8.596 | 0.4058 / 8.651 | 0.6975 / 8.644 |
| 2.5 | 0.0333 / 8.691 | 0.5152 / 8.686 | 0.9165 / 8.703 |

Treat these as reproduction checks, not universal targets. The key controlled signature is strong `ad` change with small `Zm` change within one shape family.

## Small-strain checks

- Use a consistent half-amplitude definition for stress and shear strain.
- Scan amplitudes from `1e-7` to `3e-6` and demonstrate a low-strain modulus plateau.
- Check kinetic/strain-energy ratio, volume-strain residual and mean-pressure drift.
- Repeat with lower cyclic damping and frequency to exclude numerical-rate effects.
- Confirm one loop does not materially change `ad`, `Zm` or void ratio.

## Expected trends

- G0 decreases as void ratio increases; the source reports an overall fit near `R2=0.94`.
- Ellipsoidal specimens are stiffer than spherical specimens at comparable density.
- Stronger fabric anisotropy lowers G0 for the same shape/state.
- The fabric effect grows at larger void ratio.
- G0 generally increases from 0 to 45 to 90 degree loading.
- Strong-fabric 90-degree data may not follow one global exponential G0-void-ratio law.

## Scope limits

Constant volume is only a mechanical analogue of undrained response. This example does not explicitly calculate pore pressure and is not a validated cyclic-liquefaction model.
