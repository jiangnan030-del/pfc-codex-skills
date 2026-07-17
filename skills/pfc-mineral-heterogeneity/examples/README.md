# Example Cases

This directory documents how to use the bundled mineral heterogeneity templates. The actual source-like templates live under `../scripts/canonical/`.

## Directory Layout

```text
scripts/
  canonical/
    mineral_cluster_assignment.p2fis
    mineral_lpbm_parameters.dat
    weibull_damage.p2fis
    otsu_phase_fraction.py
examples/
  README.md
```

## Recommended Validation Cases

### 1. Synthetic granite fractions

Use target fractions from the source example:

```text
mica: 4.81%
quartz: 35.86%
feldspar: 59.32%
```

Validation:

- achieved ball area fractions within tolerance
- contact groups present for each phase
- staged save after mineral assignment

### 2. Per-mineral LPBM assignment

Use the parameter table in `references/parameter-assignment.md` as a starting seed.

Validation:

- contact properties differ by group
- weak phases or interfaces receive intended lower strengths
- `model clean` precedes serious cycling

### 3. Weibull damage sensitivity

Run the same mineral specimen with several shape parameters such as:

```text
beta = 2.0, 3.3, 6.0, 10.0
```

Validation:

- damage multiplier statistics are recorded
- UCS and elastic modulus trends are compared
- random seed is fixed or intentionally varied

## Materialization Pattern

Copy the relevant templates into a clean PFC case folder, then parameterize them through the parent workflow.

Example shell pattern from the skill root:

```bash
mkdir -p my_mineral_case
cp scripts/canonical/*.p2fis scripts/canonical/*.dat my_mineral_case/
```

Then run the staged command files in the appropriate PFC environment.

## Publication Notes

- Do not publish raw private images unless they are cleared for redistribution.
- Store only small, generic templates in the skill.
- Keep large generated save states, project metadata, and output dumps out of the canonical skill assets.
- Report target fractions, achieved fractions, random seed, and interface rule with any result.
