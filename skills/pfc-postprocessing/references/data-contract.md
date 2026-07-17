# Data Contract

This skill is public because it defines stable input files. If your files satisfy these contracts, the scripts can run on any machine.

## 1. Stress-strain curve

File: `stress_strain.csv`

Required columns:

- `strain`
- `stress_mpa`

Optional columns:

- `crack_num`

## 2. Ball field data

File examples:

- `plotdata_ball_fields.csv`
- `plotdata_ball_fields_peak.csv`

Required columns:

- `x`
- `y`
- `disp_x`
- `disp_y`
- `vel_x`
- `vel_y`
- `radius`

## 3. Stress field data

File examples:

- `plotdata_stress.csv`
- `plotdata_stress_peak.csv`

Required columns:

- `x`
- `y`

Accepted stress columns:

- `stress_xx` or `sxx`
- `stress_yy` or `syy`
- `stress_xy` or `sxy`

## 4. Porosity field data

File examples:

- `plotdata_porosity.csv`
- `plotdata_porosity_peak.csv`

Required columns:

- `x`
- `y`
- `porosity`

Optional columns:

- `coord_num`

## 5. Fracture orientation data

File: `plotdata_fracture_orientations.csv`

Required columns:

- `angle_deg`

Optional columns:

- `type` such as `tension` or `shear`
- `cx`
- `cy`

## 6. Contact orientation data

Accepted public contract:

- `angle_deg`
- optional `magnitude`
- optional `type`

This contract is used by migrated contact-export examples.

## 7. Animation frames

Accepted inputs:

- a directory of `.png` files
- filenames containing sortable integers, such as `jieguo_1.png`, `frame_0001.png`

The frame-ordering script will normalize them to a stable `frame_0001.png` pattern.
