#!/usr/bin/env python3
"""Full trade autopsy of every production trade from v3_enriched_trades.csv."""
import csv, json, re
from collections import defaultdict
from datetime import datetime

lines = []
def p(s=''):
    lines.append(s)

trades = []
with open('/tmp/v3_enriched_trades.csv') as f:
    for r in csv.DictReader(f):
        trades.append(r)

def si(v):
    try: return int(v)
    except: return 0

def sf(v):
    try: return float(v)
    except: return 0.0

def parse_game_state(gs_str):
    """Parse the semicolon-separated game state dict string."""
    if not gs_str:
        return {}
    result = {}
    # Remove outer braces
    gs_str = gs_str.strip()
    if gs_str.startswith('{'):
        gs_str = gs_str[1:]
    if gs_str.endswith('}'):
        gs_str = gs_str[:-1]
    # Split by semicolons
    for part in gs_str.split(';'):
        part = part.strip()
        if ':' not in part:
            continue
        key, _, val = part.partition(':')
        key = key.strip().strip("'\"")
        val = val.strip().strip("'\"")
        result[key] = val
    return result

# Enrich all trades
for t in trades:
    mode = t.get('entry_mode', '') or ''
    t['strategy'] = 'MAKER' if '92plus' in mode else 'STB'
    ts_str = t['timestamp']
    try:
        t['dt'] = datetime.strptime(ts_str[:19], '%Y-%m-%d %H:%M:%S')
    except:
        t['dt'] = datetime(2026, 1, 1)
    t['ep'] = si(t.get('entry_price', 0))
    t['xp'] = si(t.get('exit_price', 0))
    t['pnl'] = si(t.get('pnl_cents', 0))
    t['hold'] = sf(t.get('hold_time_seconds', 0))
    t['exit'] = t.get('exit_type', '')
    t['sport'] = t.get('sport', '')
    t['closed'] = t['exit'] != ''
    t['depth5'] = sf(t.get('depth_ratio_5c', 0))
    t['depth10'] = sf(t.get('depth_ratio_10c', 0))
    t['spread_entry'] = si(t.get('spread', 0))
    t['book_spread'] = si(t.get('book_spread', 0))
    t['pre_10m'] = si(t.get('pre_entry_price_10m', 0))
    t['first_seen'] = si(t.get('first_seen_price', 0))
    t['combined_mid'] = sf(t.get('combined_mid', 0))
    t['score_diff_val'] = si(t.get('score_diff', 0))
    t['who_winning'] = t.get('who_winning_at_entry', '') or ''
    t['max_bid'] = si(t.get('max_bid_after_entry', 0))
    t['trajectory'] = t.get('price_trajectory', '') or ''
    t['volume'] = si(t.get('volume_at_entry', 0))
    t['bid5'] = si(t.get('bid_depth_5c', 0))
    t['ask5'] = si(t.get('ask_depth_5c', 0))
    t['bid10'] = si(t.get('bid_depth_10c', 0))
    t['ask10'] = si(t.get('ask_depth_10c', 0))
    t['total_depth'] = si(t.get('total_depth', 0))
    t['book_mid'] = sf(t.get('book_mid', 0))
    t['period'] = t.get('period', '') or ''
    t['clock'] = si(t.get('clock_seconds', 0))
    t['sets_won'] = t.get('sets_won', '') or ''
    t['games_cs'] = t.get('games_current_set', '') or ''
    t['is_deciding'] = t.get('is_deciding_set', '') or ''

    # Parse game states
    t['gs_entry'] = parse_game_state(t.get('game_state_at_entry', ''))
    t['gs_exit'] = parse_game_state(t.get('game_state_at_exit', ''))

    # Ticker category
    tk = t.get('ticker', '')
    if 'KXATPCHALLENGERMATCH' in tk:
        t['cat'] = 'atp_challenger'
    elif 'KXWTACHALLENGERMATCH' in tk:
        t['cat'] = 'wta_challenger'
    elif 'KXATPMATCH' in tk:
        t['cat'] = 'atp_main'
    elif 'KXWTAMATCH' in tk:
        t['cat'] = 'wta_main'
    else:
        t['cat'] = t['sport']

    # Dip vs spike
    if t['first_seen'] > 0:
        t['is_dip'] = t['ep'] < t['first_seen']
        t['price_vs_open'] = t['ep'] - t['first_seen']
    elif t['pre_10m'] > 0:
        t['is_dip'] = t['ep'] < t['pre_10m']
        t['price_vs_open'] = t['ep'] - t['pre_10m']
    else:
        t['is_dip'] = None
        t['price_vs_open'] = None

    # Was our side winning at entry?
    side = t.get('entry_side', '')
    t['our_side'] = side
    if t['who_winning']:
        t['our_side_winning'] = (side.upper() == t['who_winning'].upper())
    else:
        # Try from game state
        gs = t['gs_entry']
        away = si(gs.get('away_points', gs.get('away_overall_score', 0)))
        home = si(gs.get('home_points', gs.get('home_overall_score', 0)))
        # We don't know which side is home/away from just the side abbrev
        t['our_side_winning'] = None

    # Fee
    ct = 10 if t['sport'] == 'nhl' and t['strategy'] == 'MAKER' else 25
    t['ct'] = ct
    if t['strategy'] == 'MAKER' or t.get('entry_type') == 'maker':
        t['fee'] = max(1, ct * 0.3)
    else:
        t['fee'] = ct * 1.5
    t['net_pnl'] = t['pnl'] - t['fee'] if t['closed'] else None

