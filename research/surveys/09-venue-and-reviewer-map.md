# Publication strategy: certified minimality for SIMD shuffle sequences

*Produced 2026-08-27 by an Opus 5 research agent. All deadlines verified that day by direct fetch of venue-owned pages; session search budget exhausted early, so evidence is from venue sites, publisher pages, DBLP, and Scholar via SerpApi. Reproduced verbatim (full report plus its addendum's corrections folded in).*

---

## 1. VENUES

### Deadline calendar

| Date | Venue / cycle | Status |
|---|---|---|
| **Wed 9 Sep 2026** | ASPLOS 2027, September cycle | 13 days out |
| **Thu 10 Sep 2026** | **CGO 2027 Round 2** | 14 days out |
| **Wed 14 Oct 2026** | **OOPSLA 2027 Round 1** | announced |
| **Thu 15 Oct 2026** | **TACAS 2027** (+ mandatory artifact 29 Oct) | announced |
| Thu 15 Oct 2026 | TCHES 2027 Issue 2 (rolling) | announced |
| Thu 12 Nov 2026 | PLDI 2027 (single round) | announced |
| ~Nov 2026 | CC 2027 | pattern only |
| **Wed 20 Jan 2027** | **CAV 2027** | announced |
| 15 Jan / 15 Apr 2027 | TCHES 2027 Issues 3 / 4 | announced |
| ~Feb–Mar 2027 | SAT 2027, CP 2027 | pattern only |
| Wed 7 Apr 2027 | OOPSLA 2027 Round 2 | announced |
| ~May 2027 | FMCAD 2027, SC² 2027 | pattern only |
| ~Aug 2027 | CADE-31 (Nijmegen) — **not IJCAR; IJCAR returns 2028** | pattern only |

### Compiler / systems venues

**CGO 2027** — Salt Lake City, Mar 2027. R2 paper 10 Sep 2026 AoE; **two live official pages disagree on the notification date (2 Nov vs 9 Nov)**. 11 pages body, double-blind. AE voluntary, post-acceptance; tool papers require successful AE. Closest recent: *Tensor Program Superoptimization through Cost-Guided Symbolic Program Synthesis* (2026), *Synthesizing Instruction Selection Back-Ends from ISA Specifications Made Practical* (2026).

**OOPSLA 2027 (SPLASH)** — Prague, Oct 2027. R1 14 Oct 2026, notification 18 Dec; R2 7 Apr 2027. **23 pages excluding references**, PACMPL, double-blind, Major-Revision outcome. **Heaviest artifact culture** (15 Distinguished Artifacts in 2025). Closest: **Minotaur (2024, Distinguished Paper)**, **HieraSynth (2025)**, Hydra (2024), *Certified and efficient instruction scheduling* (2020).

**ASPLOS 2027** — Heraklion, Apr 2027. Only the September cycle remains (9 Sep). 11 pages. Owns the historical superoptimization lineage but has published no superoptimization paper 2023–2026.

**PLDI 2027** — Atlanta, Jun 2027, single round 12 Nov 2026; page limit not yet announced; Distinguished Artifact awards.

**CC 2027** — CFP not published; **AE mandatory for Tool Papers** — the only venue where the artifact is load-bearing for the decision.

**PACT** — weakest fit. **LCTES** — weak, but published Kudriavtsev & Kogge, *Generation of permutations for SIMD processors* (2005) — a fallback if reframed around Helium/RVV. **POPL** — 2027 deadline passed; poor fit. **SOAP** — 4–6pp workshop, archival (prior-publication friction).

### Formal-methods / SAT / CP venues

**TACAS 2027** — Copenhagen, Apr 2027. Paper 15 Oct; **MANDATORY artifact 29 Oct**; notification 22 Dec. **18pp** (up from 16), LNCS, gold OA. **Strictest AE**: mandatory for tool papers, due eight weeks before notification. TACAS's artifact definition names "machine-checkable proofs" explicitly. ~32% acceptance. Closest: *DRAT Proofs of Unsatisfiability for SAT Modulo Monotonic Theories* (2024); *Happy Ending: An Empty Hexagon in Every Set of 30 Points* (2024).

**CAV 2027** — Amsterdam, Jul 2027. Paper 20 Jan 2027; tool artifacts 11 Mar; notification 23 Apr. ~18pp regular. CAV 2026: 81/319 ≈ 25.4%. Closest: *Automating Bitvector and Finite Field Equivalence Proofs in Lean* (2026), *Introducing Certificates to the Hardware Model Checking Competition* (2025).

**FMCAD** — **best-matched program, worst page budget** (9pp long). AE deadline = paper deadline; concurrent review. FMCAD 2026: *Lean Certified Bitvector Solving without Bitblasting*; *Verified Real-time Proof Checking for Large-Scale SAT Solving*; *Trimming Pseudo-Boolean Proofs*; *ParaProofa*. 2027 unannounced (~May).

**SAT 2027** — LIPIcs, OA; long 9–15pp; SAT 2026 43.2%. **CP 2027** — LIPIcs; **"Certification" is a tracked keyword (8 submitted, 4 accepted in 2026)**; closest: *Formally Verified Certification of Constraint Programming Proofs*, *End-to-End Certified Graph Colouring*, **VIPR Certificate Construction from Black-Box ILP Solvers** — the nearest published analogue to the companion observation. **IJCAR** — 2026 already happened; next is CADE-31. **CHES/TCHES** — rolling; 2027/2 due 15 Oct 2026; ≤20pp; IACR gold OA. **The key precedent (SLOTHY) lives here.**

**Workshops.** PxTP dormant since 2021 — do not plan around it. SC² live (presentation-only 4pp does not consume the submission). VSTTE 2027 unannounced.

### Competition norms — the rhetorical spine

- **SAT Competition 2026 Main track: proofs MANDATORY.** *"All solvers participating in the Main track are required to provide certificates in both SAT and UNSAT cases… A solver will be disqualified if it produces a wrong answer or a wrong certificate."* Checkers: `cake_lpr`, GRAT, VeriPB/CakePB. A separate Experimental Track exists for solvers that cannot certify.
- **Pseudo-Boolean Competition:** *"Certificates of unsatisfiability/optimality must be generated in the VeriPB format."*
- CP: no competition mandate found (MiniZinc/XCSP3 rules not checked); SAT 2026 hosted a proof-logging workshop (McCreesh, Nordström).

**SAT solved this a decade ago and enforces it competitively; compiler and CP tooling have not.**

### Artifact weighting
Load-bearing only at **TACAS**, **FMCAD**, **CC Tool track**; strongest culture short of a rule at **OOPSLA**. Everywhere else the DRAT must earn its keep in body pages.

### Top 4 for THIS paper
1. **OOPSLA 2027 R1 — 14 Oct 2026.** The prior art it displaces is there; 23 pages fits the whole stack; heaviest artifact culture; Major-Revision path.
2. **CGO 2027 R2 — 10 Sep 2026.** Fastest; 14 days; only if a near-complete draft and the LLVM-comparison experiment exist.
3. **TACAS 2027 — 15 Oct / artifact 29 Oct.** Audience already believes the thesis; AE is credit, not risk. Lead with the encoding theorem.
4. **FMCAD 2027 — ~May 2027.** Best-matched program; 9 pages; a focused follow-up on the encoding and checker.

**Alternates:** CAV 2027 (hedge); **TCHES** (dark horse — SLOTHY makes it the venue with highest contrast); CP 2027 (where the companion observation changes minds). **Avoid PACT, POPL, PxTP.**

## 2. RELATED WORK THE PAPER MUST CITE

**The finding that matters most.** Two independent searches — 8 and ~30 formulations — converged: **no prior paper emits a machine-checkable minimality certificate for an instruction sequence.** ~38 formulations, same result. State it narrowly, in three clusters: (1) superoptimizers that claim optimality and ship no certificate; (2) certificate-producing verification of *correctness*, never *minimality* — **correctness is a ∀-statement discharged per rewrite; minimality is a non-existence statement over a search space, and non-existence is exactly what a refutation proof is for**; (3) machine-checkable exact combinatorial bounds — technique established (Kochen–Specker 2023, Rota's basis 2022, W(3,3) 2026, C(12,6,4)=41 2026), never pointed at a machine ISA.

**The caveat that must appear.** **Bansal & Aiken (ASPLOS 2006) already produce optimal-within-a-window sequences by exhaustive enumeration** — the same logical shape. **You are not first to claim instruction-sequence optimality. You are first to make the claim re-checkable by a third party without re-running or trusting your tool.** Do not claim "first machine-checkable proof in compilers" either. *(Compiler-gap addendum: Franchetti & Püschel, CC 2008, proved stride permutations minimal on SSE2/Cell — cite as the antecedent.)*

**Tier 1 — the three papers reviewers will be holding.** **HieraSynth** (Lu & Bodík, PACMPL 9(OOPSLA2) Art. 384, doi:10.1145/3763162) — *"Combined with an accurate cost model, this completeness proves that the generated program is optimal"*; Bitwuzla 0.7.0 at 3600 s; no certificate export; escape hatch independently extracted twice: *"For applications requiring a definitive unrealizability proof, we can disable timeouts for leaf nodes."* **Minotaur** (Liu, Mada, Regehr, OOPSLA 2024, Distinguished; doi:10.1145/3689766; verify article number 313 vs 326) — no optimality claim; "formally verified" means Alive2 refinement per rewrite. **SLOTHY** (Abdulrahman, Becker, Kannwischer, Klein, TCHES 2024(1), doi:10.46586/tches.v2024.i1.87-132) — *"automatically finds optimal and traceable instruction scheduling"*; **auditable = human-readable**; OR-Tools CP-SAT; no certificate. **The companion observation with a name and a DOI — frame it around SLOTHY, not an anonymous vendor.**

**Tier 2 — the methodological ancestor.** Cruz-Filipe, Larsen, Schneider-Kamp, JAR 59(4) 2017, doi:10.1007/s10817-017-9405-9; Cruz-Filipe & Schneider-Kamp, ITP 2015, doi:10.1007/978-3-319-22102-1_10; Codish et al., ICTAI 2014 / JCSS 2016. **Cite generously — the template is theirs.** Novelty: domain transfer to a real ISA with a latency cost model, plus an encoding that makes the certificate free (lanes as tags ⇒ pure propositional refutation; they needed a bespoke extracted checker).

**Tier 3 — superoptimization lineage.** Massalin ASPLOS 1987 (`10.1145/36206.36194`, DBLP form); Bansal & Aiken ASPLOS 2006 (`10.1145/1168857.1168906`); **Binary Translation Using Peephole Superoptimizers — OSDI 2008**; STOKE ASPLOS 2013; Sharma et al. OOPSLA 2015; LENS ASPLOS 2016; Unbounded superoptimization Onward! 2017; **Souper — arXiv:1711.04422, never formally published**; Hydra OOPSLA 2024; MISAAL PLDI 2025 (`10.1145/3729301`); GASOL TOSEM 2022; SuperStack PLDI 2024 (`10.1145/3656435`); Crick's Bath thesis 2009; TOAST ICLP 2006.

**Tier 4 — shuffle/permutation synthesis.** **LLVM's x86 shuffle lowering has no paper** — the 2014 Carruth rewrite exists only as a Discourse thread and `X86ISelLowering.cpp`; cite the thread and the file path. Kudriavtsev & Kogge LCTES 2005; Ren–Wu–Padua PLDI 2006; Nuzman–Rosen–Zaks PLDI 2006; Swizzle Inventor ASPLOS 2019; VeGen ASPLOS 2021; Diospyros ASPLOS 2021; Rake ASPLOS 2022; Pitchfork ASPLOS 2023; Coyote ASPLOS 2023. **None searches for a minimal shuffle sequence.**

**Tier 5 — translation validation and certified compilation.** Alive2 PLDI 2021; Alive PLDI 2015; **Six, Boulmé, Monniaux, *Certified and efficient instruction scheduling*, OOPSLA 2020 (`10.1145/3428197`) — the nearest "certified compiler back-end decision"; they certify a schedule is *correct*, you certify no shorter sequence *exists***; Peek PLDI 2016; Pnueli et al. TACAS 1998; Necula PLDI 2000; CompCert.

**Tier 6 — exact synthesis and proof logging.** Gulwani et al. PLDI 2011; SKETCH; Soeken et al. DATE 2018 / TCAD 2017; Kojevnikov et al. SAT 2009; **Knuth TAOCP Vol. 4A §7.1.2** (Fascicle 6 is *Satisfiability* — pick deliberately). DRAT-trim SAT 2014; cake_lpr STTT 2023; GRAT; Heule–Kiesl–Biere CADE 2017; Pollitt–Fleury–Biere SAT 2023; FRAT; Codel–Avigad–Heule FMCAD 2024; Tan et al. FMCAD 2026. Alethe/Carcara (metadata unverified). Gocht–McCreesh–Nordström CP 2022 (*auditable*, meaning far more than SLOTHY's); Bogaerts et al. JAIR 2023; VeriPB; Flippo et al. CP 2024/2026; Szeider CP 2026 (VIPR from black-box ILP); Hoen et al. CP 2024; Bryant–Biere–Heule TACAS 2022.

**Framing citations.** **Certifying algorithms** — McConnell, Mehlhorn, Näher, Schweitzer, CSR 5(2) 2011, 337 cites — the canonical "untrusted computation + trusted small checker." Pair with **Dagstuhl Seminar 25231, *Certifying Algorithms for Automated Reasoning*** (Bjørner, Heule, Kaufmann, Nordström, Koops, June 2025) — the field's own statement that this is an organized program; position the paper as extending it into compilers.

## 3. THE FIVE STRONGEST REVIEWER OBJECTIONS

1. **"The subset is cherry-picked."** Fair, most dangerous. Defuse: (a) make the subset a machine-readable parameter shipped as data; (b) **do the length-1 check over the entire documented AVX2 shuffle repertoire** — finite per-instruction, per-immediate enumeration; converts the headline from subset-relative to ISA-absolute at almost no cost; (c) report a scaling curve as |S| grows.
2. **"Reversal at length 2 is trivial."** Fair about the upper bound, wrong about the lower. The production LLVM lowering is an undocumented heuristic with no paper — reversal is a case where the compiler's answer happens to be minimal and **nobody could previously say so.** Frame it as the calibration instance; the objection dies only with a non-folklore optimum (§4).
3. **"The cost model is made up."** Derive from uops.info / Agner Fog / LLVM's `X86Sched*.td`; ship as data; **run under three published profiles** — stability is stronger than one number, instability is a genuine finding.
4. **"Why not CaDiCaL + drat-trim? Pure Rust is not a contribution."** Largely fair; don't claim Rust as a contribution. Run the identical encoding through CaDiCaL and check with drat-trim, cake_lpr, and your checker — three-way agreement *is* the thesis. Say what the kernel adds beyond a CNF-level checker (the chain from original terms down); if it doesn't stick, use cake_lpr. Engineering claims (no C, one kernel across formats, WASM) are enablers: one paragraph.
5. **"No comparison to Minotaur/HieraSynth; DRAT for 2,697 variables is not impressive."** Treat as one. State the axis (asserted by the tool vs checkable by a third party); quote the timeout sentence; concede scale with numbers; **run at least one Minotaur benchmark through the pipeline**; report proof-logging overhead and the scaling wall.

**Two more:** 6. "Lane tags are a standard abstraction" — defuse with a soundness-and-completeness theorem for shuffle-only sets and a differential experiment against bit-blasting. 7. "The CP anecdote is a cheap shot" — make it a named, versioned, reproducible observation attached to SLOTHY, and cite the CP 2026 certification cohort as evidence the community has the format and lacks adoption.

## 4. FRAMING

**Titles.** 1. *Nobody Has to Trust the Superoptimizer: Machine-Checkable Optimality Certificates for Instruction Sequences.* 2. *Auditable Minimality: Certified Optimal SIMD Shuffle Sequences from Untrusted Search* (deliberate contrast with SLOTHY). 3. *Two Instructions and a Proof* (talk/arXiv title; invites objection 2). Prefer 1 or 2.

**Abstract skeleton (150 words).** Problem (2 sentences): superoptimizers increasingly claim *optimality*; such claims rest on trusting the search and its solver, and no tool exports evidence a third party can check. Method (3): a stack in which search is untrusted and checking is small and independent; lanes as symbolic tags make minimality pure SAT, so refutations emit DRAT natively; every satisfying sequence replayed against original semantics. Demonstration (2, **third not first**): 32-byte reversal, minimum length 2 in a declared subset, minimum cost 4 under a published profile, 1.9 MB certificate; N production patterns certified, K where LLVM is provably non-optimal. Stance (1): SAT solvers have required proof logs for a decade; compiler optimality claims should too.

**The one experiment that most strengthens the paper: a certified optimality census over real shuffle patterns** (Highway, simdjson, LLVM's test suite) — three columns: LLVM's sequence, certified optimum, certificate. **The rows where LLVM wins are the unique contribution**: Minotaur can already show LLVM is beatable; nobody can show LLVM is *exactly optimal* in a checkable way. Runner-up: the three-profile cost-model sweep. Third: a second ISA (NEON/RVV) — after the census.

## Caveats
Unverified: all nine compiler-venue acceptance rates; PLDI 2027 page limit; CGO R2 notification date; FMCAD 2026's 31.7%; ASPLOS badge set; Minotaur's article number; several `cited_by` counts; Alethe/Carcara/VIPR/FRAT/uops.info exact citations. Pattern-only: CC, LCTES, SOAP, PACT, POPL 2028, SAT, CP, FMCAD, VSTTE, SC², CADE-31. Not checked: MiniZinc Challenge and XCSP3 rules.
