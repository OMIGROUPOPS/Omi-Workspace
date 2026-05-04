#!/usr/bin/env python3
"""For each of the 28 NCAAMB losses, determine if current config would have blocked it.

Current config (as of Mar 15 evening):
- Bounce chain v2: 3 signals (stable, tight, wall), tier = chain * 8
- Detection fixes: stable sparse data fix, wall threshold 0.7
- Game state: reject scheduled/not_started, reject 15+pt deficit in 2H, <3min clock, ended
- Scenario B: STB spike gate REMOVED, maker spike gate at C-tier + spike>10c
- first_seen_prices: set BEFORE volume gate
- 35ct sizing
- Premarket fix: 92+ maker path now checks game state

We also need to know WHEN each loss trade was entered — what version of the code was running.

Key config changes during Mar 11-15:
- Mar 11-12: OLD config (5-signal chain, no detection fixes, first_seen bug in tennis)
- Mar 13 AM: bounce chain v2 deployed (3-signal)
- Mar 13 PM: detection fixes (stable sparse, wall 0.7)
- Mar 14: sizing 25ct->35ct, first_seen fix
- Mar 15: Scenario B spike gates, premarket fix

Strategy: Use settlement data for the 28 losses, cross-reference with CSV for
entry details (game state, entry price, etc), and determine which filters apply.
"""
import csv, asyncio, aiohttp, sys
from datetime import datetime
sys.path.insert(0, '/root/Omi-Workspace/arb-executor')
from ncaamb_stb import api_get, load_credentials

CSV = "/tmp/v3_enriched_trades.csv"

