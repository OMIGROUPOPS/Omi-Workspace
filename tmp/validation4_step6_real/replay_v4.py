"""Step 6 v4 — simpler framing: per-cell volatility envelope + exit_target optimization.

For each cell:
  1. Measure peak_bid distribution after entry (p25/p50/p75/p90).
  2. Simulate maker entry via bid+1+offset; fill when subsequent ask <= our maker price.
     Actual fill price = our maker price at that moment.
  3. Sweep (dca_drop, exit_target, strategy) — pick config that maximizes mean PnL per trade.
  4. hold_99 recommended only when peak_bid reaches >=95c on majority of trades.
  5. Report fill_rate at recommended target.

Pragmatic fill model:
  - Track our maker price as bid changes (bid+1+offset, clipped).
  - We're "live" any tick where maker price is within entry_lo..entry_hi and < ask.
  - Fill triggers when next tick's ask <= our current maker (seller crossed to us).
  - If 30min gate elapses without fill, escalate to bid+2+offset.
  - If still unfilled by the end of the pregame window, no fill (abort trade).

Pregame window approximation: first 80% of ticks (last 20% = match live).
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
OUT = f'{REAL}/out_v4'
CELLS_DIR = f'{OUT}/cells'
os.makedirs(CELLS_DIR, exist_ok=True)

ES = 10
DS = 5
UNPACK = struct.Struct('<IBB').unpack

COARSE_DCA = [None, 5, 10, 15, 20, 25, 30]
COARSE_EXIT = [None, 5, 10, 15, 20, 25, 30]


def load_ticks(bin_path):
    with open(bin_path, 'rb') as f:
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
    """Find the first fill of our maker buy using bid+1+offset (then bid+2 after 30min).

    Returns (fill_idx, fill_price, fill_ts) or (None, None, None) if no fill.
    """
    if not ticks:
        return None, None, None
    first_ts = ticks[0][0]
    last_ts = ticks[-1][0]
    pregame_cutoff = first_ts + int((last_ts - first_ts) * pregame_ratio)

    # Track our current maker price across ticks
    prev_maker = None
    for i in range(len(ticks)):
        ts, bid, ask = ticks[i]
        if ts > pregame_cutoff:
            break
        bump = 2 if (ts - first_ts) > 1800 else 1
        candidate = bid + bump + offset
        candidate = min(candidate, ask - 1)
        candidate = max(1, candidate)
        in_range = entry_lo <= candidate <= entry_hi

        # Check if previous maker got filled by current ask
        if prev_maker is not None and ask <= prev_maker:
            return i, prev_maker, ts
        # Check same-tick fill (rare but possible)
        if in_range and ask <= candidate:
            return i, candidate, ts

        prev_maker = candidate if in_range else None

    return None, None, None


def peak_bid_after(ticks, entry_idx):
    """Return max bid reached after the entry fill, plus ts of that peak."""
    max_b = 0
    max_ts = None
    for j in range(entry_idx + 1, len(ticks)):
        ts, bid, ask = ticks[j]
        if bid > max_b:
            max_b = bid
            max_ts = ts
    return max_b, max_ts


def simulate(ticks, entry_lo, entry_hi, offset, dca_drop, exit_target, strategy, settle_bid,
             entry_idx=None, entry_px=None):
    """Full trade simulation with real maker placement. Accepts pre-computed entry for speed."""
    if entry_idx is None:
        entry_idx, entry_px, _ = maker_fill(ticks, entry_lo, entry_hi, offset)
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

    peak_bid = 0
    for j in range(entry_idx + 1, len(ticks)):
        ts, bid, ask = ticks[j]
        if bid > peak_bid: peak_bid = bid

        # Sell fill: bid reaches sell_target
        if bid >= sell_target:
            sell_px = sell_target
            if dca_filled:
                pnl = ES * (sell_px - entry_px) + DS * (sell_px - dca_px)
            else:
                pnl = ES * (sell_px - entry_px)
            return dict(
                event='SOLD_POST_DCA' if dca_filled else 'SOLD_PRE_DCA',
                entry_px=entry_px, sell_px=sell_px, pnl=pnl, pos=pos,
                cap=cost, avg=avg, dca_px=dca_px, peak_bid=peak_bid,
                roi=100.0 * pnl / cost,
            )

        # DCA: ask <= dca_trigger
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
    return dict(
        event=event, entry_px=entry_px, sell_px=outcome, pnl=pnl, pos=pos,
        cap=cost, avg=avg, dca_px=dca_px, peak_bid=peak_bid,
        roi=100.0 * pnl / cost if cost else 0.0,
    )


def cell_stats(cell_data, dca, exit_target, strategy, entry_lo, entry_hi, offset):
    # cell_data values are (ticks, settle_bid, entry_idx, entry_px) — entry cached
    results = []
    for tk, tup in cell_data.items():
        ticks, settle_bid, e_idx, e_px = tup
        if e_idx is None:
            continue
        r = simulate(ticks, entry_lo, entry_hi, offset, dca, exit_target, strategy, settle_bid,
                     entry_idx=e_idx, entry_px=e_px)
        if r is not None and r['cap'] > 0:
            results.append(r)
    if not results:
        return None
    pnls = [r['pnl'] for r in results]
    rois = [r['roi'] for r in results]
    fills = [r['entry_px'] for r in results]
    filled_exit = sum(1 for r in results if 'SOLD' in r['event'])
    wins = sum(1 for p in pnls if p > 0)
    return dict(
        n=len(results),
        avg_fill=statistics.mean(fills),
        fill_rate_exit=100.0 * filled_exit / len(results),
        win_rate=100.0 * wins / len(results),
        mean_pnl=statistics.mean(pnls),
        median_pnl=statistics.median(pnls),
        mean_roi=statistics.mean(rois),
        median_roi=statistics.median(rois),
        p25_roi=statistics.quantiles(rois, n=4)[0] if len(rois) >= 4 else min(rois),
        p75_roi=statistics.quantiles(rois, n=4)[2] if len(rois) >= 4 else max(rois),
        max_loss=-min(pnls) if pnls else 0,
        total_pnl=sum(pnls),
    )


def sweep(cell_data, dcas, exits, entry_lo, entry_hi, offset, strategies=('A', 'B')):
    out = []
    for dca in dcas:
        for ext in exits:
            strats = strategies if dca is not None else ('NA',)
            for strat in strats:
                s = cell_stats(cell_data, dca, ext, strat, entry_lo, entry_hi, offset)
                if s is None:
                    continue
                out.append(dict(dca_drop=dca, exit_target=ext, strategy=strat, **s))
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
    print(f'Cells: {len(all_cells)}')

    # First pass: peak-bid distribution per cell (using fills from cheap config)
    envelope_rows = []
    all_config_rows = []
    cell_best = {}
    timings = []

    for name in all_cells:
        t_cell = time.time()
        ck = parse_name(name)
        if ck is None:
            continue
        cfg = DEPLOYMENT.get(ck)
        if cfg is None:
            print(f'  [{name}] SKIP no cfg')
            continue
        entry_lo = cfg['entry_lo']; entry_hi = cfg['entry_hi']
        offset = cfg.get('maker_bid_offset', 0) or 0

        # Load ticks + cache entry-fill per trajectory
        cell_data = {}
        peaks = []
        fills = []
        for tk in cell_tickers[name]:
            p = f'{TICKS_DIR}/{tk.replace("/","_")}.bin'
            if not os.path.exists(p): continue
            ticks = load_ticks(p)
            if len(ticks) < 10: continue
            m = ticker_meta.get(tk, {})
            sb = m.get('settle_bid')
            entry_idx, entry_px, _ = maker_fill(ticks, entry_lo, entry_hi, offset)
            # Cache entry for sweep
            cell_data[tk] = (ticks, sb, entry_idx, entry_px)
            if entry_idx is None:
                continue
            fills.append(entry_px)
            pk, _ = peak_bid_after(ticks, entry_idx)
            peaks.append((entry_px, pk))

        if not cell_data or not peaks:
            print(f'  [{name}] NO_FILL_DATA')
            continue

        n_fills = len(peaks)
        n_attempts = len(cell_data)
        fill_rate_entry = 100.0 * n_fills / n_attempts if n_attempts else 0

        # Peak bid distribution (peaks is list of (entry_px, peak_bid))
        peak_vals = [pk for _, pk in peaks]
        peak_above_entry = [pk - ep for ep, pk in peaks]  # how much bid rose above entry
        p25 = statistics.quantiles(peak_vals, n=4)[0] if len(peak_vals) >= 4 else min(peak_vals)
        p50 = statistics.median(peak_vals)
        p75 = statistics.quantiles(peak_vals, n=4)[2] if len(peak_vals) >= 4 else max(peak_vals)
        p90 = statistics.quantiles(peak_vals, n=10)[-1] if len(peak_vals) >= 10 else max(peak_vals)
        reaches_99 = sum(1 for pk in peak_vals if pk >= 99) / len(peak_vals)
        avg_fill = statistics.mean(fills)
        envelope_rows.append(dict(
            cell=name, n=n_fills, n_attempts=n_attempts, fill_rate_entry=fill_rate_entry,
            avg_fill=avg_fill, p25_peak=p25, p50_peak=p50, p75_peak=p75, p90_peak=p90,
            reaches_99=100.0 * reaches_99, entry_lo=entry_lo, entry_hi=entry_hi, offset=offset,
        ))

        # Run sweep
        rows = sweep(cell_data, COARSE_DCA, COARSE_EXIT, entry_lo, entry_hi, offset)
        for r in rows:
            r['cell'] = name
        all_config_rows.extend(rows)
        if not rows:
            continue

        # Fine sweep around mean_pnl winner
        rows.sort(key=lambda r: r['mean_pnl'], reverse=True)
        top = rows[0]
        if top['dca_drop'] is None:
            dca_range = [None, 1, 2, 3, 4, 5]
        else:
            dca_range = list(range(max(1, top['dca_drop'] - 5), top['dca_drop'] + 6))
        if top['exit_target'] is None:
            exit_range = [None, 1, 2, 3, 4, 5, 6, 7, 8]
        else:
            exit_range = list(range(max(1, top['exit_target'] - 5), top['exit_target'] + 6))
        fine = sweep(cell_data, dca_range, exit_range, entry_lo, entry_hi, offset)
        for r in fine: r['cell'] = name
        all_config_rows.extend(fine)
        combined = rows + fine

        # Best by mean_pnl
        combined.sort(key=lambda r: r['mean_pnl'], reverse=True)
        best_mean = combined[0]
        # Best hold_99 for comparison
        h99 = sorted([r for r in combined if r['exit_target'] is None], key=lambda r: r['mean_pnl'], reverse=True)
        h99_best = h99[0] if h99 else None
        # Best finite
        fin = sorted([r for r in combined if r['exit_target'] is not None], key=lambda r: r['mean_pnl'], reverse=True)
        fin_best = fin[0] if fin else None

        # HOLD_99 justified criterion: >= 50% trajectories have peak_bid >= 95c
        reaches_95 = sum(1 for pk in peak_vals if pk >= 95) / len(peak_vals)
        hold99_justified = reaches_95 >= 0.50

        # Pick recommended: if hold_99 is BEST and justified, pick hold_99. Otherwise pick best finite.
        if best_mean['exit_target'] is None and hold99_justified:
            rec = best_mean
            rec_type = 'hold_99 (envelope reaches 99c often)'
        elif best_mean['exit_target'] is None and not hold99_justified:
            # hold_99 wins on sim but envelope doesn't reach 95c >= 50% → prefer finite
            if fin_best:
                rec = fin_best
                rec_type = 'finite (hold_99 wins sim but reaches_95%={:.0f}% < 50% threshold)'.format(100*reaches_95)
            else:
                rec = best_mean
                rec_type = 'hold_99 (no finite fallback)'
        else:
            rec = best_mean
            rec_type = 'finite'

        cell_best[name] = dict(
            rec=rec, rec_type=rec_type, h99_best=h99_best, fin_best=fin_best,
            envelope=dict(p25=p25, p50=p50, p75=p75, p90=p90, reaches_99=reaches_99*100,
                          reaches_95=reaches_95*100, avg_fill=avg_fill),
            n_trajs=len(cell_data), n_fills=n_fills,
            entry_lo=entry_lo, entry_hi=entry_hi, offset=offset,
        )
        dt = time.time() - t_cell
        timings.append((name, n_attempts, n_fills, dt))
        print(f'  [{name}] n={n_fills}/{n_attempts} fill={fill_rate_entry:.0f}% peaks p50={p50} p75={p75} p90={p90} rch95={100*reaches_95:.0f}% dt={dt:.0f}s rec={rec["dca_drop"]}/{rec["exit_target"]}/{rec["strategy"]} mean_pnl={rec["mean_pnl"]:+.1f}c [{rec_type}]', flush=True)

    # Write envelope CSV
    with open(f'{OUT}/peak_bid_envelope.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell', 'entry_lo', 'entry_hi', 'offset', 'n', 'n_attempts', 'fill_rate_entry',
                    'avg_fill_px', 'p25_peak', 'p50_peak', 'p75_peak', 'p90_peak', 'reaches_99_pct'])
        for r in envelope_rows:
            w.writerow([r['cell'], r['entry_lo'], r['entry_hi'], r['offset'], r['n'], r['n_attempts'],
                        round(r['fill_rate_entry'], 1), round(r['avg_fill'], 1),
                        r['p25_peak'], r['p50_peak'], r['p75_peak'], r['p90_peak'],
                        round(r['reaches_99'], 1)])

    # Recommendations CSV
    with open(f'{OUT}/recommendations.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell', 'n', 'entry_lo', 'entry_hi', 'offset',
                    'avg_fill_px', 'p50_peak_bid', 'p75_peak_bid', 'p90_peak_bid', 'reaches_95_pct',
                    'rec_dca', 'rec_exit', 'rec_strat', 'rec_type',
                    'mean_pnl_c', 'median_pnl_c', 'mean_roi', 'median_roi', 'p25_roi', 'win_rate',
                    'fill_rate_exit', 'max_loss',
                    'h99_dca', 'h99_exit', 'h99_mean_pnl',
                    'fin_dca', 'fin_exit', 'fin_strat', 'fin_mean_pnl'])
        for name in all_cells:
            if name not in cell_best: continue
            cb = cell_best[name]
            rec = cb['rec']; env = cb['envelope']
            h = cb['h99_best']; fn = cb['fin_best']
            w.writerow([name, rec['n'], cb['entry_lo'], cb['entry_hi'], cb['offset'],
                        round(env['avg_fill'], 1), env['p50'], env['p75'], env['p90'], round(env['reaches_95'], 1),
                        '' if rec['dca_drop'] is None else rec['dca_drop'],
                        'hold99' if rec['exit_target'] is None else rec['exit_target'],
                        rec['strategy'], cb['rec_type'],
                        round(rec['mean_pnl'], 1), round(rec['median_pnl'], 1),
                        round(rec['mean_roi'], 2), round(rec['median_roi'], 2),
                        round(rec['p25_roi'], 2), round(rec['win_rate'], 1),
                        round(rec['fill_rate_exit'], 1), rec['max_loss'],
                        '' if not h else ('' if h['dca_drop'] is None else h['dca_drop']),
                        '' if not h else 'hold99',
                        '' if not h else round(h['mean_pnl'], 1),
                        '' if not fn else ('' if fn['dca_drop'] is None else fn['dca_drop']),
                        '' if not fn else fn['exit_target'],
                        '' if not fn else fn['strategy'],
                        '' if not fn else round(fn['mean_pnl'], 1)])

    # All configs CSV
    with open(f'{OUT}/all_configs.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell', 'dca', 'exit', 'strat', 'n', 'avg_fill', 'fill_rate_exit',
                    'win_rate', 'mean_pnl', 'median_pnl', 'mean_roi', 'median_roi',
                    'p25_roi', 'p75_roi', 'max_loss', 'total_pnl'])
        for r in all_config_rows:
            w.writerow([r['cell'],
                        '' if r['dca_drop'] is None else r['dca_drop'],
                        'hold99' if r['exit_target'] is None else r['exit_target'],
                        r['strategy'], r['n'],
                        round(r['avg_fill'], 1), round(r['fill_rate_exit'], 1),
                        round(r['win_rate'], 1), round(r['mean_pnl'], 1),
                        round(r['median_pnl'], 1), round(r['mean_roi'], 2),
                        round(r['median_roi'], 2), round(r['p25_roi'], 2),
                        round(r['p75_roi'], 2), r['max_loss'], r['total_pnl']])

    print(f'\nTOTAL: {time.time()-t0:.1f}s across {len(cell_best)} cells')


if __name__ == '__main__':
    main()
