# Example Cases

This directory documents how to use the bundled PFC basics templates. The actual `.dat`, `.dxf`, `.stl`, `.p2dat`, and `.p3dat` files live in `../scripts/canonical/` so executable/source-like assets stay under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    basic-elements-pfc6/
      1create_ball.dat
      2pengzhuang.dat
      3create_wall.dat
    clump-rblock-pfc6/
      1ClumpTemplate.dat
      2CreateClump.dat
      3rblockTemplate.dat
      4createrblock.dat
      11.dxf
      22.stl
    legacy-basics-reference/
      selected PFC5-era .p2dat/.p3dat snippets
examples/
  README.md
```

## Supported Example Sets

### `scripts/canonical/basic-elements-pfc6/`

PFC 6.0-native foundation examples.

Suggested learning order:

```text
1create_ball.dat
2pengzhuang.dat
3create_wall.dat
```

Use this set first when teaching or validating the minimal PFC object lifecycle.

### `scripts/canonical/clump-rblock-pfc6/`

PFC 6.0 clump and rigid-block basics.

Suggested learning order:

```text
1ClumpTemplate.dat
2CreateClump.dat
3rblockTemplate.dat
4createrblock.dat
```

Use this set when the specimen needs non-spherical particles or rigid blocks but does not yet require full CAD import routing.

### `scripts/canonical/legacy-basics-reference/`

Reference-only PFC5-era snippets for balls, walls, groups, and ranges.

Use these snippets to compare syntax and intent, then rewrite into PFC 6.0-native stages before recommending them in a public workflow.

## Validation Expectation

For a new machine or before publishing a derived basics template:

1. Run one PFC 6.0 basic-elements file.
2. Confirm domain extents, object count, object positions, groups, and contact setup.
3. Run one clump/rblock file if non-spherical shapes are relevant.
4. Keep legacy snippets as reference until audited and modernized.
5. Return to `pfc-workflow` for complete case staging.

## How To Materialize A Basics Example

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_basic_case
cp -r scripts/canonical/basic-elements-pfc6/* my_basic_case/
```

Then run the staged `.dat` files in the appropriate PFC environment.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav`, project metadata, media, PDFs, archives, or huge generated outputs as authoritative examples.
- Legacy `.p2dat`/`.p3dat` snippets should remain reference-only unless explicitly audited for the target PFC version.
