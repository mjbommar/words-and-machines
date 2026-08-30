# Book downloads

Current development builds of *Instruction Sets, Programs, and Proofs:
Semantics, Equivalence, and Optimization*.

| File | Format | Notes |
|---|---|---|
| `instruction-sets-programs-and-proofs.pdf` | 7×10 print PDF | 565 pages; four-part contents, glossary, and index; fonts embedded; no Type 3 fonts |
| `instruction-sets-programs-and-proofs.epub` | EPUB 3 | Reflowable edition with embedded diagrams; `epubcheck` reports zero errors and zero warnings |
| `title-page.png` | PNG | README preview linked to the complete PDF |

The files were rebuilt on 2026-08-30 after the four-part spine, heading
hierarchy, glossary, and index revision. Build commands:

```sh
sudo apt-get install epubcheck
make -C book pdf bleed ebook grayscale draft kdp-cover lulu-cover pdfx epub
```

## SHA-256

```text
cec06554f7d4007ab24666699c61fa229e10509427b48b1b41fb347bb20911ad  instruction-sets-programs-and-proofs.pdf
91bdfd2d96f90dfaebd267a4d155816f014c030ead6304dc2e113d82760da447  instruction-sets-programs-and-proofs.epub
1da8d69a02339d3349c047a8ad009dc4d0bcd9c8f7a79a03bf3281030700df32  title-page.png
```
