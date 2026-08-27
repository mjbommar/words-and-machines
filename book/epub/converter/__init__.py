"""Book-agnostic LaTeX -> EPUB 3 converter (ADR 0007).

Converts the constrained LaTeX dialect defined in
docs/architecture/authoring-contract.md into a valid EPUB 3 package.
All metadata comes from build/epub-metadata.json (generated from
book.yaml by scripts/generate_metadata.py, ADR 0002) — this package
contains zero book-specific strings.

Provenance: fresh rewrite of the converters shipped with the
datacenter / htsd / wiki / RFC books (docs/research/), keeping the
handler-registry design and the RFC book's generators approach while
dropping every book-specific handler.
"""

from .core import build_book

__all__ = ["build_book"]
__version__ = "0.1.0"
