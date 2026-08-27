# ADR 0013 — Math/logic callout set (color + icon), on the boxes module

## Decision
Add four semantic callouts aimed at mathematics, logic, and technical
books, alongside the five generic ones (ADR 0005): **`proofkit`**
(a definition or worked proof), **`tryit`** (a reader exercise),
**`goingdeeper`** (an optional depth track), and **`archive`** (a quoted
primary document). Unlike the single-accent generic family, each carries
a **distinct hue** *and* a **leading icon** (fontawesome5: drafting
compass / pencil-ruler / layer group / scroll), so a color edition tells
them apart at a glance and — because the hues collapse under
`\GrayscaleMode` while the icons remain — so does a black-and-white POD
interior. The EPUB converter maps each to `<aside class="callout
callout-KIND">` with a class-based CSS `::before` icon glyph; the four
print-only `\icon…` title macros strip to nothing in EPUB (the CSS badge
replaces them).

## Alternatives considered
- **Reuse the five generic callouts** (map Proof Kit → definition, Try It
  → example, etc.): lossy — readers of a technical book genuinely need to
  distinguish a proof from an exercise from a depth aside, and the generic
  titles erase that. It also fought real book projects that had already
  grown these four boxes independently (foundations-book).
- **New hues only, no icons**: fails the black-and-white POD interior,
  where all hues collapse to grays and the boxes become indistinguishable.
- **Icons only, monochrome (strict ADR 0006)**: works in B&W but throws
  away the high-quality *color* edition the portfolio also ships. Icons
  **and** hues serve both editions from one source.

## Rationale
Two editions, one source. Color print and ebook keep the hues; B&W POD
keeps the icons. `\GrayscaleMode` already collapses chroma in `colors.tex`
(ADR 0006) — the math/logic hues (`ml-blue/teal/amber`, plus the existing
indigo accent for `goingdeeper`) are added to that same collapse block, so
nothing chromatic reaches a grayscale press while the icon still
differentiates. The converter change is one dict entry per box plus a
four-macro strip, matching the "one place to add a callout" design of
ADR 0007.

## Consequences
- `latex/preamble/colors.tex`: `ml-*` hue ramp + grayscale collapse +
  four `callout-*-frame/bg` token pairs.
- `latex/preamble/boxes.tex`: loads `fontawesome5`; four `\newtcolorbox`
  on the shared `bookcallout` skeleton; `\iconProofKit…\iconArchive`.
- `epub/converter/handlers/blocks.py`: four entries in `CALLOUT_TITLES`.
- `epub/converter/handlers/inline.py`: the four icon macros strip to "".
- `epub/css/epub.css`: hue + `::before` icon per class (title text carries
  the accessible label; the glyph is presentational).
- `docs/architecture/authoring-contract.md`: the four names documented.
- Provenance: the foundations-book project, which grew Proof Kit / Try It
  / Going Deeper / From-the-Archive boxes before they were upstreamed here.
