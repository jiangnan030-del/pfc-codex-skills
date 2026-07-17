# Contact Models

Use this file when selecting the contact constitutive law for a PFC workflow.

## Quick selector

- `linear` — granular materials, compaction stages, frictional packing
- `linearcbond` — simple contact bond, limited moment transfer
- `linearpbond` — bonded geomaterials, cemented specimens, rock-like behavior
- `flatjoint` — stronger interlock, improved compressive response, useful when standard parallel bonds underpredict strength ratio or frictional resistance
- `rrlinear` — rolling resistance effects for non-spherical behavior or peak/residual strengthening in granular systems
- `hertz` — nonlinear elastic normal contact behavior

## Selection logic

1. Start with the simplest model that can reproduce the required observables.
2. Use `linearpbond` as the default bonded-material baseline unless the user has a strong reason otherwise.
3. Switch to `flatjoint` when the baseline bonded model cannot capture realistic compression, shear transfer, or observed failure texture.
4. Add rolling resistance only when particle rotation effects matter and the user wants a simpler alternative to non-spherical particles.
5. Confirm all keywords against the target PFC version before writing final command blocks.

## Reporting expectation

Any answer that recommends a contact model should also explain:

- why that model matches the target material
- which macro observables it is expected to control best
- what its main limitations are
