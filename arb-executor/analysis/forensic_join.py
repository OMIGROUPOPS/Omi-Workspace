#!/usr/bin/env python3
"""READ-ONLY forensic join: Kalshi fills/settlements (ground truth) + bot-log events.
Per-leg lifecycle + bug-class quantification (T50 backwards, entry_mode mislabel, held-into-live,
cancel churn, reconcile mismatch, orphans, fill-based P&L reconcile). Cohorts 26JUN01/02/03."""
import json, glob
from collections import defaultdict

D = json.load(open("/tmp/forensic_data.json"))
WIN = ("26JUN01", "26JUN02", "26JUN03")
inwin = lambda tk: any(w in tk for w in WIN)
c = lambda x: round(float(x) * 100)
ev_of = lambda tk: tk.rsplit("-", 1)[0]

# ---------- Kalshi side ----------
fills = [f for f in D["fills"] if inwin(f.get("ticker", ""))]
setts = {s["ticker"]: s for s in D["settlements"] if inwin(s.get("ticker", ""))}
posns = {p["ticker"]: p for p in D["positions"] if inwin(p.get("ticker", ""))}
orders = [o for o in D["orders"] if inwin(o.get("ticker", ""))]
byf = defaultdict(list)
for f in fills:
    byf[f["ticker"]].append(f)
px = lambda f: c(f["yes_price_dollars"]) if f.get("outcome_side") == "yes" else c(f["no_price_dollars"])

# ---------- log side ----------
place, filled, xposted, xfilled, holdsettle, recon_mm = {}, {}, {}, {}, {}, []
cancels = defaultdict(lambda: {"n": 0, "spreads": []})
orphan, pbskip, matchlive_ev, skiplive_ev, mlcancel = [], [], set(), set(), []
WANT = ("v4_place", "entry_filled", "v4_exit_posted", "exit_filled", "v4_resting_cancel",
        "paired_basis_skip", "match_live_detected", "skip_live_match", "reconcile_price_mismatch",
        "orphan_buy_cancelled", "hold_to_settle", "match_live_resting_cancel", "entry_cancelled")
for logf in sorted(glob.glob("logs/live_v3_2026060*.jsonl")):
    for line in open(logf, errors="replace"):
        if '"event"' not in line:
            continue
        if not any(w in line for w in WANT):
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        e = r.get("event"); tk = r.get("ticker", ""); d = r.get("details", {})
        evk = d.get("event", "")  # event_ticker for ticker-less rows
        if e == "v4_place":
            place.setdefault(tk, []).append(d)
        elif e == "entry_filled":
            filled[tk] = d
        elif e == "v4_exit_posted":
            xposted[tk] = d
        elif e == "exit_filled":
            xfilled.setdefault(tk, []).append(d)
        elif e == "hold_to_settle":
            holdsettle[tk] = d
        elif e == "v4_resting_cancel":
            cancels[tk]["n"] += 1
            if "spread" in d:
                cancels[tk]["spreads"].append(d["spread"])
        elif e == "paired_basis_skip":
            pbskip.append(d)
        elif e == "match_live_detected":
            matchlive_ev.add(evk)
        elif e == "skip_live_match":
            skiplive_ev.add(evk)
        elif e == "match_live_resting_cancel":
            mlcancel.append(tk or evk)
        elif e == "reconcile_price_mismatch":
            recon_mm.append((tk, d))
        elif e == "orphan_buy_cancelled":
            orphan.append((tk, d))

# ---------- per-leg fill-based P&L + join ----------
legs = set(byf) | {t for t, s in setts.items() if float(s.get("yes_count_fp", 0)) or float(s.get("no_count_fp", 0))} \
       | {t for t, p in posns.items() if float(p.get("position_fp", 0))} | {o["ticker"] for o in orders} | set(place)
legs = {t for t in legs if inwin(t)}

