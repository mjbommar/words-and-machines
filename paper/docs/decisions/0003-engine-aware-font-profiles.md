# ADR 0003 — Engine-aware font profiles

## Decision
Four font profiles (`libertinus`, `newtx`, `lmodern`, `plex`) each render on
pdflatex (8-bit packages) AND xelatex/lualatex (fontspec + unicode-math), from
one `typography.font_profile` knob. `plex` is OpenType-only and errors clearly
on pdflatex. Fonts are loaded by family/package NAME, never file path.

## Evidence
The portfolio splits: arXiv papers use pdflatex + CM/Libertine; the SSRN
cluster uses lualatex + fontspec Libertinus. arXiv's FAQ names pdflatex/xelatex
as safe and omits lualatex, so the SAME paper must be able to switch engines
without a font rewrite. `libertinus` uniquely has both a pdflatex package and
an OTF, making it the flagship default that works everywhere.

## Rejected
- fontspec-only (lualatex) like the SSRN cluster: strands the arXiv-safe
  pdflatex path.
- One hard-coded font: the survey shows real papers want CM, Libertine, Times,
  and Plex.

## Consequences
- `make doctor` checks package resolution (pdflatex) or fontconfig resolution
  (Unicode engines) for the active profile, catching "font not found" before a
  full build.
