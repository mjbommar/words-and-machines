# Directory Layout

```
book-template/
├── book.yaml                 # single source of truth (ADR 0002)
├── Makefile                  # standard target vocabulary (ADR 0006)
├── pyproject.toml, uv.lock   # converter package + shared deps (ADR 0010)
├── README.md                 # quickstart
├── CLAUDE.md                 # canonical AI instructions (ADR 0012)
├── AGENTS.md                 # one-line pointer to CLAUDE.md
├── .claude/agents/           # phased agent library
├── .github/workflows/        # CI: build + validate
│
├── latex/
│   ├── main.tex              # single entry doc, mode conditionals
│   ├── preamble/             # main, packages, fonts, colors, geometry,
│   │                         # styling, boxes, code, verse, commands, hyperref-last
│   ├── chapters/             # ch01-*.tex … (canonical content)
│   ├── frontmatter/          # halftitle, titlepage, copyright, dedication, epigraph
│   ├── backmatter/           # acknowledgments, about-author, colophon
│   ├── bib/references.bib
│   ├── figures/
│   ├── cover/cover.tex       # TikZ wrap cover (ADR 0008)
│   └── generated/            # metadata.tex, cover-vars.tex, edition.tex (GITIGNORED)
│
├── epub/
│   ├── converter/            # book-agnostic package (ADR 0007)
│   │   ├── __init__.py, core.py, handlers/, generators.py
│   ├── css/epub.css
│   └── fonts/                # populated per font profile at build time
│
├── scripts/                  # PEP 723, run via uv run (ADR 0010)
│   ├── generate_metadata.py  # book.yaml → generated/metadata.tex (+ validation)
│   ├── update_cover_vars.py  # page count → spine → generated/cover-vars.tex
│   ├── build_epub.py         # CLI wrapper around epub/converter
│   ├── check_style.py        # STYLE.md / STYLE-AI-TELLS.md enforcement
│   ├── check_prose.py        # repetition, n-grams, cross-chapter dup
│   ├── book_stats.py         # word counts, deltas per review round
│   ├── verify_citation.py    # URL gates (httpx) + --fetch browser fetch
│   │                         #   + Wayback archiving (verified=/archived=)
│   ├── sample_text.py        # random span sampler for review
│   └── init_book.py          # template instantiation
│
├── research/                 # per-chapter research folders (README contract)
├── outline/                  # book outline, narrative architecture
├── notes/                    # working notes, structure experiments
├── build/                    # ALL build output (GITIGNORED)
├── releases/                 # <date>-<printing>/ + SHA256SUMS (committed when shipping)
│
└── docs/
    ├── PLAN.md, ROADMAP.md
    ├── research/             # 15 source-project reviews (provenance)
    ├── decisions/            # ADRs 0001–0012
    ├── architecture/         # this folder
    ├── guides/               # STYLE, STYLE-CRAFT, STYLE-AI-TELLS, SPIRIT-template,
    │                         # CODE-STYLE, WRITING-PROCESS, REVIEW-QA, CITATIONS, RESEARCH
    └── publishing/           # KDP-TEMPLATE, METADATA-TEMPLATE, RELEASE-CHECKLIST, COVER-SPEC
```

Rules:
- Nothing under `build/` or `latex/generated/` is ever committed or hand-edited.
- Chapter files are named `chNN-slug.tex`; the slug list in `book.yaml` editions refers to `chNN` ids.
- `review-NN/` round folders are created under `docs/` as the book progresses.
