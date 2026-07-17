#!/usr/bin/env python3
"""P3 census — every conception since 07-15 entering via a NON-CORRIDOR
phase on an ITF event with lifetime volume under 1,500. Volume = current
Kalshi lifetime (only grows: 'under now' => 'under at conception' EXACT;
'over now but under then' missed => the count is a LOWER BOUND, said)."""
import json, glob, time, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")
CUT = datetime(2026,7,15,tzinfo=ET).timestamp()
conc = {}   # ev -> first conception row (non-corridor)
fills = {}  # ev -> realized cents (exit_filled + settled pnl)
for f in sorted(glob.glob('/root/Omi-Workspace/arb-executor/logs/live_v3_2026071[4-7].jsonl')):
    for l in open(f, encoding='utf-8', errors='replace'):
        if '"order_placed"' in l:
            try: j = json.loads(l)
            except: continue
            if j.get('ts_epoch',0) < CUT: continue
            d = j.get('details') or {}
            if d.get('action') != 'buy': continue
            tk = j.get('ticker') or ''
            if 'KXITF' not in tk: continue
            ev = tk.rsplit('-',1)[0]
            w = (d.get('window') or {})
            ph = w.get('phase')
            if ph == 'CORRIDOR': continue   # corridor door had the check
            conc.setdefault(ev, {'ts': j['ts_epoch'], 'phase': ph, 'tk': tk})
        elif '"exit_filled"' in l or '"settled"' in l:
            try: j = json.loads(l)
            except: continue
            if j.get('ts_epoch',0) < CUT: continue
            d = j.get('details') or {}
            tk = j.get('ticker') or ''
            if 'KXITF' not in tk: continue
            pnl = d.get('pnl_cents')
            if pnl is not None:
                fills[tk.rsplit('-',1)[0]] = fills.get(tk.rsplit('-',1)[0], 0) + pnl
def vol_of(ev):
    try:
        with urllib.request.urlopen(
            'https://api.elections.kalshi.com/trade-api/v2/events/%s?with_nested_markets=true' % ev,
            timeout=15) as r:
            d = json.load(r)
        return sum(float(m.get('volume_fp') or 0) for m in (d.get('event') or {}).get('markets') or [])
    except Exception:
        return None
under = []
for ev, row in conc.items():
    v = vol_of(ev); time.sleep(0.12)
    if v is not None and v < 1500:
        under.append((ev, row['phase'], round(v,1), fills.get(ev)))
print('non-corridor ITF conceptions since 07-15:', len(conc))
print('UNDER 1,500 lifetime EVEN NOW (exact lower bound):', len(under))
tot = sum(x[3] for x in under if x[3] is not None)
n_set = sum(1 for x in under if x[3] is not None)
print('realized on the under-floor set: %+.0fc across %d settled/cashed events' % (tot, n_set))
for x in sorted(under, key=lambda y: (y[3] if y[3] is not None else 0)):
    print('  %-38s phase=%s vol=%s realized=%s' % (x[0].split('-',1)[-1], x[1], x[2], x[3]))
