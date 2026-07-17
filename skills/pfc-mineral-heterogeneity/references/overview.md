# Overview

## Purpose

`pfc-mineral-heterogeneity` provides a reusable route for mineral-composition-aware heterogeneous rock modeling in PFC. It is a child skill of `pfc-workflow`; it supplies mineral phase extraction, random clustered mineral assignment, per-mineral LPBM contact parameters, interface rules, Weibull damage, and validation checks, then hands full workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- digital image or phase-fraction intake
- Otsu-style mineral segmentation concepts
- mineral area/volume fraction targets
- cellular-automata style random cluster construction
- ball group and contact group naming for mineral phases
- per-mineral LPBM parameter tables
- mineral interface assignment rules
- Weibull damage multipliers for bond strength/stiffness
- heterogeneous rock validation checklists

This skill does not own:

- full PFC case orchestration
- generic contact-law theory beyond the mineral LPBM route
- standard laboratory-test execution
- servo boundary implementation details
- non-AE post-processing or AE/source-mechanism analysis
- CAD/STL geometry import details except as optional phase-map support

## Source Method Summary

The source method targets granite-like rock where mineral phases are not homogenized. The route is:

```text
digital image -> grayscale/filter -> Otsu multi-threshold segmentation -> mineral fractions
-> random cellular mineral clusters -> ball/contact groups -> per-mineral LPBM parameters
-> Weibull damage multipliers -> UCS/BTS/triaxial validation
```

A source granite example used approximately:

```text
mica: 4.81%
quartz: 35.86%
feldspar: 59.32%
```

The key modeling premise is that the numerical specimen should match mineral content and broad distribution well enough for mechanical studies, but does not need pixel-perfect image reconstruction unless the user explicitly asks for a digital-rock replica.

## Documentation Enrichment

PFC 6.0 command documentation was queried through `pfc-mcp` while building this skill. The resulting notes are summarized in `references/heterogeneous-contact-doc-notes.md`.

Key checked command families:

- `model random`, `model clean`, `model save`, `model restore`
- `ball group`, `ball list`
- `contact group`, `contact list`
- `contact cmat`, `contact model`, `contact method`, `contact property`
- `fish define`, `fish history`
- `measure history`
- `geometry import`, `geometry assign-groups`
- `program call`

## Bundled Template Set

Reusable source-like templates are stored under `scripts/canonical/`:

- `mineral_cluster_assignment.p2fis`: FISH template for area-based mineral cluster assignment and contact grouping.
- `mineral_lpbm_parameters.dat`: command template for per-mineral LPBM parameter assignment.
- `weibull_damage.p2fis`: FISH template for Weibull random multipliers on bonded-contact properties.
- `otsu_phase_fraction.py`: Python helper template for image segmentation / phase fraction extraction.

Templates are intentionally generic. They should be copied into a case folder and parameterized through the parent workflow.

## Recommended Handoff

After this skill produces the heterogeneous specimen design, return to `pfc-workflow` with:

- target mineral fractions
- random seed and clustering rule
- ball/contact group names
- per-mineral parameter table
- interface rule
- Weibull parameters and affected contact properties
- validation targets
- recommended downstream child skills for contact models, servo calibration, standard tests, post-processing, or AE
