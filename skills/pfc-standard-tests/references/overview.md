# Overview

## Purpose

`pfc-standard-tests` provides reusable PFC 6.0 templates for common rock and soil mechanics laboratory simulations. Earlier versions of this skill pointed to private local folders. This version embeds the relevant command files and geometry under `scripts/canonical/`, making the skill suitable for transfer or publication.

## Topic Boundary

This skill owns standard mechanical-test setup and interpretation only:

- UCS / uniaxial compression
- Biaxial compression
- Conventional triaxial compression with rigid walls
- Conventional triaxial compression with flexible membrane shells
- Direct shear
- Brazilian splitting
- Three-point bending

It does not own generic PFC installation, calibration automation, fluid coupling, FLAC coupling, advanced AE moment tensor processing, or final publication plotting except where basic stress/force/crack outputs are needed to validate a standard test.

## Bundled Source Set

All source files are stored with relative paths:

- `scripts/canonical/biaxial/`
- `scripts/canonical/ucs/`
- `scripts/canonical/brazilian/`
- `scripts/canonical/direct-shear/`
- `scripts/canonical/three-point-bending/`
- `scripts/canonical/triaxial-rigid/`
- `scripts/canonical/triaxial-flexible-membrane/`

The original source directories were local teaching-case folders. Do not preserve those absolute paths in public documentation. Use the bundled relative folders as the implementation surface.

## Case Flow Summary

### Biaxial Compression

Folder: `scripts/canonical/biaxial/`

- `1chengyang.dat`: create a 2D rectangular particle assembly.
- `2yuya.dat`: preload/compact the assembly.
- `3jiaojiaojie.dat`: add or activate bonded contacts.
- `4weiya.dat`: apply confinement.
- `5jiazai.dat`: monotonic loading.
- `5.1循环加载.dat`: cyclic loading variant.
- `readme.dat`: source note from the teaching case.

Use this when the user asks for confined 2D compression with lateral stress control or cyclic loading.

### UCS / Uniaxial Compression

Folder: `scripts/canonical/ucs/`

- `1chengyang.dat`: 2D rectangular sample creation.
- `2yuya.dat`: preload/settle.
- `3jiaojiaojie.dat`: bond creation.
- `3liewen.dat`: crack-related setup stage.
- `4jialiewen.dat`: add fracture tracking.
- `4xiezai.dat`: unload/release stage.
- `5jiazai.dat`: axial loading to failure.
- `fracture.p2fis`: 2D bond-break to DFN/fragment tracking helper.

Use this as the default 2D bonded-rock compression template.

### Brazilian Splitting

Folder: `scripts/canonical/brazilian/`

- `1chengyang.dat`: circular/disc sample creation.
- `2yuya.dat`: settle/preload.
- `3jiajiaojie.dat`: bond creation.
- `4xiezai.dat`: unload/release stage.
- `5jiazai.dat`: diametral loading.
- `fracture.p2fis`: 2D fracture tracking.

Use this for indirect tensile strength simulation. Expected primary curve is load-displacement or tensile-stress proxy versus displacement/time.

### Direct Shear

Folder: `scripts/canonical/direct-shear/`

- `1chengyang.dat`: shear-box particle assembly.
- `2yuya.dat`: preloading/settling.
- `3jiajiaojie.dat`: bonding.
- `4jiazhouya.dat`: apply normal stress.
- `5jiazai.dat`: horizontal shear loading.
- `fracture.p2fis`: 2D fracture tracking.

Use this when the user needs normal stress, shear displacement, shear force/stress, and post-peak residual behavior.

### Three-Point Bending

Folder: `scripts/canonical/three-point-bending/`

- `11.dxf`: geometry asset used by the case.
- `1chengyang.dat`: base sample creation.
- `2tihuan.dat`: geometry/object replacement stage.
- `3jiajiaojie.dat`: bonding.
- `4addjiazai.dat`: add loading/support boundaries.
- `5jiazai.dat`: bending load stage.
- `fracture.p2fis`: 2D fracture tracking.

Use this for notched beam or beam bending workflows. Check `11.dxf` licensing before public redistribution if the upstream teaching material has restrictions.

### Conventional Triaxial, Rigid Wall

Folder: `scripts/canonical/triaxial-rigid/`

- `1chengyang.dat`: 3D cylindrical sample generation.
- `2yuya.dat`: isotropic compaction/preload.
- `3jiajiaojie.dat`: bonding.
- `4weiya.dat`: confining pressure with rigid wall boundaries.
- `5jiazai.dat`: axial loading.
- `fracture.p3fis`: 3D bond-break fracture tracking.

Use this for a simpler 3D triaxial workflow when membrane realism is not required.

### Conventional Triaxial, Flexible Membrane

Folder: `scripts/canonical/triaxial-flexible-membrane/`

- `1chengyang.dat`: 3D cylindrical sample generation.
- `2yuya.dat`: isotropic compaction/preload.
- `3jiajiaojie.dat`: bonding.
- `4jiarouxing.dat`: create flexible membrane shell and wall-structure interaction.
- `5jiazai.dat`: axial loading with membrane confinement.
- `fracture.p3fis`: 3D fracture tracking.

Use this for more realistic triaxial confinement where radial pressure is applied through shell elements.

## Inclusion Rules

- Keep code assets (`.dat`, `.p2fis`, `.p3fis`, `.dxf`) that are necessary to reproduce the template.
- Do not include `.sav`, `.prj`, binary result states, videos, or PDF tutorials as core runtime assets.
- Rebuild `.sav` states from the staged command files when validating.
- Keep `manifest.json` updated when bundled files change.

## Publication Notes

Before uploading to GitHub:

- Verify that redistribution of the teaching-case code and `11.dxf` is permitted.
- Add a license notice if upstream content has a known license or attribution requirement.
- Remove any remaining absolute paths from documentation.
- Prefer ASCII filenames in new files, but keep original filenames where they are part of the source template lineage.
