# Theory

## Scope

This reference covers Chapter 5.1 and 5.2:

- brittle-rock mechanical traits and phenomena
- standard bonded-particle model basics
- why standard BPM struggles to match brittle-rock behavior

## Core brittle-rock traits

The chapter emphasizes three recurring traits for intact brittle rock:

- **High compression-tension contrast**: uniaxial compressive strength is much larger than tensile strength; the compression-tension ratio is often on the order of 10-20.
- **Large internal friction effect**: fractured blocks are not free to slide easily along failure surfaces.
- **Nonlinear strength envelope**: brittle-rock strength is better described by a nonlinear envelope such as the Hoek-Brown family rather than a purely linear Mohr-Coulomb line.

## Deep-rock phenomena

The chapter highlights three deep-rock mechanical phenomena that matter for modeling choices:

- **brittle-to-ductile transition under confining pressure**
- **zonal disintegration / zonal failure around excavations**
- **rockburst associated with unloading, stress concentration, and rapid energy release**

These phenomena explain why shallow-lab intuition is not enough for deep brittle rock.

## Standard BPM summary

Standard BPM idealizes rock as rigid circular or spherical particles connected by parallel bonds. The bond can transfer force and moment and fails when tension or shear criteria are exceeded.

This model is useful as a baseline because it is simple, efficient, and mechanically interpretable.

## Why standard BPM is insufficient for brittle rock

The chapter identifies three main shortcomings when standard BPM is calibrated against brittle-rock tests:

- **Compression-tension ratio too low**: the model can match UCS yet still predict tensile strength that is too large.
- **Internal friction too small**: the macroscopic friction angle from the model is often lower than expected for brittle rock.
- **Strength envelope too linear**: the fitted envelope does not naturally reproduce the nonlinear Hoek-Brown-like trend.

## Interpretation rule

Use standard BPM as the reference model for comparison, parameter sensitivity, and defect diagnosis. When the user needs better brittle-rock fidelity, route them toward equivalent-crystal or flat-joint style models.
