# Example Cases

This directory documents how to use the bundled PFC contact-model code templates. The actual `.dat` files live in `../scripts/canonical/` so executable/source-like code stays under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    linear-model-pfc6/
      1faxiang.dat
      2qiexiang.dat
    linearpbond-model-pfc6/
      1faxiang.dat
      2qiexiang.dat
      3qiexiang_2.dat
examples/
  README.md
```

## Supported Example Sets

### `scripts/canonical/linear-model-pfc6/`

PFC 6.0 two-ball linear contact demonstration.

Suggested run order:

```text
1faxiang.dat
2qiexiang.dat
```

Use `1faxiang.dat` for normal loading and `2qiexiang.dat` for shear response after restoring the normal-loading state.

### `scripts/canonical/linearpbond-model-pfc6/`

PFC 6.0 two-ball linear parallel-bond demonstration.

Suggested run order:

```text
1faxiang.dat
2qiexiang.dat
3qiexiang_2.dat
```

Use these examples to inspect bond activation, tensile/cohesive parameters, shear response, and bond stress/strength indicators.

## Validation Expectation

For a new machine or before publishing a derived contact-model template:

1. Run the linear two-ball normal and shear examples first.
2. Confirm `model clean` occurs after contact-model assignment and before contact lookup.
3. Confirm histories record force and displacement/stress quantities needed for interpretation.
4. For bonded examples, confirm `contact method bond` is executed after compatible contacts exist.
5. Confirm any macro-property claims are backed by a calibration or standard test workflow.

## How To Materialize A Contact Example

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_contact_case
cp -r scripts/canonical/linear-model-pfc6/* my_contact_case/
```

Then run the staged `.dat` files in the appropriate PFC environment.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav`, project metadata, media, PDFs, archives, or large output dumps as authoritative examples.
- If upstream licensing is unclear, publish rewritten snippets and retain this README as usage guidance.
