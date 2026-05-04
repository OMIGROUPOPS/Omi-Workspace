#!/usr/bin/env python3
"""Perfect Bounce Discovery — optimized O(n) sliding window approach.

Instead of O(n²) pairwise comparison, uses a rolling-min approach:
1. For each tick, maintain a 5-min rolling max (the recent "top")
2. When current ask drops 10c+ below rolling max → potential drop detected
3. Once in drop state, track minimum. When ask rises 7c+ above minimum → bounce confirmed
"""
import csv, math, time as time_mod
from collections import defaultdict, deque
from datetime import datetime

lines = []
def p(s=''):
    lines.append(s)

# Load our actual trades for matching
our_trades = {}
with open('/tmp/v3_enriched_trades.csv') as f:
    for r in csv.DictReader(f):
        tk = r.get('ticker', '')
        ts_str = r.get('timestamp', '')
        try:
            dt = datetime.strptime(ts_str[:19], '%Y-%m-%d %H:%M:%S')
            entry_ts = dt.timestamp()
        except:
            entry_ts = 0
        ep = int(r.get('entry_price', 0) or 0)
        exit_type = r.get('exit_type', '')
        pnl = int(r.get('pnl_cents', 0) or 0)
        hold = float(r.get('hold_time_seconds', 0) or 0)
        mode = r.get('entry_mode', '') or ''
        strategy = 'MAKER' if '92plus' in mode else 'STB'
        if tk not in our_trades:
            our_trades[tk] = []
        our_trades[tk].append((entry_ts, ep, exit_type, pnl, hold, strategy))

print("Loaded %d tickers from trade log" % len(our_trades))

MIN_ENTRY_ASK = 55
MAX_ENTRY_ASK = 90
SPORT_SPREAD_MAX = {"ncaamb": 4, "nba": 4, "nhl": 8, "tennis": 6, "mlb": 4}

