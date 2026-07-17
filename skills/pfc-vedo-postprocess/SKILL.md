---
name: "PFC Vedo Postprocess"
description: "Post-process and visualize ITASCA PFC/PFC2D/PFC3D DEM results with vedo. Use this skill whenever the user mentions PFC/DEM post-processing, particle rendering, force chains, crack visualization, displacement or velocity fields, shear-band slices, exported .npz/.vtp/.csv PFC data, or making publication-quality DEM figures and animations with vedo."
globs:
  - "**/pfc_*.npz"
  - "**/*force*chain*.py"
  - "**/*vedo*.py"
  - "**/*.vtp"
---

# PFC x vedo Post-processing Skill

Use this skill to turn PFC/DEM data into reproducible vedo visualizations: particles, contacts/force chains, cracks, vector fields, slices, and time-series animations.

## Scope and Routing

Handle the visualization layer directly:
- Export or load particle/contact/crack/field data.
- Build vedo scenes with reproducible camera, colors, labels, scalar bars, resolution, and output paths.
- Produce publication-quality screenshots, MP4/GIF animations, and reusable Python scripts.

Route these parts elsewhere or ask for upstream details:
- Physical definitions such as Love-Weber stress, fabric tensor, crack classification criteria, or c/phi parameter extraction belong to the user's PFC modeling workflow, not this visualization skill.
- PFC `itasca` object API details can differ by PFC version; verify method names before relying on them.
- AE/moment-tensor beachball interpretation is a separate AE post-processing topic; only render the exported locations/tensors here if already provided.

## Default Workflow

1. Identify the data path.
   - If the user is inside PFC with `itasca`, export a compact snapshot per step.
   - If files already exist, inspect `.npz`, `.csv`, `.vtp`, or folder naming before writing render code.
2. Confirm or infer the schema.
   - Typical arrays: `pos`, `rad`, `disp`, `vel`, `grp`, `c_p1`, `c_p2`, `c_fn`, `c_bonded`, `cr_pos`, `cr_nrm`, `cr_size`, `cr_type`.
   - For 2D models, promote coordinates to 3D by setting `z=0`.
3. Start lightweight.
   - Sample large models (`[::N]`), use low sphere resolution, or render points while tuning the camera and color scale.
   - Switch to full-resolution spheres/tubes only after the view is stable.
4. Make rendering reproducible.
   - Write camera, color maps, scalar ranges, resolution, force sign convention, and output names into a config file or constants block.
   - Use fixed global `vmin/vmax` for animations so colors do not flicker frame to frame.
5. Export useful outputs.
   - Save scripts next to outputs, usually `balls_disp.png`, `force_chain.png`, `cracks.png`, `slice.png`, and `pfc_loading.mp4`.
   - Prefer `offscreen=True` for batch rendering and automation.

## Data Conventions

Use the schema in `references/export-schema.md` when creating or reading snapshots. If the user's files differ, adapt the loader and document the mapping in the script header.

Important checks:
- Units: PFC and vedo both use Cartesian coordinates; preserve SI units unless the user requests scaling.
- Force sign: confirm whether positive normal force means compression or tension for the user's PFC version/export.
- Normals: normalize crack normals before orienting discs.
- Empty arrays: contact/crack arrays may be empty early in a simulation; handle them without crashing.

## Visualization Recipes

Read `references/vedo-recipes.md` when writing code for:
- Particles colored by displacement, velocity, stress, or group.
- Force chains as line/tube objects with width proportional to contact force.
- Cracks as oriented discs colored by tensile/shear class.
- Displacement/velocity vectors as arrows.
- Cut-away or thin-slice shear-band views.

Read `references/animation.md` when making time-series videos.

## Publication Style

Use `references/colormaps.md` for default color choices:
- Sequential magnitudes: `viridis` by default; `jet` only when the user wants high visual contrast.
- Diverging signed values: `coolwarm` or `RdBu`, centered at zero.
- Classes/groups: `Set2` or explicit named colors.

Always include the scientific meaning of colors in scalar bars, legends, titles, filenames, or captions. Make compression/tension and tensile/shear conventions explicit because those are common sources of misinterpretation.

## Common Pitfalls

- Too many particles: sample first, lower `Spheres(..., res=8-12)`, use `Points`, or render offscreen.
- Force-chain colors reversed: verify the contact normal force sign before labeling red/blue.
- Displacement invisible: arrow/deformation vectors usually need a scale factor.
- Animation flicker: fix camera and global scalar range.
- Crack discs point the wrong way: normalize normals and test one obvious crack before batch rendering.
- 2D data fails in vedo: promote `(x, y)` to `(x, y, 0)` and render with `viewup='z'`.

## First Response Pattern

When the user asks for PFC + vedo post-processing, ask only for missing essentials:
- Data source: running PFC/`itasca` session or exported files?
- Target views: particles, force chains, cracks, vectors, slices, animation?
- PFC version and force sign convention if contacts are involved.
- Desired output folder, image resolution, and whether offscreen rendering is needed.

If the repository already contains scripts or snapshots, inspect them first and adapt existing style instead of starting from scratch.

## Required Inputs

Ask for these if missing:

- exported particle/contact/crack/field files and their schema;
- target visualization type: particles, displacement, vectors, slices, force chains, cracks, or animation;
- coordinate units, scalar fields, and color/size mapping rules;
- required output formats such as PNG, SVG, PDF, MP4, or source CSV;
- whether outputs must match a paper style or project style guide.

## Local Contents

- `references/animation.md`: animation workflow and camera conventions.
- `references/colormaps.md`: color mapping and semantic palette rules.
- `references/export-schema.md`: expected export-file schemas.
- `references/vedo-recipes.md`: reusable vedo plotting recipes.

