"""Execute the exact Axeyum Python listings printed in the manuscript."""

from __future__ import annotations

import unittest

from scripts.check_code_listings import CodeListing, listings


A0_ADDITION = "Encode, decode, and execute one A0 addition"


class AxeyumMachineExampleTests(unittest.TestCase):
    def _a0_addition(self) -> CodeListing:
        matches = [listing for listing in listings() if listing.caption == A0_ADDITION]
        self.assertEqual(len(matches), 1, "expected exactly one bound A0 addition listing")
        return matches[0]

    def test_chapter_6_a0_addition_listing_runs_unchanged(self) -> None:
        listing = self._a0_addition()
        namespace: dict[str, object] = {"__name__": "__book_listing__"}
        code = compile(listing.body, listing.location, "exec")
        exec(code, namespace)

    def test_wrong_addition_result_fires_the_listing_assertion(self) -> None:
        listing = self._a0_addition()
        mutated = listing.body.replace(
            "after.register(3).unsigned == 0x80",
            "after.register(3).unsigned == 0x81",
        )
        self.assertNotEqual(mutated, listing.body, "mutation control changed no source")
        with self.assertRaises(AssertionError):
            exec(compile(mutated, f"{listing.location}:control", "exec"), {})


if __name__ == "__main__":
    unittest.main()
