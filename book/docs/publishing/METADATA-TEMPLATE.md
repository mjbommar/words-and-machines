# Publishing Metadata Dossier — Template

Fill-in dossier for ISBN registration (Bowker), cataloging (PCIP), category
selection (BISAC), keywords, and comp-title pricing. Everything you decide
here lands in `book.yaml` (ADR 0002) — this worksheet is where you work it
out; `book.yaml` is where it lives; the copyright page, OPF, and KDP form are
generated from it.

All concrete values below are **EXAMPLES** to show shape and register —
replace every one.

---

## 1. ISBN assignment table

One ISBN per format per edition. Buy through Bowker MyIdentifiers
(https://www.myidentifiers.com/) — the 10-pack is the economic minimum for a
multi-format book. KDP's free ISBN is an alternative for print only, but then
Amazon is the publisher of record and PCIP options narrow.

| Format | Edition | ISBN | `book.yaml` key | Assigned (date) | Registered at Bowker |
|---|---|---|---|---|---|
| Paperback | full | | `identifiers.isbn_print` | | ☐ |
| EPUB | full | | `identifiers.isbn_epub` | | ☐ |
| Hardcover | full | | `identifiers.isbn_hardcover` | | ☐ |
| Paperback | *(named edition, ADR 0011)* | | `editions.<name>.isbn_print` | | ☐ |
| EPUB | *(named edition)* | | `editions.<name>.isbn_epub` | | ☐ |

Rules:

- A new **format** or a new **edition** (changed content selection, new title
  suffix) needs a new ISBN. A corrected **printing** of the same edition does
  not (see [`RELEASE-CHECKLIST.md`](RELEASE-CHECKLIST.md)).
- Kindle gets an ASIN from Amazon regardless; the epub ISBN still goes in the
  EPUB `dc:identifier` (the converter reads it from `book.yaml`).
- After assigning, complete the Bowker record: plain-text description (§6),
  Bowker subject categories (§3 note), cover JPEG (`make cover-image`),
  price, page count, pub date.
- LCCN (`identifiers.lccn`): optional for self-published work; the PCIP block
  (§2) stands in for CIP in house practice.

---

## 2. PCIP block (Publisher's Cataloging-in-Publication)

Printed on the copyright page. Model on Library of Congress CIP formatting;
LCSH subject headings and LCC/DDC classification can be drafted from close
comp titles' CIP data (look inside comps' copyright pages) and refined with
LC's online tools (id.loc.gov for LCSH, LCC outline, dewey.info for DDC).

Fill-in skeleton:

```
Publisher's Cataloging-in-Publication Data

Names: [Lastname, Firstname], author.
Title: [Title] : [subtitle, lowercase] / [Author Name].
Description: First edition. | [City, State] : [Publisher], [Year]. |
    Includes bibliographical references [and index]. |
    [Other notes: series, parallel text, glossary, ...]
Identifiers: ISBN [print ISBN] (paperback) | ISBN [epub ISBN] (ebook)
Subjects: LCSH:
    [Heading 1].
    [Heading 2].
    [Heading 3--Subdivision].
Classification: LCC [class number] [cutter] [year] | DDC [number]--dc23
```

> EXAMPLE (structure only — a parallel-text translation with added
> contributors and an "Other titles" uniform-title line):
>
> ```
> Names: [Lastname, Firstname], author. | [Original author], author. |
>     [Translator name], translator.
> Other titles: [Uniform title]. English & [Language].
> Description: First edition. | Parallel text in [Language] and English. |
>     Includes glossary.
> Subjects: LCSH:
>     [Author]--Translations into English.
>     [Language] language--Readers.
> Classification: LCC PA0000.A0 X00 2026 | DDC 000/.00--dc23
> ```

Cross-check: the ISBNs in the PCIP block are generated from `book.yaml`;
`make doctor` flags copyright-page/`book.yaml` drift.

---

## 3. BISAC selection worksheet

Pick up to 3 codes for `classification.bisac` (KDP takes 3 categories; Bowker
and other services also read these). Browse the full list at BISG.

Strategy that has worked: **lead with the differentiator, not the crowded
default category**; pair one broad code (visibility) with two niche codes
(ranking potential).

