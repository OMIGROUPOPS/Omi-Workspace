#!/usr/bin/env python3
"""Corrected sport-specific spike analysis.

Problem: 37 trades have empty pnl_cents in CSV — they were unsettled when
the CSV was generated. Many have since settled as LOSSES but the analysis
treated them as pnl=0 ("pending"). This systematically hides losses.

Fix: For trades with empty pnl, compute pnl from settlement:
  - If the market settled, pnl = -(entry_price * contracts) for NO settlement
  - Pull actual settlement from Kalshi API
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

    # Find trades with missing pnl
    missing_pnl = []
    for i, t in enumerate(trades):
        pnl = (t.get("pnl_cents", "") or "").strip()
        if pnl == "" or pnl == "nan":
            missing_pnl.append(i)

    print(f"Trades with missing pnl: {len(missing_pnl)}")
    print()

    # For each missing trade, check if it settled
    async with aiohttp.ClientSession() as s:
        # Get all fills to find actual contract counts and settlement
        fills_resp = await api_get(s, api_key, private_key,
            '/trade-api/v2/portfolio/fills?limit=1000', rl)
        fills = fills_resp.get('fills', []) if fills_resp else []

        # Build fill map: ticker -> list of fills
        fill_map = {}
        for f in fills:
            t = f.get('ticker', '')
            fill_map.setdefault(t, []).append(f)

        # Get settlements
        settlements_resp = await api_get(s, api_key, private_key,
            '/trade-api/v2/portfolio/settlements?limit=500', rl)
        settlements = settlements_resp.get('settlements', []) if settlements_resp else []

        # Build settlement map: ticker -> settlement
        settle_map = {}
        for st in settlements:
            t = st.get('ticker', '')
            settle_map[t] = st

        print(f"Fills loaded: {len(fills)}")
        print(f"Settlements loaded: {len(settlements)}")
        print()

        # Also get positions to check what's still open
        pos_resp = await api_get(s, api_key, private_key,
            '/trade-api/v2/portfolio/positions?count_filter=position&limit=200', rl)
        open_tickers = set()
        if pos_resp:
            for p in pos_resp.get('market_positions', []):
                ct = p.get('position', 0)
                if ct > 0:
                    open_tickers.add(p.get('ticker', ''))

    print("=" * 80)
    print("SECTION 1: ALL 37 MISSING-PNL TRADES — RESOLVED STATUS")
    print("=" * 80)

    resolved = 0
    still_open = 0

    for idx in missing_pnl:
        t = trades[idx]
        ticker = t.get('ticker', '')
        side = t.get('entry_side', '?')
        entry = int(float(t.get('entry_price', 0) or 0))
        sport = t.get('sport', '?')
        mode = t.get('entry_mode', '')
        ts = t.get('timestamp', '')[:16]

        # Check settlement
        sdata = settle_map.get(ticker)
        is_open = ticker in open_tickers

        if sdata:
            # Settled — compute actual pnl
            settled_yes = sdata.get('yes_settlement', False)
            revenue = sdata.get('revenue', 0)  # in cents
            # Revenue is what you got back. pnl = revenue - cost
            # For buy-yes: cost = entry_price * contracts
            # But we don't know contracts from CSV. Use revenue directly.
            # If settled YES and you bought YES: revenue = 100 * contracts, pnl = (100 - entry) * contracts
            # If settled NO and you bought YES: revenue = 0, pnl = -entry * contracts

            # Get contract count from fills
            ticker_fills = [f for f in fill_map.get(ticker, []) if f.get('action') == 'buy']
            total_ct = sum(f.get('count', 0) for f in ticker_fills)
            avg_price = sum(f.get('yes_price', 0) * f.get('count', 0) for f in ticker_fills) / max(total_ct, 1) if total_ct > 0 else entry

            if settled_yes:
                pnl = int((100 - avg_price) * total_ct)
                wl = "W" if pnl > 0 else "L"
            else:
                pnl = int(-avg_price * total_ct)
                wl = "L"

            t['pnl_cents'] = str(pnl)
            resolved += 1
            status = f"SETTLED {'YES' if settled_yes else 'NO'} → pnl={pnl:+d}c ({wl}) ct={total_ct} avg={avg_price:.0f}c"
        elif is_open:
            still_open += 1
            status = "STILL OPEN"
            # Check sell fills
            sell_fills = [f for f in fill_map.get(ticker, []) if f.get('action') == 'sell']
            if sell_fills:
                sell_ct = sum(f.get('count', 0) for f in sell_fills)
                sell_avg = sum(f.get('yes_price', 0) * f.get('count', 0) for f in sell_fills) / max(sell_ct, 1)
                buy_fills = [f for f in fill_map.get(ticker, []) if f.get('action') == 'buy']
                buy_ct = sum(f.get('count', 0) for f in buy_fills)
                buy_avg = sum(f.get('yes_price', 0) * f.get('count', 0) for f in buy_fills) / max(buy_ct, 1)
                pnl = int((sell_avg - buy_avg) * min(buy_ct, sell_ct))
                t['pnl_cents'] = str(pnl)
                status += f" (sold {sell_ct}ct@{sell_avg:.0f}c, pnl~{pnl:+d}c)"
        else:
            # Not settled, not open — might have been sold
            sell_fills = [f for f in fill_map.get(ticker, []) if f.get('action') == 'sell']
            buy_fills = [f for f in fill_map.get(ticker, []) if f.get('action') == 'buy']
            if sell_fills:
                sell_ct = sum(f.get('count', 0) for f in sell_fills)
                sell_rev = sum(f.get('yes_price', 0) * f.get('count', 0) for f in sell_fills)
                buy_ct = sum(f.get('count', 0) for f in buy_fills)
                buy_cost = sum(f.get('yes_price', 0) * f.get('count', 0) for f in buy_fills)
                pnl = int(sell_rev - buy_cost) if buy_ct > 0 else 0
                t['pnl_cents'] = str(pnl)
                resolved += 1
                status = f"SOLD ct={sell_ct} pnl={pnl:+d}c"
            else:
                status = "UNKNOWN (no settlement, no position, no sells)"
                # Assume settled NO = full loss
                buy_fills_t = [f for f in fill_map.get(ticker, []) if f.get('action') == 'buy']
                total_ct = sum(f.get('count', 0) for f in buy_fills_t)
                if total_ct > 0:
                    avg_price = sum(f.get('yes_price', 0) * f.get('count', 0) for f in buy_fills_t) / total_ct
                    pnl = int(-avg_price * total_ct)
                    t['pnl_cents'] = str(pnl)
                    status += f" → assuming loss: {pnl:+d}c (ct={total_ct} avg={avg_price:.0f}c)"

        is_maker = entry >= 88 or 'maker' in (mode or '') or '92' in (mode or '')
        print(f"  {ts}  {sport:>8s}  {side:<6s}  entry={entry:>3d}c  {'MAKER' if is_maker else 'STB':>5s}  {status}")

    print(f"\n  Resolved: {resolved} | Still open: {still_open} | Unknown: {len(missing_pnl) - resolved - still_open}")

    # ─── SECTION 2: The 5 specific losses ───
    print()
    print("=" * 80)
    print("SECTION 2: THE 5 CONFIRMED LOSSES — DETAIL")
    print("=" * 80)

    target_sides = ['YUZ', 'UTU', 'BON', 'ROD', 'GOJ']
    for t in trades:
        side = t.get('entry_side', '')
        if side not in target_sides:
            continue
        entry = int(float(t.get('entry_price', 0) or 0))
        pnl_raw = (t.get('pnl_cents', '') or '').strip()
        pnl = int(float(pnl_raw)) if pnl_raw and pnl_raw != 'nan' else 0
        sport = t.get('sport', '?')
        mode = t.get('entry_mode', '')
        pre10m = t.get('pre_entry_price_10m', '')
        fsp = t.get('first_seen_price', '')

        # Compute spike
        if pre10m and pre10m not in ('', 'nan'):
            try:
                fsp_val = int(float(pre10m))
            except:
                fsp_val = 50
        else:
            fsp_val = 50

        spike = entry - fsp_val
        cls = "SPIKE" if spike > 2 else ("DIP" if spike < -2 else "FLAT")
        is_maker = entry >= 88 or 'maker' in (mode or '') or '92' in (mode or '')
        wl = "W" if pnl > 0 else ("L" if pnl < 0 else "P")

        print(f"  {side:<6s} {sport:>8s}  entry={entry:>3d}c  fsp={fsp_val:>3d}c  spike={spike:+d}c  "
              f"cls={cls:<5s}  {'MAKER' if is_maker else 'STB':>5s}  "
              f"pnl={pnl:+d}c  wl={wl}  pre10m=[{pre10m}]  mode=[{mode}]")

    # ─── SECTION 3: Corrected sport breakdown ───
    print()
    print("=" * 80)
    print("SECTION 3: CORRECTED SPORT-SPECIFIC SPIKE ANALYSIS")
    print("=" * 80)

    # Reprocess all trades with corrected pnl
    for t in trades:
        entry = int(float(t.get('entry_price', 0) or 0))
        pnl_raw = (t.get('pnl_cents', '') or '').strip()
        pnl = int(float(pnl_raw)) if pnl_raw and pnl_raw != 'nan' else 0
        sport = t.get('sport', '?')
        mode = t.get('entry_mode', '')

        pre10m = t.get('pre_entry_price_10m', '')
        if pre10m and pre10m not in ('', 'nan'):
            try:
                fsp_val = int(float(pre10m))
            except:
                fsp_val = 50
        else:
            fsp_val = 50

        spike = entry - fsp_val
        is_maker = entry >= 88 or 'maker' in (mode or '') or '92' in (mode or '')

        t['_entry'] = entry
        t['_pnl'] = pnl
        t['_spike'] = spike
        t['_cls'] = "SPIKE" if spike > 2 else ("DIP" if spike < -2 else "FLAT")
        t['_is_maker'] = is_maker
        t['_sport'] = sport
        t['_wl'] = "W" if pnl > 0 else ("L" if pnl < 0 else "P")

    sports = sorted(set(t['_sport'] for t in trades))

    print(f"\n  {'Sport':<10s} {'Type':<7s} {'Spikes':>7s} {'W':>4s} {'L':>4s} {'P':>4s} {'WR%':>7s} {'PnL':>10s} {'$/day':>8s}")
    print(f"  {'─'*10} {'─'*7} {'─'*7} {'─'*4} {'─'*4} {'─'*4} {'─'*7} {'─'*10} {'─'*8}")

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
            print(f"  {sport:<10s} {entry_type:<7s} {len(spikes):>7d} {w:>4d} {l:>4d} {p:>4d} {wr:>6.1f}% {total_pnl:>+9d}c ${total_pnl/100/5:>7.2f}")

    # ─── SECTION 4: All losses with spike profile ───
    print()
    print("=" * 80)
    print("SECTION 4: ALL LOSSES (CORRECTED) — SPIKE PROFILE")
    print("=" * 80)

    losses = [t for t in trades if t['_wl'] == 'L']
    stb_losses = [t for t in losses if not t['_is_maker']]
    maker_losses = [t for t in losses if t['_is_maker']]

    print(f"\n  Total losses: {len(losses)} (STB: {len(stb_losses)}, Maker: {len(maker_losses)})")

    print(f"\n  STB LOSSES:")
    for t in sorted(stb_losses, key=lambda x: x['_pnl']):
        side = t.get('entry_side', '?')
        print(f"    {t['_sport']:>8s}  {side:<6s}  entry={t['_entry']:>3d}c  spike={t['_spike']:+d}c  "
              f"cls={t['_cls']:<5s}  pnl={t['_pnl']:+d}c")

    print(f"\n  MAKER LOSSES:")
    for t in sorted(maker_losses, key=lambda x: x['_pnl']):
        side = t.get('entry_side', '?')
        print(f"    {t['_sport']:>8s}  {side:<6s}  entry={t['_entry']:>3d}c  spike={t['_spike']:+d}c  "
              f"cls={t['_cls']:<5s}  pnl={t['_pnl']:+d}c")

    # ─── SECTION 5: Does this change Scenario B? ───
    print()
    print("=" * 80)
    print("SECTION 5: DOES THIS CHANGE SCENARIO B?")
    print("=" * 80)

    stb_spike_losses = [t for t in stb_losses if t['_cls'] == 'SPIKE']
    maker_spike_losses = [t for t in maker_losses if t['_cls'] == 'SPIKE']

    stb_spike_loss_total = sum(t['_pnl'] for t in stb_spike_losses)
    maker_spike_loss_total = sum(t['_pnl'] for t in maker_spike_losses)

    print(f"\n  STB spike losses: {len(stb_spike_losses)} totaling {stb_spike_loss_total:+d}c (${stb_spike_loss_total/100:.2f})")
    for t in stb_spike_losses:
        side = t.get('entry_side', '?')
        print(f"    {t['_sport']:>8s}  {side:<6s}  entry={t['_entry']}c  spike={t['_spike']:+d}c  pnl={t['_pnl']:+d}c")

    print(f"\n  Maker spike losses: {len(maker_spike_losses)} totaling {maker_spike_loss_total:+d}c (${maker_spike_loss_total/100:.2f})")
    for t in maker_spike_losses:
        side = t.get('entry_side', '?')
        print(f"    {t['_sport']:>8s}  {side:<6s}  entry={t['_entry']}c  spike={t['_spike']:+d}c  pnl={t['_pnl']:+d}c")

    # Simulate STB spike gate thresholds
    all_stb_spikes = [t for t in trades if not t['_is_maker'] and t['_cls'] == 'SPIKE']
    print(f"\n  STB spike gate simulation (total STB spikes: {len(all_stb_spikes)}):")
    for threshold in [5, 10, 15, 20, 25]:
        blocked = [t for t in all_stb_spikes if t['_spike'] > threshold]
        blocked_l = [t for t in blocked if t['_wl'] == 'L']
        blocked_w = [t for t in blocked if t['_wl'] == 'W']
        blocked_p = [t for t in blocked if t['_wl'] == 'P']
        saved = abs(sum(t['_pnl'] for t in blocked_l))
        lost = sum(t['_pnl'] for t in blocked_w) + sum(t['_pnl'] for t in blocked_p)
        net = saved - lost
        print(f"    gate spike>{threshold:>2d}c: block {len(blocked_l)}L + {len(blocked_w)}W + {len(blocked_p)}P = "
              f"{len(blocked)} total | save {saved}c - lose {lost}c = net {net:+d}c (${net/100:.2f})")

    # Also per-sport STB spike gate
    print(f"\n  Per-sport STB spike losses:")
    for sport in sports:
        sport_stb_spike_l = [t for t in stb_spike_losses if t['_sport'] == sport]
        sport_stb_spikes = [t for t in all_stb_spikes if t['_sport'] == sport]
        if sport_stb_spikes:
            stb_w = len([t for t in sport_stb_spikes if t['_wl'] == 'W'])
            stb_l = len([t for t in sport_stb_spikes if t['_wl'] == 'L'])
            stb_pnl = sum(t['_pnl'] for t in sport_stb_spikes)
            settled = stb_w + stb_l
            wr = stb_w / settled * 100 if settled else 0
            print(f"    {sport:>8s}: {len(sport_stb_spikes)} spikes | {stb_w}W {stb_l}L | WR={wr:.1f}% | PnL={stb_pnl:+d}c")

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

asyncio.run(main())
