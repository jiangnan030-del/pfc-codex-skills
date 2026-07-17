---
name: pfc-ae-energy
description: Child skill of pfc-workflow for acoustic-emission, macro energy, AE event clustering, and moment-tensor source-mechanism analysis in PFC bonded-particle simulations.
---

# PFC AE Energy

This is a child skill under `pfc-workflow`. It does not own full-case solve planning, generic calibration, standard non-AE plotting, or contact-law design. It owns the AE / energy / source-mechanism branch after the parent workflow has produced a calibrated bonded specimen and decided that fracture-process monitoring is required.

## When To Use

Use this skill when the user wants to:

- track bond-break activity as AE hits or crack events
- add stage-wise crack statistics to UCS, Brazilian, biaxial, triaxial, or custom loading models
- compute macro energy-density indicators from stress-strain data
- cluster nearby bond breaks into AE events
- compute scalar moment, moment magnitude, T-k coordinates, or source type
- classify tensile, shear, double-couple shear, mixed, or compressive/implosive mechanisms from tensor-derived quantities
- export AE event tables, cumulative counts, hit rates, spatial maps, stage summaries, or Hudson/T-k style figures

Do not use this skill as the main workflow wrapper when the request is really "run the whole case" or "organize the full PFC project". In those cases, `pfc-workflow` is the parent skill and this skill is only a downstream branch.

## Parent Skill Relationship

- Parent `pfc-workflow`: owns full case planning, model staging, calibration, solve management, V&V, and delivery.
- Sibling `pfc-contact-models`: owns contact-law choice, CMAT setup, bond installation, and contact property validation.
- Sibling `pfc-postprocessing`: owns generic non-AE plots, field images, VTK/VTP exports, and reports.
- Child branch here: AE hits/events, macro energy density, tensor source-mechanism interpretation, and AE-specific figures/tables.

## First Rules

1. Confirm the PFC version first. PFC 6.0 callback, contact, fracture, and export syntax may differ from later releases.
2. Confirm the specimen is mechanically calibrated before enabling paper-grade AE interpretation.
3. Decide up front whether the task needs Level 1 hits, Level 2 clustered events, or Level 3 moment tensor.
4. Keep the solve path stable. Add monitoring with callbacks and exports, not GUI-only manual steps.
5. Save milestone states before loading, at key stages, at peak, and at final so AE outputs can be tied to physical states.
6. Be explicit about units. For macro energy-density plots, stress in `MPa` integrated over strain gives `MJ/m^3`.
7. Do not claim tensor-derived source mechanisms unless tensor columns and classification thresholds exist.

## Route Levels

Choose the lightest route that satisfies the request.

### Level 1: AE Hits

Each bond break is treated as one AE hit.

Outputs:

- hit time, strain, stress, position, and mode
- cumulative hit count
- tension/shear hit counts
- AE hit rate
- simple AE spatial map

Use for fast studies, debugging, or when the user only needs crack activity timing and localization.

### Level 2: Clustered AE Events

Nearby bond breaks in time and space are grouped into one AE event.

Outputs:

- event center
- event duration
- participating hit count
- event size proxy
- stage-wise event count and event maps

Use when event statistics should be compared with laboratory AE catalogs or when raw bond-break counts are too granular.

### Level 3: Moment Tensor And Source Type

Clustered events receive tensor-derived quantities.

Outputs:

- tensor columns `mt_xx`, `mt_yy`, `mt_zz`, `mt_xy`, `mt_xz`, `mt_yz`
- scalar moment `M0`
- moment magnitude `Mw`
- T-k source-type coordinates
- tensile / shear / double-couple shear / mixed labels
- source-type plots and stage-wise mechanism fractions

Use when the user explicitly asks for moment tensor, scalar moment, T-k, Hudson plot, source mechanism, rupture type, or paper-grade AE interpretation.

## Documentation-Backed Rules

PFC 6.0 documentation points checked through `pfc-mcp` are summarized in `references/ae-doc-notes.md`.

Relevant command families:

- `fish callback`: event/cycle hooks for monitoring bond breaks or contact events.
- `fish history`: cumulative AE, tension, shear, or scalar diagnostics through time.
- `model history`, `measure history`: stress/strain/mechanical-state monitoring.
- `contact list`, `contact model`, `contact property`, `contact method`, `contact cmat`: audit and setup context for bonded contacts.
- `fracture create`, `fracture list`, `fracture export`, `fracture contact-model`: optional fracture-object workflows.
- `history export`, `table export`, `data scalar/vector/tensor-export`: export routes for histories and fields.
- `program call`: modular AE monitoring, loading, and export stages.

Verify exact callback event names and syntax in the installed PFC version before finalizing a runnable `.p2fis` or `.p3fis` file.

## Moment Tensor Essentials

For an AE event source region, compute a tensor from contact-force changes and lever arms:

```text
M_ij = sum_k DeltaF_i^k * R_j^k
```

where `DeltaF_i^k` is contact-force change and `R_j^k` is the vector from event center to contact point. Symmetrize before eigenvalue-based interpretation when necessary.

