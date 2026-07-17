---
name: figmirror
description: >
  Use FigMirror whenever the user provides or references a paper/chart figure
  screenshot and wants their own data plotted in that figure's visual style,
  including requests like mirror/copy/match this figure style, make my data look
  like this paper, reproduce this figure with my data, or produce a
  NeurIPS/ICML/ICLR/Nature-style matplotlib figure. It preprocesses cropped or
  uncropped reference figures, runs a Drawer/Reviewer loop, and outputs a
  camera-ready PDF plus a self-contained matplotlib script with an inline DATA
  SECTOR. Do not use for generic charting requests that lack a reference image
  or explicit style-transfer target.
---

# FigMirror (`figmirror`)

Use this skill when the user wants to:
- Transfer the visual style of a top-conference paper figure to their own data.
- Produce a camera-ready matplotlib figure matching a reference screenshot in
  style, not in data.
- Mirror 3D paper-figure references such as surfaces, scatter, trajectories,
  bars, layered waterfalls, or plane projections when the reference or data is
  actually 3D.
- Receive a self-contained `.py` script with editable inline data plus PNG/PDF
  outputs.

## Required Inputs

- A reference figure screenshot (`PNG`/`JPG`). It may include margins, captions,
  neighboring panels, or page text; Stage 0 preprocesses it.
- The user's data in any parseable form: pasted table, CSV, TSV, markdown table, or
  dirty terminal text.
- A working directory for iteration artifacts.

## 3D Insert Gate

Enable `references/three-d-prompting.md` only when the user asks for a 3D
figure, the reference is visibly 3D, or the parsed data requires a 3D encoding
such as `x/y/z`, surfaces, trajectories, layered profiles, closed objects, 3D
small multiples, 3D bars, or plane projections. Do not use this insert to turn
an ordinary 2D task into 3D.

## 3D UCS Surface + Error Lollipop Pattern

Use this pattern when reproducing a paper-style 3D UCS comparison figure where
experimental values are complete over a `(distance, angle)` grid and simulated
values are compared at grid points:

- Encode the experimental UCS field as a smooth `plot_trisurf` surface; color the
  surface by UCS value itself, not by error.
- Encode simulation error as vertical 3D lollipops with `err = sim - exp`; positive
  errors extend upward from the surface and negative errors extend downward below
  the surface.
- Draw negative-error cylinders/spheres before the surface and positive-error
  cylinders/spheres after the surface, with `ax.computed_zorder = False`, so
  below-surface and above-surface semantics are visually preserved.
- Prefer shaded cylinder + sphere glyphs over flat `ax.plot`/`ax.scatter` when a
  publication-grade 3D reference uses volumetric markers; size glyphs from axis
  spans and `BOX_ASPECT` so they remain round in display space.
- Do not label every lollipop when many points are present. Put the overall error
  range in the legend or caption and keep the individual glyphs uncluttered.
- If below-surface error sticks become hidden, lower the surface alpha first; for
  this UCS figure family an alpha around `0.45` is a practical starting point.
- For the finalized Ding-style UCS overlay, keep the left-side Z-axis view at
  `ax.view_init(elev=23, azim=48)` unless the user explicitly asks to rotate it.

## Architecture

- **Python runner** owns UI lifecycle, cancellation, Stage-0 bootstrap, optional
  data-gen, and launching the main Codex process.
- **Codex Orchestrator + Drawer** run in the same top-level Codex process. This
  process owns iteration state, drawing, local floor self-checks, Reviewer audit
  staging, JSON parsing, stop decisions, and final selection.
- **Reviewer** runs as a fresh-context `codex exec` audit with attached
  reference/draft images. Do not expose it to `data.txt`, drawer notes, and source
  code; the Orchestrator still owns the Reviewer invocation and parses its JSON.
- **3D flow** uses the standard Orchestrator, Drawer, fresh-context Reviewer,
  and optional candidate-scoring path for strict reproduction.

## Workflow

