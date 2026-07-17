---
name: pfc-modeling-techniques
description: Practical ITASCA PFC 6.0 geotechnical modeling techniques for boundary servo control, particle assembly construction, contact versus cmat assignment, initial-state consistency, loading-rate control, size-effect checks, and FISH-based macro-parameter extraction. Use when the user asks how to build, servo, stabilize, quality-control, or measure a PFC geotechnical model, and especially when they want full PFC 6.0 code rather than a summary.
---

# PFC 6.0 Modeling Techniques

Use this skill for hands-on PFC modeling questions: boundary control, particle
construction, reliability checks, and macro-parameter extraction.

## Load order

1. If the user explicitly wants complete code, load
   `references/source-code-complete-pfc6.md` first.
2. Then load only the focused reference files needed for the task:
   - `references/source-code-meta-examples-pfc6.md`
   - `references/source-code-boundary-servo-pfc6.md`
   - `references/source-code-particle-assemblies-pfc6.md`
   - `references/source-code-reliability-scaling-pfc6.md`
   - `references/source-code-fish-parameter-extraction-pfc6.md`
3. Load the descriptive references only when you need formulas, heuristics, or
   topic framing:
   - `references/boundary-servo.md`
   - `references/particle-assemblies.md`
   - `references/reliability-and-scaling.md`
   - `references/fish-parameter-extraction.md`

## When to use

- choose between rigid-wall servo, flexible boundary servo, and
  particle-expansion stress control
- build specimens with `ball`, `clump`, `rblock`, Voronoi-like blocks, or mixed
  representations
- decide whether a property change belongs in `contact property` or
  `contact cmat`
- keep calibration and engineering models in a consistent initial state
- reduce artifacts from loading rate, poor equilibrium, sparse contacts, or
  size effect
- extract `E`, `nu`, peak strength, crack metrics, or stress-field summaries
  with FISH

## Full code migration rule

When the request is about "all code", "complete migration", "full template", or
"convert the original markdown code to PFC 6.0", do not summarize first.

- `references/source-code-complete-pfc6.md` is the primary artifact
- it is now an index that routes to the split full-code files
- the split files still cover source blocks `01` to `23`
- the split files preserve source order and PFC 6.0 normalization

## PFC 5.x to 6.0 syntax reminders

- `new` -> `model new`
- `res xxx` -> `model restore 'xxx'`
- `cmat default ...` -> `contact cmat default ...`
- `solve aratio 1e-5` -> `model solve ratio-average 1e-5`
- `set fish callback ...` -> `fish callback add/remove ...`
- `hist id ...` -> `fish history name ...`

## Working stance

1. Bring assemblies to a low unbalanced-force state before serious loading or
   bonding.
2. Keep calibration and target models aligned in packing, confinement, size
   scale, and boundary logic.
3. Distinguish current-contact edits from future-contact assignment.
4. Treat loading rate as a numerical control parameter unless the constitutive
   logic is explicitly rate-dependent.
5. Prefer reproducible FISH measurements over visual judgment alone.

## Output contract

For a modeling-technique answer, provide:

- the recommended modeling route and why it fits the geometry or loading path
- the minimum checks needed to verify state quality before calibration
- the key implementation pattern or FISH recipe needed
- the main failure modes that would invalidate the result

## Required Inputs

Ask for these if missing:

- PFC version and target dimension;
- modeling technique needed: particle assembly, boundary servo, FISH extraction, scaling, or reliability check;
- specimen geometry, units, target density/porosity, and boundary assumptions;
- whether the request is explanatory, code-generation, audit, or migration work;
- follow-on route, such as standard test, calibration, post-processing, or report delivery.

## Workflow

1. Identify the modeling-technique category and read the matching `references/` file.
2. Confirm version-sensitive syntax before generating commands.
3. Prefer canonical PFC 6.0 source snippets where available.
4. Keep assumptions explicit and route specialist tasks back to `pfc-workflow` or the relevant child skill.
5. Return a compact handoff with selected technique, commands/templates, risks, and validation checks.

## Local Contents

- `references/particle-assemblies.md`: particle generation and assembly rules.
- `references/boundary-servo.md`: servo-control patterns and checks.
- `references/fish-parameter-extraction.md`: FISH extraction and helper logic.
- `references/reliability-and-scaling.md`: scaling, reliability, and audit notes.
- `references/source-code-*.md`: source-code reference snippets for reuse or migration.

