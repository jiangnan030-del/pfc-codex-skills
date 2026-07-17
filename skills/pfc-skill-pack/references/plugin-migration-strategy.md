# Plugin Migration Strategy

## Goal
Convert the 17 legacy plugin folders into maintainable skill interfaces without making old `.exe` binaries mandatory.

## Three plugin classes

### 1. Geometry import tools
Examples:
- AutoCAD contour extraction
- CAD wall import into PFC3D
- FEM mesh to PFC2D or PFC3D filling

Migration rule:
- Document accepted input geometry such as `dxf`, node lists, element lists, and boundary polylines.
- Replace opaque executables with Python preprocessing scripts where the workflow is inferable.
- Preserve old executables only as optional fallbacks.

### 2. Particle filling and grading tools
Examples:
- graded aggregate generators
- delaunay fill workflows
- overlapping sphere or rigid-disc cluster filling
- riprap and embankment filling models

Migration rule:
- Convert the workflow into parameterized `dat`, FISH, or Python templates.
- Make PSD, porosity, boundary, and random-seed settings explicit.
- Use PFC6.0 chapter assets such as cluster, clump, rblock, and graded-particle examples as the baseline implementation style.

### 3. Checking and boundary search tools
Examples:
- boundary search in 2D or 3D
- model checking utilities
- local or total boundary extraction

Migration rule:
- Treat them as preprocessing utilities.
- If full logic is not recoverable, keep an operational checklist: input files, expected output files, and how those outputs feed later PFC stages.
- Favor independent Python validators over GUI-bound binaries.

## Output contract every migrated plugin note must expose
- purpose
- original source folder
- required input files
- generated output files
- downstream PFC6.0 command-flow handoff
- replacement status: documented only, partially scripted, or fully scripted