Common derived quantities:

```text
M0 = sqrt((m1^2 + m2^2 + m3^2) / 2)
Mw = (2 / 3) * log10(M0) - 6
T  = 2 * M2' / max(abs(M1'), abs(M3'))
k  = M_iso / (abs(M_iso) + max(abs(M1'), abs(M3')))
```

A practical T-k classification is:

- linear tensile: `-1 <= T <= -0.4` and `0.2 <= k <= 0.4`
- linear shear: `0.4 <= T <= 1` and `-0.4 <= k <= -0.2`
- double-couple shear: `-0.2 <= T <= 0.2` and `-0.2 <= k <= 0.2`
- mixed: all remaining valid points

## Workflow

### 1. Confirm Precondition

The parent workflow should already provide:

- calibrated bonded specimen
- accepted contact model and bond parameters
- loading plan and stage definitions
- milestone save strategy
- target output contract

### 2. Instrument The Solve

- register callback logic for bond-break or contact-event monitoring
- capture at least `time`, `strain`, `stress`, `x`, `y` or `x,y,z`, and `mode`
- keep cumulative tension and shear counters
- for heavy moment tensor, cache contact state needed for `DeltaF` and lever arms

### 3. Export Histories And Events

At minimum, export:

- stress-strain
- total crack or AE count
- tension and shear counts separately when available
- raw AE hit or event table
- peak and final saved states

### 4. Cluster And Compute Mechanisms

For Level 2/3:

- cluster hits using documented time-space thresholds
- compute event centers and durations
- for Level 3, compute tensors, scalar moments, magnitudes, T-k values, and source types
- keep raw hit IDs or enough traceability to audit event composition

### 5. Build Energy Outputs

If no direct contact-energy accounting is available, compute macro indicators from stress-strain:

- total input energy density from `integral(sigma d epsilon)`
- recoverable elastic energy density from `sigma^2 / (2E)`
- dissipated energy density from `input - elastic`

State clearly when this is a macro energy approximation rather than direct micro-contact energy release.

### 6. Plot By Stage

Default plot family:

- stress-strain + cumulative AE
- AE hit/event rate vs strain
- input, elastic, and dissipated energy vs strain
- AE spatial event map
- stage-wise AE count summary
- T-k / Hudson source-type plot when Level 3 data exist
- stage-wise mechanism fractions when Level 3 data exist


## Fig.9 PFC GUI State Capture During Heavy AE

Do **not** run a second loading simulation only to create Fig.9 A-F PFC GUI screenshots.
When a heavy AE run is being prepared, integrate the Fig.9 save-state checkpoints
directly into the case `3load.dat` so the same run produces both AE CSV outputs and
GUI-exportable states.

### Required integration

Add Fig.9 checkpoint strain variables beside the normal stage variables, using the
current case's AE/load curve targets when available:

```fish
[fig9_a_strain = ...]
[fig9_b_strain = ...]
[fig9_c_strain = ...]
[fig9_d_strain = ...]
[fig9_a_saved = 0]
[fig9_b_saved = 0]
[fig9_c_saved = 0]
[fig9_d_saved = 0]
[fig9_e_saved = 0]
```

Inside the heavy-AE `loadhalt_wall` function, save the Fig.9 states as the wall
strain reaches the target points:

```fish
if fig9_a_saved = 0
  if abs_strain >= fig9_a_strain
    command
      model save 'fig9_A'
    endcommand
    fig9_a_saved = 1
  end_if
end_if
```

Repeat for `fig9_B`, `fig9_C`, and `fig9_D`. Save `fig9_E` together with the
normal `peak` state, and save `fig9_F` together with the normal `final` state:

```fish
model save 'peak'
model save 'fig9_E'
...
model save 'final'
model save 'fig9_F'
```

After the heavy AE run, export PFC GUI screenshots by restoring these states and
using the current GUI ball+fracture template exactly:

```fish
model restore 'fig9_A'
plot export bitmap filename 'fig9_A_balls_fractures.png' size 1600 1200
```

This links Fig.9 GUI state export to the heavy AE simulation and avoids a second
full loading run. Preserve the user's current GUI template; do not `plot create`,
`plot clear`, or modify plot items unless explicitly requested.

## Fig.9 Lower-Row AE Mechanism Panels

Use this workflow when the user wants only the lower row of the Fig.9-style
composite: a 1×6 or 2×6 AE mechanism panel set that shows AE location,
source-type class, and magnitude, but does **not** include the PFC screenshot row.
This is the preferred fallback when the PFC GUI export row is still being tuned.

### Required input

The case directory must contain:

- `ae_clustered_events.csv`
- spatial columns `center_x_mm`, `center_y_mm`
- magnitude column `moment_magnitude`
- tensor columns `mt_iso`, `mt_dev_1`, `mt_dev_2`, `mt_dev_3` for source classification
- stage threshold reference data, typically from `ae_multiaxis_step_source.csv`

### Source classification rule

