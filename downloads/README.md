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
721db80f901e4847b359718ba8b13751338c18be4e06338a1b9ccea6e34b75ba  instruction-sets-programs-and-proofs.pdf
634e15e4434189a21796755eaae5ee8ea79a6ece284bb4901354b077dd39ddfa  instruction-sets-programs-and-proofs.epub
1da8d69a02339d3349c047a8ad009dc4d0bcd9c8f7a79a03bf3281030700df32  title-page.png
```
