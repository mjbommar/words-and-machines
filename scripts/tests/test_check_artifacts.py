"""Mutation controls for the active manifest checker itself."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_artifacts", ROOT / "scripts" / "check_artifacts.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class ManifestSchemaControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (
                ROOT
                / "artifacts/claims/A0.comp.byte-roundtrip-8-16/manifest.json"
            ).read_text()
        )

    def errors(self, mutation):
        record = copy.deepcopy(self.manifest)
        mutation(record)
        return CHECK.validate_schema_value(record, CHECK.SCHEMA)

    def test_nested_required_field_is_load_bearing(self):
        errors = self.errors(lambda record: record["checker"].pop("expected_result"))
        self.assertTrue(any("expected_result" in error for error in errors), errors)

    def test_nested_unknown_field_is_rejected(self):
        errors = self.errors(lambda record: record["negative_control"].update(extra=True))
        self.assertTrue(any("unknown field extra" in error for error in errors), errors)

    def test_bad_digest_is_rejected_by_schema(self):
        errors = self.errors(
            lambda record: record["artifacts"][0].update(sha256="not-a-digest")
        )
        self.assertTrue(any("does not match" in error for error in errors), errors)

    def test_empty_semantic_inputs_are_rejected(self):
        errors = self.errors(lambda record: record.update(semantic_inputs=[]))
        self.assertTrue(any("too few items" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
