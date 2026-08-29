#!/usr/bin/env python3
"""RISC-V Bitmanip (draft v0.93) permutation-instruction reachability.

Objects: M.riscv.byteperm24 and M.riscv.table22 (see objects/).

Implements `ror`, `grev`, `shfl`, `unshfl` on 32-bit words from the draft
spec's own pseudocode, converts each of the 92 concrete instructions
(ror k=1..31, grev k=1..31, shfl k=1..15, unshfl k=1..15) to a permutation of
the 32 bit positions, and runs breadth-first search over composed
permutations from the identity.

Two claims are checked, and the exit status depends on BOTH:
  1. Every one of the 24 byte permutations of a 32-bit word is reachable with
     at most 3 instructions from {ror, grev, shfl, unshfl}  (spec Table 4.1),
     and the per-permutation minima are reported (the spec does not give them).
  2. The cumulative reachable-permutation counts match the draft spec's
     Table 2.2 whose source artifact (svn.clairexen.net/.../permexplore) is
     now a 404:  ROT+GREV  : 1 62 864 4640 23312 92192 294992 703744 1012856 1046224 1048576
                 ROT+GREV+SHFL (to depth 4): 1 85 3030 78659 2002167
Exit 0 only if both reproduce exactly.
"""
from __future__ import annotations
import json, sys
from itertools import permutations
from pathlib import Path

W = 32; M = (1 << W) - 1

def ror(x, k): k %= W; return ((x >> k) | (x << (W - k))) & M
def grev(x, k):
    for sh, m in ((1, 0x55555555), (2, 0x33333333), (4, 0x0F0F0F0F), (8, 0x00FF00FF), (16, 0x0000FFFF)):
        if k & sh: x = ((x & m) << sh) | ((x >> sh) & m)
    return x & M
def _shfl_stage(x, mask_l, mask_r, n):
    y = x & ~(mask_l | mask_r) & M
    return (y | ((x & mask_l) << n) | ((x & mask_r) >> n)) & M
STAGES = ((8, 0x00FF0000, 0x0000FF00), (4, 0x0F000F00, 0x00F000F0), (2, 0x30303030, 0x0C0C0C0C), (1, 0x44444444, 0x22222222))
def shfl(x, k):
    for n, l, r in STAGES:
        if k & n: x = _shfl_stage(x, r, l, n)
    return x
def unshfl(x, k):
    for n, l, r in reversed(STAGES):
        if k & n: x = _shfl_stage(x, r, l, n)
    return x

def as_perm(f):  # bit i of input -> position perm[i] of output
    p = [0] * W
    for i in range(W):
        y = f(1 << i)
        assert y and (y & (y - 1)) == 0, "not a bit permutation"
        p[i] = y.bit_length() - 1
    return tuple(p)

def compose(p, q):  # apply p then q
    return tuple(q[p[i]] for i in range(W))

def gens(with_shfl):
    g = {}
    for k in range(1, 32):
        g[f"ROR({k})"] = as_perm(lambda x, k=k: ror(x, k))
        g[f"GREV({k})"] = as_perm(lambda x, k=k: grev(x, k))
    if with_shfl:
        for k in range(1, 16):
            g[f"SHFL({k})"] = as_perm(lambda x, k=k: shfl(x, k))
            g[f"UNSHFL({k})"] = as_perm(lambda x, k=k: unshfl(x, k))
    return g

def bfs(g, depth, want=None):
    ident = tuple(range(W))
    seen = {ident: []}; frontier = [ident]; counts = [1]
    for d in range(1, depth + 1):
        nxt = []
        for p in frontier:
            for name, q in g.items():
                r = compose(p, q)
                if r not in seen:
                    seen[r] = seen[p] + [name]; nxt.append(r)
        frontier = nxt; counts.append(len(seen))
        if want is not None and all(w in seen for w in want): break
    return seen, counts

def byte_perms():
    out = {}
    for s in permutations(range(4)):
        p = [0] * W
        for a in range(4):
            for r in range(8): p[8 * a + r] = 8 * s[a] + r
        out["".join("ABCD"[i] for i in s)] = tuple(p)
    return out

def main():
    here = Path(__file__).resolve().parent.parent
    out = here / "artifacts" / "riscv" / "bitmanip-permutations-reproduction.json"
    # claim 1
    g4 = gens(True); bp = byte_perms()
    seen, _ = bfs(g4, 4, want=set(bp.values()))
    minima = {name: (len(seen[p]), seen[p]) for name, p in bp.items()}
    maxlen = max(l for l, _ in minima.values())
    hist = {k: sum(1 for l, _ in minima.values() if l == k) for k in range(0, 5)}
    # claim 2
    _, c_rg = bfs(gens(False), 10)
    _, c_rgs = bfs(g4, 4)
    spec_rg = [1, 62, 864, 4640, 23312, 92192, 294992, 703744, 1012856, 1046224, 1048576]
    spec_rgs = [1, 85, 3030, 78659, 2002167]
    ok = maxlen <= 3 and c_rg == spec_rg and c_rgs == spec_rgs
    rep = {"objects": ["M.riscv.byteperm24", "M.riscv.table22"],
           "byte_perm_max_len": maxlen, "byte_perm_len_histogram": hist,
           "byte_perm_minima": {k: {"len": l, "seq": s} for k, (l, s) in sorted(minima.items())},
           "table22_rot_grev": c_rg, "table22_rot_grev_spec": spec_rg,
           "table22_rot_grev_shfl_to4": c_rgs, "table22_rot_grev_shfl_spec_to4": spec_rgs,
           "verdict": "REPRODUCED" if ok else "DISAGREES"}
    out.write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({k: rep[k] for k in ("byte_perm_max_len","byte_perm_len_histogram","table22_rot_grev","table22_rot_grev_shfl_to4","verdict")}))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
