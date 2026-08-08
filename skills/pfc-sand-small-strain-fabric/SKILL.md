---
name: pfc-sand-small-strain-fabric
description: >
  Child skill of pfc-workflow for PFC3D studies of sand small-strain shear
  modulus (G0/Gmax). Build spherical and ellipsoidal clumps, prescribe
  major-axis orientation distributions, use Hertz-Mindlin contacts, run
  constant-volume small-amplitude cyclic triaxial tests, and calculate G0,
  fabric tensors and mechanical coordination number. Use for particle-shape
  effects, fabric anisotropy, directional stiffness, cyclic triaxial DEM,
  bender-element interpretation, or G0-void-ratio relationships.
version: 1.0.0
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

This is a specialist child of `pfc-workflow`:

- P1: define particle shape, void ratio, fabric, pressure and loading direction.
- P2: create spherical/ellipsoidal clumps and controlled orientation fabric.
- P3: calibrate Hertz-Mindlin contact response and initial state.
- P4: consolidate, rotate the material/loading axes and run one small-strain loop.
- P5: calculate G0, fabric anisotropy, mechanical coordination and fitted laws.
- P6/P7: verify amplitude/rate/seed/resolution independence and deliver results.

Return to `pfc-workflow` for generic project planning, batch execution, V&V and reporting.

## When To Use

Use this skill when the task mentions:

- small-strain or maximum shear modulus (`G0`, `Gmax`) of sand;
- particle shape, elongation, ellipsoidal grains or clumps;
- depositional/fabric anisotropy or directional stiffness;
- constant-volume/undrained small-amplitude cyclic triaxial DEM;
- fabric tensor, contact-normal distribution or mechanical coordination number;
- the coupling among void ratio, pressure, fabric and loading direction.

Do not use it as a complete liquefaction model: pore-pressure generation and cyclic strength require additional validation or fluid coupling.

## Physical Picture -> Numerical Mapping

| Physical item | PFC representation | Main control/output |
|---|---|---|
| Grain shape | sphere or 5/7/9-pebble ellipsoidal clump | aspect ratio `rm=1.0/1.5/2.0/2.5` |
| Depositional fabric | prescribed major-axis orientation distribution | Ani I/II/III |
| Fabric intensity | contact-normal fabric tensor | `Rij`, `aij`, `ad` |
| Load-bearing skeleton | mechanical coordination number | `Zm` |
| Quartz-sand contact | Hertz-Mindlin contact | `Gp`, `nu`, friction |
| Undrained equivalence | axial strain control + zero-volume lateral control | volume-strain residual |
| Direction effect | rotate specimen or loading coordinates | 0/45/90 degrees |
| Small-strain stiffness | stress/strain amplitude of one loop | `G0 = DeltaSigma/gamma` |

## Core Equations

Particle aspect ratio:

```text
rm = la / lb
```

Contact-normal fabric tensor and anisotropy invariant:

```text
Rij = (1/Nc) * sum(n_i * n_j)
aij = (15/2) * (Rij - deltaij/3)
ad  = sqrt((3/2) * aij * aij)
```

Mechanical coordination number:

```text
Zm = (2*Nc - N1) / (Np - N1 - N0)
```

Small-strain modulus and the Hardin-Richart-style fit:

```text
G0 = DeltaSigma / gamma
G0 = A * exp(-a*e) * (p0/pa)^n
```

Use the same amplitude convention for stress and strain (half amplitude or peak-to-peak, never mixed).

## Operating Rules

1. Separate shape, density, fabric and direction with a controlled case matrix.
2. Compare G0 only at matched void ratio, pressure and approximately matched `Zm`.
3. Verify a low-strain modulus plateau; do not assume one imposed amplitude is the strict Gmax limit.
4. Keep cyclic loading quasi-static and monitor kinetic/strain-energy ratio.
5. Enforce zero volume change without applying two incompatible servos to one degree of freedom.
6. Export target and achieved orientation distributions, not only a rendered figure.
7. Save template, compacted, consolidated, rotated and cyclic stages separately.
8. Verify every command and API against the target PFC version through `pfc-mcp`.

## Required Inputs

- PFC version and SI unit convention.
- Equivalent particle-size distribution and specimen dimensions.
- Shape: sphere or ellipsoid aspect ratio `rm`.
- Orientation distribution/Ani level and random seed.
- Target void ratio or relative density.
- Initial confining pressure and loading direction.
- Cyclic axial-strain amplitude, frequency and loop count.
- Hertz-Mindlin properties and convergence criteria.

If the paper/reproduction source omits pressure or grading details, keep them explicit parameters; do not invent values.

## Pipeline

```text
S1 define factor matrix
 -> S2 build clump templates and controlled orientation fabric
 -> S3 compact to target void ratio and install/calibrate Hertz contacts
 -> S4 consolidate and verify ad/Zm
 -> S5 rotate specimen/loading direction
 -> S6 run a constant-volume small-strain loop
 -> S7 calculate G0, fabric and force-chain metrics
 -> S8 fit G0-e-p and complete V&V
```

## Standard Operating Procedure