closed = [t for t in trades if t['closed']]
still_open = [t for t in trades if not t['closed']]
losses = [t for t in closed if t['pnl'] <= 0]
winners = [t for t in closed if t['pnl'] > 0]

def fmt_game_state(gs, sport):
    """Format game state dict into readable string."""
    if not gs:
        return '(no game state)'
    if sport in ('ncaamb', 'nba', 'nhl'):
        away = gs.get('away_points', '?')
        home = gs.get('home_points', '?')
        period = gs.get('period', '?')
        clock = gs.get('clock', '')
        last_play = gs.get('last_play', '')
        if last_play and len(last_play) > 80:
            last_play = last_play[:80] + '...'
        return "Score: %s-%s | Period: %s | Clock: %s | Last: %s" % (away, home, period, clock, last_play)
    else:
        # Tennis
        c1_score = gs.get('competitor1_overall_score', gs.get('away_overall_score', '?'))
        c2_score = gs.get('competitor2_overall_score', gs.get('home_overall_score', '?'))
        c1_round = gs.get('competitor1_current_round_score', '?')
        c2_round = gs.get('competitor2_current_round_score', '?')
        serving = gs.get('serving', '')
        return "Sets: %s-%s | Games: %s-%s | Serving: %s" % (c1_score, c2_score, c1_round, c2_round, serving)

