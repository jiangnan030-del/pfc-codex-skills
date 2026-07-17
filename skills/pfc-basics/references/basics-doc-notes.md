# PFC Basics Documentation Notes

These notes summarize PFC 6.0 command documentation checked through `pfc-mcp` for the foundation modeling workflow. Treat them as quick guidance, not a replacement for the official manual.

## Core Model Lifecycle

### `model new`

- Clears the current model state and starts a new model.
- Use `force` when intentionally discarding unsaved model state.
- Start every reusable template with an explicit `model new` unless it is designed to continue from a restore point.

Pattern:

```text
model new
```

### `model domain`

- Defines the active model domain and its extents.
- A domain is required before creating or importing many model objects, especially walls.
- Domain conditions can include behaviors such as stop, destroy, reflect, or periodic boundary behavior depending on the target workflow.
- Choose extents that comfortably contain generated particles, walls, clumps, and rblocks.

Pattern:

```text
model domain extent -10 10 -10 10 -10 10
```

### `model cycle` / `model step`

- Advances the model by a requested number of cycles/timesteps.
- `model cycle` accepts a `calm` interval keyword in the PFC 6.0 documentation.
- Use short cycle blocks during construction or sanity checks before long solves.

Pattern:

```text
model cycle 1000 calm 100
```

### `model solve`

- Runs the model until one or more solve criteria are satisfied.
- Prefer explicit solve criteria for public templates rather than open-ended cycling.
- Route calibration or servo-specific solve design to `pfc-servo-calibration` when stress/force control is central.

### `model calm`

- Calms the system by reducing velocities during model preparation or equilibration.
- Useful after particle generation/distribution and before a controlled solve stage.

### `model save` / `model restore`

- `model save` writes the model state to a file.
- `model restore` loads a saved model state.
- Keep `.sav` files as generated outputs, not canonical skill assets, unless explicitly required and redistributable.

## Basic Object Creation

### Balls

Checked commands:

- `ball create`
- `ball generate`
- `ball distribute`
- `ball attribute`
- `ball property`
- `ball group`

Guidance:

- Use `ball create` for deterministic single particles or precise coordinates.
- Use `ball generate` for non-overlapping generation within a box/range and count/attempt constraints.
- Use `ball distribute` when target porosity and initial overlaps are acceptable.
- Use `ball attribute` for physical state such as density/damping/velocity where applicable.
- Use `ball property` for contact-model-facing properties such as friction or stiffness, depending on the active contact model.
- Use `ball group` and named ranges to preserve stage and material provenance.

### Walls

Checked commands:

- `wall generate`
- `wall import`
- `wall attribute`
- `wall property`

Guidance:

- Use `wall generate` for simple containers and loading platens.
- Use `wall import` for CAD/STL/DXF-derived surfaces; route detailed import work to `pfc-cad-import`.
- Define the model domain before wall generation/import.
- Check wall names, groups, extents, and facet count before cycling.

### Clumps

Checked commands:

- `clump template`
- `clump generate`
- `clump distribute`

Guidance:

- Use `clump template` for shape definition before clump generation/distribution.
- Use clumps when non-spherical particle shape matters but fully rigid blocks are not required.
- Route detailed geometry-derived clump template work to `pfc-cad-import`.

### Rigid Blocks

Checked commands:

- `rblock construct`
- `rblock generate`

Guidance:

- Use rblocks for rigid polyhedral/blocky particles.
- Confirm geometry, template, and contact assumptions before using rblocks in calibrated studies.
- Route contact-law details to `pfc-contact-models` if the block contact behavior is nontrivial.

## Contact Setup Interface

Checked commands:

- `contact cmat`
- `contact model`
- `contact property`
- `contact method`
- `contact group`

Guidance:

- In a basics template, only include minimal contact setup needed for runnable examples.
- Use CMAT/default contact assignment when defining expected future contacts.
- Use direct `contact model` / `contact property` only when modifying existing contacts.
- Route detailed contact-law selection, property inheritance, bonding, and method order to `pfc-contact-models`.

## Ranges And Groups

Checked commands and concepts:

- `model range create`
- position and coordinate filters
- ID filters
- group filters
- geometry-based filters
- logical operations such as and/or/not/union where supported

Guidance:

- Use groups for semantic identity: material, stage, boundary, specimen part, or source geometry.
- Use named ranges when a selection is reused across multiple commands.
- Keep range criteria explicit in templates so downstream users can audit what was selected.
- Route complex geometry-based range selection to `pfc-cad-import` when CAD/geometry surfaces drive the selection.

## Minimal Foundation Template

```text
model new
model domain extent -5 5 -5 5 -5 5

; choose one object route
ball create radius 0.25 position 0 0 0
wall generate box -2 2 -2 2 -2 2

; minimal setup, then check and calm
model clean
model cycle 100 calm 10
model save 'basic-foundation'
```

## Skill Boundary Notes

- `pfc-basics` teaches the foundation objects and command order.
- `pfc-cad-import` owns CAD/DXF/STL geometry import and geometry-derived object creation.
- `pfc-contact-models` owns detailed contact-law setup and validation.
- `pfc-servo-calibration` owns controlled loading and calibration sequences.
- `pfc-standard-tests` owns laboratory-test templates built from the basic objects.
