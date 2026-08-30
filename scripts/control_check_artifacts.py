#!/usr/bin/env python3
"""Negative control: remove a nested required manifest field and require rejection."""

from __future__ import annotations

import copy
import json

import check_artifacts


def main() -> int:
    path = (
        check_artifacts.ARTIFACTS
        / "claims/A0.comp.byte-roundtrip-8-16/manifest.json"
    )
    record = copy.deepcopy(json.loads(path.read_text()))
    record["checker"].pop("expected_result")
    errors = check_artifacts.validate_schema_value(record, check_artifacts.SCHEMA)
    if any("expected_result" in error for error in errors):
        print("schema-mismatch: nested checker.expected_result is missing")
        return 1
    print("control-failure: malformed manifest was accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
