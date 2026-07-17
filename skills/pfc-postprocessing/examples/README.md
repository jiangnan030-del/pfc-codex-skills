# Examples

This directory teaches the workflow in three layers.

## 1. `minimal_case`
Audience: someone with no PFC installation and no prior project structure.

What it proves:
- the public scripts can run on stable CSV contracts
- curve, field, and rose outputs can be learned from zero
- the workflow does not depend on the author's local paths

Run:

```bash
python .codex/skills/pfc-postprocessing/scripts/run_demo.py
```

## 2. `pfc6_ch22_case`
Audience: someone who already has PFC6.0 Chapter 22 materials and wants to bridge them into the public workflow.

What it proves:
- Chapter 22 assets can be described in a reusable way
- `outfig.py` logic can be rewritten as a public frame-export template
- save-state workflows can be explained without shipping old `.sav` files

## 3. `plugin_migration_case`
Audience: someone who inherited old PFC5 export tools and wants public, scriptable replacements.

What it proves:
- legacy text exports can be converted into public CSV contracts
- rose diagrams and field plots can be regenerated without old `.exe` tools
- migration is about preserving meaning, not preserving opaque binaries
