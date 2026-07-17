# Scripts

This directory contains public-friendly templates for `pfc-fast-calibration`.

## Canonical Assets

- `canonical/orthogonal_design_13params.csv`: 27-run, 13-factor orthogonal design from the source method.
- `canonical/regression_fast_calibration.py`: source equations, example targets, and helper functions for prediction/back-solving.
- `canonical/improved_lpbm_assign.p3fis`: PFC/FISH template for strong/weak `linearpbond` grouping and Weibull damage.
- `canonical/extract_macro_metrics.py`: Python helper for extracting macro metrics from exported stress-strain histories.
- `canonical/manifest.json`: file inventory with hashes.

## Policy

- Scripts are templates, not calibrated final cases.
- Keep command flow split into specimen generation, consolidation, contact assignment, loading, and extraction.
- Do not hard-code local absolute paths.
- Do not store large `.sav`, project files, or generated output dumps in the skill.
- Verify PFC syntax with the installed version before production runs.

## Future Helpers

Suggested additions:

- `materialize_orthogonal_campaign.py`: create `run_001` ... `run_027` folders from the CSV.
- `merge_campaign_metrics.py`: collect `metrics.json` from every run.
- `fit_regressions.py`: refit equations from a new campaign and report cross-validation error.
