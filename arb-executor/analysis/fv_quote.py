#!/usr/bin/env python3
"""[C-FV-OBSERVE-SHIP] operator's per-book pricing panel + the FV-OBSERVE
blend. READ-ONLY as a tool; the hook is logging-only.

NEVER-BANS: reference only -- this module NEVER generates a placement, NEVER
vetoes one, and carries NO in-match logic. It prints/logs; the operator and
the calibration read decide.

Usage: python3 analysis/fv_quote.py RADRAK | python3 analysis/fv_quote.py Samson

DATA: the paid Odds API pipeline (tennis_odds.py -> book_prices rows, one
no-vig fair pair per bookmaker per poll; 32-33 books per event when a
tournament is covered). The BLEND uses the SHARP_BOOKS only. betexplorer is
the FALLBACK row, displayed as such, never blended. One no-vig
implementation: tennis_odds.calc_no_vig (file-path import below) -- the same
math OMI Edge's engine consumes; one backend, two consumers, divergence
impossible.

STALENESS CONTRACT (Plex): the blend computes only with >= N_FRESH_MIN fresh
sharp books within AGE_BOUND_SEC (premarket). Below the floor -> fv=None,
reason='stale_sources' -- logged, never faked. Once the match is live, the
premarket-natured book rows drop from the blend (reason 'nature_stale').
Coverage reality (checked 2026-06-12): SHARP_BOOKS has 3 keys and French-
Open-era events carried all 3 (32-33 total books/event), so Plex's N=3
stands; the failure mode is the honest NULL."""
import sys, asyncio, json, time, sqlite3, datetime, importlib.util
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

# ---- the ONE no-vig implementation (tennis_odds.calc_no_vig) ----
_spec = importlib.util.spec_from_file_location("tennis_odds_mod", BASE / "tennis_odds.py")
_TO = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_TO)
calc_no_vig = _TO.calc_no_vig
SHARP_BOOKS = list(_TO.SHARP_BOOKS)

N_FRESH_MIN = 3                # Plex floor: fresh sharp books required to blend
AGE_BOUND_SEC = 3600           # premarket freshness bound (60 min)
ODDS_FRESH_SEC = 1800          # betexplorer fallback display freshness
WALL = 1000                    # G2 vocabulary: a level >= this is a wall

def blend_quote(sources):
    """Uniform weights over fresh sources. sources=[(name, value, fresh)].
    Returns (value|None, label, used, dropped). Single fresh -> single:<name>
    (refuses the blend label)."""
    used = [(n, v) for n, v, fresh in sources if fresh and v is not None]
    dropped = [n for n, v, fresh in sources if not fresh or v is None]
    if not used:
        return None, "no_fresh_source", [], dropped
    if len(used) == 1:
        return used[0][1], "single:%s" % used[0][0], [u[0] for u in used], dropped
    return (sum(v for _, v in used) / len(used),
            "blend_uniform_%d" % len(used), [u[0] for u in used], dropped)

def weights_line(entries):
    """entries=[(name, weight, age_str, reason_when_zero)] -- every source
    listed; w=0 carries its reason."""
    parts = []
    for name, w, age, reason in entries:
        parts.append("%s w=%.2f (%s)" % (name, w, age) if w > 0
                     else "%s w=0 (%s)" % (name, reason))
    return "WEIGHTS: " + " | ".join(parts)

