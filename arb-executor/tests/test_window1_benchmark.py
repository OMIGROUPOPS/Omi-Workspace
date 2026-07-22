import importlib.util
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


MODULE_PATH = (Path(__file__).resolve().parents[1]
               / 'analysis' / 'window1_benchmark.py')
SPEC = importlib.util.spec_from_file_location('window1_benchmark', MODULE_PATH)
window1 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = window1
SPEC.loader.exec_module(window1)

BenchmarkError = window1.BenchmarkError
build_event_ledger = window1.build_event_ledger
canonical_true_prints = window1.canonical_true_prints
replay_resting_buy = window1.replay_resting_buy
resolve_window_end = window1.resolve_window_end
score_outcomes = window1.score_outcomes
valid_full_book = window1.valid_full_book
validate_replay = window1.validate_replay
next_complete_utc_dates = window1.next_complete_utc_dates
period_for_day = window1.period_for_day
load_holdout_declaration = window1.load_holdout_declaration


def book(ticker, timestamp, quantity, *, gap=False, source="ws_depth",
         depth="full"):
    return {
        "receipt_id": f"book-{ticker}-{timestamp}",
        "ticker": ticker,
        "exchange_ts": timestamp,
        "source": source,
        "capture_depth": depth,
        "epoch_id": "epoch-1",
        "sequence": int(timestamp),
        "sequence_valid": True,
        "gap_before": gap,
        "corrupt": False,
        "bids": [[40, quantity], [39, 10]],
        "asks": [[41, 10]],
    }


def order(event_id, ticker, order_id, *, end=20):
    return {
        "event_id": event_id,
        "ticker": ticker,
        "leg": ticker.rsplit("-", 1)[-1],
        "order_id": order_id,
        "client_order_id": f"client-{order_id}",
        "purpose": "entry",
        "action": "buy",
        "price_cents": 40,
        "quantity": 5,
        "exchange_created_ts": 10,
        "evaluation_end_exchange_ts": end,
    }


def true_print(identity, ticker, timestamp, size, *, source="public_tape",
               exchange_ts=True):
    return {
        "receipt_id": identity,
        "ticker": ticker,
        "exchange_ts": timestamp if exchange_ts else None,
        "local_received_ts": timestamp + 100,
        "price_cents": 40,
        "size": size,
        "source": source,
        "true_print": True,
    }


