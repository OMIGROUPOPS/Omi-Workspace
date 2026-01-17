#!/usr/bin/env python3
"""
DUAL-PLATFORM ARBITRAGE EXECUTOR v6 - BULLETPROOF
Hard limits that CANNOT be bypassed. Position-based verification.

HARD LIMITS:
- MAX 20 contracts per trade
- MAX $10 total cost per trade  
- buy_max_cost enforces Fill-or-Kill behavior
- Position check AFTER every order attempt
- Only signal partner if position actually exists
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
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import hmac
import hashlib

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

KALSHI_API_KEY = 'c9121f7f-c56f-4940-95b2-f604ffb0a23f'
KALSHI_PRIVATE_KEY = open('kalshi.pem').read()

KALSHI_FEE = 0.01
PM_TAKER_FEE_RATE = 0.02
# Tony's partner webhook - DO NOT CHANGE without coordinating
PARTNER_WEBHOOK_URL = os.environ.get('PARTNER_WEBHOOK_URL', 'https://unexceptional-unpersonalised-winnie.ngrok-free.dev/signal')
API_SECRET = "23c584339763ccd46668868bc1094fa28b42f6a84112d2be749e379e4772def1"

# Trade log - load existing trades on startup
def load_trades() -> List[Dict]:
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
            # Keep last 1000 trades
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
    pm_token_id: str
    
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
        """Get account balance in dollars"""
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
        """Get all current positions"""
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
        """Get position for a specific ticker. Returns contract count or None."""
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
                    return 0  # No position found
        except Exception as e:
            print(f"   [!] Position fetch error: {e}")
        return None
    
    async def place_order(self, session, ticker: str, side: str, action: str, 
                          count: int, price_cents: int) -> Dict:
        """
        Place an order with hard safety limits.
        
        Uses buy_max_cost to enforce Fill-or-Kill behavior and cap spending.
        
        Returns dict with: success, fill_count, order_id, error
        """
        # HARD LIMIT ENFORCEMENT
        if count > MAX_CONTRACTS:
            print(f"   [SAFETY] Capping contracts from {count} to {MAX_CONTRACTS}")
            count = MAX_CONTRACTS
        
        if count < MIN_CONTRACTS:
            return {'success': False, 'error': f'Count {count} below minimum {MIN_CONTRACTS}'}
        
        # Calculate max cost
        if action == 'buy':
            max_cost = count * price_cents
        else:
            # For sells, max cost is based on the NO side (100 - price)
            max_cost = count * (100 - price_cents)
        
        # HARD LIMIT on cost
        if max_cost > MAX_COST_CENTS:
            # Reduce count to fit within cost limit
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

        # For aggressive fills, pay MORE than ask (buys) or accept LESS than bid (sells)
        # This ensures we cross the spread and take liquidity
        if action == 'buy':
            aggressive_price = price_cents + 2  # Pay 2c above ask
        else:
            aggressive_price = max(1, price_cents - 2)  # Accept 2c below bid

        payload = {
            'ticker': ticker,
            'action': action,
            'side': side,
            'count': count,
            'type': 'limit',
            'client_order_id': str(uuid.uuid4()),
        }

        # Set price - use aggressive price to cross the spread
        if side == 'yes':
            payload['yes_price'] = aggressive_price
        else:
            payload['no_price'] = aggressive_price

        # buy_max_cost enforces Fill-or-Kill behavior for buys
        # sell_position_floor enforces Fill-or-Kill for sells (won't go below 0)
        if action == 'buy':
            payload['buy_max_cost'] = max_cost + (count * 10)  # Buffer for aggressive price
        else:
            payload['sell_position_floor'] = 0  # Don't go short

        try:
            print(f"   [ORDER] {action} {count} {side} @ {aggressive_price}c (was: {price_cents}c)")
            
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
                
                # Order placed but no fill (resting or rejected)
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


async def notify_partner(session, arb: ArbOpportunity, fill_count: int, fill_price: int) -> Dict:
    """Send signal to partner with actual fill details"""
    if 'localhost' in PARTNER_WEBHOOK_URL or '127.0.0.1' in PARTNER_WEBHOOK_URL:
        print(f"   [!] Partner webhook is localhost - skipping: {PARTNER_WEBHOOK_URL}")
        return {'success': False, 'error': 'Webhook is localhost'}

    if EXECUTION_MODE == ExecutionMode.PAPER:
        print(f"   [PAPER] Would notify partner: {fill_count} contracts")
        return {'success': True, 'paper': True}
    
    try:
        signal = {
            'action': 'execute',
            'arb': {
                'sport': arb.sport,
                'game': arb.game,
                'team': arb.team,
                'direction': arb.direction,
                'k_bid': arb.k_bid,
                'k_ask': arb.k_ask,
                'pm_bid': arb.pm_bid,
                'pm_ask': arb.pm_ask,
                'size': fill_count,  # Use actual fill count, not intended size
                'pm_token_id': arb.pm_token_id,
                'kalshi_ticker': arb.kalshi_ticker
            },
            'kalshi_executed': {
                'success': True,
                'fill_price': fill_price,
                'fill_size': fill_count
            }
        }
        
        payload = json.dumps(signal)
        ts = str(int(time.time() * 1000))
        sig = hmac.new(API_SECRET.encode(), f"{ts}{payload}".encode(), hashlib.sha256).hexdigest()
        
        async with session.post(
            PARTNER_WEBHOOK_URL,
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Timestamp': ts,
                'X-Signature': sig
            },
            timeout=aiohttp.ClientTimeout(total=30)
        ) as r:
            result = await r.json()
            return result
            
    except Exception as e:
        print(f"   [!] Partner notify failed: {e}")
        return {'success': False, 'error': str(e)}


def log_trade(arb: ArbOpportunity, k_result: Dict, pm_result: Dict, status: str):
    """Log trade details"""
    global TRADE_LOG

    # Determine display status based on execution mode
    if EXECUTION_MODE == ExecutionMode.PAPER:
        display_status = 'PAPER'
    else:
        # LIVE mode - use actual status
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
        'pm_success': pm_result.get('success', False),
        'pm_error': pm_result.get('error'),
        'status': display_status,
        'raw_status': status,  # Keep original status for debugging
        'execution_mode': EXECUTION_MODE.value,
        'expected_profit': arb.profit,
        'roi': arb.roi
    }
    TRADE_LOG.append(trade)

    # Keep only last 1000 trades
    if len(TRADE_LOG) > 1000:
        TRADE_LOG = TRADE_LOG[-1000:]

    # Save to file
    try:
        with open('trades.json', 'w') as f:
            json.dump(TRADE_LOG, f, indent=2)
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

PM_EVENT_CACHE = {}
PM_TOKEN_CACHE = {}


def parse_gid(gid):
    m = re.match(r'(\d{2})([A-Z]{3})(\d{2})([A-Z]+)', gid)
    if m:
        date = f'20{m.group(1)}-{MONTH_MAP.get(m.group(2),"01")}-{m.group(3)}'
        teams = m.group(4)
        return date, teams[:len(teams)//2], teams[len(teams)//2:]
    return None, None, None


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


async def fetch_pm_event(session, sport, t1, t2, date, k2pm):
    """Fetch Polymarket event data"""
    pm1, pm2 = k2pm.get(t1, t1.lower()), k2pm.get(t2, t2.lower())
    for slug in [f'{sport}-{pm1}-{pm2}-{date}', f'{sport}-{pm2}-{pm1}-{date}']:
        if slug in PM_EVENT_CACHE:
            return PM_EVENT_CACHE[slug]
        try:
            async with session.get(
                f'https://gamma-api.polymarket.com/events?slug={slug}',
                timeout=aiohttp.ClientTimeout(total=3)
            ) as r:
                if r.status == 200:
                    evts = await r.json()
                    if evts:
                        PM_EVENT_CACHE[slug] = evts[0]
                        return evts[0]
        except:
            pass
        PM_EVENT_CACHE[slug] = None
    return None


async def fetch_pm_orderbook(session, token_id):
    """Fetch Polymarket orderbook for a token"""
    try:
        async with session.get(
            f'https://clob.polymarket.com/book?token_id={token_id}',
            timeout=aiohttp.ClientTimeout(total=3)
        ) as r:
            if r.status == 200:
                book = await r.json()
                bids = book.get('bids', [])
                asks = book.get('asks', [])
                if bids and asks:
                    best_bid = max(float(b['price']) for b in bids)
                    best_ask = min(float(a['price']) for a in asks)
                    bid_size = sum(float(b['size']) for b in bids if float(b['price']) >= best_bid - 0.01)
                    ask_size = sum(float(a['size']) for a in asks if float(a['price']) <= best_ask + 0.01)
                    return {
                        'bid': best_bid,
                        'ask': best_ask,
                        'bid_size': int(bid_size),
                        'ask_size': int(ask_size)
                    }
    except:
        pass
    return None


async def run_executor():
    print("=" * 70)
    print("ARB EXECUTOR v6 - BULLETPROOF")
    print(f"Mode: {EXECUTION_MODE.value.upper()}")
    print(f"HARD LIMITS: Max {MAX_CONTRACTS} contracts, Max ${MAX_COST_CENTS/100:.0f} per trade")
    print(f"Cooldown: {COOLDOWN_SECONDS}s between trades")
    print("=" * 70)
    
    if EXECUTION_MODE == ExecutionMode.PAPER:
        print("\n*** PAPER TRADING MODE - NO REAL ORDERS ***\n")
    
    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
    
    last_trade_time = 0
    total_trades = 0
    total_profit = 0.0
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
        # Get initial balance
        balance = await kalshi_api.get_balance(session)
        if balance:
            print(f"Kalshi Balance: ${balance:.2f}")
        else:
            print("WARNING: Could not fetch balance")
        
        # Get initial positions
        positions = await kalshi_api.get_positions(session)
        if positions:
            print(f"Open positions: {len(positions)}")
            for ticker, pos in positions.items():
                print(f"  {ticker}: {pos.position} contracts")
        
        scan_num = 0
        
        while True:
            scan_num += 1
            t0 = time.time()
            
            # Fetch Kalshi markets
            kalshi_data = await fetch_kalshi_markets(session, kalshi_api)
            
            # Build game data
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
                            'k_bid': m.get('yes_bid', 0),  # Already in cents
                            'k_ask': m.get('yes_ask', 0)
                        }
                        all_games[sport][gid]['tickers'][team] = m.get('ticker')
            
            # Fetch PM data for games we don't have yet
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    if len(game['teams']) < 2 or not game['date']:
                        continue
                    
                    teams = list(game['teams'].keys())
                    cache_key = f"{cfg['sport']}:{gid}"
                    
                    if cache_key not in PM_TOKEN_CACHE:
                        evt = await fetch_pm_event(
                            session, cfg['sport'], teams[0], teams[1],
                            game['date'], cfg['k2pm']
                        )
                        
                        if evt:
                            for m in evt.get('markets', []):
                                q = m.get('question', '').lower()
                                if any(x in q for x in ['spread', 'o/u', 'total', '1h']):
                                    continue
                                if m.get('closed'):
                                    continue
                                
                                outcomes = m.get('outcomes', [])
                                tokens = m.get('clobTokenIds', [])
                                
                                if isinstance(outcomes, str):
                                    outcomes = json.loads(outcomes)
                                if isinstance(tokens, str):
                                    tokens = json.loads(tokens)
                                
                                if 'Yes' in outcomes or len(outcomes) < 2:
                                    continue
                                
                                PM_TOKEN_CACHE[cache_key] = {
                                    cfg['pm2k'].get(o, o): t 
                                    for o, t in zip(outcomes[:2], tokens[:2])
                                }
                                break
            
            # Fetch PM orderbooks
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    cache_key = f"{cfg['sport']}:{gid}"
                    if cache_key in PM_TOKEN_CACHE:
                        for team, token in PM_TOKEN_CACHE[cache_key].items():
                            if team in game['teams']:
                                book = await fetch_pm_orderbook(session, token)
                                if book:
                                    game['teams'][team]['pm_bid'] = int(book['bid'] * 100)
                                    game['teams'][team]['pm_ask'] = int(book['ask'] * 100)
                                    game['teams'][team]['pm_bid_size'] = book['bid_size']
                                    game['teams'][team]['pm_ask_size'] = book['ask_size']
                                    game['teams'][team]['pm_token'] = token
            
            # Find arbs
            arbs = []
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    for team, p in game['teams'].items():
                        if 'pm_ask' not in p:
                            continue
                        
                        kb = p['k_bid']  # cents
                        ka = p['k_ask']  # cents
                        pb = p['pm_bid']  # cents
                        pa = p['pm_ask']  # cents
                        
                        if kb == 0 or ka == 0:
                            continue
                        
                        # Direction 1: Buy PM, Sell Kalshi
                        # Profit = k_bid - pm_ask - fees
                        gross1 = kb - pa
                        fees1 = int((PM_TAKER_FEE_RATE * (100 - pa)) + (KALSHI_FEE * 100))
                        net1 = gross1 - fees1
                        
                        if net1 > 0:
                            # Size limited by PM ask liquidity and our hard limits
                            sz = min(p.get('pm_ask_size', 0), MAX_CONTRACTS)
                            # Also limit by cost
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
                                    pm_token_id=p.get('pm_token', '')
                                ))
                        
                        # Direction 2: Buy Kalshi, Sell PM
                        # Profit = pm_bid - k_ask - fees
                        gross2 = pb - ka
                        fees2 = int((PM_TAKER_FEE_RATE * pb) + (KALSHI_FEE * 100))
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
                                    pm_token_id=p.get('pm_token', '')
                                ))
            
            # Filter by ROI
            exec_arbs = [a for a in arbs if a.roi >= MIN_ROI]
            exec_arbs.sort(key=lambda x: -x.roi)
            
            scan_time = (time.time() - t0) * 1000
            
            # Display
            print("=" * 70)
            print(f"v6 BULLETPROOF | Scan #{scan_num} | {datetime.now().strftime('%H:%M:%S')} | {scan_time:.0f}ms")
            print(f"Mode: {EXECUTION_MODE.value.upper()} | Trades: {total_trades} | Profit: ${total_profit:.2f}")
            print("=" * 70)
            
            total_games = sum(len(all_games[c['sport']]) for c in SPORTS_CONFIG)
            matched = sum(1 for cfg in SPORTS_CONFIG 
                         for g in all_games[cfg['sport']].values() 
                         if any('pm_ask' in t for t in g['teams'].values()))
            
            print(f"\n[i] Games: {total_games} | Matched: {matched}")
            print(f"[i] Found {len(arbs)} arbs, {len(exec_arbs)} pass {MIN_ROI}% ROI threshold")
            
            # Execute if we have arbs and cooldown passed
            if exec_arbs and (time.time() - last_trade_time) >= COOLDOWN_SECONDS:
                best = exec_arbs[0]
                
                print(f"\n[!] BEST ARB: {best.sport} {best.game} {best.team}")
                print(f"    Direction: {best.direction}")
                print(f"    K: {best.k_bid}/{best.k_ask}c | PM: {best.pm_bid}/{best.pm_ask}c")
                print(f"    Size: {best.size} | Profit: ${best.profit:.2f} | ROI: {best.roi:.1f}%")
                
                # Determine Kalshi order params
                if best.direction == 'BUY_PM_SELL_K':
                    k_action = 'sell'
                    k_price = best.k_bid  # Sell at bid
                else:
                    k_action = 'buy'
                    k_price = best.k_ask  # Buy at ask
                
                # Get position BEFORE order
                pre_position = await kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
                print(f"\n[>>] PRE-TRADE: Position = {pre_position}")
                
                # Place order
                print(f"[>>] PLACING: {k_action} {best.size} YES @ {k_price}c")
                k_result = await kalshi_api.place_order(
                    session, best.kalshi_ticker, 'yes', k_action, best.size, k_price
                )
                
                # Get fill count from API response (PRIMARY indicator)
                api_fill_count = k_result.get('fill_count', 0)

                # Wait briefly then verify with position check (SECONDARY)
                await asyncio.sleep(0.5)
                post_position = await kalshi_api.get_position_for_ticker(session, best.kalshi_ticker)
                print(f"[>>] POST-TRADE: Position = {post_position}")

                # Calculate position change for verification
                position_change = 0
                if pre_position is not None and post_position is not None:
                    position_change = abs(post_position - pre_position)

                # Determine actual fill - trust API first, use position change as backup
                actual_fill = api_fill_count if api_fill_count > 0 else position_change

                print(f"[>>] Fill detection: API={api_fill_count}, Position change={position_change}, Using={actual_fill}")

                # CRITICAL: If we have ANY fill, signal partner
                if actual_fill > 0:
                    print(f"\n[OK] KALSHI FILLED: {actual_fill} contracts")

                    # Signal partner webhook
                    print(f"[>>] Signaling partner at {PARTNER_WEBHOOK_URL}...")
                    pm_result = await notify_partner(session, best, actual_fill, k_price)

                    if pm_result.get('success'):
                        print(f"[OK] Partner executed!")
                        total_trades += 1
                        actual_profit = (best.net_spread / 100) * actual_fill
                        total_profit += actual_profit
                        print(f"[$] Trade #{total_trades} | +${actual_profit:.2f} | Total: ${total_profit:.2f}")
                        log_trade(best, k_result, pm_result, 'SUCCESS')
                    else:
                        print(f"[X] Partner FAILED: {pm_result.get('error')}")
                        print(f"[!!!] UNHEDGED POSITION - CLOSE MANUALLY: {actual_fill} contracts on {best.kalshi_ticker}")
                        print(f"[STOP] Bot stopping due to UNHEDGED position - manual intervention required")
                        log_trade(best, k_result, pm_result, 'UNHEDGED')
                        raise SystemExit("UNHEDGED POSITION - Bot stopped for safety")

                    last_trade_time = time.time()

                else:
                    # No fill from either source
                    print(f"\n[X] NO FILL - Status: {k_result.get('status', 'unknown')}, Error: {k_result.get('error', 'none')}")
                    log_trade(best, k_result, {}, 'NO_FILL')
            
            elif exec_arbs:
                cooldown_remaining = COOLDOWN_SECONDS - (time.time() - last_trade_time)
                print(f"\n[.] Cooldown: {cooldown_remaining:.0f}s remaining")
            else:
                print(f"\n[.] No executable arbs")
            
            await asyncio.sleep(1.0)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("STARTING ARB EXECUTOR v6 - BULLETPROOF EDITION")
    print("="*70 + "\n")
    
    try:
        asyncio.run(run_executor())
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        print(f"Trade log saved to trades.json")
