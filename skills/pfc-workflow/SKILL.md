---
name: pfc-workflow
description: Orchestrate evidence-backed ITASCA PFC2D/PFC3D studies across planning, modeling, calibration, solving, post-processing, V&V, and delivery; use for full DEM workflows, model audits, or pfc-code-backed case generation.
---

# PFC Workflow

`pfc-workflow` is the lifecycle orchestrator for complete ITASCA PFC studies. It keeps cross-phase decisions in one place and delegates only specialist work to child skills.

The workflow is **evidence-backed**:

1. user data and case constraints define the physical problem;
2. target-version documentation or `pfc-mcp` is the syntax authority;
3. the pinned `pfc-code` catalog supplies reproducible example/tutorial/verification evidence;
4. local references and child skills supply reusable methods;
5. general model knowledge fills only clearly labeled gaps.

Do not treat an example parameter value or legacy command alias as a universal default.

## When to use

Use this skill when the user wants to:

- create or audit a PFC2D/PFC3D model;
- choose a stage architecture, contact model, boundary condition, or measurement plan;
- build granular, bonded, jointed, heterogeneous, dynamic, thermal, fluid, or coupled cases;
- calibrate micro-parameters against macro targets;
- run UCS, Brazilian, biaxial, triaxial, direct-shear, cyclic, creep, or custom paths;
- automate a campaign through FISH, Python, DOE, surrogates, or optimizers;
- export curves, crack events, force chains, porosity, fabric, fields, or animations;
- prove numerical credibility and deliver a reproducible case package.

If the task is a single narrow specialist question, route directly to the matching child skill. If it spans phases, remain here and delegate only the specialist portion.

## Required inputs

Before writing production commands, obtain or explicitly mark assumptions for:

1. PFC product and version (`PFC2D`/`PFC3D`, 6.0/7.0/later);
2. dimension and unit system;
3. material class and required contact behavior;
4. geometry, particle-size distribution, and target resolution;
5. initial stress/state and boundary modes by axis;
6. loading path, rate, stop condition, and quasi-static/dynamic criterion;
7. calibration targets with units, tolerances, and experimental provenance;
8. output contract: histories, saved states, raw exports, figures, and report metrics;
9. available runtime route: GUI, console, Python/`itasca`, or `pfc-mcp`;
10. run budget, license/parallelism constraints, and delivery deadline.

If a missing item can change the model family or invalidate results, ask for it. Do not hide it behind a guessed default.

## Evidence protocol: pfc-code knowledge base

Read `references/pfc-code-modeling-standard.md` before generating or substantially refactoring a case.

When the repository-level knowledge base is available, query it from the repository root:

```bash
python scripts/query_pfc_code_kb.py "<topic>" --dimension 2d
python scripts/query_pfc_code_kb.py "<topic>" --dimension 3d
python scripts/query_pfc_code_kb.py --check
```

Use the catalog in `../../knowledge/pfc-code/` as follows:

- **tutorial** — feature semantics and command ordering;
- **example** — end-to-end orchestration and stage boundaries;
- **verification** — numerical/analytical check for P6;
- **python** — `itasca`, array, and callback automation;
- **thermal/coupling** — multiphysics and auxiliary-file contracts.

For high-risk logic, prefer an evidence triad: one tutorial, one end-to-end example, and one verification case. Record the pinned commit and source paths in the delivery manifest.

The upstream `pfc-code` repository had no root license file at the pinned review commit. Use metadata, links, hashes, and independently derived rules; do not vendor or relicense upstream source files without a rights review.

## Non-negotiable stage gates

| Gate | Pass condition |
|---|---|
| `G0 Version` | Product/version, dimension, units, and stress sign are explicit; final syntax is checked against that version. |
| `G1 Provenance` | User inputs, experimental targets, example evidence, assumptions, and copied/adapted assets are traceable. |
| `G2 Determinism` | Seed, domain, CMAT defaults, object generation, and boundary identifiers are explicit. |
| `G3 Equilibrium` | Packing/prestress passes a declared convergence criterion; fixed cycle count alone is insufficient. |
| `G4 Contact state` | CMAT intent for future contacts and commands for current contacts are distinguished and audited. |
| `G5 Reset` | After contact-model/bond changes, displacement and unintended residual forces/moments are handled, cycled, re-equilibrated, and saved. |
| `G6 Loading` | Each axis has an explicit control mode; rate/inertia/servo stability and halt logic are checked. |
| `G7 Measurement` | Equations, sign, area/volume, sample interval, histories, measures, and callbacks are initialized before loading. |
| `G8 V&V` | Critical numerical features are verified; physical targets and failure mode are validated within tolerances. |
| `G9 Delivery` | Raw data, state map, parameters, seed, version, source evidence, figures, and rerun instructions are complete. |

