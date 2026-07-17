# Formulas

This reference preserves the formula set for the improved linear parallel-bond fast-calibration method.

## Linear Parallel-Bond Model

The linear parallel-bond model contact force and moment are:

```text
F_c = F_l + F_d + Fbar
M_c = Mbar
```

where:

- `F_c` is total contact force.
- `M_c` is total contact moment.
- `F_l` is the linear force.
- `F_d` is the dashpot/damping force.
- `Fbar` is the parallel-bond force.
- `Mbar` is the parallel-bond moment.

Parallel-bond force and moment decomposition:

```text
Fbar = -Fbar_n * n_c + Fbar_s
Mbar = Mbar_b
Fbar_s = Fbar_st * t_c
Mbar_b = Mbar_bs * s_c
```

Normal and shear stiffness for the linear part:

```text
k_n = A * E_star / L
k_s = k_n / k_star
```

For 3D ball-ball contacts:

```text
A = pi * r^2
r = min(R1, R2)
```

For ball-facet contacts:

```text
r = R1
```

Parallel-bond stiffness relations:

```text
kbar_n = Ebar_star / L
kbar_s = kbar_n / kbar_star
```

Bond failure checks:

```text
sigma_bar > sigma_c_bar -> tensile bond break
tau_bar > tau_c_bar     -> shear bond break
```

Shear strength limit:

```text
tau_c_bar = c_bar - sigma * tan(phi_bar)
```

## Improved Strong/Weak Contact Model

The improved route randomly splits ball-ball contacts into strong and weak groups.

Weak-contact filling ratio:

```text
Rf = N_weak / N_ball_ball
```

Strong contact parameters:

```text
Ebar_star_strong = Ebar_star
k_star_strong = k_star
kbar_star_strong = kbar_star * R_k
sigma_c_strong = sigma_c_bar
c_strong = c_bar
```

Weak contact parameters:

```text
Ebar_star_weak = Ebar_star * R_E
k_star_weak = k_star
kbar_star_weak = kbar_star * R_k
sigma_c_weak = sigma_c_bar * R_sigma
c_weak = c_bar * R_sigma
```

Cohesion ratio:

```text
c_bar = coh_ratio * sigma_c_bar
```

Linear modulus from bonded modulus ratio:

```text
E_star = E_ratio * Ebar_star
```

## Weibull Damage

Probability density:

```text
f(x) = (beta / alpha^beta) * x^(beta - 1) * exp(-(x / alpha)^beta), x >= 0
```

Cumulative distribution:

```text
F(x) = 1 - exp(-(x / alpha)^beta)
```

Monte Carlo inverse transform:

```text
x = alpha * (-ln(1 - f))^(1 / beta)
```

where `f` is a uniform random value in `(0, 1)`. The source method uses:

```text
alpha = 1.0
beta = beta_weibull
```

Apply to weak and strong bonded-contact properties after group assignment:

```text
pb_ten <- pb_ten * x
pb_coh <- pb_coh * x
pb_kn  <- pb_kn  * x
pb_ks  <- pb_ks  * x
```

For new studies, explicitly document whether stiffness, strength, or both are damaged.

## Macro Metric Extraction

Elastic modulus from uniaxial compression stress-strain curve:

```text
E = (sigma_2 - sigma_1) / (epsilon_2 - epsilon_1)
```

Source definition:

```text
epsilon_1 = axial strain at 0.05%
epsilon_2 = axial strain at 0.15%
```

Poisson's ratio:

```text
nu = (nu_1 + nu_2) / 2
```

Source definition:

```text
nu_1 = Poisson's ratio at axial strain 0.1%
nu_2 = Poisson's ratio at axial strain 0.2%
```

Crack-damage stress ratio:

```text
crack_damage_ratio = sigma_cd / UCS
```

`sigma_cd` is the axial stress at the volumetric strain compression-to-dilation transition point.

Compression/tension ratio:

```text
UCS_UTS_ratio = UCS / UTS
```

Mohr-Coulomb fit from triaxial tests:

```text
tau = c + sigma_n * tan(phi)
```

Use multiple confining pressures for a robust `c` and `phi`. A single triaxial confining pressure is not enough to define a reliable envelope unless combined with other assumptions.

## Pearson Correlation

For micro-parameter series `X` and macro-output series `Y`:

```text
r = sum_i((X_i - mean(X)) * (Y_i - mean(Y))) /
    sqrt(sum_i((X_i - mean(X))^2) * sum_i((Y_i - mean(Y))^2))
```

Use Pearson coefficients to identify dominant factors before fitting regression equations.

## Regression Equations

The following empirical equations are source-specific. They are useful as a reproduction reference and initial predictor, not universal rock laws.

Elastic modulus:

```text
E = 0.031 * Ebar_star - 0.886 * kbar_star - 6.728 * Rf + 16.546
R^2 = 0.909
```

Poisson's ratio:

```text
nu = -0.0002 * Ebar_star + 0.029 * kbar_star + 0.158 * Rf - 0.0001
R^2 = 0.706
```

Uniaxial compressive strength:

```text
UCS = -0.087 * Ebar_star
      + 70.061 * E_ratio
      + 0.646 * sigma_c_bar
      + 15.55 * coh_ratio
      + 24.043 * mu
      - 0.446 * phi_bar
      - 84.036 * beta_bar_moment
      - 76.097 * Rf
      + 135.056 * R_sigma
      + 28.910
R^2 = 0.851
```

Linear friction angle fit:

```text
phi = 0.019 * Ebar_star
      + 1.454 * coh_ratio
      + 7.531 * mu
      - 14.064 * beta_bar_moment
      - 11.511 * Rf
      + 60.247
R^2 = 0.524
```

Improved nonlinear friction angle fit:

```text
phi = 0.019 * Ebar_star
      + 1.454 * coh_ratio
      + 0.974 * ln(-0.840 + 1.692 * mu)
      - 14.064 * beta_bar_moment
      + 0.970 * ln(1.942 - 2.767 * Rf)
      + 64.236
R^2 = 0.680
```

Cohesion:

```text
c = -0.016 * Ebar_star
    + 0.081 * sigma_c_bar
    + 1.573 * coh_ratio
    - 0.065 * phi_bar
    - 5.364 * beta_bar_moment
    - 7.011 * Rf
    + 14.867 * R_sigma
    + 7.653
R^2 = 0.705
```

Crack-damage stress ratio:

```text
sigma_cd/UCS = -0.419 * E_ratio
               - 0.003 * sigma_c_bar
               - 0.065 * coh_ratio
               + 0.003 * phi_bar
               + 0.260 * beta_bar_moment
               + 0.325 * Rf
               + 0.281 * R_E
               + 0.572
R^2 = 0.699
```

Compression/tension ratio:

```text
UCS/UTS = 0.126 * phi_bar
          - 9.056 * beta_bar_moment
          + 9.484 * Rf
          - 16.026 * R_sigma
          + 3.352
R^2 = 0.713
```

## Back-Solving Strategy

The source example fixes these parameters first:

```text
E_ratio = 0.3
kbar_star = 3
beta_bar_moment = 0.5
Rf = 0.7
beta_weibull = 3
R_E = 0.1
R_k = 2
```

Then it back-solves or manually selects the remaining parameters:

```text
Ebar_star = 85 GPa
sigma_c_bar = 135 MPa
coh_ratio = 2
mu = 0.7
phi_bar = 30 deg
R_sigma = 0.1
```

The validation simulation should still be run after back-solving.
