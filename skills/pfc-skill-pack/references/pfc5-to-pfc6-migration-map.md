# PFC5-to-PFC6 Migration Map

## Why This File Exists

Legacy PFC assets often use mixed file extensions, project formats, saved states, and FISH idioms. This map is the shared checklist every specialist skill should use before claiming PFC 6.0 compatibility.

## 1. File And Project Format Mapping

| Legacy asset | PFC 6-first target | Notes |
| --- | --- | --- |
| `.p2dat` / `.p3dat` | `.dat` | Keep the staged command-flow idea, but normalize file names by function such as `1model.dat`, `2bond.dat`, `3load.dat`, `4export.dat`. |
| `.p2prj` / `.p3prj` | rebuilt `.prj` if needed | Rebuild project references in a fresh PFC 6 project instead of trusting legacy project metadata. |
| `.p2sav` / `.p3sav` | regenerated `.sav` | Save files are version-sensitive; keep old saves as historical references, not authoritative deliverables. |
| mixed FISH sidecars | `.p2fis` / `.p3fis` or inline FISH blocks | Preserve standalone fracture-tracking or callback modules where they help maintenance. |
| old plugin `.exe` | documented optional fallback or replacement script | Prefer a transparent script if the transformation logic is recoverable. |

## 2. Command-Flow Restructuring Rules

- Prefer numbered stages by intent: build, bond, load, export, plot, postprocess.
- Split oversized legacy files when one file mixes specimen generation, loading, export, and plotting.
- Keep a project file only when it improves run reproducibility.
- Use relative paths for includes and external assets.
- Make random seed, dimensions, PSD, porosity, contact properties, and loading rate explicit.

## 3. Save And Project Compatibility Rules

- Do not assume legacy `.sav` files load cleanly across major versions.
- Recreate milestone saves from migrated `.dat` flows whenever possible.
- Keep old saves only as visual references, regression anchors, or source archaeology.
- Public templates should treat saves as generated outputs, not bundled source.

## 4. FISH Migration Checklist

- Recheck callback syntax and event registration.
- Recheck traversal for balls, contacts, walls, clumps, fractures, structures, and geometry sets.
- Recheck history export, map usage, string formatting, and global/local variable behavior.
- Recheck plot export and file output commands.
- Recheck property names for contact models and wall/structure interactions.
- Recheck code that depends on implicit current objects, deprecated keywords, or version-specific property names.

## 5. Plot And Export Normalization

- Prefer CSV, image export, and Python post-processing over GUI-only manual steps.
- Normalize output names by stage and field, for example:
  - `stress_strain.csv`
  - `plotdata_stress_peak.csv`
  - `forcechain_stage_A.vtp`
  - `stage_A_native.png`
- Tie each output to a saved state or stage boundary.

## 6. Migration Acceptance Test

A migrated case is acceptable only when it can answer all of the following:

1. Which source family or original case type did it come from?
2. Which legacy file types were involved?
3. What is the new PFC 6 stage layout?
4. Which outputs are reproducible without manual GUI editing?
5. Which commands or FISH blocks were manually audited for version-specific syntax?
6. Which assets are bundled, external, generated, or intentionally excluded?
7. What license or redistribution note applies to bundled code?
