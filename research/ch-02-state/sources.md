# Chapter 2 sources

Research checked on 2026-08-30. Search results are leads only. Manuscript
claims must use opened primary, standards, or official architecture sources.

## Origins and foundations

- John von Neumann, *First Draft of a Report on the EDVAC* (1945), for the
  proposed arithmetic, control, memory, input, and output organs and the need
  to retain instructions and numerical information. Do not call every feature
  of the later stored-program computer von Neumann's sole invention.
- Edward F. Moore, "Gedanken-Experiments on Sequential Machines" (1956),
  pages 129--153 in *Automata Studies*. Moore defines finite sequential
  machines by states, inputs, outputs, and transitions, then asks when an
  external experiment can distinguish two states. This is a primary bridge
  from internal state to the book's observation discipline.
- Gene Amdahl, Gerrit Blaauw, and Frederick Brooks, "Architecture of the IBM
  System/360" (1964), for the distinction between architecture and
  implementation and for compatibility across implementations. Do not claim
  that this paper invented either idea.
- Claude Shannon's relay-and-switching analysis (1938) supplies the algebraic
  bridge to switching networks. A physical-storage paragraph still needs a
  primary or authoritative circuit source before making a historical claim
  about a particular latch or flip-flop.

## Current authoritative sources

- RISC-V International, *The RISC-V Instruction Set Manual, Volume I*, project
  revision 20260120. The base integer state has `x0` hardwired to zero; writes
  to it have no architectural effect. Use the exact selected RV64 slice rather
  than treating all optional extensions as one state.
- Intel, *Intel 64 and IA-32 Architectures Software Developer's Manual*,
  version 092 (August 2026), Volume 1 for the programming environment,
  general-purpose registers, `RIP`, and `RFLAGS`. Volume 3 and the XSAVE
  material document processor-extended-state management; Chapter 13 of Volume
  1 identifies separately managed state components, a 512-byte legacy area,
  and an extended region. Do not import privileged state into A0 or infer that
  every context switch copies the whole area.
- The official Intel manual landing page dated 2026-08-19 confirms that
  version 092 is current and separates basic architecture, instruction
  reference, system programming, and model-specific registers.

## Coverage comparators

- Arvind and Shen, *Computer Architecture: A Constructive Approach*, section
  5.1.1, explicitly separates architecturally visible state from pipeline,
  shadow-register, and other implementation state.
- Harris and Harris, *Digital Design and Computer Architecture*, places
  architectural state beside instruction semantics and develops state-holding
  circuits earlier in the text.
- Behrooz Parhami, *Computer Architecture: From Microprocessors to
  Supercomputers*, covers latches, flip-flops, registers, finite-state
  machines, sequential circuits, clocks, and timing as connected foundations.
- Douglas Comer, *Essentials of Computer Architecture*, develops circuits
  that maintain state, feedback, latches, flip-flops, transition diagrams,
  counters, and clocks before processor organization.
- Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*,
  supplies the quantitative-design expectation: consequences should name the
  resource and cost rather than merely list features.

## Source cautions

- "State" is relative to a transition and observation model. Do not equate
  A0 state, a process context, an ISA's complete privileged state, and all
  physical processor state.
- A latch's voltage regions realize a bit only under a decoding and timing
  contract. Do not imply that the mathematical bit is literally a voltage.
- Saving more state can cost time and storage, but a current numerical claim
  needs a pinned platform, mechanism, and unit. Avoid generic cycle counts.
- Optional ISA extensions enlarge the state surface only when enabled and
  included in the selected execution environment.

## Axeyum substrate audit

The 2026-08-30 search of the sibling checkout found broad use of internal
solver and algorithm state, but no book-specific A0 architectural-state type,
canonical state serialization, observation declaration, or state-relation
package. Reuse the Chapter 1 bit-vector substrate where appropriate. Keep
`OP.a0.state-memory` an implementation obligation until code, replay, and
negative controls exist.
