"""Regression tests for the SBE checker.

These are intentionally small behavior fixtures. Cross-book calibration
measures editorial usefulness; these tests preserve mechanics that a green
run on the template's sample chapters cannot exercise.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_simplified", ROOT / "scripts" / "check_simplified.py")
sbe = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = sbe
SPEC.loader.exec_module(sbe)

BUILD_SPEC = importlib.util.spec_from_file_location(
    "build_simplified_lexicon",
    ROOT / "scripts" / "build_simplified_lexicon.py")
builder = importlib.util.module_from_spec(BUILD_SPEC)
assert BUILD_SPEC.loader is not None
sys.modules[BUILD_SPEC.name] = builder
BUILD_SPEC.loader.exec_module(builder)


class CheckerBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.standard = sbe.Standard({})
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    @staticmethod
    def kinds(book: sbe.Book, kind: str) -> list[sbe.Finding]:
        return [finding for finding in book.findings if finding.kind == kind]

    def test_keyterm_with_inline_definition_introduces_term(self) -> None:
        path = self.write("01.tex", "A \\keyterm{zorbax} is a small test.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "unintroduced term"))

    def test_term_markup_without_definition_does_not_explain(self) -> None:
        path = self.write(
            "01.tex",
            "The \\term{zorbax} appears. The zorbax remains.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual(1, len(self.kinds(book, "unintroduced term")))

    def test_later_acronym_expansion_does_not_rewrite_history(self) -> None:
        files = [
            self.write("01.tex", "The XYZ failed.\n"),
            self.write("02.tex", "Xylophone Yield Zone (XYZ) succeeded.\n"),
        ]
        book = sbe.Book(files, self.standard)
        messages = [f.message for f in self.kinds(book, "undefined abbreviation")]
        self.assertTrue(any("'XYZ'" in message for message in messages))

    def test_first_use_acronym_expansion_is_accepted(self) -> None:
        path = self.write(
            "01.tex", "The Xylophone Yield Zone (XYZ) succeeded. XYZ grew.\n")
        book = sbe.Book([path], self.standard)
        messages = [f.message for f in self.kinds(book, "undefined abbreviation")]
        self.assertFalse(any("'XYZ'" in message for message in messages))

    def test_plural_abbreviation_is_checked_under_its_base_form(self) -> None:
        # Lowercase `api` is in the frequency lexicon. The plural spelling is
        # nevertheless strong abbreviation evidence and must not disappear.
        path = self.write("01.tex", "APIs connect systems. APIs also fail.\n")
        book = sbe.Book([path], self.standard)
        messages = [f.message for f in self.kinds(book, "undefined abbreviation")]
        self.assertTrue(any("'API' (2x)" in message for message in messages))
        self.assertEqual(2, book.abbrev_uses["API"])

    def test_expanded_plural_abbreviation_is_accepted(self) -> None:
        path = self.write(
            "01.tex",
            "Application Programming Interfaces (APIs) connect systems. "
            "APIs also fail.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))
        # The parenthetical definition is name-adjacent and therefore not
        # counted as a bare use; the later plural is tracked under XYZ.
        self.assertEqual(1, book.abbrev_uses["API"])

    def test_possessive_abbreviation_is_checked(self) -> None:
        path = self.write("01.tex", "XYZ's failure was costly.\n")
        book = sbe.Book([path], self.standard)
        messages = [f.message for f in self.kinds(book, "undefined abbreviation")]
        self.assertTrue(any("'XYZ'" in message for message in messages))

    def test_later_sentence_does_not_count_as_reverse_expansion(self) -> None:
        path = self.write(
            "01.tex", "XYZ failed. Xylophone Yield Zone recovered.\n")
        book = sbe.Book([path], self.standard)
        messages = [f.message for f in self.kinds(book, "undefined abbreviation")]
        self.assertTrue(any("'XYZ'" in message for message in messages))

    def test_reverse_expansion_in_first_use_sentence_is_accepted(self) -> None:
        path = self.write(
            "01.tex", "XYZ, the Xylophone Yield Zone, failed.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_expansion_can_keep_a_connector_initial(self) -> None:
        path = self.write(
            "01.tex",
            "The Neutral Point of View policy, universally abbreviated NPOV, "
            "governs articles. NPOV matters.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_blanked_source_comment_does_not_break_nearby_expansion(self) -> None:
        path = self.write(
            "01.tex",
            "A community benefit agreement is a contract.\n"
            "% source note: " + "x" * 1000 + "\n"
            "CBAs are enforceable. A CBA can set conditions.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_distant_prior_initials_do_not_expand_acronym(self) -> None:
        filler = " ".join(["ordinary"] * 81)
        path = self.write(
            "01.tex",
            f"Xylophone Yield Zone existed. {filler} XYZ failed. XYZ fell.\n",
        )
        book = sbe.Book([path], self.standard)
        messages = [f.message for f in self.kinds(book, "undefined abbreviation")]
        self.assertTrue(any("'XYZ'" in message for message in messages))

    def test_reverse_expansion_can_keep_and(self) -> None:
        path = self.write(
            "01.tex",
            "ENIAC—the Electronic Numerical Integrator and Computer—filled a "
            "room. ENIAC produced heat.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_capitalized_definition_components_can_spell_acronym(self) -> None:
        path = self.write(
            "01.tex",
            "An INUS condition is Insufficient but Non-redundant, part of an "
            "Unnecessary but Sufficient bundle. INUS is a causal concept.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_hyphenated_expansion_can_spell_acronym(self) -> None:
        path = self.write(
            "01.tex",
            "A man-in-the-middle or MITM attack intercepts traffic. MITM "
            "attacks can steal passwords.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_hyphenated_compound_can_contribute_one_initial(self) -> None:
        path = self.write(
            "01.tex",
            "The Vereenigde Oost-Indische Compagnie, or VOC, issued shares. "
            "VOC persisted.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_mixed_case_names_are_not_terms(self) -> None:
        path = self.write("01.tex", "The xAI and arXiv names appear here.\n")
        book = sbe.Book([path], self.standard)
        messages = [f.message for f in self.kinds(book, "unintroduced term")]
        self.assertFalse(any("xAI" in message or "arXiv" in message
                             for message in messages))

    def test_alphanumeric_codes_are_not_abbreviations(self) -> None:
        path = self.write(
            "01.tex", "The H100 replaced A100, FP16, v2, 2xx, and abc123.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))
        self.assertEqual([], self.kinds(book, "unintroduced term"))

    def test_short_and_long_all_cap_tokens_stay_out_of_word_denominator(self) -> None:
        path = self.write("01.tex", "AI met SUPERCALIFRAGILISTIC today.\n")
        book = sbe.Book([path], self.standard)
        counted = sum(book.counts[key]
                      for key in ("core", "open", "declared", "unlisted"))
        self.assertEqual(2, counted)

    def test_configured_all_cap_name_is_not_an_abbreviation(self) -> None:
        standard = sbe.Standard({"simplified_english": {"names": ["LEXIS"]}})
        path = self.write("01.tex", "LEXIS launched a search service.\n")
        book = sbe.Book([path], standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))
        self.assertEqual(1, book.counts["name"])

    def test_listingbox_code_is_not_prose(self) -> None:
        path = self.write(
            "01.tex",
            "Before.\n\\begin{listingbox}\ndef f(value: str):\n  return value\n"
            "\\end{listingbox}\nAfter.\n",
        )
        book = sbe.Book([path], self.standard)
        messages = [f.message for f in book.findings]
        self.assertFalse(any("'str'" in message for message in messages))

    def test_quoted_transcript_environment_is_not_prose(self) -> None:
        path = self.write(
            "01.tex",
            "Before.\n\\begin{transcriptsrc}\nThe NVT uses zorbaxes.\n"
            "\\end{transcriptsrc}\nAfter.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], book.findings)

    def test_reverse_dash_gloss_introduces_term(self) -> None:
        path = self.write(
            "01.tex",
            "They have no common measure---\\emph{zorbax}. Later, the zorbax "
            "returns.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "unintroduced term"))

    def test_reverse_noun_apposition_introduces_term(self) -> None:
        path = self.write(
            "01.tex",
            "It uses the hyperbolic tangent function, zorbax. Zorbax returns.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "unintroduced term"))

    def test_comma_appositive_gloss_introduces_term(self) -> None:
        path = self.write(
            "01.tex", "They called it zorbax, a small blue tool. Zorbax grew.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "unintroduced term"))

    def test_inflections_use_library_lemmas(self) -> None:
        self.standard.open.update({"child", "run", "annotator", "clawback"})
        self.assertNotEqual("unlisted", self.standard.tier("children"))
        self.assertNotEqual("unlisted", self.standard.tier("ran"))
        self.assertNotEqual("unlisted", self.standard.tier("annotators"))
        # `clawback` is outside Simplemma's dictionary; inflect handles the
        # grammatical-number fallback without a project suffix table.
        self.assertEqual("open", self.standard.tier("clawbacks"))

    def test_derivation_is_not_silently_treated_as_inflection(self) -> None:
        self.standard.open.update({"surprise", "mechanize"})
        # OpenGloss recognizes both forms directly; neither inherits the free
        # tier from its base word.
        self.assertEqual("recognized", self.standard.tier("surprisal"))
        self.assertEqual("recognized", self.standard.tier("mechanizable"))

    def test_opengloss_recognition_does_not_silently_admit_a_term(self) -> None:
        self.standard.recognized.add("zorbax")
        path = self.write("01.tex", "A zorbax appears. The zorbax remains.\n")
        book = sbe.Book([path], self.standard)
        findings = self.kinds(book, "unintroduced term")
        self.assertEqual(1, len(findings))
        self.assertIn("OpenGloss headword", findings[0].message)

    def test_quoted_terms_and_abbreviations_are_not_author_first_uses(self) -> None:
        path = self.write(
            "01.tex", "``Zorbax uses XYZ and zorbax.'' Ordinary prose.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "unintroduced term"))
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_explicit_abbreviated_wording_identifies_short_form(self) -> None:
        path = self.write(
            "01.tex",
            "Trust on first use, often abbreviated TOFU, is a policy. "
            "TOFU can reduce setup work.\n",
        )
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_this_is_wording_can_introduce_a_term(self) -> None:
        path = self.write(
            "01.tex", "The text becomes tokens. This is zorbax. Zorbax repeats.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "unintroduced term"))

    def test_known_singular_words_are_not_damaged_by_noun_heuristic(self) -> None:
        self.standard.open.update({"analysis", "business"})
        self.assertEqual("analysis", sbe.stem_key("analysis"))
        self.assertEqual("business", sbe.stem_key("business"))
        self.assertEqual("gapless", sbe.stem_key("gapless"))
        self.assertEqual("ddos", sbe.stem_key("ddos"))

    def test_plural_round_trip_repairs_truncated_dictionary_lemma(self) -> None:
        self.assertEqual("tranche", sbe.stem_key("tranches"))

    def test_introduced_compound_parts_introduce_later_hyphenated_form(self) -> None:
        path = self.write(
            "01.tex",
            "A \u005ckeyterm{gigawatt} is one billion watts. Later, the "
            "one-gigawatt plant opened. Another one-gigawatt plant followed.\n",
        )
        book = sbe.Book([path], self.standard)
        messages = [finding.message for finding in
                    self.kinds(book, "unintroduced term")]
        self.assertFalse(any("one-gigawatt" in message for message in messages))

    def test_domain_and_model_names_are_not_abbreviations(self) -> None:
        path = self.write(
            "01.tex", "LWN.net reported it. The NVIDIA GTX 580 followed.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_uppercase_filename_suffix_is_not_an_abbreviation(self) -> None:
        path = self.write(
            "01.tex", "Open HOSTS.TXT first. Copy HOSTS.TXT afterward.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(book, "undefined abbreviation"))

    def test_single_use_terms_are_reserved_for_advisory_sweep(self) -> None:
        path = self.write("01.tex", "A zorbax appears.\n")
        normal = sbe.Book([path], self.standard)
        self.assertEqual([], self.kinds(normal, "unintroduced term"))

        advisory = sbe.Book([path], sbe.Standard({}, advisory=True))
        findings = self.kinds(advisory, "unintroduced term")
        self.assertEqual(1, len(findings))
        self.assertEqual("idea", findings[0].severity)

    def test_possessive_term_has_structured_subject_and_valid_config(self) -> None:
        path = self.write(
            "01.tex",
            "A zorbax's choice matters. Another zorbax's "
            "choice follows.\n",
        )
        book = sbe.Book([path], self.standard)
        findings = self.kinds(book, "unintroduced term")
        self.assertEqual(1, len(findings))
        self.assertEqual("zorbax's", findings[0].subject)
        self.assertIn('- term: "zorbax\'s"', book.emit_config())
        row = findings[0].render("jsonl")
        self.assertIn('"subject": "zorbax\'s"', row)

    def test_technical_phrase_exceptions_are_advisory(self) -> None:
        path = self.write(
            "01.tex",
            "Differentiate with respect to x. Payment in lieu of taxes follows.\n",
        )
        book = sbe.Book([path], self.standard)
        phrases = self.kinds(book, "unapproved phrase")
        self.assertEqual(2, len(phrases))
        self.assertEqual({"warn"}, {finding.severity for finding in phrases})

    def test_marker_attribution_excludes_quoted_material(self) -> None:
        path = self.write(
            "01.tex", "A requirement applies. ``A requirement shall apply.''\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual(1, book.marker_uses["requirement"])
        self.assertNotIn("shall", book.marker_uses)

    def test_straight_double_quoted_source_is_not_checked(self) -> None:
        path = self.write(
            "01.tex",
            'The requirement applies. "With regard to policy, notify us."\n',
        )
        book = sbe.Book([path], self.standard)
        messages = [finding.message.lower() for finding in book.findings]
        self.assertFalse(any("with regard to" in message for message in messages))
        self.assertFalse(any("notify" in message for message in messages))
        self.assertEqual(1, book.marker_uses["requirement"])

    def test_common_such_is_not_a_register_marker(self) -> None:
        path = self.write("01.tex", "Such examples are common in prose.\n")
        book = sbe.Book([path], self.standard)
        self.assertNotIn("such", book.marker_uses)

    def test_style_owned_word_remains_a_register_marker(self) -> None:
        path = self.write("01.tex", "The utilization rate increased.\n")
        book = sbe.Book([path], self.standard)
        self.assertEqual(1, book.marker_uses["utilization"])


class CuratedPolicyTests(unittest.TestCase):
    def test_duplicate_substitution_is_rejected(self) -> None:
        policy = {
            "substitutions": [
                {"from": "thereof", "to": "its", "grade": "error"},
                {"from": "Thereof", "to": "their", "grade": "warn"},
            ]
        }
        with self.assertRaises(SystemExit):
            builder.validate_curated(policy)

    def test_unknown_grade_is_rejected(self) -> None:
        policy = {
            "phrase_substitutions": [
                {"from": "in frobnication of", "to": "for", "grade": "ban"},
            ]
        }
        with self.assertRaises(SystemExit):
            builder.validate_curated(policy)

    def test_measurement_marker_set_is_canonical(self) -> None:
        policy = {
            "substitutions": [
                {"from": "utilization", "grade": "warn"},
                {"from": "technical", "grade": "idea"},
                {"from": "ordinary", "grade": "idea"},
            ],
            "phrase_substitutions": [
                {"from": "and/or", "grade": "warn"},
            ],
            "marker_only": ["technical"],
        }
        markers = builder.measurement_markers(policy)
        self.assertIn("utilization", markers)
        self.assertIn("and/or", markers)
        self.assertIn("technical", markers)
        self.assertIn("shall", markers)
        self.assertNotIn("ordinary", markers)
        self.assertNotIn("such", markers)


class BookPolicyTests(unittest.TestCase):
    def test_unknown_simplified_english_key_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            sbe.Standard({"simplified_english": {"abbrevitations": ["XYZ"]}})

    def test_unknown_threshold_key_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            sbe.Standard({
                "simplified_english": {
                    "thresholds": {"undefined_abbrevation": "off"},
                }
            })


class FileDiscoveryTests(unittest.TestCase):
    def test_main_input_graph_excludes_commented_and_unreferenced_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chapters = root / "chapters"
            sections = chapters / "sections"
            sections.mkdir(parents=True)
            main = root / "main.tex"
            main.write_text(
                "\\input{chapters/02-second}\n"
                "% \\input{chapters/commented}\n"
                "\\input{chapters/01-wrapper}\n",
                encoding="utf-8",
            )
            (chapters / "02-second.tex").write_text("Second.\n")
            (chapters / "commented.tex").write_text("Commented.\n")
            (chapters / "unused.tex").write_text("Unused.\n")
            (chapters / "01-wrapper.tex").write_text(
                "Wrapper. \\input{chapters/sections/body}\n")
            (sections / "body.tex").write_text("Body.\n")

            found = sbe.included_tex_files(
                main, include_matter=False, latex=root
            )
            self.assertEqual(
                ["02-second.tex", "01-wrapper.tex", "body.tex"],
                [path.name for path in found],
            )


if __name__ == "__main__":
    unittest.main()
