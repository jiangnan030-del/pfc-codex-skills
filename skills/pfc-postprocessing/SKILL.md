---
name: pfc-postprocessing
description: Teach and run a public, PFC6.0-first post-processing workflow for curves, fields, rose diagrams, animations, and summary tables without depending on the author's local machine layout.
---

# PFC Postprocessing

This skill teaches one thing: how to turn raw PFC output into figures, animations, and tables that another human can understand.

This is a child skill under `pfc-workflow`. It owns standard non-AE
post-processing only. If the request spans calibration, solve control, full
case orchestration, or AE/moment-tensor outputs, stay in `pfc-workflow` and
use this skill only for the standard post-processing branch.

## Non-Negotiable Script-First Rule

Do **not** draw from the prose description alone. Before generating, adapting, or running any post-processing figure, read the actual bundled script that owns that figure route. The prose in this `SKILL.md` is only a router and contract summary; the executable script is the source of truth for columns, units, rcParams, output names, and QA behavior.

Minimum read order for every task:

1. Read `references/script-catalog.md` to choose the closest existing route.
2. Read `scripts/README.md` for the maintained script order and public contract.
3. Read the selected script in `scripts/` before writing or modifying plot code.
4. If adapting a script, preserve its data contract and export contract unless the user explicitly asks to change them.
5. If no script matches, state that no bundled script exists for the requested plot and either ask to add one or create a new script under the case/project, not an undocumented one-off figure.

Random plotting from memory is forbidden because it breaks reproducibility and makes later GitHub users unable to trace how a figure was made.

If you strip away all the jargon, post-processing is just this:

1. export numbers from PFC
2. organize them into stable files
3. turn those files into pictures and summaries
4. make the whole process repeatable

That is the whole game.

## What this skill can produce

- `曲线图`：for example stress-strain curves, with peak annotations
- `场图`：for example displacement, velocity, stress, or porosity maps
- `组构/玫瑰图`：for fracture orientation or contact orientation distributions
- `动画`：frame sequences, GIFs, and optional MP4 exports
- `汇总表`：simple metrics that help compare cases
- `3D UCS 对比图`：experimental UCS smooth surface plus simulated-error lollipops for boundary-distance/inclination grids
- `3D 孔隙率曲面图`：smooth porosity surface from `plotdata_porosity.csv`, with Chinese-traditional sequential colors and publication exports

## Three ways to use this skill

### Path A: you only have this repository
Use `examples/minimal_case` and `scripts/run_demo.py`.
This is the fastest way to learn what each file means and what each script does.

### Path B: you already have PFC-exported CSV files
Use the scripts directly on your own export directory:

- `plot_curves.py`
- `plot_fields.py`
- `plot_rose.py`
- `export_animation_frames.py`
- `export_animation.py`

In the current project-style split, this child skill is also the right place
for standard case scripts such as:

- `postprocess_results_2d.py`
- `plot_contours_2d.py`
- `plot_peak_fields.py`
- `plot_stage_contact_maps.py`
- `gen_force_chain_vtp.py`
- `render_force_chain.py`
- `plot_ucs_3d_surface_lollipop.py`
- `plot_porosity_3d_surface_zhongguo.py`
- replaying native stage exports from saved states

You do not need this author's case structure. You only need the expected input files.

### Path C: you only have `.sav` / `.prj` and want frames first
Read `references/animation-workflow.md` and use the template logic from
`scripts/pfc_sav_to_frames_template.py`.
The template is a public rewrite of the chapter-22 `outfig.py` idea:
restore save states, export bitmaps, then assemble them into a GIF.

## Five-minute quickstart

Run the public demo:

```bash
python .codex/skills/pfc-postprocessing/scripts/run_demo.py
```

Then inspect:

- `examples/demo_outputs/figures`
- `examples/demo_outputs/animations`
- `examples/demo_outputs/tables`

If you understand what those three directories contain, you already understand the backbone of this skill.

## Input files, in plain language

