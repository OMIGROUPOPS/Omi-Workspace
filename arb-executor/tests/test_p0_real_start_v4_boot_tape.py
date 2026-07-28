"""Production-path tests for P0 REAL-START v4 fresh-boot tape barrier.

All exchange responses are synthetic. No network or live-account method is
reachable from this module.
"""
import asyncio
import ast
import hashlib
import inspect
import json
import os
import sys
import time
import types
import unittest
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import live_v4 as M


SHICHA = "KXITFMATCH-26JUL27SHICHA"
SHI = SHICHA + "-SHI"
CHA = SHICHA + "-CHA"


def iso(epoch):
    return datetime.fromtimestamp(
        epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def trades(ticker, count, now, start=0, price=79, prefix="T"):
    """Newest-first public executions, all inside the frozen 30-minute law."""
    return [{
        "trade_id": "%s-%s-%04d" % (prefix, ticker[-3:], start + i),
        "ticker": ticker,
        "created_time": iso(now - (start + i + 1)),
        "yes_price_dollars": "%.2f" % (price / 100.0),
        "count_fp": "1.00",
        "taker_side": "no",
    } for i in range(count)]


class TapeAPI:
    def __init__(self, rows_by_ticker, fail_page=None):
        self.rows = rows_by_ticker
        self.fail_page = fail_page
        self.calls = []

    async def get(self, session, ak, pk, path, rl):
        self.calls.append(path)
        parsed = urlparse(path)
        q = parse_qs(parsed.query)
        ticker = q["ticker"][0]
        cursor = q.get("cursor", ["0"])[0]
        page = int(cursor[1:]) if cursor.startswith("p") else 0
        if self.fail_page == (ticker, page):
            return None
        limit = int(q.get("limit", ["100"])[0])
        rows = self.rows.get(ticker, [])
        chunk = rows[page * limit:(page + 1) * limit]
        nxt = ("p%d" % (page + 1)
               if (page + 1) * limit < len(rows) else "")
        return {"trades": [dict(r) for r in chunk], "cursor": nxt}


def make_bot(event=SHICHA, tickers=(SHI, CHA), now=None):
    now = time.time() if now is None else now
    b = M.LiveV3.__new__(M.LiveV3)
    b.logs = []
    b._log = lambda ev, detail=None, ticker="": b.logs.append(
        (ev, detail or {}, ticker))
    b.session = b.ak = b.pk = b.rl = None
    b.config = {
        "tape_flow_prints30": {
            "ITF_M": 6, "ITF_W": 6,
            "ATP_CHALL": 16, "WTA_CHALL": 16,
            "ATP_MAIN": 16, "WTA_MAIN": 16,
        },
        "sizing": {"entry_contracts": 5},
        "self_fill_bell_enabled": False,
        "expiration_wire_enabled": False,
    }
    b.event_tickers = defaultdict(set)
    b.event_tickers[event].update(tickers)
    b.ticker_to_event = {t: event for t in tickers}
    b.ticker_category = {t: "ITF_M" for t in tickers}
    b.get_category = lambda value: "ITF_M"
    b.event_start_time = {event: now + 2 * 3600 + 44 * 60}
    b._pm_honest = {}
    b._gun_state = {}
    b._events_live = set()
    b._start_conflict = set()
    b._gun_void_pending = {}
    b._gun_void_logged = set()
    b._trade_times = defaultdict(list)
    b.positions = {}
    b.unmatched_holdings = {}
    b.books = {}
    b.processed_events = set()
    b._boot_tape_state = {
        event: {
            "state": M.P0_BOOT_TAPE_PENDING,
            "updated_ts": now,
            "reason": "fixture",
        }}
    b._boot_tape_ticker_state = {}
    b._boot_tape_tasks = {}
    b._boot_tape_hydration_enabled = True
    b._boot_tape_semaphore = asyncio.Semaphore(8)
    b._boot_tape_boot_started_ts = now - 1
    b._boot_tape_stats = {
        "events_evaluated": 0, "tape_rows_read": 0,
        "admitted": 0, "deduplicated": 0, "rejected": 0,
        "duration_ms": 0.0,
    }
    b._horizon_state = lambda et, now=None: (False, 0)
    b._conception_halt = False
    b.fused_gun = False
    b._completion_cross_allow = set()
    b._save_v4_resting = lambda: None
    b._untombstone_entry = lambda tk, pos: b.positions.pop(tk, None)
    b._fv_burst = {}
    b.event_start_source = {event: "kalshi_primary"}
    b._inflight_locks = {}
    b._bot_order_ids = set()
    b._bot_order_tickers = set()
    b._bot_order_action = {}
    b.n_entries = 0

    async def sweep(et, source):
        b.sweeps = getattr(b, "sweeps", [])
        b.sweeps.append((et, source))
    b._gun_sweep_entry_bids = sweep
    return b


async def hydrate_with(bot, api, now):
    with patch.object(M, "api_get", api.get):
        bot._p0v4_transition(
            SHICHA, M.P0_BOOT_TAPE_EVALUATING, "fixture",
            {"evaluation_ts": now})
        return await bot._p0v4_hydrate_event_inner(SHICHA, now)


class P0V4BootTapeTests(unittest.IsolatedAsyncioTestCase):
    async def test_shicha_pending_hydrates_real_start_before_post(self):
        now = time.time()
        b = make_bot(now=now)
        posted = []

        async def no_post(*args, **kwargs):
            posted.append((args, kwargs))
            return {"order": {"order_id": "UNLAWFUL"}}

        # Production chokepoint refuses SHI 5@79 while boot tape is pending.
        with patch.object(M, "api_post", no_post):
            oid, response = await b._place_order_unlocked(
                SHI, "buy", "yes", 79, 5, post_only=True)
        self.assertEqual("", oid)
        self.assertEqual("post_start_entry_refused",
                         response.get("_error"))
        self.assertEqual([], posted)
        self.assertEqual(
            (True, "boot_tape_not_ready"),
            b._p0v4_entry_authority_gate(SHICHA))

        rows = {SHI: trades(SHI, 651, now, price=79), CHA: []}
        receipt = await hydrate_with(b, TapeAPI(rows), now)
        await asyncio.sleep(0)
        self.assertEqual(651, receipt["admitted"])
        self.assertTrue(receipt["predicate_result"])
        self.assertEqual(
            M.P0_BOOT_TAPE_REAL_START,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual(
            receipt["source_sha256"],
            b._boot_tape_state[SHICHA]["receipt"]["source_sha256"])
        self.assertIn(SHICHA, b._events_live)
        self.assertIn(SHICHA, b._start_conflict)
        self.assertEqual(
            (True, "real_start_tape_override"),
            b._p0v4_entry_authority_gate(SHICHA))
        self.assertEqual([(SHICHA, "boot_historical_tape")], b.sweeps)
        self.assertEqual([], posted, "SHI 5@79 was never submitted")
        self.assertTrue(any(e == "sched_liar_override" for e, _, _ in b.logs))

    async def test_legitimate_future_insufficient_defers_to_existing_law(self):
        now = time.time()
        b = make_bot(now=now)
        receipt = await hydrate_with(
            b, TapeAPI({SHI: trades(SHI, 8, now), CHA: []}), now)
        self.assertFalse(receipt["predicate_result"])
        self.assertEqual(
            M.P0_BOOT_TAPE_INSUFFICIENT,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual((False, ""), b._p0v4_entry_authority_gate(SHICHA))

    async def test_missing_schedule_insufficient_does_not_fabricate_start(self):
        now = time.time()
        b = make_bot(now=now)
        b.event_start_time.clear()
        await hydrate_with(
            b, TapeAPI({SHI: trades(SHI, 1, now), CHA: []}), now)
        self.assertEqual(
            M.P0_BOOT_TAPE_INSUFFICIENT,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual(
            (True, "unknown_start"),
            b._p0v4_entry_authority_gate(SHICHA))
        self.assertNotIn(SHICHA, b._events_live)

    async def test_tape_unavailable_is_no_call_entries_blocked(self):
        now = time.time()
        b = make_bot(now=now)
        with patch.object(M, "api_get", TapeAPI(
                {SHI: [], CHA: []}, fail_page=(SHI, 0)).get):
            await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual(
            (True, "boot_tape_no_call"),
            b._p0v4_entry_authority_gate(SHICHA))

    async def test_partial_paginated_failure_never_authorizes(self):
        now = time.time()
        b = make_bot(now=now)
        rows = {SHI: trades(SHI, 150, now), CHA: []}
        with patch.object(M, "api_get", TapeAPI(
                rows, fail_page=(SHI, 1)).get):
            await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])

    async def test_duplicate_prints_deduplicate_without_double_count(self):
        now = time.time()
        b = make_bot(now=now)
        one = trades(SHI, 1, now)[0]
        receipt = await hydrate_with(
            b, TapeAPI({SHI: [one, dict(one)], CHA: []}), now)
        self.assertEqual(2, receipt["raw_rows"])
        self.assertEqual(1, receipt["admitted"])
        self.assertEqual(1, receipt["deduplicated"])

    async def test_carried_last_trade_without_receipt_is_excluded(self):
        now = time.time()
        b = make_bot(now=now)
        bad = trades(SHI, 1, now)[0]
        bad.pop("trade_id")
        with patch.object(
                M, "api_get", TapeAPI({SHI: [bad], CHA: []}).get):
            await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        self.assertIn(
            "missing_trade_id",
            b._boot_tape_state[SHICHA]["receipt"]["detail"])

    async def test_wrong_sibling_identity_is_excluded(self):
        now = time.time()
        b = make_bot(now=now)
        wrong = trades(CHA, 1, now)[0]
        with patch.object(
                M, "api_get", TapeAPI({SHI: [wrong], CHA: []}).get):
            await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        self.assertIn(
            "wrong_ticker",
            b._boot_tape_state[SHICHA]["receipt"]["detail"])

    async def test_future_print_is_excluded(self):
        now = time.time()
        b = make_bot(now=now)
        future = trades(SHI, 1, now)[0]
        future["created_time"] = iso(now + 1)
        receipt = await hydrate_with(
            b, TapeAPI({SHI: [future], CHA: []}), now)
        self.assertEqual(0, receipt["admitted"])
        self.assertEqual(1, receipt["rejected"]["future_print"])

    async def test_bbo_routing_before_hydration_is_blocked(self):
        b = make_bot()
        b._event_routing = set()
        await b._route_event(SHICHA, [SHI, CHA], time.time())
        self.assertTrue(any(
            event == "boot_tape_route_refused" and
            detail.get("reason") == "boot_tape_not_ready"
            for event, detail, _ in b.logs))
        self.assertNotIn(SHICHA, b._event_routing)

    async def test_exit_sell_remains_live_while_tape_pending(self):
        b = make_bot()
        posts = []

        async def post(session, ak, pk, path, payload, rl):
            posts.append(payload)
            return {"order_id": "EXIT-1", "status": "resting"}

        with patch.object(M, "api_post", post):
            oid, response = await b._place_order_unlocked(
                SHI, "sell", "yes", 98, 5, post_only=True)
        self.assertEqual("EXIT-1", oid)
        self.assertEqual("resting", response["status"])
        self.assertEqual(1, len(posts))
        self.assertEqual(SHI, posts[0]["ticker"])

    async def test_stale_intent_revalidated_immediately_before_post(self):
        """First gate passes; exchange-truth await fires REAL_START; POST stops."""
        now = time.time()
        b = make_bot(now=now)
        b._p0v4_transition(
            SHICHA, M.P0_BOOT_TAPE_INSUFFICIENT, "complete", {})
        calls = []

        async def get_and_fire(session, ak, pk, path, rl):
            calls.append(path)
            if len(calls) == 1:
                b._p0v4_mark_real_start(
                    SHICHA, "simultaneous_gun", {"fixture": True})
            if "/positions" in path:
                return {"market_positions": []}
            if "/orders" in path:
                return {"orders": []}
            return {}

        async def forbidden_post(*args, **kwargs):
            raise AssertionError("stale intent reached api_post")

        with patch.object(M, "api_get", get_and_fire), \
                patch.object(M, "api_post", forbidden_post):
            oid, response = await b._place_order_unlocked(
                SHI, "buy", "yes", 79, 5, post_only=True)
        self.assertEqual("", oid)
        self.assertEqual("p0v4_pre_post_refused", response.get("_error"))
        self.assertEqual("real_start_tape_override",
                         response.get("_reason"))

    async def test_simultaneous_gun_and_boot_converge_one_real_start(self):
        now = time.time()
        b = make_bot(now=now)
        detail = {"prints_30m": 10, "threshold": 6}
        self.assertTrue(b._gun_stamp(
            SHICHA, "boot_historical_tape", detail))
        self.assertFalse(b._gun_stamp(
            SHICHA, "tape_flow", detail))
        await asyncio.sleep(0)
        self.assertEqual(
            M.P0_BOOT_TAPE_REAL_START,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual(1, sum(
            e == "boot_tape_real_start" for e, _, _ in b.logs))
        self.assertEqual(1, len(b._gun_state))

    async def test_existing_resting_entry_swept_once_and_never_reposted(self):
        b = make_bot()
        pos = types.SimpleNamespace(
            entry_order_id="ENTRY-1", event_ticker=SHICHA)
        b.positions[SHI] = pos
        cancel_calls = []

        async def cancel(ticker, position, cancel_reason, race_reason):
            cancel_calls.append(
                (ticker, position.entry_order_id, cancel_reason, race_reason))
            return "cancelled"

        b._cancel_entry_and_resolve = cancel
        b._gun_sweep_entry_bids = types.MethodType(
            M.LiveV3._gun_sweep_entry_bids, b)
        b._p0v4_mark_real_start(
            SHICHA, "boot_historical_tape", {"fixture": True})
        await b._gun_sweep_entry_bids(
            SHICHA, "boot_historical_tape")
        await b._gun_sweep_entry_bids(
            SHICHA, "boot_historical_tape")
        self.assertEqual(1, len(cancel_calls))
        self.assertNotIn(SHI, b.positions)
        self.assertFalse(any(e == "order_placed" for e, _, _ in b.logs))

    def test_persistent_real_start_has_no_restart_entry_window(self):
        b = make_bot()
        b._gun_state[SHICHA] = {
            "ts": time.time() - 60, "source": "tape_flow"}
        b._p0v4_adopt_persistent_real_starts()
        self.assertEqual(
            (True, "real_start_tape_override"),
            b._p0v4_entry_authority_gate(SHICHA))

    async def test_multiple_events_are_isolated(self):
        now = time.time()
        second = "KXITFMATCH-26JUL27LEGIT"
        leg = second + "-LEG"
        b = make_bot(now=now)
        b.event_tickers[second] = {leg}
        b.ticker_to_event[leg] = second
        b.event_start_time[second] = now + 3600
        b._boot_tape_state[second] = {
            "state": M.P0_BOOT_TAPE_PENDING,
            "updated_ts": now, "reason": "fixture"}
        api = TapeAPI({
            SHI: trades(SHI, 12, now), CHA: [],
            leg: trades(leg, 1, now, prefix="L")})
        with patch.object(M, "api_get", api.get):
            b._p0v4_transition(
                SHICHA, M.P0_BOOT_TAPE_EVALUATING, "fixture", {})
            await b._p0v4_hydrate_event_inner(SHICHA, now)
            b._p0v4_transition(
                second, M.P0_BOOT_TAPE_EVALUATING, "fixture", {})
            await b._p0v4_hydrate_event_inner(second, now)
        self.assertEqual(
            M.P0_BOOT_TAPE_REAL_START,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual(
            M.P0_BOOT_TAPE_INSUFFICIENT,
            b._boot_tape_state[second]["state"])

    async def test_hydration_exception_blocks_only_entries(self):
        b = make_bot()

        async def fail(*args, **kwargs):
            raise RuntimeError("synthetic_timeout")
        b._p0v4_hydrate_event_inner = fail
        await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        # Exit code paths never call the entry authority gate.
        source = inspect.getsource(M.LiveV3._place_order_unlocked)
        self.assertIn('if action == "buy":', source)
        self.assertNotIn('if action == "sell":\n            _refuse',
                         source)

    async def test_hydration_timeout_is_no_call(self):
        b = make_bot()

        async def slow(*args, **kwargs):
            await asyncio.sleep(0.05)
        b._p0v4_hydrate_event_inner = slow
        with patch.object(M, "INFLIGHT_LOCK_TIMEOUT_SEC", 0.001):
            await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual(
            "TimeoutError",
            b._boot_tape_state[SHICHA]["receipt"]["error"])

    async def test_pagination_ceiling_is_no_call_not_partial_allow(self):
        now = time.time()
        b = make_bot(now=now)
        rows = {SHI: trades(SHI, 1001, now, price=79), CHA: []}
        with patch.object(M, "api_get", TapeAPI(rows).get):
            await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        self.assertIn(
            "pagination_ceiling",
            b._boot_tape_state[SHICHA]["receipt"]["detail"])

    async def test_source_order_ambiguity_is_no_call(self):
        now = time.time()
        b = make_bot(now=now)
        rows = trades(SHI, 2, now)
        rows.reverse()  # oldest first violates authoritative newest-first law
        with patch.object(
                M, "api_get", TapeAPI({SHI: rows, CHA: []}).get):
            await b._p0v4_hydrate_event(SHICHA)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        self.assertIn(
            "source_order_ambiguous",
            b._boot_tape_state[SHICHA]["receipt"]["detail"])

    def test_processed_market_is_not_hydrated(self):
        b = make_bot()
        b.processed_events.add(SHICHA)
        b._p0v4_schedule_pending_hydration()
        self.assertNotIn(SHICHA, b._boot_tape_tasks)
        self.assertEqual(
            M.P0_BOOT_TAPE_NO_CALL,
            b._boot_tape_state[SHICHA]["state"])
        self.assertEqual(
            "processed_or_determined_event_not_hydrated",
            b._boot_tape_state[SHICHA]["reason"])

    def test_entry_post_callsite_and_boot_order_census(self):
        src = inspect.getsource(M.LiveV3)
        tree = ast.parse(src)
        api_posts = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "api_post"]
        self.assertEqual(1, len(api_posts),
                         "one exchange POST chokepoint in LiveV3")
        place = inspect.getsource(M.LiveV3._place_order_unlocked)
        self.assertGreaterEqual(
            place.count("_p0v4_entry_authority_gate"), 2,
            "decision gate plus immediate pre-POST revalidation")
        route = inspect.getsource(M.LiveV3._route_event)
        self.assertIn("_p0v4_entry_authority_gate", route)
        run = inspect.getsource(M.LiveV3.run)
        self.assertLess(
            run.index("_p0v4_schedule_pending_hydration"),
            run.index("asyncio.create_task(self.ws_reader())"))

    async def test_same_tape_is_deterministic_and_idempotent(self):
        now = time.time()
        rows = {SHI: trades(SHI, 8, now), CHA: []}
        receipts = []
        for _ in range(2):
            b = make_bot(now=now)
            receipt = await hydrate_with(b, TapeAPI(rows), now)
            receipts.append(json.dumps(
                receipt, sort_keys=True, separators=(",", ":")))
        self.assertEqual(receipts[0], receipts[1])
        self.assertEqual(
            hashlib.sha256(receipts[0].encode()).hexdigest(),
            hashlib.sha256(receipts[1].encode()).hexdigest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
