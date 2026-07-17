---
name: pfc-workflow
description: Build, calibrate, solve, and post-process a complete ITASCA PFC workflow through a reusable skill. Use when the user asks about PFC2D/PFC3D, DEM, particle flow, bonded or granular specimens, micro-parameter calibration, UCS/Brazilian/biaxial/triaxial tests, force chains, crack evolution, porosity, VTK/VTP export, ParaView/PyVista post-processing, Bayesian optimization, Latin hypercube sampling, DOE, surrogate models, or automated calibration.
---

# PFC Workflow

This is the primary workflow skill for ITASCA PFC studies. It sits under
`pfc-skill-pack`, which owns shared package conventions and references, and it
owns the full project lifecycle: planning, specimen generation, calibration,
solving, post-processing routing, V&V, and delivery. Treat it as the
orchestrator skill for concrete PFC work.

Use subskills only through this workflow split:

- `pfc-basics`: foundation PFC 6.0 model lifecycle, domain, balls, walls,
  clumps, rblocks, groups, ranges, and minimal runnable setup patterns; use
  during P1-P2 when the case needs basic object creation before specialist routing
- `pfc-standard-tests`: canonical PFC 6.0 UCS, biaxial, triaxial,
  direct shear, Brazilian, and three-point bending test templates; use during
  P1-P2 when selecting or materializing a standard laboratory-test command flow
- `pfc-cad-import`: CAD/DXF/STL/geometry import, wall conversion, particle
  filling contracts, clump/rblock templates, and legacy helper-app preservation;
  use whenever the case starts from external geometry or preprocessing tools
- `pfc-mineral-heterogeneity`: digital image or mineral-fraction intake,
  mineral clusters, per-mineral LPBM parameters, interface contacts, and
  Weibull damage; use when rock behavior depends on mineral composition or
  heterogeneous phase distribution
- `pfc-gbm-brittle-rock`: PFC2D grain-based brittle-rock modeling, Voronoi/
  rblock GBM construction, smooth-joint grain boundaries, prefabricated cracks,
  biaxial loading, fracture tracking, and energy histories; use when the case
  is a GBM/equivalent-crystal brittle-rock workflow rather than generic mineral
  heterogeneity or FJM3D
- `pfc-contact-models`: contact-law selection, CMAT setup, contact properties,
  bond activation methods, property inheritance, and contact-level validation;
  use whenever the case needs nontrivial contact model design or audit
- `pfc-servo-calibration`: wall/ball servo logic, stress-control snippets,
  target-force/stress convergence checks, and manual micro-to-macro tuning
  order; use during P2-P3 when boundary control or calibration sequencing is
  the specialist task
- `pfc-fast-calibration`: improved LPBM rapid micro-parameter calibration,
  13-factor orthogonal design, strong/weak contact grouping, Weibull damage,
  Pearson correlation, regression formulas, and macro-target back-solving; use
  during P3 when a bonded-rock calibration needs a fast multi-parameter route
- `pfc-fish`: FISH functions, callbacks, histories, IO helpers, maps/tables,
  object traversal, and reusable helper-file refactoring; use whenever the
  case needs nontrivial FISH logic or legacy FISH audit
- `pfc-dynamics`: dynamic/seismic loading, imposed motion, damping/timestep
  audits, kinetic/strain-energy histories, slope-motion, and blasting-style
  reference review; use whenever inertial response or time-dependent loading is central
- `pfc-stress-wave-aelocation`: stress-wave propagation, Ricker excitation,
  dispersion checks, absorbing boundaries, P/S wavefronts, radiation patterns,
  cross-correlation time delays, and velocity-free AE source localization; use
  when the task is elastic-wave or AE-location specific rather than generic
  dynamic loading
- `pfc-fluid-coupling`: seepage, buoyancy, CFD element setup, Darcy/FiPy
  coupling notes, and fluid-related auxiliary file contracts; use when the
  loading path includes pore pressure, water, drag, or flow-solid interaction
- `pfc-flac-coupling`: PFC-FLAC/FLAC3D discrete-continuum handoff,
  wall-zone/interface coupling, continuum-particle stage contracts, and
  version-risk notes; use when a continuum solver is part of the model
- `pfc-postprocessing`: standard non-AE figures, fields, native stage plots,
  VTP/VTK outputs, animations, and summary tables
- `pfc-vedo-postprocess`: vedo-based PFC/DEM visualization for exported
  particles, force chains, cracks, displacement or velocity vectors, slices,
  and publication-quality 3D animations; use during P5 when the user wants a
  Python/vedo route rather than ParaView/PyVista/native plotting
