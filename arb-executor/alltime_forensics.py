#!/usr/bin/env python3
"""
All-Time P&L Forensics — trace every dollar from day one.

Pulls ALL Kalshi fills + settlements from the very beginning.
Pulls ALL PM positions + trade history.
Calculates implied deposits by working backwards from trade history.
Breaks down P&L by month and by era (pre-arb vs arb).
"""

import asyncio
import aiohttp
import json
import os
import time
import base64
import hashlib
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import padding, ed25519
from cryptography.hazmat.primitives import hashes, serialization
from dotenv import load_dotenv

load_dotenv()

# ── Kalshi credentials ──────────────────────────────────────────
KALSHI_BASE = "https://api.elections.kalshi.com"
KALSHI_API_KEY = "f3b064d1-a02e-42a4-b2b1-132834694d23"
KALSHI_PEM = Path(__file__).parent / "kalshi.pem"

def _kalshi_headers(method: str, path: str) -> dict:
    ts = str(int(time.time() * 1000))
    msg = f"{ts}{method}{path}".encode()
    with open(KALSHI_PEM, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    sig = key.sign(msg, padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ), hashes.SHA256())
    return {
        "KALSHI-ACCESS-KEY": KALSHI_API_KEY,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
        "Content-Type": "application/json",
    }

# ── PM US credentials ───────────────────────────────────────────
PM_BASE = "https://api.polymarket.us"
PM_API_KEY = os.getenv("PM_US_API_KEY", "")
PM_SECRET = os.getenv("PM_US_SECRET_KEY", "") or os.getenv("PM_US_SECRET", "")

def _pm_headers(method: str, path: str) -> dict:
    ts = str(int(time.time() * 1000))
    msg = f"{ts}{method}{path}".encode()
    raw = base64.b64decode(PM_SECRET)
    priv = ed25519.Ed25519PrivateKey.from_private_bytes(raw[:32])
    sig = priv.sign(msg)
    return {
        "X-PM-Access-Key": PM_API_KEY,
        "X-PM-Timestamp": ts,
        "X-PM-Signature": base64.b64encode(sig).decode(),
        "Content-Type": "application/json",
    }

# ── Helpers ──────────────────────────────────────────────────────
def cents_to_dollars(c):
    return c / 100.0

def parse_ts(s):
    if not s:
        return None
    try:
        # Handle various ISO formats
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except:
        return None

def month_key(dt):
    if dt is None:
        return "unknown"
    return dt.strftime("%Y-%m")

# ── Fetch ALL Kalshi fills (paginated, no date filter) ───────────
async def fetch_all_kalshi_fills(session):
    fills = []
    cursor = None
    page = 0
    while True:
        path = "/trade-api/v2/portfolio/fills?limit=100"
        if cursor:
            path += f"&cursor={cursor}"
        hdrs = _kalshi_headers("GET", path.split("?")[0])
        async with session.get(f"{KALSHI_BASE}{path}", headers=hdrs) as r:
            if r.status != 200:
                print(f"  Fills page {page}: HTTP {r.status}")
                break
            data = await r.json()
        batch = data.get("fills", [])
        if not batch:
            break
        fills.extend(batch)
        cursor = data.get("cursor")
        page += 1
        if not cursor or page > 200:
            break
    return fills

# ── Fetch ALL Kalshi settlements (paginated) ─────────────────────
async def fetch_all_kalshi_settlements(session):
    settlements = []
    cursor = None
    page = 0
    while True:
        path = "/trade-api/v2/portfolio/settlements?limit=100"
        if cursor:
            path += f"&cursor={cursor}"
        hdrs = _kalshi_headers("GET", path.split("?")[0])
        async with session.get(f"{KALSHI_BASE}{path}", headers=hdrs) as r:
            if r.status != 200:
                print(f"  Settlements page {page}: HTTP {r.status}")
                break
            data = await r.json()
        batch = data.get("settlements", [])
        if not batch:
            break
        settlements.extend(batch)
        cursor = data.get("cursor")
        page += 1
        if not cursor or page > 200:
            break
    return settlements

# ── Fetch Kalshi balance ─────────────────────────────────────────
async def fetch_kalshi_balance(session):
    path = "/trade-api/v2/portfolio/balance"
    hdrs = _kalshi_headers("GET", path)
    async with session.get(f"{KALSHI_BASE}{path}", headers=hdrs) as r:
        data = await r.json()
    return data

# ── Fetch Kalshi positions ───────────────────────────────────────
async def fetch_kalshi_positions(session):
    path = "/trade-api/v2/portfolio/positions?count_filter=position"
    hdrs = _kalshi_headers("GET", path.split("?")[0])
    async with session.get(f"{KALSHI_BASE}{path}", headers=hdrs) as r:
        data = await r.json()
    return data.get("market_positions", [])

