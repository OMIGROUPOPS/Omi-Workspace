#!/usr/bin/env python3
"""
Maker Mona Lisa — Full analysis of 92c+/95c+ maker-to-99c strategy
Uses unified BBO data (2.6M ticks) to build per-side maker entry simulations.
"""
import csv, os, math, sys
from collections import defaultdict

BBO_PATH = "/root/espn_data/unified_5sport_v2.csv"
NBA_MATRIX = "/root/espn_data/nba_full_price_matrix.csv"
OUT_PATH = "/tmp/maker_mona_lisa.txt"

def sf(v, d=None):
    try:
        f = float(v)
        return f if not math.isnan(f) else d
    except:
        return d

def si(v, d=0):
    try: return int(v)
    except: return d

def median(vals):
    v = sorted(x for x in vals if x is not None)
    if not v: return 0
    n = len(v)
    return (v[n//2-1]+v[n//2])/2 if n%2==0 else v[n//2]

def avg(vals):
    v = [x for x in vals if x is not None]
    return sum(v)/len(v) if v else 0

def pct(num, denom):
    return num/denom*100 if denom else 0

# ---------------------------------------------------------------------------
# STEP 1: Build maker simulation from unified BBO
# For each event-side: track price over time, find when it first crosses
# each entry threshold (90,91,92,93,94,95,96,97), then check if/when it hits 99c
# Also capture game state at entry moment
# ---------------------------------------------------------------------------
print("Loading unified BBO data...", file=sys.stderr)

# Group all ticks by event-side, sorted by timestamp
side_ticks = defaultdict(list)  # key = kalshi_ticker
with open(BBO_PATH) as f:
    for row in csv.DictReader(f):
        ticker = row.get("kalshi_ticker","")
        if not ticker: continue
        ts = sf(row.get("bbo_timestamp"))
        ask = si(row.get("ask"))
        bid = si(row.get("bid"))
        sport = row.get("sport","")
        if ask <= 0 or ts is None: continue
        side_ticks[ticker].append({
            "ts": ts, "ask": ask, "bid": bid, "sport": sport,
            "period": row.get("period",""), "clock": row.get("clock",""),
            "score_diff": si(row.get("score_diff")),
            "home_score": si(row.get("home_score")),
            "away_score": si(row.get("away_score")),
            "seconds_remaining": sf(row.get("seconds_remaining")),
            "event": row.get("kalshi_event",""),
            "side": row.get("kalshi_side",""),
            "final_price": si(row.get("ask")),  # will update with settlement
        })

print(f"Loaded {sum(len(v) for v in side_ticks.values())} ticks for {len(side_ticks)} sides", file=sys.stderr)

# Sort each side by timestamp
for ticker in side_ticks:
    side_ticks[ticker].sort(key=lambda x: x["ts"])

# Determine final settlement: last tick's price and whether it settled YES (>=50) or NO (<50)
# Actually use the max price ever reached as proxy for settlement
side_final = {}
for ticker, ticks in side_ticks.items():
    if not ticks: continue
    last_ask = ticks[-1]["ask"]
    max_ask = max(t["ask"] for t in ticks)
    # If max ever reached 99c, likely settled YES
    settled_yes = max_ask >= 99 or last_ask >= 95
    side_final[ticker] = {"last": last_ask, "max": max_ask, "settled_yes": settled_yes}

# ---------------------------------------------------------------------------
# Build maker entry simulations
# For each side, find first time ask crosses each threshold
# Then track: time to 99c, max price, did it ever drop below entry-3c (stop loss sim)
# ---------------------------------------------------------------------------
ENTRY_LEVELS = [90, 91, 92, 93, 94, 95, 96, 97]

# Structure: entries[ticker][entry_level] = {entry_tick, time_to_99, game_state, ...}
entries = defaultdict(dict)

for ticker, ticks in side_ticks.items():
    if len(ticks) < 3: continue
    sport = ticks[0]["sport"]
    event = ticks[0]["event"]

    for level in ENTRY_LEVELS:
        entry_tick = None
        for i, t in enumerate(ticks):
            if t["ask"] >= level:
                entry_tick = t
                entry_idx = i
                break
        if entry_tick is None:
            continue

        # Find time to 99c after entry
        time_to_99 = None
        max_after = entry_tick["ask"]
        min_after = entry_tick["ask"]
        hit_99 = False
        for t in ticks[entry_idx:]:
            if t["ask"] > max_after: max_after = t["ask"]
            if t["ask"] < min_after: min_after = t["ask"]
            if t["ask"] >= 99 and not hit_99:
                time_to_99 = (t["ts"] - entry_tick["ts"]) / 60.0  # minutes
                hit_99 = True

        # Settlement outcome
        final = side_final.get(ticker, {})
        settled_yes = final.get("settled_yes", False)

        # Win = hit 99c (maker sell fills at 99c)
        # Loss = never hit 99c AND settled NO
        # Hold-to-settle win = never hit 99c but settled YES (collect full 100c)
        if hit_99:
            outcome = "win"
            pnl_cents = (99 - level)  # profit in cents
        elif settled_yes:
            outcome = "settle_win"
            pnl_cents = (100 - level)  # full settlement
        else:
            outcome = "loss"
            pnl_cents = -level  # total loss

        entries[ticker][level] = {
            "sport": sport, "event": event, "side": entry_tick.get("side",""),
            "entry_price": level, "entry_ts": entry_tick["ts"],
            "period": entry_tick.get("period",""),
            "clock": entry_tick.get("clock",""),
            "score_diff": entry_tick.get("score_diff", 0),
            "seconds_remaining": entry_tick.get("seconds_remaining"),
            "time_to_99": time_to_99,
            "max_after": max_after, "min_after": min_after,
            "hit_99": hit_99, "settled_yes": settled_yes,
            "outcome": outcome, "pnl_cents": pnl_cents,
        }

# Collect all entries into flat list, deduped by event (one side per event per level)
def collect_entries(level, sport_filter=None, series_filter=None):
    seen_events = set()
    out = []
    for ticker in sorted(entries.keys()):
        if level not in entries[ticker]: continue
        e = entries[ticker][level]
        if sport_filter and e["sport"] != sport_filter: continue
        if series_filter:
            if not ticker.startswith(series_filter): continue
        key = e["event"]
        if key in seen_events: continue
        seen_events.add(key)
        out.append(e)
    return out

# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------
lines = []
def p(s=""):
    lines.append(s)
    print(s)

p("=" * 100)
p("MAKER MONA LISA — Full Analysis of 92c+/95c+ Maker-to-99c Strategy")
p("Data: unified BBO (2.6M ticks) across NCAAMB, NBA, NHL, Tennis")
p("Sizing: 50ct maker (current production)")
p("=" * 100)

# =========================================================================
# PART 1: Anatomy of instant resolution
# =========================================================================
p()
p("=" * 100)
p("PART 1: ANATOMY OF INSTANT RESOLUTION")
p("=" * 100)

for level in [92, 95]:
    all_e = collect_entries(level)
    if not all_e: continue
    fast = [e for e in all_e if e["time_to_99"] is not None and e["time_to_99"] < 5]
    medium = [e for e in all_e if e["time_to_99"] is not None and 5 <= e["time_to_99"] < 20]
    slow = [e for e in all_e if e["time_to_99"] is not None and e["time_to_99"] >= 20]
    loss = [e for e in all_e if not e["hit_99"] and not e["settled_yes"]]
    settle_w = [e for e in all_e if not e["hit_99"] and e["settled_yes"]]

    p()
    p(f"  Entry at {level}c → sell at 99c ({len(all_e)} events)")
    p(f"  " + "-" * 80)
    wins = [e for e in all_e if e["outcome"] in ("win","settle_win")]
    losses = [e for e in all_e if e["outcome"] == "loss"]
    p(f"  Total: {len(all_e)} | Wins: {len(wins)} ({pct(len(wins),len(all_e)):.1f}%) | Losses: {len(losses)} ({pct(len(losses),len(all_e)):.1f}%)")
    p()

    hdr = f"  {'Group':<20} {'Count':>6} {'%':>6} {'Avg Entry':>10} {'Avg Diff':>10} {'Avg Time99':>10} {'Avg SecRem':>10}"
    p(hdr)
    p("  " + "-" * 80)

    for label, group in [("Fast (<5m)", fast), ("Medium (5-20m)", medium),
                          ("Slow (20m+)", slow), ("Settle win", settle_w), ("Loss", loss)]:
        if not group: continue
        avg_ep = avg([e["entry_price"] for e in group])
        avg_diff = avg([abs(e["score_diff"]) for e in group])
        avg_t99 = avg([e["time_to_99"] for e in group if e["time_to_99"] is not None])
        avg_sec = avg([e["seconds_remaining"] for e in group if e["seconds_remaining"] is not None])
        p(f"  {label:<20} {len(group):>6} {pct(len(group),len(all_e)):>5.1f}% {avg_ep:>9.0f}c {avg_diff:>9.1f} {avg_t99:>9.1f}m {avg_sec:>9.0f}s")

    p()
    p(f"  Sport breakdown for {level}c entries:")
    p(f"  {'Sport':<12} {'Total':>6} {'Win%':>6} {'Fast%':>6} {'Loss':>6} {'AvgT99':>8}")
    p("  " + "-" * 50)
    for sport in ["ncaamb", "nba", "nhl", "tennis"]:
        sub = [e for e in all_e if e["sport"] == sport]
        if not sub: continue
        w = [e for e in sub if e["outcome"] in ("win","settle_win")]
        f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
        l_ = [e for e in sub if e["outcome"] == "loss"]
        at = avg([e["time_to_99"] for e in sub if e["time_to_99"] is not None])
        p(f"  {sport:<12} {len(sub):>6} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {at:>7.1f}m")

# =========================================================================
# PART 2: Sport-specific maker analysis
# =========================================================================
p()
p("=" * 100)
p("PART 2: SPORT-SPECIFIC MAKER ANALYSIS")
p("=" * 100)

# --- NCAAMB ---
p()
p("-" * 80)
p("2A. NCAAMB 95c MAKER")
p("-" * 80)

p()
p("  Entry level sweep:")
p(f"  {'Level':>6} {'Trades':>7} {'Win%':>6} {'Fast%':>6} {'Loss':>5} {'AvgT99':>8} {'$/day':>8} {'MaxDD':>8}")
p("  " + "-" * 60)
ncaamb_days = 36
for level in [93, 94, 95, 96, 97]:
    sub = collect_entries(level, sport_filter="ncaamb")
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    at = avg([e["time_to_99"] for e in sub if e["time_to_99"] is not None])
    # PnL at 50ct
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub)
    ppd = pnl / ncaamb_days
    # Max DD
    cumul = 0; peak = 0; mdd = 0
    for e in sorted(sub, key=lambda x: x["entry_ts"]):
        cumul += e["pnl_cents"] * 0.50 / 100
        peak = max(peak, cumul)
        mdd = max(mdd, peak - cumul)
    p(f"  {level:>5}c {len(sub):>7} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {at:>7.1f}m {ppd:>7.2f} -${mdd:.2f}")

# Score diff sweep at 95c
p()
p("  Score differential sweep (entry=95c):")
p(f"  {'Diff>=':>7} {'Trades':>7} {'Win%':>6} {'Fast%':>6} {'Loss':>5} {'$/day':>8}")
p("  " + "-" * 50)
ncaamb_95 = collect_entries(95, sport_filter="ncaamb")
for diff_min in [0, 5, 8, 10, 12, 15, 20]:
    sub = [e for e in ncaamb_95 if abs(e["score_diff"]) >= diff_min]
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub)
    ppd = pnl / ncaamb_days
    p(f"  {diff_min:>6} {len(sub):>7} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {ppd:>7.2f}")

