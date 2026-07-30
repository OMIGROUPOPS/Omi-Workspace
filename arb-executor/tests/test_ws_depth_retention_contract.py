import ast
import datetime
import hashlib
import unittest
from pathlib import Path


RECORDER = Path(__file__).resolve().parents[1] / "ws_depth_recorder.py"


def load_helpers():
    tree = ast.parse(RECORDER.read_text(encoding="utf-8"))
    names = {"_source_epoch", "_apply_book_message"}
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    namespace = {
        "datetime": datetime,
        "hashlib": hashlib,
        "_books": {},
    }
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(RECORDER), "exec"),
         namespace)
    return namespace


class WsDepthRetentionContractTests(unittest.TestCase):
    def setUp(self):
        self.helpers = load_helpers()

    def test_source_time_is_measured_or_absent_never_receive_time(self):
        source_epoch = self.helpers["_source_epoch"]
        self.assertEqual(source_epoch({"msg": {"ts": 1_700_000_000_000}}),
                         1_700_000_000)
        self.assertEqual(source_epoch({"timestamp": "2026-07-30T01:02:03Z"}),
                         1_785_373_323)
        self.assertIsNone(source_epoch({"msg": {"market_ticker": "M"}}))

    def test_snapshot_and_delta_reconstruct_both_sides_of_bbo(self):
        apply = self.helpers["_apply_book_message"]
        snapshot = apply({
            "type": "orderbook_snapshot",
            "msg": {
                "market_ticker": "M",
                "yes": [[42, 5], [41, 3]],
                "no": [[55, 7]],
            },
        })
        self.assertEqual(snapshot["yes_bid"], 42)
        self.assertEqual(snapshot["yes_ask"], 45)
        self.assertEqual(snapshot["no_bid"], 55)
        self.assertEqual(snapshot["no_ask"], 58)
        self.assertEqual(snapshot["denominator_status"], "AVAILABLE")

        delta = apply({
            "type": "orderbook_delta",
            "msg": {
                "market_ticker": "M",
                "side": "no",
                "price": 55,
                "delta": -7,
            },
        })
        self.assertIsNone(delta["yes_ask"])
        self.assertEqual(delta["denominator_status"], "NO_DENOMINATOR")

    def test_recorder_covers_all_six_tennis_series_and_hashes_raw_frames(self):
        source = RECORDER.read_text(encoding="utf-8")
        for series in (
            "KXATPMATCH",
            "KXWTAMATCH",
            "KXATPCHALLENGERMATCH",
            "KXWTACHALLENGERMATCH",
            "KXITFMATCH",
            "KXITFWMATCH",
        ):
            self.assertIn(series, source)
        self.assertIn("raw_ws_sha256", source)
        self.assertIn("staleness_status", source)


if __name__ == "__main__":
    unittest.main()
