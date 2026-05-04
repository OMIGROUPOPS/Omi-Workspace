#!/usr/bin/env python3
"""Replay analysis of REAL production trades from v3_enriched_trades.csv."""
import csv, math
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

# Classify and parse
for t in trades:
    mode = t.get('entry_mode', '') or ''
    t['strategy'] = 'MAKER' if '92plus' in mode else 'STB'
    ts_str = t['timestamp']
    try:
        t['dt'] = datetime.strptime(ts_str[:19], '%Y-%m-%d %H:%M:%S')
    except:
        t['dt'] = datetime(2026, 1, 1)
    t['date'] = t['dt'].strftime('%Y-%m-%d')
    t['hour'] = t['dt'].hour
    t['ep'] = si(t.get('entry_price', 0))
    t['xp'] = si(t.get('exit_price', 0))
    t['pnl'] = si(t.get('pnl_cents', 0))
    t['hold'] = sf(t.get('hold_time_seconds', 0))
    t['exit'] = t.get('exit_type', '')
    t['sport'] = t.get('sport', '')
    t['ct'] = 10 if t['sport'] == 'nhl' and t['strategy'] == 'MAKER' else 25
    t['closed'] = t['exit'] != ''

    # Category from ticker
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

    # Fee: taker entry ~1.5c/ct, maker entry ~0.3c/ct
    if t['strategy'] == 'MAKER' or t.get('entry_type') == 'maker':
        t['fee'] = max(1, t['ct'] * 0.3)
    else:
        t['fee'] = t['ct'] * 1.5

    t['net_pnl'] = t['pnl'] - t['fee'] if t['closed'] else None

closed = [t for t in trades if t['closed']]
still_open = [t for t in trades if not t['closed']]

date_range = "%s to %s" % (min(t['date'] for t in trades), max(t['date'] for t in trades))
p('=' * 100)
p('PRODUCTION REPLAY -- REAL TRADE LOG')
p('%d total trades (%d closed, %d still open)' % (len(trades), len(closed), len(still_open)))
p('Period: %s' % date_range)
p('=' * 100)

# ============================================================
# 1. EVERY CLOSED TRADE
# ============================================================
p()
p('=' * 100)
p('1. EVERY CLOSED TRADE')
p('=' * 100)

p('')
p('  %-20s %-8s %-15s %-6s %5s %5s %-12s %6s %5s %7s %7s' % (
    'Time', 'Side', 'Cat', 'Strat', 'Entry', 'Exit', 'ExitType', 'PnL', 'Fee', 'Net', 'Hold'))
p('  ' + '-' * 100)

for t in sorted(closed, key=lambda x: x['dt']):
    side = t.get('entry_side', t['ticker'].split('-')[-1])[:6]
    hold_str = '%.1fm' % (t['hold']/60) if t['hold'] > 0 else '?'
    net = t['net_pnl']
    p('  %-20s %-8s %-15s %-6s %4dc %4dc %-12s %5dc %4.0fc %6.0fc %7s' % (
        t['timestamp'][:19], side, t['cat'], t['strategy'],
        t['ep'], t['xp'], t['exit'], t['pnl'], t['fee'], net, hold_str))

if still_open:
    p('')
    p('  STILL OPEN (%d):' % len(still_open))
    for t in sorted(still_open, key=lambda x: x['dt']):
        side = t.get('entry_side', t['ticker'].split('-')[-1])[:6]
        p('  %-20s %-8s %-15s %-6s %4dc  (entry, no exit yet)' % (
            t['timestamp'][:19], side, t['cat'], t['strategy'], t['ep']))

# ============================================================
# 2. SUMMARY BY SPORT x STRATEGY
# ============================================================
p()
p('=' * 100)
p('2. SUMMARY BY SPORT x STRATEGY (closed trades only)')
p('=' * 100)

p('')
p('  %-18s %-6s %5s %5s %6s %10s %8s %10s %8s' % (
    'Cat', 'Strat', 'N', 'Wins', 'WR%', 'GrossPnL', 'Fees', 'NetPnL', 'AvgHold'))
p('  ' + '-' * 85)

grand_pnl = 0
grand_fees = 0

