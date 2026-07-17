# AE Documentation Notes

These notes summarize PFC 6.0 documentation points checked through `pfc-mcp` for the AE, energy, and moment-tensor route. Treat them as implementation guidance, not a replacement for the official manual.

## FISH Monitoring

### `fish callback`

- Defines FISH functions that run at selected model-cycle points or named events.
- Use this as the preferred hook for bond-break or contact-event monitoring when the target contact model exposes the needed event.
- Verify the exact callback event name in the target PFC version before publishing a final `.p2fis` or `.p3fis` file.
- Keep callback logic lightweight: record event primitives and defer clustering/tensor decomposition to export or Python post-processing when possible.

### `fish history`

- Records a FISH variable or function through time.
- Use for cumulative crack counts, tension/shear crack counts, AE counters, or scalar diagnostics that should be synchronized with stress-strain histories.
- Assign explicit history IDs or names so export scripts can be version-controlled.

### `fish list` and `fish automatic-create`

- Use `fish list` to inspect available FISH symbols while debugging.
- Use `fish automatic-create` intentionally; disable or audit automatic symbol creation in public templates to catch misspelled variables early.

## Histories And Measures

### `model history`

- Records model-level quantities through time.
- Use alongside FISH histories when plotting load stage, timestep, solve progress, or mechanical state.

### `measure create`, `measure history`, and `measure list`

- Measurement regions can track stress, strain rate, porosity, coordination number, position, or radius depending on the region and model state.
- Use measurement histories when the AE workflow needs independent stress/strain or porosity checks.
- Run `model clean` at appropriate points so measurements and contact state are current before export or cycling checks.

## Contacts And Fractures

### `contact list`

- Lists contacts and helps audit whether expected contacts, contact models, and groups exist.
- Use for debugging AE instrumentation, but avoid relying on manual listing for production exports.

### `contact model`, `contact property`, and `contact method`

- `contact model` assigns or replaces the model on existing contacts.
- `contact property` updates properties on existing contacts.
- `contact method` applies model-specific methods, such as bond installation or stiffness-related operations.
- Detailed contact-law choice belongs to `pfc-contact-models`; this skill only records the AE consequences of a validated bonded model.

### `contact cmat`

- CMAT controls how future contacts receive models/properties.
- For AE studies based on bonded materials, define and apply the contact model before enabling AE monitoring, then save a pre-load bonded state.

### `fracture create`, `fracture list`, `fracture export`, and `fracture contact-model`

- Fracture commands support DFN-style fracture objects and fracture export workflows.
- Use fracture objects only when the model explicitly maps microcracks to fracture entities.
- `fracture export` can support external fracture analysis, but raw AE event CSV remains the preferred portable exchange format for this skill.

## Exports

### `history export`

- Exports model and FISH histories to file, table, or screen depending on keywords.
- Use explicit IDs/names and stable file naming for stress-strain and crack-count data.

### `table export`

- Exports table contents to file, generally as x-y pairs.
- Use for simple time-series or intermediate diagnostics; use custom FISH/Python CSV writers for full AE event tables with many columns.

### `data scalar-export`, `data vector-export`, and `data tensor-export`

- Export scalar, vector, or tensor fields for downstream post-processing.
- Useful when AE interpretation needs spatial field context, but do not substitute these field exports for the event-level `ae_events.csv` contract.

### `program call`

- Processes another data file from the current command flow.
- Use to keep AE monitoring, loading, and export stages modular.

## Recommended PFC 6.0 AE Command Pattern

```text
model restore 'bonded'
program call 'fracture-heavy-mt.p2fis'
fish callback add @cache_bond_state -1.0
fish callback add @add_crack event bond_break
fish history id 4 @crack_tension_num
fish history id 5 @crack_shear_num
; load stage commands...
program call 'export-heavy-ae-4export.dat'
```

The exact callback registration syntax and event token must be checked against the installed PFC version before final use.

## Skill Boundary Notes

- Use this skill after the parent workflow has produced a calibrated bonded specimen.
- Use `pfc-contact-models` for contact-law setup and bond installation details.
- Use `pfc-postprocessing` for non-AE field figures.
- Use `pfc-ae-energy` for AE hits/events, macro energy density, moment tensor, source type, and mechanism evolution.
