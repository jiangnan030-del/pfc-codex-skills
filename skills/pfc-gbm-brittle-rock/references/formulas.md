# Formulas

This reference preserves the formulas and calculation logic needed by the GBM + prefabricated-crack biaxial-compression workflow.

## Brittle-Rock Indicators

Brittle hard rock often has:

```text
UCS / TS = 10 to 20 or higher
large internal friction angle
nonlinear strength envelope
```

A standard BPM often underestimates the compression/tension ratio and produces a more linear strength envelope. GBM improves this by introducing irregular grain geometry and grain-boundary contacts.

## Standard Parallel-Bond Failure Measures

For a bonded contact, maximum normal and shear stresses can be written conceptually as:

```text
sigma_max = -Fbar_n / A + |Mbar_s| * Rbar / I
tau_max   =  Fbar_s / A + |Mbar_n| * Rbar / J
```

For a circular bond in 3D:

```text
A = pi * Rbar^2
I = (1/4) * pi * Rbar^4
J = (1/2) * pi * Rbar^4
```

Failure criteria:

```text
sigma_max > sigma_b -> tensile crack
tau_max > tau_b     -> shear crack
```

In the migrated 2D case, `linearpbond` failures are tracked separately from `smoothjoint` failures.

## GBM Concept

GBM represents crystalline rock as:

```text
grain body contacts    -> linearpbond / mineral-specific LPBM
grain boundary contacts -> smoothjoint / low-strength interface
```

The source case transfers mineral labels through this chain:

```text
coarse particles with mineral groups
-> geometry nodes at particle centers
-> rblock Voronoi construction
-> rblock group assignment from nearest original ball
-> mineral geometry export
-> fine particles assigned to mineral groups by geometry-distance ranges
```

## Prefabricated Crack Geometry

The slit is represented as a rectangular polygon centered at the specimen center. For crack angle `theta`, length `l`, and aperture `a`, the four polygon vertices are:

```text
p1 = (-l/2*cos(theta) + a/2*sin(theta), -l/2*sin(theta) - a/2*cos(theta))
p2 = ( l/2*cos(theta) + a/2*sin(theta),  l/2*sin(theta) - a/2*cos(theta))
p3 = ( l/2*cos(theta) - a/2*sin(theta),  l/2*sin(theta) + a/2*cos(theta))
p4 = (-l/2*cos(theta) - a/2*sin(theta), -l/2*sin(theta) + a/2*cos(theta))
```

Then:

```text
geometry polygon create by-positions p1 p2 p3 p4
wall import from-geometry crack_geometry
ball delete range geometry-space crack_geometry count odd
```

## Biaxial Wall Stress

Specimen dimensions from wall positions:

```text
wlx = x_right - x_left
wly = y_top - y_bottom
```

Wall stress estimates:

```text
wsxx = 0.5 * (F_left_x - F_right_x) / wly
wsyy = 0.5 * (F_bottom_y - F_top_y) / wlx
```

Servo gains:

```text
gx = fac * 2 * wly / (sum_kn_x * timestep)
gy = fac * 2 * wlx / (sum_kn_y * timestep)
```

Velocity commands:

```text
v_left  =  gx * (wsxx - target_x)
v_right = -gx * (wsxx - target_x)
v_bottom =  gy * (wsyy - target_y)
v_top    = -gy * (wsyy - target_y)
```

## Biaxial Loading Metrics

Axial displacement and force:

```text
y_dis = y_top - y_bottom
y_force = |F_bottom_y - F_top_y|
```

Stress and strain:

```text
y_stress = |y_force / wlx0 / 2|
y_strain = |(y_dis - wly0) / wly0|
x_strain = |(x_dis - wlx0) / wlx0|
V_strain = x_strain + y_strain
Poisson_ratio = |x_strain / (y_strain + eps)|
Elasticity_mod = |y_stress / (y_strain + eps)|
```

The source script uses `eps = 1e-10` to avoid division by zero.

## Crack Tracking

The bond-break callback receives an event entry with contact and mode. The source callback tracks:

```text
crack_num = crack_tension_num + crack_shear_num
crack_tension_num = crack_tension_num_linearpbond + crack_tension_num_smoothjoint
crack_shear_num = crack_shear_num_linearpbond + crack_shear_num_smoothjoint
```

Mode convention:

```text
mode = 1 -> tension crack
mode = 2 -> shear crack
```

Fracture segment endpoints are built from contact position, contact normal, and a characteristic crack size:

```text
inDir = (-normal_y, normal_x)
vert1 = contact_pos + inDir * crack_size
vert2 = contact_pos - inDir * crack_size
```

## AE-Like Crack Increment

The source case records an AE-like event count increment per strain interval:

```text
if y_strain - previous_recorded_strain >= strain_interval:
    increment = crack_num - previous_recorded_crack_count
    previous_recorded_strain = y_strain
    previous_recorded_crack_count = crack_num
```

Default source value:

```text
strain_interval = 3e-6
```

This is a crack-count proxy, not a calibrated moment-tensor AE event unless routed to `pfc-ae-energy` for additional processing.

## Energy Histories

The migrated loading stage records:

```text
ball energy-body
ball energy-damp
ball energy-kinetic
wall energy-boundary
contact energy-strain
contact energy-slip
contact energy-dashpot
contact energy-pbstrain
```

Use these histories to separate stored strain energy, dissipated energy, kinetic bursts, boundary work, and bond-strain energy trends.
