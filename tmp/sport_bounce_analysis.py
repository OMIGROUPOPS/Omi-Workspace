#!/usr/bin/env python3
"""Sport-specific bounce mechanics analysis — memory-efficient two-pass.

Pass 1: Build lightweight index of event -> ticker -> (byte_start, byte_end, sport)
Pass 2: For each event, read only its 2 sides from disk, process, free immediately.

Peak memory: ~1 event's ticks at a time (not all 550MB).
"""
import csv, time, sys, math, io
from collections import defaultdict

DATA = "/tmp/v2_sorted.csv"
OUT = "/tmp/sport_bounce_analysis.txt"

def si(v):
    try: return int(v)
    except: return 0

def sf(v):
    try: return float(v)
    except: return 0.0

lines = []
def p(s=""):
    lines.append(s)

def tennis_cat(ticker):
    if "KXATPCHALLENGERMATCH" in ticker: return "atp_challenger"
    if "KXWTACHALLENGERMATCH" in ticker: return "wta_challenger"
    if "KXATPMATCH" in ticker: return "atp_main"
    if "KXWTAMATCH" in ticker: return "wta_main"
    return "tennis_other"

CFGS = {
    "ncaamb":         {"gap_min": 0,  "spread_max": 4},
    "nba":            {"gap_min": 0,  "spread_max": 6},
    "nhl":            {"gap_min": 8,  "spread_max": 8},
    "atp_challenger":  {"gap_min": 5,  "spread_max": 4},
    "wta_challenger":  {"gap_min": 5,  "spread_max": 4},
    "atp_main":        {"gap_min": 20, "spread_max": 4},
    "wta_main":        {"gap_min": 10, "spread_max": 4},
}

DAYS = {"ncaamb": 36, "nba": 3, "nhl": 16, "atp_challenger": 34,
        "wta_challenger": 33, "atp_main": 34, "wta_main": 34}

# ============================================================
# PASS 1: Build byte-offset index (tiny memory footprint)
# ============================================================
print("Pass 1: Building byte-offset index...", file=sys.stderr)
t0 = time.time()

# event -> {ticker: [start_byte, end_byte, sport]}
event_index = defaultdict(dict)
header_line = None

with open(DATA, "rb") as f:
    header_line = f.readline()  # skip header
    header_end = f.tell()

    # Parse header to get column indices
    hdr = header_line.decode().strip().split(",")
    col_ticker = hdr.index("kalshi_ticker")
    col_event = hdr.index("kalshi_event")
    col_sport = hdr.index("sport")

    prev_ticker = None
    ticker_start = header_end
    ticker_event = None
    ticker_sport = None
    line_count = 0

    while True:
        pos = f.tell()
        line = f.readline()
        if not line:
            # EOF — flush last ticker
            if prev_ticker and ticker_event:
                event_index[ticker_event][prev_ticker] = (ticker_start, pos, ticker_sport)
            break

        line_count += 1
        # Quick parse — just extract ticker, event, sport from CSV
        # Files are sorted by ticker, so we only need to detect ticker changes
        parts = line.decode().split(",")
        if len(parts) <= max(col_ticker, col_event, col_sport):
            continue
        ticker = parts[col_ticker]

        if ticker != prev_ticker:
            # Flush previous ticker
            if prev_ticker and ticker_event:
                event_index[ticker_event][prev_ticker] = (ticker_start, pos, ticker_sport)
            # Start new ticker
            prev_ticker = ticker
            ticker_start = pos
            ticker_event = parts[col_event]
            ticker_sport = parts[col_sport]

        if line_count % 500000 == 0:
            print(f"  {line_count} lines, {len(event_index)} events...", file=sys.stderr)

n_events = len(event_index)
n_sides = sum(len(v) for v in event_index.values())
print(f"Index: {n_events} events, {n_sides} sides in {time.time()-t0:.1f}s", file=sys.stderr)

