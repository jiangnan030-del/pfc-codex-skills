---
name: pfc-fluid-coupling
description: Child skill of pfc-workflow for PFC 6.0 fluid-solid coupling, buoyancy, CFD mesh input contracts, and seepage workflow handoff.
---

# PFC Fluid Coupling

Use this skill to explain, adapt, or generate PFC 6.0 fluid-solid coupling workflows. The skill is self-contained: baseline `.dat` and Python coupling examples are stored under `scripts/canonical/`.

## Parent Skill Relationship

`pfc-fluid-coupling` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for fluid-coupling scenario selection, CFD/buoyancy command patterns, auxiliary mesh/data contracts, and seepage-coupling handoff. Return to `pfc-workflow` for full case planning, solve orchestration, post-processing routing, verification, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns complete PFC project lifecycle and decides when fluid-coupling support is needed.
- Child `pfc-fluid-coupling`: owns seepage, buoyancy, CFD element setup, FiPy/Darcy coupling notes, and fluid-related input/output contracts.
- Sibling child `pfc-standard-tests`: owns standard mechanical-test templates and stage normalization.
- Sibling child `pfc-servo-calibration`: owns servo control and manual calibration sequencing.
- Sibling child `pfc-postprocessing`: owns standard figures and field exports after solve.
- Sibling child `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs after solve.

## When To Use

Use through `pfc-workflow` when a task involves fluid or pore-pressure effects:

- Explain PFC `model configure cfd`, CFD element input, buoyancy, or drag-coupling concepts.
- Set up simple particle-water buoyancy or particle falling-in-water examples.
- Document auxiliary input files such as CFD node/element tables.
- Adapt a Darcy/FiPy coupling script that updates PFC CFD fields.
- Decide which parts of a seepage workflow can be bundled and which remain external dependencies.

## Required Inputs

Ask for these if missing:

- PFC version and dimensionality: PFC2D/PFC3D, preferably PFC 6.0 unless stated otherwise.
- Coupling scenario: buoyancy only, built-in CFD elements, Darcy/FiPy update, seepage force, drag, or pore pressure.
- Particle model: specimen geometry, particle size range, porosity, density, and boundaries.
- Fluid model: density, viscosity, velocity/pressure boundary conditions, inlet/outlet definitions.
- Auxiliary files: mesh nodes, elements, particle template, or Python coupling script.
- Required outputs: particle trajectories, force histories, pressure/velocity fields, porosity/permeability, or coupled response curves.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| Fluid coupling baseline | `scripts/canonical/fluid-coupling-baseline/` | `1kelirushui.dat`, `1luoshui.dat`, `dll.py`, `particles.dat`, `Node.dat`, `Elem.dat`, `test.dat` | PFC 6.0 buoyancy, CFD element input, and FiPy/Darcy coupling examples. |
| Mesh helper app | `scripts/apps/create_mesh/` | `create_mesh.exe` | Optional legacy helper application associated with the CFD mesh input workflow; document and preserve it, but do not make it mandatory when node/element files are already bundled or can be generated another way. |

## Coupling Checklist

Use this checklist before writing or changing fluid-coupled logic:

1. Confirm whether the task needs simple buoyancy, built-in CFD elements, or external Darcy/FiPy coupling.
2. Confirm units for particle geometry, fluid density, viscosity, pressure, and velocity.
3. Confirm mesh input files and their coordinate scale if using `cfd read nodes/elements`.
4. Initialize `model configure cfd` before CFD element commands.
5. Define particle density/damping/contact model separately from fluid fields.
6. Define inlet/outlet or pressure/velocity boundary conditions explicitly.
7. Decide update interval for fluid recalculation relative to mechanical cycles.
8. Export enough data to reproduce coupled fields without GUI-only steps.

## Working Rules

- Prefer PFC 6.0-compatible syntax unless the user explicitly targets another version.
- Treat files in `scripts/canonical/` as reference templates, not final calibrated models.
- Keep auxiliary file contracts explicit: node table, element table, particle setup, Python coupling script, and generated outputs.
- Do not make helper executables the only core workflow path; place legacy apps under `scripts/apps/<app-name>/`, document their inputs/outputs, and keep transparent `.dat`/Python alternatives when possible.
- State optional Python dependencies such as `numpy` and `fipy` when using `dll.py`-style coupling.
- If the task becomes a full model run or validation study, hand control back to `pfc-workflow`.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- The selected fluid-coupling pattern and why it fits.
- Required files or snippets from `scripts/canonical/<case>/`.
- Fluid assumptions: density, viscosity, boundary conditions, flow direction, and update interval.
- Auxiliary input contract: node/element/particle file schema and expected location.
- Histories or exports needed to validate the coupled response.
- Dependency warnings such as `model configure cfd`, FiPy availability, and mesh scale.
- A clear note that full case execution, post-processing routing, V&V, and delivery continue in `pfc-workflow`.

## Local Contents

- `references/overview.md`: detailed self-contained fluid-coupling boundaries and source map.
- `examples/README.md`: how to validate bundled fluid-coupling demonstrations.
- `scripts/canonical/`: fluid-coupling demonstration code and auxiliary mesh/data files.
- `scripts/apps/create_mesh/`: optional mesh-helper application preserved with the fluid-coupling example set.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
