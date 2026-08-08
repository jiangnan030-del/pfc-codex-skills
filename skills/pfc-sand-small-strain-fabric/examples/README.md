# pfc-sand-small-strain-fabric example

Reference architecture: **Build -> Material -> Test -> Observe -> Runner**.
Verify all PFC commands, clump orientation, Hertz properties, wall reactions
and callback syntax against the target release before execution.

## Run order

1. Select a row in `../config/cases.yaml`; load `../config/ssf_defaults.fis`.
2. Run `../build/build_fabric_specimen.p3dat` and validate template geometry.
3. Confirm achieved Ani fabric and save `ssf_3d_prep_compacted_{case_id}`.
4. Run `../material/install_hertz.p3dat`; consolidate and validate ad/Zm.
5. Save `ssf_3d_hertz_material_ready_{case_id}`.
6. For every angle, restore that same material-ready state independently.
7. Run `../test/run_small_strain_cyclic.p3dat` for one complete loop.
8. Export named `ssf/cyclic/*` histories, then run:

```bash
python ../post/fabric_g0_post.py --loop output/histories/loop.csv
python ../post/plot_orientation.py output/histories/contact_normals.csv
```

For batch execution use `../run/run_fabric_suite.p3dat`; it owns logging,
canonical saves and `output/manifest.csv`.

## Naming checks

- FISH: `ssf_verb_noun`; config: `ssf_cfg_*`; state: `ssf_state_*`.
- Walls: `ssf_wall_*`; group slot: `ssf_role`; histories: `ssf/cyclic/*`.
- Case example: `rm20_ani2_a045_e065_p100_s10001`.
- Save format: `ssf_{dim}_{material}_{stage}_{case_id}`.
- Do not use numeric wall/history IDs or state inherited from another angle.

## Template and fabric checks

- Aspect ratios: 1.0, 1.5, 2.0 and 2.5; ellipsoids use 5/7/9 pebbles.
- Compare equivalent-diameter distributions, not equal major-axis lengths.
- Record volume, centroid, inertia axis, target/achieved orientation and seed.
- Within one shape family, Ani should change ad strongly while Zm remains close.

Paper-style `ad / Zm` checks:

| rm | Ani I | Ani II | Ani III |
|---:|---:|---:|---:|
| 1.5 | 0.0250 / 8.430 | 0.3166 / 8.392 | 0.4977 / 8.421 |
| 2.0 | 0.0294 / 8.596 | 0.4058 / 8.651 | 0.6975 / 8.644 |
| 2.5 | 0.0333 / 8.691 | 0.5152 / 8.686 | 0.9165 / 8.703 |

## Small-strain checks

- Use one half-amplitude convention for stress and shear strain.
- Scan 1e-7 to 3e-6 and demonstrate the low-strain modulus plateau.
- Check kinetic/strain-energy ratio, volume residual and pressure drift.
- Do not combine constant-volume lateral control with a competing pressure servo.
- Confirm one loop does not materially change ad, Zm or void ratio.

## Scope

Constant volume is a mechanical undrained analogue, not an explicit
pore-pressure or validated cyclic-liquefaction model.
