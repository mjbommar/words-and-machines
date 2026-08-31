#!/usr/bin/env python3
"""Mutation controls for the manuscript code-listing gate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_code_listings.py")
SPEC = importlib.util.spec_from_file_location("check_code_listings", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def listing(caption: str, body: str, language: str = ""):
    return MODULE.CodeListing(
        path=MODULE.ROOT / "book" / "latex" / "chapters" / "control.tex",
        line=1,
        caption=caption,
        language=language,
        body=body,
    )


class ListingControls(unittest.TestCase):
    def test_current_manuscript_is_accepted(self) -> None:
        self.assertEqual(MODULE.main(), 0)

    def test_undefined_a0_branch_label_is_rejected(self) -> None:
        broken = listing("A0 control", "00: branch.ne missing\n04: halt")
        with self.assertRaisesRegex(ValueError, "undefined A0 branch label"):
            MODULE.check_a0(broken)

    def test_invalid_a0_register_is_rejected(self) -> None:
        broken = listing("A0 control", "add r8, r0, r1")
        with self.assertRaisesRegex(ValueError, "invalid A0 register"):
            MODULE.check_a0(broken)

    def test_nonexistent_python_api_is_rejected(self) -> None:
        broken = listing(
            "Future API",
            'record = EvidenceManifest.load("claim.json")',
            "python",
        )
        with self.assertRaisesRegex(ValueError, "nonexistent API"):
            MODULE.check_python(broken)

    def test_incomplete_a0_python_example_is_rejected(self) -> None:
        broken = listing(
            "Encode, decode, and execute one A0 addition",
            "from axeyum import machine\nadd = machine.a0.Instruction.add(3, 5, 2)",
            "python",
        )
        with self.assertRaisesRegex(ValueError, "A0 Python listing omitted"):
            MODULE.check_python(broken)

    def test_a0_python_required_call_may_wrap_for_print(self) -> None:
        body = """from axeyum import machine
add = machine.a0.Instruction.add(3, 5, 2)
assert add.encode() == bytes.fromhex("10 2b 02 00")
assert machine.a0.Instruction.decode(add.encode()) == add
program = object()
before = object()
after = machine.a0.step(program, before)
assert after.register(3).unsigned == 0x80
assert after.pc.unsigned == 4
assert after.conditions == machine.a0.Conditions(
    False, True, False, True
)
"""
        MODULE.check_python(
            listing("Encode, decode, and execute one A0 addition", body, "python")
        )

    def test_invalid_rv64_instruction_is_rejected(self) -> None:
        broken = listing("RV64 control", "not_an_instruction a0, a1")
        with self.assertRaisesRegex(ValueError, "assembly failed"):
            MODULE.assemble(broken, "rv64")

    def test_wrong_x86_printed_address_is_rejected(self) -> None:
        broken = listing(
            "x86 control",
            "00: mov rax, rdi\n04: test rax, rax",
        )
        with self.assertRaisesRegex(ValueError, "disagree with assembled addresses"):
            MODULE.assemble(broken, "x86")


if __name__ == "__main__":
    unittest.main()
