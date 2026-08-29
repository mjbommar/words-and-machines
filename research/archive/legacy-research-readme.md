# Superseded evidence-led research index

Everything the book and paper rest on, in the order it was produced. Two kinds of material:

| Folder | What | Trust |
|---|---|---|
| `axeyum/` | Documents copied verbatim from the [axeyum](https://github.com/mjbommar/axeyum) repository: the five-target survey folder, the open-problems programme contract, the lane status file (the day-by-day record of what actually landed), the phase-8 track, and the ADRs behind every artifact in `../artifacts/`. | Repository record. ADR evidence sections were re-verified here where an artifact ships (see `../objects/`). |
| `surveys/` | Ten literature sweeps by Opus 5 research agents (2026-08-25 and 2026-08-27), reproduced verbatim. Each report flags its own unverified items; **treat every bound as of its date and re-check currency before citing.** Google Scholar via SerpApi proved unreliable for exact-title queries; Google web plus direct fetch was the working instrument. | Secondary. Not refereed. Several agents ran out of search budget and say so. |
| `certifiable-unknowns.html` | The first survey's ranked deliverable (2026-08-25), as published. | Snapshot. |
| `prior-art-spivak-of-isa.md` | The search for an existing from-first-principles, everything-proved treatment of an ISA. | Searched 2026-08-27; negative with controls. |

## Reading order

1. `axeyum/open-problems-2026-08/README.md` — the five targets and the three escape hatches.
2. `surveys/05-simd-permutation-lowering.md` and `surveys/06-superoptimization-frontier.md` — the two that decide the paper's related-work section.
3. `surveys/08-compiler-certification-gap.md` — the Franchetti–Püschel correction and the base rate of wrong "proved optimal" claims.
4. `surveys/10-isa-design-and-other-isas.md` — the RISC-V findings that Part IV reproduces.
5. `surveys/09-venue-and-reviewer-map.md` — where the paper goes and what its reviewers will say.

## What was *measured* rather than read

Three things in this corpus are computations, not citations, and the book relies on them:

- The ISA-design agent's exhaustive reproductions of the RISC-V bit-logic table and Bitmanip Tables 2.2/4.1 (`surveys/10-…`, §B). **Re-implemented and re-run in this repository**: `../scripts/bitlogic_bfs.py`, `../scripts/byte_perm_bfs.py`; results in `../artifacts/riscv/`.
- The engineering agent's in-session check of NIST's 29-AND AES S-box circuit against FIPS 197 on all 256 inputs (`surveys/02-…`).
- The capability report's read of axeyum's frontier, reconstruction routes, and evidence formats (`surveys/04-axeyum-capability-report.md`) — every claim there carries a `file:line`.
