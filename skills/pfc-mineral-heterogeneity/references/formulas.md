# Formulas

This reference preserves the formula set behind the mineral-composition-aware heterogeneous rock workflow. Use it when explaining the theory or when converting the source method into auditable PFC command files.

## Digital Image And Otsu Segmentation

A digital rock image can be represented as a pixel matrix. For an RGB image converted to grayscale, each pixel has an intensity value:

```text
f(x, y) in [0, 255]
```

Let gray level `i` have pixel count `n_i`, total pixel count `N`, and probability:

```text
p_i = n_i / N
```

The global gray mean is:

```text
mu = sum_i i * p_i
```

The global variance is:

```text
sigma^2 = sum_i (i - mu)^2 * p_i
```

For multi-threshold segmentation into `n` classes, thresholds split the histogram into intervals. For class `k`:

```text
omega_k = sum_{i in class k} p_i
mu_k    = sum_{i in class k} i * p_i / omega_k
sigma_k^2 = sum_{i in class k} (i - mu_k)^2 * p_i / omega_k
```

The within-class variance is:

```text
sigma_W^2 = sum_k omega_k * sigma_k^2
```

Otsu chooses thresholds that maximize between-class variance. For three classes, a common expression is:

```text
sigma_B^2 = omega_0 * omega_1 * (mu_0 - mu_1)^2
          + omega_0 * omega_2 * (mu_0 - mu_2)^2
          + omega_1 * omega_2 * (mu_1 - mu_2)^2
```

The source example maps low/middle/high grayscale phases to mica/quartz/feldspar and reports approximate mineral fractions:

```text
mica: 4.81%
quartz: 35.86%
feldspar: 59.32%
```

## Mineral Fraction In PFC

For PFC2D disks, use area fraction rather than particle count fraction when particles are polydisperse:

```text
A_total = sum_b pi * r_b^2
A_phase = sum_{b in phase} pi * r_b^2
fraction_phase = A_phase / A_total
```

For PFC3D spheres, use volume fraction:

```text
V_total = sum_b (4/3) * pi * r_b^3
V_phase = sum_{b in phase} (4/3) * pi * r_b^3
fraction_phase = V_phase / V_total
```

## Cellular-Automata Cluster Growth

The source workflow begins with all particles in the matrix phase, then grows filling-mineral clusters from random seeds. A generic acceptance probability for phase `T` is:

```text
eta_T = (A_T - A_S) / A_T
```

where:

- `A_T` is the target area for mineral `T`.
- `A_S` is the current area already assigned to mineral `T`.

A practical bounded implementation is:

```text
acceptance_probability = max(target_area - current_area, 0) / target_area
```

Use the same idea with volume for PFC3D.

## LPBM Force And Moment Components

The linear parallel-bond model combines linear contact, damping, and parallel-bond components. The total contact force and moment are represented as:

```text
F_c = F_l + F_d + F_b
M_c = M_b
```

where:

- `F_l` is the linear elastic contact force.
- `F_d` is the local damping force.
- `F_b` is the parallel-bond force.
- `M_b` is the parallel-bond moment.

A simplified damping relation is:

```text
F_d = -alpha * |F| * sign(V)
```

where `alpha` is a damping coefficient, `|F|` is force magnitude, and `V` is velocity sign.

The linear force can be split into normal and shear components:

```text
F_l = F_n^l * n_i + F_s^l * t_i
```

Normal and shear force updates:

```text
F_n^l = F_n0 + k_n * g_s
F_s^l = F_s0 + k_s * Delta_delta_s
```

The Coulomb slip limit is:

```text
F_s^l <= mu * F_n^l
```

where `mu` is the contact friction coefficient.

## Stiffness Relations

A common effective-modulus stiffness relation is:

```text
k_n = A * E* / L
k_s = k_n / k*
```

where:

- `A` is the contact area term. In 2D, the source uses `A = 2 * r * t` with `t = 1`.
- `E*` is the linear effective modulus.
- `L` is characteristic length: sum of radii for ball-ball contacts and ball radius for ball-wall contacts.
- `k*` is the normal-to-shear stiffness ratio.

