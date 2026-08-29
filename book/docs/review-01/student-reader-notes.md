# Introduction and Part I: student-reader pass

Date: 2026-08-27

Reader stance: a systems programmer who knows assembly syntax but has not
studied formal semantics.

## Reading experience

- The opening makes the central problem tangible: familiar notation does not
  determine machine behavior.
- A0 feels useful once its artificiality is explained. The draft avoids asking
  the reader to admire a toy processor for its own sake.
- The word chapter is easiest to follow when one pattern is calculated before
  a formula appears. The extension proof is denser than its neighbors and
  needs a slow read, but it earns the real-ISA question that follows.
- State and observation produce the first strong conceptual payoff. The
  scratch-register example explains why “same result” is not enough.
- The full effect of add is a good bridge from familiar assembly to semantics.
  Naming PC and flags makes the hidden work visible.
- Memory is clearest at the concrete four-byte store. The valid-range premise
  and atomic trap should stay close to the round-trip claim.
- The branch example finally makes the earlier condition bits useful. The four
  bounded-run outcomes are important, but the distinction between bound
  exhaustion and nontermination may need repetition in later chapters.
- Repeated object IDs are tolerable because the surrounding prose explains
  them. They would become intrusive if later drafts add more ledger detail.

## Revisions prompted by this pass

1. Give exact initial register values only when they affect a trace.
2. Define technical terms at first use instead of relying on the glossary or
   the reader's systems background.
3. Keep each chapter's last paragraph as a genuine question opened by the
   preceding result.
4. Preserve the candid Axeyum boundary, but never let it interrupt a worked
   argument before the reader receives its consequence.
5. In the next part, call back to the same four-instruction A0 program when
   decoding its bytes; a new example would make the reader rebuild too much
   context.
