# Orthogonal Design And Calibration Tables

This reference preserves the orthogonal design and fast-calibration data needed to reproduce the source method.

## Factor Levels

The 13 micro-parameters are tested at 3 levels.

| Level | Ebar_star (GPa) | E_ratio | kbar_star | sigma_c_bar (MPa) | coh_ratio | mu | phi_bar (deg) | beta_bar_moment | Rf | beta_weibull | R_sigma | R_E | R_k |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 100 | 0.2 | 1 | 75 | 1 | 0.5 | 40 | 0.3 | 0.3 | 3 | 0.1 | 0.1 | 1 |
| 2 | 200 | 0.3 | 2 | 100 | 2 | 0.8 | 60 | 0.5 | 0.5 | 8 | 0.2 | 0.2 | 2 |
| 3 | 300 | 0.4 | 3 | 125 | 3 | 1.1 | 80 | 0.7 | 0.7 | 13 | 0.3 | 0.3 | 3 |

## 27-Run Orthogonal Design

The full design is stored as `scripts/canonical/orthogonal_design_13params.csv`.

Use it to generate one run directory per row. Each row should materialize:

```text
run_001/params.json
run_001/assign_improved_lpbm.p3fis
run_001/ucs.dat
run_001/uts.dat
run_001/triaxial.dat
```

## Macro Result Table From Source

The source reports 27 numerical trial outputs. These values are also embedded in `regression_fast_calibration.py` for reproduction checks.

| run | E_GPa | nu | UCS_MPa | UTS_MPa | phi_deg | c_MPa | sigma_cd_MPa | sigma_cd_over_UCS | UCS_over_UTS |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 15.910 | 0.071 | 49.270 | 11.340 | 52.840 | 8.280 | 25.760 | 0.523 | 4.345 |
| 2 | 15.210 | 0.070 | 65.500 | 11.630 | 64.150 | 7.510 | 49.360 | 0.754 | 5.632 |
| 3 | 13.840 | 0.114 | 48.420 | 5.920 | 56.000 | 7.400 | 33.870 | 0.700 | 8.179 |
| 4 | 14.300 | 0.120 | 65.370 | 15.160 | 61.870 | 8.190 | 43.370 | 0.663 | 4.312 |
| 5 | 12.020 | 0.160 | 42.040 | 5.540 | 52.990 | 7.120 | 24.930 | 0.593 | 7.588 |
| 6 | 15.100 | 0.080 | 118.780 | 11.670 | 66.370 | 12.420 | 39.610 | 0.333 | 10.178 |
| 7 | 11.990 | 0.200 | 54.360 | 9.790 | 45.720 | 11.060 | 28.670 | 0.527 | 5.553 |
| 8 | 14.930 | 0.110 | 165.330 | 24.450 | 62.840 | 19.970 | 39.920 | 0.241 | 6.762 |
| 9 | 13.860 | 0.150 | 84.820 | 8.050 | 64.360 | 9.650 | 41.490 | 0.489 | 10.537 |
| 10 | 17.420 | 0.100 | 44.100 | 2.510 | 64.030 | 5.080 | 24.000 | 0.544 | 17.570 |
| 11 | 17.360 | 0.070 | 74.470 | 10.870 | 57.890 | 11.070 | 37.610 | 0.505 | 6.851 |
| 12 | 18.730 | 0.090 | 101.810 | 27.790 | 54.220 | 16.430 | 34.130 | 0.335 | 3.664 |
| 13 | 14.410 | 0.160 | 19.400 | 1.560 | 55.860 | 2.980 | 13.090 | 0.675 | 12.436 |
| 14 | 19.030 | 0.080 | 53.470 | 12.070 | 60.100 | 7.140 | 25.050 | 0.468 | 4.430 |
| 15 | 18.680 | 0.070 | 84.840 | 9.210 | 61.530 | 10.760 | 37.290 | 0.440 | 9.212 |
| 16 | 21.380 | 0.030 | 39.810 | 4.880 | 63.240 | 4.730 | 27.120 | 0.681 | 8.158 |
| 17 | 19.720 | 0.050 | 134.700 | 21.010 | 65.970 | 14.330 | 36.580 | 0.272 | 6.411 |
| 18 | 17.690 | 0.100 | 41.520 | 4.030 | 55.030 | 6.540 | 22.420 | 0.540 | 10.303 |
| 19 | 18.650 | 0.196 | 41.960 | 2.240 | 59.500 | 5.720 | 30.490 | 0.727 | 18.732 |
| 20 | 19.790 | 0.070 | 57.050 | 8.560 | 60.940 | 7.390 | 35.600 | 0.624 | 6.665 |
| 21 | 19.160 | 0.073 | 58.590 | 14.830 | 62.440 | 7.170 | 32.150 | 0.549 | 3.951 |
| 22 | 22.450 | 0.030 | 83.500 | 21.060 | 66.830 | 8.560 | 36.680 | 0.439 | 3.965 |
| 23 | 21.210 | 0.040 | 47.920 | 4.760 | 59.580 | 6.510 | 27.180 | 0.567 | 10.067 |
| 24 | 19.030 | 0.090 | 101.820 | 13.360 | 67.220 | 10.020 | 36.940 | 0.363 | 7.621 |
| 25 | 20.180 | 0.070 | 33.840 | 5.320 | 57.300 | 4.960 | 20.970 | 0.620 | 6.361 |
| 26 | 20.060 | 0.080 | 41.990 | 4.320 | 61.920 | 5.250 | 27.760 | 0.661 | 9.720 |
| 27 | 21.950 | 0.040 | 70.910 | 15.170 | 66.190 | 7.480 | 33.670 | 0.475 | 4.674 |

