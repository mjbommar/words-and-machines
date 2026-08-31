"""Regression controls for the portable Ace accessibility runner."""

import os
import unittest
from unittest.mock import patch

from scripts import check_epub_a11y


class AceCommandTests(unittest.TestCase):
    def test_prefers_pinned_puppeteer_runner_over_electron_cli(self) -> None:
        available = {"npx": "/usr/bin/npx", "ace": "/usr/local/bin/ace"}
        with patch.dict(os.environ, {}, clear=True), patch.object(
            check_epub_a11y.shutil, "which", side_effect=available.get
        ):
            self.assertEqual(
                check_epub_a11y.ace_command(),
                [
                    "npx",
                    "--yes",
                    "--package",
                    "@daisy/ace@1.4.6",
                    "ace-puppeteer",
                ],
            )

    def test_uses_direct_cli_only_when_npx_is_unavailable(self) -> None:
        available = {"ace": "/usr/local/bin/ace"}
        with patch.dict(os.environ, {}, clear=True), patch.object(
            check_epub_a11y.shutil, "which", side_effect=available.get
        ):
            self.assertEqual(check_epub_a11y.ace_command(), ["ace"])

    def test_environment_override_has_priority(self) -> None:
        with patch.dict(os.environ, {"ACE_CMD": "custom-ace --safe"}, clear=True):
            self.assertEqual(check_epub_a11y.ace_command(), ["custom-ace", "--safe"])


if __name__ == "__main__":
    unittest.main()
