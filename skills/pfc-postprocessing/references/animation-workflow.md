# Animation Workflow

## What animation really is

Animation is not a mysterious PFC feature.
It is just:

1. model states or saved views
2. one bitmap image per state
3. stable frame ordering
4. one final assembly step into GIF or MP4

## Public pattern

```text
.sav sequence
    ↓
PFC plot export bitmap
    ↓
PNG frames
    ↓
frame normalization
    ↓
GIF / optional MP4
```

## Historical source

PFC6.0 Chapter 22 `outfig.py` used this exact idea:

- restore `jieguo1 ... jieguo20`
- export `jieguo_1 ... jieguo_20` bitmap images

The public skill keeps the idea, but removes the hard-coded local assumptions.

## Public scripts

### `pfc_sav_to_frames_template.py`
Use this inside PFC Python to restore a list of save states and export bitmaps.

### `export_animation_frames.py`
Use this outside PFC to normalize frame names and order.

### `export_animation.py`
Use this to build a GIF and, when available, an MP4.

## Why GIF is the default

GIF is the lowest-friction public output:

- easy to preview on GitHub
- no external video codec assumptions
- enough for a teaching workflow

MP4 is supported only as an enhancement.
