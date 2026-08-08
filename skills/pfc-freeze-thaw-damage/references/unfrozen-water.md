# Governing equations: unfrozen water, particle volume, temperature schedule

## Eqs. (1)-(2) Pore-water particle volume versus temperature

The volume change of liquid water with temperature is neglected.

```
dV = V0 * (rho_w / rho_i)

V  = V0 + (1 - w_u) * dV     (T <= 0 C)
V  = V0                      (T >  0 C)
```

- `V0`: initial (unfrozen) volume of the pore-water particle.
- `rho_w / rho_i` is about 1.09.
- `w_u`: unfrozen water content (mass fraction of liquid water in the total pore water).

### Consistency check on the volume increment (important)

Taken literally, `dV = 1.09 * V0` doubles the volume when fully frozen, which contradicts the physical
fact that water expands about 9% on freezing. For implementation, prefer the **incremental** form:

```
dV = V0 * (rho_w / rho_i - 1)   # about 0.09 * V0
```

Then back-check the chosen convention against the measured frost-heave strains of the stress-free case
(radial strain greater than axial strain, stabilizing after roughly 10 cycles). Record which convention
was used in the run log, because all crack counts scale with it.

Radius update for a spherical pore-water particle:

```
r_target = r0 * (V_target / V0) ** (1.0 / 3.0)
```

## Eq. (3) Unfrozen water content

```
w_u = 1 - [1 + 0.139 * (-1/T)**(1/3) * ln((1 + exp(0.268*T)) / 2)] * (1 - exp(0.268*T))   (T <= 0)
w_u = 1                                                                                   (T >  0)
```

`T` in degrees Celsius. Near T = -25 C, `w_u` is already close to zero: cooling further barely changes
pore-water particle volume and produces few new cracks. This is the basis for taking **-30 C as the
minimum temperature**.

Guard the singularity at `T = 0` in code (use the `T > 0` branch or a small negative epsilon).

## Eq. (4) Temperature schedule

```
T = -30 * |sin(pi / 60 * t)|      # t in minutes, period 60 min, range 0 to -30 C
```

In the model, particle temperature is assigned uniformly, so no hold time is needed for complete
freezing or thawing, and the `T > 0 C` segment need not be simulated. One freeze-thaw cycle equals one
sweep of the schedule with enough temperature substeps that each volume update stays quasi-static.

## Eqs. (5)-(6) Radial crack-density banding

```
rho_c = N / V
V     = pi * H * [(R + 5)**2 - R**2]      # mm, sampling interval 5 mm
```

- `N`: crack count inside the band.
- `H`: specimen height.
- `R`: inner radius of the band, stepping outward in 5 mm increments.

Convert to cracks/m3 for reporting (the reference case reports values of order 1e7 cracks/m3).
