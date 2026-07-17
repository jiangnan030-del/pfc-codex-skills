---
name: pfc-stress-wave-aelocation
description: Child skill of pfc-workflow for PFC stress-wave propagation and velocity-free acoustic-emission source localization: 1D/2D wave models, Ricker excitation, dispersion checks, absorbing boundaries, P/S wavefronts, radiation patterns, Kundu localization, arbitrary-triangle sensor layouts, and cross-correlation arrival-time differences.
---

# PFC Stress Wave And AE Location

Use this skill to design, explain, or implement stress-wave propagation and acoustic-emission (AE) source localization workflows in PFC. It covers elastic wave propagation, numerical dispersion, source excitation, boundary reflection/absorption, P/S wavefront and radiation-pattern checks, and 2D velocity-free AE source location from sensor-cluster time delays.

## Parent Skill Relationship

`pfc-stress-wave-aelocation` is a child skill of `pfc-workflow`. It owns the elastic-wave and source-location specialist portion, not the full model lifecycle.

Use these handoffs:

- Parent `pfc-workflow`: owns full planning, calibration, solve campaign control, V&V, and delivery.
- Sibling `pfc-dynamics`: owns general dynamic/seismic loading, damping/timestep audits, and inertial response assumptions.
- Sibling `pfc-ae-energy`: owns AE hit/event tables, energy figures, moment tensors, T-k/Hudson/source-mechanism plots.
- Sibling `pfc-fish`: owns waveform callbacks, absorbing-boundary FISH, histories, tables, and reusable helper refactoring.
- Sibling `pfc-contact-models`: owns bonded/flat-joint contact model setup and property audits.
- Sibling `pfc-postprocessing`: owns wavefield, waveform, error-map, and summary figures after export.
- Sibling `pfc-gbm-brittle-rock` or `pfc-flat-joint-brittle-rock`: owns brittle-rock GBM/FJM specimen construction if the wave source is embedded in those models.

## When To Use

Use through `pfc-workflow` when the task asks to:

- simulate stress-wave, elastic-wave, seismic-wave, ultrasonic, or blasting-wave propagation in PFC
- compare P-wave/S-wave speed, wavefronts, attenuation, dispersion, or radiation patterns
- generate sine or Ricker wavelet sources in FISH
- design absorbing, free, or rigid boundaries for wave propagation
- localize AE sources from sensor arrays or arrival-time differences
- use Kundu velocity-free localization or arbitrary-triangle sensor clusters
- compute time delay by cross-correlation
- validate a flat-joint plate or brittle-rock model with pencil-lead-break style source localization

## Required Inputs

Ask for these if missing:

- PFC version, dimensionality, and whether dynamic mode/license is available.
- Wave goal: 1D chain, 2D wavefront, source radiation pattern, boundary test, or AE location.
- Particle size / spacing and target maximum frequency for dispersion check.
- Contact model and elastic parameters for wave speed.
- Source type: sine, Ricker velocity, Ricker force, point force, wall motion, or bond-break source.
- Boundary type: rigid, free, absorbing, or long-enough domain.
- Sensor coordinates, sampling interval, and waveform export format for AE location.
- Error tolerance and source-location evaluation metric.

## Operating Rules

1. Check dispersion before model construction: use wavelength-to-particle spacing ratio `lambda / D >= 10` for accurate wave propagation.
2. Prefer Ricker wavelets over simple sine pulses when broadband high-frequency corners would cause strong numerical dispersion.
3. Turn off local damping for physical wave propagation unless the task explicitly studies attenuation.
4. Use small, fixed timesteps; do not use mass/density scaling for wave-speed studies.
5. Reset mechanical time before source excitation when the waveform depends on time.
6. Treat absorbing boundaries as part of the model, not an afterthought.
7. Use cross-correlation for cluster-internal time delays; avoid manual arrival picking when waveforms are similar.
8. For velocity-free localization, reject near-parallel cluster-pair rays and report geometry degeneracy.

## Core Workflow

1. Classify the task: wave propagation, source excitation, boundary behavior, wavefield/radiation pattern, or AE location.
2. Run the dispersion pre-check: estimate wave speed, maximum frequency, wavelength, and `lambda / D`.
3. Build the model: 1D chain, 2D hexagonal lattice, plate specimen, or calibrated brittle-rock specimen.
4. Configure dynamic assumptions: damping, timestep, mechanical time reset, histories, and export interval.
5. Add the source: Ricker velocity/force or another documented waveform.
6. Add boundaries: rigid/free/absorbing and document expected reflection behavior.
7. Export waveforms at monitors/sensors.
8. For AE location, compute time delays by cross-correlation.
9. Convert each sensor cluster to an arrival direction; intersect cluster rays for source candidates.
10. Filter poor geometry, compute location error, and hand off figures/tables to `pfc-postprocessing` or AE interpretation to `pfc-ae-energy`.

## Documentation-Backed Rules

PFC command families checked with `pfc-mcp` are summarized in `references/pfc-doc-notes.md`:

- `model configure dynamic`, `model dynamic`
- `model mechanical timestep`, `model mechanical time-total`
- `model cycle`, `model solve`
- `ball attribute`, `wall attribute`
- `fish define`, `fish callback`, `fish history`
- `ball history`, `wall history`, `measure history`
- `model energy`, `history export`, `table export`
- `program call`

## Formula And Code Migration Rules

When the request asks about theory, formulas, exact algorithms, or code migration, load these first:

- `references/wave-theory.md`: 1D and 2D wave speed, dispersion, boundary reflection, and radiation formulas.
- `references/source-excitation.md`: Ricker/sine source rules and FISH source templates.
- `references/ae-location.md`: Kundu and arbitrary-triangle velocity-free localization formulas.
- `references/cross-correlation.md`: time-delay estimation and Python implementation notes.
- `references/calibration-plate.md`: plate calibration, sensor layouts, and expected location accuracy.
- `scripts/canonical/`: reusable source, absorbing-boundary, localization, cross-correlation figure, and plotting templates.

## Output Contract

A complete handoff back to `pfc-workflow` should include:

- wave type and model type
- dispersion calculation and pass/fail status
- source waveform parameters and implementation route
- damping/timestep/dynamic-mode assumptions
- boundary condition and reflection/absorption expectation
- monitor/sensor layout
- exported waveform requirements
- localization method, time-delay algorithm, and geometry filters
- error metrics and recommended figures/tables

## Local Contents

- `references/wave-theory.md`: wave equations, speeds, dispersion, boundaries, and radiation patterns.
- `references/source-excitation.md`: sine/Ricker sources and PFC implementation templates.
- `references/ae-location.md`: velocity-free source-location formulas.
- `references/cross-correlation.md`: signal processing and Python implementation details.
- `references/calibration-plate.md`: granite/flat-joint plate parameters and sensor layouts.
- `references/pfc-doc-notes.md`: PFC 6.0 documentation notes checked through `pfc-mcp`.
- `examples/README.md`: materialization and validation patterns.
- `scripts/canonical/`: PFC/FISH/Python templates.
- `templates/`: YAML parameter templates for sensors and wave settings.