def full_trade_autopsy(t, idx=0):
    """Print full autopsy of a single trade."""
    p("  [%d] %s %s (%s) — %s" % (idx, t['timestamp'][:19], t['our_side'], t['cat'], t['strategy']))
    p("      Entry: %dc | Exit: %dc (%s) | PnL: %dc | Net: %.0fc | Hold: %.1fm" % (
        t['ep'], t['xp'], t['exit'], t['pnl'], t['net_pnl'] if t['net_pnl'] is not None else 0, t['hold']/60))
    p("      Combined MID at entry: %.1fc | Spread: %dc | Book spread: %dc | Book MID: %.1fc" % (
        t['combined_mid'], t['spread_entry'], t['book_spread'], t['book_mid']))

    # Depth
    p("      Depth: bid5=%d ask5=%d ratio5=%.3f | bid10=%d ask10=%d ratio10=%.3f | total=%d" % (
        t['bid5'], t['ask5'], t['depth5'], t['bid10'], t['ask10'], t['depth10'], t['total_depth']))

    # Price context
    if t['pre_10m'] > 0:
        p("      Price 10m ago: %dc (delta: %+dc)" % (t['pre_10m'], t['ep'] - t['pre_10m']))
    if t['first_seen'] > 0:
        p("      First seen price: %dc (delta: %+dc)" % (t['first_seen'], t['ep'] - t['first_seen']))
    if t['is_dip'] is not None:
        label = "DIP (buying below reference)" if t['is_dip'] else "SPIKE (buying above reference)"
        p("      Entry type: %s" % label)

    # Max bid after entry (did we ever have a chance?)
    if t['max_bid'] > 0:
        p("      Max bid after entry: %dc (peak unrealized: %+dc)" % (t['max_bid'], t['max_bid'] - t['ep']))

    # Price trajectory
    if t['trajectory']:
        traj = t['trajectory'][:200]
        p("      Trajectory: %s" % traj)

    # Game state
    p("      Game state at ENTRY: %s" % fmt_game_state(t['gs_entry'], t['sport']))
    p("      Game state at EXIT:  %s" % fmt_game_state(t['gs_exit'], t['sport']))

    # Who winning
    if t['who_winning']:
        our_win = "YES" if t.get('our_side_winning') else "NO"
        p("      Who winning at entry: %s (our side winning: %s)" % (t['who_winning'], our_win))

    # Score diff
    if t['score_diff_val'] != 0 or t.get('score_diff', ''):
        p("      Score diff at entry: %d" % t['score_diff_val'])

    # Period/clock
    if t['period']:
        p("      Period: %s | Clock: %ds" % (t['period'], t['clock']))

    # Tennis specifics
    if t['sets_won']:
        p("      Sets won: %s | Games in set: %s | Deciding set: %s" % (
            t['sets_won'], t['games_cs'], t['is_deciding']))

    # Volume
    if t['volume'] > 0:
        p("      Volume at entry: %d" % t['volume'])

    p("")


# ============================================================
# PART 1: THE 2 LOSSES
# ============================================================
p('=' * 110)
p('TRADE AUTOPSY — %d TOTAL TRADES (%d closed, %d open)' % (len(trades), len(closed), len(still_open)))
p('=' * 110)

p()
p('=' * 110)
p('PART 1: THE 2 LOSSES — FULL AUTOPSY')
p('=' * 110)
p()

for i, t in enumerate(sorted(losses, key=lambda x: x['pnl'])):
    full_trade_autopsy(t, i+1)

    # Loss-specific analysis
    p("  --- LOSS ANALYSIS ---")

    # What killed us?
    gs_exit = t['gs_exit']
    if gs_exit:
        away_exit = si(gs_exit.get('away_points', 0))
        home_exit = si(gs_exit.get('home_points', 0))
        last_play = gs_exit.get('last_play', '')
        p("      Final score at exit: %d-%d" % (away_exit, home_exit))
        if last_play:
            p("      Last play at exit: %s" % last_play)

    # Price drop analysis
    if t['max_bid'] > 0:
        if t['max_bid'] >= t['ep'] + 7:
            p("      *** WAS PROFITABLE: max_bid %dc >= entry+7 (%dc) — bounced but didn't fill ***" % (
                t['max_bid'], t['ep'] + 7))
        elif t['max_bid'] > t['ep']:
            p("      Partially recovered to %dc but never reached exit target %dc" % (
                t['max_bid'], t['ep'] + 7))
        else:
            p("      Never recovered above entry — straight down from %dc" % t['ep'])

    drop = t['ep'] - t['xp']
    p("      Total price drop: %dc (entry %dc -> exit %dc)" % (drop, t['ep'], t['xp']))

    # Depth warning signal
    if t['depth5'] < 0.1:
        p("      WARNING SIGNAL: depth_ratio_5c = %.3f (< 0.10) — extremely thin bid side" % t['depth5'])
    if t['depth10'] < 0.05:
        p("      WARNING SIGNAL: depth_ratio_10c = %.3f (< 0.05) — asks overwhelming bids" % t['depth10'])

    # Pre-10m price signal
    if t['pre_10m'] > 0:
        if t['ep'] > t['pre_10m'] + 15:
            p("      WARNING SIGNAL: entry %dc is %dc ABOVE 10m-ago price %dc — buying a spike, not a dip" % (
                t['ep'], t['ep'] - t['pre_10m'], t['pre_10m']))

    # Entry mode analysis
    p("      Entry mode: %s — this was a MAKER entry at 92c" % t.get('entry_mode', ''))
    p("      The 92c maker module posts resting bids. The loss means the game turned against us")
    p("      after our bid was filled. The -10c stop at %dc kicked in." % t['xp'])
    p("")

