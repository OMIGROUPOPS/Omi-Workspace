#!/usr/bin/env python3
"""T58 regression test — premarket maker entry: live running-mid anchor + per-cell
shallow-offset table, and clean interaction with T50/T51/T52.

Validates:
  (1) _running_mid = trailing-30m mean of last-traded price; sparse -> None;
      out-of-window prints excluded.
  (2) #1 ref-price: _v4_entry_anchor references the LAST-TRADED price (default,
      running_mid_anchor OFF) — last_traded inside a tight book / on any wide book,
      tight_mid when the print is outside a tight book, skip (None) when no fresh
      print, and the inert late_miss carve-out. running_mid_anchor ON = legacy
      running-mid + bbo_mid_fallback rollback path.
  (3) per-cell table is preferred, regime table is the fallback; target_bid =
      anchor_cell - per-cell offset.
  (4) the deployed per-cell offsets are SHALLOW + mirror-correct (== the T47
      regime offsets, no f x D argmax inflation).
  (5) clean interaction with T52 (fat-spread taker block) and T51 (match-live) —
      the anchor helper only computes the target; the guards gate independently.
  (6) captured-tape sanity: TIAARN (tight 50/51 flat book) and KESMAR (fat spread)
      both yield sane shallow bids; KESMAR's taker cross is blocked by T52.

Run: cd arb-executor && python3 tests/test_t58_premarket_entry.py
"""
import sys, types, csv, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M

fails = 0
def check(c, m):
    global fails
    print(("PASS " if c else "*** FAIL ") + m)
    fails += (0 if c else 1)


def make_bot():
    s = types.SimpleNamespace()
    s.running_mid_anchor = False     # #1 ref-price: default = last-traded path (ON = legacy rollback)
    s.maker_only_entry = True        # Stage 1: keeps the late_miss carve-out inert
    s._trade_prices = {}
    s.entry_table_cell = {}
    s.entry_table = {}
    for nm in ("_running_mid", "cell_lookup", "regime_lookup", "_v4_entry_anchor"):
        setattr(s, nm, types.MethodType(getattr(M.LiveV3, nm), s))
    return s


def book(bid, ask, last_trade=None, lt_age=5.0):
    # last_trade=None -> no fresh print (stale/absent); else a print at `last_trade`, `lt_age`s old.
    return types.SimpleNamespace(
        best_bid=bid, best_ask=ask,
        last_trade_price=(last_trade if last_trade is not None else 0),
        last_trade_ts=((time.time() - lt_age) if last_trade is not None else 0.0))


# ---- (1) running-mid ----
s = make_bot()
now = time.time()
s._trade_prices["TK"] = __import__("collections").deque(
    [(now - 60, 50), (now - 30, 51), (now - 5, 49)])
rm = s._running_mid("TK")
check(abs(rm - 50.0) < 1e-9, "running-mid = mean(50,51,49) = 50.0")
# out-of-window print (older than 30m) excluded
s._trade_prices["TK2"] = __import__("collections").deque(
    [(now - 4000, 10), (now - 10, 60), (now - 5, 60)])
check(abs(s._running_mid("TK2") - 60.0) < 1e-9, "out-of-window print (>30m) excluded -> mean(60,60)=60")
check(s._running_mid("EMPTY") is None, "no trades -> running-mid None (sparse)")

# ---- (2)/(3) #1 ref-price: last-traded reference — four-state matrix + per-cell table ----
FAR = 10 * 3600   # time_to_start well outside T-20m; late_miss never relevant in the matrix
s = make_bot()
s.entry_table_cell[("ATP_MAIN", 50)] = (120, 2, 0.66, 10.9)   # placement, offset, fill, roi
s.entry_table_cell[("ATP_MAIN", 40)] = (120, 3, 0.50, 8.0)
s.entry_table[("ATP_MAIN", "r45_54")] = (120, 9, 0.5, 5.0)    # regime row w/ DIFFERENT (deep) offset

# State 1: fresh print INSIDE the book -> last_traded (NOT the BBO mid, which is far at 60)
ent = s._v4_entry_anchor("A", "ATP_MAIN", book(55, 65, last_trade=50), FAR)
anchor, asrc, cell, regime, pmin, off, ef, er, tgt, tsrc = ent
check(asrc == "last_traded" and anchor == 50, "fresh in-spread print -> last_traded at 50 (not bbo mid 60)")
check(tsrc == "per_cell" and off == 2, "per-cell table preferred; shallow offset 2 (not regime's 9)")
check(tgt == anchor - 2, "target_bid = ref_cell - per-cell offset")

# State 2: tight book (49/51, spread 2), fresh print OUTSIDE the book (53) -> tight_mid at 50
entm = s._v4_entry_anchor("M", "ATP_MAIN", book(49, 51, last_trade=53), FAR)
check(entm[1] == "tight_mid" and entm[0] == 50, "tight book + print outside (53) -> tight_mid at mid 50")

# State 3: wide book (37/75, spread 38), fresh print 40 -> last_traded at 40 unconditionally
entw = s._v4_entry_anchor("W", "ATP_MAIN", book(37, 75, last_trade=40), FAR)
check(entw[1] == "last_traded" and entw[0] == 40, "wide book -> last_traded at 40 (mid ignored)")

# State 4: stale / absent print -> None (skip_no_trade); NO general BBO-mid fallback by design
check(s._v4_entry_anchor("S", "ATP_MAIN", book(48, 52, last_trade=50, lt_age=2000), FAR) is None,
      "stale print (>1800s) -> None (skip_no_trade)")
check(s._v4_entry_anchor("Z", "ATP_MAIN", book(48, 52), FAR) is None,
      "absent print -> None (skip_no_trade)")