# Period filter
p()
p("  Period filter (entry=95c):")
for pf in ["any", "2+"]:
    sub = ncaamb_95 if pf == "any" else [e for e in ncaamb_95 if si(e["period"]) >= 2]
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / ncaamb_days
    p(f"    period={pf}: {len(sub)} trades, WR={pct(len(w),len(sub)):.1f}%, losses={len(l_)}, $/day={pnl:.2f}")

# Clock filter (period 2 only)
p()
p("  Clock filter (entry=95c, period 2+):")
ncaamb_95_p2 = [e for e in ncaamb_95 if si(e["period"]) >= 2]
for clock_max in [600, 480, 300, 180]:
    sub = [e for e in ncaamb_95_p2 if e["seconds_remaining"] is not None and e["seconds_remaining"] <= clock_max]
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / ncaamb_days
    p(f"    clock<={clock_max//60}min: {len(sub)} trades, WR={pct(len(w),len(sub)):.1f}%, fast={pct(len(f_),len(sub)):.0f}%, losses={len(l_)}, $/day={pnl:.2f}")

# --- Tennis (ATP Main) ---
p()
p("-" * 80)
p("2B. ATP MAIN DRAW 92c MAKER")
p("-" * 80)
tennis_days = 34

p()
p("  Entry level sweep:")
p(f"  {'Level':>6} {'Trades':>7} {'Win%':>6} {'Fast%':>6} {'Loss':>5} {'AvgT99':>8} {'$/day':>8}")
p("  " + "-" * 55)
for level in [90, 91, 92, 93]:
    sub = collect_entries(level, series_filter="KXATPMATCH")
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    at = avg([e["time_to_99"] for e in sub if e["time_to_99"] is not None])
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / tennis_days
    p(f"  {level:>5}c {len(sub):>7} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {at:>7.1f}m {pnl:>7.2f}")

