---
name: pfc-dynamics
description: Child skill of pfc-workflow for PFC 6.0 dynamic loading, seismic/slope-motion examples, damping/timestep checks, and blasting-style reference audits.
---

# PFC Dynamics

Use this skill to explain, adapt, or generate PFC dynamic-loading workflows. The skill is self-contained: PFC 6.0 slope/seismic examples and blasting reference snippets are stored under `scripts/canonical/`, and documentation notes checked through `pfc-mcp` are stored under `references/dynamics-doc-notes.md`.

## Parent Skill Relationship

`pfc-dynamics` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for dynamic/seismic scenario selection, imposed motion, damping, timestep, dynamic histories, and blasting-style reference audits. Return to `pfc-workflow` for full case planning, solve orchestration, post-processing routing, verification, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns complete PFC project lifecycle and decides when dynamic support is needed.
- Child `pfc-dynamics`: owns dynamic loading, seismic/waveform patterns, damping and timestep assumptions, response histories, and rate-aware caveats.
- Sibling child `pfc-fish`: owns detailed FISH helper/callback implementation when dynamic loading needs nontrivial code.
- Sibling child `pfc-standard-tests`: owns standard mechanical-test templates and stage normalization.
- Sibling child `pfc-servo-calibration`: owns servo control and manual calibration sequencing.
- Sibling child `pfc-fluid-coupling`: owns PFC CFD/seepage/buoyancy workflows.
- Sibling child `pfc-flac-coupling`: owns PFC-FLAC/FLAC3D discrete-continuum coupling.
- Sibling child `pfc-postprocessing`: owns standard figures and field exports after solve.
- Sibling child `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs after solve.

## When To Use

Use through `pfc-workflow` when a task involves time-dependent inertial response:

- slope motion or collapse after geometry removal
- seismic or waveform-style imposed velocity/displacement
- dynamic wall/ball velocity loading
- damping and timestep audits
- kinetic/strain energy history setup
- blasting, demolition, or fragmentation reference review
- rate-aware caveats for legacy command flows

## Required Inputs

Ask for these if missing:

- PFC version and dimensionality: PFC2D/PFC3D and target major version.
- Dynamic scenario: slope, seismic input, impact, blasting/demolition, vibration, or custom.
- Loading definition: velocity, displacement, force, waveform, callback, or table/file input.
- Static preparation stage and saved state before dynamic loading.
- Damping assumptions: local damping, contact damping, dashpots, calm usage, and whether damping changes between stages.
- Timestep assumptions: automatic/fixed timestep, target duration, output interval, and stability checks.
- Required histories: time, timestep, input motion, kinetic energy, strain energy, displacement, velocity, force, and damage/crack counts.

## Documentation-Backed Rules

The following PFC 6.0 documentation points were checked through `pfc-mcp` and are expanded in `references/dynamics-doc-notes.md`:

- `model configure dynamic` enables fully dynamic analysis before dynamic solve/cycle usage.
- `model dynamic` sets parameters for dynamic material analysis and requires dynamic configuration/license support.
- `model mechanical time-total 0.0` resets accumulated mechanical time before a dynamic loading stage.
- `model mechanical timestep ...` controls timestep behavior; dynamic cases must document timestep assumptions.
- `model cycle` / `model step` execute fixed timesteps; `calm` removes velocities and should not be used casually during dynamic response.
- `model solve` supports cycle/time/criteria limits; dynamic stage duration should match the loading goal.
- `ball attribute` and `wall attribute` set density, damping, velocity, displacement, spin, and imposed motion quantities.
- `model history`, `ball history`, and `wall history` should capture timestep, time, kinetic energy, input, and response signals.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| PFC 6.0 slope/seismic baseline | `scripts/canonical/slope-seismic-pfc6/` | `1diji.dat`, `2xuepo.dat`, `3dizhen.dat` | Static particle slope preparation, slope cut/removal, and sinusoidal wall-velocity dynamic loading. |
| Demolition/blasting reference | `scripts/canonical/demolition-blasting-reference/` | `crk.FIS`, `fishcall.FIS`, `flt.FIS`, `demolition_model_build.txt` | Legacy crack tracking, fishcall macros, floater cleanup, and large demolition model source reference; audit before using in PFC 6.0. |

## Dynamic Checklist

Use this checklist before writing or changing dynamic logic:

1. Build and solve the static preparation stage first.
2. Save the prepared state before dynamic loading.
3. Reset mechanical time if the loading function depends on time.
4. Define input motion explicitly: amplitude, frequency, duration, direction, and units.
5. Decide whether dynamic mode must be configured and confirm the target license/version supports it.
6. Reduce or justify damping for dynamic response if high damping was used during preparation.
7. Avoid `model calm` inside the response stage unless kinetic energy removal is intended.
8. Record input, time, timestep, kinetic energy, strain energy, displacement/velocity, and force histories.
9. State whether the case is a physical dynamic model or a teaching/reference demonstration.

## Working Rules

- Prefer PFC 6.0-safe syntax unless the user explicitly targets another version.
- Treat files in `scripts/canonical/` as reference templates, not final calibrated models.
- Route complex FISH waveform/callback implementation to `pfc-fish`, then return here for dynamic assumptions.
- Do not publish generated `.sav`, project metadata, videos, PDFs, archives, or large output dumps as authoritative assets.
- For legacy blasting/demolition snippets, preserve intent but audit syntax, callbacks, crack logic, and object intrinsics before PFC 6.0 use.
- If the task becomes a full model run or validation study, hand control back to `pfc-workflow`.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- The selected dynamic pattern and why it fits.
- Required files or snippets from `scripts/canonical/<case>/`.
- Static preparation state, dynamic loading definition, damping, timestep, and duration.
- History outputs for input and response validation.
- Version compatibility and legacy-audit notes.
- Minimal validation steps.
- A clear note that full case execution, post-processing routing, V&V, and delivery continue in `pfc-workflow`.

## Local Contents

- `references/overview.md`: detailed self-contained dynamics boundaries and source map.
- `references/dynamics-doc-notes.md`: PFC 6.0 command notes checked through `pfc-mcp`.
- `examples/README.md`: how to validate bundled dynamics demonstrations.
- `scripts/canonical/`: PFC dynamics and blasting reference snippets.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
