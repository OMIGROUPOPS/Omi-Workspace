"""Step 6 v5 — offset + dca + exit + strategy grid, per-cell optimization.

Maker placement offset is now part of the optimization grid, not a fixed input.

Coarse offsets: +1, 0, -1, -2, -3, -4, -5
Fine-tune offset at 1c resolution around coarse winner.

All ROI / PnL computed from ACTUAL maker fill price (bid + bump + offset, clipped).

Fill rate is reported for every recommendation. Cells with low fill rates are NOT
excluded — they are flagged.
"""
import os
import csv
import json
import struct
import statistics
import sys
import time
from collections import defaultdict

sys.path.insert(0, '/root/Omi-Workspace/arb-executor')
from version_b_blueprint import DEPLOYMENT

REAL = '/tmp/validation4/step6_real'
TICKS_DIR = f'{REAL}/ticks'
OUT = f'{REAL}/out_v5'
CELLS_DIR = f'{OUT}/cells'
os.makedirs(CELLS_DIR, exist_ok=True)

ES = 10
DS = 5
UNPACK = struct.Struct('<IBB').unpack

COARSE_OFFSETS = [1, 0, -1, -2, -3, -4, -5]
COARSE_DCA = [None, 5, 10, 15, 20, 25, 30]
COARSE_EXIT = [None, 5, 10, 15, 20, 25, 30]


def load_ticks(path):
    with open(path, 'rb') as f:
        data = f.read()
    n = len(data) // 6
    ticks = [UNPACK(data[i * 6:i * 6 + 6]) for i in range(n)]
    ticks.sort(key=lambda x: x[0])
    out = []
    prev = None
    for t in ticks:
        if t != prev:
            out.append(t)
            prev = t
    return out


def maker_fill(ticks, entry_lo, entry_hi, offset, pregame_ratio=0.8):
    """Find first fill of maker buy.

    Returns (fill_idx, fill_price) or (None, None).
    """
    if not ticks:
        return None, None
    first_ts = ticks[0][0]
    last_ts = ticks[-1][0]
    pregame_cutoff = first_ts + int((last_ts - first_ts) * pregame_ratio)
    prev_maker = None
    for i, (ts, bid, ask) in enumerate(ticks):
        if ts > pregame_cutoff:
            break
        bump = 2 if (ts - first_ts) > 1800 else 1
        candidate = bid + bump + offset
        candidate = min(candidate, ask - 1)
        candidate = max(1, candidate)
        in_range = entry_lo <= candidate <= entry_hi
        # Check prev_maker fill (ask dropped through)
        if prev_maker is not None and ask <= prev_maker:
            return i, prev_maker
        if in_range and ask <= candidate:
            return i, candidate
        prev_maker = candidate if in_range else None
    return None, None


def peak_bid_after(ticks, entry_idx):
    max_b = 0
    for j in range(entry_idx + 1, len(ticks)):
        if ticks[j][1] > max_b:
            max_b = ticks[j][1]
    return max_b


def simulate(ticks, entry_idx, entry_px, dca_drop, exit_target, strategy, settle_bid):
    """Given pre-computed entry, run post-entry sim for (dca, exit, strat)."""
    if entry_idx is None:
        return None
    pos = ES
    cost = ES * entry_px
    avg = entry_px
    dca_filled = False
    dca_px = None

    if exit_target is None:
        sell_target = 99
    else:
        sell_target = min(99, entry_px + exit_target)

    dca_trigger = (entry_px - dca_drop) if (dca_drop is not None and entry_px - dca_drop >= 1) else None

    for j in range(entry_idx + 1, len(ticks)):
        ts, bid, ask = ticks[j]
        if bid >= sell_target:
            sell_px = sell_target
            pnl = ES * (sell_px - entry_px) + (DS * (sell_px - dca_px) if dca_filled else 0)
            return dict(event='SOLD_POST_DCA' if dca_filled else 'SOLD_PRE_DCA',
                        entry_px=entry_px, sell_px=sell_px, pnl=pnl, pos=pos,
                        cap=cost, avg=avg, roi=100.0 * pnl / cost)
        if not dca_filled and dca_trigger is not None and 1 <= dca_trigger < 100:
            if ask <= dca_trigger:
                dca_filled = True
                dca_px = dca_trigger
                pos = ES + DS
                cost = ES * entry_px + DS * dca_px
                avg = cost / pos
                if exit_target is None:
                    sell_target = 99
                elif strategy == 'B':
                    sell_target = min(99, max(1, int(round(avg)) + exit_target))
    # Settle
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
        pnl += DS * (outcome - dca_px)
    return dict(event=event, entry_px=entry_px, sell_px=outcome, pnl=pnl, pos=pos,
                cap=cost, avg=avg, roi=100.0 * pnl / cost if cost else 0)


