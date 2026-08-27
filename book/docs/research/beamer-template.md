# Research Report: beamer-template

Source: `/home/mjbommar/projects/personal/beamer-template`

## 1. What It Is

A polished, MIT-licensed LaTeX Beamer presentation template: **127 pre-built slide commands across 14 focused modules**, with a Tailwind-inspired color system, a fallback-aware font stack, and a copy-and-configure workflow. `template/main.tex` is itself the documentation — a ~1500-line showcase deck that demonstrates every command grouped into 28 labeled parts (title variants, section dividers, stats, charts, diagrams, tables, Gantt, trees, scientific diagrams, UI mockups, decorative ornaments, closings). Also includes `experiments/animated-beamer/`, a separate proof-of-concept for motion design from LaTeX.

## 2. Structure

```
beamer-template/
├── TODO.md                        # Reorganization plan (shows the refactor methodology)
├── .github/workflows/latex.yml    # CI: xu-cheng/latex-action, lualatex + shell-escape,
│                                  #   uploads PDF artifact
├── template/                      # THE product — copy this dir to start a new deck
│   ├── main.tex                   # Showcase/reference deck demonstrating all 127 commands
│   ├── metadata.tex               # ALL user configuration in one file
│   ├── slides-catalog.json        # Machine-readable catalog of every command
│   ├── Makefile                   # latexmk wrapper, build/ output dir, watch mode
│   ├── latexmkrc                  # lualatex default, shell-escape, out_dir=build
│   ├── config/                    # 8 files: colors, packages, fonts, theme, templates,
│   │                              #   blocks, code, macros
│   ├── slides/                    # 14+ command libraries (title, section, closing, content,
│   │                              #   stats, comparisons, timelines, process, people, agenda,
│   │                              #   icons, tables, charts, diagrams, components, gantt,
│   │                              #   trees, scientific, frameworks, decorative)
│   ├── assets/, figures/          # User images / generated figures (.gitkeep placeholders)
│   └── build/                     # Gitignored output
└── experiments/animated-beamer/   # Separate uv project: moloch theme demo, Jinja2-templated
    │                              #   TikZ animations (.tex.j2), scripts/motion_video.py +
    └──                            #   zoom_video.py → render PDF pages → PNG frames → MP4
```

Separation of concerns is strict: `config/` = look and feel, `slides/` = reusable layout commands, `metadata.tex` = per-deck content variables, `main.tex` = the deck.

## 3. LaTeX / Beamer Craft

### Parameterization approach (the key transferable idea)

README Quick Start: `cp -r template/ my-presentation/`, edit `metadata.tex`, `make`. Everything a user must touch lives in `metadata.tex` as `\newcommand` definitions:

```latex
\newcommand{\PresentationTitle}{Beamer Template Showcase}
\newcommand{\PresentationSubtitle}{A Complete Gallery of Slide Variants}
\newcommand{\PresentationAuthor}{Your Name Here}
...
\newcommand{\LogoPath}{assets/logo.png}
\newcommand{\LogoHeight}{0.38cm}
\newcommand{\PresentationURL}{}      % Leave empty to disable
\newcommand{\PresentationDisclaimer}{}  % Leave empty to disable
```

Empty-string-means-disabled optional features, with `\makeatletter` fallbacks that substitute full title/author when short versions are empty. Slide layouts are *commands with positional arguments* (`\statslide{title}{{98\%}{Satisfaction}{2.5M}{Users}...}`), so content and layout never mix.

### Color system (`config/colors.tex`)

Full Tailwind-style computed scales — every family has 11 steps (50–950), with usage guidance and regeneration notes in comments:

```latex
% Each color family has 11 steps: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950
%   - 50-200:  Light tints (backgrounds, subtle highlights)
%   - 300-400: Medium tints (borders, secondary elements)
%   - 500:     Base color (primary usage)
%   - 600-700: Darker shades (hover states, emphasis)
%   - 800-950: Deep shades (text on light, high contrast)
%
% To rebrand: modify the base hex values in the Python calculation comment,
% regenerate scales, and update the \definecolor lines.
%
% Scales computed via HSL manipulation in Python:
%   - Lightness: 50=97% -> 950=8%
```

