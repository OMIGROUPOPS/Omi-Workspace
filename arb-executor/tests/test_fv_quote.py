#!/usr/bin/env python3
"""[C-FV-OBSERVE-SHIP] sharp-book FV: one no-vig backend, the Plex staleness
contract, the logging hook, and the no-decision-path pin.

Floor: blend only with >= N_FRESH_MIN fresh sharp books within AGE_BOUND_SEC;
below -> fv=None reason=stale_sources (logged, never faked); premarket-
natured rows drop once the match is live (nature_stale). The hook emits
fv / fv_gap / fv_sources (book keys + ages + status -- calibration recovers
the blend anatomy) on bot placements, manual observations, and adoptions.
ZERO behavioral effect, test-pinned.
Run: cd arb-executor && python3 tests/test_fv_quote.py
"""
import sys, types, inspect, json, sqlite3, tempfile, time, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import live_v4 as M
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "fv_quote_mod", Path(REPO) / "analysis" / "fv_quote.py")
FQ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FQ)

fails = 0
def check(c, m):
    global fails; print(("PASS " if c else "*** FAIL ") + m); fails += (0 if c else 1)

# ---- 1. ONE no-vig implementation: tennis_odds.calc_no_vig everywhere ----
f1, f2 = FQ.calc_no_vig(2.0, 2.0)
check((f1, f2) == (0.5, 0.5), "calc_no_vig sane (2.0/2.0 -> 50/50)")
src_fq = inspect.getsource(FQ)
check('"tennis_odds.py"' in src_fq and "calc_no_vig = _TO.calc_no_vig" in src_fq,
      "fv_quote consumes tennis_odds' calc_no_vig (one backend, two consumers)")
check(src_fq.count("raw1 / total") == 0,
      "no second no-vig formula in fv_quote (divergence impossible)")

# ---- 2. the staleness contract on a real (temp) book_prices table ----
def mkdb(rows):
    fp = tempfile.mktemp(suffix=".db")
    con = sqlite3.connect(fp)
    con.execute("""CREATE TABLE book_prices (event_ticker TEXT, book_key TEXT,
        player1_name TEXT, player2_name TEXT, book_p1_fv_cents REAL,
        book_p2_fv_cents REAL, raw_odds_p1 REAL, raw_odds_p2 REAL,
        vig_pct REAL, sport_key TEXT, commence_time TEXT, polled_at TEXT)""")
    for r in rows:
        con.execute("INSERT INTO book_prices VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", r)
    con.commit(); con.close()
    return fp

ET = "KXWTAMATCH-26JUN13TESTAA"
def ts_ago(sec):
    return datetime.datetime.fromtimestamp(time.time() - sec).strftime("%Y-%m-%d %H:%M:%S")

ROWS3 = [(ET, bk, "Anna Alpha", "Berta Beta", 60.0, 40.0, o1, o2, 5.0,
          "tennis_test", "2026-06-13T15:00:00Z", ts_ago(age))
         for bk, o1, o2, age in (("pinnacle", 1.60, 2.50, 120),
                                 ("betfair_ex_eu", 1.65, 2.45, 300),
                                 ("matchbook", 1.62, 2.48, 600))]
db3 = mkdb(ROWS3)
fv, sources, reason = FQ.sharp_fv(ET, "Anna Alpha", False, db_path=db3)
check(fv is not None and reason is None and len(sources) == 3
      and all(s[2] == "fresh" for s in sources),
      "3 fresh sharps -> blend computes (fv %.1f), anatomy lists all 3 fresh" % (fv or 0))
exp = sum(round(FQ.calc_no_vig(o1, o2)[0] * 100, 1)
          for _, o1, o2, _ in (("p", 1.60, 2.50, 0), ("b", 1.65, 2.45, 0),
                               ("m", 1.62, 2.48, 0))) / 3
check(abs(fv - exp) < 0.05, "blend = uniform mean of per-book no-vig fairs")
fvb, _, _ = FQ.sharp_fv(ET, "Berta Beta", False, db_path=db3)
check(abs(fv + fvb - 100.0) < 0.1, "leg pair sums to 100 (pairwise no-vig)")

db2 = mkdb(ROWS3[:2])
fv, sources, reason = FQ.sharp_fv(ET, "Anna Alpha", False, db_path=db2)
check(fv is None and reason == "stale_sources" and len(sources) == 2,
      "BELOW THE FLOOR (2 of %d): fv=NULL reason=stale_sources, never faked"
      % FQ.N_FRESH_MIN)

dbold = mkdb([(ET, "pinnacle", "Anna Alpha", "Berta Beta", 60.0, 40.0, 1.60,
               2.50, 5.0, "t", "2026-06-13T15:00:00Z", ts_ago(7200))] + ROWS3[1:])
