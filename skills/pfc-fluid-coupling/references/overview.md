# Overview

## Purpose

`pfc-fluid-coupling` provides reusable PFC 6.0 fluid-solid coupling guidance. It is a child skill of `pfc-workflow`; it supplies targeted seepage, buoyancy, CFD element, and Darcy/FiPy coupling expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- simple buoyancy and particle-water force examples
- `model configure cfd` and CFD node/element input contracts
- PFC CFD element density, viscosity, velocity, and buoyancy setup
- FiPy/Darcy pressure solve integration patterns
- auxiliary mesh/data file handoff requirements

This skill does not own:

- full case lifecycle orchestration
- standard mechanical-test template selection
- FLAC coupling
- general dynamics/blasting
- post-processing figure generation
- AE/energy/source-mechanism analysis

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/fluid-coupling-baseline/`
- `scripts/apps/create_mesh/`

Included files:

- `1kelirushui.dat`: particle-water buoyancy style example using applied vertical force based on submerged area.
- `1luoshui.dat`: built-in CFD setup using `model configure cfd`, `cfd read nodes`, `cfd read elements`, buoyancy, density, viscosity, and fluid velocity.
- `Node.dat`: example CFD node table used by `1luoshui.dat`.
- `Elem.dat`: example CFD element table used by `1luoshui.dat`.
- `particles.dat`: particle and wall setup used by the Python Darcy/FiPy example.
- `dll.py`: Python-side Darcy flow example using FiPy, NumPy, PFC `itasca`, `ballarray`, and `cfdarray` APIs.
- `test.dat`: minimal placeholder source file from the baseline example set.
- `scripts/apps/create_mesh/create_mesh.exe`: optional legacy mesh-helper application associated with the CFD node/element workflow. Keep it as a preserved helper, not as the only reproducible path.

## Fluid-Coupling Patterns

### 1. Simple Buoyancy

Use when the user only needs water-level buoyancy without full CFD mesh solving.

Pattern:

```text
compute submerged fraction or area/volume
force = fluid_density * gravity * submerged_area_or_volume
apply force to particles each cycle
```

The bundled `1kelirushui.dat` demonstrates this idea for 2D particles crossing a water level.

### 2. Built-In CFD Element Coupling

Use when the user has a CFD mesh node/element table and wants PFC to apply CFD buoyancy/drag fields.

Pattern:

```text
model configure cfd
cfd read nodes "Node.dat"
cfd read elements "Elem.dat"
cfd buoyancy on
element cfd attribute density ...
element cfd attribute viscosity ...
element cfd attribute velocity-x ...
```

The bundled `1luoshui.dat` demonstrates this setup.

### 3. Python Darcy/FiPy Coupling

Use when pore pressure or Darcy flow must be solved externally and written back to PFC CFD arrays.

Pattern:

```text
create FiPy mesh
create PFC CFD mesh from FiPy vertices/cells
read porosity from PFC
compute permeability/mobility
solve pressure equation
write pressure, pressure gradient, and velocity to PFC CFD arrays
update periodically during cycling
```

The bundled `dll.py` demonstrates this pattern. It requires Python dependencies outside plain PFC command files, especially `numpy` and `fipy`, plus access to PFC's embedded `itasca` Python API.

## Inclusion Rules

- Keep minimal `.dat`, `.py`, and small mesh/data tables needed to reproduce the workflow.
- Do not make helper executables mandatory unless no transparent replacement exists; store preserved apps under `scripts/apps/` and document their input/output contract.
- Document any optional external solver dependency clearly.
- Keep mesh scale, node/element schema, and boundary conditions explicit.

## Handoff To pfc-workflow

After this skill provides coupling snippets or a file-contract plan, return to `pfc-workflow` for:

- full case directory creation
- standard test or specimen selection
- solve management
- post-processing route selection
- V&V and delivery
