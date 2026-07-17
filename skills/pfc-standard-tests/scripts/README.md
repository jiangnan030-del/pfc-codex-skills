# Scripts

This directory is reserved for small helper scripts that make the bundled standard-test templates easier to materialize, inspect, or validate.

## Current Stance

- The authoritative implementation surface is the bundled PFC 6.0 command flow in `canonical/` from this directory, or `scripts/canonical/` from the skill root.
- The skill does not require helper binaries at runtime.
- Future scripts should be optional, deterministic, and safe to run in a clean project folder.

## Suggested Future Helpers

### `materialize_case.py`

Purpose: copy one canonical case into a new working directory and optionally rename stage files.

Suggested interface:

```bash
python scripts/materialize_case.py --case ucs --out /path/to/workdir
```

Expected behavior:

- Validate that `--case` is one of the canonical folders.
- Copy all files from `scripts/canonical/<case>/` to the output directory.
- Print the recommended run order.
- Never modify the canonical files in place.

### `check_manifest.py`

Purpose: verify `scripts/canonical/manifest.json` against current file hashes.

Suggested interface:

```bash
python scripts/check_manifest.py
```

Expected behavior:

- Recompute SHA-256 for each bundled source asset.
- Report missing, added, or changed files.
- Exit nonzero only when files are missing or hashes differ.

### `scan_private_paths.py`

Purpose: keep the skill GitHub-ready by finding private absolute paths.

Suggested interface:

```bash
python scripts/scan_private_paths.py
```

Suggested behavior:

- Search the skill directory for drive-letter absolute paths, home-directory paths, private download-folder names, and other machine-local references.
- Print file and line numbers for each match.
- Keep the pattern list inside the script so documentation remains repository-independent.

## Script Rules

- Use explicit CLI arguments; do not infer output folders from hidden global state.
- Do not require PFC itself unless the script is explicitly a validation runner.
- Keep scripts cross-platform where possible, but allow Windows examples because PFC is commonly installed on Windows.
- Preserve explicit inputs, outputs, and stage names.
- Do not copy `.sav`, `.prj`, videos, PDFs, or generated result files into public examples.
