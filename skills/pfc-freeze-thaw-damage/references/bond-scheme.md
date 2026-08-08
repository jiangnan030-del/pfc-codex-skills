# Bond scheme: three contact families

The two-particle system creates three contact families, each with a distinct role.

| Family | Role | Allowed to break? |
| --- | --- | --- |
| rock-rock (mineral-mineral) | carries the mechanical load; its breakage **is** the damage measure | yes, registered as a crack |
| water-rock (pore water-mineral) | transmits frost-heave force from expanding ice to the skeleton | no |
| water-water (pore water-pore water) | keeps the pore-water cluster coherent while expanding | no |

## Reference parameter set (Sichuan yellow sandstone, 50 x 100 mm)

| Bond family | Tensile strength (MPa) | Modulus (GPa) | Cohesion (MPa) | Friction angle (deg) | kn/ks |
| --- | --- | --- | --- | --- | --- |
| Rock-rock | 3.10 | 1.5 | 4.5 | 40 | 1.5 |
| Water-rock | 100 | 0.56 | 100 | 0 | 1.5 |
| Water-water | 100 | 0.56 | 100 | 0 | 1.5 |

Particles:

- Mineral: density 2500 kg/m3, radius 0.8-1.0 mm.
- Pore water: density 920 kg/m3, radius 0.6-0.8 mm, randomly distributed in the pores.

## Assignment recipe

1. Generate mineral particles first, then insert pore-water particles into the pore space.
2. Put particles in groups, e.g. `rock` and `water`, so contacts can be filtered by group pair.
3. Install a bonded contact model on all contacts, then override properties by group pair:
   - `range contact type ball-ball group rock group rock` -> rock-rock parameters,
   - contacts touching a `water` particle -> the 100 MPa "unbreakable" parameter set.
4. Set the water bond friction angle to 0: these bonds should only transmit force, not add shear resistance.
5. Keep the low modulus (0.56 GPa) for water bonds so the expanding pore cluster does not artificially
   stiffen the specimen.
6. Save the bonded state (`ftc_bonded`) before calibration and before any freeze-thaw run.

## Calibration gate

Calibrate rock-rock parameters against the pre-freeze uniaxial test until UCS and E agree within a few
percent. Reference case: numerical 73.40 MPa / 8.72 GPa versus test 75.05 MPa / 9.02 GPa (2.2% / 3.3%).
Do not start freeze-thaw cycling before this gate passes: crack counts are only meaningful relative to a
calibrated skeleton.

## Crack bookkeeping

Only rock-rock bond breakages count as cracks. For each crack record:

- position (for radial banding, Eqs. 5-6),
- failure mode (tensile or shear, for the tensile-fraction statistic),
- normal orientation (for the dip angle relative to the specimen axis, 5 degree bins),
- cycle number and current temperature (for the crack-count/temperature curve).
