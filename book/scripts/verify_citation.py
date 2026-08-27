# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.27", "savepagenow>=1.2"]
# ///
"""Citation URL verification + archiving (docs/guides/CITATIONS.md).

Walks latex/bib/references.bib, checks every entry with a `url` field,
and reports reachability plus the `verified = {YYYY-MM-DD}` stamp status.
Born of a measured 57% URL error rate in a prior book: treat every
unverified citation as wrong until checked.

`--archive` additionally pins every cited URL in the Wayback Machine
and records the snapshot as `archived = {snapshot-url}`: the CDX
availability API is consulted first (an existing snapshot of any age is
kept — `verified=` is the freshness signal, the archive is the
outlives-the-URL copy), and only unarchived URLs go through Save Page
Now (via `savepagenow`; authenticated at ~6 req/min with
SAVEPAGENOW_ACCESS_KEY/SECRET_KEY from archive.org/account/s3.php,
anonymous and slower without).

    uv run scripts/verify_citation.py                 # report all url entries
    uv run scripts/verify_citation.py --key smith2024 # one entry
    uv run scripts/verify_citation.py --stamp         # add verified={today} on success
    uv run scripts/verify_citation.py --archive       # snapshot + archived= stamps
    uv run scripts/verify_citation.py --require-stamps --require-archives  # release gate
    uv run scripts/verify_citation.py --unused        # bib entries never cited in chapters

`--fetch URL` opens the page in a real headless Firefox and prints the
metadata a citation needs (title, byline, dates, JSON-LD) plus the page
as markdown — the verify-before-cite fetch for sites that block plain
HTTP and for JS-rendered pages. It needs two extra packages, so run it as:

    uv run --with playwright,markdownify scripts/verify_citation.py --fetch URL
    ... --fetch URL --markdown        # full page markdown (read the source)
    # one-time browser install: uv run --with playwright playwright install firefox

Escalation ladder when even that is blocked (DataDome/PerimeterX class):
Chrome DevTools MCP -> Wayback snapshot -> manual browser. Recipes and
the honest limits of each rung: docs/guides/CITATIONS.md §3.

This checks REACHABILITY and stamp presence only — it does not compare the
entry's title/author/date against the fetched page. That judgment call is
the citation-verifier agent's job (docs/guides/CITATIONS.md): open the
source, confirm it says what the prose claims, then --stamp.

For bot-walled sources plain HTTP misses, re-check by hand or with a real
browser (uv run --with playwright python - <<'EOF' ... EOF); this script
uses httpx with a desktop UA as the fast first pass.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "latex" / "bib" / "references.bib"
UA = ("Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0")


def parse_entries(text: str) -> list[dict]:
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.DOTALL):
        body = m.group(3)
        fields = {k.lower(): v.strip() for k, v in
                  re.findall(r"(\w+)\s*=\s*\{([^{}]*)\}", body)}
        entries.append({"type": m.group(1), "key": m.group(2),
                        "fields": fields, "span": m.span()})
    return entries


def check_url(client: httpx.Client, url: str) -> tuple[bool, str]:
    try:
        r = client.get(url, follow_redirects=True,
                       headers={"User-Agent": UA}, timeout=20)
        return r.status_code < 400, f"HTTP {r.status_code}"
    except httpx.HTTPError as e:
        return False, type(e).__name__


def existing_snapshot(client: httpx.Client, url: str) -> str | None:
    """Closest Wayback snapshot via the availability API, or None."""
    try:
        r = client.get("https://archive.org/wayback/available",
                       params={"url": url}, timeout=20,
                       follow_redirects=True,
                       headers={"User-Agent": UA})
        closest = r.json().get("archived_snapshots", {}).get("closest", {})
        if closest.get("available"):
            return closest["url"].replace("http://", "https://", 1)
    except (httpx.HTTPError, ValueError):
        pass
    return None


def save_snapshot(url: str, authed: bool) -> tuple[str | None, str]:
    """Capture via Save Page Now; returns (snapshot url, status note)."""
    import savepagenow
    try:
        snapshot, _fresh = savepagenow.capture_or_cache(
            url, user_agent=UA, authenticate=authed)
        # SPN sometimes answers with a timestamp-less redirect form;
        # only a dated /web/<ts>/ URL is a durable citation.
        if not re.search(r"/web/\d{8,14}", snapshot or ""):
            return None, f"SPN returned undated URL ({snapshot}) — retry"
        return snapshot, "captured"
    except savepagenow.exceptions.TooManyRequests:
        return None, "SPN rate-limited — rerun later" + (
            "" if authed else " (or set SAVEPAGENOW_ACCESS_KEY/SECRET_KEY)")
    except Exception as e:  # savepagenow raises several runtime errors
        return None, f"SPN {type(e).__name__}"


# Runs in the page: JSON-LD first (most reliable), then meta tags, then
# a DOM byline probe. Keep in sync with the DevTools-console variant in
# docs/guides/CITATIONS.md §3.
FETCH_META_JS = """
() => {
  const out = {title: document.title, meta: {}, ld: []};
  for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
    try {
      const walk = (n) => {
        if (Array.isArray(n)) { n.forEach(walk); return; }
        if (n && typeof n === 'object') {
          const hit = {};
          for (const k of ['headline','datePublished','dateModified','author'])
            if (k in n) hit[k] = typeof n[k] === 'object'
              ? (n[k].name || JSON.stringify(n[k]).slice(0, 80)) : n[k];
          if (Object.keys(hit).length) out.ld.push(hit);
          Object.values(n).forEach(walk);
        }
      };
      walk(JSON.parse(s.textContent));
    } catch (e) {}
  }
  for (const name of ['og:title','og:site_name','article:published_time',
                      'article:modified_time','author','date']) {
    const el = document.querySelector(
      `meta[property="${name}"], meta[name="${name}"]`);
    if (el && el.content) out.meta[name] = el.content;
  }
  const by = document.querySelector(
    '[rel="author"], .byline, [class*="byline" i], [itemprop="author"]');
  if (by) out.meta['dom-byline'] = by.textContent.trim().slice(0, 120);
  return out;
}
"""

BLOCK_MARKERS = ("captcha", "datadome", "perimeterx", "px-captcha",
                 "verification required", "access denied",
                 "unusual activity")


def fetch_with_browser(url: str, full_markdown: bool) -> int:
    """--fetch: real headless Firefox -> metadata + markdown."""
    try:
        from markdownify import markdownify
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "verify_citation: --fetch needs extra packages; run as\n"
            "  uv run --with playwright,markdownify "
            "scripts/verify_citation.py --fetch URL\n"
            "(one-time: uv run --with playwright playwright install firefox)")

    with sync_playwright() as p:
        try:
            browser = p.firefox.launch(headless=True)
        except Exception:
            sys.exit("verify_citation: no Firefox for Playwright — run "
                     "`uv run --with playwright playwright install firefox`")
        # Realistic context: real Firefox already sends its own real UA
        # (never override it — a mismatched UA is itself a bot tell);
        # give it a plausible viewport, locale, and timezone.
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  locale="en-US",
                                  timezone_id="America/New_York")
        page = ctx.new_page()
        resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)  # let client-side rendering settle
        status = resp.status if resp else 0
        meta = page.evaluate(FETCH_META_JS)
        html = page.evaluate(
            "() => (document.querySelector('article, main, [role=main]')"
            " || document.body).innerHTML")
        browser.close()

    print(f"STATUS   {status}")
    print(f"TITLE    {meta['title']}")
    for k, v in meta["meta"].items():
        print(f"META     {k} = {v}")
    seen = set()
    for hit in meta["ld"]:
        line = "; ".join(f"{k}={v}" for k, v in hit.items())
        if line not in seen:
            seen.add(line)
            print(f"JSON-LD  {line}")
    md = markdownify(html, heading_style="ATX",
                     strip=["img", "script", "style"])
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    print(f"MARKDOWN {len(md)} chars"
          + ("" if full_markdown else " (first 600; --markdown for all)"))
    print(md if full_markdown else md[:600])

    page_signal = (meta["title"] + " " + md[:2000]).lower()
    if status >= 400 or any(m in page_signal for m in BLOCK_MARKERS):
        print("\nverify_citation: looks bot-walled — escalate per "
              "docs/guides/CITATIONS.md §3 (DevTools MCP -> Wayback "
              "snapshot -> manual browser). This is 'unverified', "
              "not 'dead'.", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stamp", action="store_true",
                    help="write verified={today} into entries that pass")
    ap.add_argument("--archive", action="store_true",
                    help="pin URLs in the Wayback Machine; write archived={...}")
    ap.add_argument("--require-stamps", action="store_true",
                    help="exit 1 if any url entry lacks a verified stamp")
    ap.add_argument("--require-archives", action="store_true",
                    help="exit 1 if any url entry lacks an archived stamp")
    ap.add_argument("--key", default=None, help="check only this entry key")
    ap.add_argument("--unused", action="store_true",
                    help="list bib entries never cited in latex/chapters/ and exit")
    ap.add_argument("--fetch", metavar="URL", default=None,
                    help="fetch one URL in a real headless Firefox and print "
                         "title/byline/dates + markdown (needs "
                         "--with playwright,markdownify)")
    ap.add_argument("--markdown", action="store_true",
                    help="with --fetch: print the full page markdown")
    args = ap.parse_args()

    if args.fetch:
        sys.exit(fetch_with_browser(args.fetch, args.markdown))

    if not BIB.exists():
        sys.exit(f"verify_citation: {BIB.relative_to(ROOT)} not found")
    text = BIB.read_text()
    all_entries = parse_entries(text)

    if args.unused:
        chapters = " ".join(p.read_text() for p in
                            sorted((ROOT / "latex" / "chapters").glob("ch*.tex")))
        unused = [e["key"] for e in all_entries
                  if not re.search(rf"\\\w*cite\w*(?:\[[^\]]*\])*\{{[^}}]*"
                                   rf"\b{re.escape(e['key'])}\b", chapters)]
        for key in unused:
            print(f"unused: {key}")
        print(f"verify_citation: {len(unused)} of {len(all_entries)} entries "
              "never cited in chapters")
        sys.exit(1 if unused else 0)

    entries = [e for e in all_entries if "url" in e["fields"]]
    if args.key:
        entries = [e for e in entries if e["key"] == args.key]
        if not entries:
            sys.exit(f"verify_citation: no url-bearing entry with key {args.key!r}")
    if not entries:
        print("verify_citation: no url-bearing entries")
        return

    today = datetime.date.today().isoformat()
    authed = bool(os.environ.get("SAVEPAGENOW_ACCESS_KEY"))
    spn_wait = 10 if authed else 25  # ~6/min authenticated, ~2/min anon
    failures, unstamped, unarchived = 0, 0, 0
    stamps_to_add, archives_to_add = [], {}
    spn_used = False
    with httpx.Client() as client:
        for e in entries:
            url = e["fields"]["url"]
            stamped = e["fields"].get("verified", "")
            archived = e["fields"].get("archived", "")
            ok, status = check_url(client, url)
            mark = "OK " if ok else "FAIL"
            print(f"{mark} {e['key']:<28} {status:<12} "
                  f"verified={stamped or '—'}  archived={'yes' if archived else '—'}"
                  f"  {url[:60]}")
            if not ok:
                failures += 1
            elif not stamped:
                unstamped += 1
                if args.stamp:
                    stamps_to_add.append(e["key"])

            if args.archive and not archived:
                snapshot = existing_snapshot(client, url)
                if snapshot:
                    archives_to_add[e["key"]] = snapshot
                    print(f"     {e['key']:<28} archive: existing snapshot")
                else:
                    if spn_used:             # politeness between captures
                        time.sleep(spn_wait)
                    snapshot, note = save_snapshot(url, authed)
                    spn_used = True
                    if snapshot:
                        archives_to_add[e["key"]] = snapshot
                    print(f"     {e['key']:<28} archive: {note}")
            if not archived and e["key"] not in archives_to_add:
                unarchived += 1

    if stamps_to_add:
        for key in stamps_to_add:
            text = re.sub(
                rf"(@\w+\s*\{{\s*{re.escape(key)}\s*,)",
                rf"\1\n  verified = {{{today}}},",
                text, count=1)
    for key, snapshot in archives_to_add.items():
        text = re.sub(
            rf"(@\w+\s*\{{\s*{re.escape(key)}\s*,)",
            rf"\1\n  archived = {{{snapshot}}},",
            text, count=1)
    if stamps_to_add or archives_to_add:
        BIB.write_text(text)
        if stamps_to_add:
            print(f"verify_citation: stamped {len(stamps_to_add)} entries "
                  f"verified={{{today}}}")
        if archives_to_add:
            print(f"verify_citation: recorded {len(archives_to_add)} "
                  "archived= snapshot(s)")

    if failures:
        sys.exit(f"verify_citation: {failures} unreachable URL(s) — fix or "
                 "verify manually via a real browser before citing")
    if args.require_stamps and unstamped and not args.stamp:
        sys.exit(f"verify_citation: {unstamped} entry(ies) lack verified= "
                 "stamps (run with --stamp after manual review)")
    if args.require_archives and unarchived:
        sys.exit(f"verify_citation: {unarchived} entry(ies) lack archived= "
                 "snapshots (run with --archive)")
    print(f"verify_citation: OK ({len(entries)} url entries)")


if __name__ == "__main__":
    main()