### `stress_strain.csv`
This is the whole specimen speaking as one object.
It answers: how hard did the specimen resist, and when did it peak or soften?

### `plotdata_ball_fields*.csv`
This is particle-level motion data.
It answers: where are particles moving, and how strongly?

### `plotdata_stress*.csv`
This is a grid or measurement-based stress field.
It answers: where is the specimen carrying high stress?

### `plotdata_porosity*.csv`
This is a grid of looseness or compactness.
It answers: where is the material opening up or densifying?

### `plotdata_fracture_orientations.csv`
This is a direction list.
It answers: which way cracks prefer to grow?

### frame images such as `jieguo_1.png`
These are snapshots in time.
They answer: how did the scene evolve, step by step?

## Scripts

Always choose scripts through `references/script-catalog.md`, then read the script before use. The quick router is:

| User asks for | Read and use | Must not skip |
| --- | --- | --- |
| stress-strain or global curve | `scripts/plot_curves.py` | `stress_strain.csv` contract and peak-summary output |
| displacement/velocity/stress/porosity fields | `scripts/plot_fields.py` | actual accepted column aliases and SciPy dependency |
| fracture/contact rose diagram | `scripts/plot_rose.py` | accepted angle column names and 0-180 degree folding |
| unordered frame images | `scripts/export_animation_frames.py` | filename sorting and `frames_manifest.csv` |
| GIF/MP4 from ordered frames | `scripts/export_animation.py` | `frame_*.png` input requirement |
| PFC `.sav` to bitmap frames | `scripts/pfc_sav_to_frames_template.py` | PFC Python environment requirement |
| legacy ball/contact exports | `scripts/convert_legacy_ball_export.py`, `scripts/convert_legacy_contact_export.py` | converter output CSV schema |
| Nature displacement vectors | `scripts/plot_nature_ball_displacement_vectors.py` | six-stage CSV naming and shared colour scale |
| Nature velocity vectors | `scripts/plot_nature_ball_velocity_vectors.py` | velocity unit conversion and six-stage CSV naming |
| 3D porosity surface | `scripts/plot_porosity_3d_surface_zhongguo.py` | `plotdata_porosity.csv` columns and export suffixes |
| 3D UCS surface/lollipop | `scripts/plot_ucs_3d_surface_lollipop.py` plus `references/ucs-3d-surface-lollipop.md` | inline `DATA` block and lollipop grammar |
| public demo/smoke test | `scripts/run_demo.py` | generated example outputs under `examples/demo_outputs` |

Common arguments for scripts using `_common.make_argument_parser` are `--input-dir`, `--output-dir`, `--case-name`, and `--stage`. Script-specific arguments are documented in `references/script-catalog.md` and in each script's `argparse` block.

## Public rules

- Never hard-code the author's local absolute paths.
- Treat data contracts as the main interface, not project-specific folder names.
- Prefer CSV + Python + reproducible image outputs over GUI-only manual actions.
- Keep old `.exe` tools as historical references only; do not make them mandatory.

If the request also mentions AE, energy, source mechanisms, or moment tensors,
hand that branch back to `pfc-ae-energy` through the parent `pfc-workflow`
skill instead of duplicating the logic here.

## Where the teaching examples come from

- `examples/minimal_case` is a public, simplified abstraction of the workspace `pfc_2d` plotting workflow.
- `examples/pfc6_ch22_case` explains how to bridge from PFC6.0 Chapter 22 post-processing assets.
- `examples/plugin_migration_case` shows how old plugin-like exports become stable CSV inputs for public scripts.



## PFC GUI native stage exports

Use these notes when the user asks for PFC GUI/native screenshots from saved
stages. These exports require an active PFC GUI bridge and should be run from
inside PFC, for example through the websocket bridge with `itasca.command(...)`.

### Ball displacement magnitude screenshots

