#!/usr/bin/env python3
"""Exit 0 iff the DIMACS CNF is refuted by unit propagation alone (no search).

Used to document certificates that are NOT load-bearing: if the formula already
conflicts under unit propagation, any DRAT file whose last step is the empty
clause will be accepted by a backward checker, so the proof carries no
information beyond the formula itself. Exit 1 if a full propagation fixpoint is
reached without conflict (the proof IS load-bearing), 2 on read error.
"""
import sys

def main(path):
    clauses = []
    with open(path) as f:
        for line in f:
            if not line or line[0] in "pc":
                continue
            lits = [int(t) for t in line.split()][:-1]
            if lits:
                clauses.append(lits)
    assign = {}
    changed = True
    while changed:
        changed = False
        for c in clauses:
            if any(assign.get(abs(l)) == (l > 0) for l in c):
                continue
            free = [l for l in c if abs(l) not in assign]
            if not free:
                print(f"UP-CONFLICT clauses={len(clauses)} assigned={len(assign)}")
                return 0
            if len(free) == 1:
                assign[abs(free[0])] = free[0] > 0
                changed = True
    print(f"UP-FIXPOINT-NO-CONFLICT clauses={len(clauses)} assigned={len(assign)}")
    return 1

if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1]))
    except (IndexError, OSError) as e:
        print(f"error: {e}"); sys.exit(2)
