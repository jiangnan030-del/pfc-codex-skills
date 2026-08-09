# pfc-code knowledge base adapter

This directory integrates [`jiangnan030-del/pfc-code`](https://github.com/jiangnan030-del/pfc-code) as an **external, pinned, queryable evidence corpus** for `pfc-workflow`.

It deliberately does **not** copy upstream `.p2dat`, `.p3dat`, `.fis`, `.py`, or project files into this MIT repository.

## Why this integration mode

- The upstream repository is useful: it contains paired PFC2D/PFC3D examples, tutorials, verification cases, Python integrations, thermal cases, and coupling inputs.
- At the reviewed commit, the upstream root did not expose a `LICENSE` file. Metadata, links, hashes, and independently derived modeling rules can be stored here, but source files should not be vendored or relicensed until rights are confirmed.
- A pinned catalog gives Agents reproducible evidence paths without pretending that example files are authoritative documentation.
- PFC command syntax is version-sensitive. The target-version documentation or `pfc-mcp` remains the final syntax authority.

## Contents

- `source-lock.json` — upstream repository, pinned commit, and content policy.
- `catalog.json` — curated entries tagged by dimension, evidence tier, lifecycle phase, and topic.
- `../../scripts/query_pfc_code_kb.py` — deterministic offline catalog query and validation tool.
- `../../skills/pfc-workflow/references/pfc-code-modeling-standard.md` — modeling rules derived from cross-case patterns.

## Evidence tiers

1. **Tutorials** explain feature semantics and ordering.
2. **Examples** show end-to-end orchestration and stage boundaries.
3. **Verifications** supply numerical/analytical checks for P6.
4. **Python** cases show `itasca`, arrays, and callback automation.
5. **Thermal/coupling** cases show auxiliary-file and multiphysics contracts.

For a high-risk change, use an evidence triad when possible: one tutorial, one end-to-end example, and one verification case. Never promote a single numerical value from an example into a universal default.

## Query

From the repository root:

```bash
python scripts/query_pfc_code_kb.py "parallel bond ucs" --dimension 3d
python scripts/query_pfc_code_kb.py "cmat existing future contacts" --dimension 2d
python scripts/query_pfc_code_kb.py "porosity verification" --kind verification
python scripts/query_pfc_code_kb.py --check
```

The tool is offline: it searches the pinned catalog and prints commit-pinned GitHub links. It does not download or execute upstream content.

## Optional local checkout

If a human or Agent needs to inspect many upstream files locally, clone the pinned source outside tracked content:

```bash
git clone --filter=blob:none https://github.com/jiangnan030-del/pfc-code.git .cache/pfc-code
git -C .cache/pfc-code checkout af774eb322e6c6bef18a56a0a69770e0e82c9bdf
python scripts/query_pfc_code_kb.py --check --local-root .cache/pfc-code
```

Do not commit the checkout. Use it as read-only evidence, then write independent templates that follow the modeling standard and pass version-specific checks.

## Updating the pin

1. Review the new upstream tree and commit history.
2. Re-check whether a license has been added or changed.
3. Update `source-lock.json` and the catalog source commit together.
4. Revalidate every curated path and blob SHA.
5. Run `python scripts/query_pfc_code_kb.py --check`.
6. Review changed examples for syntax/version drift before changing a skill rule.
7. Regenerate the skill index and run `scripts/validate_skills.py`.
