# SSRN readiness checklist

Copy this to the repo root as `TODO-SSRN.md` and work it before uploading.
Status legend: `[ ]` open · `[~]` in progress · `[x]` done · `[>]` deferred.

## Content

- [ ] Abstract is final and matches the built PDF exactly (`make ssrn`).
- [ ] Title/subtitle final. If you changed a "framework"-style subtitle, record
      the prior one in `venue.ssrn.prior_subtitle` (the dossier notes it's
      reversible; SSRN's 2026-06-15 rules disfavor such subtitles).
- [ ] Keywords set (`classification.keywords`) — SSRN uses them for discovery.
- [ ] JEL codes set (`classification.jel`) for econ/law.
- [ ] Every claim that needs a source is cited AND verified
      (`note = {verified YYYY-MM-DD}`; see docs/guides/CITATIONS.md).

## Disclosures (SSRN requires the AI statement when AI was used)

- [ ] `disclosure.ai_used` / `ai_statement` correct (also a first-page footnote
      and the Disclosures section).
- [ ] Funding, competing interests, data availability filled in `paper.yaml`.

## Submission form (from SSRN-METADATA.md)

- [ ] All authors have affiliations + valid emails on the page.
- [ ] Related SSRN papers listed (`venue.ssrn.related`) — link a companion
      dataset/prior abstract if any.
- [ ] Suggested networks / eJournals chosen (`venue.ssrn.networks`).

## Build & upload

- [ ] `make validate` green.
- [ ] `make ssrn` — regenerate the PDF + dossier the SAME DAY you upload
      (the title page is dated `\today` unless `paper.date` is pinned).
- [ ] Upload `build/latex/main.pdf` (PDF only).

## Outstanding for the author

- [ ] _(list anything a co-author or reviewer must resolve before posting)_
