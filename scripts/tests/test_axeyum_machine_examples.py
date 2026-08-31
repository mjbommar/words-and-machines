"""Execute the exact Axeyum Python listings printed in the manuscript."""

from __future__ import annotations

import unittest
import shutil
import subprocess
import tempfile
from pathlib import Path

from axeyum import machine

from scripts.check_code_listings import CodeListing, classify, listings, strip_assembly_annotations


A0_ADDITION = "Encode, decode, and execute one A0 addition"
RV64 = "rv64"
X64 = "x86"


def manuscript_listing(caption: str) -> CodeListing:
    matches = [listing for listing in listings() if listing.caption == caption]
    if len(matches) != 1:
        raise AssertionError(f"expected exactly one listing captioned {caption!r}")
    return matches[0]


def linked_bytes(listing: CodeListing) -> bytes:
    """Assemble one exact listing, resolving its declared external helper."""
    architecture = classify(listing)
    source = strip_assembly_annotations(listing.body, x86=architecture == X64)
    if architecture == RV64:
        source = ".option norvc\n.text\n" + source
        triple = "riscv64"
        if "helper" in source:
            source += "helper:\n    jalr x0, 0(ra)\n"
    elif architecture == X64:
        source = ".intel_syntax noprefix\n.text\n" + source
        triple = "x86_64"
        if "helper" in source:
            source += "helper:\n    ret\n"
    else:
        raise AssertionError(f"not a real-ISA listing: {listing.location}")

    llvm_mc = shutil.which("llvm-mc")
    llvm_objcopy = shutil.which("llvm-objcopy")
    if llvm_mc is None or llvm_objcopy is None:
        raise AssertionError("llvm-mc and llvm-objcopy are required")
    with tempfile.TemporaryDirectory(prefix="book-machine-listing-") as directory:
        root = Path(directory)
        object_path = root / "listing.o"
        binary_path = root / "listing.bin"
        assembled = subprocess.run(
            [llvm_mc, f"-triple={triple}", "-filetype=obj", "-o", str(object_path)],
            input=source,
            text=True,
            capture_output=True,
            check=False,
        )
        if assembled.returncode != 0:
            raise AssertionError(f"{listing.location}: {assembled.stderr.strip()}")
        extracted = subprocess.run(
            [llvm_objcopy, "-O", "binary", "--only-section=.text", str(object_path), str(binary_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        if extracted.returncode != 0:
            raise AssertionError(f"{listing.location}: {extracted.stderr.strip()}")
        return binary_path.read_bytes()


def rv64_step_until(program: object, state: object, target: int, limit: int = 128):
    for _ in range(limit):
        if state.pc == target or state.outcome.kind != "running":
            break
        state = machine.rv64.step(program, state)
    if state.outcome.kind != "running" or state.pc != target:
        raise AssertionError(f"RV64 did not reach {target}: pc={state.pc}, {state.outcome.kind}")
    return state


def x64_step_until(program: object, state: object, target: int, limit: int = 128):
    for _ in range(limit):
        if state.rip == target or state.outcome.kind != "running":
            break
        state = machine.x64.step(program, state)
    if state.outcome.kind != "running" or state.rip != target:
        raise AssertionError(f"x86-64 did not reach {target}: rip={state.rip}, {state.outcome.kind}")
    return state


def memory_with_word(size: int, address: int, value: int):
    data = bytearray(size)
    data[address : address + 8] = value.to_bytes(8, "little")
    return machine.a0.Memory.from_bytes(data)


class AxeyumMachineExampleTests(unittest.TestCase):
    def _a0_addition(self) -> CodeListing:
        return manuscript_listing(A0_ADDITION)

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

    def test_every_real_isa_listing_decodes_wholly_in_the_selected_slice(self) -> None:
        counts = {RV64: 0, X64: 0}
        for listing in listings():
            architecture = classify(listing)
            if architecture not in counts:
                continue
            code = linked_bytes(listing)
            if architecture == RV64:
                self.assertEqual(len(code) % 4, 0, listing.location)
                for offset in range(0, len(code), 4):
                    word = int.from_bytes(code[offset : offset + 4], "little")
                    machine.rv64.Instruction.decode(word)
            else:
                offset = 0
                while offset < len(code):
                    _, length = machine.x64.Instruction.decode(code[offset:])
                    self.assertGreater(length, 0, listing.location)
                    offset += length
                self.assertEqual(offset, len(code), listing.location)
            counts[architecture] += 1
        self.assertEqual(counts, {RV64: 7, X64: 6})

    def test_rv64_branch_count_leaf_absolute_copy_and_xor_listings_execute(self) -> None:
        branch_code = linked_bytes(manuscript_listing("A branch sixteen bytes forward"))
        branch = machine.rv64.Program(0, branch_code)
        equal = machine.rv64.State(machine.a0.Memory.zeroed(0), 0)
        equal = equal.with_register(5, 7).with_register(2, 7)
        unequal = equal.with_register(2, 8)
        self.assertEqual(machine.rv64.step(branch, equal).pc, 16)
        self.assertEqual(machine.rv64.step(branch, unequal).pc, 4)

        count_code = linked_bytes(manuscript_listing("RV64I counts a0 down to zero"))
        count = machine.rv64.State(machine.a0.Memory.zeroed(0), 0).with_register(10, 3)
        count = rv64_step_until(machine.rv64.Program(0, count_code), count, len(count_code))
        self.assertEqual(count.register(10), 0)

        leaf_code = linked_bytes(
            manuscript_listing("An RV64I leaf under the selected integer ABI")
        )
        leaf = machine.rv64.State(machine.a0.Memory.zeroed(0), 0)
        leaf = leaf.with_register(10, 41).with_register(1, 64)
        leaf = rv64_step_until(machine.rv64.Program(0, leaf_code), leaf, 64)
        self.assertEqual(leaf.register(10), 42)

        frame_code = linked_bytes(manuscript_listing("A selected RV64I non-leaf frame"))
        frame = machine.rv64.State(machine.a0.Memory.zeroed(256), 0)
        frame = frame.with_register(2, 128).with_register(1, 64)
        frame = frame.with_register(8, 9).with_register(10, 5)
        frame = rv64_step_until(machine.rv64.Program(0, frame_code), frame, 64)
        self.assertEqual(frame.register(10), 10)
        self.assertEqual(frame.register(8), 9)
        self.assertEqual(frame.register(2), 128)

        absolute_code = linked_bytes(manuscript_listing("RV64I absolute value"))
        for value, expected in [(7, 7), (2**64 - 7, 7)]:
            state = machine.rv64.State(machine.a0.Memory.zeroed(0), 0)
            state = state.with_register(10, value)
            state = rv64_step_until(
                machine.rv64.Program(0, absolute_code), state, len(absolute_code)
            )
            self.assertEqual(state.register(10), expected)

        copy_code = linked_bytes(manuscript_listing("Two RV64I ways to copy a0 to itself"))
        for entry in (0, 4):
            state = machine.rv64.State(machine.a0.Memory.zeroed(0), entry)
            state = state.with_register(10, 0x1234)
            after = machine.rv64.step(machine.rv64.Program(0, copy_code), state)
            self.assertEqual(after.register(10), 0x1234)

        xor_code = linked_bytes(manuscript_listing("RV64I XOR reduction"))
        data_base = 128
        continuation = 64
        data = bytearray(160)
        for index, value in enumerate((1, 2, 4)):
            start = data_base + index * 8
            data[start : start + 8] = value.to_bytes(8, "little")
        xor_state = machine.rv64.State(machine.a0.Memory.from_bytes(data), 0)
        xor_state = xor_state.with_register(10, data_base)
        xor_state = xor_state.with_register(11, 3).with_register(1, continuation)
        xor_state = rv64_step_until(machine.rv64.Program(0, xor_code), xor_state, continuation)
        self.assertEqual(xor_state.register(10), 7)

    def test_x64_count_leaf_absolute_zero_and_xor_listings_execute(self) -> None:
        count_code = linked_bytes(manuscript_listing("x86-64 counts RDI down to zero"))
        count = machine.x64.State(machine.a0.Memory.zeroed(0), 0).with_register(7, 3)
        count = x64_step_until(machine.x64.Program(0, count_code), count, len(count_code))
        self.assertEqual(count.register(7), 0)

        leaf_code = linked_bytes(manuscript_listing("An x86-64 System V leaf function"))
        leaf = machine.x64.State(memory_with_word(136, 128, 64), 0)
        leaf = leaf.with_register(7, 41).with_register(4, 128)
        leaf = x64_step_until(machine.x64.Program(0, leaf_code), leaf, 64)
        self.assertEqual(leaf.register(0), 42)

        frame_code = linked_bytes(
            manuscript_listing("A selected System V AMD64 non-leaf frame")
        )
        frame = machine.x64.State(memory_with_word(136, 128, 64), 0)
        frame = frame.with_register(0, 2).with_register(3, 9)
        frame = frame.with_register(4, 128).with_register(7, 5)
        frame = x64_step_until(machine.x64.Program(0, frame_code), frame, 64)
        self.assertEqual(frame.register(0), 7)
        self.assertEqual(frame.register(3), 9)
        self.assertEqual(frame.register(4), 136)

        absolute_code = linked_bytes(
            manuscript_listing("x86-64 absolute value in the selected local contract")
        )
        for value, expected in [(7, 7), (2**64 - 7, 7)]:
            state = machine.x64.State(machine.a0.Memory.zeroed(0), 0).with_register(7, value)
            state = x64_step_until(
                machine.x64.Program(0, absolute_code), state, len(absolute_code)
            )
            self.assertEqual(state.register(0), expected)

        zero_code = linked_bytes(manuscript_listing("Two x86-64 ways to write zero to RAX"))
        xor_zero = machine.x64.State(machine.a0.Memory.zeroed(0), 0)
        xor_zero = machine.x64.step(machine.x64.Program(0, zero_code), xor_zero)
        move_zero = machine.x64.State(machine.a0.Memory.zeroed(0), 2)
        move_zero = machine.x64.step(machine.x64.Program(0, zero_code), move_zero)
        self.assertEqual(xor_zero.register(0), move_zero.register(0))
        self.assertNotEqual(xor_zero.flags, move_zero.flags)

        xor_code = linked_bytes(manuscript_listing("x86-64 XOR reduction"))
        data_base = 128
        stack = 192
        continuation = 64
        data = bytearray(208)
        for index, value in enumerate((1, 2, 4)):
            start = data_base + index * 8
            data[start : start + 8] = value.to_bytes(8, "little")
        data[stack : stack + 8] = continuation.to_bytes(8, "little")
        state = machine.x64.State(machine.a0.Memory.from_bytes(data), 0)
        state = state.with_register(7, data_base).with_register(6, 3).with_register(4, stack)
        state = x64_step_until(machine.x64.Program(0, xor_code), state, continuation)
        self.assertEqual(state.register(0), 7)

    def test_unsupported_but_assemblable_instruction_is_rejected(self) -> None:
        listing = CodeListing(
            path=Path("control.tex"),
            line=1,
            caption="x86 unsupported control",
            language="",
            body="nop",
        )
        code = linked_bytes(listing)
        with self.assertRaises(ValueError):
            machine.x64.Instruction.decode(code)


if __name__ == "__main__":
    unittest.main()
