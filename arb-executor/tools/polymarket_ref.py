#!/usr/bin/env python3
"""PHASE-C P3 07-17 — POLYMARKET REFERENCE WIRE (read-only; ratified by the
operator's recorded words: a live reference price in discovery's anchor
family beside the FV anchors; history good).

Gamma discovery (tennis events, paginated — the arb-era scars honored:
outcome arrays map by surname, YES token may be INVERTED vs our leg) →
CLOB top-of-book for the live divergence number → /prices-history banked
for the backwalk. Freshness stamps on every row; a per-event THINNESS
FLOOR (top-of-book notional < $%(floor)s → the voice REFUSES to quote,
thin:true with its size). Scorecarded seat — no gate, no veto, weight
earned at the Phase-F bench.

Cron: */5 via install_polymarket_cron.sh. Output:
  state/polymarket_ref.json           {kalshi_event: row}
  state/polymarket_history/<slug>.json  (banked price history, append)
"""
import json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "state/polymarket_ref.json"
HIST = ROOT / "state/polymarket_history"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
THIN_FLOOR_USD = 50.0   # DECREED v1: sub-$50 top-of-book = no quote

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "omi-pm-ref"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def kalshi_codes():
    """Tracked tennis events from the engine's milestone cache: surname
    3-letter codes -> kalshi event ticker (today+tomorrow only)."""
    try:
        ms = json.loads((ROOT / "state/milestone_starts.json").read_text())
    except Exception:
        return {}
    out = {}
    now = time.time()
    from datetime import datetime
    for et in ms:
        m = re.search(r"-26[A-Z]{3}\d{2}([A-Z]{6})$", et)
        if not m:
            continue
        sd = (ms[et] or {}).get("start_date")
        try:
            ts = datetime.fromisoformat(sd.replace("Z", "+00:00")).timestamp()
        except Exception:
            continue
        if not (now - 12 * 3600 < ts < now + 36 * 3600):
            continue
        code = m.group(1)
        out.setdefault((code[:3], code[3:]), et)
    return out

def main():
    codes = kalshi_codes()
    rows = {}
    offset = 0
    events = []
    while True:   # pagination scar: page until empty
        try:
            page = get(GAMMA + "/events?closed=false&limit=100&offset=%d"
                       "&tag_slug=tennis" % offset)
        except Exception:
            break
        if not page:
            break
        events.extend(page)
        if len(page) < 100:
            break
        offset += 100
        if offset > 1000:
            break
    now = time.time()
    HIST.mkdir(parents=True, exist_ok=True)
    for ev in events:
        title = (ev.get("title") or "")
        mkts = ev.get("markets") or []
        for mk in mkts:
            try:
                outcomes = json.loads(mk.get("outcomes") or "[]")
                tokens = json.loads(mk.get("clobTokenIds") or "[]")
            except ValueError:
                continue
            if len(outcomes) != 2 or len(tokens) != 2:
                continue
            o0 = re.sub(r"[^A-Za-z]", "", outcomes[0].split()[-1])[:3].upper()
            o1 = re.sub(r"[^A-Za-z]", "", outcomes[1].split()[-1])[:3].upper()
            ket = codes.get((o0, o1)) or codes.get((o1, o0))
            if not ket:
                continue
            inverted = (o0, o1) not in codes   # scar: YES may map leg-2
            try:
                bk = get(CLOB + "/book?token_id=%s" % tokens[0])
                bb = (bk.get("bids") or [])
                ba = (bk.get("asks") or [])
                top_bid = float(bb[-1]["price"]) if bb else None
                top_bid_sz = float(bb[-1]["size"]) if bb else 0.0
                top_ask = float(ba[-1]["price"]) if ba else None
                notional = (top_bid or 0) * top_bid_sz
            except Exception:
                top_bid = top_ask = None
                notional = 0.0
            thin = notional < THIN_FLOOR_USD
            rows[ket] = {
                "pm_title": title[:60], "slug": ev.get("slug"),
                "token0": tokens[0], "inverted_vs_leg1": inverted,
                "yes_bid": top_bid, "yes_ask": top_ask,
                "top_notional_usd": round(notional, 1),
                "thin": thin,
                "thin_floor_usd": THIN_FLOOR_USD,
                "fetched_at": now}
            # history bank (backwalk fodder)
            try:
                h = get(CLOB + "/prices-history?market=%s&interval=1d"
                        "&fidelity=10" % tokens[0])
                hp = HIST / ("%s.json" % (ev.get("slug") or ket))
                hp.write_text(json.dumps({"kalshi_event": ket,
                                          "fetched_at": now,
                                          "history": h.get("history")}))
            except Exception:
                pass
            time.sleep(0.3)
    OUT.write_text(json.dumps({"rows": rows, "built_at": now,
                               "n": len(rows)}))
    print("polymarket_ref rows:", len(rows))

if __name__ == "__main__":
    main()
