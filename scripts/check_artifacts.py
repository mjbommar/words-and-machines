#!/usr/bin/env python3
"""Validate active evidence manifests and their local digests."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
SCHEMA = json.loads((ARTIFACTS / "schema" / "manifest.schema.json").read_text())
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CLAIM = re.compile(r"^(A0|RV64|X64|REL|EVID)\.[A-Za-z0-9._-]+$")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def local_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    if ROOT not in path.parents:
        raise ValueError(f"path escapes repository: {value}")
    return path


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        rec = json.loads(path.read_text())
    except Exception as exc:
        return [f"invalid JSON: {exc}"]

    allowed = SCHEMA["properties"]
    for key in SCHEMA["required"]:
        if key not in rec:
            errors.append(f"missing required field {key}")
    for key in rec:
        if key not in allowed:
            errors.append(f"unknown field {key}")
    if rec.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not CLAIM.fullmatch(rec.get("claim_id", "")):
        errors.append("invalid claim_id")
    if rec.get("trust_class") not in allowed["trust_class"]["enum"]:
        errors.append("invalid trust_class")

    for group in ("semantic_inputs", "artifacts"):
        if not rec.get(group):
            errors.append(f"{group} must not be empty")
        for item in rec.get(group, []):
            value = item.get("path", "")
            expected = item.get("sha256", "")
            if not SHA256.fullmatch(expected):
                errors.append(f"{group} invalid sha256 for {value}")
                continue
            try:
                target = local_path(value)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if not target.is_file():
                errors.append(f"{group} path missing: {value}")
            elif digest(target) != expected:
                errors.append(f"{group} digest mismatch: {value}")

    control = rec.get("negative_control", {})
    for field in ("command", "expected_failure", "mutates"):
        if not control.get(field):
            errors.append(f"negative_control missing {field}")
    return errors


def main() -> int:
    manifests = sorted((ARTIFACTS / "claims").glob("*/manifest.json"))
    bad = 0
    for path in manifests:
        errors = validate(path)
        print(("BAD" if errors else "ok "), path.relative_to(ROOT))
        for error in errors:
            print("    -", error)
        bad += bool(errors)
    print(f"{len(manifests)} active manifest(s), {bad} with problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
