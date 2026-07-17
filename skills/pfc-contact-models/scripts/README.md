# Scripts

This directory contains source-like contact-model templates and optional helper scripts for `pfc-contact-models`.

## Current Contents

- `canonical/linear-model-pfc6/`: bundled PFC 6.0 `.dat` examples for linear normal/shear contact response.
- `canonical/linearpbond-model-pfc6/`: bundled PFC 6.0 `.dat` examples for linear parallel-bond normal/shear response and bond stress checks.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Contact-model snippets are reference demonstrations until calibrated in a target macro workflow.
- Future scripts should preserve explicit contact law, CMAT order, property blocks, methods, histories, and stage names.

## Suggested Future Helpers

### `materialize_contact_case.py`

Purpose: copy one contact-model demonstration into a new working directory.

Suggested interface:

```bash
python scripts/materialize_contact_case.py --case linear-model-pfc6 --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print required version assumptions and recommended run order.
- Never modify canonical files in place.

### `audit_contact_setup.py`

Purpose: inspect contact-model setup files for command-order and validation risks.

Expected behavior:

- Detect CMAT/model/property/method commands.
- Warn if contacts are queried before `model clean` or before initial cycling.
- Warn if `contact model` or `contact cmat apply` may overwrite existing contact state.
- List histories and contact properties used for validation.

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
