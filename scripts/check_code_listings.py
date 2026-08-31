#!/usr/bin/env python3
"""Fail when a manuscript code listing is not executable in its declared layer.

The book formerly printed several nonexistent Python APIs inside code boxes.
This gate keeps prose design targets out of executable-looking listings and
assembles every RV64I and x86-64 listing with LLVM.  A0 has no textual assembler
yet, so the gate parses its complete teaching grammar, checks operands and
register ranges, verifies explicit four-byte addresses, and resolves labels.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LATEX = ROOT / "book" / "latex"
LISTING = re.compile(
    r"\\begin\{codelisting\}\[(?P<options>.*?)\]\n"
    r"(?P<body>.*?)\\end\{codelisting\}",
    re.DOTALL,
)
CAPTION = re.compile(r"caption=\{(?P<caption>[^}]*)\}")
ADDRESS = re.compile(r"^(?P<address>[0-9a-fA-F]+):\s*(?P<body>.*)$")
LABEL_AND_BODY = re.compile(r"^(?P<label>[A-Za-z_][A-Za-z0-9_]*):\s*(?P<body>.*)$")
REGISTER = re.compile(r"r([0-7])$")
FUTURE_API = re.compile(
    r"illustrative|not yet implemented|future (?:api|interface)|"
    r"EvidenceManifest|CandidateLanguage\.a0|from axeyum\.machines|abs_case\(",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CodeListing:
    path: Path
    line: int
    caption: str
    language: str
    body: str

    @property
    def location(self) -> str:
        return f"{self.path.relative_to(ROOT)}:{self.line}"


def listings() -> list[CodeListing]:
    found: list[CodeListing] = []
    # Code promises can appear in front matter, appendices, or other included
    # sources as well as chapters.  Scan the complete manuscript tree so a new
    # listing cannot evade the executable gate by moving directories.
    for path in sorted(LATEX.rglob("*.tex")):
        text = path.read_text()
        for match in LISTING.finditer(text):
            caption_match = CAPTION.search(match["options"])
            caption = caption_match["caption"] if caption_match else ""
            language_match = re.search(
                r"(?:^|,)language=(?:\{(?P<braced>[^}]*)\}|(?P<plain>[^,]*))",
                match["options"],
            )
            language = ""
            if language_match:
                language = (language_match["braced"] or language_match["plain"] or "").strip()
            found.append(
                CodeListing(
                    path=path,
                    line=text.count("\n", 0, match.start()) + 1,
                    caption=caption,
                    language=language.lower(),
                    body=match["body"].rstrip(),
                )
            )
    return found


def classify(listing: CodeListing) -> str:
    caption = listing.caption.lower()
    body = listing.body
    if listing.language in {"python", "py"}:
        return "python"
    if body.startswith("AXEYUM="):
        return "shell"
    if "logical xor-reduction" in caption:
        return "pseudocode"
    if "rv64" in caption or re.search(r"\b(?:a[01]|x[0-9]|t[01]|sp|ra|s0)\b", body):
        return "rv64"
    if "x86" in caption or "system v" in caption or re.search(r"\b(?:rax|eax|rdi|rsi|rsp|rbx)\b", body):
        return "x86"
    return "a0"


def split_a0_lines(body: str, *, two_column: bool) -> list[str]:
    lines: list[str] = []
    for raw in body.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        # Only the tiny alphabet prints two independent instructions per row.
        if two_column:
            lines.extend(part.strip() for part in re.split(r"\s{6,}", raw) if part.strip())
        else:
            lines.append(raw)
    return lines


def parse_operands(text: str) -> list[str]:
    return [operand.strip() for operand in text.split(",") if operand.strip()]


def require_register(value: str, location: str) -> None:
    if not REGISTER.fullmatch(value):
        raise ValueError(f"{location}: invalid A0 register {value!r}; expected r0 through r7")


def check_a0(listing: CodeListing) -> None:
    labels: set[str] = set()
    branches: list[str] = []
    addresses: list[int] = []
    instructions: list[tuple[str, list[str], str]] = []
    for raw in split_a0_lines(
        listing.body,
        two_column="complete tiny candidate alphabet" in listing.caption.lower(),
    ):
        text = raw
        address_match = ADDRESS.match(text)
        if address_match:
            addresses.append(int(address_match["address"], 16))
            text = address_match["body"].strip()
        label_match = LABEL_AND_BODY.match(text)
        if label_match:
            labels.add(label_match["label"])
            text = label_match["body"].strip()
        if not text:
            continue
        parts = text.split(None, 1)
        mnemonic = parts[0].lower()
        operands = parse_operands(parts[1] if len(parts) == 2 else "")
        instructions.append((mnemonic, operands, raw))

    if addresses:
        expected = list(range(addresses[0], addresses[0] + 4 * len(addresses), 4))
        if addresses != expected:
            raise ValueError(
                f"{listing.location}: explicit A0 addresses {addresses} are not consecutive four-byte steps"
            )

    arity = {
        "mov": 2,
        "movi": 2,
        "add": 3,
        "sub": 3,
        "xor": 3,
        "cmp": 2,
        "load": 2,
        "halt": 0,
    }
    for mnemonic, operands, raw in instructions:
        if mnemonic.startswith("branch."):
            if len(operands) != 1:
                raise ValueError(f"{listing.location}: malformed A0 branch in {raw!r}")
            branches.append(operands[0])
            continue
        if mnemonic not in arity:
            raise ValueError(f"{listing.location}: unknown A0 mnemonic {mnemonic!r}")
        if len(operands) != arity[mnemonic]:
            raise ValueError(
                f"{listing.location}: {mnemonic} expects {arity[mnemonic]} operands in {raw!r}"
            )
        if mnemonic == "halt":
            continue
        if mnemonic == "movi":
            require_register(operands[0], listing.location)
            try:
                immediate = int(operands[1], 0)
            except ValueError as error:
                raise ValueError(f"{listing.location}: invalid A0 immediate {operands[1]!r}") from error
            if not -128 <= immediate <= 127:
                raise ValueError(f"{listing.location}: A0 immediate {immediate} does not fit signed byte")
            continue
        if mnemonic == "load":
            require_register(operands[0], listing.location)
            memory = re.fullmatch(r"\[(r[0-7])\s*([+-])\s*(\d+)\]", operands[1])
            if not memory:
                raise ValueError(f"{listing.location}: malformed A0 load operand {operands[1]!r}")
            continue
        for operand in operands:
            require_register(operand, listing.location)

    missing = sorted(set(branches) - labels)
    if missing:
        raise ValueError(f"{listing.location}: undefined A0 branch label(s): {', '.join(missing)}")


def strip_assembly_annotations(body: str, *, x86: bool) -> str:
    output: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if x86:
            line = line.split(";", 1)[0].rstrip()
        address_match = ADDRESS.match(line)
        if address_match and address_match["address"].isdigit():
            line = address_match["body"].strip()
        output.append(line)
    return "\n".join(output) + "\n"


def explicit_addresses(body: str) -> list[int]:
    addresses: list[int] = []
    for raw in body.splitlines():
        match = ADDRESS.match(raw.strip())
        if match and match["address"].isdigit() and match["body"].strip():
            addresses.append(int(match["address"], 16))
    return addresses


def assemble(listing: CodeListing, architecture: str) -> None:
    llvm_mc = shutil.which("llvm-mc")
    if llvm_mc is None:
        raise ValueError(f"{listing.location}: llvm-mc is required to validate {architecture} listings")
    x86 = architecture == "x86"
    source = strip_assembly_annotations(listing.body, x86=x86)
    if x86:
        source = ".intel_syntax noprefix\n" + source
        triple = "x86_64"
    else:
        source = ".option norvc\n" + source
        triple = "riscv64"
    result = subprocess.run(
        [llvm_mc, f"-triple={triple}", "-show-encoding"],
        input=source,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip().replace("\n", " | ")
        raise ValueError(f"{listing.location}: {architecture} assembly failed: {detail}")
    declared = explicit_addresses(listing.body)
    if declared:
        encodings = re.findall(r"encoding:\s*\[([^]]+)\]", result.stdout)
        lengths = [len(encoding.split(",")) for encoding in encodings]
        if len(lengths) != len(declared):
            raise ValueError(
                f"{listing.location}: found {len(declared)} printed addresses but "
                f"assembler emitted {len(lengths)} instructions"
            )
        calculated = [declared[0]]
        for length in lengths[:-1]:
            calculated.append(calculated[-1] + length)
        if declared != calculated:
            raise ValueError(
                f"{listing.location}: printed {architecture} addresses {declared} "
                f"disagree with assembled addresses {calculated}"
            )


def check_python(listing: CodeListing) -> None:
    compile(listing.body, listing.location, "exec")
    # Python permits calls and expressions to wrap across physical lines.  The
    # manuscript should be free to fit code to the printed measure without
    # weakening the required-operation check.
    compact_body = re.sub(r"\s+", "", listing.body)
    if listing.caption == "Encode, decode, and execute one A0 addition":
        required = [
            "from axeyum import machine",
            "machine.a0.Instruction.add(3, 5, 2)",
            'bytes.fromhex("10 2b 02 00")',
            "machine.a0.Instruction.decode(add.encode())",
            "machine.a0.step(program, before)",
            "after.register(3).unsigned == 0x80",
            "after.pc.unsigned == 4",
            "machine.a0.Conditions(False, True, False, True)",
        ]
        missing = [
            fragment
            for fragment in required
            if re.sub(r"\s+", "", fragment) not in compact_body
        ]
        if missing:
            raise ValueError(
                f"{listing.location}: A0 Python listing omitted {', '.join(missing)}"
            )
        if not (ROOT / "scripts/tests/test_axeyum_machine_examples.py").is_file():
            raise ValueError(f"{listing.location}: A0 Python runtime harness is missing")
        return
    if listing.caption == "Inspect and replay one evidence manifest":
        required = [
            "from scripts.evidence_manifest import EvidenceManifest",
            "manifest.verify_digests()",
            "manifest.reproduce()",
            "manifest.check()",
            "manifest.run_negative_control()",
            "manifest.trust_boundary()",
        ]
        missing = [fragment for fragment in required if fragment not in listing.body]
        if missing:
            raise ValueError(
                f"{listing.location}: manifest listing omitted {', '.join(missing)}"
            )
        if not (ROOT / "scripts/tests/test_evidence_manifest.py").is_file():
            raise ValueError(f"{listing.location}: manifest runtime harness is missing")
        return
    if FUTURE_API.search(listing.body):
        raise ValueError(f"{listing.location}: illustrative or nonexistent API in Python listing")
    raise ValueError(
        f"{listing.location}: Python listing has no declared runtime harness; add one to this gate before publishing it"
    )


def check_shell(listing: CodeListing) -> None:
    expected = "AXEYUM=/path/to/current/axeyum-main make check-run"
    if listing.body.strip() != expected:
        raise ValueError(f"{listing.location}: unrecognized shell listing; bind it explicitly in the code gate")
    if not (ROOT / "scripts" / "check_artifacts.py").is_file():
        raise ValueError(f"{listing.location}: listed artifact checker does not exist")


def check_pseudocode(listing: CodeListing) -> None:
    required = ["p := a", "c := n", "x := 0", "while c != 0:", "return x"]
    missing = [line for line in required if line not in listing.body]
    if missing:
        raise ValueError(f"{listing.location}: logical pseudocode lacks {missing}")


def main() -> int:
    failures: list[str] = []
    counts: dict[str, int] = {}
    found = listings()
    for listing in found:
        try:
            architecture = classify(listing)
            if (
                FUTURE_API.search(listing.body)
                and not (
                    architecture == "python"
                    and listing.caption == "Inspect and replay one evidence manifest"
                )
            ):
                raise ValueError(f"{listing.location}: future or illustrative API appears in code")
            counts[architecture] = counts.get(architecture, 0) + 1
            if architecture == "a0":
                check_a0(listing)
            elif architecture in {"rv64", "x86"}:
                assemble(listing, architecture)
            elif architecture == "python":
                check_python(listing)
            elif architecture == "shell":
                check_shell(listing)
            else:
                check_pseudocode(listing)
        except (SyntaxError, ValueError) as error:
            failures.append(str(error))
    for failure in failures:
        print(f"BAD {failure}")
    summary = " ".join(f"{name}={count}" for name, count in sorted(counts.items()))
    print(f"code-listings: {len(found)} checked ({summary}); failures={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