Do **not** rely only on `source_type_tk` text labels, because they can miss
implosive events. Prefer the tensor-derived Feignier & Young-style ISO ratio:

```text
%ISO = mt_iso / (|mt_iso| + max(|mt_dev_1|, |mt_dev_2|, |mt_dev_3|))
```

Classify with a configurable threshold:

- `%ISO > +iso_threshold` → `Explosion`
- `%ISO < -iso_threshold` → `Implosion`
- otherwise → `Shear`

The default threshold is `0.3`. Expose it as `--iso-threshold` so the user can
raise or lower implosion sensitivity. Use `0.2` as a candidate when the user
wants more Implosion events, while `0.3` keeps Shear dominant.

### Panel contract

- Draw hollow circles with edge colors:
  - Explosion = `red_strong`
  - Shear = `green_3`
  - Implosion = `blue_main`
- Map magnitude to marker size nonlinearly, e.g. normalized `**1.55`, with
  explicit min/max marker sizes.
- Keep a fixed square view box, e.g. `(-20, 20) mm` in both axes.
- Hide ticks and tick labels; keep a thin neutral border only.
- Place the stage letter `A`–`F` beneath each panel.

### Stage logic

For the reference `b45_d14` figure, derive A–F from the current loading curve:

- A/B/C/D: cumulative thresholds along the pre-peak curve
- E: peak stress point
- F: first post-peak point where stress falls to about 75% of peak, or final
  if the curve never crosses that level

Use cumulative display, i.e. include all AE events with `abs(strain_start)` less
than or equal to the target stage threshold.

### Python plotting script

Use the skill template script:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_fig9_ae_mechanism_panels.py b45_d14 --hide-top --output-prefix fig9_macrocrack_mechanism_ae_only_iso
```

Useful options:

```powershell
python .\plot_fig9_macrocrack_mechanism.py b45_d14 --hide-top --output-prefix fig9_macrocrack_mechanism_ae_only_iso --iso-threshold 0.3
```

### Outputs

The script writes:

- `*_ae_only_iso.svg` as the primary editable vector output
- `*_ae_only_iso.png`
- `*_ae_only_iso.pdf`
- `*_ae_only_iso_summary.csv`

The summary CSV should contain:

- `stage`
- `target_strain_abs`
- `ae_events`
- `explosion`
- `shear`
- `implosion`
- `iso_min`
- `iso_max`

### Diagnostics

Print a short diagnostic block when running the script:

- the input AE column names
- whether tensor-based ISO classification was used
- the `iso_threshold`
- the final Explosion/Shear/Implosion counts

### Nature-style contract

Follow the same `nature-figure` rules used elsewhere in this skill:

- mandatory editable SVG font lines at the top of the script
- `apply_publication_style(...)`
- `finalize_figure(...)`
- white background, no grid, frameless legend, thin neutral panel borders
- SVG primary, PNG/PDF secondary

## Fig.10 AE Source Fracture-Type Evolution

Use this workflow when the user wants the Fig.10-style two-panel source-type
summary: cumulative Explosion/Shear/Implosion event counts over loading plus
stage-wise source-type percentages from moment-tensor decomposition.

### Required input

The case directory must contain:

- `ae_clustered_events.csv`
- tensor columns `mt_iso`, `mt_dev_1`, `mt_dev_2`, `mt_dev_3`
- `strain_start` for placing events along the loading history
- `ae_multiaxis_step_source.csv` with `step_load_1e4`, `strain_abs`, and `stress_plot_mpa`

### Source classification rule

Use the same tensor-derived ISO rule as the Fig.9 lower-row AE panels. Do not use
`source_type_tk` alone, because it can miss Implosion events:

```text
%ISO = mt_iso / (|mt_iso| + max(|mt_dev_1|, |mt_dev_2|, |mt_dev_3|))
```

- `%ISO > +iso_threshold` → `Explosion`
- `%ISO < -iso_threshold` → `Implosion`
- otherwise → `Shear`

Keep `--iso-threshold 0.3` as the default. Treat `0.2` as a documented candidate
when the user wants more Implosion events.

### Panel contract

Panel `(a)`:

- plot `Stress/MPa` against `Step/10^4` on the left y-axis as a black line
- plot cumulative `Explosion`, `Shear`, and `Implosion` counts on the right y-axis
- use triangle markers on the source-type cumulative curves
- annotate stage points `O`, `A`, `B`, `C`, `D`, `E`, `F`
- keep the legend frameless and near the upper-left

Panel `(b)`:

- compute interval source-type percentages for `BC`, `CD`, `DE`, `EF`, and `OF`
- draw a 100% stacked bar chart
- stack order: `Implosion` at bottom, `Shear` middle, `Explosion` top
- annotate each sufficiently large segment with an integer percentage
- put the source-type legend above the bars without a frame

### Python plotting script

Use the skill template script:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_fig10_ae_source_types.py b45_d14 --output-prefix fig10_ae_source_types_notitle --iso-threshold 0.3
```

The verified local script is:

