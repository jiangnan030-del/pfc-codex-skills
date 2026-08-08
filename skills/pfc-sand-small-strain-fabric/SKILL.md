---
name: pfc-sand-small-strain-fabric
description: >
  Child skill of pfc-workflow for PFC3D studies of sand small-strain shear
  modulus (G0/Gmax). Build spherical and ellipsoidal clumps, prescribe
  major-axis fabric, install Hertz-Mindlin contacts, run constant-volume
  small-amplitude cyclic tests, and calculate G0, fabric tensors and
  mechanical coordination. Uses a Build-Material-Test-Observe-Runner
  architecture and the ssf_ naming namespace.
version: 1.1.0
requires: ["pfc-mcp"]
related_skills:
  - pfc-workflow
  - pfc-basics
  - pfc-contact-models
  - pfc-modeling-techniques
  - pfc-servo-calibration
  - pfc-postprocessing
  - pfc-python
---

# PFC Sand Small-Strain Fabric Skill

## Parent Skill Relationship

This specialist child implements `pfc-workflow` phases P1-P7 for sand G0:

- P1: define shape, void ratio, fabric, pressure, angle and seeds.
- P2: build clump templates and controlled orientation fabric.
- P3: install/calibrate Hertz-Mindlin contacts and consolidate.
- P4: run one declared constant-volume small-strain loop per case.
- P5: calculate G0, damping, fabric, coordination and fitted laws.
- P6/P7: verify amplitude/rate/seed/resolution independence and deliver a manifest.

## When To Use

Use for G0/Gmax, small-strain sand stiffness, ellipsoidal grains, fabric
anisotropy, directional modulus, cyclic-triaxial DEM, fabric tensors,
mechanical coordination or G0-void-ratio relationships.

This is not a complete liquefaction model: constant volume is only a mechanical
undrained analogue; explicit pore-pressure generation needs additional coupling.

## Architecture Contract

All PFC code follows five layers:

| Layer | Entry | Owns | Must not do |
|---|---|---|---|
| Build | `build/build_fabric_specimen.p3dat` | templates, orientation, packing, compaction | cyclic test or final G0 |
| Material | `material/install_hertz.p3dat` | Hertz install, friction, equilibrium, consolidation | direction cases/history |
| Test | `test/run_small_strain_cyclic.p3dat` | one declared angle/amplitude test | rebuild or change shape |
| Observe | `lib/ssf_*.fis` | metrics, control, histories, stop rules | restore/save/long solve |
| Runner | `run/run_fabric_suite.p3dat` | dependency checks, case routing, log/save/manifest | duplicate equations |

Each direction case starts from the same material-ready save. Shared libraries
must be idempotent: setup/reset removes prior callbacks and clears state.

## Naming Contract

Namespace: `ssf` (sand small-strain fabric).

- FISH functions: `ssf_verb_noun`, e.g. `ssf_compute_fabric`.
- Configuration globals: `ssf_cfg_*`.
- Runtime state: `ssf_state_*`.
- Derived outputs: `ssf_out_*`.
- Walls: `ssf_wall_xmin/xmax/ymin/ymax/zmin/zmax`; never depend on wall IDs.
- Groups: `ssf:grain`, `ssf:boundary`, slot `ssf_role`.
- Histories: `ssf/cyclic/axial_strain`, `ssf/cyclic/deviator_stress`, etc.
- Executable command files: `.p3dat`; 3D FISH libraries: `.p3fis`;
  truly dimension-independent libraries only: `.fis`.

Case ID:

```text
rm20_ani2_a045_e065_p100_s10001
```

It encodes aspect ratio, Ani level, angle, void ratio, pressure (kPa) and seed.

Save name:

```text
ssf_{dim}_{material}_{stage}_{case_id}
```

Canonical stages:

```text
ssf_3d_prep_compacted_{case_id}
ssf_3d_hertz_material_ready_{case_id}
ssf_3d_hertz_rotated_{case_id}
ssf_3d_hertz_cyclic_done_{case_id}
```

## Physical Mapping

| Physical item | PFC representation | Control/output |
|---|---|---|
| Grain shape | sphere or 5/7/9-pebble ellipsoidal clump | rm=1.0/1.5/2.0/2.5 |
| Depositional fabric | major-axis orientation distribution | Ani I/II/III |
| Fabric intensity | contact-normal fabric tensor | Rij, aij, ad |
| Load-bearing skeleton | mechanical coordination | Zm |
| Quartz contact | Hertz-Mindlin | Gp, nu, friction |
| Undrained analogue | axial strain + zero-volume lateral control | volume residual |
| Direction effect | rotate material/loading coordinates | 0/45/90 degrees |
| Small-strain stiffness | one-loop stress/strain amplitude | G0 |

## Core Equations

```text
rm = la/lb
Rij = mean(n_i*n_j)
aij = (15/2)*(Rij-deltaij/3)
ad  = sqrt((3/2)*sum(aij*aij))
Zm  = (2*Nc-N1)/(Np-N1-N0)
G0  = DeltaSigma/gamma
G0  = A*exp(-a*e)*(p0/pa)^n
```

