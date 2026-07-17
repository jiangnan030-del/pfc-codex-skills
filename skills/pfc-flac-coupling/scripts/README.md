# Scripts

This directory contains source-like coupling templates and optional helper scripts for `pfc-flac-coupling`.

## Current Contents

- `canonical/discrete-continuum-baseline/`: bundled minimal `.dat` command flow for continuum baseline plus particle coupling.
- `canonical/flac3d-pfc-chapter11/`: readable FLAC3D/PFC command snippets stored as `.txt` source references.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Legacy binary save/project files are not required runtime dependencies.
- Future scripts should preserve explicit inputs, outputs, handoff boundaries, and stage names.

## Suggested Future Helpers

### `materialize_coupling_case.py`

Purpose: copy one coupling demonstration into a new working directory.

Suggested interface:

```bash
python scripts/materialize_coupling_case.py --case discrete-continuum-baseline --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print required Itasca version assumptions and recommended run order.
- Never modify canonical files in place.

### `audit_coupling_snippets.py`

Purpose: inspect `.txt` snippets before converting them into runnable `.dat` stages.

Expected behavior:

- Group snippets by stage prefix.
- Report commands that may be version-sensitive.
- Suggest stage names and output checkpoints.

### `check_manifest.py`

Purpose: verify `scripts/canonical/manifest.json` against current file hashes.

Expected behavior:

- Recompute SHA-256 for bundled source assets.
- Report missing, added, or changed files.
- Exit nonzero only when files are missing or hashes differ.

## Script Rules

- Use explicit CLI arguments.
- Do not assume a particular drive, user name, download folder, or project directory.
- Do not require PFC/FLAC unless the script is explicitly a validation runner.
- Do not mutate files unless a `--write` flag is provided.
- Keep helper scripts optional; the skill should remain understandable from markdown and bundled templates.
