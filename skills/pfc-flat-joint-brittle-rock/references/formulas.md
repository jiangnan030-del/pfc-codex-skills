# Formulas

## Installation-gap logic

The chapter defines the installation-gap idea through:

$$
g = g_{\text{ratio}} \min(R_A, R_B)
$$

where:

- $g$: installation gap
- $g_{\text{ratio}}$: installation-gap ratio
- $R_A$, $R_B$: radii of the two particles

Use this to explain how flat-joint contacts can be installed beyond the nearly-zero gap convention of the standard BPM.

## Flat-joint element stresses

The chapter gives the element-level stresses as:

$$
\left\{
\begin{array}{l}
\sigma_{\max}^{(e)}=\dfrac{-\bar{F}_{e}^{n}}{A^{(e)}} \\
\tau_{\max}^{(e)}=\dfrac{\bar{F}_{e}^{s}}{A^{(e)}}
\end{array}
\right.
$$

where:

- $\bar{F}_{e}^{n}$, $\bar{F}_{e}^{s}$: normal and shear force on element $e$
- $A^{(e)}$: area of element $e$

## Bonded-element shear strength with tension cut-off

$$
\tau_c = c_b - \bar{\sigma} \tan\phi_b
$$

where:

- $c_b$: bonded-element cohesion
- $\phi_b$: local friction angle
- $\bar{\sigma}$: normal stress acting on the element

## Residual friction strength after bond break

$$
\tau_r = -\bar{\sigma} \tan\phi_r
$$

where $\phi_r$ is the residual friction angle.

## Reporting rule

When reusing these equations:

- distinguish bonded-element and residual states
- say whether the context is conceptual derivation, calibration, or parameter study
- connect each formula to the modeling advantage it provides over standard BPM
