#!/usr/bin/env python3
"""
DUAL-PLATFORM ARBITRAGE EXECUTOR v5
Kalshi: $150 | Polymarket: $494
"""
import asyncio
import aiohttp
import time
import base64
import json
import re
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List
from enum import Enum
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import hmac
import hashlib

class ExecutionMode(Enum):
    PAPER = "paper"
    LIVE = "live"

EXECUTION_MODE = ExecutionMode.LIVE

TRADING_RULES = {
    'MIN_NET_SPREAD': 0.5,
    'MIN_ROI': 5.0,
    'MIN_PROFIT': 1.0,
    'MAX_CAPITAL': 176,
    'MIN_SIZE': 10,
    'MAX_POSITION_DOLLARS': 50,
}

KALSHI_API_KEY = 'c9121f7f-c56f-4940-95b2-f604ffb0a23f'
KALSHI_PRIVATE_KEY = open('kalshi.pem').read()

KALSHI_FEE = 0.01
PM_TAKER_FEE_RATE = 0.02
PARTNER_WEBHOOK_URL = os.environ.get('PARTNER_WEBHOOK_URL', 'http://localhost:8080/signal')
API_SECRET = "23c584339763ccd46668868bc1094fa28b42f6a84112d2be749e379e4772def1"

@dataclass
class ArbOpportunity:
    timestamp: datetime
    sport: str
    game: str
    team: str
    direction: str
    k_bid: float
    k_ask: float
    pm_bid: float
    pm_ask: float
    gross_spread: float
    fees: float
    net_spread: float
    size: float
    kalshi_ticker: str
    pm_token_id: str
    @property
    def profit(self): return (self.net_spread / 100) * self.size
    @property
    def capital(self): return self.size * (self.pm_ask / 100) if self.direction == 'BUY_PM_SELL_K' else self.size * (self.k_ask / 100)
    @property
    def roi(self): return (self.profit / self.capital * 100) if self.capital > 0 else 0

@dataclass
class ExecutionResult:
    success: bool
    platform: str
    side: str
    price: float
    size: float
    order_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    fill_price: Optional[float] = None
    fill_size: Optional[float] = None

