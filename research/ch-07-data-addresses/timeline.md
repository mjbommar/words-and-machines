# Chapter 7 chronology

This chronology separates documented design, working hardware, published
architecture, and later terminology. Verify every priority claim against a
primary source before manuscript use.

| Date | Development | Relevance and caution |
|---|---|---|
| 1940s | Early stored-program orders name memory locations | Connect finite address fields to stored values; machines used different conventions |
| late 1940s | Manchester and EDSAC programs operate on addressed words | Do not equate word addressing, modern byte addressing, or later load/store terminology |
| 1949 | The Manchester Mark I has B-lines that can modify instruction addresses | A documented early milestone; avoid turning it into an unqualified priority claim |
| 1964 | System/360 publishes base-plus-index-plus-displacement forms in a compatible family | Shows address formation as durable architecture and economic interface |
| 1970s--1980s | Microprocessors develop overlapping registers and richer effective-address forms; RISC projects foreground load/store regularity | Keep separate lineages and avoid a universal RISC/CISC binary |
| 2000s | x86-64 extends registers and adds RIP-relative data addressing while preserving subregister history | Exact behavior depends on mode, prefix, and selected form |
| 2010s | RISC-V standardizes regular base load/store encodings with optional extensions | Misalignment and environment behavior remain scoped |
| 2026 | Current manuals and compiler interfaces pin the chapter's practical claims | Quantities and APIs are dated; architecture rules are versioned |