Families: Slate (cool gray), Stone (warm gray), Primary (teal-blue, base #005073), Secondary, Accent (orange), Success/Warning/Danger. On top sit semantic aliases (`TextPrimary`, `TextMuted`, `BackgroundMain`, `BrandPrimary`, `BrandSecondary`, `BrandAccent`, `SemanticDanger`...) — slides reference only semantics, so rebranding = changing base values in one file.

### Fonts (`config/fonts.tex`) — graceful degradation across engines

```latex
% Font stack priority:
%   Sans:  Fira Sans -> TeX Gyre Heros -> Latin Modern Sans
%   Mono:  JetBrains Mono -> Fira Code -> Latin Modern Mono
%   Math:  Latin Modern Math (or default)

\ifluatex
  \IfFontExistsTF{Fira Sans}{
    \setsansfont{Fira Sans}[
      Scale=0.95,
      BoldFont={Fira Sans SemiBold},
      ...
    ]
  }{ \IfFontExistsTF{TeX Gyre Heros}{...}{ \setsansfont{Latin Modern Sans}[...] } }
  ...
\else\ifxetex
  ... XeLaTeX config ...
\else
  ... pdfLaTeX lmodern fallback ...
\fi\fi
```

Note the deliberate `BoldFont={Fira Sans SemiBold}` (semibold as bold — softer headings) and semantic font commands (`\headingfont`, `\codefont`, `\accentfont`) plus a size scale (`\textsmaller`, `\textlarger`, `\texthuge`) so slides never hardcode font switches.

### Theme (`config/theme.tex`) — availability-aware theme selection

```latex
\IfFileExists{beamerthememoloch.sty}{%
  \usetheme{moloch}%
}{%
  \IfFileExists{beamerthememetropolis.sty}{%
    \usetheme[numbering=fraction, progressbar=foot,]{metropolis}%
  }{%
    \usetheme{default}%
  }%
}
```

Then every Beamer semantic slot is explicitly mapped to the palette (`\setbeamercolor{structure}{fg=BrandSecondary}`, blocks, progress bar, alerts, etc.), so the design survives even on the `default` theme.

### Other craft worth noting

- `fitbox` / `fitboxframed` / `fitcard` environments (tcolorbox `fitting` library) — auto-scale text to fixed dimensions, "great for content cards where you need predictable sizing regardless of content length." Useful anywhere AI generates variable-length content into fixed layouts.
- Print-friendly grayscale chart variants (`\piechartslidegray`, `\barchartslidegray`) alongside color ones.
- `slides-catalog.json` — machine-readable index of all 127 commands with arg counts, per-file counts. Explicitly built so tooling/AI can discover available layouts without parsing TeX.
- `TODO.md` documents the refactor from 11 grab-bag files ("content-layouts.tex (29 items) - grab bag") to 14 focused modules with consistent naming — a useful record of how the modularization decisions were made.
- Build: `Makefile` wraps latexmk (`-lualatex -output-directory=build`), `watch` via `-pvc`, `xelatex` alternate target; `latexmkrc` sets `$pdf_mode = 4`, shell-escape for SVG/Inkscape, `$out_dir = 'build'`, clean extension list. GitHub Actions builds the PDF on every push and uploads it as an artifact.
- `experiments/animated-beamer/`: moloch + fontspec + unicode-math + microtype minimal deck; cached "heavy figures" compiled once to PDF then `\includegraphics`'d; Jinja2 `.tex.j2` animation templates driven by Python (`motion_video.py --fps 60 --seconds 8`) rendering PDF→PNG frames→ffmpeg MP4.

## 4. Transferable to a Book Template

1. **Copy-and-configure workflow**: the entire product is one directory you `cp -r`, with a single `metadata.tex` holding every user-editable value (title, author, logo, optional features that disable when empty). A book template should have the exact analogue: `metadata.tex`/`book-config.tex` with title/subtitle/author/ISBN/trim-size, consumed by title page, copyright page, headers, cover, and PDF metadata.
2. **config/ vs slides/ vs content split** → maps to book-template `preamble/` (look) vs feature environments (reusable structures) vs `chapters/` (content). Both existing books already do this partially; beamer-template does it most cleanly and documents it best.
3. **Tailwind computed color scales + semantic alias layer** — the most rigorous of the three color systems (complexity-book's is the same idea with fewer steps). Rebrand = edit base values in one file.
4. **Font fallback chains** with `\IfFontExistsTF` and engine detection — makes the template build on machines without the preferred fonts installed; neither book project does this (both hard-require their fonts).
5. **Availability-aware package/theme loading** (`\IfFileExists`) — same portability idea applied to themes.
6. **`slides-catalog.json` pattern** → a book template could ship an `environments-catalog.json` of feature boxes/commands with arg signatures so AI assistants can discover the design system programmatically.
7. **The showcase document**: `main.tex` doubles as living documentation demonstrating every component. A book template should ship a `sample-chapter.tex` that exercises every box, epigraph, figure style, and command.
8. **CI PDF build** (`.github/workflows/latex.yml` with `xu-cheng/latex-action@v3`, lualatex, shell-escape, artifact upload) — trivially portable; neither book repo has CI.
9. **Auto-fit boxes** for fixed-geometry content, and the cached-heavy-figures pattern (compile TikZ once → include PDF) for build-time control.

Minor caution: the slide macros' multi-brace positional argument syntax (`{{n1}{l1}{n2}{l2}...}`) is compact but error-prone to author by hand; for a book template, keyval interfaces (as complexity-book's `importance=` boxes use) age better.
