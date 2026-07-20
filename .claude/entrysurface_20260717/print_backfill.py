#!/usr/bin/env python3
# LOOP 7 ADDENDUM (a) — THE PRINT BACKFILL, corpus-wide. Complete trade
# history for every corpus ticker from Kalshi /markets/trades (public,
# paged, 429-disciplined, resumable via ingest_log src='backfill').
# Inserts into the ONE store (subsecond_store.db prints). Census by era
# printed at the end — the store becomes corpus-deep.
import json, sqlite3, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / 'state/subsecond_store.db'
con = sqlite3.connect(DB)
con.execute("CREATE TABLE IF NOT EXISTS ingest_log(src TEXT, path TEXT "
            "PRIMARY KEY, rows INTEGER, ingested_at REAL)")
done = {r[0] for r in con.execute(
    "SELECT path FROM ingest_log WHERE src='backfill'")}
tickers = set()
for line in open(ROOT / 'state/range_spectrum_v1.jsonl'):
    r = json.loads(line)
    for leg in r['legs']:
        tickers.add(r['event'] + '-' + leg)
todo = sorted(t for t in tickers if t not in done)
print('backfill todo:', len(todo), 'of', len(tickers), flush=True)
BASE = ('https://api.elections.kalshi.com/trade-api/v2/markets/trades'
        '?ticker=%s&limit=1000')
n_rows = 0
for i, tk in enumerate(todo):
    ev = tk.rsplit('-', 1)[0]
    cursor = None
    rows = []
    ok = True
    for page in range(60):
        url = BASE % tk + (('&cursor=%s' % cursor) if cursor else '')
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'omi-backfill'})
            with urllib.request.urlopen(req, timeout=15) as r2:
                d = json.load(r2)
        except Exception as e:
            if '429' in str(e):
                time.sleep(6)
                continue
            ok = False
            break
        tr = d.get('trades') or []
        for t in tr:
            ts = t.get('created_time')
            try:
                from datetime import datetime
                ep = datetime.fromisoformat(
                    ts.replace('Z', '+00:00')).timestamp()
            except Exception:
                continue
            rows.append((ev, tk, ep,
                         int(round(float(t.get('yes_price_dollars')
                                         or 0) * 100)),
                         float(t.get('count_fp') or t.get('count') or 0),
                         'backfill'))
        cursor = d.get('cursor')
        if not cursor or not tr:
            break
        time.sleep(0.15)
    if ok:
        if rows:
            con.executemany('INSERT INTO prints VALUES(?,?,?,?,?,?)', rows)
            n_rows += len(rows)
        con.execute("INSERT OR REPLACE INTO ingest_log VALUES(?,?,?,?)",
                    ('backfill', tk, len(rows), time.time()))
    time.sleep(0.2)
    if i % 200 == 199:
        con.commit()
        print(i + 1, '/', len(todo), 'rows+', n_rows, flush=True)
con.commit()
by = con.execute("SELECT strftime('%Y-%m', ts, 'unixepoch'), COUNT(*) "
                 "FROM prints WHERE src='backfill' GROUP BY 1").fetchall()
print('BACKFILL-DONE rows', n_rows, 'era census:', by)
