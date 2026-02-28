#!/usr/bin/env python3
"""
OMI Edge Bot Control Server
HTTP/WebSocket server to control arb_executor remotely.

Endpoints:
- GET  /status  - Get bot state, balance, positions
- POST /start   - Start the executor
- POST /stop    - Stop the executor
- POST /mode    - Switch between PAPER/LIVE
- GET  /trades  - Get trade history
- WS   /ws      - Real-time log streaming
"""
import asyncio
import aiohttp
import json
import time
import base64
import sys
import io
import os
from datetime import datetime
from typing import Optional, Dict, List, Set
from contextlib import redirect_stdout, redirect_stderr
from threading import Thread, Lock
from queue import Queue
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import Kalshi API auth from executor
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# ============================================================================
# CONFIGURATION
# ============================================================================
KALSHI_API_KEY = 'f3b064d1-a02e-42a4-b2b1-132834694d23'
KALSHI_PRIVATE_KEY_PATH = 'kalshi.pem'
KALSHI_BASE_URL = 'https://api.elections.kalshi.com'

# ============================================================================
# BOT STATE
# ============================================================================
class BotState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"

class ExecutionMode(Enum):
    PAPER = "paper"
    LIVE = "live"

@dataclass
class Position:
    ticker: str
    position: int
    market_exposure: int
    resting_orders_count: int = 0
    total_cost: int = 0

# Global state
bot_state = BotState.STOPPED
execution_mode = ExecutionMode.PAPER
bot_task: Optional[asyncio.Task] = None
bot_process = None
log_queue: Queue = Queue(maxsize=1000)
connected_clients: Set[WebSocket] = set()
state_lock = Lock()
session_start_time: Optional[str] = None  # Track when current session started

