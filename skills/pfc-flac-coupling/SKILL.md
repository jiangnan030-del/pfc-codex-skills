---
name: pfc-flac-coupling
description: Child skill of pfc-workflow for PFC 6.0 and FLAC/FLAC3D discrete-continuum coupling, wall-zone handoff, and command-flow contracts.
---

# PFC FLAC Coupling

Use this skill to explain, adapt, or generate PFC-FLAC/FLAC3D coupling workflows. The skill is self-contained: baseline PFC/FLAC command-flow examples are stored under `scripts/canonical/`.

## Parent Skill Relationship

`pfc-flac-coupling` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for discrete-continuum coupling scenario selection, FLAC/PFC handoff contracts, wall-zone/interface setup, and version-risk notes. Return to `pfc-workflow` for full case planning, solve orchestration, post-processing routing, verification, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns complete PFC project lifecycle and decides when FLAC-coupling support is needed.
- Child `pfc-flac-coupling`: owns PFC-FLAC/FLAC3D handoff patterns, coupling stages, command-flow contracts, and saved-state assumptions.
- Sibling child `pfc-fluid-coupling`: owns PFC CFD/seepage/buoyancy workflows that do not require FLAC coupling.
- Sibling child `pfc-standard-tests`: owns standard mechanical-test templates and stage normalization.
- Sibling child `pfc-servo-calibration`: owns servo control and manual calibration sequencing.
- Sibling child `pfc-postprocessing`: owns standard figures and field exports after solve.
- Sibling child `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs after solve.

## When To Use

Use through `pfc-workflow` when a task uses both continuum zones and particles:

- Explain PFC-FLAC or PFC-FLAC3D coupling stages.
- Set up `zone` continua with particle or wall coupling.
- Use `wall-zone create` or interface-style boundary transfer.
- Organize coupled command flows and saved-state checkpoints.
- Decide which side owns gravity, boundary conditions, material model, and outputs.
- Document version-specific risks around `.f3sav`, `.f3prj`, `.sav`, and coupling commands.

## Required Inputs

Ask for these if missing:

- Software versions: PFC, FLAC, FLAC3D, and whether they are run in one coupled environment.
- Coupling scenario: slope, rockfall, foundation, excavation, granular-continuum interaction, or custom.
- Continuum side: zone geometry, constitutive model, boundary conditions, density, gravity, and saved state.
- Particle side: particle generation, contact model, density, damping, and domain.
- Handoff boundary: wall-zone, interface, structural element, geometry surface, or file-based exchange.
- Required outputs: continuum displacement/stress, particle trajectories, contact forces, coupled histories, or exported fields.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| Discrete-continuum baseline | `scripts/canonical/discrete-continuum-baseline/` | `1dimian.dat`, `2luoshi .dat` | Minimal continuum ground plus particle/wall-zone coupling example. |
| FLAC3D-PFC chapter 11 commands | `scripts/canonical/flac3d-pfc-chapter11/` | `11.*.txt` command snippets | Coupling command-flow fragments from a FLAC3D/PFC chapter example set; use as reference snippets, not blind-run projects. |

## Coupling Checklist

Use this checklist before writing or changing coupled logic:

1. Confirm which program owns the base continuum state and which program owns particle generation.
2. Create and solve the continuum baseline before introducing particles.
3. Save the continuum baseline state before coupling.
4. Create a coupling boundary: wall-zone, interface, or another explicit handoff surface.
5. Generate particles only after the continuum/coupling boundary exists.
6. Confirm gravity, density, damping, and timestep strategy on both sides.
7. Add histories for continuum displacement/stress and particle/contact response.
8. Save coupled milestones separately from uncoupled baseline states.
9. Avoid relying on old binary saves as the only reproducible source.

## Working Rules

- Prefer PFC 6.0/FLAC3D 6-era syntax unless the user explicitly targets another version.
- Treat files in `scripts/canonical/` as reference templates, not final coupled projects.
- Keep auxiliary file contracts explicit: continuum state, particle state, coupling boundary, and generated outputs.
- Do not bundle or require large PDFs, old project files, or binary saves as the core workflow.
- If old command snippets use `.txt`, preserve them as readable references and convert to `.dat` only after syntax audit.
- If the task becomes a full model run or validation study, hand control back to `pfc-workflow`.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- The selected PFC-FLAC coupling pattern and why it fits.
- Required files or snippets from `scripts/canonical/<case>/`.
- Which side owns geometry, material model, boundary conditions, gravity, and histories.
- Coupling boundary definition and saved-state sequence.
- Version and binary-save risk notes.
- Outputs needed to validate coupled response.
- A clear note that full case execution, post-processing routing, V&V, and delivery continue in `pfc-workflow`.

## Local Contents

- `references/overview.md`: detailed self-contained PFC-FLAC coupling boundaries and source map.
- `examples/README.md`: how to validate bundled coupling demonstrations.
- `scripts/canonical/`: PFC-FLAC coupling command-flow sources.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
