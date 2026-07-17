# Full Code Map for PFC 6.0

This file is now the code index, not the code dump.

Use it to route to the right full-code reference:

- `source-code-boundary-servo-pfc6.md`
  - blocks `03` to `04`
  - particle-expansion stress control and wall-motion / ball-mill example
- `source-code-meta-examples-pfc6.md`
  - blocks `01` to `02`
  - skill frontmatter example and overview flowchart
- `source-code-particle-assemblies-pfc6.md`
  - blocks `05` to `08`
  - ball / clump / rblock construction, geometry regrouping, zone-to-rblock,
    and Voronoi-like regrouping
- `source-code-reliability-scaling-pfc6.md`
  - blocks `09` to `14`
  - initial-state stop logic, `contact` vs `cmat`, direct current-contact
    assignment, callback-based future-contact assignment, and loading-rate
    control
- `source-code-fish-parameter-extraction-pfc6.md`
  - blocks `15` to `23`
  - modulus, Poisson ratio, peak metrics, `sigma_ci`, crack tracking, and
    particle-average stress

## Load rule

- If the user wants all code for one topic, load only the matching split file.
- If the user wants a full migration audit, load all four split files in order.
- Keep the descriptive references separate:
  - `boundary-servo.md`
  - `particle-assemblies.md`
  - `reliability-and-scaling.md`
  - `fish-parameter-extraction.md`

## Traceability map

| Source blocks | Split file |
| --- | --- |
| `01`-`02` | `source-code-meta-examples-pfc6.md` |
| `03`-`04` | `source-code-boundary-servo-pfc6.md` |
| `05`-`08` | `source-code-particle-assemblies-pfc6.md` |
| `09`-`14` | `source-code-reliability-scaling-pfc6.md` |
| `15`-`23` | `source-code-fish-parameter-extraction-pfc6.md` |