For displacement magnitude, do **not** rely on the current plot if the user has
not explicitly prepared it. Create a fresh ball plot for each restored save and
color balls by the vector attribute `displacement`; in PFC this defaults to
magnitude unless another quantity is supplied. This is the verified PFC6.0
syntax:

```python
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

stages = [
    ("stage_a", "stage_A_ball_displacement_mag.png", "stage_A_ball_displacement_mag"),
    ("stage_b", "stage_B_ball_displacement_mag.png", "stage_B_ball_displacement_mag"),
    ("stage_c", "stage_C_ball_displacement_mag.png", "stage_C_ball_displacement_mag"),
    ("stage_d", "stage_D_ball_displacement_mag.png", "stage_D_ball_displacement_mag"),
    ("peak", "stage_peak_ball_displacement_mag.png", "stage_peak_ball_displacement_mag"),
    ("final", "stage_final_ball_displacement_mag.png", "stage_final_ball_displacement_mag"),
]

for save_name, filename, plot_name in stages:
    it.command(f"model restore '{save_name}'")
    it.command(f"plot create '{plot_name}'")
    it.command("plot clear")
    it.command("plot view extent (-0.025,-0.025) (0.025,0.025)")
    it.command('plot item create ball active on color-by vector-attribute "displacement" color-options scaled ramp rainbow minimum automatic maximum automatic legend active on')
    it.command(f"plot export bitmap filename '{filename}' size 1600 1200")
```

Do not use plain `plot export bitmap` for displacement unless the current GUI
plot is known to be the correct displacement plot; otherwise it may export a
ball/default/fracture plot with the wrong item settings.

### Ball displacement vector screenshots

For displacement **vector/arrow** screenshots that the user configured in the
PFC GUI, use the same current-template rule as fracture exports: preserve the
current GUI plot exactly. Do **not** create, clear, or modify the plot after the
user has prepared the vector view.

Verified workflow:

```python
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

# Optional audit export of the current GUI vector plot.
it.command("plot export bitmap filename 'manual_current_ball_displacement_vector.png' size 1600 1200")

stages = [
    ("stage_a", "stage_A_ball_displacement_vector.png"),
    ("stage_b", "stage_B_ball_displacement_vector.png"),
    ("stage_c", "stage_C_ball_displacement_vector.png"),
    ("stage_d", "stage_D_ball_displacement_vector.png"),
    ("peak", "stage_peak_ball_displacement_vector.png"),
    ("final", "stage_final_ball_displacement_vector.png"),
]

for save_name, filename in stages:
    it.command(f"model restore '{save_name}'")
    it.command(f"plot export bitmap filename '{filename}' size 1600 1200")
```

Use the explicit ball displacement magnitude workflow above only when the user
wants scalar displacement-coloured balls or has not manually prepared a vector
plot. For GUI vector arrows, current-template export is safer because arrow
shape, scaling, legend, and glyph density are GUI style choices.

### Ball velocity vector screenshots

For velocity **vector/arrow** screenshots that the user configured in the PFC
GUI, use the same current-template workflow as displacement-vector and fracture
exports. Preserve the current GUI plot exactly; do **not** create, clear, or
modify the plot after the user has prepared the vector view.

Verified workflow:

```python
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

# Optional audit export of the current GUI velocity-vector plot.
it.command("plot export bitmap filename 'manual_current_ball_velocity_vector.png' size 1600 1200")

stages = [
    ("stage_a", "stage_A_ball_velocity_vector.png"),
    ("stage_b", "stage_B_ball_velocity_vector.png"),
    ("stage_c", "stage_C_ball_velocity_vector.png"),
    ("stage_d", "stage_D_ball_velocity_vector.png"),
    ("peak", "stage_peak_ball_velocity_vector.png"),
    ("final", "stage_final_ball_velocity_vector.png"),
]

for save_name, filename in stages:
    it.command(f"model restore '{save_name}'")
    it.command(f"plot export bitmap filename '{filename}' size 1600 1200")
```

