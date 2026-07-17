---
name: pfc-equivalent-crystal-model
description: Build or explain an equivalent crystal model for brittle rock. Use when the user asks about crystal-network construction, equivalent crystalline modeling, Chapter 5.3 formulas, fine-scale parameter calibration, crack-pattern validation, Hoek-Brown fitting, compression-tension ratio analysis, or how to plot equivalent-crystal simulation outputs.
---

# PFC Equivalent Crystal Model

This skill turns Chapter 5.3 into a reusable route for equivalent-crystal modeling, formula retention, validation logic, and plotting contracts.

## When to use

Use this skill when the user wants to:

- explain what an equivalent crystal model is
- rebuild the crystal-network and particle-model overlay workflow
- retain core fine-scale parameters and validation logic
- compare simulated crack patterns with laboratory observations
- fit a Hoek-Brown style nonlinear strength envelope

## First rules

1. Keep model construction, parameter assignment, and validation as separate stages.
2. Distinguish crystal-body behavior from crystal-network interface behavior.
3. When discussing validation, pair crack-pattern evidence with stress-strain evidence.
4. State clearly whether a figure comes from direct tension, uniaxial compression, or triaxial compression.
5. Use the equivalent crystal model as a brittle-rock fidelity upgrade over the standard BPM baseline.

## Default workflow

### 1. Recover the modeling logic

Read `references/theory.md` for the crystal-network generation logic, particle assembly, equivalent-crystal overlay, parameter meaning, and test-validation route.

### 2. Retrieve the key formulas

Read `references/formulas.md` for the retained Hoek-Brown fitting expression and the chapter's compression-tension interpretation.

### 3. Plan validation and figures

Read `references/plotting.md` for the default figure family:

- stress-strain curves
- crack-distribution figures
- laboratory vs simulation comparison
- Hoek-Brown fit
- UCS/TS ratio summary

### 4. Trace chapter provenance

Read `references/chapter-map.md` when you need the exact chapter section or figure scope behind the model narrative.

## Read next

- `references/theory.md`
- `references/formulas.md`
- `references/plotting.md`
- `references/chapter-map.md`

## Output contract

For a complete response or delivery, prefer these artifacts:

- a concise equivalent-crystal construction summary
- the retained nonlinear strength-fit formula and symbol definitions
- a validation checklist covering crack pattern, stress-strain, and compression-tension ratio
- a figure list with inputs and output filenames

## Local Contents

- `references/chapter-map.md`: workflow and chapter mapping for equivalent-crystal modeling.
- `references/formulas.md`: calibration and interpretation formulas.
- `references/plotting.md`: expected figure and source-data patterns.
- `references/theory.md`: model assumptions, limitations, and physical interpretation.

