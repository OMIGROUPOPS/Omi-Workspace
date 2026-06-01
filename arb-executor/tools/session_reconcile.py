#!/usr/bin/env python3
"""T57 — end-of-session account reconciliation (bot-state vs Kalshi-actual).

Execution-lock gate: confirms the account is FLAT (0 unsettled positions, 0
resting orders) before a deploy/restart, and reports cash + portfolio + 24h
settlement revenue from the Kalshi API per the P&L-reporting discipline.
Exit 0 if flat (safe to deploy), 1 otherwise (do not deploy).
Run: cd arb-executor && python3 tools/session_reconcile.py
"""
import sys, asyncio, aiohttp, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # repo for live_v4 + fv
import live_v4 as L


async def main():
    ak, pk = L.load_credentials(); rl = L.RateLimiter()
    async with aiohttp.ClientSession() as s:
        bal = await L.api_get(s, ak, pk, "/trade-api/v2/portfolio/balance", rl)
        pos = await L.api_get(s, ak, pk,
            "/trade-api/v2/portfolio/positions?count_filter=position&settlement_status=unsettled&limit=500", rl)
        ords = await L.api_get(s, ak, pk, "/trade-api/v2/portfolio/orders?status=resting&limit=500", rl)
        min_ts = int(time.time()) - 86400
        setl = await L.api_get(s, ak, pk,
            "/trade-api/v2/portfolio/settlements?min_ts=%d&limit=500" % min_ts, rl)

    opn = [p for p in (pos or {}).get("market_positions", []) if int(float(p.get("position_fp", 0))) != 0]
    rest = (ords or {}).get("orders", [])
    settlements = (setl or {}).get("settlements", [])
    cash_c = (bal or {}).get("balance")
    cash = (cash_c / 100.0) if isinstance(cash_c, (int, float)) else cash_c

    print("=== T57 SESSION RECONCILE (Kalshi-actual) ===")
    if isinstance(cash, float):
        print("cash_balance: $%.2f" % cash)
    else:
        print("cash_balance: %r" % cash)
    print("open_unsettled_positions: %d" % len(opn))
    for p in opn:
        print("    %s qty=%d exposure=%s" % (p.get("ticker"),
              int(float(p.get("position_fp", 0))), p.get("market_exposure_dollars")))
    print("resting_orders: %d" % len(rest))
    for o in rest[:25]:
        print("    %s %s %s" % (o.get("ticker"), o.get("action"), o.get("side")))
    # 24h realized P&L from settlements (NET, in dollars).
    # Bug fixed 2026-06-01: prior code summed the `revenue` field — which is in
    # CENTS (100x overstatement when printed as dollars), is GROSS not net, and
    # is 0 for hedged both-leg holdings (so it silently missed most payouts).
    # Correct per-settlement payout = yes_count*value + no_count*(100-value) in
    # cents (value = per-contract settle: 100/0 for binary, scalar value e.g. 92
    # otherwise); net = payout - cost_basis - fees. Reported net per the
    # P&L-reporting discipline (net realized, never gross notional).
    fnum = lambda d, k: float(d.get(k) or 0)
    payout = cost = fees = 0.0
    for x in settlements:
        yc = fnum(x, "yes_count_fp"); nc = fnum(x, "no_count_fp"); val = fnum(x, "value")
        payout += (yc * val + nc * (100.0 - val)) / 100.0
        cost += fnum(x, "yes_total_cost_dollars") + fnum(x, "no_total_cost_dollars")
        fees += fnum(x, "fee_cost")
    net = payout - cost - fees
    print("settlements_last_24h: %d  net_realized_pnl=$%.2f  (gross_payout=$%.2f cost=$%.2f fees=$%.2f)"
          % (len(settlements), net, payout, cost, fees))

    flat = (len(opn) == 0 and len(rest) == 0)
    print("portfolio: cash only" if flat else "portfolio: cash + %d open position(s)" % len(opn))
    print("FLAT:", flat, "->", "SAFE TO DEPLOY" if flat else "NOT FLAT -- DO NOT DEPLOY")
    return 0 if flat else 1


sys.exit(asyncio.run(main()))
