#!/usr/bin/env python3
"""Build and verify the immutable Round-2 development data diet.

The manifest contains sanitized receipts only.  Private event, tape, and
market-cache bytes remain outside Git.  Capability execution must call
``validate_bound_inputs`` before reading an event stream.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


VERSION = "window1-round2-data-binding-v1"
D_REQUIRED = 804
LEG_REQUIRED = 1608
DEV_DATES = [f"2026-07-{day:02d}" for day in range(12, 21)]
SEALED_DATES = [f"2026-07-{day:02d}" for day in range(24, 27)]
CACHE_VERSION = "window1-guarded-event-market-cache-v3"
CACHE_KEY = "b85371c8eb52996f66ac25d9b60f0b41f6fbbba4afe883b135962782ae491b0b"

START_LEDGER = (
    ".claude/window1_start_guard_corrected_20260724/"
    "REAL_START_LEDGER_V5.jsonl"
)
FEATURE_LEDGER = ".claude/window1_20260721/WINDOW1_FEATURE_MATRIX.jsonl"
LIFECYCLE_LEDGER = (
    ".claude/window1_20260721/EVENT_LEG_LIFECYCLE_LEDGER.jsonl"
)
REPOSITORY_INPUTS = {
    "start_boundary_ledger": START_LEDGER,
    "feature_availability_flags": FEATURE_LEDGER,
    "own_order_fingerprint_receipts": LIFECYCLE_LEDGER,
    "cohort_surface": ".claude/master_20260709/cohort.json",
    "shape_surface": "arb-executor/data/shape_corpus/manifest.json",
    "orientation_surface": ".claude/trendpath/ORIENT_V1.json",
    "drift_surface": ".claude/entrysurface_20260717/drift_surfaces_v1.json",
    "band_surface": ".claude/entrysurface_20260717/band_map_v1.json",
    "divot_surface": ".claude/entrysurface_20260717/divot_tables_v1.json",
    "recut_surface": ".claude/seqfloor_20260708/recut_cells.json",
    "source_classification_receipt": (
        ".claude/window1_20260721/SOURCE_COVERAGE_SUMMARY.json"
    ),
}


class BindingError(RuntimeError):
    """Raised when a bound development input is absent or changed."""


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BindingError(f"JSON object required: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise BindingError(
                    f"JSON object required: {path}:{line_number}"
                )
            rows.append(value)
    return rows


def git_blob_oid(repo: Path, relative: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:{relative}"],
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise BindingError(f"repository input is not committed: {relative}")
    return result.stdout.strip()


def repository_receipt(
    repo: Path,
    logical_name: str,
    relative: str,
    *,
    causal_timestamp_field: str,
    status: str = "available",
    counts: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    path = repo / relative
    if not path.is_file():
        raise BindingError(f"repository input missing: {relative}")
    return {
        "logical_name": logical_name,
        "locator": relative,
        "source": "committed_git_blob",
        "git_blob_oid": git_blob_oid(repo, relative),
        "content_sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "counts": dict(counts or {}),
        "date_range": [DEV_DATES[0], DEV_DATES[-1]],
        "causal_timestamp_field": causal_timestamp_field,
        "availability": status,
        "holdout_dates_present": 0,
    }


def _finite_positive(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number > 0


def _date_census(rows: Iterable[Mapping[str, Any]]) -> Counter[str]:
    return Counter(str(row.get("event_date") or "") for row in rows)


def _surface_counts(repo: Path) -> dict[str, dict[str, int]]:
    cohort = read_json(repo / REPOSITORY_INPUTS["cohort_surface"])
    shape = json.loads((
        repo / REPOSITORY_INPUTS["shape_surface"]
    ).read_text(encoding="utf-8"))
    orientation = read_json(
        repo / REPOSITORY_INPUTS["orientation_surface"]
    )
    drift = read_json(repo / REPOSITORY_INPUTS["drift_surface"])
    band = read_json(repo / REPOSITORY_INPUTS["band_surface"])
    divot = read_json(repo / REPOSITORY_INPUTS["divot_surface"])
    recut = read_json(repo / REPOSITORY_INPUTS["recut_surface"])
    return {
        "cohort_surface": {
            "rows": len(cohort.get("rows") or []),
            "events": 0,
            "tickers": 0,
        },
        "shape_surface": {
            "rows": (
                len(shape)
                if isinstance(shape, list)
                else len(
                    shape.get("files")
                    or shape.get("artifacts")
                    or []
                )
            ),
            "events": 0,
            "tickers": 0,
        },
        "orientation_surface": {
            "rows": sum(
                len(cells)
                for cells in (orientation.get("cats") or {}).values()
            ),
            "events": 0,
            "tickers": 0,
        },
        "drift_surface": {
            "rows": sum(
                len(cells)
                for cells in (drift.get("recognition") or {}).values()
            ),
            "events": 0,
            "tickers": 0,
        },
        "band_surface": {
            "rows": sum(
                len(row.get("bands") or [])
                for row in (band.get("cats") or {}).values()
            ),
            "events": 0,
            "tickers": 0,
        },
        "divot_surface": {
            "rows": len(divot.get("bands") or {}),
            "events": 0,
            "tickers": 0,
        },
        "recut_surface": {
            "rows": sum(
                len(cells) for cells in recut.values()
                if isinstance(cells, Mapping)
            ),
            "events": 0,
            "tickers": 0,
        },
        "source_classification_receipt": {
            "rows": 1,
            "events": D_REQUIRED,
            "tickers": LEG_REQUIRED,
        },
    }


def inspect_market_cache(
    cache_root: Path,
    events: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    files = sorted(cache_root.glob("*.json.gz"), key=lambda item: item.name)
    if len(files) != D_REQUIRED:
        raise BindingError(f"market cache file count changed: {len(files)}")
    expected_names = {f"{event_id}.json.gz" for event_id in events}
    if {item.name for item in files} != expected_names:
        raise BindingError("market cache identity set differs from D=804")

    event_receipts = []
    ticker_count = print_count = snapshot_count = 0
    positive_print_count = excluded_print_count = 0
    bbo_tickers = top5_tickers = 0
    first_ts: float | None = None
    last_ts: float | None = None
    source_classes: Counter[str] = Counter()
    for item in files:
        event_id = item.name[:-8]
        with gzip.open(item, "rt", encoding="utf-8") as handle:
            payload = json.load(handle)
        if (
            payload.get("event_id") != event_id
            or payload.get("cache_version") != CACHE_VERSION
            or payload.get("cache_key") != CACHE_KEY
            or len(payload.get("legs") or []) != 2
        ):
            raise BindingError(f"market cache envelope invalid: {event_id}")
        expected_tickers = {
            str(row["ticker"]) for row in events[event_id]["legs"]
        }
        actual_tickers = {
            str(row.get("ticker") or "") for row in payload["legs"]
        }
        if actual_tickers != expected_tickers:
            raise BindingError(f"market cache tickers differ: {event_id}")
        event_prints = event_snapshots = 0
        for leg in payload["legs"]:
            ticker_count += 1
            seen: set[str] = set()
            prior = -math.inf
            prints = list(leg.get("prints") or [])
            snapshots = list(leg.get("snapshots") or [])
            event_prints += len(prints)
            event_snapshots += len(snapshots)
            print_count += len(prints)
            snapshot_count += len(snapshots)
            for row in prints:
                identity = str(row.get("trade_id") or "")
                timestamp = float(row["ts"])
                if not identity or identity in seen or timestamp < prior:
                    raise BindingError(
                        f"print identity/order invalid: {event_id}"
                    )
                seen.add(identity)
                prior = timestamp
                first_ts = timestamp if first_ts is None else min(
                    first_ts, timestamp
                )
                last_ts = timestamp if last_ts is None else max(
                    last_ts, timestamp
                )
                if _finite_positive(row.get("size")):
                    positive_print_count += 1
                else:
                    excluded_print_count += 1
            prior = -math.inf
            if snapshots:
                bbo_tickers += 1
            if any(
                len(row.get("bids") or []) >= 5
                and len(row.get("asks") or []) >= 5
                for row in snapshots
            ):
                top5_tickers += 1
            for row in snapshots:
                timestamp = float(row["ts"])
                if timestamp < prior:
                    raise BindingError(
                        f"snapshot order invalid: {event_id}"
                    )
                prior = timestamp
                source_classes[str(row.get("source") or "unknown")] += 1
                first_ts = timestamp if first_ts is None else min(
                    first_ts, timestamp
                )
                last_ts = timestamp if last_ts is None else max(
                    last_ts, timestamp
                )
        event_receipts.append({
            "event_id": event_id,
            "event_date": events[event_id]["event_date"],
            "file": item.name,
            "bytes": item.stat().st_size,
            "sha256": sha256_file(item),
            "ticker_count": 2,
            "positive_print_rows": event_prints,
            "book_snapshot_rows": event_snapshots,
        })
    file_set = [{
        "name": row["file"],
        "bytes": row["bytes"],
        "sha256": row["sha256"],
    } for row in event_receipts]
    return {
        "cache_version": CACHE_VERSION,
        "cache_key": CACHE_KEY,
        "files": len(files),
        "bytes": sum(item.stat().st_size for item in files),
        "hash_set_sha256": hashlib.sha256(
            compact(file_set).encode()
        ).hexdigest(),
        "event_count": len(event_receipts),
        "ticker_count": ticker_count,
        "print_rows": print_count,
        "positive_size_print_rows": positive_print_count,
        "excluded_nonpositive_or_malformed_print_rows": (
            excluded_print_count
        ),
        "book_snapshot_rows": snapshot_count,
        "bbo_tickers": bbo_tickers,
        "top5_tickers": top5_tickers,
        "first_causal_ts": first_ts,
        "last_causal_ts": last_ts,
        "book_source_classes": dict(sorted(source_classes.items())),
        "events": event_receipts,
    }


def build_manifest(
    repo: Path,
    *,
    events_path: Path,
    prints_path: Path,
    tape_manifest_path: Path,
    cache_root: Path,
) -> dict[str, Any]:
    surface_counts = _surface_counts(repo)
    events_rows = read_jsonl(events_path)
    events = {str(row["event_id"]): row for row in events_rows}
    dates = _date_census(events_rows)
    if (
        len(events_rows) != D_REQUIRED
        or len(events) != D_REQUIRED
        or sorted(dates) != DEV_DATES
        or any(date in dates for date in SEALED_DATES)
    ):
        raise BindingError("development event/date fence changed")
    tickers = {
        str(leg["ticker"])
        for event in events_rows for leg in event.get("legs") or []
    }
    if len(tickers) != LEG_REQUIRED:
        raise BindingError("1,608-leg identity contract changed")
    if any(len(event.get("legs") or []) != 2 for event in events_rows):
        raise BindingError("event pair law changed")

    starts = read_jsonl(repo / START_LEDGER)
    if {str(row["event_id"]) for row in starts} != set(events):
        raise BindingError("start ledger identity set changed")
    start_classes = Counter(
        str(row.get("start_source_class") or "") for row in starts
    )
    censor_reasons = Counter(
        str(row.get("guard_censor_reason") or "none") for row in starts
    )
    features_all = read_jsonl(repo / FEATURE_LEDGER)
    features = [
        row for row in features_all
        if int(row.get("boundary_hours_before_schedule") or -1) == 8
    ]
    feature_keys = {
        (str(row["event_id"]), str(row["ticker"])) for row in features
    }
    if (
        len(features) != LEG_REQUIRED
        or feature_keys != {
            (str(event["event_id"]), str(leg["ticker"]))
            for event in events_rows for leg in event["legs"]
        }
    ):
        raise BindingError("T-8 feature identity set changed")
    feature_counts = {
        "rows": len(features),
        "events": D_REQUIRED,
        "tickers": LEG_REQUIRED,
        "rows_all_boundaries": len(features_all),
        "rows_T8": len(features),
        "top5_available": sum(bool(row.get("top5_available")) for row in features),
        "own_volume_attributable": sum(
            bool(row.get("own_historical_order_volume_attributable"))
            for row in features
        ),
        "pinnacle_available": sum(
            bool(row.get("pinnacle_available")) for row in features
        ),
        "full_depth_sequence_valid": sum(
            bool(row.get("full_depth_sequence_valid")) for row in features
        ),
    }
    lifecycle = read_jsonl(repo / LIFECYCLE_LEDGER)
    if len(lifecycle) != LEG_REQUIRED:
        raise BindingError("own-order lifecycle leg count changed")

    tape_manifest = read_json(tape_manifest_path)
    tape_artifact = (
        tape_manifest.get("artifacts", {})
        .get("normalized_true_prints", {})
    )
    prints_sha256 = sha256_file(prints_path)
    if (
        prints_path.stat().st_size != int(tape_artifact.get("bytes") or -1)
        or prints_sha256 != tape_artifact.get("sha256")
    ):
        raise BindingError("normalized public print archive changed")
    if (
        tape_manifest.get("immutable_denominator", {}).get("D") != D_REQUIRED
        or tape_manifest.get("immutable_denominator", {}).get(
            "required_leg_tickers"
        ) != LEG_REQUIRED
        or tape_manifest.get("records", {}).get(
            "zero_size_rows_retained_as_zero"
        ) != 0
    ):
        raise BindingError("public tape contract changed")

    cache = inspect_market_cache(cache_root, events)
    if cache["excluded_nonpositive_or_malformed_print_rows"] != 0:
        raise BindingError("bound market cache contains invalid print sizes")

    repo_receipts = {
        name: repository_receipt(
            repo,
            name,
            relative,
            causal_timestamp_field=(
                "causal_post_utc"
                if name == "feature_availability_flags"
                else "exchange/order receipt timestamps"
                if name == "own_order_fingerprint_receipts"
                else "evaluation evidence timestamps; policy inaccessible"
                if name == "start_boundary_ledger"
                else "surface_fit_receipt"
            ),
            status=(
                "unavailable_for_round2_policy"
                if name == "shape_surface"
                else "available"
            ),
            counts=(
                feature_counts
                if name == "feature_availability_flags"
                else {
                    "rows": len(starts),
                    "events": len(starts),
                    "tickers": LEG_REQUIRED,
                    "source_classes": dict(sorted(start_classes.items())),
                    "censoring_reasons": dict(sorted(censor_reasons.items())),
                }
                if name == "start_boundary_ledger"
                else {
                    "rows": len(lifecycle),
                    "events": D_REQUIRED,
                    "tickers": LEG_REQUIRED,
                }
                if name == "own_order_fingerprint_receipts"
                else surface_counts[name]
            ),
        )
        for name, relative in REPOSITORY_INPUTS.items()
    }
    external = {
        "immutable_event_ledger": {
            "logical_name": "immutable_event_ledger",
            "locator": "$WINDOW1_PRIVATE_ROOT/joined/events.jsonl",
            "runtime_argument": "--events",
            "source": "private_normalized_export",
            "content_sha256": sha256_file(events_path),
            "bytes": events_path.stat().st_size,
            "counts": {
                "rows": len(events_rows),
                "events": len(events),
                "tickers": len(tickers),
                "dates": dict(sorted(dates.items())),
            },
            "date_range": [DEV_DATES[0], DEV_DATES[-1]],
            "causal_timestamp_field": (
                "schedule_observed_exchange_ts and "
                "scheduled_start_exchange_ts"
            ),
            "availability": "available",
            "holdout_dates_present": 0,
        },
        "public_print_archive": {
            "logical_name": "public_print_archive",
            "locator": "$WINDOW1_PRIVATE_ROOT/fit-local/prints.jsonl",
            "runtime_argument": "--prints",
            "source": "public Kalshi GET trade export; no POST/DELETE",
            "content_sha256": prints_sha256,
            "bytes": prints_path.stat().st_size,
            "counts": {
                "rows": tape_manifest["records"]["canonical_true_print_rows"],
                "events": D_REQUIRED,
                "tickers": LEG_REQUIRED,
                "zero_size_rows": 0,
            },
            "date_range": [DEV_DATES[0], DEV_DATES[-1]],
            "causal_timestamp_field": "exchange created_time",
            "availability": "available",
            "holdout_dates_present": 0,
        },
        "public_tape_manifest": {
            "logical_name": "public_tape_manifest",
            "locator": (
                "$WINDOW1_PRIVATE_ROOT/fit-local/"
                "PUBLIC_TAPE_MANIFEST.sanitized.json"
            ),
            "runtime_argument": "--tape-manifest",
            "source": "sanitized public tape receipt",
            "content_sha256": sha256_file(tape_manifest_path),
            "bytes": tape_manifest_path.stat().st_size,
            "counts": {
                "rows": 1,
                "events": D_REQUIRED,
                "tickers": LEG_REQUIRED,
            },
            "date_range": [DEV_DATES[0], DEV_DATES[-1]],
            "causal_timestamp_field": "exchange created_time",
            "availability": "available",
            "holdout_dates_present": 0,
        },
        "per_leg_market_streams": {
            "logical_name": "per_leg_market_streams",
            "locator": "$WINDOW1_PRIVATE_ROOT/fit-local/guarded-cache-v3",
            "runtime_argument": "--market-cache",
            "source": (
                "receipt-identified positive-size public trades plus "
                "premarket_ticks_top5 causal snapshots"
            ),
            "content_sha256": cache["hash_set_sha256"],
            "bytes": cache["bytes"],
            "counts": {
                "rows": (
                    cache["print_rows"] + cache["book_snapshot_rows"]
                ),
                "events": cache["event_count"],
                "tickers": cache["ticker_count"],
                **{
                    key: cache[key]
                    for key in (
                        "files", "event_count", "ticker_count",
                        "print_rows", "positive_size_print_rows",
                        "book_snapshot_rows", "bbo_tickers",
                        "top5_tickers",
                        "excluded_nonpositive_or_malformed_print_rows",
                    )
                },
            },
            "date_range": [DEV_DATES[0], DEV_DATES[-1]],
            "causal_timestamp_field": "print.ts and snapshot.ts",
            "availability": "available",
            "holdout_dates_present": 0,
            "cache_version": cache["cache_version"],
            "cache_key": cache["cache_key"],
            "event_file_receipts": cache["events"],
            "book_source_classes": cache["book_source_classes"],
        },
    }
    external["reference_and_window1_close_inputs"] = {
        "logical_name": "reference_and_window1_close_inputs",
        "locator": (
            "$WINDOW1_PRIVATE_ROOT/fit-local/guarded-cache-v3/*.json.gz"
        ),
        "runtime_argument": "--market-cache",
        "source": (
            "last receipt-identified positive-size public true print "
            "judged only by the separate evaluation clock"
        ),
        "content_sha256": cache["hash_set_sha256"],
        "bytes": cache["bytes"],
        "counts": {
            "rows": cache["positive_size_print_rows"],
            "events": cache["event_count"],
            "tickers": cache["ticker_count"],
        },
        "date_range": [DEV_DATES[0], DEV_DATES[-1]],
        "causal_timestamp_field": "print.ts",
        "availability": "bound_evaluation_only_not_scored",
        "holdout_dates_present": 0,
    }
    binding_hashes = {
        name: row["content_sha256"]
        for name, row in {**repo_receipts, **external}.items()
    }
    return {
        "schema_version": VERSION,
        "D": D_REQUIRED,
        "leg_identities": LEG_REQUIRED,
        "development_dates": DEV_DATES,
        "sealed_holdout_dates": SEALED_DATES,
        "holdout_dates_present_in_any_input": 0,
        "policy_input_partition": {
            "policy_clock_inputs": [
                "schedule_observed_exchange_ts",
                "scheduled_start_exchange_ts",
                "declared_policy_corridor",
            ],
            "evaluation_only_inputs": [
                "verified/proxy/interval actual-start evidence",
                "Window-1-close public print reference",
            ],
            "candidate_code_receives_evaluation_inputs": False,
        },
        "input_records": {**repo_receipts, **external},
        "reference_and_window1_close_binding": {
            "start_boundary_receipt": binding_hashes[
                "start_boundary_ledger"
            ],
            "true_print_stream_receipt": binding_hashes[
                "reference_and_window1_close_inputs"
            ],
            "availability": "bound_for_future_evaluation_not_scored",
        },
        "source_classifications_and_censoring": {
            "source_classes": dict(sorted(start_classes.items())),
            "censoring_reasons": dict(sorted(censor_reasons.items())),
            "receipt": binding_hashes["start_boundary_ledger"],
        },
        "unavailable": {
            "pinnacle": feature_counts["pinnacle_available"] == 0,
            "full_depth": feature_counts["full_depth_sequence_valid"] == 0,
            "shape_policy_mapping": (
                "shape corpus is bound but no independent non-AIM causal "
                "Round-2 mapping exists"
            ),
        },
        "binding_bundle_sha256": hashlib.sha256(
            compact(binding_hashes).encode()
        ).hexdigest(),
        "candidate_scoring_performed": False,
        "tuning_performed": False,
        "ablation_scoring_performed": False,
        "holdout_opened": False,
        "holdout_queried": False,
    }


def validate_bound_inputs(
    repo: Path,
    manifest_path: Path,
    *,
    events_path: Path,
    prints_path: Path,
    tape_manifest_path: Path,
    cache_root: Path,
) -> dict[str, Any]:
    frozen = read_json(manifest_path)
    if (
        frozen.get("schema_version") != VERSION
        or frozen.get("D") != D_REQUIRED
        or frozen.get("leg_identities") != LEG_REQUIRED
        or frozen.get("development_dates") != DEV_DATES
        or frozen.get("holdout_dates_present_in_any_input") != 0
    ):
        raise BindingError("frozen data-binding envelope changed")
    records = frozen["input_records"]
    for name, relative in REPOSITORY_INPUTS.items():
        receipt = records.get(name) or {}
        path = repo / relative
        if (
            not path.is_file()
            or sha256_file(path) != receipt.get("content_sha256")
            or git_blob_oid(repo, relative) != receipt.get("git_blob_oid")
        ):
            raise BindingError(f"bound repository input changed: {name}")
    external_paths = {
        "immutable_event_ledger": events_path,
        "public_print_archive": prints_path,
        "public_tape_manifest": tape_manifest_path,
    }
    for name, path in external_paths.items():
        receipt = records.get(name) or {}
        if (
            not path.is_file()
            or path.stat().st_size != int(receipt.get("bytes") or -1)
            or sha256_file(path) != receipt.get("content_sha256")
        ):
            raise BindingError(f"bound external input changed: {name}")
    event_rows = read_jsonl(events_path)
    if (
        len(event_rows) != D_REQUIRED
        or len({
            str(leg["ticker"])
            for event in event_rows for leg in event["legs"]
        }) != LEG_REQUIRED
        or sorted(_date_census(event_rows)) != DEV_DATES
        or any(
            str(row["event_date"]) in SEALED_DATES for row in event_rows
        )
    ):
        raise BindingError("bound event population/date fence changed")
    cache_receipt = records["per_leg_market_streams"]
    expected_files = {
        str(row["file"]): row
        for row in cache_receipt["event_file_receipts"]
    }
    actual_files = {
        item.name: item
        for item in cache_root.glob("*.json.gz")
    }
    if set(actual_files) != set(expected_files):
        raise BindingError("bound market-cache file set changed")
    file_set = []
    for name in sorted(expected_files):
        item = actual_files[name]
        expected = expected_files[name]
        digest = sha256_file(item)
        if (
            item.stat().st_size != int(expected["bytes"])
            or digest != expected["sha256"]
        ):
            raise BindingError(f"bound market stream changed: {name}")
        file_set.append({
            "name": name,
            "bytes": item.stat().st_size,
            "sha256": digest,
        })
    current_set_hash = hashlib.sha256(
        compact(file_set).encode()
    ).hexdigest()
    if current_set_hash != cache_receipt["content_sha256"]:
        raise BindingError("bound market-cache bundle hash changed")
    return frozen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("build", "validate"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--prints", type=Path, required=True)
    parser.add_argument("--tape-manifest", type=Path, required=True)
    parser.add_argument("--market-cache", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    paths = {
        "events_path": args.events.resolve(),
        "prints_path": args.prints.resolve(),
        "tape_manifest_path": args.tape_manifest.resolve(),
        "cache_root": args.market_cache.resolve(),
    }
    if args.mode == "build":
        value = build_manifest(repo, **paths)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    else:
        value = validate_bound_inputs(
            repo, args.manifest.resolve(), **paths
        )
    print(compact({
        "schema_version": value["schema_version"],
        "D": value["D"],
        "leg_identities": value["leg_identities"],
        "binding_bundle_sha256": value["binding_bundle_sha256"],
        "holdout_queried": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