# Filter to events with exactly 2 sides and non-mlb
valid_events = {}
for ev, sides in event_index.items():
    if len(sides) == 2:
        sports = set(v[2] for v in sides.values())
        if "mlb" not in sports:
            valid_events[ev] = sides

del event_index  # free index memory
print(f"Valid 2-sided events (non-mlb): {len(valid_events)}", file=sys.stderr)

# ============================================================
# PASS 2: Process each event from disk
# ============================================================
print("Pass 2: Processing events from disk...", file=sys.stderr)

def read_ticks(fh, start, end, hdr_cols):
    """Read ticks for one ticker from byte range. Returns list of dicts."""
    fh.seek(start)
    raw = fh.read(end - start).decode()
    ticks = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) < len(hdr_cols):
            continue
        row = {hdr_cols[i]: parts[i] for i in range(len(hdr_cols))}
        ticks.append(row)
    return ticks


def process_side(ticks, ticker, sport, partner_ticks):
    """Process one side with real combined_mid from partner."""
    if len(ticks) < 10:
        return None

    cat = tennis_cat(ticker) if sport == "tennis" else sport
    cfg = CFGS.get(cat, {"gap_min": 0, "spread_max": 4})

    winner = ticks[-1].get("winner", "")
    is_winner = (ticks[-1].get("kalshi_side","") == winner) if winner else None

    # Build partner ask lookup: sorted list of (timestamp, ask)
    partner_lookup = []
    for t in partner_ticks:
        ts = sf(t.get("bbo_timestamp", 0))
        ask = si(t.get("ask", 0))
        if ts > 0 and ask > 0:
            partner_lookup.append((ts, ask))
    # Already sorted by timestamp since file is sorted within each ticker

    if not partner_lookup:
        return None

    def get_partner_ask(ts):
        lo, hi = 0, len(partner_lookup) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if partner_lookup[mid][0] <= ts:
                lo = mid
            else:
                hi = mid - 1
        return partner_lookup[lo][1]

    # Find entry
    entry_idx = None
    for i, tick in enumerate(ticks):
        ask = si(tick.get("ask", 0))
        bid = si(tick.get("bid", 0))
        if ask <= 0 or bid <= 0:
            continue
        spread = ask - bid
        ts = sf(tick.get("bbo_timestamp", 0))
        p_ask = get_partner_ask(ts)
        combined_mid = ask + p_ask
        gap = p_ask  # partner ask

        if (55 <= ask <= 90 and spread <= cfg["spread_max"]
                and gap >= cfg["gap_min"] and combined_mid <= 97):
            entry_idx = i
            break

    if entry_idx is None:
        return None

    etick = ticks[entry_idx]
    entry_ask = si(etick.get("ask", 0))
    entry_ts = sf(etick.get("bbo_timestamp", 0))
    entry_period = etick.get("period", "")
    entry_home = si(etick.get("home_score", 0))
    entry_away = si(etick.get("away_score", 0))
    entry_diff = abs(entry_home - entry_away)

    # Scan forward
    trajectory = {}
    max_bounce = 0
    max_drawdown = 0
    score_events = []
    prev_home, prev_away = entry_home, entry_away
    first_score_bounce = None
    exit_levels = {}

    for j in range(entry_idx + 1, len(ticks)):
        t = ticks[j]
        bid = si(t.get("bid", 0))
        el = sf(t.get("bbo_timestamp", 0)) - entry_ts
        if el < 0:
            continue
        bnc = bid - entry_ask
        if bnc > max_bounce: max_bounce = bnc
        if bnc < max_drawdown: max_drawdown = bnc

        for ts_key in [15, 30, 60, 120, 300, 600, 1800, 3600]:
            if ts_key not in trajectory and el >= ts_key:
                trajectory[ts_key] = bnc

        for target in [3, 5, 7, 10, 12, 15, 20, 25, 30]:
            if target not in exit_levels and bnc >= target:
                exit_levels[target] = el

        ch = si(t.get("home_score", 0))
        ca = si(t.get("away_score", 0))
        if ch != prev_home or ca != prev_away:
            score_events.append({"elapsed_s": el, "bounce": bnc})
            if first_score_bounce is None:
                first_score_bounce = bnc
            prev_home, prev_away = ch, ca

    if 7 in exit_levels:
        exit_type = "target_7c"
        hold_s = exit_levels[7]
    elif is_winner:
        exit_type = "win_settle"
        hold_s = sf(ticks[-1].get("bbo_timestamp", 0)) - entry_ts
    else:
        exit_type = "loss_settle"
        hold_s = sf(ticks[-1].get("bbo_timestamp", 0)) - entry_ts

    return {
        "ticker": ticker, "cat": cat, "sport": sport,
        "entry_ask": entry_ask, "entry_period": entry_period,
        "entry_diff": entry_diff,
        "exit_type": exit_type, "hold_s": hold_s,
        "max_bounce": max_bounce, "max_drawdown": max_drawdown,
        "trajectory": trajectory, "score_events": score_events,
        "n_score_events": len(score_events),
        "first_score_bounce": first_score_bounce,
        "exit_levels": exit_levels, "is_winner": is_winner,
    }


