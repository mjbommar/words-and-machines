"""Reader-facing controls for the typed single-manifest interface."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.evidence_manifest import EvidenceManifest, ManifestError


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "artifacts/claims/X64.comp.decoder-step/manifest.json"


class EvidenceManifestTests(unittest.TestCase):
    def test_load_exposes_exact_trust_boundary(self) -> None:
        manifest = EvidenceManifest.load(MANIFEST)
        boundary = manifest.trust_boundary()
        self.assertEqual(manifest.claim_id, "X64.comp.decoder-step")
        self.assertEqual(boundary.trust_class, "computation")
        self.assertIn("seventeen", boundary.scope.lower())
        self.assertIn("1cb53b9a", boundary.axeyum_revision)

    def test_verify_digests_returns_every_bound_path(self) -> None:
        verified = EvidenceManifest.load(MANIFEST).verify_digests()
        self.assertEqual(len(verified), 2)
        self.assertTrue(all((ROOT / path).is_file() for path in verified))

    def test_path_escape_fails_closed(self) -> None:
        with self.assertRaisesRegex(ManifestError, "escapes repository"):
            EvidenceManifest.load("../outside.json")

    def test_positive_checker_requires_declared_text(self) -> None:
        manifest = EvidenceManifest.load(MANIFEST)
        with patch("scripts.evidence_manifest.checks.run_command", return_value=(0, "wrong")):
            with self.assertRaisesRegex(ManifestError, "omitted expected result"):
                manifest.check()

    def test_negative_control_must_exit_nonzero(self) -> None:
        manifest = EvidenceManifest.load(MANIFEST)
        with patch("scripts.evidence_manifest.checks.run_command", return_value=(0, "accepted")):
            with self.assertRaisesRegex(ManifestError, "control did not fire"):
                manifest.run_negative_control()

    def test_negative_control_requires_declared_failure_class(self) -> None:
        manifest = EvidenceManifest.load(MANIFEST)
        with patch("scripts.evidence_manifest.checks.run_command", return_value=(1, "other")):
            with self.assertRaisesRegex(ManifestError, "omitted expected failure"):
                manifest.run_negative_control()


if __name__ == "__main__":
    unittest.main()
