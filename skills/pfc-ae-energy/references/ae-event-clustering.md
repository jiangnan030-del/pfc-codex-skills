# AE Event Clustering

Use this reference when the workflow must move from raw bond-break AE hits to event-level AE catalogs.

## Why Clustering Is Needed

A laboratory AE event may correspond to one microcrack or to several nearby microcracks that connect within a short time. In PFC, raw bond breaks are easy to count, but treating every bond break as an equal-strength independent event can distort event-size statistics and mechanism interpretation.

Use clustering when the requested output includes:

- AE event count rather than raw hit count
- event duration
- event center
- scalar moment or moment magnitude
- T-k or source-type classification
- stage-wise rupture mechanism evolution

## Event Definition

An AE event is a set of microcracks that are close in time and space.

Minimum event fields:

- `event_id`
- `start_time`, `end_time`, and `duration`
- `center_x`, `center_y`, optional `center_z`
- `n_hits` or participating crack count
- stage or strain/stress at representative time
- representative tensor or size proxy
- mechanism label if tensor-derived quantities exist

## Duration Rule

A practical rule from the source document is:

1. Assume rupture extension speed is about half of shear-wave speed.
2. Estimate the time for a shear wave to cross the event action region.
3. Use twice that time as the candidate event duration.
4. During that duration, merge new cracks whose action region overlaps the active event region.
5. If no new cracks satisfy the time-space condition, close the event.

This rule should be parameterized in public templates. Do not hard-code material wave speeds without documenting units and calibration source.

## Merge Criteria

A new microcrack can join an active event when both criteria hold:

- time criterion: `hit_time <= active_event_end_time`
- space criterion: hit action region overlaps the active event action region, or hit distance to event center is within the configured spatial threshold

When a hit is merged:

- update the event center
- update event radius or action region
- update event end time if the action region grows
- accumulate candidate tensor/size information
- preserve the raw hit IDs for traceability

## Representative Tensor Rule

For a rigorous moment-tensor event, do not store a full tensor at every cycle unless the case explicitly requires it. Store the tensor associated with the maximum scalar moment during the event duration.

Recommended event table columns:

```text
event_id,start_time,end_time,duration,representative_time,
center_x,center_y,center_z,n_hits,strain,stress_mpa,
M0,Mw,T,k,source_type,mt_xx,mt_yy,mt_zz,mt_xy,mt_xz,mt_yz
```

For 2D workflows, keep unavailable 3D columns blank or omit them consistently and document the convention.

## Stage Assignment

Assign each event to a loading stage using a stable stage rule:

- by strain thresholds
- by stress fraction of peak
- by saved-state labels such as O/A/B/C/D/E
- by user-provided stage markers

Do not mix raw-hit stages and clustered-event stages without explaining the difference.

## Validation Checks

After clustering, check:

- raw AE hit count is greater than or equal to clustered event count
- every raw hit belongs to zero or one event, depending on whether filtering is allowed
- event duration is nonnegative
- event center lies inside or near the specimen
- moment magnitude or event-size distribution is plausible
- first event time aligns with crack-initiation expectations

## Common Traps

- using a single spatial threshold across models with different particle radii without scaling it
- changing the clustering window between cases that are later compared
- assigning source mechanism from a single hit while reporting a multi-hit event
- losing raw hit IDs, making the event catalog impossible to audit
- claiming laboratory AE event equivalence without documenting clustering assumptions
