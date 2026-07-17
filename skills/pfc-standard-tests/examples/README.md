# Example Cases

This directory documents how to use the bundled standard-test code templates. The actual PFC `.dat`, `.p2fis`, `.p3fis`, and geometry files live in `../scripts/canonical/` so code stays under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    biaxial/
    ucs/
    brazilian/
    direct-shear/
    three-point-bending/
    triaxial-rigid/
    triaxial-flexible-membrane/
examples/
  README.md
```

## Supported Cases

### `scripts/canonical/biaxial/`

2D biaxial compression workflow.

Suggested run order:

```text
1chengyang.dat
2yuya.dat
3jiaojiaojie.dat
4weiya.dat
5jiazai.dat
```

Optional cyclic loading variant:

```text
5.1循环加载.dat
```

### `scripts/canonical/ucs/`

2D uniaxial compression workflow with optional fracture tracking.

Suggested run order:

```text
1chengyang.dat
2yuya.dat
3jiaojiaojie.dat
4jialiewen.dat
4xiezai.dat
5jiazai.dat
```

Include:

```text
fracture.p2fis
```

### `scripts/canonical/brazilian/`

2D Brazilian splitting workflow.

Suggested run order:

```text
1chengyang.dat
2yuya.dat
3jiajiaojie.dat
4xiezai.dat
5jiazai.dat
```

Include:

```text
fracture.p2fis
```

### `scripts/canonical/direct-shear/`

2D direct shear workflow.

Suggested run order:

```text
1chengyang.dat
2yuya.dat
3jiajiaojie.dat
4jiazhouya.dat
5jiazai.dat
```

Include:

```text
fracture.p2fis
```

### `scripts/canonical/three-point-bending/`

2D three-point bending workflow using an external DXF geometry asset.

Suggested run order:

```text
1chengyang.dat
2tihuan.dat
3jiajiaojie.dat
4addjiazai.dat
5jiazai.dat
```

Include:

```text
11.dxf
fracture.p2fis
```

### `scripts/canonical/triaxial-rigid/`

3D conventional triaxial compression with rigid wall confinement.

Suggested run order:

```text
1chengyang.dat
2yuya.dat
3jiajiaojie.dat
4weiya.dat
5jiazai.dat
```

Include:

```text
fracture.p3fis
```

### `scripts/canonical/triaxial-flexible-membrane/`

3D conventional triaxial compression with shell membrane confinement.

Suggested run order:

```text
1chengyang.dat
2yuya.dat
3jiajiaojie.dat
4jiarouxing.dat
5jiazai.dat
```

Include:

```text
fracture.p3fis
```

## Validation Expectation

For a new machine or before publishing a derived case:

1. Run one 2D case first, usually `ucs`, because it exercises sample generation, bonding, loading, and `fracture.p2fis`.
2. Run one 3D case next, usually `triaxial-rigid`, because it exercises PFC3D syntax and `fracture.p3fis`.
3. If using flexible confinement, validate `triaxial-flexible-membrane` separately because it depends on shell structure and wall-structure coupling commands.
4. Rebuild saved states from `.dat` files; do not ship `.sav` states as the authoritative source.
5. Confirm that expected histories/curves are created before adapting parameters.

## How To Materialize A Case In A Project

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in stage order. If a case uses `fracture.p2fis` or `fracture.p3fis`, keep the fracture helper in the same working directory unless the `.dat` file is edited to use another path.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_ucs_case
cp -r scripts/canonical/ucs/* my_ucs_case/
```

Then run the staged `.dat` files in PFC 6.0.

## GitHub Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Check redistribution permission for upstream teaching assets before publishing.
- If upstream licensing is unclear, publish only derived/rewritten templates and keep a note that users must provide original teaching assets themselves.
