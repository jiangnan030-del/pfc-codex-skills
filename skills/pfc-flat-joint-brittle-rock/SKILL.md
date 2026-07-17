---
name: pfc-flat-joint-brittle-rock
description: Explain or structure flat-joint brittle-rock modeling for Chapter 5.4-5.5 tasks. Use when the user asks about FJM or FJM3D formulas, installation-gap effects, interlocking, rotation resistance, stress-dependent shear strength, prefabricated cracks, Brazilian tests, uniaxial or triaxial calibration, core discing, or how to plot flat-joint simulation results.
---

# PFC Flat Joint Brittle Rock

This skill turns Chapter 5.4-5.5 into a reusable route for flat-joint modeling, formula retention, test design, and plotting contracts.

## When to use

Use this skill when the user wants to:

- explain why flat-joint models improve on standard BPM
- retain core FJM or FJM3D formulas and parameter logic
- discuss Brazilian test, uniaxial tension, triaxial compression, or core discing
- analyze the effect of installation gap ratio, crack density, or local strength parameters
- organize plots for crack evolution, parametric studies, or discing patterns

## First rules

1. State which standard BPM limitation the flat-joint feature is solving.
2. Keep the contact-installation logic separate from the element failure logic.
3. When discussing parametric studies, define which parameter is being swept and which observable is measured.
4. For Brazilian and core-discing plots, state the loading path and stress state explicitly.
5. Reuse Chapter 5.5 conclusions as summary guidance, not as a standalone skill.

## Default workflow

### 1. Recover the mechanism upgrades

Read `references/theory.md` for the four main flat-joint upgrades: self-locking, rotation resistance, stress-dependent shear strength, and prefabricated cracks.

### 2. Retrieve the key formulas

Read `references/formulas.md` for installation-gap logic, element stress expressions, bonded-element strength envelope, and residual friction expression.

### 3. Plan the tests and plots

Read `references/plotting.md` for the default figure family:

- FJM structure schematic
- parameter-effect plots
- Brazilian-test figures
- crack-evolution figures
- core-discing pattern figures

### 4. Trace chapter provenance

Read `references/chapter-map.md` when you need the exact section, figure, or experiment mapping inside Chapter 5.4-5.5.

## Read next

- `references/theory.md`
- `references/formulas.md`
- `references/plotting.md`
- `references/chapter-map.md`

## Output contract

For a complete response or delivery, prefer these artifacts:

- a short explanation of which FJM mechanism fixes which BPM defect
- the core formula block with symbol definitions
- a test matrix for uniaxial, triaxial, Brazilian, or discing cases
- a figure list with explicit axes, inputs, and output names

## Local Contents

- `references/chapter-map.md`: topic and workflow routing for flat-joint brittle-rock cases.
- `references/formulas.md`: strength, stiffness, and calibration formulas.
- `references/plotting.md`: required plots and publication output conventions.
- `references/theory.md`: flat-joint model assumptions and interpretation notes.