# --- WTA Main (currently excluded) ---
p()
p("-" * 80)
p("2C. WTA MAIN DRAW — SHOULD IT GET 92c+ MAKER?")
p("-" * 80)

p()
p("  Entry level sweep:")
p(f"  {'Level':>6} {'Trades':>7} {'Win%':>6} {'Fast%':>6} {'Loss':>5} {'AvgT99':>8} {'$/day':>8}")
p("  " + "-" * 55)
for level in [90, 91, 92, 93]:
    sub = collect_entries(level, series_filter="KXWTAMATCH")
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    at = avg([e["time_to_99"] for e in sub if e["time_to_99"] is not None])
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / tennis_days
    p(f"  {level:>5}c {len(sub):>7} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {at:>7.1f}m {pnl:>7.2f}")

# --- Challenger series ---
p()
p("-" * 80)
p("2D. CHALLENGERS (ATP + WTA) — MAKER VIABILITY")
p("-" * 80)

for series_label, series_prefix in [("ATP Challengers", "KXATPCHALLENGERMATCH"),
                                      ("WTA Challengers", "KXWTACHALLENGERMATCH")]:
    p(f"\n  {series_label}:")
    p(f"  {'Level':>6} {'Trades':>7} {'Win%':>6} {'Fast%':>6} {'Loss':>5} {'$/day':>8}")
    p("  " + "-" * 50)
    for level in [90, 92, 95]:
        sub = collect_entries(level, series_filter=series_prefix)
        if not sub: continue
        w = [e for e in sub if e["outcome"] in ("win","settle_win")]
        f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
        l_ = [e for e in sub if e["outcome"] == "loss"]
        pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / tennis_days
        p(f"  {level:>5}c {len(sub):>7} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {pnl:>7.2f}")

