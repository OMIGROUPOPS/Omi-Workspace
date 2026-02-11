#!/usr/bin/env python3
"""
auto_mapper.py — Automated pregame mapping scheduler.

Runs pregame_mapper.py --incremental on a loop, detects new/changed mappings,
and writes a signal file so the executor can hot-reload without restarting.

Usage:
    python auto_mapper.py --interval 30          # Every 30 minutes (default)
    python auto_mapper.py --interval 15 --once   # Run once and exit
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAPPING_FILE = os.path.join(SCRIPT_DIR, "verified_mappings.json")
SIGNAL_FILE = os.path.join(SCRIPT_DIR, "mappings_updated.flag")
LOG_FILE = os.path.join(SCRIPT_DIR, "logs", "auto_mapper.log")

os.makedirs(os.path.join(SCRIPT_DIR, "logs"), exist_ok=True)


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def read_mapping_keys() -> set:
    """Read current game keys from verified_mappings.json."""
    if not os.path.exists(MAPPING_FILE):
        return set()
    try:
        with open(MAPPING_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("games", {}).keys())
    except (json.JSONDecodeError, KeyError):
        return set()


def write_signal(new_count: int, prev_count: int, added: list):
    """Write signal file so the executor knows to reload."""
    with open(SIGNAL_FILE, "w") as f:
        json.dump({
            "updated_at": datetime.now().isoformat(),
            "prev_count": prev_count,
            "new_count": new_count,
            "added_games": added[:20],
        }, f, indent=2)
    log(f"Signal written -> {SIGNAL_FILE}")


async def run_mapper_once() -> bool:
    """Run pregame_mapper.py --incremental. Returns True if mappings changed."""
    before = read_mapping_keys()
    log(f"Before: {len(before)} mappings")

    mapper_script = os.path.join(SCRIPT_DIR, "pregame_mapper.py")
    cmd = [sys.executable, mapper_script, "--incremental"]

    log(f"Running: {' '.join(cmd)}")
    start = time.time()

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=SCRIPT_DIR,
    )
    stdout, _ = await proc.communicate()
    elapsed = time.time() - start

    if proc.returncode != 0:
        log(f"Mapper FAILED (exit {proc.returncode}, {elapsed:.1f}s)")
        if stdout:
            for line in stdout.decode(errors="replace").strip().split("\n")[-5:]:
                log(f"  | {line}")
        return False

    log(f"Mapper OK ({elapsed:.1f}s)")

    after = read_mapping_keys()
    log(f"After: {len(after)} mappings")

    added = sorted(after - before)
    removed = sorted(before - after)

    if added:
        log(f"NEW GAMES ({len(added)}):")
        for k in added:
            log(f"  + {k}")
    if removed:
        log(f"Removed ({len(removed)}):")
        for k in removed:
            log(f"  - {k}")

    changed = added or removed
    if changed:
        write_signal(len(after), len(before), added)
    else:
        log("No changes")

    return bool(changed)


async def run_loop(interval_minutes: int, once: bool):
    log(f"Auto-mapper started (interval={interval_minutes}m, once={once})")

    while True:
        try:
            await run_mapper_once()
        except Exception as e:
            log(f"ERROR: {e}")

        if once:
            log("Single run complete, exiting")
            break

        log(f"Sleeping {interval_minutes}m...")
        await asyncio.sleep(interval_minutes * 60)


def main():
    parser = argparse.ArgumentParser(description="Automated pregame mapper scheduler")
    parser.add_argument("--interval", type=int, default=120, help="Minutes between runs (default: 120)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    try:
        asyncio.run(run_loop(args.interval, args.once))
    except KeyboardInterrupt:
        log("Interrupted, shutting down")


if __name__ == "__main__":
    main()
