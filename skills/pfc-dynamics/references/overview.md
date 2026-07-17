# Overview

## Purpose

`pfc-dynamics` provides reusable PFC dynamic-loading guidance. It is a child skill of `pfc-workflow`; it supplies targeted seismic, slope-motion, damping, timestep, and blasting-reference expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- static-to-dynamic stage separation
- slope/seismic dynamic demonstrations
- imposed wall/particle velocity and waveform-style loading assumptions
- damping, calm, timestep, and duration checks
- dynamic response histories
- blasting/demolition reference audits
- rate-aware caveats for legacy snippets

This skill does not own:

- full case lifecycle orchestration
- detailed FISH callback implementation beyond dynamic assumptions
- fluid or FLAC coupling
- standard mechanical-test template selection
- post-processing figure generation
- AE/energy/source-mechanism analysis

## Documentation Enrichment

PFC 6.0 command documentation was queried through `pfc-mcp` while building this skill. The resulting command notes are summarized in `references/dynamics-doc-notes.md`.

Key checked commands:

- `model configure dynamic`
- `model dynamic`
- `model mechanical`
- `model cycle` / `model step`
- `model solve`
- `model calm`
- `ball attribute`
- `wall attribute`
- `model history`, `ball history`, and `wall history`

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/slope-seismic-pfc6/`
- `scripts/canonical/demolition-blasting-reference/`

Included PFC 6.0 baseline files:

- `1diji.dat`: creates the particle assembly and static foundation state.
- `2xuepo.dat`: restores the foundation state, cuts/deletes slope material, solves, and saves a slope state.
- `3dizhen.dat`: restores the slope state, reduces damping, resets mechanical time, and applies sinusoidal wall velocity through FISH logic for a two-second dynamic response.

Included demolition/blasting reference files:

- `crk.FIS`: legacy crack-tracking package.
- `fishcall.FIS`: legacy FISH callback macro definitions.
- `flt.FIS`: legacy floater elimination utilities.
- `demolition_model_build.txt`: large legacy model construction source reference with normalized filename.

Legacy files are included as readable references and should be audited before direct use in PFC 6.0.

## Recommended Dynamic Pattern

1. Build and solve the static model.
2. Save the prepared state.
3. Restore prepared state for the dynamic stage.
4. Configure dynamic mode if the target case needs fully dynamic analysis.
5. Reset mechanical time if a waveform or callback uses time.
6. Define input motion and damping explicitly.
7. Record time, timestep, input motion, kinetic energy, strain energy, displacement, velocity, and force histories.
8. Solve for the intended duration or cycle count.

## Dynamic Risk Notes

- High damping used for static preparation can suppress physical dynamic response.
- `model calm` removes kinetic energy and should not be used inside a response window unless intended.
- Fixed timestep choices must be justified by stability and waveform resolution.
- A running slope-removal or demolition case is not automatically a validated seismic/blasting model.
- Legacy callback and crack-tracking packages may require syntax/intrinsic updates before PFC 6.0 use.

## Inclusion Rules

- Keep minimal `.dat`, `.FIS`, and source-like `.txt` files needed to understand the workflow.
- Do not bundle generated save states, project metadata, videos, PDFs, archives, or large output dumps as authoritative assets.
- Preserve legacy files as references only when they add coverage not already present in PFC 6.0 examples.
- Keep loading definition, damping, timestep, and output histories explicit.

## Handoff To pfc-workflow

After this skill provides a dynamic-stage plan or snippets, return to `pfc-workflow` for:

- full case directory creation
- specialist FISH/coupling routing if needed
- solve management
- post-processing route selection
- V&V and delivery
