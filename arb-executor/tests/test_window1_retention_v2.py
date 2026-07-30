import ast
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
LIVE = REPO / "arb-executor" / "live_v4.py"
SCRAPER = REPO / "arb-executor" / "kalshi_price_scraper.py"


def function_source(name):
    source = LIVE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == name
    )
    return ast.get_source_segment(source, node) or ""


def scraper_function_source(name):
    source = SCRAPER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == name
    )
    return ast.get_source_segment(source, node) or ""


class RetentionV2Tests(unittest.TestCase):
    def test_ws_frames_retain_source_receive_staleness_and_raw_hash(self):
        meta = function_source("_ws_frame_meta")
        ingest = function_source("_ingest_ws_frame")
        bbo = function_source("_log_bbo_retention")
        trade = function_source("_log_trade_retention")

        self.assertIn("raw_sha256", meta)
        self.assertIn("source_ts", meta)
        self.assertIn("staleness_ms", meta)
        self.assertIn("_ws_frame_meta(raw, msg)", ingest)
        self.assertIn("best_bid_cents", bbo)
        self.assertIn("best_ask_cents", bbo)
        self.assertIn("trade_id", trade)

    def test_decision_consultation_carries_exact_anchor_lineage(self):
        anchor = function_source("_v4_entry_anchor")
        dossier = function_source("_entry_dossier")

        self.assertIn("consulted_at_ts", anchor)
        self.assertIn("anchor_source", anchor)
        self.assertIn("last_trade_source_ts", anchor)
        self.assertIn("last_trade_raw_sha256", anchor)
        self.assertIn("bbo_source_ts", anchor)
        self.assertIn("bbo_raw_sha256", anchor)
        self.assertIn('"consultation_lineage"', dossier)

    def test_retention_is_enabled(self):
        config = json.loads(
            (REPO / "arb-executor" / "config" /
             "deploy_v5_live.json").read_text(encoding="utf-8")
        )
        self.assertTrue(config["decision_input_retention_v2"])

    def test_schedule_revisions_retain_fields_and_raw_response_hash(self):
        init_db = scraper_function_source("init_db")
        poll = scraper_function_source("poll_cycle")

        self.assertIn("kalshi_schedule_revisions", init_db)
        self.assertIn("schedule_sha256", init_db)
        self.assertIn("raw_response_sha256", init_db)
        self.assertIn("hashlib.sha256(r.content)", poll)
        self.assertIn("occurrence_datetime", poll)
        self.assertIn("expected_expiration_time", poll)


if __name__ == "__main__":
    unittest.main()