```powershell
python .\plot_fig10_ae_source_types.py b45_d14 --output-prefix fig10_ae_source_types_notitle --iso-threshold 0.3
```

### Outputs

The script writes:

- `fig10_ae_source_types_notitle.svg` as the primary editable vector output
- `fig10_ae_source_types_notitle.png`
- `fig10_ae_source_types_notitle.pdf`
- `fig10_ae_source_types_notitle_cumulative.csv`
- `fig10_ae_source_types_notitle_stage_percent.csv`

If the user already generated `fig10_ae_source_types_cumulative.csv` and
`fig10_ae_source_types_stage_percent.csv` with another prefix, preserve those CSVs
unless explicitly asked to clean them.

### Diagnostics

Print a short diagnostic block:

- whether tensor ISO classification was used
- `iso_threshold`
- total Explosion/Shear/Implosion counts
- interval counts for `BC`, `CD`, `DE`, `EF`, and `OF`

### Nature-style contract

- mandatory editable SVG font lines at the top of the script
- `apply_publication_style(...)`
- `finalize_figure(...)`
- no top figure title when the user requests the compact manuscript panel version
- SVG primary, PNG/PDF secondary

## Fig.11 AE Sources of Different Fracture Types

Use this workflow when the user wants a Fig.11-style composite showing a central
specimen AE/source map surrounded by six circular local source-mechanism insets.
The current implementation composes the figure in Python/matplotlib from exported
PFC particle fields plus AE hit/event CSVs, avoiding fragile GUI screenshot layout.

### Required input

The case directory must contain:

- `ae_clustered_events.csv` with `event_id`, `center_x_mm`, `center_y_mm`, `moment_magnitude`, `r_value`, `tension_hits`, `shear_hits`, `hit_count`, and in-plane moment tensor columns `mt_xx`, `mt_yy`, `mt_xy`
- `ae_events.csv` with hit-level `x`, `y`, `mode_label`, and optionally `radius_model`
- `plotdata_ball_fields_final.csv` with particle `x`, `y`, and `radius`

The script can fall back to `plotdata_ball_fields_peak.csv` or legacy
`plotdata_ball_fields.csv`, but for manuscript output prefer the explicitly named
final-state export `plotdata_ball_fields_final.csv`.

### Source classification rule

For Fig.11, follow the paper-style `R` rule rather than micro-crack count ratio:

- `R > +r_threshold` -> `Explosion`
- `R < -r_threshold` -> `Implosion`
- `|R| <= r_threshold` -> `Shear`

Default `--r-threshold` is `30.0`. If an event contains more tension hits but its
`R` lies inside the shear band, still classify it as `Shear`.

### Figure contract

- Central panel: draw the full specimen particle field, overlay tension/shear AE hits, and mark six selected events with black numbered circles.
- Insets: draw local particle microstructure in circular views, red tension hits, blue shear hits, a green AE event circle, green/blue circular boundaries, and white principal-axis arrows.
- Principal arrows: compute the in-plane eigensystem of `[[mt_xx, mt_xy], [mt_xy, mt_yy]]`; arrow direction is the eigenvector direction and arrow length scales with relative absolute eigenvalue.
- Text labels in each inset: `M= {moment_magnitude:.2f}` and `R= {r_value:.2f}`.
- Use blue dashed connector lines from central numbered events to the corresponding insets.
- No top or bottom figure title in the compact manuscript version unless explicitly requested.

### Python plotting script

Use the skill template script:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_fig11_ae_sources.py b45_d14 --output-prefix fig11_ae_sources --r-threshold 30
```

To force specific representative events:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_fig11_ae_sources.py b45_d14 --event-ids 33,75,31,15,364,231
```

### Outputs

The script writes:

- `fig11_ae_sources.svg` as the primary editable vector output
- `fig11_ae_sources.png`
- `fig11_ae_sources.pdf`
- `fig11_ae_sources_selected_events.csv`

The selected-event CSV contains:

- `event_id`
- `center_x_mm`
- `center_y_mm`
- `moment_magnitude`
- `r_value`
- `source_class`

### Diagnostics

Print a short diagnostic block:

- total event count, particle count, and hit count
- class counts using `R +/- r_threshold`
- selected six events with `event_id`, class, `M`, `R`, tension hits, and shear hits

### Nature-style contract

- mandatory editable SVG font lines at the top of the script
- `apply_publication_style(...)`
- `finalize_figure(...)`
- SVG primary, PNG/PDF secondary


