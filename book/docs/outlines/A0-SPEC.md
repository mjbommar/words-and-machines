# A0 specification contract

This is the canonical abstract target for the outline, chapters, active
objects, and future Axeyum package.

## Parameters and state

- Word width \(w\) is a positive multiple of 8.
- Width-four examples in the book explain word laws but are not full A0 states.
- Arithmetic is modulo \(2^w\).
- Data memory is finite and byte-addressed.
- Program code is a separate immutable finite byte map.

The architectural state is

\[
S=(R,M,pc,Z,N,C,V,O).
\]

The register map \(R\) contains ordinary registers r0 through r7. Memory
\(M\) holds data bytes. The outcome \(O\) is running, halted, or trapped with a
reason. A0 has no hardwired zero register and no implicit stack pointer.

## Program encoding

Every instruction occupies four bytes and begins at an address divisible by
four. The next sequential program counter is \(pc+4\) modulo \(2^w\), subject
to a valid code fetch.

| Byte | Contents |
|---|---|
| 0 | opcode |
| 1 | low three bits rd; next three bits rs1; high bits reserved zero |
| 2 | low three bits rs2; next three bits branch condition; high bits reserved zero |
| 3 | signed eight-bit immediate or zero when unused |

Reserved bits or nonzero unused fields make the encoding illegal. This
encoding favors inspection over density and resembles neither companion ISA.

## Operand rules

- A register operand reads or writes one named register.
- An immediate is the sign extension of byte 3 to width \(w\).
- A memory address is \(R[rs1]+\operatorname{sext}(\text{byte 3})\).
- A relative target is \(pc+4+4\operatorname{sext}(\text{byte 3})\).
- Shift counts use the unsigned value of rs2 modulo \(w\).

Wrapped addresses must still pass the finite range check.

## Opcodes and effects

| Opcode | Instruction | Reads | Writes | Conditions |
|---|---|---|---|---|
| 0x00 | mov rd, rs1 | rs1 | rd, pc | preserve |
| 0x01 | movi rd, imm | immediate | rd, pc | preserve |
| 0x02 | load rd, [rs1+imm] | rs1, memory | rd, pc, outcome | preserve |
| 0x03 | store rs2, [rs1+imm] | rs1, rs2 | memory, pc, outcome | preserve |
| 0x10 | add rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | addition |
| 0x11 | sub rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | subtraction |
| 0x12 | and rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | logic |
| 0x13 | or rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | logic |
| 0x14 | xor rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | logic |
| 0x15 | not rd, rs1 | rs1 | rd, ZNCV, pc | logic |
| 0x18 | shl rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | shift |
| 0x19 | shr rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | shift |
| 0x1a | sar rd, rs1, rs2 | rs1, rs2 | rd, ZNCV, pc | shift |
| 0x20 | cmp rs1, rs2 | rs1, rs2 | ZNCV, pc | subtraction |
| 0x30 | branch.cond rel | selected conditions | pc | preserve |
| 0x31 | jump rel | immediate | pc | preserve |
| 0xff | halt | outcome | outcome | preserve |

All omitted opcodes are illegal.

## Condition rules

For result \(r\), \(Z\) holds exactly when \(r=0\), and \(N\) is its high bit.

For \(r=x+y\bmod 2^w\), \(C\) records whether the unsigned mathematical sum is
at least \(2^w\). The overflow bit \(V\) holds when the inputs have the same
high bit and the result has the other high bit.

For \(r=x-y\bmod 2^w\), \(C\) records no unsigned borrow, so \(x\geq y\).
Overflow holds when the input high bits differ and the result high bit differs
from that of \(x\).

Logic sets \(Z,N\) and clears \(C,V\). A zero-count shift preserves the source
and clears \(C\). A nonzero shift puts the last shifted-out bit in \(C\).
Shifts set \(Z,N\) and clear \(V\). Arithmetic right shift repeats the source
high bit.

## Branch conditions

| Code | Name | Predicate |
|---|---|---|
| 0 | eq | \(Z\) |
| 1 | ne | not \(Z\) |
| 2 | lt | \(N\) differs from \(V\) |
| 3 | ge | \(N\) equals \(V\) |
| 4 | lo | not \(C\) |
| 5 | hs | \(C\) |
| 6 | hi | \(C\) and not \(Z\) |
| 7 | ls | not \(C\) or \(Z\) |

A taken branch uses the relative target. An untaken branch uses \(pc+4\).

## Memory and traps

Loads and stores use little-endian order and access \(w/8\) bytes. The first
model permits unaligned data access but requires every byte to lie in range.

A running state can trap for a misaligned program counter, incomplete code
fetch, illegal encoding, non-byte-multiple load or store width, or data range
failure. A halted or trapped state has no successor.

## Exclusions and controls

A0 excludes floating point, vectors, atomics, concurrency, weak memory,
privilege, virtual memory, interrupts, caches, timing, self-modifying code, and
ABI rules.

The executable package must include controls for byte order, destination,
condition writes, sequential and branch PC rules, carry, overflow, borrow,
reserved fields, invalid data range, and execution after halt or trap.