# ============================================================
# PART 2: FASTEST WINNERS
# ============================================================
p('=' * 110)
p('PART 2: THE 10 FASTEST WINNERS')
p('=' * 110)
p()

winners_sorted = sorted(winners, key=lambda x: x['hold'])
for i, t in enumerate(winners_sorted[:10]):
    full_trade_autopsy(t, i+1)
    p("  --- SPEED ANALYSIS ---")
    p("      Hold time: %.1f seconds (%.1f minutes)" % (t['hold'], t['hold']/60))
    if t['max_bid'] > 0:
        p("      Max bid: %dc — bounced %dc above entry" % (t['max_bid'], t['max_bid'] - t['ep']))
    if t['pre_10m'] > 0:
        delta = t['ep'] - t['pre_10m']
        if delta < 0:
            p("      Entered %dc BELOW 10m-ago price — buying a genuine dip" % abs(delta))
        else:
            p("      Entered %dc above 10m-ago price" % delta)

    # What made it fast?
    if t['depth5'] > 0.3:
        p("      Strong depth ratio (%.3f) — bids supporting the bounce" % t['depth5'])
    if t['spread_entry'] <= 1:
        p("      Tight spread (%dc) — efficient market, quick recovery" % t['spread_entry'])
    p("")

# ============================================================
# PART 3: SLOWEST WINNERS
# ============================================================
p('=' * 110)
p('PART 3: THE 10 SLOWEST WINNERS')
p('=' * 110)
p()

for i, t in enumerate(winners_sorted[-10:]):
    full_trade_autopsy(t, i+1)
    p("  --- PATIENCE ANALYSIS ---")
    p("      Hold time: %.0f seconds (%.1f minutes)" % (t['hold'], t['hold']/60))
    if t['max_bid'] > 0:
        p("      Max bid: %dc — eventual bounce of %dc" % (t['max_bid'], t['max_bid'] - t['ep']))
    if t['pre_10m'] > 0:
        delta = t['ep'] - t['pre_10m']
        p("      Entry vs 10m-ago: %+dc" % delta)

    # Why slow?
    if t['depth5'] < 0.15:
        p("      Low depth ratio (%.3f) — weak bid support, slow recovery" % t['depth5'])
    if t['strategy'] == 'MAKER':
        p("      MAKER trade — had to wait for game to end (settlement)")
    if t['ep'] >= 85:
        p("      High entry (%dc) — less room for price appreciation, needed patience" % t['ep'])
    p("")

# ============================================================
# PART 4: THE PATTERN — SCORECARD
# ============================================================
p('=' * 110)
p('PART 4: THE PATTERN — WHAT SEPARATES WINNERS FROM LOSERS, FAST FROM SLOW')
p('=' * 110)
p()

# Stats comparison
p("  LOSSES vs WINNERS COMPARISON:")
p("  %30s %15s %15s %15s" % ("Metric", "Losses (2)", "Fast10 Win", "Slow10 Win"))
p("  " + "-" * 80)

fast10 = winners_sorted[:10]
slow10 = winners_sorted[-10:]

def avg_metric(group, key):
    vals = [t[key] for t in group if t[key] is not None and t[key] != 0]
    return sum(vals)/len(vals) if vals else 0