hdr_cols = header_line.decode().strip().split(",")
all_trades = []
processed = 0

with open(DATA, "rb") as f:
    for event, sides in valid_events.items():
        tickers_list = list(sides.keys())
        t1, t2 = tickers_list
        start1, end1, sport1 = sides[t1]
        start2, end2, sport2 = sides[t2]

        ticks1 = read_ticks(f, start1, end1, hdr_cols)
        ticks2 = read_ticks(f, start2, end2, hdr_cols)

        sport = sport1

        trade1 = process_side(ticks1, t1, sport, ticks2)
        trade2 = process_side(ticks2, t2, sport, ticks1)

        if trade1: all_trades.append(trade1)
        if trade2: all_trades.append(trade2)

        # Free tick data immediately
        del ticks1, ticks2

        processed += 1
        if processed % 50 == 0:
            print(f"  {processed}/{len(valid_events)} events, {len(all_trades)} trades...", file=sys.stderr)

del valid_events
print(f"Total: {len(all_trades)} trades from {processed} events", file=sys.stderr)

by_cat = defaultdict(list)
for t in all_trades:
    by_cat[t["cat"]].append(t)

p("=" * 100)
p("SPORT-SPECIFIC BOUNCE MECHANICS ANALYSIS")
p(f"{len(all_trades)} simulated STB trades from unified BBO data")
p("=" * 100)

# ============================================================
# 1. NHL BOUNCE ANATOMY
# ============================================================
p()
p("=" * 100)
p("1. NHL BOUNCE ANATOMY")
p("=" * 100)

