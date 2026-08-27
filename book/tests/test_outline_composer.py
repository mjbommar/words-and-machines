"""Regression tests for the stateful outline composer.

These fix the three properties the composer exists to provide — determinism,
idempotent deepening, and internal consistency — plus the two ontology rules
a generative tool must never break (no faults as directives, no descriptor
banks in a move list). They run against the real in-repo ontology, because
that is what the tool ships with.
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import re
import tomllib
import random
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

SPEC = importlib.util.spec_from_file_location(
    "outline_composer", ROOT / "scripts" / "outline_composer.py")
oc = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = oc
SPEC.loader.exec_module(oc)


def run(*argv: str) -> int:
    """Invoke the CLI the way a shell would; returns the exit code.

    Output is swallowed — these tests assert on exit codes and on the state
    file, and a CLI chatty by design would drown the unittest report.
    """
    old = sys.argv
    sys.argv = ["outline_composer.py", *argv]
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            return oc.main()
    finally:
        sys.argv = old


class ComposerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)

    def path(self, name: str = "composition.yaml") -> Path:
        return self.root / name

    def init(self, *extra: str, name: str = "composition.yaml",
             kind: str = "fiction", seed: str = "7",
             words: str = "80000") -> Path:
        path = self.path(name)
        code = run("init", "--kind", kind, "--words", words,
                   "--seed", seed, "--file", str(path), *extra)
        self.assertEqual(0, code, "init should succeed")
        return path

    @staticmethod
    def state(path: Path) -> dict:
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    @staticmethod
    def node_blocks(path: Path) -> dict[str, str]:
        """Every node's own YAML text, keyed by id — the idempotence probe."""
        state = yaml.safe_load(path.read_text(encoding="utf-8"))
        out = {}
        for node, _depth, _parent in oc.walk(state.get("nodes") or []):
            out[str(node.get("id"))] = yaml.safe_dump(
                node, sort_keys=False, allow_unicode=True)
        return out


class DeterminismTests(ComposerTestCase):
    def test_same_seed_produces_byte_identical_state(self) -> None:
        a = self.init(name="a.yaml")
        b = self.init(name="b.yaml")
        self.assertEqual(a.read_text(encoding="utf-8"),
                         b.read_text(encoding="utf-8"))

    def test_different_seeds_diverge(self) -> None:
        a = self.init(name="a.yaml", seed="7")
        b = self.init(name="b.yaml", seed="8")
        self.assertNotEqual(a.read_text(encoding="utf-8"),
                            b.read_text(encoding="utf-8"))

    def test_deepen_is_reproducible_from_the_same_state(self) -> None:
        a = self.init(name="a.yaml")
        b = self.init(name="b.yaml")
        run("deepen", "ch02", "--file", str(a))
        run("deepen", "ch02", "--file", str(b))
        self.assertEqual(a.read_text(encoding="utf-8"),
                         b.read_text(encoding="utf-8"))


