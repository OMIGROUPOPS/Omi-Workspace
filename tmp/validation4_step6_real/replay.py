"""Step 6 — true tick-replay heat map (reads raw .raw files, parses lazily).

Loads ticks per ticker from /tmp/validation4/step6_real/ticks/*.raw,
runs chronological tick-by-tick simulation. No aggregates anywhere.
"""
import os
import csv
import json
import statistics
import time
import datetime
import calendar

REAL = '/tmp/validation4/step6_real'
TICKS_DIR = f'{REAL}/ticks'
OUT = f'{REAL}/out'
CELLS_DIR = f'{OUT}/cells'
os.makedirs(CELLS_DIR, exist_ok=True)

ES = 10
DS = 5

COARSE_DCA = [None, 5, 10, 15, 20, 25, 30]
COARSE_EXIT = [None, 5, 10, 15, 20, 25, 30]


import struct
UNPACK = struct.Struct('<IBB').unpack

def parse_raw(path):
    """Read binary tick file (records of '<IBB' = 6 bytes each), return sorted unique."""
    ticks = []
    with open(path, 'rb') as f:
        data = f.read()
    n = len(data) // 6
    for i in range(n):
        ts, bid, ask = UNPACK(data[i*6:i*6+6])
        ticks.append((ts, bid, ask))
    ticks.sort(key=lambda x: x[0])
    out = []
    prev = None
    for t in ticks:
        if t != prev:
            out.append(t)
            prev = t
    return out


def replay(ticks, entry_px, dca_drop, exit_target, strategy, settle_bid):
    """Tick-by-tick simulation. Returns dict or None."""
    ets_idx = None
    for i, (ts, bid, ask) in enumerate(ticks):
        if ask <= entry_px:
            ets_idx = i
            break
    if ets_idx is None:
        return None

    pos = ES
    avg = entry_px
    dca_filled = False
    dca_price = None

    if exit_target is None:
        sell_target = 99
    else:
        sell_target = min(99, entry_px + exit_target)

    dca_trigger_ask = None
    if dca_drop is not None:
        dca_trigger_ask = entry_px - dca_drop

    for i in range(ets_idx + 1, len(ticks)):
        ts, bid, ask = ticks[i]

        # Sell fill check
        if bid >= sell_target:
            sell_px = sell_target
            pnl = ES * (sell_px - entry_px)
            if dca_filled:
                pnl += DS * (sell_px - dca_price)
            return dict(
                event='SOLD_POST_DCA' if dca_filled else 'SOLD_PRE_DCA',
                sell_px=sell_px, pnl=pnl, pos=pos, avg=avg, dca=dca_price,
                cap=ES * entry_px + (DS * dca_price if dca_filled else 0),
            )

        # DCA fire check
        if (not dca_filled) and dca_trigger_ask is not None and 1 <= dca_trigger_ask < 100:
            if ask <= dca_trigger_ask:
                dca_filled = True
                dca_price = dca_trigger_ask
                pos = ES + DS
                avg = int(round((ES * entry_px + DS * dca_price) / (ES + DS)))
                if exit_target is None:
                    sell_target = 99
                elif strategy == 'B':
                    sell_target = min(99, max(1, avg + exit_target))

    if settle_bid is None:
        return None
    if settle_bid >= 80:
        outcome = 100; event = 'SETTLE_WON'
    elif settle_bid <= 20:
        outcome = 0; event = 'SETTLE_LOST'
    else:
        outcome = settle_bid; event = 'SETTLE_MID'
    pnl = ES * (outcome - entry_px)
    if dca_filled:
        pnl += DS * (outcome - dca_price)
    return dict(
        event=event, sell_px=outcome, pnl=pnl, pos=pos, avg=avg, dca=dca_price,
        cap=ES * entry_px + (DS * dca_price if dca_filled else 0),
    )


def cell_stats(cell_data, dca, exit_target, strategy):
    results = []
    for tk, (ticks, entry_px, settle_bid) in cell_data.items():
        r = replay(ticks, entry_px, dca, exit_target, strategy, settle_bid)
        if r is not None and r.get('cap', 0) > 0:
            results.append(r)
    if not results:
        return None
    pnls = [r['pnl'] for r in results]
    caps = [r['cap'] for r in results]
    rois = [100.0 * p / c for p, c in zip(pnls, caps)]
    wins = sum(1 for p in pnls if p > 0)
    return dict(
        n=len(results),
        win_rate=100.0 * wins / len(results),
        mean_roi=statistics.mean(rois),
        median_roi=statistics.median(rois),
        p25_roi=statistics.quantiles(rois, n=4)[0] if len(rois) >= 4 else rois[0],
        p75_roi=statistics.quantiles(rois, n=4)[2] if len(rois) >= 4 else rois[-1],
        max_loss=-min(pnls) if pnls else 0,
        total_pnl=sum(pnls),
    )


