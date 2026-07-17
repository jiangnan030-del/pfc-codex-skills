# Overview

## Purpose

`pfc-basics` provides reusable PFC 6.0 foundation modeling guidance. It is a child skill of `pfc-workflow`; it supplies model lifecycle, domain, ball, wall, clump, rblock, range, group, and minimal contact setup expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- clean model start and save/restore conventions
- model domain extents and basic boundary conditions
- ball creation, generation, distribution, attributes, properties, and grouping
- simple wall generation/import awareness, attributes, properties, and grouping
- basic clump template, generation, and distribution patterns
- basic rblock construction/generation patterns
- simple groups, named ranges, and selection logic
- minimal runnable command-flow templates

This skill does not own:

- CAD/DXF/STL geometry import details
- contact-law selection and detailed CMAT/property/method design
- standard laboratory-test workflows
- servo calibration and controlled loading
- nontrivial FISH callbacks or helper libraries
- dynamic/seismic/fluid/FLAC coupling
- final plotting, AE, or energy analysis

## Documentation Enrichment

PFC 6.0 command documentation was queried through `pfc-mcp` while building this skill. The resulting command notes are summarized in `references/basics-doc-notes.md`.

Key checked commands:

- `model new`
- `model domain`
- `model cycle` / `model step`
- `model solve`
- `model calm`
- `model save` / `model restore`
- `ball create`, `ball generate`, `ball distribute`, `ball attribute`, `ball property`, `ball group`
- `wall generate`, `wall import`, `wall attribute`, `wall property`
- `clump template`, `clump generate`, `clump distribute`
- `rblock construct`, `rblock generate`
- `contact cmat`, `contact model`, `contact property`, `contact method`
- named ranges and group/position/ID/geometry filters

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/basic-elements-pfc6/`
- `scripts/canonical/clump-rblock-pfc6/`
- `scripts/canonical/legacy-basics-reference/`

Included PFC 6.0 basic-element files:

- `1create_ball.dat`: minimal ball creation.
- `2pengzhuang.dat`: basic collision/contact demonstration.
- `3create_wall.dat`: minimal wall creation.

Included PFC 6.0 clump/rblock files:

- `1ClumpTemplate.dat`: clump template setup.
- `2CreateClump.dat`: clump creation.
- `3rblockTemplate.dat`: rblock template setup.
- `4createrblock.dat`: rblock creation.
- `11.dxf`, `22.stl`: small geometry fixtures used by template examples.

Included reference-only legacy snippets:

- selected PFC5-era ball create/generate/distribute examples
- selected wall create/generate examples
- selected group/range examples
- snippets are normalized into ASCII filenames and treated as audit/reference material, not drop-in PFC 6.0 workflows

## Recommended Native Pattern

1. Start a clean model.
2. Define domain extents.
3. Create or generate the simplest object family needed.
4. Assign groups and named ranges early.
5. Add only minimal contact setup for runnable examples.
6. Clean/calm/check using short cycles.
7. Hand off to `pfc-workflow` for specialist routing and full case execution.

## Inclusion Rules

- Keep small `.dat`, `.dxf`, `.stl`, `.p2dat`, and `.p3dat` files needed to explain foundation workflows.
- Convert legacy text files to UTF-8 when copied into the skill.
- Do not bundle generated save states, project metadata, videos, PDFs, archives, or large output dumps as authoritative assets.
- Keep file and folder names public-friendly and encoding-safe.

## Handoff To pfc-workflow

After this skill provides a foundation object plan, return to `pfc-workflow` for:

- CAD import routing if external geometry is involved
- contact-law routing if model behavior depends on contact physics
- standard test, calibration, dynamics, coupling, post-processing, or AE routing
- full case directory creation and validation
