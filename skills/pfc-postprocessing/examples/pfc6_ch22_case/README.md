# PFC6.0 Chapter 22 Bridge Case

## old_source
- `<PFC6_CH22_SOURCE_DIR>`
- especially:
  - `动图制作\outfig.py`
  - `动图制作\jieguo*.sav`
  - `动图制作\jieguo_*.png`
  - `测量圆参数分析`
  - `应力十字架`

## input_contract
- save states or exported frame images
- measurement-grid stress data
- porosity-grid data
- fracture orientation data when available

## output_contract
- ordered frame PNGs
- GIF animation
- stress figure
- porosity figure
- rose diagram or other directional figure

## replacement_script
- `scripts/pfc_sav_to_frames_template.py`
- `scripts/export_animation_frames.py`
- `scripts/export_animation.py`
- `scripts/plot_fields.py`

## validation_example
The public animation case mirrors the chapter-22 idea:

1. collect a sequence of frame images
2. normalize them
3. assemble a GIF

This example is public and GitHub-safe because it avoids shipping external `.sav` dependencies.