- `references/theory.md`: AE interpretation ladder, tensor equations, source classification, and energy distinction.
- `references/ae-event-clustering.md`: time-space clustering rules and event table contract.
- `references/source-type-plot.md`: T-k, Hudson-style, and rupture/source-orientation figure requirements.
- `references/calibration-cases.md`: example granite targets and sanity checks.
- `references/ae-doc-notes.md`: PFC 6.0 command notes checked through `pfc-mcp`.
- `references/implementation.md`: PFC instrumentation and export patterns.
- `references/heavy-moment-tensor.md`: rigorous heavy-AE implementation route.
- `references/outputs.md`: default figure/table contract.
- `templates/heavy-ae/plot_ae_energy.py`: Python AE/energy/Hudson post-processing script.
- `templates/heavy-ae/fracture-heavy-mt.p2fis`: PFC 6.0 heavy AE callback template.
- `templates/heavy-ae/export-heavy-ae-4export.dat`: stress-strain plus AE CSV export.
- `templates/heavy-ae/3load-history-snippet.dat`: crack history IDs needed by AE plots.
- `templates/heavy-ae/plot_fig9_ae_mechanism_panels.py`: Fig.9 lower-row AE location/source-type/magnitude panels.
- `templates/heavy-ae/plot_fig10_ae_source_types.py`: Fig.10 cumulative source-type curves plus stage-percentage bars.
- `templates/heavy-ae/plot_fig11_ae_sources.py`: Fig.11 central AE map plus six local source-mechanism insets.

## AE Magnitude Versus Micro-Crack Count Relation Figure

Use this workflow when the user wants a scatter + fit figure relating clustered
AE event magnitude to the number of micro-cracks/bond-break hits contained in
each event. In the heavy AE outputs, use `moment_magnitude` for magnitude and
`hit_count` for the event micro-crack count.

### Required input

The case directory must contain:

- `ae_clustered_events.csv`
- a magnitude column, normally `moment_magnitude`
- an integer event-size/count column, normally `hit_count`

The verified `b45_d14` example has most events at `hit_count = 1`, with sparse
larger events up to `hit_count = 5`. Do not invent reference-figure large events
such as `8` or `18` unless the user explicitly asks for schematic/reference-data
reproduction.

### Python plotting script

Use:

```powershell
python .\plot_ae_magnitude_microcrack_relation.py b45_d14
```

or from the skill template:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_ae_magnitude_microcrack_relation.py <case-dir>
```

Useful options:

```powershell
python .\plot_ae_magnitude_microcrack_relation.py b45_d14 --magnitude-col moment_magnitude --count-col hit_count --bin-width 0.10 --output-prefix ae_magnitude_microcrack_relation
```

The script outputs:

- `ae_magnitude_microcrack_relation.svg` as the primary editable vector figure
- `ae_magnitude_microcrack_relation.png` as a raster preview
- `ae_magnitude_microcrack_relation.pdf`
- `ae_magnitude_microcrack_relation_source.csv`
- `ae_magnitude_microcrack_relation_binned_source.csv`
- `ae_magnitude_microcrack_relation_fit.csv`

### Data processing contract

- Plot every clustered AE event as `(magnitude, microcrack_count)`.
- Apply only a small vertical display jitter (default `±0.06`) to separate
overlapping integer counts. Fitting and source data must preserve the raw integer
`microcrack_count`.
- Bin magnitudes with fixed width, default `0.10`.
- For each bin, compute mean, median, maximum, event count, and the cumulative
upper envelope:
  `envelope_microcrack_count = cummax(max_microcrack_count)`.
- Fit the envelope using the baseline-power model requested for the low-flat / terminal-rise trend:

```text
N = baseline + amp * max(M - M0, 0)^power
```

- `baseline` is fixed to the minimum observed micro-crack count, usually `1`.
- Search `M0` over the interior magnitude range and `power` over `2.0..4.0`; for
each pair solve non-negative `amp` by least squares, then keep the best `R^2`.
- For the verified `b45_d14` run, the fitted result was approximately:
  `baseline = 1.00`, `amp = 6.61`, `M0 = -7.695`, `power = 2.00`, `R^2 = 0.879`.
- Export source data columns:
  `magnitude, microcrack_count, microcrack_count_display, fit_prediction`.
- Export binned source columns including:
  `magnitude_bin_center, mean_microcrack_count, median_microcrack_count, max_microcrack_count, event_count, envelope_microcrack_count, fit_prediction`.
- Export fit parameters:
  `model, target, baseline, amp, M0, power, r2, fit_points, magnitude_min, magnitude_max`.

### Nature-style plotting contract

The script follows the `nature-figure` Python/matplotlib rules:

- The first three `rcParams` lines must be the editable-SVG font setup:
  `font.family = sans-serif`,
  `font.sans-serif = ["Arial", "DejaVu Sans", "Liberation Sans"]`,
  `svg.fonttype = none`.
- Use `apply_publication_style(font_size=15, axes_linewidth=2.0)` before creating
  the figure.
- Use `finalize_figure()` to save SVG first, then PNG at 300 dpi and PDF, then
  close the figure.
- Use semantic colors:
  - scatter outline: `neutral_black #272727`
  - fit line: `red_strong #B64342`
- Scatter style: hollow circles, `facecolors='none'`, `linewidths≈1.5`, legend
  label `aenum`.
- Fit curve: red line, `linewidth≈2.5`, legend label `Fitting curve`.
- Keep top/right spines off, no grid, y-axis from zero, and compact tick locators
  via `MaxNLocator`.
- Put the legend frameless and horizontal above the axes. Put the equation in the
  upper-right with a light white background. Use plain text for the equation if
  mathtext causes excessive memory use during `tight_layout`.

