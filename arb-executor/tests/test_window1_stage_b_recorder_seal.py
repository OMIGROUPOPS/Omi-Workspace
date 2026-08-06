import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


REGISTRY = load(
    "window1_holdout_capture_registry",
    "analysis/window1_holdout_capture_registry.py",
)
RECON = load(
    "window1_nightly_reconciliation",
    "analysis/window1_nightly_reconciliation.py",
)


class StageBRecorderSealTests(unittest.TestCase):
    def test_recorder_guard_matches_only_the_real_recorder_command(self):
        source = (ROOT / "deploy/ws_capture_guard.sh").read_text()
        self.assertIn("^python3 -u ws_depth_recorder.py$", source)
        self.assertNotIn('pgrep -f "ws_depth_recorder.py"', source)

    def test_touch_class_registry_has_no_strategy_or_trading_surface(self):
        source = (ROOT / "analysis/window1_holdout_capture_registry.py").read_text()
        self.assertNotIn("/portfolio/", source)
        self.assertNotIn("post_order", source)
        self.assertNotIn("score_event", source)
        self.assertEqual(set(REGISTRY.SERIES.values()), {
            "ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"
        })
        self.assertIn("LOCK_EX | fcntl.LOCK_NB", source)
        self.assertIn("SKIP_ALREADY_RUNNING", source)

    def test_event_date_and_identity_receipt_are_deterministic(self):
        event = {
            "event_id": "KXATPMATCH-26AUG06ABCCDE",
            "category": "ATP_MAIN",
            "event_date": "2026-08-06",
            "tickers": ["E-ABC", "E-CDE"],
            "series": "KXATPMATCH",
        }
        self.assertEqual(
            REGISTRY.event_date(event["event_id"]).isoformat(),
            "2026-08-06",
        )
        self.assertEqual(
            REGISTRY.digest(event),
            REGISTRY.digest(dict(reversed(list(event.items())))),
        )

    def test_reconciliation_sample_is_seeded_and_stable(self):
        events = [{"event_id": f"E-{number:03d}"} for number in range(60)]
        first = RECON.deterministic_sample(events, "2026-08-06", 20)
        second = RECON.deterministic_sample(
            list(reversed(events)), "2026-08-06", 20
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 20)
        self.assertEqual(len({row["event_id"] for row in first}), 20)

    def test_reconciliation_compare_names_every_mismatch(self):
        ours = {
            "same": {"price": 40, "size": "5", "side": "yes"},
            "price": {"price": 41, "size": "5", "side": "yes"},
            "size": {"price": 40, "size": "4", "side": "yes"},
            "side": {"price": 40, "size": "5", "side": "no"},
            "ours-only": {"price": 40, "size": "5", "side": "yes"},
        }
        exchange = {
            "same": {"price": 40, "size": "5", "side": "yes"},
            "price": {"price": 42, "size": "5", "side": "yes"},
            "size": {"price": 40, "size": "5", "side": "yes"},
            "side": {"price": 40, "size": "5", "side": "yes"},
            "exchange-only": {"price": 40, "size": "5", "side": "yes"},
        }
        self.assertEqual(RECON.compare(ours, exchange), {
            "exchange_trades": 5,
            "our_prints": 5,
            "ex_not_ours": 1,
            "ours_not_ex": 1,
            "price_mm": 1,
            "size_mm": 1,
            "side_mm": 1,
        })

    def test_stored_loader_filters_ticker_and_guarded_window(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prints.jsonl.gz"
            rows = [
                {
                    "exchange_ts": "2026-08-06T12:00:00Z",
                    "price_cents": 40,
                    "receipt_id": "inside",
                    "size": 5,
                    "taker_side": "yes",
                    "ticker": "E-A",
                    "trade_id": "inside",
                    "true_print": True,
                },
                {
                    "exchange_ts": "2026-08-06T15:00:00Z",
                    "price_cents": 41,
                    "receipt_id": "outside-time",
                    "size": 5,
                    "taker_side": "yes",
                    "ticker": "E-A",
                    "trade_id": "outside-time",
                    "true_print": True,
                },
                {
                    "exchange_ts": "2026-08-06T12:00:00Z",
                    "price_cents": 50,
                    "receipt_id": "outside-ticker",
                    "size": 5,
                    "taker_side": "no",
                    "ticker": "E-B",
                    "trade_id": "outside-ticker",
                    "true_print": True,
                },
            ]
            with gzip.open(path, "wt", encoding="utf-8") as handle:
                for row in rows:
                    handle.write(json.dumps(row) + "\n")
            loaded = RECON.load_stored(
                path, {"E-A"}, {"E-A": (1786010000, 1786020000)}
            )
            self.assertEqual(set(loaded), {"inside"})

    def test_public_trade_preserves_exchange_fields(self):
        row = RECON.public_trade({
            "trade_id": "T",
            "ticker": "E-A",
            "created_time": "2026-08-06T12:00:00Z",
            "yes_price_dollars": "0.4200",
            "count_fp": "5.00",
            "taker_side": "yes",
        }, "E-A")
        self.assertEqual(row, {
            "trade_id": "T",
            "ticker": "E-A",
            "ts": 1786017600.0,
            "price": 42,
            "size": "5",
            "side": "yes",
        })

    def test_nightly_source_is_public_trade_get_only_and_n20_bound(self):
        source = (ROOT / "analysis/window1_nightly_reconciliation.py").read_text()
        self.assertIn("/markets/trades", source)
        self.assertNotIn("/portfolio/", source)
        self.assertIn('"N": 20', source)
        self.assertIn(
            "scheduled_start_minus_8h_through_guarded_cutoff_inclusive",
            source,
        )


if __name__ == "__main__":
    unittest.main()
