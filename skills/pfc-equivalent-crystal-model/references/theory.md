# Theory

## Scope

This reference covers Chapter 5.3 and its application of the equivalent crystal model to brittle rock.

## Why this model exists

The chapter introduces the equivalent crystal model to address the key weaknesses of the standard BPM. The main idea is to represent:

- **crystal bodies** with a particle-based bonded model
- **crystal network interfaces** with a smooth-joint style interface representation

This adds irregular microstructural organization and better interlocking behavior without abandoning a DEM workflow.

## Model-construction route

The chapter's construction logic can be reused in four stages:

1. **Build a crystal-network structure** over the computational domain.
2. **Build a particle assembly** with the target specimen size and particle-size range.
3. **Overlay the crystal network on the particle model** so the assembly is partitioned into adjacent crystal bodies.
4. **Replace contacts crossing crystal interfaces** with interface-style contacts, forming the equivalent crystal model.

## Material interpretation

Use this interpretive split:

- particle-bonded regions represent the crystal body behavior
- interface contacts represent the crystal-network boundary behavior

Both components can deform and fail, and both are needed to reproduce the observed brittle-rock response.

## Parameter logic

The chapter uses fine-scale mechanical parameters to match macroscopic behavior. The important point is not the exact value alone but the calibration role:

- particle or bond stiffness affects deformation response
- bond strength controls crack initiation and local failure
- interface properties control boundary sliding, separation, and crack routing

## Validation route

The chapter validates the model through:

- direct tension or axial tension response
- uniaxial compression response
- triaxial compression response under different confining pressures
- crack-pattern comparisons with laboratory failure images
- nonlinear strength-envelope fitting
- compression-tension ratio comparison against granite-like brittle rock

## Key conclusion

The equivalent crystal model improves brittle-rock realism because it can reproduce:

- stronger brittleness in tension/compression contrast
- more realistic crack routing
- nonlinear strength-envelope behavior compatible with Hoek-Brown style fitting
