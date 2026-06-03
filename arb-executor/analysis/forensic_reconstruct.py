#!/usr/bin/env python3
"""READ-ONLY per-position lifecycle reconstruction for the cutoff-window cohorts (26JUN01/02/03).
Joins Kalshi fills (is_taker ground truth) + settlements + open positions + resting orders.
Computes P&L two ways (cost-derived vs revenue-field-derived) to catch the T57 100x class.
Outputs a per-leg record + pair-combined-basis (over-100 / 108 check). No log join here."""
import json
from collections import defaultdict

D = json.load(open("/tmp/forensic_data.json"))
WIN = ("26JUN01", "26JUN02", "26JUN03")


def inwin(tk):
    return any(w in tk for w in WIN)


def c(x):
    return round(float(x) * 100)  # dollars-string -> cents int


fills = [f for f in D["fills"] if inwin(f.get("ticker", ""))]
setts = {s["ticker"]: s for s in D["settlements"] if inwin(s.get("ticker", ""))}
posns = {p["ticker"]: p for p in D["positions"] if inwin(p.get("ticker", ""))}
orders = [o for o in D["orders"] if inwin(o.get("ticker", ""))]

# group fills by ticker
byf = defaultdict(list)
for f in fills:
    byf[f["ticker"]].append(f)

# universe of legs = any ticker with fills, a settlement w/ nonzero count, an open posn, or a resting order
legs = set(byf) | {t for t, s in setts.items() if float(s.get("yes_count_fp", 0)) or float(s.get("no_count_fp", 0))}
legs |= {t for t, p in posns.items() if float(p.get("position_fp", 0))}
legs |= {o["ticker"] for o in orders}

# event (pair) -> legs, for combined-basis
def event_of(tk):
    return tk.rsplit("-", 1)[0]


ev_entry_basis = defaultdict(dict)  # event -> {leg: entry_avg_cents}

records = []
for tk in sorted(legs):
    fs = sorted(byf.get(tk, []), key=lambda x: x["created_time"])
    buys = [f for f in fs if f["action"] == "buy"]
    sells = [f for f in fs if f["action"] == "sell"]

    def avg(side_fills, pricefield):
        tot = sum(float(f["count_fp"]) for f in side_fills)
        if not tot:
            return None, 0, None
        wp = sum(float(f["count_fp"]) * c(f[pricefield]) for f in side_fills) / tot
        tk_mix = sum(1 for f in side_fills if f["is_taker"])
        return round(wp, 1), tot, (tk_mix, len(side_fills))

    # outcome side we actually traded: most fills carry outcome_side; entries are buys of that outcome
    # price we paid = yes_price_dollars if we bought yes outcome, else no_price_dollars
    def entry_px(f):
        return c(f["yes_price_dollars"]) if f.get("outcome_side") == "yes" else c(f["no_price_dollars"])

    buy_tot = sum(float(f["count_fp"]) for f in buys)
    buy_cost_c = sum(float(f["count_fp"]) * entry_px(f) for f in buys)
    buy_avg = round(buy_cost_c / buy_tot, 1) if buy_tot else None
    buy_taker = sum(1 for f in buys if f["is_taker"])
    sell_tot = sum(float(f["count_fp"]) for f in sells)
    sell_avg = round(sum(float(f["count_fp"]) * (c(f["yes_price_dollars"]) if f.get("outcome_side") == "yes" else c(f["no_price_dollars"])) for f in sells) / sell_tot, 1) if sell_tot else None
    sell_taker = sum(1 for f in sells if f["is_taker"])
    outc = buys[0].get("outcome_side") if buys else (fs[0].get("outcome_side") if fs else "?")

    p = posns.get(tk, {})
    pos_fp = float(p.get("position_fp", 0))
    realized = float(p.get("realized_pnl_dollars", 0)) if p else None
    exposure = float(p.get("market_exposure_dollars", 0)) if p else None

    s = setts.get(tk)
    settled = s is not None
    pnl_cost = None
    pnl_rev = None
    result = None
    if settled:
        result = s.get("market_result")
        yc = float(s.get("yes_count_fp", 0)); nc = float(s.get("no_count_fp", 0))
        ycost = float(s.get("yes_total_cost_dollars", 0)); ncost = float(s.get("no_total_cost_dollars", 0))
        fee = float(s.get("fee_cost", 0))
        payout = (yc if result == "yes" else nc) * 1.00  # each winning contract pays $1
        pnl_cost = round(payout - ycost - ncost - fee, 2)
        rev = s.get("revenue", 0)
        pnl_rev = round(rev - (ycost + ncost) - fee, 2)  # if revenue were dollars (the buggy interpretation)

    if buy_avg is not None:
        ev_entry_basis[event_of(tk)][tk] = buy_avg

    rest = [(o["action"], c(o["yes_price_dollars"]) if o.get("outcome_side") == "yes" else c(o["no_price_dollars"]), float(o["remaining_count_fp"])) for o in orders if o["ticker"] == tk]

    records.append({
        "ticker": tk, "outcome": outc,
        "entry_n": buy_tot, "entry_avg_c": buy_avg, "entry_taker": "%d/%d" % (buy_taker, len(buys)) if buys else "-",
        "exit_n": sell_tot, "exit_avg_c": sell_avg, "exit_taker": "%d/%d" % (sell_taker, len(sells)) if sells else "-",
        "pos_now": pos_fp, "exposure": exposure, "realized$": realized,
        "settled": settled, "result": result, "pnl_cost$": pnl_cost, "pnl_rev$": pnl_rev,
        "resting": rest,
        "first_fill": fs[0]["created_time"][:19] if fs else None,
        "last_fill": fs[-1]["created_time"][:19] if fs else None,
    })

