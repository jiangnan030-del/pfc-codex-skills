---
name: pfc-basics
description: Child skill of pfc-workflow for PFC 6.0 foundation modeling: model lifecycle, domains, balls, walls, clumps, rblocks, groups, ranges, and minimal runnable setup patterns.
---

# PFC Basics

Use this skill to explain, adapt, or generate PFC 6.0 foundation modeling workflows. It covers the smallest reusable building blocks: model lifecycle, domain setup, balls, walls, clumps, rblocks, groups, ranges, and minimal contact setup needed for runnable examples.

## Parent Skill Relationship

`pfc-basics` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for foundational object creation and command-order questions, then return to `pfc-workflow` for complete case planning, calibration, solve management, post-processing, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns full PFC case lifecycle and decides when foundation modeling help is needed.
- Child `pfc-basics`: owns model start/domain/object/range/group basics and minimal runnable examples.
- Sibling child `pfc-cad-import`: owns CAD/DXF/STL import, wall conversion, geometry-based ranges, and geometry-derived templates.
- Sibling child `pfc-contact-models`: owns contact-law selection, CMAT, contact methods, bonding, and contact validation.
- Sibling child `pfc-standard-tests`: owns canonical lab-test templates after basic objects are selected.
- Sibling child `pfc-servo-calibration`: owns servo-controlled loading and calibration sequencing.
- Sibling child `pfc-fish`: owns nontrivial FISH functions, callbacks, histories, and reusable helper files.
- Sibling child `pfc-dynamics`: owns dynamic/seismic/impact loading basics and checks.
- Sibling child `pfc-fluid-coupling`: owns fluid-solid coupling and seepage/buoyancy routes.
- Sibling child `pfc-flac-coupling`: owns PFC-FLAC/FLAC3D coupled workflows.
- Sibling child `pfc-postprocessing`: owns standard non-AE plots, fields, exports, and reports.
- Sibling child `pfc-ae-energy`: owns AE/energy/source-mechanism outputs.

## When To Use

Use through `pfc-workflow` when the task asks to:

- start a clean PFC model or explain the basic command order
- define model domains and simple boundary behavior
- create or generate balls
- create, generate, or import simple walls
- create clump templates or generate/distribute clumps at a basic level
- construct/generate rblocks at a basic level
- assign simple groups or named ranges
- prepare a minimal runnable `.dat` foundation before routing to a specialist child skill

## Required Inputs

Ask for these if missing:

- PFC2D or PFC3D target.
- Model size/domain extents and units.
- Desired object type: ball, wall, clump, rblock, or mixed specimen.
- Deterministic creation vs random generation/distribution.
- Particle size, grading, porosity, count, or simple shape intent.
- Whether a CAD/geometry source is involved; if yes, route geometry details to `pfc-cad-import`.
- Whether the next stage is a standard test, calibration, dynamics, coupling, or post-processing route.

## Documentation-Backed Rules

The following PFC 6.0 documentation points were checked through `pfc-mcp` and are expanded in `references/basics-doc-notes.md`:

- `model new` starts a clean model; `force` intentionally discards unsaved state.
- `model domain` defines active domain extents and boundary conditions.
- `model cycle` / `model step` advance timesteps; short checks should precede long solves.
- `model solve` should use explicit criteria in public templates.
- `model calm` is useful after generation/distribution and before controlled solves.
- `model save` / `model restore` are runtime state operations, not canonical source assets.
- `ball create`, `ball generate`, and `ball distribute` cover deterministic creation, non-overlap generation, and porosity-style distribution.
- `wall generate` handles simple containers; `wall import` belongs in the CAD/geometry route when external files are involved.
- `clump template`, `clump generate`, and `clump distribute` cover basic clump setup.
- `rblock construct` and `rblock generate` cover basic rigid-block setup.
- `contact cmat`, `contact model`, `contact property`, and `contact method` are only touched minimally here; specialist contact design belongs to `pfc-contact-models`.
- named ranges, position/ID/group filters, and geometry filters should be explicit and auditable.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| Basic elements PFC 6.0 | `scripts/canonical/basic-elements-pfc6/` | `1create_ball.dat`, `2pengzhuang.dat`, `3create_wall.dat` | Minimal ball, collision/contact, and wall examples. |
| Clump/rblock PFC 6.0 | `scripts/canonical/clump-rblock-pfc6/` | `.dat`, `.dxf`, `.stl` | Basic clump template, clump creation, rblock template, and rblock creation examples. |
| Legacy basics reference | `scripts/canonical/legacy-basics-reference/` | selected `.p2dat`/`.p3dat` snippets | PFC5-era ball/wall/group/range snippets preserved as reference-only templates for audit and modernization. |

## Foundation Workflow Checklist

1. Start from `model new` unless continuing from a documented restore point.
2. Define `model domain extent` before creating/importing domain-sensitive objects.
3. Create/generate/distribute one object family at a time.
4. Assign clear groups for material, stage, boundary, and source role.
5. Use named ranges when selections are reused.
6. Apply only minimal contact setup needed for a runnable foundation.
7. Run `model clean`, short `model cycle`, and sanity checks before routing to calibration or solve.
8. Return to `pfc-workflow` for full-stage orchestration.

## Working Rules

- Prefer PFC 6.0-native examples in `scripts/canonical/basic-elements-pfc6/` and `scripts/canonical/clump-rblock-pfc6/`.
- Treat legacy `.p2dat`/`.p3dat` snippets in `scripts/canonical/legacy-basics-reference/` as reference-only until audited for PFC 6.0 syntax and physics.
- Do not make generated `.sav`, project metadata, videos, PDFs, archives, or large output dumps authoritative skill assets.
- If geometry import becomes central, route to `pfc-cad-import`.
- If contact-law choice becomes central, route to `pfc-contact-models`.
- If the task becomes a lab test or calibration problem, route back to `pfc-workflow` and the relevant child skill.

## Output Contract

A complete `pfc-basics` handoff back to `pfc-workflow` should include:

- selected foundation object route and why it fits
- required files or snippets from `scripts/canonical/<case>/`
- model dimension, units, and domain extent assumptions
- object creation/generation/distribution commands
- groups and named ranges introduced
- minimal contact setup, if any
- sanity checks and short-cycle validation steps
- notes for follow-on routing to CAD import, contact models, standard tests, servo calibration, dynamics, coupling, post-processing, or AE/energy analysis

## Local Contents

- `references/overview.md`: self-contained boundaries, source map, and inclusion rules.
- `references/basics-doc-notes.md`: PFC 6.0 command notes checked through `pfc-mcp`.
- `examples/README.md`: example validation order and materialization guidance.
- `scripts/canonical/`: bundled PFC 6.0 and reference snippets.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
