#!/usr/bin/env python3
"""
Sport-specific Mona Lisa optimization.
Each sport/series gets its own optimal gap, spread, price config.
"""
import csv, os, math
from collections import defaultdict
from datetime import datetime

DATA_DIR = "/root/espn_data"
FILES = {
    "tennis": "tennis_stb_price_matrix.csv",
    "ncaamb": "ncaamb_stb_price_matrix.csv",
    "nba":    "nba_stb_price_matrix.csv",
    "nhl":    "nhl_stb_price_matrix.csv",
}
CONTRACTS = 25

def sf(v, d=None):
    try:
        f = float(v)
        return f if not math.isnan(f) else d
    except:
        return d

def load_all():
    trades = []
    for key, fname in FILES.items():
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path): continue
        with open(path) as f:
            for r in csv.DictReader(f):
                ep = sf(r.get("entry_price"))
                if ep is None: continue
                mid = sf(r.get("entry_combined_mid"), 0)
                spread = sf(r.get("entry_spread_est"), 0)
                gap = mid - ep if mid else 0
                filled = r.get("filled","").lower() in ("true","1","yes")
                fill_time = sf(r.get("fill_time_min"))
                final = sf(r.get("final_price"))
                ttsettle = sf(r.get("time_to_settle_min"), 60)
                hold = fill_time if (filled and fill_time is not None) else (ttsettle if ttsettle else 60)
                osp = sf(r.get("other_side_price"), 0)
                series = r.get("series_type", "")

                # Determine sport_key
                if key == "tennis":
                    sport_key = series  # ATP_CHALL, ATP, WTA_CHALL, WTA
                else:
                    sport_key = key.upper()

                # entry_time for date extraction
                et_str = r.get("entry_time", "")
                entry_date = None
                try:
                    if "T" in et_str:
                        entry_date = et_str[:10]
                    elif et_str:
                        entry_date = datetime.utcfromtimestamp(float(et_str)).strftime("%Y-%m-%d")
                except:
                    pass

                trades.append({
                    "sport_key": sport_key, "ep": ep, "mid": mid, "gap": gap,
                    "spread": spread, "filled": filled, "fill_time": fill_time,
                    "final": final, "hold": hold, "osp": osp, "event": r.get("event",""),
                    "entry_date": entry_date, "entry_time": sf(et_str, 0),
                })
    return trades

def dedup(subset):
    events = set()
    out = []
    for t in subset:
        if t["event"] not in events:
            events.add(t["event"])
            out.append(t)
    return out

def avg(vals):
    v = [x for x in vals if x is not None]
    return sum(v)/len(v) if v else 0

