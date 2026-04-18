#!/usr/bin/env python3
"""Trade audit for tennis bot — March 18, 2026"""
import requests, json, time, base64, re, sys
from collections import defaultdict
from datetime import datetime, timezone
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

API_BASE = 'https://api.elections.kalshi.com'
api_key = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
pk = serialization.load_pem_private_key(
    open('/root/Omi-Workspace/arb-executor/kalshi.pem', 'rb').read(),
    password=None, backend=default_backend())

def ah(method, path):
    ts = str(int(time.time() * 1000))
    sign_path = path.split('?')[0]  # strip query params for signing
    msg = (ts + method + sign_path).encode('utf-8')
    sig = pk.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {'KALSHI-ACCESS-KEY': api_key,
            'KALSHI-ACCESS-SIGNATURE': base64.b64encode(sig).decode(),
            'KALSHI-ACCESS-TIMESTAMP': ts, 'Content-Type': 'application/json'}

def api_get(path):
    time.sleep(0.15)
    r = requests.get(API_BASE + path, headers=ah('GET', path), timeout=15)
    if r.status_code == 200:
        return r.json()
    print('  API ERR %d: %s' % (r.status_code, path[:80]), file=sys.stderr)
    return None

SERIES = ['KXATPMATCH', 'KXWTAMATCH', 'KXATPCHALLENGERMATCH', 'KXWTACHALLENGERMATCH']
STRAT_MAP = {
    'KXATPMATCH': 'ATP_MAIN',
    'KXWTAMATCH': 'WTA_MAIN',
    'KXATPCHALLENGERMATCH': 'ATP_CHALL',
    'KXWTACHALLENGERMATCH': 'WTA_CHALL',
}

def get_strategy(ticker):
    for prefix, strat in STRAT_MAP.items():
        if ticker.startswith(prefix):
            return strat
    return '?'

def is_tennis(ticker):
    return any(ticker.startswith(s) for s in SERIES)

# ===== Step 1: Pull all orders =====
print('Pulling orders...', file=sys.stderr)
all_orders = []
cursor = ''
for _ in range(20):
    path = '/trade-api/v2/portfolio/orders?limit=100&status=all'
    if cursor:
        path += '&cursor=' + cursor
    data = api_get(path)
    if not data:
        break
    orders = data.get('orders', [])
    for o in orders:
        if not is_tennis(o.get('ticker', '')):
            continue
        created = o.get('created_time', '')
        if created >= '2026-03-18T00:00:00':
            all_orders.append(o)
    cursor = data.get('cursor', '')
    if not cursor or not orders:
        break
    if orders[-1].get('created_time', '') < '2026-03-17T00:00:00':
        break

print('Found %d tennis orders since Mar 18' % len(all_orders), file=sys.stderr)

# ===== Step 1b: Pull all fills =====
print('Pulling fills...', file=sys.stderr)
all_fills = []
cursor = ''
for _ in range(20):
    path = '/trade-api/v2/portfolio/fills?limit=100'
    if cursor:
        path += '&cursor=' + cursor
    data = api_get(path)
    if not data:
        break
    fills = data.get('fills', [])
    for f in fills:
        if not is_tennis(f.get('ticker', '')):
            continue
        created = f.get('created_time', '')
        if created >= '2026-03-18T00:00:00':
            all_fills.append(f)
    cursor = data.get('cursor', '')
    if not cursor or not fills:
        break
    if fills[-1].get('created_time', '') < '2026-03-17T00:00:00':
        break

print('Found %d tennis fills since Mar 18' % len(all_fills), file=sys.stderr)

# ===== Step 1c: Pull settlements =====
print('Pulling settlements...', file=sys.stderr)
settlements = {}
cursor = ''
for _ in range(10):
    path = '/trade-api/v2/portfolio/settlements?limit=100'
    if cursor:
        path += '&cursor=' + cursor
    data = api_get(path)
    if not data:
        break
    for s in data.get('settlements', []):
        if is_tennis(s.get('ticker', '')):
            settlements[s['ticker']] = s
    cursor = data.get('cursor', '')
    if not cursor:
        break

