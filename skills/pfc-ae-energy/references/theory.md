# Theory Route

This reference distills the rock-fracture acoustic-emission route into a reusable PFC workflow. It is based on the idea that a calibrated bonded-particle model can expose microcrack timing, location, force changes, and contact geometry directly, so AE interpretation can be built from PFC state rather than from a sensor inversion alone.

## Interpretation Ladder

### Level 1: AE Hits

Treat each bond break as one AE hit.

Use when the goal is:

- onset of cracking
- cumulative crack activity
- tension vs shear evolution
- stage-wise fracture activity
- lightweight monitoring that minimally changes solve time

### Level 2: AE Events

Group multiple bond breaks into one AE event if they are close in space and time.

Use when the goal is:

- event count rather than raw crack count
- event center location
- event duration
- event size distribution
- meaningful comparison with laboratory AE event catalogs

### Level 3: Moment-Tensor Interpretation

For each AE event, compute a moment tensor from contact-force changes and lever arms relative to the event center.

Use when the goal is:

- source mechanism classification
- scalar moment and moment magnitude
- T-k or Hudson-style source-type plots
- stage-wise tensile/shear/mixed mechanism evolution
- paper-grade AE interpretation of rupture process

## Moment Tensor In PFC

In PFC/DEM, the force and geometry around a broken bond can be read directly. For an AE source region, assemble the moment tensor from contact-force changes and contact lever arms:

```text
M_ij = sum_k DeltaF_i^k * R_j^k
```

where:

- `DeltaF_i^k` is the force change of contact `k` in direction `i`.
- `R_j^k` is the vector from event center to the contact point in direction `j`.
- `k = 1..S` covers contacts associated with the source region.

Symmetrize the tensor before eigenvalue-based interpretation when the implementation produces a nonsymmetric numerical tensor:

```text
M = 0.5 * (M + transpose(M))
```

For multi-crack events, use the geometric or weighted event center and the event's participating contacts/cracks. To limit memory use, store the tensor at the time of maximum scalar moment within the event duration, not every timestep tensor.

## Scalar Moment And Moment Magnitude

Given tensor eigenvalues `m1`, `m2`, and `m3`, use the scalar moment proxy:

```text
M0 = sqrt((m1^2 + m2^2 + m3^2) / 2)
```

A common moment-magnitude relation is:

```text
Mw = (2 / 3) * log10(M0) - 6
```

Use project-specific units consistently. If the PFC force/length units differ from SI, document the scaling before comparing magnitudes to laboratory or field AE magnitudes.

## Tensor Decomposition

Decompose the tensor into:

- `ISO`: isotropic volumetric expansion or contraction.
- `DC`: double-couple shear component.
- `CLVD`: compensated linear vector dipole component.

Interpret CLVD cautiously. In field inversions CLVD may be inflated by noise, velocity model error, or sensor geometry. In PFC, numerical discretization, force-cache timing, and event clustering choices can also affect the apparent CLVD fraction.

## Classification Criteria

Use one or more criteria, but state which one drives the final labels.

### Epsilon Parameter

```text
epsilon = -m_dev_abs_min / abs(m_dev_abs_max)
```

Guidance:

- `epsilon = 0`: pure double-couple tendency.
- `epsilon = +/-0.5`: pure CLVD tendency.
- positive values suggest tensile-source tendency.
- negative values suggest compressive-source tendency.

### R Ratio

```text
R = 100 * trace(M) / (abs(trace(M)) + sum(abs(m_dev_k)))
```

Typical interpretation:

- `R > 30`: tensile-dominated.
- `-30 <= R <= 30`: shear-dominated.
- `R < -30`: implosive/compressive tendency.

### P_DC Criterion

Use the percentage of double-couple component:

- `P_DC >= 60%`: shear.
- `P_DC <= 40%`: tensile.
- `40% < P_DC < 60%`: mixed.

### T-k Source-Type Parameters

Sort tensor eigenvalues so `M1 >= M2 >= M3`. Let `M_iso = (M1 + M2 + M3) / 3` and `M' = M - M_iso` in eigenvalue space.

```text
T = 2 * M2' / max(abs(M1'), abs(M3'))
k = M_iso / (abs(M_iso) + max(abs(M1'), abs(M3')))
```

Use `T` for deviatoric source type and `k` for volumetric tendency.

One practical four-class partition used by the source document is:

- linear tensile: `-1 <= T <= -0.4` and `0.2 <= k <= 0.4`
- linear shear: `0.4 <= T <= 1` and `-0.4 <= k <= -0.2`
- double-couple shear: `-0.2 <= T <= 0.2` and `-0.2 <= k <= 0.2`
- mixed: all remaining valid T-k points

For plotting, use symbol shape for mechanism type and point size for moment magnitude or scalar moment.

## Macro Energy Interpretation

Use two distinct labels and do not mix them:

- **micro event energy or event size**: event-level release proxy, scalar moment, or moment magnitude.
- **macro energy density**: area under stress-strain and derived elastic/dissipated partitions.

If the implementation does not directly compute contact-scale released energy, do not claim it does. Call it a macro energy analysis.

## Expected Rupture Evolution Checks

Use these as qualitative sanity checks, not hard pass/fail criteria:

- compaction stage: little or no AE
- linear elastic stage: small-amplitude, sparse AE; first cracking may appear near the crack-initiation point
- stable crack growth: increasing AE frequency and amplitude
- unstable crack growth and peak: rapid AE acceleration and larger event sizes
- post-peak: intense AE and localized damage
- tensile events often dominate raw counts in bonded-particle rock models
- shear or mixed events often become larger near or after peak stress

## Common Interpretation Traps

- treating every microcrack as an equal-strength independent AE event
- using moment-tensor labels when only raw crack hits were recorded
- storing full-timestep tensors and exhausting memory
- ignoring unit scaling in scalar moment or magnitude
- interpreting CLVD too literally without checking event clustering and force-cache timing
- enabling AE before the specimen is macro-calibrated
- loading too fast and polluting AE timing with inertial effects