# --- NHL ---
p()
p("-" * 80)
p("2E. NHL 92c+ MAKER — IS IT VIABLE?")
p("-" * 80)
nhl_days = 12

p()
p("  Entry level sweep:")
p(f"  {'Level':>6} {'Trades':>7} {'Win%':>6} {'Fast%':>6} {'Loss':>5} {'AvgT99':>8} {'$/day':>8}")
p("  " + "-" * 55)
for level in [90, 92, 94, 95, 96]:
    sub = collect_entries(level, sport_filter="nhl")
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    at = avg([e["time_to_99"] for e in sub if e["time_to_99"] is not None])
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / nhl_days
    p(f"  {level:>5}c {len(sub):>7} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {at:>7.1f}m {pnl:>7.2f}")

# Score diff for NHL
p()
p("  NHL score diff sweep (entry=95c):")
nhl_95 = collect_entries(95, sport_filter="nhl")
for diff_min in [0, 1, 2, 3]:
    sub = [e for e in nhl_95 if abs(e["score_diff"]) >= diff_min]
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / nhl_days
    p(f"    diff>={diff_min}: {len(sub)} trades, WR={pct(len(w),len(sub)):.1f}%, losses={len(l_)}, $/day={pnl:.2f}")

# --- NBA ---
p()
p("-" * 80)
p("2F. NBA 95c MAKER")
p("-" * 80)
nba_days = 24  # NBA has more data in full matrix

