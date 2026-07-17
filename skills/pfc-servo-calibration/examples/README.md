# Example Cases

This directory documents how to use the bundled servo-control code templates. The actual PFC `.dat` files live in `../scripts/canonical/` so executable code stays under the skill's `scripts` area.

## Directory Layout

```text
scripts/
  canonical/
    manifest.json
    servo-principles/
      1sifu_1.dat
      2sifu_2.dat
      3sifu_3.dat
      3sifu_4.dat
      4sifu_4_jixu.dat
examples/
  README.md
```

## Supported Example Set

### `scripts/canonical/servo-principles/`

Minimal PFC 6.0 examples for force-control and wall-servo ideas.

Suggested learning order:

```text
1sifu_1.dat
2sifu_2.dat
3sifu_3.dat
3sifu_4.dat
4sifu_4_jixu.dat
```

Use the first three files to understand force-to-displacement conversion on small systems. Use `3sifu_4.dat` then `4sifu_4_jixu.dat` to study contact-map stiffness and continued wall servo in a particle assembly.

## Validation Expectation

For a new machine or before publishing a derived servo template:

1. Run `1sifu_1.dat` and confirm the simple two-ball target-force calculation behaves as expected.
2. Run `3sifu_4.dat` to create the particle assembly and save the intermediate state.
3. Run `4sifu_4_jixu.dat` and confirm the wall force history approaches the target without unstable oscillation.
4. Add velocity caps and tolerance checks before using the pattern in a real specimen.
5. Confirm histories are written for target, actual force/stress, boundary velocity, and error.

## How To Materialize A Servo Example

Copy the selected folder from `scripts/canonical/` into a clean PFC work directory, then execute files in the suggested order.

Example shell copy pattern, run from the skill root:

```bash
mkdir -p my_servo_case
cp -r scripts/canonical/servo-principles/* my_servo_case/
```

Then run the staged `.dat` files in PFC 6.0.

## Publication Notes

- `scripts/canonical/manifest.json` records file hashes and sizes for traceability.
- Do not publish generated `.sav` files as authoritative examples.
- If upstream licensing is unclear, publish rewritten servo snippets and retain this README as usage guidance.
