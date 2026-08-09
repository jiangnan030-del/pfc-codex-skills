# PFC modeling standard derived from pfc-code

Use this reference when creating, reviewing, or refactoring a PFC case. It converts repeated patterns in the pinned `pfc-code` corpus into a normative workflow contract.

The source corpus is evidence, not the final command authority. Confirm syntax against the target PFC version or `pfc-mcp` before execution. Do not copy upstream files into this repository while the upstream license is undeclared.

## Normative language

- **MUST** — required for a reproducible public workflow unless the case documents a justified exception.
- **SHOULD** — default good practice; deviations need a reason.
- **MAY** — optional pattern selected by case needs.

## Source retrieval before drafting

From the repository root, query the curated catalog:

```bash
python scripts/query_pfc_code_kb.py "<topic>" --dimension 2d
python scripts/query_pfc_code_kb.py "<topic>" --dimension 3d
```

For high-risk logic, inspect an evidence triad when available:

1. a tutorial for feature semantics;
2. an example for orchestration;
3. a verification case for a numerical check.

Record the pinned commit and paths used. Never turn one example's seed, tolerance, damping, rate, radius, bond gap, or material parameter into a universal default.

## 1. Case architecture

### MUST

- Use a thin driver (`run_all`, `doall`, or `master`) that owns case-level parameters and stage order, not detailed physics.
- Split build, compaction/equilibration, contact/bond installation, loading/test, and reusable FISH utilities into explicit stages.
- End callable data files with `program return` or the verified equivalent for the target version.
- Use relative paths only.
- Save named milestones and branch derivative tests from the same validated baseline.

### SHOULD

- Use dimension-explicit extensions (`.p2dat`, `.p3dat`, `.p2fis`, `.p3fis`) for new code.
- Keep generic `.dat`/`.fis` only when compatibility requires it, and declare the intended product/version in the header.
- Keep utility files side-effect-light: definitions first, explicit initialization from the driver/test.

Recommended stage names:

```text
00_scope / parameters
10_build_unbonded
20_compact_or_equilibrate
30_install_contacts_or_bonds
40_initialize_instrumentation
50_load_or_solve
60_export
70_verify
```

## 2. Deterministic model initialization

### MUST

- Start a standalone case from a clean model state.
- Declare target PFC product/version, dimension, units, stress sign convention, and seed.
- Define domain extents and boundary behavior explicitly.
- Define default CMAT behavior before generating objects whose contacts depend on it.
- Set density, damping, gravity, and particle/contact properties explicitly rather than relying on hidden GUI state.

### SHOULD

- Use a fixed random seed for calibration and regression baselines.
- Use separate seeds only for declared uncertainty ensembles.
- Keep generated particles away from vessel edges when the generation method can eject particles during relaxation.

## 3. Packing and equilibrium gate

### MUST

- Treat `ball distribute` output as an overlapping initial condition that requires relaxation.
- Use calm/cycle and an explicit solve criterion before declaring a specimen ready.
- Record the convergence measure and tolerance used.
- If density scaling is used for quasi-static preparation, restore automatic/physical timestep control before loading.
- Detect and report floaters when they can affect the macro response.

### SHOULD

- Store wall pointers or stable identifiers once and reuse them.
- Recompute current specimen dimensions/areas when servo target forces depend on changing geometry.
- Save an unbonded/equilibrated milestone before installing bonds.

A specimen is not ready merely because a fixed number of cycles completed.

## 4. CMAT and contact-state gate

The corpus makes a critical distinction:

- **CMAT** controls how new/future contacts are assigned.
- **contact commands / CMAT apply** modify current contacts.

### MUST

- State whether each parameter update targets future contacts, current contacts, or both.
- Use ordered optional CMAT slots and explicit ranges for multi-material cases.
- After changing a contact model, verify model name, property values, contact count, and group/range coverage.
- Treat model replacement as destructive to prior contact-state data unless the target-version documentation says otherwise.

### Bond installation

- Install bonds in a separate, auditable stage.
- If bonding at positive gap, ensure candidate inactive contacts exist. The verified pattern may require CMAT `proximity`, contact detection/`model clean`, CMAT application, and then `contact method bond gap ...`.
- Do not increase `bond gap` blindly to fix missing bonds; first inspect contact detection and the physical meaning of the gap.

## 5. State-transition reset gate

After packing, contact-model replacement, or bond installation:

### MUST

- Reset reference displacement before a test when strain should start at zero.
- Decide explicitly whether residual linear forces and contact moments are physical prestress or numerical leftovers.
- If they are leftovers, reset them using target-version-valid commands, cycle at least once, and re-equilibrate.
- Save the resulting bonded/initialized baseline.