- `pfc-ae-energy`: AE event export, AE energy metrics, clustered events,
  mechanism plots, and Hudson/T-k style source analysis

If a task spans more than one phase, stay in `pfc-workflow` and delegate only
the specialist parts to those subskills.

## When to use

Use this skill when the user wants to:

- build a PFC2D or PFC3D model from scratch
- choose contact models for granular, bonded, or jointed materials
- calibrate micro-parameters against macro targets such as modulus, strength, friction angle, cohesion, or peak strain
- run UCS, Brazilian, biaxial, triaxial, direct shear, creep, cyclic, or coupled analyses
- export force chains, crack data, porosity, stress-strain curves, or field plots
- structure a PFC repository, reproducible workflow, or publishable DEM project
- automate calibration with Bayesian optimization, DOE, LHS, surrogate models, response surfaces, or differential evolution

## First rules

1. Confirm the target PFC version before drafting commands. Syntax differs across PFC 6.0, 7.0, and later releases.
2. If the user has `pfc-mcp`, use it to verify command syntax and run small trial snippets before long solves.
3. Always fix random seeds, separate parameters from command flow, and save milestone states.
4. During calibration, move one parameter family at a time unless the task is explicitly an automated optimization campaign.
5. Prefer reproducible exports over manual GUI-only screenshots.
6. For expensive black-box calibration, default to `LHS -> surrogate -> Bayesian optimization`, not brute-force trial-and-error.

## Lifecycle

Follow this seven-phase lifecycle unless the user explicitly narrows scope:

- `P1` Problem definition and planning
- `P2` Preprocessing and specimen generation
- `P3` Calibration and parameter inversion
- `P4` Solve control and run management
- `P5` Post-processing and visualization
- `P6` Verification and validation
- `P7` Report and reproducible delivery

## Routing guide

Read the matching reference files before answering in depth:

- `references/contact-models.md` for contact law selection
- `references/calibration.md` for manual micro-to-macro mapping and tuning order
- `references/auto-calibration.md` for Bayesian optimization, differential evolution, response surfaces, and campaign logic
- `references/doe-surrogate.md` for Latin hypercube sampling, surrogate fitting, cross-validation, and sample-efficiency strategy
- `references/postprocess.md` for histories, measures, crack monitoring, and output lists
- `references/export-paraview.md` for VTK/VTP/CSV export and ParaView or PyVista workflows
- `references/advanced-topics.md` for clumps, DFN, periodic boundaries, coupled physics, automation, and performance traps
- `references/vnv-report.md` for verification, validation, and delivery standards

Use these subskills as children, not peers:

- `pfc-basics` during planning/modeling when the task needs a clean model start,
  domain extents, basic balls/walls/clumps/rblocks, groups, ranges, or a minimal
  runnable foundation before routing to a more specialized child skill
- `pfc-standard-tests` during planning/modeling when the loading path is a
  canonical laboratory test and the case should start from a reusable PFC 6.0
  template or normalized stage list
- `pfc-cad-import` during planning/preprocessing when the task starts from
  CAD/DXF/STL/FEM geometry, external preprocessing apps, wall import, particle
  filling, clump templates, rblocks, or geometry-based range selection
- `pfc-mineral-heterogeneity` during planning/modeling/calibration setup when
  the task starts from mineral fractions, segmented rock images, phase maps,
  mineral clusters, per-mineral LPBM parameters, phase-interface contacts, or
  Weibull damage heterogeneity
- `pfc-gbm-brittle-rock` during planning/modeling/solve setup when the task is
  a PFC2D GBM/equivalent-crystal brittle-rock case with Voronoi/rblock grain
  geometry, mineral-body LPBM contacts, smooth-joint grain boundaries,
  prefabricated cracks, biaxial loading, fracture tracking, or energy histories
- `pfc-contact-models` during planning/modeling/calibration setup when the task
  needs contact-law selection, CMAT/property/method ordering, bond activation,
  inheritance assumptions, or contact-level validation
- `pfc-servo-calibration` during modeling/calibration when the task needs
  stress/force servo control, stiffness-based boundary updates, or a manual
  micro-to-macro tuning sequence
- `pfc-fast-calibration` during calibration when the task needs improved LPBM
  strong/weak contacts, Weibull damage, 13-factor orthogonal design, Pearson
  correlation, regression formulas, or quick back-solving from macro targets
- `pfc-fish` during planning/modeling/solve setup when the task needs FISH
  functions, callbacks, histories, object traversal, data IO, maps/tables, or
  refactoring reusable helper files