Use explicit plot creation only for scalar velocity-magnitude ball plots. For GUI
velocity arrows, current-template export preserves the user's arrow scale,
legend, glyph density, and color mapping.

### Contact force-chain screenshots

For contact force-chain screenshots that the user configured in the PFC GUI,
preserve the current GUI plot exactly. Do **not** create, clear, or modify the
plot after the user has prepared the contact force-chain view. This keeps the
user's contact item settings, force-chain thickness, colour mapping, legend, and
filtering intact.

Verified current-template workflow:

```python
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

# Optional audit export of the current GUI contact force-chain plot.
it.command("plot export bitmap filename 'manual_current_contact_forcechain.png' size 1600 1200")

stages = [
    ("stage_a", "stage_A_contact_forcechain.png"),
    ("stage_b", "stage_B_contact_forcechain.png"),
    ("stage_c", "stage_C_contact_forcechain.png"),
    ("stage_d", "stage_D_contact_forcechain.png"),
    ("peak", "stage_peak_contact_forcechain.png"),
    ("final", "stage_final_contact_forcechain.png"),
]

for save_name, filename in stages:
    it.command(f"model restore '{save_name}'")
    it.command(f"plot export bitmap filename '{filename}' size 1600 1200")
```

Use scripted `plot item create contact ...` only when the user has not prepared a
GUI force-chain template or explicitly asks for a reproducible command-created
style. When using the user's GUI view, current-template export is the safe path.

### Ball + fracture screenshots

For combined ball + fracture screenshots where the user has configured both Ball
and Fracture items in the PFC GUI, preserve the current GUI plot template exactly.
Do **not** run `plot create`, `plot clear`, or `plot item modify`, because those
commands can reset ball styling and fracture `DFN Name` coloring. This workflow is
for publication-style overlays where balls provide specimen context and fractures
show `crack_tension` / `crack_shear` or other DFN categories.

Verified current-template workflow:

```python
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

# Optional audit export of the currently configured GUI ball+fracture plot.
it.command("plot export bitmap filename 'manual_current_balls_fractures.png' size 1600 1200")

stages = [
    ("stage_a", "stage_A_balls_fractures.png"),
    ("stage_b", "stage_B_balls_fractures.png"),
    ("stage_c", "stage_C_balls_fractures.png"),
    ("stage_d", "stage_D_balls_fractures.png"),
    ("peak", "stage_peak_balls_fractures.png"),
    ("final", "stage_final_balls_fractures.png"),
]

for save_name, filename in stages:
    it.command(f"model restore '{save_name}'")
    it.command(f"plot export bitmap filename '{filename}' size 1600 1200")
```

Important combined-export rules:

- Use this only after the user confirms the GUI template has already been set.
- Preserve the current plot exactly; do not create or clear the plot.
- Do not attempt command-side `Fracture -> Color By -> DFN Name` setup in PFC2D
  6.0. It is unreliable and can produce parser errors such as bad conversion of
  `dfn` parameters.
- Command-created fallback is acceptable only when the user asks for a rough
  reproducible overlay and does not need exact GUI `DFN Name` styling:
  `plot item create ball active on` plus `plot item create fracture active on`.
  Treat this as a fallback, not the paper-figure route.

### Fracture / DFN Name screenshots

For fracture screenshots where the user has set `Fracture -> Color By -> DFN
Name` in the GUI, preserve the current GUI plot template exactly. Do **not** run
`plot create`, `plot clear`, or `plot item modify`, because those commands reset
the GUI-selected `DFN Name` coloring and display controls. The verified workflow
from the `Intact` case is to restore each save and export the current plot only:

```python
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

# Optional audit export of the currently configured GUI fracture plot.
it.command("plot export bitmap filename 'manual_current_fractures.png' size 1600 1200")

stages = [
    ("stage_a", "stage_A_fractures.png"),
    ("stage_b", "stage_B_fractures.png"),
    ("stage_c", "stage_C_fractures.png"),
    ("stage_d", "stage_D_fractures.png"),
    ("peak", "stage_peak_fractures.png"),
    ("final", "stage_final_fractures.png"),
]

for save_name, filename in stages:
    it.command(f"model restore '{save_name}'")
    it.command(f"plot export bitmap filename '{filename}' size 1600 1200")
```

