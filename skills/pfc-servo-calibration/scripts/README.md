# Scripts

This directory contains the executable source templates and optional helper scripts for `pfc-servo-calibration`.

## Current Contents

- `canonical/servo-principles/`: bundled PFC 6.0 `.dat` servo demonstration files.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- Legacy helper binaries are not required runtime dependencies.
- Future scripts should preserve explicit inputs, outputs, target variables, and stage names.

## Suggested Future Helpers

### `materialize_servo_case.py`

Purpose: copy one servo demonstration into a new working directory.

Suggested interface:

```bash
python scripts/materialize_servo_case.py --case servo-principles --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print the recommended run order.
- Never modify canonical files in place.

### `check_servo_history.py`

Purpose: inspect exported histories from a servo run and report convergence quality.

Expected behavior:

- Read target and measured force/stress histories.
- Compute maximum overshoot, final error, and oscillation indicators.
- Suggest velocity/gain/timestep changes when convergence is poor.

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
- Keep helper scripts optional; the skill should remain understandable from markdown and bundled `.dat` templates.
