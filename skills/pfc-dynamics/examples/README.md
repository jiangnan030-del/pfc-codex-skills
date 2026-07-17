# Example Cases

This directory documents how to use the bundled PFC dynamics code templates. The actual `.dat`, `.FIS`, and source-like `.txt` files live in `../scripts/canonical/` so executable/source-like code stays under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    slope-seismic-pfc6/
      1diji.dat
      2xuepo.dat
      3dizhen.dat
    demolition-blasting-reference/
      crk.FIS
      fishcall.FIS
      flt.FIS
      demolition_model_build.txt
examples/
  README.md
```

## Supported Example Sets

### `scripts/canonical/slope-seismic-pfc6/`

PFC 6.0 slope and sinusoidal wall-motion example.

Suggested run order:

```text
1diji.dat
2xuepo.dat
3dizhen.dat
```

Use `1diji.dat` to create the initial assembly, `2xuepo.dat` to form the slope and save the prepared state, and `3dizhen.dat` to apply time-dependent wall velocity.

### `scripts/canonical/demolition-blasting-reference/`

Legacy blasting/demolition reference snippets.

Suggested use:

```text
read crack-tracking and callback packages
audit FISH callback syntax and object intrinsics
rewrite only the needed parts for the target PFC version
```

Do not treat these legacy files as ready-to-run PFC 6.0 workflows without syntax and physics review.

## Validation Expectation

For a new machine or before publishing a derived dynamics template:

1. Validate the static preparation stage before dynamic loading.
2. Confirm dynamic loading starts from a saved/prepared state.
3. Confirm mechanical time is reset if the loading function depends on time.
4. Confirm damping and timestep assumptions are documented.
5. Confirm histories capture input motion and dynamic response.
6. Confirm legacy blasting/demolition snippets are clearly marked as reference-only unless rewritten.

## How To Materialize A Dynamics Example

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_dynamic_case
cp -r scripts/canonical/slope-seismic-pfc6/* my_dynamic_case/
```

Then run the staged `.dat` files in the appropriate PFC environment.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav`, project metadata, media, PDFs, archives, or large output dumps as authoritative examples.
- If upstream licensing is unclear, publish rewritten snippets and retain this README as usage guidance.
