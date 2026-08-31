"""Reader-visible semantics that the strict EPUB gate must preserve."""

import json
import tempfile
import unittest
from pathlib import Path

from converter.core import Context, Extracted, preprocess
from TexSoup import TexSoup


class EpubConverterTests(unittest.TestCase):
    def context(self, root: Path) -> Context:
        ctx = Context({}, root / "book", root / "work", {}, {})
        ctx.begin_chapter(1, "chapter.xhtml", Extracted())
        return ctx

    def render(self, source: str, ctx: Context) -> str:
        store = Extracted()
        ctx.extracted = store
        parsed = TexSoup(preprocess(source, store))
        return "\n".join(ctx.convert_blocks(parsed.contents))

    def test_math_lists_and_typographic_wrappers_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ctx = self.context(Path(directory))
            html = self.render(
                r"Before \(x \mathbin{\cdot} y\)."
                r"\begin{enumerate}\item One \textit{term}.\end{enumerate}"
                r"\[x+1=2\]",
                ctx,
            )
        self.assertIn('<math xmlns="http://www.w3.org/1998/Math/MathML"', html)
        self.assertIn("<ol>", html)
        self.assertIn("<li><p>One <i>term</i>.</p></li>", html)
        self.assertIn('display="block"', html)
        self.assertNotIn("<mo><mrow>", html)
        self.assertEqual([], ctx.content_errors)
        self.assertEqual({}, ctx.unknowns)

    def test_artifact_uses_the_object_record_and_keeps_its_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "objects").mkdir()
            (root / "book").mkdir()
            record = {
                "id": "A0.comp.demo",
                "title": "Demonstration",
                "epistemic_status": "computed",
                "scope": "One input.",
                "evidence": [{"kind": "trace-replay",
                              "trust_class": "computation",
                              "check_status": "checked"}],
            }
            (root / "objects" / "A0.comp.demo.json").write_text(json.dumps(record))
            ctx = self.context(root)
            html = self.render(
                r"\begin{artifact}{A0.comp.demo}Body survives."
                r"\ArtifactScope{A0.comp.demo}\end{artifact}",
                ctx,
            )
        self.assertIn("Demonstration", html)
        self.assertIn("Body survives.", html)
        self.assertIn("computed", html)
        self.assertIn("One input.", html)
        self.assertIn("trace-replay / computation (checked)", html)
        self.assertIn('aria-label="Object A0.comp.demo: Demonstration"', html)
        self.assertEqual([], ctx.content_errors)
        self.assertEqual({}, ctx.unknowns)


if __name__ == "__main__":
    unittest.main()
