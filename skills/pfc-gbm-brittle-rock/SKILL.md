---
name: pfc-gbm-brittle-rock
description: Child skill of pfc-workflow for PFC2D grain-based brittle-rock modeling: GBM/equivalent crystal networks, mineral-group assignment, smooth-joint grain boundaries, prefabricated cracks, biaxial compression, fracture/energy monitoring, and brittle-rock validation.
---

# PFC GBM Brittle Rock

Use this skill to design, explain, or implement PFC2D grain-based brittle-rock models (GBM / equivalent crystal model) from the bundled GBM + prefabricated-crack biaxial-compression case. The core route is: mineral-seeded particle pack -> Voronoi/rblock grain geometry -> mineral geometry export -> fine particle refill by mineral regions -> biaxial consolidation -> prefabricated crack cut -> per-mineral LPBM + smooth-joint grain-boundary assignment -> biaxial loading with fracture, AE-like, and energy histories.

## Parent Skill Relationship

`pfc-gbm-brittle-rock` is a child skill of `pfc-workflow`. It owns the GBM specimen-construction and brittle-rock mechanism portion, not the full project lifecycle.

Use these handoffs:

- Parent `pfc-workflow`: owns full planning, calibration campaign control, solve management, V&V, and delivery.
- Sibling `pfc-basics`: basic domain, ball, wall, geometry, group, and range setup.
- Sibling `pfc-cad-import`: geometry import/export, geometry ranges, wall import, and rblock/geometry conversion details.
- Sibling `pfc-mineral-heterogeneity`: image/mineral fraction intake, mineral phase logic, and per-mineral parameter assignment.
- Sibling `pfc-contact-models`: `linearpbond`, `smoothjoint`, CMAT ordering, bond methods, and contact-property audits.
- Sibling `pfc-servo-calibration`: biaxial confining pressure, wall-servo gains, and stress convergence.
- Sibling `pfc-fish`: fracture tracking, callbacks, histories, and reusable FISH refactoring.
- Sibling `pfc-ae-energy`: AE/energy/source-mechanism post-processing if fracture or energy histories are used as AE proxies.
- Sibling `pfc-postprocessing`: stress-strain, crack-count, energy, and field plots.

Relationship with existing brittle-rock family skills:

- `pfc-brittle-rock-bpm`: use for standard BPM limits and baseline brittle-rock theory.
- `pfc-equivalent-crystal-model`: use for chapter-level equivalent-crystal explanation and Hoek-Brown validation narrative.
- `pfc-flat-joint-brittle-rock`: use when the task is FJM/FJM3D rather than GBM/smooth-joint grain boundaries.

## When To Use

Use through `pfc-workflow` when the task asks to:

- build or explain a GBM / equivalent crystal model in PFC2D
- model brittle rock with mineral grains and grain-boundary interfaces
- convert mineral-seeded particles into Voronoi/rblock grain regions
- assign quartz, feldspar, and mica-style groups to a fine particle specimen
- use `smoothjoint` contacts to represent grain boundaries
- add a prefabricated slit/fracture before biaxial compression
- monitor tension/shear cracks by `linearpbond` and `smoothjoint` source
- compare GBM against standard BPM for brittle-rock compression/tension behavior

## Required Inputs

Ask for these if missing:

- PFC version and whether the target is PFC2D.
- Specimen width/height and particle radius range.
- Mineral groups and target proportions or the source case proportions.
- Prefabricated crack angle, length, and aperture.
- Biaxial confining stress and loading rate.
- Mineral contact parameters and smooth-joint grain-boundary parameters.
- Required outputs: stress-strain, crack counts, energy terms, AE-like event increments, fractures, or fields.

## Migrated Source Case

The bundled canonical case is `scripts/canonical/gbm-prefabricated-crack-biaxial/`.

Stages:

1. `stage_01_initial_particle_pack.dat`: coarse mineral-seeded particle pack.
2. `stage_02_voronoi_rblock_geometry.dat`: convert particle centers to Voronoi/rblock geometry.
3. `stage_03_export_mineral_geometry.dat`: assign rblocks back to mineral groups and export geometry sets.
4. `stage_04_refill_particles_by_mineral_geometry.dat`: fine particle refill and mineral group assignment by geometry.
5. `stage_05_biaxial_confining_servo.dat`: biaxial confining stress servo.
6. `stage_06_prefabricated_crack_cut.dat`: create slit geometry and delete balls inside it.
7. `stage_07_gbm_contact_assignment.dat`: assign per-mineral LPBM contacts and smooth-joint grain-boundary contacts.
8. `stage_08_trim_specimen.dat`: trim outer particles and save ready state.
9. `stage_09_biaxial_loading_monitoring.dat`: load in biaxial compression and record mechanics/fracture/energy histories.
10. `fracture_tracking.p2fis`: bond-break callback, fracture creation, and fragment updates.

Large/generated source files such as save states and project metadata are intentionally not bundled.

## Documentation-Backed Rules

PFC command families checked through `pfc-mcp` are summarized in `references/pfc-doc-notes.md`:

- `ball distribute`, `ball group`, `wall generate`, `wall import`
- `geometry set`, `geometry polygon create`, geometry range selection
- `rblock construct`, `rblock export`, `rblock delete`
- `contact cmat`, `contact model`, `contact method`, `contact property`
- `smoothjoint` as a version-sensitive contact model term
- `fracture create`, `fragment compute`, `fish callback event bond_break`
- `history`, `fish history`, `model energy mechanical on`

## Working Rules

- Do not use GBM as a 3D solution; this migrated case is PFC2D.
- Keep the coarse mineral-seed construction separate from fine particle refill.
- Keep mineral-body contacts (`linearpbond`) separate from grain-boundary contacts (`smoothjoint`).
- Treat the provided contact parameters as source-case seeds, not universal granite constants.
- Route detailed smooth-joint syntax and CMAT inheritance audits to `pfc-contact-models`.
- Route biaxial servo stability to `pfc-servo-calibration`.
- Route fracture callback refactoring to `pfc-fish`.

## Output Contract

A complete handoff back to `pfc-workflow` should include:

- GBM stage list and copied command files
- mineral group names and proportions
- grain-boundary model and smooth-joint parameters
- prefabricated crack angle, length, aperture, and geometry selection rule
- confining stress, loading velocity, and stop criterion
- fracture/energy/history output list
- validation plan against stress-strain, crack mode, crack path, and brittle-rock expectations

## Local Contents

- `references/overview.md`: scope, model boundary, and stage route.
- `references/formulas.md`: brittle-rock BPM, GBM, smooth-joint, biaxial, crack and energy formulas.
- `references/source-code-complete-pfc6.md`: full staged code migration notes.
- `references/pfc-doc-notes.md`: PFC documentation notes for GBM-related commands.
- `references/gbm-prefabricated-crack-case.md`: source case parameters and outputs.
- `examples/README.md`: materialization and validation guidance.
- `scripts/canonical/gbm-prefabricated-crack-biaxial/`: migrated public-safe `.dat` and `.p2fis` templates.
- `scripts/canonical/manifest.json`: script inventory.
