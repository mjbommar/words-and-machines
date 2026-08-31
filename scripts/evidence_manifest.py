"""Typed, reader-facing inspection of one book evidence manifest.

This module is orchestration, not a second implementation of machine
semantics.  Positive and negative verdicts come from the commands named by the
manifest, which invoke the pinned Axeyum Rust producer and checker.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts import check_artifacts as checks
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    import check_artifacts as checks


class ManifestError(RuntimeError):
    """A manifest could not be validated or one of its checks failed."""


@dataclass(frozen=True)
class CommandResult:
    """The observable result of one declared manifest command."""

    kind: str
    command: str
    returncode: int
    output: str
    matched: str


@dataclass(frozen=True)
class TrustBoundary:
    """The trust statement recorded by a manifest, without reinterpretation."""

    claim_id: str
    trust_class: str
    scope: str
    exclusions: tuple[str, ...]
    limitations: tuple[str, ...]
    checker_version: str
    axeyum_revision: str


class EvidenceManifest:
    """A validated active manifest rooted in this book repository.

    Loading validates the complete schema, all pinned file digests, and the
    corresponding object-ledger binding.  Running commands is explicit because
    a manifest is executable input and should never execute merely on import.
    """

    def __init__(self, path: Path, record: dict[str, object]) -> None:
        self.path = path
        self._record = record

    @classmethod
    def load(cls, path: str | Path) -> "EvidenceManifest":
        """Load and validate an active manifest by repository-relative path."""

        candidate = Path(path)
        if not candidate.is_absolute():
            try:
                candidate = checks.local_path(str(candidate))
            except ValueError as error:
                raise ManifestError(str(error)) from error
        else:
            candidate = candidate.resolve()
            if checks.ROOT not in candidate.parents:
                raise ManifestError(f"path escapes repository: {path}")
        record, errors = checks.validate(candidate)
        if record is None or errors:
            detail = "; ".join(errors) if errors else "manifest did not decode"
            raise ManifestError(f"cannot load {path}: {detail}")
        return cls(candidate, record)

    @property
    def claim_id(self) -> str:
        """Return the stable claim identifier."""

        return str(self._record["claim_id"])

    def verify_digests(self) -> tuple[str, ...]:
        """Recompute every semantic-input and artifact digest.

        Returns the verified repository-relative paths.  A mismatch raises
        :class:`ManifestError`; success is never inferred from mere existence.
        """

        verified: list[str] = []
        for group in ("semantic_inputs", "artifacts"):
            for item in self._record[group]:
                target = checks.local_path(item["path"])
                observed = checks.digest(target) if target.is_file() else None
                if observed != item["sha256"]:
                    raise ManifestError(
                        f"{group} digest mismatch for {item['path']}: "
                        f"expected {item['sha256']}, observed {observed or 'missing'}"
                    )
                verified.append(item["path"])
        return tuple(verified)

    def verify_axeyum_revision(self, axeyum: str | Path | None = None) -> str:
        """Require the checkout to contain the manifest's pinned revision."""

        checkout = Path(
            axeyum or os.environ.get("AXEYUM", checks.ROOT.parent / "axeyum")
        ).expanduser().resolve()
        head = subprocess.run(
            ["git", "-C", str(checkout), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if head.returncode != 0:
            raise ManifestError(f"cannot read Axeyum revision at {checkout}")
        expected = self._record["environment"]["axeyum_revision"]
        ancestry = subprocess.run(
            [
                "git",
                "-C",
                str(checkout),
                "merge-base",
                "--is-ancestor",
                expected,
                head.stdout.strip(),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if ancestry.returncode != 0:
            raise ManifestError(
                f"Axeyum checkout does not contain pinned revision {expected}; "
                f"HEAD is {head.stdout.strip()}"
            )
        return head.stdout.strip()

    @staticmethod
    def _tail(output: str) -> str:
        return "\n".join(output.splitlines()[-3:])

    @staticmethod
    def _command_environment(axeyum: str | Path | None) -> dict[str, str]:
        environment = os.environ.copy()
        if axeyum is not None:
            environment["AXEYUM"] = str(Path(axeyum).expanduser().resolve())
        return environment

    def reproduce(self, axeyum: str | Path | None = None) -> CommandResult:
        """Run the declared producer and require all pinned digests to survive."""

        self.verify_axeyum_revision(axeyum)
        producer = self._record["producer"]
        returncode, output = checks.run_command(
            producer["command"], env=self._command_environment(axeyum)
        )
        if returncode != 0:
            raise ManifestError(
                f"producer exited {returncode}: {self._tail(output)}"
            )
        self.verify_digests()
        return CommandResult("producer", producer["command"], returncode, output, "digests")

    def check(self, axeyum: str | Path | None = None) -> CommandResult:
        """Run the declared positive checker and match its required result text."""

        checker = self._record["checker"]
        returncode, output = checks.run_command(
            checker["command"], env=self._command_environment(axeyum)
        )
        expected = checker["expected_result"]
        if returncode != 0:
            raise ManifestError(f"checker exited {returncode}: {self._tail(output)}")
        if expected not in output:
            raise ManifestError(f"checker output omitted expected result {expected!r}")
        return CommandResult("checker", checker["command"], returncode, output, expected)

    def run_negative_control(self, axeyum: str | Path | None = None) -> CommandResult:
        """Require the declared mutation to fail with its named failure class."""

        control = self._record["negative_control"]
        returncode, output = checks.run_command(
            control["command"], env=self._command_environment(axeyum)
        )
        expected = control["expected_failure"]
        if returncode == 0:
            raise ManifestError("negative control exited 0 (control did not fire)")
        if expected not in output:
            raise ManifestError(f"negative control omitted expected failure {expected!r}")
        return CommandResult("negative-control", control["command"], returncode, output, expected)

    def trust_boundary(self) -> TrustBoundary:
        """Return the manifest's exact scope, exclusions, and trust class."""

        return TrustBoundary(
            claim_id=self.claim_id,
            trust_class=self._record["trust_class"],
            scope=self._record["scope"],
            exclusions=tuple(self._record["exclusions"]),
            limitations=tuple(self._record["limitations"]),
            checker_version=self._record["checker"]["version"],
            axeyum_revision=self._record["environment"]["axeyum_revision"],
        )
