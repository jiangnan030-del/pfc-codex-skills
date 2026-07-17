# Migration Notes

## Topic-specific conversion checklist
- replace GUI-only plotting steps with stable CSV contracts and public Python scripts
- keep Chapter-22 logic, but remove local-machine assumptions and hard-coded paths
- treat `outfig.py` as the historical seed for `sav -> frames -> gif`
- convert legacy ball/contact text exports into public CSV inputs before plotting
- keep only post-processing-adjacent plugin logic inside this skill
- teach from the smallest runnable example before introducing full PFC workflows

## Shared checklist
- Review `../pfc-skill-pack/references/pfc5-to-pfc6-migration-map.md`.
- Rebuild project files in PFC6.0 when old project metadata is ambiguous.
- Preserve only reproducible outputs in the final skill workflow.