p()
p("  Entry level sweep:")
p(f"  {'Level':>6} {'Trades':>7} {'Win%':>6} {'Fast%':>6} {'Loss':>5} {'AvgT99':>8} {'$/day':>8}")
p("  " + "-" * 55)
for level in [93, 94, 95, 96]:
    sub = collect_entries(level, sport_filter="nba")
    if not sub: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    at = avg([e["time_to_99"] for e in sub if e["time_to_99"] is not None])
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / nba_days
    p(f"  {level:>5}c {len(sub):>7} {pct(len(w),len(sub)):>5.1f}% {pct(len(f_),len(sub)):>5.1f}% {len(l_):>5} {at:>7.1f}m {pnl:>7.2f}")

# NBA quarter + diff analysis
p()
p("  NBA quarter + score diff (entry=95c):")
nba_95 = collect_entries(95, sport_filter="nba")
for q_min in [1, 2, 3, 4]:
    for diff_min in [0, 10, 15]:
        sub = [e for e in nba_95 if si(e["period"]) >= q_min and abs(e["score_diff"]) >= diff_min]
        if not sub or len(sub) < 2: continue
        w = [e for e in sub if e["outcome"] in ("win","settle_win")]
        l_ = [e for e in sub if e["outcome"] == "loss"]
        pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / nba_days
        p(f"    Q>={q_min} diff>={diff_min}: {len(sub)} trades, WR={pct(len(w),len(sub)):.1f}%, losses={len(l_)}, $/day={pnl:.2f}")

# =========================================================================
# PART 3: Risk per sport on maker module
# =========================================================================
p()
p("=" * 100)
p("PART 3: RISK PER SPORT ON MAKER MODULE (50ct sizing)")
p("=" * 100)
p()

sport_configs = [
    ("NCAAMB", "ncaamb", None, 95, ncaamb_days),
    ("NBA", "nba", None, 95, nba_days),
    ("NHL", "nhl", None, 95, nhl_days),
    ("ATP Main", None, "KXATPMATCH", 92, tennis_days),
    ("WTA Main", None, "KXWTAMATCH", 92, tennis_days),
    ("ATP Chall", None, "KXATPCHALLENGERMATCH", 92, tennis_days),
    ("WTA Chall", None, "KXWTACHALLENGERMATCH", 92, tennis_days),
]

p(f"{'Sport':<12} {'Entry':>5} {'Trades':>6} {'WR%':>6} {'AvgWin':>8} {'AvgLoss':>9} {'BE_WR':>6} {'Edge':>7} {'Fast%':>6} {'MaxDD':>8} {'$/day':>7}")
p("-" * 95)

part3_results = []
for label, sport_f, series_f, level, days in sport_configs:
    sub = collect_entries(level, sport_filter=sport_f, series_filter=series_f)
    if not sub:
        p(f"{label:<12} {level:>4}c {'N/A':>6}")
        continue

    wins = [e for e in sub if e["outcome"] in ("win","settle_win")]
    losses = [e for e in sub if e["outcome"] == "loss"]
    fast = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]

    # Avg win/loss in dollars at 50ct
    if wins:
        avg_win = avg([e["pnl_cents"] * 0.50 / 100 for e in wins])
    else:
        avg_win = (99 - level) * 0.50 / 100

    if losses:
        avg_loss = abs(avg([e["pnl_cents"] * 0.50 / 100 for e in losses]))
    else:
        avg_loss = level * 0.50 / 100

    wr = pct(len(wins), len(sub))
    be_wr = pct(avg_loss, avg_loss + avg_win) if (avg_loss + avg_win) > 0 else 0
    edge = wr - be_wr

    # Max DD and max single loss
    cumul = 0; peak = 0; mdd = 0
    sorted_sub = sorted(sub, key=lambda x: x["entry_ts"])
    for e in sorted_sub:
        cumul += e["pnl_cents"] * 0.50 / 100
        peak = max(peak, cumul)
        mdd = max(mdd, peak - cumul)

    max_single_loss = max([abs(e["pnl_cents"] * 0.50 / 100) for e in losses]) if losses else 0
    pnl_total = sum(e["pnl_cents"] * 0.50 / 100 for e in sub)
    ppd = pnl_total / days
    wins_to_recover = avg_loss / avg_win if avg_win > 0 else 999

    p(f"{label:<12} {level:>4}c {len(sub):>6} {wr:>5.1f}% ${avg_win:>6.2f} ${avg_loss:>7.2f} {be_wr:>5.1f}% {edge:>+5.1f}pp {pct(len(fast),len(sub)):>5.0f}% -${mdd:>6.2f} ${ppd:>5.2f}")

    part3_results.append({
        "label": label, "level": level, "n": len(sub), "wins": len(wins),
        "losses": len(losses), "wr": wr, "avg_win": avg_win, "avg_loss": avg_loss,
        "be_wr": be_wr, "edge": edge, "fast_pct": pct(len(fast), len(sub)),
        "mdd": mdd, "ppd": ppd, "max_single": max_single_loss,
        "wins_to_recover": wins_to_recover, "days": days,
    })

