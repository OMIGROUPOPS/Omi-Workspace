"""Step 6 v3 — tick-replay with TRUE maker placement logic.

Fixes from v2:
1. Entry fill price = actual maker placement (bid+1+offset clipped to entry range),
   NOT cell nominal sub_hi.
2. DCA fill price = actual_fill - dca_drop (a real price, not a static).
3. ROI computed on actual blended cost.
4. Edge-over-market: our_win_rate vs (1 - avg_fill/100) = market-implied loss rate.
5. Recommendation filter: hold_99 only when n>=30, edge>5%, mean>10%, p25>-50%.

Inputs:
- /tmp/validation4/step6_real/ticks/<ticker>.bin  (binary '<IBB' records)
- /tmp/validation4/step6_real/ticker_meta.json
- /tmp/validation4/step6_real/cell_tickers.json
- /tmp/validation4/old_blueprint.py + current version_b_blueprint.py  (for entry_lo/hi, offset)
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
sys.path.insert(0, '/tmp/validation4')
from version_b_blueprint import DEPLOYMENT

REAL = '/tmp/validation4/step6_real'
TICKS_DIR = f'{REAL}/ticks'
OUT = f'{REAL}/out_v3'
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
    # dedupe adjacent identical ticks
    out = []
    prev = None
    for t in ticks:
        if t != prev:
            out.append(t)
            prev = t
    return out


def simulate_maker(ticks, entry_lo, entry_hi, maker_offset, dca_drop, exit_target, strategy, settle_bid, taker_after_sec=None):
    """Tick-by-tick replay with real maker placement.

    - entry_lo/hi: sub-range from cell config (e.g., 57-59 for ATP_CHALL leader 55-59)
    - maker_offset: per-cell offset (0 for leaders, negative for underdogs)
    - taker_after_sec: if set, cross the ask as taker if no fill after this many seconds
      (None = no taker, maker-only). Use first_ts + taker_after_sec as cutoff.

    Returns dict with actual_fill_price, blended_cost, pnl, roi, etc.
    """
    if not ticks:
        return None
    first_ts = ticks[0][0]
    # Estimate match start = last tick - 1 hour (tennis matches are ~1.5-2 hours)
    # Also could look at categories, but this is good enough
    last_ts = ticks[-1][0]

    # --- Phase 1: entry fill ---
    entry_fill_px = None
    entry_fill_idx = None
    for i, (ts, bid, ask) in enumerate(ticks):
        age = ts - first_ts
        # compute candidate maker price
        bump = 2 if age > 1800 else 1
        buy_px = bid + bump + maker_offset
        buy_px = min(buy_px, ask - 1)  # post-only
        buy_px = max(1, buy_px)
        # must be within sub-range
        if buy_px < entry_lo or buy_px > entry_hi:
            # if taker-after, check if time to cross
            if taker_after_sec is not None and age >= taker_after_sec and entry_lo <= ask <= entry_hi:
                entry_fill_px = ask  # cross
                entry_fill_idx = i
                break
            continue
        # maker_price in range. Check if ask has crossed down to our maker level.
        # Simplification: if ask <= buy_px, our maker would have filled by now.
        if ask <= buy_px:
            # Fill at buy_px (maker) — but cap at ask (could be lower if we got lucky)
            entry_fill_px = min(buy_px, ask)
            entry_fill_idx = i
            break
        # Taker fallback path
        if taker_after_sec is not None and age >= taker_after_sec and entry_lo <= ask <= entry_hi:
            entry_fill_px = ask
            entry_fill_idx = i
            break

    if entry_fill_px is None:
        return None

    pos = ES
    cost = ES * entry_fill_px
    blended_cost_per_ct = entry_fill_px
    dca_filled = False
    dca_fill_px = None

    # Sell target
    if exit_target is None:
        sell_target = 99
    else:
        sell_target = min(99, entry_fill_px + exit_target)

    dca_trigger_px = None
    if dca_drop is not None:
        dca_trigger_px = entry_fill_px - dca_drop

    # --- Phase 2: post-entry iteration ---
    for i in range(entry_fill_idx + 1, len(ticks)):
        ts, bid, ask = ticks[i]

        # Sell check: our maker sell rests at sell_target. Fills when bid reaches it.
        if bid >= sell_target and sell_target <= 99:
            sell_px = sell_target
            pnl = pos * (sell_px - blended_cost_per_ct) if not dca_filled else (
                ES * (sell_px - entry_fill_px) + DS * (sell_px - dca_fill_px))
            return dict(
                event='SOLD_POST_DCA' if dca_filled else 'SOLD_PRE_DCA',
                entry_fill_px=entry_fill_px,
                sell_px=sell_px, pnl=pnl, pos=pos,
                blended_cost=cost, avg_cost=blended_cost_per_ct if not dca_filled else int(round(cost / pos)),
                dca_fill_px=dca_fill_px, cap=cost, roi=100.0 * pnl / cost,
            )

        # DCA check
        if (not dca_filled) and dca_trigger_px is not None and 1 <= dca_trigger_px < 100:
            if ask <= dca_trigger_px:
                dca_filled = True
                dca_fill_px = dca_trigger_px  # maker DCA fills at this price
                pos = ES + DS
                cost = ES * entry_fill_px + DS * dca_fill_px
                blended_cost_per_ct = cost / pos
                if exit_target is None:
                    sell_target = 99
                elif strategy == 'B':
                    sell_target = min(99, max(1, int(round(blended_cost_per_ct)) + exit_target))
                # Strategy A: sell_target unchanged

    # No sell — settle
    if settle_bid is None:
        return None
    if settle_bid >= 80:
        outcome = 100; event = 'SETTLE_WON'
    elif settle_bid <= 20:
        outcome = 0; event = 'SETTLE_LOST'
    else:
        outcome = settle_bid; event = 'SETTLE_MID'
    pnl = ES * (outcome - entry_fill_px)
    if dca_filled:
        pnl += DS * (outcome - dca_fill_px)
    return dict(
        event=event, entry_fill_px=entry_fill_px,
        sell_px=outcome, pnl=pnl, pos=pos,
        blended_cost=cost, avg_cost=blended_cost_per_ct,
        dca_fill_px=dca_fill_px, cap=cost, roi=100.0 * pnl / cost if cost else 0.0,
    )


def cell_stats(cell_data, dca, exit_target, strategy, entry_lo, entry_hi, maker_offset):
    results = []
    fills = []
    for tk, (ticks, settle_bid) in cell_data.items():
        r = simulate_maker(ticks, entry_lo, entry_hi, maker_offset, dca, exit_target, strategy, settle_bid)
        if r is not None and r['cap'] > 0:
            results.append(r)
            fills.append(r['entry_fill_px'])
    if not results:
        return None
    pnls = [r['pnl'] for r in results]
    rois = [r['roi'] for r in results]
    wins = sum(1 for p in pnls if p > 0)
    avg_fill = statistics.mean(fills) if fills else 0.0
    market_implied_win = 100.0 * (1 - avg_fill / 100) if avg_fill > 0 else 0.0
    our_win_rate = 100.0 * wins / len(results)
    return dict(
        n=len(results),
        avg_fill_px=avg_fill,
        our_win_rate=our_win_rate,
        market_implied_win=market_implied_win,
        edge=our_win_rate - (100.0 - avg_fill),  # our_win - market_implied_win
        mean_roi=statistics.mean(rois),
        median_roi=statistics.median(rois),
        p10_roi=statistics.quantiles(rois, n=10)[0] if len(rois) >= 10 else min(rois),
        p25_roi=statistics.quantiles(rois, n=4)[0] if len(rois) >= 4 else min(rois),
        p75_roi=statistics.quantiles(rois, n=4)[2] if len(rois) >= 4 else max(rois),
        p90_roi=statistics.quantiles(rois, n=10)[-1] if len(rois) >= 10 else max(rois),
        max_loss=-min(pnls),
        total_pnl=sum(pnls),
    )


def sweep(cell_data, dcas, exits, entry_lo, entry_hi, maker_offset, strategies=('A', 'B')):
    out = []
    for dca in dcas:
        for ext in exits:
            strats = strategies if dca is not None else ('NA',)
            for strat in strats:
                s = cell_stats(cell_data, dca, ext, strat, entry_lo, entry_hi, maker_offset)
                if s is None:
                    continue
                out.append(dict(dca_drop=dca, exit_target=ext, strategy=strat, **s))
    return out


def classify_edge(row):
    n = row['n']
    edge = row['edge']
    mean = row['mean_roi']
    p25 = row['p25_roi']
    is_hold99 = row['exit_target'] is None
    if not is_hold99:
        return 'finite'
    # hold_99: strict filter
    if n < 30:
        return 'LOW_N'
    if mean < 10:
        return 'LOW_ROI'
    if edge < 5:
        return 'MARKET-FOLLOWING'
    if edge < 10:
        return 'WEAK_EDGE'
    if p25 < -50:
        return 'TAIL_RISK'
    return 'REAL_EDGE'


def recommend(cell_rows):
    """Pick the best config for a cell, honoring hold_99 filter."""
    # Filter out low-n
    valid = [r for r in cell_rows if r['n'] >= max(15, max(r2['n'] for r2 in cell_rows) // 2)]
    if not valid:
        valid = cell_rows

    # First try to find hold_99 with real edge
    h99 = [r for r in valid if r['exit_target'] is None]
    good_h99 = [r for r in h99 if classify_edge(r) == 'REAL_EDGE']
    good_h99.sort(key=lambda r: r['mean_roi'], reverse=True)

    # Finite candidates (strictest: mean>0, med>0, p25 > -50)
    finite = [r for r in valid if r['exit_target'] is not None
              and r['mean_roi'] > 0 and r['median_roi'] > 0 and r['p25_roi'] > -50]
    finite.sort(key=lambda r: r['mean_roi'], reverse=True)

    # If any hold_99 meets the strict bar, pick it; else best finite; else best-mean anything
    if good_h99:
        pick = good_h99[0]
        pick_class = 'REAL_EDGE_HOLD99'
    elif finite:
        pick = finite[0]
        pick_class = 'FINITE_WINNER'
    else:
        valid.sort(key=lambda r: r['mean_roi'], reverse=True)
        pick = valid[0]
        pick_class = 'FALLBACK_BEST_MEAN'
    return pick, pick_class


def main():
    t0 = time.time()
    with open(f'{REAL}/cell_tickers.json') as f:
        cell_tickers = json.load(f)
    with open(f'{REAL}/ticker_meta.json') as f:
        ticker_meta = json.load(f)

    all_cells = sorted(cell_tickers.keys())
    print(f'Cells: {len(all_cells)}')

    # Parse cell_id -> (cat, direction, lo, hi)
    def parse_name(name):
        parts = name.rsplit('_', 2)
        if len(parts) != 3:
            return None
        cat = '_'.join(parts[0].split('_')[:-1]) if '_' in parts[0] else parts[0]
        # name format: CAT_DIRECTION_LO-HI e.g., ATP_CHALL_leader_55-59
        # split differently
        tokens = name.split('_')
        # category is tokens[0] if no underscore OR tokens[0]+'_'+tokens[1]
        if tokens[0] in ('ATP', 'WTA'):
            cat = tokens[0] + '_' + tokens[1]
            direction = tokens[2]
            lo_hi = tokens[3]
        else:
            return None
        lo, hi = lo_hi.split('-')
        return (cat, direction, int(lo), int(hi))

    all_rows = []
    cell_recs = {}
    timings = []

    for name in all_cells:
        t_cell = time.time()
        cell_key = parse_name(name)
        if cell_key is None:
            print(f'  [{name}] SKIP: unparseable cell name')
            continue
        cfg = DEPLOYMENT.get(cell_key)
        if cfg is None:
            print(f'  [{name}] SKIP: cell not in current DEPLOYMENT')
            continue
        entry_lo = cfg.get('entry_lo', cell_key[2])
        entry_hi = cfg.get('entry_hi', cell_key[3])
        offset = cfg.get('maker_bid_offset', 0) or 0

        # Load ticks
        cell_data = {}
        for tk in cell_tickers[name]:
            bin_path = f'{TICKS_DIR}/{tk.replace("/","_")}.bin'
            if not os.path.exists(bin_path):
                continue
            ticks = load_ticks(bin_path)
            if len(ticks) < 2:
                continue
            m = ticker_meta.get(tk, {})
            sb = m.get('settle_bid')
            cell_data[tk] = (ticks, sb)

        if not cell_data:
            print(f'  [{name}] NO_DATA')
            continue

        # Coarse
        rows = sweep(cell_data, COARSE_DCA, COARSE_EXIT, entry_lo, entry_hi, offset)
        for r in rows:
            r['cell_id'] = name
            r['cell_key'] = cell_key
            r['entry_lo'] = entry_lo
            r['entry_hi'] = entry_hi
            r['offset'] = offset
        if not rows:
            print(f'  [{name}] NO_COARSE_ROWS')
            continue

        # Fine around best
        rows.sort(key=lambda r: r['mean_roi'], reverse=True)
        top = rows[0]
        if top['dca_drop'] is None:
            dca_range = [None, 1, 2, 3, 4, 5]
        else:
            lo_d = max(1, top['dca_drop'] - 5); hi_d = top['dca_drop'] + 5
            dca_range = list(range(lo_d, hi_d + 1))
        if top['exit_target'] is None:
            exit_range = [None, 1, 2, 3, 4, 5]
        else:
            lo_e = max(1, top['exit_target'] - 5); hi_e = top['exit_target'] + 5
            exit_range = list(range(lo_e, hi_e + 1))
        fine_rows = sweep(cell_data, dca_range, exit_range, entry_lo, entry_hi, offset)
        for r in fine_rows:
            r['cell_id'] = name
            r['cell_key'] = cell_key
            r['entry_lo'] = entry_lo
            r['entry_hi'] = entry_hi
            r['offset'] = offset

        combined = rows + fine_rows
        all_rows.extend(combined)

        rec, rec_class = recommend(combined)
        # Also pick the best alternative (finite if hold_99 won, or hold_99 if finite won)
        if rec['exit_target'] is None:
            # hold_99 won — find best finite for comparison
            fin_list = [r for r in combined if r['exit_target'] is not None]
            fin_list.sort(key=lambda r: r['mean_roi'], reverse=True)
            alt = fin_list[0] if fin_list else None
        else:
            # finite won — find best hold_99 for comparison
            h_list = [r for r in combined if r['exit_target'] is None]
            h_list.sort(key=lambda r: r['mean_roi'], reverse=True)
            alt = h_list[0] if h_list else None

        cell_recs[name] = dict(rec=rec, rec_class=rec_class, alt=alt,
                               n_trajs=len(cell_data), entry_lo=entry_lo,
                               entry_hi=entry_hi, offset=offset)
        dt = time.time() - t_cell
        timings.append((name, len(cell_data), sum(len(t) for t, _ in cell_data.values()), dt))
        print(f'  [{name}] n={len(cell_data)} offset={offset} dt={dt:.0f}s rec={rec["dca_drop"]}/{rec["exit_target"]}/{rec["strategy"]} class={rec_class} mean_roi={rec["mean_roi"]:+.1f}% edge={rec["edge"]:+.1f}', flush=True)

    # Write full stage1+fine rows
    with open(f'{OUT}/all_configs.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell_id', 'entry_lo', 'entry_hi', 'offset',
                    'dca_drop', 'exit_target', 'strategy',
                    'n', 'avg_fill_px', 'our_win_rate', 'market_implied_win', 'edge',
                    'mean_roi', 'median_roi', 'p10_roi', 'p25_roi', 'p75_roi', 'p90_roi',
                    'max_loss', 'total_pnl'])
        for r in all_rows:
            w.writerow([r['cell_id'], r['entry_lo'], r['entry_hi'], r['offset'],
                        '' if r['dca_drop'] is None else r['dca_drop'],
                        'hold99' if r['exit_target'] is None else r['exit_target'],
                        r['strategy'], r['n'],
                        round(r['avg_fill_px'], 2), round(r['our_win_rate'], 1),
                        round(r['market_implied_win'], 1), round(r['edge'], 1),
                        round(r['mean_roi'], 2), round(r['median_roi'], 2),
                        round(r['p10_roi'], 2), round(r['p25_roi'], 2),
                        round(r['p75_roi'], 2), round(r['p90_roi'], 2),
                        r['max_loss'], r['total_pnl']])

    # Recommendations CSV
    with open(f'{OUT}/all_cells_recommendations_v2.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cell_id', 'direction', 'tier', 'n_trades', 'entry_lo', 'entry_hi', 'offset',
                    'rec_dca', 'rec_exit', 'rec_strat', 'rec_class',
                    'avg_actual_fill', 'sub_hi_nominal',
                    'mean_roi', 'median_roi', 'p10', 'p25', 'p75', 'p90',
                    'our_win_rate', 'market_implied_win', 'edge_over_market',
                    'max_loss', 'total_pnl',
                    'edge_classification', 'confidence',
                    'alt_dca', 'alt_exit', 'alt_strat', 'alt_mean_roi', 'alt_edge'])
        for name in all_cells:
            if name not in cell_recs:
                continue
            cr = cell_recs[name]
            r = cr['rec']
            alt = cr['alt']
            cls = classify_edge(r) if r['exit_target'] is None else 'finite'
            # Confidence
            n = r['n']
            conf = 'HIGH' if n >= 50 else ('MEDIUM' if n >= 20 else 'LOW')
            ck = r['cell_key']
            w.writerow([
                name, ck[1], f'{ck[2]}-{ck[3]}', n, r['entry_lo'], r['entry_hi'], r['offset'],
                '' if r['dca_drop'] is None else r['dca_drop'],
                'hold99' if r['exit_target'] is None else r['exit_target'],
                r['strategy'], cr['rec_class'],
                round(r['avg_fill_px'], 2), r['entry_hi'],
                round(r['mean_roi'], 2), round(r['median_roi'], 2),
                round(r['p10_roi'], 2), round(r['p25_roi'], 2),
                round(r['p75_roi'], 2), round(r['p90_roi'], 2),
                round(r['our_win_rate'], 1), round(r['market_implied_win'], 1),
                round(r['edge'], 1), r['max_loss'], r['total_pnl'],
                cls, conf,
                '' if not alt else ('' if alt['dca_drop'] is None else alt['dca_drop']),
                '' if not alt else ('hold99' if alt['exit_target'] is None else alt['exit_target']),
                '' if not alt else alt['strategy'],
                '' if not alt else round(alt['mean_roi'], 2),
                '' if not alt else round(alt['edge'], 1),
            ])

    # Edge analysis text
    lines = []
    lines.append('=' * 100)
    lines.append('STEP 6 v3 — EDGE-OVER-MARKET ANALYSIS')
    lines.append('=' * 100)
    lines.append('')
    lines.append('Methodology:')
    lines.append('  - avg_actual_fill = mean of maker fill prices across trajectories in each cell')
    lines.append('  - market_implied_win = 1 - (avg_actual_fill / 100). This is what the market prices.')
    lines.append('  - our_win_rate = % of trades returning positive ROI (maker+DCA+exit sim)')
    lines.append('  - edge = our_win_rate - market_implied_win')
    lines.append('')
    lines.append('Classification for hold_99 cells:')
    lines.append('  REAL_EDGE     : edge > 10%, mean_roi > 10%, n >= 30, p25 > -50%')
    lines.append('  WEAK_EDGE     : 5% < edge <= 10%')
    lines.append('  MARKET-FOLLOWING: edge <= 5% (not hold_99-worthy)')
    lines.append('  LOW_N / LOW_ROI / TAIL_RISK : self-explanatory')
    lines.append('')
    lines.append(f'{"cell":38} {"n":>3} {"fill":>5} {"our%":>5} {"mkt%":>5} {"edge":>5} {"mean":>6} {"med":>6} {"rec":>14} {"class":>18}')
    for name in all_cells:
        if name not in cell_recs: continue
        cr = cell_recs[name]
        r = cr['rec']
        rec_str = ('hold99' if r['exit_target'] is None else f'+{r["exit_target"]}c')
        cls = classify_edge(r) if r['exit_target'] is None else 'finite'
        lines.append(f'{name:38} {r["n"]:>3} {r["avg_fill_px"]:>5.1f} {r["our_win_rate"]:>4.1f}% {r["market_implied_win"]:>4.1f}% {r["edge"]:>+5.1f} {r["mean_roi"]:>+5.1f}% {r["median_roi"]:>+5.1f}% {rec_str:>14} {cls:>18}')
    with open(f'{OUT}/edge_analysis.txt', 'w') as f:
        f.write('\n'.join(lines))

    # Per-cell reports
    def fmt(r):
        return (f'dca={str(r["dca_drop"]):>4} exit={str(r["exit_target"]) if r["exit_target"] is not None else "hold99":>6} '
                f'strat={r["strategy"]:>2} | n={r["n"]:>3} fill={r["avg_fill_px"]:>5.1f}c mean={r["mean_roi"]:+6.2f}% '
                f'med={r["median_roi"]:+6.2f}% win={r["our_win_rate"]:>4.1f}% edge={r["edge"]:>+5.1f} maxL={r["max_loss"]:>4}c')
    all_by_cell = defaultdict(list)
    for r in all_rows:
        all_by_cell[r['cell_id']].append(r)
    for name, rows in all_by_cell.items():
        if name not in cell_recs: continue
        cr = cell_recs[name]
        rows.sort(key=lambda r: r['mean_roi'], reverse=True)
        L = []
        L.append(f'CELL: {name} | n_trajs: {cr["n_trajs"]} | entry_range: {cr["entry_lo"]}-{cr["entry_hi"]} | offset: {cr["offset"]}')
        if cr['n_trajs'] < 30:
            L.append('*** SAMPLE WARNING: n < 30 ***')
        L.append('')
        L.append(f'RECOMMENDATION: {fmt(cr["rec"])}')
        L.append(f'  class: {cr["rec_class"]}')
        if cr['alt']:
            L.append(f'  alternative:   {fmt(cr["alt"])}')
        L.append('')
        L.append('Top 5 by mean ROI:')
        for r in rows[:5]: L.append('  ' + fmt(r))
        L.append(''); L.append('Top 5 by median ROI:')
        for r in sorted(rows, key=lambda x: x['median_roi'], reverse=True)[:5]: L.append('  ' + fmt(r))
        L.append(''); L.append('Top 5 by p25 ROI (worst-case bottom 25%):')
        for r in sorted(rows, key=lambda x: x['p25_roi'], reverse=True)[:5]: L.append('  ' + fmt(r))
        with open(f'{CELLS_DIR}/{name}.txt', 'w') as f:
            f.write('\n'.join(L))

    print(f'\nTOTAL: {time.time()-t0:.1f}s across {len(cell_recs)} cells')


if __name__ == '__main__':
    main()