for metric, key in [
    ("Avg entry price", "ep"),
    ("Avg depth_ratio_5c", "depth5"),
    ("Avg depth_ratio_10c", "depth10"),
    ("Avg spread", "spread_entry"),
    ("Avg book_spread", "book_spread"),
    ("Avg score_diff", "score_diff_val"),
    ("Avg total_depth", "total_depth"),
    ("Avg combined_mid", "combined_mid"),
]:
    l = avg_metric(losses, key)
    f = avg_metric(fast10, key)
    s = avg_metric(slow10, key)
    p("  %30s %15.2f %15.2f %15.2f" % (metric, l, f, s))

p()
p("  STRATEGY DISTRIBUTION:")
for label, group in [("Losses", losses), ("Fast10 Winners", fast10), ("Slow10 Winners", slow10)]:
    stb = sum(1 for t in group if t['strategy'] == 'STB')
    maker = sum(1 for t in group if t['strategy'] == 'MAKER')
    p("    %s: STB=%d, MAKER=%d" % (label, stb, maker))

p()
p("  DIP vs SPIKE DISTRIBUTION:")
for label, group in [("Losses", losses), ("Fast10 Winners", fast10), ("Slow10 Winners", slow10)]:
    dips = sum(1 for t in group if t['is_dip'] is True)
    spikes = sum(1 for t in group if t['is_dip'] is False)
    unknown = sum(1 for t in group if t['is_dip'] is None)
    p("    %s: DIPS=%d, SPIKES=%d, UNKNOWN=%d" % (label, dips, spikes, unknown))

p()
p("  SPORT DISTRIBUTION:")
for label, group in [("Losses", losses), ("Fast10 Winners", fast10), ("Slow10 Winners", slow10), ("All Winners", winners)]:
    by_cat = defaultdict(int)
    for t in group:
        by_cat[t['cat']] += 1
    cats = ', '.join('%s=%d' % (k, v) for k, v in sorted(by_cat.items()))
    p("    %s: %s" % (label, cats))

# ============================================================
# SCORECARD
# ============================================================
p()
p("  " + "=" * 90)
p("  TRADE QUALITY SCORECARD")
p("  " + "=" * 90)
p()
p("  5 yes/no questions at entry time:")
p("    Q1: Is depth_ratio_5c >= 0.15?  (bid side has support)")
p("    Q2: Is entry price a DIP? (below first_seen or pre_10m)")
p("    Q3: Is combined_mid >= 97? (both sides still priced high)")
p("    Q4: Is book_spread <= 2? (tight book)")
p("    Q5: Is strategy STB? (not maker)")
p()

# Score each trade
tier_results = {'A': [], 'B': [], 'C': []}
tier_pnl = {'A': 0, 'B': 0, 'C': 0}

for t in closed:
    score = 0
    q1 = t['depth5'] >= 0.15
    q2 = t['is_dip'] is True
    q3 = t['combined_mid'] >= 97
    q4 = t['book_spread'] <= 2
    q5 = t['strategy'] == 'STB'
    score = sum([q1, q2, q3, q4, q5])
    t['scorecard'] = score
    t['q_answers'] = (q1, q2, q3, q4, q5)

    if score >= 5:
        tier = 'A'
    elif score >= 3:
        tier = 'B'
    else:
        tier = 'C'
    t['tier'] = tier
    tier_results[tier].append(t)
    tier_pnl[tier] += t['net_pnl']

p("  SCORECARD RESULTS:")
p("  %6s %8s %8s %8s %10s %10s %8s" % ("Tier", "Trades", "Winners", "Losers", "NetPnL", "Avg PnL", "AvgHold"))
p("  " + "-" * 70)

for tier in ['A', 'B', 'C']:
    group = tier_results[tier]
    if not group:
        p("  %6s %8d %8s %8s %10s %10s %8s" % (tier, 0, '-', '-', '-', '-', '-'))
        continue
    w = sum(1 for t in group if t['pnl'] > 0)
    l = sum(1 for t in group if t['pnl'] <= 0)
    net = tier_pnl[tier]
    avg_pnl = net / len(group)
    holds = [t['hold'] for t in group if t['hold'] > 0]
    avg_hold = sum(holds)/len(holds)/60 if holds else 0
    p("  %4s-tier %6d %8d %8d $%8.2f $%8.2f %7.1fm" % (
        tier, len(group), w, l, net/100, avg_pnl/100, avg_hold))