def sweep(cell_data, dcas, exits, strategies=('A', 'B')):
    out = []
    for dca in dcas:
        for ext in exits:
            strats = strategies if dca is not None else ('NA',)
            for strat in strats:
                s = cell_stats(cell_data, dca, ext, strat)
                if s is None:
                    continue
                out.append(dict(dca_drop=dca, exit_target=ext, strategy=strat, **s))
    return out


def load_cell_data(tickers, ticker_meta):
    out = {}
    for tk in tickers:
        bin_path = f'{TICKS_DIR}/{tk.replace("/","_")}.bin'
        if not os.path.exists(bin_path):
            continue
        ticks = parse_raw(bin_path)
        if len(ticks) < 2:
            continue
        m = ticker_meta.get(tk, {})
        ep = m.get('sub_range_hi')
        sb = m.get('settle_bid')
        if ep is None:
            continue
        out[tk] = (ticks, ep, sb)
    return out


def main():
    t_total = time.time()
    with open(f'{REAL}/cell_tickers.json') as f:
        cell_tickers = json.load(f)
    with open(f'{REAL}/ticker_meta.json') as f:
        ticker_meta = json.load(f)
    all_cells = sorted(cell_tickers.keys())
    print(f'Cells: {len(all_cells)}')

    stage1_rows = []
    stage2_rows = []
    cell_optima = {}
    timings = []

    for name in all_cells:
        t_load = time.time()
        cell_data = load_cell_data(cell_tickers[name], ticker_meta)
        t_load_done = time.time() - t_load
        n_replayed = len(cell_data)
        n_target = len(cell_tickers[name])
        total_ticks = sum(len(t) for t, _, _ in cell_data.values())

        t_sim = time.time()
        rows = sweep(cell_data, COARSE_DCA, COARSE_EXIT)
        for r in rows: r['cell_id'] = name
        stage1_rows.extend(rows)

        if not rows:
            t_cell = time.time() - t_load
            timings.append((name, n_target, n_replayed, total_ticks, t_load_done, time.time() - t_sim, t_cell, 0))
            print(f'  [{name}] tk={n_target} replayed={n_replayed} ticks={total_ticks} load={t_load_done:.1f}s NO_DATA')
            continue

        rows.sort(key=lambda r: r['mean_roi'], reverse=True)
        coarse_top = rows[0]
        cell_optima[name] = {'coarse_top': coarse_top, 'coarse_rows': rows, 'n_replayed': n_replayed}

        # Stage 2 fine
        if coarse_top['dca_drop'] is None:
            dca_range = [None, 1, 2, 3, 4, 5]
        else:
            lo = max(1, coarse_top['dca_drop'] - 5); hi = coarse_top['dca_drop'] + 5
            dca_range = list(range(lo, hi + 1))
        if coarse_top['exit_target'] is None:
            exit_range = [None, 1, 2, 3, 4, 5]
        else:
            lo = max(1, coarse_top['exit_target'] - 5); hi = coarse_top['exit_target'] + 5
            exit_range = list(range(lo, hi + 1))
        fine_rows = sweep(cell_data, dca_range, exit_range)
        for r in fine_rows: r['cell_id'] = name
        stage2_rows.extend(fine_rows)
        t_sim_done = time.time() - t_sim
        cell_optima[name]['fine_rows'] = fine_rows
        cell_optima[name]['fine_top_mean'] = sorted(fine_rows, key=lambda r: r['mean_roi'], reverse=True)[:5]
        cell_optima[name]['fine_top_median'] = sorted(fine_rows, key=lambda r: r['median_roi'], reverse=True)[:5]
        cell_optima[name]['fine_top_maxloss'] = sorted(fine_rows, key=lambda r: r['max_loss'])[:5]
        robust = [r for r in fine_rows if r['mean_roi'] > 0 and r['median_roi'] > 0
                  and r['win_rate'] > 50 and r['p25_roi'] > -50]
        robust.sort(key=lambda r: r['mean_roi'], reverse=True)
        cell_optima[name]['robust'] = robust[:5]

        t_cell = time.time() - t_load
        timings.append((name, n_target, n_replayed, total_ticks, t_load_done, t_sim_done, t_cell, len(rows) + len(fine_rows)))
        print(f'  [{name}] tk={n_target} replayed={n_replayed} ticks={total_ticks/1000:.0f}K load={t_load_done:.1f}s sim={t_sim_done:.1f}s total={t_cell:.1f}s configs={len(rows)+len(fine_rows)}', flush=True)

    # Write CSVs
    def write_csv(path, rows):
        with open(path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['cell_id','dca_drop','exit_target','strategy_AB','n_trades','win_rate','mean_roi','median_roi','p25_roi','p75_roi','max_loss','total_pnl_baby'])
            for r in rows:
                w.writerow([r['cell_id'],
                    '' if r['dca_drop'] is None else r['dca_drop'],
                    'hold99' if r['exit_target'] is None else r['exit_target'],
                    r['strategy'], r['n'],
                    round(r['win_rate'], 1), round(r['mean_roi'], 2),
                    round(r['median_roi'], 2), round(r['p25_roi'], 2),
                    round(r['p75_roi'], 2), r['max_loss'], r['total_pnl']])
    write_csv(f'{OUT}/stage1_coarse.csv', stage1_rows)
    write_csv(f'{OUT}/stage2_fine.csv', stage2_rows)

    with open(f'{OUT}/cell_timings.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell','n_target','n_replayed','total_ticks','load_seconds','sim_seconds','total_seconds','configs_run'])
        for row in timings:
            w.writerow(row)

    # Per-cell reports
    def fmt(r):
        return (f'dca={str(r["dca_drop"]):>4} exit={str(r["exit_target"]) if r["exit_target"] is not None else "hold99":>6} '
                f'strat={r["strategy"]:>2} | n={r["n"]:>3} mean={r["mean_roi"]:+6.2f}% med={r["median_roi"]:+6.2f}% '
                f'win={r["win_rate"]:>4.1f}% maxL={r["max_loss"]:>4}c total={r["total_pnl"]:>+6}c')

    for name in all_cells:
        if name not in cell_optima or 'fine_top_mean' not in cell_optima[name]: continue
        opt = cell_optima[name]
        ct = opt['coarse_top']; ft = opt['fine_top_mean'][0] if opt['fine_top_mean'] else None
        if ft is None: continue
        L = []
        L.append(f'CELL: {name} | n_trajs_replayed: {opt["n_replayed"]}')
        if opt['n_replayed'] < 30: L.append('*** SAMPLE WARNING: n < 30 ***')
        L.append('')
        L.append(f'COARSE WINNER: dca={ct["dca_drop"]} exit={ct["exit_target"] if ct["exit_target"] is not None else "hold99"} strat={ct["strategy"]} | mean={ct["mean_roi"]:+.2f}% med={ct["median_roi"]:+.2f}% n={ct["n"]}')
        L.append(f'FINE WINNER  : dca={ft["dca_drop"]} exit={ft["exit_target"] if ft["exit_target"] is not None else "hold99"} strat={ft["strategy"]} | mean={ft["mean_roi"]:+.2f}% med={ft["median_roi"]:+.2f}% n={ft["n"]}')
        L.append(f'Fine improvement: {ft["mean_roi"]-ct["mean_roi"]:+.2f}% mean ROI')
        L.append('')
        L.append('Top 5 by mean ROI:')
        for r in opt['fine_top_mean']: L.append('  ' + fmt(r))
        L.append(''); L.append('Top 5 by median ROI:')
        for r in opt['fine_top_median']: L.append('  ' + fmt(r))
        L.append(''); L.append('Top 5 by lowest max_loss:')
        for r in opt['fine_top_maxloss']: L.append('  ' + fmt(r))
        L.append('')
        if opt['robust']:
            r = opt['robust'][0]
            L.append('ROBUST PICK (mean>0, med>0, win>50%, p25_roi > -50%):'); L.append('  ' + fmt(r))
        else:
            L.append('ROBUST PICK: none meets all criteria')
        L.append('')
        h99 = [r for r in opt['fine_rows'] if r['exit_target'] is None]
        if h99:
            hb = max(h99, key=lambda r: r['mean_roi'])
            L.append('HOLD_99 best in fine grid:')
            L.append('  ' + fmt(hb))
            if opt['robust']:
                rp = opt['robust'][0]
                dm = hb['mean_roi'] - rp['mean_roi']
                dml = hb['max_loss'] - rp['max_loss']
                rec = 'prefer hold_99' if dm >= 1.0 and dml <= 10 else ('prefer finite' if dm <= -1.0 or dml > 20 else 'config-insensitive')
                L.append(f'  vs robust: meanΔ={dm:+.2f}% medΔ={hb["median_roi"]-rp["median_roi"]:+.2f}% maxLossΔ={dml:+}c | {rec}')
        with open(f'{CELLS_DIR}/{name}.txt', 'w') as f:
            f.write('\n'.join(L))

    print(f'\nTOTAL: {time.time()-t_total:.1f}s across {len(timings)} cells')


if __name__ == '__main__':
    main()
