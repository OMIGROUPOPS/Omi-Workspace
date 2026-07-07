#!/usr/bin/env python3
"""READ-ONLY forensic pass 2: true dup buys (qty>lot), naked $ at real marks,
restart-window attribution. Lot = sizing.entry_contracts = 5."""
import json, sys, time
sys.path.insert(0, "/root")
from forensic_pull_20260707 import load_creds, get, paged

CUTOFF = "2026-07-07T04:00:00Z"
LOT = 5.0
# ET restart windows (UTC): boots at 05:07:21, 06:07:01, 06:34:20 Jul7; 16:15:50, 19:26:13 Jul6
BOOTS = ["2026-07-06T16:15:50Z", "2026-07-06T19:26:13Z",
         "2026-07-07T05:07:21Z", "2026-07-07T06:07:01Z", "2026-07-07T06:34:20Z"]


def f(x):
    return float(x or 0)


def boot_window(ts):
    prior = [b for b in BOOTS if b <= ts]
    return ("boot@" + prior[-1]) if prior else "pre-Jul6-12:15ET"


def main():
    ak, pk = load_creds()
    j = json.load(open("/root/forensic_20260707.json"))
    fills, orders = j["fills"], j["resting_orders"]

    raw_pos = paged(ak, pk, "/trade-api/v2/portfolio/positions?limit=200", "market_positions")
    pos = {p["ticker"]: f(p["position_fp"]) for p in raw_pos if f(p["position_fp"]) != 0}

    sells, buys = {}, {}
    for o in orders:
        row = {"oid": o["order_id"], "px": f(o["yes_price_dollars"]) * 100,
               "rem": f(o["remaining_count_fp"]), "ts": o["created_time"]}
        (sells if o["action"] == "sell" else buys).setdefault(o["ticker"], []).append(row)

    buys_all, sells_all = {}, {}
    for x in fills:
        d = {"ts": x["created_time"], "px": f(x["yes_price_dollars"]) * 100,
             "qty": f(x["count_fp"]), "oid": x["order_id"], "taker": x["is_taker"]}
        (buys_all if x["action"] == "buy" else sells_all).setdefault(x["ticker"], []).append(d)
    for d in (buys_all, sells_all):
        for tk in d:
            d[tk].sort(key=lambda r: r["ts"])

    marks = {}
    for tk in pos:
        try:
            m = get(ak, pk, "/trade-api/v2/markets/%s" % tk).get("market", {})
            marks[tk] = {"bid": f(m.get("yes_bid_dollars")) * 100,
                         "ask": f(m.get("yes_ask_dollars")) * 100,
                         "last": f(m.get("last_price_dollars")) * 100,
                         "status": m.get("status")}
        except Exception as e:
            marks[tk] = {"error": str(e), "bid": 0, "status": "?"}
        time.sleep(0.1)

    # ---- TRUE dups: net bought since midnight > LOT, or held > LOT ----
    dup = {}
    for tk in sorted(set(list(buys_all) + list(pos))):
        recent = [r for r in buys_all.get(tk, []) if r["ts"] >= CUTOFF]
        bought = sum(r["qty"] for r in recent)
        held = pos.get(tk, 0)
        if bought > LOT + 0.01 or held > LOT + 0.01:
            bf = buys_all.get(tk, [])
            basis = sum(r["px"] * r["qty"] for r in bf) / max(sum(r["qty"] for r in bf), 1e-9)
            dup[tk] = {
                "held": held, "bought_since_0000ET": bought,
                "n_buy_orders_since": len({r["oid"] for r in recent}),
                "basis_48h_wavg": round(basis, 2),
                "mark_bid": marks.get(tk, {}).get("bid"),
                "buy_fills_48h": [dict(r, window=boot_window(r["ts"])) for r in bf],
                "sell_fills_48h": sells_all.get(tk, []),
            }

    # ---- coverage at real marks ----
    cov = []
    for tk, held in sorted(pos.items()):
        resting = sum(r["rem"] for r in sells.get(tk, []))
        naked = held - resting
        cov.append({"ticker": tk, "held": held, "resting_sell": resting,
                    "naked": round(naked, 2), "sell_orders": sells.get(tk, []),
                    "open_buys": buys.get(tk, []),
                    "mark_bid": marks.get(tk, {}).get("bid"),
                    "status": marks.get(tk, {}).get("status")})
    naked_legs = [c for c in cov if c["naked"] > 0.01]

    out = {"positions": pos, "marks": marks, "dup": dup, "coverage": cov,
           "summary": {
               "n_positions": len(pos), "n_dup_tickers": len(dup),
               "n_naked_legs": len(naked_legs),
               "naked_qty": round(sum(c["naked"] for c in naked_legs), 2),
               "naked_dollars_at_bid": round(sum(
                   c["naked"] * (c["mark_bid"] or 0) / 100 for c in naked_legs), 2)}}
    json.dump(out, open("/root/forensic_analysis2_20260707.json", "w"), indent=1)

    print(json.dumps(out["summary"], indent=1))
    print("\n== TRUE DUP/MULTI-BUY (bought>5 since 00:00ET or held>5) ==")
    for tk, d in dup.items():
        print("%s held=%g bought_since=%g orders=%d basis=%.1f bid=%s" % (
            tk, d["held"], d["bought_since_0000ET"], d["n_buy_orders_since"],
            d["basis_48h_wavg"], d["mark_bid"]))
        for r in d["buy_fills_48h"]:
            print("   BUY %s px=%g qty=%g taker=%s oid=%s %s" % (
                r["ts"], r["px"], r["qty"], r["taker"], r["oid"][:13], r["window"]))
    print("\n== NAKED LEGS (real marks) ==")
    for c in naked_legs:
        print(" %-45s held=%-6g resting=%-5g naked=%-5g bid=%-4g $naked=%.2f %s" % (
            c["ticker"], c["held"], c["resting_sell"], c["naked"], c["mark_bid"] or 0,
            c["naked"] * (c["mark_bid"] or 0) / 100, c["status"]))


if __name__ == "__main__":
    main()
