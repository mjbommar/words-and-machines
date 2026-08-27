# LaTeX Pipeline

## Entry point
`latex/main.tex`: `book` class, options from base_size, `twoside,openright`. Reads `generated/metadata.tex` first, then `preamble/main.tex`, then front/main(edition)/back matter. Mode conditionals (`\BleedMode` etc.) are consulted inside preamble modules, never in chapters.

## Preamble modules (load order fixed — ADR 0005)
1. **packages.tex** — geometry, fancyhdr, titlesec, tcolorbox, booktabs, graphicx, microtype, csquotes, biblatex, etoolbox; NO hyperref here
2. **fonts.tex** — engine detection; profile dispatch (`libertinus`/`garamond`/`plex`); family names only (no paths); oldstyle text figures, lining in tables; CJK/emoji fallback via luaotfload when lualatex; tuned microtype protrusion per profile (RFC book's table for plex)
3. **colors.tex** — primitive scales → semantic tokens → component bindings; `\GrayscaleMode` collapses accents to grays here
4. **geometry.tex** — trim presets; interior: `inner=0.875in, outer=0.625in, top/bottom≈0.75/0.875in` at 6×9 (KDP-safe, from the-last-book/datacenter); `\BleedMode` adds 0.125in bleed via `paperwidth/paperheight` + shifted layout; `\EbookMode` symmetric margins, no gutter
5. **styling.tex** — spelled-out chapter word (`\chapterword` — datacenter pattern), right-aligned two-line chapter heads; fancyhdr styles `frontmatterstyle`/`mainmatterstyle`/`backmatterstyle` (author verso / title recto running heads, folio placement); widow/orphan penalties (10000), `\raggedbottom` policy for verse books; `\enable/\disablecleardoublepage`
6. **boxes.tex** — tcolorbox family, `importance=` keyval scaling frame weight/color, `lines before break=3` smart breaking (complexity pattern)
7. **code.tex** *(module)* — listings with `lstnewenvironment`, the `\lst@AddToHook{Init}{\catcode`\#=12}` fix (vibe-coding), per-language styles, `breaklines`, 72-char guidance, `promptcode`/`outputcode` environments
8. **verse.tex** *(module)* — paracol `\columnratio{0.70}`, `\stanzasync`, hanging indents, per-5 line numbers, `\setchapterheads` markboth workaround (iliad/ovid)
9. **commands.tex** — semantic inline macros (authoring-contract.md table)
10. **hyperref-last.tex** — hyperref + bookmark; print builds force black links; `\EbookMode` enables colored links; PDF metadata from `\BookTitle`/`\BookAuthor`

## Bibliography
biblatex + biber. Preset `authoryear`: `style=authoryear, maxcitenames=2, maxbibnames=99` (house block byte-identical in ai-law-finance + ai-professional-services). Preset `superscript`: numeric-superscript `\scite` with two-column footnotesize bibliography (datacenter). Selected via metadata macro from book.yaml.

## Invocation
latexmk, `-output-directory=build/latex`, engine per book.yaml, `-usepretex` for mode flags, distinct `-jobname` per variant (`book-print`, `book-bleed`, `book-ebook`, `book-grayscale`, `book-draft-YYYYMMDD`). Three passes handled by latexmk; biber integrated.
