# Overview

## Purpose

`pfc-fish` provides reusable PFC FISH authoring and refactoring guidance. It is a child skill of `pfc-workflow`; it supplies targeted language, callback, history, IO, and traversal expertise, then hands complete workflow execution back to the parent skill.

## Topic Boundary

This skill owns:

- `fish define` function design and reusable helper organization
- callback registration and callback-state hygiene
- FISH histories for derived scalar metrics
- variables, locals/globals, arrays, maps, matrices, tensors, strings, and vectors
- conditionals, loops, and object traversal
- basic FISH file IO and data import/export helpers
- migration/audit guidance for old FISH snippets

This skill does not own:

- full case lifecycle orchestration
- standard mechanical-test template selection
- servo calibration strategy except for small FISH helper snippets
- coupling physics except FISH helper code used by those skills
- post-processing figure generation
- AE/energy/source-mechanism analysis

## Documentation Enrichment

PFC 6.0 command documentation was queried through `pfc-mcp` while building this skill. The resulting command notes are summarized in `references/fish-doc-notes.md`.

Key checked commands:

- `fish define`
- `fish callback`
- `fish history`
- `fish list`
- `fish automatic-create`
- `fish operator`
- `program call`

## Bundled Source Set

All reusable source files are stored with relative paths:

- `scripts/canonical/fish-basics-pfc6/`
- `scripts/canonical/fish-basics-pfc5-reference/`

Included PFC 6.0 baseline files:

- `1value.dat`: basic value/symbol examples.
- `2xunhuan.dat`: loop examples.
- `3fishcreate_ball.dat`: particle creation through FISH logic.
- `3huidiao.dat`: callback example.
- `4shepizouwei.dat`: random-walk style example.
- `5guitusaipao.dat`: particle/geometry behavior example.
- `6jianduan.dat`: shear-like example logic.

Included legacy reference themes:

- variable definition and assignment
- data types
- custom functions
- conditional branches
- loops and jumps
- interactive IO
- data recording/output
- data reading/application
- map usage
- common FISH standard functions

Legacy `.p2dat` snippets are included as readable references and should be audited before direct use in PFC 6.0.

## Recommended FISH Patterns

### 1. Reusable Function

Use when a value is computed repeatedly or should be reused by histories/callbacks.

```text
fish define metric_name
  local value = 0.0
  metric_name = value
end
```

### 2. Callback Function

Use when the model must update state during cycling.

```text
fish define callback_name
  ; keep callback work small and deterministic
end
fish callback add callback_name <cycle-point-or-event>
```

Always document the callback trigger, frequency, process filter, and mutated state.

### 3. History Function

Use when the model needs a custom scalar output.

```text
fish define custom_history
  custom_history = 0.0
end
fish history name 'custom_history' custom_history
```

### 4. Helper File Split

Use when reusable FISH code should be shared across cases.

```text
program call 'fish_helpers.dat'
program call 'case_setup.dat'
program call 'solve_stage.dat'
```

## Inclusion Rules

- Keep minimal `.dat`, `.p2dat`, and small input `.dat` files needed to understand the workflow.
- Do not bundle generated save states, project metadata, videos, PDFs, or large output dumps as authoritative assets.
- Preserve legacy files as references only when they add coverage not already present in PFC 6.0 examples.
- Keep FISH helper dependencies, run order, and object-existence assumptions explicit.

## Handoff To pfc-workflow

After this skill provides FISH snippets or a helper-file plan, return to `pfc-workflow` for:

- full case directory creation
- standard-test or coupling-skill routing if needed
- solve management
- post-processing route selection
- V&V and delivery
