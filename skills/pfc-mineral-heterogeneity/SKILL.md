---
name: pfc-mineral-heterogeneity
description: Child skill of pfc-workflow for mineral-composition-aware heterogeneous rock modeling in PFC: digital image segmentation, mineral clusters, per-mineral LPBM parameters, interface contacts, Weibull damage, and validation of multi-mineral specimens.
---

# PFC Mineral Heterogeneity

Use this skill to design, explain, or implement PFC workflows for heterogeneous multi-mineral rock such as granite. The core route is: digital image or mineral fraction input -> mineral cluster generation -> ball/contact grouping -> per-mineral LPBM parameter assignment -> Weibull damage distribution -> standard mechanical validation.

## Parent Skill Relationship

`pfc-mineral-heterogeneity` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for mineral-aware specimen construction and parameter assignment, then return to `pfc-workflow` for full case planning, calibration campaign control, solve management, post-processing, V&V, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns the full project lifecycle and decides when mineral heterogeneity is needed.
- Child `pfc-mineral-heterogeneity`: owns mineral fractions, image-derived phase maps, mineral clusters, per-mineral groups, per-mineral contact parameters, and damage heterogeneity.
- Sibling `pfc-basics`: owns clean foundation model, balls, walls, groups, and ranges.
- Sibling `pfc-cad-import`: owns CAD/DXF/STL/geometry import and geometry-derived ranges.
- Sibling `pfc-contact-models`: owns detailed contact-law selection, CMAT strategy, bond methods, and contact validation.
- Sibling `pfc-standard-tests`: owns UCS, Brazilian, biaxial, triaxial, shear, and bending test templates.
- Sibling `pfc-servo-calibration`: owns stress/force servo loading and calibration sequencing.
- Sibling `pfc-fish`: owns reusable FISH helper design and callback/history details.
- Sibling `pfc-postprocessing`: owns standard non-AE plots and field exports.
- Sibling `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs.

## When To Use

Use through `pfc-workflow` when the task asks to:

- model granite or other multi-mineral heterogeneous rock
- convert digital image segmentation into PFC mineral phases
- assign quartz, feldspar, mica, matrix, inclusion, or interface groups
- build random clustered mineral domains with target area fractions
- calibrate separate LPBM parameters for each mineral or interface
- reduce unrealistic compression/tension strength ratio from homogeneous BPM models
- study mineral fraction, mineral distribution, or Weibull damage effects
- compare heterogeneous and homogeneous rock models

## Required Inputs

Ask for these if missing:

- PFC2D or PFC3D target and PFC version.
- Mineral phases and target fractions, or the segmented image / phase map.
- Specimen dimensions, particle radius distribution, and units.
- Contact model route: usually LPBM / `linearpbond` for bonded rock.
- Macro calibration targets: elastic modulus, Poisson's ratio, UCS, BTS/UTS, and failure pattern when available.
- Per-mineral starting values or relative ratios for stiffness and strength.
- Interface rule: matrix-dominant, weaker-boundary, mica-priority, area-ratio random assignment, or explicit phase-pair table.
- Weibull damage parameters if damage heterogeneity is required.

## Documentation-Backed Rules

PFC 6.0 documentation points checked through `pfc-mcp` are summarized in `references/heterogeneous-contact-doc-notes.md`.

Relevant command families:

- `model random`, `model clean`, `model save`, `model restore`: reproducible staged construction.
- `ball group`, `contact group`: mineral and interface phase assignment.
- `contact cmat`, `contact model`, `contact method`, `contact property`: LPBM assignment and per-group parameter changes.
- `ball list`, `contact list`: FISH traversal and auditing.
- `fish define`, `fish history`: cluster construction, Weibull random variables, and diagnostics.
- `measure history`: stress/strain/porosity/coordination checks.
- `geometry import`, `geometry assign-groups`: optional image/geometry-assisted phase assignment.
- `program call`: modular construction, assignment, loading, and export stages.

## Default Workflow

When the request is about formulas, exact theory, complete code, or source-command migration, load these first:

- `references/formulas.md` for Otsu, mineral fractions, LPBM, calibration-fit, strength-ratio, and Weibull formulas.
- `references/source-code-complete-pfc6.md` for the full A-G command-flow route and PFC 6.0-oriented skeleton.

### 1. Mineral Fraction Source

Choose one source route:

- segmented image or phase map
- Otsu multi-threshold grayscale segmentation
- user-provided mineral fractions
- synthetic phase fractions for sensitivity studies

For the source example, granite phases are mica, quartz, and feldspar with approximate fractions:

```text
mica: 4.81%
quartz: 35.86%
feldspar: 59.32%
```

### 2. Mineral Cluster Construction

For PFC2D, start with all balls assigned to the matrix phase, then seed filling phases and grow them across contact-connected neighbor balls until target area fractions are reached.

Recommended rules:

- use ball area `pi * radius^2` for 2D phase fractions
- use ball volume for 3D phase fractions
- fix `model random` before clustering
- write phase fraction diagnostics after grouping
- save a staged model after mineral groups are assigned

### 3. Contact Group Assignment

Assign contact groups from endpoint ball groups:

- same phase -> same mineral contact group
- different phases -> interface group or phase-pair group
- weak minerals or mica-rich contacts can be assigned preferentially to the weaker phase when following the source workflow

Example group names:

```text
mineral_quartz
mineral_feldspar
mineral_mica
pbond_quartz
pbond_feldspar
pbond_mica
pbond_boundary
```

### 4. Per-Mineral LPBM Parameters

Use `linearpbond` for ball-ball contacts unless the user requests another contact model. Assign stiffness and strength by contact group after contacts and groups exist.

Source example final values:

| Mineral | Linear emod (GPa) | PB emod (GPa) | kratio | pb_ten (MPa) | pb_coh (MPa) |
| --- | ---: | ---: | ---: | ---: | ---: |
| mica | 1.9 | 6.8 | 2.7 | 49.6 | 49.6 |
| quartz | 7.5 | 28 | 2.7 | 66.2 | 66.2 |
| feldspar | 9.6 | 32 | 2.7 | 332.5 | 332.5 |

Treat these as starting values, not universal parameters.

### 5. Weibull Damage

Apply damage as random multipliers on bond strength and optionally bond stiffness:

```text
x = alpha * (-ln(1 - R))^(1 / beta)
```

where `R` is uniform random in `[0, 1)`, `alpha` controls scale, and `beta` controls dispersion. Larger `beta` gives a more concentrated distribution.

### 6. Validation

Validate against macro targets before production studies:

- elastic modulus
- Poisson's ratio
- UCS
- BTS or UTS
- compression/tension strength ratio
- crack pattern and mineral-localization behavior
- phase fraction and contact-group diagnostics

## Working Rules

- Prefer transparent PFC 6.0 commands and FISH templates over black-box preprocessing.
- Keep image segmentation, cluster generation, contact assignment, parameter assignment, and mechanical loading as separate stages.
- Treat source values as calibration seeds, not final rock constants.
- Fix random seeds and save staged states after phase assignment, bonding, damage, and loading.
- Do not claim pixel-perfect digital-rock reconstruction when using random cellular clusters.
- Route detailed contact-law design to `pfc-contact-models` and standard test execution to `pfc-standard-tests` / `pfc-workflow`.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- mineral phases and target fractions
- image segmentation or synthetic fraction route
- cluster construction rule and random seed
- ball group names and contact group names
- phase/contact parameter table
- interface assignment rule
- Weibull damage parameters and affected properties
- staged save points
- validation targets and required plots/tables
- routing notes for contact models, standard tests, servo calibration, post-processing, and AE if needed

## Local Contents

- `references/formulas.md`: Otsu, LPBM, calibration-fit, strength-ratio, and Weibull formulas.
- `references/source-code-complete-pfc6.md`: full A-G command-flow route and PFC 6.0-oriented code skeleton.
- `references/overview.md`: boundary, workflow, and inclusion rules.
- `references/mineral-image-workflow.md`: Otsu segmentation and cellular-automata cluster route.
- `references/parameter-assignment.md`: per-mineral calibration, interface rules, and Weibull damage.
- `references/heterogeneous-contact-doc-notes.md`: PFC 6.0 command notes checked through `pfc-mcp`.
- `examples/README.md`: validation examples and materialization guidance.
- `scripts/canonical/`: reusable PFC/FISH and Python template snippets.
- `scripts/README.md`: script policy and future helper guidance.
