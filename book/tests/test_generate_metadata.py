from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_metadata  # noqa: E402


class PublisherValidationTests(unittest.TestCase):
    def config(self) -> dict:
        return yaml.safe_load((ROOT / "book.yaml").read_text())

    def test_draft_metadata_may_leave_publisher_unconfirmed(self) -> None:
        config = self.config()
        config["book"]["publisher"] = ""
        generate_metadata.validate(config)

    def test_strict_release_requires_confirmed_publisher(self) -> None:
        config = self.config()
        config["book"]["publisher"] = ""
        with self.assertRaises(SystemExit):
            generate_metadata.validate_strict(config)

    def test_strict_release_still_checks_enabled_format_isbns(self) -> None:
        config = copy.deepcopy(self.config())
        config["book"]["publisher"] = "Confirmed Publisher"
        with self.assertRaises(SystemExit):
            generate_metadata.validate_strict(config)


if __name__ == "__main__":
    unittest.main()
