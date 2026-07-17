# CAD And Geometry Import Documentation Notes

These notes summarize PFC command documentation points checked through `pfc-mcp` for PFC 6.0. Treat them as usage guidance, not a replacement for the official manual.

## Core Commands Checked

### `geometry import`

- Imports geometric data from a file into a geometry set.
- PFC documentation reports support for DXF, Itasca geometry format, and STL.
- DXF import is a partial AutoCAD version 12 implementation.
- Imported DXF layer names and STL solid names can be mapped to group slot 1.
- STL import can merge coincident nodes/edges by default; the merge behavior can be controlled when import speed or topology matters.

Pattern:

```text
geometry set 'cad_surface'
geometry import 'model.dxf'
geometry list information
```

### `geometry generate`

- Generates simple geometry shapes in the current geometry set.
- Useful shapes include box, disk, sphere, cone, and cylinder.
- Use generated geometry as a transparent replacement for small CAD fixtures when possible.

### `geometry export`

- Exports geometry nodes, edges, and polygons.
- Supported output includes Itasca geometry, DXF, and STL depending on geometry type and keyword.
- STL export applies to polygons and not free nodes/edges.

### `wall import`

- Imports walls directly from supported geometry files or from geometry sets.
- A model domain must exist before wall import.
- All wall facets must fall within the model domain.
- Wall import stitches connected facets from geometry and requires a manifold, orientable surface.
- Imported walls can be named, grouped, assigned IDs, seeded, or imported with error-skipping depending on geometry quality.

Pattern:

```text
model domain extent -10 10 -10 10 -10 10
wall import filename 'container.stl' name 'container' group 'boundary'
```

### `wall generate`

- Generates simple PFC walls directly.
- Use this instead of CAD import when the boundary is simple enough: box, circle, plane, polygon, disk, cylinder, cone, sphere, etc.
- A model domain must exist before wall generation.

### `clump template`

- Creates/imports/exports clump templates.
- A clump template may be made from pebbles or from a surface description.
- Geometry-based clump templates support surface-based inertial calculations and Bubble Pack style pebble approximation.
- Use this route when CAD geometry describes particle shape rather than a boundary wall.

### `ball generate` vs `ball distribute`

- `ball generate` creates non-overlapping balls and stops at target number or placement-attempt limit.
- `ball distribute` creates balls with overlaps until a target porosity is achieved.
- CAD/geometry ranges can be used to constrain where generated or distributed particles are accepted.

### `rblock construct` / `rblock generate`

- Rigid blocks can be constructed from geometry or template data and generated through template-based packing.
- Use when shape fidelity and rigid-block behavior are needed instead of spheres or clumps.

## Authoring Guidance

- Prefer native `geometry import`, `wall import`, `clump template`, `rblock`, and `ball generate/distribute` workflows before relying on old helper executables.
- Define model domain before wall import/generation.
- Check geometry topology before converting it into walls: manifoldness, orientation, scale, duplicate vertices, and disconnected surfaces.
- Record the file contract for any external helper: input geometry, input parameters, output command file, output DXF/STL, and PFC handoff command.
- Preserve legacy executables under `scripts/apps/` as optional helpers; keep transparent `.dat`, `.dxf`, `.stl`, or text contracts under `scripts/canonical/` whenever possible.

## Minimal Native CAD Import Pattern

```text
model new
model domain extent -10 10 -10 10 -10 10
geometry set 'imported'
geometry import 'boundary.stl'
geometry list information
wall import from-geometry 'imported' name 'boundary' group 'boundary'
model clean
```

## Minimal Geometry-Range Pattern

```text
geometry import 'region.dxf'
ball distribute radius 0.05 0.10 porosity 0.35 range geometry-space 'region' inside
model clean
```

The exact range keyword should be verified for the target PFC version and geometry type before publishing a final template.
