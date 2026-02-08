#!/usr/bin/env python3
"""
Auto-refresh mapper for pregame arbitrage executor.

Runs pregame_mapper.py every 30 minutes and restarts the executor
when new games are discovered.

Usage:
    python auto_mapper.py [--interval 1800] [--spread-min 3] [--contracts 1]
"""

import time
import subprocess
import json
import os
import signal
import sys
import argparse
from datetime import datetime

# Configuration
MAPPER_SCRIPT = "pregame_mapper.py"
EXECUTOR_SCRIPT = "arb_executor_ws.py"
MAPPINGS_FILE = "verified_mappings.json"


def log(msg: str):
    """Log with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def get_mapping_count() -> int:
    """Get current number of verified mappings."""
    try:
        with open(MAPPINGS_FILE) as f:
            return len(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def get_mapping_games() -> set:
    """Get set of game keys from current mappings."""
    try:
        with open(MAPPINGS_FILE) as f:
            mappings = json.load(f)
            return {m.get("game_key", "") for m in mappings}
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def run_mapper() -> bool:
    """Run the pregame mapper. Returns True if successful."""
    try:
        result = subprocess.run(
            ["python", MAPPER_SCRIPT],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log("ERROR: Mapper timed out after 120s")
        return False
    except Exception as e:
        log(f"ERROR: Mapper failed: {e}")
        return False


def start_executor(spread_min: int, contracts: int, max_trades: int) -> subprocess.Popen:
    """Start the WebSocket executor as a background process."""
    cmd = [
        "python", EXECUTOR_SCRIPT,
        "--live",
        "--spread-min", str(spread_min),
        "--contracts", str(contracts),
        "--max-trades", str(max_trades)
    ]
    log(f"Starting executor: {' '.join(cmd)}")

    # Start executor, redirect output to log file
    log_file = open("logs/executor_auto.log", "a")
    proc = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True
    )
    log(f"Executor started with PID {proc.pid}")
    return proc


def stop_executor(proc: subprocess.Popen):
    """Gracefully stop the executor process."""
    if proc and proc.poll() is None:
        log(f"Stopping executor PID {proc.pid}...")
        proc.terminate()
        try:
            proc.wait(timeout=10)
            log("Executor stopped gracefully")
        except subprocess.TimeoutExpired:
            log("Executor didn't stop, killing...")
            proc.kill()
            proc.wait()


def main():
    parser = argparse.ArgumentParser(description="Auto-refresh mapper for arb executor")
    parser.add_argument("--interval", type=int, default=1800, help="Refresh interval in seconds (default: 1800 = 30 min)")
    parser.add_argument("--spread-min", type=int, default=3, help="Minimum spread in cents (default: 3)")
    parser.add_argument("--contracts", type=int, default=1, help="Max contracts per trade (default: 1)")
    parser.add_argument("--max-trades", type=int, default=10, help="Max trades before stopping (default: 10)")
    parser.add_argument("--no-executor", action="store_true", help="Only refresh mappings, don't manage executor")
    args = parser.parse_args()

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    log("=" * 60)
    log("AUTO-MAPPER STARTED")
    log(f"Refresh interval: {args.interval}s ({args.interval // 60} min)")
    log(f"Executor params: spread={args.spread_min}c, contracts={args.contracts}, max-trades={args.max_trades}")
    log("=" * 60)

    executor_proc = None
    prev_games = set()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        log("\nShutting down...")
        stop_executor(executor_proc)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while True:
            # Get current state before refresh
            prev_count = get_mapping_count()
            prev_games = get_mapping_games()

            # Run mapper
            log("Running pregame_mapper.py...")
            success = run_mapper()

            if not success:
                log("Mapper failed, will retry next interval")
                time.sleep(args.interval)
                continue

            # Check results
            new_count = get_mapping_count()
            new_games = get_mapping_games()

            added_games = new_games - prev_games
            removed_games = prev_games - new_games

            log(f"Mappings: {new_count} verified")

            if added_games:
                log(f"NEW GAMES ADDED: {len(added_games)}")
                for game in sorted(added_games):
                    log(f"  + {game}")

            if removed_games:
                log(f"Games removed: {len(removed_games)}")
                for game in sorted(removed_games):
                    log(f"  - {game}")

            # Restart executor if games changed
            if not args.no_executor:
                should_restart = False

                if executor_proc is None:
                    log("No executor running, starting...")
                    should_restart = True
                elif executor_proc.poll() is not None:
                    log(f"Executor exited (code {executor_proc.returncode}), restarting...")
                    should_restart = True
                elif added_games:
                    log("New games found, restarting executor...")
                    should_restart = True

                if should_restart:
                    stop_executor(executor_proc)
                    executor_proc = start_executor(args.spread_min, args.contracts, args.max_trades)

            # Wait for next refresh
            next_refresh = datetime.now().timestamp() + args.interval
            next_time = datetime.fromtimestamp(next_refresh).strftime("%H:%M:%S")
            log(f"Next refresh at {next_time}")
            log("-" * 40)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        log("\nInterrupted by user")
    finally:
        stop_executor(executor_proc)
        log("Auto-mapper stopped")


if __name__ == "__main__":
    main()
