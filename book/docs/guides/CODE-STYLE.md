# CODE-STYLE — Code, Terminals, and Prompts in Print

Rules for every code example, terminal session, error message, and AI prompt/response
that appears in a book. The governing constraint: a 6"×9" trade page at a mono font
gives you **65–75 usable characters** in a code block. Code that exceeds it breaks
mid-word, overflows, or shrinks to unreadable.¹

**The three promises of book code:** readable in print, runnable without modification,
understandable by a reader new to programming.

---

## 1. Line width limits

| Content type | Hard limit | Target |
|---|---|---|
| Code (any language) | **72 characters** | 65 |
| Terminal commands | 72 | 60 |
| JSON / YAML output | 72 | 60 |
| Error messages | 72 (truncate) | — |
| File paths shown in code | 50 | 40 |

**72 is absolute and includes indentation.** Count with a ruler line:

```
# This comment is exactly seventy-two characters long, no more, no less
```

---

## 2. Line-breaking recipes by language

### Python — implicit continuation with parentheses

```python
# BAD: 89 characters
result = analyze_contract(file_path, extraction_rules, output_format, include_meta)

# GOOD: break inside parentheses
result = analyze_contract(
    file_path,
    extraction_rules,
    output_format,
    include_meta,
)
```

### Python — long strings: implicit concatenation

```python
error_msg = (
    "The file could not be processed because the format "
    "is not supported by the current version"
)
```

### Python — long paths: variables + pathlib

```python
from pathlib import Path

documents = Path.home() / "Documents" / "Matters"
contract = documents / "AcmeCorp" / "agreement.pdf"
```

### Shell — backslash continuation, one flag per line

```bash
curl -X POST https://api.example.com/v1/messages \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model": "model-name"}'
```

### JSON — always vertical

```json
{
  "client": {
    "name": "Acme Corporation",
    "id": "2024-001"
  }
}
```

### Quick reference

| Language | Technique |
|---|---|
| Python | parentheses > backslash; string concat for text |
| Bash | trailing `\`, two-space continuation indent |
| JSON/YAML | vertical, 2-space indent |
| SQL | one clause per line, keywords at line start |
| URLs in prose | short URL you control, footnote, or `\url{}` hyphenation |

---

## 3. Path and environment conventions

- **One standard working directory for the whole book** (e.g. `~/projects/` or a
  domain-appropriate `~/legal-projects/`), introduced once, used everywhere.
- **Never real user paths.** No `/Users/sarah/Documents/Client Files/...`.
- **Variables over hardcoding**; `pathlib.Path` for platform neutrality.
- Show the directory tree once, early, and keep examples consistent with it.

---

## 4. Platform handling

1. **Default to Unix commands** — they cover Mac, Linux, and Windows via WSL.
2. **Installation/setup gets platform-specific treatment once**, in the setup chapter.
3. **When a command genuinely differs**, use platform markers (icons or labels) inline:
   - macOS: `pbcopy < file.txt`
   - Windows (WSL): `clip.exe < file.txt`
   - Linux: `xclip -selection clipboard < file.txt`
4. Document WSL path translation once (`C:\Users\...` ↔ `/mnt/c/Users/...`), reference
   thereafter.

---

## 5. Terminal sessions

- Prompt is always `$` — no `%`, `>`, `PS>`, no `user@host` prefixes.
- Separate command from output visually; blank line between command/output pairs.

```bash
$ python --version
Python 3.11.4
```

---

## 6. Output and error truncation

Real tracebacks are 20+ lines and 100+ characters wide. Show the relevant portion only,
with an explicit truncation marker, and shorten paths to basenames:

```
[... traceback truncated ...]
  File "analyzer.py", line 23, in process_document
    with open(path) as f:
FileNotFoundError: No such file or directory: 'contract.pdf'
```

For long tool output, keep the head and the line that matters. When an error implies a
fix, show it as a comment pair:

```
# ModuleNotFoundError: No module named 'pymupdf'
# Fix: pip install pymupdf
```

**Rule:** printed output must be *actual* output from a run of the printed code —
truncated, never invented.

---

## 7. Prompts and AI responses

Books that show AI interaction need distinct, consistent environments:

| Environment | Use for |
|---|---|
| `promptcode` (or equivalent) | What the reader types to the model — verbatim |
| `outputcode` | The model's response — real, truncated with `[...]` |
| `terminalbox` | Shell sessions (commands + output) |
| language code blocks | Source code with highlighting |

Rules:
- Prompts are shown **verbatim and reproducible** — same 72-char wrapping discipline.
- Model responses are real outputs, dated/versioned when behavior matters ("works on
  model X-2024-04, not on Y"), and truncated honestly.
- Never paraphrase inside a code/prompt box; paraphrase belongs in prose.
- Pin model names/versions when a claim depends on them.

---

## 8. Comments

- Explain **why**, not what — and domain context a programmer wouldn't know.
- Comments obey the same 72-char limit; break long ones across lines.

```python
# GOOD: explains why
# Skip files modified in the last hour (may still be in use)
if file.stat().st_mtime > time.time() - 3600:
    continue

# BAD: explains what
# Open the file
with open(file_path) as f:
```

---

## 9. Code–prose rhythm

The reader should never be more than ~10 lines of code from prose explaining why those
lines matter.²

**Bad pattern:** 3 paragraphs of setup → 40 lines of code → 3 paragraphs of analysis.

**Good pattern:**
1–2 sentences of what to look for → 5–10 lines of code → 2–3 sentences on the result and
why it matters → 1 sentence of setup → next block.

Blocks over ~15 lines need a strong reason (a complete script the reader will copy —
which should also live in the companion repo).

---

## 10. Checklist for every code example

- [ ] Tested; runs without modification; output shown matches an actual run
- [ ] No line exceeds 72 characters (including indentation and comments)
- [ ] Paths use the book's standard directory and variables, never hardcoded user paths
- [ ] Comments explain why, not what
- [ ] Errors/output truncated with explicit markers
- [ ] Platform-specific content marked; default is Unix/WSL-compatible
- [ ] Correct environment (code / terminal / prompt / output)
- [ ] Prose within 10 lines of any code
- [ ] Long/complete versions in the companion repository, referenced by path

---

¹ Distilled from vibe-coding-for-lawyers `docs/CODE-STYLE-GUIDE.md` — the house's most
complete code-in-books artifact (72-char rule, recipes, truncation, platform strategy).
² Interleaving rhythm from hacking-with-ai-book STYLE-CRAFT ("code-prose interleaving").
