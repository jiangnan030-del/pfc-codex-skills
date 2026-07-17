# AE Calibration Cases And Sanity Checks

Use this reference when a user asks whether an AE/moment-tensor simulation is physically plausible or asks for starting values from the source material. These values are not universal material parameters; they are example starting points that must be recalibrated through `pfc-workflow` and `pfc-contact-models`.

## Rule Before AE Monitoring

Do not enable paper-grade AE interpretation before the specimen is mechanically calibrated.

Minimum macro targets should include:

- elastic modulus
- Poisson's ratio when relevant
- UCS or target strength
- peak strain or failure mode when available
- density and wave-speed consistency if moment magnitude or event duration uses wave speed

## Example Granite Targets From Source Material

One referenced granite AE case used a specimen around `70 x 70 x 150 mm` with approximate macro targets:

- UCS: `50-86 MPa`
- elastic modulus: `3.9 GPa`
- Poisson's ratio: `0.22`
- P-wave velocity: `3815 m/s`
- S-wave velocity: `2800 m/s`

A reported simulation match was approximately:

- UCS: `57.76 MPa`
- elastic modulus: `4.5 GPa`
- Poisson's ratio: `0.23`

## Example Micro-Parameter Starting Points

Treat these as example seeds, not final parameters.

```text
minimum particle radius: 0.3-0.7 mm
radius ratio: 1.66-1.75
density: 2810-4109 kg/m^3
friction coefficient: 0.5-0.8
particle modulus: 3.6-60 GPa
particle stiffness ratio kn/ks: 1-2.5
parallel-bond modulus: 3.6-30 GPa
parallel-bond stiffness ratio kn/ks: 1-2.5
parallel-bond tensile strength mean/std: about 30/3 to 40/8 MPa
parallel-bond cohesion or shear strength mean/std: about 30/3 to 40/8 MPa
parallel-bond radius multiplier: 1.0 in the cited examples
```

Route parameter design and contact-law details to `pfc-contact-models`. Route calibration campaign design to `pfc-workflow` or `pfc-servo-calibration` depending on the loading path.

## Expected AE Evolution

Use these checks as qualitative reasonableness criteria:

- compaction stage: little or no AE
- linear elastic stage: low AE count and small amplitudes
- stable crack-growth stage: AE frequency increases
- unstable growth approaching peak: AE event count and energy proxies accelerate
- post-peak: intense AE and localization
- cumulative AE often grows nonlinearly or near-exponentially with strain
- raw tensile cracks often dominate counts in bonded rock models
- shear/mixed source types may grow in relative importance near and after peak

## Stage Labels

If using O/A/B/C/D/E stage labels, document how they are assigned. Recommended sources:

- stress-strain landmarks
- crack-initiation and crack-damage points
- peak stress and residual region
- saved states from the parent workflow

Do not compare stage-wise AE fractions across cases unless stage definitions are identical.

## Common Calibration Traps

- tuning AE thresholds before the mechanical specimen is calibrated
- changing particle-size distribution after AE calibration
- changing loading rate between calibration and AE production runs
- interpreting moment magnitude without unit scaling
- using one event-duration parameter across materials with different wave speeds
- comparing raw hit counts from one case with clustered event counts from another

## Reporting Minimum

A report-ready AE calibration note should include:

- PFC version and dimensionality
- contact model and bonded-state creation route
- specimen size and units
- particle radius range and density
- macro calibration targets and achieved values
- loading rate and damping strategy
- AE hit/event definition
- clustering time-space parameters
- tensor classification thresholds
- output file list and reproducibility notes
