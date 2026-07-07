#!/usr/bin/env python3
"""BLEED ATTRIBUTION 2026-07-07 (STEP 1), v2. Exchange truth, honest era
(Jul-5 10:39:54 ET boot -> now). Dollar-realizes the containment doc's defect
classes and splits daily gross into MECHANICAL vs STRATEGIC.

v2: era-bounded pagination (newest-first, break past era); sell-order
lifecycles from the bot jsonl logs (order_placed/order_cancelled, matched to
executed via fills oids) instead of ~300 per-ticker API pulls; public tape
pulled ONLY for legs that show a naked window with a band on record.

Classes:
  (a) dup/multi-buy surplus (guard replay) -> pro-rata realized + open mark risk
  (b) naked BASE-lot band-touch (KHRYOU class): banked-vs-took, no overlap with (a)
  (c) fractional residues (int-floor invisible)

Assumptions: pro-rata cost within ticker; sell alive qty = posted count
(conservative over-cover); pre-era opening at era-avg basis; marks at yes_bid;
touch = print > band, or prints AT band >= 2x naked qty.
Usage (VPS, in arb-executor): python3 bleed_attribution_20260707.py"""
import json, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, "/root")
from forensic_pull_20260707 import load_creds, get

ERA = "2026-07-05T14:39:54Z"
ERA_EPOCH = datetime(2026, 7, 5, 14, 39, 54, tzinfo=timezone.utc).timestamp()
LOT = 5.0
ET = timezone(timedelta(hours=-4))
LOGS = ["/root/Omi-Workspace/arb-executor/logs/live_v3_20260705.jsonl",
        "/root/Omi-Workspace/arb-executor/logs/live_v3_20260706.jsonl",
        "/root/Omi-Workspace/arb-executor/logs/live_v3_20260707.jsonl"]


def f(x):
    return float(x or 0)


