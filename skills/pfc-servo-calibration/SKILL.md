---
name: pfc-servo-calibration
description: Child skill of pfc-workflow for PFC 6.0 servo-control patterns and micro-to-macro calibration sequencing.
---

# PFC Servo And Calibration

Use this skill to explain, adapt, or generate PFC 6.0 servo-control snippets and calibration sequencing plans. The skill is self-contained: canonical servo demonstration `.dat` files are stored under `scripts/canonical/`.

## Parent Skill Relationship

`pfc-servo-calibration` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for servo logic, stress-control snippets, and calibration sequence design; return to `pfc-workflow` for full case planning, solve orchestration, post-processing routing, verification, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns complete PFC project lifecycle and decides when servo/calibration support is needed.
- Child `pfc-servo-calibration`: owns wall/ball servo concepts, stress-control checklists, tuning order, and bundled servo demonstration templates.
- Sibling child `pfc-standard-tests`: owns standard test templates and stage normalization.
- Sibling child `pfc-postprocessing`: owns standard figures and field exports after solve.
- Sibling child `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs after solve.

## When To Use

Use through `pfc-workflow` when the task reaches stress control or parameter tuning:

- Explain wall servo logic, target stress/force control, or stiffness-based velocity updates.
- Add or review servo-control FISH code for walls, platens, biaxial cells, or triaxial confinement.
- Plan manual micro-to-macro calibration order for bonded or granular specimens.
- Convert a simple target-force example into a reusable PFC 6.0 snippet.
- Diagnose unstable servo gains, overshoot, timestep issues, or oscillating boundary forces.

## Required Inputs

Ask for these if missing:

- PFC version and dimensionality: PFC2D or PFC3D, preferably PFC 6.0 unless stated otherwise.
- Control target: force, stress, strain, displacement, confining pressure, or mixed control.
- Controlled boundary: wall ID/name, ball group, platen pair, membrane, or cell boundary.
- Macro targets: elastic modulus, UCS/peak strength, Poisson ratio, friction angle, cohesion, residual strength, or peak strain.
- Test family used for calibration: UCS, biaxial, triaxial, Brazilian, direct shear, or custom.
- Current snippet or case files if the user is debugging an existing servo.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| Servo principles | `scripts/canonical/servo-principles/` | `1sifu_1.dat`, `2sifu_2.dat`, `3sifu_3.dat`, `3sifu_4.dat`, `4sifu_4_jixu.dat` | Minimal PFC 6.0 target-force and stiffness-based wall/ball servo demonstrations. |

## Servo Control Checklist

Use this checklist before writing or changing servo logic:

1. Identify the controlled object and target component, e.g. `wall.force.contact.y(wp)`.
2. Compute or estimate current contact stiffness in the controlled direction.
3. Convert target force/stress error to displacement increment using stiffness.
4. Convert displacement increment to velocity using timestep or update interval.
5. Limit maximum velocity to avoid overshoot.
6. Update stiffness periodically because contact maps change during compaction and failure.
7. Save a state before enabling servo and another after reaching target stress.
8. Track histories for target, actual force/stress, error, and boundary velocity.

## Calibration Order

Default manual calibration sequence:

1. Geometry and PSD: specimen size, particle radius range, porosity, seed.
2. Elastic response: tune particle/contact modulus and stiffness ratio first.
3. Poisson/lateral response: adjust stiffness ratio and boundary condition assumptions.
4. Peak strength: tune bond tensile/cohesive/shear strength after elastic slope is acceptable.
5. Post-peak and residual: tune friction, damping, softening logic, or contact model choice.
6. Failure mode: inspect cracks, shear bands, force chains, and boundary effects.
7. Robustness: repeat with at least one different seed or resolution if results are sensitive.

## Working Rules

- Prefer PFC 6.0-compatible syntax unless the user explicitly targets another version.
- Keep servo snippets small and test them in isolation before embedding them in a full model.
- Treat files in `scripts/canonical/` as reference templates, not final calibrated models.
- Do not hide calibration logic in GUI-only steps or binary save states.
- Preserve milestone saves around stress-control stages.
- If automated calibration is requested, hand control back to `pfc-workflow` after defining parameter bounds, macro targets, and servo-safe run constraints.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- The selected servo/calibration pattern and why it fits.
- Required files or snippets from `scripts/canonical/<case>/`.
- Controlled boundary, target variable, measured variable, and update rule.
- Histories to record for servo validation.
- Calibration parameter order and stop criteria.
- Stability warnings: timestep, damping, gain/velocity cap, stiffness refresh, and overshoot risk.
- A clear note that full case execution, post-processing routing, V&V, and delivery continue in `pfc-workflow`.

## Local Contents

- `references/overview.md`: detailed self-contained servo/calibration boundaries and source map.
- `examples/README.md`: how to validate bundled servo demonstrations.
- `scripts/canonical/`: servo demonstration code.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