## Dominant Factor Summary

- `E`: mainly controlled by `Ebar_star`, `kbar_star`, and `Rf`.
- `nu`: mainly controlled by `Ebar_star`, `kbar_star`, and `Rf`.
- `UCS`: controlled by `Ebar_star`, `E_ratio`, `sigma_c_bar`, `coh_ratio`, `mu`, `phi_bar`, `beta_bar_moment`, `Rf`, and `R_sigma`.
- `phi`: mainly controlled by `Ebar_star`, `coh_ratio`, `mu`, `beta_bar_moment`, and `Rf`.
- `c`: controlled by `Ebar_star`, `sigma_c_bar`, `coh_ratio`, `phi_bar`, `beta_bar_moment`, `Rf`, and `R_sigma`.
- `sigma_cd/UCS`: controlled by `E_ratio`, `sigma_c_bar`, `coh_ratio`, `phi_bar`, `beta_bar_moment`, `Rf`, and `R_E`.
- `UCS/UTS`: mainly controlled by `phi_bar`, `beta_bar_moment`, `Rf`, and `R_sigma`.

## Example Fast Calibration

Target grey sandstone macro values:

| Metric | Target | Simulation | Error |
| --- | ---: | ---: | ---: |
| E (GPa) | 12.07 | 12.28 | 1.7% |
| nu | 0.202 | 0.186 | 6.9% |
| UCS (MPa) | 82.53 | 83.85 | 1.3% |
| sigma_cd/UCS | 0.514 | 0.436 | 15.2% |
| phi (deg) | 38.30 | 36.42 | 4.9% |
| c (MPa) | 22.08 | 23.59 | 6.8% |
| UCS/UTS | 12.00 | 11.52 | 4.0% |

Fixed values:

```text
E_ratio = 0.3
kbar_star = 3
beta_bar_moment = 0.5
Rf = 0.7
beta_weibull = 3
R_E = 0.1
R_k = 2
```

Back-solved / selected values:

```text
Ebar_star = 85 GPa
sigma_c_bar = 135 MPa
coh_ratio = 2
mu = 0.7
phi_bar = 30 deg
R_sigma = 0.1
```
