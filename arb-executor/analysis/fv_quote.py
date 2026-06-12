#!/usr/bin/env python3
"""[C-FV-PERBOOK] operator's on-demand per-book pricing panel. READ-ONLY.

NEVER-BANS: reference only -- this tool NEVER generates a placement, NEVER
vetoes one, and carries NO in-match logic. It prints; the operator decides.

Usage: python3 analysis/fv_quote.py RADRAK
       python3 analysis/fv_quote.py Samson
Per match: a PANEL with both legs as columns and sources as rows --
  - each bookmaker row (betexplorer_books, when present): raw odds ->
    implied cents vig-removed PAIRWISE within that book, the book's raw
    pair-sum (overround) and read age
  - betexplorer_avg: the tournament-page average pair (same treatment)
  - kalshi_mid / kalshi_last (the derived-cent native; last is display-only)
  - BLEND: uniform weights over FRESH sources, with the WEIGHTS LINE --
    every source's weight and age; dropped sources at w=0 with the reason
    (stale/absent). A single fresh source prints single:<name> and REFUSES
    the blend label. Stale rows are SHOWN as stale; live odds are never
    synthesized (the collector is premarket: in-play matches will often
    have no fresh book rows -- that is shown, not papered over).

COLLECTOR FINDING (2026-06-12, checked first per spec): betexplorer.py
stores the AGGREGATE only, and the source itself does not serve a
per-bookmaker table to this collector's egress (match pages carry average
data-odd pairs + bet365 branding; the odds-tab endpoints 404). The
betexplorer_books table + reader are wired so a future per-book source
fills the panel automatically; today those rows print as absent."""
import sys, asyncio, json, time, sqlite3, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

ODDS_FRESH_SEC = 1800          # odds read older than 30min = stale (shown, weight 0)
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

def weights_line(entries):
    """The operator's weights line. entries = [(name, weight, age_str,
    reason_when_zero)]. Every source listed; w=0 carries its reason."""
    parts = []
    for name, w, age, reason in entries:
        if w > 0:
            parts.append("%s w=%.2f (%s)" % (name, w, age))
        else:
            parts.append("%s w=0 (%s)" % (name, reason))
    return "WEIGHTS: " + " | ".join(parts)

def _age_str(sec):
    if sec is None:
        return "?"
    if sec < 90:
        return "%ds" % sec
    return "%dmin" % (sec // 60)

def _pair_implied(o1, o2):
    """Pairwise vig removal within ONE book. Returns (c1, c2, oversum_pct)."""
    r1, r2 = 1.0 / o1, 1.0 / o2
    t = r1 + r2
    return (round(r1 / t * 100, 1), round(r2 / t * 100, 1), round(t * 100, 1))

def _surname(full):
    return (full or "").split()[-1].upper()

def odds_pair_for(name_a, name_b):
    """Freshest betexplorer_staging row matching BOTH surnames. Returns
    {p1, p2, o1, o2, age} or None. Aggregate (tournament-page average)."""
    sa, sb = _surname(name_a), _surname(name_b)
    con = sqlite3.connect("file:%s?mode=ro" % (BASE / "tennis.db"), uri=True)
    out = None
    for p1, p2, o1, o2, ts in con.execute(
            "SELECT p1_name, p2_name, raw_odds_p1, raw_odds_p2, scraped_at "
            "FROM betexplorer_staging ORDER BY scraped_at DESC LIMIT 4000"):
        u1, u2 = (p1 or "").upper(), (p2 or "").upper()
        if ((sa in u1 and sb in u2) or (sa in u2 and sb in u1)):
            age = time.time() - datetime.datetime.strptime(
                ts, "%Y-%m-%d %H:%M:%S").timestamp()
            swapped = sa in u2
            out = {"p1": p1, "p2": p2, "o1": o1, "o2": o2, "age": age,
                   "swapped": swapped}
            break
    con.close()
    return out

def book_rows_for(name_a, name_b):
    """Per-bookmaker rows from betexplorer_books, when the table exists and
    has rows for this pair. Returns [{book, o1, o2, age, swapped}]. Today the
    source does not serve per-book odds to this collector (see header) -- an
    empty list is the honest answer, rendered as absent."""
    sa, sb = _surname(name_a), _surname(name_b)
    con = sqlite3.connect("file:%s?mode=ro" % (BASE / "tennis.db"), uri=True)
    rows = []
    try:
        for bk, p1, p2, o1, o2, ts in con.execute(
                "SELECT bookmaker, p1_name, p2_name, raw_odds_p1, raw_odds_p2, "
                "scraped_at FROM betexplorer_books ORDER BY scraped_at DESC LIMIT 4000"):
            u1, u2 = (p1 or "").upper(), (p2 or "").upper()
            if ((sa in u1 and sb in u2) or (sa in u2 and sb in u1)):
                if any(r["book"] == bk for r in rows):
                    continue  # freshest per book only
                age = time.time() - datetime.datetime.strptime(
                    ts, "%Y-%m-%d %H:%M:%S").timestamp()
                rows.append({"book": bk, "o1": o1, "o2": o2, "age": age,
                             "swapped": sa in u2})
    except sqlite3.OperationalError:
        pass  # table absent: per-book capture not available (collector finding)
    con.close()
    return rows

# legacy single-name lookup kept for the FV-OBSERVE hook
def odds_for(p_name_full):
    surname = _surname(p_name_full)
    con = sqlite3.connect("file:%s?mode=ro" % (BASE / "tennis.db"), uri=True)
    best = None
    for p1, p2, f1, f2, ts in con.execute(
            "SELECT p1_name, p2_name, p1_fv_cents, p2_fv_cents, scraped_at "
            "FROM betexplorer_staging ORDER BY scraped_at DESC LIMIT 4000"):
        for nm, fv in ((p1, f1), (p2, f2)):
            if surname and surname in (nm or "").upper():
                age = time.time() - datetime.datetime.strptime(
                    ts, "%Y-%m-%d %H:%M:%S").timestamp()
                if best is None or age < best[1]:
                    best = (fv, age, "%s vs %s @ %s" % (p1, p2, ts))
        if best and best[1] < 600:
            break
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
            "best_ask": best_ask, "last": last_p, "last_age": last_age}

