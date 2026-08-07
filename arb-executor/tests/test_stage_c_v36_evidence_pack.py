import csv
import hashlib
import json
import sys
import unittest
from pathlib import Path


if len(sys.argv) < 2:
    raise RuntimeError("usage: test_stage_c_v36_evidence_pack.py OUTPUT_DIR")
OUTPUT_ROOT = Path(sys.argv[1]).resolve()
del sys.argv[1]


class StageCV36EvidencePackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = OUTPUT_ROOT
        cls.selection = json.loads((cls.root / "EVIDENCE_SELECTION.json").read_text(encoding="utf-8"))

    def marks(self, short):
        return json.loads((self.root / "exemplar_packs" / f"{short}_DECISION_MARKS.json").read_text(encoding="utf-8"))

    def test_six_roles_are_exact(self):
        self.assertEqual([x["short"] for x in self.selection["games"]], ["ARNROM", "KIRSEK", "DAHBAE", "LAJVAN", "WESPAA", "MATMOR"])

    def test_arnrom_94(self):
        marks = self.marks("ARNROM")
        self.assertEqual(marks["legs"]["ARN"]["frozen_result"]["entry_cents"], 56)
        self.assertEqual(marks["legs"]["ROM"]["frozen_result"]["entry_cents"], 38)

    def test_deep_clean_maker(self):
        marks = self.marks("KIRSEK")
        kir = marks["legs"]["KIR"]["frozen_result"]
        self.assertEqual((kir["entry_cents"], kir["print_backed_floor_cents"]), (15, 15))
        self.assertIn("MAKER", kir["fill_class"])

    def test_wide_spread_both_maker(self):
        marks = self.marks("DAHBAE")
        self.assertTrue(all("MAKER" in leg["frozen_result"]["fill_class"] for leg in marks["legs"].values()))
        self.assertEqual(sum(leg["frozen_result"]["entry_cents"] for leg in marks["legs"].values()), 98)

    def test_carried_wart(self):
        marks = self.marks("LAJVAN")
        deltas = sorted(leg["frozen_result"]["entry_cents"] - leg["frozen_result"]["close_telemetry_only_cents"] for leg in marks["legs"].values())
        self.assertEqual(deltas, [-8, 4])

    def test_rest_starved(self):
        marks = self.marks("WESPAA")
        self.assertFalse(any(leg["frozen_result"]["credited"] for leg in marks["legs"].values()))
        self.assertEqual(marks["legs"]["WES"]["frozen_result"]["resting_target_at_hard_edge_cents"], 60)

    def test_skip(self):
        marks = self.marks("MATMOR")
        self.assertEqual(sum(leg["conservation"]["extracted_decision_count"] for leg in marks["legs"].values()), 0)

    def test_decision_and_timeline_conservation(self):
        for row in self.selection["games"]:
            marks = self.marks(row["short"])
            self.assertTrue(all(leg["conservation"]["pass"] for leg in marks["legs"].values()))
            with (self.root / "exemplar_packs" / f"{row['short']}_DUAL_TIMELINE_V2.csv").open(encoding="utf-8", newline="") as handle:
                timeline = list(csv.DictReader(handle))
            self.assertEqual(len(timeline), row["timeline_rows"])
            self.assertEqual({x["leg"] for x in timeline}, set(marks["legs"]))
            self.assertEqual(sum(x["row_type"] == "WINDOW_LEFT" for x in timeline), 2)
            self.assertEqual(sum(x["row_type"] == "WINDOW_RIGHT" for x in timeline), 2)

    def test_forbidden_access(self):
        receipt = json.loads((self.root / "FORBIDDEN_ACCESS_RECEIPT.json").read_text(encoding="utf-8"))
        for key in ("live_capital_accesses", "live_engine_launches", "shadow_launches", "policy_invocations", "score_invocations", "network_runtime_accesses", "order_accesses", "position_accesses", "cron_mutations"):
            self.assertEqual(receipt[key], 0)

    def test_artifact_manifest(self):
        manifest = json.loads((self.root / "ARTIFACT_HASH_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["file_count"], len(manifest["files"]))
        for name, expected in manifest["files"].items():
            path = self.root / name
            self.assertTrue(path.is_file(), name)
            self.assertEqual(path.stat().st_size, expected["bytes"], name)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected["sha256"], name)

    def test_frozen_source_identity(self):
        source = json.loads((self.root / "SOURCE_HASH_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(source["v36"]["commit"], "bfde0d8d1135f5c5f48a5f3d619ab30050efab83")
        self.assertEqual(source["v36"]["policy_sha256"], "5db3922d5749e11548bca0c301abec19da5e2dfb993ffc17a44ec90989e34f73")
        self.assertEqual(source["certified_prints"]["required_sha256"], "e9b5a765b51ddbf0d65364c4f38744ad949ca3c675e5b3a0e472392fbcfabb55")


if __name__ == "__main__":
    unittest.main()