class BounceDetector:
    def __init__(self):
        self.bounces_by_sport = defaultdict(list)
        self.tickers_processed = 0
        self.tickers_with_bounces = 0
        self.total_ticks = 0

    def process_ticker(self, ticker, ticks):
        if len(ticks) < 20:
            return

        sport = ticks[0]['sport']
        side = ticks[0]['kalshi_side']

        # Build price array
        prices = []
        for t in ticks:
            ts = float(t['bbo_timestamp'])
            ask_raw = t.get('ask', '')
            bid_raw = t.get('bid', '')
            spread_raw = t.get('spread', '')
            if not ask_raw:
                continue
            try:
                ask = int(ask_raw)
                bid = int(bid_raw) if bid_raw else None
                spread = int(spread_raw) if spread_raw else None
            except (ValueError, TypeError):
                continue
            prices.append((ts, ask, bid, spread,
                           t.get('period', ''),
                           t.get('score_diff', ''),
                           t.get('home_score', ''),
                           t.get('away_score', '')))

        if len(prices) < 20:
            return

        # O(n) bounce detection using state machine
        # States: WATCHING (looking for drop), DROPPING (in a drop, tracking bottom), RECOVERING
        n = len(prices)

        # Rolling 5-min max using deque
        max_deque = deque()  # (index, ask) — monotone decreasing
        DROP_THRESH = 10
        RECOVERY_THRESH = 7
        DROP_WINDOW = 300  # 5 min
        RECOVERY_WINDOW = 600  # 10 min

        bounces_found = []
        i = 0

        while i < n:
            ts_i, ask_i, bid_i, spread_i = prices[i][:4]

            # Maintain 5-min rolling max
            while max_deque and prices[max_deque[-1][0]][0] < ts_i - DROP_WINDOW:
                max_deque.popleft()
            while max_deque and prices[max_deque[-1][0]][1] <= ask_i:
                max_deque.pop()
            max_deque.append((i, ask_i))

            rolling_max = prices[max_deque[0][0]][1]
            top_idx = max_deque[0][0]

            # Check if current price is 10c+ below rolling max
            drop = rolling_max - ask_i
            if drop >= DROP_THRESH:
                # We're in a potential drop. Find the true bottom
                bottom_ask = ask_i
                bottom_idx = i
                bottom_ts = ts_i

                # Scan forward to find the minimum within next 60 seconds
                j = i + 1
                while j < n and prices[j][0] - ts_i < 60:
                    if prices[j][1] < bottom_ask:
                        bottom_ask = prices[j][1]
                        bottom_idx = j
                        bottom_ts = prices[j][0]
                    j += 1

                # Now look for recovery from the bottom
                max_recovery = 0
                recovery_idx = None
                time_to_7c = None

                # Pre-bottom data (2 min before bottom)
                pre_spreads = []
                pre_bids = []
                for k in range(max(0, bottom_idx - 100), bottom_idx):
                    if bottom_ts - prices[k][0] <= 120:
                        if prices[k][3] is not None:
                            pre_spreads.append(prices[k][3])
                        if prices[k][2] is not None:
                            pre_bids.append(prices[k][2])

                # Pre-bottom price trajectory for deceleration
                pre_asks = []
                for k in range(max(0, bottom_idx - 30), bottom_idx):
                    if bottom_ts - prices[k][0] <= 120:
                        pre_asks.append(prices[k][1])

                post_spreads = []

                k = bottom_idx + 1
                while k < n and prices[k][0] - bottom_ts <= RECOVERY_WINDOW:
                    recovery = prices[k][1] - bottom_ask
                    if prices[k][3] is not None:
                        post_spreads.append(prices[k][3])
                    if recovery > max_recovery:
                        max_recovery = recovery
                        recovery_idx = k
                    if recovery >= RECOVERY_THRESH and time_to_7c is None:
                        time_to_7c = prices[k][0] - bottom_ts
                    k += 1

                if max_recovery >= RECOVERY_THRESH:
                    # Confirmed bounce!
                    top_ts = prices[top_idx][0]
                    actual_drop = prices[top_idx][1] - bottom_ask

                    # Check if we traded this
                    traded = False
                    our_entry_price = None
                    our_pnl = None
                    our_strategy = None
                    for (ets, ep, ext, opnl, oh, ostrat) in our_trades.get(ticker, []):
                        if abs(ets - bottom_ts) < 300:
                            traded = True
                            our_entry_price = ep
                            our_pnl = opnl
                            our_strategy = ostrat
                            break

                    # Miss reasons
                    miss_reasons = []
                    if not traded:
                        if bottom_ask < MIN_ENTRY_ASK:
                            miss_reasons.append('below_floor')
                        if bottom_ask > MAX_ENTRY_ASK:
                            miss_reasons.append('above_ceiling')
                        at_spread = prices[bottom_idx][3]
                        if at_spread and at_spread > SPORT_SPREAD_MAX.get(sport, 4):
                            miss_reasons.append('spread_too_wide')
                        sd_str = prices[bottom_idx][5]
                        if sd_str and sd_str.lstrip('-').isdigit():
                            sd = abs(int(sd_str))
                            if sd >= 10:
                                miss_reasons.append('score_diff_high')
                        if time_to_7c is not None and time_to_7c < 30:
                            miss_reasons.append('too_fast_bounce')
                        if not miss_reasons:
                            miss_reasons.append('filter_passed_but_missed')

                    # Price deceleration
                    price_decel = False
                    if len(pre_asks) >= 4:
                        mid_pt = len(pre_asks) // 2
                        first_drop = pre_asks[0] - pre_asks[mid_pt] if pre_asks[0] > pre_asks[mid_pt] else 0
                        second_drop = pre_asks[mid_pt] - pre_asks[-1] if pre_asks[mid_pt] > pre_asks[-1] else 0
                        price_decel = second_drop < first_drop * 0.5 if first_drop > 0 else False

                    # Bid stabilization
                    bid_stable = False
                    if len(pre_bids) >= 3:
                        recent = pre_bids[-5:] if len(pre_bids) >= 5 else pre_bids
                        bid_stable = (max(recent) - min(recent)) <= 3

                    # Recovery rate (c/min)
                    if recovery_idx and prices[recovery_idx][0] > bottom_ts:
                        recovery_rate = max_recovery / ((prices[recovery_idx][0] - bottom_ts) / 60.0)
                    else:
                        recovery_rate = 0

                    bounce = {
                        'ticker': ticker, 'side': side, 'sport': sport,
                        'top_ask': prices[top_idx][1], 'top_ts': top_ts,
                        'bottom_ask': bottom_ask, 'bottom_ts': bottom_ts,
                        'drop_size': actual_drop,
                        'time_to_bottom': bottom_ts - top_ts,
                        'max_recovery': max_recovery,
                        'time_to_recovery': time_to_7c,
                        'traded': traded,
                        'our_entry_price': our_entry_price,
                        'our_pnl': our_pnl,
                        'our_strategy': our_strategy,
                        'miss_reasons': miss_reasons,
                        'at_bottom_spread': prices[bottom_idx][3],
                        'at_bottom_bid': prices[bottom_idx][2],
                        'pre_bottom_avg_spread': sum(pre_spreads) / len(pre_spreads) if pre_spreads else None,
                        'price_decel': price_decel,
                        'bid_stable': bid_stable,
                        'recovery_rate': recovery_rate,
                        'score_diff': prices[bottom_idx][5],
                        'period': prices[bottom_idx][4],
                        'post_bottom_avg_spread': sum(post_spreads) / len(post_spreads) if post_spreads else None,
                    }
                    bounces_found.append(bounce)

                # Skip ahead past this bounce to avoid duplicates
                skip_to = bottom_idx + 1
                while skip_to < n and prices[skip_to][0] - bottom_ts < 120:
                    skip_to += 1
                i = skip_to
                continue

            i += 1

        if bounces_found:
            self.bounces_by_sport[sport].extend(bounces_found)
            self.tickers_with_bounces += 1
        self.tickers_processed += 1
        self.total_ticks += len(prices)


