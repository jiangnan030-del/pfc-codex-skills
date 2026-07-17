# Outputs

## Minimum figure set

### 1. Stress-AE overview

One figure with:

- stress-strain curve
- cumulative AE on the secondary axis
- optional stage markers

### 2. AE rate figure

Plot total AE hit rate and, if available, tension and shear hit rates.

### 3. Energy figure

Plot:

- total input energy density
- elastic energy density
- dissipated energy density

### 4. AE spatial map

Scatter or stage-wise map of event positions:

- color by stress, strain, or stage
- symbol by tension vs shear
- size by magnitude or size proxy

## Minimum table set

- total AE hits
- tension AE hits
- shear AE hits
- first-crack strain and stress
- strain of peak AE rate
- peak and final energy-density indicators

## Paper-grade extensions

Only add these when the workflow truly supports them:

- source-type `T-k` map
- Chinese Hudson `u-v` source-mechanism plot with curved grid and guide lines
- mechanism fractions by stage
- magnitude-frequency relation
- stage-wise cumulative event maps
- tensor-derived tensile / shear / double-couple shear / mixed classification
- scalar moment and moment magnitude summaries
- clustering parameter record and event-size distribution

Do not create source-mechanism plots when only raw crack mode labels are available. Tensor-derived source type requires tensor columns, eigenvalue processing, and documented classification thresholds.

## Current heavy-AE figure contract

When the project already has full tensor columns in `ae_events.csv`, the
current bundled Python post-processing route should also emit:

- `ae_source_event_map.png/svg/pdf`
- `ae_tk_source_map.png/svg/pdf`
- `ae_tk_diamond_cn.png/svg/pdf/tiff`
- `ae_orientation_stereonet.png/svg/pdf/tiff`
- `ae_orientation_moment_polar.png/svg/pdf/tiff`
- `ae_orientation_axes.csv`
- `ae_tk_diamond_cn_source_data.csv`

The Chinese Hudson plot uses the current `templates/heavy-ae/plot_ae_energy.py`
implementation, including:

- clustered AE events with tensor-derived source types
- scalar moment and moment magnitude point scaling
- curved Hudson-style `u-v` grid
- special point handling for `(-2/3,-2/3)` and `(2/3,2/3)` on the skewed diamond edge
- guide lines drawn directly in `u-v` space for paper-style annotation topology

## Required Level Labels

Use these terms consistently in filenames, captions, and reports:

- `AE hit`: raw bond break or crack callback record.
- `AE event`: time-space clustered group of one or more hits.
- `source type`: tensor-derived mechanism label.
- `rupture/source orientation`: principal-axis direction derived from tensor eigenvectors.
- `crack mode`: raw contact/bond failure mode such as tension or shear.
- `macro energy density`: stress-strain integral and elastic/dissipated partitions.
- `event size`: scalar moment, moment magnitude, or explicitly named proxy.
