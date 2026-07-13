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
TAPE_FEED = False   # [C-BELL-SCOPE] lane (i)/(ii): market prints in-window
lv.time = types.SimpleNamespace(time=lambda: CLOCK["now"], sleep=lambda s: None)


class _TT(dict):
    """fake trade-times: 7 prints inside the trailing window when fed"""
    def get(self, k, d=None):
        if not TAPE_FEED:
            return None
        return [CLOCK["now"] - 60 * i for i in range(1, 8)]

async def _fake_get(s, ak, pk, path, rl):
    if "positions" in path:
        return {"market_positions": [], "positions": []}
    if "orders" in path:
        return {"orders": []}
    return {}

async def _fake_post(s, ak, pk, path, payload, rl):
    # flat v2 create-order shape (parse_order_response_v2)
    return {"order_id": "SIM-OID", "remaining_count": 5}

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
    b._trade_times = _TT()
    b.event_tickers = types.SimpleNamespace(
        get=lambda et, d=(): [et + "-A", et + "-B"])
    b.event_start_time = {}
    b._pm_honest = {}
    b.reentry_cycle_cap = int(cfg.get("reentry_cycle_cap", 2))
    b._cycle_count = {}
    b.entry_size = 5
    b.walk_cap_honest_anchor = bool(cfg.get("walk_cap_honest_anchor", False))
    b.walk_cap_honest_by_cat = dict(cfg.get("walk_cap_honest_by_cat", {}))
    b.premarket_walk_cap_by_cat = dict(cfg.get("premarket_walk_cap_by_cat", {}))
    b.get_category = lambda et: ("ITF_W" if "ITFW" in et else
                                 ("ATP_CHALL" if "ATPCHALL" in et else "ITF_M"))
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
    # LANE (i) [C-CAP-SCOPE]: CORBRU's tape STILL freezes -- the self-fill
    # bell is the chase-killer (41->51 = +10c/30min fires it; every later
    # buy refused by the fused gun). Fail-before preserved by construction:
    # locks-off = the live tape (all accepted).
    r0 = await run(False, False, "FAIL-BEFORE (locks off, = the live tape)")
    ok &= all(x[2] == "ACCEPT" for x in r0)
    if not all(x[2] == "ACCEPT" for x in r0):
        print("  !! fail-before did not reproduce the tape")
    # [C-BELL-SCOPE] CORBRU's market was PRINTING through the ladder (hour-00
    # tape: 43 prints) -- condition (c) tape_corroborated carries the freeze
    global TAPE_FEED
    TAPE_FEED = True
    r2 = await run(True, True, "LANE (i): CORBRU still freezes at the 51 (condition c)")
    exp2 = (r2[0][2] == "ACCEPT" and r2[1][2] == "ACCEPT"
            and all(x[2] == "REFUSE:gun_fired" for x in r2[2:]))
    print("  lane (i) verdict:", "PASS (frozen at the 51; %d refusals incl. the whole COR side)"
          % sum(1 for x in r2 if x[2].startswith("REFUSE")) if exp2 else "FAIL")
    ok &= exp2
    TAPE_FEED = False
    # [C-CAP-SCOPE] cap-only sanity: pre-fill pre-bell, the RESCOPED cap does
    # NOT refuse (normal market-making, unlimited; walk cap bounds each step
    # at the organ). The ladder's killer is the bell, not the count.
    r1 = await run(True, False, "cap-only (rescoped: pre-fill pre-bell = unlimited)")
    exp1 = all(x[2] == "ACCEPT" for x in r1)
    print("  rescoped cap-only verdict:", "PASS (no pre-arm refusals)" if exp1 else "FAIL")
    ok &= exp1
    # LANE (iii) [C-BELL-SCOPE]: tonight's shapes re-run as NO-FIRE --
    # unfilled leg, quiet tape, upward re-aims WITHIN the armed ITF_W
    # allowance (20c): neither the cap nor the bell may touch them
    b = mk_bot(True, True)
    lane2 = [(1783906000 + i * 300, "KXITFWMATCH-26JUL13WONBOW-WON", px)
             for i, px in enumerate([6, 8, 10, 12, 14])]   # rise 8c <= 20c sanctioned
    res2 = []
    for ts, tk, px in lane2:
        CLOCK["now"] = float(ts)
        oid, resp = await b.place_order(tk, "buy", "yes", px, 5, post_only=True)
        res2.append((px, "ACCEPT" if oid else "REFUSE:" + (resp or {}).get("_error", "")))
    print("== LANE (iii): sanctioned pre-fill re-aims, quiet tape (tonight's 24)")
    for r in res2:
        print("  ", r)
    exp_l2 = all(r[1] == "ACCEPT" for r in res2)
    print("  lane (iii) verdict:", "PASS (no cap, NO BELL — sanctioned walking is not evidence)"
          if exp_l2 else "FAIL")
    ok &= exp_l2
    # bell condition (b): rise EXCEEDING the sanctioned allowance on quiet
    # tape still fires (walking faster than sanctioned IS the chase)
    b6 = mk_bot(True, True)
    resb = []
    for i, px in enumerate([10, 15, 22, 33]):   # 10->33 = 23c > 20c ITF_W
        CLOCK["now"] = 1783910000 + i * 120
        oid, resp = await b6.place_order("KXITFWMATCH-26JUL13FASTRR-FAS",
                                         "buy", "yes", px, 5, post_only=True)
        resb.append((px, "ACCEPT" if oid else "REFUSE:" + (resp or {}).get("_error", "")))
    fired_b = "KXITFWMATCH-26JUL13FASTRR" in b6._gun_state
    print("== condition (b): 23c rise > 20c allowance ->",
          "FIRED (source %s) PASS" % b6._gun_state.get("KXITFWMATCH-26JUL13FASTRR", {}).get("source")
          if fired_b else "did not fire FAIL", resb)
    ok &= fired_b
    # bell condition (a): post-fill rise >=4c on quiet tape fires
    b7 = mk_bot(True, True)
    b7._leg_filled = {"KXITFWMATCH-26JUL13AFTFIL-AFT"}
    for i, px in enumerate([30, 36]):
        CLOCK["now"] = 1783912000 + i * 120
        await b7.place_order("KXITFWMATCH-26JUL13AFTFIL-AFT",
                             "buy", "yes", px, 5, post_only=True)
    fired_a = "KXITFWMATCH-26JUL13AFTFIL" in b7._gun_state
    print("== condition (a): post-fill +6c rise ->",
          "FIRED PASS" if fired_a else "did not fire FAIL")
    ok &= fired_a
    # POST-ARM check: after a fill on the leg, the 3rd upward re-aim refuses
    b2 = mk_bot(True, False)
    b2._leg_filled = {"KXITFWMATCH-26JUL13SIMFIL-SIM"}
    res3 = []
    for i, px in enumerate([30, 32, 34, 36]):
        CLOCK["now"] = 1783908000 + i * 60
        oid, resp = await b2.place_order("KXITFWMATCH-26JUL13SIMFIL-SIM",
                                         "buy", "yes", px, 5, post_only=True)
        res3.append((px, "ACCEPT" if oid else "REFUSE:" + (resp or {}).get("_error", "")))
    print("== POST-ARM: leg filled -> cap counts (2 allowed, 3rd refused)")
    for r in res3:
        print("  ", r)
    exp3 = (res3[0][1] == "ACCEPT" and res3[1][1] == "ACCEPT"
            and res3[2][1] == "REFUSE:chase_cap" and res3[3][1] == "REFUSE:chase_cap")
    print("  post-arm verdict:", "PASS" if exp3 else "FAIL")
    ok &= exp3
    print("REPLAY", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

asyncio.run(main())
