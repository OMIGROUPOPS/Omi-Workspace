#!/usr/bin/env python3
"""Read-only final-status verification for containment cancellation receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


REMOTE_TEMPLATE = r'''
import asyncio
import json
import os
from pathlib import Path
import sys

ROOT = Path("/root/Omi-Workspace")
EXEC = ROOT / "arb-executor"
sys.path.insert(0, str(EXEC))
os.chdir(EXEC)
import aiohttp
import live_v4 as live

ORDER_IDS = json.loads(%s)


async def main():
    ak, pk = live.load_credentials()
    if not ak:
        raise RuntimeError("KALSHI_API_KEY unavailable")
    rl = live.RateLimiter()
    out = []
    async with aiohttp.ClientSession() as session:
        for order_id in ORDER_IDS:
            path = "/trade-api/v2/portfolio/orders/" + order_id
            data = await live.api_get(session, ak, pk, path, rl)
            row = data.get("order", data) if isinstance(data, dict) else data
            out.append({
                "order_id": order_id,
                "status": row.get("status") if isinstance(row, dict) else None,
                "ticker": row.get("ticker") if isinstance(row, dict) else None,
                "action": row.get("action") if isinstance(row, dict) else None,
                "remaining_count_fp": (
                    row.get("remaining_count_fp")
                    if isinstance(row, dict) else None
                ),
                "fill_count_fp": (
                    row.get("fill_count_fp") if isinstance(row, dict) else None
                ),
                "raw_exchange_response": data,
            })
    print(json.dumps(out, sort_keys=True, separators=(",", ":")))


asyncio.run(main())
'''


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="root@104.131.191.95")
    parser.add_argument("--receipt", action="append", default=[])
    parser.add_argument("--order-id", action="append", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    order_ids: list[str] = []
    source_receipts = []
    for name in args.receipt:
        path = Path(name).resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("cancellation_ledger", [])
        source_receipts.append({
            "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "rows": len(rows),
        })
        order_ids.extend(str(row["order_id"]) for row in rows)
    order_ids.extend(args.order_id)
    if not order_ids:
        raise SystemExit("at least one receipt or order ID is required")
    if len(order_ids) != len(set(order_ids)):
        raise SystemExit("duplicate cancellation order identity across receipts")
    encoded = json.dumps(json.dumps(order_ids))
    remote = REMOTE_TEMPLATE % encoded
    command = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
        args.host,
        "cd /root/Omi-Workspace/arb-executor && python3 -",
    ]
    proc = subprocess.run(
        command, input=remote, text=True, capture_output=True
    )
    if proc.returncode:
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    rows = json.loads(proc.stdout)
    result = {
        "schema_version": "schedule-liar-final-order-status-v1",
        "read_only": True,
        "source_receipts": source_receipts,
        "queried_order_count": len(order_ids),
        "unique_order_count": len(set(order_ids)),
        "status_counts": {
            status: sum(row["status"] == status for row in rows)
            for status in sorted({row["status"] for row in rows})
        },
        "all_non_resting": all(row["status"] != "resting" for row in rows),
        "rows": rows,
        "exchange_mutations": 0,
        "service_restarts": 0,
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(result)
    output.write_bytes(payload)
    print(json.dumps({
        "output": str(output),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "queried_order_count": len(order_ids),
        "status_counts": result["status_counts"],
        "all_non_resting": result["all_non_resting"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