## AE Event Micro-Crack Count Distribution Figure

Use this workflow when the user wants the frequency distribution of how many
micro-cracks/bond-break hits are contained in each clustered AE event. In the
current heavy AE output, the required per-event count is `hit_count` in
`ae_clustered_events.csv`.

### Required input

The case directory must contain:

- `ae_clustered_events.csv`
- an integer event-size/count column, normally `hit_count`

The verified `b45_d14` example used the actual `hit_count` distribution:
`1 -> 329`, `2 -> 31`, `3 -> 4`, `4 -> 1`, `5 -> 1`. Do not copy reference
figure counts such as `902, 105, ...` unless the user explicitly asks for a
reference-data reproduction.

### Python plotting script

Use:

```powershell
python .\plot_ae_microcrack_count_distribution.py b45_d14
```

or from the skill template:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_ae_microcrack_count_distribution.py <case-dir>
```

Useful options:

```powershell
python .\plot_ae_microcrack_count_distribution.py b45_d14 --count-col hit_count --x-max 18 --output-prefix ae_microcrack_count_distribution
```

The script outputs:

- `ae_microcrack_count_distribution.svg` as the primary editable vector figure
- `ae_microcrack_count_distribution.png` as a raster preview
- `ae_microcrack_count_distribution.pdf`
- `ae_microcrack_count_distribution_source.csv`
- `ae_microcrack_count_distribution_fit.csv`

### Data processing contract

- Count the number of clustered AE events for each positive integer
  `microcrack_count`.
- By default, set the x-range to the case maximum count; use `--x-max` only when
  a fixed reference range is needed.
- Fit both candidate decay models on non-zero frequencies:
  - power law: `N = a * x^(-b)`
  - exponential: `N = a * exp(-b*x)`
- Select the model with the higher `R^2` and draw it as the red fitting curve.
- Export source data columns:
  `microcrack_count, frequency, fit_prediction`.
- Export fit parameters including selected `model`, `a`, `b`, `r2`, plus both
  candidate models' `a`, `b`, and `R^2` for audit.
- For the verified `b45_d14` example, the selected model was power law:
  `N = 341.95 x^(-3.88)`, `R^2 = 0.997`.

### Nature-style plotting contract

The script follows the `nature-figure` Python/matplotlib rules:

- The first three `rcParams` lines must be the editable-SVG font setup:
  `font.family = sans-serif`,
  `font.sans-serif = ["Arial", "DejaVu Sans", "Liberation Sans"]`,
  `svg.fonttype = none`.
- Use `apply_publication_style(font_size=15, axes_linewidth=2.0)` before creating
  the figure.
- Use `finalize_figure()` to save SVG first, then PNG at 300 dpi and PDF, then
  close the figure.
- Use semantic colors:
  - bars: `blue_secondary #3775BA`
  - bar edge: `neutral_dark #4D4D4D`
  - fit line: `red_strong #B64342`
  - value labels: `neutral_black #272727`
- Keep top/right spines off, no grid, frameless legend in the upper-right blank
  area, integer x ticks, and sparse integer y ticks via `MaxNLocator`.
- Place fitted-equation text away from the legend. The verified layout places it
  around `x=0.97, y=0.68` in axes coordinates, with a light white background to
  avoid overlap with data.
- Label each non-zero bar with its frequency, centered above the bar and offset
  slightly upward.

## AE Magnitude-Frequency And Gutenberg-Richter b-Value Figure

Use this workflow when the user wants an AE event magnitude-frequency plot and a
Gutenberg-Richter b-value relationship from clustered PFC AE events. The current
verified route uses the Level 2/3 clustered event table produced by the heavy AE
post-processing route.

### Required input

The case directory must contain:

- `ae_clustered_events.csv`
- a magnitude column, normally `moment_magnitude`

For heavy AE outputs, `ae_clustered_events.csv` should also preserve
`scalar_moment`, `magnitude_proxy`, `hit_count`, and source-mechanism columns for
audit, but the b-value figure only needs the selected magnitude column.

### Python plotting script

Use:

```powershell
python .\plot_ae_gr_bvalue.py b45_d14
```

