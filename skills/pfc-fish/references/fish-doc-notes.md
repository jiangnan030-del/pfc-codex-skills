# FISH Documentation Notes

These notes summarize PFC documentation points checked through `pfc-mcp` for PFC 6.0 command documentation. Treat them as usage guidance, not a replacement for the official manual.

## Core Commands Checked

### `fish define`

- Syntax pattern: `fish define <name> ... end`.
- Purpose: define a FISH function with a valid symbol name.
- Tokens after the function name are arguments.
- Use for reusable calculations, callbacks, histories, exports, and object traversal.

Minimal pattern:

```text
fish define my_value(a, b)
  local c = a + b
  my_value = c
end
```

### `fish callback`

- Purpose: add or remove functions executed in response to callback events.
- Use for per-cycle updates, periodic exports, custom stop checks, particle creation/removal, or state-dependent loading.
- Callback frequency/process filters are available in the command documentation; choose them deliberately to avoid slowing large models.

Safe pattern:

```text
fish define update_measure
  ; compute a scalar or update state
end
fish callback add update_measure <cycle-point-or-event>
```

When refactoring old tutorials, always document:

- when the callback runs
- how often it runs
- which process it depends on
- what global state it mutates

### `fish history`

- Syntax pattern: `fish history [name <label>] <symbol>`.
- Purpose: sample the numeric value returned by a FISH symbol at the model history interval.
- Use for stress, strain, force, displacement, energy, custom damage, AE counts, and other derived scalar quantities.

Pattern:

```text
fish define my_metric
  my_metric = 0.0
end
fish history name 'my_metric' my_metric
```

### `fish list`

- Purpose: list FISH-related quantities.
- Useful keywords include symbols, callbacks, arrays, and parsed code.
- Use during debugging or migration audits to confirm symbols and callbacks have been registered as expected.

### `fish automatic-create`

- Purpose: control whether new global symbols are automatically created when unrecognized valid symbol names appear.
- Public templates should avoid accidental globals. Prefer explicit `local` variables inside functions and deliberate global names for outputs/callback state.

### `fish operator`

- Purpose: define a FISH operator intended to be safe in a multi-threaded environment.
- Use only when a normal FISH function is insufficient and thread-safety assumptions are understood.
- Most teaching and workflow snippets should use `fish define` first.

### `program call`

- Purpose: process one or more data files.
- Use this to split reusable FISH helpers from case-specific `.dat` stages.
- Prefer small helper files with names that reveal their role, for example `fish_metrics.dat`, `fish_callbacks.dat`, or `fish_export.dat`.

## Authoring Guidance

- Put reusable calculations in `fish define` functions.
- Keep callbacks short and documented.
- Use `fish history` for scalar outputs instead of print-only diagnostics.
- Prefer `local` variables inside functions; reserve globals for histories, callbacks, or intentional shared state.
- Avoid tutorial-style omnibus files in production cases; split helper definitions from case setup and solve stages.
- Add a short run-order comment when a FISH helper depends on particles, walls, contacts, or measures that are created later.

## Migration Checklist For Old FISH Snippets

1. Identify every global symbol and decide whether it should become local.
2. Identify every callback and document its cycle point or event.
3. Identify every history and confirm it returns a numeric scalar.
4. Confirm object traversal uses valid PFC 6.0 object lists/intrinsics.
5. Remove print-only checks or convert important values to histories/tables/files.
6. Split reusable functions into helper files called by `program call`.
7. Test small snippets before running full calibration or production solves.
