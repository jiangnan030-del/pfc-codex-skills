# Formulas

## Parallel-bond maximum stresses

In the standard BPM parallel-bond description, the chapter gives the maximum tensile and shear stresses on the bond as:

$$
\left\{
\begin{array}{l}
\sigma_{\max}=\dfrac{-\bar{F}_{i}^{\mathrm{n}}}{A}+\dfrac{\left|\bar{M}_{i}^{\mathrm{s}}\right|}{I}\bar{R} \\
\tau_{\max}=\dfrac{\bar{F}_{i}^{\mathrm{s}}}{A}+\dfrac{\left|\bar{M}_{i}^{\mathrm{n}}\right|}{J}\bar{R}
\end{array}
\right.
$$

where:

- $\bar{F}_{i}^{\mathrm{n}}$, $\bar{F}_{i}^{\mathrm{s}}$: normal and shear contact forces
- $\bar{M}_{i}^{\mathrm{n}}$, $\bar{M}_{i}^{\mathrm{s}}$: twisting and bending moments
- $\bar{R}$: average particle radius for the bonded pair
- $A$, $I$, $J$: bond cross-sectional area, moment of inertia, and polar moment

## Geometric terms

$$
\left\{
\begin{array}{l}
A=\pi \bar{R}^{2} \\
I=\dfrac{1}{4}\pi \bar{R}^{4} \\
J=\dfrac{1}{2}\pi \bar{R}^{4}
\end{array}
\right.
$$

## Failure criteria

Use the chapter's two-step interpretation:

- **tension failure** when $\sigma_{\max}$ exceeds bond tensile strength $\sigma_b$
- **shear failure** when $\tau_{\max}$ exceeds bond shear strength $\tau_b$

## Reporting rule

When reusing these formulas:

- define each symbol once
- state whether the figure or derivation is 2D or 3D
- pair the formula with its physical limitation: bond shear strength in the standard BPM is not naturally stress-dependent in the way brittle rock often is
