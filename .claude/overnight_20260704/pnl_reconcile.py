#!/usr/bin/env python3
"""[READ-ONLY] Mandatory P&L format: cash balance + portfolio positions + Kalshi API
fills/settlements reconciliation for the window boot->shutdown.
Also: latch-override false-fire check (did override-latched events settle within 3h?)."""
import json, time, base64
from pathlib import Path
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import requests

pk = serialization.load_pem_private_key(Path('kalshi.pem').read_bytes(), password=None, backend=default_backend())
B = 'https://api.elections.kalshi.com/trade-api/v2'
def s(m, p):
    ts = str(int(time.time() * 1000)); sp = '/trade-api/v2' + p.split('?')[0]
    sig = pk.sign((ts + m + sp).encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                  salt_length=padding.PSS.DIGEST_LENGTH), hashes.SHA256())
    return {'KALSHI-ACCESS-KEY': 'f3b064d1-a02e-42a4-b2b1-132834694d23',
            'KALSHI-ACCESS-SIGNATURE': base64.b64encode(sig).decode(), 'KALSHI-ACCESS-TIMESTAMP': ts}
def g(p):
    for _ in range(4):
        try:
            return requests.get(B + p, headers=s('GET', p), timeout=30).json()
        except Exception:
            time.sleep(0.4)
    return {}

ET = timezone(timedelta(hours=-4))
BOOT = datetime(2026, 7, 3, 18, 32, 5, tzinfo=ET)
SHUT = datetime(2026, 7, 4, 12, 58, 55, tzinfo=ET)
BOOT_TS, SHUT_TS = int(BOOT.timestamp()), int(SHUT.timestamp())

print('==== 1. CASH ====')
bal = g('/portfolio/balance')
print(json.dumps(bal))

print('\n==== 2. PORTFOLIO (open positions) ====')
cur = None; rows = []
while True:
    q = f'/portfolio/positions?limit=200&settlement_status=unsettled' + (f'&cursor={cur}' if cur else '')
    r = g(q); rows += r.get('market_positions', []); cur = r.get('cursor')
    if not cur:
        break
mv = 0
for p in rows:
    if p.get('position', 0) == 0:
        continue
    print(f"  {p['ticker']:48s} pos={p['position']:>5} exposure={p.get('market_exposure')} realized={p.get('realized_pnl')}")
    mv += p.get('market_exposure', 0) or 0
print(f"  total open-position exposure (cents): {mv}")

print('\n==== 3. API FILLS in window ====')
cur = None; fl = []
while True:
    q = f'/portfolio/fills?limit=200&min_ts={BOOT_TS}&max_ts={SHUT_TS}' + (f'&cursor={cur}' if cur else '')
    r = g(q); fl += r.get('fills', []); cur = r.get('cursor')
    if not cur or len(fl) > 2000:
        break
buy = [f for f in fl if f.get('action') == 'buy']
sell = [f for f in fl if f.get('action') == 'sell']
tk_ct = {}
for f in fl:
    tk_ct.setdefault(f['ticker'], [0, 0, 0])
    i = 0 if f['action'] == 'buy' else 1
    tk_ct[f['ticker']][i] += f.get('count', 0)
    tk_ct[f['ticker']][2] += (1 if f.get('is_taker') else 0)
print(f"fills: {len(fl)} rows | buy {sum(f.get('count',0) for f in buy)} shares | sell {sum(f.get('count',0) for f in sell)} shares")
for tk, (b, sl, tkr) in sorted(tk_ct.items()):
    print(f"  {tk:48s} buy={b:>5} sell={sl:>5} taker_fills={tkr}")

print('\n==== 4. API SETTLEMENTS in window ====')
cur = None; st = []
while True:
    q = f'/portfolio/settlements?limit=200&min_ts={BOOT_TS}&max_ts={SHUT_TS}' + (f'&cursor={cur}' if cur else '')
    r = g(q); st += r.get('settlements', []); cur = r.get('cursor')
    if not cur or len(st) > 1000:
        break
tot = 0
for x in st:
    rev = x.get('revenue', 0); cost = (x.get('yes_total_cost', 0) or 0) + (x.get('no_total_cost', 0) or 0)
    net = rev - cost; tot += net
    print(f"  {x['ticker']:48s} mkt_result={x.get('market_result'):4s} rev={rev:>7} cost={cost:>7} net={net:>+7}c")
print(f"  SETTLEMENT NET (window): {tot}c = ${tot/100:.2f}")

print('\n==== 5. LATCH-OVERRIDE FALSE-FIRE CHECK ====')
# override-latched events with big tts: did the market close/settle within ~3.5h of latch?
CHECK = {
    'KXITFWMATCH-26JUL03MAXBRO': '2026-07-03', 'KXITFWMATCH-26JUL03GUOSNI': '2026-07-03',
    'KXITFMATCH-26JUL04BITTUR': '2026-07-04', 'KXITFMATCH-26JUL04PANDER': '2026-07-04',
    'KXWTAMATCH-26JUL04NAVKOS': '2026-07-04',
}
for ev in CHECK:
    r = g(f'/events/{ev}')
    for m in r.get('markets', []) or []:
        print(f"  {m['ticker']:48s} status={m.get('status')} result={m.get('result')} close={m.get('close_time')}")
