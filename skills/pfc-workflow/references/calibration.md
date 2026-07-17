# Calibration

Use this file when the user asks how to tune PFC micro-parameters against macro behavior by hand or semi-manually.

If the user explicitly asks about `贝叶斯优化`, `LHS`, `代理模型`, `响应面`, `DOE`, or `自动标定`, switch to:

- `references/auto-calibration.md`
- `references/doe-surrogate.md`

## Default tuning order

1. elastic response
2. peak strength
3. post-peak and residual response
4. envelope-level behavior across multiple confining conditions

## Micro-to-macro steering map

- Elastic modulus `E` -> primarily contact or bond `emod`
- Poisson-like lateral response -> stiffness ratio such as `kratio`
- UCS or compressive strength -> bond cohesion and tensile strength families
- Tensile strength ratio -> relative balance of tensile and cohesive bond strength
- Friction angle or shear resistance -> friction, bond friction angle, rolling resistance, or model family choice
- Peak strain and brittleness -> stiffness, bond strength level, heterogeneity, grading, and sometimes rolling or shape effects

## Calibration rules

- Move one parameter family at a time.
- Log every run as micro parameters -> macro outputs.
- Use small, monotonic changes before aggressive jumps.
- Re-check the baseline specimen before calibrating derivative cases.
- Define stopping tolerances explicitly, for example relative error thresholds.

## Common workflow

### Elastic stage

Use the low-strain segment to match modulus-related targets first.

### Strength stage

After elastic parameters are stable, tune bond strength parameters to match UCS, tensile response, or failure envelope.

### Envelope stage

Run multiple confinement or loading conditions only after the zero- or low-confinement baseline is credible.

### Sensitivity stage

Perturb each active parameter around the current point to estimate local response slopes and reduce blind trial-and-error.

## Anti-patterns

- changing stiffness, bond strength, and friction aggressively in the same round
- calibrating a highly structured specimen before the intact or baseline specimen is acceptable
- judging calibration from screenshots instead of exported metrics
