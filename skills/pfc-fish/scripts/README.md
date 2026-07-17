# Scripts

This directory contains source-like FISH templates and optional helper scripts for `pfc-fish`.

## Current Contents

- `canonical/fish-basics-pfc6/`: bundled PFC 6.0 `.dat` examples for FISH basics, callbacks, particle creation, and applied logic.
- `canonical/fish-basics-pfc5-reference/`: legacy `.p2dat` and small `.dat` input files grouped by FISH language topic.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Legacy `.p2dat` examples are reference snippets until audited and rewritten for the target PFC version.
- Future scripts should preserve explicit inputs, outputs, run order, and object dependencies.

## Suggested Future Helpers

### `materialize_fish_case.py`

Purpose: copy one FISH demonstration into a new working directory.

Suggested interface:

```bash
python scripts/materialize_fish_case.py --case fish-basics-pfc6 --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print required version assumptions and recommended run order.
- Never modify canonical files in place.

### `audit_fish_symbols.py`

Purpose: inspect FISH files for global/local/callback/history risks.

Expected behavior:

- List `fish define` blocks.
- List `fish callback` registrations.
- List `fish history` symbols.
- Warn about likely accidental globals or missing callback documentation.

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
