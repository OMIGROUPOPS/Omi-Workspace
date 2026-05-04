#!/usr/bin/env python3
"""Corrected spike analysis v2 — uses settlement API for actual pnl.

Settlement API gives:
  - yes_count_fp: contracts held at settlement
  - yes_total_cost: total cost in cents of YES contracts held
  - market_result: "yes" or "no"
  - If settled NO with YES position: loss = -yes_total_cost
  - If settled YES with YES position: profit = (100 * count) - yes_total_cost
"""
import csv, asyncio, aiohttp, sys
sys.path.insert(0, '/root/Omi-Workspace/arb-executor')
from ncaamb_stb import api_get, load_credentials

CSV = "/tmp/v3_enriched_trades.csv"

async def main():
    api_key, private_key = load_credentials()
    class RL:
        async def acquire(self): pass
    rl = RL()

    with open(CSV) as f:
        reader = csv.DictReader(f)
        trades = list(reader)

    print(f"Loaded {len(trades)} trades")

    # Pull ALL settlements (paginate)
    all_settlements = []
    async with aiohttp.ClientSession() as s:
        cursor = None
        while True:
            url = '/trade-api/v2/portfolio/settlements?limit=500'
            if cursor:
                url += f'&cursor={cursor}'
            resp = await api_get(s, api_key, private_key, url, rl)
            if not resp:
                break
            batch = resp.get('settlements', [])
            all_settlements.extend(batch)
            cursor = resp.get('cursor')
            if not cursor or not batch:
                break

    print(f"Settlements loaded: {len(all_settlements)}")

    # Build settlement map: ticker -> settlement data
    settle_map = {}
    for st in all_settlements:
        t = st.get('ticker', '')
        settle_map[t] = st

    # ─── Fix pnl for all trades ───
    # Strategy:
    # 1. If CSV has pnl_cents (was sold before settlement), keep it
    # 2. If CSV has empty pnl, look up settlement data
    # 3. Settlement gives us actual held contracts and their cost

    fixed_count = 0
    for t in trades:
        ticker = t.get('ticker', '')
        entry = int(float(t.get('entry_price', 0) or 0))
        pnl_raw = (t.get('pnl_cents', '') or '').strip()
        sport = t.get('sport', '?')
        mode = t.get('entry_mode', '')
        side = t.get('entry_side', '?')

        # Spike classification
        pre10m = (t.get('pre_entry_price_10m', '') or '').strip()
        if pre10m and pre10m not in ('nan', 'None', ''):
            try:
                fsp = int(float(pre10m))
            except:
                fsp = 50
        else:
            fsp = 50

        spike = entry - fsp
        is_maker = entry >= 88 or 'maker' in (mode or '') or '92' in (mode or '')

        t['_entry'] = entry
        t['_spike'] = spike
        t['_cls'] = "SPIKE" if spike > 2 else ("DIP" if spike < -2 else "FLAT")
        t['_is_maker'] = is_maker
        t['_sport'] = sport
        t['_fsp'] = fsp
        t['_side'] = side

        if pnl_raw and pnl_raw != 'nan':
            pnl = int(float(pnl_raw))
            t['_pnl'] = pnl
            t['_wl'] = "W" if pnl > 0 else ("L" if pnl < 0 else "P")
            t['_source'] = 'csv'
        else:
            # Look up settlement
            sdata = settle_map.get(ticker)
            if sdata:
                result = sdata.get('market_result', '')
                yes_ct = float(sdata.get('yes_count_fp', '0') or '0')
                yes_cost = int(sdata.get('yes_total_cost', 0) or 0)
                no_ct = float(sdata.get('no_count_fp', '0') or '0')
                no_cost = int(sdata.get('no_total_cost', 0) or 0)

                if result == 'no' and yes_ct > 0:
                    # Held YES, settled NO = full loss
                    pnl = -yes_cost
                    t['_pnl'] = pnl
                    t['_wl'] = "L"
                    t['_ct'] = int(yes_ct)
                    t['_source'] = 'settlement_NO'
                    fixed_count += 1
                elif result == 'yes' and yes_ct > 0:
                    # Held YES, settled YES = profit
                    pnl = int(100 * yes_ct) - yes_cost
                    t['_pnl'] = pnl
                    t['_wl'] = "W" if pnl > 0 else "L"
                    t['_ct'] = int(yes_ct)
                    t['_source'] = 'settlement_YES'
                    fixed_count += 1
                elif result == 'yes' and no_ct > 0:
                    # Held NO side, settled YES = loss on NO
                    pnl = -no_cost
                    t['_pnl'] = pnl
                    t['_wl'] = "L"
                    t['_ct'] = int(no_ct)
                    t['_source'] = 'settlement_NO_side'
                    fixed_count += 1
                elif result == 'no' and no_ct > 0:
                    # Held NO, settled NO = profit
                    pnl = int(100 * no_ct) - no_cost
                    t['_pnl'] = pnl
                    t['_wl'] = "W" if pnl > 0 else "L"
                    t['_ct'] = int(no_ct)
                    t['_source'] = 'settlement_NO_win'
                    fixed_count += 1
                else:
                    # Settled but no position (already sold before settlement)
                    # The CSV entry was the trade, and it was sold for pnl recorded in another row
                    # or pnl was supposed to come from exit_price
                    exit_p = (t.get('exit_price', '') or '').strip()
                    if exit_p and exit_p not in ('nan', ''):
                        try:
                            pnl = int(float(exit_p)) - entry
                            t['_pnl'] = pnl
                            t['_wl'] = "W" if pnl > 0 else ("L" if pnl < 0 else "P")
                            t['_source'] = 'exit_price'
                            fixed_count += 1
                        except:
                            t['_pnl'] = 0
                            t['_wl'] = "P"
                            t['_source'] = 'unknown_settled_0ct'
                    else:
                        t['_pnl'] = 0
                        t['_wl'] = "P"
                        t['_source'] = 'unknown_settled_0ct'
            else:
                # No settlement data = still open or very recent
                t['_pnl'] = 0
                t['_wl'] = "P"
                t['_source'] = 'no_settlement'

    print(f"Fixed from settlement: {fixed_count}")

    # ─── SECTION 1: The 37 missing-pnl trades resolved ───
    print()
    print("=" * 80)
    print("SECTION 1: ALL MISSING-PNL TRADES — RESOLVED")
    print("=" * 80)

    for t in trades:
        if t.get('_source', 'csv') != 'csv':
            side = t['_side']
            entry = t['_entry']
            sport = t['_sport']
            pnl = t['_pnl']
            wl = t['_wl']
            src = t['_source']
            ct = t.get('_ct', '?')
            maker = 'MAKER' if t['_is_maker'] else 'STB'
            print(f"  {sport:>8s}  {side:<6s}  entry={entry:>3d}c  {maker:>5s}  pnl={pnl:>+6d}c  wl={wl}  ct={ct}  src={src}")

    # ─── SECTION 2: The 5 specific losses ───
    print()
    print("=" * 80)
    print("SECTION 2: THE 5 CONFIRMED LOSSES")
    print("=" * 80)
    print(f"  {'Side':<6s} {'Sport':>8s} {'Entry':>6s} {'FSP':>5s} {'Spike':>7s} {'Cls':<6s} {'Type':>5s} {'PnL':>8s} {'W/L':>4s} {'Ct':>4s} {'Source':<20s}")
    print(f"  {'─'*6} {'─'*8} {'─'*6} {'─'*5} {'─'*7} {'─'*6} {'─'*5} {'─'*8} {'─'*4} {'─'*4} {'─'*20}")

    for name in ['YUZ', 'UTU', 'BON', 'ROD', 'GOJ']:
        for t in trades:
            if t['_side'] == name:
                ct = t.get('_ct', '?')
                print(f"  {t['_side']:<6s} {t['_sport']:>8s} {t['_entry']:>5d}c {t['_fsp']:>4d}c {t['_spike']:>+6d}c "
                      f"{t['_cls']:<6s} {'MAKER' if t['_is_maker'] else 'STB':>5s} {t['_pnl']:>+7d}c "
                      f"{t['_wl']:>4s} {str(ct):>4s} {t.get('_source', '?'):<20s}")

    # ─── SECTION 3: Corrected sport breakdown ───
    print()
    print("=" * 80)
    print("SECTION 3: CORRECTED SPORT-SPECIFIC SPIKE ANALYSIS")
    print("=" * 80)

    sports = sorted(set(t['_sport'] for t in trades))

    print(f"\n  {'Sport':<10s} {'Type':<7s} {'Spikes':>6s} {'W':>4s} {'L':>4s} {'P':>4s}  {'WR%':>7s} {'PnL':>10s} {'$/day':>8s}")
    print(f"  {'─'*10} {'─'*7} {'─'*6} {'─'*4} {'─'*4} {'─'*4}  {'─'*7} {'─'*10} {'─'*8}")

    for sport in sports:
        for entry_type in ['STB', 'MAKER']:
            spikes = [t for t in trades if t['_sport'] == sport
                       and t['_cls'] == 'SPIKE'
                       and t['_is_maker'] == (entry_type == 'MAKER')]
            if not spikes:
                continue
            w = len([t for t in spikes if t['_wl'] == 'W'])
            l = len([t for t in spikes if t['_wl'] == 'L'])
            p = len([t for t in spikes if t['_wl'] == 'P'])
            settled = w + l
            wr = w / settled * 100 if settled else 0
            total_pnl = sum(t['_pnl'] for t in spikes)
            print(f"  {sport:<10s} {entry_type:<7s} {len(spikes):>6d} {w:>4d} {l:>4d} {p:>4d}  {wr:>6.1f}% {total_pnl:>+9d}c ${total_pnl/100/5:>7.2f}")

    # ─── SECTION 4: All losses ───
    print()
    print("=" * 80)
    print("SECTION 4: ALL LOSSES (CORRECTED)")
    print("=" * 80)

    losses = [t for t in trades if t['_wl'] == 'L']
    stb_losses = [t for t in losses if not t['_is_maker']]
    maker_losses = [t for t in losses if t['_is_maker']]

    print(f"\n  Total losses: {len(losses)} (STB: {len(stb_losses)}, Maker: {len(maker_losses)})")

    if stb_losses:
        print(f"\n  STB LOSSES ({len(stb_losses)}):")
        for t in sorted(stb_losses, key=lambda x: x['_pnl']):
            ct = t.get('_ct', '?')
            print(f"    {t['_sport']:>8s}  {t['_side']:<6s}  entry={t['_entry']:>3d}c  spike={t['_spike']:+d}c  "
                  f"cls={t['_cls']:<5s}  pnl={t['_pnl']:+d}c  ct={ct}")

    if maker_losses:
        print(f"\n  MAKER LOSSES ({len(maker_losses)}):")
        for t in sorted(maker_losses, key=lambda x: x['_pnl']):
            ct = t.get('_ct', '?')
            print(f"    {t['_sport']:>8s}  {t['_side']:<6s}  entry={t['_entry']:>3d}c  spike={t['_spike']:+d}c  "
                  f"cls={t['_cls']:<5s}  pnl={t['_pnl']:+d}c  ct={ct}")

    # ─── SECTION 5: Does this change Scenario B? ───
    print()
    print("=" * 80)
    print("SECTION 5: SCENARIO B REASSESSMENT")
    print("=" * 80)

    stb_spike_losses = [t for t in stb_losses if t['_cls'] == 'SPIKE']
    maker_spike_losses = [t for t in maker_losses if t['_cls'] == 'SPIKE']
    stb_nonspike_losses = [t for t in stb_losses if t['_cls'] != 'SPIKE']
    maker_nonspike_losses = [t for t in maker_losses if t['_cls'] != 'SPIKE']

    print(f"\n  STB spike losses: {len(stb_spike_losses)} | PnL={sum(t['_pnl'] for t in stb_spike_losses):+d}c")
    for t in stb_spike_losses:
        print(f"    {t['_sport']:>8s}  {t['_side']:<6s}  entry={t['_entry']}c  spike={t['_spike']:+d}c  pnl={t['_pnl']:+d}c")

    print(f"\n  STB non-spike losses: {len(stb_nonspike_losses)} | PnL={sum(t['_pnl'] for t in stb_nonspike_losses):+d}c")
    for t in stb_nonspike_losses:
        print(f"    {t['_sport']:>8s}  {t['_side']:<6s}  entry={t['_entry']}c  spike={t['_spike']:+d}c  cls={t['_cls']}  pnl={t['_pnl']:+d}c")

    print(f"\n  Maker spike losses: {len(maker_spike_losses)} | PnL={sum(t['_pnl'] for t in maker_spike_losses):+d}c")
    for t in maker_spike_losses:
        print(f"    {t['_sport']:>8s}  {t['_side']:<6s}  entry={t['_entry']}c  spike={t['_spike']:+d}c  pnl={t['_pnl']:+d}c")

    # STB spike gate simulation
    all_stb_spikes = [t for t in trades if not t['_is_maker'] and t['_cls'] == 'SPIKE']
    print(f"\n  STB SPIKE GATE SIMULATION ({len(all_stb_spikes)} spike trades):")
    for threshold in [5, 10, 15, 20]:
        blocked = [t for t in all_stb_spikes if t['_spike'] > threshold]
        bl = [t for t in blocked if t['_wl'] == 'L']
        bw = [t for t in blocked if t['_wl'] == 'W']
        bp = [t for t in blocked if t['_wl'] == 'P']
        saved = abs(sum(t['_pnl'] for t in bl))
        lost = sum(t['_pnl'] for t in bw)
        net = saved - lost
        print(f"    spike>{threshold:>2d}c: block {len(bl)}L + {len(bw)}W + {len(bp)}P "
              f"| save {saved}c - lose {lost}c = net {net:+d}c")

    # Per-sport breakdown
    print(f"\n  Per-sport STB spike profile:")
    for sport in sports:
        sp = [t for t in all_stb_spikes if t['_sport'] == sport]
        if not sp:
            continue
        w = len([t for t in sp if t['_wl'] == 'W'])
        l = len([t for t in sp if t['_wl'] == 'L'])
        p = len([t for t in sp if t['_wl'] == 'P'])
        pnl = sum(t['_pnl'] for t in sp)
        settled = w + l
        wr = w / settled * 100 if settled else 0
        print(f"    {sport:>8s}: {len(sp):>3d} spikes | {w}W {l}L {p}P | WR={wr:.1f}% | PnL={pnl:+d}c")
        if l > 0:
            for t in [t for t in sp if t['_wl'] == 'L']:
                print(f"              LOSS: {t['_side']} entry={t['_entry']}c spike={t['_spike']:+d}c pnl={t['_pnl']:+d}c")

    # ─── Corrected totals ───
    print()
    print("=" * 80)
    print("CORRECTED TOTALS")
    print("=" * 80)

    all_w = len([t for t in trades if t['_wl'] == 'W'])
    all_l = len([t for t in trades if t['_wl'] == 'L'])
    all_p = len([t for t in trades if t['_wl'] == 'P'])
    total_pnl = sum(t['_pnl'] for t in trades)
    settled = all_w + all_l
    wr = all_w / settled * 100 if settled else 0

    print(f"\n  All trades: {len(trades)} | {all_w}W {all_l}L {all_p}P | WR={wr:.1f}% | PnL={total_pnl:+d}c (${total_pnl/100:.2f})")
    print(f"  PnL/day: ${total_pnl/100/5:.2f}")

    loss_total = sum(t['_pnl'] for t in losses)
    print(f"  Total losses: {len(losses)} | {loss_total:+d}c (${loss_total/100:.2f})")
    print(f"  Loss/day: ${loss_total/100/5:.2f}")

asyncio.run(main())
