---
name: pfc-freeze-thaw-damage
description: >
  Simulate stress-freeze-thaw coupling of porous rock in PFC with a two-particle system
  (mineral grains + pore-water particles): drive pore-particle expansion from temperature via an
  unfrozen-water-content equation, keep a constant axial stress with an end-wall servo, and
  post-process frost-heave strains and crack statistics (radial density banding, dip-angle bins,
  tensile/shear ratio). Use when the user mentions freeze-thaw cycles, frost heave or frost damage,
  cold-region tunnels or slopes, or coupled stress and freeze-thaw loading.
version: 1.1.0
related_skills:
  - pfc-workflow                  # bus: P2 modeling / P4 solve / P5 post-processing
  - pfc-basics
  - pfc-contact-models
  - pfc-servo-calibration
  - pfc-modeling-techniques
  - pfc-postprocessing
---

# PFC Freeze-Thaw Damage

Explicitly simulate **stress-freeze-thaw coupling** in PFC using a two-particle system (mineral grains
plus pore-water particles) and the **particle-expansion method**: cyclic temperature -> unfrozen water
content -> pore-water particle volume growth -> rock-rock bond breakage = frost-heave damage. A constant
axial stress applied by end walls before cycling gives "freeze-thaw under real-time load", as opposed to
the traditional "freeze-thaw first, mechanical test afterwards" route.

Two output tracks:

- **Frost-heave deformation**: axial / radial / volumetric strain versus cycle number.
- **Fracture evolution**: crack density banding, dip-angle distribution, tensile/shear ratio.

## Parent Skill Relationship

`pfc-freeze-thaw-damage` is a child skill of `pfc-workflow`, plugging into P2 (modeling), P4 (solve) and
P5 (post-processing).

- Parent `pfc-workflow`: owns the full project lifecycle and decides when freeze-thaw support is needed.
- Child `pfc-freeze-thaw-damage`: owns the two-particle specimen, the three bond families, the
  temperature -> unfrozen-water -> volume driver, and freeze-thaw-specific statistics.
- Complementary skill (high-temperature route): thermo-mechanical models that use the PFC thermal module
  with heat conduction driving grain thermal expansion. **This skill does not enable the thermal module**;
  temperature is assigned uniformly and mapped directly to pore-water particle volume.
- Sibling `pfc-servo-calibration` / `pfc-modeling-techniques`: wall servo control and curve-based
  parameter extraction.
- Sibling `pfc-postprocessing`: generic figures and exports after solve.

## When To Use

- Freeze-thaw deformation and damage assessment for cold-region tunnels, slopes and other rock masses.
- Numerical tests that need coupled "real-time load + freeze-thaw" rather than load-after-thaw.
- Meso-mechanism outputs of frost damage: crack density banding, dip-angle distribution, tensile/shear ratio.

## Physical Picture -> Numerical Mapping

| Physical element | Numerical treatment | Key points |
| --- | --- | --- |
| Mineral skeleton | Mineral particles + rock-rock bonds | density 2500 kg/m3, radius 0.8-1.0 mm; bonds carry load and may break |
| Pore water | Pore-water particles | density 920 kg/m3, radius 0.6-0.8 mm, randomly filling the pores |
| Volumetric expansion on freezing | Pore-water particle radius scaled to a target volume | volume increment controlled by rho_w/rho_i and unfrozen water content (Eqs. 1-3) |
| Water-rock / water-water interaction | Very strong bonds (tensile strength and cohesion 100 MPa) | transmit frost-heave force only, never allowed to fail |
| Frost-heave damage | Rock-rock bond breakage registered as a crack | classify by tensile/shear, radial band, dip-angle bin |
| Real-time axial stress | Constant sigma_1 applied by top/bottom walls before cycling | four levels: 0, 0.2 sigma_0, 0.4 sigma_0, 0.6 sigma_0 (sigma_0 = pre-freeze UCS) |

## Operating Rules

