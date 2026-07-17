# PFC Documentation Notes

These notes summarize PFC command families relevant to the GBM brittle-rock workflow. They were checked with `pfc-mcp` search results for PFC 6.0-oriented command documentation. Verify exact syntax against the installed PFC version before production runs.

## Particle And Boundary Setup

### `ball distribute`

- Distributes balls with overlaps until a target porosity is achieved.
- The source uses bins and volume fractions for the coarse mineral-seeded pack, then a single radius range for fine refill.
- Fix `model random` before using it for reproducibility.

### `wall generate`

- Builds box boundaries for 2D biaxial compression.
- The source uses named vessel walls and stores wall pointers for servo and stress calculation.

### `wall import`

- Imports walls from geometry objects or supported external geometry files.
- The source uses it to convert the prefabricated crack polygon into a wall-like geometry before deleting particles inside the crack.

## Geometry And Rblocks

### `geometry set`

- Creates or selects a geometry set.
- The source uses `rock` for particle-center geometry and `liewen1` for the crack polygon.

### `geometry polygon create`

- Creates a polygon in the current geometry set from nodes, edges, or points.
- The prefabricated crack uses four computed corner points.

### `rblock construct`

- Constructs rblocks from existing geometry or template data.
- The source uses `rblock construct from-geometry ... voronoi` to create a grain network from particle-center nodes.

### `rblock export`

- Exports rblock boundaries to geometry sets.
- The source exports one geometry set per mineral group, then deletes rblocks and refills fine particles.

## Contact Models And CMAT

### `contact cmat`

- Defines Contact Model Assignment Table entries.
- The source uses per-mineral `contact cmat add` entries for same-mineral `linearpbond` contacts, then a default `smoothjoint` entry for ball-ball grain boundaries.
- Use `contact cmat list` to audit entries before `contact cmat apply`.

### `contact model`, `contact method`, `contact property`

- Use these after CMAT application to install, bond, or modify existing contacts.
- Verify property names such as `pb_deform`, `pb_coh`, `pb_ten`, `sj_kn`, and `sj_coh` for the target version.

### `smoothjoint`

- The source uses `smoothjoint` to represent grain-boundary interfaces.
- Local documentation search may not index model-specific details under the literal query; verify the contact model reference directly for installed-version property names.

## Fractures, Fragments, And FISH

### `fish callback`

- Adds/removes FISH functions at cycle points or events.
- The source registers `@add_crack` on the `bond_break` event.
- Remove stale callbacks when switching loading modes or reusing save states.

### `fracture create`

- Creates deterministic fractures.
- The source creates a fracture segment at each broken contact using calculated vertices.

### `fragment compute`

- Computes fragments based on contact connectivity.
- The source periodically calls `fragment compute` after crack accumulation thresholds.

### `history` / `fish history`

- Records scalar values such as stress, strain, crack counts, and energy quantities.
- Keep history IDs/names documented so post-processing scripts can map them correctly.

## Recommended Audit Order

Before loading:

```text
model clean
contact cmat list
contact list range contact type 'ball-ball'
fish list symbols
```

During loading:

```text
fish callback list
history list
fragment list
fracture list
```

After loading:

```text
history export
fracture export
fragment list
```
