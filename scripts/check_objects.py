#!/usr/bin/env python3
"""Validate every object record and (optionally) re-run its checkers.

    scripts/check_objects.py            # schema + semantic rules only
    scripts/check_objects.py --run      # also execute checker_command and negative_control
    scripts/check_objects.py --run --only M.avx2

Semantic rules (enforced, not just structure -- mirrors axeyum's validate-facts.py):
  * a `proved`/`computed` object must carry at least one evidence row with check_status=checked
  * an `open`/`conjectured` object must carry NO checked evidence of the claim itself
  * every `theorem`/`computation` needs `scope` (a minimality claim without its subset is meaningless)
  * every evidence row with an artifact must point at a path that exists
  * with --run: checker_command must exit 0; negative_control (if present) must exit NONZERO
Exit status: 0 only if everything passes.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OBJ = ROOT / "objects"

def load_schema():
    return json.loads((OBJ / "schema" / "object.schema.json").read_text())

def validate_schema(rec, schema):
    """Minimal structural validation without jsonschema dependency."""
    errs = []
    for k in schema["required"]:
        if k not in rec: errs.append(f"missing required '{k}'")
    props = schema["properties"]
    for k in rec:
        if k not in props: errs.append(f"unknown field '{k}'")
    for k, spec in props.items():
        if k in rec and "enum" in spec and rec[k] not in spec["enum"]:
            errs.append(f"'{k}'={rec[k]!r} not in {spec['enum']}")
    import re
    if "id" in rec and not re.match(props["id"]["pattern"], rec["id"]):
        errs.append(f"bad id {rec['id']!r}")
    for ev in rec.get("evidence", []):
        for k in ("kind", "check_status"):
            if k not in ev: errs.append(f"evidence missing '{k}'")
        evp = props["evidence"]["items"]["properties"]
        for k in ev:
            if k not in evp: errs.append(f"evidence unknown field '{k}'")
        if ev.get("kind") not in evp["kind"]["enum"]: errs.append(f"evidence kind {ev.get('kind')!r} invalid")
        if ev.get("check_status") not in evp["check_status"]["enum"]: errs.append(f"check_status {ev.get('check_status')!r} invalid")
    return errs

def semantic(rec):
    errs = []
    st = rec["epistemic_status"]; ev = rec.get("evidence", [])
    checked = [e for e in ev if e["check_status"] == "checked"]
    if st in ("proved", "computed") and not checked:
        errs.append(f"{st} object with no checked evidence")
    if st in ("open", "conjectured") and any(e["kind"] not in ("claim-ref", "none") for e in checked):
        errs.append(f"{st} object carries checked evidence of the claim")
    if rec["kind"] in ("theorem", "computation") and not rec.get("scope"):
        errs.append("theorem/computation without 'scope'")
    for e in ev:
        a = e.get("artifact")
        if a and not (ROOT / a).exists(): errs.append(f"artifact missing: {a}")
        if e["check_status"] == "checked" and not e.get("checker_command") and e["kind"] not in ("claim-ref",):
            errs.append("checked evidence without checker_command")
    return errs

def run(cmd):
    p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=1800)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-3:]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", action="store_true"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    schema = load_schema(); bad = 0; n = 0
    for p in sorted(OBJ.glob("*.json")):
        rec = json.loads(p.read_text()); n += 1
        if a.only and not rec["id"].startswith(a.only): continue
        errs = validate_schema(rec, schema) + semantic(rec)
        if a.run:
            for e in rec.get("evidence", []):
                if e.get("checker_command"):
                    rc, tail = run(e["checker_command"])
                    if rc != 0: errs.append(f"checker_command exited {rc}: {tail}")
                if e.get("negative_control"):
                    rc, tail = run(e["negative_control"])
                    if rc == 0: errs.append(f"negative_control exited 0 (checker cannot fail): {tail}")
        flag = "ok " if not errs else "BAD"
        print(f"{flag} {rec['id']:36} {rec['epistemic_status']:10} {rec['kind']}")
        for e in errs: print(f"      - {e}");
        bad += bool(errs)
    print(f"\n{n} objects, {bad} with problems" + (" (checkers executed)" if a.run else " (structure only; add --run)"))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
