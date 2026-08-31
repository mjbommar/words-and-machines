from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from scripts import verify_citation


class ArchiveFallbackTests(unittest.TestCase):
    def test_direct_success_does_not_consult_archive(self) -> None:
        with patch.object(
            verify_citation, "check_url", return_value=(True, "HTTP 200")
        ) as check:
            result = verify_citation.check_with_archive_fallback(
                object(), "https://origin.example/source", "https://archive.example/copy"
            )
        self.assertEqual(result, (True, "HTTP 200"))
        check.assert_called_once()

    def test_reachable_archive_recovers_blocked_origin(self) -> None:
        with patch.object(
            verify_citation,
            "check_url",
            side_effect=[(False, "HTTP 403"), (True, "HTTP 200")],
        ):
            result = verify_citation.check_with_archive_fallback(
                object(), "https://origin.example/source", "https://archive.example/copy"
            )
        self.assertEqual(result, (True, "HTTP 403; archive HTTP 200"))

    def test_missing_or_dead_archive_remains_failure(self) -> None:
        with patch.object(
            verify_citation, "check_url", return_value=(False, "HTTP 403")
        ) as check:
            no_archive = verify_citation.check_with_archive_fallback(
                object(), "https://origin.example/source", ""
            )
        self.assertEqual(no_archive, (False, "HTTP 403"))
        check.assert_called_once()

        with patch.object(
            verify_citation,
            "check_url",
            side_effect=[(False, "HTTP 403"), (False, "HTTP 404")],
        ):
            dead_archive = verify_citation.check_with_archive_fallback(
                object(), "https://origin.example/source", "https://archive.example/missing"
            )
        self.assertEqual(dead_archive, (False, "HTTP 403; archive HTTP 404"))

    def test_timestampless_wayback_url_resolves_to_immutable_snapshot(self) -> None:
        response = Mock(
            status_code=200,
            url="https://web.archive.org/web/20240530155124/http://example.com/source",
        )
        client = Mock()
        client.get.return_value = response
        result = verify_citation.resolve_dated_snapshot(
            client, "https://web.archive.org/web/https://example.com/source"
        )
        self.assertEqual(result, str(response.url))

    def test_dated_wayback_url_needs_no_network_resolution(self) -> None:
        client = Mock()
        snapshot = "https://web.archive.org/web/20240530155124/https://example.com/source"
        self.assertEqual(
            verify_citation.resolve_dated_snapshot(client, snapshot), snapshot
        )
        client.get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
