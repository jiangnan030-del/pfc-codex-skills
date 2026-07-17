# Overview

## Purpose

`pfc-gbm-brittle-rock` packages a PFC2D grain-based brittle-rock case with mineral groups, smooth-joint grain boundaries, a prefabricated crack, biaxial compression, fracture tracking, and energy histories.

The migrated workflow is:

```text
coarse mineral-seeded pack -> Voronoi/rblock grain geometry -> mineral geometry sets
-> fine particle refill by mineral regions -> biaxial consolidation -> prefabricated crack
-> per-mineral LPBM + smooth-joint grain boundary -> biaxial loading and fracture monitoring
```

## Boundary

This skill owns:

- PFC2D GBM / equivalent crystal workflow from the source case
- mineral group transfer from coarse particles to geometry to fine particles
- prefabricated crack geometry and particle deletion route
- `linearpbond` mineral-body contacts plus `smoothjoint` grain-boundary contacts
- fracture callback, crack counts, and energy-history contract
- public-safe migration of `.dat` and `.p2fis` templates

This skill does not own:

- 3D FJM/FJM3D modeling
- generic standard BPM theory beyond GBM comparison
- servo theory in detail
- general mineral image segmentation
- complete AE moment tensor/source mechanism post-processing

## Relationship To Existing Skills

Use current repository skills as follows:

| Need | Skill |
| --- | --- |
| Full PFC case workflow | `pfc-workflow` |
| Standard BPM brittle-rock defects | `pfc-brittle-rock-bpm` |
| Equivalent crystal / GBM chapter narrative | `pfc-equivalent-crystal-model` |
| FJM/FJM3D brittle rock | `pfc-flat-joint-brittle-rock` |
| Mineral fractions or image-derived mineral groups | `pfc-mineral-heterogeneity` |
| `linearpbond` / `smoothjoint` contact design | `pfc-contact-models` |
| Biaxial servo | `pfc-servo-calibration` |
| FISH callbacks and fracture tracking | `pfc-fish` |
| AE/energy figures | `pfc-ae-energy` or `pfc-postprocessing` |

## Migrated Case Summary

The source case is a 2D GBM specimen with four mineral-like groups:

```text
shiying       quartz
xiechangshi   plagioclase / oblique feldspar style group
zhengchangshi orthoclase / positive feldspar style group
yunmu         mica
```

The case uses:

- initial coarse mineral-seeded particle pack
- Voronoi-like rblock construction from particle centers
- geometry export for each mineral group
- fine particle refill and assignment by geometry-distance ranges
- biaxial stress consolidation at about `-10 MPa`
- prefabricated crack with angle `45 deg`, length `12 mm`, aperture `2 mm`
- per-mineral LPBM contact parameters
- `smoothjoint` default grain-boundary contacts
- fracture callback by bond-break event
- histories for stress, strain, crack counts, crack mode, contact model source, energy terms, and AE-like crack increments

## Public Asset Policy

Bundled:

- `.dat` command templates
- `.p2fis` fracture tracking template
- `manifest.json`

Not bundled:

- `.sav` save states
- `.prj` / project metadata
- PDF explanation files
- generated plots or output dumps

## Recommended Validation

Minimum validation outputs:

- biaxial stress-strain curve
- axial/lateral/volumetric strain curves
- peak stress and post-peak drop
- crack count vs strain
- tension/shear crack counts
- `linearpbond` vs `smoothjoint` crack-source counts
- energy histories
- fracture plot at selected stages
