---
name: pfc-fish
description: Child skill of pfc-workflow for PFC 6.0 FISH authoring, callbacks, histories, object traversal, IO, and refactoring reusable FISH helpers.
---

# PFC FISH

Use this skill to explain, adapt, refactor, or generate PFC FISH code. The skill is self-contained: PFC 6.0 FISH tutorial examples and legacy reference snippets are stored under `scripts/canonical/`, and documentation notes checked through `pfc-mcp` are stored under `references/fish-doc-notes.md`.

## Parent Skill Relationship

`pfc-fish` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for FISH language design, helper-file organization, callbacks, histories, data IO, maps, traversal, and refactoring. Return to `pfc-workflow` for full case planning, solve orchestration, post-processing routing, verification, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns complete PFC project lifecycle and decides when specialist FISH support is needed.
- Child `pfc-fish`: owns FISH functions, callbacks, histories, tables/maps, IO helpers, object traversal, and code hygiene.
- Sibling child `pfc-standard-tests`: owns standard mechanical-test templates and stage normalization.
- Sibling child `pfc-servo-calibration`: owns servo control and manual calibration sequencing.
- Sibling child `pfc-fluid-coupling`: owns PFC CFD/seepage/buoyancy workflows.
- Sibling child `pfc-flac-coupling`: owns PFC-FLAC/FLAC3D discrete-continuum coupling.
- Sibling child `pfc-postprocessing`: owns standard figures and field exports after solve.
- Sibling child `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs after solve.

## When To Use

Use through `pfc-workflow` when a task needs FISH code or FISH reasoning:

- Teach or refactor FISH variables, functions, loops, conditionals, arrays, matrices, tensors, strings, vectors, and maps.
- Write reusable `fish define` helpers.
- Add `fish callback` logic for per-cycle or event-driven updates.
- Add `fish history` outputs for custom scalar metrics.
- Traverse balls, walls, contacts, clumps, measures, fragments, or other model objects.
- Read/write simple data files or split helpers into `program call` modules.
- Audit legacy FISH snippets for PFC 6.0 compatibility and code hygiene.

## Required Inputs

Ask for these if missing:

- PFC version and dimensionality: PFC2D/PFC3D and target major version.
- Task type: helper function, callback, history, object traversal, IO, map/table usage, or refactor.
- Target objects: balls, walls, contacts, clumps, measures, zones, fractures, or custom state.
- Run stage: before particle creation, after contact formation, during cycling, after solve, or export-only.
- Expected output: scalar history, table, file, model mutation, stop condition, or diagnostic print.
- Existing snippet if one is being audited.

## Documentation-Backed Rules

The following PFC 6.0 documentation points were checked through `pfc-mcp` and are expanded in `references/fish-doc-notes.md`:

- `fish define` defines a named FISH function; tokens after the name are arguments.
- `fish callback` adds/removes functions executed at callback events or cycle locations.
- `fish history [name <label>] <symbol>` samples the numeric return value of a FISH symbol at the history interval.
- `fish list` lists FISH symbols, callbacks, arrays, and related debugging information.
- `fish automatic-create` controls automatic global symbol creation; public templates should avoid accidental globals.
- `fish operator` is for multi-threaded-safe operators and should not replace normal `fish define` helpers unless needed.
- `program call` is the preferred command-level mechanism for splitting reusable FISH helpers from case stages.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| PFC 6.0 FISH basics | `scripts/canonical/fish-basics-pfc6/` | `1value.dat`, `2xunhuan.dat`, `3fishcreate_ball.dat`, `3huidiao.dat`, `4shepizouwei.dat`, `5guitusaipao.dat`, `6jianduan.dat` | PFC 6.0-native tutorial examples for variables, loops, callbacks, object creation, random walk, and shear-like logic. |
| Legacy FISH reference snippets | `scripts/canonical/fish-basics-pfc5-reference/` | themed `.p2dat` and small `.dat` input files | PFC 5-era FISH examples for data types, functions, conditionals, loops, IO, map usage, and standard functions; audit before using in PFC 6.0. |

## FISH Authoring Checklist

Use this checklist before writing or changing FISH logic:

1. Decide whether each symbol is local, intentional global, history output, or callback state.
2. Put reusable calculations in named `fish define` functions.
3. Keep callback functions short, deterministic, and documented with cycle point/event and frequency.
4. Use `fish history` for scalar outputs needed during solve.
5. Split reusable FISH helpers from model setup using `program call`.
6. Add object-existence assumptions when traversing balls, walls, contacts, or measures.
7. Avoid relying on generated `.sav` or project files as the only source of truth.
8. Test the smallest snippet before inserting it into a full workflow.

## Working Rules

- Prefer PFC 6.0-safe syntax unless the user explicitly targets another version.
- Treat files in `scripts/canonical/` as reference templates, not final calibrated models.
- For legacy `.p2dat` snippets, preserve intent but audit syntax, object intrinsics, callbacks, and IO before promoting to PFC 6.0.
- Do not publish generated `.sav`, project metadata, videos, PDFs, or large output dumps as authoritative assets.
- When a FISH helper changes model behavior during a solve, include a history or validation check proving the callback is active.
- If the task becomes a full model run or validation study, hand control back to `pfc-workflow`.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- The selected FISH pattern and why it fits.
- Required files or snippets from `scripts/canonical/<case>/`.
- Function names, globals, locals, callback registration, and history definitions.
- Run-order assumptions and object dependencies.
- Version compatibility and legacy-audit notes.
- Minimal validation steps.
- A clear note that full case execution, post-processing routing, V&V, and delivery continue in `pfc-workflow`.

## Local Contents

- `references/overview.md`: detailed self-contained FISH boundaries and source map.
- `references/fish-doc-notes.md`: PFC 6.0 command notes checked through `pfc-mcp`.
- `examples/README.md`: how to validate bundled FISH demonstrations.
- `scripts/canonical/`: PFC FISH tutorial/source snippets.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
