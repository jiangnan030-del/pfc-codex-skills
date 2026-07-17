# Calibration Plate

This reference preserves the source document's laboratory and numerical validation details for AE source localization.

## Granite Plate Laboratory Test

Specimen:

```text
plate size = 600 x 600 x 18 mm
effective location area = 500 x 500 mm
source points = 4
repeats per source = 6 pencil-lead breaks
```

Acquisition:

```text
12-channel Richter acquisition
10 MHz sampling
Nano30 sensors
50 dB preamplifier gain
couplant = silicone grease
pencil lead = 0.5 mm HB
lead extension = 2.5 mm
angle to plate = 30 deg
```

Sensor cluster layouts:

| Layout | Geometry | Characteristic spacing | Better-point ratio |
| --- | --- | ---: | ---: |
| I | isosceles right triangle | 30 mm legs | 82.6% |
| II | general right triangle | 20 mm shortest leg, 60 deg to hypotenuse | 84.0% |
| III | equilateral triangle | 30 mm side | 71.0% |

A “better point” has source-location error below 20%.

## Numerical Flat-Joint Plate Validation

Flat-joint plate:

```text
plate size = 500 x 500 x 18 mm
particle count = 101764
d_min = 3 mm
d_max = 4.5 mm
rho = 2800 kg/m3
Ec = 80 GPa
kn/ks = 1.8
```

Bond/contact parameters:

```text
Nr = 1
Na = 3
Ebar_c = 80 GPa
sigma_c_bar = 15 MPa
c_bar = 200 MPa
kbar_n/kbar_s = 1.8
mu = 0.4
```

Mechanical calibration:

| Property | Lab | Simulation | Error |
| --- | ---: | ---: | ---: |
| UCS (MPa) | 187.15 | 190.0 | 1.52% |
| tensile strength (MPa) | 10.6 | 10.5 | 0.94% |
| E (GPa) | 64.8 | 64.1 | 1.08% |
| nu | 0.21 | 0.20 | 4.76% |

Numerical source:

```text
source direction = z force on source particle
frequency = 100 kHz
amplitude = 1.0e-8 N
timestep = 5.0e-8 s
source types = sine and Ricker
```

Numerical location quality:

| Source type | Layout I | Layout II | Layout III |
| --- | ---: | ---: | ---: |
| sine | 100% | 100% | 87.5% |
| Ricker | 100% | 95.8% | 95.8% |

## Interpretation Notes

- Numerical location accuracy is usually higher than laboratory accuracy because the numerical model has fewer unknown defects and coupling issues.
- In a 3D plate, 2D localization ignores out-of-plane particle coordinate differences; this introduces unavoidable timing error.
- If a source lies close to a line connecting two clusters, the pairwise location can become unstable.
- Layout II performed best in the laboratory set, while I/II/III all performed well numerically for the tested model.
