#!/usr/bin/env python3
"""Simulate EXACT final production config against full BBO dataset.

Memory-efficient: builds byte-offset index, processes one event at a time.
Simulates both STB and Maker strategies with all current filters.
"""
import csv, time, sys, math
from collections import defaultdict
from datetime import datetime

DATA = "/tmp/v2_sorted.csv"
OUT = "/tmp/final_config_projection.txt"

def si(v):
    try: return int(v)
    except: return 0

def sf(v):
    try: return float(v)
    except: return 0.0

lines = []
def p(s=""):
    lines.append(s)
    print(s, file=sys.stderr)

# ============================================================
# EXACT PRODUCTION CONFIG
# ============================================================
STB_CONFIGS = {
    "ncaamb":          {"min_ask": 55, "max_ask": 90, "max_mid": 97, "spread_max": 4, "gap_min": 0,  "exit": 7, "trail": False, "max_diff": 9, "ct": 25},
    "nba":             {"min_ask": 55, "max_ask": 90, "max_mid": 97, "spread_max": 6, "gap_min": 0,  "exit": 7, "trail": False, "max_diff": 999, "ct": 25},
    "atp_main":        {"min_ask": 55, "max_ask": 90, "max_mid": 97, "spread_max": 4, "gap_min": 20, "exit": 7, "trail": True, "trail_width": 4, "ct": 25, "max_diff": 999},
    "atp_challenger":  {"min_ask": 55, "max_ask": 90, "max_mid": 97, "spread_max": 4, "gap_min": 5,  "exit": 7, "trail": True, "trail_width": 3, "ct": 25, "max_diff": 999},
    "wta_main":        {"min_ask": 55, "max_ask": 90, "max_mid": 97, "spread_max": 4, "gap_min": 10, "exit": 7, "trail": True, "trail_width": 4, "ct": 25, "max_diff": 999},
    "wta_challenger":  {"min_ask": 55, "max_ask": 90, "max_mid": 97, "spread_max": 4, "gap_min": 5,  "exit": 7, "trail": True, "trail_width": 3, "ct": 25, "max_diff": 999},
    # NHL: NO STB
}

MAKER_CONFIGS = {
    "ncaamb":          {"bid": 90, "sell": 99, "depth_filter": True, "min_depth": 0.15, "elapsed_min": 0, "ct": 25},
    "nba":             {"bid": 90, "sell": 99, "depth_filter": False, "elapsed_min": 0, "ct": 25},
    "nhl":             {"bid": 92, "sell": 99, "depth_filter": False, "elapsed_min": 0, "ct": 10},
    "atp_main":        {"bid": 90, "sell": 99, "depth_filter": False, "elapsed_min": 0, "ct": 25},
    "wta_main":        {"bid": 90, "sell": 99, "depth_filter": False, "elapsed_min": 20*60, "ct": 25},
    "atp_challenger":  {"bid": 90, "sell": 99, "depth_filter": False, "elapsed_min": 60*60, "ct": 25},
    "wta_challenger":  {"bid": 90, "sell": 99, "depth_filter": False, "elapsed_min": 0, "ct": 25},
}

def ticker_to_cat(ticker, sport):
    if sport == "tennis":
        if "KXATPCHALLENGERMATCH" in ticker: return "atp_challenger"
        if "KXWTACHALLENGERMATCH" in ticker: return "wta_challenger"
        if "KXATPMATCH" in ticker: return "atp_main"
        if "KXWTAMATCH" in ticker: return "wta_main"
        return None
    if sport == "ncaamb": return "ncaamb"
    if sport == "nba": return "nba"
    if sport == "nhl": return "nhl"
    return None

# ============================================================
# PASS 1: Build byte-offset index
# ============================================================
print("Pass 1: Building index...", file=sys.stderr)
t0 = time.time()

event_index = defaultdict(dict)

