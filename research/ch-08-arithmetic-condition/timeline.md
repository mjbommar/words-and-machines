# Chapter 8 chronology

This chronology separates mathematical publication, mechanical practice,
circuit theory, machine architecture, and later software contracts. It avoids
sole-inventor claims where a concept developed along several lines.

| Date | Development | Relevance and caution |
|---|---|---|
| 1703 | Leibniz publishes an explanation of binary arithmetic | A major printed account, not the beginning of every binary idea |
| 1801 | Gauss gives congruence a systematic arithmetic language | Later notation makes wraparound identities concise; it was not written as an ISA specification |
| 19th century | Mechanical calculators and engine designs embody carries and repeated arithmetic | Separate proposed designs, built machines, and modern digital circuits |
| 1854 | Boole publishes an algebra of logical relations | Mathematical foundation; arithmetic meanings still require representation rules |
| 1938 | Shannon relates Boolean algebra to relay and switching circuits | Establishes a design method for switching networks, not one unique adder |
| 1940s | Electronic stored-program machines expose arithmetic state and conditional transfers | Exact accumulator, sign, overflow, and branch conventions vary by machine |
| 1951 | Booth publishes a signed binary multiplication technique | The paper explicitly links number representation and equipment economy |
| 1964 | System/360 publishes arithmetic rules and a program-visible condition code in a compatible family | Shows condition state as a durable software interface |
| 1973 | Kogge and Stone publish a parallel recurrence method later used for prefix carry computation | One influential depth/structure point in a larger adder-design space |
| 1980s--present | RISC and x86 lineages preserve conditions in different architectural shapes | Compare exact predicates and state, not slogans |
| 2000s--present | Languages and compiler IRs expose wrapping, checked, saturating, and no-wrap contracts | Policies affect optimization, safety, debugging, and portability |
| 2026 | Current ISA manuals, LLVM semantics, and Rust APIs pin practical claims | Rules and APIs are versioned; circuit costs remain implementation-specific |
