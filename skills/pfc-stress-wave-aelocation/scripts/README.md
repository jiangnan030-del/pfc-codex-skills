# Scripts

This directory contains public-friendly templates for stress-wave propagation and AE source localization.

## Canonical Assets

- `chain_1d.p2dat`: 1D particle-chain wave-speed scaffold.
- `hex_2d.p2dat`: 2D hexagonal wavefield scaffold.
- `ricker_source.p2fis`: Ricker velocity source FISH template.
- `absorbing_boundary.p2fis`: absorbing-boundary dashpot template.
- `ae_locate.py`: velocity-free AE source localization helper.
- `plot_wavefield.py`: waveform plotting helper.
- `plot_cross_correlation_demo.py`: reproduces the two-panel waveform and CCR time-delay figure.
- `manifest.json`: file inventory with SHA-256 hashes.

## Rules

- Treat PFC files as templates and verify syntax against the installed PFC version.
- Keep source, boundary, export, and localization steps separate.
- Do not include generated save states, binary results, or private paths.
- Use Python helpers on exported histories rather than reading PFC save states directly.
