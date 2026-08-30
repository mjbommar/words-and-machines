# Book downloads

Current development builds of *Instruction Sets, Programs, and Proofs:
Semantics, Equivalence, and Optimization*.

| File | Format | Notes |
|---|---|---|
| `instruction-sets-programs-and-proofs.pdf` | 7×10 print PDF | 553 pages; fonts embedded; no Type 3 fonts; raster images pass the 300-ppi preflight gate |
| `instruction-sets-programs-and-proofs.epub` | EPUB 3 | Reflowable edition with embedded diagrams; `epubcheck` reports zero errors and zero warnings |
| `title-page.png` | PNG | README preview linked to the complete PDF |

The files were built on 2026-08-30 from the manuscript committed immediately
before this distribution update. Build commands:

```sh
sudo apt-get install epubcheck
make -C book pdf bleed ebook grayscale draft kdp-cover lulu-cover pdfx epub
```

## SHA-256

```text
96c6184d889d5a6a1b7d7ad87783ded5fc3c23574dc83072616941f41b05e775  instruction-sets-programs-and-proofs.pdf
7b592b671d4d8cc8a2ae7878f8f8df1b8eb59ade31e2bda95bf545c8bf1f38d5  instruction-sets-programs-and-proofs.epub
1da8d69a02339d3349c047a8ad009dc4d0bcd9c8f7a79a03bf3281030700df32  title-page.png
```
