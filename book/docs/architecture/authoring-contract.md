# Authoring Contract

Chapters may use **only** the vocabulary below. This is simultaneously (a) the style surface authors learn, (b) what the EPUB converter parses, and (c) what `make epub-check` audits. Anything outside it fails the coverage audit. (Pattern: the-last-book's PARSE CONTRACT.)

## Document structure
- `\chapter{Title}` — one per file, first content line
- `\section{...}`, `\subsection{...}` — no deeper levels in body text
- `\scenebreak` — typographic break (print: fleuron/blank; EPUB: `<hr class="scene"/>`)
- `\label{ch:...}` / `\ref{ch:...}` on chapters and sections only

## Inline semantics (macro ↔ EPUB class, defined in `preamble/commands.tex`)
| Macro | Print | EPUB |
|-------|-------|------|
| `\emph{...}` | italics | `<em>` |
| `\term{...}` | italics (first-use term) | `<i class="term">` |
| `\work{...}` | italics (book/film titles) | `<i class="work">` |
| `\person{...}` | small caps optional | `<span class="person">` |
| `\code{...}` | mono (module: code) | `<code>` |
| `\keyterm{...}` | bold-face term at its definition site | `<dfn class="keyterm">` |
| `\foreignphrase{...}` | italics | `<i class="foreign">` |

## Block environments
- `quotation` (+ `\attribution{...}`) — block quotes
- `callout` family (module: boxes): `keyidea`, `example`, `warning`, `sidebar`, `definition` — each takes an optional title; optional `importance=low|medium|high`
- math/logic callouts (module: boxes): `proofkit`, `tryit`, `goingdeeper`, `archive` — same interface as the callout family, but each carries a distinct hue **and** a leading icon (compass / pencil / layers / letter) so they stay distinguishable in a color edition and in grayscale POD. Use for a definition-or-proof, a reader exercise, an optional depth track, and a quoted primary document, respectively. To override the title, prepend the matching `\iconProofKit`/`\iconTryIt`/`\iconGoingDeeper`/`\iconArchive` macro, e.g. `title={\iconProofKit\ Proof Kit: Cantor's Theorem}`.
- `codelisting` (module: code): `\begin{codelisting}[language=python,caption=...]`
- `verse` module: `parallelverse` + `\stanzasync` (see preamble/verse.tex)
- `figure` with `\includegraphics` + `\caption` + `\label` (images in `latex/figures/`, prefer PDF/PNG); optional `\figalt{...}` sets the EPUB alt text (≤140 chars; `\figalt{}` = decorative). Without it the alt falls back to the caption; a figure with neither fails `make epub-check`
- `table` with `booktabs` rules only (`\toprule`/`\midrule`/`\bottomrule`)

## Notes & citations
- `\footnote{...}` — print footnote; EPUB chapter endnote with backlink
- `\autocite{key}` / `\textcite{key}` (authoryear) or `\scite{key}` (superscript preset)
- Every cited URL in `references.bib` carries `verified = {YYYY-MM-DD}` (see guides/CITATIONS.md)

## Forbidden in chapters
Raw TikZ, manual spacing (`\vspace`, `\\` outside tables/verse), font commands (`\textbf` allowed, `\bfseries` not), `\newcommand`, low-level TeX, literal title/author strings (use metadata macros), hard-coded colors.

`scripts/check_style.py` flags forbidden constructs; the converter's coverage audit catches anything unhandled.


## Object ledger bindings (this book)

Chapters may additionally use, and only these:

- `\obj{ID}` — typeset an object id.
- `\ObjStatus{ID}`, `\ObjScope{ID}`, `\ObjEvidence{ID}`, `\ObjTitle{ID}` — values read from `../objects/ID.json` via the generated `preamble/objects-generated.tex`. **Never type a status word by hand**; if the ledger says `open`, the book says `open`.
- `\begin{artifact}{ID} … \ArtifactScope{ID} \end{artifact}` — the box that accompanies every object with something to check.

Run `make ledger` at the repository root after editing any object record.
