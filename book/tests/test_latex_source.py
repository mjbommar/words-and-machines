from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from converter.latex_source import (
    VERBATIM_ENVS,
    discover_verbatim_environments,
    extract_prose,
)


class SourcePreservingLatexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        discover_verbatim_environments.cache_clear()
        self.tmp.cleanup()

    def test_canonical_verbatim_vocabulary_is_shared(self) -> None:
        from converter.core import VERBATIM_ENVS as epub_verbatim

        self.assertIs(VERBATIM_ENVS, epub_verbatim)

    def test_discovers_legacy_listing_name_with_digits(self) -> None:
        preamble = self.root / "latex" / "preamble"
        preamble.mkdir(parents=True)
        (preamble / "boxes.tex").write_text(
            r"\newtcblisting{vt100box}[1][]{listing only}"
        )
        raw = (
            "Before.\n"
            "\\begin{vt100box}\n$ unmatched { code % literal\n"
            "\\end{vt100box}\n"
            "After.\n"
        )
        text = extract_prose(raw, root=self.root)
        self.assertIn("Before.", text)
        self.assertIn("After.", text)
        self.assertNotIn("unmatched", text)
        self.assertEqual(raw.count("\n"), text.count("\n"))

    def test_nested_environment_options_do_not_leak_into_prose(self) -> None:
        raw = (
            r"\begin{definitionbox}[unbreakable,importance=low,"
            r"title={\textbf{Private Label}}]Visible body.\end{definitionbox}"
        )
        text = extract_prose(raw, root=self.root)
        self.assertIn("Visible body.", text)
        self.assertNotIn("Private Label", text)
        self.assertNotIn("importance", text)

    def test_semantic_wrappers_are_transparent_but_opaque_keys_are_not(self) -> None:
        raw = (
            r"The \proto{DNS} resolver appears in \hyperref[sec:dns]{the next "
            r"section}. \autocite{secret-key} \Cref{fig:hidden}. "
            r"\rowcolors{2}{white}{bg-note}"
        )
        text = extract_prose(raw, root=self.root)
        self.assertIn("DNS", text)
        self.assertIn("the next section", text)
        self.assertNotIn("sec:dns", text)
        self.assertNotIn("secret-key", text)
        self.assertNotIn("fig:hidden", text)
        self.assertNotIn("bg-note", text)

    def test_caption_is_prose_but_table_data_and_quotation_are_not(self) -> None:
        raw = (
            "\\begin{table}\n\\caption{Reader-facing caption}\n"
            "\\begin{tabular}{ll}secret & cells\\\\\\end{tabular}\n"
            "\\end{table}\n"
            "\\begin{quotation}quoted promulgate text\\end{quotation}\n"
        )
        text = extract_prose(raw, root=self.root)
        self.assertIn("Reader-facing caption", text)
        self.assertNotIn("secret", text)
        self.assertNotIn("promulgate", text)


if __name__ == "__main__":
    unittest.main()
