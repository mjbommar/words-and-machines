# Active evidence artifacts

This directory contains only evidence produced under the A0, RV64, x86-64,
cross-machine, and evidence-manifest architecture.

The first active artifacts are the complete width-8/16 byte-roundtrip
computation and one narrow-versus-broad observation trace. Both bind A0
semantic package v2 and recompute their reports. Reversed byte order and
omission of requested r3 are their load-bearing controls; each must fail with
`semantic-mismatch`. These routes do not establish a general-width theorem,
universal observation law, or any later machine route.

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
