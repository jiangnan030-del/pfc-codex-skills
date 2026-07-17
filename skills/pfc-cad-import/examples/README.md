# Example Cases

This directory documents how to use the bundled PFC CAD/geometry import templates. The actual `.dat`, `.dxf`, `.stl`, `.p2clp`, and optional helper app files live in `../scripts/` so executable/source-like assets stay under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    geometry-range-pfc6/
      1_createGeometry.dat
      2_importGeo.dat
      3_range.dat
      4_rangefish.dat
      11.dxf
      11.stl
      22.dxf
      22.stl
    cluster-shape-pfc6/
      method1/
      method2/
      method3/
  apps/
    legacy-plugins/
      <slug>/
        app.exe
        small-example-inputs...
examples/
  README.md
```

## Supported Example Sets

### `scripts/canonical/geometry-range-pfc6/`

PFC 6.0-native geometry and range examples.

Suggested learning order:

```text
1_createGeometry.dat
2_importGeo.dat
3_range.dat
4_rangefish.dat
```

Use these first when teaching or validating PFC 6.0 geometry import/range syntax.

### `scripts/canonical/cluster-shape-pfc6/`

PFC 6.0 cluster, clump template, replacement, export, and rblock/geometry workflows.

Suggested use:

```text
method1: geometry-driven sample/replacement/export
method2: clump template and cluster replacement
method3: rblock/geometry resampling and interparticle variants
```

### `scripts/apps/legacy-plugins/`

Optional preserved helper applications.

Suggested use:

```text
inspect input/output files
write an input contract
prefer native PFC or script replacement when possible
run app only if its license and role are acceptable
```

## Validation Expectation

For a new machine or before publishing a derived CAD import template:

1. Validate native `geometry import` or `geometry generate` first.
2. Confirm model domain covers all imported wall facets before `wall import`.
3. Use `geometry list information` or equivalent checks before conversion.
4. Confirm units, coordinate axes, scale, and layer/group mapping.
5. For particle filling, validate object counts, porosity, grading, and range acceptance.
6. For helper apps, document input/output contracts before recommending use.

## How To Materialize A CAD Import Example

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_geometry_case
cp -r scripts/canonical/geometry-range-pfc6/* my_geometry_case/
```

Then run the staged `.dat` files in the appropriate PFC environment.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav`, project metadata, media, PDFs, archives, or huge generated DXF/text outputs as authoritative examples.
- Preserved apps under `scripts/apps/` should remain optional unless their license and role are explicit.
