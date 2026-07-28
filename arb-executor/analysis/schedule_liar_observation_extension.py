#!/usr/bin/env python3
"""Extend schedule-liar observation without repeating the initial cancel pass.

This operations-only helper polls the fully paginated resting order book until
one additional reconcile receipt is observed (bounded by seven minutes).  It
uses only the deployed GET/DELETE path and cancels each newly observed resting
tennis BUY order ID at most once.  It never posts, edits remote files, changes
configuration, or restarts the service.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


REMOTE_PROGRAM = r'''
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path("/root/Omi-Workspace")
EXEC = ROOT / "arb-executor"
sys.path.insert(0, str(EXEC))
os.chdir(EXEC)
import aiohttp
import live_v4 as live

MAX_DURATION = int(sys.argv[1])
INTERVAL = int(sys.argv[2])
TENNIS_PREFIXES = (
    "KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH",
    "KXWTACHALLENGERMATCH", "KXITFMATCH", "KXITFWMATCH",
)
LOG = Path("/tmp/live_v4.log")
HEARTBEAT = Path("/tmp/heartbeat_live_v3.json")


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def is_tennis(ticker):
    return str(ticker or "").startswith(TENNIS_PREFIXES)


def normalize_order(row):
    value = row.get("remaining_count_fp")
    if value in (None, ""):
        value = row.get("remaining_count")
    price = row.get("yes_price_dollars")
    return {
        "order_id": str(row.get("order_id") or ""),
        "ticker": str(row.get("ticker") or ""),
        "action": str(row.get("action") or "").lower(),
        "side": row.get("side"),
        "price_cents": (
            int(round(float(price) * 100)) if price not in (None, "") else None
        ),
        "remaining_quantity": (
            float(value) if value not in (None, "") else None
        ),
        "raw_exchange_row": row,
    }


async def fetch_orders(session, ak, pk, rl):
    rows = []
    cursor = None
    pages = 0
    seen = set()
    while True:
        path = "/trade-api/v2/portfolio/orders?status=resting"
        if cursor:
            path += "&cursor=" + cursor
        data = await live.api_get(session, ak, pk, path, rl)
        pages += 1
        if not isinstance(data, dict) or not isinstance(data.get("orders"), list):
            raise RuntimeError("unprovable_paginated_order_read")
        rows.extend(data["orders"])
        nxt = data.get("cursor") or None
        if not nxt:
            return [normalize_order(row) for row in rows], pages
        if nxt in seen or pages >= 100:
            raise RuntimeError("invalid_order_pagination")
        seen.add(nxt)
        cursor = nxt


async def fetch_positions(session, ak, pk, rl):
    rows = []
    cursor = None
    pages = 0
    seen = set()
    while True:
        path = (
            "/trade-api/v2/portfolio/positions?count_filter=position"
            "&settlement_status=unsettled"
        )
        if cursor:
            path += "&cursor=" + cursor
        data = await live.api_get(session, ak, pk, path, rl)
        pages += 1
        if not isinstance(data, dict) or not isinstance(
                data.get("market_positions"), list):
            raise RuntimeError("unprovable_paginated_position_read")
        rows.extend(data["market_positions"])
        nxt = data.get("cursor") or None
        if not nxt:
            return rows, pages
        if nxt in seen or pages >= 100:
            raise RuntimeError("invalid_position_pagination")
        seen.add(nxt)
        cursor = nxt


def read_new_log(offset):
    if not LOG.exists():
        return "", offset
    with LOG.open("rb") as handle:
        handle.seek(offset)
        raw = handle.read()
        return raw.decode("utf-8", errors="replace"), handle.tell()


async def main():
    ak, pk = live.load_credentials()
    if not ak:
        raise RuntimeError("KALSHI_API_KEY unavailable")
    rl = live.RateLimiter()
    pid_rows = run("pgrep", "-f", "^python3 -u live_v4.py$").splitlines()
    if len(pid_rows) != 1:
        raise RuntimeError("live_process_identity_not_unique")
    source = EXEC / "live_v4.py"
    head = run("git", "-C", str(ROOT), "rev-parse", "HEAD")
    blob = run("git", "-C", str(ROOT), "hash-object",
               "arb-executor/live_v4.py")
    start_epoch = time.time()
    start_utc = now()
    log_offset = LOG.stat().st_size if LOG.exists() else 0
    attempted = set()
    cancellations = []
    samples = []
    log_text = ""
    reconcile_lines = []

    async with aiohttp.ClientSession() as session:
        while True:
            orders, order_pages = await fetch_orders(session, ak, pk, rl)
            positions, position_pages = await fetch_positions(session, ak, pk, rl)
            new_entries = [
                order for order in orders
                if order["action"] == "buy" and is_tennis(order["ticker"])
                and order["order_id"] not in attempted
            ]
            for order in new_entries:
                attempted.add(order["order_id"])
                endpoint = live.ORDER_CREATE_V2_PATH + "/" + order["order_id"]
                request_utc = now()
                ok = await live.api_delete(session, ak, pk, endpoint, rl)
                cancellations.append({
                    "order_id": order["order_id"],
                    "ticker": order["ticker"],
                    "side": order["side"],
                    "action": order["action"],
                    "price_cents": order["price_cents"],
                    "remaining_quantity": order["remaining_quantity"],
                    "classification": "tennis_entry_buy",
                    "classification_evidence": (
                        "exchange action=buy and frozen tennis-series prefix"
                    ),
                    "request_utc": request_utc,
                    "endpoint": "DELETE " + endpoint,
                    "route": "running live_v4.api_delete / _real_api_delete",
                    "route_response": bool(ok),
                })
            delta, log_offset = read_new_log(log_offset)
            log_text += delta
            reconcile_lines = [
                line for line in log_text.splitlines()
                if "] RECONCILE " in line
            ]
            heartbeat = (
                json.loads(HEARTBEAT.read_text()) if HEARTBEAT.exists() else None
            )
            samples.append({
                "captured_utc": now(),
                "resting_tennis_entries_before_sample_cancels": len(new_entries),
                "resting_tennis_exits": sum(
                    order["action"] == "sell" and is_tennis(order["ticker"])
                    for order in orders
                ),
                "held_positions": len(positions),
                "order_pages": order_pages,
                "position_pages": position_pages,
                "heartbeat": heartbeat,
            })
            elapsed = time.time() - start_epoch
            if reconcile_lines and elapsed >= 30:
                break
            if elapsed >= MAX_DURATION:
                break
            await asyncio.sleep(INTERVAL)

        final_orders, final_order_pages = await fetch_orders(
            session, ak, pk, rl
        )
        final_positions, final_position_pages = await fetch_positions(
            session, ak, pk, rl
        )
    end_epoch = time.time()
    final_entries = [
        order for order in final_orders
        if order["action"] == "buy" and is_tennis(order["ticker"])
    ]
    final_exits = [
        order for order in final_orders
        if order["action"] == "sell" and is_tennis(order["ticker"])
    ]
    entry_receipts = [
        line for line in log_text.splitlines()
        if "ORDER_PLACED" in line and '"action": "buy"' in line
        and any(prefix in line for prefix in TENNIS_PREFIXES)
    ]
    conception_receipts = [
        line for line in log_text.splitlines()
        if ("CONCEPTION_STAMP" in line or "V4_PLACE" in line)
        and any(prefix in line for prefix in TENNIS_PREFIXES)
    ]
    fill_receipts = [
        line for line in log_text.splitlines()
        if "ENTRY_FILLED" in line
        and any(prefix in line for prefix in TENNIS_PREFIXES)
    ]
    result = {
        "schema_version": "schedule-liar-observation-extension-v1",
        "start_utc": start_utc,
        "end_utc": now(),
        "duration_seconds": round(end_epoch - start_epoch, 3),
        "vps_head": head,
        "live_pid": int(pid_rows[0]),
        "live_source": {
            "git_blob": blob,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "bytes": source.stat().st_size,
        },
        "reconcile_cycle_receipts": reconcile_lines,
        "reconcile_cycle_count": len(reconcile_lines),
        "cancellation_ledger": cancellations,
        "samples": samples,
        "tennis_entry_order_receipts": entry_receipts,
        "tennis_conception_receipts": conception_receipts,
        "tennis_entry_fill_receipts": fill_receipts,
        "final_resting_tennis_entry_buys": final_entries,
        "final_resting_tennis_exit_sells": final_exits,
        "final_exchange_positions": final_positions,
        "pagination": {
            "orders_pages": final_order_pages,
            "positions_pages": final_position_pages,
        },
        "halt_control": "UNAVAILABLE",
        "service_restarts": 0,
        "order_posts_by_tool": 0,
        "position_mutations_by_tool": 0,
        "remote_files_written": 0,
        "log_slice_sha256": hashlib.sha256(
            log_text.encode("utf-8")
        ).hexdigest(),
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


asyncio.run(main())
'''


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="root@104.131.191.95")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-duration-seconds", type=int, default=420)
    parser.add_argument("--interval-seconds", type=int, default=15)
    args = parser.parse_args()
    command = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
        args.host,
        "cd /root/Omi-Workspace/arb-executor && python3 - %d %d" % (
            args.max_duration_seconds, args.interval_seconds
        ),
    ]
    proc = subprocess.run(
        command, input=REMOTE_PROGRAM, text=True, capture_output=True
    )
    if proc.returncode:
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    data = json.loads(proc.stdout)
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(data)
    output.write_bytes(payload)
    print(json.dumps({
        "output": str(output),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "reconcile_cycle_count": data["reconcile_cycle_count"],
        "new_entry_cancellations": len(data["cancellation_ledger"]),
        "final_entries": len(data["final_resting_tennis_entry_buys"]),
        "service_restarts": data["service_restarts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