for strategy in ['STB', 'MAKER']:
    by_cat = defaultdict(list)
    for t in closed:
        if t['strategy'] == strategy:
            by_cat[t['cat']].append(t)

    strat_pnl = 0
    strat_fee = 0
    strat_n = 0
    strat_wins = 0

    for cat in ['ncaamb', 'nba', 'nhl', 'atp_main', 'atp_challenger', 'wta_main', 'wta_challenger']:
        ct = by_cat.get(cat, [])
        if not ct:
            continue
        wins = sum(1 for t in ct if t['pnl'] > 0)
        wr = wins / len(ct) * 100
        pnl = sum(t['pnl'] for t in ct)
        fees = sum(t['fee'] for t in ct)
        net = pnl - fees
        holds = [t['hold'] for t in ct if t['hold'] > 0]
        avg_hold = sum(holds) / len(holds) / 60 if holds else 0
        p('  %-18s %-6s %5d %5d %5.1f%% $%8.2f $%6.2f $%8.2f %7.1fm' % (
            cat, strategy, len(ct), wins, wr, pnl/100, fees/100, net/100, avg_hold))
        strat_pnl += pnl
        strat_fee += fees
        strat_n += len(ct)
        strat_wins += wins

    if strat_n:
        strat_net = strat_pnl - strat_fee
        p('  %-18s %-6s %5d %5d %5.1f%% $%8.2f $%6.2f $%8.2f' % (
            'SUBTOTAL', strategy, strat_n, strat_wins,
            strat_wins/strat_n*100, strat_pnl/100, strat_fee/100, strat_net/100))
        grand_pnl += strat_pnl
        grand_fees += strat_fee
    p('')

grand_net = grand_pnl - grand_fees
total_wins = sum(1 for t in closed if t['pnl'] > 0)
p('  %-18s %-6s %5d %5d %5.1f%% $%8.2f $%6.2f $%8.2f' % (
    'GRAND TOTAL', 'ALL', len(closed), total_wins,
    total_wins/max(1,len(closed))*100, grand_pnl/100, grand_fees/100, grand_net/100))

# ============================================================
# 3. $/HOUR BREAKDOWN
# ============================================================
p()
p('=' * 100)
p('3. $/HOUR BREAKDOWN (by date)')
p('=' * 100)

for date in sorted(set(t['date'] for t in closed)):
    day_trades = [t for t in closed if t['date'] == date]
    p('')
    p('  %s:' % date)
    by_hour = defaultdict(list)
    for t in day_trades:
        by_hour[t['hour']].append(t)

    p('  %6s %7s %5s %10s %10s' % ('Hour', 'Trades', 'Wins', 'GrossPnL', 'NetPnL'))
    p('  ' + '-' * 45)
    day_net = 0
    for h in sorted(by_hour.keys()):
        ht = by_hour[h]
        wins = sum(1 for t in ht if t['pnl'] > 0)
        pnl = sum(t['pnl'] for t in ht)
        net = sum(t['net_pnl'] for t in ht)
        day_net += net
        p('  %4d:00 %7d %5d $%8.2f $%8.2f' % (h, len(ht), wins, pnl/100, net/100))
    day_pnl = sum(t['pnl'] for t in day_trades)
    p('  %6s %7d %5d $%8.2f $%8.2f' % (
        'TOTAL', len(day_trades),
        sum(1 for t in day_trades if t['pnl'] > 0),
        day_pnl/100, day_net/100))

# ============================================================
# 4. AVERAGE TRADES PER HOUR
# ============================================================
p()
p('=' * 100)
p('4. AVERAGE TRADES PER HOUR')
p('=' * 100)

for date in sorted(set(t['date'] for t in trades)):
    day_all = [t for t in trades if t['date'] == date]
    hours_active = len(set(t['hour'] for t in day_all))
    first_h = min(t['dt'] for t in day_all)
    last_h = max(t['dt'] for t in day_all)
    span_h = (last_h - first_h).total_seconds() / 3600
    p('')
    p('  %s: %d trades across %d active hours (%.1fh span)' % (
        date, len(day_all), hours_active, span_h))
    p('    Trades/active hour: %.1f' % (len(day_all) / max(1, hours_active)))
    day_closed = [t for t in closed if t['date'] == date]
    if day_closed:
        day_net = sum(t['net_pnl'] for t in day_closed)
        p('    $/active hour: $%.2f' % (day_net / 100 / max(1, hours_active)))
        if span_h > 0.1:
            p('    $/span hour: $%.2f' % (day_net / 100 / span_h))

# ============================================================
# 5. DAY-BY-DAY P&L
# ============================================================
p()
p('=' * 100)
p('5. DAY-BY-DAY P&L')
p('=' * 100)

p('')
p('  %-12s %7s %7s %5s %6s %10s %8s %10s %5s' % (
    'Date', 'Trades', 'Closed', 'Wins', 'WR%', 'GrossPnL', 'Fees', 'NetPnL', 'Open'))
p('  ' + '-' * 78)

