#!/usr/bin/env python3
"""Exhaustive minimum straight-line-program length for all 256 three-input
Boolean functions over two RISC-V instruction subsets, compared against the
table in riscv-crypto `doc/supp/bitlogic.adoc`.

Object: M.riscv.bitlogic256 (see objects/).

Method (complete, not heuristic): breadth-first search where a *state* is the
frozenset of 8-bit truth tables currently held in registers, starting from the
three inputs {x=0xAA, y=0xCC, z=0xF0}. A level applies every binary op to every
unordered pair of held values, and unary NOT to every held value. A chain of
length L computing f is a path of length L in this graph; deduplicating on the
held-value set is sound because the held values fully determine what can be
computed next. The first level at which f appears in some state is its exact
minimum chain length. This is the same cost model the document uses: SLP length
with sharing (a Boolean chain), inferred in scripts/README.md.

Exit status depends on the FINDING: 0 only if every one of the 512 table
entries is reproduced exactly (Len column), nonzero otherwise. A run that
completes but disagrees exits 1. The constants 0x00/0xFF are scored Len=0 by
the document because RISC-V hardwires x0; we mirror that convention.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

X, Y, Z = 0xAA, 0xCC, 0xF0
MASK = 0xFF

BASE = {
    "and": lambda a, b: a & b,
    "or":  lambda a, b: a | b,
    "xor": lambda a, b: a ^ b,
}
EXT = dict(BASE, **{
    "andn": lambda a, b: a & ~b & MASK,   # a & ~b
    "orn":  lambda a, b: (a | ~b) & MASK, # a | ~b
    "xnor": lambda a, b: (a ^ ~b) & MASK, # a ^ ~b
})

def bfs(binops, max_len=8):
    start = frozenset({X, Y, Z})
    first = {X: 0, Y: 0, Z: 0, 0x00: 0, 0xFF: 0}   # x0 convention
    frontier = {start}
    for L in range(1, max_len + 1):
        nxt = set()
        for st in frontier:
            vals = sorted(st)
            cands = set()
            for i, a in enumerate(vals):
                cands.add(~a & MASK)
                for b in vals[i:]:
                    for op in binops.values():
                        cands.add(op(a, b) & MASK)
                        cands.add(op(b, a) & MASK)
            for c in cands:
                if c in st:
                    continue
                if c not in first:
                    first[c] = L
                nxt.add(st | {c})
        frontier = nxt
        if len(first) == 256:
            break
    assert len(first) == 256, f"incomplete after {max_len} levels: {len(first)}"
    return first

ROW = re.compile(r"^\|\s*(0x[0-9A-Fa-f]{2})\s*\|\s*([01]{8})\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*`\+(.*?)\+`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*`\+(.*?)\+`\s*$")

def parse_table(path: Path):
    rows = {}
    for line in path.read_text().splitlines():
        m = ROW.match(line)
        if m:
            tt = int(m.group(1), 16)
            assert int(m.group(2), 2) == tt, f"TT column disagrees with Numb at {m.group(1)}"
            unesc = lambda e: e.replace("\\|", "|")
            rows[tt] = {"ext_len": int(m.group(3)), "ext_dep": int(m.group(4)), "ext_expr": unesc(m.group(5)),
                        "base_len": int(m.group(6)), "base_dep": int(m.group(7)), "base_expr": unesc(m.group(8))}
    return rows

def c_eval(expr: str) -> int:
    e = expr.replace("&~", "& ~").replace("|~", "| ~").replace("^~", "^ ~")
    return eval(e, {"__builtins__": {}}, {"x": X, "y": Y, "z": Z}) & MASK

def main():
    here = Path(__file__).resolve().parent.parent
    adoc = here / "artifacts" / "riscv" / "bitlogic.adoc"
    out = here / "artifacts" / "riscv" / "bitlogic256-reproduction.json"
    rows = parse_table(adoc)
    if len(rows) != 256:
        print(f"FAIL: parsed {len(rows)} rows, expected 256"); return 2
    # semantic check of every expression
    sem_bad = [f"{tt:#04x}" for tt, r in rows.items()
               if c_eval(r["base_expr"]) != tt or c_eval(r["ext_expr"]) != tt]
    base = bfs(BASE); ext = bfs(EXT)
    # NOTE: the document's Len for base ISA counts fused ops only in the ext column;
    # but the base column's expressions may use NOT (1 instr) — our BASE set includes unary NOT.
    mism = []
    for tt, r in rows.items():
        if base[tt] != r["base_len"]: mism.append(("base", f"{tt:#04x}", r["base_len"], base[tt]))
        if ext[tt]  != r["ext_len"]:  mism.append(("ext",  f"{tt:#04x}", r["ext_len"],  ext[tt]))
    hist = lambda d: {k: sum(1 for v in d.values() if v == k) for k in sorted(set(d.values()))}
    report = {
        "object": "M.riscv.bitlogic256",
        "rows_parsed": len(rows),
        "semantic_errors": sem_bad,
        "base_len_histogram": hist(base), "ext_len_histogram": hist(ext),
        "base_max": max(base.values()), "ext_max": max(ext.values()),
        "mismatches_vs_document": mism,
        "ch_0xD8": {"base": base[0xD8], "ext": ext[0xD8]},
        "maj_0xE8": {"base": base[0xE8], "ext": ext[0xE8]},
        "verdict": "REPRODUCED" if not mism and not sem_bad else "DISAGREES",
    }
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("rows_parsed","semantic_errors","base_max","ext_max","ch_0xD8","maj_0xE8","verdict")}, indent=1))
    print(f"mismatches: {len(mism)}")
    for m in mism[:20]: print("  ", m)
    return 0 if report["verdict"] == "REPRODUCED" else 1

if __name__ == "__main__":
    sys.exit(main())
