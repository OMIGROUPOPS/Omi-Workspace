import sqlite3, json
from collections import defaultdict

conn = sqlite3.connect('/root/Omi-Workspace/arb-executor/tennis.db')
cur = conn.cursor()

def classify(tier, price):
    d = 'leader' if price >= 50 else 'underdog'
    bs = int(price // 5) * 5
    return '%s_%s_%d-%d' % (tier, d, bs, bs+4)

with open('/root/Omi-Workspace/arb-executor/config/deploy_v4.json') as f:
    cfg = json.load(f)
active = cfg.get('active_cells', {})
DISABLED = {
    'ATP_MAIN_underdog_40-44': 9, 'ATP_CHALL_underdog_30-34': 15,
    'ATP_MAIN_leader_75-79': 14, 'ATP_CHALL_underdog_25-29': 21,
    'ATP_MAIN_underdog_35-39': 12, 'ATP_CHALL_leader_60-64': 6,
    'ATP_MAIN_leader_60-64': 15, 'ATP_MAIN_underdog_25-29': 22,
    'ATP_CHALL_underdog_15-19': 31, 'WTA_MAIN_leader_55-59': 10,
    'WTA_MAIN_underdog_40-44': 5, 'WTA_MAIN_underdog_30-34': 16,
    'WTA_MAIN_underdog_35-39': 11, 'ATP_MAIN_leader_55-59': 13,
    'ATP_MAIN_underdog_20-24': 25, 'WTA_MAIN_leader_60-64': 8,
    'WTA_MAIN_underdog_15-19': 31, 'WTA_MAIN_underdog_20-24': 22,
}
ALL = {}
for c, p in active.items(): ALL[c] = p.get('exit_cents', 0)
for c, e in DISABLED.items(): ALL[c] = e

cur.execute("""SELECT event_ticker, category, first_price_winner, max_price_winner,
    first_price_loser, max_price_loser
    FROM historical_events
    WHERE first_ts > '2026-03-20' AND first_ts < '2026-04-18'
    AND total_trades >= 10
    AND first_price_winner > 0 AND first_price_loser > 0""")

cb = defaultdict(lambda: {'wt':0,'ws':0,'lt':0,'ls':0})
for evt, cat, fpw, maxw, fpl, maxl in cur.fetchall():
    tier = cat
    cw = classify(tier, fpw)
    if cw in ALL:
        ec = ALL[cw]
        cb[cw]['wt'] += 1
        if maxw and maxw >= min(99, fpw + ec):
            cb[cw]['ws'] += 1
    cl = classify(tier, fpl)
    if cl in ALL:
        ec = ALL[cl]
        cb[cl]['lt'] += 1
        if maxl and maxl >= min(99, fpl + ec):
            cb[cl]['ls'] += 1

print('| Cell | N_w | Scalp_w% | N_l | Scalp_l% | Combined% | Gap |')
print('|---|---|---|---|---|---|---|')
for cell in sorted(cb.keys()):
    d = cb[cell]
    wt,ws,lt,ls = d['wt'],d['ws'],d['lt'],d['ls']
    if wt+lt < 15: continue
    w_sr = ws/wt*100 if wt else 0
    l_sr = ls/lt*100 if lt else 0
    comb = (ws+ls)/(wt+lt)*100 if (wt+lt) else 0
    print('| %s | %d | %.0f%% | %d | %.0f%% | %.0f%% | %+.0f |' % (
        cell, wt, w_sr, lt, l_sr, comb, w_sr-l_sr))

conn.close()