nhl = by_cat.get("nhl", [])
p(f"\n  Total NHL trades: {len(nhl)}")
if nhl:
    wins7 = [t for t in nhl if t["exit_type"] == "target_7c"]
    settles = [t for t in nhl if t["exit_type"] == "win_settle"]
    losses = [t for t in nhl if t["exit_type"] == "loss_settle"]
    total_wins = len(wins7) + len(settles)
    p(f"  +7c exits: {len(wins7)}  Settle wins: {len(settles)}  Losses: {len(losses)}")
    p(f"  Win rate: {total_wins/max(1,len(nhl))*100:.1f}%")

    with_score = [t for t in wins7 if t["n_score_events"] > 0]
    without_score = [t for t in wins7 if t["n_score_events"] == 0]
    p(f"\n  Of {len(wins7)} +7c wins:")
    p(f"    With score change during hold: {len(with_score)} ({len(with_score)/max(1,len(wins7))*100:.1f}%)")
    p(f"    Pure drift (no scoring): {len(without_score)} ({len(without_score)/max(1,len(wins7))*100:.1f}%)")
    if with_score:
        avg_b = sum(t["first_score_bounce"] or 0 for t in with_score) / len(with_score)
        p(f"    Avg bounce at first score change: {avg_b:+.1f}c")

    goal_exit = drift_exit = 0
    for t in wins7:
        last_se = None
        for se in t["score_events"]:
            if se["elapsed_s"] <= t["hold_s"]: last_se = se
        if last_se and (t["hold_s"] - last_se["elapsed_s"]) < 120:
            goal_exit += 1
        else:
            drift_exit += 1
    p(f"\n  Exit mechanism ({len(wins7)} wins):")
    p(f"    Within 2min of goal: {goal_exit} ({goal_exit/max(1,len(wins7))*100:.1f}%) — GOAL SPIKE")
    p(f"    No recent goal: {drift_exit} ({drift_exit/max(1,len(wins7))*100:.1f}%) — DRIFT")

    p(f"\n  Trajectory (all {len(nhl)} trades):")
    for ts_key in [15, 30, 60, 120, 300, 600, 1800, 3600]:
        vals = [t["trajectory"].get(ts_key) for t in nhl if ts_key in t["trajectory"]]
        if vals:
            label = f"{ts_key}s" if ts_key < 60 else f"{ts_key//60}m"
            p(f"    {label:>5}: {sum(vals)/len(vals):+.1f}c  (n={len(vals)})")

    if wins7:
        wh = sorted([t["hold_s"] for t in wins7])
        p(f"\n  +7c hold times:")
        p(f"    Avg: {sum(wh)/len(wh)/60:.1f}m  Median: {wh[len(wh)//2]/60:.1f}m")
        for cutoff, label in [(60,"<1m"),(120,"<2m"),(300,"<5m"),(600,"<10m"),(1800,"<30m")]:
            ct = sum(1 for h in wh if h < cutoff)
            p(f"    {label}: {ct}/{len(wh)} ({ct/len(wh)*100:.0f}%)")

    p(f"\n  Max bounce reached:")
    for threshold in [3,5,7,10,15,20,25,30,40,50]:
        ct = sum(1 for t in nhl if t["max_bounce"] >= threshold)
        if ct > 0:
            p(f"    >= {threshold:2d}c: {ct:4d} ({ct/len(nhl)*100:.1f}%)")

# ============================================================
# 2. TENNIS BOUNCE ANATOMY
# ============================================================
p()
p("=" * 100)
p("2. TENNIS BOUNCE ANATOMY")
p("=" * 100)

for cat in ["atp_challenger", "wta_challenger", "atp_main", "wta_main"]:
    trades = by_cat.get(cat, [])
    if not trades: continue
    wins7 = [t for t in trades if t["exit_type"] == "target_7c"]
    settles = [t for t in trades if t["exit_type"] == "win_settle"]
    losses = [t for t in trades if t["exit_type"] == "loss_settle"]
    total_wins = len(wins7) + len(settles)

    p(f"\n  {cat.upper()}: {len(trades)} trades")
    p(f"    +7c: {len(wins7)}  Settle: {len(settles)}  Loss: {len(losses)}  WR: {total_wins/max(1,len(trades))*100:.1f}%")

    if wins7:
        wh = sorted([t["hold_s"] for t in wins7])
        p(f"    +7c hold: avg={sum(wh)/len(wh)/60:.1f}m  med={wh[len(wh)//2]/60:.1f}m")
        fast = sum(1 for h in wh if h < 120)
        p(f"    Fast (<2m): {fast}/{len(wh)} ({fast/len(wh)*100:.0f}%)")

    with_score = [t for t in wins7 if t["n_score_events"] > 0]
    p(f"    Score change during +7c win: {len(with_score)}/{len(wins7)} ({len(with_score)/max(1,len(wins7))*100:.0f}%)")

    p(f"    Trajectory:")
    for ts_key in [15,30,60,120,300,600,1800,3600]:
        vals = [t["trajectory"].get(ts_key) for t in trades if ts_key in t["trajectory"]]
        if vals:
            label = f"{ts_key}s" if ts_key < 60 else f"{ts_key//60}m"
            p(f"      {label:>5}: {sum(vals)/len(vals):+.1f}c  (n={len(vals)})")

    p(f"    Max bounce:")
    for threshold in [7,10,15,20,25,30,40,50]:
        ct = sum(1 for t in trades if t["max_bounce"] >= threshold)
        if ct > 0:
            p(f"      >= {threshold:2d}c: {ct:4d} ({ct/len(trades)*100:.1f}%)")

