# Directory layout

```
paper-template/
├── paper.yaml                 # single source of truth
├── Makefile                   # self-documenting build (make help)
├── pyproject.toml             # (scripts are PEP-723 self-contained; uv run)
├── CLAUDE.md / AGENTS.md / GEMINI.md   # AI instructions (CLAUDE is canonical)
├── README.md · LICENSE
├── latex/
│   ├── main.tex               # single entry point (all variants)
│   ├── preamble/              # modular preamble (fixed load order)
│   │   ├── main.tex           #   the loader
│   │   ├── packages.tex       #   encodings, core packages, bib system
│   │   ├── fonts.tex          #   engine+profile font dispatch, microtype
│   │   ├── colors.tex         #   layered color system + grayscale collapse
│   │   ├── styling.tex        #   sections, running heads, spacing, draft
│   │   ├── boxes.tex          #   callout boxes        (module: boxes)
│   │   ├── code.tex           #   listings             (module: code)
│   │   ├── commands.tex       #   inline macros, apparatus, algorithms
│   │   └── hyperref-last.tex  #   xurl + hyperref + cleveref (LAST)
│   ├── frontmatter/titleblock.tex   # title, authors, abstract, JEL/keywords
│   ├── backmatter/disclosures.tex   # funding, COI, data, AI (SSRN)
│   ├── sections/              # CANONICAL prose — NN_*.tex, A_*.tex (appendix)
│   ├── figures/               # built figure PDFs (gitignored) + src/*.tikz
│   │   ├── figure-preamble.tex     #   shared preamble for standalone TikZ
│   │   └── src/*.tikz               #   TikZ sources (committed)
│   ├── tables/                # optional generated/hand tables (\input)
│   ├── bib/references.bib     # the one bibliography
│   └── generated/            # MACHINE-WRITTEN (gitignored; .gitkeep only)
├── scripts/                   # all uv run, zero install
│   ├── generate_metadata.py   #   yaml -> metadata.tex + 00README.json
│   ├── init_paper.py          #   personalize a fresh clone
│   ├── build_figures.py       #   matplotlib figures (scripts/data/*.csv)
│   ├── build_tikz.py          #   standalone TikZ figures
│   ├── make_arxiv.py          #   verified arXiv source bundle
│   ├── export_arxiv_metadata.py #  ARXIV-SUBMISSION.md (form + checklist)
│   ├── export_ssrn_metadata.py#   SSRN-METADATA.md dossier
│   ├── check_style.py         #   authoring-contract lint (sections/)
│   ├── check_refs.py          #   undefined refs/cites, alt-text, dead sections
│   ├── wordcount.py · doctor.py · package_release.py
│   └── data/*.csv             #   figure data (committed, reproducible)
├── docs/
│   ├── PLAN.md
│   ├── architecture/          # build-system, config-schema, directory-layout
│   ├── decisions/             # ADRs (numbered)
│   └── guides/                # STYLE-PAPER, FIGURES, CITATIONS, SUBMISSION
├── .claude/agents/            # AI-assisted paper workflow
└── .github/workflows/build.yml  # CI on TL2025-historic (matches arXiv)
```

## The two rules that matter most

1. **Never edit `latex/generated/` or `build/`** — regenerate from `paper.yaml`.
2. **Prose lives only in `latex/sections/`** — everything else is machinery.
