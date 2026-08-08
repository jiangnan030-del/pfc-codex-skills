---
name: pfc-python
description: >
  Child skill of pfc-workflow for driving ITASCA PFC (PFC2D/PFC3D) from Python via the embedded
  `itasca` module: issue PFC commands with itasca.command(), iterate ball/contact objects, register
  Python callbacks inside the cycle loop (set_callback / remove_callback), and exchange bulk data
  through ballarray / cfdarray. Use when the user wants to script PFC with Python, build models
  procedurally, post-process with numpy/matplotlib, or couple PFC with external Python libraries
  (e.g. FiPy finite-volume Darcy flow).
version: 1.0.0
related_skills:
  - pfc-workflow
  - pfc-basics
  - pfc-fish
  - pfc-fluid-coupling
  - pfc-fast-calibration
  - pfc-postprocessing
---

# PFC + Python (itasca module)

Use this skill for the cross-cutting capability of **driving and extending PFC from Python**. Modeling,
calibration and post-processing mainlines stay in `pfc-workflow`; physics topics stay in their own
child skills.

## Parent Skill Relationship

`pfc-python` is a child skill of `pfc-workflow`. It owns only Python-side automation and secondary
development.

- Parent `pfc-workflow`: owns the full PFC project lifecycle and decides when Python scripting is needed.
- Child `pfc-python`: owns the `itasca` module surface, object/type system, callbacks, bulk array
  exchange (`ballarray` / `cfdarray`), and Python-side coupling with external libraries.
- Sibling `pfc-fish`: owns native FISH scripting; prefer FISH for in-model logic, Python for external
  libraries, data science, and orchestration.
- Sibling `pfc-fluid-coupling`: owns CFD/seepage physics; this skill owns the Python plumbing it uses.
- Sibling `pfc-fast-calibration`: owns multi-case parameter sweeps scheduled from Python.

## When To Use

- The user wants Python instead of pure FISH/command streams for model building, parametrization or post-processing.
- Custom algorithms must be injected into the PFC solve loop (callbacks).
- PFC must be coupled with external Python libraries (numpy / matplotlib / FiPy / ML).

## Operating Rules

1. Distinguish the two interaction layers: submodule functions (`itasca.ball.*`, `itasca.contact.*`)
   versus object methods (`ball.radius()`, `contact.prop()`).
2. For bulk particle/fluid data use `ballarray` / `cfdarray` (numpy arrays); do not loop object-by-object.
3. Register callbacks with `set_callback(name, order)` and unregister with `remove_callback`; `order`
   selects the insertion point in the cycle loop.
4. Confirm the embedded Python version first (PFC5.0 = Python 2.7, PFC6.0/7.0/9.0 = Python 3.x) and
   adjust syntax; see `references/python2-to-3.md`.
5. Case-specific file names, meshes and coordinates in `scripts/` are examples only. Verify command
   syntax against the official documentation for the target PFC version before use.

## Required Inputs

Ask for these if missing:

- PFC version, dimensionality (PFC2D/PFC3D) and embedded Python version.
- Goal: procedural model building, in-loop algorithm, bulk data extraction, or external coupling.
- Specimen geometry, particle size range, porosity, densities, contact model and boundaries.
- For coupling: fluid density/viscosity, mesh resolution, inlet/outlet masks, flow rate or pressures,
  and the flow-solve interval relative to mechanical cycles.
- Required outputs: histories, fields, figures, or exported arrays.

## Core API Map

| Need | API |
| --- | --- |
| Send PFC commands | `itasca.command("""...multi-line...""")` |
| Count / find / iterate balls | `itasca.ball.count()`, `itasca.ball.find(id)`, `itasca.ball.near(pos)`, `itasca.ball.list()` |
| Ball object methods | `ball.id()`, `ball.radius()`, `ball.set_radius()`, `ball.pos()`, `ball.contacts()` |
| Contacts | `itasca.contact.list(all=True)`, `c.pos()`, `c.force_global()`, `c.props()`, `c.prop(name)`, `c.set_prop(name, v)`, `c.end1()`, `c.end2()` |
| Contact types | `itasca.BallBallContact`, `itasca.BallFacetContact` |
| In-loop callbacks | `itasca.set_callback("fn", order)`, `itasca.remove_callback("fn", order)`, `itasca.cycle()` |
| Bulk particle arrays | `from itasca import ballarray as ba` -> `ba.radius()`, `ba.pos()` |
| Bulk CFD arrays | `from itasca import cfdarray as ca` -> `ca.create_mesh()`, `ca.porosity()`, `ca.set_pressure()`, `ca.set_pressure_gradient()`, `ca.set_extra()` |
| Per-element CFD access | `from itasca.element import cfd` -> `element.set_vel(...)` |
| Clumps | `itasca.clump.list()`, `itasca.clump.pebble.list()`, `cl.vol()`, `cl.in_group('stone')`, `itasca.clump.find(id).delete()` |

## Canonical Script Map

| Topic | File | Purpose |
| --- | --- | --- |
| itasca basics | `scripts/itasca_basics.py` | Commands, ball/contact iteration, virtual vs active contacts, callback demo. |
| Soil-rock mixture 3D direct shear | `scripts/shear_box.py` | Clump-based stone/cement placement by volume fraction, 10-wall shear box, stone-content back-calculation, initial-state save. |
| PFC-FiPy Darcy seepage (one-way) | `scripts/darcy_flow.py` | Steady pressure diffusion on a FiPy grid, Kozeny-Carman permeability from PFC porosity, write-back of pressure/gradient/velocity, callback-driven flow updates. |

## Checklist

1. Confirm embedded Python version and adjust Python 2 vs 3 syntax.
2. Use triple-quoted strings for multi-line `itasca.command()`; verify placeholder counts in `.format()`.
3. Vectorize bulk reads/writes with `ballarray` / `cfdarray` instead of per-object Python loops.
4. Pick the correct callback `order`; throttle work with `it.cycle() % N == 0`; unregister when done.
5. Replace example-specific assets (`particles.p3dat`, `input_clump_moban`, 10x20x10 mesh, inlet/outlet
   masks, `grain_size`) with real project values.
6. Keep units self-consistent (PFC is unitless); the bundled examples use SI.
7. For `ca.create_mesh`, reorder FiPy `_cellVertexIDs` as `(0, 2, 3, 1, 4, 6, 7, 5)` to match PFC element
   vertex conventions, otherwise element geometry is wrong.

## Output Contract

A complete handoff back to `pfc-workflow` should include:

- The chosen Python integration pattern (commands, object iteration, callback, bulk arrays, coupling).
- The scripts or snippets used, with case-specific values replaced.
- Callback registration points and update intervals.
- Data-exchange contract: which arrays/fields are read from and written back to PFC.
- Dependency notes (`numpy`, `matplotlib`, `fipy`, `configure cfd`).
- A note that full case execution, V&V and delivery continue in `pfc-workflow`.

## Local Contents

- `references/itasca-api.md`: itasca module surface, object/type system, callbacks, array exchange.
- `references/python2-to-3.md`: Python 2 -> 3 migration notes and source-correction disclosure.
- `references/pitfalls.md`: common traps and terminology calibration.
- `scripts/itasca_basics.py`, `scripts/shear_box.py`, `scripts/darcy_flow.py`: reference examples.
- `examples/README.md`: how to validate the bundled demonstrations.
