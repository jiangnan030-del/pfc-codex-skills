# Overview

## Purpose

`pfc-contact-models` provides reusable PFC contact-law selection and property-setup guidance. It is a child skill of `pfc-workflow`; it supplies targeted CMAT, contact property, contact method, and contact-model validation expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- selecting contact laws for intended material behavior
- CMAT setup and future-contact assignment rules
- existing-contact model/property changes
- bond activation and deformability methods
- ball/wall/clump surface properties and inheritance assumptions
- contact-level validation histories/listings
- migration/audit guidance for old contact snippets

This skill does not own:

- full case lifecycle orchestration
- full macro calibration campaigns
- servo-control strategy except contact-law implications
- detailed FISH callback implementation
- post-processing figure generation
- AE/energy/source-mechanism analysis

## Documentation Enrichment

PFC 6.0 command and reference documentation was queried through `pfc-mcp` while building this skill. The resulting command notes are summarized in `references/contact-model-doc-notes.md`.

Key checked commands/references:

- `contact cmat default`
- `contact model`
- `contact property`
- `contact method`
- `contact cmat apply`
- `contact list`
- `ball property`
- `wall property`
- `model clean`
- reference models: `linear`, `linearpbond`, `hertz`, `flatjoint`, `smoothjoint`, and `softbond`

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/linear-model-pfc6/`
- `scripts/canonical/linearpbond-model-pfc6/`

Included linear-model files:

- `1faxiang.dat`: two-ball normal loading with a `linear` contact model, fixed timestep, force/displacement histories, and saved normal-loading state.
- `2qiexiang.dat`: restores the normal-loading state, applies shear motion, and records normal/shear force plus friction-limit reference.

Included linearpbond files:

- `1faxiang.dat`: two-ball normal loading with `linearpbond`, bond activation, tensile/cohesive parameter setup, and force/displacement histories.
- `2qiexiang.dat`: direct shear-style bonded contact loading.
- `3qiexiang_2.dat`: restores the normal-loading state and derives bond normal/shear stress indicators from contact properties.

## Recommended Contact Setup Pattern

1. Select contact model and target contact types.
2. Define CMAT rules and properties before contact creation.
3. Create pieces and boundaries.
4. Run `model clean` so contacts are generated and initialized.
5. Apply model methods such as `bond` only after compatible contacts exist.
6. Add histories/listing checks for force, displacement, stress, energy, and failure state.
7. Solve the local/contact demonstration or pass the micro-property block back into a calibrated workflow.

## Contact Model Selection Notes

- `linear`: general unbonded elastic-frictional contact behavior.
- `linearpbond`: cemented/rock-like behavior with a finite parallel bond that can carry force and moment.
- `hertz`: nonlinear contact response for elastic sphere-style contacts.
- `flatjoint`: rock-like contact behavior with flat-joint mechanics.
- `smoothjoint`: joint/discontinuity-oriented contact behavior.
- `softbond`: bonded/unbonded soft-bond behavior.

## Inclusion Rules

- Keep minimal `.dat` files needed to understand contact-law demonstrations.
- Do not bundle generated save states, project metadata, videos, PDFs, archives, or large output dumps as authoritative assets.
- Preserve legacy guidance only when it adds contact-law coverage not already present in PFC 6.0 examples.
- Keep model/property/method order explicit.

## Handoff To pfc-workflow

After this skill provides a contact-law plan or snippets, return to `pfc-workflow` for:

- full case directory creation
- standard-test or servo-calibration routing if needed
- solve management
- post-processing route selection
- V&V and delivery
