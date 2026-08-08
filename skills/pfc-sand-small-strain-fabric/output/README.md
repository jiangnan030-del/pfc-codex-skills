# SSF output contract

Runtime outputs are not source files. Use this layout:

```text
output/
├── logs/         # suite and per-case logs
├── saves/        # ssf_{dim}_{material}_{stage}_{case_id}.sav
├── histories/    # named ssf/cyclic/* and ssf/state/* exports
├── figures/      # loops, G0 fits and orientation plots
└── manifest.csv  # one auditable row per case
```

Manifest fields are declared in `../config/cases.yaml`. Every case records its
input/output saves, PFC version, seed, configuration, status, elapsed time and
code hash. Keep large generated data out of Git.
