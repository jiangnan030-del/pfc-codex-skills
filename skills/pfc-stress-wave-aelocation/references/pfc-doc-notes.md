# PFC Documentation Notes

These notes summarize PFC command families checked with `pfc-mcp` for stress-wave propagation and AE source-location workflows. Verify exact syntax in the installed PFC version before production runs.

## Dynamic Configuration

### `model configure dynamic`

- Enables dynamic material analysis features when supported by the installed version/license.
- Use before `model dynamic` commands in dynamic wave-propagation cases.

### `model dynamic`

- Sets parameters for dynamic material analysis.
- Available only after dynamic configuration and when the Dynamic Option is present.

### `model mechanical timestep`

- Controls mechanical timestep behavior.
- For wave-speed studies, use a documented fixed timestep or a verified stable automatic timestep.
- Do not use mass scaling for physical arrival-time studies.

### `model mechanical time-total`

- Resets or controls accumulated mechanical time.
- Reset to zero before source excitation when the waveform is a function of time.

## Cycling And Loading

### `model cycle` / `model step`

- Executes a fixed number of timesteps.
- Prefer explicit cycle/time duration for wave propagation rather than quasi-static solve criteria.

### `model solve`

- Can run until cycle, time, or custom criteria are reached.
- For dynamic wave windows, document the intended duration and stop condition.

### `ball attribute` / `wall attribute`

- Set velocity, displacement, spin, damping, density, or other object attributes.
- Use velocity or force histories carefully and reset dynamic states before each source test.

## FISH Waveforms And Histories

### `fish define`

- Define Ricker wavelets, sine sources, absorbing-boundary forces, custom monitors, and localization exports.

### `fish callback`

- Add/remove functions during cycle points or events.
- Use callbacks for source application and absorbing-boundary force updates.
- Remove callbacks after the source duration or before switching stages.

### `fish history`

- Records FISH scalar variables, including waveform value, computed time delay, or custom monitor values.

### `ball history` / `wall history`

- Records particle or wall displacement, velocity, force, and other quantities by ID, name, or position.
- Use for sensor signals when the monitored object is a ball or wall.

### `measure history`

- Records region-level quantities such as stress, strain rate, porosity, and position.
- Useful for plate/specimen diagnostics but less direct than ball histories for AE waveform timing.

## Energies And Export

### `model energy`

- Enables mechanical energy tracking.
- Use when comparing source input, boundary work, kinetic energy, and wave attenuation.

### `history export`

- Exports recorded histories to a file or table.
- Required for Python cross-correlation and plotting.

### `table export`

- Exports table data to a file.
- Useful if FISH callbacks write time-series values into tables rather than histories.

## Modular Files

### `program call`

- Use to separate model construction, source definition, boundary definition, wave run, history export, and localization post-processing.

Recommended staged pattern:

```text
program call 'build_wave_model.dat'
program call 'ricker_source.p2fis'
program call 'absorbing_boundary.p2fis'
program call 'run_wave_export.dat'
```

## Audit Checklist

Before running:

```text
model list
fish list symbols
history list
```

During/after running:

```text
history export file 'sensor_histories.csv'
table export 'waveform_table' 'waveforms.tab'
```

Record the PFC version, timestep, source frequency, particle spacing, damping, and boundary assumptions with every exported waveform set.
