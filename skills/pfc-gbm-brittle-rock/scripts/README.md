# Scripts

This directory contains public-safe PFC command templates migrated from the GBM + prefabricated-crack biaxial-compression source case.

## Current Assets

```text
canonical/gbm-prefabricated-crack-biaxial/
  stage_01_initial_particle_pack.dat
  stage_02_voronoi_rblock_geometry.dat
  stage_03_export_mineral_geometry.dat
  stage_04_refill_particles_by_mineral_geometry.dat
  stage_05_biaxial_confining_servo.dat
  stage_06_prefabricated_crack_cut.dat
  stage_07_gbm_contact_assignment.dat
  stage_08_trim_specimen.dat
  stage_09_biaxial_loading_monitoring.dat
  fracture_tracking.p2fis
canonical/manifest.json
```

## Migration Policy

- `.dat` and `.p2fis` source templates are preserved and renamed by stage.
- Binary save states, project files, and PDFs are not included.
- The files are templates; verify syntax for the installed PFC version before use.
- Keep any future helper scripts optional and under `scripts/`.

## Suggested Future Helpers

- `materialize_gbm_case.py`: copy staged templates into a new case folder and rewrite case name/seed.
- `audit_gbm_groups.py`: parse exported group/count summaries and check mineral/contact groups.
- `plot_gbm_histories.py`: make stress-strain, crack-count, and energy figures from exported histories.
