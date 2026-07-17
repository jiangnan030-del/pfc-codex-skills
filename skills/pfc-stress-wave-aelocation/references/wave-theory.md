# Wave Theory

## 1D Particle Chain

Use a one-dimensional particle chain to validate elastic wave speed, source shape, dispersion, and boundary behavior before moving to 2D/3D models.

For a contact-bonded 1D chain with particle radius `R`, contact normal stiffness `k_n`, particle density `rho_p`, and equivalent continuum density `rho`:

```text
E_c = k_n / (4R)
rho = (pi / 6) * rho_p
alpha = sqrt(E_c / rho)
```

Source example:

```text
rho_p = 2000 kg/m3
rho = 1047 kg/m3
alpha_theory = 7569 m/s
alpha_simulation = 7560 m/s
relative_error = 0.12%
```

For a parallel-bonded chain:

```text
Ebar_c = 2R * kbar_n
alpha = sqrt((E_c + (pi/4) * Ebar_c) / rho)
```

The source notes that parallel-bond chains may distort waveforms because tensile-state stiffness differs from compressive-state stiffness, so contact-bonded chains are preferred for clean wave-speed measurement.

## Numerical Dispersion

A particle chain behaves like a mass-spring lattice. The dispersion relation is:

```text
omega = 2 * sqrt(K / m) * sin(kD / 2)
```

Phase velocity:

```text
V_p = 2 * sqrt(K / m) * sin(kD / 2) / k
```

Group velocity:

```text
V_g = D * sqrt(K / m) * cos(kD / 2)
```

Long-wavelength limit:

```text
lambda >> D
sin(kD / 2) ~= kD / 2
V_p = V_g = D * sqrt(K / m)
```

Practical criterion:

```text
lambda / D >= 10
```

Equivalently:

```text
lambda = c_min / f_max
lambda / D = c_min / (f_max * D)
```

If this fails, lower the source frequency, reduce particle spacing, or do not interpret wavefront and arrival-time results as continuum-elastic waves.

## Boundary Reflection

Reflection behavior is controlled by acoustic impedance:

```text
Z = rho * c
K = Z_I / Z_II
```

Idealized cases:

| Boundary | Impedance ratio | Reflection | Boundary displacement |
| --- | --- | --- | --- |
| rigid / fixed | K -> 0 | same amplitude, opposite sign | zero by cancellation |
| free | K -> infinity | same amplitude, same sign | doubled |
| absorbing | K -> 1 | ideally none | transmitted/absorbed |

A 1D absorbing boundary can be approximated by applying a dashpot-like concentrated force to boundary particles:

```text
F = -C_abs * u_dot
```

Source expression:

```text
C_abs = (2/3) * pi * R^2 * rho_p * sqrt(3 * k_n / (2 * pi * R * rho_p))
```

## 2D Hexagonal Lattice

For a 2D hexagonal particle lattice, the average density is:

```text
rho = 2m / (sqrt(3) * D^2)
```

Lame constants:

```text
lambda_Lame = mu = (sqrt(3) / 4) * K
```

P-wave and S-wave speeds:

```text
alpha = D * sqrt(9K / (8m))
beta  = D * sqrt(3K / (8m))
alpha / beta = sqrt(3)
```

Source example values:

```text
alpha_theory = 2539 m/s
beta_theory = 1466 m/s
alpha_measured = 2417 m/s
beta_measured = 1340 m/s
measured_ratio = 1.8
```

A 2D hexagonal lattice produces approximately circular P and S wavefronts. P-wave particle motion is radial; S-wave particle motion is tangential.

## Radiation Pattern From A Point Force

For a concentrated force in the positive `y` direction, far-field displacement patterns can be written with direction cosines:

```text
gamma_x = cos(theta)
gamma_y = sin(theta)
```

P-wave displacement magnitude:

```text
|u_P| = |sin(theta)|
```

S-wave displacement magnitude:

```text
|u_S| = |cos(theta)|
```

Interpretation:

- P waves are strongest along the force direction and zero perpendicular to it.
- S waves are strongest perpendicular to the force direction and zero along it.

## Common Wave Modeling Traps

- `lambda / D < 10`: numerical dispersion dominates.
- local damping left on: artificial attenuation pollutes measured amplitude.
- mass scaling / timestep scaling used: wave speed and time-of-flight become nonphysical.
- boundary reflections ignored: late arrivals are contaminated.
- only one monitor used: cannot distinguish velocity, attenuation, dispersion, and source effects.
