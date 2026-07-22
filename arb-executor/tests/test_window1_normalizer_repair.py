import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "arb-executor" / "analysis" / "window1_normalizer_repair.py"
SPEC = importlib.util.spec_from_file_location("window1_normalizer_repair", MODULE_PATH)
REPAIR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(REPAIR)


class Window1NormalizerRepairTests(unittest.TestCase):
    def test_upstream_trade_retains_receipt_size_clock_and_direction(self):
        row = {
            "trade_id": "sanitized-receipt",
            "created_time": "2026-07-12T12:00:00Z",
            "yes_price_dollars": "0.42",
            "count_fp": "5",
            "taker_side": "yes",
        }
        got = REPAIR.upstream_public_trade(row, "KXSAMPLE")
        self.assertEqual(got["receipt_id"], "sanitized-receipt")
        self.assertEqual(got["size"], 5.0)
        self.assertEqual(got["price_cents"], 42)
        self.assertEqual(got["taker_side"], "yes")
        self.assertTrue(got["true_print"])

    def test_upstream_trade_rejects_missing_identity_or_positive_size(self):
        base = {
            "trade_id": "sanitized-receipt",
            "created_time": "2026-07-12T12:00:00Z",
            "yes_price_dollars": "0.42",
            "count_fp": "5",
        }
        for key, value in (("trade_id", None), ("count_fp", 0)):
            row = dict(base)
            row[key] = value
            with self.assertRaises(ValueError):
                REPAIR.upstream_public_trade(row, "KXSAMPLE")

    def test_daysheet_ct_is_preserved_but_identity_loss_is_rejected(self):
        got = REPAIR.inspect_daysheet_cache(
            {"ts": 1.0, "price_c": 42, "ct": 5}, "KXSAMPLE")
        self.assertEqual(got["preserved_fields"]["size"], 5.0)
        self.assertFalse(got["admissible_true_print"])
        self.assertIn("stable receipt identity", got["contract_rejections"][0])

    def test_zero_and_missing_size_never_become_one(self):
        self.assertEqual(REPAIR.positive_size(0), 0.0)
        self.assertEqual(REPAIR.positive_size(None), 0.0)
        transition = REPAIR.synthetic_transition("KXSAMPLE", 1.0, 42)
        self.assertEqual(transition["size"], 0.0)
        self.assertFalse(transition["admissible_true_print"])

    def test_limited_books_are_not_exact_queue_evidence(self):
        top5 = REPAIR.limited_book("premarket_ticks", "KXSAMPLE", 1.0)
        top20 = REPAIR.limited_book("depth_recorder", "KXSAMPLE", 1.0)
        self.assertEqual(top5["capture_depth"], "top5")
        self.assertEqual(top20["capture_depth"], "top20")
        self.assertFalse(top5["exact_queue_use"])
        self.assertFalse(top20["full_ladder"])

    def test_samples_are_explicitly_structural(self):
        samples = REPAIR.sanitized_samples()
        self.assertTrue(samples["structural_samples_not_market_observations"])


if __name__ == "__main__":
    unittest.main()