with open(DATA, "rb") as f:
    header_line = f.readline()
    header_end = f.tell()
    hdr = header_line.decode().strip().split(",")
    col_ticker = hdr.index("kalshi_ticker")
    col_event = hdr.index("kalshi_event")
    col_sport = hdr.index("sport")

    prev_ticker = None
    ticker_start = header_end
    ticker_event = None
    ticker_sport = None
    n = 0

    while True:
        pos = f.tell()
        line = f.readline()
        if not line:
            if prev_ticker and ticker_event:
                event_index[ticker_event][prev_ticker] = (ticker_start, pos, ticker_sport)
            break
        n += 1
        parts = line.decode().split(",")
        if len(parts) <= max(col_ticker, col_event, col_sport):
            continue
        ticker = parts[col_ticker]
        if ticker != prev_ticker:
            if prev_ticker and ticker_event:
                event_index[ticker_event][prev_ticker] = (ticker_start, pos, ticker_sport)
            prev_ticker = ticker
            ticker_start = pos
            ticker_event = parts[col_event]
            ticker_sport = parts[col_sport]

hdr_cols = header_line.decode().strip().split(",")

valid_events = {}
for ev, sides in event_index.items():
    if len(sides) == 2:
        sports = set(v[2] for v in sides.values())
        if "mlb" not in sports:
            valid_events[ev] = sides
del event_index

print(f"Index: {len(valid_events)} valid events in {time.time()-t0:.1f}s", file=sys.stderr)

# ============================================================
# PASS 2: Simulate both strategies per event
# ============================================================

def read_ticks(fh, start, end, hdr_cols):
    fh.seek(start)
    raw = fh.read(end - start).decode()
    ticks = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line: continue
        parts = line.split(",")
        if len(parts) < len(hdr_cols): continue
        ticks.append({hdr_cols[i]: parts[i] for i in range(len(hdr_cols))})
    return ticks


def sim_stb(ticks, ticker, sport, partner_ticks):
    """Simulate STB entry on one side."""
    cat = ticker_to_cat(ticker, sport)
    if cat is None or cat not in STB_CONFIGS:
        return None
    cfg = STB_CONFIGS[cat]

    if len(ticks) < 10:
        return None

    # Determine if this side won: winner is "home"/"away", map via home_abbr/away_abbr
    winner_raw = ticks[-1].get("winner", "")
    side_abbr = ticks[-1].get("kalshi_side", "")
    home_abbr = ticks[-1].get("home_abbr", "")
    away_abbr = ticks[-1].get("away_abbr", "")
    if winner_raw == "home":
        winning_side = home_abbr
    elif winner_raw == "away":
        winning_side = away_abbr
    else:
        winning_side = None
    is_winner = (side_abbr == winning_side) if winning_side else None

    # Build partner ask lookup
    plookup = []
    for t in partner_ticks:
        ts = sf(t.get("bbo_timestamp", 0))
        a = si(t.get("ask", 0))
        if ts > 0 and a > 0:
            plookup.append((ts, a))

    if not plookup:
        return None

    def partner_ask(ts):
        lo, hi = 0, len(plookup) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if plookup[mid][0] <= ts: lo = mid
            else: hi = mid - 1
        return plookup[lo][1]

    # Find entry
    entry_idx = None
    for i, tick in enumerate(ticks):
        ask = si(tick.get("ask", 0))
        bid = si(tick.get("bid", 0))
        if ask <= 0 or bid <= 0: continue
        spread = ask - bid
        ts = sf(tick.get("bbo_timestamp", 0))
        p_ask = partner_ask(ts)
        combined_mid = ask + p_ask
        gap = p_ask

        # Score diff filter
        diff = abs(si(tick.get("home_score", 0)) - si(tick.get("away_score", 0)))
        if diff > cfg["max_diff"]:
            continue

        if (cfg["min_ask"] <= ask <= cfg["max_ask"]
                and spread <= cfg["spread_max"]
                and gap >= cfg["gap_min"]
                and combined_mid <= cfg["max_mid"]):
            entry_idx = i
            break

    if entry_idx is None:
        return None

    etick = ticks[entry_idx]
    entry_ask = si(etick.get("ask", 0))
    entry_ts = sf(etick.get("bbo_timestamp", 0))
    entry_date = datetime.fromtimestamp(entry_ts).strftime("%Y-%m-%d")

    # Simulate exit
    if cfg["trail"]:
        # Trail: 99c safety, activate at entry+exit, trail by width
        trail_trigger = entry_ask + cfg["exit"]
        trail_w = cfg.get("trail_width", 3)
        floor_price = entry_ask + cfg["exit"]
        trail_active = False
        trail_price = 99
        exit_price = None
        exit_ts = None

        for j in range(entry_idx + 1, len(ticks)):
            t = ticks[j]
            bid = si(t.get("bid", 0))
            if bid <= 0: continue

            # Check if sell would fill (bid >= current sell price)
            if bid >= trail_price:
                exit_price = trail_price
                exit_ts = sf(t.get("bbo_timestamp", 0))
                break

            # Update trail
            if bid >= trail_trigger:
                new_trail = bid - trail_w
                new_trail = max(new_trail, floor_price)
                new_trail = min(new_trail, 99)
                if not trail_active:
                    trail_active = True
                    trail_price = new_trail
                elif new_trail > trail_price:
                    trail_price = new_trail

        if exit_price is None:
            # Settle
            if is_winner:
                exit_price = 100
            else:
                exit_price = 0
            exit_ts = sf(ticks[-1].get("bbo_timestamp", 0))
    else:
        # Fixed exit: entry + 7c
        target = entry_ask + cfg["exit"]
        exit_price = None
        exit_ts = None
        for j in range(entry_idx + 1, len(ticks)):
            t = ticks[j]
            bid = si(t.get("bid", 0))
            if bid >= target:
                exit_price = target
                exit_ts = sf(t.get("bbo_timestamp", 0))
                break
        if exit_price is None:
            if is_winner:
                exit_price = 100
            else:
                exit_price = 0
            exit_ts = sf(ticks[-1].get("bbo_timestamp", 0))

    ct = cfg["ct"]
    pnl_cents = (exit_price - entry_ask) * ct
    # Fee: ~1c/ct on entry (maker attempt), ~0 on exit (maker sell)
    fee_cents = ct  # approximate
    net_pnl = pnl_cents - fee_cents
    hold_s = exit_ts - entry_ts if exit_ts else 0

    return {
        "strategy": "STB",
        "cat": cat, "ticker": ticker,
        "entry_ask": entry_ask, "exit_price": exit_price,
        "pnl_cents": pnl_cents, "fee_cents": fee_cents, "net_pnl": net_pnl,
        "ct": ct, "hold_s": hold_s,
        "entry_ts": entry_ts, "entry_date": entry_date,
        "is_winner": is_winner,
        "won": exit_price > entry_ask,
    }


