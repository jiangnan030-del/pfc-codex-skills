---
name: pfc-skill-pack
description: Shared hub for the PFC skill family, defining routing, reusable references, migration rules, plugin policy, and repository packaging conventions.
---

# PFC Skill Pack

Use this skill as the shared governance layer for a PFC skill family. It is not a modeling specialist by itself; it defines how the individual PFC skills relate, what common references they should use, and how to keep the package portable for GitHub or other public distribution.

## Role In The Skill Family

`pfc-skill-pack` is the package-level hub. It coordinates conventions but does not replace specialist skills.

Recommended hierarchy:

```text
pfc-skill-pack
  └─ pfc-workflow
      ├─ pfc-standard-tests
      ├─ pfc-postprocessing
      └─ pfc-ae-energy
```

Other domain skills, such as contact-model, FISH, CAD import, dynamics, coupling, and calibration skills, should follow the same rules in this pack while remaining focused on their own topic boundary.

## When To Use

- Organize or audit a PFC skill repository before publishing.
- Decide which PFC subskill should handle a user request.
- Apply shared PFC 5-to-PFC 6 compatibility checks.
- Define what assets can be bundled and what should remain external.
- Replace private/local paths with relative package paths.
- Document plugin or legacy-tool workflows without making black-box executables mandatory.

## Working Rules

- Keep public skills self-contained: use relative paths and bundled templates where redistribution is allowed.
- Put executable helper code under `scripts/`.
- Put reusable prompt/document templates under `templates/`.
- Put shared policy and compatibility references under `references/`.
- Avoid local absolute paths, private download folder names, or project-specific directories.
- Do not make old `.exe` tools or binary save states the core implementation surface.
- Specialist skills should expose: when to use, required inputs, runnable assets, outputs, and PFC-version caveats.

## Routing Summary

- `pfc-workflow`: parent orchestrator for complete model lifecycle.
- `pfc-standard-tests`: child skill for canonical laboratory-test templates and stage normalization.
- `pfc-postprocessing`: child skill for standard figures, fields, exports, animations, and report tables.
- `pfc-ae-energy`: child skill for AE, energy, event clustering, and source-mechanism plots.
- `pfc-fast-calibration`: child skill for improved LPBM fast calibration using strong/weak contact grouping, Weibull damage, orthogonal design, and regression back-solving.
- `dual-target-calibration`: child skill for exactly two active levers and two coupled targets under a tight trial budget, with zero-crossing, guarded local solves, basin recovery, and sensitivity checkpoints.
- `pfc-gbm-brittle-rock`: child skill for PFC2D GBM/equivalent-crystal brittle-rock modeling with smooth-joint grain boundaries, prefabricated cracks, biaxial loading, fracture tracking, and energy histories.
- `pfc-stress-wave-aelocation`: child skill for stress-wave propagation, Ricker excitation, dispersion and boundary checks, cross-correlation time delays, and velocity-free AE source localization.
- Foundation skills such as basics, FISH, contact models, and servo calibration should be invoked by `pfc-workflow` when their specialized topic is needed.
- Advanced skills such as CAD import, fluid coupling, FLAC coupling, and dynamics should be routed only when the workflow requires those physics or preprocessing paths.

## Shared References

Read these before making package-level changes:

- `references/asset-inventory.md`: portable asset classes and inclusion rules.
- `references/pfc5-to-pfc6-migration-map.md`: shared compatibility checklist.
- `references/plugin-catalog.md`: grouped plugin/tool taxonomy.
- `references/plugin-migration-strategy.md`: policy for replacing or documenting legacy tools.

## Scripts And Templates

- `scripts/build_skill_index.py`: lists sibling skill folders that contain `SKILL.md`.
- `scripts/README.md`: script placement and future helper guidance.
- `templates/case-intake.md`: generic intake form for adding or auditing a skill case.

## Output Contract

When using this hub, return:

- The selected specialist skill or skill relationship.
- The shared reference file that justifies the decision.
- A portable folder/path convention using only relative paths.
- Any required compatibility or redistribution warnings.
- A clear handoff back to `pfc-workflow` when the task becomes a concrete modeling workflow.

## Local Contents

- `README.md`: shared skill-pack overview and publication checklist.
- `references/asset-inventory.md`: source, generated, binary, and private-asset inclusion rules.
- `references/pfc5-to-pfc6-migration-map.md`: compatibility and migration checklist.
- `references/plugin-catalog.md`: legacy plugin taxonomy.
- `references/plugin-migration-strategy.md`: replacement and documentation policy for old tools.
- `scripts/build_skill_index.py`: helper for sibling-skill inventory.
- `templates/case-intake.md`: reusable intake form for adding or auditing cases.