Use the same amplitude convention for stress and strain.

## Operating Rules

1. Separate shape, density, fabric, pressure and direction in the case matrix.
2. Keep Build, Material, Test, Observe and Runner responsibilities independent.
3. Use the `ssf_` namespace and named walls/groups/histories everywhere.
4. Compare G0 only at matched void ratio, pressure and approximately matched Zm.
5. Demonstrate a low-strain plateau and quasi-static energy response.
6. In constant-volume mode, use lateral DOFs only for volume control; report
   mean-pressure drift instead of applying a competing pressure servo.
7. Export target and achieved orientations, not only a rendered plot.
8. Write every case to `output/manifest.csv` with version, seed and code hash.
9. Verify target-version syntax through `pfc-mcp` before running.

## Pipeline

```text
Runner defines case_id
 -> Build creates templates/fabric and compacted save
 -> Material installs Hertz and creates material-ready save
 -> Observe validates ad and Zm
 -> Test restores material-ready, rotates and runs one loop
 -> Observe calculates G0/damping/energy/fabric change
 -> Runner writes cyclic-done save, log and manifest
 -> post-processing fits G0-e-p and creates orientation plots
```

## Standard Operating Procedure

1. Read `config/cases.yaml`; generate one unique case ID.
2. Build sphere and 5/7/9-pebble templates for rm=1.5/2.0/2.5.
3. Check volume, centroid, inertia axes and equivalent-diameter consistency.
4. Sample Ani I/II/III orientations and compact to target void ratio.
5. Install Hertz-Mindlin and consolidate to the declared initial pressure.
6. Calculate ad and Zm; stop the case if initial-state tolerances fail.
7. Restore material-ready independently for every 0/45/90-degree case.
8. Run one complete 5 Hz loop at axial strain half-amplitude 3.0e-6.
9. Calculate G0, damping, pressure drift, volume residual and energy ratio.
10. Repeat amplitude/frequency/damping/resolution/seed checks and write manifest.

## Reference Starting Values

| Parameter | Value |
|---|---:|
| Grain shear modulus | 18 GPa |
| Grain Poisson ratio | 0.15 |
| Density | 2650 kg/m3 |
| Grain friction | 0.5 |
| Wall friction | 0.0 |
| Preparation local damping | 0.7 |
| Cyclic axial-strain half-amplitude | 3.0e-6 |
| Frequency | 5 Hz |

These are reproduction starting points, not universal Toyoura-sand calibration.

## Observe Interface

```text
ssf_reset_case_state()
ssf_assert_dependencies()
ssf_sample_major_axis(ani_level)
ssf_compute_fabric()       -> ssf_out_rij/aij/ad
ssf_compute_coordination() -> ssf_out_zm
ssf_setup_measurement()
ssf_apply_cyclic_control()
ssf_should_halt()
ssf_finalize_case()
```

## Runner Manifest

Each row records:

```text
case_id,dim,material,shape,ani,void_ratio,pressure,angle,seed,
input_save,output_save,G0,damping,ad_before,ad_after,Zm,
volume_residual,pressure_drift,energy_ratio,status,elapsed,code_hash
```

## Expected Trends

- G0 decreases with void ratio; the source combined fit is about R2=0.94.
- Ellipsoidal specimens are generally stiffer than spherical ones.
- For one shape/state, stronger fabric anisotropy lowers G0.
- The fabric effect increases at larger void ratio.
- At matched fabric, G0 generally increases from 0 to 45 to 90 degrees.
- Strong-fabric 90-degree cases may not obey one global exponential G0-e law.

## V&V Gate

Verify clump geometry, achieved orientation, ad/Zm, particle resolution,
timestep, frequency, damping, random seeds, kinetic/strain-energy ratio,
volume residual and fabric change over the loop. Validate against bender-element,
resonant-column or small-strain cyclic-triaxial measurements where available.

## Output Contract

Deliver:

- `config/cases.yaml` plus `config/ssf_defaults.fis`;
- canonical compacted/material-ready/rotated/cyclic-done saves;
- named `ssf/cyclic/*` and `ssf/state/*` histories;
- loop data, G0, damping, void ratio, pressure drift, ad, Zm and plots;
- `output/manifest.csv`, logs, code hash, V&V evidence and exceptions.

## Local Contents

- `config/`: defaults and case matrix.
- `build/`: template/fabric specimen creation.
- `material/`: Hertz-Mindlin installation/consolidation.
- `test/`: one declared small-strain cyclic test.
- `lib/`: contracts, fabric, servo and measurement interfaces.
- `run/`: reproducible suite runner.
- `post/`: G0/fabric fitting and orientation plotting.
- `references/`: equations, calibration cautions and expected trends.
- `examples/`: run order and checks.
- `output/`: logs, saves, histories, figures and manifest schema.
