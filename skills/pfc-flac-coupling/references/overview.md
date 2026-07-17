# Overview

## Purpose

`pfc-flac-coupling` provides reusable PFC-FLAC/FLAC3D coupling guidance. It is a child skill of `pfc-workflow`; it supplies targeted discrete-continuum handoff expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- PFC-FLAC/FLAC3D discrete-continuum coupling concepts
- continuum baseline setup before particle insertion
- `wall-zone` or interface-style handoff boundaries
- coupled saved-state sequencing
- command-flow contracts between continuum and particle stages
- version-risk notes for old project and save formats

This skill does not own:

- full case lifecycle orchestration
- PFC-only CFD/seepage coupling
- standard mechanical-test template selection
- general dynamics/blasting
- post-processing figure generation
- AE/energy/source-mechanism analysis

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/discrete-continuum-baseline/`
- `scripts/canonical/flac3d-pfc-chapter11/`

Included baseline files:

- `1dimian.dat`: creates a continuum ground/zone baseline, applies material properties and boundary constraints, solves, and saves the baseline state.
- `2luoshi .dat`: restores the baseline, creates a wall-zone coupling boundary, generates particles, assigns contact properties, and solves the coupled particle-continuum setup.

Included chapter-11 files:

- `11.*.txt`: readable FLAC3D/PFC coupling command snippets. Keep these as reference fragments until syntax and run order are audited for a target environment.

## Coupling Pattern

The minimal discrete-continuum pattern is:

1. Create continuum zones and assign constitutive model/properties.
2. Apply gravity and boundary constraints.
3. Solve continuum baseline and save it.
4. Restore baseline and create the particle-coupling boundary.
5. Generate particles and assign contact/material properties.
6. Solve coupled system and record both continuum and particle histories.

In the bundled baseline, `1dimian.dat` creates the continuum baseline and `2luoshi .dat` adds particles through `wall-zone create`.

## Version And Handoff Risks

- FLAC/PFC project and save files are version-sensitive; avoid making old binary states authoritative.
- Coupling commands may differ across Itasca major versions.
- `.txt` command snippets should be audited and, if needed, converted into stage-specific `.dat` files before public use.
- Decide explicitly whether FLAC/FLAC3D or PFC owns each boundary condition and each output.

## Inclusion Rules

- Keep minimal `.dat` and readable command snippets needed to understand the workflow.
- Do not bundle binary save states, project metadata, videos, PDFs, or large archived course packs as authoritative assets.
- Document any optional external files or generated states clearly.
- Keep geometry scale, zone/particle interface, and boundary conditions explicit.

## Handoff To pfc-workflow

After this skill provides coupling snippets or a file-contract plan, return to `pfc-workflow` for:

- full case directory creation
- solve management
- post-processing route selection
- V&V and delivery