### SHOULD

- Log contact counts before and after bonding.
- Check that the force reset does not erase intended confinement or prestress.
- Branch UCS, tension, triaxial, or sensitivity tests from the same baseline save.

## 6. Boundary and loading contract

### MUST

- Declare whether each axis is stress-controlled, force-controlled, velocity-controlled, strain-controlled, fixed, or free.
- Convert target stress to force using the current effective boundary area.
- Use a combined halt contract: target state plus equilibrium/stability criteria.
- Reset histories/displacement/reference dimensions immediately before loading.
- Separate preparation damping from loading damping and justify both.

### SHOULD

- Cap servo velocity/gain and update target force when geometry changes.
- Use a pilot run to check inertia, overshoot, and sign conventions before a full solve.
- For strength tests, stop using an explicit strain limit or a confirmed post-peak drop rule; label fallback stops as fallback, not physical peak confirmation.

## 7. Instrumentation and measurement contract

### MUST

- Define stress and strain equations, sign convention, sampling interval, and units.
- Record raw histories needed to reproduce reported metrics.
- Initialize measurement objects and event callbacks before the loading interval they describe.
- Keep saved-state names synchronized with exported stage labels.

### SHOULD

- Cross-check macro stress by at least two independent methods when practical:
  - boundary reaction / current area;
  - Love-Weber contact-force tensor over a declared volume;
  - measure-region stress.
- Cross-check strain with wall motion, measure-region integration, or gauge particles.
- Treat disagreement between estimators as a diagnostic, not as a plotting nuisance.

## 8. Fracture, fragment, and callback contract

### MUST

- Register bond-break callbacks explicitly and remove/re-register them safely on restore or reinitialization.
- Classify tensile and shear failures using documented event fields.
- Store event time, position, orientation, and source object references needed for later updates.
- Document callback cycle points; object creation, force application, and geometry updates have different legal/order-sensitive positions.

### SHOULD

- Batch expensive fragment recomputation instead of running it for every break.
- Bounds-check event geometry before updating fracture positions.
- Remove callbacks when their stage ends to prevent state leakage into later solves.

## 9. Python automation contract

### MUST

- Keep the PFC command layer and Python orchestration layer separately testable.
- Pin interpreter/environment requirements and declare generated outputs.
- Use array interfaces for bulk exchange when object-by-object traversal is a bottleneck.
- Register and remove callbacks deterministically.
- Avoid notebook-cell duplication in production scripts.

### SHOULD

- Return machine-readable metrics in addition to plots.
- Treat plots as derived artifacts; retain curve/source arrays.
- Use independent run directories for calibration candidates.

## 10. Verification and validation gate

### Verification MUST cover the numerical feature that carries the conclusion.

Examples from the corpus:

- measure/porosity against closed-form geometry;
- wave propagation before dynamic application models;
- bonded assembly comparisons that expose force-reset effects;
- thermal free expansion before constrained thermomechanical studies.

### Validation MUST compare the model with physical targets.

- Calibrate from one reproducible baseline.
- Match curves and failure mode, not only a peak scalar.
- Run seed/resolution/timestep/damping sensitivity where relevant.
- Keep calibration and confirmation runs separate.

## 11. Delivery manifest

Every delivered case SHOULD include a small manifest such as:

```yaml
pfc_product: PFC2D
pfc_version: "6.0"
dimension: 2d
units: SI
stress_sign: compression_negative
seed: 10001
entrypoint: run_all.p2dat
stages:
  unbonded: states/unbonded.p2sav
  bonded: states/bonded.p2sav
  peak: states/peak.p2sav
  final: states/final.p2sav
source_evidence:
  repository: https://github.com/jiangnan030-del/pfc-code
  commit: af774eb322e6c6bef18a56a0a69770e0e82c9bdf
  paths: []
syntax_verified_with: pfc-mcp-or-target-version-docs
```

## 12. Review checklist

- [ ] Version, dimension, units, sign, and seed declared
- [ ] Thin driver and explicit stage files
- [ ] CMAT/current-contact intent documented
- [ ] Packing convergence passed
- [ ] Bond/contact reset gate passed
- [ ] Boundary modes and halt criteria declared
- [ ] Histories and callbacks initialized before loading
- [ ] Two-method stress/strain cross-check considered
- [ ] Verification case chosen for the critical numerical feature
- [ ] Validation targets and acceptance tolerances declared
- [ ] Raw outputs, milestone states, and provenance manifest delivered
