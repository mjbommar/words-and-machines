# STYLE-AI-TELLS — The Rule-Per-Tell Catalog

The concrete "do not write like this" companion to [STYLE.md](STYLE.md). These are not
taste preferences — they are detection signatures that experienced readers spot
instantly, and almost all of them are **padding**: cutting them makes prose both more
human and more readable.

**Why this works as a lens.** AI prose is smooth, uniform, and predictable — low
*burstiness* (sentence lengths don't vary) and low *perplexity* (word choices are the
obvious ones). Human writing surprises. Every tell below is a way smoothness leaks out.

**Format:** every tell gets a name, why it reads as AI, a detection heuristic, and a
rewrite. The mechanically detectable subset is collected in the ` ```tell-patterns `
block at the end (parsed by `scripts/check_style.py`).

---

## Part 1: Syntactic tells

### 1.1 The "This" disease
**Why:** serial "This" openers create a monotone pointing pattern.
**Detect:** more than one sentence per paragraph starting "This ..."; any two consecutive.
- Before: *This filter removes grit. This does not remove germs. This is why you boil.*
- After: *The filter removes grit, not germs. That's why you still boil.*
**Rule:** max one "This" opener per paragraph; never consecutive.

### 1.2 The gerund opener
**Why:** "-ing" phrase openers feel sophisticated and become a tic in bulk.
**Detect:** sentence starts with Having/Being/Knowing/Recognizing/Leveraging/Understanding.
- Before: *Having established the connection, the server waits. Recognizing the threat, engineers responded.*
- After: *The server establishes the connection, then waits. Engineers saw the threat and responded.*
**Rule:** max one gerund opener per page; never consecutive.

### 1.3 The "As X, Y" stack
**Why:** stacked temporal/participial clauses at the sentence head.
**Detect:** repeated `^As the/more/time...` openers on one page.
- Before: *As the network grew, challenges emerged. As users connected, it strained.*
- After: *The network grew. More users connected, straining the infrastructure.*
**Rule:** max one "As X, Y" per page.

### 1.4 The triadic flourish (compulsive triple)
**Why:** AI loves threes — three examples, three reasons, First/Second/Third, "from X to
Y to Z" — relentlessly, whether or not the content has three parts.
**Detect:** three parallel items or numbered ordinals in prose; "from A to B to C" sweeps.
- Before: *Boiling provides safety, reliability, and simplicity. First, it kills germs. Second, it needs no chemicals. Third, anyone can do it.*
- After: *Boiling kills germs with nothing but heat and time. That's why it's the default when you can manage a fire.*
**Rule:** vary grouping sizes — two sometimes, four occasionally. Ordinals only in real
procedures (which belong in a numbered list, not prose).

### 1.5 Not-X-but-Y and "isn't just"
**Why:** the signature AI pivot — negate a smaller thing to inflate the real one. "It's
not just a database; it's a philosophy." Reads as unearned profundity.
**Detect:** "not just/only/merely X, but Y"; "isn't just"; "more than just."
- Before: *The RFC process isn't just a document series — it's a way of thinking about consensus.*
- After: *The RFC process turned disagreement into a procedure: publish, argue, revise.*
**Rule:** state what the thing *is*. If the contrast is real, earn it with evidence, not
with the construction.

### 1.6 Filler transitions
**Why:** they add nothing and signal "professional."
**Detect:** sentence-initial However/Furthermore/Moreover/Additionally/Indeed/Thus/
Consequently/Nevertheless; "That said," "With that in mind," "Moving forward."
**Fix:** delete. The sentence works without them. If it doesn't, fix the connection, not
the lubricant. Real connectors: *but, and, so, yet, still, instead, meanwhile.* Best
transition: none — an echo of a key word, a plain contrast, or time ("By the second day...").

### 1.7 The hedging cluster and hedged intensifiers
**Why:** stacked hedges dodge commitment; hedged intensifiers ("quite significant,"
"fairly important," "rather interesting") cancel themselves out.
**Detect:** might/could/may/seems/appears + possibly/potentially/perhaps; quite/fairly/
rather/somewhat + significant/important/interesting.
- Before: *Rain might possibly tend to be one of the relatively cleaner sources.*
- After: *Rain is usually the least contaminated source you'll find.*
**Rule:** hedge once, specifically, only for genuine uncertainty — then stop. One
qualifier per claim. Never hedge a hard floor (a dose, a deadline, a boil time).

### 1.8 The nominalization habit
**Why:** verbs dressed as nouns weaken prose.
**Detect:** make a decision, give consideration, reach a conclusion, conduct an
assessment, provide assistance, take action.
**Fix:** decide, consider, conclude, assess, help, act.

### 1.9 The rhetorical-question transition
**Why:** cheap setup. "So what does this mean for security? It means..."
**Detect:** question mark immediately answered by "It means/Because/The answer."
**Rule:** max one rhetorical question per chapter; never as a transition. Just make the point.

### 1.10 The summary opener (announcing instead of doing)
**Why:** AI signals what it's about to do. "In this section, we will explore..."
**Detect:** "In this chapter/section," "Let me explain/walk you through," "Here's what
you need to know about."
**Fix:** just start. *"DNS works through delegation."* — not "Let me explain how DNS works."

### 1.11 The passive-responsibility dodge
**Why:** AI avoids naming who does what. "Comments should be submitted."
**Detect:** "should be [past participle]" with no actor.
**Fix:** name the actor. *"Submit your comments before the deadline."*

### 1.12 The trailing participle of significance
**Why:** the dominant mid-2025-era tell (per Wikipedia's AI-cleanup corpus): a comma
plus an "-ing" clause that asserts unearned meaning — "…, ensuring reliability,"
"…, showcasing its versatility," "…, cementing its place in history."
**Detect:** comma + ensuring/showcasing/highlighting/underscoring/emphasizing/
reflecting/cementing/solidifying/signaling at a clause tail.
- Before: *The plant opened in 2024, marking a significant milestone and underscoring the region's growing role.*
- After: *The plant opened in 2024. It was the county's first new employer in nine years.*
**Rule:** if the participle clause states a consequence, make it a sentence with
evidence; if it states nothing, delete it.

---

## Part 2: Structural tells

### 2.1 Uniform paragraph length (the identical paragraph)
**Why:** topic sentence → three supports → wrap-up, every single time; sections of
suspiciously equal length and matching shape.
**Detect:** eyeball a page — do paragraph blocks all look the same size? Do sibling
sections all run the same length?
**Fix:** let content set length. Some paragraphs are two sentences; some build evidence
to a claim; some are one hard line.

### 2.2 The summary-paragraph ending
**Why:** AI closes every section by restating what it just said ("In conclusion, we have
seen that..."). The reader read it two paragraphs ago.
**Detect:** does the final paragraph contain any information not already stated? Delete
it as an experiment — the section almost always ends better.
**Rule:** end on the last piece of new, concrete information. Then stop.

### 2.3 The motivational closer
**Why:** empty encouragement in place of an ending. "Now you're equipped to..." "Your
voice matters." "Together, we can make a difference."
**Detect:** could the closing sentence go on a poster?
**Fix:** replace with a concrete fact, action, or image — or just stop.

### 2.4 Excessive signposting
**Why:** "Having discussed X, we now turn to Y"; headings that exist only to say "new
topic"; constant "as mentioned earlier."
**Fix:** trust the reader. Cut scaffold headings; if you must remind, restructure so you
don't have to.

### 2.5 The exhaustive list
**Why:** AI wants to be complete and lists everything: "X, Y, Z, W, V, and U."
**Fix:** give two or three examples; imply the rest ("including X, Y, and Z"). Exception:
lists where completeness is the point (safety-critical enumerations, reference tables).

### 2.6 The disclaimer sludge
**Why:** front-loaded caveats and qualifications before saying anything. Readers skip it.
- Before: *While every situation is unique and details may differ, the general principles outlined here should provide a useful framework, though of course you should consult professionals...*
- After: *Most communities follow a similar process. The details vary by state — check your zoning code.*
**Rule:** state the principle; one caveat sentence if essential.

### 2.7 The hypothetical example
**Why:** AI invents tidy scenarios ("Imagine a small town in the Midwest...") instead of
citing real ones.
**Rule:** real examples over hypotheticals, always. If no perfect real example exists,
use the closest and note the difference.

---

## Part 3: Semantic tells

### 3.1 The false balance and the "both are true" closure
**Why:** presenting all sides into mush. "Both perspectives have merit, and the truth
lies somewhere in between." Its miniature: set up two things, then flatly label them
coexisting (*"Both were true at once."*) — the words just hold hands.
**Fix:** take the position the evidence supports; qualify specifically. For genuine
uncertainty in a guide: state the range honestly, name the source of uncertainty, then
ask *who bears the downside risk if the optimistic case is wrong* — and redirect to
action. For the closure tic: cut the label; the juxtaposition already does the work.

### 3.2 The weasel citation
**Why:** unnamed authority avoids commitment. "Studies show," "experts agree," "many
researchers argue," "it is widely accepted."
**Rule:** name the source or make the claim yourself.

### 3.3 Temporal waffling
**Why:** vague markers dodge date precision. "In recent years," "over time,"
"eventually," "in the early days."
**Rule:** use the specific date when known ("Since 2020," "By 1993," "In March 1988").
Vague markers only when the date is genuinely unknown.

### 3.4 The value-neutral praise
**Why:** praising without committing to specific merit: impressive, remarkable,
noteworthy, elegant, compelling — with no evidence.
- Before: *The solution was elegant.*
- After: *The solution used three lines of code to replace three thousand.*
**Rule:** show why; let the reader conclude it.

### 3.5 The testament/underscore/highlight lexicon
**Why:** a family of AI-favored abstraction verbs and nouns that gesture at significance
instead of demonstrating it: "a testament to," "underscores the importance of,"
"highlights the need for," "serves as a reminder," "stands as a," "plays a crucial role."
**Fix:** delete the frame; state the fact that supposedly does the underscoring.

### 3.6 The superlative pile
**Why:** stacked qualifiers cancel out. "Arguably one of the most significant
developments in the relatively brief history of the still-evolving field."
**Fix:** make a claim. "The most important development of the decade."

### 3.7 Empty reassurance
**Why:** "simply," "just," "easily," "don't worry" soften what the reader needs to feel
and imply difficulty is trivial. In safety or instructional prose this is also a hazard.
**Rule:** cut "simply/just/easily" before verbs; never promise it'll be fine.

### 3.8 The copulative dodge
**Why:** LLMs avoid plain "is/are" in favor of inflated linking verbs: "boasts a,"
"features a," "serves as," "stands as," "represents." Wikipedia's AI-cleanup corpus
documents a measurable post-2023 drop in is/are frequency.
- Before: *The library boasts a collection of 40,000 volumes and serves as a community hub.*
- After: *The library holds 40,000 volumes. Half the town has a card.*
**Rule:** "is" is a fine verb. Reach past it only when the stronger verb is literally
true (the dam *impounds*, the statute *requires*).

### 3.9 The despite-challenges cadence
**Why:** the outline-shaped closer — "Despite these challenges, X continues to..." /
"faces several challenges... but remains..." — concedes vaguely, reassures vaguely,
and says nothing. It is how a model ends a section it has no ending for.
**Detect:** Despite + challenges/obstacles/criticism followed by continues/remains/
endures; "faces several challenges."
**Fix:** name the specific challenge and what specifically happened to it — or end on
the last concrete fact.

### 3.10 The promotional register
**Why:** brochure vocabulary leaks in from marketing training data: "nestled in,"
"in the heart of," "vibrant," "rich heritage," "renowned," "a diverse array of,"
"natural beauty." Encyclopedic and narrative prose both die of it.
**Rule:** cut the adjective, keep the checkable noun. If a place matters, show one
verifiable detail instead of an adjective cluster.

---

## Part 4: Punctuation tells

### 4.1 Em-dash chains
**Why:** the single most recognizable typographic AI tell. Multiple em dashes per
paragraph, or a dash-pair plus a trailing dash in one sentence.
**Detect:** 2+ em dashes in a paragraph; 3+ always fails.
**Rule:** one per paragraph, and each must do real work (a reveal, an urgent aside).

### 4.2 Parenthetical overuse
**Why:** parentheses every few sentences signal information that should be integrated.
**Fix hierarchy:** commas → colons → new sentence → em dash → parentheses (rare).

---

## Part 5: Repetition and reader fatigue

Repetition is its own machine-tell. The reader thinks "didn't I just read this?" and
stops trusting your attention. Catch these five (full audit workflow in REVIEW-QA.md):

1. **Verbatim duplicates** within a chapter — a strong phrase written twice. Keep the
   stronger placement.
2. **Repeated quotes/statistics across chapters** — state precisely once in a home
   chapter; reference or vary elsewhere.
3. **The thesis hammer** — restating the central argument in near-identical words. Say it
   where it lands hardest; trust the evidence.
4. **Structural clones** — every chapter opening with a vignette, every bridge closing
   the same way. Vary opening types and closing gestures across adjacent chapters.
5. **Vocabulary ruts** — a key word going numb through overuse. Notice, then vary or cut
   where it matters. (Don't mechanically thesaurus — sometimes the plain word four times
   is right.)

Keep repetition that earns its place: a deliberate refrain that *accumulates meaning* is
a leitmotif, not a fatigue tell. Test: on second encounter does the reader think "yes,
that again — it matters" (keep) or "didn't I read this?" (cut).

---

## Part 6: Detection heuristics (fast self-checks)

- **If-then-delete:** delete the sentence. Paragraph still works? It was filler.
- **Who-said-this:** read aloud. Textbook / press release / TED talk / Wikipedia / vendor
  pitch → rewrite. Competent human → keep.
- **Burstiness eyeball:** five consecutive sentences all within ~3 words of each other →
  revise for variance.
- **Surprise test:** is there one thing that would make a reader pause — a concrete
  number, a non-obvious catch, a vivid image? If every sentence goes exactly where
  expected, it's AI-flavored.
- **Adverb budget:** >10% adverbs in a paragraph → trim. Most delete clean.
- **First/last-paragraph test:** delete the section's opening and closing paragraphs as
  an experiment. AI openings and closings are almost always deletable.

---

## Part 7: Machine-readable patterns

Python `re` syntax, one per line, case-insensitive assumed, `^` matches sentence/line
starts (linter applies MULTILINE to extracted prose). These catch the *mechanical* subset;
the judgment tells above still need human/agent review.

```tell-patterns
^this\s+(is|was|means|leads|makes|allows|creates|highlights|underscores)\b
^(having|being|seeing|knowing|understanding|recognizing|leveraging|utilizing)\s+\w+
^as\s+(the|more|time|we|you|a)\b[^.]{5,60},
^(furthermore|moreover|additionally|indeed|nevertheless|nonetheless|thus|hence|consequently|subsequently),
\b(that said|with (that|this) in mind|having said that|that being said|moving forward|going forward|against this backdrop)\b
\b(might|could|may)\s+(possibly|potentially|perhaps)\b
\b(seems? to suggest|appears? to (indicate|suggest))\b
\b(quite|fairly|rather|somewhat)\s+(significant|important|interesting|complex|remarkable)\b
\b(make|makes|made|making)\s+a\s+(decision|choice)\b
\b(give|gave|giving)\s+consideration\s+to\b
\b(reach|reached)\s+a\s+conclusion\b
\b(provide|provided|providing)\s+assistance\b
\bnot\s+(just|only|merely|simply)\s+[^.;:]{3,60}\s*[,;—-]+\s*but\b
\bisn'?t\s+just\b
\bit'?s\s+not\s+(just|only|merely|simply)\b
\bmore\s+than\s+just\s+a\b
\bnot\s+only\b[^.]{5,80}\bbut\s+also\b
\bfirst[,.]\s[^.]{5,120}\.\s+second[,.]\s
\bfrom\s+\w[\w\s]{2,30}\s+to\s+\w[\w\s]{2,30}\s+to\s+\w[\w\s]{2,30}\b
\ba\s+testament\s+to\b
\bunderscor(es?|ing)\s+the\b
\bhighlight(s|ing)?\s+the\s+(importance|need|fact|significance)\b
\bserves?\s+as\s+a\s+reminder\b
\bstands?\s+as\s+an?\b
\bplays?\s+an?\s+(crucial|vital|key|pivotal|central)\s+role\b
\b(some\s+experts?|many\s+(researchers|people|observers)|studies\s+have\s+shown|it\s+is\s+widely\s+(accepted|believed)|experts\s+agree|critics\s+contend|proponents\s+suggest)\b
\b(in\s+recent\s+years|over\s+time|at\s+some\s+point|in\s+the\s+early\s+days)\b
\bin\s+the\s+(world|realm|landscape)\s+of\b
\bnavigat(e|ing)\s+the\s+(complexit|landscape|world|challenge)\w*\b
\b(deep\s+dive|dive\s+deep(er)?|let'?s\s+dive)\b
\bso\s+what\s+does\s+this\s+mean\b
\bwhat\s+does\s+this\s+mean\s+for\b[^?]{0,40}\?\s*(it\s+means|because)
\bboth\s+(were|are|remain|stay)\s+(still\s+)?true\b
\bin\s+(this|the\s+(next|following))\s+(chapter|section),?\s+we\s+(will|'ll)\b
\bhave\s+you\s+ever\s+wondered\b
\bimagine\s+(if|a\s+world)\b
(?:[^—\n]*—){3,}
\b(simply|just|easily)\s+(boil|add|run|open|click|follow|install|apply)\b
\barmed\s+with\s+(this|these)\b
\bnow\s+you'?re?\s+(ready|equipped)\s+to\b
\bwhether\s+you'?re\s+a\b[^.]{5,60}\bor\s+a\b
,\s+(ensuring|showcasing|highlighting|underscoring|emphasizing|cementing|solidifying|signaling)\s+\w
\bboasts?\s+an?\b
\bdespite\s+(its|these|the|this)[^.]{0,80}\b(challenges|obstacles|setbacks|criticism)
\bfaces?\s+several\s+challenges\b
\b(continues?|continued)\s+to\s+(captivate|inspire|resonate|thrive)\b
\bnestled\s+(in|among|between|within)\b
\bin\s+the\s+heart\s+of\b
\b(diverse|wide|vast)\s+array\s+of\b
\b(lasting|indelible)\s+(mark|impression|legacy)\b
\bsetting\s+the\s+stage\s+for\b
\bkey\s+turning\s+point\b
\bdeeply\s+rooted\s+in\b
\b(evolving|shifting|changing)\s+landscape\b
\bmarks?\s+a\s+(significant|major|pivotal)\s+(shift|milestone|step|moment)\b
\brich\s+(cultural\s+)?(heritage|history|tradition)\b
```

### Machine artifacts (zero tolerance)

Unlike the budgeted style tells above, these are mechanical residues of a chatbot
workflow — markdown leaking into LaTeX, citation-plumbing tokens, chatbot voice,
smart quotes from a paste (this house style uses `` ``...'' `` exclusively). Any
match is an **error**, not a budget item: none of these can appear in a finished
book for any legitimate reason. Sourced from Wikipedia's "Signs of AI writing"
artifact catalog (oaicite/contentReference/turn0search markers, knowledge-cutoff
disclaimers, collaborative-voice closers).

```artifact-patterns
\*\*[^*\n]{2,80}\*\*
^#{1,6}\s+\S
\b(oaicite|contentReference|oai_citation|turn\d+(search|view|news)\d+|attributableIndex|grok_card)\b
\butm_(source|medium|campaign)=
\bas\s+an\s+AI(\s+language)?\s+model\b
\bas\s+of\s+my\s+(last\s+)?(knowledge\s+)?(update|cutoff|training)\b
\bknowledge\s+cutoff\b
\bI\s+(hope\s+this\s+helps|cannot\s+browse|can'?t\s+access\s+(the\s+)?internet)\b
\bwould\s+you\s+like\s+me\s+to\b
[“”‘’]
[\U0001F300-\U0001FAFF✅✨❌❗❤️\U0001F900-\U0001F9FF]
```

Notes for the QA-script author:
- Apply to prose only (strip LaTeX/Markdown apparatus first, as
  `the-last-book/scripts/check_prose.py` does).
- `^this\s+...` and the gerund/As-openers are *budgeted* tells (one per paragraph/page),
  not zero-tolerance — report counts, fail on density.
- The em-dash-chain pattern `(?:[^—\n]*—){3,}` fires per line/paragraph.
- Expect false positives on `first... second...` inside genuine numbered procedures;
  exempt list environments.

---

## Part 8: The pre-submission scan

1. Run the tell-patterns + banned lists; fix what they surface (`make check` also
   fails on any machine artifact from the zero-tolerance block above).
2. Read it aloud (still the single best detector).
3. Check burstiness — do sentence lengths actually vary? `make metrics`
   (scripts/prose_metrics.py) computes it per chapter (sentence-length cv), plus
   MTLD/MATTR lexical diversity and paragraph-length uniformity, with thresholds a
   genre profile can override.
4. Delete the first sentence; keep it deleted if the prose improved.
5. Confirm no thesis hammer, no vocabulary rut, no structural clone of the neighboring
   chapter. For the vocabulary rut, `make vocab` (scripts/vocab_variety.py) ranks the
   manuscript's overused words against their OpenGloss/Wikipedia base rates and shows
   synonyms annotated with their own book counts — `--sort ratio --pos adj,adv,verb`
   isolates style words from topic terms; `fresh picks` are alternatives the book
   hasn't touched.
6. Confirm the surprise test passes at least once per section.
7. Optionally `make pangram` (scripts/pangram_check.py, paid external
   detector) for an outside-in detectability score — calibration notes in
   REVIEW-QA §2.
8. `make slop` (scripts/slop_audit.py) ranks paragraphs by slop signals —
   contrast frames, slop-forensics vocabulary, compression-ratio outliers —
   at file/section/paragraph/sentence level with file:line anchors. `--llm`
   judges sampled units against a 54-tell taxonomy (`--list-tells`; toggle
   ids/groups via `--tells`/`--skip-tells`) with per-tell evidence quotes
   and an aggregate: `--unit paragraph|sentence|line|section|file`,
   `--sample worst|random|all`, `--n 3`, `--pct 2`, or `--limit 0` for the
   whole book; models: `anthropic:claude-sonnet-5`,
   `anthropic:claude-fable-5`, `openai:gpt-5.6-terra`.

---

*Synthesized from the STYLE-AI-TELLS catalogs of history-through-rfc-book (the largest,
rule-per-tell with regexes), htsd-book (guide-specific tells), the-last-book (padding-as-
safety-hazard framing, "both are true" tic), history-book, wiki-history-book
(repetition/fatigue taxonomy), and datacenter-2026-book.*
