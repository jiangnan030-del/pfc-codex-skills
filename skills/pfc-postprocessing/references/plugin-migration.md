# Plugin Migration

This skill only absorbs post-processing-adjacent legacy tools. It does not try to swallow all modeling or geometry preprocessors.

## Included migration classes

### 1. Animation export
- historical source: `第二十二章 后处理\动图制作\outfig.py`
- old idea: restore save states and export bitmaps
- new public interface: `pfc_sav_to_frames_template.py` + `export_animation_frames.py` + `export_animation.py`

### 2. Ball export
- historical source: `导出二维颗粒信息.p2dat`
- old idea: dump particle positions, radii, IDs, and groups to a text file
- new public interface: `convert_legacy_ball_export.py` and standard ball-field CSV contracts

### 3. Contact export
- historical source: `导出接触信息命令流PFC5.0.txt`
- old idea: dump contact positions, normals, shear vectors, and forces to a text file
- new public interface: `convert_legacy_contact_export.py` and contact-orientation CSV used by `plot_rose.py`

### 4. Fabric and rose plotting
- historical source: old `plot_rose_picture_2D.exe` style tools
- old idea: consume contact or fracture direction data and output rose-like graphics
- new public interface: `plot_rose.py`

### 5. Stress cross / measurement grid
- historical source: Chapter 22 `应力十字架` and `测量圆参数分析`
- old idea: use measurement data to visualize stress and internal state
- new public interface: `plot_fields.py` plus the public stress and porosity contracts

## Migration record template

Each migrated example should record:

- `old_source`
- `input_contract`
- `output_contract`
- `replacement_script`
- `validation_example`

## Important limitation

Legacy `.exe` files are evidence of workflow intent, not public runtime dependencies.