class KalshiAPI:
    BASE_URL = 'https://api.elections.kalshi.com'
    def __init__(self, api_key, private_key):
        self.api_key = api_key
        self.private_key = serialization.load_pem_private_key(private_key.encode(), password=None, backend=default_backend())
    def _sign(self, ts, method, path):
        msg = f'{ts}{method}{path}'.encode('utf-8')
        sig = self.private_key.sign(
            msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(sig).decode('utf-8')
    def _headers(self, method, path):
        ts = str(int(time.time() * 1000))
        return {'KALSHI-ACCESS-KEY': self.api_key, 'KALSHI-ACCESS-SIGNATURE': self._sign(ts, method, path), 'KALSHI-ACCESS-TIMESTAMP': ts, 'Content-Type': 'application/json'}
    async def get_balance(self, session):
        path = '/trade-api/v2/portfolio/balance'
        try:
            async with session.get(f'{self.BASE_URL}{path}', headers=self._headers('GET', path), timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status == 200: return (await r.json()).get('balance', 0) / 100
        except: pass
        return None
    async def place_order(self, session, ticker, side, action, count, price):
        if EXECUTION_MODE == ExecutionMode.PAPER:
            await asyncio.sleep(0.1)
            return ExecutionResult(success=True, platform='kalshi', side=f'{action}_{side}', price=price, size=count, order_id=f'PAPER-{int(time.time()*1000)}', timestamp=datetime.now(), fill_price=price, fill_size=count)
        path = '/trade-api/v2/portfolio/orders'
        payload = {'ticker': ticker, 'action': action, 'side': side, 'count': count, 'type': 'limit'}
        payload['yes_price' if side == 'yes' else 'no_price'] = price
        try:
            async with session.post(f'{self.BASE_URL}{path}', headers=self._headers('POST', path), json=payload, timeout=aiohttp.ClientTimeout(total=5)) as r:
                data = await r.json()
                print(f"   [DEBUG] Kalshi response status={r.status}: {data}")
                order = data.get('order', {})
                filled = order.get('filled_count', 0)
                if filled and filled > 0:
                    return ExecutionResult(success=True, platform='kalshi', side=f'{action}_{side}', price=price, size=count, order_id=order.get('order_id'), timestamp=datetime.now(), fill_price=order.get('avg_price'), fill_size=filled)
                if r.status in [200, 201]:
                    return ExecutionResult(success=True, platform='kalshi', side=f'{action}_{side}', price=price, size=count, order_id=order.get('order_id'), timestamp=datetime.now(), fill_price=order.get('avg_price'), fill_size=order.get('filled_count', 0))
                return ExecutionResult(success=False, platform='kalshi', side=f'{action}_{side}', price=price, size=count, error=data.get('error', {}).get('message', str(data)), timestamp=datetime.now())
        except Exception as e:
            return ExecutionResult(success=False, platform='kalshi', side=f'{action}_{side}', price=price, size=count, error=str(e), timestamp=datetime.now())

class TradingRulesEngine:
    def __init__(self, rules):
        self.rules = rules
        self.positions_by_game = {}
        self.locked_capital = []
        self.kalshi_balance = 150.0
        self.pm_balance = 494.0
        self.realized_profit = 0.0
        self.pending_profit = 0.0
    def release_expired(self):
        now = datetime.now()
        settled = [(t,a,g,p) for t,a,g,p in self.locked_capital if t <= now]
        self.locked_capital = [(t,a,g,p) for t,a,g,p in self.locked_capital if t > now]
        for _,_,game,profit in settled:
            self.realized_profit += profit
            self.kalshi_balance += profit/2
            self.pm_balance += profit/2
            print(f"   [$$] SETTLED: {game} +${profit:.2f}")
    def get_available_capital(self):
        self.release_expired()
        locked = sum(a for _,a,_,_ in self.locked_capital)
        return min(self.kalshi_balance, self.pm_balance) - locked
    def get_active_games(self): return [g for _,_,g,_ in self.locked_capital]
    def check(self, arb):
        if arb.roi < self.rules['MIN_ROI']: return False, f"ROI {arb.roi:.1f}% < 5%"
        if arb.profit < self.rules['MIN_PROFIT']: return False, "Profit < $1"
        avail = self.get_available_capital()
        if arb.capital > avail: return False, f"Need ${arb.capital:.0f}, have ${avail:.0f}"
        if arb.capital > self.rules['MAX_CAPITAL']: return False, "Over max capital"
        if arb.size < self.rules['MIN_SIZE']: return False, "Size < 10"
        if arb.game in self.get_active_games(): return False, "Already in game"
        return True, "PASS"
    def record_trade(self, arb, lockup_hours=3.0):
        unlock = datetime.now() + timedelta(hours=lockup_hours)
        self.locked_capital.append((unlock, arb.capital, arb.game, arb.profit))
        self.pending_profit += arb.profit
        print(f"   [i] Locked ${arb.capital:.0f} until {unlock.strftime('%H:%M')}")

MONTH_MAP = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}
NBA_K2PM = {'ATL':'atl','BOS':'bos','BKN':'bkn','CHA':'cha','CHI':'chi','CLE':'cle','DAL':'dal','DEN':'den','DET':'det','GSW':'gsw','HOU':'hou','IND':'ind','LAC':'lac','LAL':'lal','MEM':'mem','MIA':'mia','MIL':'mil','MIN':'min','NOP':'nop','NYK':'nyk','OKC':'okc','ORL':'orl','PHI':'phi','PHX':'phx','POR':'por','SAC':'sac','SAS':'sas','TOR':'tor','UTA':'uta','WAS':'was'}
NBA_PM2K = {'Hawks':'ATL','Celtics':'BOS','Nets':'BKN','Hornets':'CHA','Bulls':'CHI','Cavaliers':'CLE','Mavericks':'DAL','Nuggets':'DEN','Pistons':'DET','Warriors':'GSW','Rockets':'HOU','Pacers':'IND','Clippers':'LAC','Lakers':'LAL','Grizzlies':'MEM','Heat':'MIA','Bucks':'MIL','Timberwolves':'MIN','Pelicans':'NOP','Knicks':'NYK','Thunder':'OKC','Magic':'ORL','76ers':'PHI','Suns':'PHX','Trail Blazers':'POR','Kings':'SAC','Spurs':'SAS','Raptors':'TOR','Jazz':'UTA','Wizards':'WAS'}
NFL_K2PM = {'ARI':'ari','ATL':'atl','BAL':'bal','BUF':'buf','CAR':'car','CHI':'chi','CIN':'cin','CLE':'cle','DAL':'dal','DEN':'den','DET':'det','GB':'gb','HOU':'hou','IND':'ind','JAC':'jax','KC':'kc','LA':'la','LAC':'lac','LV':'lv','MIA':'mia','MIN':'min','NE':'ne','NO':'no','NYG':'nyg','NYJ':'nyj','PHI':'phi','PIT':'pit','SEA':'sea','SF':'sf','TB':'tb','TEN':'ten','WAS':'was'}
NFL_PM2K = {'Cardinals':'ARI','Falcons':'ATL','Ravens':'BAL','Bills':'BUF','Panthers':'CAR','Bears':'CHI','Bengals':'CIN','Browns':'CLE','Cowboys':'DAL','Broncos':'DEN','Lions':'DET','Packers':'GB','Texans':'HOU','Colts':'IND','Jaguars':'JAC','Chiefs':'KC','Rams':'LA','Chargers':'LAC','Raiders':'LV','Dolphins':'MIA','Vikings':'MIN','Patriots':'NE','Saints':'NO','Giants':'NYG','Jets':'NYJ','Eagles':'PHI','Steelers':'PIT','Seahawks':'SEA','49ers':'SF','Buccaneers':'TB','Titans':'TEN','Commanders':'WAS'}
NHL_K2PM = {'ANA':'ana','BOS':'bos','BUF':'buf','CGY':'cgy','CAR':'car','CHI':'chi','COL':'col','CBJ':'cbj','DAL':'dal','DET':'det','EDM':'edm','FLA':'fla','LA':'la','MIN':'min','MTL':'mtl','NSH':'nsh','NJ':'nj','NYI':'nyi','NYR':'nyr','OTT':'ott','PHI':'phi','PIT':'pit','SJ':'sj','SEA':'sea','STL':'stl','TB':'tb','TOR':'tor','VAN':'van','VGK':'vgk','WPG':'wpg','WSH':'wsh'}
NHL_PM2K = {'Ducks':'ANA','Bruins':'BOS','Sabres':'BUF','Flames':'CGY','Hurricanes':'CAR','Blackhawks':'CHI','Avalanche':'COL','Blue Jackets':'CBJ','Stars':'DAL','Red Wings':'DET','Oilers':'EDM','Panthers':'FLA','Kings':'LA','Wild':'MIN','Canadiens':'MTL','Predators':'NSH','Devils':'NJ','Islanders':'NYI','Rangers':'NYR','Senators':'OTT','Flyers':'PHI','Penguins':'PIT','Sharks':'SJ','Kraken':'SEA','Blues':'STL','Lightning':'TB','Maple Leafs':'TOR','Canucks':'VAN','Golden Knights':'VGK','Jets':'WPG','Capitals':'WSH'}
EPL_K2PM = {'AVL':'ast','ARS':'ars','BOU':'bou','BRE':'bre','BRI':'bri','CHE':'che','CRY':'cry','EVE':'eve','FUL':'ful','IPS':'ips','LEI':'lei','LIV':'liv','MCI':'mac','MUN':'mun','NEW':'new','NFO':'nfo','SOU':'sou','TOT':'tot','WHU':'whu','WOL':'wol'}
EPL_PM2K = {'Aston Villa':'AVL','Arsenal':'ARS','Bournemouth':'BOU','Brentford':'BRE','Brighton':'BRI','Chelsea':'CHE','Crystal Palace':'CRY','Everton':'EVE','Fulham':'FUL','Ipswich':'IPS','Leicester':'LEI','Liverpool':'LIV','Man City':'MCI','Man United':'MUN','Newcastle':'NEW','Nottingham Forest':'NFO','Southampton':'SOU','Tottenham':'TOT','West Ham':'WHU','Wolves':'WOL'}
SPORTS_CONFIG = [
    {'sport':'nba','series':'KXNBAGAME','k2pm':NBA_K2PM,'pm2k':NBA_PM2K,'icon':'[NBA]','tennis':False},
    {'sport':'nfl','series':'KXNFLGAME','k2pm':NFL_K2PM,'pm2k':NFL_PM2K,'icon':'[NFL]','tennis':False},
    {'sport':'nhl','series':'KXNHLGAME','k2pm':NHL_K2PM,'pm2k':NHL_PM2K,'icon':'[NHL]','tennis':False},
    {'sport':'epl','series':'KXEPLGAME','k2pm':EPL_K2PM,'pm2k':EPL_PM2K,'icon':'[EPL]','tennis':False},
    {'sport':'atp','series':'KXATPMATCH','k2pm':{},'pm2k':{},'icon':'[ATP]','tennis':True},
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

def extract_player_name(title):
    m = re.search(r'Will ([A-Za-z\s\-]+) win', title)
    if m:
        parts = m.group(1).strip().split()
        return parts[-1].lower()[:7] if len(parts) >= 2 else m.group(1).lower()[:7]
    return None

def calc_min_spread(price): return PM_TAKER_FEE_RATE * (1 - price) + KALSHI_FEE

async def fetch_kalshi_all(session, kalshi_api):
    async def fetch_series(series):
        path = f'/trade-api/v2/markets?status=open&series_ticker={series}&limit=200'
        try:
            async with session.get(f'{kalshi_api.BASE_URL}{path}', headers=kalshi_api._headers('GET', path), timeout=aiohttp.ClientTimeout(total=3)) as r:
                if r.status == 200: return series, (await r.json()).get('markets', [])
        except: pass
        return series, []
    results = await asyncio.gather(*[fetch_series(c['series']) for c in SPORTS_CONFIG])
    return {s: m for s, m in results}

async def fetch_pm_event(session, sport, t1, t2, date, k2pm, is_tennis=False, pm_names=None):
    if is_tennis and pm_names: pm1, pm2 = pm_names.get(t1, t1.lower()), pm_names.get(t2, t2.lower())
    else: pm1, pm2 = k2pm.get(t1, t1.lower()), k2pm.get(t2, t2.lower())
    for slug in [f'{sport}-{pm1}-{pm2}-{date}', f'{sport}-{pm2}-{pm1}-{date}']:
        if slug in PM_EVENT_CACHE: return PM_EVENT_CACHE[slug]
        try:
            async with session.get(f'https://gamma-api.polymarket.com/events?slug={slug}', timeout=aiohttp.ClientTimeout(total=2)) as r:
                if r.status == 200:
                    evts = await r.json()
                    if evts: PM_EVENT_CACHE[slug] = evts[0]; return evts[0]
        except: pass
        PM_EVENT_CACHE[slug] = None
    return None

async def fetch_pm_books_batch(session, tokens):
    async def fetch_book(token):
        try:
            async with session.get(f'https://clob.polymarket.com/book?token_id={token}', timeout=aiohttp.ClientTimeout(total=2)) as r:
                if r.status == 200:
                    book = await r.json()
                    bids, asks = book.get('bids', []), book.get('asks', [])
                    if bids and asks:
                        bb, ba = max(float(b['price']) for b in bids), min(float(a['price']) for a in asks)
                        return token, {'bid': bb, 'ask': ba, 'bid_size': sum(float(b['size']) for b in bids if float(b['price']) >= bb - 0.001), 'ask_size': sum(float(a['size']) for a in asks if float(a['price']) <= ba + 0.001)}
        except: pass
        return token, None
    results = await asyncio.gather(*[fetch_book(t) for t in tokens])
    return {t: b for t, b in results if b}

async def notify_partner(session, arb, k_result):
    if PARTNER_WEBHOOK_URL == 'http://localhost:8080/signal':
        print("   [!] Partner webhook not configured")
        return {'success': False, 'error': 'No webhook'}
    try:
        signal = {'action': 'execute', 'arb': {'sport': arb.sport, 'game': arb.game, 'team': arb.team, 'direction': arb.direction, 'k_bid': arb.k_bid, 'k_ask': arb.k_ask, 'pm_bid': arb.pm_bid, 'pm_ask': arb.pm_ask, 'size': arb.size, 'pm_token_id': arb.pm_token_id, 'kalshi_ticker': arb.kalshi_ticker}, 'kalshi_executed': {'success': k_result.success, 'fill_price': k_result.fill_price, 'fill_size': k_result.fill_size, 'order_id': k_result.order_id}}
        payload = json.dumps(signal)
        ts = str(int(time.time() * 1000))
        sig = hmac.new(API_SECRET.encode(), f"{ts}{payload}".encode(), hashlib.sha256).hexdigest()
        async with session.post(PARTNER_WEBHOOK_URL, data=payload, headers={'Content-Type': 'application/json', 'X-Timestamp': ts, 'X-Signature': sig}, timeout=aiohttp.ClientTimeout(total=10)) as r:
            return await r.json()
    except Exception as e:
        print(f"   [!] Partner notify failed: {e}")
        return {'success': False, 'error': str(e)}

async def run_executor():
    print("="*70)
    print(f"ARB EXECUTOR v5 | Mode: {EXECUTION_MODE.value.upper()}")
    print(f"Capital: K=$150 | PM=$494")
    print(f"Sports: NBA | NFL | NHL | EPL | ATP")
    print("="*70)
    kalshi_api = KalshiAPI(KALSHI_API_KEY, KALSHI_PRIVATE_KEY)
    rules = TradingRulesEngine(TRADING_RULES)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100)) as session:
        bal = await kalshi_api.get_balance(session)
        if bal: 
            rules.kalshi_balance = bal
            print(f"Kalshi Balance: ${bal:.2f}")
        else:
            print("WARNING: Could not fetch Kalshi balance")
        scan_num = 0
        total_trades = 0
        total_profit = 0.0
        last_sync = 0
        while True:
            scan_num += 1
            if time.time() - last_sync > 60:
                b = await kalshi_api.get_balance(session)
                if b: rules.kalshi_balance = b
                last_sync = time.time()
            t0 = time.time()
            kalshi_data = await fetch_kalshi_all(session, kalshi_api)
            all_games = {}
            for cfg in SPORTS_CONFIG:
                sport = cfg['sport']
                all_games[sport] = {}
                for m in kalshi_data.get(cfg['series'], []):
                    parts = m.get('ticker', '').split('-')
                    if len(parts) >= 3:
                        gid, team = parts[1], parts[2]
                        if team == 'TIE': continue
                        if gid not in all_games[sport]:
                            date, _, _ = parse_gid(gid)
                            all_games[sport][gid] = {'date': date, 'teams': {}, 'tickers': {}, 'pm_names': {}}
                        all_games[sport][gid]['teams'][team] = {'k_bid': m.get('yes_bid', 0) / 100, 'k_ask': m.get('yes_ask', 0) / 100}
                        all_games[sport][gid]['tickers'][team] = m.get('ticker')
                        if cfg.get('tennis'):
                            pn = extract_player_name(m.get('title', ''))
                            if pn: all_games[sport][gid]['pm_names'][team] = pn
            pm_tasks, pm_keys = [], []
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    if len(game['teams']) < 2 or not game['date']: continue
                    teams = list(game['teams'].keys())
                    ck = f"{cfg['sport']}:{gid}"
                    if ck not in PM_TOKEN_CACHE:
                        pm_tasks.append(fetch_pm_event(session, cfg['sport'], teams[0], teams[1], game['date'], cfg['k2pm'], cfg.get('tennis', False), game.get('pm_names', {})))
                        pm_keys.append((cfg['sport'], gid, cfg['pm2k'], cfg.get('tennis', False), game.get('pm_names', {})))
            pm_results = await asyncio.gather(*pm_tasks) if pm_tasks else []
            for (sport, gid, pm2k, is_tennis, pm_names), evt in zip(pm_keys, pm_results):
                if not evt: continue
                for m in evt.get('markets', []):
                    q = m.get('question', '').lower()
                    if any(x in q for x in ['spread', 'o/u', 'total', '1h', 'set ']) or m.get('closed'): continue
                    outcomes, tokens = m.get('outcomes', []), m.get('clobTokenIds', [])
                    if isinstance(outcomes, str): outcomes = json.loads(outcomes)
                    if isinstance(tokens, str): tokens = json.loads(tokens)
                    if 'Yes' in outcomes:
                        if sport == 'epl':
                            EPL_NAMES = {'brighton':'BRI','bournemouth':'BOU','aston villa':'AVL','arsenal':'ARS','chelsea':'CHE','liverpool':'LIV','man city':'MCI','man united':'MUN','newcastle':'NEW','tottenham':'TOT','west ham':'WHU','wolves':'WOL','everton':'EVE','fulham':'FUL','brentford':'BRE','crystal palace':'CRY','nottingham':'NFO','leicester':'LEI','ipswich':'IPS','southampton':'SOU'}
                            if 'draw' not in q:
                                for tn, kc in EPL_NAMES.items():
                                    if tn in q:
                                        ck = f'{sport}:{gid}'
                                        if ck not in PM_TOKEN_CACHE: PM_TOKEN_CACHE[ck] = {}
                                        PM_TOKEN_CACHE[ck][kc] = tokens[0]
                                        break
                        continue
                    if len(outcomes) < 2: continue
                    if is_tennis:
                        mapping = {}
                        for o, t in zip(outcomes[:2], tokens[:2]):
                            ol = o.lower()[:7]
                            for kc, pn in pm_names.items():
                                if pn[:4] in ol or ol[:4] in pn: mapping[kc] = t; break
                        PM_TOKEN_CACHE[f"{sport}:{gid}"] = mapping
                    else:
                        PM_TOKEN_CACHE[f"{sport}:{gid}"] = {pm2k.get(o, o): t for o, t in zip(outcomes[:2], tokens[:2])}
                    break
            all_tokens, token_map = [], {}
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    ck = f"{cfg['sport']}:{gid}"
                    if ck in PM_TOKEN_CACHE:
                        for team, token in PM_TOKEN_CACHE[ck].items():
                            all_tokens.append(token)
                            token_map[token] = (cfg['sport'], gid, team)
            books = await fetch_pm_books_batch(session, all_tokens)
            for token, book in books.items():
                if token in token_map:
                    sport, gid, team = token_map[token]
                    if team in all_games[sport][gid]['teams']:
                        all_games[sport][gid]['teams'][team].update({'pm_bid': book['bid'], 'pm_ask': book['ask'], 'pm_bid_size': book['bid_size'], 'pm_ask_size': book['ask_size'], 'pm_token': token})
            scan_time = (time.time() - t0) * 1000
            arbs = []
            avail_capital = rules.get_available_capital()
            for cfg in SPORTS_CONFIG:
                for gid, game in all_games[cfg['sport']].items():
                    for team, p in game['teams'].items():
                        if 'pm_ask' not in p: continue
                        kb, ka, pb, pa = p['k_bid'], p['k_ask'], p['pm_bid'], p['pm_ask']
                        if kb == 0 or ka == 0: continue
                        g1, f1, n1 = kb - pa, calc_min_spread(pa), (kb - pa) - calc_min_spread(pa)
                        if n1 > 0:
                            cost_per_contract = pa + 0.02
                            max_by_dollars = int(50 / cost_per_contract) if cost_per_contract > 0 else 0
                            max_by_capital = int(avail_capital / cost_per_contract) if cost_per_contract > 0 else 0
                            sz = min(p.get('pm_ask_size', 0), max_by_dollars, max_by_capital)
                            if sz >= 10:
                                arbs.append(ArbOpportunity(datetime.now(), cfg['sport'].upper(), gid, team, 'BUY_PM_SELL_K', kb*100, ka*100, pb*100, pa*100, g1*100, f1*100, n1*100, sz, game['tickers'].get(team, ''), p.get('pm_token', '')))
                        g2, f2, n2 = pb - ka, PM_TAKER_FEE_RATE * pb + KALSHI_FEE, (pb - ka) - (PM_TAKER_FEE_RATE * pb + KALSHI_FEE)
                        if n2 > 0:
                            cost_per_contract = ka + 0.02
                            max_by_dollars = int(50 / cost_per_contract) if cost_per_contract > 0 else 0
                            max_by_capital = int(avail_capital / cost_per_contract) if cost_per_contract > 0 else 0
                            sz = min(p.get('pm_bid_size', 0), max_by_dollars, max_by_capital)
                            if sz >= 10:
                                arbs.append(ArbOpportunity(datetime.now(), cfg['sport'].upper(), gid, team, 'BUY_K_SELL_PM', kb*100, ka*100, pb*100, pa*100, g2*100, f2*100, n2*100, sz, game['tickers'].get(team, ''), p.get('pm_token', '')))
            exec_arbs = [a for a in arbs if rules.check(a)[0]]
            exec_arbs.sort(key=lambda x: -x.roi)
            print("="*70)
            print(f"ARB EXECUTOR v5 | Scan #{scan_num} | {datetime.now().strftime('%H:%M:%S')} | {scan_time:.0f}ms")
            print(f"Mode: {EXECUTION_MODE.value.upper()} | Trades: {total_trades} | Profit: ${total_profit:.2f}")
            print("="*70)
            matched = sum(1 for cfg in SPORTS_CONFIG for g in all_games[cfg['sport']].values() if any('pm_ask' in t for t in g['teams'].values()))
            total_games = sum(len(all_games[c['sport']]) for c in SPORTS_CONFIG)
            print(f"\n[i] Tracking {total_games} games, {matched} matched")
            avail = rules.get_available_capital()
            locked = sum(a for _,a,_,_ in rules.locked_capital)
            print(f"[$] Capital: ${avail:.0f} avail | ${locked:.0f} locked | K=${rules.kalshi_balance:.0f}")
            print(f"[?] Found {len(arbs)} arbs, {len(exec_arbs)} pass rules")
            if exec_arbs:
                print(f"\n[!] EXECUTABLE ARBS:")
                for a in exec_arbs[:5]:
                    print(f"   {a.sport} {a.game} {a.team}: {a.direction}")
                    print(f"      K:{a.k_bid:.0f}/{a.k_ask:.0f} PM:{a.pm_bid:.0f}/{a.pm_ask:.0f} | ${a.profit:.2f} | {a.roi:.1f}%")
                best = exec_arbs[0]
                print(f"\n[>>] EXECUTING: {best.sport} {best.game} {best.team}")
                k_action, k_price = ('sell', int(best.k_bid) - 2) if best.direction == 'BUY_PM_SELL_K' else ('buy', int(best.k_ask) + 2)
                
                pre_balance = await kalshi_api.get_balance(session)
                trade_cost = int(best.size) * (k_price / 100) * 1.03
                print(f"   [SAFETY] Balance: ${pre_balance:.2f} | Trade cost (with fees): ${trade_cost:.2f} | Size: {int(best.size)}")
                
                if pre_balance is None:
                    print(f"   [X] ABORT: Could not verify balance")
                    await asyncio.sleep(5)
                    continue
                
                if trade_cost > pre_balance:
                    print(f"   [X] ABORT: Trade cost ${trade_cost:.2f} > balance ${pre_balance:.2f}")
                    await asyncio.sleep(5)
                    continue
                
                max_affordable = int((pre_balance * 0.90) / (k_price / 100))
                if int(best.size) > max_affordable:
                    print(f"   [!] Reducing size from {int(best.size)} to {max_affordable}")
                    best.size = max_affordable
                
                if best.size < 10:
                    print(f"   [X] ABORT: Size {best.size} too small after adjustment")
                    await asyncio.sleep(5)
                    continue
                
                k_result = await kalshi_api.place_order(session, best.kalshi_ticker, 'yes', k_action, int(best.size), k_price)
                
                # ALWAYS check balance after order attempt
                await asyncio.sleep(0.5)
                post_balance = await kalshi_api.get_balance(session)
                balance_dropped = post_balance and pre_balance and (pre_balance - post_balance) > 0.10
                
                if balance_dropped:
                    actual_spent = pre_balance - post_balance
                    estimated_fill = int(actual_spent / (k_price / 100)) if k_price > 0 else int(best.size)
                    # CAP fill size to never exceed intended size
                    estimated_fill = min(estimated_fill, int(best.size))
                    print(f"   [!!!] BALANCE DROPPED: ${pre_balance:.2f} -> ${post_balance:.2f} (spent ${actual_spent:.2f})")
                    print(f"   [!!!] ESTIMATED FILL: {estimated_fill} contracts")
                    
                    k_result.success = True
                    k_result.fill_size = estimated_fill
                    k_result.fill_price = k_price
                    
                    print(f"   [>>] Sending to partner...")
                    pm_result = await notify_partner(session, best, k_result)
                    if pm_result.get('success'):
                        print(f"   [OK] PM executed!")
                        total_trades += 1
                        total_profit += best.profit
                        rules.record_trade(best)
                        print(f"   [$] Trade #{total_trades}! +${best.profit:.2f} | Total: ${total_profit:.2f}")
                    else:
                        print(f"   [X] PM FAILED: {pm_result.get('error')}")
                        print(f"   [!!!] CRITICAL: UNHEDGED POSITION - CHECK MANUALLY")
                
                elif k_result.success and k_result.fill_size and k_result.fill_size > 0:
                    print(f"   [OK] Kalshi: {k_result.fill_size} @ {k_result.fill_price}c")
                    print(f"   [>>] Sending to partner...")
                    pm_result = await notify_partner(session, best, k_result)
                    if pm_result.get('success'):
                        print(f"   [OK] PM executed!")
                        total_trades += 1
                        total_profit += best.profit
                        rules.record_trade(best)
                        print(f"   [$] Trade #{total_trades}! +${best.profit:.2f} | Total: ${total_profit:.2f}")
                    else:
                        print(f"   [X] PM FAILED: {pm_result.get('error')}")
                        print(f"   [!] CHECK MANUALLY - Kalshi executed but PM failed")
                else:
                    print(f"   [X] Kalshi failed: {k_result.error}")
                    print(f"   [i] Balance unchanged: ${post_balance:.2f}")
            else:
                print(f"\n[.] No executable arbs. Waiting...")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(run_executor())
    except KeyboardInterrupt:
        print("\nShutting down...")