async def quote_event(st, et, markets):
    legs = [await _leg_market(st, m) for m in markets[:2]]
    out = ["", "=" * 78,
           "FV PANEL  %s   (REFERENCE ONLY -- never places, never vetoes, no in-match logic)" % et,
           "=" * 78]
    if len(legs) < 2:
        out.append("(single-leg event; panel needs the pair)")
        return "\n".join(out)
    A, B = legs
    fresh_a, fresh_b = [], []
    wl_a, wl_b = [], []
    hdr = "%-18s %-8s %8s %8s %9s | %8s %8s" % (
        "SOURCE", "age", "%s_raw" % A["name"].split()[-1][:7],
        "%s_raw" % B["name"].split()[-1][:7], "oversum",
        "%s_c" % A["name"].split()[-1][:7], "%s_c" % B["name"].split()[-1][:7])
    out.append(hdr)
    out.append("-" * len(hdr))

    def add_odds_row(label, o1, o2, age, swapped):
        ca, cb, oversum = _pair_implied(o1, o2)
        if swapped:
            ca, cb = cb, ca
            o1, o2 = o2, o1
        fresh = age is not None and age <= ODDS_FRESH_SEC
        tag = "" if fresh else "  STALE"
        out.append("%-18s %-8s %8.2f %8.2f %8.1f%% | %8.1f %8.1f%s" % (
            label, _age_str(age), o1, o2, oversum, ca, cb, tag))
        if fresh:
            fresh_a.append((label, ca)); fresh_b.append((label, cb))
            return None
        return "stale %s" % _age_str(age)

    books = book_rows_for(A["name"], B["name"])
    if books:
        for b in books:
            reason = add_odds_row(b["book"][:18], b["o1"], b["o2"], b["age"], b["swapped"])
            wl_a.append((b["book"][:18], reason)); wl_b.append((b["book"][:18], reason))
    else:
        out.append("%-18s %-8s %8s %8s %9s | %8s %8s" % (
            "per-book", "--", "--", "--", "--", "--", "--")
            + "  ABSENT (source serves no per-book table to this collector)")
        wl_a.append(("per-book", "absent: not served"))
        wl_b.append(("per-book", "absent: not served"))

    agg = odds_pair_for(A["name"], B["name"])
    if agg:
        reason = add_odds_row("betexplorer_avg", agg["o1"], agg["o2"], agg["age"], agg["swapped"])
        wl_a.append(("betexplorer_avg", reason)); wl_b.append(("betexplorer_avg", reason))
    else:
        out.append("%-18s %-8s %8s %8s %9s | %8s %8s  ABSENT" % (
            "betexplorer_avg", "--", "--", "--", "--", "--", "--"))
        wl_a.append(("betexplorer_avg", "absent")); wl_b.append(("betexplorer_avg", "absent"))

    out.append("%-18s %-8s %8s %8s %9s | %8s %8s" % (
        "kalshi_mid", "live", "--", "--", "--",
        ("%.1f" % A["mid"]) if A["mid"] is not None else "?",
        ("%.1f" % B["mid"]) if B["mid"] is not None else "?"))
    if A["mid"] is not None:
        fresh_a.append(("kalshi_mid", A["mid"]))
    else:
        wl_a.append(("kalshi_mid", "no two-sided book"))
    if B["mid"] is not None:
        fresh_b.append(("kalshi_mid", B["mid"]))
    else:
        wl_b.append(("kalshi_mid", "no two-sided book"))
    out.append("%-18s %-8s %8s %8s %9s | %8s %8s  (display only)" % (
        "kalshi_last", "%s/%s" % (_age_str(A["last_age"]), _age_str(B["last_age"])),
        "--", "--", "--",
        A["last"] if A["last"] is not None else "?",
        B["last"] if B["last"] is not None else "?"))

    for leg, fresh, wl in ((A, fresh_a, wl_a), (B, fresh_b, wl_b)):
        fv, label, used, _ = blend_quote([(n, v, True) for n, v in fresh])
        n_used = len(used)
        w = (1.0 / n_used) if n_used else 0.0
        entries = [(n, w, "live" if n == "kalshi_mid" else "fresh", "") for n, v in fresh]
        entries += [(n, 0.0, "", r or "stale/absent") for n, r in wl]
        entries.append(("kalshi_last", 0.0, "", "display-only"))
        gaps = []
        if fv is not None and leg["best_bid"] is not None:
            gaps.append("fv-bid %+.1f" % (fv - leg["best_bid"]))
        if fv is not None and leg["best_ask"] is not None:
            gaps.append("ask-fv %+.1f" % (leg["best_ask"] - fv))
        flag = ""
        if fv is not None and leg["best_bid"] is not None and fv < leg["best_bid"]:
            flag = "  << FV BELOW BID (bid rich)"
        elif fv is not None and leg["best_ask"] is not None and fv > leg["best_ask"]:
            flag = "  << FV ABOVE ASK (ask cheap)"
        out.append("")
        out.append("BLEND %-12s : %s  [%s]  %s%s" % (
            leg["name"][:12],
            ("%.1fc" % fv) if fv is not None else "UNAVAILABLE",
            label, " ".join(gaps), flag))
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
