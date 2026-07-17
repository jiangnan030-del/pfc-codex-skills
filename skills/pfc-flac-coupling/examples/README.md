# Example Cases

This directory documents how to use the bundled PFC-FLAC coupling code templates. The actual `.dat` and command-snippet files live in `../scripts/canonical/` so executable or source-like code stays under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    discrete-continuum-baseline/
      1dimian.dat
      2luoshi .dat
    flac3d-pfc-chapter11/
      11.*.txt
examples/
  README.md
```

## Supported Example Sets

### `scripts/canonical/discrete-continuum-baseline/`

Minimal PFC/FLAC-style discrete-continuum example.

Suggested run order:

```text
1dimian.dat
2luoshi .dat
```

Use `1dimian.dat` to create and save the continuum baseline. Use `2luoshi .dat` to restore the baseline, create a `wall-zone` coupling boundary, and add particles.

### `scripts/canonical/flac3d-pfc-chapter11/`

Readable command snippets from a FLAC3D/PFC coupling chapter.

Suggested use:

```text
read and audit snippets by stage
convert required snippets into stage-specific .dat files for the target version
avoid blind execution until version and run order are checked
```

## Validation Expectation

For a new machine or before publishing a derived PFC-FLAC coupling template:

1. Validate the minimal `discrete-continuum-baseline` example first.
2. Confirm the continuum baseline solves before particles are generated.
3. Confirm `wall-zone create` or the selected coupling boundary exists before particle insertion.
4. Confirm both continuum and particle outputs are recorded.
5. Treat old binary saves or project files as generated/reference states, not the source of truth.

## How To Materialize A Coupling Example

Copy the selected folder from `scripts/canonical/` into a clean work directory, then execute or audit files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_flac_pfc_case
cp -r scripts/canonical/discrete-continuum-baseline/* my_flac_pfc_case/
```

Then run the staged files in the appropriate Itasca environment.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav`, `.f3sav`, `.prj`, or `.f3prj` files as authoritative examples.
- If upstream licensing is unclear, publish rewritten snippets and retain this README as usage guidance.