p()
p("  Detailed risk:")
p(f"  {'Sport':<12} {'MaxSingle':>10} {'WinsToRecover':>14} {'Sizing':>10}")
p("  " + "-" * 50)
for r in part3_results:
    if r["n"] == 0: continue
    sizing = "50ct OK" if r["edge"] > 3 else ("25ct safer" if r["edge"] > 0 else "DO NOT TRADE")
    p(f"  {r['label']:<12} ${r['max_single']:>8.2f} {r['wins_to_recover']:>13.1f} {sizing:>10}")

# =========================================================================
# PART 4: The Maker Mona Lisa — optimal config per sport
# =========================================================================
p()
p("=" * 100)
p("PART 4: THE MAKER MONA LISA — OPTIMAL CONFIG PER SPORT")
p("=" * 100)
p()

# For each sport, find optimal entry level by maximizing $/day with WR > 90%
p(f"{'Sport':<12} {'Entry':>5} {'DiffFilter':>10} {'Period':>8} {'Trades':>6} {'$/day':>7} {'WR%':>6} {'Fast%':>6} {'MaxDD':>8}")
p("-" * 80)

maker_configs = []

# NCAAMB: sweep entry + diff
best_ncaamb = None
for level in [93, 94, 95, 96, 97]:
    base = collect_entries(level, sport_filter="ncaamb")
    for diff_min in [0, 5, 8, 10, 12, 15]:
        sub = [e for e in base if abs(e["score_diff"]) >= diff_min]
        if len(sub) < 10: continue
        w = [e for e in sub if e["outcome"] in ("win","settle_win")]
        l_ = [e for e in sub if e["outcome"] == "loss"]
        wr = pct(len(w), len(sub))
        f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
        pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / ncaamb_days
        cumul = 0; peak = 0; mdd = 0
        for e in sorted(sub, key=lambda x: x["entry_ts"]):
            cumul += e["pnl_cents"] * 0.50 / 100
            peak = max(peak, cumul)
            mdd = max(mdd, peak - cumul)
        if best_ncaamb is None or pnl > best_ncaamb["ppd"]:
            best_ncaamb = {"level": level, "diff": diff_min, "n": len(sub), "wr": wr,
                          "fast": pct(len(f_), len(sub)), "ppd": pnl, "mdd": mdd, "losses": len(l_)}

if best_ncaamb:
    b = best_ncaamb
    p(f"{'NCAAMB':<12} {b['level']:>4}c {'diff>='+str(b['diff']):>10} {'any':>8} {b['n']:>6} ${b['ppd']:>5.2f} {b['wr']:>5.1f}% {b['fast']:>5.0f}% -${b['mdd']:>.2f}")
    maker_configs.append({"sport": "NCAAMB", **b})