def sim_maker(ticks, ticker, sport, partner_ticks):
    """Simulate maker entry on one side — pullback model.

    Real behavior: bot sees ask >= bid_level+2 (strong favorite side),
    posts resting bid at bid_level. Gets filled if ask pulls back to bid_level.
    Key: price must START above bid_level, then come DOWN to it.
    """
    cat = ticker_to_cat(ticker, sport)
    if cat is None or cat not in MAKER_CONFIGS:
        return None
    cfg = MAKER_CONFIGS[cat]

    if len(ticks) < 10:
        return None

    # Determine if this side won
    winner_raw = ticks[-1].get("winner", "")
    side_abbr = ticks[-1].get("kalshi_side", "")
    home_abbr = ticks[-1].get("home_abbr", "")
    away_abbr = ticks[-1].get("away_abbr", "")
    if winner_raw == "home":
        winning_side = home_abbr
    elif winner_raw == "away":
        winning_side = away_abbr
    else:
        winning_side = None
    is_winner = (side_abbr == winning_side) if winning_side else None

    bid_level = cfg["bid"]
    sell_target = cfg["sell"]
    ct = cfg["ct"]

    # Pullback model (realistic):
    # Phase 1: ask must be >= bid_level + 2 for at least 3 consecutive ticks
    #          (simulates the WS handler seeing the opportunity and posting a bid)
    # Phase 2: ask then drops to <= bid_level (our resting bid gets filled)
    # Phase 3: only ONE maker entry per event per day (can't stack)
    entry_idx = None
    first_ts = sf(ticks[0].get("bbo_timestamp", 0))
    above_count = 0
    bid_posted = False

    for i, tick in enumerate(ticks):
        ask = si(tick.get("ask", 0))
        bid = si(tick.get("bid", 0))
        if ask <= 0: continue
        ts = sf(tick.get("bbo_timestamp", 0))

        # Elapsed filter
        elapsed = ts - first_ts
        if elapsed < cfg["elapsed_min"]:
            continue

        # Phase 1: accumulate consecutive ticks above threshold
        if not bid_posted:
            if ask >= bid_level + 2:
                above_count += 1
                if above_count >= 3:
                    bid_posted = True  # resting bid is now live
            else:
                above_count = 0
            continue

        # Phase 2: pullback fill — but ask must have been ABOVE bid_level
        # in the tick immediately before (not a continuous slide through)
        if ask <= bid_level:
            # Check previous tick was above bid_level (genuine pullback, not slide-through)
            if i > 0:
                prev_ask = si(ticks[i-1].get("ask", 0))
                if prev_ask > bid_level:
                    entry_idx = i
                    break
            # Also accept if bid_posted (we know price was recently above)
            entry_idx = i
            break

    if entry_idx is None:
        return None

    etick = ticks[entry_idx]
    entry_ask = bid_level  # we buy at our bid
    entry_ts = sf(etick.get("bbo_timestamp", 0))
    entry_date = datetime.fromtimestamp(entry_ts).strftime("%Y-%m-%d")

    # Exit: hold to sell_target (99c) or settlement
    exit_price = None
    exit_ts = None
    for j in range(entry_idx + 1, len(ticks)):
        t = ticks[j]
        bid = si(t.get("bid", 0))
        if bid >= sell_target:
            exit_price = sell_target
            exit_ts = sf(t.get("bbo_timestamp", 0))
            break

    if exit_price is None:
        if is_winner:
            exit_price = 100
        else:
            exit_price = 0
        exit_ts = sf(ticks[-1].get("bbo_timestamp", 0))

    pnl_cents = (exit_price - entry_ask) * ct
    fee_cents = max(1, ct // 5)  # maker fee ~0.2c/ct
    net_pnl = pnl_cents - fee_cents
    hold_s = exit_ts - entry_ts if exit_ts else 0

    return {
        "strategy": "MAKER",
        "cat": cat, "ticker": ticker,
        "entry_ask": entry_ask, "exit_price": exit_price,
        "pnl_cents": pnl_cents, "fee_cents": fee_cents, "net_pnl": net_pnl,
        "ct": ct, "hold_s": hold_s,
        "entry_ts": entry_ts, "entry_date": entry_date,
        "is_winner": is_winner,
        "won": exit_price > entry_ask,
    }


print("Pass 2: Simulating trades...", file=sys.stderr)
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

        # STB both sides
        for ticks, ticker, partner in [(ticks1, t1, ticks2), (ticks2, t2, ticks1)]:
            trade = sim_stb(ticks, ticker, sport, partner)
            if trade:
                all_trades.append(trade)

        # Maker: only the FAVORITE side per event (higher initial ask = stronger favorite)
        # Real bot sees the favorite at 92+ and posts bid; doesn't bid on the underdog
        # Pick the side with higher initial ask (first 10 ticks average)
        def avg_ask_start(ticks, n=10):
            vals = [si(t.get("ask",0)) for t in ticks[:n] if si(t.get("ask",0)) > 0]
            return sum(vals)/len(vals) if vals else 0
        avg1 = avg_ask_start(ticks1)
        avg2 = avg_ask_start(ticks2)
        # Only try maker on the favorite side (higher ask)
        if avg1 >= avg2:
            maker_order = [(ticks1, t1, ticks2)]
        else:
            maker_order = [(ticks2, t2, ticks1)]
        for ticks, ticker, partner in maker_order:
            trade = sim_maker(ticks, ticker, sport, partner)
            if trade:
                all_trades.append(trade)

        del ticks1, ticks2
        processed += 1
        if processed % 50 == 0:
            print(f"  {processed}/{len(valid_events)} events, {len(all_trades)} trades...", file=sys.stderr)

del valid_events
print(f"Total: {len(all_trades)} trades from {processed} events", file=sys.stderr)

# ============================================================
# ANALYSIS
# ============================================================

# Get date range
all_dates = sorted(set(t["entry_date"] for t in all_trades))
first_ts = min(t["entry_ts"] for t in all_trades)
last_ts = max(t["entry_ts"] for t in all_trades)
n_days = max(1, (last_ts - first_ts) / 86400)

p("=" * 100)
p("FINAL PRODUCTION CONFIG SIMULATION")
p(f"Data: {all_dates[0]} to {all_dates[-1]} ({n_days:.1f} days, {len(all_trades)} trades)")
p("=" * 100)

# ============================================================
# 1. Combined $/day by strategy and sport
# ============================================================
p()
p("=" * 100)
p("1. COMBINED $/DAY — EXACT FINAL CONFIG")
p("=" * 100)

stb_trades = [t for t in all_trades if t["strategy"] == "STB"]
maker_trades = [t for t in all_trades if t["strategy"] == "MAKER"]

p(f"\n  {'Category':<20} {'Strategy':<8} {'N':>5} {'Wins':>5} {'WR%':>6} {'PnL':>10} {'Fees':>8} {'Net':>10} {'$/day':>8}")
p(f"  {'-'*90}")

total_net = 0
total_stb_net = 0
total_maker_net = 0

for strategy, trades in [("STB", stb_trades), ("MAKER", maker_trades)]:
    by_cat = defaultdict(list)
    for t in trades:
        by_cat[t["cat"]].append(t)

    strat_net = 0
    for cat in ["ncaamb", "nba", "nhl", "atp_main", "atp_challenger", "wta_main", "wta_challenger"]:
        ct = by_cat.get(cat, [])
        if not ct: continue
        wins = sum(1 for t in ct if t["won"])
        wr = wins / len(ct) * 100
        pnl = sum(t["pnl_cents"] for t in ct)
        fees = sum(t["fee_cents"] for t in ct)
        net = sum(t["net_pnl"] for t in ct)
        dpd = net / 100 / n_days
        strat_net += net
        p(f"  {cat:<20} {strategy:<8} {len(ct):>5} {wins:>5} {wr:>5.1f}% ${pnl/100:>8.2f} ${fees/100:>6.2f} ${net/100:>8.2f} ${dpd:>7.2f}")

    dpd = strat_net / 100 / n_days
    p(f"  {'SUBTOTAL':<20} {strategy:<8} {len(trades):>5} {sum(1 for t in trades if t['won']):>5} {sum(1 for t in trades if t['won'])/max(1,len(trades))*100:>5.1f}% {'':>10} {'':>8} ${strat_net/100:>8.2f} ${dpd:>7.2f}")
    if strategy == "STB":
        total_stb_net = strat_net
    else:
        total_maker_net = strat_net
    total_net += strat_net
    p()

dpd_total = total_net / 100 / n_days
p(f"  {'TOTAL':<20} {'ALL':<8} {len(all_trades):>5} {sum(1 for t in all_trades if t['won']):>5} {sum(1 for t in all_trades if t['won'])/max(1,len(all_trades))*100:>5.1f}% {'':>10} {'':>8} ${total_net/100:>8.2f} ${dpd_total:>7.2f}")

# ============================================================
# 2. Day by day P&L
# ============================================================
p()
p("=" * 100)
p("2. DAY BY DAY P&L")
p("=" * 100)

daily = defaultdict(lambda: {"stb_net": 0, "maker_net": 0, "stb_n": 0, "maker_n": 0, "stb_wins": 0, "maker_wins": 0})
for t in all_trades:
    d = t["entry_date"]
    s = t["strategy"].lower()
    daily[d][f"{s}_net"] += t["net_pnl"]
    daily[d][f"{s}_n"] += 1
    if t["won"]:
        daily[d][f"{s}_wins"] += 1

p(f"\n  {'Date':<12} {'STB_N':>6} {'STB_WR':>7} {'STB_$':>9} {'MKR_N':>6} {'MKR_WR':>7} {'MKR_$':>9} {'Total_$':>9} {'Cumul':>9}")
p(f"  {'-'*80}")

cumul = 0
daily_totals = []
for d in sorted(daily.keys()):
    dd = daily[d]
    stb_n = dd["stb_n"]
    mkr_n = dd["maker_n"]
    stb_wr = dd["stb_wins"] / stb_n * 100 if stb_n else 0
    mkr_wr = dd["maker_wins"] / mkr_n * 100 if mkr_n else 0
    stb_d = dd["stb_net"] / 100
    mkr_d = dd["maker_net"] / 100
    tot = stb_d + mkr_d
    cumul += tot
    daily_totals.append(tot)
    p(f"  {d:<12} {stb_n:>6} {stb_wr:>6.1f}% ${stb_d:>7.2f} {mkr_n:>6} {mkr_wr:>6.1f}% ${mkr_d:>7.2f} ${tot:>7.2f} ${cumul:>7.2f}")

# ============================================================
# 3. Last 24h window (6pm yesterday to now)
# ============================================================
p()
p("=" * 100)
p("3. LAST 24H WINDOW")
p("=" * 100)

import time as _time
now = _time.time()
t_24h = now - 86400
# Since data ends Mar 8, use last 24h of data instead
data_end = max(t["entry_ts"] for t in all_trades)
data_24h = data_end - 86400

last24 = [t for t in all_trades if t["entry_ts"] >= data_24h]
if last24:
    start_dt = datetime.fromtimestamp(min(t["entry_ts"] for t in last24))
    end_dt = datetime.fromtimestamp(max(t["entry_ts"] for t in last24))
    p(f"\n  Window: {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%Y-%m-%d %H:%M')}")
    p(f"  Trades: {len(last24)}")

    for strategy in ["STB", "MAKER"]:
        st = [t for t in last24 if t["strategy"] == strategy]
        if not st: continue
        wins = sum(1 for t in st if t["won"])
        net = sum(t["net_pnl"] for t in st) / 100
        p(f"\n  {strategy}:")
        by_cat = defaultdict(list)
        for t in st:
            by_cat[t["cat"]].append(t)
        for cat in sorted(by_cat.keys()):
            ct = by_cat[cat]
            w = sum(1 for t in ct if t["won"])
            n = sum(t["net_pnl"] for t in ct) / 100
            avg_hold = sum(t["hold_s"] for t in ct) / len(ct) / 60
            p(f"    {cat:<20} {len(ct)} trades, {w} wins ({w/len(ct)*100:.0f}%), ${n:.2f}, avg hold {avg_hold:.1f}m")
        p(f"    TOTAL: {len(st)} trades, {wins} wins ({wins/len(st)*100:.0f}%), ${net:.2f}")

    total_24 = sum(t["net_pnl"] for t in last24) / 100
    p(f"\n  COMBINED 24H: ${total_24:.2f}")
else:
    p("\n  No trades in last 24h window of data")

# ============================================================
# 4. Best/Worst/Median day
# ============================================================
p()
p("=" * 100)
p("4. BEST DAY / WORST DAY / MEDIAN DAY")
p("=" * 100)

if daily_totals:
    sorted_days = sorted(daily.items(), key=lambda x: x[1]["stb_net"] + x[1]["maker_net"])
    worst_d, worst_v = sorted_days[0]
    best_d, best_v = sorted_days[-1]
    worst_pnl = (worst_v["stb_net"] + worst_v["maker_net"]) / 100
    best_pnl = (best_v["stb_net"] + best_v["maker_net"]) / 100

    sorted_totals = sorted(daily_totals)
    median_pnl = sorted_totals[len(sorted_totals) // 2]
    avg_pnl = sum(daily_totals) / len(daily_totals)

    p(f"\n  Worst day:  {worst_d}  ${worst_pnl:>8.2f}  ({worst_v['stb_n']} STB, {worst_v['maker_n']} maker)")
    p(f"  Best day:   {best_d}  ${best_pnl:>8.2f}  ({best_v['stb_n']} STB, {best_v['maker_n']} maker)")
    p(f"  Median day:          ${median_pnl:>8.2f}")
    p(f"  Average day:         ${avg_pnl:>8.2f}")

    # Breakdown of best and worst
    for label, d, v in [("WORST", worst_d, worst_v), ("BEST", best_d, best_v)]:
        p(f"\n  {label} DAY BREAKDOWN ({d}):")
        day_trades = [t for t in all_trades if t["entry_date"] == d]
        for strategy in ["STB", "MAKER"]:
            st = [t for t in day_trades if t["strategy"] == strategy]
            if not st: continue
            by_cat = defaultdict(list)
            for t in st:
                by_cat[t["cat"]].append(t)
            for cat in sorted(by_cat.keys()):
                ct = by_cat[cat]
                w = sum(1 for t in ct if t["won"])
                n = sum(t["net_pnl"] for t in ct) / 100
                losses = [t for t in ct if not t["won"]]
                loss_detail = ""
                if losses:
                    loss_detail = f" | losses: " + ", ".join(
                        f"{t['ticker'].split('-')[-1]}@{t['entry_ask']}c→{t['exit_price']}c"
                        for t in losses[:3])
                p(f"    {strategy} {cat:<18} {len(ct)} trades, {w}W, ${n:.2f}{loss_detail}")

# ============================================================
# 5. Monthly projection
# ============================================================
p()
p("=" * 100)
p("5. MONTHLY PROJECTION (30 DAYS)")
p("=" * 100)

if daily_totals:
    avg_day = sum(daily_totals) / len(daily_totals)
    monthly = avg_day * 30

    # Confidence interval using daily variance
    if len(daily_totals) > 1:
        variance = sum((d - avg_day) ** 2 for d in daily_totals) / (len(daily_totals) - 1)
        std = math.sqrt(variance)
        se_monthly = std * math.sqrt(30)
        ci_low = monthly - 1.96 * se_monthly
        ci_high = monthly + 1.96 * se_monthly
    else:
        ci_low = ci_high = monthly

    stb_avg = sum(t["net_pnl"] for t in stb_trades) / 100 / n_days
    maker_avg = sum(t["net_pnl"] for t in maker_trades) / 100 / n_days

    p(f"\n  Average $/day:     ${avg_day:.2f}")
    p(f"    STB component:   ${stb_avg:.2f}/day")
    p(f"    Maker component: ${maker_avg:.2f}/day")
    p(f"\n  Projected 30-day:  ${monthly:.2f}")
    if len(daily_totals) > 1:
        p(f"  95% CI:            [${ci_low:.2f}, ${ci_high:.2f}]")
        p(f"  Daily std dev:     ${std:.2f}")
    p(f"  Win days:          {sum(1 for d in daily_totals if d > 0)}/{len(daily_totals)}")
    p(f"  Sharpe (daily):    {avg_day/std:.2f}" if len(daily_totals) > 1 and std > 0 else "")

    # Capital efficiency
    avg_locked = sum(t["entry_ask"] * t["ct"] for t in all_trades) / len(all_trades)
    avg_concurrent = len(all_trades) / n_days * (sum(t["hold_s"] for t in all_trades) / len(all_trades) / 86400)
    p(f"\n  Avg capital per trade:  ${avg_locked/100:.2f}")
    p(f"  Avg trades/day:         {len(all_trades)/n_days:.1f}")
    p(f"  Current balance:        $425")

    # March Madness adjustment
    p(f"\n  MARCH MADNESS NOTE:")
    p(f"    Data covers {n_days:.1f} days of regular season")
    p(f"    March Madness = 2-3x NCAAMB volume (32→64 games/day in rounds 1-2)")
    p(f"    NCAAMB STB currently: ${sum(t['net_pnl'] for t in stb_trades if t['cat']=='ncaamb')/100/n_days:.2f}/day")
    p(f"    With 2x volume: ~${sum(t['net_pnl'] for t in stb_trades if t['cat']=='ncaamb')/100/n_days*2:.2f}/day")

# ============================================================
# SUMMARY TABLE
# ============================================================
p()
p("=" * 100)
p("EXECUTIVE SUMMARY")
p("=" * 100)

total_dpd = total_net / 100 / n_days
stb_dpd = total_stb_net / 100 / n_days
maker_dpd = total_maker_net / 100 / n_days
stb_wr = sum(1 for t in stb_trades if t["won"]) / max(1, len(stb_trades)) * 100
maker_wr = sum(1 for t in maker_trades if t["won"]) / max(1, len(maker_trades)) * 100

p(f"\n  STB:    {len(stb_trades)} trades, {stb_wr:.1f}% WR, ${stb_dpd:.2f}/day")
p(f"  Maker:  {len(maker_trades)} trades, {maker_wr:.1f}% WR, ${maker_dpd:.2f}/day")
p(f"  TOTAL:  ${total_dpd:.2f}/day → ${total_dpd*30:.2f}/month")
if daily_totals and len(daily_totals) > 1:
    p(f"  95% CI: ${ci_low:.2f} to ${ci_high:.2f}/month")

with open(OUT, "w") as f:
    f.write("\n".join(lines))
print(f"\nDone. {len(lines)} lines -> {OUT}", file=sys.stderr)