# ============================================================================
# KALSHI API CLIENT
# ============================================================================
class KalshiClient:
    def __init__(self):
        self.api_key = KALSHI_API_KEY
        try:
            with open(KALSHI_PRIVATE_KEY_PATH, 'r') as f:
                key_data = f.read()
            self.private_key = serialization.load_pem_private_key(
                key_data.encode(), password=None, backend=default_backend()
            )
        except Exception as e:
            print(f"Failed to load Kalshi key: {e}")
            self.private_key = None

    def _sign(self, ts: str, method: str, path: str) -> str:
        msg = f'{ts}{method}{path}'.encode('utf-8')
        sig = self.private_key.sign(
            msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(sig).decode('utf-8')

    def _headers(self, method: str, path: str) -> Dict:
        ts = str(int(time.time() * 1000))
        return {
            'KALSHI-ACCESS-KEY': self.api_key,
            'KALSHI-ACCESS-SIGNATURE': self._sign(ts, method, path),
            'KALSHI-ACCESS-TIMESTAMP': ts,
            'Content-Type': 'application/json'
        }

    async def get_balance(self) -> Optional[float]:
        if not self.private_key:
            return None
        path = '/trade-api/v2/portfolio/balance'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{KALSHI_BASE_URL}{path}',
                    headers=self._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        return data.get('balance', 0) / 100
        except Exception as e:
            print(f"Balance fetch error: {e}")
        return None

    async def get_positions(self) -> List[Dict]:
        if not self.private_key:
            return []
        path = '/trade-api/v2/portfolio/positions?count_filter=position'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{KALSHI_BASE_URL}{path}',
                    headers=self._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        positions = []
                        for mp in data.get('market_positions', []):
                            if mp.get('position', 0) != 0:
                                positions.append({
                                    'ticker': mp['ticker'],
                                    'position': mp['position'],
                                    'market_exposure': mp.get('market_exposure', 0),
                                    'resting_orders_count': mp.get('resting_orders_count', 0),
                                    'total_cost': mp.get('total_cost', 0)
                                })
                        return positions
        except Exception as e:
            print(f"Positions fetch error: {e}")
        return []

    async def get_fills(self, limit: int = 50) -> List[Dict]:
        if not self.private_key:
            return []
        path = f'/trade-api/v2/portfolio/fills?limit={limit}'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{KALSHI_BASE_URL}{path}',
                    headers=self._headers('GET', path),
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as r:
                    if r.status == 200:
                        data = await r.json()
                        return data.get('fills', [])
        except Exception as e:
            print(f"Fills fetch error: {e}")
        return []

kalshi = KalshiClient()

# ============================================================================
# LOG CAPTURE
# ============================================================================
class LogCapture:
    """Captures stdout/stderr and broadcasts to WebSocket clients"""

    def __init__(self, original):
        self.original = original
        self.buffer = ""

    def write(self, text):
        self.original.write(text)
        if text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = {"time": timestamp, "message": text.rstrip()}

            # Add to queue
            if log_queue.full():
                try:
                    log_queue.get_nowait()
                except:
                    pass
            log_queue.put(log_entry)

            # Broadcast to clients
            asyncio.create_task(broadcast_log(log_entry))

    def flush(self):
        self.original.flush()

async def broadcast_log(log_entry: Dict):
    """Send log entry to all connected WebSocket clients"""
    if not connected_clients:
        return

    message = json.dumps({"type": "log", "data": log_entry})
    disconnected = set()

    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            disconnected.add(client)

    connected_clients.difference_update(disconnected)

async def broadcast_state():
    """Send state update to all connected clients"""
    if not connected_clients:
        return

    state_data = {
        "type": "state",
        "data": {
            "bot_state": bot_state.value,
            "mode": execution_mode.value,
            "timestamp": datetime.now().isoformat()
        }
    }

    message = json.dumps(state_data)
    disconnected = set()

    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            disconnected.add(client)

    connected_clients.difference_update(disconnected)

# ============================================================================
# BOT CONTROL
# ============================================================================
import subprocess

async def start_bot(clear: bool = False):
    """Start the arb executor as a subprocess"""
    global bot_state, bot_process, session_start_time

    if bot_state == BotState.RUNNING:
        return False, "Bot is already running"

    bot_state = BotState.STARTING
    session_start_time = datetime.now().isoformat()
    await broadcast_state()

    # Log session start separator
    clear_msg = " (CLEARED)" if clear else ""
    session_log = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": f"\n{'='*50}\n=== NEW SESSION STARTED ({execution_mode.value.upper()}){clear_msg} ===\n{'='*50}"
    }
    await broadcast_log(session_log)

    try:
        executor_path = os.path.join(os.path.dirname(__file__), 'arb_executor_v7.py')

        # Build command line args
        mode_flag = '--live' if execution_mode == ExecutionMode.LIVE else '--paper'
        cmd_args = [sys.executable, executor_path, '--start', mode_flag]
        if clear:
            cmd_args.append('--clear')

        bot_process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.path.dirname(__file__)
        )

        bot_state = BotState.RUNNING
        await broadcast_state()

        # Start log reader task
        asyncio.create_task(read_bot_output())

        return True, "Bot started"

    except Exception as e:
        bot_state = BotState.ERROR
        await broadcast_state()
        return False, str(e)

async def read_bot_output():
    """Read output from bot subprocess and broadcast"""
    global bot_state, bot_process

    if not bot_process or not bot_process.stdout:
        return

    try:
        while True:
            line = await bot_process.stdout.readline()
            if not line:
                break

            text = line.decode('utf-8', errors='ignore').rstrip()
            if text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_entry = {"time": timestamp, "message": text}

                if log_queue.full():
                    try:
                        log_queue.get_nowait()
                    except:
                        pass
                log_queue.put(log_entry)

                await broadcast_log(log_entry)

        # Process ended
        return_code = await bot_process.wait()
        bot_state = BotState.STOPPED
        await broadcast_state()

        log_entry = {"time": datetime.now().strftime("%H:%M:%S"),
                     "message": f"[BOT] Process exited with code {return_code}"}
        await broadcast_log(log_entry)

    except Exception as e:
        bot_state = BotState.ERROR
        await broadcast_state()

