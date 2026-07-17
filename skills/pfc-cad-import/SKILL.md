---
name: pfc-cad-import
description: Child skill of pfc-workflow for PFC 6.0 CAD/DXF/STL geometry import, wall/geometry conversion, particle filling, clump/rblock templates, and legacy helper app contracts.
---

# PFC CAD Import

Use this skill to explain, adapt, or generate PFC CAD/geometry import workflows. The skill is self-contained: PFC 6.0 geometry/range and cluster-shape examples are stored under `scripts/canonical/`, preserved legacy helper apps are stored under `scripts/apps/`, and documentation notes checked through `pfc-mcp` are stored under `references/cad-import-doc-notes.md`.

## Parent Skill Relationship

`pfc-cad-import` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for CAD/DXF/STL import, geometry sets, wall conversion, particle filling contracts, clump/rblock geometry templates, and legacy helper app classification. Return to `pfc-workflow` for full case planning, solve orchestration, post-processing routing, verification, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns complete PFC project lifecycle and decides when CAD/geometry import support is needed.
- Child `pfc-cad-import`: owns geometry file contracts, import commands, wall/particle/template handoff, and legacy plugin/app preservation.
- Sibling child `pfc-fish`: owns detailed FISH helper/callback implementation.
- Sibling child `pfc-contact-models`: owns contact-law selection and property setup after geometry/material creation.
- Sibling child `pfc-standard-tests`: owns standard laboratory-test templates.
- Sibling child `pfc-servo-calibration`: owns servo control and calibration sequencing.
- Sibling child `pfc-dynamics`: owns dynamic/seismic loading assumptions.
- Sibling child `pfc-fluid-coupling`: owns PFC CFD/seepage/buoyancy workflows.
- Sibling child `pfc-flac-coupling`: owns PFC-FLAC/FLAC3D coupling.
- Sibling child `pfc-postprocessing`: owns standard figures and field exports after solve.
- Sibling child `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs after solve.

## When To Use

Use through `pfc-workflow` when a task needs geometry preprocessing:

- import DXF/STL/geometry files into PFC
- convert geometry into walls or boundaries
- fill CAD/FEM regions with balls, clumps, or rigid blocks
- create clump templates from geometry or CAD-derived shapes
- audit legacy CAD/FEM helper executables and their input/output contracts
- replace a black-box helper with transparent PFC 6.0 commands or scripts
- classify geometry import, particle-fill, boundary-search, or material-group workflows

## Required Inputs

Ask for these if missing:

- Geometry source format: DXF, STL, Itasca geometry, FEM node/element tables, text coordinates, or helper-app output.
- Target object: geometry set, wall, balls, clumps, rblocks, material groups, or boundary particles.
- Dimensionality: PFC2D/PFC3D and target PFC major version.
- Required geometry scale, coordinate system, units, and domain extents.
- Whether the shape is a boundary, a region to fill, a particle template, or a validation/checking surface.
- Expected intermediate/output files from any legacy helper app.

## Documentation-Backed Rules

The following PFC 6.0 documentation points were checked through `pfc-mcp` and are expanded in `references/cad-import-doc-notes.md`:

- `geometry import` imports DXF/STL/Itasca geometry data into geometry sets.
- `geometry generate` creates simple native geometry when CAD import is unnecessary.
- `geometry export` exports geometry data for review or downstream use.
- `wall import` imports walls from supported files or geometry sets; model domain and valid manifold/orientable geometry are required.
- `wall generate` creates simple walls directly and should be preferred for simple boundaries.
- `clump template` can build clump templates from pebbles or geometry/surface descriptions.
- `ball generate` creates non-overlapping balls; `ball distribute` fills to target porosity with overlaps.
- `rblock construct` / `rblock generate` support rigid-block geometry/template workflows.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| Geometry/range PFC 6.0 | `scripts/canonical/geometry-range-pfc6/` | `.dat`, `.dxf`, `.stl` | Native geometry creation/import, range use, and geometry/FISH examples. |
| Cluster/shape PFC 6.0 | `scripts/canonical/cluster-shape-pfc6/` | method folders with `.dat`, `.dxf`, `.stl`, `.p2clp` | Cluster, clump template, replacement, export, and rblock/geometry workflows. |
| Legacy plugin apps | `scripts/apps/legacy-plugins/` | `app.exe` plus small adjacent inputs | Optional preserved helper apps for CAD/FEM import, particle filling, boundary search, water-pressure, and material grouping workflows. |

## CAD Import Checklist

Use this checklist before writing or changing geometry import logic:

1. Decide if native PFC commands can replace the external helper.
2. Define the model domain before wall import/generation.
3. Validate geometry scale, units, coordinate axes, orientation, and topology.
4. Use geometry sets for inspection before converting geometry into walls or templates.
5. For particle filling, document target porosity, size distribution, allowed overlap, and acceptance region.
6. For clump/rblock templates, document surface quality and inertial-attribute assumptions.
7. Keep legacy helper apps optional and document their input/output contract.
8. Route full model staging and validation back to `pfc-workflow`.

## Working Rules

- Prefer PFC 6.0-native `geometry`, `wall`, `ball`, `clump`, and `rblock` commands before relying on legacy apps.
- Treat files in `scripts/canonical/` as reference templates, not final calibrated models.
- Treat apps in `scripts/apps/` as optional preserved helper applications, not mandatory public dependencies.
- Do not publish generated `.sav`, project metadata, videos, PDFs, archives, or very large generated outputs as authoritative assets.
- If the task becomes a full model run or validation study, hand control back to `pfc-workflow`.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- Selected geometry import/fill/template pattern and why it fits.
- Required files or snippets from `scripts/canonical/<case>/` or optional apps from `scripts/apps/<app>/`.
- Input/output file contract, units, coordinate system, and domain extent.
- Wall/geometry/particle/clump/rblock handoff commands.
- Validation checks for geometry topology and generated PFC objects.
- Version compatibility and legacy-helper notes.
- A clear note that full case execution, post-processing routing, V&V, and delivery continue in `pfc-workflow`.

## Local Contents

- `references/overview.md`: detailed self-contained CAD import boundaries and source map.
- `references/cad-import-doc-notes.md`: PFC 6.0 command notes checked through `pfc-mcp`.
- `references/plugin-cases.md`: legacy helper app classification and contracts.
- `examples/README.md`: how to validate bundled CAD/geometry demonstrations.
- `scripts/canonical/`: native PFC geometry/range and cluster-shape snippets.
- `scripts/apps/`: optional preserved legacy helper applications.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
