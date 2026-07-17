# Scripts

This directory contains source-like dynamic templates and optional helper scripts for `pfc-dynamics`.

## Current Contents

- `canonical/slope-seismic-pfc6/`: bundled PFC 6.0 `.dat` examples for static slope preparation and sinusoidal dynamic loading.
- `canonical/demolition-blasting-reference/`: legacy `.FIS` callback/crack/floater utilities plus a large demolition model construction source reference.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Legacy demolition/blasting files are reference snippets until audited and rewritten for the target PFC version.
- Future scripts should preserve explicit inputs, outputs, loading function, damping, timestep, and stage names.

## Suggested Future Helpers

### `materialize_dynamic_case.py`

Purpose: copy one dynamics demonstration into a new working directory.

Suggested interface:

```bash
python scripts/materialize_dynamic_case.py --case slope-seismic-pfc6 --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print required version assumptions and recommended run order.
- Never modify canonical files in place.

### `audit_dynamic_case.py`

Purpose: inspect dynamics files for loading, damping, timestep, and history completeness.

Expected behavior:

- Detect `model configure dynamic`, `model mechanical time-total`, `model calm`, damping assignments, and velocity/force input commands.
- List FISH callbacks or `whilestepping` functions that update input motion.
- Warn when dynamic loading lacks time, timestep, input, or energy histories.

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
- Keep helper scripts optional; the skill should remain understandable from markdown and bundled templates.
