#!/usr/bin/env python3
"""C-CHASE-KILL replay (harness law): CORBRU's recorded ladder driven through
the REAL chokepoint (`_place_order_unlocked` guard stack, real `_log`, real
`_gun_stamp`) with only I/O stubbed (api_get/api_post canned, log to temp,
module clock = the tape's own timestamps).

FAIL-BEFORE: locks disabled (yesterday's config) -> all 14 BRU rungs accepted,
both COR rungs accepted (matches the live tape: chase ran 1:00-2:43 am).
PASS-AFTER (cap only): rungs 1-2 accepted, rungs 3-14 chase_cap_refused --
"fills three through six REFUSED" and everything after them.
PASS-AFTER (both locks): rung 1 (41) accepted; rung 2 (51) fires the
self-fill bell (+10c < 30min) and is allowed through as the evidence; rungs
3-14 AND the COR side refused via the gun guard (source self_fill) -- the
event frozen at the 51, 3+ hours of chase refused.
"""
import asyncio, importlib.util, json, sys, tempfile, types
from pathlib import Path

ROOT = Path("/root/Omi-Workspace/arb-executor")
spec = importlib.util.spec_from_file_location("lv4", ROOT / "live_v4.py")
sys.path.insert(0, str(ROOT))
lv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lv)

# ---- the tape (recorded order_placed buys, live_v3_20260711.jsonl 07-12) ----
BRU = "KXITFWMATCH-26JUL12CORBRU-BRU"
COR = "KXITFWMATCH-26JUL12CORBRU-COR"
LADDER = [  # (epoch, ticker, price) -- placements as recorded
    (1783832444, BRU, 41), (1783832445, BRU, 51), (1783834590, BRU, 52),
    (1783834764, BRU, 52), (1783834884, BRU, 53), (1783835032, BRU, 54),
    (1783837009, BRU, 55), (1783837121, BRU, 57), (1783837225, BRU, 58),
    (1783837398, BRU, 59), (1783837489, BRU, 60), (1783837610, BRU, 61),
    (1783837733, BRU, 63), (1783837856, BRU, 65),
    (1783837920, COR, 24), (1783837987, COR, 28), (1783838049, COR, 32),
]

CLOCK = {"now": 0.0}
lv.time = types.SimpleNamespace(time=lambda: CLOCK["now"], sleep=lambda s: None)

async def _fake_get(s, ak, pk, path, rl):
    if "positions" in path:
        return {"market_positions": [], "positions": []}
    if "orders" in path:
        return {"orders": []}
    return {}

async def _fake_post(s, ak, pk, path, payload, rl):
    return {"order": {"order_id": "SIM-OID", "status": "resting"}}

lv.api_get = _fake_get
lv.api_post = _fake_post


def mk_bot(chase_cap, bell):
    b = lv.LiveV3.__new__(lv.LiveV3)
    cfg = json.loads((ROOT / "config/deploy_v5_live.json").read_text())
    cfg["chase_pursuit_cap_enabled"] = chase_cap
    cfg["self_fill_bell_enabled"] = bell
    b.config = cfg
    b.log_file = open(tempfile.mktemp(suffix=".jsonl"), "w")
    b.books = {}
    b.positions = {}
    b.session, b.ak, b.pk, b.rl = None, "", None, None
    b._conception_halt = False
    b.fused_gun = True
    b._gun_state = {}
    b._events_live = set()
    b._trade_times = {}
    b.event_start_time = {}
    b._pm_honest = {}
    b.reentry_cycle_cap = int(cfg.get("reentry_cycle_cap", 2))
    b._cycle_count = {}
    b.entry_size = 5
    b._bot_order_ids = set()
    b._bot_order_tickers = set()
    # not-under-test helpers shadowed (horizon needs the pm-clock estate;
    # wall-observe needs book depth -- neither is the chokepoint under test)
    b._horizon_state = lambda et, now=None: (False, None)
    b._wall_observe = lambda *a, **k: None
    return b


async def run(chase_cap, bell, label):
    b = mk_bot(chase_cap, bell)
    results = []
    for ts, tk, px in LADDER:
        CLOCK["now"] = float(ts)
        oid, resp = await b.place_order(tk, "buy", "yes", px, 5, post_only=True)
        err = (resp or {}).get("_error", "")
        results.append((tk[-3:], px, "ACCEPT" if oid else "REFUSE:" + err))
    print("==", label)
    for r in results:
        print("  ", r)
    return results

async def main():
    ok = True
    # FAIL-BEFORE: yesterday's behavior
    r0 = await run(False, False, "FAIL-BEFORE (locks off, = the live tape)")
    ok &= all(x[2] == "ACCEPT" for x in r0)
    if not all(x[2] == "ACCEPT" for x in r0):
        print("  !! fail-before did not reproduce the tape")
    # PASS-AFTER, cap only: rungs 3+ refused
    r1 = await run(True, False, "PASS-AFTER cap-only")
    # cap is PER LEG: BRU rungs 1-2 accepted, 3-14 refused ("fills three
    # through six" and everything after them); COR's own first two accepted,
    # its third refused
    exp1 = (all(x[2] == "ACCEPT" for x in r1[:2])
            and all(x[2] == "REFUSE:chase_cap" for x in r1[2:14])
            and all(x[2] == "ACCEPT" for x in r1[14:16])
            and r1[16][2] == "REFUSE:chase_cap")
    print("  cap-only verdict:", "PASS" if exp1 else "FAIL")
    ok &= exp1
    # PASS-AFTER, both locks: freeze at the 51
    r2 = await run(True, True, "PASS-AFTER both locks (the dispatch's bar)")
    exp2 = (r2[0][2] == "ACCEPT" and r2[1][2] == "ACCEPT"
            and all(x[2] == "REFUSE:gun_fired" for x in r2[2:]))
    print("  both-locks verdict:", "PASS (frozen at the 51; %d refusals incl. the whole COR side)"
          % sum(1 for x in r2 if x[2].startswith("REFUSE")) if exp2 else "FAIL")
    ok &= exp2
    print("REPLAY", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

asyncio.run(main())
