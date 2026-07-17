# Example Cases

This directory documents how to use the bundled PFC FISH code templates. The actual `.dat`, `.p2dat`, and small input data files live in `../scripts/canonical/` so executable/source-like code stays under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    fish-basics-pfc6/
      1value.dat
      2xunhuan.dat
      3fishcreate_ball.dat
      3huidiao.dat
      4shepizouwei.dat
      5guitusaipao.dat
      6jianduan.dat
    fish-basics-pfc5-reference/
      01-.../*.p2dat
      02-.../*.p2dat
      ...
      10-.../*.p2dat
examples/
  README.md
```

## Supported Example Sets

### `scripts/canonical/fish-basics-pfc6/`

PFC 6.0-native FISH examples.

Suggested learning order:

```text
1value.dat
2xunhuan.dat
3fishcreate_ball.dat
3huidiao.dat
4shepizouwei.dat
5guitusaipao.dat
6jianduan.dat
```

Use these first when teaching or validating PFC 6.0 FISH syntax.

### `scripts/canonical/fish-basics-pfc5-reference/`

Legacy reference snippets grouped by topic:

```text
variables
data types
custom functions
conditionals
loops
interactive IO
data recording/output
data reading/application
map usage
standard functions
```

Use these as reference material only. Audit syntax and intrinsics before using them in a PFC 6.0 workflow.

## Validation Expectation

For a new machine or before publishing a derived FISH template:

1. Validate one PFC 6.0-native basics file first.
2. Validate `3huidiao.dat` or another callback example if callback logic is involved.
3. Confirm all histories return numeric scalar values.
4. Confirm callback registration appears in `fish list callbacks` if used.
5. Confirm old `.p2dat` snippets are either rewritten for PFC 6.0 or clearly marked as reference-only.

## How To Materialize A FISH Example

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_fish_case
cp -r scripts/canonical/fish-basics-pfc6/* my_fish_case/
```

Then run the staged `.dat` files in the appropriate PFC environment.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav`, project metadata, media, PDFs, or large output dumps as authoritative examples.
- If upstream licensing is unclear, publish rewritten snippets and retain this README as usage guidance.
