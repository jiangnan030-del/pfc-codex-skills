# Overview

## Purpose

`pfc-cad-import` provides reusable PFC CAD/geometry preprocessing guidance. It is a child skill of `pfc-workflow`; it supplies targeted DXF/STL import, geometry set, wall conversion, particle filling, clump/rblock template, and legacy helper-app expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- PFC geometry set creation/import/export
- DXF/STL/geometry file contracts
- wall import/generation from CAD or geometry
- particle filling contracts for balls, clumps, and rblocks
- clump templates and rblock geometry routes
- legacy helper-app classification and preservation
- replacing old black-box helpers with native PFC 6.0 commands when possible

This skill does not own:

- full case lifecycle orchestration
- contact-law selection after geometry creation
- detailed FISH implementation beyond import/fill helper needs
- fluid or FLAC coupling
- post-processing figure generation
- AE/energy/source-mechanism analysis

## Documentation Enrichment

PFC 6.0 command documentation was queried through `pfc-mcp` while building this skill. The resulting command notes are summarized in `references/cad-import-doc-notes.md`.

Key checked commands:

- `geometry import`
- `geometry generate`
- `geometry export`
- `geometry list`
- `wall import`
- `wall generate`
- `clump template`
- `ball generate`
- `ball distribute`
- `rblock construct` and `rblock generate`

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/geometry-range-pfc6/`
- `scripts/canonical/cluster-shape-pfc6/`
- `scripts/apps/legacy-plugins/`

Included PFC 6.0 geometry/range files:

- `1_createGeometry.dat`: native geometry creation workflow.
- `2_importGeo.dat`: geometry import workflow using bundled DXF/STL examples.
- `3_range.dat`: geometry/range filtering example.
- `4_rangefish.dat`: geometry/range workflow with FISH logic.
- `11.dxf`, `22.dxf`, `11.stl`, `22.stl`: small geometry fixtures for import/range examples.

Included PFC 6.0 cluster/shape examples:

- `method1/`: geometry-driven sampling/replacement/export examples.
- `method2/`: clump template and cluster replacement examples, including `11.p2clp`.
- `method3/`: rblock/geometry resampling and interparticle variants.

Included legacy helper apps:

- `scripts/apps/legacy-plugins/`: optional preserved helper applications plus small adjacent input examples.
- These apps cover CAD wall import, 2D/3D particle fill, finite-element mesh conversion, boundary search, water-pressure boundary particle detection, material grouping, contour extraction, and related preprocessing tasks.

## Recommended Native Pattern

1. Create a model domain.
2. Import or generate geometry into a named geometry set.
3. List/check geometry before conversion.
4. Convert geometry into a wall, clump template, rblock template, or particle-fill region.
5. Validate object count, bounding box, groups, topology, and scale.
6. Return to `pfc-workflow` for contact model, calibration, solve, and post-processing routes.

## Legacy Helper App Pattern

When an old executable is needed or preserved:

1. Record inputs: geometry file, mesh file, parameter file, coordinate system, units, and expected format.
2. Record outputs: PFC command file, DXF/STL geometry, particle coordinates, boundary particles, groups, or check reports.
3. Store the executable under `scripts/apps/<app-name>/`.
4. Store small reproducible input examples next to the app.
5. Keep a native PFC or script replacement path in `scripts/canonical/` whenever possible.

## Inclusion Rules

- Keep small `.dat`, `.dxf`, `.stl`, `.p2clp`, and text input examples needed to understand workflows.
- Preserve helper executables under `scripts/apps/` when they are part of the workflow history.
- Do not bundle generated save states, project metadata, videos, PDFs, archives, or very large generated outputs as authoritative assets.
- Use ASCII folder/file names for public-facing copies when original helper names are local-language or mojibake-prone.

## Handoff To pfc-workflow

After this skill provides a geometry import/fill/template plan, return to `pfc-workflow` for:

- full case directory creation
- contact model or calibration routing if needed
- solve management
- post-processing route selection
- V&V and delivery
