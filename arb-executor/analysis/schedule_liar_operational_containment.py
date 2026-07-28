#!/usr/bin/env python3
"""One-time schedule-liar tennis-entry containment receipt builder.

This is operations tooling, not live-engine code.  It runs the already-deployed
Kalshi GET/DELETE route in the live checkout over SSH, never imports or changes
configuration, and never posts an order.  The only exchange mutation it can
perform is cancelling a resting tennis BUY.
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
import re
import subprocess
import sys
import time

ROOT = Path("/root/Omi-Workspace")
EXEC = ROOT / "arb-executor"
sys.path.insert(0, str(EXEC))
os.chdir(EXEC)
import aiohttp
import live_v4 as live

MODE = sys.argv[1]
DURATION = int(sys.argv[2])
INTERVAL = int(sys.argv[3])
INCIDENT_LINE = int(sys.argv[4])
TENNIS_PREFIXES = (
    "KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH",
    "KXWTACHALLENGERMATCH", "KXITFMATCH", "KXITFWMATCH",
)
LOG = Path("/tmp/live_v4.log")
STATE = EXEC / "state" / "live_v4_resting.json"
HEARTBEAT = Path("/tmp/heartbeat_live_v3.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def is_tennis(ticker):
    return str(ticker or "").startswith(TENNIS_PREFIXES)


def price_cents(row):
    for key in ("yes_price_dollars", "price", "yes_price"):
        value = row.get(key)
        if value not in (None, ""):
            value = float(value)
            return int(round(value * 100)) if value < 2 else int(round(value))
    return None


def remaining_qty(row):
    for key in ("remaining_count_fp", "remaining_count", "count_fp", "count"):
        value = row.get(key)
        if value not in (None, ""):
            return float(value)
    return None


def normalize_order(row):
    ticker = str(row.get("ticker") or "")
    action = str(row.get("action") or "").lower()
    classification = (
        "tennis_entry_buy" if is_tennis(ticker) and action == "buy"
        else "tennis_exit_sell" if is_tennis(ticker) and action == "sell"
        else "other"
    )
    return {
        "order_id": str(row.get("order_id") or ""),
        "ticker": ticker,
        "event_id": ticker.rsplit("-", 1)[0] if "-" in ticker else "",
        "action": action,
        "side": row.get("side"),
        "status": row.get("status"),
        "price_cents": price_cents(row),
        "remaining_quantity": remaining_qty(row),
        "initial_count_fp": row.get("initial_count_fp"),
        "fill_count_fp": row.get("fill_count_fp"),
        "client_order_id": row.get("client_order_id"),
        "created_time": row.get("created_time"),
        "classification": classification,
        "classification_evidence": (
            "exchange action=buy and ticker has frozen tennis-series prefix"
            if classification == "tennis_entry_buy"
            else "exchange action=sell and ticker has frozen tennis-series prefix"
            if classification == "tennis_exit_sell"
            else "not a resting tennis entry/exit order"
        ),
        "raw_exchange_row": row,
    }


def normalize_position(row):
    ticker = str(row.get("ticker") or "")
    return {
        "ticker": ticker,
        "event_id": ticker.rsplit("-", 1)[0] if "-" in ticker else "",
        "is_tennis": is_tennis(ticker),
        "exchange_position_qty": float(row.get("position_fp") or 0),
        "market_exposure_dollars": row.get("market_exposure_dollars"),
        "total_traded_dollars": row.get("total_traded_dollars"),
        "realized_pnl_dollars": row.get("realized_pnl_dollars"),
        "raw_exchange_row": row,
    }


async def fetch_all(session, ak, pk, rl, path, collection):
    rows = []
    cursor = None
    seen = set()
    pages = 0
    while True:
        full = path + (("&" if "?" in path else "?") + "cursor=" + cursor
                       if cursor else "")
        data = await live.api_get(session, ak, pk, full, rl)
        pages += 1
        if not isinstance(data, dict) or not isinstance(data.get(collection), list):
            raise RuntimeError("unprovable_paginated_read:%s:page=%d" %
                               (collection, pages))
        rows.extend(data[collection])
        nxt = data.get("cursor") or None
        if not nxt:
            break
        if nxt in seen:
            raise RuntimeError("repeated_cursor:%s:page=%d" % (collection, pages))
        seen.add(nxt)
        cursor = nxt
        if pages >= 100:
            raise RuntimeError("page_bound:%s" % collection)
    return rows, pages


def read_state():
    if not STATE.exists():
        return {"available": False}
    raw = STATE.read_bytes()
    parsed = json.loads(raw)
    return {
        "available": True,
        "path": str(STATE),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "mtime_epoch": STATE.stat().st_mtime,
        "shape": parsed.get("_shape") if isinstance(parsed, dict) else None,
        "legs": parsed.get("legs", {}) if isinstance(parsed, dict) else {},
        "unmatched_holdings": (
            parsed.get("unmatched_holdings", {}) if isinstance(parsed, dict) else {}
        ),
    }


def log_records_since(line_start):
    labels = (
        "CONCEPTION_STAMP", "V4_PLACE", "ORDER_PLACED", "ORDER_CANCELLED",
        "V4_MOVE_REPOST", "ENTRY_FILLED", "ENTRY_PARTIAL",
        "RECONCILE_V4_ADOPTED", "BUY_BLOCKED_CONCEPTION_HALT",
        "CYCLE_CAP_REFUSED", "CONCEPTION_HALT_ARMED",
        "CONCEPTION_HALT_CLEARED", "RECONCILE ",
        "V4_EXIT_POSTED", "RECONCILE_EXIT", "EXIT_",
    )
    out = []
    last_halt = None
    reconcile = []
    if not LOG.exists():
        return out, last_halt, reconcile
    with LOG.open("r", errors="replace") as f:
        for n, line in enumerate(f, 1):
            if n < line_start:
                continue
            if "CONCEPTION_HALT_ARMED" in line:
                last_halt = {"line": n, "state": "ARMED", "raw": line.rstrip()}
            elif "CONCEPTION_HALT_CLEARED" in line:
                last_halt = {"line": n, "state": "CLEAR", "raw": line.rstrip()}
            if "] RECONCILE " in line:
                reconcile.append({"line": n, "raw": line.rstrip()})
            if not any(label in line for label in labels):
                continue
            ticker_match = re.search(r"(KX[A-Z0-9]+MATCH-[A-Z0-9-]+)", line)
            ticker = ticker_match.group(1) if ticker_match else ""
            if ticker and not is_tennis(ticker):
                continue
            out.append({"line": n, "ticker": ticker, "raw": line.rstrip()})
    return out, last_halt, reconcile


def infer_engine_booked(exchange_positions, actions):
    result = {}
    for pos in exchange_positions:
        ticker = pos["ticker"]
        candidates = []
        for rec in actions:
            if rec.get("ticker") != ticker:
                continue
            raw = rec["raw"]
            if not any(label in raw for label in (
                    "ENTRY_FILLED", "ENTRY_PARTIAL", "RECONCILE_V4_ADOPTED")):
                continue
            qty = None
            for pattern in (
                r'"qty"\s*:\s*([0-9.]+)',
                r'"entry_qty"\s*:\s*([0-9.]+)',
                r'"new_fills"\s*:\s*([0-9.]+)',
            ):
                match = re.search(pattern, raw)
                if match:
                    qty = float(match.group(1))
                    break
            candidates.append({"line": rec["line"], "qty": qty, "raw": raw})
        if candidates:
            latest = candidates[-1]
            result[ticker] = {
                "quantity": latest["qty"],
                "status": "receipt_derived",
                "receipt": latest,
            }
        else:
            result[ticker] = {
                "quantity": None,
                "status": "unavailable_no_post_boot_booking_receipt",
            }
    return result


async def snapshot(session, ak, pk, rl, incident_line):
    positions_raw, position_pages = await fetch_all(
        session, ak, pk, rl,
        "/trade-api/v2/portfolio/positions?count_filter=position"
        "&settlement_status=unsettled",
        "market_positions",
    )
    orders_raw, order_pages = await fetch_all(
        session, ak, pk, rl,
        "/trade-api/v2/portfolio/orders?status=resting",
        "orders",
    )
    orders = [normalize_order(row) for row in orders_raw]
    positions = [normalize_position(row) for row in positions_raw]
    actions, last_halt, reconcile = log_records_since(incident_line)
    pid_rows = run("pgrep", "-f", "^python3 -u live_v4.py$").splitlines()
    if len(pid_rows) != 1:
        raise RuntimeError("live_process_identity_not_unique:%r" % pid_rows)
    pid = int(pid_rows[0])
    heartbeat = None
    if HEARTBEAT.exists():
        heartbeat = json.loads(HEARTBEAT.read_text())
    head = run("git", "-C", str(ROOT), "rev-parse", "HEAD")
    branch = run("git", "-C", str(ROOT), "rev-parse", "--abbrev-ref", "HEAD")
    blob = run("git", "-C", str(ROOT), "hash-object",
               "arb-executor/live_v4.py")
    source = EXEC / "live_v4.py"
    return {
        "captured_utc": utc_now(),
        "captured_epoch": time.time(),
        "host": run("hostname"),
        "vps_head": head,
        "vps_branch": branch,
        "live_pid": pid,
        "live_process_start": run(
            "ps", "-p", str(pid), "-o", "lstart=", "-o", "etime=", "-o", "cmd="
        ),
        "live_source": {
            "path": str(source),
            "git_blob": blob,
            "sha256": sha256_path(source),
            "bytes": source.stat().st_size,
        },
        "service_health": {
            "process_count": len(pid_rows),
            "heartbeat": heartbeat,
            "heartbeat_age_seconds": (
                round(time.time() - float(heartbeat.get("ts", 0)), 3)
                if heartbeat else None
            ),
        },
        "halt": {
            "last_receipt_since_incident": last_halt,
            "effective_state": (
                last_halt["state"] if last_halt else "CLEAR_AT_BOOT_NO_LATER_ARM"
            ),
            "persistent_operator_hold_available": False,
            "reason": (
                "running engine exposes only audit-derived _conception_halt; "
                "a passing halted_reaudit clears it automatically"
            ),
        },
        "pagination": {
            "positions_pages": position_pages,
            "orders_pages": order_pages,
        },
        "exchange_positions": positions,
        "resting_orders": orders,
        "counts": {
            "held_positions": len(positions),
            "resting_orders": len(orders),
            "tennis_entry_buys": sum(
                o["classification"] == "tennis_entry_buy" for o in orders
            ),
            "tennis_entry_buy_quantity": sum(
                o["remaining_quantity"] or 0 for o in orders
                if o["classification"] == "tennis_entry_buy"
            ),
            "tennis_exit_sells": sum(
                o["classification"] == "tennis_exit_sell" for o in orders
            ),
            "tennis_exit_sell_quantity": sum(
                o["remaining_quantity"] or 0 for o in orders
                if o["classification"] == "tennis_exit_sell"
            ),
        },
        "engine_state": read_state(),
        "engine_booked_quantities": infer_engine_booked(positions, actions),
        "tennis_conception_and_order_actions_since_incident": actions,
        "reconcile_receipts_since_incident": reconcile,
    }


async def get_order(session, ak, pk, rl, oid):
    path = "/trade-api/v2/portfolio/orders/%s" % oid
    return await live.api_get(session, ak, pk, path, rl)


async def cancel_order(session, ak, pk, rl, order, reason, reappeared):
    oid = order["order_id"]
    endpoint = live.ORDER_CREATE_V2_PATH + "/" + oid
    before = await get_order(session, ak, pk, rl, oid)
    request_utc = utc_now()
    request_epoch = time.time()
    ok = await live.api_delete(session, ak, pk, endpoint, rl)
    final = await get_order(session, ak, pk, rl, oid)
    return {
        "event_id": order["event_id"],
        "ticker": order["ticker"],
        "order_id": oid,
        "side": order["side"],
        "action": order["action"],
        "price_cents": order["price_cents"],
        "remaining_quantity": order["remaining_quantity"],
        "entry_exit_classification": order["classification"],
        "classification_evidence": order["classification_evidence"],
        "reason": reason,
        "reappeared_during_observation": reappeared,
        "request_utc": request_utc,
        "request_epoch": request_epoch,
        "endpoint": "DELETE " + endpoint,
        "route": "running live_v4.api_delete / _real_api_delete",
        "route_response": bool(ok),
        "exchange_before": before,
        "exchange_final": final,
    }


async def main():
    ak, pk = live.load_credentials()
    if not ak:
        raise RuntimeError("KALSHI_API_KEY unavailable")
    rl = live.RateLimiter()
    async with aiohttp.ClientSession() as session:
        if MODE == "snapshot":
            result = {
                "schema_version": "schedule-liar-operational-snapshot-v1",
                "mode": MODE,
                "snapshot": await snapshot(session, ak, pk, rl, INCIDENT_LINE),
                "exchange_mutations": 0,
            }
            print(json.dumps(result, sort_keys=True, separators=(",", ":")))
            return

        if MODE != "contain":
            raise RuntimeError("unsupported mode")

        pre = await snapshot(session, ak, pk, rl, INCIDENT_LINE)
        cancellation_ledger = []
        attempted = set()
        for order in pre["resting_orders"]:
            if order["classification"] != "tennis_entry_buy":
                continue
            attempted.add(order["order_id"])
            cancellation_ledger.append(await cancel_order(
                session, ak, pk, rl, order,
                "authorized one-time cancellation of every resting tennis entry buy",
                False,
            ))

        immediate_post = await snapshot(session, ak, pk, rl, INCIDENT_LINE)
        observation_start_epoch = time.time()
        observation_start_utc = utc_now()
        log_offset = LOG.stat().st_size if LOG.exists() else 0
        samples = []
        reappeared = []
        end_at = observation_start_epoch + DURATION
        while time.time() < end_at:
            await asyncio.sleep(min(INTERVAL, max(0.0, end_at - time.time())))
            snap = await snapshot(session, ak, pk, rl, INCIDENT_LINE)
            new_entries = [
                order for order in snap["resting_orders"]
                if order["classification"] == "tennis_entry_buy"
                and order["order_id"] not in attempted
            ]
            for order in new_entries:
                attempted.add(order["order_id"])
                row = await cancel_order(
                    session, ak, pk, rl, order,
                    "new tennis entry appeared during required observation; "
                    "cancelled exact order once",
                    True,
                )
                cancellation_ledger.append(row)
                reappeared.append(row)
            samples.append({
                "captured_utc": snap["captured_utc"],
                "resting_tennis_entry_buys_before_sample_cancels": len(new_entries),
                "resting_tennis_exit_sells": snap["counts"]["tennis_exit_sells"],
                "held_positions": snap["counts"]["held_positions"],
                "heartbeat_age_seconds": snap["service_health"]["heartbeat_age_seconds"],
                "halt_effective_state": snap["halt"]["effective_state"],
            })

        final = await snapshot(session, ak, pk, rl, INCIDENT_LINE)
        observation_end_epoch = time.time()
        observation_end_utc = utc_now()
        log_slice = ""
        if LOG.exists():
            with LOG.open("rb") as f:
                f.seek(log_offset)
                log_slice = f.read().decode("utf-8", errors="replace")
        lines = log_slice.splitlines()
        reconcile_lines = [line for line in lines if "] RECONCILE " in line]
        entry_order_lines = [
            line for line in lines
            if "ORDER_PLACED" in line and '"action": "buy"' in line
            and any(prefix in line for prefix in TENNIS_PREFIXES)
        ]
        conception_lines = [
            line for line in lines
            if ("CONCEPTION_STAMP" in line or "V4_PLACE" in line)
            and any(prefix in line for prefix in TENNIS_PREFIXES)
        ]
        entry_fill_lines = [
            line for line in lines
            if "ENTRY_FILLED" in line
            and any(prefix in line for prefix in TENNIS_PREFIXES)
        ]
        exit_activity_lines = [
            line for line in lines
            if any(label in line for label in (
                "V4_EXIT_POSTED", "RECONCILE_EXIT", "EXIT_FILLED",
                "EXIT_RECEIPTS_BOOKED",
            ))
        ]
        preserved_exit_ids = {
            o["order_id"] for o in pre["resting_orders"]
            if o["classification"] == "tennis_exit_sell"
        }
        final_exit_ids = {
            o["order_id"] for o in final["resting_orders"]
            if o["classification"] == "tennis_exit_sell"
        }
        result = {
            "schema_version": "schedule-liar-operational-containment-v1",
            "mode": MODE,
            "halt_control": {
                "status": "UNAVAILABLE",
                "scope": "none",
                "reason": (
                    "the only running-engine control is audit-derived "
                    "_conception_halt, which self-clears on an unrelated passing "
                    "halted_reaudit; no documented persistent sport/global operator "
                    "pause exists"
                ),
                "activation_attempted": False,
                "engine_or_config_modified": False,
            },
            "pre_snapshot": pre,
            "immediate_post_snapshot": immediate_post,
            "final_snapshot": final,
            "cancellation_ledger": cancellation_ledger,
            "observation": {
                "start_utc": observation_start_utc,
                "end_utc": observation_end_utc,
                "duration_seconds": round(
                    observation_end_epoch - observation_start_epoch, 3
                ),
                "poll_interval_seconds": INTERVAL,
                "samples": samples,
                "reconcile_cycle_receipts": reconcile_lines,
                "reconcile_cycle_count": len(reconcile_lines),
                "tennis_entry_order_receipts": entry_order_lines,
                "tennis_conception_receipts": conception_lines,
                "tennis_entry_fill_receipts": entry_fill_lines,
                "exit_management_receipts": exit_activity_lines,
                "new_entry_cancellations": reappeared,
                "log_slice_sha256": hashlib.sha256(
                    log_slice.encode("utf-8")
                ).hexdigest(),
            },
            "conservation": {
                "pre_held_positions": pre["exchange_positions"],
                "final_held_positions": final["exchange_positions"],
                "pre_engine_booked_quantities": pre["engine_booked_quantities"],
                "final_engine_booked_quantities": final["engine_booked_quantities"],
                "pre_tennis_exit_order_ids": sorted(preserved_exit_ids),
                "final_tennis_exit_order_ids": sorted(final_exit_ids),
                "exit_ids_no_longer_resting": sorted(
                    preserved_exit_ids - final_exit_ids
                ),
                "new_exit_ids": sorted(final_exit_ids - preserved_exit_ids),
            },
            "status": "BLOCKED",
            "status_reason": (
                "HALT CONTROL UNAVAILABLE; cancellation-only fallback cannot "
                "guarantee durable suppression and any new entry keeps status FAIL"
            ),
            "remote_files_written": 0,
            "service_restarts": 0,
            "order_posts_by_tool": 0,
            "position_mutations_by_tool": 0,
        }
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))


asyncio.run(main())
'''


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) +
            "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="root@104.131.191.95")
    parser.add_argument("--mode", choices=("snapshot", "contain"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--duration-seconds", type=int, default=300)
    parser.add_argument("--interval-seconds", type=int, default=15)
    parser.add_argument("--incident-line", type=int, default=2783981)
    args = parser.parse_args()

    command = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
        args.host,
        "cd /root/Omi-Workspace/arb-executor && python3 - %s %d %d %d" % (
            args.mode, args.duration_seconds, args.interval_seconds,
            args.incident_line,
        ),
    ]
    proc = subprocess.run(
        command, input=REMOTE_PROGRAM, text=True, capture_output=True
    )
    if proc.returncode:
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print("remote output was not canonical JSON: %s" % exc, file=sys.stderr)
        print(proc.stdout[-2000:], file=sys.stderr)
        return 2

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(data)
    output.write_bytes(payload)
    print(json.dumps({
        "mode": args.mode,
        "output": str(output),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "remote_exchange_mutations": (
            len(data.get("cancellation_ledger", []))
            if args.mode == "contain" else 0
        ),
        "service_restarts": data.get("service_restarts", 0),
        "status": data.get("status", "SNAPSHOT_ONLY"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
