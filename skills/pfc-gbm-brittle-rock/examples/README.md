# Example Cases

The runnable-style templates for this skill are under `../scripts/canonical/gbm-prefabricated-crack-biaxial/`.

## Migrated GBM + Prefabricated-Crack Biaxial Case

Recommended run order:

```text
stage_01_initial_particle_pack.dat
stage_02_voronoi_rblock_geometry.dat
stage_03_export_mineral_geometry.dat
stage_04_refill_particles_by_mineral_geometry.dat
stage_05_biaxial_confining_servo.dat
stage_06_prefabricated_crack_cut.dat
stage_07_gbm_contact_assignment.dat
stage_08_trim_specimen.dat
stage_09_biaxial_loading_monitoring.dat
```

`stage_09_biaxial_loading_monitoring.dat` calls:

```text
fracture_tracking.p2fis
```

## Materialization Pattern

Copy the canonical case folder into a working case directory, then run it inside the target PFC environment after syntax review.

```bash
mkdir -p my_gbm_case
cp -r ../scripts/canonical/gbm-prefabricated-crack-biaxial/* my_gbm_case/
```

## Validation Checklist

Before trusting results, check:

- all stages run in order and produce expected save states
- mineral groups exist after stage 4
- confinement reaches target stress in stage 5
- crack geometry removes the intended slit in stage 6
- `linearpbond` and `smoothjoint` contacts both exist after stage 7
- fracture callback is active in stage 9
- histories record stress, strain, crack counts, energy terms, and AE-like increments

## Publication Notes

- Do not publish large generated save states as part of the skill.
- If figures are needed, route plotting to `pfc-postprocessing` or `pfc-ae-energy`.
- If the crack counts are interpreted as AE, state that they are crack-increment proxies unless calibrated into AE events.
