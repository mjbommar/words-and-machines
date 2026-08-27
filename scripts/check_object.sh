#!/usr/bin/env bash
# Re-verify one SIMD certificate object end to end. Exit status depends on the FINDING.
#
#   scripts/check_object.sh DIR BINARY ARGS... [--vacuous-formula]
#
# DIR      artifact directory holding *.cnf.gz, *.drat.gz, SHA256SUMS.raw
# BINARY   name of an axeyum example under $AXEYUM/target/release/examples
# ARGS     arguments before `--check-drat` (e.g. "reverse 1 120")
#
# Steps, each of which can fail:
#   1. gunzip into a scratch dir and verify SHA-256 of the RAW bytes against SHA256SUMS.raw
#   2. run the axeyum checker; require exit 0 AND "verdict=unsat-checked" on stdout
#   3. negative control: a 2-byte-truncated proof MUST be rejected (nonzero exit)
#      -- unless --vacuous-formula is given, in which case the object declares that the
#      formula is refuted by unit propagation alone; then step 3 is replaced by an
#      independent unit-propagation check (scripts/up_refutes.py) that MUST report conflict,
#      and the DRAT is documented as not load-bearing.
set -u
DIR=$1; BIN=$2; shift 2
VACUOUS=0; ARGS=()
for a in "$@"; do [ "$a" = "--vacuous-formula" ] && VACUOUS=1 || ARGS+=("$a"); done
AXEYUM=${AXEYUM:-$HOME/projects/personal/axeyum}
B=$AXEYUM/target/release/examples/$BIN
[ -x "$B" ] || { echo "SKIP: no prebuilt $B (set AXEYUM); artifact hashes will still be verified"; NOBIN=1; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
for gz in "$DIR"/*.gz; do gunzip -c "$gz" > "$T/$(basename "${gz%.gz}")"; done
( cd "$T" && sha256sum -c "$OLDPWD/$DIR/SHA256SUMS.raw" --quiet ) || { echo "FAIL: artifact hash mismatch"; exit 1; }
echo "ok: raw artifact hashes match SHA256SUMS.raw"
[ "${NOBIN:-0}" = 1 ] && exit 0
DRAT=$(ls "$T"/*.drat | head -1)
OUT=$(timeout 600 "$B" "${ARGS[@]}" --check-drat "$DRAT" 2>&1); RC=$?
echo "$OUT" | tail -2
[ $RC -eq 0 ] && echo "$OUT" | grep -q 'verdict=unsat-checked' || { echo "FAIL: checker did not accept the proof (rc=$RC)"; exit 1; }
if [ $VACUOUS = 1 ]; then
  python3 "$(dirname "$0")/up_refutes.py" "$T"/*.cnf || { echo "FAIL: object claims UP-refutable formula but unit propagation did not conflict"; exit 1; }
  echo "ok: formula refuted by unit propagation alone; the DRAT is NOT load-bearing (declared)"
else
  head -c -2 "$DRAT" > "$T/trunc.drat"
  if timeout 600 "$B" "${ARGS[@]}" --check-drat "$T/trunc.drat" >/dev/null 2>&1; then
    echo "FAIL: negative control -- truncated proof was ACCEPTED (checker cannot fail)"; exit 1
  fi
  echo "ok: negative control -- truncated proof rejected"
fi
echo "VERIFIED"
