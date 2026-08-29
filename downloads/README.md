# Book downloads

Current development builds of *Instruction Sets, Programs, and Proofs:
Semantics, Equivalence, and Optimization*.

| File | Format | Notes |
|---|---|---|
| `instruction-sets-programs-and-proofs.pdf` | 7×10 print PDF | 287 pages; fonts embedded; no Type 3 fonts; raster images pass the 300-ppi preflight gate |
| `instruction-sets-programs-and-proofs.epub` | EPUB 3 | 66 embedded images; ZIP integrity and EPUB container ordering checked; formal `epubcheck` pending |
| `title-page.png` | PNG | README preview linked to the complete PDF |

The files were built on 2026-08-29 from the manuscript committed immediately
before this distribution update. Build commands:

```sh
make -C book figures PNG=1
make -C book pdf
uv run --directory book scripts/build_epub.py \
  --cover build/cover/cover-front.png
```

## SHA-256

```text
82bf0521847098cb42665207747806d7c42352ddf525276e0e2b0e429eb01d55  instruction-sets-programs-and-proofs.pdf
a7be023e4c2a8ad17216ac6a92a0b635a7a7066700c120e9cced92cc9a285436  instruction-sets-programs-and-proofs.epub
1da8d69a02339d3349c047a8ad009dc4d0bcd9c8f7a79a03bf3281030700df32  title-page.png
```
