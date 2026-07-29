#!/usr/bin/env python3
"""Create a consistent read-only-source SQLite snapshot for offline replay."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sqlite3


def run(source: Path, destination: Path) -> int:
    if destination.exists():
        raise SystemExit(f"destination already exists: {destination}")
    source_uri = f"file:{source.as_posix()}?mode=ro"
    source_connection = sqlite3.connect(source_uri, uri=True)
    destination_connection = sqlite3.connect(str(destination))
    try:
        source_connection.backup(
            destination_connection, pages=16384, sleep=0.02
        )
        destination_connection.commit()
        page_count = int(destination_connection.execute(
            "PRAGMA page_count"
        ).fetchone()[0])
        page_size = int(destination_connection.execute(
            "PRAGMA page_size"
        ).fetchone()[0])
    finally:
        destination_connection.close()
        source_connection.close()
    print(f"snapshot={destination}")
    print(f"bytes={os.path.getsize(destination)}")
    print(f"page_count={page_count}")
    print(f"page_size={page_size}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--source", type=Path, required=True)
    result.add_argument("--destination", type=Path, required=True)
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(run(arguments.source, arguments.destination))