# Stream through file
detector = BounceDetector()
current_ticker = None
current_ticks = []
t0 = time_mod.time()

with open('/tmp/v2_sorted.csv') as f:
    reader = csv.DictReader(f)
    row_count = 0
    for row in reader:
        row_count += 1
        ticker = row['kalshi_ticker']

        if ticker != current_ticker:
            if current_ticker and current_ticks:
                detector.process_ticker(current_ticker, current_ticks)
            current_ticker = ticker
            current_ticks = []

            if row_count % 500000 == 0:
                elapsed = time_mod.time() - t0
                nb = sum(len(v) for v in detector.bounces_by_sport.values())
                print(f"  ...{row_count/1e6:.1f}M rows, {detector.tickers_processed} tickers, "
                      f"{nb} bounces, {elapsed:.0f}s")

        current_ticks.append(row)

    if current_ticker and current_ticks:
        detector.process_ticker(current_ticker, current_ticks)

elapsed = time_mod.time() - t0
total_bounces = sum(len(v) for v in detector.bounces_by_sport.values())
print(f"Done: {row_count} rows, {detector.tickers_processed} tickers, "
      f"{total_bounces} bounces in {elapsed:.0f}s")

all_bounces = []
for sport, bounces in detector.bounces_by_sport.items():
    all_bounces.extend(bounces)

# ============================================================
# REPORT
# ============================================================
p('=' * 120)
p('THE PERFECT BOUNCE DISCOVERY')
p('%d bounces found across %d tickers (%.1fM ticks in %.0fs)' % (
    len(all_bounces), detector.tickers_with_bounces, detector.total_ticks / 1e6, elapsed))
p('Definition: drop >= 10c in <= 5 min, then recovery >= 7c in <= 10 min')
p('=' * 120)

# ============================================================
# 1. BOUNCE CENSUS
# ============================================================
p()
p('=' * 120)
p('1. BOUNCE CENSUS BY SPORT')
p('=' * 120)
p()
p('  %-12s %8s %8s %8s %9s %9s %10s %10s' % (
    'Sport', 'Total', 'Entered', 'Missed', 'AvgDrop', 'AvgBounce', 'AvgToBot', 'AvgToRecov'))
