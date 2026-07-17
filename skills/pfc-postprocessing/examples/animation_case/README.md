# Animation Case

This example mirrors the Chapter-22 idea behind `outfig.py`, but in a public form.

## What is inside

- `raw_frames/` with `jieguo_*.png`

## Teaching point

Animation is just ordered frame images plus one assembly step.

## Recommended commands

```bash
python .codex/skills/pfc-postprocessing/scripts/export_animation_frames.py ^
  --input-dir .codex/skills/pfc-postprocessing/examples/animation_case/raw_frames ^
  --output-dir .codex/skills/pfc-postprocessing/examples/demo_outputs/ordered_frames

python .codex/skills/pfc-postprocessing/scripts/export_animation.py ^
  --input-dir .codex/skills/pfc-postprocessing/examples/demo_outputs/ordered_frames ^
  --output-dir .codex/skills/pfc-postprocessing/examples/demo_outputs/animations ^
  --stem demo_animation
```
