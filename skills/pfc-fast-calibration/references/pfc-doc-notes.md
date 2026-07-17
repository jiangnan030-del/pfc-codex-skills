# PFC Documentation Notes

These notes summarize PFC command families relevant to the fast-calibration workflow. They are based on prior PFC 6.0 documentation checks through `pfc-mcp` and should be verified against the installed version before production runs.

## Reproducibility And Staging

### `model random`

- Sets the random seed for stochastic specimen generation, weak-contact grouping, and Weibull damage.
- Use a fixed seed for orthogonal-design comparisons.
- Change the seed only for robustness studies.

### `model clean`

- Updates contacts and spatial data structures.
- Run after particle generation and before assigning contact groups or contact properties.
- Run again after major contact-model changes when validation queries depend on current contacts.

### `model calm`

- Removes velocities/rotations to quiet the model after generation or consolidation.
- Use before saving a staged calibration state.

### `model save` / `model restore`

- Use milestone states such as `ini`, `consolidation_state`, `consolidation_state222`, `tri-compress2`, and `tension`.
- Do not rely on a single long run for 27 orthogonal trials.

## Contact Assignment

### `contact cmat`

- Controls default contact model assignment for new contacts.
- Use `contact cmat apply` cautiously because it updates existing contacts according to the CMAT.

### `contact model`

- Installs `linearpbond` on selected ball-ball contacts.
- Use explicit ranges or groups to avoid changing wall/facet contacts unintentionally.

### `contact method`

- Applies model-specific methods such as `deform`, `pb_deformability`, or `bond`.
- Set methods after the contact model is installed.

### `contact property`

- Assigns properties to existing contacts.
- Use strong and weak contact groups as the primary selectors.

### `contact group`

- Labels contacts for strong/weak assignment.
- Keep group names stable across all 27 runs so scripts can audit counts.

## Pieces And Boundaries

### `ball attribute`

- Use for density, damping, velocity reset, displacement reset, and contact-force reset.
- Reset velocities/displacements before loading stages.

### `ball group`

- Use for specimen, top-grip, bottom-grip, and any audit groups.
- For calibration campaigns, group names should not depend on local file paths or GUI state.

### `wall generate` / `wall attribute`

- Used to build cylinder side walls and axial platens.
- Servo loading should be separated into reusable FISH functions.

## FISH And Histories

### `fish define`

- Used for servo stress computation, stopping criteria, weak-contact assignment, Weibull random variables, and metric extraction.
- Keep functions modular and remove callbacks when moving from one loading mode to another.

### `fish callback`

- Runs FISH functions at specified cycle points.
- Always remove obsolete callbacks before switching from compression/servo to tension/grip loading.

### `fish history` / `history`

- Record stress, strain, Poisson's ratio, volumetric strain, and computed diagnostics.
- Export histories to text files for Python metric extraction.

### `measure create` / `measure history`

- Creates measurement spheres/regions for stress or porosity diagnostics.
- Run `model clean` before relying on measure-derived quantities.

## Modular Files

### `program call`

- Use to separate generation, consolidation, parameter assignment, loading, and export stages.
- A typical orthogonal run should call a small list of stage files instead of one large file.

## Recommended Stage Order

```text
model restore 'ini'
program call 'servo_consolidation.dat'
program call 'improved_lpbm_assign.p3fis'
program call 'run_compression.dat'
program call 'run_tension.dat'
program call 'export_metrics.dat'
```

## Version Caveats

- PFC syntax differs across 6.0, 7.0, and later versions.
- Verify `pb_deformability`, `pb_fa`, `pb_mcf`, `contact.prop`, `history export`, and `fish callback` syntax with `pfc-mcp` for the installed version.
- Treat bundled scripts as templates, not guaranteed drop-in production files.
