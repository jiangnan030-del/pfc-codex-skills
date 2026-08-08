# pfc-python examples

The scripts under `../scripts/` are reference implementations, not calibrated models. Validate them
like this:

## 1. `itasca_basics.py`

Run inside PFC's Python console. Expected behaviour:

- 8000 balls created; radius sum = 8000 * 1.25e-3 = 10.0.
- After `cycle 1`, the ball nearest the origin has 6 contacts in a cubic packing.
- `itasca.contact.list(all=True)` returns one more contact than `itasca.contact.list()` in the
  three-ball/one-wall model (the virtual ball-ball contact).
- The callback fires 5 times during `cycle 5`, and 0 times after `remove_callback`.

## 2. `shear_box.py`

Prerequisite: an `input_clump_moban` file defining clump templates `s1`..`s5`.

Checks:

- 10 walls exist (`bottom`, `right_bottom`, `dangban_right`, `right_top`, `top_wall`, `left_top`,
  `dangban_left`, `left_bottom`, `front`, `behind`).
- No clump pebble crosses the specimen box after `in_box()`.
- `compute_block_ratio()` returns a stone content close to `stone_need` (0.33); tune `clump_poro`,
  bin sizes and the cement porosity if not.
- `save ini` produces an equilibrated, zeroed initial state before shearing.

## 3. `darcy_flow.py`

Prerequisites: `particles.p3dat`, plus `numpy` and `fipy` available to PFC's Python.

Checks:

- `configure cfd` runs before any CFD element command.
- `test_inflow_outflow()` passes: |inflow + outflow| < 1e-6 (mass balance).
- Pressure, pressure gradient and element velocity fields appear in PFC after `cfd update`.
- The `update_flow` callback re-solves flow every 100 mechanical cycles.

Before adapting to a real case, replace grid resolution, inlet/outlet masks, flow rate, grain size,
fluid density/viscosity and all file names.