cumul = 0
daily_nets = []
for date in sorted(set(t['date'] for t in trades)):
    day_all = [t for t in trades if t['date'] == date]
    day_closed = [t for t in closed if t['date'] == date]
    day_open = [t for t in still_open if t['date'] == date]
    wins = sum(1 for t in day_closed if t['pnl'] > 0)
    wr = wins / len(day_closed) * 100 if day_closed else 0
    pnl = sum(t['pnl'] for t in day_closed)
    fees = sum(t['fee'] for t in day_closed)
    net = pnl - fees
    cumul += net
    daily_nets.append(net / 100)
    p('  %-12s %7d %7d %5d %5.1f%% $%8.2f $%6.2f $%8.2f %5d' % (
        date, len(day_all), len(day_closed), wins, wr,
        pnl/100, fees/100, net/100, len(day_open)))

p('')
p('  Cumulative net: $%.2f' % (cumul / 100))

# ============================================================
# 6. PROJECTION
# ============================================================
p()
p('=' * 100)
p('6. PROJECTION')
p('=' * 100)

total_closed_net = sum(t['net_pnl'] for t in closed) / 100
first_trade = min(t['dt'] for t in trades)
last_trade = max(t['dt'] for t in trades)
total_span_h = (last_trade - first_trade).total_seconds() / 3600
active_hours = len(set((t['date'], t['hour']) for t in trades))

p('')
p('  Data span: %.1f hours (%s to %s)' % (total_span_h, first_trade, last_trade))
p('  Active hours (with trades): %d' % active_hours)
p('  Closed trades: %d' % len(closed))
p('  Net P&L (closed): $%.2f' % total_closed_net)
p('  $/active hour: $%.2f' % (total_closed_net / max(1, active_hours)))
p('  $/calendar hour: $%.2f' % (total_closed_net / max(0.1, total_span_h)))

if daily_nets:
    avg_day = sum(daily_nets) / len(daily_nets)
    p('')
    p('  PROJECTIONS:')
    p('    Daily avg (from %d days):     $%.2f/day' % (len(daily_nets), avg_day))
    p('    If 24/7 at $/active-hour:     $%.2f/day' % (
        total_closed_net / max(1, active_hours) * 24))
    p('    Monthly (30d) at daily avg:   $%.2f' % (avg_day * 30))
    p('    Monthly (24/7 rate):          $%.2f' % (
        total_closed_net / max(1, active_hours) * 24 * 30))

# Still-open positions
if still_open:
    p('')
    p('  STILL OPEN: %d positions' % len(still_open))
    maker_open = [t for t in still_open if t['strategy'] == 'MAKER']
    stb_open = [t for t in still_open if t['strategy'] == 'STB']
    if stb_open:
        stb_up = sum(7 * t['ct'] for t in stb_open)
        p('    STB open (%d): if all +7c: +$%.2f' % (len(stb_open), stb_up/100))
    if maker_open:
        maker_up = sum((99 - t['ep']) * t['ct'] for t in maker_open)
        p('    Maker open (%d): if all settle win: +$%.2f' % (
            len(maker_open), maker_up/100))

# Strategy split
stb_closed = [t for t in closed if t['strategy'] == 'STB']
maker_closed = [t for t in closed if t['strategy'] == 'MAKER']
stb_net = sum(t['net_pnl'] for t in stb_closed) / 100 if stb_closed else 0
maker_net = sum(t['net_pnl'] for t in maker_closed) / 100 if maker_closed else 0
p('')
p('  STRATEGY SPLIT (closed):')
p('    STB:   $%.2f from %d trades ($%.2f/day)' % (
    stb_net, len(stb_closed), stb_net / max(0.1, len(daily_nets))))
p('    Maker: $%.2f from %d trades ($%.2f/day)' % (
    maker_net, len(maker_closed), maker_net / max(0.1, len(daily_nets))))

# ============================================================
# 7. LOSSES DETAIL
# ============================================================
p()
p('=' * 100)
p('7. EVERY LOSS')
p('=' * 100)

losses = [t for t in closed if t['pnl'] <= 0]
if losses:
    p('')
    for t in sorted(losses, key=lambda x: x['pnl']):
        side = t.get('entry_side', t['ticker'].split('-')[-1])[:8]
        p('  %s %-8s %-15s %-6s entry=%dc exit=%dc pnl=%dc (%s) hold=%.0fm' % (
            t['timestamp'][:19], side, t['cat'], t['strategy'],
            t['ep'], t['xp'], t['pnl'], t['exit'], t['hold']/60))
else:
    p('  No losses!')

out = '\n'.join(lines)
with open('/tmp/replay_results.txt', 'w') as f:
    f.write(out)
print(out)
print('\nDone. %d lines -> /tmp/replay_results.txt' % len(lines))
