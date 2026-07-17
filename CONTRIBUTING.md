# Contributing

Thanks for improving the PFC Codex skill family. This repository is designed for reusable Agent workflows, so changes should be portable, auditable, and easy to validate.

## Project Structure

- `skills/<skill>/SKILL.md` — the Agent entrypoint. Keep it concise and procedural.
- `skills/<skill>/references/` — theory, command notes, formulas, routing details, and long explanations.
- `skills/<skill>/scripts/` — reusable helper code and templates. Prefer source files over generated outputs.
- `skills/<skill>/examples/` — minimal reproducible examples and README files.
- `references/skill-index.md` — generated inventory of the skill family.
- `scripts/validate_skills.py` — publication-readiness validator.

## Skill Quality Contract

Every public skill should answer:

1. **When to use it** — trigger conditions and boundaries.
2. **Required inputs** — what the Agent must ask for if missing.
3. **Workflow** — ordered steps, routing, and safety checks.
4. **Output contract** — files, tables, figures, or handoff notes expected at completion.
5. **Local contents** — important references, examples, scripts, and templates.
6. **Version caveats** — PFC version assumptions and syntax risks.

## Validation

Before opening a PR, run:

```bash
<PYTHON312>/python.exe scripts/validate_skills.py
```

A PR should not introduce:

- private absolute paths such as `<WINDOWS_PATH>` in public docs;
- GitHub/API tokens, passwords, or license keys;
- generated PFC saves/projects, videos, archives, or large binary outputs;
- local Markdown links that do not resolve;
- helper executables when source code or documented replacement steps are possible.

## Commit Scope

Keep each PR focused: one new skill, one workflow refinement, one validation fix, or one documentation pass. Explain both what changed and why it improves reproducibility.