# NBA: sweep entry + diff + quarter
best_nba = None
for level in [93, 94, 95, 96]:
    base = collect_entries(level, sport_filter="nba")
    for diff_min in [0, 10, 15]:
        sub = [e for e in base if abs(e["score_diff"]) >= diff_min]
        if len(sub) < 3: continue
        w = [e for e in sub if e["outcome"] in ("win","settle_win")]
        l_ = [e for e in sub if e["outcome"] == "loss"]
        wr = pct(len(w), len(sub))
        f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
        pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / nba_days
        cumul = 0; peak = 0; mdd = 0
        for e in sorted(sub, key=lambda x: x["entry_ts"]):
            cumul += e["pnl_cents"] * 0.50 / 100
            peak = max(peak, cumul)
            mdd = max(mdd, peak - cumul)
        if best_nba is None or pnl > best_nba["ppd"]:
            best_nba = {"level": level, "diff": diff_min, "n": len(sub), "wr": wr,
                       "fast": pct(len(f_), len(sub)), "ppd": pnl, "mdd": mdd, "losses": len(l_)}

if best_nba:
    b = best_nba
    p(f"{'NBA':<12} {b['level']:>4}c {'diff>='+str(b['diff']):>10} {'any':>8} {b['n']:>6} ${b['ppd']:>5.2f} {b['wr']:>5.1f}% {b['fast']:>5.0f}% -${b['mdd']:>.2f}")
    maker_configs.append({"sport": "NBA", **b})

# NHL
best_nhl = None
for level in [90, 92, 94, 95, 96]:
    base = collect_entries(level, sport_filter="nhl")
    for diff_min in [0, 1, 2, 3]:
        sub = [e for e in base if abs(e["score_diff"]) >= diff_min]
        if len(sub) < 3: continue
        w = [e for e in sub if e["outcome"] in ("win","settle_win")]
        l_ = [e for e in sub if e["outcome"] == "loss"]
        wr = pct(len(w), len(sub))
        f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
        pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / nhl_days
        cumul = 0; peak = 0; mdd = 0
        for e in sorted(sub, key=lambda x: x["entry_ts"]):
            cumul += e["pnl_cents"] * 0.50 / 100
            peak = max(peak, cumul)
            mdd = max(mdd, peak - cumul)
        if best_nhl is None or pnl > best_nhl["ppd"]:
            best_nhl = {"level": level, "diff": diff_min, "n": len(sub), "wr": wr,
                       "fast": pct(len(f_), len(sub)), "ppd": pnl, "mdd": mdd, "losses": len(l_)}

if best_nhl:
    b = best_nhl
    p(f"{'NHL':<12} {b['level']:>4}c {'diff>='+str(b['diff']):>10} {'any':>8} {b['n']:>6} ${b['ppd']:>5.2f} {b['wr']:>5.1f}% {b['fast']:>5.0f}% -${b['mdd']:>.2f}")
    maker_configs.append({"sport": "NHL", **b})

# ATP Main
best_atp = None
for level in [90, 91, 92, 93]:
    sub = collect_entries(level, series_filter="KXATPMATCH")
    if len(sub) < 5: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    wr = pct(len(w), len(sub))
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / tennis_days
    cumul = 0; peak = 0; mdd = 0
    for e in sorted(sub, key=lambda x: x["entry_ts"]):
        cumul += e["pnl_cents"] * 0.50 / 100
        peak = max(peak, cumul)
        mdd = max(mdd, peak - cumul)
    if best_atp is None or pnl > best_atp["ppd"]:
        best_atp = {"level": level, "diff": 0, "n": len(sub), "wr": wr,
                   "fast": pct(len(f_), len(sub)), "ppd": pnl, "mdd": mdd, "losses": len(l_)}

if best_atp:
    b = best_atp
    p(f"{'ATP Main':<12} {b['level']:>4}c {'none':>10} {'any':>8} {b['n']:>6} ${b['ppd']:>5.2f} {b['wr']:>5.1f}% {b['fast']:>5.0f}% -${b['mdd']:>.2f}")
    maker_configs.append({"sport": "ATP_Main", **b})