# ---- print per-leg ----
print("=" * 160)
print("PER-LEG LIFECYCLE (cohorts 26JUN01/02/03)  -- %d legs" % len(records))
print("=" * 160)
hdr = "%-46s %3s %5s %6s %5s %6s %6s %7s %8s %5s %8s %8s" % (
    "TICKER", "out", "eN", "eAvg", "etak", "xN", "xAvg", "posNow", "realiz$", "setl", "pnlCost", "pnlRev")
print(hdr)
print("-" * 160)
for r in records:
    print("%-46s %3s %5.0f %6s %5s %6.0f %6s %7.0f %8s %5s %8s %8s" % (
        r["ticker"][:46], (r["outcome"] or "?")[:3], r["entry_n"], r["entry_avg_c"], r["entry_taker"],
        r["exit_n"], r["exit_avg_c"] if r["exit_avg_c"] is not None else "-", r["pos_now"],
        ("%.2f" % r["realized$"]) if r["realized$"] is not None else "-", "Y" if r["settled"] else "n",
        ("%.2f" % r["pnl_cost$"]) if r["pnl_cost$"] is not None else "-",
        ("%.2f" % r["pnl_rev$"]) if r["pnl_rev$"] is not None else "-"))

# ---- pair combined basis (over-100 / 108 check) ----
print("\n" + "=" * 80)
print("PAIR COMBINED ENTRY BASIS (both legs bought) -- over-100 / 108 check")
print("=" * 80)
for ev, d in sorted(ev_entry_basis.items()):
    if len(d) >= 2:
        tot = sum(d.values())
        flag = "  *** OVER-100" if tot > 100 else ""
        print("  %-44s  %s  = %.0f%s" % (ev.replace("KX", "")[:44], " + ".join("%s:%.0f" % (k.rsplit("-", 1)[1], v) for k, v in d.items()), tot, flag))

# ---- P&L reconciliation summary ----
print("\n" + "=" * 80)
print("SETTLEMENT P&L RECONCILE (cost-derived vs revenue-field-derived)")
print("=" * 80)
sc = sum(r["pnl_cost$"] for r in records if r["pnl_cost$"] is not None)
sr = sum(r["pnl_rev$"] for r in records if r["pnl_rev$"] is not None)
print("  sum settled pnl (cost-derived) : $%.2f" % sc)
print("  sum settled pnl (revenue-field): $%.2f   (divergence => revenue units bug if large)" % sr)
print("  open positions (pos_fp != 0)   :", sum(1 for r in records if r["pos_now"]))
print("  resting orders                 :", sum(len(r["resting"]) for r in records))
json.dump(records, open("/tmp/forensic_records.json", "w"), default=str)
print("\nrecords -> /tmp/forensic_records.json")
