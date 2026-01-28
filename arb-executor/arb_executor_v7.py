#!/usr/bin/env python3
"""
DUAL-PLATFORM ARBITRAGE EXECUTOR v7 - DIRECT US EXECUTION
Kalshi + Polymarket US, both executed directly from US.
No partner webhook. Ed25519 auth for Polymarket US API.

HARD LIMITS:
- MAX 20 contracts per trade
- MAX $10 total cost per trade
- buy_max_cost enforces Fill-or-Kill behavior
- Position check AFTER every order attempt
- Only execute PM US if Kalshi position actually exists
"""
import asyncio
import aiohttp
import time
import base64
import json
import re
import os
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, ed25519
from cryptography.hazmat.backends import default_backend

# ============================================================================
# HARD LIMITS - DO NOT CHANGE THESE
# ============================================================================
MAX_CONTRACTS = 20          # Absolute max contracts per trade
MAX_COST_CENTS = 1000       # Absolute max cost in cents ($10)
MIN_CONTRACTS = 5           # Minimum contracts to bother with
MIN_ROI = 5.0               # Minimum ROI percentage
COOLDOWN_SECONDS = 10       # Seconds between trade attempts
# ============================================================================

class ExecutionMode(Enum):
    PAPER = "paper"
    LIVE = "live"

# START IN PAPER MODE - Change to LIVE only when ready
EXECUTION_MODE = ExecutionMode.PAPER

KALSHI_API_KEY = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
KALSHI_PRIVATE_KEY = open('kalshi.pem').read()

# Polymarket US credentials (Ed25519 auth)
PM_US_API_KEY = 'b215c231-f041-4b98-a048-a203acb6573e'
PM_US_SECRET_KEY = 'WL5Q1uEF3vCvESisQ/kLfflRQFNeOOVyZ8uA84l7A0ktsX2NxnB9IYFdGoKWtQq1RygUlFE0KY60r3o6vCSe3w=='

# Fee rates
KALSHI_FEE = 0.01
PM_US_TAKER_FEE_RATE = 0.001  # 0.10% (10 basis points) on notional

# PM US order intents
PM_BUY_YES = 1
PM_SELL_YES = 2
PM_BUY_NO = 3
PM_SELL_NO = 4

# Trade log - load existing trades on startup
def load_trades() -> List[Dict]:
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
            return trades[-1000:] if len(trades) > 1000 else trades
    except (FileNotFoundError, json.JSONDecodeError):
        return []

TRADE_LOG: List[Dict] = load_trades()

@dataclass
class ArbOpportunity:
    timestamp: datetime
    sport: str
    game: str
    team: str
    direction: str
    k_bid: float  # cents
    k_ask: float  # cents
    pm_bid: float  # cents
    pm_ask: float  # cents
    gross_spread: float
    fees: float
    net_spread: float
    size: int  # contracts
    kalshi_ticker: str
    pm_slug: str
    pm_outcome_index: int  # 0 = YES side (outcome[0]), 1 = NO side (outcome[1])

    @property
    def profit(self):
        return (self.net_spread / 100) * self.size

    @property
    def capital(self):
        if self.direction == 'BUY_PM_SELL_K':
            return self.size * (self.pm_ask / 100)
        else:
            return self.size * (self.k_ask / 100)

    @property
    def roi(self):
        return (self.profit / self.capital * 100) if self.capital > 0 else 0

@dataclass
class Position:
    ticker: str
    position: int  # positive = YES, negative = NO
    market_exposure: int


