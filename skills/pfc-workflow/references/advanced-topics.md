# Advanced Topics

Use this file for workflow extensions beyond a simple bonded or granular baseline.

## Particle shape and generation

- clumps for irregular particle interlock
- rigid blocks or polyhedral analogs for blocky systems
- grading-driven generation from measured particle-size distributions

## Geometry and DFN

- imported geometry for excavation or boundary control
- DFN-based structural weakness or mapped fracture sets
- cutting or masking operations for tunnels, slopes, or voids

## Boundary conditions

- rigid walls for simple loading
- flexible membranes for triaxial realism
- periodic boundaries for representative volume studies
- servo control for constant stress, strain rate, or volume paths

## Extended test families

- UCS
- Brazilian splitting
- biaxial and triaxial compression
- direct shear or ring shear
- creep and cyclic loading

## Coupled physics

- thermal-mechanical coupling
- seepage or CFD-DEM style workflows
- hydraulic or pore-pressure driven failure scenarios

## Automation

- batch parameter sweeps
- design of experiments
- surrogate-assisted or optimizer-assisted calibration
- campaign orchestration through standardized run tables and metrics files

## Performance traps

- timestep misuse
- overly aggressive density scaling in non-quasi-static problems
- damping choices that distort the response
- particle counts that exceed the information need of the study
- parallel optimization that overwhelms GUI-bound or license-limited PFC environments
