"""
Intra-Kalshi Market Discovery — Phase 1
Fetches the full Kalshi market surface and flags pricing anomalies.

Usage:
    cd arb-executor
    python -m intra_kalshi.discovery [--top-n 50] [--output market_surface.json]
"""

import argparse
import asyncio
import base64
import json
import os
import sys
import time
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = 'https://api.elections.kalshi.com'
MAX_CONCURRENCY = 10
MAX_RPS = 18          # Basic tier = 20, keep 2 headroom
RETRY_BACKOFFS = [1, 2, 4]

# ---------------------------------------------------------------------------
# Auth — RSA-PSS SHA256 signing (mirrored from arb_executor_v7)
# ---------------------------------------------------------------------------

def load_credentials():
    """Load API key and PEM private key."""
    # Try .env first
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(env_path)
    except ImportError:
        pass

    api_key = os.getenv('KALSHI_API_KEY', 'f3b064d1-a02e-42a4-b2b1-132834694d23')

    pem_path = Path(__file__).resolve().parent.parent / 'kalshi.pem'
    if not pem_path.exists():
        sys.exit(f'[FATAL] kalshi.pem not found at {pem_path}')
    private_key = serialization.load_pem_private_key(
        pem_path.read_bytes(), password=None, backend=default_backend()
    )
    return api_key, private_key


