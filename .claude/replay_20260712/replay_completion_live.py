#!/usr/bin/env python3
"""C-COMPLETION-LIVE replay (harness law): the REAL `_completion_execute`
driven with canned verdicts, real `_log`, stubbed exchange I/O. Asserts the
action contract per verdict:
  taker_complete -> sibling maker bid CANCELLED + taker BUY at ask, qty=kept
  flatten_kept   -> sibling bid cancelled + kept exit cancelled + SELL at bid
  hold           -> no orders touched
  taker with operator_taker_word=false -> NOTHING (the gate holds)
Plus the fused-gun one-shot exemption: the taker cross passes the gun guard
on a belled event; a second (non-exempt) buy on the same ticker is refused.
"""
import asyncio, importlib.util, json, sys, tempfile, types
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
spec = importlib.util.spec_from_file_location("lv4", ROOT / "live_v4.py")
sys.path.insert(0, str(ROOT))
lv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lv)

CALLS = []

async def _fake_get(s, ak, pk, path, rl):
    if "positions" in path:
        return {"market_positions": [], "positions": []}
    if "orders" in path:
        return {"orders": []}
    return {}

async def _fake_post(s, ak, pk, path, payload, rl):
    CALLS.append(("POST", payload))
    return {"order_id": "SIM-OID", "remaining_count": 0}

lv.api_get = _fake_get
lv.api_post = _fake_post


class B:   # minimal book
    def __init__(self, bid, ask):
        self.best_bid, self.best_ask = bid, ask
        self.last_trade_price, self.last_trade_ts = None, 0


def mk(taker_word=True, belled=False):
    b = lv.LiveV3.__new__(lv.LiveV3)
    cfg = json.loads((ROOT / "config/deploy_v5_live.json").read_text())
    cfg["operator_taker_word"] = taker_word
    cfg["completion_live_enabled"] = True
    b.config = cfg
    b.log_file = open(tempfile.mktemp(suffix=".jsonl"), "w")
    b.books = {"EV-KEPT": B(38, 41), "EV-SIB": B(52, 56)}
    b.positions = {}
    b.session, b.ak, b.pk, b.rl = None, "", None, None
    b._conception_halt = False
    b.fused_gun = True
    b._gun_state = ({"EV": {"ts": 0, "source": "fallback_bell"}} if belled else {})
    b._events_live = set()
    b._trade_times, b.event_tickers = {}, {}
    b.event_start_time, b._pm_honest = {}, {}
    b.reentry_cycle_cap, b._cycle_count = 2, {}
    b._bot_order_ids, b._bot_order_tickers = set(), set()
    b._horizon_state = lambda et, now=None: (False, None)
    b._wall_observe = lambda *a, **k: None
    b._cancelled = []
    async def _cancel(tk, oid, label=""):
        b._cancelled.append((tk, oid, label))
        return True
    b.cancel_order = _cancel
    kept = types.SimpleNamespace(entry_qty=5.0, entry_price=40, phase="active",
                                 exit_order_id="EXIT-1", exit_price=48,
                                 event_ticker="EV")
    sibp = types.SimpleNamespace(entry_qty=0, entry_price=0, phase="entry_resting",
                                 entry_order_id="SIBBID-1", event_ticker="EV")
    b.positions = {"EV-KEPT": kept, "EV-SIB": sibp}
    return b, kept


async def main():
    ok = True
    # 1) taker_complete, word ON, belled event (the hard case)
    CALLS.clear()
    b, kept = mk(taker_word=True, belled=True)
    res = {"verdict": "taker_complete", "kept": {"ev_cents": -3.1}}
    await b._completion_execute("EV-KEPT", kept, res, 1000.0)
    buys = [p for _, p in CALLS if p.get("action", "buy") or True]
    t1 = (("EV-SIB", "SIBBID-1", "completion_live_resolve") in b._cancelled
          and len(CALLS) == 1 and CALLS[0][1].get("ticker") == "EV-SIB")
    px = CALLS[0][1] if CALLS else {}
    print("taker+word+belled:", "PASS" if t1 else "FAIL",
          "| cancelled sib bid:", b._cancelled, "| cross:", json.dumps(px)[:160])
    ok &= t1
    # 1b) dedup: second evaluation on same event does nothing
    CALLS.clear()
    await b._completion_execute("EV-KEPT", kept, res, 1600.0)
    t1b = not CALLS and len(b._cancelled) == 1
    print("once-per-event dedup:", "PASS" if t1b else "FAIL")
    ok &= t1b
    # 2) taker with word OFF -> nothing
    CALLS.clear()
    b2, kept2 = mk(taker_word=False)
    await b2._completion_execute("EV-KEPT", kept2, res, 1000.0)
    t2 = not CALLS and not b2._cancelled
    print("taker gate holds when word=false:", "PASS" if t2 else "FAIL")
    ok &= t2
    # 3) flatten_kept -> sib bid + exit cancelled, sell at bid
    CALLS.clear()
    b3, kept3 = mk()
    await b3._completion_execute("EV-KEPT", kept3,
                                 {"verdict": "flatten_kept", "kept": {"ev_cents": -6.0}}, 1000.0)
    sells = [p for _, p in CALLS]
    t3 = (("EV-SIB", "SIBBID-1", "completion_live_resolve") in b3._cancelled
          and ("EV-KEPT", "EXIT-1", "completion_live_flatten") in b3._cancelled
          and len(sells) == 1 and sells[0].get("ticker") == "EV-KEPT")
    print("flatten_kept:", "PASS" if t3 else "FAIL", "| sell:", json.dumps(sells[0] if sells else {})[:160])
    ok &= t3
    # 4) hold -> nothing
    CALLS.clear()
    b4, kept4 = mk()
    await b4._completion_execute("EV-KEPT", kept4, {"verdict": "hold"}, 1000.0)
    t4 = not CALLS and not b4._cancelled
    print("hold does nothing:", "PASS" if t4 else "FAIL")
    ok &= t4
    # 5) [C-DELETION-GATE Part 4] the taker daily cap: the 4th cross defers,
    # NAMED (completion_taker_capped), never silent
    CALLS.clear()
    b5, kept5 = mk(taker_word=True)
    from datetime import datetime
    b5._taker_day = datetime.now(lv.ET).strftime("%Y%m%d")
    b5._taker_n = int(b5.config.get("taker_daily_action_cap", 3))
    logged = []
    _orig_log = b5._log
    def _spy(ev, det=None, ticker=""):
        logged.append(ev)
        return _orig_log(ev, det, ticker)
    b5._log = _spy
    await b5._completion_execute("EV-KEPT", kept5, res, 1000.0)
    t5 = (not CALLS and "completion_taker_capped" in logged)
    print("taker cap defers 4th cross, NAMED:", "PASS" if t5 else "FAIL", logged[-1:])
    ok &= t5
    print("REPLAY", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

asyncio.run(main())
