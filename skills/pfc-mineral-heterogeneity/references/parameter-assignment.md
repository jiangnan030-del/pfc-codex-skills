# Parameter Assignment

Use this reference when assigning per-mineral or interface LPBM parameters after mineral groups and contact groups exist.

## Calibration Philosophy

The mineral heterogeneity route exists because homogeneous BPM/LPBM models can produce unrealistic compression/tension strength ratios and miss mineral-controlled crack localization. Use separate mineral or interface parameters when the rock has identifiable phases such as feldspar, quartz, and mica.

Default calibration order:

1. choose matrix and filling phases
2. set filling/matrix strength ratios from compression/tension ratio targets
3. calibrate elastic response using effective modulus and stiffness ratio
4. calibrate strength using bond tensile/cohesion values
5. tune interface rules and damage distribution
6. validate against UCS, BTS/UTS, Poisson's ratio, and crack pattern

## Example Source Targets

Example laboratory targets from the source material:

```text
Young's modulus: 21.04 GPa
peak UCS: 216.43 MPa
Poisson's ratio: 0.22
Brazilian tensile strength: 19.96 MPa
```

Example numerical match:

```text
Young's modulus: 20.6 GPa
peak UCS: 226.67 MPa
BTS: 16.7 MPa
```

## Example Per-Mineral Parameters

Treat these as calibration seeds, not universal constants.

| Mineral | Linear emod (GPa) | PB emod (GPa) | kratio | pb_ten (MPa) | pb_coh (MPa) |
| --- | ---: | ---: | ---: | ---: | ---: |
| mica | 1.9 | 6.8 | 2.7 | 49.6 | 49.6 |
| quartz | 7.5 | 28 | 2.7 | 66.2 | 66.2 |
| feldspar | 9.6 | 32 | 2.7 | 332.5 | 332.5 |

A source workflow used feldspar as the matrix and quartz/mica as filling phases. Filling-to-matrix bond-strength ratios around `0.1-0.2` were used to bring the compression/tension ratio into a realistic range. Example ratios were approximately:

```text
quartz / feldspar strength ratio: 0.15
mica / feldspar strength ratio: 0.12
```

## PFC Assignment Pattern

After `model clean` and contact grouping:

```text
contact model linearpbond range contact type 'ball-ball'
contact method bond gap 1e-3
contact method deform emod ... kratio ... range group 'pbond_feldspar'
contact method pb_deform emod ... kratio ... range group 'pbond_feldspar'
contact property pb_ten ... pb_coh ... range group 'pbond_feldspar'
```

Use `contact property` for existing contacts after grouping. Use `contact cmat` for future contacts or when building a reusable contact assignment table.

## Interface Rules

Choose one rule and document it:

- **matrix-dominant**: mixed contacts inherit matrix properties.
- **weak-boundary**: mixed contacts use weaker boundary properties.
- **weak-mineral priority**: contacts touching mica or another weak mineral inherit weak properties.
- **phase-pair table**: every mineral pair has a dedicated group and parameter row.
- **area-ratio stochastic**: mixed contacts are assigned based on mineral area fraction or target ratio.

For publishable studies, prefer a phase-pair table because it is explicit and auditable.

## Weibull Damage

Use Weibull multipliers to represent mineral-scale pre-existing defects, pores, or microcracks.

Random multiplier:

```text
x = alpha * (-ln(1 - R))^(1 / beta)
```

where:

- `R` is a uniform random value in `[0, 1)`
- `alpha` is the scale parameter
- `beta` is the shape parameter
- larger `beta` means less dispersion

Apply to:

- `pb_ten`
- `pb_coh`
- optionally `pb_kn`
- optionally `pb_ks`

Do not apply damage to every property by default. State what is damaged and why.

## Sensitivity Studies

Recommended mineral heterogeneity studies:

- fixed parameters, varied confining pressure
- fixed parameters, varied filling/matrix fraction
- fixed mineral fractions, varied Weibull `beta`
- homogeneous vs heterogeneous model comparison
- weak-boundary vs phase-pair interface comparison

## Validation Checklist

Before production runs, verify:

- mineral fraction error is within tolerance
- contact group counts are nonzero and plausible
- LPBM properties are assigned after contact grouping
- `model clean` was run before serious cycling
- UCS/BTS or UTS ratio is realistic
- failure pattern localizes through expected weak phases or interfaces
- random seed and Weibull parameters are recorded
