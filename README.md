<div align="center">

# PFC Codex Skills

**Reusable Agent skills for ITASCA PFC modeling, calibration, post-processing, AE/energy analysis, and publication-quality DEM visualization**

PFC workflow orchestration · PFC 6.0 templates · calibration contracts · ParaView/Python post-processing · AE/energy analysis · GitHub-ready validation

</div>

---

This repository packages the `.codex/skills` skill family as portable Agent skills. The design follows the same separation-of-concerns pattern as `gzh-design-skill`: a short `SKILL.md` entrypoint for each skill, reusable references under `references/`, executable helpers under `scripts/`, examples under `examples/`, and deterministic validation before publication.

## Core Skills

- `pfc-skill-pack` — shared governance, packaging policy, compatibility maps, and asset inclusion rules.
- `pfc-workflow` — the orchestrator for complete PFC projects: planning, preprocessing, calibration, solving, post-processing, V&V, and delivery.
- `pfc-basics` — model lifecycle, domains, particles, walls, clumps, rblocks, groups, and minimal runnable setup.
- `pfc-contact-models` — contact-law selection, CMAT, contact properties, bonding, inheritance, and contact-level validation.
- `pfc-standard-tests` — UCS, Brazilian, biaxial, triaxial, direct shear, and other canonical laboratory test workflows.
- `pfc-servo-calibration` and `pfc-fast-calibration` — manual servo tuning and rapid LPBM/DOE-style micro-parameter calibration.
- `pfc-fish` — FISH functions, callbacks, histories, file IO, maps/tables, and helper refactoring.
- `pfc-postprocessing`, `pfc-vedo-postprocess`, and `pfc-ae-energy` — reproducible exports, plots, 3D visualizations, force chains, crack evolution, AE/energy metrics, and source-mechanism figures.
- `figmirror` and `xxd-data-viz` — figure-style transfer and Chinese traditional-color data visualization support.

See [references/skill-index.md](references/skill-index.md) for the generated skill inventory.

## Directory Structure

```text
.codex/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .gitignore
├── scripts/
│   └── validate_skills.py
├── references/
│   └── skill-index.md
└── skills/
    ├── pfc-skill-pack/
    ├── pfc-workflow/
    ├── pfc-*/
    ├── figmirror/
    └── xxd-data-viz/
```

## Quick Start

Clone or copy this `.codex` folder into an Agent workspace that supports Codex/Claude-style skills, then invoke a skill by name, for example:

```text
Use pfc-workflow to plan a PFC 6.0 UCS calibration workflow.
Use pfc-postprocessing to refresh stress-strain, force-chain, crack, and displacement figures.
Use pfc-ae-energy to run the AE/energy post-processing pipeline after saved-state exports are complete.
```

For project work, start from `pfc-workflow`. It routes specialist subtasks to child skills and keeps the case lifecycle reproducible.

## Publication Rules

- Keep all public documentation portable: use relative paths or placeholders such as `<PFC_CONSOLE_EXE>` and `<CASE_DIR>` instead of private machine paths.
- Do not commit generated `.sav`, `.p2prj`, `.p3prj`, videos, PDFs, archives, private experimental datasets, or binary helper apps.
- Keep executable source in `scripts/`, reusable case contracts in `templates/`, and background theory or command notes in `references/`.
- Prefer PFC 6.0-compatible public templates unless a skill explicitly declares another target version.
- Run the validation loop before pushing to GitHub.

## Validation Loop

Use the E-drive Python requested for this workspace:

```bash
<PYTHON312>/python.exe scripts/validate_skills.py
```

The validator checks required frontmatter, missing local Markdown links, private absolute paths, likely leaked tokens, oversized files, and publication-risk binary assets.

## Notes On Proprietary Software

These skills can describe PFC command flows and include redistributable templates, but they do not grant PFC, FLAC3D, ParaView, or third-party software licenses. Users must configure local executables and valid licenses in their own project environment.
