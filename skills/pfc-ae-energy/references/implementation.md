# Implementation

## Route Selection

Choose the lightest route that satisfies the question.

### Level 1: AE Hits

Each bond break is one AE hit.

Use when outputs are:

- cumulative crack count
- tension/shear crack count
- first-crack point
- AE hit rate
- simple AE spatial map

### Level 2: Clustered AE Events

Nearby hits in time and space become one AE event.

Use when outputs are:

- event duration
- event center
- event size distribution
- stage-wise event count
- event-level maps rather than raw crack maps

### Level 3: Moment Tensor

Clustered events receive tensor-derived source metrics.

Use when outputs are:

- scalar moment and moment magnitude
- T-k or Hudson source-type plots
- tensile/shear/mixed mechanism labels from tensor decomposition
- stage-wise source-type fractions
- paper-grade source-mechanism interpretation

## PFC Instrumentation Pattern

Default pattern:

1. restore a calibrated bonded specimen
2. define global counters and event arrays
3. optionally cache pre-break contact force state
4. register a bond-break or contact-event callback
5. on each break, record time, strain, stress, position, failure mode, and local contact information
6. write FISH histories for cumulative crack counts
7. export `stress_strain.csv` and `ae_events.csv`
8. cluster and compute tensor quantities in Python when possible

The exact callback event name and registration syntax must be verified for the target PFC version. See `references/ae-doc-notes.md`.

## Heavy AE Template Set

For the rigorous moment-tensor route, use the template bundle under `templates/heavy-ae/`:

- `fracture-heavy-mt.p2fis`
- `export-heavy-ae-4export.dat`
- `3load-history-snippet.dat`
- `plot_ae_energy.py`

These files are meant to be applied together, not one by one.

## Recommended Exports

### Required For Level 1

- `stress_strain.csv`
- `ae_events.csv` or raw hit table
- cumulative crack or AE count histories

### Required For Level 2

- all Level 1 exports
- `ae_clustered_events.csv`
- clustering parameter record: time window, spatial threshold, stage rule

### Required For Level 3

- all Level 2 exports
- tensor columns: `mt_xx`, `mt_yy`, `mt_zz`, `mt_xy`, `mt_xz`, `mt_yz`
- tensor-derived columns: `M0`, `Mw`, `T`, `k`, and `source_type`

### Recommended `ae_events.csv` Columns

```text
id,time,strain,stress_mpa,x,y,z,mode,mode_label,pbstrain_energy,
mt_xx,mt_yy,mt_zz,mt_xy,mt_xz,mt_yz
```

For 2D models, use a documented convention for unavailable `z`, `mt_zz`, `mt_xz`, and `mt_yz` fields.

### Recommended `stress_strain.csv` Columns

```text
strain,stress_mpa,crack_num,crack_tension_num,crack_shear_num
```

## Moment Tensor Computation Pattern

For each clustered event:

1. determine the event center
2. collect participating contact-force changes `DeltaF`
3. collect lever arms `R` from event center to contact points
4. compute `M = sum(outer(DeltaF, R))`
5. symmetrize `M`
6. compute eigenvalues, scalar moment, magnitude, T-k, and source type
7. write event-level results to `ae_clustered_events.csv`

Prefer Python for eigenvalue decomposition and plotting. Keep FISH focused on data capture and stable export.

## Post-Processing Pattern

Use Python to compute:

- cumulative AE from cumulative counters
- AE hit rate as numerical derivative with respect to strain or time
- space-time clustering from AE hits to event catalogs
- scalar moment and moment magnitude from tensor eigenvalues
- T-k parameters and source-type classification
- rupture/source orientation from tensor eigenvectors
- total input energy density from cumulative trapezoidal integration of stress-strain
- elastic energy density from a fitted elastic modulus
- dissipated energy density as `input - elastic`

## Orientation Plot Implementation

The heavy-AE template now includes `plot_ae_orientation`, which is called after T-k and Hudson plots are generated.

Implementation notes:

- reconstruct the 3 x 3 moment tensor from `mt_xx`, `mt_yy`, `mt_zz`, `mt_xy`, `mt_xz`, and `mt_yz`
- compute eigenvectors using `numpy.linalg.eigh`
- use the maximum eigenvalue vector as the `T axis` and the minimum eigenvalue vector as the `P axis`
- fold undirected axes to a 0-180 degree azimuth convention
- write `ae_orientation_axes.csv` for source-data traceability
- export `ae_orientation_stereonet` and `ae_orientation_moment_polar` in PNG, SVG, PDF, and TIFF
- keep SVG text editable and PDF fonts as TrueType for publication editing

For 2D PFC data, out-of-plane tensor terms are commonly zero, so most points lie on or near a planar projection. This should be documented rather than treated as a plotting failure.

## Common Traps

- peak saved before the intended AE stage markers
- units mixed between `m` and `mm`
- event arrays not initialized before callback registration
- copying only `fracture-heavy-mt.p2fis` but forgetting matching load histories and export file changes
- claiming AE events when no clustering logic exists
- claiming moment-tensor physics when only raw crack hits were recorded
- storing every timestep tensor and exhausting memory
- changing clustering thresholds between compared cases

## Good Wording

- say `AE hits` for raw bond-break counts
- say `AE events` only when clustering logic exists
- say `macro energy density` when computed from stress-strain
- say `scalar moment` or `moment magnitude` when tensor columns exist
- say `event size proxy` when using non-rigorous local indicators