- `pfc-dynamics` during planning/modeling/solve setup when the task needs
  dynamic/seismic loading, waveform or imposed-motion design, damping/timestep
  checks, kinetic-energy histories, slope motion, impact, or blasting-style references
- `pfc-stress-wave-aelocation` during planning/modeling/solve/postprocessing
  when the task needs stress-wave propagation, Ricker or sine sources,
  dispersion checks, absorbing boundaries, P/S wavefronts, radiation patterns,
  sensor waveforms, cross-correlation time delays, or velocity-free AE source
  localization
- `pfc-fluid-coupling` during planning/modeling when the task needs fluid-solid
  coupling, buoyancy, CFD mesh files, seepage-force assumptions, or Python
  Darcy/FiPy coupling handoff
- `pfc-flac-coupling` during planning/modeling when the task needs a continuum
  FLAC/FLAC3D domain coupled to PFC particles, wall-zone/interface handoff, or
  coupled save-state staging
- `pfc-postprocessing` after the mechanical solve when the need is standard
  figures/fields/animations without AE specialization
- `pfc-vedo-postprocess` after the mechanical solve when the user specifically
  wants vedo, lightweight scripted 3D rendering, particle/force-chain/crack
  scenes, cut-away shear-band views, or DEM animations from exported PFC data
- `pfc-ae-energy` only when the case needs AE exports, AE plots, moment-tensor
  interpretation, or T-k / Hudson style outputs

## Default workflow

### P1 Planning

Define five items before touching code:

1. dimensionality: 2D or 3D
2. specimen/material class: granular, bonded, jointed, or coupled
3. loading path: UCS, Brazilian, biaxial, triaxial, direct shear, cyclic, creep, or custom
4. target observables: strength, modulus, peak strain, crack evolution, porosity, residual behavior, or failure mode
5. output contract: which curves, tables, field plots, and saved states must be reproducible

Use `templates/scope.md` as the planning skeleton.

### P2 Modeling

Build a representative specimen with a fixed seed, documented grading, explicit boundaries, and staged saves such as compacted, bonded, and loaded states.

If the loading path is a standard test, first route the template selection and
stage normalization through `pfc-standard-tests`; then return to
`pfc-workflow` for parameterization, calibration, solve planning, and delivery.

Read `references/contact-models.md` before choosing `linear`, `linearcbond`, `linearpbond`, `flatjoint`, `rrlinear`, or `hertz`.

### P3 Calibration

Use this sequence by default:

1. calibrate elastic response first with `emod` and stiffness ratio
2. calibrate strength next with bond strength parameters
3. calibrate frictional behavior and failure envelope after elastic and strength baselines are stable
4. switch to automated optimization when manual steering no longer yields predictable gains
5. stop when the selected macro targets meet the user-defined tolerance

If calibration depends on target stress/force control, confining pressure,
servo-wall stability, or tuning-order explanation, route that specialist portion
through `pfc-servo-calibration`; then return to `pfc-workflow` for the campaign
or final solve plan.

If calibration needs improved LPBM strong/weak contacts, Weibull damage,
13-parameter orthogonal design, Pearson correlation, regression equations, or
macro-target back-solving, route the specialist calibration portion through
`pfc-fast-calibration`; then return to `pfc-workflow` for campaign execution,
validation, post-processing routing, and delivery.

Use `templates/params.yaml` for simple manual bounds and `templates/calibration_campaign.yaml` for automated campaigns.

### P4 Solve control

Use small pilot solves before full runs. Control time step, damping, stop criteria, and batch strategy explicitly. Save restart states rather than relying on one long fragile run.

### P5 Post-processing

At minimum, expect reproducible exports for:

- stress-strain data
- peak and residual metrics
- crack count or damage evolution
- force chains or contact-force fields
- porosity or volumetric response
- saved states tied to plotting stages

At this phase, route work as follows:

- standard curves/fields/stage/native plots -> `pfc-postprocessing`
- vedo 3D particle/force-chain/crack/vector/slice/animation rendering -> `pfc-vedo-postprocess`
- AE/energy/mechanism plots -> `pfc-ae-energy`

### P6 Verification and validation

Separate these two checks:

- verification: numerical settings, sensitivity to resolution, timestep, damping, or solver settings
- validation: agreement with experiments, field data, or accepted benchmark behavior

### P7 Delivery

Deliver three artifact classes:

- model and exported data
- figures and summary tables
- method/report text with version, seeds, parameter tables, and command flow traceability

## Foundation basics route

