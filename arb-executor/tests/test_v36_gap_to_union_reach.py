import importlib.util
import hashlib
import gzip
import json
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "arb-executor/analysis/build_v36_gap_to_union_reach.py"
SPEC = importlib.util.spec_from_file_location("v36_gap", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MOD)


class GapToReachUnitTests(unittest.TestCase):
    def test_take_shallow_owner(self):
        row = {"entry_cents": 56, "fill_class": "PROVEN_TAKER_X", "decision_count": 1}
        owner, _, cents = MOD.issue_owner(row, {"union_reach_cents": 50, "leg_direction": "CLIMBING"}, {})
        self.assertEqual((owner, cents), ("TAKE_FIRED_ABOVE_REACH", 6))

    def test_cap_owner_uses_reach_moment_cap(self):
        row = {"entry_cents": None, "fill_class": None, "decision_count": 5}
        owner, _, cents = MOD.issue_owner(row, {"union_reach_cents": 61, "leg_direction": "FALLING"}, {"pair_cap_cents": 58, "order_after_cents": 58, "combined_state": "FALLING"})
        self.assertEqual((owner, cents), ("PAIR_CAP_ARITHMETIC", 3))

    def test_reachable_rest_exposes_fill_model_seam(self):
        row = {"entry_cents": None, "fill_class": None, "decision_count": 5}
        owner, _, cents = MOD.issue_owner(row, {"union_reach_cents": 40, "leg_direction": "FALLING"}, {"pair_cap_cents": None, "order_after_cents": 41, "combined_state": "SETTLED"})
        self.assertEqual((owner, cents), ("FILL_MODEL_SEAM_NOT_V36_ORGAN", 0))

    def test_divot_owner(self):
        row = {"entry_cents": None, "fill_class": None, "decision_count": 5}
        owner, _, cents = MOD.issue_owner(row, {"union_reach_cents": 68, "leg_direction": "CLIMBING"}, {"pair_cap_cents": None, "order_after_cents": 65, "combined_state": "RISING"})
        self.assertEqual((owner, cents), ("DIVOT_CLASS_NOT_IMPLEMENTED", 3))

    def test_admission_is_unpriced(self):
        row = {"entry_cents": None, "fill_class": None, "decision_count": 0}
        owner, _, cents = MOD.issue_owner(row, {"union_reach_cents": 44, "leg_direction": "FALLING"}, None)
        self.assertEqual(owner, "ADMISSION_NO_TWO_SIDED_BOOK")
        self.assertIsNone(cents)


class FrozenArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = Path(os.environ.get("V36_GAP_ARTIFACT_DIR", ROOT / ".claude/window1_live_v4_replay/v36_gap_to_union_reach_20260807"))

    def test_class_conservation(self):
        doc = json.loads((self.artifact / "CLASS_SUMMARY.json").read_text())
        expected = {"MATCHED": 52, "SHALLOW": 212, "ONE_MISSING": 486, "BOTH_MISSING": 35, "NO_REACH": 19}
        self.assertEqual({key: doc["aggregate"][key]["games"] for key in expected}, expected)
        self.assertTrue(doc["conservation"]["pass"])

    def test_reach_exact_reconstruction(self):
        doc = json.loads((self.artifact / "REACH_RECONSTRUCTION_RECEIPT.json").read_text())
        self.assertTrue(doc["exact_match"])
        self.assertEqual(doc["reconstructed"]["union"]["under_par"], 637)
        self.assertEqual(doc["reconstructed"]["union"]["none"], 19)
        self.assertEqual(doc["prints"]["accepted_rows"], 373203)

    def test_layer_issue_conservation(self):
        doc = json.loads((self.artifact / "LAYER_BIND_RANKING.json").read_text())
        self.assertEqual(doc["issue_conservation"], {"issue_sides": 1209, "missing_sides": 556, "shallow_sides": 653})
        self.assertEqual(sum(row["issue_sides"] for row in doc["coarse_organ_ranking"]), 1209)

    def test_no_forbidden_access(self):
        doc = json.loads((self.artifact / "FORBIDDEN_ACCESS_RECEIPT.json").read_text())
        self.assertFalse(any(value for key, value in doc.items() if key != "statement"))

    def test_builder_does_not_import_policy(self):
        text = MODULE_PATH.read_text()
        self.assertNotIn("import live_v4", text)
        self.assertNotIn("from live_v4", text)

    def test_artifact_manifest_covers_package(self):
        doc = json.loads((self.artifact / "ARTIFACT_HASH_MANIFEST.json").read_text())
        rows = {row["path"]: row for row in doc["files"]}
        expected = {p.name for p in self.artifact.iterdir() if p.is_file() and p.name != "ARTIFACT_HASH_MANIFEST.json"}
        self.assertEqual(set(rows), expected)
        for name, row in rows.items():
            data = (self.artifact / name).read_bytes()
            self.assertEqual(row["bytes"], len(data))
            self.assertEqual(row["sha256"], hashlib.sha256(data).hexdigest())

    def test_ledger_row_conservation(self):
        expected = {
            "UNION_REACH_LEG_LEDGER.jsonl.gz": 1608,
            "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz": 1608,
            "V36_GAP_TO_REACH_GAME_LEDGER.jsonl.gz": 804,
            "LAYER_BIND_ISSUE_LEDGER.jsonl.gz": 1209,
        }
        for name, count in expected.items():
            with gzip.open(self.artifact / name, "rt", encoding="utf-8") as f:
                self.assertEqual(sum(1 for _ in f), count, name)


if __name__ == "__main__":
    unittest.main()