rows = []
total_realized = 0.0
for tk in sorted(legs):
    fs = sorted(byf.get(tk, []), key=lambda x: x["created_time"])
    buys = [f for f in fs if f["action"] == "buy"]
    sells = [f for f in fs if f["action"] == "sell"]
    bq = sum(float(f["count_fp"]) for f in buys); sq = sum(float(f["count_fp"]) for f in sells)
    bcost = sum(float(f["count_fp"]) * px(f) for f in buys) / 100.0      # $
    sproc = sum(float(f["count_fp"]) * px(f) for f in sells) / 100.0     # $
    bavg = round(bcost * 100 / bq, 1) if bq else None
    savg = round(sproc * 100 / sq, 1) if sq else None
    btak = sum(1 for f in buys if f["is_taker"]);
    fee = sum(float(f.get("fee_cost", 0)) for f in fs)
    net = bq - sq  # contracts still held of the bought outcome
    s = setts.get(tk); result = s.get("market_result") if s else None
    outc = (buys[0] if buys else fs[0]).get("outcome_side") if fs else "?"
    # settlement payout on net held: win if our outcome == result
    payout = 0.0
    if s and net > 0:
        if result == "scalar":
            payout = net * float(s.get("value", 0)) / 100.0   # retirement/void: proportional payout in cents
        else:
            payout = net * (1.00 if outc == result else 0.0)
    pnl = round(sproc - bcost + payout - fee, 2)
    if s or net == 0:  # realized (settled or fully closed)
        total_realized += pnl
    # log joins
    pl = place.get(tk, [{}])[-1]
    fl = filled.get(tk, {})
    xp = xposted.get(tk, {})
    xf = xfilled.get(tk, [])
    rows.append({
        "tk": tk, "outc": outc, "bq": bq, "bavg": bavg, "btak": "%d/%d" % (btak, len(buys)) if buys else "-",
        "sq": sq, "savg": savg, "net": net, "result": result,
        "pnl": pnl, "settled": s is not None,
        "offset": pl.get("offset"), "emode": pl.get("entry_mode"), "ptype": fl.get("play_type"),
        "band_x": xp.get("band_x"), "exit_posted_px": xp.get("exit_price"),
        "xfill_pnl": round(sum(x.get("pnl_dollars", 0) for x in xf), 2) if xf else None,
        "cancels": cancels[tk]["n"], "held": tk in holdsettle,
    })

# ---------- OUTPUT ----------
print("=" * 175)
print("PER-LEG LIFECYCLE + FILL-BASED P&L  (cohorts 26JUN01/02/03, %d legs)" % len(rows))
print("=" * 175)
print("%-44s %3s %3s %5s %5s %3s %5s %4s %4s %-13s %-13s %4s %5s %6s %4s" % (
    "TICKER", "out", "bq", "bavg", "savg", "net", "rslt", "off", "bnd", "entry_mode", "play_type", "canc", "held", "PNL$", "set"))
print("-" * 175)
for r in rows:
    print("%-44s %3s %3.0f %5s %5s %3.0f %5s %4s %4s %-13s %-13s %4d %5s %6s %4s" % (
        r["tk"][:44], (r["outc"] or "?")[:3], r["bq"], r["bavg"], r["savg"] if r["savg"] is not None else "-",
        r["net"], (r["result"] or "-")[:4], str(r["offset"]) if r["offset"] is not None else "-",
        str(r["band_x"]) if r["band_x"] is not None else "-", (r["emode"] or "-")[:13], (r["ptype"] or "-")[:13],
        r["cancels"], "Y" if r["held"] else "-", "%.2f" % r["pnl"], "Y" if r["settled"] else "n"))
print("-" * 175)
print("TOTAL realized P&L (fill-based, settled+closed): $%.2f" % total_realized)

