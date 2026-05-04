#!/usr/bin/env python3
"""Pull REAL P&L from Kalshi API — every settlement Mar 11-15.
No CSV. Only Kalshi truth.
"""
import asyncio, aiohttp, sys, json
from datetime import datetime, timezone
sys.path.insert(0, '/root/Omi-Workspace/arb-executor')
from ncaamb_stb import api_get, load_credentials

async def main():
    api_key, private_key = load_credentials()
    class RL:
        async def acquire(self): pass
    rl = RL()

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

        # Pull ALL fills (paginate)
        all_fills = []
        cursor = None
        while True:
            url = '/trade-api/v2/portfolio/fills?limit=1000'
            if cursor:
                url += f'&cursor={cursor}'
            resp = await api_get(s, api_key, private_key, url, rl)
            if not resp:
                break
            batch = resp.get('fills', [])
            all_fills.extend(batch)
            cursor = resp.get('cursor')
            if not cursor or not batch:
                break

        # Get current positions
        pos_resp = await api_get(s, api_key, private_key,
            '/trade-api/v2/portfolio/positions?count_filter=position&limit=200', rl)
        open_positions = {}
        if pos_resp:
            for p in pos_resp.get('market_positions', []):
                ct = p.get('position', 0)
                if ct > 0:
                    open_positions[p.get('ticker', '')] = ct

    print(f"Total settlements: {len(all_settlements)}")
    print(f"Total fills: {len(all_fills)}")
    print(f"Open positions: {len(open_positions)}")

    # Build fill map
    fill_map = {}
    for f in all_fills:
        t = f.get('ticker', '')
        fill_map.setdefault(t, []).append(f)

    # ════════════════════════════════════════════════════════════════
    # SECTION 1: EVERY SETTLEMENT Mar 11-15 — sorted by sport
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 100)
    print("SECTION 1: EVERY KALSHI SETTLEMENT — Mar 11-15, 2026")
    print("=" * 100)

    # Filter to Mar 11-15
    mar_settlements = []
    for st in all_settlements:
        ts = st.get('settled_time', '')
        if ts and ts.startswith('2026-03-1'):
            day = int(ts[8:10])
            if 11 <= day <= 15:
                mar_settlements.append(st)

    # Detect sport from ticker
    def detect_sport(ticker):
        t = ticker.upper()
        if 'NCAAMB' in t or 'NCAA' in t:
            return 'ncaamb'
        elif 'NBA' in t:
            return 'nba'
        elif 'NHL' in t:
            return 'nhl'
        elif 'ATP' in t or 'WTA' in t or 'CHALLENGER' in t or 'MATCH' in t:
            return 'tennis'
        else:
            return 'other'

    # Detect entry type from fills
    def detect_entry_type(ticker, fills_for_ticker):
        buys = [f for f in fills_for_ticker if f.get('action') == 'buy']
        if not buys:
            return 'unknown', 0, 0
        total_ct = sum(f.get('count', 0) for f in buys)
        total_cost = sum(f.get('count', 0) * f.get('yes_price', 0) for f in buys)
        avg_price = total_cost / total_ct if total_ct > 0 else 0
        entry_type = 'MAKER' if avg_price >= 88 else 'STB'
        return entry_type, total_ct, avg_price

    # Compute P&L from settlement
    # yes_total_cost = what you paid for YES contracts still held
    # If settled YES: you get 100 * yes_count, profit = 100*ct - yes_total_cost
    # If settled NO: you get 0, loss = -yes_total_cost
    # But also check: did you sell some before settlement?

    sport_trades = {'ncaamb': [], 'nba': [], 'nhl': [], 'tennis': [], 'other': []}

    for st in mar_settlements:
        ticker = st.get('ticker', '')
        side = ticker.rsplit('-', 1)[-1]
        sport = detect_sport(ticker)
        result = st.get('market_result', '')
        yes_ct = float(st.get('yes_count_fp', '0') or '0')
        yes_cost = int(st.get('yes_total_cost', 0) or 0)
        no_ct = float(st.get('no_count_fp', '0') or '0')
        no_cost = int(st.get('no_total_cost', 0) or 0)
        settled_time = st.get('settled_time', '')[:19]
        fee = float(st.get('fee_cost', '0') or '0')

        # Settlement P&L (what Kalshi actually credited/debited)
        if result == 'yes' and yes_ct > 0:
            pnl = int(100 * yes_ct) - yes_cost
            held_ct = int(yes_ct)
            held_side = 'YES'
        elif result == 'no' and yes_ct > 0:
            pnl = -yes_cost
            held_ct = int(yes_ct)
            held_side = 'YES'
        elif result == 'no' and no_ct > 0:
            pnl = int(100 * no_ct) - no_cost
            held_ct = int(no_ct)
            held_side = 'NO'
        elif result == 'yes' and no_ct > 0:
            pnl = -no_cost
            held_ct = int(no_ct)
            held_side = 'NO'
        else:
            pnl = 0
            held_ct = 0
            held_side = '?'

        # Also check fills for pre-settlement sells
        ticker_fills = fill_map.get(ticker, [])
        sell_fills = [f for f in ticker_fills if f.get('action') == 'sell']
        sell_ct = sum(f.get('count', 0) for f in sell_fills)
        sell_rev = sum(f.get('count', 0) * f.get('yes_price', 0) for f in sell_fills)

        buy_fills = [f for f in ticker_fills if f.get('action') == 'buy']
        buy_ct = sum(f.get('count', 0) for f in buy_fills)
        buy_cost_total = sum(f.get('count', 0) * f.get('yes_price', 0) for f in buy_fills)
        avg_entry = buy_cost_total / buy_ct if buy_ct > 0 else 0

        # Total P&L = sold_pnl + settlement_pnl
        sold_pnl = sell_rev - int(avg_entry * sell_ct) if sell_ct > 0 and buy_ct > 0 else 0
        total_pnl = pnl + sold_pnl

        entry_type = 'MAKER' if avg_entry >= 88 else 'STB'
        wl = 'W' if total_pnl > 0 else ('L' if total_pnl < 0 else 'BE')

        trade = {
            'ticker': ticker,
            'side': side,
            'sport': sport,
            'result': result,
            'held_ct': held_ct,
            'held_side': held_side,
            'yes_cost': yes_cost,
            'settlement_pnl': pnl,
            'sold_ct': sell_ct,
            'sold_pnl': sold_pnl,
            'total_pnl': total_pnl,
            'buy_ct': buy_ct,
            'avg_entry': avg_entry,
            'entry_type': entry_type,
            'settled_time': settled_time,
            'wl': wl,
            'fee': fee,
        }
        sport_trades[sport].append(trade)

    # Print per sport
    for sport in ['ncaamb', 'nba', 'nhl', 'tennis']:
        trades_s = sorted(sport_trades[sport], key=lambda x: x['settled_time'])
        if not trades_s:
            continue

        w = len([t for t in trades_s if t['wl'] == 'W'])
        l = len([t for t in trades_s if t['wl'] == 'L'])
        total = sum(t['total_pnl'] for t in trades_s)
        fees = sum(t['fee'] for t in trades_s)

        print(f"\n  {'─'*96}")
        print(f"  {sport.upper()} — {len(trades_s)} settlements | {w}W {l}L | "
              f"PnL={total:+d}c (${total/100:.2f}) | Fees=${fees:.2f}")
        print(f"  {'─'*96}")
        print(f"  {'Side':<6s} {'Type':>5s} {'Entry':>5s} {'Ct':>4s} {'Result':>6s} "
              f"{'HeldCt':>6s} {'SettlePnL':>9s} {'SoldCt':>6s} {'SoldPnL':>8s} "
              f"{'TotalPnL':>9s} {'W/L':>3s} {'Date':>11s}")

        for t in trades_s:
            print(f"  {t['side']:<6s} {t['entry_type']:>5s} {t['avg_entry']:>4.0f}c {t['buy_ct']:>4d} "
                  f"{t['result']:>6s} {t['held_ct']:>6d} {t['settlement_pnl']:>+8d}c "
                  f"{t['sold_ct']:>6d} {t['sold_pnl']:>+7d}c {t['total_pnl']:>+8d}c "
                  f"{t['wl']:>3s} {t['settled_time'][5:16]:>11s}")

    # ════════════════════════════════════════════════════════════════
    # SECTION 2: NCAAMB STB — ONLY LOSSES
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 100)
    print("SECTION 2: NCAAMB LOSSES — REAL KALSHI DATA")
    print("=" * 100)

    ncaamb_losses = [t for t in sport_trades['ncaamb'] if t['wl'] == 'L']
    ncaamb_stb_losses = [t for t in ncaamb_losses if t['entry_type'] == 'STB']
    ncaamb_maker_losses = [t for t in ncaamb_losses if t['entry_type'] == 'MAKER']

    print(f"\n  Total NCAAMB losses: {len(ncaamb_losses)}")
    print(f"  STB losses: {len(ncaamb_stb_losses)} | Maker losses: {len(ncaamb_maker_losses)}")

    if ncaamb_stb_losses:
        print(f"\n  STB LOSSES:")
        for t in ncaamb_stb_losses:
            print(f"    {t['side']:<6s} entry={t['avg_entry']:.0f}c ct={t['buy_ct']} "
                  f"held={t['held_ct']}ct result={t['result']} "
                  f"pnl={t['total_pnl']:+d}c  {t['settled_time'][:10]}")

    if ncaamb_maker_losses:
        print(f"\n  MAKER LOSSES:")
        for t in ncaamb_maker_losses:
            print(f"    {t['side']:<6s} entry={t['avg_entry']:.0f}c ct={t['buy_ct']} "
                  f"held={t['held_ct']}ct result={t['result']} "
                  f"pnl={t['total_pnl']:+d}c  {t['settled_time'][:10]}")

    # ════════════════════════════════════════════════════════════════
    # SECTION 3: COR (Corwin) AUTOPSY
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 100)
    print("SECTION 3: CORWIN (COR) — FULL AUTOPSY")
    print("=" * 100)

    cor_ticker = None
    for ticker in fill_map:
        if 'COR' in ticker.upper() and 'MAR15' in ticker:
            cor_ticker = ticker
            break

    if not cor_ticker:
        # Check settlements
        for st in all_settlements:
            if 'COR' in st.get('ticker', '').upper() and 'MAR15' in st.get('ticker', ''):
                cor_ticker = st['ticker']
                break

    if cor_ticker:
        print(f"\n  Ticker: {cor_ticker}")
        side = cor_ticker.rsplit('-', 1)[-1]

        # Fills
        cor_fills = fill_map.get(cor_ticker, [])
        print(f"  Fills ({len(cor_fills)}):")
        for f in cor_fills:
            print(f"    {f.get('created_time', '?')[:19]}  {f.get('action', '?'):>4s}  "
                  f"{f.get('count', 0)}ct @ {f.get('yes_price', 0)}c")

        # Settlement
        cor_settle = None
        for st in all_settlements:
            if st.get('ticker', '') == cor_ticker:
                cor_settle = st
                break
        if cor_settle:
            print(f"  Settlement: result={cor_settle.get('market_result')} "
                  f"yes_ct={cor_settle.get('yes_count_fp')} "
                  f"yes_cost={cor_settle.get('yes_total_cost')} "
                  f"fee={cor_settle.get('fee_cost')}")
        else:
            print(f"  Settlement: NOT YET SETTLED")

        # Check if still open
        if cor_ticker in open_positions:
            print(f"  Status: STILL OPEN ({open_positions[cor_ticker]}ct)")
    else:
        print(f"  Could not find COR ticker for Mar 15")
        # Try broader search
        for ticker in list(fill_map.keys()) + [st.get('ticker', '') for st in all_settlements]:
            if 'VANCOR' in ticker.upper():
                print(f"  Found: {ticker}")

    # ════════════════════════════════════════════════════════════════
    # SECTION 4: CURRENT OPEN POSITIONS
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 100)
    print("SECTION 4: CURRENT OPEN POSITIONS + RECENT LOSSES")
    print("=" * 100)

    print(f"\n  Open positions ({len(open_positions)}):")
    for ticker, ct in open_positions.items():
        side = ticker.rsplit('-', 1)[-1]
        sport = detect_sport(ticker)
        # Get entry price from fills
        buys = [f for f in fill_map.get(ticker, []) if f.get('action') == 'buy']
        total_ct = sum(f.get('count', 0) for f in buys)
        total_cost = sum(f.get('count', 0) * f.get('yes_price', 0) for f in buys)
        avg = total_cost / total_ct if total_ct > 0 else 0
        print(f"    {sport:>8s}  {side:<6s}  {ct}ct  entry~{avg:.0f}c  {ticker}")

    # Most recent settlements (last 10)
    recent = sorted(all_settlements, key=lambda x: x.get('settled_time', ''), reverse=True)[:15]
    print(f"\n  Last 15 settlements:")
    for st in recent:
        ticker = st.get('ticker', '')
        side = ticker.rsplit('-', 1)[-1]
        sport = detect_sport(ticker)
        result = st.get('market_result', '')
        yes_ct = float(st.get('yes_count_fp', '0') or '0')
        yes_cost = int(st.get('yes_total_cost', 0) or 0)

        if result == 'yes' and yes_ct > 0:
            pnl = int(100 * yes_ct) - yes_cost
        elif result == 'no' and yes_ct > 0:
            pnl = -yes_cost
        else:
            no_ct = float(st.get('no_count_fp', '0') or '0')
            no_cost = int(st.get('no_total_cost', 0) or 0)
            if result == 'no' and no_ct > 0:
                pnl = int(100 * no_ct) - no_cost
            elif result == 'yes' and no_ct > 0:
                pnl = -no_cost
            else:
                pnl = 0

        wl = 'W' if pnl > 0 else ('L' if pnl < 0 else 'BE')
        ts = st.get('settled_time', '')[:19]
        print(f"    {ts}  {sport:>8s}  {side:<6s}  result={result:>3s}  "
              f"held={int(yes_ct)}ct  cost={yes_cost}c  pnl={pnl:>+6d}c  {wl}")

    # ════════════════════════════════════════════════════════════════
    # SECTION 5: GRAND TOTALS FROM KALSHI API
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 100)
    print("SECTION 5: GRAND TOTALS — KALSHI API TRUTH")
    print("=" * 100)

    for sport in ['ncaamb', 'nba', 'nhl', 'tennis']:
        all_t = sport_trades[sport]
        stb = [t for t in all_t if t['entry_type'] == 'STB']
        maker = [t for t in all_t if t['entry_type'] == 'MAKER']

        stb_w = len([t for t in stb if t['wl'] == 'W'])
        stb_l = len([t for t in stb if t['wl'] == 'L'])
        stb_pnl = sum(t['total_pnl'] for t in stb)

        maker_w = len([t for t in maker if t['wl'] == 'W'])
        maker_l = len([t for t in maker if t['wl'] == 'L'])
        maker_pnl = sum(t['total_pnl'] for t in maker)

        print(f"\n  {sport.upper()}")
        print(f"    STB:   {len(stb):>3d} trades | {stb_w}W {stb_l}L | "
              f"WR={stb_w/(stb_w+stb_l)*100 if (stb_w+stb_l) else 0:.1f}% | "
              f"PnL={stb_pnl:+d}c (${stb_pnl/100:.2f}) | $/day=${stb_pnl/100/5:.2f}")
        print(f"    MAKER: {len(maker):>3d} trades | {maker_w}W {maker_l}L | "
              f"WR={maker_w/(maker_w+maker_l)*100 if (maker_w+maker_l) else 0:.1f}% | "
              f"PnL={maker_pnl:+d}c (${maker_pnl/100:.2f}) | $/day=${maker_pnl/100/5:.2f}")

    grand_total = sum(t['total_pnl'] for sport in sport_trades.values() for t in sport)
    grand_w = sum(1 for sport in sport_trades.values() for t in sport if t['wl'] == 'W')
    grand_l = sum(1 for sport in sport_trades.values() for t in sport if t['wl'] == 'L')
    grand_fees = sum(t['fee'] for sport in sport_trades.values() for t in sport)

    print(f"\n  GRAND TOTAL: {grand_w}W {grand_l}L | WR={grand_w/(grand_w+grand_l)*100:.1f}% | "
          f"PnL={grand_total:+d}c (${grand_total/100:.2f}) | $/day=${grand_total/100/5:.2f}")
    print(f"  Fees: ${grand_fees:.2f}")

asyncio.run(main())
