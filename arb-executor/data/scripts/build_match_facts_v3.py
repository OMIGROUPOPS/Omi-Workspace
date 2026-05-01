"""
Build match_facts_v3.csv — the canonical match-start source for Phase 3 Stage 1.

Two passes:
1. Kalshi API: enumerate in-window event_tickers, pull /events/{event_ticker} metadata.
   Output: /tmp/match_facts_v3_metadata.csv (per-market rows with all Kalshi fields)
2. bbo_log_v4 stream: for each ticker, run volatility-jump detector to find pregame_close_ts.
   Algorithm matches /tmp/extract_facts.py lines 60-95: mid jump >= 3c within 30s sustained 2 windows.
   Fallback if never found: 80% of ticker lifetime within open_time / close_time bounds.
"""
import sys, os, csv, time, json, gzip, sqlite3, requests
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, '/root/Omi-Workspace/arb-executor')
from alltime_forensics import _kalshi_headers

WINDOW_START = '2026-03-20'
WINDOW_END = '2026-04-10'
DB_PATH = '/root/Omi-Workspace/arb-executor/tennis.db'
BBO_PATH = '/tmp/bbo_log_v4.csv.gz'
OUT_METADATA = '/tmp/match_facts_v3_metadata.csv'
OUT_FINAL = '/tmp/match_facts_v3.csv'
LOG_PATH = '/tmp/build_match_facts_v3.log'
RATE_LIMIT_DELAY = 0.05

JUMP_CENTS = 3
JUMP_WINDOW_SEC = 30
SUSTAIN_WINDOWS = 2

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = '[' + ts + '] ' + msg
    print(line, flush=True)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')