class IdempotenceTests(ComposerTestCase):
    def test_deepening_one_node_leaves_every_other_node_untouched(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        before = self.node_blocks(path)

        run("deepen", "ch03", "--file", str(path))
        after = self.node_blocks(path)

        # ch03 gained children; nothing else may have moved a byte
        for node_id, text in before.items():
            if node_id == "ch03":
                continue
            self.assertIn(node_id, after, f"{node_id} disappeared")
            self.assertEqual(text, after[node_id],
                             f"{node_id} changed while ch03 was deepened")
        self.assertNotEqual(before["ch03"], after["ch03"])
        self.assertTrue(any(k.startswith("ch03.") for k in after))

    def test_repeat_deepen_without_reroll_is_a_no_op(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        first = path.read_text(encoding="utf-8")
        code = run("deepen", "ch01", "--file", str(path))
        self.assertEqual(0, code, "a repeat deepen is soft, not an error")
        self.assertEqual(first, path.read_text(encoding="utf-8"))

    def test_reroll_refuses_when_a_child_is_deepened(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        run("deepen", "ch01.s01", "--file", str(path))
        before = path.read_text(encoding="utf-8")

        code = run("deepen", "ch01", "--reroll", "--file", str(path))
        self.assertEqual(1, code, "--reroll must refuse to discard work")
        self.assertEqual(before, path.read_text(encoding="utf-8"))

        code = run("deepen", "ch01", "--reroll", "--force", "--file",
                   str(path))
        self.assertEqual(0, code, "--force opts in to discarding it")
        self.assertNotEqual(before, path.read_text(encoding="utf-8"))


class BudgetTests(ComposerTestCase):
    def deepen_everything(self, path: Path, rounds: int = 2) -> None:
        for _ in range(rounds):
            run("deepen", "--all-stubs", "--file", str(path))

    def test_children_budgets_sum_to_their_parent_exactly(self) -> None:
        path = self.init()
        self.deepen_everything(path)
        state = self.state(path)
        checked = 0
        for node, _depth, _parent in oc.walk(state["nodes"]):
            kids = node.get("children") or []
            if not kids:
                continue
            checked += 1
            self.assertEqual(int(node["words"]),
                             sum(int(k["words"]) for k in kids),
                             f"{node['id']} budget does not partition")
        self.assertGreater(checked, 0, "nothing was deepened")

    def test_level_one_budgets_sum_to_the_book(self) -> None:
        path = self.init()
        state = self.state(path)
        self.assertEqual(state["meta"]["words"],
                         sum(int(n["words"]) for n in state["nodes"]))

    def test_children_tile_the_parent_span_in_order(self) -> None:
        path = self.init()
        self.deepen_everything(path)
        state = self.state(path)
        for node, _depth, _parent in oc.walk(state["nodes"]):
            kids = node.get("children") or []
            if not kids:
                continue
            start, end = oc.node_span(node)
            cursor = start
            for kid in kids:
                ks, ke = oc.node_span(kid)
                self.assertAlmostEqual(cursor, ks, places=5,
                                       msg=f"{kid['id']} does not tile")
                self.assertLess(ks, ke)
                cursor = ke
            self.assertAlmostEqual(cursor, end, places=5)


class LintTests(ComposerTestCase):
    def test_clean_composition_lints_clean_under_strict(self) -> None:
        path = self.init()
        run("deepen", "--all-stubs", "--file", str(path))
        self.assertEqual(0, run("lint", "--strict", "--file", str(path)))

    def test_a_promise_paid_before_it_is_made_is_reported(self) -> None:
        path = self.init()
        run("deepen", "--all-stubs", "--file", str(path))
        state = self.state(path)
        promise = next(p for p in state["promises"]
                       if p["opened_by"] != "ch01")
        promise["paid_by"] = "ch01"          # earlier than opened_by
        promise["intentional_open"] = False
        path.write_text(yaml.safe_dump(state, sort_keys=False), "utf-8")

        findings = oc.lint_state(self.state(path))
        messages = [m for tag, _w, m in findings.rows if tag == "WARN"]
        self.assertTrue(
            any("cannot be paid before it is made" in m for m in messages),
            f"expected a backwards-promise warning, got {messages}")
        self.assertEqual(1, run("lint", "--strict", "--file", str(path)))

    def test_broken_budget_and_span_are_reported(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        state = self.state(path)
        state["nodes"][0]["children"][0]["words"] = 1
        state["nodes"][0]["children"][0]["position"] = [0.0, 0.9]
        path.write_text(yaml.safe_dump(state, sort_keys=False), "utf-8")
        messages = [m for tag, _w, m in oc.lint_state(self.state(path)).rows
                    if tag == "WARN"]
        self.assertTrue(any("children budget" in m for m in messages))
        self.assertTrue(any("escapes its parent" in m for m in messages))

    def test_a_fault_planted_in_a_move_list_is_reported(self) -> None:
        path = self.init()
        state = self.state(path)
        fault = sorted(oc.fault_names())[0]
        state["nodes"][0]["moves"].append(
            {"name": fault, "branch": "fallacies_eristic",
             "category": "informal_fallacies", "definition": "", "why": ""})
        path.write_text(yaml.safe_dump(state, sort_keys=False), "utf-8")
        messages = [m for tag, _w, m in oc.lint_state(self.state(path)).rows
                    if tag == "WARN"]
        self.assertTrue(any("names a fault" in m for m in messages))

    def test_a_descriptor_bank_entry_in_a_move_list_is_reported(self) -> None:
        path = self.init()
        state = self.state(path)
        state["nodes"][0]["moves"].append(
            {"name": "rocky desert", "branch": "settings_and_environments",
             "category": "geographic_biomes", "definition": "", "why": ""})
        path.write_text(yaml.safe_dump(state, sort_keys=False), "utf-8")
        messages = [m for tag, _w, m in oc.lint_state(self.state(path)).rows
                    if tag == "WARN"]
        self.assertTrue(any("descriptor bank" in m for m in messages))

    def test_status_deepened_without_children_is_reported(self) -> None:
        path = self.init()
        state = self.state(path)
        state["nodes"][0]["status"] = "deepened"
        path.write_text(yaml.safe_dump(state, sort_keys=False), "utf-8")
        messages = [m for tag, _w, m in oc.lint_state(self.state(path)).rows
                    if tag == "WARN"]
        self.assertTrue(any("no children" in m for m in messages))

    def test_lint_survives_a_hand_mangled_file(self) -> None:
        path = self.init()
        state = self.state(path)
        state["nodes"][0]["position"] = "somewhere in the middle"
        state["nodes"][1]["words"] = "lots"
        state["promises"] = ["not a mapping"]
        state["registry"]["entities"] = [{"name": "a rival",
                                          "introduced_at": "ch99"}]
        path.write_text(yaml.safe_dump(state, sort_keys=False), "utf-8")
        findings = oc.lint_state(self.state(path))     # must not raise
        self.assertGreater(findings.warnings, 0)


class OntologyRuleTests(ComposerTestCase):
    """Rule 3 of the ontology: faults are audit targets, never directives;
    descriptor banks fuel ideation slots, never move lists."""

    def collect_moves(self, path: Path) -> list[dict]:
        state = self.state(path)
        moves = []
        for node, _depth, _parent in oc.walk(state["nodes"]):
            moves.extend(node.get("moves") or [])
        return moves

    def test_no_move_is_a_fault_in_either_kind(self) -> None:
        faults = oc.fault_names()
        for kind in ("fiction", "nonfiction"):
            path = self.init(name=f"{kind}.yaml", kind=kind, words="60000")
            run("deepen", "--all-stubs", "--file", str(path))
            run("deepen", "--all-stubs", "--file", str(path))
            moves = self.collect_moves(path)
            self.assertGreater(len(moves), 20, f"{kind}: too few moves rolled")
            for move in moves:
                self.assertNotIn(move["name"].strip().lower(), faults,
                                 f"{kind}: fault {move['name']!r} emitted")

    def test_no_move_comes_from_a_descriptor_bank(self) -> None:
        banks = oc.descriptor_bank_names()
        for kind in ("fiction", "nonfiction"):
            path = self.init(name=f"{kind}.yaml", kind=kind, words="60000")
            run("deepen", "--all-stubs", "--file", str(path))
            for move in self.collect_moves(path):
                self.assertNotIn(move["branch"], oc.DESCRIPTOR_BANKS)
                self.assertNotIn(move["name"].strip().lower(), banks)

    def test_descriptor_banks_still_fill_the_registry(self) -> None:
        path = self.init()
        registry = self.state(path)["registry"]
        self.assertIn("settings_and_environments",
                      registry["setting"]["source"])
        self.assertIn("tones_and_moods", registry["tone"]["source"])


class CurveTests(ComposerTestCase):
    MAN_IN_HOLE = [[0.0, 0.3], [0.15, 0.35], [0.35, -0.6], [0.6, -0.55],
                   [0.85, 0.35], [1.0, 0.7]]

    def test_valence_interpolates_linearly_between_curve_points(self) -> None:
        # halfway from (0.15, 0.35) to (0.35, -0.60) is 0.35 - 0.95/2
        self.assertAlmostEqual(-0.125,
                               oc.curve_at(self.MAN_IN_HOLE, 0.25), places=6)
        self.assertAlmostEqual(0.35, oc.curve_at(self.MAN_IN_HOLE, 0.15))
        self.assertAlmostEqual(0.3, oc.curve_at(self.MAN_IN_HOLE, 0.0))
        self.assertAlmostEqual(0.7, oc.curve_at(self.MAN_IN_HOLE, 1.0))
        self.assertIsNone(oc.curve_at([], 0.4))

    def test_node_valence_matches_the_recorded_spine_curve(self) -> None:
        path = self.init(
            "--template", "man in hole", name="mih.yaml", words="90000")
        state = self.state(path)
        self.assertEqual([[p, v] for p, v in self.MAN_IN_HOLE],
                         [[float(p), float(v)] for p, v in state["spine"]["curve"]])
        run("deepen", "--all-stubs", "--file", str(path))
        state = self.state(path)
        for node, _depth, _parent in oc.walk(state["nodes"]):
            start, end = oc.node_span(node)
            self.assertAlmostEqual(
                oc.curve_at(self.MAN_IN_HOLE, (start + end) / 2),
                node["valence"], places=3, msg=node["id"])

    def test_span_mode_reads_slope_first_then_valence(self) -> None:
        self.assertEqual("falling", oc.span_mode(0.5, -0.4))
        self.assertEqual("rising", oc.span_mode(-0.5, 0.4))
        self.assertEqual("flat", oc.span_mode(0.0, 0.0))
        self.assertEqual("falling", oc.span_mode(-0.6, 0.0))
        self.assertEqual("flat", oc.span_mode(None, None))


class ConditioningTests(ComposerTestCase):
    def test_falling_and_rising_spans_draw_different_move_pools(self) -> None:
        onto = oc.Ontology()
        pool = oc.build_move_pool(onto, oc.MOVE_BRANCHES_BY_KIND["fiction"])
        self.assertTrue(pool)
        falling = {m["name"] for m in oc.conditioned_moves(
            pool, random.Random(1), "falling", -0.6, -0.3,
            "the plan comes apart", k=40)}
        rising = {m["name"] for m in oc.conditioned_moves(
            pool, random.Random(1), "rising", 0.6, 0.3,
            "the plan comes apart", k=40)}
        self.assertTrue(falling - rising, "conditioning had no effect")

    def test_word_partition_is_exact_and_deterministic(self) -> None:
        for total in (1, 7, 1000, 9999):
            weights = [1.0, 1.3, 0.8, 0.9]
            parts = oc.partition_words(total, weights)
            self.assertEqual(total, sum(parts))
            self.assertEqual(parts, oc.partition_words(total, weights))


class CliTests(ComposerTestCase):
    def test_init_refuses_to_clobber_without_force(self) -> None:
        path = self.init()
        before = path.read_text(encoding="utf-8")
        code = run("init", "--kind", "nonfiction", "--words", "1000",
                   "--seed", "1", "--file", str(path))
        self.assertEqual(1, code)
        self.assertEqual(before, path.read_text(encoding="utf-8"))
        self.assertEqual(0, run("init", "--kind", "nonfiction", "--words",
                                "1000", "--seed", "1", "--force",
                                "--file", str(path)))

    def test_unknown_template_and_node_are_hard_errors(self) -> None:
        path = self.init()
        self.assertEqual(1, run("init", "--kind", "fiction", "--words",
                                "1000", "--template", "no such arc anywhere",
                                "--file", str(self.path("x.yaml"))))
        self.assertEqual(1, run("deepen", "nope01", "--file", str(path)))
        self.assertEqual(1, run("show", "nope01", "--file", str(path)))
        self.assertEqual(1, run("lint", "--file", str(self.path("gone.yaml"))))

    def test_render_writes_markdown(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        md = self.path("outline.md")
        self.assertEqual(0, run("render", "--file", str(path),
                                "--out", str(md)))
        text = md.read_text(encoding="utf-8")
        self.assertIn("# Outline", text)
        self.assertIn("`ch01.s01`", text)
        self.assertIn("Promise ledger", text)
        self.assertNotIn("latex/", text)

        data = oc.document(self.state(path))
        self.assertEqual("ch01", data["nodes"][0]["id"])
        self.assertTrue(data["nodes"][0]["children"])
        self.assertEqual(0.0, data["nodes"][0]["position_pct"][0])

    def test_set_validates_and_writes(self) -> None:
        path = self.init()
        self.assertEqual(0, run("set", "registry.tense=present",
                                "--file", str(path)))
        self.assertEqual("present", self.state(path)["registry"]["tense"])
        self.assertEqual(1, run("set", "registry.tense=subjunctive",
                                "--file", str(path)))
        self.assertEqual(1, run("set", "nodes.ch01.words=10",
                                "--file", str(path)))
        self.assertEqual("present", self.state(path)["registry"]["tense"])

    def test_chapters_flag_redistributes_the_spine(self) -> None:
        path = self.init("--template", "man in hole", "--chapters", "9",
                         name="nine.yaml")
        state = self.state(path)
        self.assertEqual(9, len(state["nodes"]))
        self.assertEqual(state["meta"]["words"],
                         sum(int(n["words"]) for n in state["nodes"]))

    def test_crossover_template_is_a_warning_not_a_failure(self) -> None:
        code = run("init", "--kind", "nonfiction", "--words", "40000",
                   "--seed", "3", "--template", "man in hole",
                   "--file", str(self.path("cross.yaml")))
        self.assertEqual(0, code)
        state = self.state(self.path("cross.yaml"))
        self.assertEqual("man in hole", state["spine"]["template"]["name"])


class SchemaTests(ComposerTestCase):
    def test_state_round_trips_through_yaml_unchanged(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        text = path.read_text(encoding="utf-8")
        reloaded = yaml.safe_load(text)
        again = yaml.safe_dump(reloaded, sort_keys=False, allow_unicode=True,
                               default_flow_style=False, width=100)
        self.assertEqual(text, again, "a load/dump cycle must be a no-op")

    def test_node_keys_keep_their_canonical_order(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        expected = ["id", "title", "purpose", "position", "words", "valence",
                    "status", "moves", "opens", "pays", "children"]
        state = self.state(path)
        for node, _depth, _parent in oc.walk(state["nodes"]):
            self.assertEqual(expected, list(node.keys()), node["id"])

    def test_deepen_does_not_mutate_unrelated_promises(self) -> None:
        path = self.init()
        run("deepen", "ch01", "--file", str(path))
        before = copy.deepcopy(self.state(path)["promises"])
        run("deepen", "ch05", "--file", str(path))
        after = self.state(path)["promises"]
        self.assertEqual(before, after[:len(before)])


class RenderFormatTests(ComposerTestCase):
    """json/toml carry the same document; html is one self-contained page."""

    def composition(self) -> Path:
        path = self.init()
        run("deepen", "--all-stubs", "--file", str(path))
        run("deepen", "ch01.s01", "--file", str(path))   # a third level
        return path

    def rendered(self, path: Path, fmt: str) -> str:
        out = self.path(f"outline.{fmt}")
        self.assertEqual(0, run("render", "--format", fmt, "--file",
                                str(path), "--out", str(out)))
        return out.read_text(encoding="utf-8")

    @staticmethod
    def flat(nodes):
        for node in nodes:
            yield node
            yield from RenderFormatTests.flat(node.get("children") or [])

    def test_json_parses_and_holds_the_invariants(self) -> None:
        path = self.composition()
        doc = json.loads(self.rendered(path, "json"))
        self.assertEqual({"composer", "meta", "registry", "spine", "nodes",
                          "promises"}, set(doc))
        nodes = list(self.flat(doc["nodes"]))
        ids = [n["id"] for n in nodes]
        self.assertEqual(len(ids), len(set(ids)), "node ids must be unique")
        self.assertGreater(len(ids), 12)
        self.assertEqual(doc["meta"]["words"],
                         sum(n["words"] for n in doc["nodes"]))
        for node in nodes:
            kids = node.get("children") or []
            if kids:
                self.assertEqual(node["words"],
                                 sum(k["words"] for k in kids), node["id"])
            self.assertEqual(2, len(node["position"]))
            self.assertLess(node["position"][0], node["position"][1])
        known = {n["id"] for n in nodes}
        for promise in doc["promises"]:
            self.assertIn(promise["opened_by"], known)
            if "paid_by" in promise:
                self.assertIn(promise["paid_by"], known)

    def test_the_omit_empty_convention_holds(self) -> None:
        path = self.composition()
        doc = json.loads(self.rendered(path, "json"))

        def check(value, where):
            if isinstance(value, dict):
                for key, val in value.items():
                    self.assertNotIn(val, (None, "", [], {}),
                                     f"{where}.{key} should have been omitted")
                    check(val, f"{where}.{key}")
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    check(val, f"{where}[{i}]")

        check(doc, "doc")
        # an unpaid, intentionally open promise omits paid_by, keeps the flag
        stub = [n for n in self.flat(doc["nodes"]) if n["status"] == "stub"]
        self.assertTrue(stub)
        self.assertNotIn("children", stub[0])

    def test_toml_round_trips_and_equals_the_json_document(self) -> None:
        path = self.composition()
        as_json = json.loads(self.rendered(path, "json"))
        as_toml = tomllib.loads(self.rendered(path, "toml"))
        self.assertEqual(as_json, as_toml)
        # the deep tree really did survive as arrays of tables
        self.assertTrue(as_toml["nodes"][0]["children"][0]["children"])
        text = self.path("outline.toml").read_text(encoding="utf-8")
        self.assertIn("[[nodes]]", text)
        self.assertIn("[[nodes.children]]", text)
        self.assertIn("[[nodes.children.children]]", text)

    def test_html_is_self_contained_and_anchored(self) -> None:
        path = self.composition()
        page = self.rendered(path, "html")
        doc = json.loads(self.rendered(path, "json"))

        self.assertIn("<svg", page)
        self.assertIn("</svg>", page)
        self.assertIn("prefers-color-scheme: dark", page)

        for node in self.flat(doc["nodes"]):
            self.assertIn(f'id="node-{node["id"]}"', page,
                          f"no anchor for {node['id']}")
        for promise in doc["promises"]:
            self.assertIn(f'id="{promise["id"]}"', page)

        # self-contained: no external references of any kind
        self.assertEqual([], re.findall(r"https?://", page))
        self.assertEqual([], re.findall(r"<(?:script|iframe|link|img)\b",
                                        page, re.I))
        # url(#arcfill) is an internal SVG fragment reference; any
        # other url( would be a fetch
        self.assertEqual([], re.findall(r"@import|url\((?!#)", page))

    def test_json_alias_still_works_and_defaults_to_markdown(self) -> None:
        path = self.init()
        out = self.path("legacy.json")
        self.assertEqual(0, run("render", "--json", "--file", str(path),
                                "--out", str(out)))
        legacy = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(legacy, oc.document(self.state(path)))

        default = self.path("default.txt")
        self.assertEqual(0, run("render", "--file", str(path),
                                "--out", str(default)))
        self.assertTrue(
            default.read_text(encoding="utf-8").startswith("# Outline"))

    def test_every_format_prints_to_stdout_without_out(self) -> None:
        path = self.init()
        for fmt in ("md", "json", "toml", "html"):
            sink = io.StringIO()
            argv, sys.argv = sys.argv, [
                "outline_composer.py", "render", "--format", fmt,
                "--file", str(path)]
            try:
                with contextlib.redirect_stdout(sink):
                    code = oc.main()
            finally:
                sys.argv = argv
            self.assertEqual(0, code, fmt)
            self.assertGreater(len(sink.getvalue()), 200, fmt)


if __name__ == "__main__":
    unittest.main()
