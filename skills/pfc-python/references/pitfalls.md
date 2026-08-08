# Pitfalls

- **Per-object loops are slow**: with hundreds of thousands of particles use `ballarray` / `cfdarray`
  vectorized reads and writes instead of `for b in itasca.ball.list()`.
- **Wrong callback insertion point**: different `order` values fire at different stages of the solve
  cycle. The seepage example uses `order=1` and throttles with `it.cycle() % N == 0`.
- **Mesh vertex ordering**: `ca.create_mesh` needs FiPy `_cellVertexIDs` reordered as
  `(0, 2, 3, 1, 4, 6, 7, 5)` to match PFC element vertex conventions, otherwise element geometry is wrong.
- **Unit consistency**: PFC is unitless. Permeability, viscosity and density must match the geometric
  unit system (the bundled examples use SI).
- **`.format()` placeholder mismatch**: multi-line command strings with many injected coordinates are
  easy to get wrong; count placeholders against arguments.
- **Version syntax drift**: command syntax differs across PFC versions. Validate against the official
  documentation for the target version before running.
- **Scope of PFC's built-in CFD**: it supports 3D one-way seepage influence analysis only. Genuine
  two-way coupling needs external solvers (OpenFOAM / FiPy), with Python as the data-transfer layer.