check(s._v4_entry_anchor("S2", "ATP_MAIN", book(48, 52, last_trade=50, lt_age=5000), FAR) is None,
      "stale book does NOT fall back to bbo_mid (skip by design)")

# late_miss carve-out: inert under Stage 1, active only when taker is restored
check(s._v4_entry_anchor("L", "ATP_MAIN", book(48, 52, last_trade=50, lt_age=5000), 60) is None,
      "Stage 1: no fresh print inside T-20m -> still skip (late_miss gated off)")
s.maker_only_entry = False
entl = s._v4_entry_anchor("L", "ATP_MAIN", book(48, 52, last_trade=50, lt_age=5000), 60)
check(entl is not None and entl[1] == "late_miss" and entl[0] == 52,
      "taker restored: no fresh print inside T-20m -> late_miss returns current_ask (52)")
s.maker_only_entry = True

# regime fallback when per-cell row absent
s.entry_table_cell = {("ATP_MAIN", 99): (120, 1, 0.9, 7.0)}  # only c=99 present
entc = s._v4_entry_anchor("C", "ATP_MAIN", book(49, 51, last_trade=50), FAR)
check(entc[9] == "regime" and entc[5] == 9, "per-cell miss -> regime fallback")

# ROLLBACK: running_mid_anchor=True restores the legacy running-mid + bbo_mid_fallback path
r = make_bot(); r.running_mid_anchor = True
r.entry_table_cell[("ATP_MAIN", 50)] = (120, 2, 0.66, 10.9)
r.entry_table[("ATP_MAIN", "r45_54")] = (120, 9, 0.5, 5.0)
r._trade_prices["A"] = __import__("collections").deque([(now - 10, 50), (now - 5, 51)])
entr = r._v4_entry_anchor("A", "ATP_MAIN", book(55, 65, last_trade=99), FAR)  # last-traded ignored in rollback
check(entr[1] == "running_mid" and entr[0] in (50, 51), "ROLLBACK: running_mid (legacy), ignores last-traded")
r._trade_prices["B"] = __import__("collections").deque()
check(r._v4_entry_anchor("B", "ATP_MAIN", book(48, 52), FAR)[1] == "bbo_mid_fallback",
      "ROLLBACK: sparse trades -> bbo_mid_fallback (legacy)")

# ---- (4) deployed per-cell offsets shallow + == T47 regime offsets ----
reg = {}
with open(REPO / "docs/policy/per_regime_offsets_v2.csv", newline="") as f:
    for r in csv.DictReader(f):
        reg[(r["category"], r["anchor_regime"])] = int(float(r["bid_offset_cents"]))
n_cells = 0; shallow = 0; mirror_ok = True
with open(REPO / "docs/policy/entry_table_percell.csv", newline="") as f:
    for r in csv.DictReader(f):
        n_cells += 1
        off = int(float(r["bid_offset_cents"]))
        if off <= 3:
            shallow += 1
        if reg[(r["category"], r["regime"])] != off:
            mirror_ok = False
check(n_cells == 360, "per-cell table has 360 rows (4 cat x 90 cells)")
check(mirror_ok, "every per-cell offset == its T47 regime offset (no f x D argmax inflation)")
check(shallow >= n_cells * 0.7, "majority of cells shallow (<=3c): %d/%d" % (shallow, n_cells))

# ---- (5) interaction with T52 / T51 (orthogonal guards still fire) ----
g = types.SimpleNamespace(_log=lambda *a, **k: None)
g._taker_spread_ok = types.MethodType(M.LiveV3._taker_spread_ok, g)
check(g._taker_spread_ok(50, 52) is True, "T52 tight spread still allows taker")
check(g._taker_spread_ok(37, 75) is False, "T52 fat spread (KESMAR-like) still blocks taker")
ET = "E"; g.event_tickers = {ET: set()}; g._trade_times = {}; g._events_live = set()
g._is_match_live = types.MethodType(M.LiveV3._is_match_live, g)
check(g._is_match_live(ET) is False, "T51 quiet event not flagged live (no conflict with anchor)")

# ---- (6) captured-tape sanity ----
# load real per-cell table for ATP_MAIN + ATP_CHALL
cell_tbl = {}
with open(REPO / "docs/policy/entry_table_percell.csv", newline="") as f:
    for r in csv.DictReader(f):
        cell_tbl[(r["category"], int(float(r["c"])))] = (
            int(float(r["placement_minute"])), int(float(r["bid_offset_cents"])),
            float(r["expected_fill_rate"]), float(r["expected_net_roi_pct"]))
t = make_bot(); t.entry_table_cell = cell_tbl

# TIAARN: tight 50/51 flat book, fresh in-spread print at 50 -> last_traded
tia = t._v4_entry_anchor("TIA", "ATP_MAIN", book(50, 51, last_trade=50), FAR)
check(tia[1] == "last_traded" and tia[0] == 50,
      "TIAARN: tight book, in-spread print -> last_traded 50 (not the eventual settle)")
check(1 <= tia[8] < tia[0] and tia[5] <= 3, "TIAARN: sane shallow bid (target %d, offset %d)" % (tia[8], tia[5]))

# KESMAR: fat-spread book; fresh traded print at 40 -> last_traded (mid ignored on a wide book)
kes = t._v4_entry_anchor("KES", "ATP_CHALL", book(37, 75, last_trade=40), FAR)
check(kes[0] == 40 and 1 <= kes[8] < 40 and kes[5] <= 5,
      "KESMAR: sane shallow maker bid off last_traded 40 (target %d, offset %d)" % (kes[8], kes[5]))
check(g._taker_spread_ok(37, 75) is False,
      "KESMAR: T52 blocks the taker cross on the fat spread (resting maker target unaffected)")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
