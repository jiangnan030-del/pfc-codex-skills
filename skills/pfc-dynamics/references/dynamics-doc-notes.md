# Dynamics Documentation Notes

These notes summarize PFC command documentation points checked through `pfc-mcp` for PFC 6.0. Treat them as usage guidance, not a replacement for the official manual.

## Core Commands Checked

### `model configure dynamic`

- `model configure` enables additional calculation modes.
- `dynamic` is the keyword for fully dynamic analysis.
- Configuration must be specified before dynamic cycling/solving that depends on the dynamic option.
- Dynamic analysis may require the corresponding Itasca license option.

Pattern:

```text
model new
model configure dynamic
; create geometry, particles, contacts, boundaries
model cycle 1
```

### `model dynamic`

- Sets parameters for a dynamic material analysis.
- Available only after `model configure dynamic` and when the Dynamic Option is present.
- Use this command family for dynamic-specific settings before the dynamic stage.

### `model mechanical`

- Mechanical analysis is active by default.
- `model mechanical time-total 0.0` resets accumulated mechanical time before a new loading/dynamic stage.
- `model mechanical timestep ...` controls timestep behavior. PFC examples include automatic timestep, fixed timestep, increment, maximum, safety-factor, and timestep scaling.
- Dynamic cases should document timestep assumptions explicitly.

### `model cycle` / `model step`

- Executes a fixed number of timesteps.
- `model step` is a synonym for `model cycle`.
- The optional `calm <i>` keyword resets linear and angular velocities every `i` cycles for mechanical processes.
- Do not use aggressive `calm` during the dynamic response stage unless the damping/removal of kinetic energy is physically intended.

### `model solve`

- Cycles until one or more stop criteria are reached.
- Without `and`, solving stops when any listed criterion is met; with `and`, all criteria must be met.
- `cycles`, `time`, and equilibrium-style criteria should be chosen according to the dynamic loading goal.

### `model calm`

- Sets linear and rotational velocities to zero for mechanical processes.
- Useful before switching from equilibrium preparation to a new loading stage.
- Usually inappropriate inside the actual dynamic response window unless intentionally removing kinetic energy.

### `ball attribute`

- Sets ball attributes and is a synonym for `ball initialize`.
- Important dynamic attributes include density, damping, displacement, velocity, force-applied, and spin.
- Nonzero density is required for mass/inertia and equation-of-motion integration.
- Local damping (`damp`) affects energy dissipation and must be justified for dynamic studies.

### `wall attribute`

- Sets wall attributes and is a synonym for `wall initialize`.
- Important dynamic-loading attributes include translational velocity, angular velocity/spin, displacement, and rotation center.
- Wall velocities are a common route for imposed motion or simplified waveform loading.

### Histories

- `model history` can record timestep, mechanical time, cycles, force ratio, unbalanced force, and mechanical energy partitions including kinetic and strain energy.
- `ball history` can record position, displacement, velocity, and unbalanced force for selected particles.
- `wall history` can record displacement, velocity, spin, and contact force for selected walls.
- Dynamic cases should include time, timestep, kinetic energy, input motion, and response histories.

## Dynamic Authoring Guidance

- Separate static preparation from dynamic loading.
- Reset mechanical time before the dynamic stage when interpreting waveforms or imposed velocities.
- Reduce damping before dynamic response if the static preparation used high local damping.
- Record input and response histories at a sampling interval compatible with the waveform.
- Track timestep stability and kinetic/strain energy during dynamic stages.
- Avoid treating a static slope-removal case as a validated dynamic/seismic model unless loading, damping, timestep, and histories are documented.

## Minimal Dynamic Stage Pattern

```text
model restore 'prepared_state'
model configure dynamic
ball attribute damp 0.1
model mechanical time-total 0.0

fish define update_input
  ; use mechanical time to compute imposed motion
end
fish callback add update_input <cycle-point-or-event>

model history name 'mech_time' mechanical time-total
model history name 'kinetic' mechanical energy energy-kinetic
model history name 'timestep' timestep
model solve time <duration>
```

The exact callback event and command syntax must be checked for the target PFC version and case dimensionality.