When the user asks for basic PFC command order, `model new`, domain setup,
balls, walls, clumps, rblocks, groups, named ranges, or a minimal runnable
foundation model, route the specialist setup portion through `pfc-basics`; then
return to `pfc-workflow` for contact-model routing, calibration, solve strategy,
validation, and delivery.

## CAD and geometry route

When the user asks for CAD/DXF/STL import, geometry sets, wall import, geometry
export, external helper apps, particle filling from CAD/FEM regions, clump or
rblock templates, or geometry-based range selection, route the specialist
preprocessing portion through `pfc-cad-import`; then return to `pfc-workflow`
for contact models, calibration, solve strategy, validation, and delivery.

## Mineral heterogeneity route

When the user asks for digital-image mineral segmentation, mineral fractions,
quartz/feldspar/mica or other phase-aware rock models, cellular mineral
clusters, per-mineral LPBM parameters, phase-interface contact rules, or
Weibull damage distribution, route the specialist specimen-construction and
parameter-assignment portion through `pfc-mineral-heterogeneity`; then return
to `pfc-workflow` for full calibration campaign control, solve strategy,
post-processing routing, V&V, and delivery.

## GBM brittle-rock route

When the user asks for GBM, equivalent crystal modeling, PFC2D brittle rock
with mineral grain geometry, Voronoi/rblock grain construction, smooth-joint
grain boundaries, prefabricated crack biaxial compression, fracture tracking,
or crack/energy histories from the migrated GBM case, route the specialist
construction and monitoring portion through `pfc-gbm-brittle-rock`; then return
to `pfc-workflow` for full campaign control, validation, post-processing
routing, and delivery.

## Contact model route

When the user asks for contact laws, CMAT setup, linear/parallel-bond/Hertz/
flat-joint/smooth-joint/soft-bond selection, contact properties, bond methods,
property inheritance, or contact-level validation, route the specialist
contact-design portion through `pfc-contact-models`; then return to
`pfc-workflow` for full case staging, macro calibration, validation, and delivery.

## Fast calibration route

When the user asks for improved parallel-bond fast calibration, high UCS/UTS
ratio correction, strong/weak contact grouping, Weibull damage for calibration,
13-factor orthogonal design, Pearson correlation, macro-micro regression, or
back-solving micro-parameters from macro targets, route the specialist
calibration-method portion through `pfc-fast-calibration`; then return to
`pfc-workflow` for full campaign control, standard-test routing, V&V, and
reproducible delivery.

## FISH helper route

When the user asks for FISH functions, callbacks, histories, IO, maps/tables,
object traversal, data recording, reusable helper files, or legacy FISH snippet
audits, route the specialist code-design portion through `pfc-fish`; then
return to `pfc-workflow` for full case staging, solve strategy, validation, and
delivery.

## Dynamics route

When the user asks for dynamic/seismic loading, imposed motion, waveform input,
impact, slope motion, blasting/demolition references, damping audits, timestep
stability, or kinetic/strain-energy response histories, route the specialist
dynamic-design portion through `pfc-dynamics`; then return to `pfc-workflow`
for full case staging, solve strategy, validation, and delivery.

## Stress-wave and AE-location route

When the user asks for stress waves, elastic waves, P/S wave speed,
wavefronts, radiation patterns, Ricker wavelets, numerical dispersion,
absorbing/free/rigid boundaries, sensor arrays, arrival-time differences,
cross-correlation, Kundu velocity-free localization, arbitrary-triangle sensor
clusters, pencil-lead-break validation, or AE source coordinates, route the
specialist wave and localization portion through `pfc-stress-wave-aelocation`;
then return to `pfc-workflow` for full campaign control, specimen calibration,
post-processing routing, V&V, and delivery.

## Advanced physics route

When the user asks for seepage, buoyancy, CFD elements, pore pressure, drag,
Darcy flow, or water-particle interaction, route the specialist fluid-coupling
portion through `pfc-fluid-coupling`; then return to `pfc-workflow` for the full
case plan, solve strategy, post-processing routing, V&V, and delivery.

When the user asks for PFC-FLAC/FLAC3D, discrete-continuum coupling, continuum
zones plus particles, wall-zone coupling, or coupled FLAC/PFC save-state
staging, route the specialist handoff portion through `pfc-flac-coupling`; then
return to `pfc-workflow` for the full case plan, solve strategy,
post-processing routing, V&V, and delivery.

For dynamics, blasting, thermal, or other advanced topics, read
`references/advanced-topics.md` and use the relevant specialist skill if one is
available.

## Automated calibration stance

When the user asks about `贝叶斯优化`, `LHS`, `拉丁超立方`, `代理模型`, `DOE`, `响应面`, `遗传算法`, or `自动标定`, answer with this default sequence:

