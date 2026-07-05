#!/usr/bin/env python3
"""[READ-ONLY] Causal audit extractor: per event, the full CODE CHAIN from the logs
(posts/mechanisms/fills/sibling handling/cuts) + EXCHANGE TRUTH from the fills &
settlements APIs. Writes /tmp/causal_audit.json."""
import json, time, base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests

pk = serialization.load_pem_private_key(Path('kalshi.pem').read_bytes(), password=None, backend=default_backend())
B = 'https://api.elections.kalshi.com/trade-api/v2'
def sgn(m, p):
    ts = str(int(time.time() * 1000)); sp = '/trade-api/v2' + p.split('?')[0]
    sig = pk.sign((ts + m + sp).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {'KALSHI-ACCESS-KEY': 'f3b064d1-a02e-42a4-b2b1-132834694d23',
            'KALSHI-ACCESS-SIGNATURE': base64.b64encode(sig).decode(), 'KALSHI-ACCESS-TIMESTAMP': ts}
def g(p):
    for _ in range(4):
        try:
            return requests.get(B + p, headers=sgn('GET', p), timeout=25).json()
        except Exception:
            time.sleep(0.4)
    return {}

EVENTS = [
    "KXATPCHALLENGERMATCH-26JUL04GIUFEL", "KXATPCHALLENGERMATCH-26JUL04HEICEC",
    "KXATPCHALLENGERMATCH-26JUL04HEMMOE", "KXATPCHALLENGERMATCH-26JUL04KASPIR",
    "KXATPCHALLENGERMATCH-26JUL04MELCAS", "KXATPCHALLENGERMATCH-26JUL04RINDIA",
    "KXATPMATCH-26JUL04DESVA", "KXATPMATCH-26JUL04TIABUB",
    "KXITFMATCH-26JUL03HARNAS", "KXITFMATCH-26JUL04BENAHO", "KXITFMATCH-26JUL04ORLPOP",
    "KXITFWMATCH-26JUL04CLALAM", "KXWTAMATCH-26JUL04ANIKEY", "KXWTAMATCH-26JUL04EALSWI",
    "KXWTAMATCH-26JUL04MERRYB", "KXWTAMATCH-26JUL04PAOSAK",
    # tonight's post-window games
    "KXATPCHALLENGERMATCH-26JUL04HERPDA", "KXITFWMATCH-26JUL04ZANSIE",
    "KXATPCHALLENGERMATCH-26JUL04WATSHI", "KXATPCHALLENGERMATCH-26JUL04LEGWIN",
    "KXITFMATCH-26JUL04ZAMBRI",
]
LOGS = ["logs/live_v3_20260703.jsonl", "logs/live_v3_20260704.jsonl"]
KEEP = {"window_open_set", "v4_place", "order_placed", "order_cancelled", "entry_filled",
        "v4_exit_posted", "exit_filled", "settled", "premarket_walk_capped",
        "leg2_reshuffle_reaim", "reaim_sibling_arrival", "reaim_sibling_cancel",
        "sibling_repost_placed", "sibling_repost_skip", "match_live_detected",
        "match_live_grace_armed", "match_live_resting_cancel", "match_live_unlatched",
        "fv_burst_anchor", "liquid_repost_at_touch", "completion_fill",
        "reconcile_v4_adopted", "reconcile_v4_exit_found", "staircase_hold_place"}
SLIM = {"staircase_hold_place": 3}   # cap repetitive events per ticker

chains = defaultdict(list)
counts = defaultdict(lambda: defaultdict(int))
for lp in LOGS:
    if not Path(lp).exists():
        continue
    for line in open(lp, encoding="utf-8", errors="replace"):
        if '"event"' not in line:
            continue
        ev_hit = next((E for E in EVENTS if E in line), None)
        if not ev_hit:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        e = o.get("event")
        if e not in KEEP:
            continue
        tk = o.get("ticker") or ""
        if e in SLIM:
            counts[ev_hit][(e, tk)] += 1
            if counts[ev_hit][(e, tk)] > SLIM[e]:
                continue
        d = o.get("details", {})
        keep_d = {k: d.get(k) for k in ("price", "cell", "action", "label", "success",
                  "fill_price", "posted_price", "qty", "play_type", "source", "direction",
                  "anchor_src", "table_src", "reference_source", "target_bid", "current_price",
                  "exit_price", "band_x", "entry_price", "pnl_cents", "settle",
                  "proposed_target", "walk_ceiling", "conception_cell", "cap",
                  "from", "to", "leg1_basis", "goal", "goal_level", "level", "aim",
                  "tts_min", "trades_in_window", "grace_sec", "graced",
                  "entry_minus_fv_burst", "fv_mid", "s1_posted", "is_taker", "avg",
                  "cell_id", "sibling_bid") if k in d}
        chains[ev_hit].append({"ts": o.get("ts_epoch"), "et_str": o.get("ts", "")[11:22],
                               "e": e, "tk": tk[-8:], "d": keep_d, "log": lp[-13:-6]})

# ---- exchange truth per ticker ----
truth = {}
for E in EVENTS:
    # discover leg tickers from chain + market API
    tks = sorted({c["tk"] for c in chains[E] if c["tk"]})
    full_tks = set()
    r = g(f"/events/{E}")
    for m in (r.get("markets") or []):
        full_tks.add(m["ticker"])
        truth.setdefault(m["ticker"], {})["result"] = m.get("result")
        truth[m["ticker"]]["status"] = m.get("status")
    for tk in full_tks:
        fl = g(f"/portfolio/fills?ticker={tk}&limit=200").get("fills", [])
        buys = [(float(f.get("count_fp", 0)), round(float(f.get("yes_price_dollars", 0)) * 100),
                 bool(f.get("is_taker")), f.get("created_time", "")) for f in fl if f.get("action") == "buy"]
        sells = [(float(f.get("count_fp", 0)), round(float(f.get("yes_price_dollars", 0)) * 100),
                  bool(f.get("is_taker")), f.get("created_time", "")) for f in fl if f.get("action") == "sell"]
        bq = sum(b[0] for b in buys); sq = sum(s[0] for s in sells)
        cost = sum(b[0] * b[1] for b in buys); rev = sum(s[0] * s[1] for s in sells)
        res = truth.get(tk, {}).get("result")
        settle_qty = bq - sq
        settle_rev = settle_qty * 100 if (res == "yes" and settle_qty > 0) else 0
        pnl_c = rev + settle_rev - cost if bq > 0 else 0
        truth[tk].update({"buy_qty": bq, "avg_buy": round(cost / bq, 1) if bq else None,
                          "sell_qty": sq, "avg_sell": round(rev / sq, 1) if sq else None,
                          "taker_buys": sum(1 for b in buys if b[2]),
                          "open_qty": settle_qty if truth.get(tk, {}).get("status") != "finalized" else 0,
                          "pnl_cents": round(pnl_c, 1)})

json.dump({"chains": chains, "truth": truth},
          open("/tmp/causal_audit.json", "w"), default=str)
print("events:", len(EVENTS), "| chain lines:", sum(len(v) for v in chains.values()),
      "| tickers with truth:", len(truth))
