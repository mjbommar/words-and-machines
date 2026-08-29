# STYLE-PAPER — the authoring contract

The rules that keep sections consistent, convertible, and enforceable. `make
check` (`check_style.py`) enforces the hard ones on `latex/sections/`.

## Where prose lives

- Prose lives **only** in `latex/sections/NN_*.tex` (numbered; the house
  convention). Appendices are `A_*.tex`, `B_*.tex` after `\appendix`.
- The title block, disclosures, and preamble are template internals — don't put
  paper prose there.

## Macros you may use (and nothing lower-level)

| Macro | For |
|---|---|
| `\term{…}` | first use of a technical term (italic) |
| `\keyterm{…}` | a defined term at its definition site (bold, primary color) |
| `\work{…}` | titles of works |
| `\foreignphrase{…}` | non-English phrase |
| `\code{…}` | inline code / commands / flags (escape specials: `\_ \# \% \{ \}`, `\textbackslash`) |
| `\attribution{…}` | credit line closing a `quotation` |

Environments: the callout boxes (`keyresult`, `caution`, `note`, `databox`),
`codelisting` (highlighted block code), `figure`, `table`
(with `booktabs`/`threeparttable`/`siunitx`), `sidewaystable`/`sidewaysfigure`
(wide, landscape), the theorem family (`theorem`, `lemma`, `definition`,
`assumption`, `remark`), and `algorithm` + `algorithmic`.

## Hard rules (fail the build)

1. **No raw `\color`/`\textcolor`** in sections — use a semantic macro or a
   callout box. Color meaning is bound in `preamble/colors.tex`.
2. **No manual `\vspace`/`\hspace`** with hard-coded lengths — spacing is the
   preamble's job.
3. **No `\newcommand`/`\def`** in sections — macros live in
   `preamble/commands.tex`. Need a new one? Add it there.
4. **No `minted`/`--shell-escape`** — breaks arXiv. Use `codelisting`.
5. **No `TODO`/`FIXME`/`XXX`** left in prose.

## Advisory (warnings, not failures)

- Filler words (`very`, `really`, `clearly`, `obviously`, `simply`, `just`) —
  usually deletable.
- Bare URLs in prose — wrap in `\url{}` or cite.

## Numbers: one source of truth

Never hand-type a statistic in two places. Put each key figure in a
`\newcommand` number-macro in `preamble/commands.tex` (e.g.
`\newcommand{\nSamples}{12{,}345\xspace}`) and cite the macro, or derive it in
`paper.yaml`. This is the discipline the portfolio's best papers (ioctl,
needles, rfc) enforce; it stops prose and captions from drifting apart.

## Cross-references and citations

- Reference everything through `cleveref`: `\cref{fig:x}`, `\cref{tab:y}`,
  `\cref{sec:z}`, `\cref{eq:w}` — it supplies the right word and links.
- Cite with `\citep{key}` / `\citet{key}` (both bibliography systems provide
  them). See `docs/guides/CITATIONS.md`.
- Label convention: `fig:`, `tab:`, `sec:`, `eq:`, `alg:`, `thm:`, `def:`.

## Accessibility

Every `\includegraphics` needs an `alt=` key (≤ ~140 chars) — it is what
arXiv's HTML/LaTeXML conversion gives screen readers, and `make check` fails
without it. For a dense diagram, also describe it in the surrounding prose.