or from the skill template:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_ae_gr_bvalue.py <case-dir>
```

Useful options:

```powershell
python .\plot_ae_gr_bvalue.py b45_d14 --magnitude-col moment_magnitude --bin-width 0.10 --output-prefix ae_gr_bvalue
```

The script outputs:

- `ae_gr_bvalue.svg` as the primary editable vector figure
- `ae_gr_bvalue.png` as a raster preview
- `ae_gr_bvalue.pdf`
- `ae_gr_bvalue_source.csv`
- `ae_gr_bvalue_fit.csv`

### Data processing contract

- Build a fixed-width magnitude histogram, default `bin_width = 0.10`.
- Compute cumulative frequency as `N(M) = count(magnitude >= M_bin_center)`.
- Compute `logN = log10(N)`.
- Fit the post-peak descending branch with `logN = a - bM`.
- Export source data columns:
  `magnitude_bin_center, magnitude_bin_left, magnitude_bin_right, frequency, cumulative_N, logN`.
- Export fit parameters:
  `a, b, slope, r2, fit_min_magnitude, fit_max_magnitude, fit_points, peak_magnitude`.
- Do not hard-code literature ranges or target b-values; use the case data. For
  the verified `b45_d14` example, the measured result was approximately
  `logN = -3.95M - 26.58`, `b = 3.95`, `R^2 = 0.999`, with a fit branch around
  `M = -7.25` to `-6.95`.

### Nature-style plotting contract

The script follows the `nature-figure` Python/matplotlib rules:

- The first three `rcParams` lines must be exactly the editable-SVG font setup:
  `font.family = sans-serif`,
  `font.sans-serif = ["Arial", "DejaVu Sans", "Liberation Sans"]`,
  `svg.fonttype = none`.
- Use `apply_publication_style(font_size=15, axes_linewidth=2.0)` before creating
  the figure.
- Use `finalize_figure()` to save SVG first, then PNG at 300 dpi and PDF, then
  close the figure.
- Use semantic colors:
  - histogram bars: `blue_secondary #3775BA`
  - histogram edge: `neutral_dark #4D4D4D`
  - logN hollow squares: `neutral_black #272727`
  - G-R fit line: `red_strong #B64342`
  - Frequency axis spine/ticks: `blue_main #0F4D92`
- Put bars on the bottom layer with:
  `ax1.set_zorder(ax2.get_zorder() + 1)` and `ax1.patch.set_visible(False)`.
- Keep top spines off, no grid, frameless legend in the upper left, and equation
  text in the upper right with `ha='right', va='top'`.
- Size axes from actual data using compact locators; do not fix Frequency to
  large reference values such as 100 or 150 unless the data require it.

## Step/1e4 Multi-Axis AE Figure

Use this workflow when the user wants a paper-style PFC uniaxial compression +
AE curve with stress, AE activity, cumulative AE events, and total crack number
on one shared `Step/10^4` x-axis.

### Required PFC history/export contract

The loading file must include the normal stress/strain/crack histories plus a
mechanical cycle history:

```fish
history interval 10
history id 99 @monitor
history id 1 @wsyy
history id 2 @weyy
history id 3 @crack_num
history id 4 @crack_tension_num
history id 5 @crack_shear_num
model history id 6 mechanical cycles-total
```

The export file should write both:

- `stress_strain.csv`: strain-based response for normal post-processing
- `stress_strain_step.csv`: step-based response with columns
  `step, step_1e4, strain, stress_mpa, crack_num, crack_tension_num, crack_shear_num`

Use `templates/heavy-ae/3load-history-snippet.dat` and
`templates/heavy-ae/export-heavy-ae-4export.dat` as the current templates. The
export template intentionally uses a second loop variable `j` for the Step table;
PFC 6.0 FISH can raise `Local variable or argument previously defined` if the
same `loop local i` name is reused inside one function.

### Python plotting script

Use:

```powershell
python .\plot_ae_multiaxis_step.py b45_d14
```

or from the skill template:

```powershell
python .codex\skills\pfc-ae-energy\templates\heavy-ae\plot_ae_multiaxis_step.py <case-dir>
```

The script expects:

- `stress_strain_step.csv`
- `ae_clustered_events.csv`

It outputs:

- `ae_multiaxis_step.png/svg/pdf`
- `ae_multiaxis_step_source.csv`
- `ae_multiaxis_step_bar_source.csv`
- `ae_multiaxis_step_event_source.csv`

### Plot grammar

- x-axis: load-relative `Step/10^4`, computed as `(step - first_step) / 10000`
  for readable loading curves. Raw `step_1e4` is preserved in source data.
- left y-axis: `Stress/MPa`, black curve.
- right y-axis 1: `AE ratio/%`, red bars, binned from clustered AE events.
- right y-axis 2: `AE Count`, blue cumulative event curve.
- right y-axis 3: `Total crack number`, lime/green cumulative crack curve.
- `AE Count` and `Total crack number` axes must be sized from actual data maxima,
  not fixed to large reference values such as 1200 or 1500.
- Do not include a bottom `(b)` panel label unless the user explicitly asks for a
  subfigure label.
- Current plotting version uses a peak-preserving visual origin correction: only
  the very short initial seating segment up to `0.03 x 10^4` load-relative step is
  redrawn from zero into the raw curve; later stress values, including UCS/peak
  stress, remain raw. Preserve both `stress_raw_mpa` and `stress_plot_mpa` in the
  source CSV. If the user wants strictly raw stress, remove this visual correction
  and document that the first plotted stress may not start at zero.

## Output Contract

For a complete AE/energy delivery, prefer these artifacts:

