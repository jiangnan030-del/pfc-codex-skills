# Plotting

## Default figure families

### 1. Stress-strain response

Use separate or stacked figures for:

- direct tension / axial tension
- uniaxial compression
- triaxial compression at multiple confining pressures

Suggested axes:

- x-axis: axial strain or tensile strain
- y-axis: axial stress or tensile stress in MPa

Recommended outputs:

- `ecm_tension_curve.png`
- `ecm_compression_curves.png`

### 2. Crack-distribution figure

Purpose: show where cracks localize and how interface-driven failure differs from interior particle-bond failure.

Suggested layers:

- tensile cracks
- shear cracks
- optional distinction between crystal-boundary and crystal-body failure

Recommended output:

- `ecm_crack_distribution.png`

### 3. Laboratory vs simulation comparison

Purpose: compare macro failure mode and crack path.

Suggested layout:

- left: laboratory specimen failure photo or schematic
- right: simulation crack map

Recommended output:

- `ecm_lab_vs_sim.png`

### 4. Hoek-Brown fit

Purpose: show that the equivalent-crystal results follow a nonlinear envelope.

- x-axis: $\sigma_3$
- y-axis: $\sigma_1$
- series: simulation points and nonlinear fit

Recommended output:

- `ecm_hb_fit.png`

### 5. Compression-tension ratio summary

Purpose: compare equivalent-crystal, laboratory brittle rock, and standard BPM.

Recommended output:

- `ecm_ratio_comparison.png`

Inputs:

- UCS values
- TS values
- optional standard BPM reference values

## Output contract

Each figure should state:

- loading condition
- confining pressure when applicable
- whether the curve is laboratory or simulation derived
- whether crack colors correspond to tension/shear or to crystal-body/interface mechanisms