Important fracture export rules:

- If the user wants `DFN Name` coloring (`crack_tension`, `crack_shear`, etc.),
  ask them to set it in the GUI first, then export using the current-template
  workflow above.
- Do **not** attempt to set `DFN Name` with commands like `plot item modify 1
  color-by dfn name ...`; PFC6.0 can reject or silently normalize these forms,
  and they do not reliably preserve the GUI `DFN Name` style.
- Do **not** invent missing DFNs. Check the model data first if the user claims
  only tensile or only shear cracks are present.
- If the user wants only one DFN visible and has not configured the GUI, use the
  GUI display controls when possible; command-side display toggles should be a
  last resort and must match actual DFN names.

## Nature-style displacement vector source data and plotting

When the user asks to export displacement vector data and draw a Nature-style
figure, follow the `nature-figure` skill contract first. If the backend has not
been selected, ask `Python or R?` and stop. Once Python is selected, keep all
figure rendering in Python/matplotlib.

### Export source data from PFC saves

Export one CSV per stage from PFC. Columns are model units in metres unless a
post-processing script adds `_mm` columns.

```python
import csv
import math
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

stages = [
    ("A", "stage_a"),
    ("B", "stage_b"),
    ("C", "stage_c"),
    ("D", "stage_d"),
    ("peak", "peak"),
    ("final", "final"),
]

for label, save_name in stages:
    it.command(f"model restore '{save_name}'")
    rows = []
    for b in it.ball.list():
        p = b.pos()
        d = b.disp()
        dx = float(d.x())
        dy = float(d.y())
        rows.append([
            int(b.id()), float(p.x()), float(p.y()),
            dx, dy, math.sqrt(dx * dx + dy * dy), float(b.radius())
        ])
    out = case / f"plotdata_ball_displacement_arrows_stage_{label}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "x", "y", "disp_x", "disp_y", "disp_mag", "radius"])
        w.writerows(rows)
```

Package these CSV files into an Excel workbook for source data:

```python
from pathlib import Path
import pandas as pd

case = Path("<case-dir>")
stages = ["A", "B", "C", "D", "peak", "final"]
out = case / f"{case.name}_displacement_vector_source_data.xlsx"
summary = []
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    for stage in stages:
        df = pd.read_csv(case / f"plotdata_ball_displacement_arrows_stage_{stage}.csv")
        for col in ["x", "y", "disp_x", "disp_y", "disp_mag", "radius"]:
            df[col + "_mm"] = df[col] * 1000.0
        df.to_excel(writer, sheet_name=f"stage_{stage}", index=False)
        summary.append({
            "stage": stage,
            "n_balls": len(df),
            "max_disp_mm": df["disp_mag_mm"].max(),
            "mean_disp_mm": df["disp_mag_mm"].mean(),
            "p95_disp_mm": df["disp_mag_mm"].quantile(0.95),
        })
    pd.DataFrame(summary).to_excel(writer, sheet_name="summary", index=False)
```

### Python Nature-style plotting

Use or adapt the project script `plot_nature_ball_displacement_vectors.py`.
Expected inputs:

- `plotdata_ball_displacement_arrows_stage_A.csv`
- `plotdata_ball_displacement_arrows_stage_B.csv`
- `plotdata_ball_displacement_arrows_stage_C.csv`
- `plotdata_ball_displacement_arrows_stage_D.csv`
- `plotdata_ball_displacement_arrows_stage_peak.csv`
- `plotdata_ball_displacement_arrows_stage_final.csv`

Run:

```bash
python plot_nature_ball_displacement_vectors.py <case-dir> --thin 2
```

Expected outputs:

