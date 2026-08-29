from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from trim_catalog import TRIM_CATALOG, TRIM_PRESETS
from update_cover_vars import KDP_SPINE_PER_PAGE


class TrimCatalogTests(unittest.TestCase):
    def test_expected_preset_dimensions(self) -> None:
        expected = {
            "5x8": (5.0, 8.0),
            "5.5x8.5": (5.5, 8.5),
            "6x9": (6.0, 9.0),
            "7x10": (7.0, 10.0),
            "7.5x9.25": (7.5, 9.25),
            "8x10": (8.0, 10.0),
            "8.25x11": (8.25, 11.0),
            "8.5x11": (8.5, 11.0),
        }
        self.assertEqual(expected, TRIM_PRESETS)

    def test_large_trim_classification_matches_kdp_boundary(self) -> None:
        for spec in TRIM_CATALOG.values():
            expected = spec.width > 6.12 or spec.height > 9
            self.assertEqual(expected, spec.kdp_large)

    def test_kdp_hardcover_subset(self) -> None:
        supported = {
            name for name, spec in TRIM_CATALOG.items()
            if spec.kdp_hardcover
        }
        self.assertEqual(
            {"5.5x8.5", "6x9", "7x10", "8.25x11"},
            supported,
        )

    def test_every_paper_has_limits_and_spine_formula(self) -> None:
        papers = set(KDP_SPINE_PER_PAGE)
        for spec in TRIM_CATALOG.values():
            self.assertEqual(papers, set(spec.paperback_max))
            self.assertTrue(all(limit >= 550
                                for limit in spec.paperback_max.values()))

    def test_large_textbook_presets_recommend_twelve_point(self) -> None:
        self.assertEqual(12, TRIM_CATALOG["8.25x11"].recommended_base_size)
        self.assertEqual(12, TRIM_CATALOG["8.5x11"].recommended_base_size)
        self.assertEqual(11, TRIM_CATALOG["7x10"].recommended_base_size)


if __name__ == "__main__":
    unittest.main()
