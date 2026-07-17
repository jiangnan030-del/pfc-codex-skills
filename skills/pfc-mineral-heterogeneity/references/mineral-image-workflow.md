# Mineral Image Workflow

Use this reference when the model should reflect mineral composition from a digital image or a phase map.

## Input Routes

Choose one route:

1. **Segmented phase map**: user already provides mineral labels per pixel or region.
2. **RGB / grayscale image**: segment with preprocessing and Otsu thresholds.
3. **Manual fractions**: user supplies target mineral percentages without spatial map.
4. **Synthetic sweep**: user varies mineral fractions to study sensitivity.

## Otsu Multi-Threshold Route

The source workflow uses grayscale conversion, denoising, median filtering, and Otsu multi-threshold segmentation to separate mineral phases.

Core concept:

- grayscale values are grouped into mineral classes
- thresholds maximize between-class variance
- class fractions become target mineral area fractions for 2D PFC construction

For a three-mineral granite example:

```text
low grayscale: mica
middle grayscale: quartz
high grayscale: feldspar
```

Example reported fractions:

```text
mica: 4.81%
quartz: 35.86%
feldspar: 59.32%
```

## Phase Fraction Calculation

For image data:

```text
fraction_i = pixels_in_phase_i / total_valid_pixels
```

For PFC2D balls:

```text
area_i = sum(pi * radius^2 for balls in phase_i)
fraction_i = area_i / total_ball_area
```

For PFC3D balls:

```text
volume_i = sum(4/3 * pi * radius^3 for balls in phase_i)
fraction_i = volume_i / total_ball_volume
```

Use area for PFC2D and volume for PFC3D. Do not mix pixel fraction and particle count fraction unless particle size is uniform and documented.

## Cellular-Automata Cluster Construction

The source method builds clustered mineral domains rather than pixel-perfect mineral masks.

Recommended PFC2D pattern:

1. Assign all balls to the matrix phase, usually the most abundant mineral.
2. Seed filling phases randomly with a fixed random seed.
3. Grow each seeded phase across contact-connected neighbor balls.
4. Accept new balls with a probability tied to remaining target area.
5. Stop each phase when its target area fraction is reached within tolerance.
6. Save a mineral-assigned state.

Generic acceptance idea:

```text
acceptance_probability = max(target_area - current_area, 0) / target_area
```

The exact probability can be modified to control cluster compactness and connectivity.

## Interface Assignment

After ball mineral groups are assigned, classify contacts:

- same mineral endpoints -> mineral contact group
- different mineral endpoints -> interface group or phase-pair group

Simple group scheme:

```text
pbond_feldspar
pbond_quartz
pbond_mica
pbond_boundary
```

Detailed group scheme:

```text
pbond_feldspar_feldspar
pbond_quartz_quartz
pbond_mica_mica
pbond_feldspar_quartz
pbond_feldspar_mica
pbond_quartz_mica
```

Use the detailed scheme when the user needs phase-pair-specific interfaces.

## Diagnostics

After grouping, export or report:

- target fraction per mineral
- achieved fraction per mineral
- number of balls per mineral
- number of contacts per contact group
- matrix/filling/interface contact fractions
- random seed
- cluster tolerance

## Common Traps

- matching particle counts instead of area/volume fractions with polydisperse balls
- using image pixel fractions without documenting excluded background pixels
- changing the random seed during calibration comparison
- assigning mineral groups before the final packing/contact network is stable
- applying contact properties before contacts are cleaned and grouped
- claiming exact digital image reconstruction when the method only preserves fractions and clustered distribution