def ts_parse(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def et_day(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(ET).strftime("%m-%d")


def et_day_ep(ep):
    return datetime.fromtimestamp(ep, ET).strftime("%m-%d")


def paged_until(ak, pk, base, key, tsfield):
    """Newest-first cursor walk; stop once a page's oldest row predates ERA."""
    out, cur = [], None
    while True:
        j = get(ak, pk, base + ("&cursor=%s" % cur if cur else ""))
        rows = j.get(key) or []
        out.extend(rows)
        cur = j.get("cursor")
        if not cur or not rows or (rows[-1].get(tsfield, "") < ERA):
            return [r for r in out if r.get(tsfield, "") >= ERA]
        time.sleep(0.1)


def main():
    ak, pk = load_creds()

    fills = paged_until(ak, pk, "/trade-api/v2/portfolio/fills?limit=200", "fills", "created_time")
    tickers = sorted({x["ticker"] for x in fills})

    setl = {}
    for s in paged_until(ak, pk, "/trade-api/v2/portfolio/settlements?limit=200",
                         "settlements", "settled_time"):
        setl.setdefault(s["ticker"], (s["market_result"], s["settled_time"]))

    pos_now, cur = {}, None
    while True:
        j = get(ak, pk, "/trade-api/v2/portfolio/positions?limit=200" +
                ("&cursor=%s" % cur if cur else ""))
        rows = j.get("market_positions") or []
        for p in rows:
            if f(p["position_fp"]) != 0:
                pos_now[p["ticker"]] = f(p["position_fp"])
        cur = j.get("cursor")
        if not cur or not rows:
            break
    marks = {}
    for tk in pos_now:
        try:
            m = get(ak, pk, "/trade-api/v2/markets/%s" % tk).get("market", {})
            marks[tk] = f(m.get("yes_bid_dollars")) * 100
        except Exception:
            marks[tk] = 0.0
        time.sleep(0.06)

    # ---- ledger ----
    led = {}
    for x in fills:
        d = led.setdefault(x["ticker"], {"buys": [], "sells": [], "fees": 0.0})
        row = (x["created_time"], f(x["yes_price_dollars"]) * 100, f(x["count_fp"]), x["order_id"])
        d["fees"] += f(x.get("fee_cost"))
        (d["buys"] if x["action"] == "buy" else d["sells"]).append(row)
    sell_fill_by_oid = {}
    for tk, d in led.items():
        for ts, px, qty, oid in d["sells"]:
            sell_fill_by_oid.setdefault(oid, []).append(ts_parse(ts))

    def ticker_pnl(tk):
        d = led[tk]
        bq = sum(r[2] for r in d["buys"]); sq = sum(r[2] for r in d["sells"])
        bc = sum(r[1] * r[2] for r in d["buys"]); sp = sum(r[1] * r[2] for r in d["sells"])
        avg = bc / bq if bq else 0.0
        net = bq - sq
        realized = sp - avg * sq - d["fees"] * 100
        unreal = 0.0
        if tk in setl:
            realized += (100.0 if setl[tk][0] == "yes" else 0.0) * net - avg * net
        else:
            held = pos_now.get(tk, 0.0)
            unreal = held * (marks.get(tk, 0.0) - avg)
        return realized, unreal, bq, sq, net, avg

    # ---- sell-order lifecycles from jsonl ----
    sell_orders = {}   # tk -> list of {oid, px, qty, t0, t1}
    cancels = {}       # oid -> cancel epoch
    for lp in LOGS:
        p = Path(lp)
        if not p.exists():
            continue
        with p.open() as fh:
            for line in fh:
                if '"order_placed"' not in line and '"order_cancelled"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                ep = e.get("ts_epoch", 0)
                if ep < ERA_EPOCH:
                    continue
                det = e.get("details", {})
                if e["event"] == "order_placed" and det.get("action") == "sell":
                    sell_orders.setdefault(e.get("ticker", ""), []).append(
                        {"oid": det.get("order_id", ""), "px": det.get("price", 0),
                         "qty": f(det.get("count", 0)), "t0": ep, "t1": None})
                elif e["event"] == "order_cancelled" and det.get("success"):
                    cancels[det.get("order_id", "")] = ep
    now_ep = time.time()
    for tk, lst in sell_orders.items():
        for o in lst:
            fills_o = sell_fill_by_oid.get(o["oid"], [])
            t_exec = max(fills_o) if fills_o else None
            t_can = cancels.get(o["oid"])
            ends = [t for t in (t_exec, t_can) if t]
            o["t1"] = min(ends) if ends else (ts_parse(setl[tk][1]) if tk in setl else now_ep)

    # ---- class (a) ----
    class_a = {}
    for tk in tickers:
        d = led[tk]
        xs = sorted([("buy",) + r for r in d["buys"]] + [("sell",) + r for r in d["sells"]],
                    key=lambda r: r[1])
        net_all = sum(r[2] for r in d["buys"]) - sum(r[2] for r in d["sells"])
        held = max(0.0, pos_now.get(tk, 0.0) - net_all)
        surplus, first_ts, seen = 0.0, None, {}
        for kind, ts, px, qty, oid in xs:
            if kind == "sell":
                held = max(0.0, held - qty); continue
            if oid in seen:
                if seen[oid] == "blocked":
                    surplus += qty; first_ts = first_ts or ts
                else:
                    held += qty
                continue
            if held + qty > LOT + 0.01:
                seen[oid] = "blocked"; surplus += qty; first_ts = first_ts or ts
            else:
                seen[oid] = "ok"; held += qty
        if surplus > 0.009:
            realized, unreal, bq, sq, net, avg = ticker_pnl(tk)
            frac = surplus / bq if bq else 0.0
            class_a[tk] = {"surplus_qty": surplus, "day": et_day(first_ts),
                           "mech_realized_c": realized * frac, "mech_mark_c": unreal * frac,
                           "settled": tk in setl}

    # ---- class (b): naked BASE-lot windows -> tape check ----
    candidates = []
    windows_by_tk = {}
    for tk in tickers:
        so = sell_orders.get(tk, [])
        if not so:
            continue
        band = so[-1]["px"]
        evs = []
        for ts, px, qty, oid in led[tk]["buys"]:
            evs.append((ts_parse(ts), "buy", qty))
        for ts, px, qty, oid in led[tk]["sells"]:
            evs.append((ts_parse(ts), "sell", qty))
        end_t = ts_parse(setl[tk][1]) if tk in setl else now_ep
        for o in so:
            evs.append((o["t0"], "cover+", o["qty"]))
            evs.append((min(o["t1"], end_t), "cover-", o["qty"]))
        evs.sort()
        held = cov = 0.0
        prev_t, open_naked, wins = None, 0.0, []
        for t, kind, q in evs:
            if open_naked > 0.009 and prev_t is not None and t > prev_t:
                wins.append((prev_t, t, open_naked))
            if kind == "buy": held += q
            elif kind == "sell": held = max(0.0, held - q)
            elif kind == "cover+": cov += q
            else: cov = max(0.0, cov - q)
            prev_t = t
            open_naked = max(0.0, min(held, LOT) - cov)
        if open_naked > 0.009 and prev_t is not None and end_t > prev_t:
            wins.append((prev_t, end_t, open_naked))
        wins = [(a, b, q) for a, b, q in wins if b - a > 60]
        if wins:
            candidates.append(tk)
            windows_by_tk[tk] = (band, wins)

    class_b = {}
    for tk in candidates:
        band, wins = windows_by_tk[tk]
        try:
            trades, cur = [], None
            while True:
                j = get(ak, pk, "/trade-api/v2/markets/trades?ticker=%s&limit=1000" % tk +
                        ("&cursor=%s" % cur if cur else ""))
                rows = j.get("trades") or []
                trades.extend(rows)
                cur = j.get("cursor")
                if not cur or not rows or rows[-1].get("created_time", "") < ERA:
                    break
            time.sleep(0.08)
        except Exception:
            continue

        def tpx(t):
            if t.get("yes_price_dollars") is not None:
                return round(f(t["yes_price_dollars"]) * 100)
            return round(f(t.get("yes_price", 0)))
        tr = [(ts_parse(t["created_time"]), tpx(t), f(t.get("count_fp", t.get("count", 0))))
              for t in trades if t.get("created_time", "") >= ERA]
        touched = 0.0
        for a, b, q in wins:
            above = any(a <= x[0] <= b and x[1] > band for x in tr)
            atband = sum(x[2] for x in tr if a <= x[0] <= b and x[1] == band)
            if above or atband >= 2 * q:
                touched = max(touched, q)
        if touched <= 0.009:
            continue
        if tk in setl:
            out_px = 100.0 if setl[tk][0] == "yes" else 0.0
            day, settled = et_day(setl[tk][1]), True
        else:
            out_px, day, settled = marks.get(tk, 0.0), "07-07", False
        delta = touched * (band - out_px)
        if delta > 0.5:
            class_b[tk] = {"naked_qty": touched, "band": band, "outcome_px": out_px,
                           "delta_c": delta, "day": day, "settled": settled,
                           "n_windows": len(wins)}

    # ---- class (c) ----
    class_c = {}
    for tk in tickers:
        realized, unreal, bq, sq, net, avg = ticker_pnl(tk)
        pos_q = pos_now.get(tk, 0.0) if tk not in setl else max(0.0, net)
        frac_part = pos_q - int(pos_q)
        if 0.009 < frac_part < 1.0:
            out = (100.0 if setl[tk][0] == "yes" else 0.0) if tk in setl else marks.get(tk, 0.0)
            class_c[tk] = {"frac": round(frac_part, 2), "c": frac_part * (out - avg),
                           "day": et_day(setl[tk][1]) if tk in setl else "07-07"}

    # ---- daily gross realized ----
    daily = {}
    fees_total = 0.0
    for tk in tickers:
        d = led[tk]
        bq = sum(r[2] for r in d["buys"]); bc = sum(r[1] * r[2] for r in d["buys"])
        avg = bc / bq if bq else 0.0
        fees_total += d["fees"] * 100
        for ts, px, qty, _ in d["sells"]:
            daily[et_day(ts)] = daily.get(et_day(ts), 0.0) + (px - avg) * qty
        if tk in setl:
            res, st = setl[tk]
            net = bq - sum(r[2] for r in d["sells"])
            daily[et_day(st)] = daily.get(et_day(st), 0.0) + ((100.0 if res == "yes" else 0.0) - avg) * net

    out = {"era": ERA, "n_fills": len(fills), "n_tickers": len(tickers), "n_settled": len(setl),
           "n_b_candidates": len(candidates), "n_sell_order_tickers": len(sell_orders),
           "class_a": class_a, "class_b": class_b, "class_c": class_c,
           "daily_gross_c": daily, "fees_c": fees_total}
    json.dump(out, open("/root/bleed_attribution_20260707.json", "w"), indent=1)

    def usd(c):
        return c / 100.0

    print("STATS fills=%d tickers=%d settled=%d b_candidates=%d" %
          (len(fills), len(tickers), len(setl), len(candidates)))
    print()
    print("## CLASS (a) dup/multi-buy surplus")
    print("| ticker | day | surplus sh | realized $ | mark risk $ | settled |")
    print("|---|---|---|---|---|---|")
    for tk, v in sorted(class_a.items(), key=lambda kv: kv[1]["mech_realized_c"]):
        print("| %s | %s | %g | %+.2f | %+.2f | %s |" % (
            tk, v["day"], v["surplus_qty"], usd(v["mech_realized_c"]),
            usd(v["mech_mark_c"]), "Y" if v["settled"] else "open"))
    ar = sum(v["mech_realized_c"] for v in class_a.values())
    am = sum(v["mech_mark_c"] for v in class_a.values())
    print("(a) TOTAL: %d tickers | realized %+.2f | mark risk %+.2f" % (len(class_a), usd(ar), usd(am)))
    print()
    print("## CLASS (b) naked base-lot, band touched")
    print("| ticker | day | naked sh | band | outcome | foregone $ | settled |")
    print("|---|---|---|---|---|---|---|")
    for tk, v in sorted(class_b.items(), key=lambda kv: -kv[1]["delta_c"]):
        print("| %s | %s | %g | %d | %g | %.2f | %s |" % (
            tk, v["day"], v["naked_qty"], v["band"], v["outcome_px"],
            usd(v["delta_c"]), "Y" if v["settled"] else "open"))
    br = sum(v["delta_c"] for v in class_b.values())
    br_settled = sum(v["delta_c"] for v in class_b.values() if v["settled"])
    print("(b) TOTAL: %d legs | foregone %.2f (settled portion %.2f)" % (len(class_b), usd(br), usd(br_settled)))
    print()
    cr = sum(v["c"] for v in class_c.values())
    print("## CLASS (c) fractional residues: %d legs | net %+.2f" % (len(class_c), usd(cr)))
    for tk, v in sorted(class_c.items(), key=lambda kv: kv[1]["c"]):
        print("| %s | %s | %.2f | %+.2f |" % (tk, v["day"], v["frac"], usd(v["c"])))
    print()
    print("## DAILY GROSS (realized) | fees total %.2f" % usd(fees_total))
    mech_day = {}
    for v in class_a.values():
        if v["settled"]:
            mech_day[v["day"]] = mech_day.get(v["day"], 0.0) + v["mech_realized_c"]
    for v in class_b.values():
        if v["settled"]:
            mech_day[v["day"]] = mech_day.get(v["day"], 0.0) - v["delta_c"]
    for v in class_c.values():
        if v["day"] != "07-07":
            mech_day[v["day"]] = mech_day.get(v["day"], 0.0) + v["c"]
    print("| day | gross $ | mechanical $ | strategic residual $ |")
    print("|---|---|---|---|")
    for day in sorted(daily):
        g, m = usd(daily[day]), usd(mech_day.get(day, 0.0))
        print("| %s | %+.2f | %+.2f | %+.2f |" % (day, g, m, g - m))


if __name__ == "__main__":
    main()