Never advance a campaign merely because files exist. A fallback state is not a confirmed physical stage, and a generated scaffold is not a runtime-validated model.

## Workflow

### P1 — Problem definition and plan

Produce a reviewed scope before code:

- question and decision the model supports;
- 2D/3D rationale and scale/resolution rationale;
- material/contact-model hypothesis;
- boundary and loading path;
- target observables and acceptance tolerances;
- numerical verification plan and physical validation data;
- output/delivery contract;
- version/runtime constraints.

Use `templates/scope.md`.

### P2 — Build and initialize

Use a thin driver and explicit stages:

```text
00_scope_or_parameters
10_build_unbonded
20_compact_or_equilibrate
30_install_contacts_or_bonds
40_initialize_instrumentation
50_load_or_solve
60_export
70_verify
```

Required behavior:

1. define domain and CMAT before dependent contact creation;
2. fix a seed for baseline/calibration runs;
3. generate boundaries and particles with documented grading;
4. relax and solve to an explicit equilibrium threshold;
5. restore automatic/physical timestep control after any preparation-only density scaling;
6. identify floaters when relevant;
7. save an unbonded/equilibrated milestone;
8. install contact models/bonds in a separate auditable stage;
9. handle current contacts versus future CMAT assignment explicitly;
10. reset only unintended state, re-equilibrate, and save the initialized baseline.

Read `references/contact-models.md`, `references/advanced-topics.md`, and `references/pfc-code-modeling-standard.md`.

### P3 — Calibration and inversion

Default order:

1. elastic response;
2. strength;
3. post-peak/residual behavior;
4. multi-confinement envelope;
5. structured/heterogeneous variants only after the intact baseline passes.

Choose one route deliberately:

- **manual/servo** — `pfc-servo-calibration`, one parameter family at a time;
- **two levers/two targets** — `dual-target-calibration`, only when rank/crossing prerequisites pass;
- **improved LPBM rapid route** — `pfc-fast-calibration` for the declared 13-factor method;
- **black-box multi-target route** — `LHS -> real runs -> surrogate diagnostics -> Bayesian/RSM/DE proposals -> independent confirmation` using `references/auto-calibration.md` and `references/doe-surrogate.md`.

Every run must map micro parameters to macro outputs in a machine-readable record. A surrogate prediction is not a calibrated result until a true PFC run and an independent confirmation run pass.

### P4 — Solve and run management

- Run a small pilot before an expensive solve.
- Declare timestep mode, damping, inertia criterion, servo limits, callback order, and stop logic.
- Save restart states instead of relying on one long run.
- Remove or re-register callbacks safely across restore/restart boundaries.
- Keep calibration candidates in independent run directories.
- Respect GUI, license, memory, and parallelism limits.

### P5 — Post-process

At minimum, preserve raw data for:

- stress-strain and other governing response curves;
- peak, residual, stage, and stop-status metrics;
- crack/bond-break evolution where relevant;
- force/contact/fabric or coordination statistics;
- porosity/volumetric response where relevant;
- milestone-state map and export provenance.

Cross-check critical stress/strain measures using two independent estimators when practical. Route standard outputs to `pfc-postprocessing`, vedo scenes to `pfc-vedo-postprocess`, and AE/energy/moment-tensor outputs to `pfc-ae-energy`.

Read `references/postprocess.md` and `references/export-paraview.md`.

### P6 — Verification and validation

Verification asks whether the numerical feature is implemented reliably. Use the `pfc-code` verification tier to select feature-level checks such as measure/porosity, wave propagation, bonded-state reset, or thermal expansion.

Validation asks whether the model reproduces physical behavior. Compare curves, key scalars, and failure mode; run seed/resolution/timestep/damping sensitivity as required.

Read `references/vnv-report.md`.

### P7 — Report and deliver

Deliver:

- scope and assumptions;
- version, units, sign convention, seed, and environment;
- parameter/contact-model tables;
- thin driver and stage files;
- saved-state map and raw exports;
- calibration run table and confirmation run;
- verification/validation evidence;
- figures generated from retained data;
- source-evidence manifest and exact rerun command.

## Specialist routing

