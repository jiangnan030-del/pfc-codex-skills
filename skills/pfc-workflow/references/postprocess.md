# Post-processing

Use this file when the user asks what to export, monitor, or plot from PFC.

## Core outputs

A complete post-processing chain should usually include:

- stress-strain curve
- peak and residual stress summary
- peak strain or strain at key stages
- crack count or damage evolution
- porosity or volumetric response when relevant
- force-chain or contact-force visualization
- saved states for key stages such as pre-peak, peak, and final

## In-model monitoring ideas

- histories for axial or shear stress and strain
- crack counters or bond-break measures
- contact counts and coordination estimates
- measure objects for stress, strain, and porosity

## Minimal output checklist

- exported curve data in CSV
- stage-specific saved states
- figure-ready tabular outputs
- clear mapping between saved state names and reported stages

## Plot families

- curve plots: stress-strain, damage, porosity, coordination number
- field plots: displacement, velocity, stress-related maps, porosity maps
- structural plots: cracks, force chains, failure traces
- summary tables: modulus, peak stress, residual stress, peak strain, crack counts

## Good practice

- derive figures from exported source data
- define stage naming once and keep it consistent
- include enough metadata to regenerate figures later

## Project-style full-case chain

For the current project pattern, a complete case usually means this chain:

1. `run_case.py --solve-only` for calibration loops
2. `postprocess_results_2d.py` for experiment-vs-simulation curve comparison
3. `plot_contours_2d.py` for peak/final fracture and field contour exports
4. `plot_peak_fields.py` for peak-field overlays
5. `plot_stage_contact_maps.py` for stage contact coordination and filtered force chains
6. `gen_force_chain_vtp.py` plus `render_force_chain.py` for stage force-chain renders
7. native stage exports for:
   - `stage_*_native.png`
   - `stage_*_fracture_only.png`
   - `stage_*_fracture_ball.png`
   - `stage_*_contact_distribution.png`
   - `stage_*_contact_forcechain.png`
   - `probe_contact_*.png`
   - `peak_ball_native.png`

If the solve is complete but some native stage images are missing, prefer
replaying native exports from the saved `stage_*.sav`, `peak.sav`, and
`final.sav` states instead of rerunning the entire mechanical solve.