p()
p("  LOSSES BY TIER:")
for t in losses:
    p("    %s: %s %s %dc -> %dc (%s) score=%d/5 [depth=%s dip=%s mid=%s spread=%s stb=%s]" % (
        t['tier'], t['our_side'], t['cat'], t['ep'], t['xp'], t['exit'],
        t['scorecard'],
        'Y' if t['q_answers'][0] else 'N',
        'Y' if t['q_answers'][1] else 'N',
        'Y' if t['q_answers'][2] else 'N',
        'Y' if t['q_answers'][3] else 'N',
        'Y' if t['q_answers'][4] else 'N'))

p()
p("  FAST WINNERS (hold < 2min) BY TIER:")
fast_wins = [t for t in winners if t['hold'] < 120]
for tier in ['A', 'B', 'C']:
    n = sum(1 for t in fast_wins if t['tier'] == tier)
    p("    %s-tier: %d trades" % (tier, n))

p()
p("  SLOW WINNERS (hold > 30min) BY TIER:")
slow_wins = [t for t in winners if t['hold'] > 1800]
for tier in ['A', 'B', 'C']:
    n = sum(1 for t in slow_wins if t['tier'] == tier)
    p("    %s-tier: %d trades" % (tier, n))

# ============================================================
# PART 5: MACRO vs MICRO HARMONY
# ============================================================
p()
p('=' * 110)
p('PART 5: MACRO vs MICRO HARMONY')
p('=' * 110)
p()

p("  For each trade: MACRO context (game situation) vs MICRO trigger (market event)")
p()

# Classify macro strength
def macro_strength(t):
    """Rate macro context: STRONG, MEDIUM, WEAK."""
    reasons = []
    # Combined mid near 100 = strong consensus
    if t['combined_mid'] >= 98:
        reasons.append("consensus_high")
    elif t['combined_mid'] >= 96:
        reasons.append("consensus_medium")
    else:
        reasons.append("consensus_low")

    # Score diff (basketball)
    if t['sport'] in ('ncaamb', 'nba'):
        if t['score_diff_val'] > 0:
            if t['score_diff_val'] <= 5:
                reasons.append("close_game")
            elif t['score_diff_val'] <= 10:
                reasons.append("moderate_lead")
            else:
                reasons.append("blowout")

    # Strategy context
    if t['strategy'] == 'MAKER' and t['ep'] >= 92:
        reasons.append("high_price_maker")

    # Rate
    if 'consensus_high' in reasons and 'blowout' not in reasons:
        return 'STRONG', reasons
    elif 'consensus_low' in reasons or 'blowout' in reasons:
        return 'WEAK', reasons
    else:
        return 'MEDIUM', reasons

def micro_strength(t):
    """Rate micro trigger: STRONG, MEDIUM, WEAK."""
    reasons = []
    # Depth ratio
    if t['depth5'] >= 0.3:
        reasons.append("strong_bid_support")
    elif t['depth5'] >= 0.15:
        reasons.append("moderate_bid_support")
    elif t['depth5'] > 0:
        reasons.append("weak_bid_support")

    # Is dip
    if t['is_dip'] is True:
        reasons.append("genuine_dip")
    elif t['is_dip'] is False:
        reasons.append("buying_spike")

    # Spread
    if t['spread_entry'] <= 1:
        reasons.append("tight_spread")
    elif t['spread_entry'] >= 3:
        reasons.append("wide_spread")

    # Rate
    strong = sum(1 for r in reasons if r in ('strong_bid_support', 'genuine_dip', 'tight_spread'))
    weak = sum(1 for r in reasons if r in ('weak_bid_support', 'buying_spike', 'wide_spread'))
    if strong >= 2:
        return 'STRONG', reasons
    elif weak >= 2:
        return 'WEAK', reasons
    else:
        return 'MEDIUM', reasons