p('  ' + '-' * 95)

total_entered = 0
total_missed = 0
for sport in ['ncaamb', 'nba', 'nhl', 'tennis', 'mlb']:
    bounces = detector.bounces_by_sport.get(sport, [])
    if not bounces:
        continue
    entered = [b for b in bounces if b['traded']]
    missed = [b for b in bounces if not b['traded']]
    total_entered += len(entered)
    total_missed += len(missed)
    avg_drop = sum(b['drop_size'] for b in bounces) / len(bounces)
    avg_bounce = sum(b['max_recovery'] for b in bounces) / len(bounces)
    ttb = [b['time_to_bottom'] for b in bounces if b['time_to_bottom'] > 0]
    avg_ttb = sum(ttb) / len(ttb) / 60 if ttb else 0
    ttr = [b['time_to_recovery'] for b in bounces if b['time_to_recovery'] is not None]
    avg_ttr = sum(ttr) / len(ttr) / 60 if ttr else 0
    p('  %-12s %8d %8d %8d %8.1fc %8.1fc %9.1fm %9.1fm' % (
        sport, len(bounces), len(entered), len(missed),
        avg_drop, avg_bounce, avg_ttb, avg_ttr))

p()
p('  TOTAL: %d bounces (%d entered, %d missed)' % (len(all_bounces), total_entered, total_missed))

# ============================================================
# 2. WHY WE MISSED
# ============================================================
p()
p('=' * 120)
p('2. WHY WE MISSED BOUNCES')
p('=' * 120)
p()

missed = [b for b in all_bounces if not b['traded']]
reason_counts = defaultdict(int)
for b in missed:
    for r in b['miss_reasons']:
        reason_counts[r] += 1

p('  %-35s %8s %8s' % ('Reason', 'Count', '% Miss'))
p('  ' + '-' * 55)
for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
    p('  %-35s %8d %7.1f%%' % (reason, count, count / max(1, len(missed)) * 100))

p()
p('  BY SPORT:')
for sport in ['ncaamb', 'nba', 'nhl', 'tennis', 'mlb']:
    sm = [b for b in missed if b['sport'] == sport]
    if not sm:
        continue
    p()
    p('  %s (%d missed):' % (sport, len(sm)))
    sr = defaultdict(int)
    for b in sm:
        for r in b['miss_reasons']:
            sr[r] += 1
    for r, c in sorted(sr.items(), key=lambda x: -x[1]):
        p('    %-30s %5d' % (r, c))

# ============================================================
# 3. ENTRY EFFICIENCY
# ============================================================
p()
p('=' * 120)
p('3. ENTRY EFFICIENCY ON CAUGHT BOUNCES')
p('=' * 120)
p()