# ── Fetch PM balance ─────────────────────────────────────────────
async def fetch_pm_balance(session):
    path = "/v1/account/balances"
    hdrs = _pm_headers("GET", path)
    async with session.get(f"{PM_BASE}{path}", headers=hdrs) as r:
        data = await r.json()
    for b in data.get("balances", []):
        if b.get("currency") == "USD":
            return float(b.get("buyingPower", 0))
    return 0.0

# ── Fetch PM positions ───────────────────────────────────────────
async def fetch_pm_positions(session):
    path = "/v1/portfolio/positions"
    hdrs = _pm_headers("GET", path)
    async with session.get(f"{PM_BASE}{path}", headers=hdrs) as r:
        data = await r.json()
    positions = data.get("positions", {})
    # Could be dict or list
    if isinstance(positions, dict):
        return positions
    return positions

# ── Fetch PM orders (trade history) ──────────────────────────────
async def fetch_pm_orders(session):
    """Try to fetch PM order history."""
    orders = []
    for endpoint in ["/v1/orders", "/v1/portfolio/orders", "/v1/orders/history"]:
        try:
            hdrs = _pm_headers("GET", endpoint)
            async with session.get(f"{PM_BASE}{endpoint}", headers=hdrs) as r:
                if r.status == 200:
                    data = await r.json()
                    result = data.get("orders", data if isinstance(data, list) else [])
                    if result:
                        print(f"  PM orders from {endpoint}: {len(result)} records")
                        orders = result
                        break
                    else:
                        print(f"  PM {endpoint}: empty")
                else:
                    print(f"  PM {endpoint}: HTTP {r.status}")
        except Exception as e:
            print(f"  PM {endpoint}: {e}")
    return orders

