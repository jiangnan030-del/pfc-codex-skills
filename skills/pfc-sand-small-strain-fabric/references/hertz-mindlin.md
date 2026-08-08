# Hertz-Mindlin setup and calibration cautions

## Reference starting values

| Parameter | Value |
|---|---:|
| Grain shear modulus | 18 GPa |
| Grain Poisson ratio | 0.15 |
| Density | 2650 kg/m3 |
| Grain friction | 0.5 |
| Wall friction | 0.0 |
| Local damping | 0.7 |

Use the Hertz-Mindlin model for the non-spherical quartz-sand clumps. Exact command/property names differ across PFC releases; verify them with target-version documentation.

## Calibration order

1. Match PSD, specimen geometry, void ratio and initial pressure.
2. Check compression response, contact count and coordination.
3. Match the low-strain modulus level using contact elasticity.
4. Check friction and shape against monotonic response if required.
5. Only then compare fabric/direction cases.

## Cyclic cautions

- `local damping=0.7` is useful during preparation but may alter a small hysteresis loop. Run a damping sensitivity study.
- A nominal 5 Hz input is acceptable only if inertial/energy checks confirm quasi-static behavior for the numerical scale.
- Zero volume and constant pressure can become incompatible controls if applied to the same degrees of freedom. Define independent controlled variables.
- If pressure or grading is absent from the source table, keep it configurable rather than guessing.
- Compare half-amplitude with half-amplitude, or peak-to-peak with peak-to-peak.