class WindowBoundaryTests(unittest.TestCase):
    def test_inspected_july_18_through_20_are_development(self):
        for day in ('2026-07-18', '2026-07-19', '2026-07-20'):
            self.assertEqual(period_for_day(day), 'fit')

    def test_forward_holdout_dates_follow_freeze_utc_date(self):
        freeze = window1.dt.datetime(
            2026, 7, 22, 0, 1, tzinfo=window1.dt.timezone.utc)
        self.assertEqual(next_complete_utc_dates(freeze), [
            '2026-07-23', '2026-07-24', '2026-07-25'])
        self.assertEqual(
            period_for_day('2026-07-23', next_complete_utc_dates(freeze)),
            'holdout')

    def test_holdout_declaration_proves_committed_freeze_blob(self):
        freeze = {
            'forward_holdout': {
                'dates': ['2026-07-23', '2026-07-24', '2026-07-25'],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            freeze_path = root / 'window1_freeze.json'
            freeze_path.write_text(
                json.dumps(freeze, sort_keys=True), encoding='utf-8')
            freeze_bytes = freeze_path.read_bytes()
            declaration = {
                'holdout_dates': freeze['forward_holdout']['dates'],
                'source_freeze_sha256':
                    window1.sha256_file(freeze_path),
                'git_commit_sha': 'a' * 40,
                'freeze_receipt_repo_path':
                    '.claude/window1/window1_freeze.json',
                'freeze_and_dates_committed_before_holdout': True,
            }
            declaration_path = root / 'declaration.json'
            declaration_path.write_text(
                json.dumps(declaration), encoding='utf-8')
            completed = mock.Mock(
                returncode=0, stdout=freeze_bytes, stderr=b'')
            with mock.patch.object(
                    window1.subprocess, 'run', return_value=completed):
                loaded = load_holdout_declaration(
                    declaration_path, freeze, freeze_path)
            self.assertEqual(loaded, declaration)

    def test_schedule_only_gets_named_positive_corridor(self):
        end, source = resolve_window_end(
            {"scheduled_start_exchange_ts": 1_000}, 30)
        self.assertEqual(end, 2_800)
        self.assertEqual(source, "schedule_plus_30m_corridor")
        with self.assertRaises(BenchmarkError):
            resolve_window_end({"scheduled_start_exchange_ts": 1_000}, 0)

    def test_verified_actual_start_controls_right_edge(self):
        end, source = resolve_window_end({
            "scheduled_start_exchange_ts": 1_000,
            "actual_start_exchange_ts": 900,
            "actual_start_verified": True,
            "actual_start_source": "sportradar_milestone",
        }, 30)
        self.assertEqual(end, 900)
        self.assertEqual(source, "sportradar_milestone")


class PrintLawTests(unittest.TestCase):
    def test_zero_and_missing_sizes_stay_zero_and_receipts_deduplicate(self):
        rows = [
            true_print("r1", "T-A", 1, 0),
            true_print("r1", "T-A", 1, 0, source="exchange_trade"),
            true_print("r2", "T-A", 2, None),
        ]
        prints, errors = canonical_true_prints(rows)
        self.assertEqual(errors, [])
        self.assertEqual(len(prints), 2)
        self.assertEqual(sum(row["size"] for row in prints), 0)

    def test_synthetic_source_and_local_only_clock_are_rejected(self):
        synthetic = true_print("r1", "T-A", 1, 5,
                               source="transition_row")
        local_only = true_print("r2", "T-A", 2, 5,
                                exchange_ts=False)
        prints, errors = canonical_true_prints([synthetic, local_only])
        self.assertEqual(prints, [])
        self.assertEqual({row["mismatch_type"] for row in errors},
                         {"source", "clock"})


class BookLawTests(unittest.TestCase):
    def test_top_five_and_top_twenty_cannot_support_queue_replay(self):
        ok5, reason5 = valid_full_book(
            book("T-A", 1, 3, source="premarket_ticks", depth="top5"))
        ok20, reason20 = valid_full_book(
            book("T-A", 1, 3, source="depth_recorder", depth="top20"))
        self.assertFalse(ok5)
        self.assertIn("top-five", reason5)
        self.assertFalse(ok20)
        self.assertIn("top-20", reason20)

    def test_gap_and_corruption_invalidate_ws_epoch(self):
        ok, reason = valid_full_book(book("T-A", 1, 3, gap=True))
        self.assertFalse(ok)
        self.assertIn("gap", reason)
        corrupt = book("T-A", 1, 3)
        corrupt["corrupt"] = True
        ok, reason = valid_full_book(corrupt)
        self.assertFalse(ok)
        self.assertIn("corrupt", reason)


class QueueReplayTests(unittest.TestCase):
    def test_exact_fill_requires_volume_through_queue_and_order(self):
        result = replay_resting_buy(
            order("E", "T-A", "o1"),
            [{"receipt_id": "r1", "ticker": "T-A", "exchange_ts": 12,
              "price_cents": 40, "size": 8, "source": "public_tape"}],
            [book("T-A", 9, 3)],
        )
        self.assertEqual(result.status, "filled")
        self.assertEqual(result.completion_earliest, 12)
        self.assertEqual(result.completion_latest, 12)

    def test_exact_nonfill_is_reproduced(self):
        result = replay_resting_buy(
            order("E", "T-A", "o1"),
            [{"receipt_id": "r1", "ticker": "T-A", "exchange_ts": 12,
              "price_cents": 40, "size": 2, "source": "public_tape"}],
            [book("T-A", 9, 3)],
        )
        self.assertEqual(result.status, "not_filled")

    def test_unattributed_cancellation_is_queue_unknown(self):
        result = replay_resting_buy(
            order("E", "T-A", "o1"),
            [{"receipt_id": "r1", "ticker": "T-A", "exchange_ts": 12,
              "price_cents": 40, "size": 5, "source": "public_tape"}],
            [book("T-A", 9, 3), book("T-A", 11, 0)],
        )
        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.mismatch_type, "queue")


class DenominatorAndMetricTests(unittest.TestCase):
    def events(self):
        return [
            {"event_id": "E1", "category": "ATP_MAIN",
             "event_date": "2026-07-12", "legs": ["E1-A", "E1-B"]},
            {"event_id": "E2", "category": "WTA_MAIN",
             "event_date": "2026-07-13", "legs": ["E2-A", "E2-B"]},
            {"event_id": "E3", "category": "ATP_CHALL",
             "event_date": "2026-07-14", "legs": []},
            {"event_id": "E4", "category": "WTA_CHALL",
             "event_date": "2026-07-15", "legs": ["E4-A", "E4-B"],
             "floor_exclusion": "verified_pre_window_cancel_or_void",
             "floor_evidence_receipt_id": "void-r1"},
        ]

    def test_missing_data_remains_in_denominator(self):
        ledger, errors = build_event_ledger(self.events())
        self.assertEqual(errors, [])
        e3 = next(row for row in ledger if row["event_id"] == "E3")
        self.assertTrue(e3["floor_pass"])
        self.assertEqual(e3["data_state"], "unknown_missing_leg_map")
        e4 = next(row for row in ledger if row["event_id"] == "E4")
        self.assertFalse(e4["floor_pass"])

    def test_raw_d_c_s_and_delta_yardsticks_are_separate(self):
        ledger, _ = build_event_ledger(self.events())
        outcomes = [
            {"event_id": "E1", "candidate_id": "p1", "period": "fit",
             "status": "ok", "legs": [
                 {"leg": "A", "filled_quantity": 5,
                  "required_quantity": 5, "fill_vwap_cents": 60,
                  "w1_close_reference_cents": 62},
                 {"leg": "B", "filled_quantity": 5,
                  "required_quantity": 5, "fill_vwap_cents": 39,
                  "w1_close_reference_cents": 38},
             ]},
            {"event_id": "E2", "candidate_id": "p1", "period": "fit",
             "status": "ok", "legs": [
                 {"leg": "A", "filled_quantity": 5,
                  "required_quantity": 5, "fill_vwap_cents": 55,
                  "w1_close_reference_cents": 54},
                 {"leg": "B", "filled_quantity": 5,
                  "required_quantity": 5, "fill_vwap_cents": 47,
                  "w1_close_reference_cents": 49},
             ]},
        ]
        result = score_outcomes(ledger, outcomes, period="fit",
                                candidate_id="p1")
        self.assertEqual((result["D"], result["C"], result["S"]), (3, 2, 1))
        self.assertEqual(result["combined_vs_par_delta_distribution"]["p50"], -1)
        self.assertEqual(result["pair_reference_delta"]["n"], 2)
        self.assertEqual(result["unknown_missing_error_thin_corrupt_n"], 1)
        self.assertFalse(result["exits_or_window2_fields_consumed"])


class ValidationGateTests(unittest.TestCase):
    def test_failed_attempt_requires_exchange_rejection_receipt(self):
        events = [{"event_id": "E1", "category": "ATP_MAIN",
                   "event_date": "2026-07-12", "legs": ["T-A", "T-B"]}]
        ledger, _ = build_event_ledger(events)
        attempts = [
            {**order("E1", "T-A", ""), "accepted": False,
             "attempt_receipt_id": "attempt-1", "exchange_created_ts": None},
            order("E1", "T-B", "o2"),
        ]
        summary, mismatches = validate_replay(
            ledger, attempts, [], [], [book("T-B", 9, 3)])
        self.assertFalse(summary["gate_pass"])
        self.assertEqual(summary["failed_attempts_compared"], 1)
        self.assertEqual(summary["matched_failed_attempts"], 0)
        self.assertTrue(any(row["mismatch_type"] == "clock"
                            for row in mismatches))

    def test_gate_matches_one_fill_and_one_nonfill(self):
        events = [{"event_id": "E1", "category": "ATP_MAIN",
                   "event_date": "2026-07-12", "legs": ["T-A", "T-B"]}]
        ledger, _ = build_event_ledger(events)
        orders = [order("E1", "T-A", "o1"), order("E1", "T-B", "o2")]
        fills = [{"fill_id": "f1", "order_id": "o1", "ticker": "T-A",
                  "price_cents": 40, "quantity": 5, "exchange_ts": 12}]
        raw_prints = [true_print("r1", "T-A", 12, 8),
                      true_print("r2", "T-B", 12, 2)]
        prints, errors = canonical_true_prints(raw_prints)
        self.assertEqual(errors, [])
        books = [book("T-A", 9, 3), book("T-B", 9, 3)]
        summary, mismatches = validate_replay(
            ledger, orders, fills, prints, books)
        self.assertTrue(summary["gate_pass"])
        self.assertEqual(summary["matched_fills"], 1)
        self.assertEqual(summary["matched_nonfills"], 1)
        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