def parse_iso(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp()

def parse_bbo_ts(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()

def pass1_kalshi_metadata():
    log('=== PASS 1: Kalshi API event metadata pull ===')
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT DISTINCT event_ticker FROM historical_events WHERE date(first_ts) >= ? AND date(first_ts) <= ?",
                (WINDOW_START, WINDOW_END))
    event_tickers = [r[0] for r in cur.fetchall()]
    con.close()
    log('In-window event_tickers from historical_events: ' + str(len(event_tickers)))

    rows_out = []
    errors = 0
    start_time = time.time()

    for i, et in enumerate(event_tickers):
        if i and i % 100 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            eta = (len(event_tickers) - i) / rate / 60 if rate > 0 else 0
            log('  Pass 1: ' + str(i) + '/' + str(len(event_tickers)) +
                ' (' + str(round(rate, 1)) + ' req/s, ETA ' + str(round(eta, 1)) + 'min)')
        try:
            path = '/trade-api/v2/events/' + et
            headers = _kalshi_headers('GET', path)
            r = requests.get('https://api.elections.kalshi.com' + path, headers=headers, timeout=15)
            if r.status_code != 200:
                errors += 1
                continue
            data = r.json()
            ev = data.get('event', {})
            markets = data.get('markets', []) or ev.get('markets', [])
            event_title = ev.get('title', '')
            event_subtitle = ev.get('sub_title', '')
            event_category = ev.get('category', '')
            competition = ev.get('product_metadata', {}).get('competition', '')

            for m in markets:
                rows_out.append({
                    'event_ticker': et,
                    'ticker_id': m.get('ticker', ''),
                    'category': event_category,
                    'title': m.get('title', '') or event_title,
                    'sub_title': event_subtitle,
                    'competition': competition,
                    'open_time': m.get('open_time', ''),
                    'close_time': m.get('close_time', ''),
                    'expected_expiration_time': m.get('expected_expiration_time', ''),
                    'settlement_ts': m.get('settlement_ts', ''),
                    'result': m.get('result', ''),
                    'expiration_value': m.get('expiration_value', ''),
                    'settlement_value_dollars': m.get('settlement_value_dollars', ''),
                    'volume_fp': m.get('volume_fp', ''),
                    'open_interest_fp': m.get('open_interest_fp', ''),
                    'last_price_dollars': m.get('last_price_dollars', ''),
                })
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            errors += 1
            if errors < 10:
                log('  Error on ' + et + ': ' + str(e))

    log('Pass 1 complete: ' + str(len(rows_out)) + ' markets fetched, ' + str(errors) +
        ' errors, ' + str(round(time.time() - start_time, 1)) + 's')

    if not rows_out:
        log('ERROR: No metadata rows. Aborting.')
        sys.exit(1)

    cols = list(rows_out[0].keys())
    with open(OUT_METADATA, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows_out)
    log('Wrote ' + OUT_METADATA + ' (' + str(len(rows_out)) + ' rows)')
    return rows_out

def pass2_volatility_jump(metadata_rows):
    log('=== PASS 2: bbo_log volatility-jump detection ===')

    ticker_bounds = {}
    for row in metadata_rows:
        tid = row.get('ticker_id', '').strip()
        ot = parse_iso(row.get('open_time'))
        ct = parse_iso(row.get('close_time'))
        if tid and ot and ct:
            ticker_bounds[tid] = (ot, ct)
    log('Tickers with valid open/close bounds: ' + str(len(ticker_bounds)))

    ticker_windows = defaultdict(list)
    n_lines = 0
    n_ticks_kept = 0

    log('Streaming bbo_log_v4...')
    start_time = time.time()

    with gzip.open(BBO_PATH, 'rt') as f:
        f.readline()
        for line in f:
            n_lines += 1
            if n_lines % 20_000_000 == 0:
                elapsed = time.time() - start_time
                rate = n_lines / elapsed
                log('  Lines: ' + format(n_lines, ',') + ' | Kept: ' + format(n_ticks_kept, ',') +
                    ' | Active tickers: ' + str(len(ticker_windows)) +
                    ' | Rate: ' + str(round(rate)) + '/s | Elapsed: ' + str(round(elapsed/60, 1)) + 'min')

            parts = line.rstrip('\n').split(',')
            if len(parts) != 5:
                continue
            ts_str, ticker, bid_str, ask_str, _ = parts

            bounds = ticker_bounds.get(ticker)
            if bounds is None:
                continue

            try:
                ts = parse_bbo_ts(ts_str)
                bid = float(bid_str)
                ask = float(ask_str)
            except (ValueError, TypeError):
                continue

            ot, ct = bounds
            if ts < ot or ts > ct:
                continue

            mid = (bid + ask) / 2.0
            window_start = int(ts) // 30 * 30

            n_ticks_kept += 1
            wins = ticker_windows[ticker]
            if wins and wins[-1][0] == window_start:
                _, max_mid, min_mid = wins[-1]
                wins[-1] = (window_start, max(max_mid, mid), min(min_mid, mid))
            else:
                wins.append((window_start, mid, mid))

    log('Pass 2 streaming complete: ' + format(n_lines, ',') + ' lines, ' +
        format(n_ticks_kept, ',') + ' kept, ' + str(len(ticker_windows)) + ' tickers')
    log('Streaming time: ' + str(round((time.time() - start_time)/60, 1)) + 'min')

    log('Running volatility-jump detector...')
    derived = {}
    for ticker, wins in ticker_windows.items():
        if len(wins) < SUSTAIN_WINDOWS + 1:
            ot, ct = ticker_bounds[ticker]
            derived[ticker] = (ot + 0.8 * (ct - ot), 'fallback_short_data')
            continue

        found_idx = None
        for i in range(len(wins) - SUSTAIN_WINDOWS):
            ok = all((wins[i+k][1] - wins[i+k][2]) >= JUMP_CENTS for k in range(SUSTAIN_WINDOWS))
            if ok:
                found_idx = i
                break

        if found_idx is not None:
            derived[ticker] = (float(wins[found_idx][0]), 'jump')
        else:
            ot, ct = ticker_bounds[ticker]
            derived[ticker] = (ot + 0.8 * (ct - ot), 'fallback_no_jump')

    log('Detector complete: ' + str(len(derived)) + ' tickers labeled')
    method_counts = defaultdict(int)
    for _, method in derived.values():
        method_counts[method] += 1
    log('Method breakdown: ' + str(dict(method_counts)))

    log('Merging metadata + derived pregame_close_ts...')
    final_rows = []
    for row in metadata_rows:
        tid = row.get('ticker_id', '').strip()
        if tid in derived:
            pc_ts, method = derived[tid]
            row['pregame_close_ts'] = int(pc_ts)
            row['pregame_detection_method'] = method
        else:
            row['pregame_close_ts'] = ''
            row['pregame_detection_method'] = 'no_bbo_data'
        final_rows.append(row)

    cols = list(final_rows[0].keys())
    with open(OUT_FINAL, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(final_rows)
    log('Wrote ' + OUT_FINAL + ' (' + str(len(final_rows)) + ' rows)')
    return final_rows

def pass3_validate(final_rows):
    log('=== PASS 3: Validate against match_facts_full overlap ===')

    mf = {}
    with open('/root/Omi-Workspace/arb-executor/data/match_facts_full.csv') as f:
        for row in csv.DictReader(f):
            tid = row.get('ticker_id', '').strip()
            pc = row.get('pregame_close_ts', '').strip()
            if not tid or not pc:
                continue
            try:
                mf[tid] = int(float(pc))
            except:
                pass
    log('match_facts_full reference rows: ' + str(len(mf)))

    deltas_by_cat = defaultdict(list)
    overlap_count = 0
    method_in_overlap = defaultdict(int)

    for row in final_rows:
        tid = row.get('ticker_id', '').strip()
        if tid in mf and row.get('pregame_close_ts'):
            try:
                v3 = int(row['pregame_close_ts'])
                ref = mf[tid]
                delta_min = (v3 - ref) / 60
                cat = row.get('category', 'UNKNOWN')
                deltas_by_cat[cat].append(delta_min)
                method_in_overlap[row.get('pregame_detection_method', '')] += 1
                overlap_count += 1
            except:
                pass

    log('Overlap with match_facts_full: ' + str(overlap_count))
    log('Methods used in overlap: ' + str(dict(method_in_overlap)))

    import statistics
    log('')
    log('Delta v3 - reference (minutes), per category:')
    cols_h = ['category', 'n', 'median', 'mean', 'stdev', 'p10', 'p90']
    log('  '.join(c.ljust(10) for c in cols_h))
    for cat, deltas in deltas_by_cat.items():
        if not deltas:
            continue
        n = len(deltas)
        ds = sorted(deltas)
        std = statistics.stdev(deltas) if n > 1 else 0
        row_v = [cat, str(n),
                 str(round(statistics.median(deltas), 1)),
                 str(round(statistics.mean(deltas), 1)),
                 str(round(std, 1)),
                 str(round(ds[int(n*0.10)], 1)),
                 str(round(ds[int(n*0.90)], 1))]
        log('  '.join(c.ljust(10) for c in row_v))

if __name__ == '__main__':
    open(LOG_PATH, 'w').close()
    metadata = pass1_kalshi_metadata()
    final = pass2_volatility_jump(metadata)
    pass3_validate(final)
    log('=== DONE ===')