1. Create a spherical baseline and 5/7/9-pebble ellipsoid templates for `rm=1.5/2.0/2.5`.
2. Check each template's volume, centroid, inertia tensor and major-axis direction.
3. Sample clump orientations: Ani I near-uniform on the sphere; Ani II/III increasingly concentrated around the target depositional plane.
4. Compact using layered under-compaction or an equivalent controlled procedure to the target void ratio.
5. Install Hertz-Mindlin contacts and consolidate to the selected initial pressure.
6. Calculate `ad` and `Zm`. Within one shape family, Ani levels should change `ad` strongly while leaving `Zm` nearly stable.
7. Rotate the specimen or the loading coordinate system to 0, 45 or 90 degrees.
8. Apply a sinusoidal axial strain while lateral walls enforce zero volume change; record one complete equilibrated loop.
9. Calculate G0 from consistent stress/strain amplitudes; fit results by shape, fabric and direction.
10. Run strain-amplitude, frequency, damping, resolution and random-seed checks.

## Reference Parameter Set

Quartz-sand reproduction starting point:

| Parameter | Value |
|---|---:|
| Particle shear modulus | 18 GPa |
| Particle Poisson ratio | 0.15 |
| Particle density | 2650 kg/m3 |
| Particle-particle friction | 0.5 |
| Particle-wall friction | 0.0 |
| Local damping (preparation stage) | 0.7 |
| Cyclic axial-strain amplitude | 3.0e-6 |
| Frequency | 5 Hz |

These are reproduction seeds, not universal calibrated Toyoura-sand properties. Check damping sensitivity during the cyclic stage.

## Case Matrix

- Shape: sphere plus `rm=1.5, 2.0, 2.5` ellipsoids.
- Fabric: Ani I, Ani II, Ani III for each ellipsoid family.
- Direction: 0 degrees for the baseline; 0/45/90 degrees for directional Ani cases.
- Density/pressure: configurable; compare only matched states.
- Repeats: at least three random seeds for uncertainty reporting.

## Post-Processing Recipe

- Loop: stress-strain curve, G0, loop area, damping ratio and mean-pressure drift.
- State: void ratio, volume-strain residual, unbalanced-force ratio and energy ratio.
- Fabric: `Rij`, `aij`, `ad`, principal direction and angle to loading.
- Skeleton: `Zm`, total contacts, rattler fraction and strong/weak force-chain orientation.
- Fit: `A`, `a`, `n`, R-squared and confidence intervals for each shape/fabric/direction group.
- Plot: common-scale spherical histogram plus equal-area orientation map to reduce 3D occlusion.

## Result-Verification Checklist

Expected trends from Wang et al. (2026):

- G0 decreases as void ratio increases; the combined fit reported about `R2=0.94`.
- At comparable density, ellipsoidal specimens have greater G0 than spherical ones; G0 generally rises with aspect ratio.
- For one shape and state, stronger fabric anisotropy lowers G0; its effect becomes larger at higher void ratio.
- At matched fabric, G0 increases as loading direction changes from 0 to 45 to 90 degrees.
- Alignment of particle major axes and loading direction forms a more efficient force-chain network.
- Some strong-fabric 90-degree cases do not follow a simple exponential G0-e law; do not force a global fit.

## V&V Gate

Verification:

- clump geometry/inertia and achieved aspect ratio;
- target versus achieved orientation distribution;
- particle-resolution, timestep, frequency, damping and seed sensitivity;
- kinetic/strain-energy ratio and volume-strain residual;
- unchanged fabric after one genuinely small loop.

Validation:

- compare with bender-element, resonant-column or small-strain cyclic-triaxial data;
- validate the G0-e-p curve and directional modulus ratio, not one G0 point only;
- scan amplitudes (for example 1e-7 to 3e-6) to demonstrate the low-strain plateau.

## Limitations

- Multi-sphere ellipsoids simplify real angularity, roundness and surface roughness.
- Constant volume is a mechanical undrained analogue, not explicit pore-pressure simulation.
- The published 22-case trends do not uniquely define a general constitutive law for strong fabric at 90 degrees.
- Extension to `G/Gmax-gamma`, damping, cyclic liquefaction and anisotropic elasticity needs additional cases and validation.

## Output Contract

Deliver:

- `params.yaml` with version, units, PSD, templates, orientations, pressure, amplitude, frequency, damping and seeds;
- staged saves: `clump_templates -> fabric_compacted -> consolidated -> rotated_angle -> cyclic_done`;
- loop data, G0, void ratio, pressure drift, `ad`, `Zm`, orientation and force-chain plots;
- shape x fabric x void-ratio x direction summary, fits, V&V evidence and exceptions.

## Local Contents

- `references/fabric-metrics.md`: tensor, invariant, coordination and orientation-plot rules.
- `references/hertz-mindlin.md`: reference parameters and calibration cautions.
- `references/findings.md`: measured trends and acceptance checks.
- `scripts/make_ellipsoid_clumps.p3dat`: template-generation skeleton.
- `scripts/prepare_fabric.p3fis`: controlled orientation sampling and fabric metrics.
- `scripts/cyclic_small_strain.p3fis`: consolidation/loading control skeleton.
- `scripts/fabric_g0_post.py`: G0, tensor, coordination and fit postprocessor.
- `templates/params.yaml`: reproducible case parameters.
- `examples/README.md`: run order and validation checks.
