"""Regression controls for build-doctor command-scope checks."""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import doctor  # noqa: E402


class DoctorTargetTests(unittest.TestCase):
    def test_parent_repository_target_satisfies_documented_command(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            book_makefile = root / "book.mk"
            repository_makefile = root / "repository.mk"
            book_makefile.write_text("pdf:\n")
            repository_makefile.write_text("code-check:\n")
            missing = doctor.missing_make_targets(
                "Run make pdf and repository-level make code-check.",
                (book_makefile, repository_makefile),
            )
            self.assertEqual(missing, set())

    def test_target_absent_from_both_scopes_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            makefile = Path(directory) / "Makefile"
            makefile.write_text("pdf:\n")
            self.assertEqual(
                doctor.missing_make_targets("Run make imaginary.", (makefile,)),
                {"imaginary"},
            )


if __name__ == "__main__":
    unittest.main()