Parallel-bond force and moment components are:

```text
F_b = F_n^b * n_i + F_s^b * t_i
M_b = M_n^b * n_i + M_s^b * t_i
```

For 2D, torsion is zero and bending moment changes with relative rotation. A simplified source expression is:

```text
M_s^b = M_s^b - k_n * I * Delta_theta_s
I = (2/3) * R^3 * t
```

The bond fails when tensile or shear stress exceeds bond strength:

```text
sigma_b > pb_ten  -> tensile bond failure
tau_b   > pb_coh  -> shear bond failure
```

## Calibration Fit Relations From Source Example

These empirical fit relations are example-specific. Use them as a chapter reproduction reference, not universal material laws.

Bond effective modulus from target Young's modulus:

```text
E = 0.673 * Ebar* + 0.207
```

Linear effective modulus from target Young's modulus:

```text
E = 0.211 * E* + 19.007
```

Stiffness ratio from target Poisson's ratio:

```text
nu = 0.0815 * k* + 0.0024
```

Bond strength scale from UCS:

```text
UCS = 0.612 * tau_c_bar + 24.82
```

Source calibration targets:

```text
Young's modulus: 21.04 GPa
UCS: 216.43 MPa
Poisson's ratio: 0.22
BTS: 19.96 MPa
```

Example final parameters:

| Mineral | Linear emod (GPa) | PB emod (GPa) | kratio | pb_ten (MPa) | pb_coh (MPa) |
| --- | ---: | ---: | ---: | ---: | ---: |
| mica | 1.9 | 6.8 | 2.7 | 49.6 | 49.6 |
| quartz | 7.5 | 28 | 2.7 | 66.2 | 66.2 |
| feldspar | 9.6 | 32 | 2.7 | 332.5 | 332.5 |

## Filling / Matrix Strength Ratio

The source method uses feldspar as the matrix and quartz/mica as filling minerals. Reducing filling/matrix bond strength can improve the simulated compression/tension ratio.

Example ratios:

```text
quartz / feldspar strength ratio: 0.15
mica / feldspar strength ratio: 0.12
```

Reported sensitivity trend:

| Filling/matrix strength ratio | UCS (MPa) | UTS (MPa) | BTS (MPa) | UCS/UTS | UCS/BTS |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.01 | 148.78 | 5.08 | 10.23 | 29.28 | 14.54 |
| 0.05 | 157.00 | 5.94 | 10.57 | 26.43 | 14.85 |
| 0.10 | 192.50 | 12.64 | 13.20 | 15.23 | 14.58 |
| 0.15 | 225.00 | 19.50 | 16.70 | 11.54 | 13.47 |
| 0.25 | 236.79 | 30.50 | 17.35 | 7.76 | 13.64 |
| 0.45 | 262.32 | 50.63 | 18.02 | 5.18 | 14.56 |
| 0.75 | 334.00 | 74.42 | 22.68 | 4.49 | 14.72 |
| 1.00 | 356.40 | 83.78 | 22.85 | 4.25 | 15.58 |

## Weibull Damage Distribution

Probability density:

```text
f(x) = (beta / alpha) * (x / alpha)^(beta - 1) * exp(-(x / alpha)^beta), x >= 0
```

Cumulative distribution:

```text
F(x) = 1 - exp(-(x / alpha)^beta)
```

Inverse transform for random variable `x`:

```text
x = alpha * (-ln(1 - R))^(1 / beta)
```

where:

- `R` is uniform random in `[0, 1)`.
- `alpha` controls scale.
- `beta` controls dispersion.

Use the random multiplier on selected bond properties:

```text
pb_ten <- pb_ten * x_strength
pb_coh <- pb_coh * x_strength
pb_kn  <- pb_kn  * x_stiffness
pb_ks  <- pb_ks  * x_stiffness
```

Document whether stiffness, strength, or both are damaged.
