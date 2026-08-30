# Index and Glossary

The glossary and index are part of the teaching apparatus. Maintain them while
revising a chapter, not as a final production sweep.

## Different jobs

`glossary.yaml` defines the compact vocabulary a reader may need to recover
away from its first explanation. Each entry gives the book's meaning in plain
English. It is not a list of every technical noun.

The index answers a different question: where can a reader learn, compare, or
apply a concept? Add `\indexentry{...}` at a useful explanatory passage, not at
every occurrence. Prefer a few strong locators to a concordance.

## While revising a chapter

1. Identify terms that become load-bearing in the chapter. Explain each in the
   prose before relying on it.
2. Add or improve a glossary entry when a reader will need the definition again
   in another chapter. Keep the headword stable and the definition independent
   enough to read out of context.
3. Add index locators at the definition, the principal worked example, an
   important contrast, and a material boundary when those locations serve
   different reader needs.
4. Use subentries for a real conceptual family, such as
   `\indexentry{memory!aliasing}`. Use `see` references for common alternate
   names; do not create two competing top-level entries.
5. Run `make structure`. It checks the spine and also requires every glossary
   headword to have a top-level index route.

The print build generates the alphabetical glossary and index. The EPUB build
generates the glossary and nested Part--Chapter--Section navigation; invisible
index markers do not appear in EPUB prose.

## Quality test

A good glossary definition names the category, states the distinguishing fact,
and avoids depending on another undefined term. A good index entry points to a
passage worth reading. Neither system excuses unexplained jargon in the body.
