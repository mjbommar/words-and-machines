#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydetex>=1.1.1",
#     "nupunkt>=0.6.0",
# ]
# ///
"""
Check for repetitive language patterns in the book.

Analyzes LaTeX chapters and/or research notes to find:
- Repeated n-grams (3-6 word phrases)
- Common sentence starts
- Duplicate sentences

Uses pydetex to strip LaTeX and nupunkt for sentence segmentation.

Usage:
    # Analyze LaTeX chapters
    uv run scripts/check_repetition.py

    # Analyze research notes
    uv run scripts/check_repetition.py --research

    # Find duplicate sentences
    uv run scripts/check_repetition.py --duplicates

    # Analyze specific files
    uv run scripts/check_repetition.py --file latex/chapters/01-intro.tex
"""

import argparse
import re
from collections import Counter, defaultdict
from pathlib import Path

from pydetex import pipelines
from nupunkt import PunktSentenceTokenizer

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LATEX_DIR = PROJECT_ROOT / "latex"
CHAPTERS_DIR = LATEX_DIR / "chapters"
RESEARCH_DIR = PROJECT_ROOT / "research" / "_shared"


def strip_latex(text: str) -> str:
    """Strip LaTeX formatting from text."""
    cleaned = pipelines.strict(text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def strip_markdown(text: str) -> str:
    """Strip Markdown formatting from text."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    # Remove headers
    text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove emphasis
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove list markers
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    # Remove tables
    text = re.sub(r'\|[^\n]+\|', '', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    """Extract n-grams from a list of tokens."""
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def tokenize_words(text: str) -> list[str]:
    """Simple word tokenization."""
    words = re.findall(r"[a-z']+", text.lower())
    return words


def normalize_sentence(text: str) -> str:
    """Normalize a sentence for comparison."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_files(args) -> list[tuple[Path, str]]:
    """Find files to analyze. Returns list of (path, type) tuples."""
    files = []

    if args.file:
        path = Path(args.file)
        if path.suffix == '.tex':
            files.append((path, 'latex'))
        elif path.suffix == '.md':
            files.append((path, 'markdown'))
        return files

    if args.research:
        # Analyze research notes
        for subdir in ['people', 'events', 'themes', 'controversies']:
            dir_path = RESEARCH_DIR / subdir
            if dir_path.exists():
                for md_file in dir_path.glob('*.md'):
                    if md_file.name not in ('README.md', 'TEMPLATE.md'):
                        files.append((md_file, 'markdown'))
    else:
        # Analyze LaTeX chapters
        if CHAPTERS_DIR.exists():
            for tex_file in sorted(CHAPTERS_DIR.glob('*.tex')):
                files.append((tex_file, 'latex'))

    return files


def analyze_ngrams(files: list[tuple[Path, str]], sent_tokenizer) -> None:
    """Analyze n-gram frequencies across files."""
    all_text = []
    all_sentences = []

    for file_path, file_type in files:
        print(f"Processing: {file_path.name}")
        raw_text = file_path.read_text()

        if file_type == 'latex':
            clean_text = strip_latex(raw_text)
        else:
            clean_text = strip_markdown(raw_text)

        all_text.append(clean_text)
        sentences = sent_tokenizer.tokenize(clean_text)
        all_sentences.extend(sentences)

    full_text = " ".join(all_text)
    words = tokenize_words(full_text)

    print(f"\nTotal words: {len(words):,}")
    print(f"Total sentences: {len(all_sentences):,}")

    # Count n-grams
    for n in [3, 4, 5, 6]:
        print(f"\n{'='*60}")
        print(f"Most common {n}-grams (3+ occurrences):")
        print('='*60)

        ngrams = get_ngrams(words, n)
        counts = Counter(ngrams)
        common = [(ng, c) for ng, c in counts.most_common(200) if c >= 3]

        if not common:
            print("  (none)")
            continue

        for ngram, count in common[:40]:
            phrase = " ".join(ngram)
            print(f"  {count:3d}x  {phrase}")

    # Common sentence starts
    print(f"\n{'='*60}")
    print("Common sentence starts (first 4 words, 3+ occurrences):")
    print('='*60)

    sentence_starts = []
    for sent in all_sentences:
        words_in_sent = tokenize_words(sent)
        if len(words_in_sent) >= 4:
            sentence_starts.append(tuple(words_in_sent[:4]))

    start_counts = Counter(sentence_starts)
    common_starts = [(s, c) for s, c in start_counts.most_common(50) if c >= 3]

    if not common_starts:
        print("  (none)")
    else:
        for start, count in common_starts[:25]:
            phrase = " ".join(start)
            print(f"  {count:3d}x  {phrase}")


def find_duplicates(files: list[tuple[Path, str]], sent_tokenizer, min_words: int = 8) -> None:
    """Find duplicate sentences across files."""
    sentence_locations: dict[str, list[tuple[str, str, int]]] = defaultdict(list)

    for file_path, file_type in files:
        raw_text = file_path.read_text()

        if file_type == 'latex':
            clean_text = strip_latex(raw_text)
        else:
            clean_text = strip_markdown(raw_text)

        sentences = sent_tokenizer.tokenize(clean_text)

        for i, sent in enumerate(sentences):
            normalized = normalize_sentence(sent)
            word_count = len(normalized.split())
            if word_count >= min_words:
                sentence_locations[normalized].append(
                    (file_path.name, sent.strip(), i)
                )

    # Find duplicates
    duplicates = {
        norm: locs for norm, locs in sentence_locations.items() if len(locs) > 1
    }

    print(f"\n{'='*60}")
    print(f"Duplicate Sentences (min {min_words} words)")
    print('='*60)

    if not duplicates:
        print("\n  No duplicate sentences found!")
        return

    print(f"\n  Found {len(duplicates)} duplicate sentences:\n")

    sorted_dups = sorted(duplicates.items(), key=lambda x: -len(x[1]))

    for normalized, locations in sorted_dups[:20]:
        print(f"\n  [{len(locations)} occurrences]")
        for filename, original, sent_idx in locations:
            display = original if len(original) <= 80 else original[:80] + "..."
            print(f"    {filename}: \"{display}\"")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Check for repetitive language patterns"
    )
    parser.add_argument(
        '--research', '-r',
        action='store_true',
        help="Analyze research notes instead of LaTeX chapters"
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help="Analyze a specific file"
    )
    parser.add_argument(
        '--duplicates', '-d',
        action='store_true',
        help="Focus on finding duplicate sentences"
    )
    parser.add_argument(
        '--min-words',
        type=int,
        default=8,
        help="Minimum words for duplicate detection (default: 8)"
    )
    args = parser.parse_args()

    files = find_files(args)

    if not files:
        if args.research:
            print("No research notes found in research/_shared/")
        else:
            print("No LaTeX chapters found in latex/chapters/")
        print("Use --research to analyze research notes, or --file to specify a file.")
        return

    print(f"Found {len(files)} files to analyze\n")

    sent_tokenizer = PunktSentenceTokenizer()

    if args.duplicates:
        find_duplicates(files, sent_tokenizer, args.min_words)
    else:
        analyze_ngrams(files, sent_tokenizer)
        find_duplicates(files, sent_tokenizer, args.min_words)


if __name__ == "__main__":
    main()
