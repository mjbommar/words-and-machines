# ADR 0002 — paper.yaml is the single source of truth

## Decision
One `paper.yaml` holds all identity and configuration; `generate_metadata.py`
derives `latex/generated/metadata.tex` (macros + `\ifPaper…` flags),
`build/arxiv-readme.json`, and drives the SSRN dossier. LaTeX never hard-codes
title/author/keywords/JEL. Placeholder values (`TODO`/`[bracketed]`) fail the
build.

## Evidence
The SSRN-cluster papers already prototyped this (a `commands.tex` with
`\keywords`/`\jelcodes`, per-paper `\hypersetup` metadata); promoting it to a
generator removes the hand-maintained title/author/abstract that drifted from
the `SSRN-METADATA.md` dossier in practice.

## Consequences
- The dossier and the built PDF can never disagree (both derive from yaml).
- `main.tex` reads `generated/metadata.tex` before `\documentclass` (base size
  and two-column feed the class options).
- `make arxiv` inlines the generated file so the bundle needs no generation step.
