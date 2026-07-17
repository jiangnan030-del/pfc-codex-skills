# GBM Prefabricated-Crack Biaxial Case

This reference records the migrated source case parameters and expected outputs.

## Source Case Name

```text
GBM + prefabricated crack + biaxial compression
```

## Specimen And Packing

Initial coarse seed stage:

```text
W = 60 mm
L = 120 mm
porosity = 0.1
random seed = 10001
density = 2600 kg/m3
```

Fine refill stage:

```text
W = 50 mm
L = 100 mm
rmin = 0.3 mm
rmax = 0.45 mm
porosity = 0.1
random seed = 10001
ball friction = 0.1
wall friction = 0.0
```

## Mineral Groups

| Group | Meaning | Coarse seed fraction |
| --- | --- | ---: |
| shiying | quartz-style group | 0.3 |
| xiechangshi | feldspar-style group | 0.3 |
| zhengchangshi | feldspar-style group | 0.3 |
| yunmu | mica-style group | 0.1 |

## Prefabricated Crack

```text
theta = 45 deg
length = 12 mm
aperture = 2 mm
geometry set = liewen1
```

The crack is inserted by creating a rectangular polygon and deleting balls inside it.

## Biaxial Confinement And Loading

Confinement:

```text
txx = -10 MPa
tyy = -10 MPa
```

Loading:

```text
do_yservo = false
vertical wall velocity magnitude = 0.5
stop when stress drops below 70% of peak
```

## Contact Parameters

Per-mineral body contacts use `linearpbond`.

| Group | density | emod (GPa) | kratio | pb_coh (MPa) | pb_ten (MPa) | fric | pb_fa |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shiying | 2648 | 13.8 | 1 | 185.2 | 185.2 | 0.1 | 45 |
| xiechangshi | 2600 | 13.1 | 1 | 205.9 | 205.9 | 0.1 | 45 |
| zhengchangshi | 2600 | 8.7 | 1 | 165.9 | 165.9 | 0.1 | 45 |
| yunmu | 2850 | 5.9 | 1 | 150.3 | 150.3 | 0.1 | 45 |

Default grain-boundary contacts use `smoothjoint`:

| Property | Value |
| --- | ---: |
| sj_kn | 500 GPa |
| sj_ks | 500 GPa |
| sj_fric | 0.1 |
| sj_ten | 9 MPa |
| sj_fa | 45 deg |
| sj_coh | 90 MPa |
| sj_large | 1 |
| sj_state | 3 |

## Recorded Histories

Mechanical:

```text
y_dis, x_dis, y_stress, y_strain, x_strain, V_strain, Poisson_Ratio, Elasticity_mod
```

Cracks:

```text
crack_num
crack_tension_num
crack_shear_num
crack_tension_num_linearpbond
crack_tension_num_smoothjoint
crack_shear_num_linearpbond
crack_shear_num_smoothjoint
```

Energy:

```text
energy_body
energy_damp
energy_kinetic
energy_boundary
energy_strain
energy_slip
energy_dashpot
energy_pbstrain
```

AE-like increment:

```text
zhenling = crack increment per y-strain interval of 3e-6
```

## Validation Checks

Before using results:

- confirm mineral group counts after fine refill
- confirm same-mineral contacts use `linearpbond`
- confirm mixed/grain-boundary contacts use `smoothjoint`
- confirm the prefabricated crack removes particles cleanly
- confirm confinement reaches target within tolerance
- confirm fracture callback creates both tension and shear fracture sets
- confirm energy histories are enabled before loading
