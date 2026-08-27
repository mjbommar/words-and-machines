#!/usr/bin/env bash
# Decide one SMT-LIB file with axeyum's front door and require an EXPECTED verdict.
#   scripts/check_smt.sh FILE.smt2 unsat|sat
# Exit 0 iff the printed verdict equals the expectation. Any other outcome
# (unknown, error, timeout, mismatch) exits 1 -- the status depends on the finding.
set -u
F=$1; EXPECT=$2
AXEYUM=${AXEYUM:-$HOME/projects/personal/axeyum}
B=$AXEYUM/target/release/examples/smtcomp_cli
[ -x "$B" ] || { echo "FAIL: no prebuilt $B (set AXEYUM)"; exit 1; }
V=$(timeout 300 "$B" "$F" --timeout-ms 120000 2>/dev/null | tail -1)
echo "$F -> $V (expected $EXPECT)"
[ "$V" = "$EXPECT" ]
