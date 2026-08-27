# CITATIONS — Verify Before You Cite

Citation discipline for every book in this template. This exists because careless
verification has failed before, measurably.

---

## 1. The cautionary tale: the 57% error rate

In one project's early verification pass, citations were "confirmed" from search-result
snippets without fetching sources. A later real audit found **57% of checked citations
had errors** — wrong authors, wrong dates, wrong titles. A second project's spot-check
found a 50% error rate in its sample. These were not edge cases:¹

| Source | Cited author | Actual author |
|---|---|---|
| CNN | Samantha Kang, Holmes Lybrand | **Clare Duffy** |
| Planet Detroit | Steve Ruggiero | **Brian Allnutt** |
| TechCrunch | Kyle Wiggers | **Amanda Silberling** |
| Epoch AI | Ben Cottier, Robi Mularczyk | **Josh You** |

What went wrong, so it never recurs:
- Declared "CONFIRMED" after a web search without reading the source.
- Used a plain fetcher, got blocked (403/451), then guessed.
- Checked that an article *exists* but not its author/date.
- Trusted search snippets over the actual page.
- Rushed to appear helpful.

### The iron rules

1. **NEVER claim a citation is verified without fetching the actual source.**
2. **Check every field — title, author, date, URL — against the fetched page,
   character by character.**
3. **If you cannot fetch a URL, say so explicitly. Do not guess.**
4. **"I verified" must be accompanied by the fetch output that proves it.**

---

## 2. Claim classification

Before verifying, classify every factual statement in a chapter:²

| Category | Description | Verification path |
|---|---|---|
| **OBVIOUS** | Common knowledge, definitional | No citation needed |
| **SPEC-VERIFIABLE** | Standards, laws, specs, dates, authors | Check the primary document (RFC, statute, filing) |
| **HISTORICAL** | Events, quotes, incidents | Primary sources: archives, minutes, oral histories |
| **STATISTICAL** | Numbers, percentages, counts | Named report/dataset with date; check the math on derived comparisons |
| **BIOGRAPHICAL** | Personal details about people | Oral histories, obituaries, first-person accounts |

**Source priority:** local/primary sources first (project datasets, document archives,
official filings), web search last. When searching, prefer primary > institutional >
trade press > general web. Document *why* a web source was needed.

---

## 3. The verification workflow

### Fetching — the escalation ladder

Each rung was tested against live sites (2026-07). A miss at any rung is
"unverified", never "dead" — climb the ladder before deleting a citation.

| Rung | Tool | Beats | Blocked by |
|---|---|---|---|
| 0 | `verify_citation.py` (httpx, desktop UA) | normal sites | most news/corporate bot walls (Reuters: 401) |
| 1 | `--fetch` (real headless Firefox + JS rendering) | UA/TLS fingerprint checks, JS-rendered pages | CDP/behavior walls (DataDome, PerimeterX) |
| 2 | Chrome DevTools MCP (real Chrome) | pages needing interaction: cookie walls, scroll-to-load, tabs | DataDome-class walls — they detect devtools explicitly |
| 3 | Wayback snapshot (`archived=`) | every wall, for anything crawled | pages too fresh to have a snapshot (capture first) |
| 4 | Manual browser | everything | nothing — record what you saw and when |

**Rung 0 — the mechanical pass.** Reachability and stamp coverage only; it
does not compare titles/authors/dates against the page (that judgment is
yours, per the checklist below):

```bash
uv run scripts/verify_citation.py                 # all url-bearing entries
uv run scripts/verify_citation.py --key KEY       # specific entry
uv run scripts/verify_citation.py --unused        # entries not cited anywhere
uv run scripts/verify_citation.py --stamp         # stamp passes after manual review
uv run scripts/verify_citation.py --archive       # pin Wayback snapshots (archived=)
uv run scripts/verify_citation.py --require-stamps --require-archives  # release gate
```

**Rung 1 — real browser fetch.** Launches headless Firefox, waits for
client-side rendering, and prints exactly what verification needs — title,
byline, published/modified dates (JSON-LD → meta tags → DOM byline) — plus
the article converted to markdown:

```bash
# one-time browser download:
uv run --with playwright playwright install firefox

uv run --with playwright,markdownify scripts/verify_citation.py --fetch URL
uv run --with playwright,markdownify scripts/verify_citation.py --fetch URL --markdown  # full text
```

What makes the browser "realistic" (encoded in the script; keep these if you
write your own):

- **Real Firefox, not headless Chromium** — different TLS/JS fingerprint,
  fewer headless tells, and it passes walls that block Chromium headless.
- **Never override the user agent** on a real browser — a UA that doesn't
  match the engine's fingerprint is itself a bot tell. Do set a plausible
  `viewport` (1440×900), `locale` (`en-US`), and `timezone_id`.
- **`wait_until="domcontentloaded"` + a fixed settle wait (~3s)**, not
  `networkidle` — ad-heavy news pages never go network-idle.