- `<case-dir>/nature_ball_displacement_vectors.png`
- `<case-dir>/nature_ball_displacement_vectors.svg`
- `<case-dir>/nature_ball_displacement_vectors.pdf`
- `<case-dir>/nature_ball_displacement_vectors.tiff`

Figure defaults to a six-panel, shared-colour-scale quiver layout in millimetres.
Keep SVG text editable (`svg.fonttype = none`) and PDF text embedded as TrueType
(`pdf.fonttype = 42`). Export TIFF at 600 dpi for journal submission.


## Nature-style velocity vector source data and plotting

When the user asks for a Nature-style velocity vector figure, follow the same
`nature-figure` backend rule as displacement vectors: if Python/R has not been
selected, ask first; once Python is selected, keep all figure rendering in
Python/matplotlib.

### Export source data from PFC saves

Export one CSV per stage from PFC. Position/radius are in metres; velocity is in
model velocity units, normally metres per second. Convert to `mm/s` in Python for
paper-style axes and colour bars.

```python
import csv
import math
import itasca as it
from pathlib import Path

case = Path(r"<case-dir>")
it.command(f"program directory '{case.as_posix()}'")

stages = [
    ("A", "stage_a"),
    ("B", "stage_b"),
    ("C", "stage_c"),
    ("D", "stage_d"),
    ("peak", "peak"),
    ("final", "final"),
]

for label, save_name in stages:
    it.command(f"model restore '{save_name}'")
    rows = []
    for b in it.ball.list():
        p = b.pos()
        v = b.vel()
        vx = float(v.x())
        vy = float(v.y())
        rows.append([
            int(b.id()), float(p.x()), float(p.y()),
            vx, vy, math.sqrt(vx * vx + vy * vy), float(b.radius())
        ])
    out = case / f"plotdata_ball_velocity_arrows_stage_{label}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "x", "y", "vel_x", "vel_y", "vel_mag", "radius"])
        w.writerows(rows)
```

Package these CSV files into an Excel workbook for source data:

```python
from pathlib import Path
import pandas as pd

case = Path("<case-dir>")
stages = ["A", "B", "C", "D", "peak", "final"]
out = case / f"{case.name}_velocity_vector_source_data.xlsx"
summary = []
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    for stage in stages:
        df = pd.read_csv(case / f"plotdata_ball_velocity_arrows_stage_{stage}.csv")
        for col in ["x", "y", "radius"]:
            df[col + "_mm"] = df[col] * 1000.0
        for col in ["vel_x", "vel_y", "vel_mag"]:
            df[col + "_mm_s"] = df[col] * 1000.0
        df.to_excel(writer, sheet_name=f"stage_{stage}", index=False)
        summary.append({
            "stage": stage,
            "n_balls": len(df),
            "max_vel_mm_s": df["vel_mag_mm_s"].max(),
            "mean_vel_mm_s": df["vel_mag_mm_s"].mean(),
            "p95_vel_mm_s": df["vel_mag_mm_s"].quantile(0.95),
        })
    pd.DataFrame(summary).to_excel(writer, sheet_name="summary", index=False)
```

### Python Nature-style plotting

Use or adapt `plot_nature_ball_velocity_vectors.py`. It mirrors the displacement
vector figure script but reads velocity CSVs and labels the shared colour scale
as velocity magnitude in `mm/s`.

Expected inputs:

- `plotdata_ball_velocity_arrows_stage_A.csv`
- `plotdata_ball_velocity_arrows_stage_B.csv`
- `plotdata_ball_velocity_arrows_stage_C.csv`
- `plotdata_ball_velocity_arrows_stage_D.csv`
- `plotdata_ball_velocity_arrows_stage_peak.csv`
- `plotdata_ball_velocity_arrows_stage_final.csv`

Run:

```bash
python plot_nature_ball_velocity_vectors.py <case-dir> --thin 2
```

Expected outputs:

- `<case-dir>/nature_ball_velocity_vectors.png`
- `<case-dir>/nature_ball_velocity_vectors.svg`
- `<case-dir>/nature_ball_velocity_vectors.pdf`
- `<case-dir>/nature_ball_velocity_vectors.tiff`

