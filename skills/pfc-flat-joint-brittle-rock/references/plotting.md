# Plotting

## Default figure families

### 1. FJM structure schematic

Purpose: explain abstract interfaces, discretized elements, and improved interlocking/rotation behavior.

Recommended output:

- `fjm_structure_schematic.png`

### 2. Parameter-effect plots

Suggested parameter sweeps:

- installation-gap ratio
- crack density
- local strength
- local friction angle
- residual friction angle

Suggested observables:

- tensile strength
- crack count or crack mode fraction
- peak stress
- failure-pattern descriptors

Recommended outputs:

- `fjm_parameter_sweep.png`
- `fjm_microparameter_response.png`

### 3. Brazilian-test figure set

Purpose: show tensile failure process and parameter sensitivity.

Suggested plots:

- load-displacement or stress-displacement curve
- crack-evolution snapshots
- radial or horizontal stress interpretation plot

Recommended outputs:

- `fjm_brazilian_curve.png`
- `fjm_brazilian_cracks.png`
- `fjm_brazilian_stress_field.png`

### 4. Uniaxial / triaxial validation figures

- x-axis: strain
- y-axis: stress in MPa
- optional crack overlay at selected stages

Recommended outputs:

- `fjm_uniaxial_triaxial_curves.png`
- `fjm_failure_modes.png`

### 5. Core-discing figures

Purpose: compare discing patterns across stress states.

Suggested grouping:

- hydrostatic pressure case
- equal horizontal principal stress case
- unequal principal stress case

Recommended outputs:

- `fjm_core_discing_modes.png`
- `fjm_core_discing_comparison.png`

## Output contract

Every figure should specify:

- loading path or stress state
- controlled parameter and response metric
- whether the image is conceptual, parametric, or calibrated simulation output
- the crack legend if multiple crack modes are shown
