#!/usr/bin/env python3
"""[C-FV-QUOTE] operator's on-demand fair-value quote. READ-ONLY.

NEVER-BANS: reference only -- this tool NEVER generates a placement, NEVER
vetoes one, and carries NO in-match logic. It prints; the operator decides.

Usage: python3 analysis/fv_quote.py RADRAK
       python3 analysis/fv_quote.py Raducanu
Per leg: odds-implied price (betexplorer, vig-removed, + read age), Kalshi
mid + last print (+ age), 5-level book chains with depth ratio (G2
vocabulary: wall >= 1000 shares at a level), and the BLEND -- uniform weights
over FRESH sources only; a single fresh source is printed as single-source,
never called a blend. Stale sources are dropped AND shown as dropped.

The blend computation (blend_quote) is the single codepath shared with the
FV-OBSERVE v4_place hook (flag fv_observe, default OFF, pending Plex's split
countersign)."""
import sys, asyncio, json, time, sqlite3, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

ODDS_FRESH_SEC = 1800          # betexplorer read older than 30min = stale, dropped
LAST_FRESH_SEC = 3600          # last print older than 60min = shown, excluded from blend
WALL = 1000                    # G2 vocabulary: a level >= this is a wall

def blend_quote(sources):
    """THE shared blend: uniform weights over fresh sources.
    sources = [(name, value_cents, fresh_bool)]. Returns (value|None, label,
    used, dropped). Single fresh source -> its value, label 'single:<name>'
    (refuses to be called a blend)."""
    used = [(n, v) for n, v, fresh in sources if fresh and v is not None]
    dropped = [n for n, v, fresh in sources if not fresh or v is None]
    if not used:
        return None, "no_fresh_source", [], dropped
    if len(used) == 1:
        return used[0][1], "single:%s" % used[0][0], [u[0] for u in used], dropped
    return (sum(v for _, v in used) / len(used),
            "blend_uniform_%d" % len(used), [u[0] for u in used], dropped)

async def _kalshi(session_tuple, path):
    import live_v4 as L
    s, ak, pk, rl = session_tuple
    return await L.api_get(s, ak, pk, path, rl)

async def find_event(st, fragment):
    """Match event tickers / player names across ALL series incl. ITF."""
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

def odds_for(p_name_full):
    """Freshest betexplorer_staging row mentioning the player's surname.
    Returns (fv_cents, age_sec, matched_row_label) or (None, None, reason)."""
    surname = p_name_full.split()[-1].upper()
    con = sqlite3.connect("file:%s?mode=ro" % (BASE / "tennis.db"), uri=True)
    best = None
    for p1, p2, f1, f2, ts in con.execute(
            "SELECT p1_name, p2_name, p1_fv_cents, p2_fv_cents, scraped_at "
            "FROM betexplorer_staging ORDER BY scraped_at DESC LIMIT 4000"):
        for nm, fv in ((p1, f1), (p2, f2)):
            if surname in (nm or "").upper():
                age = time.time() - datetime.datetime.strptime(
                    ts, "%Y-%m-%d %H:%M:%S").timestamp()
                if best is None or age < best[1]:
                    best = (fv, age, "%s vs %s @ %s" % (p1, p2, ts))
        if best and best[1] < 600:
            break
    con.close()
    return best if best else (None, None, "no betexplorer row for %s" % surname)

async def quote_event(st, et, markets):
    out = ["", "=" * 76,
           "FV QUOTE  %s   (REFERENCE ONLY -- never places, never vetoes, no in-match logic)" % et,
           "=" * 76]
    for m in markets:
        tk = m["ticker"]
        full_name = m.get("yes_sub_title") or tk
        ob = await _kalshi(st, "/trade-api/v2/markets/%s/orderbook?depth=5" % tk)
        trades = await _kalshi(st, "/trade-api/v2/markets/trades?ticker=%s&limit=1" % tk)
        yes_levels, no_levels = [], []
        if ob:
            o = ob.get("orderbook_fp") or ob.get("orderbook") or ob
            raw_yes = (o.get("yes_dollars") or o.get("yes_dollars_fp")
                       or o.get("yes") or [])
            raw_no = (o.get("no_dollars") or o.get("no_dollars_fp")
                      or o.get("no") or [])
            yes_levels = [(round(float(p) * 100) if float(p) < 2 else int(float(p)),
                           int(float(q))) for p, q in raw_yes][-5:]
            no_levels = [(100 - (round(float(p) * 100) if float(p) < 2 else int(float(p))),
                          int(float(q))) for p, q in raw_no][-5:]
        bids = sorted(yes_levels, reverse=True)
        asks = sorted(no_levels)
        best_bid = bids[0][0] if bids else None
        best_ask = asks[0][0] if asks else None
        mid = (best_bid + best_ask) / 2.0 if (best_bid is not None and best_ask is not None) else None
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
        ofv, oage, olabel = odds_for(full_name)
        fv, label, used, dropped = blend_quote([
            ("odds_implied", ofv, bool(oage is not None and oage <= ODDS_FRESH_SEC)),
            ("kalshi_mid", mid, mid is not None),
        ])
        bd = sum(q for _, q in bids); ad = sum(q for _, q in asks)
        ratio = bd / (bd + ad) if (bd + ad) else 0.5
        walls = ["%dc x%d" % (p, q) for p, q in bids + asks if q >= WALL]
        out.append("")
        out.append("LEG: %s  (%s)" % (full_name, tk))
        out.append("  odds-implied : %s" % (
            "%.1fc (age %dmin, %s)" % (ofv, oage // 60, olabel) if ofv is not None
            else "none (%s)" % olabel))
        out.append("  kalshi       : mid %s  last %s" % (
            "%.1fc" % mid if mid is not None else "?",
            "%sc (age %s)" % (last_p, "%dmin" % (last_age // 60) if last_age is not None else "?")
            if last_p is not None else "none"))
        out.append("  book (5-lvl) : bids %s" % (" ".join("%d x%d" % l for l in bids) or "EMPTY"))
        out.append("                 asks %s" % (" ".join("%d x%d" % l for l in asks) or "EMPTY"))
        out.append("  depth        : bid %d / ask %d  ratio %.2f%s" % (
            bd, ad, ratio, ("  WALLS: " + ", ".join(walls)) if walls else ""))
        if fv is not None:
            gaps = []
            if best_bid is not None:
                gaps.append("fv-bid %+.1f" % (fv - best_bid))
            if best_ask is not None:
                gaps.append("ask-fv %+.1f" % (best_ask - fv))
            flag = ""
            if best_bid is not None and fv < best_bid:
                flag = "  << FV BELOW BID (bid rich)"
            elif best_ask is not None and fv > best_ask:
                flag = "  << FV ABOVE ASK (ask cheap)"
            out.append("  FV           : %.1fc  [%s; dropped: %s]  %s%s" % (
                fv, label, ", ".join(dropped) or "none", " ".join(gaps), flag))
        else:
            out.append("  FV           : UNAVAILABLE (no fresh source; dropped: %s)"
                       % (", ".join(dropped) or "none"))
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
