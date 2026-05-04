#!/usr/bin/env python3
"""Optimal sport-specific spike gates with corrected loss data.
Uses settlement API for real pnl on all 215 trades.
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
        trades = list(csv.DictReader(f))

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

    settle_map = {}
    for st in all_settlements:
        settle_map[st.get('ticker', '')] = st

    # ─── Enrich all trades ───
    for t in trades:
        ticker = t.get('ticker', '')
        entry = int(float(t.get('entry_price', 0) or 0))
        mode = t.get('entry_mode', '') or ''
        sport = t.get('sport', '?')
        side = t.get('entry_side', '?')
        series = t.get('series', '') or ''

        pre10m = (t.get('pre_entry_price_10m', '') or '').strip()
        if pre10m and pre10m not in ('nan', 'None', ''):
            try:
                fsp = int(float(pre10m))
            except:
                fsp = 50
        else:
            fsp = 50

        spike = entry - fsp
        is_maker = entry >= 88 or 'maker' in mode or '92' in mode

        # Chain info from CSV
        chain_raw = (t.get('chain_detail', '') or t.get('bounce_chain', '') or '').strip()
        chain_score_raw = 0
        # Try to extract chain score from various formats
        for field in ['chain_score', 'bounce_chain_score']:
            v = (t.get(field, '') or '').strip()
            if v and v not in ('nan', ''):
                try:
                    chain_score_raw = int(float(v))
                except:
                    pass

        t['_entry'] = entry
        t['_spike'] = spike
        t['_cls'] = "SPIKE" if spike > 2 else ("DIP" if spike < -2 else "FLAT")
        t['_is_maker'] = is_maker
        t['_sport'] = sport
        t['_fsp'] = fsp
        t['_side'] = side
        t['_chain'] = chain_raw
        t['_chain_score'] = chain_score_raw
        t['_series'] = series
        t['_ticker'] = ticker

        # Game state
        gs = (t.get('game_state_at_entry', '') or '').strip()
        t['_gs'] = gs

        # Resolve pnl
        pnl_raw = (t.get('pnl_cents', '') or '').strip()
        if pnl_raw and pnl_raw != 'nan':
            pnl = int(float(pnl_raw))
            t['_pnl'] = pnl
            t['_wl'] = "W" if pnl > 0 else ("L" if pnl < 0 else "P")
        else:
            sdata = settle_map.get(ticker)
            if sdata:
                result = sdata.get('market_result', '')
                yes_ct = float(sdata.get('yes_count_fp', '0') or '0')
                yes_cost = int(sdata.get('yes_total_cost', 0) or 0)
                no_ct = float(sdata.get('no_count_fp', '0') or '0')

                if result == 'no' and yes_ct > 0:
                    t['_pnl'] = -yes_cost
                    t['_wl'] = "L"
                elif result == 'yes' and yes_ct > 0:
                    t['_pnl'] = int(100 * yes_ct) - yes_cost
                    t['_wl'] = "W" if t['_pnl'] > 0 else "L"
                elif result == 'yes' and no_ct > 0:
                    no_cost = int(sdata.get('no_total_cost', 0) or 0)
                    t['_pnl'] = -no_cost
                    t['_wl'] = "L"
                elif result == 'no' and no_ct > 0:
                    no_cost = int(sdata.get('no_total_cost', 0) or 0)
                    t['_pnl'] = int(100 * no_ct) - no_cost
                    t['_wl'] = "W" if t['_pnl'] > 0 else "L"
                else:
                    t['_pnl'] = 0
                    t['_wl'] = "P"
            else:
                t['_pnl'] = 0
                t['_wl'] = "P"

    DAYS = 5

    # ════════════════════════════════════════════════════════════════
    # SECTION 1: NCAAMB STB SPIKE GATE SWEEP
    # ════════════════════════════════════════════════════════════════
    print("=" * 90)
    print("SECTION 1: NCAAMB STB — SPIKE GATE SWEEP")
    print("=" * 90)

    ncaamb_stb = [t for t in trades if t['_sport'] == 'ncaamb' and not t['_is_maker']]
    ncaamb_stb_spikes = [t for t in ncaamb_stb if t['_cls'] == 'SPIKE']
    ncaamb_stb_all = ncaamb_stb  # include non-spikes too for total WR

    w_all = len([t for t in ncaamb_stb if t['_wl'] == 'W'])
    l_all = len([t for t in ncaamb_stb if t['_wl'] == 'L'])
    pnl_all = sum(t['_pnl'] for t in ncaamb_stb)
    print(f"\n  Baseline (no gate): {len(ncaamb_stb)} trades | {w_all}W {l_all}L | "
          f"WR={w_all/(w_all+l_all)*100:.1f}% | PnL={pnl_all:+d}c | $/day=${pnl_all/100/DAYS:.2f}")

    print(f"\n  {'Gate':>12s} {'Pass':>5s} {'Block':>5s} {'PassW':>5s} {'PassL':>5s} {'BlkW':>5s} {'BlkL':>5s}"
          f" {'WR%':>6s} {'PassPnL':>9s} {'$/day':>8s} {'Net':>9s}")
    print(f"  {'─'*12} {'─'*5} {'─'*5} {'─'*5} {'─'*5} {'─'*5} {'─'*5}"
          f" {'─'*6} {'─'*9} {'─'*8} {'─'*9}")

    for threshold in [3, 5, 7, 10, 12, 15, 17, 20, 25]:
        # Gate blocks spike trades with spike > threshold
        blocked = [t for t in ncaamb_stb if t['_cls'] == 'SPIKE' and t['_spike'] > threshold]
        passed = [t for t in ncaamb_stb if not (t['_cls'] == 'SPIKE' and t['_spike'] > threshold)]

        pw = len([t for t in passed if t['_wl'] == 'W'])
        pl = len([t for t in passed if t['_wl'] == 'L'])
        bw = len([t for t in blocked if t['_wl'] == 'W'])
        bl = len([t for t in blocked if t['_wl'] == 'L'])
        pass_pnl = sum(t['_pnl'] for t in passed)
        wr = pw / (pw + pl) * 100 if (pw + pl) > 0 else 0
        net = pass_pnl - pnl_all

        print(f"  spike>{threshold:>2d}c   {len(passed):>5d} {len(blocked):>5d} {pw:>5d} {pl:>5d} {bw:>5d} {bl:>5d}"
              f" {wr:>5.1f}% {pass_pnl:>+8d}c ${pass_pnl/100/DAYS:>7.2f} {net:>+8d}c")

    # ════════════════════════════════════════════════════════════════
    # SECTION 2: TENNIS STB SPIKE GATE SWEEP
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 90)
    print("SECTION 2: TENNIS STB — SPIKE GATE SWEEP")
    print("=" * 90)

    tennis_stb = [t for t in trades if t['_sport'] == 'tennis' and not t['_is_maker']]

    w_all = len([t for t in tennis_stb if t['_wl'] == 'W'])
    l_all = len([t for t in tennis_stb if t['_wl'] == 'L'])
    pnl_all = sum(t['_pnl'] for t in tennis_stb)
    print(f"\n  Baseline (no gate): {len(tennis_stb)} trades | {w_all}W {l_all}L | "
          f"WR={w_all/(w_all+l_all)*100:.1f}% | PnL={pnl_all:+d}c | $/day=${pnl_all/100/DAYS:.2f}")

    # Tennis losses detail
    tennis_losses = [t for t in tennis_stb if t['_wl'] == 'L']
    print(f"\n  Tennis STB losses ({len(tennis_losses)}):")
    for t in tennis_losses:
        is_chall = 'challenger' in t['_ticker'].lower() or 'challenger' in t['_series'].lower()
        tour = "CHALLENGER" if is_chall else "MAIN/WTA"
        print(f"    {t['_side']:<6s} entry={t['_entry']}c spike={t['_spike']:+d}c pnl={t['_pnl']:+d}c  {tour}  ticker={t['_ticker'][:50]}")

    print(f"\n  {'Gate':>12s} {'Pass':>5s} {'Block':>5s} {'PassW':>5s} {'PassL':>5s} {'BlkW':>5s} {'BlkL':>5s}"
          f" {'WR%':>6s} {'PassPnL':>9s} {'$/day':>8s} {'Net':>9s}")
    print(f"  {'─'*12} {'─'*5} {'─'*5} {'─'*5} {'─'*5} {'─'*5} {'─'*5}"
          f" {'─'*6} {'─'*9} {'─'*8} {'─'*9}")

    for threshold in [3, 5, 7, 10, 12, 15, 17, 20]:
        blocked = [t for t in tennis_stb if t['_cls'] == 'SPIKE' and t['_spike'] > threshold]
        passed = [t for t in tennis_stb if not (t['_cls'] == 'SPIKE' and t['_spike'] > threshold)]

        pw = len([t for t in passed if t['_wl'] == 'W'])
        pl = len([t for t in passed if t['_wl'] == 'L'])
        bw = len([t for t in blocked if t['_wl'] == 'W'])
        bl = len([t for t in blocked if t['_wl'] == 'L'])
        pass_pnl = sum(t['_pnl'] for t in passed)
        wr = pw / (pw + pl) * 100 if (pw + pl) > 0 else 0
        net = pass_pnl - pnl_all

        print(f"  spike>{threshold:>2d}c   {len(passed):>5d} {len(blocked):>5d} {pw:>5d} {pl:>5d} {bw:>5d} {bl:>5d}"
              f" {wr:>5.1f}% {pass_pnl:>+8d}c ${pass_pnl/100/DAYS:>7.2f} {net:>+8d}c")

    # ════════════════════════════════════════════════════════════════
    # SECTION 3: NBA STB — confirmation
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 90)
    print("SECTION 3: NBA STB — CONFIRMED NO GATE NEEDED")
    print("=" * 90)

    nba_stb = [t for t in trades if t['_sport'] == 'nba' and not t['_is_maker']]
    w = len([t for t in nba_stb if t['_wl'] == 'W'])
    l = len([t for t in nba_stb if t['_wl'] == 'L'])
    pnl = sum(t['_pnl'] for t in nba_stb)
    print(f"\n  NBA STB: {len(nba_stb)} trades | {w}W {l}L | WR={w/(w+l)*100 if (w+l) else 0:.0f}% | PnL={pnl:+d}c")

    # ════════════════════════════════════════════════════════════════
    # SECTION 4: NHL STB
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 90)
    print("SECTION 4: NHL STB — 0-2, CONFIRMED DEAD")
    print("=" * 90)

    nhl_stb = [t for t in trades if t['_sport'] == 'nhl' and not t['_is_maker']]
    w = len([t for t in nhl_stb if t['_wl'] == 'W'])
    l = len([t for t in nhl_stb if t['_wl'] == 'L'])
    pnl = sum(t['_pnl'] for t in nhl_stb)
    print(f"\n  NHL STB: {len(nhl_stb)} trades | {w}W {l}L | PnL={pnl:+d}c")
    for t in nhl_stb:
        print(f"    {t['_side']:<6s} entry={t['_entry']}c spike={t['_spike']:+d}c pnl={t['_pnl']:+d}c")

    # ════════════════════════════════════════════════════════════════
    # SECTION 5: NCAAMB 10 LOSSES — PATTERN ANALYSIS
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 90)
    print("SECTION 5: NCAAMB STB — 10 LOSS DEEP DIVE")
    print("=" * 90)

    ncaamb_losses = [t for t in ncaamb_stb if t['_wl'] == 'L']
    print(f"\n  {'Side':<6s} {'Entry':>5s} {'FSP':>5s} {'Spike':>6s} {'Chain':<30s} {'GameState':<40s} {'PnL':>7s}")
    print(f"  {'─'*6} {'─'*5} {'─'*5} {'─'*6} {'─'*30} {'─'*40} {'─'*7}")

    for t in ncaamb_losses:
        chain = t['_chain'][:28] if t['_chain'] else '?'
        gs = t['_gs'][:38] if t['_gs'] else '?'
        print(f"  {t['_side']:<6s} {t['_entry']:>4d}c {t['_fsp']:>4d}c {t['_spike']:>+5d}c {chain:<30s} {gs:<40s} {t['_pnl']:>+6d}c")

    # Pattern analysis
    print(f"\n  Pattern analysis:")
    high_spike = [t for t in ncaamb_losses if t['_spike'] > 15]
    med_spike = [t for t in ncaamb_losses if 5 < t['_spike'] <= 15]
    low_spike = [t for t in ncaamb_losses if t['_spike'] <= 5]
    print(f"    spike > 15c: {len(high_spike)} losses ({sum(t['_pnl'] for t in high_spike):+d}c)")
    print(f"    spike 6-15c: {len(med_spike)} losses ({sum(t['_pnl'] for t in med_spike):+d}c)")
    print(f"    spike <= 5c: {len(low_spike)} losses ({sum(t['_pnl'] for t in low_spike):+d}c)")

    # Test compound filters: chain >= 2 AND spike <= X
    print(f"\n  Compound filter test (require chain>=2 OR spike<=X):")
    # Actually test: would chain>=2 AND spike<=15 catch them?
    # For each loss, check if chain_score >= 2
    print(f"\n  Chain scores on losses:")
    for t in ncaamb_losses:
        print(f"    {t['_side']:<6s} chain_score={t['_chain_score']} chain={t['_chain'][:30]}  spike={t['_spike']:+d}c")

    # Since chain data is sparse in CSV, test spike-only gates
    # Also test entry-price-based gates
    print(f"\n  Entry price analysis on losses:")
    high_entry = [t for t in ncaamb_losses if t['_entry'] >= 75]
    low_entry = [t for t in ncaamb_losses if t['_entry'] < 75]
    print(f"    entry >= 75c: {len(high_entry)} losses ({sum(t['_pnl'] for t in high_entry):+d}c)")
    print(f"    entry <  75c: {len(low_entry)} losses ({sum(t['_pnl'] for t in low_entry):+d}c)")

    # Would an entry+spike combo work?
    print(f"\n  Combo: entry >= 75c AND spike > 10c:")
    ncaamb_combo_blocked = [t for t in ncaamb_stb if t['_entry'] >= 75 and t['_spike'] > 10]
    ncaamb_combo_passed = [t for t in ncaamb_stb if not (t['_entry'] >= 75 and t['_spike'] > 10)]
    bl = [t for t in ncaamb_combo_blocked if t['_wl'] == 'L']
    bw = [t for t in ncaamb_combo_blocked if t['_wl'] == 'W']
    pw = len([t for t in ncaamb_combo_passed if t['_wl'] == 'W'])
    pl = len([t for t in ncaamb_combo_passed if t['_wl'] == 'L'])
    pass_pnl = sum(t['_pnl'] for t in ncaamb_combo_passed)
    print(f"    Blocked: {len(bl)}L + {len(bw)}W = {len(ncaamb_combo_blocked)}")
    print(f"    Passed: {pw}W + {pl}L | WR={pw/(pw+pl)*100:.1f}% | PnL={pass_pnl:+d}c")

    # ════════════════════════════════════════════════════════════════
    # SECTION 6: COMBINED OPTIMAL CONFIG
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 90)
    print("SECTION 6: COMBINED OPTIMAL CONFIG")
    print("=" * 90)

    # Find optimal threshold per sport
    configs = {}
    for sport, subset in [('ncaamb', ncaamb_stb), ('tennis', tennis_stb)]:
        best_net = -999999
        best_thresh = None
        baseline_pnl = sum(t['_pnl'] for t in subset)

        for threshold in range(3, 30):
            blocked = [t for t in subset if t['_cls'] == 'SPIKE' and t['_spike'] > threshold]
            passed = [t for t in subset if not (t['_cls'] == 'SPIKE' and t['_spike'] > threshold)]
            pass_pnl = sum(t['_pnl'] for t in passed)
            net = pass_pnl - baseline_pnl
            if net > best_net:
                best_net = net
                best_thresh = threshold

        configs[sport] = best_thresh

    print(f"\n  Optimal STB spike gates (maximizing net PnL vs no-gate):")
    print(f"  ┌──────────┬───────────────┬──────────┬────────┬──────────┐")
    print(f"  │ Sport    │ STB Gate      │ PnL/day  │ WR%    │ vs nogat │")
    print(f"  ├──────────┼───────────────┼──────────┼────────┼──────────┤")

    total_pnl_gated = 0
    total_w_gated = 0
    total_l_gated = 0
    total_trades_gated = 0

    for sport in ['nba', 'ncaamb', 'nhl', 'tennis']:
        stb = [t for t in trades if t['_sport'] == sport and not t['_is_maker']]
        baseline = sum(t['_pnl'] for t in stb)

        if sport == 'nba':
            gate_desc = "NO GATE"
            passed = stb
        elif sport == 'nhl':
            gate_desc = "DISABLED"
            passed = []
        elif sport in configs:
            thresh = configs[sport]
            gate_desc = f"spike > {thresh}c"
            passed = [t for t in stb if not (t['_cls'] == 'SPIKE' and t['_spike'] > thresh)]
        else:
            gate_desc = "NO GATE"
            passed = stb

        pw = len([t for t in passed if t['_wl'] == 'W'])
        pl = len([t for t in passed if t['_wl'] == 'L'])
        pass_pnl = sum(t['_pnl'] for t in passed)
        wr = pw / (pw + pl) * 100 if (pw + pl) > 0 else 0
        diff = pass_pnl - baseline

        total_pnl_gated += pass_pnl
        total_w_gated += pw
        total_l_gated += pl
        total_trades_gated += len(passed)

        print(f"  │ {sport:<8s} │ {gate_desc:<13s} │ ${pass_pnl/100/DAYS:>6.2f}  │ {wr:>5.1f}% │ {diff:>+7d}c │")

    # Add maker trades (unchanged)
    maker_trades = [t for t in trades if t['_is_maker']]
    maker_pnl = sum(t['_pnl'] for t in maker_trades)
    mw = len([t for t in maker_trades if t['_wl'] == 'W'])
    ml = len([t for t in maker_trades if t['_wl'] == 'L'])
    print(f"  │ ALL      │ MAKER (exist) │ ${maker_pnl/100/DAYS:>6.2f}  │ {mw/(mw+ml)*100 if (mw+ml) else 0:>5.1f}% │         │")
    print(f"  └──────────┴───────────────┴──────────┴────────┴──────────┘")

    grand_pnl = total_pnl_gated + maker_pnl
    grand_w = total_w_gated + mw
    grand_l = total_l_gated + ml
    print(f"\n  COMBINED: ${grand_pnl/100/DAYS:.2f}/day | {grand_w}W {grand_l}L | WR={grand_w/(grand_w+grand_l)*100:.1f}%")

    # ════════════════════════════════════════════════════════════════
    # SECTION 7: PROJECTED $/DAY AT 35ct WITH OPTIMAL GATES
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 90)
    print("SECTION 7: PROJECTED $/DAY AT 35ct WITH OPTIMAL GATES")
    print("=" * 90)

    # Current data was mostly at 25ct. Scale STB to 35ct (1.4x), keep maker at 25ct
    scale = 35.0 / 25.0

    print(f"\n  Scaling: STB pnl × {scale:.2f} (25ct → 35ct), Maker unchanged (25ct)")

    total_scaled = 0
    for sport in ['nba', 'ncaamb', 'tennis']:
        stb = [t for t in trades if t['_sport'] == sport and not t['_is_maker']]

        if sport == 'nba':
            passed = stb
            gate = "no gate"
        elif sport in configs:
            thresh = configs[sport]
            passed = [t for t in stb if not (t['_cls'] == 'SPIKE' and t['_spike'] > thresh)]
            gate = f"spike>{thresh}c"
        else:
            passed = stb
            gate = "no gate"

        stb_pnl = sum(t['_pnl'] for t in passed)
        stb_scaled = stb_pnl * scale
        total_scaled += stb_scaled

        pw = len([t for t in passed if t['_wl'] == 'W'])
        pl = len([t for t in passed if t['_wl'] == 'L'])
        wr = pw / (pw + pl) * 100 if (pw + pl) > 0 else 0

        print(f"    {sport:>8s} STB ({gate}): {len(passed)} trades | {pw}W {pl}L | "
              f"25ct=${stb_pnl/100/DAYS:.2f}/day → 35ct=${stb_scaled/100/DAYS:.2f}/day")

    total_scaled += maker_pnl  # maker stays at 25ct
    print(f"    {'MAKER':>8s} (existing gate): {len(maker_trades)} trades | "
          f"${maker_pnl/100/DAYS:.2f}/day (stays 25ct)")

    print(f"\n  ┌─────────────────────────────────────────────────────┐")
    print(f"  │ PROJECTED at 35ct STB + 25ct Maker + optimal gates  │")
    print(f"  │ PnL/day: ${total_scaled/100/DAYS:.2f}                              │")
    print(f"  │ PnL/week: ${total_scaled/100/DAYS*7:.2f}                            │")
    print(f"  └─────────────────────────────────────────────────────┘")

    # ════════════════════════════════════════════════════════════════
    # SECTION 8: IMPLEMENTATION SPEC
    # ════════════════════════════════════════════════════════════════
    print()
    print("=" * 90)
    print("SECTION 8: IMPLEMENTATION SPEC")
    print("=" * 90)

    ncaamb_thresh = configs.get('ncaamb', 15)
    tennis_thresh = configs.get('tennis', 15)

    print(f"""
  SPORT-SPECIFIC STB SPIKE GATES:

  ncaamb_stb.py — STB entry path:
    After computing _spike_m and _pre_sc:
    if sport in ('ncaamb', 'nba') and _spike_m > {ncaamb_thresh} and _ds_m == 'SPIKE':
        if _pre_sc < 10:  # C-tier only
            log("[REJECT_STB_SPIKE] {{side}} spike={{spike}}c > {ncaamb_thresh}c C-tier — blocked")
            return
    NBA: NO spike gate (100% WR, zero losses)
    NHL: STB disabled entirely

  tennis_stb.py — STB entry path:
    if _spike_m > {tennis_thresh} and _ds_m == 'SPIKE':
        if _pre_sc < 10:  # C-tier only
            log("[REJECT_STB_SPIKE] {{side}} spike={{spike}}c > {tennis_thresh}c C-tier — blocked")
            return

  92+ MAKER path (both bots): Keep existing Scenario B gate
    if _m_score < 10 and _m_spike > 10:
        log("[REJECT_MAKER_SPIKE] ...")
        return
""")

asyncio.run(main())
