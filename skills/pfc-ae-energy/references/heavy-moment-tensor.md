# Heavy Moment-Tensor Route

Use this route when the workflow must stay consistent with earlier cases that already use cached contact-force and contact-moment based AE inversion, or when the user explicitly asks for moment tensor, scalar moment, moment magnitude, T-k, Hudson plots, or source mechanism.

## What Makes It Heavy

Compared with a lightweight AE-hit workflow, the heavy route adds:

- a pre-break contact-force cache updated before bond failure
- per-event force-change and lever-arm collection
- pseudo or rigorous moment-tensor reconstruction at break/event time
- tensor columns in event exports
- event clustering before source-type interpretation
- larger event arrays and more FISH memory traffic
- slower solve time and higher risk of bridge instability on long runs

## What Stays Comparable

The heavy route preserves direct comparability for:

- `ae_events.csv`
- `ae_clustered_events.csv`
- source maps based on tensor columns
- scalar moment, moment magnitude, and T-k post-processing
- `ae_tk_diamond_cn.*` figures already generated in previous cases

## Minimum Integration Set

To integrate the heavy route into a case, update all pieces together:

1. `fracture-heavy-mt.p2fis`
   - register contact state cache logic
   - register bond-break crack logic
   - record tension/shear counters
   - record strain/stress/position/mode fields
   - record `pbstrain_energy` or equivalent event-size proxy when available
   - export full tensor columns
2. `3load.dat`
   - add histories for total, tension, and shear crack counters
   - save milestone states needed for stage-wise AE interpretation
3. `4export.dat` or `export-heavy-ae-4export.dat`
   - export stress-strain and crack histories
   - call the AE event export function
4. `plot_ae_energy.py`
   - compute clustering, macro energy density, tensor metrics, T-k classification, and figures

If one of these pieces is missing, the AE post-processing chain will be incomplete even if the solve itself succeeds.

## Moment-Tensor Event Rule

For a clustered event, compute or retain the tensor at the representative time with maximum scalar moment. Avoid storing every timestep tensor unless the user explicitly requests waveform-level research output and accepts the memory cost.

Recommended tensor columns:

```text
mt_xx,mt_yy,mt_zz,mt_xy,mt_xz,mt_yz
```

Recommended derived columns:

```text
M0,Mw,T,k,source_type
```

## Practical Warning

The heavy route can fail in two different ways:

- slow-but-valid: the run eventually completes and writes `ae_events.csv`
- bridge-side execution failure: PFC returns an error status before all solve outputs are synced

When that happens, first check whether the temporary solve workspace already has `peak.sav`, `final.sav`, `stress_strain.csv`, or `ae_events.csv` before deciding to rerun.

## Interpretation Warning

Do not report source mechanisms unless the event table contains tensor data and the post-processing script has documented classification thresholds. If only `mode` or `mode_label` exists, report tension/shear crack-mode statistics rather than tensor-derived source type.
