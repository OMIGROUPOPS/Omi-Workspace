"""
G9 producer — full Kalshi tennis archive pull.
Scope: ~14,700 markets across 10 months.
  - Historical tier (close_time < 2026-03-02): /historical/markets + /historical/trades + /historical/markets/{ticker}/candlesticks
  - Live tier (close_time >= 2026-03-02): /markets + /markets/trades + /series/{series}/markets/{ticker}/candlesticks

Output structure (per-market):
  arb-executor/data/historical_pull/
    market_metadata/{ticker}.json
    trades/{ticker}.csv
    candlesticks/{ticker}.csv

Plus:
  enumeration/{tier}_{series}.json
  done_tickers.txt (resume checkpoint)
  build.log
  errors.log

Resumable: re-running skips tickers in done_tickers.txt
Adaptive throttle: 50ms baseline, exponential backoff on 429s
"""
import sys, os, json, csv, time, signal
from datetime import datetime, timezone
sys.path.insert(0, '/root/Omi-Workspace/arb-executor')
try:
    from swing_ladder import _kalshi_headers
except ImportError:
    from alltime_forensics import _kalshi_headers
import requests

BASE = 'https://api.elections.kalshi.com/trade-api/v2'
OUT = '/root/Omi-Workspace/arb-executor/data/historical_pull'
CUTOFF_TS = 1772409600  # 2026-03-02T00:00:00Z UTC (verified)
SERIES = ['KXATPMATCH', 'KXATPCHALLENGERMATCH', 'KXWTAMATCH', 'KXWTACHALLENGERMATCH']
RATE_DELAY = 0.05
PAGE_LIMIT_TRADES = 1000
CANDLE_INTERVAL = 1

os.makedirs(OUT + '/market_metadata', exist_ok=True)
os.makedirs(OUT + '/trades', exist_ok=True)
os.makedirs(OUT + '/candlesticks', exist_ok=True)
os.makedirs(OUT + '/enumeration', exist_ok=True)

LOG_PATH = OUT + '/build.log'
ERR_PATH = OUT + '/errors.log'
DONE_PATH = OUT + '/done_tickers.txt'

_shutdown_requested = False

def log(msg, file=None):
    target = file if file else LOG_PATH
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = '[' + ts + '] ' + msg
    print(line, flush=True)
    with open(target, 'a') as f:
        f.write(line + '\n')

def err(msg):
    log(msg, file=ERR_PATH)

def _sigterm_handler(signum, frame):
    global _shutdown_requested
    _shutdown_requested = True
    log('Shutdown signal received - finishing current market and exiting.')

signal.signal(signal.SIGINT, _sigterm_handler)
signal.signal(signal.SIGTERM, _sigterm_handler)

class Throttle:
    def __init__(self, base=RATE_DELAY, mx=30.0):
        self.delay = base
        self.base = base
        self.max = mx
    def sleep(self):
        time.sleep(self.delay)
    def back_off(self):
        self.delay = min(self.delay * 2, self.max)
        log('Throttle: backed off to ' + str(round(self.delay, 2)) + 's')
    def recover(self):
        self.delay = max(self.delay / 1.5, self.base)

throttle = Throttle()

