# `book.yaml` Schema

Validated by `scripts/generate_metadata.py` (JSON Schema embedded in the script). Placeholder scanning: any string equal to or containing `TODO`, `FIXME`, `[...]`-bracketed tokens, or `XXX` fails generation unless `--allow-placeholders`.

```yaml
# ── Identity ────────────────────────────────────────────────
book:
  title: "TODO Your Title"
  subtitle: ""                      # optional
  author: "TODO Author Name"
  author_short: ""                  # for running heads; default = author
  publisher: "TODO Publisher"
  imprint: ""                       # optional
  year: 2026
  edition_statement: "First Edition"
  copyright_holder: ""              # default = author
  description: >-                   # back cover + OPF + KDP listing
    TODO one-paragraph description.
  language: en-US

# ── Identifiers ─────────────────────────────────────────────
identifiers:
  isbn_print: ""                    # required by --strict (make release) if formats.print
  isbn_epub: ""                     # required by --strict (make release) if formats.epub
  isbn_hardcover: ""                # optional
  lccn: ""                          # optional

# ── Classification (KDP/Bowker dossier) ─────────────────────
classification:
  bisac: ["TODO000000"]             # up to 3
  keywords: []                      # up to 7, ≤50 chars each (KDP limit)
  audience: "trade"                 # trade | academic | young-readers

# ── Physical / formats ──────────────────────────────────────
formats:
  print: true
  epub: true
  hardcover: false

trim:
  preset: "7x10"                    # compact: 5x8 | 5.5x8.5
                                    # trade: 6x9
                                    # technical: 7x10 | 7.5x9.25 | 8x10
                                    # large: 8.25x11 | 8.5x11
                                    # 7x10 is this book's selected format;
                                    # 8.25x11 and 8.5x11 normally use 12pt
  paper: "white"                    # white | cream | groundwood |
                                    # standard-color |
                                    # premium-color (sets KDP spine formula)
  bleed: 0.125                      # inches, KDP standard

# ── Typography ──────────────────────────────────────────────
typography:
  font_profile: "libertinus"        # libertinus | garamond | plex
  engine: "lualatex"                # lualatex | xelatex (verse profile needs xelatex)
  base_size: 11                     # pt: 10 | 11 | 12

# ── Citations ───────────────────────────────────────────────
citations:
  style: "authoryear"               # authoryear | superscript (endnote-style trade)
  bibliography_title: "Sources"

# ── Style profile ───────────────────────────────────────────
style:
  profile: "narrative-nonfiction"   # genre profile layered over STYLE.md,
                                    # or "" for base. Files ship in
                                    # docs/guides/styles/: narrative-nonfiction
                                    # | practical-guide | technical-handson
                                    # | young-readers | verse-translation.
                                    # check_style.py merges the profile's
                                    # banned-list deltas + tell_budget +
                                    # sentence_hard_max over the base lists.
                                    # Unknown name fails generate_metadata.

# ── Simplified Book English (advisory vocabulary policy) ─────
# Validated by scripts/check_simplified.py, not generate_metadata.py. Every
# key is optional; unknown keys fail so a typo cannot silently weaken a check.
simplified_english:
  enabled: true                     # true | false
  terms:                            # admitted subject terms; `not` gates drift
    - term: "data center"
      not: ["datacenter", "data-center"]
  abbreviations: ["FERC"]          # bare forms allowed without expansion
  names: ["LEXIS"]                 # official all-cap names, not acronyms
  ignore: ["with respect to"]      # accepted substitution exceptions
  allow: ["interconnection"]       # extra core words
  deny: ["utilize"]                # extra error-grade word bans
  thresholds:
    unintroduced: warn              # error | warn | off
    undefined_abbreviation: warn    # error | warn | off
    unintroduced_min_uses: 2        # positive integer
    gloss_window: 400               # positive integer, characters
    max_findings_per_file: 40       # positive integer

# ── Modules (feature toggles) ───────────────────────────────
modules:
  code: false                       # listings + CODE-STYLE rules
  verse: false                      # paracol parallel text (forces xelatex)
  boxes: true                       # semantic callout family

# ── Editions (ADR 0011) ─────────────────────────────────────
editions:
  full:
    default: true
    frontmatter: [preface]           # optional authored matter before the Introduction
    introduction: ch00               # optional; unnumbered in print, first in EPUB
    chapters: [ch01, ch02, ch03]
  # essential:
  #   title_suffix: "Essential Edition"
  #   isbn_print: ""
  #   isbn_epub: ""
  #   chapters: [ch01, ch03]

# ── Publishing ──────────────────────────────────────────────
publishing:
  platforms: ["kdp"]                # kdp | lulu-paperback | lulu-hardcover
  kindle_drm: false                 # bool; effectively permanent per title —
                                    # DRM-free Kindle books are buyer-
                                    # downloadable EPUB/PDF (since 2026-01-20)
  ai_disclosure:                    # KDP questionnaire, per content type
    text: generated                 # none | assisted | generated
    images: none                    #   "generated" = AI created it (even
    translations: none              #   with heavy edits) -> must disclose;
    detail: ""                      #   "assisted" = AI edited your work ->
                                    #   no disclosure. Optional extent note.
    statement: >-                   # printed on copyright page + EPUB
      TODO disclosure statement.
  # (a bare string is also accepted: it becomes the statement, with the
  #  per-type answers left to classify at upload time)
  price_usd_print: null
  price_usd_ebook: null
```

## Outputs of `generate_metadata.py`

1. **`latex/generated/metadata.tex`** — `\BookTitle`, `\BookSubtitle`, `\BookAuthor`, `\BookAuthorShort`, `\BookPublisher`, `\BookYear`, `\BookISBNPrint`, `\BookISBNEpub`, `\BookDescription`, `\BookAIDisclosure`, `\BookEditionStatement`, trim/bleed dimension macros, plus `\BookHasSubtitle` etc. boolean flags.
2. **`latex/generated/introduction.tex`** — optional edition Introduction,
   included while the book is still in front matter.
3. **`latex/generated/edition.tex`** — ordered `\input{chapters/...}` list for
   the selected edition (`--edition NAME`).
3. **`build/epub-metadata.json`** — normalized dict consumed by `epub/converter/generators.py`.
4. **`docs/publishing/KDP.md`** — dossier skeleton, only with `--emit-kdp` (won't overwrite an edited file).

All LaTeX/EPUB sources reference these macros/values only — never literal strings (ADR 0002).
