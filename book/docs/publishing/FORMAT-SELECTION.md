# Choosing the format for this book

The canonical print edition uses **7×10 inches, white paper, and 11-point
type**. This is a technical-textbook format: it gives proofs, equations, code,
and diagrams more room than 6×9 without turning ordinary paragraphs into long
lines. It also permits a same-size KDP hardcover edition.

The shared authority for dimensions, KDP page limits, hardcover compatibility,
and recommended type sizes is `scripts/trim_catalog.py`. Metadata validation,
the doctor, cover calculations, and format tests all import that catalog.

## Why 7×10

- The text measure remains capped at about 33 em; extra sheet width becomes
  useful outer space instead of tiring line length.
- It accommodates proof displays, state diagrams, instruction encodings, and
  side-by-side machine examples.
- KDP supports both paperback and hardcover at this trim.
- It retains the ordinary black-and-white paperback ceiling of 828 pages on
  white paper, leaving room for the fuller textbook this manuscript is meant
  to become.

An 8×10 paperback would not receive a lower KDP large-trim printing rate, would
mostly add outer margin under the present geometry, and has no matching KDP
hardcover. Use it only if later diagrams or comparison tables demonstrate a
real need for the wider sheet. Use 8.25×11 for a deliberately large
paperback/hardcover textbook pair, normally with 12-point type.

## Available preset families

| Family | Presets | Typical use |
|---|---|---|
| Compact | 5×8, 5.5×8.5 | Short prose, portable editions |
| Trade | 6×9 | General nonfiction and ordinary prose |
| Technical | 7×10, 7.5×9.25, 8×10 | Textbooks, code, equations, diagrams |
| Large textbook | 8.25×11, 8.5×11 | Workbooks, manuals, large tables |

KDP treats widths above 6.12 inches or heights above 9 inches as large trim.
Of these presets, KDP hardcover supports 5.5×8.5, 6×9, 7×10, and 8.25×11,
with a 75–550-page range. Paperback limits depend on trim and paper and are
checked from the catalog. Current costs and marketplace eligibility must be
rechecked before release; they are not frozen in repository code.

After changing trim, paper, type size, or enabled formats, run
`make test-formats`, `make doctor`, and render representative prose, proof,
code, table, and figure pages before accepting the change.