# ============================================================
# 3. NCAAMB/NBA BOUNCE ANATOMY
# ============================================================
p()
p("=" * 100)
p("3. NCAAMB/NBA BOUNCE ANATOMY")
p("=" * 100)

for cat in ["ncaamb", "nba"]:
    trades = by_cat.get(cat, [])
    if not trades: continue
    wins7 = [t for t in trades if t["exit_type"] == "target_7c"]
    settles = [t for t in trades if t["exit_type"] == "win_settle"]
    losses = [t for t in trades if t["exit_type"] == "loss_settle"]
    total_wins = len(wins7) + len(settles)

    p(f"\n  {cat.upper()}: {len(trades)} trades")
    p(f"    +7c: {len(wins7)}  Settle: {len(settles)}  Loss: {len(losses)}  WR: {total_wins/max(1,len(trades))*100:.1f}%")

    if wins7:
        wh = sorted([t["hold_s"] for t in wins7])
        p(f"    +7c hold: avg={sum(wh)/len(wh)/60:.1f}m  med={wh[len(wh)//2]/60:.1f}m")
        fast = sum(1 for h in wh if h < 120)
        p(f"    Fast (<2m): {fast}/{len(wh)} ({fast/len(wh)*100:.0f}%)")

    with_score = [t for t in wins7 if t["n_score_events"] > 0]
    without = [t for t in wins7 if t["n_score_events"] == 0]
    p(f"    With score change: {len(with_score)}/{len(wins7)} ({len(with_score)/max(1,len(wins7))*100:.0f}%)")
    p(f"    Pure drift: {len(without)}/{len(wins7)} ({len(without)/max(1,len(wins7))*100:.0f}%)")

    p1 = [t for t in trades if si(t["entry_period"]) == 1]
    p2 = [t for t in trades if si(t["entry_period"]) >= 2]
    if p1:
        p1w = sum(1 for t in p1 if t["exit_type"] == "target_7c" or t.get("is_winner"))
        p(f"    1H entries: {len(p1)}, WR={p1w/len(p1)*100:.1f}%")
    if p2:
        p2w = sum(1 for t in p2 if t["exit_type"] == "target_7c" or t.get("is_winner"))
        p(f"    2H+ entries: {len(p2)}, WR={p2w/len(p2)*100:.1f}%")

    p(f"    Trajectory:")
    for ts_key in [15,30,60,120,300,600,1800,3600]:
        vals = [t["trajectory"].get(ts_key) for t in trades if ts_key in t["trajectory"]]
        if vals:
            label = f"{ts_key}s" if ts_key < 60 else f"{ts_key//60}m"
            p(f"      {label:>5}: {sum(vals)/len(vals):+.1f}c  (n={len(vals)})")

    p(f"    Max bounce:")
    for threshold in [3,5,7,10,15,20,25,30]:
        ct = sum(1 for t in trades if t["max_bounce"] >= threshold)
        p(f"      >= {threshold:2d}c: {ct:4d} ({ct/len(trades)*100:.1f}%)")

    p(f"    Score diff at entry:")
    for lo,hi,label in [(0,5,"0-4"),(5,10,"5-9"),(10,20,"10-19"),(20,99,"20+")]:
        bucket = [t for t in trades if lo <= t["entry_diff"] < hi]
        if bucket:
            bw = sum(1 for t in bucket if t["exit_type"] == "target_7c" or t.get("is_winner"))
            p(f"      diff {label}: {len(bucket)} trades, WR={bw/len(bucket)*100:.1f}%")

# ============================================================
# 4. SPORT-SPECIFIC OPTIMAL EXIT
# ============================================================
p()
p("=" * 100)
p("4. SPORT-SPECIFIC OPTIMAL EXIT TARGET")
p("=" * 100)

