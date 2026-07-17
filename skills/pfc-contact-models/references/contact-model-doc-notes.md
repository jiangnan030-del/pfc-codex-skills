# Contact Model Documentation Notes

These notes summarize PFC command and reference documentation points checked through `pfc-mcp` for PFC 6.0. Treat them as usage guidance, not a replacement for the official manual.

## Core Commands Checked

### `contact cmat default`

- Sets the default slot of the Contact Model Assignment Table (CMAT).
- Use it before contacts are created when you want future contacts to receive a model and properties automatically.
- Typical pattern for granular response:

```text
contact cmat default model linear property kn 1e7 ks 1e7 fric 0.5
```

- Typical pattern for bonded response:

```text
contact cmat default model linearpbond property kn 1e7 ks 1e7 fric 0.5 ...
  pb_kn 5e6 pb_ks 5e6 pb_ten 3.5e5 pb_coh 3.5e5 pb_fa 50
```

### `contact model`

- Assigns a contact model to existing contacts.
- Replaces the existing contact model entirely; information stored in the previous model is lost.
- Use with care after a model has already generated contacts.
- Built-in models checked in the command documentation include `linear`, `linearcbond`, `linearpbond`, `hertz`, `flatjoint`, `smoothjoint`, `rrlinear`, `burger`, `hysteretic`, and `null`.

### `contact property`

- Modifies properties on existing contacts whose current contact model recognizes the property.
- This is different from CMAT assignment: CMAT controls future contacts, while `contact property` changes existing contacts.
- Optional inheritance settings exist for inheritable properties.
- Examples from documentation include linear properties such as `kn`, `ks`, `fric` and linearpbond properties such as `pb_kn`, `pb_ks`, `pb_ten`, `pb_coh`, `pb_fa`, and `pb_rmul`.

### `contact method`

- Executes model-specific methods on existing contacts.
- Common methods include `deformability`, `pb_deformability`, and `bond` for supported models.
- Documentation examples include:

```text
contact method deformability emod 60e9 kratio 2.5
contact method bond gap 0.0 pb_deformability emod 60e9 kratio 2.5
```

Use methods when a contact model provides a higher-level way to compute stiffness or activate bonds.

### `contact cmat apply`

- Applies the CMAT to existing contacts.
- Reassigns contact models according to CMAT rules and loses previous contact-model information.
- Use only when you intentionally want to reinitialize existing contact models.

### `contact list`

- Lists contact information.
- Useful keywords include force, energy, energy-list, extra variables, and all/type/range filters.
- Use for debugging contact state and verifying model assignment.

### `ball property` / `wall property`

- Assign surface properties used by contact models.
- These are distinct from attributes like position, velocity, radius, or density.
- Property names depend on the active contact model.
- Use these when relying on property inheritance from pieces/facets into contacts.

### `model clean`

- Creates contacts, initializes piece properties, updates spatial data structures, and updates contact activity.
- Use after creating geometry/balls and before expecting contact-model assignment to exist.
- If contact model or property rules should apply during initial contact creation, define them before `model clean`.

## Contact Model References Checked

### `linear`

- Linear elastic-frictional contact model with optional viscous damping.
- General-purpose model with normal/shear stiffness and Coulomb friction.
- Good for unbonded granular behavior or simple stiffness/friction demonstrations.

### `linearpbond`

- Linear parallel bond model representing a finite cement-like bond between contacting pieces.
- Combines linear interface behavior with a parallel bond that can transmit forces and moments.
- Common for cemented particulate materials and rock-like bonded specimens.

### Other Reference Models

- `hertz`: nonlinear contact model based on Hertz/Mindlin-style behavior.
- `flatjoint`: bonded flat-joint model for rock-like grain contacts.
- `smoothjoint`: joint-oriented behavior for contacts aligned with discontinuities.
- `softbond`: bonded/unbonded systems with soft-bond behavior.

## Authoring Guidance

- Decide whether contacts are unbonded, bonded, nonlinear, jointed, or plugin-defined before writing CMAT rules.
- Set CMAT before contact creation whenever possible.
- Use `model clean` after creating pieces so contacts are actually generated.
- Use `contact method bond` only after supported bonded contacts exist.
- Use `contact property` for existing contacts and CMAT/property inheritance for future contacts.
- Record force, displacement, stress, bond stress, and damage histories that match the selected contact law.
- Do not claim macro stiffness/strength from a micro-property block without calibration.
