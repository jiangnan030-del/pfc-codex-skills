# PFC Skill Pack

This directory is the shared hub for the PFC skill family. It defines repository conventions, shared compatibility references, asset inclusion rules, and plugin replacement policy used by the specialist PFC skills.

The pack is designed for portable publication: use relative paths, include only redistributable source/templates, and avoid private machine paths or local project assumptions.

## Skill Hierarchy

```text
pfc-skill-pack
  └─ pfc-workflow
      ├─ pfc-standard-tests
      ├─ pfc-postprocessing
      └─ pfc-ae-energy
```

`pfc-workflow` remains the total workflow skill. `pfc-skill-pack` is the shared governance and packaging hub.

## Shared Principles

- Prefer PFC 6.0-compatible command flows for public templates unless a skill explicitly targets another version.
- Keep executable helper code in `scripts/` and reusable prompt/document templates in `templates/`.
- Keep package policies, compatibility maps, and catalogs in `references/`.
- Use relative paths for all bundled assets.
- Treat binary save/project states as generated artifacts, not authoritative source.
- Do not make black-box `.exe` files the core implementation of a public skill.
- Every specialist skill should answer: when to use, required inputs, runnable assets, outputs, and PFC-version caveats.

## Contents

- `SKILL.md`: skill entrypoint and routing policy.
- `references/asset-inventory.md`: asset classes and inclusion rules.
- `references/pfc5-to-pfc6-migration-map.md`: compatibility checklist.
- `references/plugin-catalog.md`: taxonomy for legacy plugin/tool workflows.
- `references/plugin-migration-strategy.md`: how to replace or document old tools.
- `scripts/build_skill_index.py`: small helper to list sibling skills.
- `scripts/README.md`: script policy and extension guidance.
- `templates/case-intake.md`: intake form for adding/auditing cases.

## Publication Checklist

Before publishing the skill family:

1. Confirm every skill folder has a valid `SKILL.md`.
2. Confirm public documentation uses relative paths only.
3. Confirm bundled source assets are redistributable or rewritten.
4. Confirm generated outputs, binary saves, videos, and private project files are excluded.
5. Confirm the parent-child relationship is documented in both the parent and child skills.
