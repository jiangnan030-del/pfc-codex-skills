# Scope Template

Use this worksheet before writing PFC command flow. Keep the generic scope for every PFC project; use the exact CPB2D keys below when this scaffold applies.

## Problem definition

- Objective:
- Why DEM / PFC is needed:
- 2D or 3D:
- Material class:
- Structural complexity:

## Loading and boundary plan

- Test type:
- Boundary condition type:
- Control mode:
- Target endpoint or stop criterion:

## Observables

- Primary targets:
- Secondary targets:
- Required plots:
- Required exported tables:

## Reproducibility

- Random seed policy:
- Save-state stages:
- Path/config strategy:
- External tools required:

## CPB2D `load_intake` worksheet

Do not rename these keys or create aliases. Values in mm and Pa are converted by the scaffold where required. Experimental paths must remain under `data/experimental/`.

### `project`

- `slug`:
- `title`:
- `pfc_version`: `"6.0"`
- `random_seed_base`:

### `specimen`

- `width_mm`:
- `height_mm`:
- `particle_radius_min_mm`:
- `particle_radius_max_mm`:
- `target_porosity`:
- `density_kg_m3`:
- `damping`:

### `contact_model`

- `family`: `linearpbond`
- `linear_emod_pa`:
- `bond_emod_pa`:
- `kratio`:
- `pb_ten_pa`:
- `pb_coh_pa`:
- `pb_fa_deg`:
- `friction`:

### `loading`

- `wall_velocity_m_s`:
- `peak_drop_fraction`:
- `target_peak_strain_guess`:
- `stage_fractions`: `[0.25, 0.50, 0.75, 0.90]`
- `history_interval`:

### `outputs`

- `stress_strain`: `true`
- `crack_counts`: `true`
- `heavy_ae`: `false`

### `cases[]`

Repeat this exact set for each case. The first enabled case must be `intact`. Straight-crack geometry fields may be null only when the selected family does not require them.

- `case_name`:
- `family`:
- `enabled`:
- `experiment_file`: `data/experimental/...`
- `crack_enabled`:
- `crack_type`:
- `angle_deg`:
- `distance_mm`:
- `length_mm`:
- `width_mm`:
- `center_x_mm`:
- `center_y_mm`:

### `assumptions`

- `assumptions`: list every accepted default, unit interpretation, experimental column mapping, trial seed, and unresolved choice as a separate single-line string.

## Gate record

- Static validation status: pending / passed / failed
- First PFC runtime target: `pfc_cases/intact/run_all.dat`
- PFC2D 6.0 runtime status: unverified / passed / failed
- Runtime evidence (build, saves, CSV):
- Crack batch, calibration, postprocessing, and AE remain blocked until intact runtime passes: yes / no