1. Water-rock and water-water bond strengths are set large (e.g. 100 MPa) so they only transmit force and
   never break; only rock-rock bonds represent damage.
2. After every pore-water volume change, cycle to mechanical equilibrium before advancing temperature
   (quasi-static driving).
3. Set the minimum temperature where unfrozen water content approaches zero (about -25 to -30 C).
   Temperature is assigned uniformly; no hold time for full freezing/thawing is required, and the T > 0 C
   branch need not be simulated.
4. Apply and servo-stabilize the axial stress sigma_1 **before** entering the freeze-thaw loop; history
   axial/radial strain and crack counts throughout.
5. Calibrate UCS and E to within a few percent before any freeze-thaw run (reference case: 2.2% / 3.3%).

## Required Inputs

Ask for these if missing:

- PFC version and dimensionality (the reference case is PFC3D, cylinder 50 x 100 mm).
- Rock type, dry density, porosity, target UCS and E for calibration.
- Particle sizes and densities for mineral and pore-water particles.
- Axial stress level(s) as a fraction of pre-freeze UCS, and the number of freeze-thaw cycles.
- Temperature schedule: amplitude, period, and minimum temperature.
- Required outputs: strain histories, crack-count/temperature curves, radial density banding, dip-angle
  bins, tensile/shear ratio.

## Pipeline

```
S1 two-particle specimen
 -> S2 three bond families + UCS/E calibration
 -> S3 end walls apply and servo constant sigma_1
 -> S4 freeze-thaw main loop (temperature -> unfrozen water -> particle volume -> equilibrium)
 -> S5 deformation and crack statistics (banding / dip angle / tensile-shear)
 -> S6 cross-check against measured trends
```

## SOP: Freeze-Thaw Main Loop (7 steps)

1. Build the specimen: mineral particles, pore-water particles, and the rock-rock / water-rock /
   water-water bond families.
2. Record the initial volume V0 of every pore-water particle and assign properties per bond family.
3. Read the current mechanical time and compute the current temperature from Eq. (4).
4. Compute the unfrozen water content w_u at that temperature from Eq. (3).
5. Compute the target volume of every pore-water particle from Eqs. (1)-(2).
6. Set the pore-water particle volumes to the target and cycle to mechanical equilibrium.
7. Repeat 3-6 until the target number of cycles is reached.

For stress-freeze-thaw coupling, apply and hold sigma_1 with the end walls **before** step 3.

## Meso Parameters and Calibration Baseline

Reference case: Sichuan yellow sandstone, dry density 2.25 g/cm3, cylinder 50 x 100 mm.

| Bond family | Tensile strength (MPa) | Modulus (GPa) | Cohesion (MPa) | Friction angle (deg) | kn/ks |
| --- | --- | --- | --- | --- | --- |
| Rock-rock | 3.10 | 1.5 | 4.5 | 40 | 1.5 |
| Water-rock | 100 | 0.56 | 100 | 0 | 1.5 |
| Water-water | 100 | 0.56 | 100 | 0 | 1.5 |

- Mineral particles: density 2500 kg/m3, radius 0.8-1.0 mm.
- Pore-water particles: density 920 kg/m3, radius 0.6-0.8 mm.
- Calibration result: numerical UCS 73.40 MPa and E 8.72 GPa against test values 75.05 MPa and 9.02 GPa
  (about 2.2% and 3.3% error). Match the pre-freeze stress-strain curve before starting freeze-thaw runs.

## Post-Processing Recipe (P5)

- **Deformation**: axial/radial strain histories; volumetric strain versus cycle number. In the companion
  laboratory test, strain gauges use quartz-glass temperature compensation to remove gauge-resistance
  drift while retaining rock thermal deformation.
- **Crack-temperature curve**: within a single cycle, crack count rises quickly during cooling and
  flattens below about -25 C (where w_u -> 0).
- **Radial crack density banding**: Eqs. (5)-(6) with a 5 mm sampling interval; verify "surface > interior".
- **Dip-angle distribution**: angle between crack and specimen axis, binned every 5 degrees.
- **Tensile/shear classification**: fraction of tensile bond-failure cracks (analogous to AE mechanism statistics).