If the script is not present, create it by adapting
`plot_nature_ball_displacement_vectors.py`: replace displacement columns
`disp_x/disp_y/disp_mag` with `vel_x/vel_y/vel_mag`, convert velocity to
`mm/s`, update labels to `Velocity magnitude (mm/s)`, and save to the
`nature_ball_velocity_vectors` prefix. Keep SVG text editable and TIFF at
600 dpi.


## 3D UCS surface + simulated-error lollipops

Use this workflow when the user wants a Figure-30-style 3D comparison of UCS over boundary distance and inclination angle.
The learned grammar is strict:

- X = boundary distance `d` in mm; Y = inclination `beta` in degrees; Z = UCS in MPa.
- Experimental UCS is the complete continuous field and must be drawn as a smooth surface.
- The surface color maps the experimental UCS value itself, not the error.
- Do not use SciPy. Smooth the surface with `matplotlib.tri.Triangulation`, `CubicTriInterpolator(kind="geom")`, and `UniformTriRefiner().refine_field(..., subdiv=4)`.
- Simulated UCS is sparse and must be drawn as red lollipop error sticks in the same 3D axes.
- Each lollipop tail is anchored on the experimental surface value at the same `(d, beta)` point.
- Each lollipop head is at `experimental + amplified_error`; positive `sim - exp` points upward, negative points downward.
- Keep the lollipops uniformly saturated red; do not map lollipop color to error.
- If errors are too small to see, scale the longest stick to `STICK_MAX_FRAC` of the z-axis span; expose `AMP_OVERRIDE`, where `1.0` forces true scale.
- Force discrete marks on top with `ax.computed_zorder = False`, surface `zorder=1`, sticks `zorder=10`, balls `zorder=20`, labels `zorder=30`, and `depthshade=False`.
- Nature-style export must include editable-text SVG as the primary output, plus PNG and PDF.

Reusable files:

- Prompt/reference contract: `references/ucs-3d-surface-lollipop.md`
- Script template: `scripts/plot_ucs_3d_surface_lollipop.py`

Run the template from the target output directory:

```bash
python .codex/skills/pfc-postprocessing/scripts/plot_ucs_3d_surface_lollipop.py
```

The template has inline example data. For project-specific updates, edit only the top `DATA` block and constants `ERR_AS_PERCENT`, `STICK_MAX_FRAC`, and `AMP_OVERRIDE` unless the figure grammar itself changes.

Expected outputs:

- `figure.svg` primary vector output with editable/searchable text
- `figure.png` 300 dpi preview
- `figure.pdf` vector PDF

The script prints a self-check line with the amplification factor, error range, and number of simulated comparison points. Treat this as part of the output audit.

## Common mistakes

- Missing `stress_strain.csv` and expecting a curve plot anyway
- Using the wrong column names and assuming the script will guess everything
- Feeding unordered frame files into animation export
- Forgetting that a rose diagram needs angles, not screenshots
- Thinking “I have a `.sav` file” means “I already have post-processing data”

If the user says “I do not know where to start,” always start with `run_demo.py`.

## Local Contents

- `references/script-catalog.md`: first-stop route map generated from the actual Python scripts; read this before selecting a plotting route.
- `references/data-contract.md`: stable CSV contracts and required column meanings.
- `references/animation-workflow.md`: `.sav`/frame/GIF bridge workflow.
- `references/plugin-migration.md`: migration notes for legacy plugin-like exports.
- `references/ucs-3d-surface-lollipop.md`: strict grammar for UCS surface plus error lollipops.
- `examples/`: minimal, animation, and PFC6 chapter-style post-processing cases for smoke tests.
- `scripts/`: executable Python/PFC post-processing helpers; these are the source of truth for plot generation.
- Use this skill for non-AE figures and route AE-specific analysis to `pfc-ae-energy`.

