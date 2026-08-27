"""Regression tests for the nine-book SBE calibration report."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "calibrate_simplified", ROOT / "scripts" / "calibrate_simplified.py")
assert SPEC and SPEC.loader
calibration = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = calibration
SPEC.loader.exec_module(calibration)


class CalibrationReportTests(unittest.TestCase):
    def test_active_findings_are_partitioned_into_work_queues(self) -> None:
        finding = calibration.sbe.Finding
        findings = [
            finding("a.tex", 1, "warn", "unintroduced term", "term"),
            finding("a.tex", 2, "warn", "undefined abbreviation", "abbr"),
            finding("a.tex", 3, "warn", "unapproved word", "word"),
            finding("a.tex", 4, "error", "unapproved phrase", "phrase"),
            finding("a.tex", 5, "warn", "term drift", "other"),
            finding("a.tex", 6, "idea", "unapproved word", "advisory"),
        ]
        self.assertEqual(calibration.finding_counts(findings), {
            "terms": 1,
            "abbreviations": 1,
            "substitutions": 2,
            "other_findings": 1,
        })

    def test_markdown_uses_singular_error_and_prints_queue_totals(self) -> None:
        score = calibration.Score(
            book="Fixture", path="/fixture", files=1, words=100, names=0,
            core_percent=95.0, recognized_percent=0.5,
            unlisted_percent=1.0, markers_per_1k=0.5,
            errors=1, warnings=2, terms=1, abbreviations=1,
            substitutions=1, other_findings=0,
        )
        report = calibration.markdown([score])
        self.assertIn("1 error; 2 warnings", report)
        self.assertIn("1 terms; 1 abbreviations; 1 substitutions; 0 other", report)


if __name__ == "__main__":
    unittest.main()
