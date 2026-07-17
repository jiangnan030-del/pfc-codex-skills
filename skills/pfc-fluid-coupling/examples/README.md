# Example Cases

This directory documents how to use the bundled fluid-coupling code templates. The actual PFC `.dat`, Python, and auxiliary mesh/data files live in `../scripts/canonical/` so executable code stays under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    fluid-coupling-baseline/
      1kelirushui.dat
      1luoshui.dat
      dll.py
      particles.dat
      Node.dat
      Elem.dat
      test.dat
  apps/
    create_mesh/
      create_mesh.exe
examples/
  README.md
```

## Supported Example Set

### `scripts/canonical/fluid-coupling-baseline/`

Minimal PFC 6.0 examples for buoyancy, built-in CFD element input, and Python Darcy/FiPy coupling.

Suggested learning order:

```text
1kelirushui.dat
1luoshui.dat
particles.dat
dll.py
```

Use `1kelirushui.dat` for simple water-level buoyancy. Use `1luoshui.dat` with `Node.dat` and `Elem.dat` for built-in CFD element setup. Use `particles.dat` and `dll.py` for the Python Darcy/FiPy coupling pattern. The optional `scripts/apps/create_mesh/create_mesh.exe` helper is preserved with the skill for mesh-related workflows, but the bundled `Node.dat` and `Elem.dat` allow the baseline example to be inspected without depending on the executable.

## Validation Expectation

For a new machine or before publishing a derived fluid-coupling template:

1. Run `1kelirushui.dat` first because it does not require an external Python flow solver.
2. Run `1luoshui.dat` and confirm `Node.dat` / `Elem.dat` are found from the working directory.
3. For `dll.py`, confirm the PFC embedded Python environment has `numpy` and `fipy` available.
4. Confirm mesh scale, particle scale, fluid density, viscosity, pressure, and velocity units.
5. Confirm output histories or exported fields are sufficient to validate the coupled response.

## How To Materialize A Fluid Example

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_fluid_case
cp -r scripts/canonical/fluid-coupling-baseline/* my_fluid_case/
```

Then run the staged `.dat` or Python files in the appropriate PFC 6.0 environment.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav` files or PFC project metadata as authoritative examples.
- Do not publish helper executables as required runtime dependencies unless their license and role are explicit; preserved apps should live under `scripts/apps/` and remain optional where possible.
- If upstream licensing is unclear, publish rewritten snippets and retain this README as usage guidance.
