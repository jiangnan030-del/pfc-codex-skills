# Verification, Validation, and Reporting

Use this file when the user asks how to prove the workflow is credible and deliverable.

## Verification

Ask whether the numerical setup is solving the intended model reliably.

Typical checks:

- resolution or particle-count sensitivity
- timestep sensitivity
- damping sensitivity
- comparison with analytic or benchmark behavior where possible

## Validation

Ask whether the model matches the target physical behavior.

Typical checks:

- agreement with laboratory tests such as UCS, Brazilian, or triaxial curves
- agreement with observed failure mode, not just peak values
- multiple random seeds if variability matters

## Reporting package

A strong delivery bundle contains:

- parameter tables
- seeds and version information
- saved-state map
- exported raw data behind all figures
- figure set and summary metrics
- concise notes on assumptions, limits, and remaining mismatch

## Review questions

- Is the baseline specimen validated before complex variants?
- Are plots reproducible from exported data?
- Can another machine rerun the workflow without private paths?
- Are numerical and physical uncertainties both acknowledged?
