# Source-Type And Orientation Plots

Use this reference when a case has tensor-derived AE events and the user asks for source mechanism, T-k plots, Hudson-style diagrams, rupture/source orientation, stereonet-style principal-axis plots, or stage-wise mechanism fractions.

## Required Inputs

A source-type plot requires an event table with one tensor or tensor-derived row per clustered AE event.

Minimum columns:

```text
event_id,time,strain,stress_mpa,x,y,z,mt_xx,mt_yy,mt_zz,mt_xy,mt_xz,mt_yz
```

Recommended derived columns:

```text
M0,Mw,T,k,epsilon,R,P_DC,source_type,stage,n_hits
```

If tensor columns are missing, do not create a source-type plot. Use AE hit maps or crack-mode statistics instead.

## T-k Plot

The T-k plot uses two parameters from moment-tensor eigenvalues:

- `T`: deviatoric source-type coordinate
- `k`: isotropic or volumetric coordinate

Expected ranges are approximately:

```text
-1 <= T <= 1
-1 <= k <= 1
```

Plotting conventions:

- x-axis: `T`
- y-axis: `k`
- point color or marker: source type
- point size: scalar moment or moment magnitude
- optional facet or panel: loading stage

## Four-Class Partition

A practical partition used by the source material is:

```text
linear_tensile: -1 <= T <= -0.4 and 0.2 <= k <= 0.4
linear_shear:    0.4 <= T <= 1    and -0.4 <= k <= -0.2
dc_shear:       -0.2 <= T <= 0.2 and -0.2 <= k <= 0.2
mixed:          all other valid points
```

Use these labels consistently in CSV, plots, legends, and report text.

## Hudson-Style Diamond Plot

A Hudson-style source-type plot maps tensor-derived quantities onto a skewed diamond. In the current heavy-AE post-processing route, the Chinese figure `ae_tk_diamond_cn.*` is the preferred paper-facing plot.

Expected outputs:

- `ae_tk_diamond_cn.png`
- `ae_tk_diamond_cn.svg`
- `ae_tk_diamond_cn.pdf`
- `ae_tk_diamond_cn.tiff`
- `ae_tk_diamond_cn_source_data.csv`

Use the bundled `templates/heavy-ae/plot_ae_energy.py` implementation unless the case requires a different journal style.

## Rupture / Source Orientation Plot

Use the orientation plot when tensor eigenvectors are available and the user asks for a figure like the AE moment-tensor rupture orientation or source-orientation diagram.

The bundled Python implementation computes eigenvectors from each event tensor:

- maximum eigenvalue eigenvector: `T axis` tendency
- minimum eigenvalue eigenvector: `P axis` tendency

It then writes:

- `ae_orientation_stereonet.png/svg/pdf/tiff`: circular stereonet-style projection with `N/E/S/W` labels and an `O` center label.
- `ae_orientation_moment_polar.png/svg/pdf/tiff`: axis azimuth plot with radial distance scaled by scalar moment and colors by source type.
- `ae_orientation_axes.csv`: source data containing event ID, axis label, azimuth, projected coordinates, scalar moment, moment magnitude, source type, and stage.

For PFC2D tensor data, `mt_zz`, `mt_xz`, and `mt_yz` may be zero. In that case, the stereonet-style plot behaves mainly as a 2D orientation projection, which is expected. Full PFC3D tensor data will populate the lower-hemisphere projection more completely.

## Stage-Wise Mechanism Figures

Recommended mechanism summaries:

- event count by source type and stage
- fraction by source type and stage
- mean or median moment magnitude by source type and stage
- cumulative mechanism evolution over strain or time

Interpretation guidance:

- tensile events may dominate counts in bonded-particle rock models
- shear and mixed events may become more important near and after peak stress
- larger shear/mixed magnitudes near peak can be more informative than raw counts alone

## Beachball Or Orientation Plots

Only add beachball or source-axis plots when the implementation computes stable eigenvectors or nodal-plane equivalents. If only T-k and scalar moment are available, avoid implying full focal-mechanism orientation.

## Quality Checks

Before publishing a source-type figure:

- confirm tensor columns are finite and symmetrized
- confirm eigenvalue ordering is consistent
- confirm units and magnitude scaling are documented
- confirm all plotted events have stage labels
- confirm legends distinguish raw hit mode from tensor-derived source type
- confirm the same classification thresholds are used across cases being compared
