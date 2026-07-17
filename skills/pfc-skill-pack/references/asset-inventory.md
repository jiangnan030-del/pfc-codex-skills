# Asset Inventory

This file defines the shared asset model for public PFC skills. It replaces private source-directory references with portable asset classes and inclusion rules.

## MECE Asset Classes

### A. Bundled PFC 6-Compatible Source Assets

Typical files:

- `.dat`
- `.p2fis`
- `.p3fis`
- small required geometry files such as `.dxf`
- small CSV/YAML/JSON configuration examples

Use these as default examples, command-flow skeletons, and validation targets when redistribution is allowed.

Public-packaging rule:

- Store these under a specialist skill's `scripts/` or `templates/` directory.
- Use relative paths only.
- Keep a manifest when the skill bundles many source assets.

### B. Legacy Teaching Code

Typical files:

- older `.dat`, `.p2dat`, `.p3dat`
- older project/save files such as `.p2prj`, `.p3prj`, `.p2sav`, `.p3sav`
- older FISH snippets or sidecars

Use these for modeling patterns and command-flow archaeology, but convert them into a PFC 6-compatible interface before calling them reusable.

Public-packaging rule:

- Do not expose private source paths.
- Do not rely on legacy save/project files as authoritative sources.
- Bundle only rewritten or redistributable source files.

### C. Advanced Cases And Legacy Tools

Typical content:

- FLAC coupling workflows
- seepage or dynamics examples
- blasting examples
- CAD/FEM-to-PFC utilities
- old executable helpers with input/output text contracts

Many historical tool folders combine executables, geometry files, text files, docs, and optional PFC command files. A public skill should preserve workflow intent and file contracts rather than hard-bind to old binaries.

Public-packaging rule:

- Treat old executables as optional fallbacks unless fully replaced.
- Prefer Python/FISH/preprocessing scripts when the logic is inferable.
- Document required inputs and generated outputs.

### D. Reference Materials

Typical files:

- videos
- PDFs
- books
- papers
- screenshots

Use these as supporting references only. Do not make them part of the core runtime surface unless licensing and size are appropriate.

Public-packaging rule:

- Deduplicate repeated tutorials and repeated documents.
- Cite or summarize rather than bundling large media.

## Skill Routing Summary

- Foundation layer: basics, FISH, contact models.
- Workflow layer: `pfc-workflow`.
- Standard-test/template layer: `pfc-standard-tests`.
- Calibration layer: servo calibration and automated calibration guidance.
- Advanced physics layer: fluid coupling, FLAC coupling, dynamics.
- Geometry/preprocessing layer: CAD import and plugin replacement workflows.
- Output/reporting layer: `pfc-postprocessing` and `pfc-ae-energy`.

## Inclusion Rules

Bundle:

- minimal source files needed to reproduce a workflow
- small templates and configuration files
- helper scripts that are deterministic and documented

Do not bundle by default:

- binary save states
- generated plots/results
- private project metadata
- large media files
- black-box executables unless licensing and purpose are explicit
