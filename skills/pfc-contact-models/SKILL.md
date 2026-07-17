---
name: pfc-contact-models
description: Child skill of pfc-workflow for PFC 6.0 contact model selection, CMAT setup, contact properties, bonding methods, and contact-law audits.
---

# PFC Contact Models

Use this skill to choose, explain, adapt, or audit PFC contact-model setups. The skill is self-contained: PFC 6.0 linear and linear-parallel-bond examples are stored under `scripts/canonical/`, and documentation notes checked through `pfc-mcp` are stored under `references/contact-model-doc-notes.md`.

## Parent Skill Relationship

`pfc-contact-models` is a child skill of `pfc-workflow`. It does not own the full PFC lifecycle. Use it for contact-law selection, CMAT/property setup, bond activation, stiffness/strength property audits, and contact-model migration notes. Return to `pfc-workflow` for full case planning, solve orchestration, post-processing routing, verification, and delivery.

Parent/child split:

- Parent `pfc-workflow`: owns complete PFC project lifecycle and decides when contact-model support is needed.
- Child `pfc-contact-models`: owns contact laws, CMAT, contact properties, contact methods, bond setup, and contact-law validation checks.
- Sibling child `pfc-fish`: owns detailed FISH helper/callback implementation.
- Sibling child `pfc-servo-calibration`: owns servo control and manual macro-calibration sequencing.
- Sibling child `pfc-standard-tests`: owns standard laboratory-test templates.
- Sibling child `pfc-dynamics`: owns dynamic/seismic loading assumptions.
- Sibling child `pfc-fluid-coupling`: owns PFC CFD/seepage/buoyancy workflows.
- Sibling child `pfc-flac-coupling`: owns PFC-FLAC/FLAC3D coupling.
- Sibling child `pfc-postprocessing`: owns standard figures and field exports after solve.
- Sibling child `pfc-ae-energy`: owns AE, energy, and source-mechanism outputs after solve.

## When To Use

Use through `pfc-workflow` when a task needs contact-law reasoning:

- choose between `linear`, `linearpbond`, `linearcbond`, `hertz`, `flatjoint`, `smoothjoint`, `softbond`, `rrlinear`, or plugin contact laws
- set CMAT defaults before contact creation
- assign or modify properties on existing contacts
- activate bonds or set deformability through contact methods
- explain property inheritance from ball/wall/clump surfaces
- audit legacy contact-property blocks for PFC 6.0 compatibility
- connect micro-properties to macro-test calibration requirements

## Required Inputs

Ask for these if missing:

- PFC version and dimensionality.
- Material behavior: unbonded granular, cemented/rock-like, nonlinear elastic, jointed, rolling-resistance, or plugin-defined.
- Contact types involved: ball-ball, ball-facet, pebble-pebble, rblock, fracture, or mixed.
- Target macro behavior: stiffness, friction angle, tensile strength, cohesion, peak/residual behavior, dilation, or damage pattern.
- Whether contacts already exist or CMAT will be set before `model clean`.
- Calibration/validation test: UCS, Brazilian, biaxial, triaxial, direct shear, contact-level two-ball test, or custom.

## Documentation-Backed Rules

The following PFC 6.0 documentation points were checked through `pfc-mcp` and are expanded in `references/contact-model-doc-notes.md`:

- `contact cmat default` defines default Contact Model Assignment Table behavior for future contacts.
- `contact model` changes existing contacts and replaces prior contact-model state.
- `contact property` changes properties on existing contacts that recognize the property.
- `contact method` executes model-specific operations such as `bond`, `deformability`, or `pb_deformability`.
- `contact cmat apply` applies CMAT to existing contacts and reassigns contact models.
- `contact list` is used to verify contact model, force, energy, and contact state.
- `ball property` and `wall property` assign surface properties used by contact models; they are distinct from attributes.
- `model clean` creates contacts and initializes contact state after pieces/geometry are created.

## Canonical Template Map

| Topic | Folder | Files | Purpose |
| --- | --- | --- | --- |
| Linear model PFC 6.0 | `scripts/canonical/linear-model-pfc6/` | `1faxiang.dat`, `2qiexiang.dat` | Two-ball normal/shear loading demonstration for the linear contact model. |
| Linear parallel bond PFC 6.0 | `scripts/canonical/linearpbond-model-pfc6/` | `1faxiang.dat`, `2qiexiang.dat`, `3qiexiang_2.dat` | Two-ball normal/shear and bond stress/strength demonstrations for `linearpbond`. |

## Contact-Model Checklist

Use this checklist before writing or changing contact logic:

1. Select the contact law according to material behavior, not just available properties.
2. Define CMAT rules before creating/cleaning contacts whenever possible.
3. Run `model clean` after piece creation and before assuming contacts exist.
4. Use `contact method bond` only after compatible contacts exist.
5. Use `contact property` only when intentionally changing existing contacts.
6. Document whether properties are contact-level, ball/wall surface-level, inherited, or method-derived.
7. Add histories or contact listings that verify force, displacement, bond stress, failure, or energy response.
8. Route macro calibration back through `pfc-workflow` and, when needed, `pfc-servo-calibration` or `pfc-standard-tests`.

## Working Rules

- Prefer PFC 6.0-safe syntax unless the user explicitly targets another version.
- Treat files in `scripts/canonical/` as reference templates, not final calibrated models.
- Do not publish generated `.sav`, project metadata, videos, PDFs, archives, or large output dumps as authoritative assets.
- Do not claim macro mechanical behavior from micro-properties without calibration or validation.
- If the task becomes a full calibration or validation study, hand control back to `pfc-workflow`.

## Output Contract

A complete child-skill handoff back to `pfc-workflow` should include:

- Selected contact law and why it fits.
- Required files or snippets from `scripts/canonical/<case>/`.
- CMAT/property/method command order.
- Existing-contact vs future-contact assumptions.
- Required histories/list checks for validation.
- Macro-calibration caveats and target tests.
- A clear note that full case execution, post-processing routing, V&V, and delivery continue in `pfc-workflow`.

## Local Contents

- `references/overview.md`: detailed self-contained contact-model boundaries and source map.
- `references/contact-model-doc-notes.md`: PFC 6.0 command/reference notes checked through `pfc-mcp`.
- `examples/README.md`: how to validate bundled contact-model demonstrations.
- `scripts/canonical/`: PFC contact-model source snippets.
- `scripts/canonical/manifest.json`: file inventory with sizes and SHA-256 hashes.
- `scripts/README.md`: helper-script policy and future maintenance guidance.
