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
f0760c898d45004dd0cf7f5cb7c703bd7ed5727b3a09ee07ac51a8ffadd60a7e  instruction-sets-programs-and-proofs.pdf
5a953c3572af6342a8e78081ecc8ea63cc3833f9a962c50d61390beed0b9e214  instruction-sets-programs-and-proofs.epub
ae9ffd5b1046078615fec6c373e8198750544e7bc9595c8ba2dc2ca9b284605d  title-page.png
```
