---
name: pfc-brittle-rock-bpm
description: Explain brittle-rock mechanics traits and the limits of the standard bonded-particle model. Use when the user asks about brittle rock formulas, UCS/TS contrast, deep-rock phenomena, BPM assumptions, parallel-bond failure criteria, strength envelopes, or how to organize figures for Chapter 5.1-5.2 style analysis.
---

# PFC Brittle Rock BPM

This skill turns Chapter 5.1-5.2 into a reusable guide for brittle-rock mechanics interpretation, standard BPM explanation, formula extraction, and figure planning.

## When to use

Use this skill when the user wants to:

- summarize the three hallmark traits of brittle rock
- explain deep-rock brittle behavior, zonal failure, or rockburst context
- retain standard BPM assumptions and parallel-bond formulas
- compare standard BPM against laboratory brittle-rock behavior
- design figures for UCS/TS ratio, strength envelopes, or BPM mechanism sketches

## First rules

1. Separate observed brittle-rock behavior from what the standard BPM can actually represent.
2. Keep the high-compression low-tension contrast explicit; the UCS/TS ratio is a primary signal.
3. When quoting formulas, define symbols and the failure condition, not only the final expression.
4. Treat the standard BPM as a baseline model with known deficiencies, not as the final answer for brittle rock.
5. For plots, state whether the figure is conceptual, laboratory-derived, or simulation-derived.

## Default workflow

### 1. Frame the brittle-rock problem

Read `references/theory.md` to recover the chapter's three brittle-rock traits, three deep-rock mechanical phenomena, and the reason brittle rock is hard to represent with a simple bonded-particle model.

### 2. Retrieve the core formulas

Read `references/formulas.md` for the standard BPM parallel-bond stress expressions, geometric terms, and tension/shear failure criteria.

### 3. Plan the figures

Read `references/plotting.md` for the default figure families:

- UCS vs TS contrast
- linear vs nonlinear strength envelope comparison
- BPM force-displacement or constitutive sketch
- defect-to-figure mapping for standard BPM limitations

### 4. Trace back to the chapter

Read `references/chapter-map.md` when you need the exact section, figure, or formula provenance inside Chapter 5.1-5.2.

## Read next

- `references/theory.md`
- `references/formulas.md`
- `references/plotting.md`
- `references/chapter-map.md`

## Output contract

For a complete response or delivery, prefer these artifacts:

- a short statement of brittle-rock traits and deep-rock phenomena
- a formula block for BPM stress and failure criteria with symbol notes
- a figure list with axis definitions and input requirements
- a note that standard BPM underestimates brittle-rock compression-tension contrast and nonlinear envelope behavior

## Required Inputs

Ask for these if missing:

- PFC version and 2D/3D target;
- specimen size, loading path, and boundary-control assumptions;
- BPM/contact model family and initial micro-parameter ranges;
- macro calibration targets such as UCS, modulus, peak strain, and fracture pattern;
- available scripts, references, or existing case files to audit.

## Local Contents

- `references/chapter-map.md`: chapter-level routing and topic map.
- `references/formulas.md`: reusable formulas and parameter relationships.
- `references/plotting.md`: plotting expectations for brittle-rock BPM outputs.
- `references/theory.md`: theoretical background and modeling assumptions.

