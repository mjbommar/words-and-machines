# 04. Minimal SIMD shuffle sequences

**One-line:** a question every compiler answers heuristically thousands of times a day, for
which **no minimality result has ever been published on any ISA** — and where checking an
improvement needs no solver at all.

| | |
|---|---|
| Statement | For a byte permutation `π` of a vector register, `L(π)` = minimum instruction count over an ISA's shuffle set |
| Known | **nothing.** No table of `L(π)` exists for AVX2, NEON, SVE, or RVV |
| Gap | unmeasured — not even the Cayley-graph diameter is published |
| Encoding | pure SAT over lane tags, a few thousand variables per candidate length |
| Positive certificate | evaluate on **one** input vector of 32 distinct tags |
| Negative certificate | DRAT, natively |
| Effort | weeks to a first real result |
| Risk | medium-high — unclaimed for a reason we do not know |
| Audience | LLVM, Intel/Arm optimization guides, dav1d, simdjson, every BLAS micro-kernel |

## The problem

Fix an ISA's shuffle instruction set. For AVX2 that is `vpshufb`, `vpermd`, `vpermq`,
`vperm2i128`, `vpunpck{l,h}*`, `vpalignr`, `vpblendd`. Given a target byte permutation `π`
of a 256-bit register, `L(π)` is the minimum number of instructions realizing it.

`L` is unknown for AVX2, NEON, SVE and RISC-V Vector. **Even `max_π L(π)` — the diameter of
the shuffle Cayley graph — is unpublished for any of them.**

Note the scope boundary: AVX-512 VBMI's `vpermt2b` does arbitrary byte permutation in one
instruction, so it collapses the problem. The open cases are precisely the ISAs without it,
which is most deployed hardware.

## Why it is still open

Two reasons, and the second is the interesting one.

**The instruction set is large and `vpshufb`'s control operand is itself a 32-byte vector.**
So concrete enumeration is impossible and symbolic control constants reintroduce an
exists-forall problem. That is the stated barrier.

**But nobody has tried.** LLVM's `X86ISelLowering` shuffle lowering is thousands of lines of
hand-written heuristics with no optimality claim anywhere. Superoptimizers get close and stop:
Minotaur (OOPSLA 2024) formalizes 165 x86 vector intrinsics, MISAAL (PACMPL 2025) explicitly
targets "data swizzle instructions" — and Minotaur's authors state the exhaustive query and
decline it: *"this is very heavy lifting."*

**No superoptimizer emits a machine-checkable optimality certificate.** They emit
*correctness* certificates for rewrites they found. That sentence is the opportunity.

*(Caveat carried from the sweep: ACM DL returns 403 to automated fetches, so HieraSynth and
MISAAL were read from abstracts only, and "no superoptimizer emits an optimality certificate"
is an inference rather than a verified fact. Confirm before claiming it in public.)*

## The encoding insight

This is what makes the target attractive, and it is not obvious.

**A pure-permutation shuffle problem needs no bit-vector arithmetic at all.** Model each lane
as a symbolic tag in `0..63` rather than as 8 bits of data. Each instruction becomes a
finite-domain function on tag vectors. "Is there a `k`-instruction sequence realizing `π`?"
is then a **pure SAT / finite-domain problem of a few thousand variables per candidate
length** — far smaller than any QF_BV encoding of the same question.

That matters twice over: it is small enough to solve, and being pure SAT means **DRAT falls
out natively** rather than through a bit-blasting layer.

## Certificates

**Positive — the cheapest in the entire survey.** A shorter sequence is checked by executing
it on **one** input vector containing 32 distinct tags and comparing to `π`. No solver, no
proof, no exact arithmetic. A dozen lines of C with intrinsics, or a table lookup.

**Negative.** Exhaustive UNSAT at `k-1`, with DRAT emitted natively by the pure-SAT encoding.
Size unknown — nobody has run it — but the per-candidate formula is small.

## Fit against this stack

Good, with real build work:

- Pure SAT at a few thousand variables is deep inside comfortable range; the proof-producing
  core is the right engine and DRAT flows to `check_drat_backward` unchanged.
- No CAS, no exact reals, no `i128` overflow risk. Nothing in the CAS layer is touched.
- **What must be built: a faithful ISA semantics model.** Every instruction's lane-permutation
  behaviour, including cross-lane restrictions (`vpshufb` operates within 128-bit lanes, which
  is exactly what makes the problem nontrivial). Getting this wrong produces a confident wrong
  answer, and there is no oracle to catch it.
- Validate the model against real hardware or an emulator before trusting any UNSAT — an
  incorrect semantics makes the search refute sequences that actually work.

## What "done" looks like

Pick a small, named, useful permutation and settle it. Candidates: byte-reverse of a 256-bit
register; the 4x4 byte transpose; a deinterleave used in dav1d or simdjson.

The deliverable is `L(π) = k` for a named `π` on AVX2, with the `k`-instruction sequence and
a DRAT refutation at `k-1`. That is the first published minimality result for a shuffle on
any ISA.

A weaker but still novel deliverable: the first published *table* of best-known `L(π)` with
lower bounds, for a family of common permutations. No such table exists.

## What would kill it

**Nobody has tried, and we do not know why.** This is the honest difference between this
target and [02](02-bilinear-f2-p6.md) or [03](03-sbox-optimality-trio.md), where the
literature tells you exactly where the wall is and how long the last person's runs took.
Here there is no calibration point at all. The absence could mean an unexploited opportunity,
or it could mean everyone who looked found the exists-forall structure fatal and did not
write it up.

**Test for this early and cheaply:** encode a permutation whose optimal length is *known by
construction* — one you built from `k` instructions — and confirm the solver refutes `k-1`.
If that works, the encoding is sound and the approach is live. If the `k-1` refutation does
not terminate on a hand-built 3-instruction sequence, stop.

**Secondary risk: the ISA model is the deliverable's weakest link and has no oracle.** A
wrong semantics yields a wrong theorem that looks right. Budget real time for validating it
against hardware, and treat any UNSAT as provisional until the model is independently checked.

**Tertiary:** the result may be uninteresting if `L(π)` turns out to equal what LLVM already
emits for every permutation anyone cares about. That is a real possibility and it is not
knowable in advance.

## Sources

- [Minotaur: A SIMD-Oriented Synthesizing Superoptimizer, OOPSLA 2024](https://users.cs.utah.edu/~regehr/minotaur-oopsla24.pdf)
- [MISAAL, PACMPL 2025](https://doi.org/10.1145/3729301) — abstract only; ACM DL blocks automated fetch
- HieraSynth, [DOI 10.1145/3763162](https://doi.org/10.1145/3763162) — exhaustive synthesis to 7–8 instructions at instruction-set sizes up to 700 (RVV), up from 1–3 the prior year
- Bansal & Aiken 2006 — length 3 on a small x86 subset, 162.1 billion raw candidates reduced 52x by canonicalization
- LLVM `llvm/lib/Target/X86/X86ISelLowering.cpp` — the heuristics this would measure