1. Read these bundled references from this skill directory:
   - `references/preprocessor.md` for Stage-0 reference crop cleanup.
   - `references/orchestrator-codex.md` for loop wiring and stop conditions.
   - `references/drawer.md` for the Drawer instructions.
   - `references/reviewer.md` for the fresh-context Reviewer instructions.
   - `references/aesthetic-library.md` for the L2 convention library.
   - `references/three-d-prompting.md` only when the 3D insert gate is enabled.
2. Preserve the uploaded reference as `inputs/reference_raw.png`, then run the
   reference preprocessor to write `inputs/reference_clean.png`,
   `inputs/reference_crop_check.png`, and `inputs/reference_crop_report.md`.
3. Echo the parsed data structure before drawing. If the user explicitly asked you
   to make up data or proceed without confirmation, record that in `data_echo.md`
   and continue; otherwise ask for confirmation.
4. When the 3D insert gate is enabled, stage `references/three-d-prompting.md`
   plus `references/three-d/` beside the normal prompts. The router selects
   exactly one mode file: `three-d/style-transfer.md` for ordinary user-data
   figures, or `three-d/strict-reproduction.md` for reproduction, comparison, or
   candidate/control replacement. For strict 3D reproduction runs that need
   quantitative candidate diagnosis, also stage `scripts/score_3d_candidates.py`;
   do not use that scorer for ordinary style transfer. The top-level
   Orchestrator owns final selection and must run the selected mode's
   rendered-image gates before copying any candidate to the final figure.
5. In Codex, the top-level agent acts as both Orchestrator and Drawer. For each
   iter, read `references/drawer.md`, write `figure_iter<N>.py`,
   `img_iter<N>.png`, `notes_iter<N>.md`, and `floor_selfcheck_iter<N>.txt`
   directly in the current Codex process, and verify those files before any
   Reviewer handoff.
6. Launch the Reviewer via the fresh-context `codex exec` path described in
   `references/orchestrator-codex.md`. The Reviewer sees only the reference PNG,
   draft PNG, aesthetic library, optional 3D insert, and prior audit JSON.
7. Stop when the Reviewer returns a passing quality floor and a shipping verdict.
   If the caller supplied `max_iters`, select the best floor-passing close iteration
   when that limit is reached. If the caller enabled auto-until-shipped, keep
   iterating until `ship` or a real blocker.
8. Write final `figure.py`, `figure.png`, `figure.pdf`, `selection.md`, and
   `process.md`.

## Artifact Layout

```text
<workdir>/
  inputs/
    reference_raw.png
    reference_clean.png
    reference_crop_check.png
    reference_crop_report.md
    data.txt
    aesthetic-library.md
  prompts/
    preprocessor.md
    drawer.md
    reviewer.md
    orchestrator-codex.md
    aesthetic-library.md
    three-d-prompting.md  # router, only for 3D runs
    three-d/              # mode files and routed 3D modules, only for 3D runs
  tools/
    score_3d_candidates.py  # optional for strict 3D candidate diagnosis
  figure_iter0.py
  img_iter0.png
  notes_iter0.md
  floor_selfcheck_iter0.txt
  audit_view_0/
    reference_clean.png
    img_iter0.png
    aesthetic-library.md
    three-d-prompting.md  # router, only for 3D runs
    three-d/              # mode files and routed 3D modules, only for 3D runs
  audit_iter0.json
  audit_iter0.stderr
  ...
  figure.py
  figure.png
  figure.pdf
  selection.md
  process.md
```

## Non-Negotiables

- The reference is a style anchor, not a layout-number anchor.
- `inputs/reference_raw.png` is the preserved upload; `inputs/reference_clean.png`
  is the Stage-0 crop used for L1 measurement.
- Every visual choice must be grounded in L1 (reference image) or L2
  (`references/aesthetic-library.md`); L3 opinion is disallowed.
- Do not modify a property on the Reviewer preserve list outside its L1/L2 class.
- Do not expose `data.txt` or source code to the Reviewer audit view.
- Keep the final script self-contained and set `plt.rcParams["pdf.fonttype"] = 42`.

## Local Contents

This distribution keeps the compact FigMirror workflow entirely in this `SKILL.md`. Optional Drawer/Reviewer/preprocessor prompts, three-dimensional routing modules, and scoring helpers are not bundled in this public package; treat the workflow in this file as the authoritative portable contract.

