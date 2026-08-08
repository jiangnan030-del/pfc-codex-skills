# Measured-trend quick reference (result verification)

Use these as acceptance checks on a new freeze-thaw run. `sigma_0` is the pre-freeze UCS; cases are
`sigma_1 = 0, 0.2 sigma_0, 0.4 sigma_0, 0.6 sigma_0`.

## Deformation

- **No axial stress**: axial and radial strain increase with cycles and then stabilize with fluctuation
  after roughly 10 cycles. Radial strain exceeds axial strain (the axial dimension is larger and more
  constrained). Their difference grows, then shrinks, and oscillates around 100e-6 after 30 cycles.
- **With axial stress**: radial strain grows with cycles and accelerates nonlinearly beyond 30 cycles.
  Axial strain is negative and decreases with cycles, indicating accumulating damage and loss of
  deformation resistance. Volumetric strain keeps increasing.
- **Failure**: at 0.6 sigma_0 the specimen fails and loses bearing capacity at about 45 cycles.

## Cracking versus temperature

Within one cycle, crack count increases rapidly while cooling, then flattens below about -25 C, matching
`w_u -> 0` from the unfrozen-water equation.

## Spatial distribution (radial banding)

Crack density near the surface is clearly higher than in the interior, because the interior is
constrained in three directions while the surface is nearly free.

Reference values for 0.6 sigma_0:

| Band from axis | Crack density (cracks/m3) |
| --- | --- |
| 0-20 mm | 0.90e7 to 1.17e7 |
| 20-25 mm (edge) | 2.45e7 |

## Directionality (dip angle to specimen axis)

- Low angles (0-20 deg) dominate; 80-90 deg is rare.
- Increasing axial stress increases the low-angle share and decreases the high-angle share:

| Bin | sigma_1 = 0 | sigma_1 = 0.6 sigma_0 | Change |
| --- | --- | --- | --- |
| 0-5 deg | 10.86% | 15.01% | +38.21% |
| 85-90 deg | 0.52% | 0.24% | -85.85% |

Interpretation: axial compression suppresses crack initiation and propagation in the radial direction.

## Failure mechanism (tensile / shear)

- Freeze-thaw damage is tension-dominated: the tensile crack fraction exceeds 50% in every case
  (consistent with Winkler-type frost-heave experiments).
- As sigma_1 goes from 0 to 0.6 sigma_0, the tensile fraction drops from 68.76% to 58.97%, i.e. axial
  compression induces additional shear cracking.

## Source

Method and data distilled from a study on deformation and damage of sandstone under coupled stress and
freeze-thaw action (Zhu Tantan et al., 2023). Treat the numbers as a reference case, not as universal
values; re-calibrate for any other rock.
