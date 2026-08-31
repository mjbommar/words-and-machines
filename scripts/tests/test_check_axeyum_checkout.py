"""Controls for the Axeyum source/build compatibility preflight."""

from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

from scripts import check_axeyum_checkout as check


class AxeyumCheckoutTests(unittest.TestCase):
    def test_inventory_reads_every_distinct_manifest_revision(self) -> None:
        revisions = check.required_revisions()
        self.assertEqual(len(revisions), 7)
        self.assertEqual(tuple(sorted(set(revisions))), revisions)

    def test_missing_checkout_fails_with_a_direct_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "absent"
            stderr = io.StringIO()
            with patch.dict(os.environ, {"AXEYUM": str(missing)}), redirect_stderr(stderr):
                self.assertEqual(check.main(), 1)
        self.assertIn("checkout directory does not exist", stderr.getvalue())

    def test_unrelated_directory_cannot_pass_as_axeyum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stderr = io.StringIO()
            with patch.dict(os.environ, {"AXEYUM": directory}), redirect_stderr(stderr):
                self.assertEqual(check.main(), 1)
        self.assertIn("not an Axeyum Git checkout", stderr.getvalue())
        self.assertIn("missing built Python environment", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