print('Found %d tennis settlements' % len(settlements), file=sys.stderr)

# ===== Parse bot log =====
print('Parsing bot log...', file=sys.stderr)
log_lines = []
try:
    with open('/tmp/tennis_final.log', 'r') as f:
        log_lines = f.readlines()
except:
    pass

buy_entries = []
fill_entries = []
sell_entries = []
dip_events = []
signal_events = []

for line in log_lines:
    line = line.strip()
    if not line or line < '[2026-03-18':
        continue

    # BUY lines
    m = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)_BUY\] (\w+) add#(\d+) at (\d+)c (\d+)ct oid=(\S+)', line)
    if m:
        buy_entries.append({
            'timestamp': m.group(1), 'strat': m.group(2), 'player': m.group(3),
            'add_num': int(m.group(4)), 'price': int(m.group(5)),
            'size': int(m.group(6)), 'oid_prefix': m.group(7),
        })

    # FILL lines
    m = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)_FILL\] (\w+) add#(\d+) (\d+)ct at (\d+)c \(bid=(\S+) ask=(\S+)\) total=(\d+)ct', line)
    if m:
        fill_entries.append({
            'timestamp': m.group(1), 'strat': m.group(2), 'player': m.group(3),
            'add_num': int(m.group(4)), 'fill_size': int(m.group(5)),
            'price': int(m.group(6)), 'bid': m.group(7), 'ask': m.group(8),
            'total': int(m.group(9)),
        })

    # SELL lines
    m = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)_SELL\] (\w+) resting (\d+)c (\d+)ct oid=(\S+)', line)
    if m:
        sell_entries.append({
            'timestamp': m.group(1), 'strat': m.group(2), 'player': m.group(3),
            'price': int(m.group(4)), 'size': int(m.group(5)),
        })

    # DIP lines
    m = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)_DIP\] (\w+) dip#(\d+) at (\d+)c', line)
    if m:
        dip_events.append({
            'timestamp': m.group(1), 'strat': m.group(2), 'player': m.group(3),
            'dip_num': int(m.group(4)), 'price': int(m.group(5)),
        })

    # SIGNAL lines
    m = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)_SIGNAL\] (\w+) dip#(\d+) add#(\d+) bid=(\d+)c ask=(\d+)c spread=(\d+)c', line)
    if m:
        signal_events.append({
            'timestamp': m.group(1), 'strat': m.group(2), 'player': m.group(3),
            'dip_num': int(m.group(4)), 'add_num': int(m.group(5)),
            'bid': int(m.group(6)), 'ask': int(m.group(7)), 'spread': int(m.group(8)),
        })

# ===== Group by player =====
events = defaultdict(lambda: {
    'buys': [], 'fills': [], 'sells': [], 'signals': [], 'dips': [],
    'settlement': None, 'strat': '?', 'ticker': '',
})

player_to_ticker = {}
for o in all_orders:
    tk = o.get('ticker', '')
    player = tk.split('-')[-1]
    player_to_ticker[player] = tk

for b in buy_entries:
    events[b['player']]['buys'].append(b)
    events[b['player']]['strat'] = b['strat']
for f in fill_entries:
    events[f['player']]['fills'].append(f)
for s in signal_events:
    events[s['player']]['signals'].append(s)
for d in dip_events:
    events[d['player']]['dips'].append(d)

for tk, s in settlements.items():
    player = tk.split('-')[-1]
    events[player]['settlement'] = s
    events[player]['ticker'] = tk

for o in all_orders:
    player = o.get('ticker', '').split('-')[-1]
    events[player]['ticker'] = o.get('ticker', '')