# Classify every trade
harmony_matrix = defaultdict(list)
for t in closed:
    t['macro'], t['macro_reasons'] = macro_strength(t)
    t['micro'], t['micro_reasons'] = micro_strength(t)
    key = (t['macro'], t['micro'])
    harmony_matrix[key].append(t)

p("  MACRO x MICRO MATRIX (closed trades):")
p("  %20s %12s %12s %12s" % ("", "Micro STRONG", "Micro MED", "Micro WEAK"))
p("  " + "-" * 60)
for macro in ['STRONG', 'MEDIUM', 'WEAK']:
    cells = []
    for micro in ['STRONG', 'MEDIUM', 'WEAK']:
        group = harmony_matrix[(macro, micro)]
        if group:
            w = sum(1 for t in group if t['pnl'] > 0)
            l = sum(1 for t in group if t['pnl'] <= 0)
            net = sum(t['net_pnl'] for t in group) / 100
            avg_hold = sum(t['hold'] for t in group if t['hold'] > 0) / max(1, len(group)) / 60
            cells.append("%d(%dW/%dL)" % (len(group), w, l))
        else:
            cells.append("-")
    p("  %14s MACRO %12s %12s %12s" % (macro, cells[0], cells[1], cells[2]))

p()
p("  DETAILED MATRIX (with P&L and avg hold):")
p("  %14s %8s %6s %6s %10s %8s" % ("Macro/Micro", "Trades", "Wins", "Loses", "NetPnL", "AvgHold"))
p("  " + "-" * 60)
for macro in ['STRONG', 'MEDIUM', 'WEAK']:
    for micro in ['STRONG', 'MEDIUM', 'WEAK']:
        group = harmony_matrix[(macro, micro)]
        if not group:
            continue
        w = sum(1 for t in group if t['pnl'] > 0)
        l = sum(1 for t in group if t['pnl'] <= 0)
        net = sum(t['net_pnl'] for t in group) / 100
        holds = [t['hold'] for t in group if t['hold'] > 0]
        avg_hold = sum(holds) / len(holds) / 60 if holds else 0
        p("  %7s/%-6s %8d %6d %6d $%8.2f %7.1fm" % (
            macro, micro, len(group), w, l, net, avg_hold))

p()
p("  LOSSES — MACRO/MICRO CLASSIFICATION:")
for t in losses:
    p("    %s %s %dc: MACRO=%s %s | MICRO=%s %s" % (
        t['our_side'], t['cat'], t['ep'],
        t['macro'], t['macro_reasons'],
        t['micro'], t['micro_reasons']))

p()
p("  FAST WINNERS (hold < 2min) — MACRO/MICRO:")
for t in sorted(fast_wins, key=lambda x: x['hold'])[:5]:
    p("    %s %s %dc hold=%.0fs: MACRO=%s | MICRO=%s" % (
        t['our_side'], t['cat'], t['ep'], t['hold'],
        t['macro'], t['micro']))

p()
p("  SLOW WINNERS (hold > 30min) — MACRO/MICRO:")
for t in sorted(slow_wins, key=lambda x: -x['hold'])[:5]:
    p("    %s %s %dc hold=%.1fm: MACRO=%s | MICRO=%s" % (
        t['our_side'], t['cat'], t['ep'], t['hold']/60,
        t['macro'], t['micro']))

# ============================================================
# PART 5b: KEY FINDINGS
# ============================================================
p()
p("  " + "=" * 90)
p("  KEY FINDINGS")
p("  " + "=" * 90)
p()

# What do losses have in common?
p("  WHAT LOSSES HAVE IN COMMON:")
loss_depth = [t['depth5'] for t in losses]
loss_entry = [t['ep'] for t in losses]
p("    - Both are MAKER trades (92c entry) — 0 STB losses")
p("    - Both in NCAAMB")
p("    - Avg depth_ratio_5c: %.3f (compare: winner avg %.3f)" % (
    sum(loss_depth)/len(loss_depth),
    sum(t['depth5'] for t in winners)/len(winners)))