| Need | Child skill |
|---|---|
| model lifecycle, domain, balls, walls, clumps, rblocks, groups/ranges | `pfc-basics` |
| contact-law selection, CMAT, properties, bonds, inheritance | `pfc-contact-models` |
| UCS, Brazilian, biaxial, triaxial, direct shear, three-point bending | `pfc-standard-tests` |
| stress/force servo and manual micro-to-macro sequence | `pfc-servo-calibration` |
| exactly two active levers and two coupled targets | `dual-target-calibration` |
| improved LPBM 13-factor orthogonal/regression route | `pfc-fast-calibration` |
| FISH functions, callbacks, histories, maps/tables, IO | `pfc-fish` |
| CAD/DXF/STL, wall conversion, geometry-based filling | `pfc-cad-import` |
| assembly quality, boundary servo, loading rate, size effect, curve extraction | `pfc-modeling-techniques` |
| GBM/Voronoi/rblock brittle rock | `pfc-gbm-brittle-rock` |
| mineral segmentation and heterogeneous LPBM | `pfc-mineral-heterogeneity` |
| BPM assumptions and brittle-rock limits | `pfc-brittle-rock-bpm` |
| equivalent crystal network | `pfc-equivalent-crystal-model` |
| flat-joint brittle rock | `pfc-flat-joint-brittle-rock` |
| dynamic/seismic/impact/blasting loading | `pfc-dynamics` |
| stress waves and AE source location | `pfc-stress-wave-aelocation` |
| seepage, CFD, buoyancy, Darcy/FiPy | `pfc-fluid-coupling` |
| PFC-FLAC/FLAC3D coupling | `pfc-flac-coupling` |
| standard curves, fields, VTK/VTP, animation | `pfc-postprocessing` |
| vedo-based 3D scenes | `pfc-vedo-postprocess` |
| AE events, energy, moment tensor, source mechanism | `pfc-ae-energy` |
| Chinese traditional-color chart palette | `xxd-data-viz` |

## Operational routes

### New beginner CPB2D project

Read `references/cpb2d-project-wizard.md`, review `templates/cpb2d_intake.yaml`, and use `scripts/create_cpb2d_project.py` after reading its actual CLI.

The first runtime target is the intact `run_all.dat`. Do not batch cracked cases, calibrate, post-process, or run AE until the intact case has executed in the declared PFC2D version and its saves/CSV/status semantics are checked. `--validate-only` validates the intended scaffold contract; it does not execute PFC.

### Existing project case

Read the actual scripts under `templates/project-case/` before invoking them. Use the existing case runner and export chain rather than rebuilding project-specific logic from memory. If native stage images are missing but milestone states exist, replay exports instead of rerunning the full mechanical solve.

### Automated calibration

Read `scripts/README.md` and the actual `argparse`/schema of each script. The general chain is:

```text
lhs_design.py -> run_campaign.py -> fit_surrogate.py -> optimize_targets.py
```

Do not start until the intact runtime, experiment columns/units, seed reproducibility, and evaluator output contract pass.

## Collaboration with pfc-mcp

When `pfc-mcp` is available:

1. query the `pfc-code` catalog for candidate patterns;
2. check final keywords against target-version documentation;
3. run a minimal syntax/feature probe;
4. run the intact/pilot case;
5. inspect convergence, contact counts, saves, histories, and status;
6. only then scale to calibration or production.

`pfc-code` tells the Agent where proven patterns exist; `pfc-mcp` confirms how to express and execute them in the target environment.

## Output contract

A completed workflow must provide:

- a reviewed scope;
- reproducible entrypoint and stage map;
- version/units/sign/seed metadata;
- parameter and contact assignment tables;
- convergence and state-transition evidence;
- machine-readable histories/metrics;
- milestone states with confirmed/fallback labels;
- calibration and independent confirmation records when applicable;
- V&V results and acceptance decision;
- source-evidence manifest;
- rerun and post-processing instructions.

If runtime execution was unavailable, label the result **static design only** and list the unpassed runtime gates. Never claim a successful PFC solve from static file inspection.

## Local contents

- `references/pfc-code-modeling-standard.md` — source-derived normative stage gates.
- `../../knowledge/pfc-code/` — pinned external catalog, lock, and usage policy.
- `../../scripts/query_pfc_code_kb.py` — offline catalog query/validation.
- `references/contact-models.md` — constitutive-law selection.
- `references/calibration.md`, `auto-calibration.md`, `doe-surrogate.md` — calibration routes.
- `references/postprocess.md`, `export-paraview.md` — output and visualization contracts.
- `references/advanced-topics.md` — shape, DFN, boundaries, coupling, and performance.
- `references/vnv-report.md` — verification, validation, and delivery.
- `references/cpb2d-project-wizard.md` — beginner intake/runtime gate.
- `templates/` — scope, parameter, campaign, scaffold, and project-case assets.
- `scripts/` — scaffold, runner, and calibration helpers; actual source/CLI is authoritative.
- `tests/` — CPB2D scaffold/calibration and dual-target integration contracts.