def sign_request(private_key, ts: str, method: str, path: str) -> str:
    """RSA-PSS SHA256 signature over '{ts}{method}{path}'."""
    msg = f'{ts}{method}{path}'.encode('utf-8')
    sig = private_key.sign(
        msg,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(sig).decode('utf-8')


def auth_headers(api_key: str, private_key, method: str, path: str) -> dict:
    """Generate Kalshi auth headers. Signs path WITHOUT query params."""
    ts = str(int(time.time() * 1000))
    sign_path = path.split('?')[0]
    return {
        'KALSHI-ACCESS-KEY': api_key,
        'KALSHI-ACCESS-SIGNATURE': sign_request(private_key, ts, method, sign_path),
        'KALSHI-ACCESS-TIMESTAMP': ts,
        'Content-Type': 'application/json',
    }

# ---------------------------------------------------------------------------
# Rate limiter — sliding window
# ---------------------------------------------------------------------------

class RateLimiter:
    def __init__(self, max_rps: int = MAX_RPS):
        self.max_rps = max_rps
        self.timestamps: deque = deque()

    async def acquire(self):
        now = time.monotonic()
        # Purge entries older than 1 second
        while self.timestamps and now - self.timestamps[0] >= 1.0:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_rps:
            sleep_for = 1.0 - (now - self.timestamps[0])
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
        self.timestamps.append(time.monotonic())

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

async def api_get(session, api_key, private_key, path, rate_limiter, semaphore):
    """Authenticated GET with rate limiting, concurrency control, and retry."""
    url = f'{BASE_URL}{path}'
    for attempt, backoff in enumerate(RETRY_BACKOFFS + [None]):
        async with semaphore:
            await rate_limiter.acquire()
            headers = auth_headers(api_key, private_key, 'GET', path)
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status == 200:
                        return await r.json()
                    if r.status == 429 and backoff is not None:
                        print(f'  [429] Rate limited on {path}, retry in {backoff}s')
                        await asyncio.sleep(backoff)
                        continue
                    print(f'  [ERR] {r.status} on {path}')
                    return None
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if backoff is not None:
                    print(f'  [RETRY] {e} on {path}, retry in {backoff}s')
                    await asyncio.sleep(backoff)
                    continue
                print(f'  [FAIL] {e} on {path}')
                return None
    return None


async def paginate(session, api_key, private_key, base_path, result_key, rate_limiter, semaphore):
    """Cursor-based pagination. Returns list of all items."""
    items = []
    cursor = None
    page = 0
    while True:
        path = base_path + (f'&cursor={cursor}' if cursor else '')
        data = await api_get(session, api_key, private_key, path, rate_limiter, semaphore)
        if data is None:
            break
        batch = data.get(result_key, [])
        items.extend(batch)
        cursor = data.get('cursor')
        page += 1
        print(f'  Page {page}: +{len(batch)} {result_key} (total {len(items)})')
        if not cursor or not batch:
            break
    return items

# ---------------------------------------------------------------------------
# Price parsing — FixedPointDollars → cents
# ---------------------------------------------------------------------------

def fp_to_cents(val) -> int | None:
    """Convert FixedPointDollars string or legacy int to cents."""
    if val is None:
        return None
    if isinstance(val, str):
        try:
            return round(float(val) * 100)
        except ValueError:
            return None
    if isinstance(val, (int, float)):
        # Legacy: already in cents if int, or dollars if float < 1
        return int(val) if val > 1 else round(val * 100)
    return None

# ---------------------------------------------------------------------------
# Market normalization
# ---------------------------------------------------------------------------

def normalize_market(m: dict) -> dict:
    """Extract and compute fields from a raw Kalshi market dict."""
    yes_bid = fp_to_cents(m.get('yes_bid'))
    yes_ask = fp_to_cents(m.get('yes_ask'))
    no_bid = fp_to_cents(m.get('no_bid'))
    no_ask = fp_to_cents(m.get('no_ask'))
    last_price = fp_to_cents(m.get('last_price'))

    # Derive missing sides via binary identity
    if yes_ask is not None and no_bid is None:
        no_bid = 100 - yes_ask
    if no_ask is not None and yes_bid is None:
        yes_bid = 100 - no_ask
    if yes_bid is not None and no_ask is None:
        no_ask = 100 - yes_bid
    if no_bid is not None and yes_ask is None:
        yes_ask = 100 - no_bid

    spread = (yes_ask - yes_bid) if (yes_ask is not None and yes_bid is not None) else None
    yes_no_sum = (yes_ask + no_ask) if (yes_ask is not None and no_ask is not None) else None

    return {
        'ticker': m.get('ticker', ''),
        'title': m.get('title', ''),
        'event_ticker': m.get('event_ticker', ''),
        'series_ticker': m.get('series_ticker', ''),
        'category': m.get('category', ''),
        'market_type': m.get('market_type', 'binary'),
        'yes_bid': yes_bid,
        'yes_ask': yes_ask,
        'no_bid': no_bid,
        'no_ask': no_ask,
        'spread': spread,
        'yes_no_sum': yes_no_sum,
        'last_price': last_price,
        'volume_24h': m.get('volume_24h', 0) or m.get('volume', 0) or 0,
        'open_interest': m.get('open_interest', 0) or 0,
        'close_time': m.get('close_time', ''),
        'mutually_exclusive': m.get('mutually_exclusive'),
        'strike_type': m.get('strike_type'),
        'floor_strike': m.get('floor_strike'),
        'cap_strike': m.get('cap_strike'),
        'orderbook': None,
    }

# ---------------------------------------------------------------------------
# Step 1: Fetch events with nested markets
# ---------------------------------------------------------------------------

async def fetch_events_with_markets(session, api_key, pk, rl, sem):
    print('\n[1/5] Fetching events with nested markets...')
    path = '/trade-api/v2/events?status=open&with_nested_markets=true&limit=200'
    events = await paginate(session, api_key, pk, path, 'events', rl, sem)
    print(f'  → {len(events)} events fetched')

    markets_by_ticker = {}
    events_data = []
    for ev in events:
        ev_info = {
            'event_ticker': ev.get('event_ticker', ''),
            'title': ev.get('title', ''),
            'series_ticker': ev.get('series_ticker', ''),
            'category': ev.get('category', ''),
            'mutually_exclusive': ev.get('mutually_exclusive', False),
            'market_tickers': [],
        }
        for m in ev.get('markets', []):
            nm = normalize_market(m)
            nm['category'] = ev.get('category', nm.get('category', ''))
            markets_by_ticker[nm['ticker']] = nm
            ev_info['market_tickers'].append(nm['ticker'])
        events_data.append(ev_info)

    return events_data, markets_by_ticker

# ---------------------------------------------------------------------------
# Step 2: Cross-check via markets endpoint
# ---------------------------------------------------------------------------

async def fetch_orphan_markets(session, api_key, pk, rl, sem, known_tickers):
    print('\n[2/5] Cross-checking via markets endpoint...')
    path = '/trade-api/v2/markets?status=open&limit=1000'
    raw = await paginate(session, api_key, pk, path, 'markets', rl, sem)
    orphans = {}
    for m in raw:
        t = m.get('ticker', '')
        if t and t not in known_tickers:
            orphans[t] = normalize_market(m)
    print(f'  → {len(orphans)} orphan markets found')
    return orphans

# ---------------------------------------------------------------------------
# Step 3: Fetch orderbooks for top-N markets by volume
# ---------------------------------------------------------------------------

async def fetch_orderbooks(session, api_key, pk, rl, sem, markets, top_n):
    print(f'\n[3/5] Fetching orderbooks for top {top_n} markets by 24h volume...')
    sorted_markets = sorted(markets.values(), key=lambda m: m['volume_24h'], reverse=True)[:top_n]
    if not sorted_markets:
        print('  → No markets to fetch orderbooks for')
        return

    async def fetch_one(ticker):
        path = f'/trade-api/v2/markets/{ticker}/orderbook?depth=0'
        data = await api_get(session, api_key, pk, path, rl, sem)
        if data and ticker in markets:
            markets[ticker]['orderbook'] = {
                'yes': data.get('orderbook', {}).get('yes', []),
                'no': data.get('orderbook', {}).get('no', []),
            }

    tasks = [fetch_one(m['ticker']) for m in sorted_markets]
    await asyncio.gather(*tasks)
    populated = sum(1 for m in sorted_markets if markets[m['ticker']]['orderbook'] is not None)
    print(f'  → {populated}/{len(sorted_markets)} orderbooks populated')

# ---------------------------------------------------------------------------
# Step 4: Build tree + anomalies
# ---------------------------------------------------------------------------

def build_tree(events_data, markets):
    """Group into series → event → markets, compute aggregates."""
    tree = defaultdict(lambda: defaultdict(list))
    for ev in events_data:
        series = ev['series_ticker'] or '__none__'
        tree[series][ev['event_ticker']] = {
            'title': ev['title'],
            'category': ev['category'],
            'mutually_exclusive': ev.get('mutually_exclusive', False),
            'market_tickers': ev['market_tickers'],
            'market_count': len(ev['market_tickers']),
            'total_volume_24h': sum(markets[t]['volume_24h'] for t in ev['market_tickers'] if t in markets),
        }

    # Category breakdown
    cats = defaultdict(lambda: {'events': 0, 'markets': 0, 'volume_24h': 0})
    for ev in events_data:
        cat = ev.get('category', 'unknown') or 'unknown'
        cats[cat]['events'] += 1
        for t in ev['market_tickers']:
            if t in markets:
                cats[cat]['markets'] += 1
                cats[cat]['volume_24h'] += markets[t]['volume_24h']

    return dict(tree), dict(cats)


def scan_anomalies(events_data, markets):
    """Quick anomaly scan — YES+NO sum and multi-outcome sum checks."""
    anomalies = []

    # Binary sum check
    for m in markets.values():
        s = m.get('yes_no_sum')
        if s is not None and (s < 98 or s > 102):
            anomalies.append({
                'type': 'binary_sum',
                'ticker': m['ticker'],
                'event_ticker': m['event_ticker'],
                'title': m['title'],
                'yes_ask': m['yes_ask'],
                'no_ask': m['no_ask'],
                'sum': s,
                'deviation': s - 100,
            })

    # Multi-outcome sum check
    for ev in events_data:
        if not ev.get('mutually_exclusive'):
            continue
        yes_asks = []
        for t in ev['market_tickers']:
            m = markets.get(t)
            if m and m['yes_ask'] is not None:
                yes_asks.append((t, m['yes_ask']))
        if len(yes_asks) >= 2:
            total = sum(v for _, v in yes_asks)
            if total < 95 or total > 105:
                anomalies.append({
                    'type': 'multi_outcome_sum',
                    'event_ticker': ev['event_ticker'],
                    'title': ev['title'],
                    'market_count': len(yes_asks),
                    'yes_ask_sum': total,
                    'deviation': total - 100,
                    'markets': [{'ticker': t, 'yes_ask': v} for t, v in yes_asks],
                })

    return anomalies

# ---------------------------------------------------------------------------
# Step 5: Output
# ---------------------------------------------------------------------------

def print_summary(events_data, markets, categories, anomalies, top_n):
    """Print terminal summary."""
    print('\n' + '=' * 60)
    print('  KALSHI MARKET SURFACE DISCOVERY')
    print('=' * 60)

    print(f'\n  Events:  {len(events_data)}')
    print(f'  Markets: {len(markets)}')

    print('\n  --- Categories ---')
    for cat, info in sorted(categories.items(), key=lambda x: -x[1]['volume_24h']):
        print(f'    {cat:<25s} {info["events"]:>4} events  {info["markets"]:>5} mkts  vol24h={info["volume_24h"]:>10,}')

    # Market type breakdown
    types = defaultdict(int)
    for m in markets.values():
        types[m['market_type']] += 1
    print('\n  --- Market Types ---')
    for mt, cnt in sorted(types.items(), key=lambda x: -x[1]):
        print(f'    {mt:<20s} {cnt:>5}')

    # Top events by volume
    ev_vol = []
    for ev in events_data:
        vol = sum(markets[t]['volume_24h'] for t in ev['market_tickers'] if t in markets)
        ev_vol.append((ev['event_ticker'], ev['title'], len(ev['market_tickers']), vol))
    ev_vol.sort(key=lambda x: -x[3])
    print(f'\n  --- Top {min(top_n, 20)} Events by 24h Volume ---')
    for ticker, title, mcnt, vol in ev_vol[:20]:
        title_short = title[:50] + '...' if len(title) > 50 else title
        print(f'    {ticker:<30s} {mcnt:>3} mkts  vol={vol:>10,}  {title_short}')

    # Anomalies
    print(f'\n  --- Anomalies ({len(anomalies)}) ---')
    if not anomalies:
        print('    None detected')
    for a in anomalies[:20]:
        if a['type'] == 'binary_sum':
            print(f'    [BIN] {a["ticker"]:<30s} yes_ask={a["yes_ask"]}  no_ask={a["no_ask"]}  sum={a["sum"]}  (dev={a["deviation"]:+d})')
        elif a['type'] == 'multi_outcome_sum':
            print(f'    [MUT] {a["event_ticker"]:<30s} {a["market_count"]} mkts  sum_yes_ask={a["yes_ask_sum"]}  (dev={a["deviation"]:+d})')
    if len(anomalies) > 20:
        print(f'    ... and {len(anomalies) - 20} more')

    print('\n' + '=' * 60)


def save_output(events_data, markets, categories, anomalies, tree, output_path):
    """Save full surface to JSON."""
    payload = {
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'summary': {
            'total_events': len(events_data),
            'total_markets': len(markets),
            'categories': categories,
            'anomaly_count': len(anomalies),
        },
        'anomalies': anomalies,
        'events': events_data,
        'markets': {t: m for t, m in markets.items()},
        'tree': tree,
    }
    with open(output_path, 'w') as f:
        json.dump(payload, f, indent=2, default=str)
    print(f'\n  Saved to {output_path} ({os.path.getsize(output_path) / 1024:.0f} KB)')

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def run(top_n: int = 50, output: str = 'market_surface.json'):
    api_key, private_key = load_credentials()
    rate_limiter = RateLimiter()
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        # Step 1: Events with nested markets
        events_data, markets = await fetch_events_with_markets(
            session, api_key, private_key, rate_limiter, semaphore
        )

        # Step 2: Cross-check for orphan markets
        orphans = await fetch_orphan_markets(
            session, api_key, private_key, rate_limiter, semaphore, set(markets.keys())
        )
        markets.update(orphans)

        # Step 3: Orderbooks for top-N
        await fetch_orderbooks(
            session, api_key, private_key, rate_limiter, semaphore, markets, top_n
        )

    # Step 4: Build tree + anomalies
    tree, categories = build_tree(events_data, markets)
    anomalies = scan_anomalies(events_data, markets)

    # Step 5: Output
    print_summary(events_data, markets, categories, anomalies, top_n)
    save_output(events_data, markets, categories, anomalies, tree, output)


def main():
    parser = argparse.ArgumentParser(description='Kalshi Market Surface Discovery')
    parser.add_argument('--top-n', type=int, default=50, help='Number of top markets to fetch orderbooks for')
    parser.add_argument('--output', type=str, default='market_surface.json', help='Output JSON path')
    args = parser.parse_args()
    asyncio.run(run(top_n=args.top_n, output=args.output))


if __name__ == '__main__':
    main()
