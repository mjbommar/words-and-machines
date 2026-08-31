#!/usr/bin/env python3
"""Fail early unless AXEYUM is a source-compatible, built replay checkout."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*command: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def required_revisions() -> tuple[str, ...]:
    revisions: set[str] = set()
    for path in sorted((ROOT / "artifacts" / "claims").glob("*/manifest.json")):
        record = json.loads(path.read_text())
        revisions.add(record["environment"]["axeyum_revision"])
    return tuple(sorted(revisions))


def main() -> int:
    checkout = Path(
        os.environ.get("AXEYUM", ROOT.parent / "axeyum")
    ).expanduser().resolve()
    errors: list[str] = []

    if not checkout.is_dir():
        print(f"axeyum-checkout: ERROR: checkout directory does not exist: {checkout}", file=sys.stderr)
        return 1

    head = run("git", "rev-parse", "HEAD", cwd=checkout)
    if head.returncode != 0:
        errors.append(f"not an Axeyum Git checkout: {checkout}")
    else:
        for revision in required_revisions():
            ancestry = run(
                "git", "merge-base", "--is-ancestor", revision, head.stdout.strip(),
                cwd=checkout,
            )
            if ancestry.returncode != 0:
                errors.append(
                    f"HEAD {head.stdout.strip()} does not contain pinned revision {revision}"
                )

    python = checkout / ".venv" / "bin" / "python"
    if not python.is_file():
        errors.append(f"missing built Python environment: {python}")
    else:
        imported = run(
            str(python),
            "-c",
            "from axeyum import machine; assert machine.a0.Instruction.halt()",
            cwd=ROOT,
        )
        if imported.returncode != 0:
            detail = imported.stderr.strip().splitlines()[-1] if imported.stderr.strip() else "import failed"
            errors.append(f"Axeyum Python machine surface unavailable: {detail}")

    cargo_wrapper = checkout / "scripts" / "cargo-serialized.sh"
    if not os.access(cargo_wrapper, os.X_OK):
        errors.append(f"missing executable Cargo replay wrapper: {cargo_wrapper}")

    if errors:
        for error in errors:
            print(f"axeyum-checkout: ERROR: {error}", file=sys.stderr)
        print(
            "axeyum-checkout: use a clean checkout of current Axeyum main, then run "
            "`uv sync --dev` and `TMPDIR=/path/on/disk uv run --no-sync maturin develop`",
            file=sys.stderr,
        )
        return 1

    print(
        f"axeyum-checkout: OK {checkout} at {head.stdout.strip()} "
        f"({len(required_revisions())} pinned revisions present)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