def fetch(path, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            headers = _kalshi_headers('GET', path)
            r = requests.get(BASE + path[len('/trade-api/v2'):] if path.startswith('/trade-api/v2') else BASE + path,
                             params=params, headers=headers, timeout=30)
            if r.status_code == 200:
                throttle.recover()
                throttle.sleep()
                return r.json()
            elif r.status_code == 429:
                throttle.back_off()
                continue
            elif r.status_code in (502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            else:
                return None
        except (requests.Timeout, requests.ConnectionError) as e:
            err('Network error on ' + path + ' (attempt ' + str(attempt+1) + '): ' + str(e))
            time.sleep(2 ** attempt)
    err('Max retries exceeded for ' + path + ' ' + str(params))
    return None

def enumerate_archive():
    log('=== PASS 1: Enumeration ===')
    all_markets = []

    for series in SERIES:
        log('Enumerating /historical/markets?series_ticker=' + series)
        markets = []
        cursor = None
        pages = 0
        while pages < 100:
            params = {'series_ticker': series, 'limit': 1000}
            if cursor:
                params['cursor'] = cursor
            data = fetch('/trade-api/v2/historical/markets', params)
            if not data:
                break
            page = data.get('markets', [])
            if not page:
                break
            markets.extend(page)
            cursor = data.get('cursor')
            pages += 1
            if not cursor:
                break
        with open(OUT + '/enumeration/historical_' + series + '.json', 'w') as f:
            json.dump(markets, f, indent=2)
        log('  ' + series + ' historical: ' + str(len(markets)) + ' markets in ' + str(pages) + ' pages')
        for m in markets:
            m['_tier'] = 'historical'
        all_markets.extend(markets)

    for series in SERIES:
        log('Enumerating /markets?series_ticker=' + series + '&status=settled')
        markets = []
        cursor = None
        pages = 0
        while pages < 100:
            params = {'series_ticker': series, 'limit': 1000, 'status': 'settled'}
            if cursor:
                params['cursor'] = cursor
            data = fetch('/trade-api/v2/markets', params)
            if not data:
                break
            page = data.get('markets', [])
            if not page:
                break
            for m in page:
                ct_str = m.get('close_time', '')
                if ct_str:
                    try:
                        ct_ts = datetime.fromisoformat(ct_str.replace('Z', '+00:00')).timestamp()
                        if ct_ts >= CUTOFF_TS:
                            m['_tier'] = 'live'
                            markets.append(m)
                    except:
                        pass
            cursor = data.get('cursor')
            pages += 1
            if not cursor:
                break
        with open(OUT + '/enumeration/live_' + series + '.json', 'w') as f:
            json.dump(markets, f, indent=2)
        log('  ' + series + ' live (post-cutoff settled): ' + str(len(markets)) + ' markets in ' + str(pages) + ' pages')
        all_markets.extend(markets)

    log('Total markets enumerated: ' + str(len(all_markets)))

    with open(OUT + '/enumeration/manifest.json', 'w') as f:
        json.dump([{'ticker': m['ticker'], '_tier': m['_tier'],
                    'close_time': m.get('close_time'), 'volume_fp': m.get('volume_fp')}
                   for m in all_markets], f, indent=2)

    return all_markets

def pull_market(market):
    ticker = market['ticker']
    tier = market['_tier']

    meta_path = OUT + '/market_metadata/' + ticker + '.json'
    with open(meta_path, 'w') as f:
        json.dump(market, f, indent=2)

    ot_str = market.get('open_time', '')
    ct_str = market.get('close_time', '')
    if not ot_str or not ct_str:
        err(ticker + ': missing open_time/close_time, skipping candles + trades')
        return False
    try:
        ot = int(datetime.fromisoformat(ot_str.replace('Z', '+00:00')).timestamp())
        ct = int(datetime.fromisoformat(ct_str.replace('Z', '+00:00')).timestamp())
    except Exception as e:
        err(ticker + ': timestamp parse failed - ' + str(e))
        return False

    if tier == 'historical':
        candle_path = '/trade-api/v2/historical/markets/' + ticker + '/candlesticks'
    else:
        series = ticker.split('-')[0]
        candle_path = '/trade-api/v2/series/' + series + '/markets/' + ticker + '/candlesticks'

    candles_data = fetch(candle_path, {'start_ts': ot, 'end_ts': ct, 'period_interval': CANDLE_INTERVAL})
    if candles_data and 'candlesticks' in candles_data:
        candles = candles_data['candlesticks']
        if candles:
            flat_candles = []
            for c in candles:
                flat = {'end_period_ts': c.get('end_period_ts'),
                        'volume_fp': c.get('volume_fp'),
                        'open_interest_fp': c.get('open_interest_fp')}
                for prefix, sub in [('price', c.get('price', {})),
                                     ('yes_bid', c.get('yes_bid', {})),
                                     ('yes_ask', c.get('yes_ask', {}))]:
                    if isinstance(sub, dict):
                        for k, v in sub.items():
                            flat[prefix + '_' + k] = v
                flat_candles.append(flat)

            if flat_candles:
                all_keys = set()
                for c in flat_candles:
                    all_keys.update(c.keys())
                fieldnames = sorted(all_keys)
                with open(OUT + '/candlesticks/' + ticker + '.csv', 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(flat_candles)

    if tier == 'historical':
        trades_path = '/trade-api/v2/historical/trades'
    else:
        trades_path = '/trade-api/v2/markets/trades'

    trades = []
    cursor = None
    while True:
        params = {'ticker': ticker, 'limit': PAGE_LIMIT_TRADES}
        if cursor:
            params['cursor'] = cursor
        data = fetch(trades_path, params)
        if not data:
            break
        page = data.get('trades', [])
        if not page:
            break
        trades.extend(page)
        cursor = data.get('cursor')
        if not cursor:
            break

    if trades:
        with open(OUT + '/trades/' + ticker + '.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
            writer.writeheader()
            writer.writerows(trades)

    return True

def main():
    open(LOG_PATH, 'a').close()
    open(ERR_PATH, 'a').close()

    log('=== G9 producer starting ===')
    log('Cutoff: ' + datetime.fromtimestamp(CUTOFF_TS, tz=timezone.utc).isoformat())
    log('Output: ' + OUT)

    done = set()
    if os.path.exists(DONE_PATH):
        with open(DONE_PATH) as f:
            done = set(line.strip() for line in f if line.strip())
        log('Resume: ' + str(len(done)) + ' markets already done, skipping these')

    all_markets = enumerate_archive()

    log('=== PASS 2: Per-market pull (' + str(len(all_markets)) + ' total) ===')
    started = time.time()
    n_done = 0
    n_skipped = 0
    n_failed = 0

    all_markets.sort(key=lambda m: (m['_tier'], m.get('close_time', '')))

    with open(DONE_PATH, 'a') as done_f:
        for i, market in enumerate(all_markets):
            if _shutdown_requested:
                log('Shutdown requested - exiting cleanly')
                break
            ticker = market['ticker']
            if ticker in done:
                n_skipped += 1
                continue

            try:
                ok = pull_market(market)
                if ok:
                    done_f.write(ticker + '\n')
                    done_f.flush()
                    n_done += 1
                else:
                    n_failed += 1
            except Exception as e:
                err(ticker + ': unhandled exception - ' + str(e))
                n_failed += 1

            if (i + 1) % 100 == 0:
                elapsed = time.time() - started
                rate = (i + 1 - n_skipped) / elapsed if elapsed > 0 else 0
                remaining = (len(all_markets) - i - 1) / rate if rate > 0 else 0
                log('Progress: ' + str(i+1) + '/' + str(len(all_markets)) +
                    ' | done=' + str(n_done) + ' skipped=' + str(n_skipped) + ' failed=' + str(n_failed) +
                    ' | rate=' + str(round(rate, 1)) + '/s | ETA ' + str(round(remaining/60)) + 'min')

    elapsed_total = time.time() - started
    log('')
    log('=== DONE ===')
    log('Total time: ' + str(round(elapsed_total/60, 1)) + 'min (' + str(round(elapsed_total/3600, 1)) + 'h)')
    log('Done: ' + str(n_done) + ' | Skipped (resume): ' + str(n_skipped) + ' | Failed: ' + str(n_failed))

if __name__ == '__main__':
    main()
