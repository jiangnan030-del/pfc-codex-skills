---
name: dual-target-calibration
description: Child skill of pfc-workflow for trial-budget-limited calibration with exactly two active micro-parameter levers and two coupled macro targets, using zero-crossing checkpoints, local 2x2 solves, basin recovery, and controlled sensitivity fine-tuning.
---

# Dual-Target Calibration

Use this child skill through `pfc-workflow` during P3 when a particle or bonded model must match exactly two coupled macro targets with exactly two active levers and a small true-run budget.

Typical pairs are peak strength + peak strain, modulus + strength, or another confirmed non-zero target pair. The method is engine-agnostic; PFC execution remains owned by the parent workflow or a project adapter.

## Parent And Sibling Boundaries

- `pfc-workflow` owns intake, experiment provenance, case generation, true-run orchestration, campaign recovery, V&V, and delivery.
- `dual-target-calibration` owns the two-lever/two-target numerical decision method and its four submission checkpoints.
- `pfc-servo-calibration` owns stress/force servo and loading-boundary stability.
- `pfc-fast-calibration` owns the PFC3D improved-LPBM 13-factor orthogonal/regression route.
- `pfc-workflow` auto-calibration owns LHS, surrogate, Bayesian, RSM, and DE campaigns when more than two levers are active or local two-target assumptions fail.

Do not route here for a single target, more than two independent levers, unconfirmed experimental units, or an unrepeatable baseline.

## Required Inputs

Before any trial, require:

- confirmed target A and B values, units, signs, source rows, and provenance
- exactly two active levers X and Y, with finite increasing physical bounds
- linked parameters expressed only as `factor * parameter`
- all remaining parameters frozen
- fixed geometry, random seed, loading path, stop criteria, and output contract
- `thresholds` and `budget` copied from `config.example.yaml` into the project
- project implementations of `adapters/submit.py`, `check.py`, and `target.py`

The installed skill is read-only guidance. Copy config, adapters, and log templates into the project artifact directory; never write trial results into `skills/dual-target-calibration/`.

## When To Use

Use this method only when all are true:

1. exactly two macro targets are scored
2. exactly two independent levers are active
3. each run is expensive enough that a small sequential design matters
4. local response surfaces may be discontinuous but still contain identifiable basins
5. the baseline case already runs reproducibly

Otherwise return to `pfc-workflow` and select manual family tuning or LHS/surrogate optimization.

## Workflow

### S0 - Configure Project Copies

Copy:

- `config.example.yaml` -> `<project>/calibration/dual-target/config.yaml`
- `adapters/*.py` -> `<project>/calibration/dual-target/adapters/`
- `templates/*.md` -> `<project>/calibration/dual-target/logs/`

Fill targets, lever bounds, linked/frozen parameters, thresholds, and budget. Adapter templates intentionally block until connected to a real engine and experiment contract.

### S1 - Confirm Targets

Implement `target(source, config)` against the confirmed experiment data. Call `write_targets()` only after units, specimen identity, row policy, and compression/tension sign are confirmed.

### S2 - Seed Trial

Prefer extrapolation from a confirmed sibling case. Without one, use the physical-bound geometric midpoint and widen the next zero-crossing probes. If either relative error exceeds `thresholds.seed_divergence`, treat the seed as a wrong basin; do not continue local regression from it.

### S3 - Dual Zero-Crossing

Collect trials until both target error sets contain values on both sides of zero. The crossing pairs may differ between A and B.

**CHECKPOINT 1:** both target errors have mixed signs. No regression before this passes.

### S4 - Local Exact Solve

Select three explicitly identified, non-collinear, same-basin trials and run:

```bash
python scripts/regress_exact.py trials.csv config.yaml --rows I J K
```

The script rejects same-sign targets, excessive B-error span, rank-deficient designs, rank-deficient target responses, and out-of-bound solutions.

**CHECKPOINT 2:** only submit the predicted point when the CLI exits `0`.

### S5 - Basin Recovery

When the exact solve detects a basin jump or unsafe solution, collect at least 4-6 deliberately distributed points and run:

```bash
python scripts/regress_lstsq.py trials.csv config.yaml
```

**CHECKPOINT 3:** both response surfaces must meet `thresholds.regression_r2`, the design and response matrices must have full rank, and the predicted point must remain inside physical bounds.

### S6 - Controlled Sensitivity Fine-Tune

Estimate X sensitivity only from a pair whose Y difference is within `thresholds.sensitivity_max_relative_y_change`:

```bash
python scripts/sensitivity.py trials.csv config.yaml
```

**CHECKPOINT 4:** a detected basin jump stops local fine-tuning. Accept the nearest confirmed candidate or return to basin recovery; do not cross the boundary by repeated tiny steps.

### S7 - Archive And Handoff

Record every attempted point, including failures, in the project ledger. Hand back to `pfc-workflow`:

- confirmed target contract and tolerances
- X/Y bounds, linked/frozen parameters, seed, and engine version
- complete `trials.csv` with status/failure reason/artifact path
- checkpoint outputs and selected regression rows
- best confirmed candidate and independent confirmation run
- per-target errors and whether both pass
- basin/fallback/safety-stop evidence

Do not call a result calibrated unless both target tolerances pass on a confirmation run.

## Failure And Budget Rules

- `budget.escalate_at` permits a reviewed structural-model change; it does not authorize silently opening a third lever.
- `budget.max_trials` is a hard stop. Expanding it requires a new parent-workflow decision.
- Failed or timed-out submissions remain in the ledger; check for existing artifacts before retrying.
- A regression prediction is a proposal, not evidence. Only a true engine run can pass.
- If R2 stays poor, crossings cannot be obtained, or response rank is below 2, return to `pfc-workflow` for LHS/surrogate or model-structure review.

## Local Contents

- `config.example.yaml`: project-copy configuration template.
- `adapters/`: safe project adapter contracts; no default engine side effects.
- `scripts/dual_target_common.py`: validated numerical core.
- `scripts/regress_exact.py`: CHECKPOINT 1/2 exact local solve.
- `scripts/regress_lstsq.py`: CHECKPOINT 3 basin recovery.
- `scripts/sensitivity.py`: CHECKPOINT 4 controlled sensitivity.
- `references/parameter-effects.md`: lever-role guidance.
- `references/basin-recovery.md`: discontinuous-response diagnosis.
- `references/anti-patterns.md`: trial-budget failure modes.
- `examples/pfc2d-ctb-fissured.md`: historical method example; qualitative transfer only.
- `templates/`: project ledger and experience-log templates.
- `LICENSE` and `NOTICE.md`: AGPL-3.0 licensing and provenance for this child skill.
