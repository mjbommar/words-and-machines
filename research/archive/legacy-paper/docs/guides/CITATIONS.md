# Citations

## The two systems

`paper.yaml` `citations.system` chooses:

- **`natbib`** (default) — arXiv-robust. `\bibliographystyle{plainnat}` +
  `\bibliography{bib/references}`; the `.bbl` is version-agnostic and ships
  trivially in `make arxiv`. `style: numeric` gives sorted-compressed numeric
  citations; `style: authoryear` gives author–year.
- **`biblatex`** — the scholarly house block: `biber` backend, `authoryear` or
  `numeric-comp`, `sorting=nyt`, `maxbibnames=99`. Loaded with `natbib=true`
  so the **same** `\citep`/`\citet` source compiles under either system.

Because both provide `\citep`/`\citet`/`\citeauthor`/`\citeyear`, your section
prose never changes when you switch systems.

## Citing

```latex
\citep{key}        % (Author, 2026) / [1]     — parenthetical
\citet{key}        % Author (2026) / Author [1] — textual
\citep[see][p.~4]{key}
```

Add entries to `latex/bib/references.bib`. Keep one `.bib`.

## Verify before you cite (house rule)

Open and read the actual source before citing it. Only after reading, stamp the
entry:

```bibtex
@article{smith2026,
  ...
  note = {verified 2026-07-23}
}
```

Never mark something verified from a search snippet or memory. A prior book in
this portfolio measured 57% URL rot/error before verification — the stamp is
what makes a bibliography trustworthy.

## URLs and DOIs

`xurl` breaks long URLs at any character (loaded before hyperref); biblatex is
configured with break penalties so URLs never gap a justified line. Prefer a
DOI (`doi = {…}`) over a bare URL when one exists.
