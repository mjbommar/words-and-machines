#!/usr/bin/env python3
"""Validate every object record and (optionally) re-run its checkers.

    scripts/check_objects.py            # schema + semantic rules only
    scripts/check_objects.py --run      # also execute checker_command and negative_control
    scripts/check_objects.py --run --only A0

Semantic rules (enforced, not just structure -- mirrors axeyum's validate-facts.py):
  * a `proved`/`computed` object must carry at least one evidence row with check_status=checked
  * an `open`/`conjectured` object must carry NO checked evidence of the claim itself
  * every `theorem`/`computation` needs `scope` (a minimality claim without its subset is meaningless)
  * every evidence row with an artifact must point at a path that exists
  * checked evidence must name semantic inputs, a checker, and a negative control
  * with --run: checker_command must exit 0 and negative_control must exit NONZERO
Exit status: 0 only if everything passes.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys
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
        for k in ("kind", "trust_class", "check_status"):
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
    if rec["kind"] in ("theorem", "refinement", "computation") and not rec.get("scope"):
        errs.append("claim without 'scope'")
    for e in ev:
        a = e.get("artifact")
        if a and not (ROOT / a).exists(): errs.append(f"artifact missing: {a}")
        for raw_path, expected in e.get("sha256", {}).items():
            if not re.fullmatch(r"[0-9a-f]{64}", expected):
                errs.append(f"invalid raw digest for {raw_path}")
                continue
            path = (ROOT / raw_path).resolve()
            if ROOT not in path.parents or not path.is_file():
                errs.append(f"raw artifact missing or outside repository: {raw_path}")
                continue
            observed = hashlib.sha256(path.read_bytes()).hexdigest()
            if observed != expected:
                errs.append(f"raw artifact digest mismatch: {raw_path}")
        if e["check_status"] == "checked" and e["kind"] != "claim-ref":
            if not e.get("checker_command"):
                errs.append("checked evidence without checker_command")
            if not e.get("negative_control"):
                errs.append("checked evidence without negative_control")
            if not e.get("expected_failure"):
                errs.append("checked evidence without expected_failure")
            if not e.get("semantic_inputs"):
                errs.append("checked evidence without semantic_inputs")
    return errs

def run(cmd):
    p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=1800)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-3:]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run", action="store_true"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    schema = load_schema(); bad = 0; n = 0
    paths = sorted(OBJ.glob("*.json"))
    records = [(p, json.loads(p.read_text())) for p in paths]
    ids = {rec["id"] for _, rec in records}
    chapter_dir = ROOT / "book" / "latex" / "chapters"
    for p, rec in records:
        n += 1
        if a.only and not rec["id"].startswith(a.only): continue
        errs = validate_schema(rec, schema) + semantic(rec)
        if p.stem != rec["id"]:
            errs.append(f"filename {p.name!r} does not match id {rec['id']!r}")
        for dep in rec.get("depends_on", []):
            if dep not in ids:
                errs.append(f"missing dependency {dep!r}")
        chapter = rec.get("book", {}).get("chapter")
        if chapter and not list(chapter_dir.glob(f"{chapter}.tex")):
            errs.append(f"book chapter binding does not exist: {chapter}")
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