## Canonical Script Map

| Topic | File | Purpose |
| --- | --- | --- |
| Specimen generation | `scripts/gen_ftc_specimen.p3dat` | Two-particle specimen, three bond families, staged save chain. |
| Freeze-thaw driver | `scripts/ftc_cycle.p3fis` | temperature -> unfrozen water -> pore-particle volume -> equilibrium. |
| Axial servo | `scripts/axial_servo.p3fis` | End-wall constant-sigma_1 servo (compute_gain -> servo_walls -> stop_me). |
| Crack statistics | `scripts/crack_stats.py` | Radial density banding, dip-angle bins, tensile/shear classification. |
| Case parameters | `templates/params.yaml` | Meso parameters and cases (sigma_1 levels, cycles, temperature amplitude). |

Staged save chain: `ftc_ini` -> `ftc_bonded` -> `ftc_state1` -> `ftc_cycle_n`.

## Result-Verification Checklist

- **No axial stress**: axial and radial strain grow then stabilize after roughly 10 cycles; radial strain
  exceeds axial strain (the axial dimension is longer and more constrained); their difference grows then
  shrinks and oscillates near 100e-6 after 30 cycles.
- **With axial stress**: radial strain grows with cycles and accelerates nonlinearly beyond 30 cycles;
  axial strain is negative and decreases with cycles (damage accumulation); volumetric strain keeps growing.
  In the 0.6 sigma_0 case the specimen fails at about 45 cycles.
- **Spatial distribution**: crack density near the surface clearly exceeds the interior. For 0.6 sigma_0,
  the 0-20 mm band from the axis holds 0.90e7 to 1.17e7 cracks/m3, while the 20-25 mm edge band jumps to
  2.45e7 cracks/m3 (interior is triaxially constrained, the surface is nearly free).
- **Directionality**: low dip angles (0-20 deg) dominate and 80-90 deg is rare. Increasing axial stress
  raises the low-angle share (0-5 deg: 10.86% -> 15.01%, +38.21%) and lowers the high-angle share
  (85-90 deg: 0.52% -> 0.24%, -85.85%): axial compression suppresses radial crack initiation.
- **Mechanism**: freeze-thaw failure is tension-dominated (tensile crack fraction > 50% in all cases).
  As sigma_1 goes from 0 to 0.6 sigma_0, the tensile share falls 68.76% -> 58.97% (compression induces
  some shear).

## Limitations and Improvements

- Specimen temperature is uniform and heat conduction is ignored. Improvement: impose a cyclic temperature
  boundary on the specimen surface with the PFC thermal module and compute ice-particle volume from the
  local real-time temperature.
- Migration of pore water to the freezing front is ignored. Improvement: add a moisture-migration equation
  during freezing and scale ice-particle volume by local water content.

## Output Contract

A complete handoff back to `pfc-workflow` should include:

- Calibrated meso parameters and the pre-freeze UCS/E match.
- Bond-family assignment and the justification for unbreakable water bonds.
- Temperature schedule, minimum temperature and the unfrozen-water form used.
- Volume-increment convention actually implemented (see `references/unfrozen-water.md`).
- Axial stress level, servo tolerance, cycle count, and the staged save chain.
- Strain histories plus crack banding / dip-angle / tensile-shear statistics.
- Explicit statement of the uniform-temperature and no-migration assumptions.

## Local Contents

- `references/unfrozen-water.md`: governing equations, temperature schedule, minimum-temperature choice,
  and the volume-increment consistency check.
- `references/bond-scheme.md`: three bond families and how to assign them.
- `references/findings.md`: measured-trend quick reference for result verification.
- `scripts/`: specimen generation, freeze-thaw driver, axial servo, crack statistics.
- `templates/params.yaml`: meso parameters and case matrix.
- `examples/README.md`: how to validate the bundled workflow.
