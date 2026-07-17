# Overview

## Purpose

`pfc-fast-calibration` captures a rapid calibration method for an improved PFC3D linear parallel-bond model. It converts a large manual calibration problem into a structured process:

```text
13 micro-parameters -> 27 orthogonal runs -> macro metric extraction
-> Pearson correlation -> regression formulas -> back-solved starting parameters
-> a small number of validation iterations
```

The skill is most useful when a conventional LPBM rock specimen produces a compression/tension ratio that is too low, often around `3-4`, and the user needs a more realistic rock ratio such as `10-30`.

## Boundary

This skill owns:

- improved LPBM calibration logic
- 13-parameter factor definitions
- strong/weak ball-ball contact grouping
- Weibull random damage for bond properties
- orthogonal design and regression strategy
- macro metric extraction definitions for calibration
- source formula and code migration

This skill does not own:

- complete PFC workflow orchestration
- generic contact-law selection beyond the improved LPBM route
- servo-wall theory and stability implementation details
- canonical laboratory-test templates outside the calibration campaign
- final plotting/report production

## Skill Relationships

Use these current repository skills instead of older source-document names:

| Source relationship | Current skill handoff |
| --- | --- |
| Workflow bus | `pfc-workflow` |
| Contact theory / foundations | `pfc-contact-models`, `pfc-basics` |
| Modeling techniques / servo / curve extraction | `pfc-servo-calibration`, `pfc-standard-tests`, `pfc-postprocessing` |
| Mineral heterogeneity / Weibull / grouped assignment | `pfc-mineral-heterogeneity` |
| FISH implementation details | `pfc-fish` |

## Source Method Summary

The source method improves the LPBM by splitting ball-ball contacts into strong and weak groups. Weak contacts use reduced stiffness/strength ratios and all selected bonded properties can be multiplied by Weibull random variables.

The 13 micro-parameters are:

1. bonded effective modulus `Ebar_star`
2. linear/bonded modulus ratio `E_ratio`
3. bonded stiffness ratio `kbar_star`
4. bonded tensile strength `sigma_c_bar`
5. cohesion/tensile strength ratio `coh_ratio`
6. friction coefficient `mu`
7. bond friction angle `phi_bar`
8. moment contribution factor `beta_bar_moment`
9. weak-contact filling ratio `Rf`
10. Weibull shape parameter `beta_weibull`
11. weak/strong strength ratio `R_sigma`
12. weak/strong bond modulus ratio `R_E`
13. stiffness-ratio multiplier `R_k`

The 7 macro calibration outputs are:

```text
E, nu, UCS, phi, c, sigma_cd/UCS, UCS/UTS
```

## Source Example

A source grey sandstone example used macro targets:

```text
E = 12.07 GPa
nu = 0.202
UCS = 82.53 MPa
sigma_cd/UCS = 0.514
phi = 38.30 deg
c = 22.08 MPa
UCS/UTS = 12
```

A calibrated simulation gave:

```text
E = 12.28 GPa
nu = 0.186
UCS = 83.85 MPa
sigma_cd/UCS = 0.436
phi = 36.42 deg
c = 23.59 MPa
UCS/UTS = 11.52
```

Most errors were below 7%, while `sigma_cd/UCS` had about 15.2% error.

## Recommended Workflow

1. Confirm specimen scale, version, and target macro values.
2. Choose source reproduction or new calibration mode.
3. Generate the 27-run orthogonal table or use the bundled table.
4. Materialize one PFC case template per run.
5. Assign improved LPBM contact groups and Weibull damage.
6. Run UCS, UTS, and triaxial tests.
7. Extract `E`, `nu`, `UCS`, `UTS`, `phi`, `c`, and `sigma_cd/UCS`.
8. Fit or reuse regression equations.
9. Back-solve candidate micro-parameters.
10. Run validation iterations and report error.

## Public Skill Policy

- Keep this skill self-contained and GitHub-friendly.
- Store scripts under `scripts/canonical/`.
- Store examples as documentation only.
- Do not include private save states, project files, screenshots, or full local paths.
- Treat command files as templates that must be syntax-checked for the installed PFC version.
