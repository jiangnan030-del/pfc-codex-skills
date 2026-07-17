# Scripts

This directory contains source-like templates for `pfc-mineral-heterogeneity`.

## Current Contents

- `canonical/mineral_cluster_assignment.p2fis`: FISH template for target-area mineral grouping and contact grouping.
- `canonical/mineral_lpbm_parameters.dat`: PFC command template for per-mineral LPBM parameter assignment.
- `canonical/weibull_damage.p2fis`: FISH template for Weibull multipliers on bonded-contact properties.
- `canonical/otsu_phase_fraction.py`: Python helper template for phase fraction extraction from an image.
- `canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.

## Current Stance

- Templates are public-friendly starting points, not calibrated final models.
- Keep image segmentation, phase assignment, contact grouping, parameter assignment, damage, and loading as separate stages.
- Do not assume a particular drive, user name, download folder, or project directory.

## Suggested Future Helpers

### `materialize_mineral_case.py`

Purpose: copy one mineral heterogeneity template set into a new case directory.

Expected behavior:

- copy selected canonical templates
- write a small case manifest with target fractions and seed
- never mutate canonical files in place

### `audit_mineral_groups.py`

Purpose: validate phase and contact-group diagnostics after construction.

Expected behavior:

- read exported group-count tables
- compare target vs achieved fractions
- flag missing phase groups or contact groups

### `check_manifest.py`

Purpose: verify `scripts/canonical/manifest.json` against current file hashes.

Expected behavior:

- recompute SHA-256 values
- report missing, added, or changed files
- exit nonzero only when files are missing or hashes differ

## Script Rules

- Use explicit CLI arguments.
- Do not require PFC unless the script is explicitly a validation runner.
- Do not mutate files unless a `--write` flag is provided.
- Keep helper scripts optional; the skill should remain understandable from markdown and bundled templates.