async def stop_bot():
    """Stop the arb executor"""
    global bot_state, bot_process

    if bot_state != BotState.RUNNING:
        return False, "Bot is not running"

    bot_state = BotState.STOPPING
    await broadcast_state()

    try:
        if bot_process:
            bot_process.terminate()
            try:
                await asyncio.wait_for(bot_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                bot_process.kill()
                await bot_process.wait()

            bot_process = None

        bot_state = BotState.STOPPED
        await broadcast_state()
        return True, "Bot stopped"

    except Exception as e:
        bot_state = BotState.ERROR
        await broadcast_state()
        return False, str(e)

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="OMI Edge Bot Control")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ModeRequest(BaseModel):
    mode: str

class StartRequest(BaseModel):
    clear: bool = False  # Clear trades.json before starting

@app.get("/")
async def root():
    return {"status": "OMI Edge Bot Server", "version": "1.0"}

@app.get("/status")
async def get_status():
    """Get current bot status, balance, and positions"""
    balance = await kalshi.get_balance()
    positions = await kalshi.get_positions()

    # Load trade history
    trades = []
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
    except:
        pass

    return {
        "bot_state": bot_state.value,
        "mode": execution_mode.value,
        "balance": balance,
        "positions": positions,
        "trade_count": len(trades),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/balance")
async def get_balance():
    """Get Kalshi balance"""
    balance = await kalshi.get_balance()
    return {"balance": balance}

@app.get("/positions")
async def get_positions():
    """Get current positions"""
    positions = await kalshi.get_positions()
    return {"positions": positions}

@app.get("/fills")
async def get_fills(limit: int = 50):
    """Get recent fills"""
    fills = await kalshi.get_fills(limit)
    return {"fills": fills}

@app.get("/trades")
async def get_trades():
    """Get trade history from trades.json"""
    try:
        with open('trades.json', 'r') as f:
            trades = json.load(f)
        return {"trades": trades, "session_start": session_start_time}
    except FileNotFoundError:
        return {"trades": [], "session_start": session_start_time}
    except Exception as e:
        return {"trades": [], "error": str(e), "session_start": session_start_time}

@app.post("/clear")
async def clear_data():
    """Clear all trade history and logs"""
    global log_queue, session_start_time

    # Clear trades.json
    try:
        with open('trades.json', 'w') as f:
            json.dump([], f)
    except Exception as e:
        pass

    # Clear log queue
    while not log_queue.empty():
        try:
            log_queue.get_nowait()
        except:
            break

    # Reset session
    session_start_time = datetime.now().isoformat()

    # Broadcast clear to all clients
    clear_log = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "message": "\n=== DATA CLEARED - FRESH START ==="
    }
    await broadcast_log(clear_log)

    return {"success": True, "message": "All data cleared", "session_start": session_start_time}

@app.post("/start")
async def start(request: StartRequest = None):
    """Start the bot. Optional: POST {"clear": true} to clear old trades first."""
    clear = request.clear if request else False
    success, message = await start_bot(clear=clear)
    if success:
        return {"success": True, "message": message, "state": bot_state.value, "cleared": clear}
    raise HTTPException(status_code=400, detail=message)

@app.post("/stop")
async def stop():
    """Stop the bot"""
    success, message = await stop_bot()
    if success:
        return {"success": True, "message": message, "state": bot_state.value}
    raise HTTPException(status_code=400, detail=message)

@app.post("/mode")
async def set_mode(request: ModeRequest):
    """Set execution mode (paper/live)"""
    global execution_mode

    if bot_state == BotState.RUNNING:
        raise HTTPException(status_code=400, detail="Cannot change mode while bot is running")

    if request.mode.lower() == "live":
        execution_mode = ExecutionMode.LIVE
    elif request.mode.lower() == "paper":
        execution_mode = ExecutionMode.PAPER
    else:
        raise HTTPException(status_code=400, detail="Invalid mode. Use 'paper' or 'live'")

    await broadcast_state()
    return {"success": True, "mode": execution_mode.value}