class KalshiAPI:
    BASE_URL = 'https://api.elections.kalshi.com'

    def __init__(self, api_key, private_key):
        self.api_key = api_key
        self.private_key = serialization.load_pem_private_key(
            private_key.encode(), password=None, backend=default_backend()
        )

    def _sign(self, ts, method, path):
        msg = f'{ts}{method}{path}'.encode('utf-8')
        sig = self.private_key.sign(
            msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(sig).decode('utf-8')

    def _headers(self, method, path):
        ts = str(int(time.time() * 1000))
        return {
            'KALSHI-ACCESS-KEY': self.api_key,
            'KALSHI-ACCESS-SIGNATURE': self._sign(ts, method, path),
            'KALSHI-ACCESS-TIMESTAMP': ts,
            'Content-Type': 'application/json'
        }

    async def get_balance(self, session) -> Optional[float]:
        path = '/trade-api/v2/portfolio/balance'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get('balance', 0) / 100
        except Exception as e:
            print(f"   [!] Balance fetch error: {e}")
        return None

    async def get_positions(self, session) -> Dict[str, Position]:
        path = '/trade-api/v2/portfolio/positions?count_filter=position'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    positions = {}
                    for mp in data.get('market_positions', []):
                        if mp.get('position', 0) != 0:
                            positions[mp['ticker']] = Position(
                                ticker=mp['ticker'],
                                position=mp['position'],
                                market_exposure=mp.get('market_exposure', 0)
                            )
                    return positions
        except Exception as e:
            print(f"   [!] Positions fetch error: {e}")
        return {}

    async def get_position_for_ticker(self, session, ticker: str) -> Optional[int]:
        path = f'/trade-api/v2/portfolio/positions?ticker={ticker}&count_filter=position'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    for mp in data.get('market_positions', []):
                        if mp['ticker'] == ticker:
                            return mp.get('position', 0)
                    return 0
        except Exception as e:
            print(f"   [!] Position fetch error: {e}")
        return None

    async def place_order(self, session, ticker: str, side: str, action: str,
                          count: int, price_cents: int) -> Dict:
        # HARD LIMIT ENFORCEMENT
        if count > MAX_CONTRACTS:
            print(f"   [SAFETY] Capping contracts from {count} to {MAX_CONTRACTS}")
            count = MAX_CONTRACTS

        if count < MIN_CONTRACTS:
            return {'success': False, 'error': f'Count {count} below minimum {MIN_CONTRACTS}'}

        if action == 'buy':
            max_cost = count * price_cents
        else:
            max_cost = count * (100 - price_cents)

        if max_cost > MAX_COST_CENTS:
            if action == 'buy':
                count = MAX_COST_CENTS // price_cents
            else:
                count = MAX_COST_CENTS // (100 - price_cents)
            max_cost = count * price_cents if action == 'buy' else count * (100 - price_cents)
            print(f"   [SAFETY] Reduced to {count} contracts (max cost ${max_cost/100:.2f})")

        if count < MIN_CONTRACTS:
            return {'success': False, 'error': f'Count {count} below minimum after cost cap'}

        if EXECUTION_MODE == ExecutionMode.PAPER:
            print(f"   [PAPER] Would place: {action} {count} {side} @ {price_cents}c")
            await asyncio.sleep(0.1)
            return {
                'success': True,
                'fill_count': count,
                'order_id': f'PAPER-{int(time.time()*1000)}',
                'paper': True
            }

        path = '/trade-api/v2/portfolio/orders'
        order_price = price_cents

        payload = {
            'ticker': ticker,
            'action': action,
            'side': side,
            'count': count,
            'type': 'limit',
            'client_order_id': str(uuid.uuid4()),
        }

        if side == 'yes':
            payload['yes_price'] = order_price
        else:
            payload['no_price'] = order_price

        if action == 'buy':
            payload['buy_max_cost'] = count * order_price + (count * 2)

        try:
            print(f"   [ORDER] {action} {count} {side} @ {order_price}c")
            print(f"   [DEBUG] Payload: {payload}")

            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                data = await r.json()
                print(f"   [DEBUG] HTTP Status: {r.status}")
                print(f"   [DEBUG] Response: {data}")

                order = data.get('order', {})
                fill_count = order.get('taker_fill_count', 0) or order.get('fill_count', 0)
                status = order.get('status', '')

                print(f"   [DEBUG] Order status: {status}, fill_count: {fill_count}")

                if r.status in [200, 201] and fill_count > 0:
                    return {
                        'success': True,
                        'fill_count': fill_count,
                        'order_id': order.get('order_id'),
                        'fill_price': order.get('yes_price') if side == 'yes' else order.get('no_price'),
                        'status': status
                    }

                return {
                    'success': False,
                    'fill_count': fill_count,
                    'order_id': order.get('order_id'),
                    'status': status,
                    'error': data.get('error', {}).get('message', f'Status: {status}')
                }

        except Exception as e:
            print(f"   [!] Order error: {e}")
            return {'success': False, 'error': str(e)}

    async def cancel_order(self, session, order_id: str) -> bool:
        if not order_id:
            return False
        path = f'/trade-api/v2/portfolio/orders/{order_id}'
        try:
            async with session.delete(
                f'{self.BASE_URL}{path}',
                headers=self._headers('DELETE', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status in [200, 204]:
                    print(f"   [CANCEL] Order {order_id[:8]}... cancelled")
                    return True
                else:
                    data = await r.json()
                    error_msg = data.get('error', {}).get('message', str(data))
                    if 'not found' in error_msg.lower() or 'already' in error_msg.lower():
                        print(f"   [CANCEL] Order {order_id[:8]}... already gone")
                        return True
                    print(f"   [!] Cancel failed: {error_msg}")
                    return False
        except Exception as e:
            print(f"   [!] Cancel error: {e}")
            return False

    async def get_open_orders(self, session, ticker: str = None) -> List[Dict]:
        path = '/trade-api/v2/portfolio/orders?status=resting'
        if ticker:
            path += f'&ticker={ticker}'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    orders = data.get('orders', [])
                    return [{
                        'order_id': o.get('order_id'),
                        'ticker': o.get('ticker'),
                        'action': o.get('action'),
                        'side': o.get('side'),
                        'count': o.get('remaining_count', o.get('count', 0)),
                        'price': o.get('yes_price') or o.get('no_price'),
                        'created_time': o.get('created_time')
                    } for o in orders]
                else:
                    print(f"   [!] Get orders failed: HTTP {r.status}")
        except Exception as e:
            print(f"   [!] Get orders error: {e}")
        return []

    async def cancel_all_orders_for_ticker(self, session, ticker: str) -> int:
        cancelled = 0
        for attempt in range(3):
            orders = await self.get_open_orders(session, ticker)
            if not orders:
                if attempt == 0:
                    print(f"   [CLEANUP] No open orders for {ticker}")
                break
            print(f"   [CLEANUP] Found {len(orders)} open orders for {ticker}, cancelling...")
            for order in orders:
                order_id = order.get('order_id')
                if order_id:
                    success = await self.cancel_order(session, order_id)
                    if success:
                        cancelled += 1
                    await asyncio.sleep(0.05)
            await asyncio.sleep(0.2)
        if cancelled > 0:
            print(f"   [CLEANUP] Cancelled {cancelled} orders for {ticker}")
        return cancelled

    async def cancel_all_open_orders(self, session) -> int:
        cancelled = 0
        orders = await self.get_open_orders(session)
        if not orders:
            print("[CLEANUP] No open Kalshi orders found")
            return 0
        print(f"[CLEANUP] Found {len(orders)} total open Kalshi orders, cancelling all...")
        for order in orders:
            order_id = order.get('order_id')
            ticker = order.get('ticker', 'unknown')
            if order_id:
                print(f"   [CANCEL] {ticker}: order {order_id[:8]}...")
                success = await self.cancel_order(session, order_id)
                if success:
                    cancelled += 1
                await asyncio.sleep(0.05)
        print(f"[CLEANUP] Cancelled {cancelled} Kalshi orders total")
        return cancelled


class PolymarketUSAPI:
    """Polymarket US API client with Ed25519 authentication"""
    BASE_URL = 'https://api.polymarket.us'

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        secret_bytes = base64.b64decode(secret_key)
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_bytes[:32])

    def _sign(self, ts: str, method: str, path: str) -> str:
        """Sign: message = timestamp + method + path (no query params)"""
        message = f'{ts}{method}{path}'.encode('utf-8')
        signature = self.private_key.sign(message)
        return base64.b64encode(signature).decode('utf-8')

    def _headers(self, method: str, path: str) -> Dict:
        ts = str(int(time.time() * 1000))
        return {
            'X-PM-Access-Key': self.api_key,
            'X-PM-Timestamp': ts,
            'X-PM-Signature': self._sign(ts, method, path),
            'Content-Type': 'application/json'
        }

    async def get_balance(self, session) -> Optional[float]:
        """Get USD balance"""
        path = '/v1/account/balances'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    for b in data.get('balances', []):
                        if b.get('currency') == 'USD':
                            return float(b.get('buyingPower', b.get('currentBalance', 0)))
                else:
                    body = await r.text()
                    print(f"   [!] PM US balance HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US balance error: {e}")
        return None

    async def get_positions(self, session, market_slug: str = None) -> Dict:
        """Get portfolio positions"""
        path = '/v1/portfolio/positions'
        query = f'?market={market_slug}' if market_slug else ''
        try:
            async with session.get(
                f'{self.BASE_URL}{path}{query}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get('positions', {})
                else:
                    body = await r.text()
                    print(f"   [!] PM US positions HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US positions error: {e}")
        return {}

    async def get_moneyline_markets(self, session) -> List[Dict]:
        """Fetch all active markets (filter for sports in code)"""
        path = '/v1/markets'
        # Note: sportsMarketTypes filter doesn't work, fetch all and filter in code
        query = '?active=true&closed=false&limit=200'
        try:
            async with session.get(
                f'{self.BASE_URL}{path}{query}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get('markets', [])
                else:
                    body = await r.text()
                    print(f"   [!] PM US markets HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US markets error: {e}")
        return []

    async def place_order(self, session, market_slug: str, intent: int,
                          price: float, quantity: int, tif: int = 3,
                          sync: bool = True) -> Dict:
        """
        Place order on PM US.
        intent: 1=BUY_YES, 2=SELL_YES, 3=BUY_NO, 4=SELL_NO
        tif: 1=GTC, 2=GTD, 3=IOC, 4=FOK
        price: in dollars (e.g., 0.55)
        """
        # HARD LIMIT ENFORCEMENT
        if quantity > MAX_CONTRACTS:
            print(f"   [SAFETY] PM US: Capping contracts from {quantity} to {MAX_CONTRACTS}")
            quantity = MAX_CONTRACTS
        if quantity < MIN_CONTRACTS:
            return {'success': False, 'error': f'Quantity {quantity} below minimum'}

        max_cost_dollars = price * quantity
        if max_cost_dollars * 100 > MAX_COST_CENTS:
            quantity = int(MAX_COST_CENTS / (price * 100))
            if quantity < MIN_CONTRACTS:
                return {'success': False, 'error': 'Quantity below minimum after cost cap'}
            print(f"   [SAFETY] PM US: Reduced to {quantity} contracts")

        intent_names = {1: 'BUY_YES', 2: 'SELL_YES', 3: 'BUY_NO', 4: 'SELL_NO'}

        if EXECUTION_MODE == ExecutionMode.PAPER:
            print(f"   [PAPER] PM US: {intent_names[intent]} {quantity} @ ${price:.2f} on {market_slug}")
            await asyncio.sleep(0.1)
            return {
                'success': True,
                'fill_count': quantity,
                'fill_price': price,
                'order_id': f'PM-PAPER-{int(time.time()*1000)}',
                'paper': True
            }

        path = '/v1/orders'
        payload = {
            'market_slug': market_slug,
            'intent': intent,
            'type': 1,  # LIMIT
            'price': {'value': f'{price:.2f}', 'currency': 'USD'},
            'quantity': quantity,
            'tif': tif,
            'manualOrderIndicator': 2,  # AUTOMATIC
            'synchronousExecution': sync,
        }

        try:
            print(f"   [PM ORDER] {intent_names[intent]} {quantity} @ ${price:.2f} on {market_slug}")
            print(f"   [DEBUG] PM Payload: {json.dumps(payload)}")

            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                data = await r.json()
                print(f"   [DEBUG] PM HTTP Status: {r.status}")
                print(f"   [DEBUG] PM Response: {data}")

                if r.status == 200:
                    order_id = data.get('id')
                    executions = data.get('executions', [])

                    # Sum fills from executions
                    total_filled = 0
                    fill_price = None
                    for ex in executions:
                        ex_type = ex.get('type')
                        # 1=PARTIAL_FILL, 2=FILL
                        if ex_type in [1, 2]:
                            total_filled += ex.get('lastShares', 0)
                            last_px = ex.get('lastPx', {})
                            if last_px:
                                fill_price = float(last_px.get('value', 0))

                    return {
                        'success': total_filled > 0,
                        'fill_count': total_filled,
                        'order_id': order_id,
                        'fill_price': fill_price,
                        'executions': executions
                    }
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {r.status}: {json.dumps(data)[:200]}'
                    }
        except Exception as e:
            print(f"   [!] PM US order error: {e}")
            return {'success': False, 'error': str(e)}

    async def cancel_order(self, session, order_id: str, market_slug: str) -> bool:
        """Cancel a specific order"""
        path = f'/v1/order/{order_id}/cancel'
        try:
            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json={'market_slug': market_slug},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    print(f"   [PM CANCEL] Order {order_id[:12]}... cancelled")
                    return True
                else:
                    body = await r.text()
                    print(f"   [!] PM cancel failed: HTTP {r.status}: {body[:200]}")
                    return False
        except Exception as e:
            print(f"   [!] PM cancel error: {e}")
            return False

    async def cancel_all_orders(self, session, slugs: List[str] = None) -> List[str]:
        """Cancel all open orders, optionally filtered by market slugs"""
        path = '/v1/orders/open/cancel'
        try:
            payload = {'slugs': slugs or []}
            async with session.post(
                f'{self.BASE_URL}{path}',
                headers=self._headers('POST', path),
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    cancelled = data.get('canceledOrderIds', [])
                    if cancelled:
                        print(f"[CLEANUP] Cancelled {len(cancelled)} PM US orders")
                    return cancelled
                else:
                    body = await r.text()
                    print(f"   [!] PM cancel all failed: HTTP {r.status}: {body[:200]}")
        except Exception as e:
            print(f"   [!] PM US cancel all error: {e}")
        return []

    async def get_open_orders(self, session, slugs: List[str] = None) -> List[Dict]:
        """Get all open orders"""
        path = '/v1/orders/open'
        query = ''
        if slugs:
            query = '?' + '&'.join(f'slugs={s}' for s in slugs)
        try:
            async with session.get(
                f'{self.BASE_URL}{path}{query}',
                headers=self._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    data = await r.json()
                    return data.get('orders', [])
        except Exception as e:
            print(f"   [!] PM US open orders error: {e}")
        return []


def get_pm_execution_params(arb: ArbOpportunity) -> tuple:
    """
    Determine PM US order intent and price for the given arb.

    For BUY_PM_SELL_K: go long on PM for this team.
    For BUY_K_SELL_PM: short this team on PM by buying the opposite outcome.

    Returns (intent, price_dollars)
    """
    if arb.direction == 'BUY_PM_SELL_K':
        # Buy this team on PM
        if arb.pm_outcome_index == 0:
            intent = PM_BUY_YES
        else:
            intent = PM_BUY_NO
        price = arb.pm_ask / 100  # Cost to buy in dollars
    else:
        # BUY_K_SELL_PM: short this team by buying the opposite outcome
        if arb.pm_outcome_index == 0:
            intent = PM_BUY_NO   # Buy opposite (outcome[1])
        else:
            intent = PM_BUY_YES  # Buy opposite (outcome[0])
        # Cost of opposite = (100 - team_price) / 100
        price = (100 - arb.pm_bid) / 100

    return intent, price


def log_trade(arb: ArbOpportunity, k_result: Dict, pm_result: Dict, status: str):
    """Log trade details"""
    global TRADE_LOG

    if EXECUTION_MODE == ExecutionMode.PAPER:
        display_status = 'PAPER'
    else:
        display_status = status

    trade = {
        'timestamp': datetime.now().isoformat(),
        'sport': arb.sport,
        'game': arb.game,
        'team': arb.team,
        'direction': arb.direction,
        'intended_size': arb.size,
        'k_fill_count': k_result.get('fill_count', 0),
        'k_fill_price': k_result.get('fill_price'),
        'k_order_id': k_result.get('order_id'),
        'pm_fill_count': pm_result.get('fill_count', 0),
        'pm_fill_price': pm_result.get('fill_price'),
        'pm_order_id': pm_result.get('order_id'),
        'pm_slug': arb.pm_slug,
        'pm_success': pm_result.get('success', False),
        'pm_error': pm_result.get('error'),
        'status': display_status,
        'raw_status': status,
        'execution_mode': EXECUTION_MODE.value,
        'expected_profit': arb.profit,
        'roi': arb.roi
    }
    TRADE_LOG.append(trade)

    if len(TRADE_LOG) > 1000:
        TRADE_LOG = TRADE_LOG[-1000:]

    try:
        with open('trades.json', 'w') as f:
            json.dump(TRADE_LOG, f, indent=2)
    except:
        pass


def export_market_data(all_games: Dict, arbs: List[ArbOpportunity]):
    """Export market mapping, spread, and volume data for dashboard"""
    global VOLUME_HISTORY

    kalshi_games = []
    spreads = []
    match_stats = {}
    volume_by_sport = {}

    for cfg in SPORTS_CONFIG:
        sport = cfg['sport'].upper()
        sport_games = all_games.get(cfg['sport'], {})
        matched_count = 0
        sport_k_volume = 0
        sport_pm_volume = 0

        for gid, game in sport_games.items():
            for team, p in game['teams'].items():
                ticker = game['tickers'].get(team, '')
                has_pm = 'pm_ask' in p
                if has_pm:
                    matched_count += 1

                # Aggregate volume
                k_vol = p.get('k_volume', 0) or 0
                pm_vol = p.get('pm_volume', 0) or 0
                sport_k_volume += k_vol
                sport_pm_volume += pm_vol

                kalshi_games.append({
                    'sport': sport, 'game': gid, 'team': team, 'ticker': ticker,
                    'k_bid': p.get('k_bid', 0), 'k_ask': p.get('k_ask', 0),
                    'k_volume': k_vol, 'pm_volume': pm_vol,
                    'pm_slug': p.get('pm_slug'), 'pm_bid': p.get('pm_bid'),
                    'pm_ask': p.get('pm_ask'), 'matched': has_pm, 'date': game.get('date')
                })

                if has_pm:
                    spread = p['k_bid'] - p['pm_ask']
                    roi = (spread / p['pm_ask'] * 100) if p['pm_ask'] > 0 else 0
                    spreads.append({
                        'sport': sport, 'game': gid, 'team': team,
                        'k_bid': p['k_bid'], 'k_ask': p['k_ask'],
                        'pm_bid': p['pm_bid'], 'pm_ask': p['pm_ask'],
                        'spread': spread, 'roi': roi,
                        'status': 'ARB' if roi >= 5 else 'CLOSE' if roi >= 2 else 'NO_EDGE',
                        'pm_slug': p['pm_slug'], 'ticker': ticker
                    })

        total = len(sport_games)
        match_stats[sport] = {'matched': matched_count // 2, 'total': total,
                             'rate': (matched_count // 2 / total * 100) if total else 0}
        volume_by_sport[sport] = {
            'kalshi': sport_k_volume,
            'pm': sport_pm_volume,
            'total': sport_k_volume + sport_pm_volume
        }

    spreads.sort(key=lambda x: -x['roi'])

    # Calculate total volume
    total_k_volume = sum(v['kalshi'] for v in volume_by_sport.values())
    total_pm_volume = sum(v['pm'] for v in volume_by_sport.values())
    total_volume = total_k_volume + total_pm_volume

    # Add to volume history
    now = datetime.now()
    VOLUME_HISTORY.append({
        'timestamp': now.isoformat(),
        'kalshi': total_k_volume,
        'pm': total_pm_volume,
        'total': total_volume
    })

    # Keep only last 24 hours
    if len(VOLUME_HISTORY) > MAX_VOLUME_HISTORY:
        VOLUME_HISTORY = VOLUME_HISTORY[-MAX_VOLUME_HISTORY:]

    data = {
        'timestamp': now.isoformat(),
        'kalshi_games': kalshi_games, 'match_stats': match_stats,
        'spreads': spreads, 'total_kalshi': len(kalshi_games) // 2,
        'total_matched': sum(s['matched'] for s in match_stats.values()),
        'volume_by_sport': volume_by_sport,
        'volume_history': VOLUME_HISTORY[-50:],  # Last 50 data points for chart
        'total_volume': {
            'kalshi': total_k_volume,
            'pm': total_pm_volume,
            'total': total_volume
        }
    }

    try:
        with open('market_data.json', 'w') as f:
            json.dump(data, f)
    except:
        pass


# Market data mappings
MONTH_MAP = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06',
             'JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}

NBA_K2PM = {'ATL':'atl','BOS':'bos','BKN':'bkn','CHA':'cha','CHI':'chi','CLE':'cle',
            'DAL':'dal','DEN':'den','DET':'det','GSW':'gsw','HOU':'hou','IND':'ind',
            'LAC':'lac','LAL':'lal','MEM':'mem','MIA':'mia','MIL':'mil','MIN':'min',
            'NOP':'nop','NYK':'nyk','OKC':'okc','ORL':'orl','PHI':'phi','PHX':'phx',
            'POR':'por','SAC':'sac','SAS':'sas','TOR':'tor','UTA':'uta','WAS':'was'}

NBA_PM2K = {'Hawks':'ATL','Celtics':'BOS','Nets':'BKN','Hornets':'CHA','Bulls':'CHI',
            'Cavaliers':'CLE','Mavericks':'DAL','Nuggets':'DEN','Pistons':'DET',
            'Warriors':'GSW','Rockets':'HOU','Pacers':'IND','Clippers':'LAC',
            'Lakers':'LAL','Grizzlies':'MEM','Heat':'MIA','Bucks':'MIL',
            'Timberwolves':'MIN','Pelicans':'NOP','Knicks':'NYK','Thunder':'OKC',
            'Magic':'ORL','76ers':'PHI','Suns':'PHX','Trail Blazers':'POR',
            'Kings':'SAC','Spurs':'SAS','Raptors':'TOR','Jazz':'UTA','Wizards':'WAS'}

NHL_K2PM = {'ANA':'ana','BOS':'bos','BUF':'buf','CGY':'cgy','CAR':'car','CHI':'chi',
            'COL':'col','CBJ':'cbj','DAL':'dal','DET':'det','EDM':'edm','FLA':'fla',
            'LA':'la','MIN':'min','MTL':'mtl','NSH':'nsh','NJ':'nj','NYI':'nyi',
            'NYR':'nyr','OTT':'ott','PHI':'phi','PIT':'pit','SJ':'sj','SEA':'sea',
            'STL':'stl','TB':'tb','TOR':'tor','VAN':'van','VGK':'vgk','WPG':'wpg','WSH':'wsh'}

NHL_PM2K = {'Ducks':'ANA','Bruins':'BOS','Sabres':'BUF','Flames':'CGY','Hurricanes':'CAR',
            'Blackhawks':'CHI','Avalanche':'COL','Blue Jackets':'CBJ','Stars':'DAL',
            'Red Wings':'DET','Oilers':'EDM','Panthers':'FLA','Kings':'LA','Wild':'MIN',
            'Canadiens':'MTL','Predators':'NSH','Devils':'NJ','Islanders':'NYI',
            'Rangers':'NYR','Senators':'OTT','Flyers':'PHI','Penguins':'PIT','Sharks':'SJ',
            'Kraken':'SEA','Blues':'STL','Lightning':'TB','Maple Leafs':'TOR',
            'Canucks':'VAN','Golden Knights':'VGK','Jets':'WPG','Capitals':'WSH'}

SPORTS_CONFIG = [
    {'sport':'nba','series':'KXNBAGAME','k2pm':NBA_K2PM,'pm2k':NBA_PM2K},
    {'sport':'nhl','series':'KXNHLGAME','k2pm':NHL_K2PM,'pm2k':NHL_PM2K},
]

# PM US market cache: {cache_key: {slug, teams: {K_ABBR: {price, outcome_index}}, volume}}
PM_US_MARKET_CACHE = {}

# Volume history for trends (stores last 24h of snapshots)
VOLUME_HISTORY: List[Dict] = []
MAX_VOLUME_HISTORY = 288  # 24 hours at 5-minute intervals


def parse_gid(gid):
    m = re.match(r'(\d{2})([A-Z]{3})(\d{2})([A-Z]+)', gid)
    if m:
        date = f'20{m.group(1)}-{MONTH_MAP.get(m.group(2),"01")}-{m.group(3)}'
        teams = m.group(4)
        return date, teams[:len(teams)//2], teams[len(teams)//2:]
    return None, None, None


def map_outcome_to_kalshi(outcome_name: str, pm2k: Dict) -> Optional[str]:
    """Map a PM US outcome name to a Kalshi team abbreviation via substring match"""
    for pm_name, k_abbr in pm2k.items():
        if pm_name.lower() in outcome_name.lower():
            return k_abbr
    return None


async def fetch_kalshi_markets(session, kalshi_api):
    """Fetch all sports markets from Kalshi"""
    async def fetch_series(series):
        path = f'/trade-api/v2/markets?status=open&series_ticker={series}&limit=200'
        try:
            async with session.get(
                f'{kalshi_api.BASE_URL}{path}',
                headers=kalshi_api._headers('GET', path),
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status == 200:
                    return series, (await r.json()).get('markets', [])
        except:
            pass
        return series, []

    results = await asyncio.gather(*[fetch_series(c['series']) for c in SPORTS_CONFIG])
    return {s: m for s, m in results}


async def fetch_pm_us_markets(session, pm_api):
    """
    Fetch PM US moneyline markets and build the match cache.
    Returns count of matched markets.
    """
    global PM_US_MARKET_CACHE

    markets = await pm_api.get_moneyline_markets(session)
    if not markets:
        return 0

    matched = 0
    for market in markets:
        slug = market.get('slug', '')
        outcomes_raw = market.get('outcomes', '[]')
        prices_raw = market.get('outcomePrices', '[]')
        game_time = market.get('gameStartTime', '')

        # Parse JSON strings if needed
        try:
            outcomes = json.loads(outcomes_raw) if isinstance(outcomes_raw, str) else outcomes_raw
            prices = json.loads(prices_raw) if isinstance(prices_raw, str) else prices_raw
        except (json.JSONDecodeError, TypeError):
            continue

        # Only handle 2-outcome moneyline markets
        if not outcomes or not prices or len(outcomes) != 2 or len(prices) != 2:
            continue

        # Try to match outcomes to known teams across all sports
        for cfg in SPORTS_CONFIG:
            team_0 = map_outcome_to_kalshi(outcomes[0], cfg['pm2k'])
            team_1 = map_outcome_to_kalshi(outcomes[1], cfg['pm2k'])

            if team_0 and team_1:
                # Extract game date from gameStartTime
                game_date = None
                if game_time:
                    try:
                        # Handle ISO format with optional timezone
                        dt_str = game_time.replace('Z', '+00:00')
                        if 'T' in dt_str:
                            dt = datetime.fromisoformat(dt_str)
                        else:
                            dt = datetime.strptime(dt_str[:10], '%Y-%m-%d')
                        game_date = dt.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass

                if not game_date:
                    continue

                sport = cfg['sport']
                sorted_teams = sorted([team_0, team_1])
                cache_key = f"{sport}:{sorted_teams[0]}-{sorted_teams[1]}:{game_date}"

                price_0 = int(float(prices[0]) * 100)  # Convert to cents
                price_1 = int(float(prices[1]) * 100)

                PM_US_MARKET_CACHE[cache_key] = {
                    'slug': slug,
                    'teams': {
                        team_0: {'price': price_0, 'outcome_index': 0},
                        team_1: {'price': price_1, 'outcome_index': 1}
                    },
                    'volume': market.get('volumeNum', 0) or market.get('volume24hr', 0) or 0
                }
                matched += 1
                break

    return matched


async def run_executor():
    print("=" * 70)
    print("ARB EXECUTOR v7 - DIRECT US EXECUTION")
    print(f"Mode: {EXECUTION_MODE.value.upper()}")
    print(f"HARD LIMITS: Max {MAX_CONTRACTS} contracts, Max ${MAX_COST_CENTS/100:.0f} per trade")
    print(f"Cooldown: {COOLDOWN_SECONDS}s between trades")
    print(f"PM US Fee: {PM_US_TAKER_FEE_RATE*100:.2f}% taker | Kalshi Fee: {KALSHI_FEE*100:.0f}%")
    print("=" * 70)

    if EXECUTION_MODE == ExecutionMode.PAPER:
        print("\n*** PAPER TRADING MODE - NO REAL ORDERS ***\n")

    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
    pm_api = PolymarketUSAPI(PM_US_API_KEY, PM_US_SECRET_KEY)

    last_trade_time = 0
    total_trades = 0
    total_profit = 0.0

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
        # Get initial balances
        k_balance = await kalshi_api.get_balance(session)
        pm_balance = await pm_api.get_balance(session)

        if k_balance is not None:
            print(f"Kalshi Balance: ${k_balance:.2f}")
        else:
            print("WARNING: Could not fetch Kalshi balance")

        if pm_balance is not None:
            print(f"PM US Balance: ${pm_balance:.2f}")
        else:
            print("WARNING: Could not fetch PM US balance (check API key)")

        # Get initial Kalshi positions
        k_positions = await kalshi_api.get_positions(session)
        if k_positions:
            print(f"Kalshi positions: {len(k_positions)}")
            for ticker, pos in k_positions.items():
                print(f"  {ticker}: {pos.position} contracts")

        # Get initial PM US positions
        pm_positions = await pm_api.get_positions(session)
        if pm_positions:
            print(f"PM US positions: {len(pm_positions)}")

        # CRITICAL: Cancel ALL stale orders on startup
        if EXECUTION_MODE == ExecutionMode.LIVE:
            print("\n[STARTUP CLEANUP] Checking for stale orders...")
            k_cancelled = await kalshi_api.cancel_all_open_orders(session)
            pm_cancelled = await pm_api.cancel_all_orders(session)
            if k_cancelled > 0:
                print(f"[STARTUP CLEANUP] Cancelled {k_cancelled} stale Kalshi orders")
            if pm_cancelled:
                print(f"[STARTUP CLEANUP] Cancelled {len(pm_cancelled)} stale PM US orders")
            print("[STARTUP CLEANUP] Done - clean slate\n")

        scan_num = 0

        while True:
            scan_num += 1
            t0 = time.time()

            # Fetch markets from both platforms in parallel
            kalshi_task = fetch_kalshi_markets(session, kalshi_api)
            pm_us_task = fetch_pm_us_markets(session, pm_api)
            kalshi_data, pm_us_matched = await asyncio.gather(kalshi_task, pm_us_task)

            # Build game data from Kalshi markets
            all_games = {}
            for cfg in SPORTS_CONFIG:
                sport = cfg['sport']
                all_games[sport] = {}

                for m in kalshi_data.get(cfg['series'], []):
                    parts = m.get('ticker', '').split('-')
                    if len(parts) >= 3:
                        gid, team = parts[1], parts[2]
                        if team == 'TIE':
                            continue

                        if gid not in all_games[sport]:
                            date, _, _ = parse_gid(gid)
                            all_games[sport][gid] = {
                                'date': date,
                                'teams': {},
                                'tickers': {}
                            }

                        all_games[sport][gid]['teams'][team] = {
                            'k_bid': m.get('yes_bid', 0),
                            'k_ask': m.get('yes_ask', 0),
                            'k_volume': m.get('volume', 0) or 0
                        }
                        all_games[sport][gid]['tickers'][team] = m.get('ticker')

            # Match Kalshi games to PM US markets
            total_matched = 0
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    if len(game['teams']) < 2 or not game['date']:
                        continue

                    teams = sorted(list(game['teams'].keys()))
                    cache_key = f"{cfg['sport']}:{teams[0]}-{teams[1]}:{game['date']}"

                    pm_market = PM_US_MARKET_CACHE.get(cache_key)
                    if pm_market:
                        total_matched += 1
                        for team in game['teams']:
                            if team in pm_market['teams']:
                                pm_info = pm_market['teams'][team]
                                team_price = pm_info['price']
                                outcome_idx = pm_info['outcome_index']

                                # Get opposite team's price for implied bid
                                opposite_teams = [t for t in pm_market['teams'] if t != team]
                                opposite_price = pm_market['teams'][opposite_teams[0]]['price'] if opposite_teams else (100 - team_price)

                                game['teams'][team]['pm_ask'] = team_price  # Cost to buy this team
                                game['teams'][team]['pm_bid'] = 100 - opposite_price  # Implied sell price
                                game['teams'][team]['pm_bid_size'] = MAX_CONTRACTS  # Assume liquidity
                                game['teams'][team]['pm_ask_size'] = MAX_CONTRACTS
                                game['teams'][team]['pm_slug'] = pm_market['slug']
                                game['teams'][team]['pm_outcome_index'] = outcome_idx
                                game['teams'][team]['pm_volume'] = pm_market.get('volume', 0)

            # Find arbs
            arbs = []
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    for team, p in game['teams'].items():
                        if 'pm_ask' not in p:
                            continue

                        kb = p['k_bid']  # cents
                        ka = p['k_ask']  # cents
                        pb = p['pm_bid']  # cents (implied sell)
                        pa = p['pm_ask']  # cents (cost to buy)

                        if kb == 0 or ka == 0:
                            continue

                        # Direction 1: Buy PM, Sell Kalshi
                        # Profit = k_bid - pm_ask - fees
                        gross1 = kb - pa
                        # PM US fee: 0.10% on notional (pm_ask)
                        # Kalshi fee: 1 cent per contract
                        pm_fee1 = PM_US_TAKER_FEE_RATE * pa
                        k_fee1 = KALSHI_FEE * 100
                        fees1 = int(pm_fee1 + k_fee1)
                        net1 = gross1 - fees1

                        if net1 > 0:
                            sz = min(p.get('pm_ask_size', 0), MAX_CONTRACTS)
                            max_by_cost = MAX_COST_CENTS // pa if pa > 0 else 0
                            sz = min(sz, max_by_cost)

                            if sz >= MIN_CONTRACTS:
                                arbs.append(ArbOpportunity(
                                    timestamp=datetime.now(),
                                    sport=cfg['sport'].upper(),
                                    game=gid,
                                    team=team,
                                    direction='BUY_PM_SELL_K',
                                    k_bid=kb,
                                    k_ask=ka,
                                    pm_bid=pb,
                                    pm_ask=pa,
                                    gross_spread=gross1,
                                    fees=fees1,
                                    net_spread=net1,
                                    size=sz,
                                    kalshi_ticker=game['tickers'].get(team, ''),
                                    pm_slug=p.get('pm_slug', ''),
                                    pm_outcome_index=p.get('pm_outcome_index', 0)
                                ))

                        # Direction 2: Buy Kalshi, Sell PM
                        # Profit = pm_bid - k_ask - fees
                        gross2 = pb - ka
                        # PM US fee: 0.10% on opposite side notional (100 - pm_bid)
                        pm_fee2 = PM_US_TAKER_FEE_RATE * (100 - pb)
                        k_fee2 = KALSHI_FEE * 100
                        fees2 = int(pm_fee2 + k_fee2)
                        net2 = gross2 - fees2

                        if net2 > 0:
                            sz = min(p.get('pm_bid_size', 0), MAX_CONTRACTS)
                            max_by_cost = MAX_COST_CENTS // ka if ka > 0 else 0
                            sz = min(sz, max_by_cost)

                            if sz >= MIN_CONTRACTS:
                                arbs.append(ArbOpportunity(
                                    timestamp=datetime.now(),
                                    sport=cfg['sport'].upper(),
                                    game=gid,
                                    team=team,
                                    direction='BUY_K_SELL_PM',
                                    k_bid=kb,
                                    k_ask=ka,
                                    pm_bid=pb,
                                    pm_ask=pa,
                                    gross_spread=gross2,
                                    fees=fees2,
                                    net_spread=net2,
                                    size=sz,
                                    kalshi_ticker=game['tickers'].get(team, ''),
                                    pm_slug=p.get('pm_slug', ''),
                                    pm_outcome_index=p.get('pm_outcome_index', 0)
                                ))

            # Filter by ROI
            exec_arbs = [a for a in arbs if a.roi >= MIN_ROI]
            exec_arbs.sort(key=lambda x: -x.roi)

            scan_time = (time.time() - t0) * 1000

            # Display
            print("=" * 70)
            print(f"v7 DIRECT US | Scan #{scan_num} | {datetime.now().strftime('%H:%M:%S')} | {scan_time:.0f}ms")
            print(f"Mode: {EXECUTION_MODE.value.upper()} | Trades: {total_trades} | Profit: ${total_profit:.2f}")
            print("=" * 70)

            total_games = sum(len(all_games[c['sport']]) for c in SPORTS_CONFIG)

            print(f"\n[i] Kalshi Games: {total_games} | PM US Matched: {total_matched} | PM US Markets: {pm_us_matched}")
            print(f"[i] Found {len(arbs)} arbs, {len(exec_arbs)} pass {MIN_ROI}% ROI threshold")

            # Export market data for dashboard
            export_market_data(all_games, arbs)

            # Execute if we have arbs and cooldown passed
            if exec_arbs and (time.time() - last_trade_time) >= COOLDOWN_SECONDS:
                best = exec_arbs[0]

                print(f"\n[!] BEST ARB: {best.sport} {best.game} {best.team}")
                print(f"    Direction: {best.direction}")
                print(f"    K: {best.k_bid}/{best.k_ask}c | PM: {best.pm_bid}/{best.pm_ask}c")
                print(f"    Size: {best.size} | Profit: ${best.profit:.2f} | ROI: {best.roi:.1f}%")
                print(f"    PM Slug: {best.pm_slug} | Outcome Index: {best.pm_outcome_index}")

                # Determine Kalshi order params
                if best.direction == 'BUY_PM_SELL_K':
                    k_action = 'sell'
                    k_price = best.k_bid
                else:
                    k_action = 'buy'
                    k_price = best.k_ask

                # Get position BEFORE order
                pre_position = await kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
                print(f"\n[>>] PRE-TRADE: Kalshi Position = {pre_position}")

                # =============================================================
                # BULLETPROOF ORDER BOOK SWEEP (Kalshi side - same as v6)
                # =============================================================
                MAX_PRICE_LEVELS = 10
                actual_fill = 0
                fill_price = k_price
                k_result = {}
                placed_order_ids = []

                try:
                    for price_offset in range(MAX_PRICE_LEVELS + 1):
                        if k_action == 'buy':
                            try_price = k_price + price_offset
                        else:
                            try_price = k_price - price_offset

                        if try_price < 1 or try_price > 99:
                            print(f"   [X] Price {try_price}c out of bounds, stopping sweep")
                            break

                        if k_action == 'buy':
                            adjusted_profit = best.profit - (price_offset * best.size / 100)
                            adjusted_capital = best.size * (try_price / 100)
                        else:
                            adjusted_profit = best.profit - (price_offset * best.size / 100)
                            adjusted_capital = best.size * ((100 - try_price) / 100)

                        adjusted_roi = (adjusted_profit / adjusted_capital * 100) if adjusted_capital > 0 else 0

                        if adjusted_roi < MIN_ROI:
                            print(f"   [X] ROI {adjusted_roi:.1f}% < {MIN_ROI}% at {try_price}c, stopping sweep")
                            break

                        print(f"[>>] SWEEP {price_offset}: {k_action} {best.size} YES @ {try_price}c (ROI: {adjusted_roi:.1f}%)")
                        k_result = await kalshi_api.place_order(
                            session, best.kalshi_ticker, 'yes', k_action, best.size, try_price
                        )

                        api_fill_count = k_result.get('fill_count', 0)
                        order_id = k_result.get('order_id')

                        if order_id:
                            placed_order_ids.append(order_id)
                            print(f"   [ORDER PLACED] {order_id[:12]}...")

                        if api_fill_count > 0:
                            actual_fill = api_fill_count
                            fill_price = try_price
                            print(f"   [OK] Got fill at {try_price}c!")
                            break
                        else:
                            if order_id:
                                cancelled = await kalshi_api.cancel_order(session, order_id)
                                if not cancelled:
                                    print(f"   [!] WARNING: Cancel may have failed for {order_id[:12]}")
                            print(f"   [.] No fill at {try_price}c, trying next level...")
                            await asyncio.sleep(0.1)

                finally:
                    # CRITICAL CLEANUP: Cancel ALL Kalshi orders for this ticker
                    print(f"\n[SWEEP CLEANUP] Ensuring no resting Kalshi orders for {best.kalshi_ticker}...")
                    cleanup_count = await kalshi_api.cancel_all_orders_for_ticker(session, best.kalshi_ticker)
                    if cleanup_count > 0:
                        print(f"[SWEEP CLEANUP] Cancelled {cleanup_count} resting orders")

                # Verify with position check
                await asyncio.sleep(0.3)
                post_position = await kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
                print(f"[>>] POST-TRADE: Kalshi Position = {post_position}")

                position_change = 0
                if pre_position is not None and post_position is not None:
                    position_change = abs(post_position - pre_position)

                if actual_fill == 0 and position_change > 0:
                    actual_fill = position_change
                    print(f"[>>] Position changed by {position_change}, using as fill count")

                print(f"[>>] Final: API fill={k_result.get('fill_count', 0)}, Position change={position_change}, Using={actual_fill}")

                # =============================================================
                # EXECUTE PM US SIDE (replaces partner webhook)
                # =============================================================
                if actual_fill > 0:
                    print(f"\n[OK] KALSHI FILLED: {actual_fill} contracts @ {fill_price}c")

                    # Compute PM US execution parameters
                    pm_intent, pm_price = get_pm_execution_params(best)
                    intent_names = {1: 'BUY_YES', 2: 'SELL_YES', 3: 'BUY_NO', 4: 'SELL_NO'}

                    print(f"[>>] Executing PM US: {intent_names[pm_intent]} {actual_fill} @ ${pm_price:.2f} on {best.pm_slug}")

                    pm_result = await pm_api.place_order(
                        session,
                        market_slug=best.pm_slug,
                        intent=pm_intent,
                        price=pm_price,
                        quantity=actual_fill,
                        tif=3,   # IOC
                        sync=True
                    )

                    if pm_result.get('success'):
                        pm_fill = pm_result.get('fill_count', 0)
                        pm_fill_price = pm_result.get('fill_price')

                        print(f"[OK] PM US FILLED: {pm_fill} contracts @ ${pm_fill_price:.2f}" if pm_fill_price else f"[OK] PM US FILLED: {pm_fill} contracts")

                        if pm_fill < actual_fill:
                            unfilled = actual_fill - pm_fill
                            print(f"[!] PARTIAL PM FILL: {unfilled} contracts UNHEDGED on Kalshi")

                        total_trades += 1
                        price_diff = abs(fill_price - k_price)
                        actual_profit = best.profit - (price_diff * actual_fill / 100)
                        total_profit += actual_profit
                        print(f"[$] Trade #{total_trades} | +${actual_profit:.2f} | Total: ${total_profit:.2f}")

                        if pm_fill < actual_fill:
                            log_trade(best, k_result, pm_result, 'PARTIAL_HEDGE')
                            print(f"[!!!] PARTIALLY UNHEDGED - {actual_fill - pm_fill} contracts on {best.kalshi_ticker}")
                            print(f"[STOP] Bot stopping due to PARTIALLY UNHEDGED position")
                            raise SystemExit("PARTIALLY UNHEDGED POSITION - Bot stopped for safety")
                        else:
                            log_trade(best, k_result, pm_result, 'SUCCESS')
                    else:
                        print(f"[X] PM US FAILED: {pm_result.get('error')}")
                        print(f"[!!!] UNHEDGED POSITION - CLOSE MANUALLY: {actual_fill} contracts on {best.kalshi_ticker}")
                        print(f"[STOP] Bot stopping due to UNHEDGED position - manual intervention required")
                        log_trade(best, k_result, pm_result, 'UNHEDGED')
                        raise SystemExit("UNHEDGED POSITION - Bot stopped for safety")

                    last_trade_time = time.time()

                else:
                    print(f"\n[X] NO FILL after sweeping {MAX_PRICE_LEVELS} price levels")
                    log_trade(best, k_result, {}, 'NO_FILL')

            elif exec_arbs:
                cooldown_remaining = COOLDOWN_SECONDS - (time.time() - last_trade_time)
                print(f"\n[.] Cooldown: {cooldown_remaining:.0f}s remaining")
            else:
                print(f"\n[.] No executable arbs")

            await asyncio.sleep(1.0)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STARTING ARB EXECUTOR v7 - DIRECT US EXECUTION")
    print("Kalshi + Polymarket US | No partner webhook")
    print("="*70 + "\n")

    try:
        asyncio.run(run_executor())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print(f"Trade log saved to trades.json")