for cat in ["ncaamb", "nba", "nhl", "atp_challenger", "wta_challenger", "atp_main", "wta_main"]:
    trades = by_cat.get(cat, [])
    if not trades: continue
    days = DAYS.get(cat, 34)
    avg_entry = sum(t["entry_ask"] for t in trades) / len(trades)

    p(f"\n  {cat.upper()} ({len(trades)} trades, {days} days, avg entry {avg_entry:.0f}c):")
    p(f"  {'Target':>8} {'Hits':>6} {'Hit%':>6} {'Sttl':>5} {'Loss':>5} {'WR%':>6} {'AvgHld':>7} {'$/day':>8} {'$/min':>8}")
    p(f"  {'-'*72}")

    best_dpd = -999
    best_target = 7

    for target in [3, 5, 7, 10, 12, 15, 20, 25, 30]:
        hits = settle_w = loss_ct = 0
        total_hold = 0
        loss_pnl = 0

        for t in trades:
            el = t["exit_levels"].get(target)
            if el is not None:
                hits += 1
                total_hold += el
            elif t.get("is_winner"):
                settle_w += 1
            else:
                loss_ct += 1
                loss_pnl -= t["entry_ask"] * 25 / 100

        tgt_pnl = hits * target * 25 / 100
        stl_pnl = settle_w * (99 - avg_entry) * 25 / 100
        total_pnl = tgt_pnl + stl_pnl + loss_pnl
        total_w = hits + settle_w
        wr = total_w / len(trades) * 100
        dpd = total_pnl / days
        avg_hold = total_hold / max(1, hits) / 60
        dpm = dpd / max(0.01, avg_hold)

        if dpd > best_dpd:
            best_dpd = dpd
            best_target = target

        marker = " <<<" if target == best_target and dpd == best_dpd else ""
        p(f"  {'+'+str(target)+'c':>8} {hits:>6} {hits/len(trades)*100:>5.1f}% {settle_w:>5} {loss_ct:>5} {wr:>5.1f}% {avg_hold:>6.1f}m ${dpd:>7.2f} ${dpm:>7.4f}{marker}")

    p(f"  >>> OPTIMAL: +{best_target}c (${best_dpd:.2f}/day)")

# ============================================================
# 5. NHL VIABILITY
# ============================================================
p()
p("=" * 100)
p("5. NHL VIABILITY ASSESSMENT")
p("=" * 100)

if nhl:
    n = len(nhl)
    nhl_w = sum(1 for t in nhl if t["exit_type"] == "target_7c" or t.get("is_winner"))
    nhl_l = n - nhl_w
    wr = nhl_w / n

    p(f"\n  Trades: {n}  Wins: {nhl_w}  Losses: {nhl_l}  WR: {wr*100:.1f}%")
    p(f"  Trades/day: {n/DAYS['nhl']:.1f}")

    nhl_fast = sum(1 for t in nhl if t["exit_type"] == "target_7c" and t["hold_s"] < 120)
    p(f"  Fast fills (<2m): {nhl_fast} ({nhl_fast/n*100:.1f}%)")

    se = math.sqrt(wr * (1-wr) / n) if n > 0 else 0
    ci_low = wr - 1.96 * se
    ci_high = wr + 1.96 * se
    avg_e = sum(t["entry_ask"] for t in nhl) / n
    be_wr = avg_e / (avg_e + 7)

    p(f"\n  Statistics:")
    p(f"    n={n}, WR={wr*100:.1f}%, SE={se*100:.1f}%")
    p(f"    95% CI: [{ci_low*100:.1f}%, {ci_high*100:.1f}%]")
    p(f"    Avg entry: {avg_e:.0f}c, breakeven WR: {be_wr*100:.1f}%")
    p(f"    CI lower bound vs breakeven: {ci_low*100:.1f}% vs {be_wr*100:.1f}% — {'ABOVE' if ci_low > be_wr else 'OVERLAPS'}")

    p(f"\n  Capital comparison (per $25 locked):")
    nhl_dpd_stb = 7 * 25/100 * nhl_w / DAYS["nhl"]
    ncaamb_trades = by_cat.get("ncaamb", [])
    ncaamb_w = sum(1 for t in ncaamb_trades if t["exit_type"] == "target_7c" or t.get("is_winner"))
    ncaamb_dpd = 7 * 25/100 * ncaamb_w / DAYS["ncaamb"] if ncaamb_trades else 0
    p(f"    NHL STB 25ct: ~${nhl_dpd_stb:.2f}/day")
    p(f"    NCAAMB STB 25ct: ~${ncaamb_dpd:.2f}/day")
    p(f"    NHL Maker 10ct @92c: $4.11/day")

    p(f"\n  VERDICT:")
    if n < 50:
        p(f"    {n} trades — INSUFFICIENT for confidence. Keep at 10ct maker, observe.")
    elif n < 100 and ci_low <= be_wr:
        p(f"    {n} trades, CI overlaps breakeven. Edge UNPROVEN.")
        p(f"    RECOMMENDATION: Keep maker at 10ct. Consider dropping STB entirely.")
    elif ci_low > be_wr:
        p(f"    Edge statistically significant at 95% level.")
    else:
        p(f"    Marginal. Keep small size.")