def cell_stats(cell_data, offset, dca, exit_target, strategy):
    """Aggregate stats for one (offset, dca, exit, strat). Uses pre-cached entry per offset."""
    results = []
    n_attempts = 0
    for tk, (ticks, settle_bid, entry_cache) in cell_data.items():
        n_attempts += 1
        e = entry_cache.get(offset)
        if e is None:
            continue
        e_idx, e_px = e
        if e_idx is None:
            continue
        r = simulate(ticks, e_idx, e_px, dca, exit_target, strategy, settle_bid)
        if r is not None and r['cap'] > 0:
            results.append(r)
    if not results:
        return None
    pnls = [r['pnl'] for r in results]
    rois = [r['roi'] for r in results]
    fills = [r['entry_px'] for r in results]
    wins = sum(1 for p in pnls if p > 0)
    n = len(results)
    return dict(
        n=n,
        n_attempts=n_attempts,
        fill_rate=100.0 * n / n_attempts,
        avg_fill=statistics.mean(fills),
        win_rate=100.0 * wins / n,
        mean_pnl=statistics.mean(pnls),
        median_pnl=statistics.median(pnls),
        mean_roi=statistics.mean(rois),
        median_roi=statistics.median(rois),
        p25_roi=statistics.quantiles(rois, n=4)[0] if n >= 4 else min(rois),
        p75_roi=statistics.quantiles(rois, n=4)[2] if n >= 4 else max(rois),
        max_loss=-min(pnls) if pnls else 0,
        total_pnl=sum(pnls),
    )


def sweep(cell_data, offsets, dcas, exits, strategies=('A', 'B')):
    out = []
    for off in offsets:
        for dca in dcas:
            for ext in exits:
                strats = strategies if dca is not None else ('NA',)
                for strat in strats:
                    s = cell_stats(cell_data, off, dca, ext, strat)
                    if s is None:
                        # still record so we can see fill_rate=0
                        continue
                    out.append(dict(offset=off, dca_drop=dca, exit_target=ext, strategy=strat, **s))
    return out


def parse_name(name):
    tokens = name.split('_')
    if tokens[0] not in ('ATP', 'WTA'):
        return None
    cat = tokens[0] + '_' + tokens[1]
    direction = tokens[2]
    lo, hi = tokens[3].split('-')
    return (cat, direction, int(lo), int(hi))


