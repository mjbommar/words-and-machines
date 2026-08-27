# Narration / Audiobook Channels

`make narration-export` writes per-chapter plain text
(`build/narration/*.txt`) extracted from the converted EPUB: footnote
markers dropped, chapter-end Notes kept as a passage, figure captions
kept, code listings kept verbatim (delete those passages for books
where listings shouldn't be read aloud). It fails if LaTeX-like
fragments survive in non-code prose.

There is deliberately no full audiobook pipeline here — every current
AI-narration channel wants either the ebook itself or clean text, and
the economics (not the tooling) decide the channel.

## Channel economics (checked 2026-07; verify before committing)

| Channel | Input | Royalty | Files portable? | Notes |
|---|---|---|---|---|
| Google Play auto-narration | live Play Books EPUB | **52%** | **yes — downloadable, sellable elsewhere** | Best default: keeps your rights and files |
| KDP Virtual Voice | eligible KDP eBook | 40% | no | Amazon-only, $3.99–$14.99 price band, proprietary voices |
| Apple Books digital narration | reflowable English EPUB | standard Apple | no | Free but 1–2 months processing, limited categories; poor fit for technical books |
| ElevenLabs → Findaway/Spotify | manuscript text | varies (~$99+/book production) | yes | Premium quality; distributes everywhere **except Audible** (Amazon only allows its own Virtual Voice) |

House recommendation: start with Google Play auto-narration (portable
audio, best revenue share), add KDP Virtual Voice for Amazon reach —
they are not exclusive of each other. Skip Audible unless recording a
human narration.

Sources: KDP Virtual Voice help (kdp.amazon.com G3QRL9HQNF273Q2H),
Google Play auto-narrated audiobooks (play.google.com/books/publish/autonarrated/),
Apple digital narration (authors.apple.com/support/4519), Findaway ×
ElevenLabs distribution announcements (2025).
