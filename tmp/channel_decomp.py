import json, glob
from collections import defaultdict, Counter

ticker_meta = {}
for path in sorted(glob.glob('/root/Omi-Workspace/arb-executor/logs/live_v3_*.jsonl')):
    with open(path) as f:
        for line in f:
            try:
                d = json.loads(line)
                if d.get('event') == 'cell_match':
                    det = d.get('details', {})
                    tk = d.get('ticker', '')
                    mbs = det.get('min_before_start')
                    cell = det.get('cell', '')
                    play = det.get('scenario', '')
                    if tk:
                        ticker_meta[tk] = {'mbs': mbs, 'cell': cell, 'play': play}
            except:
                pass

entries = []
exits_by_ticker = defaultdict(list)

for path in sorted(glob.glob('/root/Omi-Workspace/arb-executor/logs/live_v3_*.jsonl')):
    with open(path) as f:
        for line in f:
            try:
                d = json.loads(line)
                ev = d.get('event', '')
                tk = d.get('ticker', '')
                ts = d.get('ts')
                tse = d.get('ts_epoch')
                if ev == 'entry_filled':
                    det = d.get('details', {})
                    meta = ticker_meta.get(tk, {})
                    entries.append({
                        'ticker': tk, 'ts': ts, 'ts_epoch': tse,
                        'fill_price': det.get('fill_price'),
                        'cell': det.get('cell', meta.get('cell', '?')),
                        'mbs': meta.get('mbs'),
                        'play': det.get('play_type', '?'),
                        'qty': det.get('qty')
                    })
                elif ev in ('scalp_filled', 'exit_filled', 'paper_exit_fill', 'paper_fill', 'exit_fill'):
                    if tk:
                        det = d.get('details', {})
                        exits_by_ticker[tk].append({
                            'ts': ts, 'ts_epoch': tse, 'event': ev,
                            'price': det.get('fill_price', det.get('price', det.get('exit_price'))),
                            'hrs_before': det.get('hours_before_commence')
                        })
            except:
                pass

print('Entries found:', len(entries))
print('Tickers with cell_match meta:', len(ticker_meta))
print('Tickers with at least one exit event:', len(exits_by_ticker))
print()

resolved = []
for ent in entries:
    ent_te = ent.get('ts_epoch')
    if not ent_te: continue
    ext_list = sorted(exits_by_ticker.get(ent['ticker'], []), key=lambda x: x.get('ts_epoch') or 0)
    scalp_exits = [e for e in ext_list if e['event'] == 'scalp_filled' and (e.get('ts_epoch') or 0) > ent_te]
    other_exits = [e for e in ext_list if e['event'] != 'scalp_filled' and (e.get('ts_epoch') or 0) > ent_te]
    chosen = None
    channel = None
    if scalp_exits:
        chosen = scalp_exits[0]
        channel = 'Channel_1_premarket'
    elif other_exits:
        chosen = other_exits[0]
        channel = 'Channel_2_in_game'
    if not chosen: continue
    delta_min = (chosen['ts_epoch'] - ent_te) / 60.0
    resolved.append({
        **ent,
        'exit_ts': chosen['ts'], 'exit_price': chosen['price'], 'exit_event': chosen['event'],
        'time_to_exit_min': delta_min, 'channel': channel,
        'pnl_per_contract': (chosen['price'] or 0) - (ent['fill_price'] or 0),
        'hrs_before': chosen.get('hrs_before')
    })

print('Resolved entry->exit pairs:', len(resolved))
print()
print('=== Channel breakdown (scalp_filled emitted = C1 pregame, exit_filled-only = C2 in-game) ===')
print(Counter(r['channel'] for r in resolved))
print()
print('=== Time-to-exit by channel ===')
for ch in ['Channel_1_premarket','Channel_2_in_game']:
    times = sorted([r['time_to_exit_min'] for r in resolved if r['channel']==ch])
    if times:
        n=len(times)
        print('  ' + ch + ': n=' + str(n) + ' median=' + ('%.1f' % times[n//2]) + 'min p25=' + ('%.1f' % times[n//4]) + 'min p75=' + ('%.1f' % times[3*n//4]) + 'min max=' + ('%.1f' % times[-1]) + 'min')
print()
print('=== P&L by channel (cents per contract, sum + mean) ===')
for ch in ['Channel_1_premarket','Channel_2_in_game']:
    pnls=[r['pnl_per_contract'] for r in resolved if r['channel']==ch]
    if pnls:
        print('  ' + ch + ': n=' + str(len(pnls)) + ' sum=' + str(sum(pnls)) + 'c mean=' + ('%.1f' % (sum(pnls)/len(pnls))) + 'c')
print()
print('=== Per-cell channel breakdown (cells with N>=4) ===')
by_cell_ch = defaultdict(lambda: defaultdict(int))
for r in resolved:
    by_cell_ch[r['cell']][r['channel']] += 1
for cell in sorted(by_cell_ch.keys()):
    counts = by_cell_ch[cell]
    total = sum(counts.values())
    if total < 4: continue
    c1 = counts.get('Channel_1_premarket', 0)
    c2 = counts.get('Channel_2_in_game', 0)
    print('  ' + str(cell).ljust(32) + ' N=' + str(total).rjust(3) + ' C1=' + str(c1).rjust(2) + ' C2=' + str(c2).rjust(2))
