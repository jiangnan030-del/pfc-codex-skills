# Scripts

This directory contains source-like CAD/geometry templates and optional preserved helper applications for `pfc-cad-import`.

## Current Contents

- `canonical/geometry-range-pfc6/`: bundled PFC 6.0 `.dat`, `.dxf`, and `.stl` examples for geometry creation/import/range workflows.
- `canonical/cluster-shape-pfc6/`: bundled PFC 6.0 cluster, clump template, rblock, replacement, and geometry export examples.
- `apps/legacy-plugins/`: optional preserved helper apps plus small adjacent input examples.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Legacy helper executables are preserved under `apps/` and treated as optional unless a case explicitly documents that no transparent replacement exists.
- Future scripts should preserve explicit inputs, outputs, geometry scale, coordinate system, and PFC handoff stages.

## Suggested Future Helpers

### `materialize_geometry_case.py`

Purpose: copy one geometry import demonstration into a new working directory.

Suggested interface:

```bash
python scripts/materialize_geometry_case.py --case geometry-range-pfc6 --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print required version assumptions and recommended run order.
- Never modify canonical files in place.

### `audit_geometry_files.py`

Purpose: inspect DXF/STL/geometry files before importing them into PFC.

Expected behavior:

- Report file type, approximate bounds, object counts, and layer/group names when available.
- Warn about suspicious scale, empty geometry, duplicate vertices, or disconnected surfaces.
- Suggest whether the route should be `geometry import`, `wall import`, `clump template`, `rblock`, or particle fill.

### `audit_legacy_app_contract.py`

Purpose: document a helper app's input/output contract before recommending it.

Expected behavior:

- List files in `scripts/apps/legacy-plugins/<slug>/`.
- Classify likely inputs and outputs.
- Generate a short contract stub for references or case notes.

### `check_manifest.py`

Purpose: verify `scripts/canonical/manifest.json` against current file hashes.

Expected behavior:

- Recompute SHA-256 for bundled source assets and optional apps.
- Report missing, added, or changed files.
- Exit nonzero only when files are missing or hashes differ.

## Script Rules

- Use explicit CLI arguments.
- Do not assume a particular drive, user name, download folder, or project directory.
- Do not require PFC unless the script is explicitly a validation runner.
- Do not mutate files unless a `--write` flag is provided.
- Keep helper scripts optional; the skill should remain understandable from markdown and bundled templates.
