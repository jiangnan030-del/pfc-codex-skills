# Reliability and Scaling

Use this reference when the model runs but the result is unstable,
inconsistent, or not trustworthy. Full code lives in:

- `source-code-reliability-scaling-pfc6.md`

## 1. Consistent initial state

The packed state must match the intended calibration state.

Check:

- porosity is reasonable
- coordination is not artificially low
- floating particles are limited
- overlap and boundary-force distributions are not pathological

## 2. `contact` versus `cmat`

Treat them as different tools:

- `contact property` updates existing contacts
- `contact cmat default` or `contact cmat add` controls future contacts

If new contacts appear during loading, using only `contact property` can create
hidden inconsistency.

## 3. Existing-contact versus future-contact assignment

Two distinct workflows exist:

1. assign current contacts after packing and before production loading
2. assign newly activated contacts with a callback during cycling

Multi-material models especially need this distinction.

## 4. Loading-rate control

Loading rate is usually a numerical control parameter, not a material law.

Rules:

- ramp from zero to the target velocity
- test sensitivity by slowing loading
- do not claim rate dependence unless the constitutive model supports it

Typical warning signs:

- large initial stress spike
- noticeable peak shift when only velocity changes
- strong inertial noise in a quasi-static test

## 5. Size effect

Macroscopic response depends on specimen size relative to particle size and
heterogeneity scale.

One empirical family quoted in the source material is

$$
E = 28.01 X^{-0.049}
$$

$$
\sigma_c = 129.32 X^{-0.106}
$$

where `X` is the specimen-size ratio in that calibration family.

Use such corrections only when:

- the material family is the same
- packing logic is consistent
- the relation has been checked in the new size range

Otherwise recalibrate at the actual scale.

## 6. Common traps

- calibrating on one packing state and deploying on another
- changing particle grading during geometry edits without recalibration
- driving walls too fast and reading oscillations as constitutive behavior
- using too few contacts in measurement windows
