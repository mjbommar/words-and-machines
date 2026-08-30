# Full-textbook expansion plan

This plan turns the structural draft in `MASTER.md` into a complete textbook.
The 2026-08-29 pass produced a full-length structural draft, not a finished
textbook. Its former 4,000--7,000-word chapter bands were too shallow for the
subject. The revised ranges below are capacity estimates, not padding targets.
A chapter is complete only when its teaching and evidence obligations are met,
its omissions are deliberately routed, and its rendered pages work at the
chosen technical-textbook trim.

## Common chapter contract

Every numbered chapter must contain:

1. a concrete encounter that creates the need for the main concept;
2. brief, sourced history where it explains a live design constraint;
3. exact definitions in semantic boxes;
4. at least two worked examples, including one failure or non-example;
5. a reader proof or derivation for every load-bearing mathematical claim;
6. one visual that earns its space: diagram, table, trace, encoding map, or
   plot;
7. paired RV64 and x86-64 treatment at the scope permitted by pinned sources;
8. an honest Axeyum route or implementation obligation, with a firing negative
   control where machine evidence exists;
9. a boundary statement saying what the chapter does not model or prove; and
10. exercises that execute, break, prove, and transfer the idea.
11. the concept's sourced origin and the historical problem that shaped it;
12. the mathematical, logical, physical, and computer-science foundations
    needed to derive rather than memorize its behavior;
13. current practical and industrial consequences, including an explicit
    economic unit where cost is part of the claim; and
14. a coverage comparison against specifications, course expectations, and
    substantial textbooks, with every omitted neighboring topic routed or
    excluded explicitly.

Definitions, proofs, examples, figures, and exercises count only when they
advance the chapter's argument. Repetition and enlarged typography do not
satisfy a length band.

## Planning bands and owed assets

| Unit | Words | Central visual or worked asset |
|---|---:|---|
| Preface | 1,500–2,500 | proof-and-evidence promise |
| Introduction | 6,000–9,000 | claim-to-evidence chain and four-part route |
| 1. Words and Their Meanings | 9,000–12,000 | interpretation map and width-four cycle |
| 2. State | 9,000–12,000 | state inventory and observation projections |
| 3. Instructions and Operands | 10,000–14,000 | fetch/decode/execute transition |
| 4. Memory | 10,000–14,000 | byte layout, physical abstraction, valid ranges, and alias geometry |
| 5. Programs and Control | 10,000–14,000 | state trace and branch fork |
| 6. Encoding and Decoding | 12,000–16,000 | one constrained encoding from each ISA |
| 7. Data Movement and Address Formation | 12,000–16,000 | paired effective-address derivations |
| 8. Arithmetic, Logic, and Condition State | 12,000–16,000 | carry/overflow cases and flag flow |
| 9. Control Transfer | 12,000–16,000 | the same loop in A0, RV64, and x86-64 |
| 10. Procedures, Stacks, and ABIs | 12,000–18,000 | paired stack frames and preservation table |
| 11. Equivalence, Observation, and Refinement | 14,000–20,000 | relation hierarchy and counterexample trace |
| 12. Relating Different Instruction Sets | 14,000–20,000 | forward-simulation diagram |
| 13. Program Languages, Costs, and Minimality | 14,000–20,000 | candidate-language tree and cost comparison |
| 14. Evidence That Can Fail | 12,000–18,000 | trust ladder and negative-control anatomy |
| 15. One Algorithm, Three Machines | 18,000–25,000 | complete three-machine case study |
| 16. The Edge of the Model | 10,000–15,000 | omitted-state map and extension routes |

The projected full manuscript is roughly 200,000–280,000 words before the
bibliography and index. The final count must follow the teaching obligation,
not this arithmetic. At this scale, trim, binding, print economics, and whether
the material should become two volumes must be reviewed from rendered pages
rather than assumed in advance.

## Axeyum learning path

Axeyum appears as a gradually assembled evidence stack, not as an unrelated
software tutorial:

- Chapters 1–2: terms, states, observations, witnesses, and the current A0
  implementation boundary;
- Chapters 3–5: executable single steps, traces, replay, and negative controls;
- Chapters 6–10: source-pinned decoder and real-ISA adapter obligations;
- Chapters 11–12: solver counterexamples, state relations, and simulation;
- Chapters 13–14: bounded search, UNSAT evidence, certificate checking, hashes,
  manifests, provenance, and trust classes;
- Chapter 15: one end-to-end reproduction, only after the required routes
  exist;
- Chapter 16: what the current stack cannot establish.

No prose may describe a planned layer as implemented. Before revising an
Axeyum capability statement, inspect the live sibling checkout and its tests.

## Production sequence

1. Complete Introduction and Part I beside the stable A0 specification.
2. Pin authoritative RV64 and x86-64 revisions and expand Part II.
3. Implement or verify the required Axeyum semantic layers.
4. Expand Part III beside real evidence rather than placeholders.
5. Select and complete the Part IV scalar case study.
6. Reconcile front matter, cross-references, glossary terms, and exercises.
7. Run print, EPUB, prose, object, artifact, citation, and visual-review gates.

## Structural-draft record — 2026-08-29

The prose expansion reached the former planning bands. The Preface is
1,203 words; the Introduction is 3,792; and all sixteen numbered chapters fall
within their individual ranges. The numbered chapters total 83,565 words.
They contain 67 rendered figure assets, repeated definition and proof boxes,
paired RV64/x86-64 treatment where the chapter scope permits it, exercises,
boundary statements, and an Axeyum route or explicit implementation
obligation.

The depth pass was checked with `make check`, `make simplified`, `make pdf`,
`make test-formats`, and `make preflight`. The 7×10 print PDF is 287 pages;
fonts are embedded, no Type 3 fonts appear, and raster images meet the
300-ppi gate. Chapter contact sheets were inspected after each expansion pass.
All cited URLs are reachable and now carry verified and archived stamps.

This record establishes a complete structural spine, not complete breadth or
depth. The short chapters provide a base for the sequential depth pass; they
must not be represented as publication-ready merely because they met the old
bands. The live
Axeyum checkout still lacks the reusable A0, RV64, and x86-64 semantic packages
named by the manuscript. Planned machine routes remain identified as future
interfaces until their executors, controls, and evidence paths exist.

## First sequential depth-pass record — 2026-08-30

The Introduction and all sixteen numbered chapters now have chapter-specific
research contracts, source ledgers, and working timelines. No feature box in
those contracts remains unchecked. The chapter sources total 185,220 words
and contain 736 exercises. The longest chapter is the 18,005-word,
three-machine case study; the final boundary chapter contains 10,454 words and
54 exercises.

The depth pass integrated sourced conceptual history, mathematical and logical
foundations, and practical industrial or economic consequences into each
chapter's main explanation. `make -C book simplified` and
`make -C book check` pass with advisory warnings. The 7-by-10-inch print build
passes at 553 pages, and chapter contact sheets were inspected during the
sequential work. The EPUB generator produces an artifact, but the local
environment lacks `epubcheck`; EPUB conformance is therefore not recorded as
verified by this pass.

This record closes the first sequential content-expansion pass. It does not
declare the book publication-ready. Machine-produced A0, RV64, and x86-64
evidence remains outside the live Axeyum boundary stated in the manuscript.
Whole-book technical review, citation verification, accessibility, EPUB
conformance, preflight, and release gates remain separate publication work.
