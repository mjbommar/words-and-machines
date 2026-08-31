# Executable artifact audit

This is the working verification record for the manuscript's executable
promises. It records evidence, not a blanket declaration that the book is
finished. Update it when a listing, object, manifest, report, checker, Axeyum
route, or publication conversion changes.

## 2026-08-31 baseline

The baseline was replayed against the fetched Axeyum `origin/main` revision
`2cb016f85694e6c475258a9f8e3c814685a1c55b`. Its editable Python package was
built in that checkout with the commands in `axeyum-guide/05-reproduce.md`.
GitHub Actions subsequently repeated the clean build and complete replay
against the newer Axeyum `main` revision
`0ed86ed17a1bd1ddc79c96144617563190faceec`; all 61 objects and 25 listings
still passed. This second result checks the documented current-main path as
well as the pinned historical revisions bound by individual manifests.

| Surface | Inventory | Verification |
|---|---:|---|
| Ledger objects | 61 | Schema, bindings, paths, digests, and every applicable checker executed |
| Active evidence manifests | 20 | Producer, positive checker, required result, and firing negative control replayed |
| A0 code listings | 8 | Exact printed text parsed, encoded through typed Axeyum instructions, and executed with a role-specific result assertion |
| RV64I code listings | 7 | Exact printed text assembled, decoded wholly by the selected Axeyum slice, and executed with role-specific assertions |
| x86-64 code listings | 6 | Exact printed text assembled, decoded wholly by the selected Axeyum slice, and executed with role-specific assertions |
| Python code listings | 2 | Exact Chapter 6 machine example and exact Chapter 14 manifest example executed unchanged |
| Shell listings | 1 | Exact command recognized; the enclosing `make check-run` invocation executes its route without recursive self-invocation |
| Deliberate pseudocode listings | 1 | Explicitly classified as pseudocode and checked against its declared logical steps; it is not presented as an ISA executable |
| Source-built diagrams | 66 | Every TikZ source compiled successfully to its named vector PDF; `validate-all` now rebuilds the full set before consuming it |
| PDF | 575 pages | Rebuilt; no undefined references or overfull boxes; fonts embedded, no Type 3 fonts, images at least 300 ppi, and two consecutive builds have identical SHA-256 digests |
| EPUB | 17 chapters plus front/back matter | Strict conversion, EPUBCheck, and Ace accessibility audit pass with zero findings; two consecutive builds have identical SHA-256 digests |

The twenty active routes are:

- A0 computations: `A0.comp.add-step-8`,
  `A0.comp.byte-roundtrip-8-16`, `A0.comp.decoder-roundtrip`,
  `A0.comp.equivalence-replay`, `A0.comp.scalar-minimality`,
  `A0.comp.state-codec`, `A0.comp.step-coverage`, and
  `A0.comp.word-package`;
- A0 theorem routes: `A0.thm.addition-flags` and
  `A0.thm.memory-frame`;
- A0 traces: `A0.trace.branch`, `A0.trace.memory-roundtrip`,
  `A0.trace.observation-separation`, and `A0.trace.run-classification`;
- cross-machine computations: `REL.comp.cross-isa-absolute-value` and
  `REL.comp.three-machine-xor`;
- RV64I routes: `RV64.comp.decoder-step` and `RV64.comp.source-pin`; and
- x86-64 routes: `X64.comp.decoder-step` and `X64.comp.source-pin`.

Run the baseline from the repository root:

```sh
AXEYUM=/path/to/current/axeyum make check-run
make -C book validate-all
make -C book preflight
```

## Defects found by this audit

1. The EPUB passed its old package validator while silently dropping most
   mathematics, semantic lists, exercises, tables, and ledger-backed artifact
   boxes. The converter now renders those constructs, declares MathML in the
   package manifest, treats unhandled content as a strict error, and has
   regression tests and a strict accessibility gate.
2. Print-oriented wrapping of the Chapter 6 `Conditions` constructor exposed a
   brittle physical-line substring check. The checker now ignores legal Python
   whitespace while retaining executable syntax and runtime checks.
3. The machine-example target claimed to execute every A0 listing but executed
   only the Chapter 6 addition. It now translates and executes all eight exact
   printed A0 listings and includes a mutation that changes an observed result.
