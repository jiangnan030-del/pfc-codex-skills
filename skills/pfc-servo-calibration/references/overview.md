# Overview

## Purpose

`pfc-servo-calibration` provides reusable PFC 6.0 servo-control and calibration sequencing guidance. It is a child skill of `pfc-workflow`; it supplies targeted servo and tuning expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- wall/ball target-force and target-stress servo concepts
- stiffness-based boundary velocity updates
- histories needed to validate servo convergence
- manual micro-to-macro calibration order
- compact PFC 6.0 servo demonstration code

This skill does not own:

- full case lifecycle orchestration
- standard-test template selection
- automated DOE/Bayesian campaign execution
- post-processing figure generation
- AE/energy/source-mechanism analysis
- coupling, dynamics, or CAD import workflows

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/servo-principles/`

Included files:

- `1sifu_1.dat`: two-ball target-force example using fixed velocity over computed travel distance.
- `2sifu_2.dat`: one-cycle target-force displacement example.
- `3sifu_3.dat`: wall target-force example using aggregate stiffness estimate.
- `3sifu_4.dat`: particle assembly and wall-box setup for continued servo demonstration.
- `4sifu_4_jixu.dat`: continued wall servo with contact-map stiffness, force error, velocity update, and history output.

## Servo Pattern

The canonical stiffness-based servo pattern is:

1. Measure current force or stress on the controlled boundary.
2. Compute error: `target - current`.
3. Estimate effective stiffness from active contacts.
4. Convert error to displacement: `delta = error / stiffness`.
5. Convert displacement to velocity over the update interval.
6. Apply a velocity cap when moving into real specimens.
7. Update until target is reached within tolerance.

In the bundled example, `4sifu_4_jixu.dat` illustrates this structure with a top wall:

```text
mubiao_force = target - wall.force.contact.y(wp)
zonggang = sum(contact.prop(ct,"kn") for ct in wall.contactmap(wp))
distance = mubiao_force / zonggang
wall.vel.y(wp) = -distance / timestep
```

When adapting to real biaxial/triaxial models, refresh stiffness during cycling and cap velocity to avoid overshoot.

## Calibration Pattern

Manual calibration should proceed from stable, low-dimensional targets to coupled nonlinear responses:

1. Fix specimen generation: seed, PSD, porosity, density, damping, domain, and wall geometry.
2. Tune elastic modulus with contact modulus and stiffness ratio.
3. Tune lateral response/Poisson ratio with stiffness ratio and boundary conditions.
4. Tune peak strength with bond strengths after elastic response is acceptable.
5. Tune post-peak/residual behavior with friction, damping, contact model choice, or softening rules.
6. Validate failure mode with cracks, force chains, shear bands, and residual curve shape.

## Inclusion Rules

- Keep minimal `.dat` snippets that demonstrate servo logic.
- Do not bundle binary save states or project metadata as authoritative assets.
- Use generated saves only during validation.
- Keep calibration examples parameterized and avoid private project paths.
- Keep black-box optimization or external executables outside this skill unless they are optional and documented.

## Handoff To pfc-workflow

After this skill provides servo snippets or a calibration plan, return to `pfc-workflow` for:

- full case directory creation
- standard test selection via `pfc-standard-tests` if needed
- solve management
- automated campaigns
- post-processing route selection
- V&V and delivery