@app.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent logs"""
    logs = []
    temp_queue = Queue()

    while not log_queue.empty() and len(logs) < limit:
        try:
            entry = log_queue.get_nowait()
            logs.append(entry)
            temp_queue.put(entry)
        except:
            break

    # Put logs back
    while not temp_queue.empty():
        try:
            log_queue.put(temp_queue.get_nowait())
        except:
            break

    return {"logs": logs[-limit:]}

@app.get("/markets")
async def get_markets():
    """Get market mapping and spread data"""
    try:
        with open('market_data.json', 'r') as f:
            return json.load(f)
    except:
        return {"kalshi_games": [], "match_stats": {}, "spreads": []}

@app.get("/spreads")
async def get_spreads():
    """Get spread data only"""
    try:
        with open('market_data.json', 'r') as f:
            data = json.load(f)
        return {"spreads": data.get("spreads", []), "timestamp": data.get("timestamp")}
    except:
        return {"spreads": [], "timestamp": None}

@app.get("/volume")
async def get_volume():
    """Get volume data by sport and trends"""
    try:
        with open('market_data.json', 'r') as f:
            data = json.load(f)
        return {
            "volume_by_sport": data.get("volume_by_sport", {}),
            "volume_history": data.get("volume_history", []),
            "total_volume": data.get("total_volume", {"kalshi": 0, "pm": 0, "total": 0}),
            "timestamp": data.get("timestamp")
        }
    except:
        return {"volume_by_sport": {}, "volume_history": [], "total_volume": {"kalshi": 0, "pm": 0, "total": 0}, "timestamp": None}

@app.get("/matchups/{sport}")
async def get_matchups(sport: str):
    """Get all matchups for a specific sport"""
    try:
        with open('market_data.json', 'r') as f:
            data = json.load(f)

        spreads = data.get("spreads", [])
        sport_spreads = [s for s in spreads if s.get("sport", "").upper() == sport.upper()]

        # Group by game
        game_map = {}
        for s in sport_spreads:
            game = s.get("game", "")
            if game not in game_map:
                game_map[game] = {
                    "game_id": f"{game}-{s.get('team', '')}",
                    "sport": s.get("sport", ""),
                    "game": game,
                    "teams": [s.get("team", "")],
                    "kalshi_price": s.get("k_bid", 0),
                    "pm_price": s.get("pm_ask", 0),
                    "spread": s.get("spread", 0),
                    "status": s.get("status", "NO_EDGE"),
                    "is_live": False,  # Could be enhanced with live game detection
                    "start_time": None,
                    "ticker": s.get("ticker", ""),
                    "pm_slug": s.get("pm_slug", ""),
                }
            else:
                # Add team to existing game
                if s.get("team") not in game_map[game]["teams"]:
                    game_map[game]["teams"].append(s.get("team", ""))
                # Update spread if this one is better
                if abs(s.get("spread", 0)) > abs(game_map[game]["spread"]):
                    game_map[game]["spread"] = s.get("spread", 0)
                    game_map[game]["status"] = s.get("status", "NO_EDGE")

        return {"matchups": list(game_map.values()), "sport": sport}
    except Exception as e:
        return {"matchups": [], "sport": sport, "error": str(e)}

@app.get("/game/{game_id}/prices")
async def get_game_prices(game_id: str, hours: float = 0, max_points: int = 500):
    """Get price history for a specific game from ALL CSV data files.

    CSV format: game_key,sport,game_id,team,timestamp,scan_num,kalshi_bid,kalshi_ask,pm_bid,pm_ask,spread_buy_pm,spread_buy_k,has_arb
    Example: nba:26JAN30BKNUTA:BKN,nba,26JAN30BKNUTA,BKN,1769787376.21,2032,57,58,55,57,0,-2,False

    UI sends game_id like: "26JAN30BKNUTA-BKN" (game-team format)

    Query params:
    - hours: Filter to last N hours (0 = all data)
    - max_points: Maximum points to return (for performance)
    """
    import csv
    import glob

    try:
        # Parse game_id from UI (format: "GAMEID-TEAM" or just "GAMEID")
        parts = game_id.rsplit("-", 1)
        search_game_id = parts[0] if parts else game_id
        search_team = parts[1] if len(parts) > 1 else ""

        print(f"[API] Loading prices for game_id={search_game_id}, team={search_team}, hours={hours}")

        # Get current market data for metadata
        matching_spread = None
        try:
            with open('market_data.json', 'r') as f:
                market_data = json.load(f)
            spreads = market_data.get("spreads", [])
            for s in spreads:
                s_game = s.get("game", "")
                s_team = s.get("team", "")
                if (search_game_id in s_game or s_game in search_game_id) and \
                   (not search_team or search_team == s_team):
                    matching_spread = s
                    break
        except Exception as e:
            print(f"[API] Could not load market_data.json: {e}")

        # Calculate time filter
        now = time.time()
        min_timestamp = now - (hours * 3600) if hours > 0 else 0

        # Load price history from ALL CSV files
        all_prices = []
        try:
            # Get all price history files (current + historical)
            csv_files = []

            # Main current session file
            if os.path.exists('price_history.csv'):
                csv_files.append('price_history.csv')

            # All timestamped historical files
            historical_files = sorted(glob.glob('price_history_*.csv'))
            csv_files.extend(historical_files)

            print(f"[API] Found {len(csv_files)} CSV files to scan")

            total_rows = 0
            total_matches = 0

            for csv_file in csv_files:
                try:
                    with open(csv_file, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            total_rows += 1
                            row_game_id = row.get('game_id', '')
                            row_team = row.get('team', '')

                            # Match game_id and optionally team
                            if row_game_id == search_game_id and (not search_team or row_team == search_team):
                                ts = float(row.get('timestamp', 0))

                                # Apply time filter
                                if min_timestamp > 0 and ts < min_timestamp:
                                    continue

                                total_matches += 1
                                ts_str = datetime.fromtimestamp(ts).isoformat() if ts > 0 else datetime.now().isoformat()

                                all_prices.append({
                                    "timestamp": ts_str,
                                    "unix_ts": ts,
                                    "kalshi_bid": float(row.get('kalshi_bid', 0)),
                                    "kalshi_ask": float(row.get('kalshi_ask', 0)),
                                    "pm_bid": float(row.get('pm_bid', 0)),
                                    "pm_ask": float(row.get('pm_ask', 0)),
                                    "spread": float(row.get('spread_buy_pm', 0)),
                                })
                except Exception as file_err:
                    print(f"[API] Error reading {csv_file}: {file_err}")
                    continue

            print(f"[API] Scanned {total_rows} total rows, found {total_matches} matches for {search_game_id}")

        except Exception as csv_err:
            print(f"[API] CSV read error: {csv_err}")

        # Sort by timestamp and remove duplicates
        all_prices.sort(key=lambda x: x.get('unix_ts', 0))

        # Remove near-duplicate timestamps (within 0.5 seconds)
        if all_prices:
            deduped = [all_prices[0]]
            for p in all_prices[1:]:
                if p['unix_ts'] - deduped[-1]['unix_ts'] > 0.5:
                    deduped.append(p)
            all_prices = deduped
            print(f"[API] After dedup: {len(all_prices)} points")

        # Smart downsampling based on requested max_points
        prices = all_prices
        if len(prices) > max_points:
            step = len(prices) // max_points
            sampled = prices[::step]
            # Always keep first and last points
            if prices[0] not in sampled:
                sampled.insert(0, prices[0])
            if prices[-1] not in sampled:
                sampled.append(prices[-1])
            prices = sampled
            print(f"[API] Downsampled to {len(prices)} points (max={max_points})")

        # Remove unix_ts from output (was only for sorting)
        for p in prices:
            p.pop('unix_ts', None)

        # If no CSV data, create single point from current spread data
        if not prices and matching_spread:
            prices = [{
                "timestamp": datetime.now().isoformat(),
                "kalshi_bid": matching_spread.get("k_bid", 0),
                "kalshi_ask": matching_spread.get("k_ask", matching_spread.get("k_bid", 0) + 1),
                "pm_bid": matching_spread.get("pm_bid", matching_spread.get("pm_ask", 0) - 1),
                "pm_ask": matching_spread.get("pm_ask", 0),
                "spread": matching_spread.get("spread", 0),
            }]
            print(f"[API] Using fallback from market_data.json")

        # Calculate stats
        current_spread = 0
        arb_status = "NO_EDGE"
        game_start = None
        game_duration_hours = 0

        if prices:
            latest = prices[-1]
            k_bid = latest.get("kalshi_bid", 0)
            pm_ask = latest.get("pm_ask", 0)
            current_spread = k_bid - pm_ask
            if current_spread > 0:
                arb_status = "ARB"
            elif current_spread >= -2:
                arb_status = "CLOSE"

            # Calculate game duration
            game_start = prices[0]["timestamp"]
            try:
                start_dt = datetime.fromisoformat(prices[0]["timestamp"])
                end_dt = datetime.fromisoformat(prices[-1]["timestamp"])
                game_duration_hours = (end_dt - start_dt).total_seconds() / 3600
            except:
                pass

        return {
            "game_id": game_id,
            "sport": matching_spread.get("sport", "") if matching_spread else "",
            "game": search_game_id,
            "team": search_team or (matching_spread.get("team", "") if matching_spread else ""),
            "ticker": matching_spread.get("ticker", "") if matching_spread else "",
            "pm_slug": matching_spread.get("pm_slug", "") if matching_spread else "",
            "is_live": len(prices) > 10,
            "start_time": game_start,
            "prices": prices,
            "current_spread": current_spread,
            "arb_status": arb_status,
            "data_points": len(prices),
            "total_data_points": len(all_prices),
            "game_duration_hours": round(game_duration_hours, 2),
            "time_filter_hours": hours,
        }
    except Exception as e:
        import traceback
        print(f"[API] Error: {e}\n{traceback.format_exc()}")
        return {"error": str(e), "game_id": game_id, "prices": []}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_clients.add(websocket)

    # Send initial state
    initial_state = {
        "type": "state",
        "data": {
            "bot_state": bot_state.value,
            "mode": execution_mode.value,
            "timestamp": datetime.now().isoformat()
        }
    }
    await websocket.send_text(json.dumps(initial_state))

    # Send recent logs
    logs = []
    temp_list = []
    while not log_queue.empty() and len(logs) < 50:
        try:
            entry = log_queue.get_nowait()
            logs.append(entry)
            temp_list.append(entry)
        except:
            break

    # Put logs back
    for entry in temp_list:
        if not log_queue.full():
            log_queue.put(entry)

    if logs:
        await websocket.send_text(json.dumps({"type": "logs", "data": logs}))

    try:
        while True:
            # Keep connection alive, handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            elif message.get("type") == "get_status":
                balance = await kalshi.get_balance()
                positions = await kalshi.get_positions()
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "data": {
                        "balance": balance,
                        "positions": positions,
                        "bot_state": bot_state.value,
                        "mode": execution_mode.value
                    }
                }))

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    except Exception as e:
        connected_clients.discard(websocket)

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    port = int(os.environ.get("BOT_SERVER_PORT", 8001))
    print("=" * 60)
    print("OMI Edge Bot Control Server")
    print("=" * 60)
    print(f"Starting server on http://0.0.0.0:{port}")
    print(f"WebSocket: ws://0.0.0.0:{port}/ws")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=port)
