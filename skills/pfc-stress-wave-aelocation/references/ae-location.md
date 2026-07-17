# AE Location

This reference preserves the velocity-free 2D AE source localization method and its arbitrary-triangle extension.

## Problem Statement

Traditional AE location usually assumes a known wave velocity. In anisotropic, cracked, or heterogeneous rock, wave speed varies with path. Velocity-free localization avoids prescribing a single velocity by using small sensor clusters and time-delay geometry.

## Kundu Velocity-Free Method

Assumption:

```text
source distance D >> intra-cluster spacing d
```

Then the wavefront arriving at one sensor cluster is approximately planar. For an isosceles right-triangle cluster with reference sensor `S_i1`:

```text
t_i21 = d * cos(theta_i) / c(theta_i)
t_i31 = d * sin(theta_i) / c(theta_i)
```

Arrival direction:

```text
theta_i = atan(t_i31 / t_i21)
```

Direction-dependent wave speed estimate:

```text
c(theta_i) = d / sqrt(t_i21^2 + t_i31^2)
```

One cluster gives a source-bearing ray. Two clusters give two rays; their intersection is the estimated source.

## Arbitrary-Triangle Generalization

Let two non-reference sensors in cluster `i` be separated from the reference sensor by vectors:

```text
v2 = a * (cos(alpha), sin(alpha))
v3 = b * (cos(beta),  sin(beta))
```

For arrival direction `theta_i`:

```text
t_i21 = a * cos(alpha - theta_i) / c(theta_i)
t_i31 = b * cos(theta_i - beta + 2*pi) / c(theta_i)
```

The generalized arrival direction is:

```text
theta_i = atan2(
    b * t_i21 * cos(beta) - a * t_i31 * cos(alpha),
    a * t_i31 * sin(alpha) - b * t_i21 * sin(beta)
)
```

Use `atan2(numerator, denominator)` to place the angle in the correct quadrant.

Then:

```text
c(theta_i) = a * cos(alpha - theta_i) / t_i21
```

## Ray Intersection

For cluster reference point `P_i = (x_i, y_i)` and bearing angle `theta_i`, define ray direction:

```text
d_i = (cos(theta_i), sin(theta_i))
```

For two clusters:

```text
P_1 + s * d_1 = P_2 + t * d_2
```

Solve the 2x2 system for `s` and `t`. The source estimate is:

```text
A = P_1 + s * d_1
```

Reject or downweight if:

```text
|cross(d_1, d_2)| < tolerance
```

because nearly parallel rays amplify small timing errors.

## Multi-Cluster Strategy

With four clusters, every pair of clusters gives one source estimate:

```text
C(4, 2) = 6 estimates
```

Recommended aggregation:

1. compute all pairwise intersections
2. reject nearly parallel ray pairs
3. reject estimates outside the physical domain unless boundary reflections are intentionally used
4. use median or robust mean as final source estimate
5. report spread as geometry/timing uncertainty

## Error Metric

For known source `A_true` and estimate `A_est`:

```text
absolute_error = ||A_est - A_true||
relative_error = absolute_error / characteristic_length
```

The source document reports a “better point” if error is below 20%.

## Geometry Pitfalls

- Source near a line connecting two clusters can produce nearly parallel bearing rays.
- Sensor triangles with very small area are unstable.
- Intra-cluster spacing must be small relative to source distance, but not so small that time delays fall below sampling resolution.
- 2D location ignores out-of-plane travel differences in 3D particle plates.