- `ae_events.csv`
- `stress_strain.csv` with crack or AE cumulative columns
- `ae_clustered_events.csv` for Level 2/3
- `ae_energy_overview.png/svg/pdf`
- `ae_event_map.png/svg/pdf`
- `ae_energy_metrics.xlsx`
- `stress_strain_step.csv` when Step/10^4 figures are requested
- `ae_multiaxis_step.png/svg/pdf` when Step/10^4 multi-axis AE figures are requested
- `ae_gr_bvalue.svg/png/pdf` when magnitude-frequency and Gutenberg-Richter b-value figures are requested
- `ae_gr_bvalue_source.csv` and `ae_gr_bvalue_fit.csv` for b-value source data and fit audit
- `ae_microcrack_count_distribution.svg/png/pdf` when per-event micro-crack count distributions are requested
- `ae_microcrack_count_distribution_source.csv` and `ae_microcrack_count_distribution_fit.csv` for distribution source data and decay-fit audit
- `ae_magnitude_microcrack_relation.svg/png/pdf` when magnitude versus per-event micro-crack count relation figures are requested
- `ae_magnitude_microcrack_relation_source.csv`, `ae_magnitude_microcrack_relation_binned_source.csv`, and `ae_magnitude_microcrack_relation_fit.csv` for relation source data and envelope-fit audit
- `fig9_macrocrack_mechanism_ae_only_iso.svg/png/pdf` when Fig.9 lower-row AE mechanism panels are requested without the PFC screenshot row
- `fig9_macrocrack_mechanism_ae_only_iso_summary.csv` for per-stage AE event counts and tensor-ISO source-type audit
- `fig10_ae_source_types_notitle.svg/png/pdf` when Fig.10 source fracture-type evolution panels are requested
- `fig10_ae_source_types_notitle_cumulative.csv` and `fig10_ae_source_types_notitle_stage_percent.csv` for cumulative counts and stage-percentage audit; older `fig10_ae_source_types_cumulative.csv` / `fig10_ae_source_types_stage_percent.csv` may also exist from earlier prefixes
- `fig11_ae_sources.svg/png/pdf` when Fig.11 AE source-mechanism composite panels are requested
- `fig11_ae_sources_selected_events.csv` for selected event audit (`event_id`, `M`, `R`, and `source_class`)

For Level 3 moment tensor, also prefer:

- `ae_source_event_map.png/svg/pdf`
- `ae_tk_source_map.png/svg/pdf`
- `ae_tk_diamond_cn.png/svg/pdf/tiff`
- `ae_tk_diamond_cn_source_data.csv`
- `ae_orientation_stereonet.png/svg/pdf/tiff`
- `ae_orientation_moment_polar.png/svg/pdf/tiff`
- `ae_orientation_axes.csv`
- stage-wise source-type fraction table or figure

## Python Post-Processing Route

For the current heavy AE workflow, prefer the bundled Python script:

- `templates/heavy-ae/plot_ae_energy.py`

This script expects at least:

- `stress_strain.csv`
- `ae_events.csv`
- `config.py` with `MODEL_TO_MM`, `case_dir`, and `case_title`

It produces the standard AE/energy figures plus the Chinese Hudson-style source-mechanism plot:

- `ae_energy_overview.png/svg/pdf`
- `ae_event_map.png/svg/pdf`
- `ae_source_event_map.png/svg/pdf`
- `ae_tk_source_map.png/svg/pdf`
- `ae_tk_diamond_cn.png/svg/pdf/tiff`
- `ae_orientation_stereonet.png/svg/pdf/tiff`
- `ae_orientation_moment_polar.png/svg/pdf/tiff`
- `ae_orientation_axes.csv`
- `ae_event_evolution.png/svg/pdf`
- `ae_clustered_events.csv`
- `ae_energy_metrics.xlsx`
- `ae_tk_diamond_cn_source_data.csv`

Run it from the case package directory so `config.py` resolves correctly, for example:

```powershell
python .\plot_ae_energy.py b90_d16
```

## Complete Case Handoff From pfc-workflow

When a case has just finished calibration in the workflow skill, the preferred handoff is:

1. freeze the accepted bond/contact parameters
2. switch the case to AE-enabled export files
3. rerun the case solve with AE enabled
4. confirm `ae_events.csv`, `stress_strain.csv`, and `final.sav` exist
5. run `plot_ae_energy.py`
6. verify AE, energy, and source-mechanism outputs requested by the user

This skill is not responsible for:

- generic non-AE curve comparison
- contour fields unrelated to AE
- native stage screenshots
- generic force-chain rendering

## Required Inputs

Ask for these if missing before running an AE/energy workflow:

- target PFC version, dimensionality, and case directory;
- saved-state sequence or exported histories that define loading stages;
- stress-strain, crack, energy, and event-export file contracts;
- stage labels or the rule used to derive stages from the loading curve;
- requested output formats and whether heavy moment-tensor analysis is in scope.

## Local Contents

- `references/`: AE theory, clustering, source-type plots, calibration notes, output contracts, and implementation details.
- `scripts/`: reusable Python/FISH helpers and plotting pipelines where included.
- Use this skill as a specialist child of `pfc-workflow`; return final artifacts and assumptions to the parent workflow.

