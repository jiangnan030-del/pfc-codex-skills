# Heterogeneous Contact Documentation Notes

These notes summarize PFC 6.0 documentation points checked through `pfc-mcp` for mineral-aware heterogeneous rock workflows. Treat them as quick guidance, not a replacement for the official manual.

## Reproducible Model Staging

### `model random`

- Sets the random-number seed used by PFC random functions.
- Use before random packing, mineral seeding, or Weibull damage assignment.
- Record the seed in the case metadata.

### `model clean`

- Creates contacts, initializes piece properties, and updates spatial data structures.
- Run after creating or changing particles and before assigning contact groups/properties that depend on the current contact network.
- Use `model clean all` only when a full remap is needed.

### `model save` / `model restore`

- Save staged states after packing, mineral grouping, bonding, damage assignment, and loading milestones.
- `model save` preserves FISH variables and histories in the saved state.

## Grouping

### `ball group`

- Assigns group names to balls, optionally scoped by ranges.
- Use ball groups for mineral phases such as `mineral_feldspar`, `mineral_quartz`, and `mineral_mica`.
- Use group slots when one object needs multiple independent classifications.

### `contact group`

- Assigns group names to contacts, optionally scoped by ranges.
- Use contact groups for mineral-pair or interface contact classes such as `pbond_feldspar`, `pbond_quartz`, `pbond_mica`, and `pbond_boundary`.
- Contact groups are the key selector for per-mineral `contact property` and `contact method` operations.

### `ball list` / `contact list`

- Useful for debugging and auditing object/group state.
- Avoid manual list output as the only validation; write summary tables from FISH or Python when possible.

## Contact Model And Properties

### `contact cmat`

- Controls default assignment rules for future contacts.
- Use when constructing reusable contact assignment tables or when new contacts are created after setup.
- Use `contact cmat apply` cautiously because it can replace existing contact model state.

### `contact model`

- Assigns or replaces the contact model on existing contacts.
- Mineral rock workflows usually use `linearpbond` for ball-ball contacts after the assembly is ready.

### `contact method`

- Applies model-specific methods, such as `deform`, `pb_deform`, and `bond` for LPBM workflows.
- Use after the correct contact model is installed.

### `contact property`

- Updates properties on existing contacts.
- Use it after contact grouping to assign per-mineral bond strengths, friction, radius multiplier, and other properties.

## FISH And Diagnostics

### `fish define`

- Defines FISH functions for mineral cluster growth, contact-group assignment, Weibull random multipliers, and diagnostics.
- Keep functions modular: phase assignment, contact assignment, property damage, and reporting should be separate.

### `fish history`

- Records FISH diagnostics over time.
- Use for mineral/contact counts, damage statistics, or custom stress-strain quantities when needed.

### `measure history`

- Records measurement-region quantities such as porosity, coordination, stress, strain rate, and position.
- Use to validate that heterogeneous assignment does not create unphysical local states.

## Geometry And Image Support

### `geometry import`

- Imports external geometry files into geometry sets.
- Use this route only when mineral phase boundaries are represented as geometry. If the source is a raster image, segment it in Python first and convert to phase labels or geometry as needed.

### `geometry assign-groups`

- Assigns groups to geometry elements based on geometric sets and projections.
- Can support phase-map workflows when mineral regions have been converted into geometry.

## Modular Command Files

### `program call`

- Processes another data file from the current command flow.
- Use for modular construction stages such as:

```text
program call 'mineral_cluster_assignment.p2fis'
program call 'mineral_lpbm_parameters.dat'
program call 'weibull_damage.p2fis'
```

## Recommended Command Order

```text
model restore 'packed_or_isoloose'
model random 10001
model clean
program call 'mineral_cluster_assignment.p2fis'
model clean
program call 'mineral_lpbm_parameters.dat'
program call 'weibull_damage.p2fis'
model calm
model save 'mineral_bonded'
```

Verify syntax against the installed PFC version before using the snippets as production code.
