# Active evidence artifacts

This directory contains only evidence produced under the A0, RV64, x86-64,
cross-machine, and evidence-manifest architecture.

Six artifacts currently bind A0 semantic package v3: complete width-8/16
byte round trips, one narrow-versus-broad observation trace, complete
width-eight addition steps, one atomic memory round trip with a boundary trap,
one taken/untaken branch pair, and four runner classifications with prefix
resumption. Every checker recomputes its report through
the bound semantics. The controls reverse bytes, omit requested r3, write an
addition result to the wrong destination, reverse memory byte order, or use the
wrong branch-target base. The runner control labels a running prefix as halted.
Each must fail with `semantic-mismatch`. These routes
do not establish general-width theorems or any later machine route.

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
