# Active evidence artifacts

This directory contains only evidence produced under the A0, RV64, x86-64,
cross-machine, and evidence-manifest architecture.

Twelve artifacts currently bind A0 semantic package v10: complete width-8/16
byte round trips, the reusable word-operation audit, the canonical complete-state
codec, one narrow-versus-broad observation trace, complete
width-eight addition steps, one atomic memory round trip with a boundary trap,
one taken/untaken branch pair, and four runner classifications with prefix
resumption, exhaustive canonical encoding of all legal structured A0
instructions, complete family/effect/trap coverage for the A0 step, and
term-bound addition and memory-frame certificates at all eight supported widths. Every
checker recomputes its report through
the bound semantics. The controls reverse bytes, omit requested r3, write an
addition result to the wrong destination, reverse memory byte order, or use the
wrong branch-target base. The runner control labels a running prefix as halted;
the decoder control accepts one reserved-bit form. The step suite injects a
hidden write, removes a condition update, and changes the sequential PC.
The word-operation control replaces zero extension with sign extension; the
state-codec control accepts one trailing byte. The
addition-proof control inverts carry, finds a satisfying width-eight
model, and replays that pair through encoded A0 execution. The memory-frame
control commits a partial sparse write on trap; its symbolic negation is
satisfiable and the changed byte is replayed against the correct encoded step.
Each must fail with `semantic-mismatch`. These routes
do not establish an arbitrary-width theorem or any later machine route.

The layout has a schema directory, versioned semantic packages, and one claims
subdirectory per object ID. Each claim directory contains one
manifest and its pinned evidence files.

Semantic packages define words, states, decoders, steps, traces, or state
relations. Claim directories consume exact package digests. Every active claim
records both the successful route and a negative control that fails for a
named reason.

## Trust classes

- definition: versioned semantic input, not evidence that a theorem holds;
- trace: recomputed example execution;
- computation: complete finite run over a declared domain;
- verdict: solver or checker result without an independent certificate;
- certificate: independently checked proof against the exact formula; and
- kernel: theorem reconstructed in the declared trusted kernel.

The class does not widen scope. A kernel result about one selected instruction
form remains about that form.

## Legacy material

The former word formulas, RISC-V Bitmanip reproductions, and vector-shuffle
certificates are in the legacy-artifacts research archive. They are
provenance, not active book evidence. Their old producers are in the
legacy-producers research archive.

## Gate

Run make artifact-check for manifest, path, digest, semantic-input, and control
validation. Run make check-run to execute bound checkers and require every
negative control to fail.