def median(vals):
    v = sorted(x for x in vals if x is not None)
    if not v: return 0
    n = len(v)
    return (v[n//2-1]+v[n//2])/2 if n%2==0 else v[n//2]

def calc_pnl(subset):
    """Return total PnL in dollars for a set of trades."""
    pnl = 0
    for t in subset:
        if t["filled"]:
            pnl += 7 * CONTRACTS / 100
        elif t["final"] is not None and t["final"] >= 50:
            pnl += (100 - t["ep"]) * CONTRACTS / 100
        else:
            pnl -= t["ep"] * CONTRACTS / 100
    return pnl

def calc_drawdown(subset):
    """Max drawdown on time-sorted trades."""
    cum = 0; peak = 0; max_dd = 0; streak = 0; max_streak = 0
    for t in subset:
        if t["filled"]:
            p = 7 * CONTRACTS / 100
        elif t["final"] is not None and t["final"] >= 50:
            p = (100 - t["ep"]) * CONTRACTS / 100
        else:
            p = -(t["ep"]) * CONTRACTS / 100
        cum += p
        if cum > peak: peak = cum
        dd = peak - cum
        if dd > max_dd: max_dd = dd
        if p < 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_dd, max_streak

def run_sport_analysis(sport_name, sport_trades, num_days, out):
    """Full Mona Lisa grid search for one sport."""
    pr = lambda s="": (print(s), out.append(s))

    n_total = len(sport_trades)
    n_filled = len([t for t in sport_trades if t["filled"]])
    n_loss = n_total - n_filled
    base_wr = n_filled / n_total * 100 if n_total else 0
    base_pnl = calc_pnl(sport_trades)
    base_daily = base_pnl / num_days if num_days else 0

    pr("  Trades: %d  Wins: %d  Losses: %d  WR: %.1f%%  PnL: $%.2f ($%.2f/day)" % (
        n_total, n_filled, n_loss, base_wr, base_pnl, base_daily))
    pr("  Avg entry: %.1fc  Avg gap: %.1fc  Avg spread: %.1fc  Avg hold: %.0fm" % (
        avg([t["ep"] for t in sport_trades]),
        avg([t["gap"] for t in sport_trades]),
        avg([t["spread"] for t in sport_trades]),
        avg([t["hold"] for t in sport_trades])))

    fast = [t for t in sport_trades if t["filled"] and t["fill_time"] is not None and t["fill_time"] < 2]
    pr("  Fast fills (<2m): %d (%.1f%%)" % (len(fast), len(fast)/n_total*100 if n_total else 0))

    if n_total < 15:
        pr("  ** TOO FEW TRADES FOR RELIABLE OPTIMIZATION **")
        pr("")
        return None

    # Price bucket analysis
    pr("")
    pr("  Price bucket analysis:")
    pr("  %-8s %5s %5s %6s %6s %8s" % ("Price", "N", "Wins", "WR%", "Fast%", "EV/trade"))
    pr("  " + "-" * 45)
    for lo, hi in [(55,60),(61,65),(66,70),(71,75),(76,80),(81,85),(86,90)]:
        sub = [t for t in sport_trades if lo <= t["ep"] <= hi]
        if not sub: continue
        w = len([t for t in sub if t["filled"]])
        f = len([t for t in sub if t["filled"] and t["fill_time"] is not None and t["fill_time"] < 2])
        wr = w/len(sub)*100
        lr = (len(sub)-w)/len(sub)
        avg_loss = avg([t["ep"] for t in sub if not t["filled"]]) * CONTRACTS / 100 if [t for t in sub if not t["filled"]] else 0
        ev = (w/len(sub)) * 1.75 - lr * avg_loss
        pr("  %-8s %5d %5d %5.1f%% %5.1f%% %7s" % (
            "%d-%dc" % (lo,hi), len(sub), w, wr,
            f/w*100 if w else 0, "$%.3f" % ev))

    # Gap threshold sweep
    pr("")
    pr("  Gap threshold sweep (deduped):")
    pr("  %-8s %5s %5s %5s %6s %6s %8s %7s %5s" % (
        "Gap>=", "N", "Win", "Loss", "WR%", "Fast%", "$/day", "MaxDD", "Strk"))
    pr("  " + "-" * 65)

    best_daily = -999
    best_gap = None
    gap_results = {}

    for g in [0, 5, 6, 8, 10, 12, 15, 20, 25]:
        sub = dedup([t for t in sport_trades if t["gap"] >= g])
        if len(sub) < 10: continue
        sub.sort(key=lambda t: t["entry_time"])
        pnl = calc_pnl(sub)
        daily = pnl / num_days
        w = len([t for t in sub if t["filled"] or (t["final"] is not None and t["final"] >= 50)])
        l = len(sub) - w
        wr = w/len(sub)*100
        f = len([t for t in sub if t["filled"] and t["fill_time"] is not None and t["fill_time"] < 2])
        dd, strk = calc_drawdown(sub)

        marker = ""
        if daily > best_daily:
            best_daily = daily
            best_gap = g
            marker = " <<<"

        gap_results[g] = {"n": len(sub), "wr": wr, "daily": daily, "dd": dd, "strk": strk,
                          "fast_pct": f/w*100 if w else 0}
        pr("  >=%-5d %5d %5d %5d %5.1f%% %5.1f%% %7s %6s %5d%s" % (
            g, len(sub), w, l, wr, f/len(sub)*100 if sub else 0,
            "$%.2f" % daily, "-$%.0f" % dd, strk, marker))

    # Spread sweep at best gap
    pr("")
    pr("  Spread sweep at gap>=%s:" % (best_gap if best_gap is not None else "?"))
    pr("  %-8s %5s %5s %6s %8s" % ("Sprd<=", "N", "Loss", "WR%", "$/day"))
    pr("  " + "-" * 38)

    best_spread = 6
    best_s_daily = -999
    for s in [2, 3, 4, 5, 6, 7, 8]:
        if best_gap is None: break
        sub = dedup([t for t in sport_trades if t["gap"] >= best_gap and t["spread"] <= s])
        if len(sub) < 10: continue
        pnl = calc_pnl(sub)
        daily = pnl / num_days
        w = len([t for t in sub if t["filled"] or (t["final"] is not None and t["final"] >= 50)])
        l = len(sub) - w
        wr = w/len(sub)*100
        marker = ""
        if daily > best_s_daily:
            best_s_daily = daily
            best_spread = s
            marker = " <<<"
        pr("  <=%-5d %5d %5d %5.1f%% %7s%s" % (s, len(sub), l, wr, "$%.2f" % daily, marker))

    # Final optimal config
    if best_gap is not None:
        optimal = dedup([t for t in sport_trades if t["gap"] >= best_gap and t["spread"] <= best_spread])
        optimal.sort(key=lambda t: t["entry_time"])
        pnl = calc_pnl(optimal)
        daily = pnl / num_days
        w = len([t for t in optimal if t["filled"] or (t["final"] is not None and t["final"] >= 50)])
        l = len(optimal) - w
        wr = w/len(optimal)*100
        ff = len([t for t in optimal if t["filled"] and t["fill_time"] is not None and t["fill_time"] < 2])
        dd, strk = calc_drawdown(optimal)
        avg_hold = avg([t["hold"] for t in optimal])
        total_hold = sum(t["hold"] for t in optimal)
        ev_min = (pnl / total_hold) if total_hold > 0 else 0

        pr("")
        pr("  >>> OPTIMAL: gap>=%d  spread<=%d  price 55-90c" % (best_gap, best_spread))
        pr("      Trades: %d  WR: %.1f%%  Fast: %.1f%%  $/day: $%.2f" % (
            len(optimal), wr, ff/len(optimal)*100 if optimal else 0, daily))
        pr("      MaxDD: -$%.0f  MaxStreak: %d  AvgHold: %.0fm" % (dd, strk, avg_hold))
        pr("      EV/min: $%.5f  (%.1f min/$1)" % (ev_min, 1/ev_min if ev_min > 0 else 0))

        return {"gap": best_gap, "spread": best_spread, "n": len(optimal), "wr": wr,
                "daily": daily, "dd": dd, "strk": strk, "fast_pct": ff/len(optimal)*100 if optimal else 0,
                "avg_hold": avg_hold, "ev_min": ev_min}
    return None


# ===========================================================================
# MAIN
# ===========================================================================
out = []
def pr(s=""):
    print(s)
    out.append(s)

trades = load_all()
trades.sort(key=lambda t: t["entry_time"])

pr("=" * 80)
pr("SPORT-SPECIFIC MONA LISA OPTIMIZATION")
pr("%d total trades" % len(trades))
pr("=" * 80)

# Count dates per sport for accurate daily calc
sport_dates = defaultdict(set)
for t in trades:
    if t["entry_date"]:
        sport_dates[t["sport_key"]].add(t["entry_date"])

# Group by sport
sport_groups = defaultdict(list)
for t in trades:
    sport_groups[t["sport_key"]].append(t)

# Order of analysis
sport_order = [
    ("ATP_CHALL", "1. ATP CHALLENGERS"),
    ("WTA_CHALL", "2. WTA CHALLENGERS"),
    ("ATP", "3. ATP MAIN DRAW"),
    ("WTA", "4. WTA MAIN DRAW"),
    ("NCAAMB", "5. NCAAMB"),
    ("NBA", "6. NBA"),
    ("NHL", "7. NHL"),
]

results = {}
for sport_key, section_title in sport_order:
    group = sport_groups.get(sport_key, [])
    if not group:
        pr("\n" + "-" * 80)
        pr(section_title)
        pr("-" * 80)
        pr("  No data available")
        continue

    num_days = len(sport_dates.get(sport_key, set()))
    if num_days == 0:
        num_days = 30  # fallback

    pr("\n" + "-" * 80)
    pr("%s  (%d trades, %d days)" % (section_title, len(group), num_days))
    pr("-" * 80)

    result = run_sport_analysis(sport_key, group, num_days, out)
    if result:
        results[sport_key] = result

# ===========================================================================
# 8. COMBINED PROJECTION
# ===========================================================================
pr("\n" + "=" * 80)
pr("8. COMBINED PROJECTION — SPORT-SPECIFIC vs ONE-SIZE-FITS-ALL")
pr("=" * 80)

pr("")
pr("  SPORT-SPECIFIC OPTIMAL CONFIGS:")
pr("  %-12s %5s %5s %6s %5s %6s %8s %6s %5s" % (
    "Sport", "Gap>=", "Sprd<=", "WR%", "N", "Fast%", "$/day", "MaxDD", "Strk"))
pr("  " + "-" * 70)

total_daily_specific = 0
total_daily_uniform = 0

for sport_key, section_title in sport_order:
    r = results.get(sport_key)
    if not r: continue
    pr("  %-12s %5d %5d %5.1f%% %5d %5.1f%% %7s %5s %5d" % (
        sport_key, r["gap"], r["spread"], r["wr"], r["n"], r["fast_pct"],
        "$%.2f" % r["daily"], "-$%.0f" % r["dd"], r["strk"]))
    total_daily_specific += r["daily"]

pr("  " + "-" * 70)
pr("  %-12s %5s %5s %6s %5s %6s %8s" % (
    "TOTAL", "", "", "", "", "", "$%.2f" % total_daily_specific))

# Uniform gap=10 for comparison
pr("")
pr("  UNIFORM gap>=10, spread<=6 (one-size-fits-all):")
total_uniform = 0
for sport_key, section_title in sport_order:
    group = sport_groups.get(sport_key, [])
    if not group: continue
    num_days = len(sport_dates.get(sport_key, set())) or 30
    sub = dedup([t for t in group if t["gap"] >= 10 and t["spread"] <= 6])
    if not sub: continue
    pnl = calc_pnl(sub)
    daily = pnl / num_days
    total_uniform += daily
    w = len([t for t in sub if t["filled"] or (t["final"] is not None and t["final"] >= 50)])
    wr = w/len(sub)*100
    pr("  %-12s gap>=10 sprd<=6: %4d trades, WR=%.1f%%, $%.2f/day" % (
        sport_key, len(sub), wr, daily))
pr("  TOTAL uniform: $%.2f/day" % total_uniform)

pr("")
pr("  DELTA: sport-specific = $%.2f vs uniform = $%.2f  (%+.2f/day)" % (
    total_daily_specific, total_uniform, total_daily_specific - total_uniform))

# ===========================================================================
# 9. WHICH SPORTS TO TRADE?
# ===========================================================================
pr("\n" + "=" * 80)
pr("9. WHICH SPORTS TO TRADE? — RANKED BY RISK-ADJUSTED EV/MIN")
pr("=" * 80)

pr("")
pr("  %-12s %8s %8s %8s %10s %8s" % (
    "Sport", "$/day", "EV/min", "WR%", "AvgHold", "VERDICT"))
pr("  " + "-" * 60)

ranked = []
for sport_key, _ in sport_order:
    r = results.get(sport_key)
    if not r: continue
    ranked.append((sport_key, r))

ranked.sort(key=lambda x: x[1]["ev_min"], reverse=True)

for sport_key, r in ranked:
    if r["daily"] <= 0:
        verdict = "KILL"
    elif r["wr"] < 90 or r["daily"] < 1:
        verdict = "MONITOR"
    elif r["wr"] >= 93:
        verdict = "DEPLOY"
    else:
        verdict = "DEPLOY*"
    pr("  %-12s %7s %8s %7.1f%% %9.0fm %8s" % (
        sport_key, "$%.2f" % r["daily"],
        "$%.5f" % r["ev_min"], r["wr"], r["avg_hold"], verdict))

pr("")
pr("  DEPLOY  = WR >= 93%%, positive daily PnL — run with confidence")
pr("  DEPLOY* = WR 90-93%%, positive — run but watch closely")
pr("  MONITOR = Marginal — paper trade or very small size")
pr("  KILL    = Negative EV — do not trade")

# ===========================================================================
# FINAL CONFIG TABLE
# ===========================================================================
pr("\n" + "=" * 80)
pr("FINAL: SPORT-SPECIFIC STB CONFIGURATION")
pr("=" * 80)
pr("")

for sport_key, r in ranked:
    if r["daily"] <= 0: continue
    pr("  %s:" % sport_key)
    pr("    gap >= %d | spread <= %d | price 55-90c" % (r["gap"], r["spread"]))
    pr("    WR: %.1f%% | $/day: $%.2f | Fast: %.1f%% | MaxDD: -$%.0f" % (
        r["wr"], r["daily"], r["fast_pct"], r["dd"]))
    pr("")

pr("  Combined daily (sport-specific): $%.2f/day ($%.0f/month)" % (
    total_daily_specific, total_daily_specific * 30))
pr("  vs uniform gap>=10:              $%.2f/day ($%.0f/month)" % (
    total_uniform, total_uniform * 30))
pr("  vs current V3:                   $77.95/day ($2339/month)")

pr("\n" + "=" * 80)

with open("/tmp/sport_specific_mona_lisa.txt", "w") as f:
    f.write("\n".join(out))
print("\n[Written to /tmp/sport_specific_mona_lisa.txt]")
