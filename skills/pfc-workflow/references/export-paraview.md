# Export to ParaView / PyVista

Use this file when the user wants reusable external visualization instead of GUI-only screenshots.

## Preferred export contract

- particle geometry or centers
- particle radius or size fields
- displacement or velocity vectors
- contact-force magnitudes and directions
- crack geometry and orientation
- stage labels and saved-state names

## Recommended formats

- `CSV` for curves and summary tables
- `VTP` or `VTK` for particles, contacts, cracks, and stage visualization

## Tool roles

- ParaView: interactive 3D inspection, slices, glyphs, tube rendering, batch renders with `pvbatch`
- PyVista: scripted VTK generation and automated figure production
- OVITO: particle animation, trajectories, and coordination-like visual analysis
- matplotlib / seaborn / Origin: 2D scientific curves and summary charts

## Rendering pattern

1. export machine-readable particle/contact/crack data
2. build a reproducible rendering script or batch file
3. version the rendering inputs with the numerical outputs
4. avoid manual scene edits unless they are documented and reproducible

## Common figure types

- stage-wise force-chain maps
- peak and final field plots
- displacement-colored particle renders
- crack orientation and density views