async def main():
    api_key, private_key = load_credentials()
    class RL:
        async def acquire(self): pass
    rl = RL()

    # Load CSV for entry details
    with open(CSV) as f:
        csv_trades = list(csv.DictReader(f))

    # Build CSV lookup by ticker
    csv_by_ticker = {}
    for t in csv_trades:
        ticker = t.get('ticker', '')
        csv_by_ticker[ticker] = t

    # Pull all settlements
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

    # Filter to NCAAMB losses Mar 11-15
    ncaamb_losses = []
    for st in all_settlements:
        ticker = st.get('ticker', '').upper()
        if 'NCAAMB' not in ticker and 'NCAA' not in ticker:
            # Also check NBA games misclassified
            if 'NBA' in ticker or 'NHL' in ticker or 'ATP' in ticker or 'WTA' in ticker or 'MATCH' in ticker or 'CHALLENGER' in ticker:
                continue
            # Unknown — skip if not ncaamb-like
            if 'NCAAMB' not in ticker:
                continue

        ts = st.get('settled_time', '')
        if not ts.startswith('2026-03-1'):
            continue
        day = int(ts[8:10])
        if day < 11 or day > 15:
            continue

        result = st.get('market_result', '')
        yes_ct = float(st.get('yes_count_fp', '0') or '0')
        yes_cost = int(st.get('yes_total_cost', 0) or 0)

        if result == 'no' and yes_ct > 0:
            pnl = -yes_cost
        elif result == 'yes' and yes_ct > 0:
            pnl = int(100 * yes_ct) - yes_cost
            if pnl >= 0:
                continue  # not a loss
        else:
            continue

        if pnl >= 0:
            continue

        side = st.get('ticker', '').rsplit('-', 1)[-1]
        ncaamb_losses.append({
            'ticker': st.get('ticker', ''),
            'side': side,
            'settled_time': ts,
            'result': result,
            'held_ct': int(yes_ct),
            'yes_cost': yes_cost,
            'pnl': pnl,
        })

    # Also get ALL ncaamb settlements for total count
    ncaamb_all = []
    for st in all_settlements:
        ticker = st.get('ticker', '').upper()
        if 'NCAAMB' not in ticker and 'NCAA' not in ticker:
            if 'NBA' in ticker or 'NHL' in ticker or 'ATP' in ticker or 'WTA' in ticker or 'MATCH' in ticker or 'CHALLENGER' in ticker:
                continue
            if 'NCAAMB' not in ticker:
                continue
        ts = st.get('settled_time', '')
        if not ts.startswith('2026-03-1'):
            continue
        day = int(ts[8:10])
        if day < 11 or day > 15:
            continue
        yes_ct = float(st.get('yes_count_fp', '0') or '0')
        yes_cost = int(st.get('yes_total_cost', 0) or 0)
        result = st.get('market_result', '')
        if result == 'yes' and yes_ct > 0:
            pnl = int(100 * yes_ct) - yes_cost
        elif result == 'no' and yes_ct > 0:
            pnl = -yes_cost
        else:
            pnl = 0
        ncaamb_all.append({
            'ticker': st.get('ticker', ''),
            'side': st.get('ticker', '').rsplit('-', 1)[-1],
            'pnl': pnl,
            'result': result,
            'held_ct': int(yes_ct),
            'yes_cost': yes_cost,
            'settled_time': st.get('settled_time', ''),
        })

    ncaamb_losses.sort(key=lambda x: x['settled_time'])

    print(f"NCAAMB settlements Mar 11-15: {len(ncaamb_all)}")
    print(f"NCAAMB losses: {len(ncaamb_losses)}")
    print()

    # ════════════════════════════════════════════════════════════════
    # For each loss, check CSV data and determine filter applicability
    # ════════════════════════════════════════════════════════════════
    print("=" * 120)
    print("NCAAMB LOSS AUDIT — WOULD CURRENT CONFIG BLOCK?")
    print("=" * 120)

    # Config timeline
    config_changes = {
        '2026-03-13T12:00': 'bounce_chain_v2',  # approximate deployment time
        '2026-03-13T16:00': 'detection_fixes',
        '2026-03-14T14:00': 'sizing_35ct',
        '2026-03-15T18:12': 'scenario_b',
        '2026-03-15T18:42': 'premarket_fix',
    }

    blocked_count = 0
    still_loss_count = 0
    blocked_pnl = 0
    still_loss_pnl = 0

    print(f"\n  {'#':>2s} {'Side':<6s} {'Date':>11s} {'HeldCt':>6s} {'PnL':>7s} "
          f"{'Config':>10s} {'Entry':>5s} {'GS':>30s} {'Spike':>6s} {'Chain':>6s} "
          f"{'Blocked?':>8s} {'Filter':<30s}")
    print(f"  {'─'*2} {'─'*6} {'─'*11} {'─'*6} {'─'*7} "
          f"{'─'*10} {'─'*5} {'─'*30} {'─'*6} {'─'*6} "
          f"{'─'*8} {'─'*30}")

    for i, loss in enumerate(ncaamb_losses):
        ticker = loss['ticker']
        side = loss['side']
        settled = loss['settled_time'][:16]
        settled_date = loss['settled_time'][:10]
        pnl = loss['pnl']
        held_ct = loss['held_ct']

        # Determine which config was running
        if settled_date <= '2026-03-13' and settled[:16] < '2026-03-13T12:00':
            config = 'OLD_5sig'
        elif settled_date <= '2026-03-13' and settled[:16] < '2026-03-13T16:00':
            config = 'v2_nofix'
        elif settled_date <= '2026-03-14' and settled[:16] < '2026-03-14T14:00':
            config = 'v2+detect'
        elif settled_date <= '2026-03-15' and settled[:16] < '2026-03-15T18:12':
            config = 'v2+35ct'
        else:
            config = 'CURRENT'

        # Look up CSV data
        csv_data = csv_by_ticker.get(ticker, {})
        entry = int(float(csv_data.get('entry_price', 0) or 0))
        gs = (csv_data.get('game_state_at_entry', '') or '')[:28]
        pre10m = csv_data.get('pre_entry_price_10m', '') or ''
        chain_detail = csv_data.get('chain_detail', '') or ''
        chain_score = csv_data.get('chain_score', '') or ''
        period = csv_data.get('period', '') or ''
        clock = csv_data.get('clock_seconds', '') or ''
        score_diff = csv_data.get('score_diff', '') or ''
        spread = csv_data.get('spread', '') or ''
        combined = csv_data.get('combined_mid', '') or ''
        entry_mode = csv_data.get('entry_mode', '') or ''

        # Compute spike
        if pre10m and pre10m not in ('', 'nan', 'None'):
            try:
                fsp = int(float(pre10m))
            except:
                fsp = 50
        else:
            fsp = 50
        spike = entry - fsp if entry > 0 else 0

        # Determine if current config would block
        blocked = False
        filter_reason = ""

        # Check: was this entered on old config that's now fixed?
        is_maker = entry >= 88 or 'maker' in entry_mode or '92' in entry_mode

        # Filter 1: No game state data = fail-closed
        if not gs or gs.strip() == '' or gs.strip() == '?':
            # Current config: if game state API fails, reject entry
            # But we need to check if the game was actually in progress
            # Old config didn't have fail-closed on all paths
            if entry > 0:  # we have CSV data
                blocked = True
                filter_reason = "FAIL_CLOSED: no game state data"

        # Filter 2: Scheduled/not_started
        if not blocked and ('scheduled' in gs.lower() or 'not_started' in gs.lower()):
            blocked = True
            filter_reason = "REJECT_GAMESTATE: not started"

        # Filter 3: Score diff check (15+ pt deficit in 2H)
        if not blocked and score_diff and period:
            try:
                sd = int(float(score_diff))
                p = int(float(period))
                if p >= 2 and sd <= -15:
                    blocked = True
                    filter_reason = f"REJECT_DEFICIT: period={p} diff={sd}"
            except:
                pass

        # Filter 4: Maker spike gate (current: spike>10c on C-tier maker)
        if not blocked and is_maker and spike > 10:
            blocked = True
            filter_reason = f"REJECT_MAKER_SPIKE: spike={spike:+d}c maker entry"

        # Filter 5: Early game + no chain (current handles this differently)
        # The early_game filter returns pending if period=1 + diff<5, then requires chain>=2
        if not blocked and period and score_diff:
            try:
                p = int(float(period))
                sd = abs(int(float(score_diff)))
                if p == 1 and sd < 5:
                    # Early game — need chain >= 2
                    cs = 0
                    if chain_score:
                        try:
                            cs = int(float(chain_score))
                        except:
                            pass
                    if cs < 2:
                        blocked = True
                        filter_reason = f"EARLY_GAME: period=1 diff={sd} chain={cs}<2"
            except:
                pass

        # Note: We can't retroactively check bounce chain detection fixes
        # (stable sparse data, wall 0.7 threshold) because the chain wasn't
        # computed with current code. But we CAN note which trades ran on old code.

        if blocked:
            blocked_count += 1
            blocked_pnl += pnl
            status = "BLOCKED"
        else:
            still_loss_count += 1
            still_loss_pnl += pnl
            status = "LOSS"
            if not filter_reason:
                # Try to determine WHY it still gets through
                if entry > 0:
                    filter_reason = f"entry={entry}c spike={spike:+d}c"
                    if gs:
                        filter_reason += f" gs={gs[:20]}"
                else:
                    filter_reason = "no CSV data (pre-tracking)"

        chain_str = chain_detail[:5] if chain_detail else '?'
        spike_str = f"{spike:+d}c" if entry > 0 else "?"

        print(f"  {i+1:>2d} {side:<6s} {settled[5:16]:>11s} {held_ct:>5d}ct {pnl:>+6d}c "
              f"{config:>10s} {entry:>4d}c {gs[:28]:>28s}  {spike_str:>5s} {chain_str:>5s} "
              f"{status:>8s} {filter_reason:<30s}")

    # ════════════════════════════════════════════════════════════════
    # Summary
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)

    total_ncaamb_pnl = sum(t['pnl'] for t in ncaamb_all)
    total_ncaamb_w = len([t for t in ncaamb_all if t['pnl'] > 0])
    total_ncaamb_l = len([t for t in ncaamb_all if t['pnl'] < 0])

    print(f"\n  NCAAMB totals (all configs): {len(ncaamb_all)} trades | {total_ncaamb_w}W {total_ncaamb_l}L | "
          f"WR={total_ncaamb_w/(total_ncaamb_w+total_ncaamb_l)*100:.1f}% | PnL={total_ncaamb_pnl:+d}c (${total_ncaamb_pnl/100:.2f})")

    print(f"\n  Of {len(ncaamb_losses)} losses:")
    print(f"    Current config BLOCKS:  {blocked_count} losses worth {blocked_pnl:+d}c (${blocked_pnl/100:.2f})")
    print(f"    Current config ALLOWS:  {still_loss_count} losses worth {still_loss_pnl:+d}c (${still_loss_pnl/100:.2f})")

    # Projected WR with blocked losses removed
    projected_w = total_ncaamb_w
    projected_l = total_ncaamb_l - blocked_count
    projected_pnl = total_ncaamb_pnl - blocked_pnl  # removing blocked losses = subtracting negative = adding
    projected_wr = projected_w / (projected_w + projected_l) * 100 if (projected_w + projected_l) > 0 else 0

    print(f"\n  PROJECTED with current config:")
    print(f"    Trades: {projected_w + projected_l} ({projected_w}W {projected_l}L)")
    print(f"    WR: {projected_wr:.1f}%")
    print(f"    PnL: {projected_pnl:+d}c (${projected_pnl/100:.2f})")
    print(f"    $/day: ${projected_pnl/100/5:.2f}")

    # Break down by config era
    print(f"\n  Losses by config era:")
    era_counts = {}
    for loss in ncaamb_losses:
        settled = loss['settled_time'][:16]
        settled_date = loss['settled_time'][:10]
        if settled_date <= '2026-03-13' and settled < '2026-03-13T12:00':
            era = 'OLD_5sig (Mar 11-13AM)'
        elif settled_date <= '2026-03-13' and settled < '2026-03-13T16:00':
            era = 'v2_nofix (Mar 13 midday)'
        elif settled[:16] < '2026-03-14T14:00':
            era = 'v2+detect (Mar 13PM-14AM)'
        elif settled[:16] < '2026-03-15T18:12':
            era = 'v2+35ct (Mar 14PM-15PM)'
        else:
            era = 'CURRENT (Mar 15 evening)'
        era_counts.setdefault(era, {'count': 0, 'pnl': 0})
        era_counts[era]['count'] += 1
        era_counts[era]['pnl'] += loss['pnl']

    for era, data in sorted(era_counts.items()):
        print(f"    {era:<30s}: {data['count']:>2d} losses | {data['pnl']:>+6d}c")

    # Also: which losses had NO CSV data at all?
    no_csv = [l for l in ncaamb_losses if l['ticker'] not in csv_by_ticker]
    in_csv = [l for l in ncaamb_losses if l['ticker'] in csv_by_ticker]
    print(f"\n  CSV coverage: {len(in_csv)} losses have CSV data, {len(no_csv)} do NOT")
    if no_csv:
        print(f"  Losses without CSV data (can't verify filters):")
        for l in no_csv:
            print(f"    {l['side']:<6s} {l['settled_time'][:16]} pnl={l['pnl']:+d}c held={l['held_ct']}ct")

asyncio.run(main())