else:
    p("\n  No NHL trades in dataset.")

# ============================================================
# SUMMARY
# ============================================================
p()
p("=" * 100)
p("SUMMARY: SPORT BOUNCE CHARACTER + OPTIMAL EXIT")
p("=" * 100)

p(f"\n  {'Sport':<18} {'N':>5} {'WR%':>6} {'OptTgt':>7} {'Hold':>7} {'$/day':>8} {'MaxBnc':>7} {'Fast%':>6} {'ScD%':>6} {'Character'}")
p(f"  {'-'*95}")

for cat in ["ncaamb", "nba", "nhl", "atp_challenger", "wta_challenger", "atp_main", "wta_main"]:
    trades = by_cat.get(cat, [])
    if not trades: continue
    days = DAYS.get(cat, 34)
    total_w = sum(1 for t in trades if t["exit_type"] == "target_7c" or t.get("is_winner"))
    wr = total_w / len(trades) * 100
    fast = sum(1 for t in trades if t["exit_type"] == "target_7c" and t["hold_s"] < 120)
    wh = [t["hold_s"] for t in trades if t["exit_type"] == "target_7c"]
    avg_hold = sum(wh) / max(1, len(wh)) / 60
    avg_mb = sum(t["max_bounce"] for t in trades) / len(trades)
    sc_pct = sum(1 for t in trades if t["n_score_events"] > 0) / len(trades) * 100
    avg_entry = sum(t["entry_ask"] for t in trades) / len(trades)

    best_dpd = -999; best_t = 7
    for target in [3,5,7,10,12,15,20,25,30]:
        h = sum(1 for t in trades if target in t["exit_levels"])
        s = sum(1 for t in trades if target not in t["exit_levels"] and t.get("is_winner"))
        l = sum(1 for t in trades if target not in t["exit_levels"] and not t.get("is_winner"))
        dpd = (h*target*25/100 + s*(99-avg_entry)*25/100 - l*avg_entry*25/100) / days
        if dpd > best_dpd: best_dpd = dpd; best_t = target

    char = {"nhl": "GOAL SPIKES", "ncaamb": "GRIND+RUNS", "nba": "GRIND+RUNS"}.get(cat, "SET/GAME")
    p(f"  {cat:<18} {len(trades):>5} {wr:>5.1f}% {'+'+str(best_t)+'c':>7} {avg_hold:>6.1f}m ${best_dpd:>7.2f} {avg_mb:>6.1f}c {fast/len(trades)*100:>5.1f}% {sc_pct:>5.1f}% {char}")

with open(OUT, "w") as f:
    f.write("\n".join(lines))
print(f"\nDone. {len(lines)} lines -> {OUT}", file=sys.stderr)