# ── Main analysis ────────────────────────────────────────────────
async def run():
    print("=" * 80)
    print("  ALL-TIME P&L FORENSICS — Every Dollar From Day One")
    print("=" * 80)

    async with aiohttp.ClientSession() as session:
        # ── 1. Fetch everything ──────────────────────────────────
        print("\n[1] Fetching all data...")

        k_fills = await fetch_all_kalshi_fills(session)
        print(f"  Kalshi fills: {len(k_fills)}")

        k_settlements = await fetch_all_kalshi_settlements(session)
        print(f"  Kalshi settlements: {len(k_settlements)}")

        k_balance_data = await fetch_kalshi_balance(session)
        k_cash = cents_to_dollars(k_balance_data.get("balance", 0))
        k_portfolio_val = cents_to_dollars(k_balance_data.get("portfolio_value", 0))
        print(f"  Kalshi cash: ${k_cash:.2f}, portfolio_value: ${k_portfolio_val:.2f}")

        k_positions = await fetch_kalshi_positions(session)
        print(f"  Kalshi open positions: {len(k_positions)}")

        pm_cash = await fetch_pm_balance(session)
        print(f"  PM cash: ${pm_cash:.2f}")

        pm_positions = await fetch_pm_positions(session)
        pm_pos_count = len(pm_positions) if isinstance(pm_positions, (dict, list)) else 0
        print(f"  PM open positions: {pm_pos_count}")

        pm_orders = await fetch_pm_orders(session)

        # ── 2. Analyze Kalshi fills ──────────────────────────────
        print("\n" + "=" * 80)
        print("  KALSHI — COMPLETE FILL HISTORY")
        print("=" * 80)

        # Parse all fills with dates
        k_fill_records = []
        for f in k_fills:
            dt = parse_ts(f.get("created_time"))
            side = f.get("side", "")
            action = f.get("action", "")
            count = int(f.get("count", 0))
            yes_price = int(f.get("yes_price", 0))
            no_price = int(f.get("no_price", 0))
            # fee_cost is a STRING in DOLLARS (e.g. "0.0200")
            fee_dollars = float(f.get("fee_cost", "0") or "0")
            fee_cents = int(round(fee_dollars * 100))
            ticker = f.get("ticker", f.get("market_ticker", ""))

            # Cash flow: buying costs money, selling returns money
            if action == "buy":
                if side == "yes":
                    cost_cents = yes_price * count
                else:
                    cost_cents = no_price * count
                cash_flow = -cost_cents - fee_cents  # negative = money out
            else:  # sell
                if side == "yes":
                    proceeds_cents = yes_price * count
                else:
                    proceeds_cents = no_price * count
                cash_flow = proceeds_cents - fee_cents  # positive = money in

            k_fill_records.append({
                "dt": dt,
                "month": month_key(dt),
                "ticker": ticker,
                "side": side,
                "action": action,
                "count": count,
                "yes_price": yes_price,
                "no_price": no_price,
                "fee": fee_cents,
                "cash_flow": cash_flow,
            })

        # Sort by date
        k_fill_records.sort(key=lambda x: x["dt"] or datetime.min.replace(tzinfo=timezone.utc))

        if k_fill_records:
            earliest = k_fill_records[0]["dt"]
            latest = k_fill_records[-1]["dt"]
            print(f"\n  Date range: {earliest} → {latest}")

        # Monthly fill summary
        monthly_fills = defaultdict(lambda: {"buys": 0, "sells": 0, "contracts": 0, "fees": 0, "cash_flow": 0})
        for r in k_fill_records:
            m = r["month"]
            monthly_fills[m]["contracts"] += r["count"]
            monthly_fills[m]["fees"] += r["fee"]
            monthly_fills[m]["cash_flow"] += r["cash_flow"]
            if r["action"] == "buy":
                monthly_fills[m]["buys"] += 1
            else:
                monthly_fills[m]["sells"] += 1

        print(f"\n  {'Month':<10} {'Buys':>6} {'Sells':>6} {'Contracts':>10} {'Fees':>10} {'Cash Flow':>12}")
        print(f"  {'─'*10} {'─'*6} {'─'*6} {'─'*10} {'─'*10} {'─'*12}")
        total_k_fees = 0
        total_k_cash_flow = 0
        for m in sorted(monthly_fills.keys()):
            mf = monthly_fills[m]
            fees_d = cents_to_dollars(mf["fees"])
            cf_d = cents_to_dollars(mf["cash_flow"])
            total_k_fees += mf["fees"]
            total_k_cash_flow += mf["cash_flow"]
            print(f"  {m:<10} {mf['buys']:>6} {mf['sells']:>6} {mf['contracts']:>10} ${fees_d:>9.2f} ${cf_d:>11.2f}")

        print(f"  {'─'*10} {'─'*6} {'─'*6} {'─'*10} {'─'*10} {'─'*12}")
        print(f"  {'TOTAL':<10} {'':>6} {'':>6} {'':>10} ${cents_to_dollars(total_k_fees):>9.2f} ${cents_to_dollars(total_k_cash_flow):>11.2f}")

        # ── 3. Analyze Kalshi settlements ────────────────────────
        print("\n" + "=" * 80)
        print("  KALSHI — COMPLETE SETTLEMENT HISTORY")
        print("=" * 80)

        k_settle_records = []
        for s in k_settlements:
            ticker = s.get("market_ticker") or s.get("event_ticker") or s.get("ticker", "")
            revenue = int(s.get("revenue", 0))
            yes_cost = int(s.get("yes_total_cost", 0))
            no_cost = int(s.get("no_total_cost", 0))
            total_cost = yes_cost + no_cost
            # fee_cost is a STRING in DOLLARS (e.g. "0.0400")
            fee_dollars = float(s.get("fee_cost", "0") or "0")
            fee_cost = int(round(fee_dollars * 100))
            result = s.get("market_result", "")
            settled_time = parse_ts(s.get("settled_time"))
            yes_count = int(float(s.get("yes_count_fp", s.get("yes_count", 0))))
            no_count = int(float(s.get("no_count_fp", s.get("no_count", 0))))

            pnl = revenue - total_cost  # Already includes the fee impact

            k_settle_records.append({
                "dt": settled_time,
                "month": month_key(settled_time),
                "ticker": ticker,
                "revenue": revenue,
                "cost": total_cost,
                "fee": fee_cost,
                "pnl": pnl,
                "result": result,
                "yes_count": yes_count,
                "no_count": no_count,
            })

        k_settle_records.sort(key=lambda x: x["dt"] or datetime.min.replace(tzinfo=timezone.utc))

        # Monthly settlement summary
        monthly_settle = defaultdict(lambda: {"count": 0, "revenue": 0, "cost": 0, "fees": 0, "pnl": 0, "wins": 0, "losses": 0})
        for r in k_settle_records:
            m = r["month"]
            monthly_settle[m]["count"] += 1
            monthly_settle[m]["revenue"] += r["revenue"]
            monthly_settle[m]["cost"] += r["cost"]
            monthly_settle[m]["fees"] += r["fee"]
            monthly_settle[m]["pnl"] += r["pnl"]
            if r["pnl"] >= 0:
                monthly_settle[m]["wins"] += 1
            else:
                monthly_settle[m]["losses"] += 1

        print(f"\n  {'Month':<10} {'Mkts':>5} {'W':>4} {'L':>4} {'Revenue':>10} {'Cost':>10} {'Fees':>10} {'P&L':>10}")
        print(f"  {'─'*10} {'─'*5} {'─'*4} {'─'*4} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
        total_revenue = 0
        total_cost = 0
        total_settle_fees = 0
        total_settle_pnl = 0
        for m in sorted(monthly_settle.keys()):
            ms = monthly_settle[m]
            total_revenue += ms["revenue"]
            total_cost += ms["cost"]
            total_settle_fees += ms["fees"]
            total_settle_pnl += ms["pnl"]
            print(f"  {m:<10} {ms['count']:>5} {ms['wins']:>4} {ms['losses']:>4} "
                  f"${cents_to_dollars(ms['revenue']):>9.2f} ${cents_to_dollars(ms['cost']):>9.2f} "
                  f"${cents_to_dollars(ms['fees']):>9.2f} ${cents_to_dollars(ms['pnl']):>9.2f}")

        print(f"  {'─'*10} {'─'*5} {'─'*4} {'─'*4} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
        print(f"  {'TOTAL':<10} {len(k_settle_records):>5} {'':>4} {'':>4} "
              f"${cents_to_dollars(total_revenue):>9.2f} ${cents_to_dollars(total_cost):>9.2f} "
              f"${cents_to_dollars(total_settle_fees):>9.2f} ${cents_to_dollars(total_settle_pnl):>9.2f}")

        # ── 4. Biggest Kalshi winners and losers ─────────────────
        print("\n  TOP 10 KALSHI LOSSES (settled):")
        print(f"  {'Ticker':<25} {'Month':>8} {'P&L':>10} {'Result':>6}")
        print(f"  {'─'*25} {'─'*8} {'─'*10} {'─'*6}")
        sorted_losses = sorted(k_settle_records, key=lambda x: x["pnl"])
        for r in sorted_losses[:10]:
            print(f"  {r['ticker']:<25} {r['month']:>8} ${cents_to_dollars(r['pnl']):>9.2f} {r['result']:>6}")

        print("\n  TOP 10 KALSHI WINS (settled):")
        print(f"  {'Ticker':<25} {'Month':>8} {'P&L':>10} {'Result':>6}")
        print(f"  {'─'*25} {'─'*8} {'─'*10} {'─'*6}")
        sorted_wins = sorted(k_settle_records, key=lambda x: x["pnl"], reverse=True)
        for r in sorted_wins[:10]:
            print(f"  {r['ticker']:<25} {r['month']:>8} ${cents_to_dollars(r['pnl']):>9.2f} {r['result']:>6}")

        # ── 5. Kalshi open positions value ───────────────────────
        print("\n" + "=" * 80)
        print("  KALSHI — OPEN POSITIONS")
        print("=" * 80)

        k_open_exposure = 0
        for p in k_positions:
            ticker = p.get("ticker", "")
            position = p.get("position", 0)
            exposure = p.get("market_exposure", 0)
            k_open_exposure += abs(exposure)
            if abs(position) > 0:
                print(f"  {ticker}: position={position}, exposure={cents_to_dollars(exposure):.2f}")

        k_open_exposure_d = cents_to_dollars(k_open_exposure)
        print(f"\n  Total K open exposure (cost basis): ${k_open_exposure_d:.2f}")

        # ── 6. PM positions ──────────────────────────────────────
        print("\n" + "=" * 80)
        print("  POLYMARKET — POSITIONS & BALANCE")
        print("=" * 80)

        def _extract_dollar(raw):
            """Extract dollar amount from dict like {amount: "1.23"} or raw float/str."""
            if isinstance(raw, dict):
                return float(raw.get("amount", raw.get("value", 0)))
            if raw is None:
                return 0.0
            return float(raw)

        pm_position_value = 0.0
        pm_position_cost = 0.0
        if isinstance(pm_positions, dict):
            for slug, pos_data in pm_positions.items():
                if isinstance(pos_data, dict):
                    net = float(pos_data.get("netPosition", 0))
                    if abs(net) < 0.001:
                        continue
                    cash_val = _extract_dollar(pos_data.get("cost", 0))
                    cv = _extract_dollar(pos_data.get("cashValue", 0))
                    pm_position_value += cv
                    pm_position_cost += abs(cash_val)

                    meta = pos_data.get("marketMetadata", {})
                    team = meta.get("team", {}).get("abbreviation", "") if isinstance(meta, dict) else ""
                    outcome = meta.get("outcome", "") if isinstance(meta, dict) else ""

                    print(f"  {slug[:40]:<40} net={net:>4.0f} cost=${abs(cash_val):>7.2f} value=${cv:>7.2f} {team} {outcome}")
        elif isinstance(pm_positions, list):
            for p in pm_positions:
                if isinstance(p, dict):
                    net = float(p.get("netPosition", p.get("size", 0)))
                    if abs(net) < 0.001:
                        continue
                    cv = _extract_dollar(p.get("cashValue", 0))
                    cost_val = _extract_dollar(p.get("cost", 0))
                    pm_position_value += cv
                    pm_position_cost += abs(cost_val)

                    slug = p.get("slug", p.get("marketSlug", ""))
                    print(f"  {slug[:40]:<40} net={net:>4.0f} cost=${abs(cost_val):>7.2f} value=${cv:>7.2f}")

        print(f"\n  PM cash: ${pm_cash:.2f}")
        print(f"  PM position cost basis: ${pm_position_cost:.2f}")
        print(f"  PM position current value: ${pm_position_value:.2f}")
        print(f"  PM total portfolio: ${pm_cash + pm_position_value:.2f}")

        # ── 7. PM order history ──────────────────────────────────
        if pm_orders:
            print("\n" + "=" * 80)
            print("  POLYMARKET — ORDER HISTORY")
            print("=" * 80)

            pm_monthly = defaultdict(lambda: {"count": 0, "filled": 0, "volume": 0.0})
            for o in pm_orders:
                if isinstance(o, dict):
                    created = parse_ts(o.get("createdAt", o.get("created_at", "")))
                    m = month_key(created)
                    pm_monthly[m]["count"] += 1
                    state = o.get("state", o.get("status", ""))
                    if "FILLED" in str(state).upper():
                        pm_monthly[m]["filled"] += 1
                    qty = float(o.get("cumQuantity", o.get("quantity", 0)))
                    px = float(o.get("avgPx", o.get("price", {}).get("value", 0)) if isinstance(o.get("avgPx"), (int, float, str)) else 0)
                    pm_monthly[m]["volume"] += qty * px if px else 0

            print(f"\n  {'Month':<10} {'Orders':>7} {'Filled':>7} {'Volume':>10}")
            print(f"  {'─'*10} {'─'*7} {'─'*7} {'─'*10}")
            for m in sorted(pm_monthly.keys()):
                pm = pm_monthly[m]
                print(f"  {m:<10} {pm['count']:>7} {pm['filled']:>7} ${pm['volume']:>9.2f}")

        # ── 8. FILL CASH FLOW DECOMPOSITION ──────────────────────
        print("\n" + "=" * 80)
        print("  KALSHI — FILL CASH FLOW DECOMPOSITION")
        print("=" * 80)

        total_buy_cost = 0    # cents, positive = money OUT
        total_sell_rev = 0    # cents, positive = money IN
        total_fill_fee = 0    # cents
        buy_contracts = 0
        sell_contracts = 0
        for r in k_fill_records:
            if r["action"] == "buy":
                if r["side"] == "yes":
                    total_buy_cost += r["yes_price"] * r["count"]
                else:
                    total_buy_cost += r["no_price"] * r["count"]
                buy_contracts += r["count"]
            else:
                if r["side"] == "yes":
                    total_sell_rev += r["yes_price"] * r["count"]
                else:
                    total_sell_rev += r["no_price"] * r["count"]
                sell_contracts += r["count"]
            total_fill_fee += r["fee"]

        net_fill_cash = -total_buy_cost + total_sell_rev - total_fill_fee

        print(f"\n  Total buy cost:     ${cents_to_dollars(total_buy_cost):>10.2f}  ({buy_contracts} contracts across {sum(1 for r in k_fill_records if r['action']=='buy')} fills)")
        print(f"  Total sell revenue: ${cents_to_dollars(total_sell_rev):>10.2f}  ({sell_contracts} contracts across {sum(1 for r in k_fill_records if r['action']=='sell')} fills)")
        print(f"  Total fill fees:    ${cents_to_dollars(total_fill_fee):>10.2f}")
        print(f"  Net fill cash flow: ${cents_to_dollars(net_fill_cash):>10.2f}  (sells - buys - fees)")

        net_settlement_revenue = sum(r["revenue"] for r in k_settle_records)
        net_settlement_fees = sum(r["fee"] for r in k_settle_records)

        print(f"\n  Settlement revenue: ${cents_to_dollars(net_settlement_revenue):>10.2f}  (cash returned at settlement)")
        print(f"  Settlement fees:    ${cents_to_dollars(net_settlement_fees):>10.2f}  (may overlap with fill fees)")

        # ── 9. CHRONOLOGICAL BALANCE REPLAY ──────────────────────
        print("\n" + "=" * 80)
        print("  KALSHI — CHRONOLOGICAL BALANCE REPLAY")
        print("=" * 80)
        print("  (Replaying all fills + settlements to find where deposits must have occurred)")

        # Merge fills and settlements into one timeline
        events = []
        for r in k_fill_records:
            events.append({
                "dt": r["dt"],
                "type": "fill",
                "cash_delta": r["cash_flow"],  # cents
                "desc": f"{r['action']} {r['count']} {r['side']} @ {r['yes_price'] if r['side']=='yes' else r['no_price']}c",
                "ticker": r["ticker"],
            })
        for r in k_settle_records:
            # Settlement cash: revenue comes in, fees go out
            # Note: whether settlement fees are ADDITIONAL to fill fees or the SAME
            # is unclear. We'll try both interpretations.
            events.append({
                "dt": r["dt"],
                "type": "settle",
                "cash_delta": r["revenue"],  # cents (revenue only, fees may already be in fills)
                "desc": f"settle {r['result']} rev={r['revenue']}c cost={r['cost']}c",
                "ticker": r["ticker"],
            })

        events.sort(key=lambda x: x["dt"] or datetime.min.replace(tzinfo=timezone.utc))

        # Replay balance — start at 0, track when it goes negative (= deposit needed)
        balance = 0  # cents
        min_balance = 0
        deposits_needed = []
        prev_month = None

        # Track monthly min balance to identify deposit timing
        monthly_replay = defaultdict(lambda: {"start": 0, "end": 0, "min": float('inf'), "deposits": 0})

        for e in events:
            m = month_key(e["dt"])
            if m != prev_month:
                if prev_month:
                    monthly_replay[prev_month]["end"] = balance
                monthly_replay[m]["start"] = balance
                prev_month = m

            balance += e["cash_delta"]

            if balance < monthly_replay[m]["min"]:
                monthly_replay[m]["min"] = balance

            # If balance goes negative, a deposit must have occurred
            if balance < 0:
                deposit_amount = -balance + 100  # Bring to 100c ($1) minimum
                deposits_needed.append({
                    "dt": e["dt"],
                    "month": m,
                    "amount": deposit_amount,
                    "event": e["desc"],
                    "ticker": e["ticker"],
                })
                balance += deposit_amount
                monthly_replay[m]["deposits"] += deposit_amount

        if prev_month:
            monthly_replay[prev_month]["end"] = balance

        total_implied = sum(d["amount"] for d in deposits_needed)

        print(f"\n  Balance replay found {len(deposits_needed)} points where deposits were needed.")
        print(f"  Total implied deposits: ${cents_to_dollars(total_implied):.2f}")
        print(f"  Final replay balance: ${cents_to_dollars(balance):.2f}")
        print(f"  Actual current cash: ${k_cash:.2f}")
        print(f"  Discrepancy: ${k_cash - cents_to_dollars(balance):.2f}")

        if deposits_needed:
            print(f"\n  DEPOSIT EVENTS (balance went negative, deposit inferred):")
            print(f"  {'Date':<24} {'Amount':>10} {'After Event':>30}")
            print(f"  {'─'*24} {'─'*10} {'─'*30}")
            for d in deposits_needed[:20]:
                print(f"  {str(d['dt'])[:23]:<24} ${cents_to_dollars(d['amount']):>9.2f} {d['event'][:30]}")
            if len(deposits_needed) > 20:
                print(f"  ... and {len(deposits_needed) - 20} more")

        print(f"\n  MONTHLY BALANCE REPLAY:")
        print(f"  {'Month':<10} {'Start':>10} {'Min':>10} {'End':>10} {'Deposits':>10}")
        print(f"  {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")
        for m in sorted(monthly_replay.keys()):
            mr = monthly_replay[m]
            min_val = mr["min"] if mr["min"] != float('inf') else 0
            print(f"  {m:<10} ${cents_to_dollars(mr['start']):>9.2f} ${cents_to_dollars(min_val):>9.2f} "
                  f"${cents_to_dollars(mr['end']):>9.2f} ${cents_to_dollars(mr['deposits']):>9.2f}")

        # ── 10. Load known deposits ──────────────────────────────
        deposits_file = Path(__file__).parent / "deposits.json"
        known_deposits = {"kalshi": 0, "polymarket": 0, "starting_k": 0, "starting_pm": 0}
        if deposits_file.exists():
            with open(deposits_file) as f:
                ddata = json.load(f)
            sb = ddata.get("starting_balances", {})
            known_deposits["starting_k"] = sb.get("kalshi", 0)
            known_deposits["starting_pm"] = sb.get("polymarket", 0)
            for d in ddata.get("deposits", []):
                p = d.get("platform", "")
                amt = d.get("amount", 0)
                if "kalshi" in p.lower():
                    known_deposits["kalshi"] += amt
                elif "poly" in p.lower():
                    known_deposits["polymarket"] += amt
            for w in ddata.get("withdrawals", []):
                p = w.get("platform", "")
                amt = w.get("amount", 0)
                if "kalshi" in p.lower():
                    known_deposits["kalshi"] -= amt
                elif "poly" in p.lower():
                    known_deposits["polymarket"] -= amt

        known_k_total = known_deposits["starting_k"] + known_deposits["kalshi"]
        known_pm_total = known_deposits["starting_pm"] + known_deposits["polymarket"]
        known_total = known_k_total + known_pm_total

        # ── 11. ERA BREAKDOWN ────────────────────────────────────
        print("\n" + "=" * 80)
        print("  P&L BY ERA")
        print("=" * 80)

        arb_start = datetime(2026, 2, 26, tzinfo=timezone.utc)

        # Kalshi fills by era
        pre_arb_fills = [r for r in k_fill_records if r["dt"] and r["dt"] < arb_start]
        arb_fills = [r for r in k_fill_records if r["dt"] and r["dt"] >= arb_start]

        pre_arb_cash = sum(r["cash_flow"] for r in pre_arb_fills)
        pre_arb_fees = sum(r["fee"] for r in pre_arb_fills)
        pre_arb_contracts = sum(r["count"] for r in pre_arb_fills)

        arb_cash = sum(r["cash_flow"] for r in arb_fills)
        arb_fees = sum(r["fee"] for r in arb_fills)
        arb_contracts = sum(r["count"] for r in arb_fills)

        print(f"\n  KALSHI FILLS BY ERA:")
        print(f"  {'Era':<20} {'Fills':>6} {'Contracts':>10} {'Fees':>10} {'Cash Flow':>12}")
        print(f"  {'─'*20} {'─'*6} {'─'*10} {'─'*10} {'─'*12}")
        print(f"  {'Pre-arb (<Feb 26)':<20} {len(pre_arb_fills):>6} {pre_arb_contracts:>10} ${cents_to_dollars(pre_arb_fees):>9.2f} ${cents_to_dollars(pre_arb_cash):>11.2f}")
        print(f"  {'Arb (>=Feb 26)':<20} {len(arb_fills):>6} {arb_contracts:>10} ${cents_to_dollars(arb_fees):>9.2f} ${cents_to_dollars(arb_cash):>11.2f}")

        # Kalshi settlements by era
        pre_arb_settle = [r for r in k_settle_records if r["dt"] and r["dt"] < arb_start]
        arb_settle = [r for r in k_settle_records if r["dt"] and r["dt"] >= arb_start]

        pre_arb_settle_pnl = sum(r["pnl"] for r in pre_arb_settle)
        arb_settle_pnl = sum(r["pnl"] for r in arb_settle)

        print(f"\n  KALSHI SETTLEMENTS BY ERA:")
        print(f"  {'Era':<20} {'Markets':>7} {'Revenue':>10} {'Cost':>10} {'P&L':>10}")
        print(f"  {'─'*20} {'─'*7} {'─'*10} {'─'*10} {'─'*10}")
        pre_rev = sum(r["revenue"] for r in pre_arb_settle)
        pre_cost = sum(r["cost"] for r in pre_arb_settle)
        arb_rev = sum(r["revenue"] for r in arb_settle)
        arb_cost = sum(r["cost"] for r in arb_settle)
        print(f"  {'Pre-arb (<Feb 26)':<20} {len(pre_arb_settle):>7} ${cents_to_dollars(pre_rev):>9.2f} ${cents_to_dollars(pre_cost):>9.2f} ${cents_to_dollars(pre_arb_settle_pnl):>9.2f}")
        print(f"  {'Arb (>=Feb 26)':<20} {len(arb_settle):>7} ${cents_to_dollars(arb_rev):>9.2f} ${cents_to_dollars(arb_cost):>9.2f} ${cents_to_dollars(arb_settle_pnl):>9.2f}")

        # ── 12. DETAILED ARB-ERA SETTLEMENTS ─────────────────────
        print(f"\n  ALL ARB-ERA SETTLEMENTS (Feb 26+):")
        print(f"  {'Ticker':<25} {'Revenue':>8} {'Cost':>8} {'Fee':>6} {'P&L':>8} {'Result':>6}")
        print(f"  {'─'*25} {'─'*8} {'─'*8} {'─'*6} {'─'*8} {'─'*6}")
        for r in arb_settle:
            print(f"  {r['ticker']:<25} ${cents_to_dollars(r['revenue']):>7.2f} ${cents_to_dollars(r['cost']):>7.2f} "
                  f"${cents_to_dollars(r['fee']):>5.2f} ${cents_to_dollars(r['pnl']):>7.2f} {r['result']:>6}")
        arb_settle_total = sum(r["pnl"] for r in arb_settle)
        print(f"  {'─'*25} {'─'*8} {'─'*8} {'─'*6} {'─'*8} {'─'*6}")
        print(f"  {'TOTAL':<25} {'':>8} {'':>8} {'':>6} ${cents_to_dollars(arb_settle_total):>7.2f}")

        # ── 13. FINAL ALL-TIME SUMMARY ───────────────────────────
        print("\n" + "=" * 80)
        print("  FINAL ALL-TIME SUMMARY")
        print("=" * 80)

        # Kalshi total = cash + position value (portfolio_value is JUST positions, not including cash)
        k_pos_value = cents_to_dollars(k_balance_data.get("portfolio_value", 0))
        k_total = k_cash + k_pos_value

        pm_total_portfolio = pm_cash + pm_position_value
        combined = k_total + pm_total_portfolio

        print(f"\n  CURRENT PORTFOLIO:")
        print(f"    Kalshi cash:                ${k_cash:>10.2f}")
        print(f"    Kalshi positions (MTM):     ${k_pos_value:>10.2f}")
        print(f"    Kalshi total:               ${k_total:>10.2f}")
        print(f"    ")
        print(f"    PM cash:                    ${pm_cash:>10.2f}")
        print(f"    PM positions (value):       ${pm_position_value:>10.2f}")
        print(f"    PM total:                   ${pm_total_portfolio:>10.2f}")
        print(f"    ")
        print(f"    COMBINED PORTFOLIO:         ${combined:>10.2f}")

        print(f"\n  CAPITAL IN (from deposits.json):")
        print(f"    K starting bal (Feb 15):    ${known_deposits['starting_k']:>10.2f}")
        print(f"    K additional deposits:      ${known_deposits['kalshi']:>10.2f}")
        print(f"    K total in:                 ${known_k_total:>10.2f}")
        print(f"    PM starting bal (Feb 15):   ${known_deposits['starting_pm']:>10.2f}")
        print(f"    PM additional deposits:     ${known_deposits['polymarket']:>10.2f}")
        print(f"    PM total in:                ${known_pm_total:>10.2f}")
        print(f"    TOTAL CAPITAL IN:           ${known_total:>10.2f}")

        print(f"\n  CAPITAL IN (from balance replay):")
        print(f"    K implied deposits:         ${cents_to_dollars(total_implied):>10.2f}")
        print(f"    (based on {len(deposits_needed)} deposit events inferred from balance going negative)")

        print(f"\n  ═══════════════════════════════════════")
        print(f"  ALL-TIME P&L (using deposits.json):")
        all_time_pnl = combined - known_total
        pct = (all_time_pnl / known_total * 100) if known_total > 0 else 0
        print(f"    ${combined:.2f} - ${known_total:.2f} = ${all_time_pnl:+.2f}  ({pct:+.1f}%)")
        print(f"  ═══════════════════════════════════════")

        print(f"\n  P&L BY PLATFORM:")
        k_pnl = k_total - known_k_total
        pm_pnl = pm_total_portfolio - known_pm_total
        print(f"    Kalshi:  ${k_total:.2f} - ${known_k_total:.2f} = ${k_pnl:+.2f}")
        print(f"    PM:      ${pm_total_portfolio:.2f} - ${known_pm_total:.2f} = ${pm_pnl:+.2f}")

        print(f"\n  P&L BY ERA (Kalshi settlements only — shows where money was made/lost):")
        print(f"    Pre-arb K settlement P&L:   ${cents_to_dollars(pre_arb_settle_pnl):>10.2f}  (Jan 11 - Feb 25)")
        print(f"    Arb-era K settlement P&L:   ${cents_to_dollars(arb_settle_pnl):>10.2f}  (Feb 26+)")
        print(f"    (K settlement losses are offset by PM wins on the other side of arb trades)")

        # ── 14. ALL FEES SUMMARY ─────────────────────────────────
        print(f"\n  ALL-TIME FEES:")
        print(f"    Kalshi fill fees:           ${cents_to_dollars(total_fill_fee):>10.2f}  ({len(k_fill_records)} fills)")
        print(f"    Kalshi settlement fees:     ${cents_to_dollars(net_settlement_fees):>10.2f}  ({len(k_settle_records)} settlements)")
        # Check if fees overlap
        fee_diff = abs(total_fill_fee - net_settlement_fees)
        if fee_diff < total_fill_fee * 0.1:
            print(f"    (Fill and settlement fees are nearly equal — likely the SAME fee reported twice)")
            print(f"    Best estimate total K fees: ${cents_to_dollars(max(total_fill_fee, net_settlement_fees)):>10.2f}")
        else:
            print(f"    Total K fees (combined):    ${cents_to_dollars(total_fill_fee + net_settlement_fees):>10.2f}")

        print("\n" + "=" * 80)
        print("  END OF ALL-TIME FORENSICS")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run())
