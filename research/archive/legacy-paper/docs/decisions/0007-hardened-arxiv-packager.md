# ADR 0007 — The arXiv bundle is verified, not just assembled

## Decision
`make_arxiv.py` rebuilds cleanly, ships `main.bbl` + `00README.json`, inlines
`generated/metadata.tex` into `main.tex`, and — before tarring — compiles the
staged bundle standalone (twice) and asserts a PDF with zero undefined
references. Only a verified stage is packaged.

## Evidence
ioctl-census's `make_arxiv.sh` is the portfolio's best packager and does
exactly this; the other papers' inline `arxiv:` targets (tar vs zip, different
path lists) skip verification and are re-implemented per repo. The failure it
prevents is a bundle that builds for the author (with their `generated/` dir and
bib backend) but not on arXiv.

## Consequences
- The bundle needs no generation step or bib backend on arXiv's side.
- No shell-escape anywhere (code is pure listings), so it compiles under
  arXiv's AutoTeX.
