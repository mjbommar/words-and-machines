# Book downloads

Current development builds of *Instruction Sets, Programs, and Proofs:
Semantics, Equivalence, and Optimization*.

| File | Format | Notes |
|---|---|---|
| `instruction-sets-programs-and-proofs.pdf` | 7×10 print PDF | 575 pages; four-part contents, glossary, and index; fonts embedded; no Type 3 fonts |
| `instruction-sets-programs-and-proofs.epub` | EPUB 3 | Reflowable edition with mathematics, exercises, artifact records, and embedded diagrams; EPUBCheck and strict Ace accessibility audit report zero findings |
| `title-page.png` | PNG | README preview linked to the complete PDF |

The files were rebuilt on 2026-08-31 after the executable-artifact and EPUB
semantic-preservation audit. Build and evidence commands:

```sh
AXEYUM=/path/to/current/axeyum-main make check-run
make -C book validate-all
```

## SHA-256

```text
f6e8ce688131261fe2c1ed54a03660249c6bfe3a875e0c0159dedfc1f17fabe0  instruction-sets-programs-and-proofs.pdf
971e26516bc7c03986cd8d3115dc0c2492484e59b700f1ecbb92b46b4d4e9402  instruction-sets-programs-and-proofs.epub
ae9ffd5b1046078615fec6c373e8198750544e7bc9595c8ba2dc2ca9b284605d  title-page.png
```
