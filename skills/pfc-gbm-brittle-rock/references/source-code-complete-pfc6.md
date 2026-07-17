# Complete PFC 6.0 Source-Code Route

This reference explains the migrated GBM + prefabricated-crack biaxial-compression source files stored under `scripts/canonical/gbm-prefabricated-crack-biaxial/`.

## Stage 1: Initial Mineral-Seeded Particle Pack

File:

```text
stage_01_initial_particle_pack.dat
```

Purpose:

- create a rectangular 2D specimen domain
- distribute particles with four mineral groups
- compact and trim particles outside the target box
- save state `1`

Source mineral groups:

```text
shiying
xiechangshi
zhengchangshi
yunmu
```

Key source proportions in the coarse seed pack:

```text
shiying: 0.3
xiechangshi: 0.3
zhengchangshi: 0.3
yunmu: 0.1
```

## Stage 2: Voronoi / Rblock Grain Geometry

File:

```text
stage_02_voronoi_rblock_geometry.dat
```

Purpose:

- restore state `1`
- create a geometry set named `rock`
- create one geometry node per ball center
- preserve mineral group information on nodes
- construct rblocks from the geometry using Voronoi logic
- save state `2`

## Stage 3: Export Mineral Geometry

File:

```text
stage_03_export_mineral_geometry.dat
```

Purpose:

- restore state `2`
- assign each rblock to the mineral group of the nearest original ball
- export one geometry set per mineral group
- delete rblocks, balls, and walls
- save state `3`

Output geometry sets:

```text
shiying
xiechangshi
zhengchangshi
yunmu
```

## Stage 4: Refill Fine Particles By Mineral Geometry

File:

```text
stage_04_refill_particles_by_mineral_geometry.dat
```

Purpose:

- restore state `3`
- create a finer ball assembly
- trim to specimen box
- assign ball groups by geometry-distance ranges
- save state `4`

This stage separates the coarse grain-network generation from the fine numerical particle assembly.

## Stage 5: Biaxial Confining Servo

File:

```text
stage_05_biaxial_confining_servo.dat
```

Purpose:

- restore state `4`
- compute wall dimensions and wall stresses
- compute stiffness-based servo gains
- servo walls to target stresses
- save state `5`

Default target stresses:

```text
txx = -10 MPa
tyy = -10 MPa
```

Route detailed servo tuning and stability checks to `pfc-servo-calibration`.

## Stage 6: Prefabricated Crack Cut

File:

```text
stage_06_prefabricated_crack_cut.dat
```

Purpose:

- restore state `5`
- compute a rectangular crack polygon from angle, length, and aperture
- create geometry set `liewen1`
- import crack geometry as a wall
- delete balls inside the crack geometry
- solve and save state `6`

Source crack parameters:

```text
theta = 45 deg
length = 12 mm
aperture = 2 mm
```

## Stage 7: GBM Contact Assignment

File:

```text
stage_07_gbm_contact_assignment.dat
```

Purpose:

- restore state `6`
- assign mineral densities
- add per-mineral `linearpbond` CMAT entries for same-mineral contacts
- assign default ball-ball `smoothjoint` contacts for grain boundaries
- assign ball-facet linear contact model
- apply CMAT, bond contacts, clean model, reset states
- save state `7`

Per-mineral LPBM seed parameters in the source case:

| Group | emod (GPa) | pb_coh (MPa) | pb_ten (MPa) |
| --- | ---: | ---: | ---: |
| shiying | 13.8 | 185.2 | 185.2 |
| xiechangshi | 13.1 | 205.9 | 205.9 |
| zhengchangshi | 8.7 | 165.9 | 165.9 |
| yunmu | 5.9 | 150.3 | 150.3 |

Default smooth-joint boundary seed values:

```text
sj_kn = 500 GPa
sj_ks = 500 GPa
sj_fric = 0.1
sj_ten = 9 MPa
sj_fa = 45 deg
sj_coh = 90 MPa
sj_large = 1
sj_state = 3
```

## Stage 8: Trim Specimen

File:

```text
stage_08_trim_specimen.dat
```

Purpose:

- restore state `7`
- ensure target confinement values are set
- trim particles outside the current wall dimensions
- save state `8`

## Stage 9: Biaxial Loading And Monitoring

Files:

```text
stage_09_biaxial_loading_monitoring.dat
fracture_tracking.p2fis
```

Purpose:

- restore state `8`
- call fracture tracking FISH
- initialize wall dimensions
- remove y-servo and load vertically by wall velocity
- enable mechanical energy
- record stress, strain, crack count, crack mode, contact-model crack source, energy terms, and AE-like crack increments
- stop after post-peak stress drops below a fraction of peak
- save state `9`

Default loading:

```text
vertical wall speed = 0.5
peak_fraction = 0.7
```

## Fracture Tracking

`fracture_tracking.p2fis` registers a bond-break callback:

```text
fish callback add @add_crack event bond_break
```

It creates deterministic fractures in DFN sets labeled by mode and contact model, such as:

```text
crack_tension_linearpbond
crack_shear_linearpbond
crack_tension_smoothjoint
crack_shear_smoothjoint
```

It also periodically calls:

```text
fragment compute
```

## Version Notes

The migrated files preserve the source case logic and naming. Before production runs:

- verify `smoothjoint` property names for the installed PFC version
- verify `rblock construct from-geometry ... voronoi` support
- verify `geometry-distance` and `geometry-space` range syntax
- verify `fish callback ... event bond_break` syntax
- verify `fracture.create` and `fragment compute` availability
