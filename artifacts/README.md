# Active evidence artifacts

This directory contains only evidence produced under the A0, RV64, x86-64,
cross-machine, and evidence-manifest architecture.

The first active artifact is
`claims/A0.comp.byte-roundtrip-8-16/manifest.json`. It binds the exact A0
semantic-source digest and records a complete finite computation over all
8- and 16-bit words. Its checker recomputes 65,792 cases. Reversed byte order
is the load-bearing negative control and must fail with `semantic-mismatch`.
This computation does not establish the general-width theorem or any later
machine route.

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
