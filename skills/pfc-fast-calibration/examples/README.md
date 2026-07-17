# Example Cases

This directory documents how to materialize and validate a fast-calibration campaign. Runnable templates live under `../scripts/canonical/`.

## Source Reproduction

Use this route when reproducing the source chapter:

1. Use `orthogonal_design_13params.csv` as the 27-run design table.
2. Use the source specimen scale and porosity described in `references/source-code-complete-pfc6.md`.
3. Materialize one run directory per row.
4. Assign improved LPBM parameters with `improved_lpbm_assign.p3fis`.
5. Run compression, tension, and triaxial tests.
6. Extract metrics and compare to `references/orthogonal-design.md`.

## New Material Calibration

Use this route when calibrating a new rock:

1. Define target `E`, `nu`, `UCS`, `UCS/UTS`, `phi`, `c`, and `sigma_cd/UCS`.
2. Decide whether source regression equations are acceptable as initial predictors.
3. Back-solve a candidate parameter set using `regression_fast_calibration.py`.
4. Run a validation case.
5. Adjust by trends if errors exceed tolerance.
6. Refit regressions only when specimen size, grading, porosity, or loading path differs substantially.

## Minimal Python Reproduction

```bash
python ../scripts/canonical/regression_fast_calibration.py --show-source-example
python ../scripts/canonical/regression_fast_calibration.py --target-E 12.07 --target-nu 0.202 --target-UCS 82.53 --target-ratio 12
```

## Outputs To Keep

For each calibration campaign, keep:

```text
campaign_manifest.json
orthogonal_design_13params.csv
run_*/params.json
run_*/compress_3d.dat
run_*/tension000.dat
run_*/metrics.json
calibration_summary.csv
regression_report.json
```

Do not bundle large PFC save states, project files, or GUI screenshots inside the public skill.