def main():
    t0 = time.time()
    with open(f'{REAL}/cell_tickers.json') as f:
        cell_tickers = json.load(f)
    with open(f'{REAL}/ticker_meta.json') as f:
        ticker_meta = json.load(f)

    all_cells = sorted(cell_tickers.keys())
    print(f'Cells: {len(all_cells)}', flush=True)

    all_rows = []
    cell_recs = {}
    envelope_rows = []

    for name in all_cells:
        t_cell = time.time()
        ck = parse_name(name)
        if ck is None:
            continue
        cfg = DEPLOYMENT.get(ck)
        if cfg is None:
            print(f'  [{name}] SKIP no deployment', flush=True)
            continue
        entry_lo = cfg['entry_lo']; entry_hi = cfg['entry_hi']
        deployed_offset = cfg.get('maker_bid_offset', 0) or 0

        # Load ticks + cache entry for each offset
        cell_data = {}
        peak_at_off0 = []  # peak bid after entry at offset=0 (envelope proxy)
        avg_fill_per_offset = defaultdict(list)
        for tk in cell_tickers[name]:
            p = f'{TICKS_DIR}/{tk.replace("/","_")}.bin'
            if not os.path.exists(p): continue
            ticks = load_ticks(p)
            if len(ticks) < 10: continue
            m = ticker_meta.get(tk, {})
            sb = m.get('settle_bid')
            entry_cache = {}
            for off in COARSE_OFFSETS:
                e_idx, e_px = maker_fill(ticks, entry_lo, entry_hi, off)
                entry_cache[off] = (e_idx, e_px)
                if e_idx is not None:
                    avg_fill_per_offset[off].append(e_px)
                    if off == 0:
                        peak_at_off0.append((e_px, peak_bid_after(ticks, e_idx)))
            cell_data[tk] = (ticks, sb, entry_cache)

        n_trajs = len(cell_data)
        if n_trajs == 0:
            print(f'  [{name}] NO_TRAJECTORIES', flush=True)
            continue

        # Envelope info (using offset=0 baseline)
        fill_rates_by_offset = {off: 100.0 * len(lst) / n_trajs for off, lst in avg_fill_per_offset.items()}
        if peak_at_off0:
            peak_vals = [pk for _, pk in peak_at_off0]
            peak_vals.sort()
            n = len(peak_vals)
            p25 = peak_vals[n // 4] if n >= 4 else peak_vals[0]
            p50 = peak_vals[n // 2]
            p75 = peak_vals[3 * n // 4] if n >= 4 else peak_vals[-1]
            p90 = peak_vals[int(0.9 * n)] if n >= 10 else peak_vals[-1]
            reaches_95 = sum(1 for pk in peak_vals if pk >= 95) / n
            reaches_99 = sum(1 for pk in peak_vals if pk >= 99) / n
        else:
            p25 = p50 = p75 = p90 = 0; reaches_95 = reaches_99 = 0
        envelope_rows.append(dict(
            cell=name, entry_lo=entry_lo, entry_hi=entry_hi, deployed_offset=deployed_offset,
            n_trajs=n_trajs, peak_p25=p25, peak_p50=p50, peak_p75=p75, peak_p90=p90,
            reaches_95_pct=100*reaches_95, reaches_99_pct=100*reaches_99,
            fill_rates_by_offset=fill_rates_by_offset,
        ))

        # Coarse sweep (offset × dca × exit × strat)
        rows = sweep(cell_data, COARSE_OFFSETS, COARSE_DCA, COARSE_EXIT)
        for r in rows:
            r['cell'] = name
        all_rows.extend(rows)

        # Filter: require n>=max(10, 50% of n_trajs) for winner selection; but keep all in output
        n_thresh = max(10, n_trajs // 4)
        eligible = [r for r in rows if r['n'] >= n_thresh]
        if not eligible:
            eligible = rows  # take whatever

        # Best mean_pnl
        eligible.sort(key=lambda r: r['mean_pnl'], reverse=True)
        coarse_top = eligible[0] if eligible else None
        if coarse_top is None:
            print(f'  [{name}] NO_RESULTS', flush=True)
            continue

        # Fine sweep: offset ±1 around coarse top, dca/exit 1c resolution
        top_off = coarse_top['offset']
        fine_offsets = list(range(top_off - 1, top_off + 2))  # 3 values around winner
        if coarse_top['dca_drop'] is None:
            fine_dca = [None, 1, 2, 3, 4, 5]
        else:
            fine_dca = list(range(max(1, coarse_top['dca_drop'] - 5), coarse_top['dca_drop'] + 6))
        if coarse_top['exit_target'] is None:
            fine_exit = [None, 1, 2, 3, 4, 5, 6, 7, 8]
        else:
            fine_exit = list(range(max(1, coarse_top['exit_target'] - 5), coarse_top['exit_target'] + 6))

        # Need to extend entry_cache for new offsets not yet computed
        for tk, (ticks, sb, ec) in cell_data.items():
            for off in fine_offsets:
                if off not in ec:
                    e_idx, e_px = maker_fill(ticks, entry_lo, entry_hi, off)
                    ec[off] = (e_idx, e_px)
                    if e_idx is not None:
                        avg_fill_per_offset[off].append(e_px)

        fine_rows = sweep(cell_data, fine_offsets, fine_dca, fine_exit)
        for r in fine_rows: r['cell'] = name
        all_rows.extend(fine_rows)

        combined = rows + fine_rows
        n_thresh = max(10, n_trajs // 4)
        eligible = [r for r in combined if r['n'] >= n_thresh]
        if not eligible:
            eligible = combined
        eligible.sort(key=lambda r: r['mean_pnl'], reverse=True)
        rec = eligible[0]

        # Same-cell comparison at offset=0 baseline (for context)
        off0_candidates = [r for r in combined if r['offset'] == 0]
        off0_candidates.sort(key=lambda r: r['mean_pnl'], reverse=True)
        off0_best = off0_candidates[0] if off0_candidates else None

        # Best hold_99 variant at any offset (for comparison)
        h99 = sorted([r for r in combined if r['exit_target'] is None],
                     key=lambda r: r['mean_pnl'], reverse=True)
        h99_best = h99[0] if h99 else None
        # Best finite variant at any offset
        fin = sorted([r for r in combined if r['exit_target'] is not None],
                     key=lambda r: r['mean_pnl'], reverse=True)
        fin_best = fin[0] if fin else None

        cell_recs[name] = dict(
            rec=rec, off0_best=off0_best, h99_best=h99_best, fin_best=fin_best,
            n_trajs=n_trajs, entry_lo=entry_lo, entry_hi=entry_hi,
            deployed_offset=deployed_offset,
            envelope=dict(p25=p25, p50=p50, p75=p75, p90=p90,
                          reaches_95=100*reaches_95, reaches_99=100*reaches_99),
            fill_rates_by_offset=fill_rates_by_offset,
        )
        dt = time.time() - t_cell
        offset_changed = ' ←CHANGE' if rec['offset'] != deployed_offset else ''
        low_fill = ' ⚠LOW_FILL' if rec['fill_rate'] < 50 else ''
        print(f'  [{name}] n_trajs={n_trajs} dt={dt:.0f}s rec=off{rec["offset"]:+}/dca{rec["dca_drop"]}/exit{rec["exit_target"]}/{rec["strategy"]} fill={rec["fill_rate"]:.0f}% mean_pnl={rec["mean_pnl"]:+.1f}c{offset_changed}{low_fill}', flush=True)

    # --- Write CSVs ---
    with open(f'{OUT}/all_configs.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell', 'offset', 'dca', 'exit', 'strat', 'n', 'n_attempts', 'fill_rate',
                    'avg_fill', 'win_rate', 'mean_pnl', 'median_pnl',
                    'mean_roi', 'median_roi', 'p25_roi', 'p75_roi', 'max_loss', 'total_pnl'])
        for r in all_rows:
            w.writerow([r['cell'], r['offset'],
                        '' if r['dca_drop'] is None else r['dca_drop'],
                        'hold99' if r['exit_target'] is None else r['exit_target'],
                        r['strategy'], r['n'], r['n_attempts'], round(r['fill_rate'], 1),
                        round(r['avg_fill'], 1), round(r['win_rate'], 1),
                        round(r['mean_pnl'], 1), round(r['median_pnl'], 1),
                        round(r['mean_roi'], 2), round(r['median_roi'], 2),
                        round(r['p25_roi'], 2), round(r['p75_roi'], 2),
                        r['max_loss'], r['total_pnl']])

    with open(f'{OUT}/recommendations.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell', 'n_trajs', 'entry_lo', 'entry_hi', 'deployed_offset',
                    'peak_p50', 'peak_p75', 'peak_p90', 'reaches_95_pct', 'reaches_99_pct',
                    'rec_offset', 'rec_dca', 'rec_exit', 'rec_strat',
                    'rec_n', 'rec_fill_rate', 'rec_mean_pnl_c', 'rec_median_pnl_c',
                    'rec_mean_roi', 'rec_win_rate', 'rec_max_loss',
                    'offset_changed_from_deploy',
                    'off0_dca', 'off0_exit', 'off0_mean_pnl', 'off0_fill_rate',
                    'h99_offset', 'h99_dca', 'h99_mean_pnl',
                    'fin_offset', 'fin_dca', 'fin_exit', 'fin_strat', 'fin_mean_pnl',
                    'low_fill_flag'])
        for name in all_cells:
            if name not in cell_recs: continue
            cr = cell_recs[name]
            r = cr['rec']; env = cr['envelope']
            o0 = cr['off0_best']; h = cr['h99_best']; fn = cr['fin_best']
            w.writerow([
                name, cr['n_trajs'], cr['entry_lo'], cr['entry_hi'], cr['deployed_offset'],
                env['p50'], env['p75'], env['p90'],
                round(env['reaches_95'], 1), round(env['reaches_99'], 1),
                r['offset'],
                '' if r['dca_drop'] is None else r['dca_drop'],
                'hold99' if r['exit_target'] is None else r['exit_target'],
                r['strategy'],
                r['n'], round(r['fill_rate'], 1),
                round(r['mean_pnl'], 1), round(r['median_pnl'], 1),
                round(r['mean_roi'], 2), round(r['win_rate'], 1), r['max_loss'],
                'YES' if r['offset'] != cr['deployed_offset'] else 'no',
                '' if not o0 else ('' if o0['dca_drop'] is None else o0['dca_drop']),
                '' if not o0 else ('hold99' if o0['exit_target'] is None else o0['exit_target']),
                '' if not o0 else round(o0['mean_pnl'], 1),
                '' if not o0 else round(o0['fill_rate'], 1),
                '' if not h else h['offset'],
                '' if not h else ('' if h['dca_drop'] is None else h['dca_drop']),
                '' if not h else round(h['mean_pnl'], 1),
                '' if not fn else fn['offset'],
                '' if not fn else ('' if fn['dca_drop'] is None else fn['dca_drop']),
                '' if not fn else fn['exit_target'],
                '' if not fn else fn['strategy'],
                '' if not fn else round(fn['mean_pnl'], 1),
                'YES' if r['fill_rate'] < 50 else 'no',
            ])

    with open(f'{OUT}/envelope.csv', 'w', newline='') as f:
        w = csv.writer(f)
        header = ['cell', 'entry_lo', 'entry_hi', 'deployed_offset', 'n_trajs',
                  'peak_p25', 'peak_p50', 'peak_p75', 'peak_p90',
                  'reaches_95_pct', 'reaches_99_pct']
        for off in COARSE_OFFSETS:
            header.append(f'fill_rate_off{off:+}')
        w.writerow(header)
        for er in envelope_rows:
            row = [er['cell'], er['entry_lo'], er['entry_hi'], er['deployed_offset'], er['n_trajs'],
                   er['peak_p25'], er['peak_p50'], er['peak_p75'], er['peak_p90'],
                   round(er['reaches_95_pct'], 1), round(er['reaches_99_pct'], 1)]
            for off in COARSE_OFFSETS:
                row.append(round(er['fill_rates_by_offset'].get(off, 0), 1))
            w.writerow(row)

    # Per-cell text reports
    def fmt(r):
        e_str = 'hold99' if r['exit_target'] is None else f'+{r["exit_target"]}c'
        return (f'off={r["offset"]:+d} dca={str(r["dca_drop"]):>4} exit={e_str:>6} '
                f'strat={r["strategy"]:>2} | n={r["n"]:>3} fill={r["fill_rate"]:>4.0f}% '
                f'fill_px={r["avg_fill"]:>4.1f}c mean={r["mean_pnl"]:+7.1f}c med={r["median_pnl"]:+7.1f}c '
                f'win={r["win_rate"]:>4.0f}% maxL={r["max_loss"]:>4}c')

    all_by_cell = defaultdict(list)
    for r in all_rows:
        all_by_cell[r['cell']].append(r)
    for name, rows in all_by_cell.items():
        if name not in cell_recs: continue
        cr = cell_recs[name]
        L = []
        L.append(f'CELL: {name} | entry_range: {cr["entry_lo"]}-{cr["entry_hi"]} | deployed_offset: {cr["deployed_offset"]:+d}')
        L.append(f'n_trajectories: {cr["n_trajs"]}')
        L.append('')
        L.append(f'Peak bid distribution (offset=0 baseline):')
        e = cr['envelope']
        L.append(f'  p25={e["p25"]}c p50={e["p50"]}c p75={e["p75"]}c p90={e["p90"]}c | reaches_95c={e["reaches_95"]:.0f}% reaches_99c={e["reaches_99"]:.0f}%')
        L.append('')
        L.append(f'Fill rate by offset:')
        for off in COARSE_OFFSETS:
            fr = cr['fill_rates_by_offset'].get(off, 0)
            L.append(f'  offset={off:+2d}: {fr:>4.0f}% fill rate')
        L.append('')
        r = cr['rec']
        L.append(f'RECOMMENDATION: {fmt(r)}')
        if r['offset'] != cr['deployed_offset']:
            L.append(f'  ** OFFSET CHANGE from {cr["deployed_offset"]:+d} to {r["offset"]:+d} **')
        if r['fill_rate'] < 50:
            L.append(f'  ** LOW FILL RATE WARNING: {r["fill_rate"]:.0f}% of trajectories did not fill at this offset **')
        L.append('')
        if cr['off0_best']:
            L.append(f'For comparison, same cell at offset=0 (baseline leader behavior):')
            L.append(f'  {fmt(cr["off0_best"])}')
        L.append('')
        L.append(f'Best hold_99 variant: {fmt(cr["h99_best"]) if cr["h99_best"] else "none"}')
        L.append(f'Best finite variant: {fmt(cr["fin_best"]) if cr["fin_best"] else "none"}')
        L.append('')
        rows.sort(key=lambda r: r['mean_pnl'], reverse=True)
        L.append('Top 10 by mean_pnl:')
        for r in rows[:10]: L.append('  ' + fmt(r))
        L.append(''); L.append('Top 10 by median_pnl:')
        for r in sorted(rows, key=lambda r: r['median_pnl'], reverse=True)[:10]: L.append('  ' + fmt(r))
        with open(f'{CELLS_DIR}/{name}.txt', 'w') as f:
            f.write('\n'.join(L))

    print(f'\nTOTAL: {time.time()-t0:.1f}s across {len(cell_recs)} cells', flush=True)


if __name__ == '__main__':
    main()
