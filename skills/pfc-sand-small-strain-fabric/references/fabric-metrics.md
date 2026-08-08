# Fabric metrics and orientation plots

## Definitions

For contact unit normals `n`, calculate

```text
Rij = mean(n_i*n_j)
aij = (15/2)*(Rij-deltaij/3)
ad  = sqrt((3/2)*sum(aij*aij))
```

`ad` measures intensity; eigenvectors of `Rij` or `aij` provide principal directions. Always state whether the tensor uses contact normals or particle major axes: they are related but not identical.

Mechanical coordination removes non-load-bearing particles:

```text
Zm = (2*Nc-N1)/(Np-N1-N0)
```

Use the paper's counting convention consistently. For clumps, define whether `Np` means clumps, pebbles or physical grains; the recommended physical interpretation uses clumps/grains.

## Reproduction targets

| rm | Ani I: ad / Zm | Ani II: ad / Zm | Ani III: ad / Zm |
|---:|---:|---:|---:|
| 1.5 | 0.0250 / 8.430 | 0.3166 / 8.392 | 0.4977 / 8.421 |
| 2.0 | 0.0294 / 8.596 | 0.4058 / 8.651 | 0.6975 / 8.644 |
| 2.5 | 0.0333 / 8.691 | 0.5152 / 8.686 | 0.9165 / 8.703 |

The desired controlled-fabric signature is large `ad` variation and small `Zm` variation within each shape family.

## Plot rules

- Use identical azimuth/polar bins, radial scales and camera views.
- Keep the maximum frequency scale common across Ani levels.
- If each panel is normalized independently, say so explicitly.
- Export sample count, bin count, seed and normalization method.
- Add an equal-area heat map or polar-density curve to reduce 3D occlusion.
- Do not interpret a major-axis histogram as a force-chain or position plot.

Expected visual sequence: Ani I is near a spherical shell, Ani II a thick disk, and Ani III a thin equatorial disk.