4. LaTeX's default table-of-contents folio column was too narrow for long Roman
   front-matter page numbers. The shared style now reserves sufficient width;
   the rebuilt PDF has no overfull-box warnings.
5. The full publication gate consumed prebuilt diagram PDFs without rebuilding
   their 66 TikZ sources. All sources now compile successfully, and
   `validate-all` rebuilds them before the PDF and EPUB targets.
6. Rebuilding a diagram twice from unchanged source produced different PDF
   trailer identifiers. The figure wrapper now suppresses LuaTeX's optional
   trailer identifier; two consecutive builds of the same source have an
   identical SHA-256 digest.
7. The documented `AXEYUM=../axeyum` convention could select an incompatible
   research branch with stale build output. The actual primary checkout at
   `~/projects/personal/axeyum` does not contain the seven manifest-pinned book
   revisions and cannot import `axeyum.machine`. The new
   `make axeyum-checkout-check` gate verifies Git ancestry, the editable Python
   surface, and the Cargo replay wrapper before any machine-listing execution.
   The reproduction guide now creates a clean current-main worktree and never
   infers compatibility from a directory name.
8. Citation verification sent a false Firefox identity from an httpx client;
   CISA and Intel rejected that protocol fingerprint while accepting the
   truthful client identity. The checker now identifies its actual client.
   Three stale or redirecting bibliography URLs were replaced by direct
   primary-source URLs. Nine uncited template references were removed, and the
   release citation target now fails if any bibliography entry is unused.
9. Repository documentation promised a GitHub Actions build, but the workflow
   file was absent. `.github/workflows/build.yml` now runs the complete
   publication gate in the pinned TeX Live container and separately builds
   current Axeyum `main` before replaying all book evidence and controls.
10. A bot-walled source caused the citation gate to call a verified source
    dead even when its recorded Wayback snapshot was reachable. The verifier
    now reports the blocked origin and checks the immutable archive as an
    explicit fallback. Its archive path also resolves timestamp-less Wayback
    convenience redirects to dated snapshots before recording them.
11. `page-anatomy.pdf` was a tracked template leftover with no TikZ source and
    no manuscript reference. It was removed; the remaining 66 figure PDFs
    have one-to-one source files and are rebuilt by the release gate.
12. The first restored publication workflow reached Ace through its Electron
    command. Electron refuses to run as root in the TeX Live CI container, so
    accessibility validation failed before producing a report. The checker
    now prefers the pinned Ace 1.4.6 Puppeteer runner, which uses the configured
    system Chromium without weakening the strict zero-violation gate. Runner
    selection has regression tests.
13. `make release` checked strict publisher and ISBN metadata only after the
    expensive publication and ONIX steps. The strict metadata preflight now
    runs first, so an unconfigured release stops immediately with the exact
    missing field rather than appearing to fail late in artifact generation.
14. The clean TeX Live container reached the prose gate and exposed an
    undeclared runtime dependency: `pydetex` imports Tkinter even for this
    headless use, while the container omitted Python's Tk bindings. The CI
    toolchain now installs `python3-tk` explicitly rather than relying on a
    developer workstation's ambient packages.

## Distribution blockers

- PDF/X-1a generation and preflight pass.
- The 17 narration exports build without LaTeX residue.
- ONIX generation and strict release metadata correctly fail because the
  enabled print and EPUB formats have no assigned ISBNs. No identifier has
  been invented.
- The unsupported publisher name `Bommarito Press` has been removed from
  `book.yaml` and therefore from rebuilt drafts. Strict release metadata now
  requires a publisher supplied or confirmed by the author; an imprint will
  not be inferred from the template.
- All 60 cited URLs carry human verification stamps and dated archive
  snapshots. Bot-walled ACM, Hamming, and IEEE origins use explicit archive
  fallbacks rather than being treated as dead.

## Limits of this baseline

Passing this audit establishes only the scopes printed by the objects and
manifests. It does not turn finite computations into universal proofs, extend
the selected RV64I or x86-64 teaching slices, or close the open obligations
named in the ledger. Prose, citations, exercises, and reader proofs require
their own technical and editorial audits. A future listing or manifest must
extend the inventory and a firing control in the same change.