# ---- BUG 1: T50 paired_basis_skip distribution (backwards?) ----
print("\n" + "=" * 90)
print("BUG-1  T50 paired_basis_skip: %d total. Was any FAIR leg (combined<=cap) blocked?" % len(pbskip))
combs = [d.get("combined", 0) for d in pbskip]
caps = [d.get("cap", 99) for d in pbskip]
wrong = [d for d in pbskip if d.get("combined", 0) <= d.get("cap", 99)]
print("  combined distribution: min=%d max=%d  | blocked with combined<=cap (WRONG/backwards): %d" % (
    min(combs) if combs else 0, max(combs) if combs else 0, len(wrong)))
for d in wrong[:8]:
    print("    WRONG-BLOCK: %s this=%d sibling=%s cost=%d combined=%d cap=%d" % (
        d.get("event", "")[-18:], d.get("this_price"), d.get("sibling"), d.get("sibling_cost"), d.get("combined"), d.get("cap")))
import collections
ev_blocked = collections.Counter(d.get("event", "") for d in pbskip)
print("  distinct events with a basis-skip: %d (these are pairs where a 2nd leg was correctly prevented)" % len(ev_blocked))

# ---- BUG 4: entry_mode mislabel vs is_taker ----
print("\n" + "=" * 90)
print("BUG-4  entry_mode/play_type (intent) vs is_taker (truth) -- per ENTRY leg")
mism = 0; tot = 0; maker_true = 0
for r in rows:
    if r["bq"] <= 0:
        continue
    tot += 1
    fs = [f for f in byf[r["tk"]] if f["action"] == "buy"]
    any_taker = any(f["is_taker"] for f in fs)
    if not any_taker:
        maker_true += 1
    intent_maker = (r["ptype"] or r["emode"] or "").find("maker") >= 0 or (r["emode"] == "resting_maker")
    if intent_maker and any_taker:
        mism += 1
print("  entry legs: %d | genuine maker (is_taker all false): %d (%.0f%%) | labelled-maker-but-TAKER: %d" % (
    tot, maker_true, 100.0 * maker_true / tot if tot else 0, mism))

# ---- BUG 3: held-into-live (position into live match, no exit) ----
print("\n" + "=" * 90)
print("BUG-3  held-into-live / no-exit:  match_live events=%d  skip_live=%d  match_live_resting_cancel=%d  hold_to_settle=%d" % (
    len(matchlive_ev), len(skiplive_ev), len(mlcancel), len(holdsettle)))
no_exit = [r for r in rows if r["bq"] > 0 and r["band_x"] is None and r["sq"] == 0]
print("  legs with an entry fill but NO exit posted AND no exit fill (held naked to settle): %d" % len(no_exit))
for r in no_exit:
    print("    %-44s entry=%s held=%s pnl=%.2f result=%s" % (r["tk"][:44], r["bavg"], "Y" if r["held"] else "-", r["pnl"], r["result"]))

# ---- cancel churn ----
print("\n" + "=" * 90)
allc = sum(v["n"] for v in cancels.values())
allsp = [s for v in cancels.values() for s in v["spreads"]]
narrow = sum(1 for s in allsp if s <= 5)
print("CANCEL CHURN  v4_resting_cancel total=%d | with spread<=5c (normal book, churn): %d (%.0f%%) | spread>5: %d" % (
    allc, narrow, 100.0 * narrow / len(allsp) if allsp else 0, len(allsp) - narrow))

# ---- reconcile mismatch + orphans ----
print("\n" + "=" * 90)
print("RECONCILE MISMATCH (bot-state vs Kalshi-actual): %d" % len(recon_mm))
for tk, d in recon_mm:
    print("    %-44s bot=%sc/q%s  kalshi=%sc/q%s  delta=%s" % (
        tk[:44], d.get("bot_entry_price"), d.get("entry_qty"), d.get("kalshi_avg_price"), d.get("kalshi_qty"), d.get("delta")))
print("ORPHAN buys cancelled: %d" % len(orphan))
for tk, d in orphan:
    print("    %-44s price=%s qty=%s" % (tk[:44], d.get("price"), d.get("qty")))