# ===== Build audit output =====
out = []
out.append('=' * 80)
out.append('  TENNIS BOT TRADE AUDIT - March 18, 2026')
out.append('  Generated: %s UTC' % datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
out.append('=' * 80)

out.append('')
out.append('STEP 1: ALL TRADES BY EVENT')
out.append('-' * 80)

total_cost = 0
total_revenue = 0
total_pnl = 0
classifications = []

sorted_players = sorted(
    [p for p in events if events[p]['fills']],
    key=lambda p: events[p]['fills'][0]['timestamp']
)

for player in sorted_players:
    ev = events[player]
    if not ev['fills']:
        continue

    ticker = ev.get('ticker', '') or player_to_ticker.get(player, '?')
    strat = ev['strat']
    settlement = ev['settlement']

    out.append('')
    out.append('  EVENT: %s' % ticker)
    out.append('  Strategy: %s | Player: %s' % (strat, player))

    # Entry details
    total_contracts = 0
    total_entry_cost = 0
    entry_prices = []

    out.append('  +-- ENTRIES ---------------------------------------------------')
    for f in ev['fills']:
        total_contracts += f['fill_size']
        cost = f['price'] * f['fill_size'] / 100
        total_entry_cost += cost
        entry_prices.append(f['price'])
        out.append('  |  add#%d  %s  %dc x %dct = $%.2f  (bid=%s ask=%s)' % (
            f['add_num'], f['timestamp'], f['price'], f['fill_size'], cost,
            f['bid'], f['ask']))

    avg_entry = sum(entry_prices) / len(entry_prices) if entry_prices else 0
    out.append('  |')
    out.append('  |  Total: %dct  Cost: $%.2f  Avg entry: %.1fc' % (
        total_contracts, total_entry_cost, avg_entry))
    out.append('  +-------------------------------------------------------------')

    total_cost += total_entry_cost

    # Outcome
    if settlement:
        result = settlement.get('market_result', '?')
        yes_cost = float(settlement.get('yes_total_cost_dollars', '0'))
        yes_count = int(float(settlement.get('yes_count_fp', '0')))

        if result == 'yes':
            revenue = yes_count  # $1 per contract
            pnl = revenue - yes_cost
            out.append('  OUTCOME: SETTLED YES -- Revenue $%.2f, Cost $%.2f, PnL +$%.2f' % (
                revenue, yes_cost, pnl))
            total_revenue += revenue
            total_pnl += pnl
        elif result == 'no':
            pnl = -yes_cost
            out.append('  OUTCOME: SETTLED NO -- TOTAL LOSS -$%.2f (%d contracts worthless)' % (
                yes_cost, yes_count))
            total_pnl += pnl
        else:
            out.append('  OUTCOME: SETTLED %s' % result)
    else:
        out.append('  OUTCOME: OPEN POSITION -- %dct at avg %.1fc' % (total_contracts, avg_entry))

    # Signal/dip context
    out.append('  +-- PRICE CONTEXT --------------------------------------------')
    if ev['dips']:
        for d in ev['dips']:
            out.append('  |  %s  dip#%d at %dc (skipped per skip_dips rule)' % (
                d['timestamp'], d['dip_num'], d['price']))

    for s in ev['signals']:
        out.append('  |  %s  SIGNAL dip#%d add#%d bid=%dc ask=%dc spread=%dc' % (
            s['timestamp'], s['dip_num'], s['add_num'], s['bid'], s['ask'], s['spread']))

    # Price direction
    if len(entry_prices) > 1:
        trend = entry_prices[-1] - entry_prices[0]
        if trend > 2:
            out.append('  |  Price RISING during DCA: %dc -> %dc (+%dc)' % (
                entry_prices[0], entry_prices[-1], trend))
        elif trend < -2:
            out.append('  |  Price FALLING during DCA: %dc -> %dc (%dc)' % (
                entry_prices[0], entry_prices[-1], trend))
        else:
            out.append('  |  Price STABLE during DCA: %dc -> %dc' % (
                entry_prices[0], entry_prices[-1]))

    if settlement:
        result = settlement.get('market_result', '?')
        if result == 'yes':
            out.append('  |  Final: Entered at %dc -> RECOVERED -> SETTLED YES' % entry_prices[0])
        else:
            out.append('  |  Final: Entered at %dc -> COLLAPSED -> SETTLED NO' % entry_prices[0])
    out.append('  +-------------------------------------------------------------')

    # Classification
    out.append('  +-- CLASSIFICATION -------------------------------------------')

    classification = 'OPEN'
    if settlement:
        result = settlement.get('market_result', '?')
        if result == 'yes':
            fills_spread = max(entry_prices) - min(entry_prices) if len(entry_prices) > 1 else 0
            if fills_spread <= 3:
                classification = 'GOOD -- Leader dip recovered to settlement'
            else:
                classification = 'GOOD (WIDE DCA) -- %dc spread across adds, recovered' % fills_spread
        else:
            first_p = entry_prices[0]
            if len(entry_prices) > 1:
                price_trend = entry_prices[-1] - entry_prices[0]
                if price_trend < -3:
                    classification = 'BAD (FALLING KNIFE) -- DCA into decline %dc->%dc' % (
                        entry_prices[0], entry_prices[-1])
                else:
                    classification = 'BAD -- Leader lost, avg entry %dc' % int(avg_entry)
            else:
                classification = 'BAD -- Single entry at %dc, leader lost' % first_p

    out.append('  |  %s' % classification)
    classifications.append((player, classification))

    # Timing analysis
    if ev['dips'] and ev['fills']:
        first_dip_ts = ev['dips'][0]['timestamp']
        first_fill_ts = ev['fills'][0]['timestamp']
        out.append('  |  First dip: %s  First buy: %s' % (first_dip_ts, first_fill_ts))
        try:
            t1 = datetime.strptime(first_dip_ts, '%Y-%m-%d %H:%M:%S')
            t2 = datetime.strptime(first_fill_ts, '%Y-%m-%d %H:%M:%S')
            delta = (t2 - t1).total_seconds()
            out.append('  |  Dip-to-buy delay: %ds' % delta)
            if delta < 10:
                out.append('  |  WARNING: PREMATURE -- old 2c dip counter fired too fast')
        except:
            pass

    if len(ev['fills']) > 1:
        try:
            ft = [datetime.strptime(f['timestamp'], '%Y-%m-%d %H:%M:%S') for f in ev['fills']]
            span = (ft[-1] - ft[0]).total_seconds()
            avg_gap = span / (len(ft) - 1)
            out.append('  |  DCA span: %d adds over %ds (avg %.0fs between adds)' % (
                len(ft), span, avg_gap))
            if span < 300 and len(ft) >= 3:
                out.append('  |  WARNING: RAPID DCA -- %d adds in %ds, dip counter not filtering' % (
                    len(ft), span))
        except:
            pass

    out.append('  +-------------------------------------------------------------')

# ===== Summary =====
out.append('')
out.append('=' * 80)
out.append('  SUMMARY')
out.append('=' * 80)
out.append('')

good = sum(1 for _, c in classifications if c.startswith('GOOD'))
bad = sum(1 for _, c in classifications if c.startswith('BAD'))
open_ct = sum(1 for _, c in classifications if c.startswith('OPEN'))

out.append('  Events traded: %d' % len(sorted_players))
out.append('  Total buy fills: %d' % sum(len(events[p]['fills']) for p in sorted_players))
out.append('  Total cost: $%.2f' % total_cost)
out.append('  Total revenue: $%.2f' % total_revenue)
out.append('  Realized PnL: $%.2f' % total_pnl)
out.append('')
out.append('  %d GOOD (settled yes) | %d BAD (settled no) | %d OPEN' % (good, bad, open_ct))
out.append('')

# Win rate
if good + bad > 0:
    out.append('  Win rate: %d/%d = %.0f%%' % (good, good + bad, 100 * good / (good + bad)))
    out.append('')

# ===== Step 4: BAD entry analysis =====
out.append('=' * 80)
out.append('  STEP 4: GAME STATE ANALYSIS -- BAD ENTRIES')
out.append('=' * 80)

for player in sorted_players:
    ev = events[player]
    s = ev.get('settlement')
    if not s or s.get('market_result') != 'no':
        continue

    ticker = ev.get('ticker', '') or player_to_ticker.get(player, '?')
    entry_prices = [f['price'] for f in ev['fills']]
    yes_cost = float(s.get('yes_total_cost_dollars', '0'))

    out.append('')
    out.append('  BAD: %s (%s) -- Lost $%.2f' % (player, ev['strat'], yes_cost))
    out.append('  Ticker: %s' % ticker)
    out.append('  Entries: %s' % '  '.join('%dc' % p for p in entry_prices))
    out.append('')

    first_p = entry_prices[0]
    last_p = entry_prices[-1] if len(entry_prices) > 1 else first_p

    out.append('  WHAT HAPPENED:')
    if len(entry_prices) >= 3 and last_p < first_p - 3:
        out.append('    - Price DECLINING during DCA: %dc -> %dc' % (first_p, last_p))
        out.append('    - Bot kept buying into a falling knife')
        out.append('    - Match was flipping -- not a temporary dip')
    elif len(entry_prices) >= 3 and last_p > first_p + 3:
        out.append('    - Price RISING during DCA: %dc -> %dc' % (first_p, last_p))
        out.append('    - Entries looked correct but leader lost anyway')
    else:
        out.append('    - Price was STABLE around %dc during entries' % int(sum(entry_prices)/len(entry_prices)))
        out.append('    - Leader appeared strong but lost the match')

    out.append('')
    out.append('  WHAT WOULD HAVE PREVENTED THIS:')
    if len(entry_prices) >= 3 and last_p < first_p - 3:
        out.append('    - Price trend filter: stop buying if bid fell >5c from first entry')
        out.append('    - Falling knife detector: blacklist ticker if 10c+ drop in 5min')
    out.append('    - Set score detection (via price jumps): large 10c+ drops = set loss')
    out.append('    - Break of serve detection: 3-5c drops in leader markets')
    out.append('    - Match flip detection: if bid crosses below 70c after entering at 80c+, exit')

    # Check double entry
    event_base = ticker.rsplit('-', 1)[0] if ticker else ''
    for other_p in sorted_players:
        if other_p == player:
            continue
        other_tk = events[other_p].get('ticker', '') or player_to_ticker.get(other_p, '')
        if other_tk and other_tk.rsplit('-', 1)[0] == event_base and events[other_p]['fills']:
            out.append('')
            out.append('  !! DOUBLE-ENTRY: Also bought %s on same match!' % other_p)
            out.append('     Same-event guard now deployed to prevent this.')

# ===== Step 5: Proposed rules =====
out.append('')
out.append('=' * 80)
out.append('  STEP 5: PROPOSED GAME STATE RULES')
out.append('=' * 80)
out.append('')
out.append('  IMPLEMENTABLE NOW (price-only, no external API):')
out.append('')
out.append('  1. PRICE TREND FILTER')
out.append('     Before entry, check 5-minute bid trend.')
out.append('     If bid has fallen >5c in last 5 min, do NOT enter.')
out.append('     Prevents: falling-knife DCA')
out.append('')
out.append('  2. CLIFF DETECTOR')
out.append('     If bid drops >10c in <2 minutes, blacklist ticker for 10 min.')
out.append('     A 10c+ cliff = set loss or break run. Not a buyable dip.')
out.append('')
out.append('  3. MATCH FLIP GUARD')
out.append('     If we entered at Xc and bid drops below X-15c, STOP adding.')
out.append('     The match has structurally flipped. Cut exposure.')
out.append('')
out.append('  4. DCA PRICE FLOOR')
out.append('     Each new add must be within 5c of avg entry price.')
out.append('     If bid is 10c+ below avg entry, match is moving against us.')
out.append('')
out.append('  REQUIRES GAME STATE API (future):')
out.append('')
out.append('  5. Set score filter: skip entry if opponent just won a set')
out.append('  6. Break detection: skip if leader just got broken on serve')
out.append('  7. Tiebreak filter: never enter during a tiebreak')
out.append('  8. Momentum: require leader to have won last 2+ points')

text = '\n'.join(out)
with open('/tmp/trade_audit_mar18.txt', 'w') as f:
    f.write(text)
print(text)
print('\n\nWritten to /tmp/trade_audit_mar18.txt', file=sys.stderr)