| Option | Primary | Secondary | Tertiary | Positioning rationale |
|---|---|---|---|---|
| A | | | | |
| B (recommended) | | | | |
| C | | | | |

> EXAMPLE row: `POL044000` (Public Policy / Science & Technology Policy) +
> `BUS070060` (Industries / Energy) + `COM004000` (AI / General) — leads with
> the political-economy angle instead of drowning in the COMPUTERS shelf.

Also record:

- **Bowker subject categories** (Bowker's dropdown is simpler than BISAC):
  Primary ________ / Secondary ________
- **Amazon browse paths** for the 3 KDP picks (the picker uses browse trees,
  not raw BISAC): 1. ________ 2. ________ 3. ________
- Post-launch: request extra categories via KDP Support if the initial picks
  underperform.

---

## 4. Keyword worksheet (7 slots, ≤50 chars each)

Rules: target what readers *type*, not what the book *is*; never repeat words
already in the title, subtitle, or chosen category names; phrases beat single
words; fill all 7 slots (`classification.keywords`).

| # | Keyword phrase | Chars (≤50) | Audience / search intent |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |

Slot archetypes worth covering (from shipped-book keyword sets):

1. Core topic, reworded to avoid title/subtitle words
2. Audience/community angle ("for general readers", "for beginners")
3. Adjacent bestseller's vocabulary (ride an established search stream)
4. Problem the reader is trying to solve
5. Concrete nouns/jargon insiders search for
6. A niche only this book serves (low volume, high conversion)
7. Genre positioning ("narrative nonfiction …", "field guide …")

> EXAMPLE entries: `data center electricity grid energy` (33) — core topic
> minus title words; `chip war semiconductors geopolitics` (34) — comp-title
> vocabulary. Count characters (`echo -n '...' | wc -c`).

Review keyword performance 30–60 days post-launch; swap underperformers.

---

## 5. Comp-title pricing table

Build within ~30 days of launch (Amazon prices drift). Tier the comps:
**Tier 1** direct competitors, **Tier 2** adjacent genre/format, **Tier 3**
aspirational shelf-mates. For each, note what differentiates your book.

| Tier | Title (comp) | Author | Pages | Paperback | Kindle | Hardcover | Differentiator vs. this book |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 1 | | | | | | | |
| 2 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |

> EXAMPLE row: Tier 1 | *Chip War* | Chris Miller | ~464 | $18–20 | $14–16 |
> $28–32 | semiconductor history, no community-impact angle.

Then decide (and copy into `book.yaml` `publishing.*`):

| Format | List price | Printing cost (KDP calc) | Royalty/copy | Notes |
|---|---|---|---|---|
| Paperback | $ | $ | $ | 60% × list − printing ([`KDP-TEMPLATE.md`](KDP-TEMPLATE.md) §7) |
| Kindle | $ | — | $ | 70% band is $2.99–$9.99; price above it knowingly |
| Hardcover | $ | $ | $ | Lulu/Ingram if not KDP |

Also state the **market gap** in two or three bullets — which niche none of
the comps fills. This paragraph tends to become the spine of the KDP
description and the Bowker annotation.

---

## 6. Descriptions and bio (one source, three renderings)

`book.yaml`'s `book.description` is the master. Derive and keep with the
dossier:

- **HTML description** (KDP, ≤4,000 chars, allowed tags only — rules in
  [`KDP-TEMPLATE.md`](KDP-TEMPLATE.md) §5)
- **Plain-text description** (Bowker/ISBN, library metadata — no HTML, no
  smart typography)
- **Short description** (~250–350 chars, for limited fields) and a
  **one-liner** (~60–70 chars)
- **Author bio**, long (Author Central/Bowker) and short (back cover) — the
  short one must match the back-cover text generated from metadata macros
- Optional: 3–4 **taglines** for marketing reuse

Checklist before filing anything externally:

- [ ] Every field above matches `book.yaml` (regenerate, don't retype)
- [ ] Character counts recorded for description (<4,000) and each keyword (≤50)
- [ ] Plain-text variants contain no HTML entities or curly quotes
- [ ] The same ISBN never appears attached to two different formats