caught = [b for b in all_bounces if b['traded']]
if caught:
    entry_deltas = []
    capture_pcts = []
    for b in caught:
        if b['our_entry_price'] and b['bottom_ask']:
            delta = b['our_entry_price'] - b['bottom_ask']
            entry_deltas.append(delta)
            if b['max_recovery'] > 0:
                capture_pcts.append(min(100, 7 / b['max_recovery'] * 100))

    if entry_deltas:
        p('  Entry precision (how far above bottom):')
        p('    Mean: %.1fc above bottom' % (sum(entry_deltas) / len(entry_deltas)))
        sorted_d = sorted(entry_deltas)
        p('    Median: %.1fc' % sorted_d[len(sorted_d)//2])
        p('    At/near bottom (<=2c): %d/%d (%.0f%%)' % (
            sum(1 for d in entry_deltas if d <= 2), len(entry_deltas),
            sum(1 for d in entry_deltas if d <= 2) / len(entry_deltas) * 100))
        p('    Within 5c: %d/%d (%.0f%%)' % (
            sum(1 for d in entry_deltas if d <= 5), len(entry_deltas),
            sum(1 for d in entry_deltas if d <= 5) / len(entry_deltas) * 100))

    if capture_pcts:
        p()
        p('  Bounce capture (7c exit vs total available):')
        p('    Avg capture: %.0f%% of total bounce' % (sum(capture_pcts) / len(capture_pcts)))
        big = [b for b in caught if b['max_recovery'] >= 15]
        p('    Bounces >= 15c where we took only 7c: %d' % len(big))
        p('    Avg total bounce on our trades: %.1fc (we take 7c)' % (
            sum(b['max_recovery'] for b in caught) / len(caught)))

# ============================================================
# 4. PERFECT BOUNCE PROFILE
# ============================================================
p()
p('=' * 120)
p('4. THE PERFECT BOUNCE PROFILE — ORDERBOOK ANATOMY')
p('=' * 120)
p()

fast_bounces = [b for b in all_bounces if b['time_to_recovery'] is not None and b['time_to_recovery'] < 120]
slow_bounces = [b for b in all_bounces if b['time_to_recovery'] is not None and b['time_to_recovery'] >= 120]

for label, group in [('FAST (recover < 2min)', fast_bounces),
                     ('SLOW (recover >= 2min)', slow_bounces),
                     ('ALL', all_bounces)]:
    if not group:
        continue
    p('  %s (%d bounces):' % (label, len(group)))

    pre_sp = [b['pre_bottom_avg_spread'] for b in group if b['pre_bottom_avg_spread'] is not None]
    at_sp = [b['at_bottom_spread'] for b in group if b['at_bottom_spread'] is not None]
    post_sp = [b['post_bottom_avg_spread'] for b in group if b['post_bottom_avg_spread'] is not None]

    if pre_sp:
        p('    2min BEFORE — avg spread: %.1fc' % (sum(pre_sp)/len(pre_sp)))
    if at_sp:
        p('    AT BOTTOM — avg spread: %.1fc' % (sum(at_sp)/len(at_sp)))
    if post_sp:
        p('    DURING RECOVERY — avg spread: %.1fc' % (sum(post_sp)/len(post_sp)))

    # Spread tightening pattern
    if pre_sp and at_sp:
        p('    Spread change (pre→bottom): %+.1fc' % (sum(at_sp)/len(at_sp) - sum(pre_sp)/len(pre_sp)))

    rates = [b['recovery_rate'] for b in group if b['recovery_rate'] > 0]
    if rates:
        p('    Recovery rate: %.1fc/min' % (sum(rates)/len(rates)))

    decel = sum(1 for b in group if b['price_decel'])
    stable = sum(1 for b in group if b['bid_stable'])
    tight = sum(1 for b in group if b['at_bottom_spread'] is not None and b['at_bottom_spread'] <= 3)
    p('    Price decelerating before bottom: %d/%d (%.0f%%)' % (decel, len(group), decel/max(1,len(group))*100))
    p('    Bid stabilizing at bottom: %d/%d (%.0f%%)' % (stable, len(group), stable/max(1,len(group))*100))
    p('    Spread <= 3c at bottom: %d/%d (%.0f%%)' % (tight, len(group), tight/max(1,len(group))*100))
    p()

# ============================================================
# 5. REAL-TIME DETECTION
# ============================================================
p('=' * 120)
p('5. CAN WE DETECT THE BOUNCE FORMING?')
p('=' * 120)
p()

triple = [b for b in all_bounces if b['price_decel'] and b['bid_stable']
          and b.get('at_bottom_spread') is not None and b['at_bottom_spread'] <= 3]
double = [b for b in all_bounces if sum([b['price_decel'], b['bid_stable'],
          (b.get('at_bottom_spread') or 99) <= 3]) >= 2]

p('  SIGNAL PREVALENCE:')
p('    Price decelerating: %d/%d (%.0f%%)' % (
    sum(1 for b in all_bounces if b['price_decel']), len(all_bounces),
    sum(1 for b in all_bounces if b['price_decel']) / max(1,len(all_bounces)) * 100))
p('    Bid stabilizing: %d/%d (%.0f%%)' % (
    sum(1 for b in all_bounces if b['bid_stable']), len(all_bounces),
    sum(1 for b in all_bounces if b['bid_stable']) / max(1,len(all_bounces)) * 100))
p('    Spread <= 3c: %d/%d (%.0f%%)' % (
    sum(1 for b in all_bounces if (b.get('at_bottom_spread') or 99) <= 3), len(all_bounces),
    sum(1 for b in all_bounces if (b.get('at_bottom_spread') or 99) <= 3) / max(1,len(all_bounces)) * 100))
p()
p('    ALL 3 signals: %d/%d (%.0f%%)' % (len(triple), len(all_bounces), len(triple)/max(1,len(all_bounces))*100))
p('    >= 2 signals: %d/%d (%.0f%%)' % (len(double), len(all_bounces), len(double)/max(1,len(all_bounces))*100))

if triple:
    traded_t = sum(1 for b in triple if b['traded'])
    p()
    p('    Triple-signal traded: %d/%d (%.0f%%)' % (traded_t, len(triple), traded_t/len(triple)*100))
    p('    Triple-signal missed: %d' % (len(triple) - traded_t))

# FALSE POSITIVE CHECK: drops of 10c+ that did NOT bounce back
# We can estimate this from the ratio of bounces vs total drops
p()
p('  FALSE POSITIVE RISK:')
p('    Total bounces found: %d across %.1f days' % (len(all_bounces), (1772997221-1772693371)/86400))
p('    (We only tracked bounces. Drops without recovery = different analysis)')

# ============================================================
# 6. MISSED BOUNCES THAT PASSED FILTERS
# ============================================================
p()
p('=' * 120)
p('6. MISSED BOUNCES THAT PASSED ALL FILTERS')
p('=' * 120)
p()

passable = [b for b in missed if 'filter_passed_but_missed' in b['miss_reasons']]
too_fast = [b for b in missed if 'too_fast_bounce' in b['miss_reasons']]

p('  Passed all filters but missed: %d' % len(passable))
p('  Too fast to catch (< 30s): %d' % len(too_fast))
p()

if passable:
    p('  TOP 30 PASSABLE MISSED (by bounce size):')
    p('  %-12s %-10s %6s %6s %6s %8s %8s %-6s %6s' % (
        'Sport', 'Side', 'Bottom', 'Drop', 'Bounce', 'ToBot', 'ToRecov', 'Period', 'Spread'))
    p('  ' + '-' * 85)
    for b in sorted(passable, key=lambda x: -x['max_recovery'])[:30]:
        ttb = b['time_to_bottom'] / 60 if b['time_to_bottom'] else 0
        ttr = b['time_to_recovery'] / 60 if b['time_to_recovery'] else 0
        sp = b['at_bottom_spread'] if b['at_bottom_spread'] is not None else '?'
        p('  %-12s %-10s %5dc %5dc %5dc %7.1fm %7.1fm %-6s %5sc' % (
            b['sport'], b['side'], b['bottom_ask'], b['drop_size'],
            b['max_recovery'], ttb, ttr, b.get('period', '?'), str(sp)))

    p()
    p('  WHY WEREN\'T THESE CAUGHT?')
    very_fast = sum(1 for b in passable if b['time_to_recovery'] is not None and b['time_to_recovery'] < 60)
    moderate = sum(1 for b in passable if b['time_to_recovery'] is not None and 60 <= b['time_to_recovery'] < 300)
    slow_m = sum(1 for b in passable if b['time_to_recovery'] is not None and b['time_to_recovery'] >= 300)
    p('    Recovery < 1 min (may not react in time): %d' % very_fast)
    p('    Recovery 1-5 min (should catch): %d' % moderate)
    p('    Recovery 5+ min (definitely should catch): %d' % slow_m)
    p('    Note: may be on unsubscribed tickers or bot was at rate limit')

if too_fast:
    p()
    p('  TOO-FAST BOUNCES (< 30s):')
    by_sport = defaultdict(int)
    for b in too_fast:
        by_sport[b['sport']] += 1
    for s, c in sorted(by_sport.items(), key=lambda x: -x[1]):
        p('    %s: %d' % (s, c))

# ============================================================
# 7. PROJECTION
# ============================================================
p()
p('=' * 120)
p('7. PROJECTION — CATCHING EVERY BOUNCE')
p('=' * 120)
p()

data_span_days = (1772997221 - 1772693371) / 86400
avg_net_per_bounce = 112  # cents from replay

current_per_day = total_entered / max(0.1, data_span_days)
catchable = [b for b in passable if b['time_to_recovery'] is not None and b['time_to_recovery'] >= 60]
additional_per_day = len(catchable) / max(0.1, data_span_days)

p('  Data span: %.1f days' % data_span_days)
p()
p('  CURRENT PERFORMANCE:')
p('    Bounces caught: %d (%.1f/day)' % (total_entered, current_per_day))
current_rev = current_per_day * avg_net_per_bounce / 100
p('    Revenue: $%.2f/day' % current_rev)
p()
p('  CATCHABLE MISSED (passed filters, >= 1min recovery):')
p('    Count: %d (%.1f/day additional)' % (len(catchable), additional_per_day))
add_rev = additional_per_day * avg_net_per_bounce / 100
p('    Additional revenue: $%.2f/day' % add_rev)
p()
p('  TOTAL IF PERFECT:')
total_per_day = current_per_day + additional_per_day
total_rev = total_per_day * avg_net_per_bounce / 100
p('    Bounces/day: %.1f' % total_per_day)
p('    Revenue: $%.2f/day' % total_rev)
p('    Monthly: $%.2f' % (total_rev * 30))
p()

# A-tier assessment
p('  A-TIER ASSESSMENT:')
if catchable:
    avg_drop = sum(b['drop_size'] for b in catchable) / len(catchable)
    avg_rec = sum(b['max_recovery'] for b in catchable) / len(catchable)
    ttr_vals = [b['time_to_recovery'] for b in catchable if b['time_to_recovery']]
    avg_ttr = sum(ttr_vals) / len(ttr_vals) / 60 if ttr_vals else 0
    p('    Avg drop: %.1fc | Avg bounce: %.1fc | Avg time to +7c: %.1fm' % (avg_drop, avg_rec, avg_ttr))
    decel_pct = sum(1 for b in catchable if b['price_decel']) / len(catchable) * 100
    stable_pct = sum(1 for b in catchable if b['bid_stable']) / len(catchable) * 100
    p('    Price decel: %.0f%% | Bid stable: %.0f%%' % (decel_pct, stable_pct))
    if avg_rec > 12:
        p('    VERDICT: YES — large bounces, high confidence')
    elif avg_rec > 8:
        p('    VERDICT: MOSTLY — solid bounces')
    else:
        p('    VERDICT: MARGINAL — tight exits')
else:
    p('    No catchable missed bounces found')

# ============================================================
# SUMMARY
# ============================================================
p()
p('=' * 120)
p('SUMMARY')
p('=' * 120)
p()
p('  Total bounces in 3.5 days of BBO: %d' % len(all_bounces))
p('  We traded: %d (%.0f%%)' % (total_entered, total_entered/max(1,len(all_bounces))*100))
p('  We missed: %d' % total_missed)
p('    Below floor/above ceiling: %d' % (reason_counts.get('below_floor',0)+reason_counts.get('above_ceiling',0)))
p('    Spread too wide: %d' % reason_counts.get('spread_too_wide', 0))
p('    Score diff high: %d' % reason_counts.get('score_diff_high', 0))
p('    Too fast (< 30s): %d' % reason_counts.get('too_fast_bounce', 0))
p('    Passed filters but missed: %d' % reason_counts.get('filter_passed_but_missed', 0))
p()
p('  THE OPPORTUNITY:')
p('    Current: %.1f bounces/day -> $%.2f/day' % (current_per_day, current_rev))
p('    Perfect: %.1f bounces/day -> $%.2f/day' % (total_per_day, total_rev))
p('    Gap: %.1f additional bounces/day -> $%.2f/day uplift' % (additional_per_day, add_rev))

out = '\n'.join(lines)
with open('/tmp/perfect_bounce_discovery.txt', 'w') as f:
    f.write(out)
print(out)
print('\nDone. %d lines -> /tmp/perfect_bounce_discovery.txt' % len(lines))
