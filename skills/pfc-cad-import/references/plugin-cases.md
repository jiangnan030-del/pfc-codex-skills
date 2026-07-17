# Plugin Cases

Legacy helper applications are preserved as optional workflow history under `scripts/apps/legacy-plugins/`. They are not mandatory public dependencies unless a case explicitly says no native replacement exists.

## Classification

### Geometry Import And Wall Conversion

Use when an external CAD/DXF/STL file becomes PFC walls or geometry sets.

Representative app classes:

- contour/polyline extraction from CAD
- CAD wall to PFC3D wall command conversion
- 3D face to polyline or surface extraction
- CAD polyline to PFC2D wall conversion

Native replacement candidates:

```text
geometry import
geometry list
wall import
wall generate
geometry export
```

### Particle Filling

Use when a CAD/FEM region is filled with balls, overlapping spheres, clumps, or rigid blocks.

Representative app classes:

- 2D Delaunay or retreat/backfill particle filling
- 2D gradation-controlled filling
- 3D overlapping sphere filling
- finite-element mesh to PFC2D/PFC3D particle commands
- riprap/throwing-stone style fill generation

Native replacement candidates:

```text
ball generate
ball distribute
clump template
clump generate
rblock construct
rblock generate
range geometry-space / geometry-based range filters
```

### Boundary Search And Checking

Use when FEM/CAD mesh boundaries must be checked, filtered, or mapped to PFC objects.

Representative app classes:

- total/local 3D boundary search
- 2D finite-element model checking
- exported node/element table checking
- boundary particle and sliding-surface detection

Native/script replacement candidates:

```text
geometry import
geometry list information
range geometry-based filters
custom Python mesh/topology checkers
PFC FISH or Python export checks
```

### Material Grouping And Microstructure

Use when CAD regions define material groups or mesoscopic cluster regions.

Representative app classes:

- material grouping for complex PFC2D models
- random microstructure polyline to PFC model conversion
- image/feature recognition preprocessing
- cluster shape generation from outlines

Native/script replacement candidates:

```text
geometry group/layer mapping
ball group range geometry-based filters
clump templates from geometry
Python DXF/polyline parsers
```

## App Folder Policy

Each preserved app folder should follow this structure:

```text
scripts/apps/legacy-plugins/<slug>/
  app.exe
  small-example-inputs...
```

Rules:

- Keep `app.exe` only when it is part of the original workflow contract.
- Keep small adjacent inputs that explain how the app is used.
- Do not copy huge generated DXF files or multi-megabyte output dumps as canonical assets.
- Normalize copied filenames to ASCII when original filenames are local-language or encoding-sensitive.
- Document input contract, output contract, and native replacement route before recommending use.

## Migration Rule

Convert each case into:

```text
input contract -> preprocessing step -> PFC 6.0 handoff -> validation check
```

Prefer transparent native PFC or Python replacement scripts for public workflows. Preserve legacy executables only for traceability and reproducibility of old teaching cases.
