# Plotting

## Default figure families

### 1. UCS-TS contrast figure

Purpose: show that brittle rock has a high compression-tension ratio while standard BPM often predicts a much lower ratio.

- x-axis: specimen, model case, or calibration route
- y-axis: strength in MPa
- series: UCS and TS side-by-side
- derived annotation: UCS/TS ratio
- recommended output: `ucs_ts_contrast.png`

Inputs:

- uniaxial compressive strength
- tensile strength from direct tension or Brazilian-equivalent conversion

### 2. Strength-envelope comparison

Purpose: compare a linear BPM envelope against a nonlinear brittle-rock envelope.

- x-axis: confining stress $\sigma_3$
- y-axis: major principal stress $\sigma_1$
- series: standard BPM fit, laboratory fit, optional Hoek-Brown fit
- recommended output: `strength_envelope_comparison.png`

Inputs:

- triaxial strength points
- fitted parameters or directly tabulated envelope points

### 3. BPM mechanism sketch

Purpose: explain the standard BPM bond-force and bond-failure logic.

- use a conceptual diagram rather than a measured plot
- annotate normal force, shear force, bending moment, and failure modes
- recommended output: `bpm_mechanism_schematic.png`

### 4. Defect mapping panel

Purpose: tie each known BPM deficiency to an observable plot.

Suggested 2x2 panel:

- low compression-tension ratio
- low macroscopic friction angle
- overly linear strength envelope
- mismatch between brittle-rock traits and BPM assumptions

- recommended output: `bpm_limitations_panel.png`

## Output contract

For each plot, include:

- data source label: lab, simulation, or conceptual
- units on both axes
- model name and parameter set if simulation-derived
- one-sentence caption stating what mismatch or mechanism the figure is meant to expose
