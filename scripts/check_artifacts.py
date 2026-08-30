#!/usr/bin/env python3
"""Validate and optionally replay every active evidence manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
SCHEMA = json.loads((ARTIFACTS / "schema" / "manifest.schema.json").read_text())
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CLAIM = re.compile(r"^(A0|RV64|X64|REL|EVID)\.[A-Za-z0-9._-]+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


def validate_schema_value(value: object, schema: dict, location: str = "$") -> list[str]:
    """Validate the JSON Schema subset used by the checked-in manifest schema."""
    errors: list[str] = []
    expected_type = schema.get("type")
    type_matches = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
    }
    if expected_type and not type_matches.get(expected_type, True):
        return [f"{location}: expected {expected_type}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: {value!r} is not in {schema['enum']!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{location}: string is too short")
        pattern = schema.get("pattern")
        if pattern and not re.fullmatch(pattern, value):
            errors.append(f"{location}: does not match {pattern!r}")
        if schema.get("format") == "date" and not DATE.fullmatch(value):
            errors.append(f"{location}: is not a YYYY-MM-DD date")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{location}: has too few items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema_value(item, item_schema, f"{location}[{index}]"))
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{location}: missing required field {key}")
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child = f"{location}.{key}"
            if key in properties:
                errors.extend(validate_schema_value(item, properties[key], child))
            elif additional is False:
                errors.append(f"{location}: unknown field {key}")
            elif isinstance(additional, dict):
                errors.extend(validate_schema_value(item, additional, child))
    return errors


def validate_binding(rec: dict, manifest_path: Path) -> list[str]:
    """Require the active object and manifest to name the same runnable route."""
    errors: list[str] = []
    claim_id = rec.get("claim_id", "")
    object_path = ROOT / "objects" / f"{claim_id}.json"
    if not object_path.is_file():
        return [f"active object missing: objects/{claim_id}.json"]
    try:
        obj = json.loads(object_path.read_text())
    except Exception as exc:
        return [f"active object invalid JSON: {exc}"]
    relative_manifest = str(manifest_path.relative_to(ROOT))
    matches = [
        evidence
        for evidence in obj.get("evidence", [])
        if relative_manifest in evidence.get("semantic_inputs", [])
    ]
    if len(matches) != 1:
        return [f"active object must bind this manifest exactly once, found {len(matches)}"]
    evidence = matches[0]
    comparisons = [
        ("checker command", evidence.get("checker_command"), rec.get("checker", {}).get("command")),
        ("negative-control command", evidence.get("negative_control"), rec.get("negative_control", {}).get("command")),
        ("negative-control failure", evidence.get("expected_failure"), rec.get("negative_control", {}).get("expected_failure")),
        ("trust class", evidence.get("trust_class"), rec.get("trust_class")),
    ]
    for label, object_value, manifest_value in comparisons:
        if object_value != manifest_value:
            errors.append(f"object/manifest {label} mismatch")
    return errors


def validate(path: Path) -> tuple[dict | None, list[str]]:
    errors: list[str] = []
    try:
        rec = json.loads(path.read_text())
    except Exception as exc:
        return None, [f"invalid JSON: {exc}"]

    errors.extend(validate_schema_value(rec, SCHEMA))
    claim_id = rec.get("claim_id", "")
    if CLAIM.fullmatch(claim_id) and path.parent.name != claim_id:
        errors.append("claim directory does not match claim_id")

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
    if not errors:
        errors.extend(validate_binding(rec, path))
    return rec, errors


def run_command(command: str) -> tuple[int, str]:
    """Run one manifest command from the repository root."""
    process = subprocess.run(
        command,
        shell=True,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    return process.returncode, (process.stdout + process.stderr).strip()


def replay(rec: dict) -> list[str]:
    """Reproduce, check, and mutation-test one declared route."""
    errors: list[str] = []
    axeyum = Path(os.environ.get("AXEYUM", "../axeyum")).expanduser().resolve()
    revision = subprocess.run(
        ["git", "-C", str(axeyum), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    expected_revision = rec["environment"]["axeyum_revision"]
    if revision.returncode != 0:
        return [f"cannot read Axeyum revision at {axeyum}"]
    if revision.stdout.strip() != expected_revision:
        return [
            f"Axeyum revision mismatch: expected {expected_revision}, "
            f"found {revision.stdout.strip()}"
        ]

    producer = rec["producer"]
    returncode, output = run_command(producer["command"])
    if returncode != 0:
        return [f"producer exited {returncode}: {output.splitlines()[-3:]}"]
    for group in ("semantic_inputs", "artifacts"):
        for item in rec[group]:
            target = local_path(item["path"])
            if not target.is_file():
                errors.append(f"producer left {group} path missing: {item['path']}")
            elif digest(target) != item["sha256"]:
                errors.append(f"producer changed pinned {group} digest: {item['path']}")
    if errors:
        return errors

    checker = rec["checker"]
    returncode, output = run_command(checker["command"])
    if returncode != 0:
        errors.append(f"checker exited {returncode}: {output.splitlines()[-3:]}")
    elif checker["expected_result"] not in output:
        errors.append(
            f"checker output omitted expected result {checker['expected_result']!r}"
        )

    control = rec["negative_control"]
    returncode, output = run_command(control["command"])
    if returncode == 0:
        errors.append("negative control exited 0 (control did not fire)")
    elif control["expected_failure"] not in output:
        errors.append(
            f"negative control omitted expected failure {control['expected_failure']!r}"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="run checker and negative control")
    args = parser.parse_args()
    manifests = sorted((ARTIFACTS / "claims").glob("*/manifest.json"))
    bad = 0
    claim_ids: set[str] = set()
    for path in manifests:
        rec, errors = validate(path)
        if rec is not None:
            claim_id = rec.get("claim_id", "")
            if claim_id in claim_ids:
                errors.append(f"duplicate claim_id {claim_id}")
            claim_ids.add(claim_id)
            if args.run and not errors:
                errors.extend(replay(rec))
        print(("BAD" if errors else "ok "), path.relative_to(ROOT))
        for error in errors:
            print("    -", error)
        bad += bool(errors)
    suffix = "; commands replayed" if args.run else "; structure only"
    print(f"{len(manifests)} active manifest(s), {bad} with problems{suffix}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