def _age_str(sec):
    if sec is None:
        return "?"
    return "%ds" % sec if sec < 90 else "%dmin" % (sec // 60)

def _surname(full):
    return (full or "").split()[-1].upper()

def _parse_ts(ts):
    return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp()

def sharp_rows(event_ticker, db_path=None):
    """Freshest row per SHARP book for the event from book_prices (the paid
    pipeline; every book persisted per poll by tennis_odds.py)."""
    con = sqlite3.connect("file:%s?mode=ro" % (db_path or BASE / "tennis.db"), uri=True)
    rows = []
    seen = set()
    try:
        q = ("SELECT book_key, player1_name, player2_name, raw_odds_p1, "
             "raw_odds_p2, commence_time, polled_at FROM book_prices "
             "WHERE event_ticker=? AND book_key IN (%s) "
             "ORDER BY polled_at DESC LIMIT 200"
             % ",".join("?" * len(SHARP_BOOKS)))
        for bk, p1, p2, o1, o2, ct, ts in con.execute(
                q, [event_ticker] + SHARP_BOOKS):
            if bk in seen:
                continue
            seen.add(bk)
            rows.append({"book": bk, "p1": p1, "p2": p2, "o1": o1, "o2": o2,
                         "commence": ct, "age": time.time() - _parse_ts(ts)})
    except sqlite3.OperationalError:
        pass
    con.close()
    return rows

def _leg_side(row, leg_name, ticker=None):
    """Which side of the odds pair is this leg: surname match first, ticker
    3-char suffix fallback (the book_prices resolver pattern)."""
    s = _surname(leg_name)
    u1, u2 = (row["p1"] or "").upper(), (row["p2"] or "").upper()
    if s and s in u1:
        return 1
    if s and s in u2:
        return 2
    if ticker:
        suf = ticker.rsplit("-", 1)[-1].upper()
        if u1.split()[-1][:3] == suf[:3] if u1 else False:
            return 1
        if u2.split()[-1][:3] == suf[:3] if u2 else False:
            return 2
    return None

def sharp_fv(event_ticker, leg_name, match_live, ticker=None, db_path=None):
    """THE FV-OBSERVE blend (one codepath, two consumers): uniform over fresh
    sharp books for one leg. Returns (fv|None, sources, reason|None).
    sources = [[book_key, age_sec, status]] -- Plex requirement: calibration
    must recover the blend's anatomy per row."""
    rows = sharp_rows(event_ticker, db_path=db_path)
    fresh_vals, sources = [], []
    for r in rows:
        side = _leg_side(r, leg_name, ticker)
        f1, f2 = calc_no_vig(r["o1"] or 0, r["o2"] or 0)
        val = None
        if side and f1 is not None:
            val = round((f1 if side == 1 else f2) * 100, 1)
        if match_live:
            status = "nature_stale"          # premarket-natured row, match live
        elif r["age"] > AGE_BOUND_SEC:
            status = "stale"
        elif val is None:
            status = "unresolvable_side"
        else:
            status = "fresh"
            fresh_vals.append(val)
        sources.append([r["book"], round(r["age"]), status])
    if len(fresh_vals) < N_FRESH_MIN:
        if not rows:
            return None, sources, "stale_sources"
        return None, sources, ("nature_stale" if match_live else "stale_sources")
    return round(sum(fresh_vals) / len(fresh_vals), 2), sources, None

# ---- betexplorer fallback (display-only; never blended) ----
def odds_pair_for(name_a, name_b):
    sa, sb = _surname(name_a), _surname(name_b)
    con = sqlite3.connect("file:%s?mode=ro" % (BASE / "tennis.db"), uri=True)
    out = None
    for p1, p2, o1, o2, ts in con.execute(
            "SELECT p1_name, p2_name, raw_odds_p1, raw_odds_p2, scraped_at "
            "FROM betexplorer_staging ORDER BY scraped_at DESC LIMIT 4000"):
        u1, u2 = (p1 or "").upper(), (p2 or "").upper()
        if ((sa in u1 and sb in u2) or (sa in u2 and sb in u1)):
            out = {"o1": o1, "o2": o2, "age": time.time() - _parse_ts(ts),
                   "swapped": sa in u2}
            break
    con.close()
    return out

# legacy single-name aggregate lookup (kept for compatibility)
def odds_for(p_name_full):
    surname = _surname(p_name_full)
    con = sqlite3.connect("file:%s?mode=ro" % (BASE / "tennis.db"), uri=True)
    best = None
    for p1, p2, f1, f2, ts in con.execute(
            "SELECT p1_name, p2_name, p1_fv_cents, p2_fv_cents, scraped_at "
            "FROM betexplorer_staging ORDER BY scraped_at DESC LIMIT 4000"):
        for nm, fv in ((p1, f1), (p2, f2)):
            if surname and surname in (nm or "").upper():
                age = time.time() - _parse_ts(ts)
                if best is None or age < best[1]:
                    best = (fv, age, "%s vs %s" % (p1, p2))
    con.close()
    return best if best else (None, None, "no betexplorer row for %s" % surname)

async def _kalshi(st, path):
    import live_v4 as L
    s, ak, pk, rl = st
    return await L.api_get(s, ak, pk, path, rl)

async def find_event(st, fragment):
    import live_v4 as L
    frag = fragment.upper()
    hits = {}
    for series in L.ALL_SERIES:
        cursor = ""
        for _ in range(6):
            path = "/trade-api/v2/markets?limit=100&status=open&series_ticker=%s" % series
            if cursor:
                path += "&cursor=%s" % cursor
            d = await _kalshi(st, path)
            if not d:
                break
            for m in d.get("markets", []):
                names = " ".join(filter(None, [m.get("yes_sub_title", ""),
                                               m.get("no_sub_title", ""),
                                               m.get("title", "")])).upper()
                if frag in m.get("event_ticker", "").upper() or frag in names:
                    hits.setdefault(m["event_ticker"], []).append(m)
            cursor = d.get("cursor", "")
            if not cursor:
                break
    return hits

async def _leg_market(st, m):
    tk = m["ticker"]
    ob = await _kalshi(st, "/trade-api/v2/markets/%s/orderbook?depth=5" % tk)
    trades = await _kalshi(st, "/trade-api/v2/markets/trades?ticker=%s&limit=1" % tk)
    yes_levels, no_levels = [], []
    if ob:
        o = ob.get("orderbook_fp") or ob.get("orderbook") or ob
        raw_yes = o.get("yes_dollars") or o.get("yes_dollars_fp") or o.get("yes") or []
        raw_no = o.get("no_dollars") or o.get("no_dollars_fp") or o.get("no") or []
        yes_levels = [(round(float(p) * 100) if float(p) < 2 else int(float(p)),
                       int(float(q))) for p, q in raw_yes][-5:]
        no_levels = [(100 - (round(float(p) * 100) if float(p) < 2 else int(float(p))),
                      int(float(q))) for p, q in raw_no][-5:]
    bids = sorted(yes_levels, reverse=True)
    asks = sorted(no_levels)
    best_bid = bids[0][0] if bids else None
    best_ask = asks[0][0] if asks else None
    mid = ((best_bid + best_ask) / 2.0
           if best_bid is not None and best_ask is not None else None)
    last_p = last_age = None
    for t in (trades or {}).get("trades", []):
        pr = t.get("yes_price_dollars", t.get("yes_price"))
        last_p = round(float(pr) * 100) if float(pr) < 2 else int(pr)
        ct = t.get("created_time", "").replace("Z", "+00:00")
        try:
            last_age = time.time() - datetime.datetime.fromisoformat(ct).timestamp()
        except Exception:
            last_age = None
        break
    return {"tk": tk, "name": m.get("yes_sub_title") or tk, "bids": bids,
            "asks": asks, "mid": mid, "best_bid": best_bid,
            "best_ask": best_ask, "last": last_p, "last_age": last_age,
            "close_time": m.get("close_time", ""),
            "expected_expiration_time": m.get("expected_expiration_time", "")}

def _match_live_guess(rows):
    """live iff the freshest sharp row's commence_time is in the past."""
    for r in rows:
        ct = (r.get("commence") or "").replace("Z", "+00:00")
        try:
            return time.time() > datetime.datetime.fromisoformat(ct).timestamp()
        except Exception:
            continue
    return False

async def quote_event(st, et, markets):
    legs = [await _leg_market(st, m) for m in markets[:2]]
    out = ["", "=" * 78,
           "FV PANEL  %s   (REFERENCE ONLY -- never places, never vetoes, no in-match logic)" % et,
           "=" * 78]
    if len(legs) < 2:
        out.append("(single-leg event; panel needs the pair)")
        return "\n".join(out)
    A, B = legs
    rows = sharp_rows(et)
    live = _match_live_guess(rows)
    na, nb = A["name"].split()[-1][:7], B["name"].split()[-1][:7]
    hdr = "%-18s %-8s %8s %8s %9s | %8s %8s" % (
        "SOURCE", "age", na + "_raw", nb + "_raw", "oversum", na + "_c", nb + "_c")
    out.append(hdr)
    out.append("-" * len(hdr))
    if rows:
        for r in rows:
            f1, f2 = calc_no_vig(r["o1"] or 0, r["o2"] or 0)
            side_a = _leg_side(r, A["name"], A["tk"])
            oversum = (1.0 / r["o1"] + 1.0 / r["o2"]) * 100 if (r["o1"] and r["o2"]) else 0
            ca = round((f1 if side_a == 1 else f2) * 100, 1) if (f1 and side_a) else None
            cb = round(100 - ca, 1) if ca is not None else None
            tag = ""
            if live:
                tag = "  NATURE_STALE (match live)"
            elif r["age"] > AGE_BOUND_SEC:
                tag = "  STALE"
            o_a = r["o1"] if side_a == 1 else r["o2"]
            o_b = r["o2"] if side_a == 1 else r["o1"]
            out.append("%-18s %-8s %8.2f %8.2f %8.1f%% | %8s %8s%s" % (
                r["book"][:18], _age_str(r["age"]), o_a or 0, o_b or 0, oversum,
                ("%.1f" % ca) if ca is not None else "?",
                ("%.1f" % cb) if cb is not None else "?", tag))
    else:
        out.append("%-18s %-8s %8s %8s %9s | %8s %8s  ABSENT (no sharp rows: Odds API "
                   "covers main tour only / tournament not served)" % (
                       "sharp books", "--", "--", "--", "--", "--", "--"))
    be = odds_pair_for(A["name"], B["name"])
    if be:
        f1, f2 = calc_no_vig(be["o1"], be["o2"])
        ca = round((f2 if be["swapped"] else f1) * 100, 1) if f1 else None
        oversum = (1.0 / be["o1"] + 1.0 / be["o2"]) * 100
        out.append("%-18s %-8s %8.2f %8.2f %8.1f%% | %8s %8s  FALLBACK (display-only, never blended)" % (
            "betexplorer_avg", _age_str(be["age"]),
            be["o2"] if be["swapped"] else be["o1"],
            be["o1"] if be["swapped"] else be["o2"], oversum,
            ("%.1f" % ca) if ca is not None else "?",
            ("%.1f" % (100 - ca)) if ca is not None else "?"))
    else:
        out.append("%-18s %-8s %8s %8s %9s | %8s %8s  FALLBACK ABSENT" % (
            "betexplorer_avg", "--", "--", "--", "--", "--", "--"))
    out.append("%-18s %-8s %8s %8s %9s | %8s %8s  (display only)" % (
        "kalshi_mid", "live", "--", "--", "--",
        ("%.1f" % A["mid"]) if A["mid"] is not None else "?",
        ("%.1f" % B["mid"]) if B["mid"] is not None else "?"))
    out.append("%-18s %-8s %8s %8s %9s | %8s %8s  (display only)" % (
        "kalshi_last", "%s/%s" % (_age_str(A["last_age"]), _age_str(B["last_age"])),
        "--", "--", "--",
        A["last"] if A["last"] is not None else "?",
        B["last"] if B["last"] is not None else "?"))

    for leg in (A, B):
        fv, sources, reason = sharp_fv(et, leg["name"], live, ticker=leg["tk"])
        n_fresh = sum(1 for s in sources if s[2] == "fresh")
        w = 1.0 / n_fresh if n_fresh else 0.0
        entries = []
        for bk, age, status in sources:
            if status == "fresh":
                entries.append((bk, w, _age_str(age), ""))
            else:
                entries.append((bk, 0.0, "", "%s %s" % (status, _age_str(age))))
        entries.append(("betexplorer_avg", 0.0, "", "fallback, never blended"))
        entries.append(("kalshi_mid", 0.0, "", "display-only"))
        entries.append(("kalshi_last", 0.0, "", "display-only"))
        gaps, flag = [], ""
        if fv is not None and leg["best_bid"] is not None:
            gaps.append("fv-bid %+.1f" % (fv - leg["best_bid"]))
            if fv < leg["best_bid"]:
                flag = "  << FV BELOW BID (bid rich)"
        if fv is not None and leg["best_ask"] is not None:
            gaps.append("ask-fv %+.1f" % (leg["best_ask"] - fv))
            if fv > leg["best_ask"]:
                flag = "  << FV ABOVE ASK (ask cheap)"
        out.append("")
        out.append("BLEND %-12s : %s  [%s]  %s%s" % (
            leg["name"][:12],
            ("%.1fc" % fv) if fv is not None else
            "NULL (reason=%s; floor: >=%d fresh sharps within %dmin)" % (
                reason, N_FRESH_MIN, AGE_BOUND_SEC // 60),
            "sharp_uniform_%d" % n_fresh if fv is not None else "no_blend",
            " ".join(gaps), flag))
        out.append("  " + weights_line(entries))
        walls = ["%dc x%d" % (p, q) for p, q in leg["bids"] + leg["asks"] if q >= WALL]
        out.append("  book: bids %s | asks %s%s" % (
            " ".join("%d x%d" % l for l in leg["bids"]) or "EMPTY",
            " ".join("%d x%d" % l for l in leg["asks"]) or "EMPTY",
            ("  WALLS: " + ", ".join(walls)) if walls else ""))
    return "\n".join(out)

async def main():
    import aiohttp, live_v4 as L
    if len(sys.argv) < 2:
        print("usage: fv_quote.py <event-code-or-name-fragment>")
        return
    frag = sys.argv[1]
    ak, pk = L.load_credentials(); rl = L.RateLimiter()
    async with aiohttp.ClientSession() as s:
        st = (s, ak, pk, rl)
        hits = await find_event(st, frag)
        if not hits:
            print("no open market matches '%s'" % frag)
            return
        for et, markets in sorted(hits.items()):
            print(await quote_event(st, et, markets))

if __name__ == "__main__":
    asyncio.run(main())
