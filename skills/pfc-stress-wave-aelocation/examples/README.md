# Example Cases

Runnable-style templates are under `../scripts/canonical/`.

## 1D Chain Wave-Speed Check

Use `chain_1d.p2dat` with `ricker_source.p2fis` to validate:

- source waveform
- arrival time at two monitors
- measured P-wave speed
- numerical dispersion at the chosen frequency

## 2D Wavefield Scaffold

Use `hex_2d.p2dat` as a starting scaffold for a hexagonal 2D lattice. Complete lattice generation and monitor placement for the target PFC version before production use.

## AE Source Location

Workflow:

1. Export sensor waveforms from PFC.
2. Compute pairwise time delays with cross-correlation.
3. Prepare a cluster JSON file with `ref`, `s2`, `s3`, `t21`, and `t31` for each cluster.
4. Run:

```bash
python ../scripts/canonical/ae_locate.py --clusters clusters.json --out ae_location_result.json
```

## Validation Checklist

- `lambda / D >= 10`
- damping is zero or explicitly justified
- timestep is fixed and much smaller than source period
- boundary reflections are outside the analysis window or absorbed
- sensor traces are exported with consistent sampling interval
- low-quality cross-correlations are flagged
- nearly parallel cluster-pair rays are rejected