fv, sources, reason = FQ.sharp_fv(ET, "Anna Alpha", False, db_path=dbold)
check(fv is None and reason == "stale_sources"
      and any(s[2] == "stale" for s in sources),
      "age past AGE_BOUND drops the row (status=stale) and breaks the floor")

# nature_stale: same fresh rows, match LIVE -> all drop
fv, sources, reason = FQ.sharp_fv(ET, "Anna Alpha", True, db_path=db3)
check(fv is None and reason == "nature_stale"
      and all(s[2] == "nature_stale" for s in sources),
      "match live -> premarket-natured rows drop (nature_stale), fv=NULL")

# ---- 3. the hook: fv / fv_gap / source list; emission sites wired ----
s = types.SimpleNamespace()
s._fv_quote_mod = types.SimpleNamespace(
    sharp_fv=lambda et, nm, live, ticker=None: (
        78.5, [["pinnacle", 100, "fresh"], ["betfair_ex_eu", 150, "fresh"],
               ["matchbook", 200, "fresh"]], None))
s._fv_observe_fields = types.MethodType(M.LiveV3._fv_observe_fields, s)
out = s._fv_observe_fields("EV", "EV-A", "Anna Alpha", 81, False)
check(out.get("fv") == 78.5 and out.get("fv_gap") == 2.5
      and out.get("fv_sources")[0][0] == "pinnacle" and "fv_reason" not in out,
      "hook emits fv, fv_gap (price - fv), and the per-book source anatomy")
s._fv_quote_mod = types.SimpleNamespace(
    sharp_fv=lambda *a, **k: (None, [["pinnacle", 99999, "stale"]], "stale_sources"))
out = s._fv_observe_fields("EV", "EV-A", "Anna Alpha", 81, False)
check(out.get("fv") is None and out.get("fv_gap") is None
      and out.get("fv_reason") == "stale_sources",
      "below-floor hook row: NULL with reason, logged not faked")
def _boom(*a, **k):
    raise RuntimeError("forced")
s_fail = types.SimpleNamespace(_fv_quote_mod=types.SimpleNamespace(sharp_fv=_boom))
s_fail._fv_observe_fields = types.MethodType(M.LiveV3._fv_observe_fields, s_fail)
check(s_fail._fv_observe_fields("EV", "EV-A", "x", 50, False) == {},
      "hook degrades to {} on failure (never blocks anything)")

src_route = inspect.getsource(M.LiveV3._route_event)
check(src_route.count("_fv_observe_fields") == 1
      and 'getattr(self, "fv_observe", False)' in src_route,
      "v4_place carries the hook exactly once, flag-guarded")
src_rec = inspect.getsource(M.LiveV3.reconcile)
check("_fv_observe_fields" in src_rec, "manual_bid_observed carries the hook")
src_ad = inspect.getsource(M.LiveV3._v4_reconcile_naked)
check("_fv_observe_fields" in src_ad, "adoption row carries the hook")

# ---- 4. ZERO behavioral effect: no decision path touches fv ----
for fn in ("_resting_cancel_reason", "_paired_basis_ok",
           "_engagement_join_eligible", "_fix6_reference", "_runway_status",
           "_manual_owns_leg", "_v4_manage_resting_inner", "check_fills",
           "_v4_apply_exit", "_completion_target"):
    src = inspect.getsource(getattr(M.LiveV3, fn))
    check("fv_observe" not in src and "_fv_quote_mod" not in src,
          "decision path %s never reads fv" % fn)

# ---- 5. tool hygiene + config ----
check("NEVER-BANS" in src_fq and "place_order" not in src_fq
      and "cancel_order" not in src_fq and "api_post" not in src_fq,
      "tool: zero order surface + never-bans header")
cfg = json.load(open(Path(REPO) / "config" / "deploy_v5_live.json"))
check(cfg.get("fv_observe") is True, "deploy config ships fv_observe: true (countersigned)")
wl = FQ.weights_line([("pinnacle", 1 / 3, "2min", ""),
                      ("matchbook", 0.0, "", "nature_stale 4min"),
                      ("betexplorer_avg", 0.0, "", "fallback, never blended")])
check("pinnacle w=0.33 (2min)" in wl and "matchbook w=0 (nature_stale 4min)" in wl
      and "betexplorer_avg w=0 (fallback, never blended)" in wl,
      "weights line: every source, w=0 with reason")

print("RESULT:", "ALL PASS" if fails == 0 else "%d FAILS" % fails)
sys.exit(1 if fails else 0)
