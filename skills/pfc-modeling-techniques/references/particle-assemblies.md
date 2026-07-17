# Particle Assemblies

Use this reference for representation choice and assembly design. Full code
lives in:

- `source-code-particle-assemblies-pfc6.md`

## 1. Representation choices

| Representation | Best use | Main tradeoff |
| --- | --- | --- |
| `ball` | fast baseline for soils and many BPM rock models | limited shape realism |
| `clump` | irregular grains, interlock-sensitive media | higher cost than balls |
| `rblock` | angular blocks, fragments, blocky rock | more geometry and contact sensitivity |
| Voronoi / zone-to-rblock | polycrystal or grain-based heterogeneity | preprocessing-heavy |

## 2. Design logic

Choose the simplest representation that still preserves the physics you need:

- use `ball` when grading, porosity, and macro response matter more than shape
- use `clump` when non-sphericity drives response
- use `rblock` when corners, facets, or block kinematics matter
- use Voronoi / zone-derived routes when internal tessellation is the main goal

## 3. Packing quality checks

Before bonding or production loading, check:

- porosity is close to target
- floating particles are limited
- overlaps are not pathological
- coordination is not unrealistically low
- wall-adjacent zones are not abnormally loose

## 4. Template-based construction

For shape libraries, a common route is:

1. import geometry
2. create clump or rblock templates
3. distribute by size bins and volume fraction
4. equilibrate packing
5. then assign final contact laws

## 5. Geometry regrouping logic

When geometry is used as an intermediate:

1. generate coarse seeds or imported shapes
2. export each region as geometry
3. refill domain with smaller particles
4. classify particles and contacts by geometry-space membership
5. mark inter-region contacts as boundaries

This route is useful for polycrystal, grain-cluster, and material-zoning
problems.

## 6. Zone-to-rblock logic

Converting zones to rblocks is helpful when:

- a continuum mesh already exists
- null / excavated / selected groups should become discrete blocks
- angular block shapes should inherit mesh topology

The key geometric task is turning each zone face into valid polygons while
rejecting degenerate zero-area facets.

## 7. State consistency rule

Calibration and engineering models should remain consistent in:

- particle size range or grading philosophy
- initial packing density or confining state
- specimen scale if size effect is not explicitly corrected
- contact-model family and assignment logic

If any of these changes, old microparameters may no longer transfer.
