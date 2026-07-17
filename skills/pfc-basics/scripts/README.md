# Scripts

This directory contains source-like PFC foundation modeling templates for `pfc-basics`.

## Current Contents

- `canonical/basic-elements-pfc6/`: bundled PFC 6.0 examples for ball creation, basic contact/collision, and wall creation.
- `canonical/clump-rblock-pfc6/`: bundled PFC 6.0 examples for clump templates, clump creation, rblock templates, and rblock creation.
- `canonical/legacy-basics-reference/`: selected PFC5-era ball/wall/group/range snippets preserved as reference-only material.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Legacy snippets are useful for migration comparison, but they are not public-ready until audited and rewritten for the target PFC version.
- Future scripts should preserve explicit inputs, outputs, domain extents, object families, groups, ranges, and stage names.

## Suggested Future Helpers

### `materialize_basics_case.py`

Purpose: copy one foundation example set into a new working directory.

Suggested interface:

```bash
python scripts/materialize_basics_case.py --case basic-elements-pfc6 --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print recommended run order and PFC version assumptions.
- Never modify canonical files in place.

### `audit_basic_dat.py`

Purpose: inspect a `.dat`, `.p2dat`, or `.p3dat` file for foundation-model assumptions.

Expected behavior:

- Report model dimension, domain extents, object creation commands, groups, ranges, and contact setup commands.
- Warn when the file appears to be legacy syntax or depends on generated save states.
- Suggest specialist routing: CAD import, contact models, standard tests, servo calibration, dynamics, or coupling.

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
