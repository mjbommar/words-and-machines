# Style Profile: Technical Hands-On

Layered over [STYLE.md](../STYLE.md) — select with `style.profile:
technical-handson` in `book.yaml`. For code-first books where the code
is the pedagogy: hacking guides, build-along tutorials, practitioner
how-tos, technical textbooks with runnable examples.

Portfolio exemplars: *Hacking with AI* (hacker community voice),
*Vibe Coding for Lawyers* (professional how-to), the *AI for Law and
Finance* textbook wing (formal pedagogical).

## Reader & register

A practitioner who will type what you show them. **Whiteboard test**
(a.k.a. the lab-bench test): could you explain this standing at a
whiteboard with a colleague, or as a talk to a room that has opened a
terminal? If it needs slideware transitions, rewrite it. Match the
sub-register to your audience — hacker-community, senior-colleague, or
textbook-formal — and hold it (declare which in `docs/SPIRIT.md`).

**Delight is not optional, and opinions are mandatory.** Say "this
defense is theater" when it is; tell the war story and the dead end.
The genre reads as dead the moment it goes neutral and hedged.

## Person & tense

- "We" build it together; "you" for the reader's actions; imperatives
  for steps. Present tense.
- Never "one"; never the corporate passive ("it should be noted that
  care must be taken").

## Rhythm

- Sentences average 12–20 words. Prose between code blocks is *setup
  and payoff*, not filler — say why the next block exists, run it,
  then say what broke or worked.
- Terminology is fixed: keep a terms table ("use," not "leverage" or
  "utilize"; "workflow," not "pipeline"; the reader's real word for
  their own role).
- **Complexity budget per page**: one new concept per section, code
  before math, at most ~3 new symbols per page and ~7–10 new terms per
  chapter. Over budget is how a hands-on book turns into a reference
  no one finishes.

## Structure & code

- **Working code or no code.** Every listing runs as printed, with
  pinned versions and dated currency (which model/CVE/API version it
  was true against).
- Code line length ≤ 72 characters (target 65) so it survives the
  print measure; use the language's line-breaking idiom, never a
  screenshot of wrapped code.
- Prompts, program output, and AI responses each get their own
  environment (`promptcode` / `outputcode` / `responsebox`) — never
  blur who or what is speaking.
- Show the dead end before the fix. The strongest teaching cycle in
  this register: it's-written → it-breaks → you-fix-it.
- Code hierarchy: raw code first, open-source tools second, commercial
  last. Exercises or labs close the chapter.

## Ethics register (pick one, hold it)

- **Community voice** (security/hacking): no corporate CYA. "We
  demonstrate against systems you control; if you find this in the
  wild, report it — the maintainer probably doesn't know."
- **Professional-responsibility voice** (regulated professions): map
  to the governing rules (e.g. ABA Model Rules for lawyers) in an
  ethics box per chapter.
- **Neutral academic** (textbooks): an evidence hierarchy per domain;
  re-verify anything newer than your training/reference cutoff.

## Craft moves

- Accuracy over hype: cite the exact version an example works against.
- Companion-repo split: the book teaches capability and judgment; the
  repo holds the runnable implementation. Don't paste the whole repo
  into the prose.
- Multi-audience boxes (e.g. partner / associate; exploit / defense)
  when one page serves readers at different levels.

## Watch for (this register's failure modes)

- Corporate/legalistic hedging as the genre AI-tell — the "consult a
  qualified professional" reflex where a real answer belongs.
- Enumerated prose ("First… Second… Third…") standing in for actual
  structure.
- Untested code, unpinned versions, "should work" hand-waving.
- **The irony check** (books *about* using AI): a book that teaches
  responsible AI use must not itself read as AI-written. Run the AI-tell
  gate harder on your own prose than on your examples.
- Regulated professions: legalese leaking into instruction ("whereas,"
  "heretofore," "notwithstanding") — say it the way a colleague would.

## Lint deltas

Prose metrics are relaxed because pasted commands and identifiers
inflate apparent sentence length; the AI-tell budget stays tight.

```style-targets
tell_budget: 3
sentence_avg_lo: 12
sentence_avg_hi: 20
sentence_hard_max: 35
paragraph_sents_lo: 2
paragraph_sents_hi: 6
# Craft diagnostics (register_report.py, rhythm_audit.py) — see ONTOLOGY.md
nominalization_per_1000_max: 45.0 # "authentication", "serialization" are the domain's nouns, not buried verbs
latinate_ratio_max: 0.55          # terms of art are Latinate by construction; renaming them costs precision
hedge_per_1000_max: 14.0          # version caveats are honest; the ceiling still catches "consult a professional" reflex
uniform_para_pct_max: 40.0        # procedure paragraphs legitimately run to one length
```

Figure density is *expected to be low* here: reference prose carries few
rhetorical schemes, and `figure_detector.py` has no minimum — a sparse
figure matrix is not a finding in this register. Its ceiling
(`--max-density`) is command-line only and does not read this block.

```banned-words-add
utilize
leverage
seamless
effortless
```

```banned-phrases-add
in today's fast-paced
consult a qualified professional before
it should be noted that
as we all know
```