p("    - Both entered at 92c with pre_10m showing recent price spike (%dc, %dc → 92c)" % (
    losses[0]['pre_10m'], losses[1]['pre_10m']))
p("    - Both had combined_mid = 100 — market was at ceiling when maker bid filled")

# What do fast winners have?
p()
p("  WHAT FAST WINNERS HAVE IN COMMON:")
fast_stb = sum(1 for t in fast_wins if t['strategy'] == 'STB')
fast_maker = sum(1 for t in fast_wins if t['strategy'] == 'MAKER')
fast_dips = sum(1 for t in fast_wins if t['is_dip'] is True)
p("    - %d/%d are STB trades" % (fast_stb, len(fast_wins)))
p("    - %d/%d are genuine dips (entry below reference price)" % (fast_dips, len(fast_wins)))
fast_depth = [t['depth5'] for t in fast_wins if t['depth5'] > 0]
if fast_depth:
    p("    - Avg depth_ratio_5c: %.3f" % (sum(fast_depth)/len(fast_depth)))

# What do slow winners have?
p()
p("  WHAT SLOW WINNERS HAVE IN COMMON:")
slow_stb = sum(1 for t in slow_wins if t['strategy'] == 'STB')
slow_maker = sum(1 for t in slow_wins if t['strategy'] == 'MAKER')
p("    - %d/%d are STB, %d/%d are MAKER" % (slow_stb, len(slow_wins), slow_maker, len(slow_wins)))
slow_depth = [t['depth5'] for t in slow_wins if t['depth5'] > 0]
if slow_depth:
    p("    - Avg depth_ratio_5c: %.3f" % (sum(slow_depth)/len(slow_depth)))
slow_ep = [t['ep'] for t in slow_wins]
if slow_ep:
    p("    - Avg entry price: %.1fc (higher entry = slower recovery)" % (sum(slow_ep)/len(slow_ep)))

# Scorecard verdict
p()
p("  SCORECARD VERDICT:")
for tier in ['A', 'B', 'C']:
    group = tier_results[tier]
    if not group:
        continue
    w = sum(1 for t in group if t['pnl'] > 0)
    wr = w / len(group) * 100
    net = tier_pnl[tier] / 100
    holds = [t['hold'] for t in group if t['hold'] > 0]
    avg_hold = sum(holds)/len(holds)/60 if holds else 0
    p("    %s-tier: %d trades, %.0f%% WR, $%.2f net, %.1fm avg hold" % (
        tier, len(group), wr, net, avg_hold))

# Harmony verdict
p()
p("  HARMONY VERDICT:")
strong_strong = harmony_matrix[('STRONG', 'STRONG')]
if strong_strong:
    w = sum(1 for t in strong_strong if t['pnl'] > 0)
    net = sum(t['net_pnl'] for t in strong_strong) / 100
    holds = [t['hold'] for t in strong_strong if t['hold'] > 0]
    avg = sum(holds)/len(holds)/60 if holds else 0
    p("    STRONG/STRONG: %d trades, %d wins, $%.2f net, %.1fm avg hold — THE SWEET SPOT" % (
        len(strong_strong), w, net, avg))

weak_any = harmony_matrix[('WEAK', 'STRONG')] + harmony_matrix[('WEAK', 'MEDIUM')] + harmony_matrix[('WEAK', 'WEAK')]
if weak_any:
    w = sum(1 for t in weak_any if t['pnl'] > 0)
    l = sum(1 for t in weak_any if t['pnl'] <= 0)
    net = sum(t['net_pnl'] for t in weak_any) / 100
    p("    WEAK macro (any micro): %d trades, %dW/%dL, $%.2f net — THE DANGER ZONE" % (
        len(weak_any), w, l, net))

out = '\n'.join(lines)
with open('/tmp/trade_autopsy.txt', 'w') as f:
    f.write(out)
print(out)
print('\nDone. %d lines -> /tmp/trade_autopsy.txt' % len(lines))