- **Extract metadata from JSON-LD first** (`script[type="application/ld+json"]`
  → `headline`/`datePublished`/`author`), then `og:*`/`article:*` meta tags,
  then a DOM byline probe. JSON-LD is the most reliable because publishers
  maintain it for Google.
- **Markdown from `article`/`main` innerHTML** via `markdownify` — not
  `document.body`, which drowns the text in nav/footer junk.

For ad-hoc extraction beyond what `--fetch` prints, the same pattern inline:

```bash
uv run --with playwright,markdownify python - <<'EOF'
from playwright.sync_api import sync_playwright
from markdownify import markdownify
with sync_playwright() as p:
    b = p.firefox.launch(headless=True)
    page = b.new_context(viewport={"width": 1440, "height": 900},
                         locale="en-US",
                         timezone_id="America/New_York").new_page()
    page.goto("URL-HERE", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(3000)                    # let JS render
    html = page.evaluate("() => (document.querySelector('article, main')"
                         " || document.body).innerHTML")
    print(markdownify(html, heading_style="ATX", strip=["img"]))
    b.close()
EOF
```

**Rung 2 — Chrome DevTools MCP.** A real Chrome with a real profile; use it
when rung 1 is blocked or the page needs interaction (cookie banners, "show
more" buttons, scroll-to-load). The working loop:

1. `new_page` with the URL (or `navigate_page` in an existing tab).
2. `take_snapshot` — the accessibility tree IS the readable page; usually
   enough to verify title/byline/date without any scripting.
3. For exact metadata or JS-rendered values, `evaluate_script` — you have
   the full console. The JSON-LD extractor, console form:

```js
() => {
  const out = {title: document.title, meta: {}, ld: []};
  for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
    try {
      const walk = (n) => {
        if (Array.isArray(n)) { n.forEach(walk); return; }
        if (n && typeof n === 'object') {
          const hit = {};
          for (const k of ['headline','datePublished','author'])
            if (k in n) hit[k] = typeof n[k] === 'object' ? n[k].name : n[k];
          if (Object.keys(hit).length) out.ld.push(hit);
          Object.values(n).forEach(walk);
        }
      };
      walk(JSON.parse(s.textContent));
    } catch (e) {}
  }
  for (const m of ['og:title','article:published_time','author']) {
    const el = document.querySelector(`meta[property="${m}"], meta[name="${m}"]`);
    if (el) out.meta[m] = el.content;
  }
  return out;
}
```

4. `take_screenshot` when the claim is visual (a chart, a layout, a UI).

Honest limit, measured: DataDome-class walls block even this and say why —
"Use of developer or inspection tools" — CDP automation is detectable. When
you hit the slider CAPTCHA, stop; rung 3.

**Rung 3 — read the archive.** The `archived=` snapshot you pin anyway
(§4) doubles as the bot-wall reader: open the
`https://web.archive.org/web/<ts>/<url>` snapshot instead of the live page —
Wayback serves what its crawler saw, wall-free. If the entry has no snapshot
yet (fresh pages often don't), run `--archive` first; a just-captured
snapshot can take a few minutes to become readable.

**Rung 4 — manual.** Open it in your own browser, verify the fields, stamp
with a note of what you saw. Some paywalls end here; that's fine — the rule
is only that a human (or agent) actually read the source.

**PDFs:** download and `pdftotext file.pdf - | head -50` — don't verify PDFs
through a browser viewport.

### Per-entry checklist

- [ ] Title matches the source exactly
- [ ] Author/organization correct (byline on the actual page, not the snippet)
- [ ] Date correct — year AND month/day where specified
- [ ] URL resolves and points to the *specific* source (not a "latest version" landing
  page); direct PDF links for reports
- [ ] Any `note` field figures match the actual source
- [ ] Derived comparisons re-computed ("enough to power X homes" math checks out)

### Verdicts

| Verdict | Meaning | Action |
|---|---|---|
| **Accurate** | Matches source and cross-references | none |
| **Mostly accurate** | Core fact right, minor imprecision | optional fix |
| **Partially accurate** | Details wrong or overstated | fix required |
| **Inaccurate** | Contradicts the source | must fix |
| **Wrong source** | Fact right, cited source doesn't contain it | update citation |

### Common error patterns to hunt

Stale landing pages; wrong month; rounding drift ("55%" → "more than 50%"); project
conflation (two projects merged into one story); quote paraphrase inside quotation marks;
causal oversimplification; entity details (HQ, spelling, role); date-projection drift
("2030 projection" becoming "by 2028").

---

## 4. The `verified` and `archived` bib fields

Every verified BibTeX entry records when it was last checked against the live
source, and where its Wayback Machine copy lives:

```bibtex
@article{duffy2025datacenters,
    author       = {Duffy, Clare},
    title        = {Exact Title From the Page},
    journaltitle = {CNN},
    date         = {2025-11-03},
    url          = {https://...},
    urldate      = {2026-06-10},
    verified     = {2026-06-10},
    archived     = {https://web.archive.org/web/20260610.../https://...}
}
```

Conventions:
- `verified = {YYYY-MM-DD}` — date of the last **full-field fetch-and-check**. Absent
  field = unverified. `urldate` is when the URL was accessed; `verified` asserts the
  metadata was checked. They usually match; they mean different things.
- `archived = {snapshot URL}` — a dated Wayback Machine snapshot; books outlive
  URLs (the 57% lesson), so verification without preservation decays.
  `uv run scripts/verify_citation.py --archive` fills it automatically:
  existing snapshots are reused (any age — `verified` carries freshness),
  missing ones are captured through Save Page Now. Authenticated capture
  (~6/min) uses `SAVEPAGENOW_ACCESS_KEY`/`SECRET_KEY` from
  archive.org/account/s3.php; anonymous works but is slower. Perma.cc is a
  fine manual alternative for load-bearing citations (free tier ~10/month).
  `make verify-citations` (and therefore `make release`) requires **both**
  stamps on every url entry.
- Entries that fail verification get a `% TODO: VERIFY — <issue>` comment above them
  until resolved; the publication gate is zero TODO-VERIFY comments.
- Stale rule: before publication, any entry whose `verified` date predates the current
  fact-check pass gets re-spot-checked (at minimum a random sample via `scripts/sample_text.py` plus `verify_citation.py` on the affected keys at
  100% pass).
- Standard entry shapes (report/article/online/book, organizations in double braces
  `{{Org Name}}`) follow the source project's cite-check doc; keep one `refs.bib`
  organized by chapter with comment headers.

---

## 5. Per-chapter verification worksheets

Fact-check passes are auditable, per chapter, in `research/fact-check-<YYYY-MM>/`:³

```
research/fact-check-2026-06/
├── 00-canonical-figures.md    ← pinned cross-chapter numbers (see REVIEW-QA.md §4)
├── ch01.md                    ← chapter worksheet / provenance log
├── ch02.md
└── ...
```

Worksheet format:

```markdown
# Chapter X — Claim Inventory & Provenance (pass 2026-06)

## Claims

1. **Line 45:** "RFC 791 was published in September 1981"
   - Type: SPEC-VERIFIABLE | Source: rfc.jsonl | Verdict: Accurate
2. **Line 78:** "Cerf sketched the design on a napkin"
   - Type: HISTORICAL | Source needed: oral history | Verdict: Wrong source → replaced
3. **Line 120:** "consumed 30% of non-residential water"
   - Type: STATISTICAL | Source: city water dept report 2024 (fetched 2026-06-10)
   - Verdict: Mostly accurate — report says 29.6%; text now "about 30%"

## Summary
Claims checked: 23 | Updated: 6 | Unresolved: 1 (flagged in synthesis)
```

Group claims into thematic batches of 5–8 for parallel verification (opening narrative /
scale figures / physical impacts / outcomes...). Every changed claim gets a provenance
row: old text, new text, source, access date. Roll up per-chapter status (claims checked
/ updated / unresolved) into a table in `docs/fact-check.md`.

---

## 6. Citation placement and honesty in prose

- Statistics: cite immediately after the number; integrate naturally ("According to the
  2025 JLARC audit...").
- Direct quotes: cite immediately; the words inside quotation marks are *exactly* the
  source's.
- Preprints labeled "(a preprint awaiting peer review)"; ongoing proceedings "ongoing";
  approximations "about." Never let a citation imply more authority than the source has.
- **Paraphrase, never reproduce.** Learning from sources is the job; copying passages —
  even public-domain ones — into the book is not. Citation is an ethical obligation:
  name the source and point the reader there.
- No weasel citations ("studies show," "experts agree") — name it or own it.
- When drawing on your own sibling projects, cite the *underlying primary source*, not
  the sibling project.

---

## 7. Quality gates

- [ ] Every cited entry verified (fetched, field-checked) with a `verified` date
- [ ] Zero `% TODO: VERIFY` comments in the bib
- [ ] Every url entry carries `archived = {Wayback snapshot}` (`verify_citation.py --archive`)
- [ ] `make verify-citations` passes (all URLs reachable, all stamped, all archived)
- [ ] Per-chapter worksheets complete; unresolved items listed in the review synthesis
- [ ] Canonical figures pinned and consistent book-wide
- [ ] Clean rebuild with no bibliography errors

---

¹ Error table and rules from datacenter-2026-book CLAUDE.md ("YOU HAVE FAILED AT THIS
BEFORE") and cite-check.md; the 50% sample from legal-tech-history-book cite-check.md.
² Claim classification from history-through-rfc-book CITATION-METHODOLOGY.md (Phase 1),
generalized ("RFC-VERIFIABLE" → "SPEC-VERIFIABLE").
³ Worksheet/provenance-log pattern from htsd-book `research/fact-check-2026-06/` and
docs/fact-check.md; Playwright workflow from legal-tech + htsd cite-check docs. The
`verified` field formalizes the convention those projects tracked via urldate + logs.