1. define parameter bounds and macro targets
2. generate LHS initial samples
3. evaluate true cases and save standardized records
4. fit surrogate models and inspect cross-validation error
5. run sequential Bayesian optimization with one expensive case per iteration
6. fall back to response-surface or differential-evolution search only when the surrogate route is unstable or the objective is too rough
7. export best parameters plus convergence and diagnostics plots

## Bundled scripts

The skill includes reusable campaign templates:

- `scripts/lhs_design.py`
- `scripts/run_campaign.py`
- `scripts/fit_surrogate.py`
- `scripts/optimize_targets.py`
- `scripts/plot_campaign_diagnostics.py`
- `scripts/runner_template.py`

Use these as patterns for public repositories. They are intentionally generic and do not assume any local PFC project layout.

## Complete case route

For a project that already has per-case folders such as `b90_d18`, prefer a
single-case runner route instead of rebuilding the workflow by hand.

Project-style runner and helpers are bundled under:

- `templates/project-case/run_case.py`
- `templates/project-case/generate_cases.py`
- `templates/project-case/config.py`
- `templates/project-case/postprocess_results_2d.py`
- `templates/project-case/plot_contours_2d.py`
- `templates/project-case/plot_peak_fields.py`
- `templates/project-case/plot_stage_contact_maps.py`
- `templates/project-case/analyze_stress_strain.py`
- `templates/project-case/gen_force_chain_vtp.py`
- `templates/project-case/render_force_chain.py`
- `templates/project-case/export_stage_contact_python_data.py`

Use this route when the user wants to run one full case from calibrated inputs
through solve, native exports, post-processing, and verification.

### Recommended execution order

1. generate or verify the case directory and common files
2. calibrate micro-parameters with `--solve-only` first
3. once macro targets are acceptable, switch the case to AE/heavy export mode
4. run the full case solve
5. refresh standard post-processing figures
6. refresh AE figures with the AE skill route
7. verify expected artifacts before delivery

This split is intentional:

- `pfc-workflow` decides when the case is ready for each phase
- `pfc-postprocessing` owns standard figure regeneration
- `pfc-vedo-postprocess` owns vedo-specific 3D scene and animation regeneration from exported PFC data
- `pfc-ae-energy` owns AE-heavy regeneration

### Interpreter split

In this project pattern, different Python environments may be appropriate for
different stages:

- bridge / `pfc-mcp` solve driving: use the interpreter that already has
  `websockets`
- AE plotting: use the interpreter that has the scientific plotting stack used
  by `plot_ae_energy.py`

Do not assume one interpreter is correct for both.

### Typical commands

Calibrate or check one case without AE/full plots:

```powershell
python .\run_case.py b90_d18 --solve-only
```

Run a full solved case with standard post-processing:

```powershell
python .\run_case.py b90_d18 --skip-native
```

If native stage plots are missing after the solve, replay only the native
exports from saved states instead of rerunning the whole simulation.

### Expected outputs for one complete case

- `stress_strain.csv`
- `curve_compare_2d.png`
- `curve_metrics_2d.xlsx`
- `plot_*_peak.*` and `plot_*_final.*`
- `plotdata_contacts_stage_*.csv`
- `plotdata_measures_stage_*.csv`
- `stage_*_native.png`
- `stage_*_fracture_only.png`
- `stage_*_fracture_ball.png`
- `stage_*_contact_distribution.png`
- `stage_*_contact_forcechain.png`
- `stage_*_contact_forcechain_filtered.png`
- `stage_*_fc.png`
- `probe_contact_*.png`
- `peak_ball_native.png`

## Collaboration with pfc-mcp

If `pfc-mcp` is available, this skill supplies the domain workflow while `pfc-mcp` supplies execution and documentation lookup. The recommended pattern is:

1. confirm version-specific syntax with the documentation route
2. run a minimal specimen-generation or loading snippet
3. save staged states and exported data
4. drive calibration and plotting from reproducible scripts, not ad hoc GUI steps
5. for automated campaigns, let a wrapper script call PFC serially and record each run in a standard table

## Local Contents

- `references/`: lifecycle routing, calibration, auto-calibration, DOE/surrogate modeling, contact models, ParaView export, post-processing, V&V, and advanced topics.
- `templates/scope.md`: reusable project-scope intake template.
- `templates/`: calibration campaign and project-case templates that use placeholders for local executables and case directories.
- Child skills under `skills/pfc-*`: specialist routes for basic modeling, CAD import, contact models, standard tests, FISH, dynamics, coupling, post-processing, vedo, AE/energy, and calibration.

