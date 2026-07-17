# Scripts

This directory contains the executable source templates and optional helper scripts for `pfc-fluid-coupling`.

## Current Contents

- `canonical/fluid-coupling-baseline/`: bundled PFC 6.0 `.dat`, Python, and auxiliary CFD mesh/data files.
- `apps/create_mesh/`: optional preserved mesh-helper application associated with the baseline CFD mesh workflow.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Legacy helper executables are stored under `apps/<app-name>/` and treated as optional unless a skill explicitly documents that no transparent replacement exists.
- Future scripts should preserve explicit inputs, outputs, fluid assumptions, mesh schemas, and stage names.

## Suggested Future Helpers

### `materialize_fluid_case.py`

Purpose: copy one fluid-coupling demonstration into a new working directory.

Suggested interface:

```bash
python scripts/materialize_fluid_case.py --case fluid-coupling-baseline --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print required Python dependencies and recommended run order.
- Never modify canonical files in place.

### `check_cfd_mesh.py`

Purpose: inspect CFD node/element tables before running PFC.

Expected behavior:

- Read node and element files.
- Report counts, coordinate ranges, and malformed rows.
- Warn about suspicious scale mismatches or missing element connectivity.

### `check_manifest.py`

Purpose: verify `scripts/canonical/manifest.json` against current file hashes.

Expected behavior:

- Recompute SHA-256 for bundled source assets.
- Report missing, added, or changed files.
- Exit nonzero only when files are missing or hashes differ.

## Script Rules

- Use explicit CLI arguments.
- Do not assume a particular drive, user name, download folder, or project directory.
- Do not require PFC unless the script is explicitly a validation runner.
- Do not mutate files unless a `--write` flag is provided.
- Flag generated plots, binary saves, project metadata, videos, and undocumented executables before publication.
- Keep helper scripts optional; the skill should remain understandable from markdown and bundled templates.
