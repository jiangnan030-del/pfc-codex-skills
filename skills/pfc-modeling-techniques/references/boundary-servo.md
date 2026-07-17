# Boundary Servo

Use this reference for the concept side of stress control, confinement, and
equilibrium in PFC. Full code lives in:

- `source-code-boundary-servo-pfc6.md`

## 1. Rigid-wall servo

Best for regular specimens such as UCS, biaxial, and triaxial samples.

### Governing equations

$$
\dot{u}_n^w = G(\sigma^m - \sigma^r) = G \Delta \sigma
$$

$$
G = \frac{\alpha A}{K_n^w N_c \Delta t}
$$

- `alpha`: release factor
- `A`: loaded area
- `K_n^w`: effective wall-normal stiffness
- `N_c`: active wall-contact count
- `Delta t`: current timestep

For a 2D wall pair, a common stress estimate is

$$
\sigma^m = \frac{\sqrt{f_{wx}^2 + f_{wy}^2}}{A}
$$

### Practical guidance

- reduce gain if stress oscillates
- increase gain if convergence is very slow
- evaluate stress history together with local void development

## 2. Servo learning path

A clean learning sequence is:

1. one wall acts as a piston
2. opposing walls move at imposed velocity
3. one-wall stress servo
4. two-wall counter-balanced servo
5. full biaxial servo

## 3. Flexible servo

Use this when the boundary should conform to an irregular outline.

For a boundary segment between `(x1, y1)` and `(x2, y2)`, one projected
x-force form is

$$
F_x = F_c \frac{y_1 - y_2}{\sqrt{(y_1-y_2)^2 + (x_1-x_2)^2}}
$$

One adaptive local relaxation form is

$$
t_r' = t_r \frac{2 \sigma_r - \sigma_m}{\sigma_r}
$$

Area-change ratio is often monitored by

$$
A_c = \frac{|\Delta A|}{A_i}
$$

Recommended starting heuristics:

- porosity `n = 0.12` to `0.17`
- stiffness ratio `k_r = k_f / k_p = 0.01` to `0.1`

## 4. Particle-expansion stress control

Use this when moving walls are inconvenient or too artificial.

Core logic:

1. create many measurement regions
2. evaluate local stress
3. compare local stress to target stress
4. locally expand or shrink particle radii
5. cycle and repeat

Useful field expressions:

$$
Q_a = \frac{Q_m}{A}
$$

$$
\bar{\sigma} = -\frac{1}{A}\sum_{N_c} F^{(c)} \otimes L^{(c)}
$$

$$
N_t = \frac{2 N_c}{A}
$$

Rule of thumb: each measurement region should contain about 20 contacts or
more.

## 5. Geometry-driven wall motion without servo

If walls only constrain or drive the specimen and you do not need stress servo,
simple prescribed wall motion is often enough.

Use this route when:

- the target is displacement-controlled
- stress feedback is not required
- geometry is the main concern rather than pressure control
