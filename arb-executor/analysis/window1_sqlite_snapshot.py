#!/usr/bin/env python3
"""Create and receipt a consistent owner-only SQLite research snapshot."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import stat
from pathlib import Path


class SnapshotError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    manifest = Path(args.manifest).resolve()
    if output.exists() or manifest.exists():
        raise SnapshotError("refusing to overwrite an existing snapshot receipt")
    output.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(output.parent, stat.S_IRWXU)
    source_before = source.stat()
    source_connection = sqlite3.connect(
        "file:" + str(source) + "?mode=ro",
        uri=True,
        timeout=30,
    )
    destination = sqlite3.connect(str(output))
    try:
        progress_state = {"last": 0}

        def progress(_status: int, remaining: int, total: int) -> None:
            completed = total - remaining
            if (
                completed - progress_state["last"] >= 100_000
                or remaining == 0
            ):
                progress_state["last"] = completed
                print(json.dumps({
                    "pages_complete": completed,
                    "pages_total": total,
                    "pages_remaining": remaining,
                }), flush=True)

        source_connection.backup(
            destination,
            pages=args.pages_per_step,
            progress=progress,
            sleep=args.sleep_seconds,
        )
        quick_check = destination.execute(
            "PRAGMA quick_check"
        ).fetchone()[0]
    finally:
        destination.close()
        source_connection.close()
    if quick_check != "ok":
        raise SnapshotError(f"snapshot quick_check failed: {quick_check}")
    os.chmod(output, stat.S_IRUSR | stat.S_IWUSR)
    source_after = source.stat()
    receipt = {
        "schema_version": "window1-sqlite-snapshot-v1",
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_logical_name": source.name,
        "source_bytes_before": source_before.st_size,
        "source_bytes_after": source_after.st_size,
        "source_mtime_ns_before": source_before.st_mtime_ns,
        "source_mtime_ns_after": source_after.st_mtime_ns,
        "source_changed_during_backup": (
            source_before.st_size != source_after.st_size
            or source_before.st_mtime_ns != source_after.st_mtime_ns
        ),
        "snapshot_bytes": output.stat().st_size,
        "snapshot_sha256": sha256_file(output),
        "quick_check": quick_check,
        "mode": oct(output.stat().st_mode & 0o777),
        "method": "sqlite_online_backup_read_only_source",
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--source", required=True)
    result.add_argument("--output", required=True)
    result.add_argument("--manifest", required=True)
    result.add_argument("--pages-per-step", type=int, default=4096)
    result.add_argument("--sleep-seconds", type=float, default=0.01)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