# WTA Main
best_wta = None
for level in [90, 91, 92, 93]:
    sub = collect_entries(level, series_filter="KXWTAMATCH")
    if len(sub) < 5: continue
    w = [e for e in sub if e["outcome"] in ("win","settle_win")]
    l_ = [e for e in sub if e["outcome"] == "loss"]
    wr = pct(len(w), len(sub))
    f_ = [e for e in sub if e["time_to_99"] is not None and e["time_to_99"] < 5]
    pnl = sum(e["pnl_cents"] * 0.50 / 100 for e in sub) / tennis_days
    cumul = 0; peak = 0; mdd = 0
    for e in sorted(sub, key=lambda x: x["entry_ts"]):
        cumul += e["pnl_cents"] * 0.50 / 100
        peak = max(peak, cumul)
        mdd = max(mdd, peak - cumul)
    if best_wta is None or pnl > best_wta["ppd"]:
        best_wta = {"level": level, "diff": 0, "n": len(sub), "wr": wr,
                   "fast": pct(len(f_), len(sub)), "ppd": pnl, "mdd": mdd, "losses": len(l_)}

if best_wta:
    b = best_wta
    p(f"{'WTA Main':<12} {b['level']:>4}c {'none':>10} {'any':>8} {b['n']:>6} ${b['ppd']:>5.2f} {b['wr']:>5.1f}% {b['fast']:>5.0f}% -${b['mdd']:.2f}")
    maker_configs.append({"sport": "WTA_Main", **b})

# =========================================================================
# PART 5: Combined system projection
# =========================================================================
p()
p("=" * 100)
p("PART 5: COMBINED SYSTEM PROJECTION — STB + MAKER")
p("=" * 100)
p()

# STB daily from sport-specific Mona Lisa
stb_daily = {
    "ATP_CHALL": 27.87, "WTA_CHALL": 6.93, "ATP": 8.56, "WTA": 8.85,
    "NCAAMB": 23.92, "NHL": 7.08,
}
stb_total = sum(stb_daily.values())

# Maker daily from Part 4
maker_total = sum(c["ppd"] for c in maker_configs)

p(f"  {'Module':<25} {'$/day':>8} {'Trades/day':>12}")
p("  " + "-" * 50)
p(f"  {'STB (sport-specific ML)':<25} ${stb_total:>6.2f}")
for c in maker_configs:
    tpd = c["n"] / c.get("days", 30) if "days" not in c else c["n"] / (ncaamb_days if "NCAAMB" in c["sport"] else nba_days if "NBA" in c["sport"] else nhl_days if "NHL" in c["sport"] else tennis_days)
    p(f"  {'Maker: ' + c['sport']:<25} ${c['ppd']:>6.2f} {tpd:>11.1f}")
p("  " + "-" * 50)
combined = stb_total + maker_total
p(f"  {'COMBINED TOTAL':<25} ${combined:>6.2f}")
p(f"  {'Monthly projection':<25} ${combined * 30:>6.0f}")
p()

# Sizing analysis
p("  SIZING ANALYSIS at $445 balance:")
p("  " + "-" * 50)
stb_exposure = 104.2 * 90 * 0.25 / 100  # ~104 trades/day * avg 90c * 25ct
maker_exposure = sum(c["n"] / (ncaamb_days if "NCAAMB" in c["sport"] else nba_days if "NBA" in c["sport"] else nhl_days if "NHL" in c["sport"] else tennis_days) for c in maker_configs) * 95 * 0.50 / 100
p(f"    STB daily exposure (25ct avg): ~${stb_exposure:.0f} across all open positions")
p(f"    Maker daily exposure (50ct avg): ~${maker_exposure:.0f} across all open positions")
p()

# Worst case scenario
worst_stb_dd = 102.25  # NCAAMB max DD from breakeven analysis
worst_maker_dd = max(c["mdd"] for c in maker_configs) if maker_configs else 0
p(f"    Worst STB drawdown:   -${worst_stb_dd:.2f}")
p(f"    Worst Maker drawdown: -${worst_maker_dd:.2f}")
p(f"    Combined worst case:  -${worst_stb_dd + worst_maker_dd:.2f}")
p(f"    Balance after worst:  ${445 - worst_stb_dd - worst_maker_dd:.2f}")
p()

# Sizing recommendation
if 445 - worst_stb_dd - worst_maker_dd > 100:
    p("    VERDICT: 50ct maker + 25ct STB is SAFE at $445")
else:
    p("    VERDICT: 50ct maker is TOO LARGE — reduce to 25ct until balance > $600")

p()
p("=" * 100)

# Write to file
with open(OUT_PATH, "w") as f:
    f.write("\n".join(lines))
print(f"\n[Written to {OUT_PATH}]")
