#!/usr/bin/env python3
"""Causal feature panel for the two tick-library tours; never imports an OS.

Raw captures and print witnesses stay outside Git. This module consumes the
hash-bound extractor's per-leg source records and writes derived column arrays.
No forecast, label, full-span cadence or post-receipt observation is a feature.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
import heapq
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import tune_bench_v2_survivorship as b

sys.dont_write_bytecode = True
TOURS = ("ATP_MAIN", "ATP_CHALL")
BLOCKS = ("SOURCE", "WAKE_CADENCE_SPREAD", "FLOW_LEVELS_DEPTH",
          "CLUSTERING_INTENSITY", "OPEN_INTEREST", "PARTNER_PAIR")


@dataclass(frozen=True)
class Field:
    name: str
    block: str | None
    source: str
    definition: str
    kind: str = "numeric"
    exclusion: str = "No observation after the receipt; missing is not zero."


FIELDS = (
    Field("formation_source", "SOURCE", "library + causal formation rule",
          "Formation rule observable by formation; categorical, not the eventual floor.", "categorical"),
    Field("bell_source", "SOURCE", "library + publication receipt",
          "Bell-source token only if its publication epoch is verified <= receipt.", "categorical",
          "Trade-density inference and undated historical machine receipts are retrospective; excluded from features."),
    Field("book_wake_mtb", "WAKE_CADENCE_SPREAD", "original observed book",
          "First source-observed positive non-crossed BBO with positive sizes on both sides, including causal preformation observations; observed wake, not an invented market onset."),
    Field("book_awake_minutes", "WAKE_CADENCE_SPREAD", "original observed book",
          "Elapsed receipt minutes since first observed two-sided book; a lower bound if capture began already awake."),
    Field("wake_left_censored", "WAKE_CADENCE_SPREAD", "original observed book",
          "First captured book was already two-sided: true earlier wake is unknown; observed age is only a lower bound."),
    Field("prefix_cadence_seconds", "WAKE_CADENCE_SPREAD", "accepted positive-size print witnesses",
          "Median of completed inter-print gaps since formation, observed by this receipt.",
          exclusion="Full-span library cadence_s is NEVER a predictor; fewer than two observed prints => missing."),
    Field("cadence_class", None, "earlier-category rank distribution",
          "Diagnostic rank interval using filed quantiles, learned only from earlier resolved games; no second vote for cadence.", "categorical"),
    Field("spread_cents", "WAKE_CADENCE_SPREAD", "native library BBO", "Current ask minus bid, cents; crossed books missing."),
    Field("spread_band", None, "cell_key_helpers.spread_band_name",
          "Filed Foundation label applied to current spread; diagnostic only, not a duplicated spread vote.", "categorical"),
    Field("bid_consumption_velocity", "FLOW_LEVELS_DEPTH", "completed minute native BBO closes",
          "Current completed-minute bid close minus previous completed-minute bid close; quote movement, NOT observed consumption."),
    Field("ask_consumption_velocity", "FLOW_LEVELS_DEPTH", "completed minute native BBO closes",
          "Current completed-minute ask close minus previous completed-minute ask close; quote movement, NOT observed consumption."),
    Field("taker_flow", "FLOW_LEVELS_DEPTH", "deduplicated accepted prints + original taker_side",
          "YES-aggressor contracts minus NO-aggressor contracts in latest completed minute; missing if any positive-size print is unattributed."),
    Field("taker_yes_contracts", "FLOW_LEVELS_DEPTH", "deduplicated accepted prints + original taker_side",
          "Sum of sizes with taker_side=yes in latest completed minute; not an event count."),
    Field("taker_no_contracts", "FLOW_LEVELS_DEPTH", "deduplicated accepted prints + original taker_side",
          "Sum of sizes with taker_side=no in latest completed minute; not an event count."),
    Field("distinct_levels_traded", "FLOW_LEVELS_DEPTH", "accepted positive-size prints",
          "Distinct traded prices in latest completed minute; not consumed resting levels."),
    Field("depth_ratio", "FLOW_LEVELS_DEPTH", "original five-level book capture",
          "Stored bid_depth_5 / (bid_depth_5 + ask_depth_5); latest observed snapshot, zero denominator missing."),
    Field("bid_depth_5", "FLOW_LEVELS_DEPTH", "original five-level book capture", "Latest observed sum of five bid sizes, contracts."),
    Field("ask_depth_5", "FLOW_LEVELS_DEPTH", "original five-level book capture", "Latest observed sum of five ask sizes, contracts."),
    Field("pressure_x_bid_response", "FLOW_LEVELS_DEPTH", "completed-minute flow and BBO",
          "Signed taker flow times that completed minute's bid-close change; learned interaction, not a trading rule."),
    Field("sell_pressure_x_replenishment", "FLOW_LEVELS_DEPTH", "completed-minute flow and five-level book",
          "NO-aggressor contracts times bid-depth change between the same consecutive completed-minute closes; no replenishment claim from quote prices alone."),
    Field("trade_clustering", "CLUSTERING_INTENSITY", "accepted positive-size prints",
          "Population standard deviation of within-minute inter-trade gaps, at minute close; undefined with fewer than three trades."),
    Field("positive_minutes_so_far", "CLUSTERING_INTENSITY", "accepted positive-size prints",
          "Number of completed in-span minutes with positive volume, causal count underlying the filed intensity class."),
    Field("causal_volume_intensity", "CLUSTERING_INTENSITY", "accepted positive-size prints",
          "Share of completed in-span minute buckets with positive volume; full-lifetime intensity excluded."),
    Field("open_interest", "OPEN_INTEREST", "Foundation overlap or original observed OI",
          "Latest observed OI available by receipt, never backfilled from later observations."),
    Field("open_interest_delta", "OPEN_INTEREST", "Foundation overlap or original observed OI",
          "Change between consecutive observed completed-minute OI values; unavailable if either value missing."),
    Field("partner_bid", "PARTNER_PAIR", "same-receipt partner BBO", "Other leg's causally carried bid."),
    Field("partner_ask", "PARTNER_PAIR", "same-receipt partner BBO", "Other leg's causally carried ask."),
    Field("paired_bid_sum", "PARTNER_PAIR", "same-receipt pair BBO", "Sum of both bids, cents."),
    Field("paired_ask_sum", "PARTNER_PAIR", "same-receipt pair BBO", "Sum of both asks, cents."),
    Field("paired_arb_gap_maker", "PARTNER_PAIR", "same-receipt pair BBO", "Filed par minus both bids, cents."),
    Field("paired_arb_gap_taker", "PARTNER_PAIR", "same-receipt pair BBO", "Both asks minus filed par, cents."),
    Field("pair_gap_abs", "PARTNER_PAIR", "same-receipt pair BBO", "Absolute deviation of paired midpoint sum from filed par, cents; NOT last-price sum."),
    Field("ws_depth_available", None, "snapshot-seeded gap-free WS depth epochs",
          "Availability only in v1; UNKNOWN without verified sequence coverage, not inferred from date or bucket presence."),
    Field("odds_available", None, "exact-event archived fv_history timestamps",
          "An exact-key in-span snapshot has been observed by receipt; undated rows and unjoinable backup excluded."),
)
FIELD_NAMES = tuple(f.name for f in FIELDS)
MODEL_FIELDS = tuple(f.name for f in FIELDS if f.block is not None)
FEATURE_INDEX = {name: i for i, name in enumerate(MODEL_FIELDS)}
CATEGORICAL = tuple(f.name for f in FIELDS if f.block and f.kind == "categorical")
_CELL_HELPERS = None


def filed_spread_bands(bids, asks, par):
    """Use the existing probability-unit Foundation classifier verbatim."""
    global _CELL_HELPERS
    if _CELL_HELPERS is None:
        path = Path(__file__).resolve().parents[1]/"data/scripts/cell_key_helpers.py"
        spec = importlib.util.spec_from_file_location("feature_panel_filed_cells", path)
        _CELL_HELPERS = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_CELL_HELPERS)
    labels = tuple(row[0] for row in _CELL_HELPERS.SPREAD_BANDS)
    codes = {name: i for i, name in enumerate(labels)}
    result = np.full(len(bids), np.nan)
    for i, (bid, ask) in enumerate(zip(bids, asks)):
        if np.isfinite(bid) and np.isfinite(ask):
            name = _CELL_HELPERS.spread_band_name(bid/par, ask/par)
            if name in codes:
                result[i] = codes[name]
    return result, labels


def iter_jsonl(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, payload):
    Path(path).write_text(json.dumps(b.clean(payload), indent=2, sort_keys=True,
                                    allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def asof(source_epoch, source_values, epochs):
    source_epoch = np.asarray(source_epoch, dtype=float)
    source_values = np.asarray(source_values, dtype=float)
    epochs = np.asarray(epochs, dtype=float)
    shape = (len(epochs),) + source_values.shape[1:]
    result = np.full(shape, np.nan)
    if not len(source_epoch):
        return result
    if np.any(np.diff(source_epoch) < 0):
        raise ValueError("UNORDERED_SOURCE")
    ix = np.searchsorted(source_epoch, epochs, side="right") - 1
    valid = ix >= 0
    result[valid] = source_values[ix[valid]]
    return result


def source_column(rows, name, epochs, clock="available_epoch"):
    if isinstance(rows, dict) and "__epochs__" in rows:
        values = rows["__columns__"].get(name)
        if values is None:
            return np.full(len(epochs), np.nan)
        return asof(rows["__epochs__"], values, epochs)
    usable = [r for r in rows if r.get(clock) is not None]
    return asof([r[clock] for r in usable], [r.get(name, np.nan) for r in usable], epochs)


def compact_rows(rows, fields):
    ordered = sorted((r for r in rows if r.get("available_epoch") is not None), key=lambda r:r["available_epoch"])
    return {"__epochs__": np.asarray([r["available_epoch"] for r in ordered], dtype=float),
            "__columns__": {field: np.asarray([r.get(field, np.nan) for r in ordered], dtype=float) for field in fields}}


def prepare_sources(sources, witnesses, minute_seconds=None):
    """Keep only derived numeric columns resident, not millions of raw dicts."""
    for source in sources.values():
        if not isinstance(source.get("minute_features"), dict):
            if "oi" in source:
                # Supplemental column order is explicit in the hashed extract.
                names = source.get("oi_columns", [])
                parsed = [dict(zip(names, row)) for row in source["oi"]]
                source["open_interest"] = [dict(
                    available_epoch=row.get("minute_ts", row.get("available_epoch", row.get("epoch"))),
                    open_interest=row.get("open_interest_ffill") if row.get("open_interest_ffill") is not None else row.get("open_interest_at_minute_end"),
                    open_interest_delta=row.get("open_interest_delta_from_prior_minute")) for row in parsed]
            if "odds_poll_epochs" in source:
                source["odds_snapshot_epochs"] = (None if source.get("odds_status") == "NOT_EXTRACTED"
                                                  else source["odds_poll_epochs"])
            # Recorder .5 on an empty book is a sentinel, not measured balance.
            for book in source.get("books", []):
                bid, ask = book.get("bid_depth_5"), book.get("ask_depth_5")
                valid = (bid is not None and ask is not None and np.isfinite(bid) and np.isfinite(ask)
                         and bid >= 0 and ask >= 0 and bid+ask > 0)
                book["depth_ratio"] = bid/(bid+ask) if valid else None
            source["minute_features"] = compact_rows(source.get("minute_features", []),
                ("taker_flow_contracts", "taker_yes_contracts", "taker_no_contracts",
                 "distinct_print_prices", "intertrade_gap_std_seconds"))
            source["books"] = compact_rows(source.get("books", []), ("bid_depth_5", "ask_depth_5", "depth_ratio"))
            source["open_interest"] = compact_rows(source.get("open_interest", []), ("open_interest", "open_interest_delta"))
        for key in ("book_observation_epochs", "odds_snapshot_epochs"):
            if source.get(key) is not None and not isinstance(source[key], np.ndarray):
                source[key] = np.asarray(source[key], dtype=float)
    for tape in witnesses.values():
        if "_prefix" not in tape:
            if "prints" not in tape:
                if tape.get("positive_prints") is None:
                    raise ValueError("MISSING_POSITIVE_PRINT_WITNESS_PAYLOAD:"+str(tape.get("ticker")))
                tape["prints"] = tape["positive_prints"]
            if tape["prints"] is None:
                raise ValueError("NULL_POSITIVE_PRINT_WITNESS_PAYLOAD:"+str(tape.get("ticker")))
            tape["_prefix"] = prepare_print_prefix(tape["prints"], tape["formation_end_epoch"])
        if minute_seconds is not None:
            positive_minute_endpoints(tape["_prefix"], minute_seconds)


def prepare_print_prefix(prints, formation):
    positive = sorted((r for r in prints if r[2] > 0 and r[0] >= formation),
                      key=lambda row: (row[0], row[3] if len(row) > 3 else 0))
    ts = np.asarray([r[0] for r in positive], dtype=float)
    medians = np.full(len(ts), np.nan)
    lower, upper = [], []
    for i, gap in enumerate(np.diff(ts), start=1):
        if not lower or gap <= -lower[0]:
            heapq.heappush(lower, -gap)
        else:
            heapq.heappush(upper, gap)
        if len(lower) > len(upper)+1:
            heapq.heappush(upper, -heapq.heappop(lower))
        elif len(upper) > len(lower):
            heapq.heappush(lower, -heapq.heappop(upper))
        medians[i] = -lower[0] if len(lower) > len(upper) else (upper[0]-lower[0])/2
    return {"epochs": ts, "medians": medians}


def positive_minute_endpoints(prepared, seconds):
    """Cache the exact immutable witness-minute index for the caller's clock."""
    cached = prepared.setdefault("positive_minute_endpoints_by_seconds", {})
    if seconds not in cached:
        ts = prepared["epochs"]
        cached[seconds] = np.unique((np.floor(ts/seconds)+1)*seconds) if len(ts) else np.array([])
    return cached[seconds]


def completed_closes(leg, epochs, seconds):
    """Half-open minute [end-seconds,end): a boundary tick is NOT the old close."""
    close = np.floor(np.asarray(epochs)/seconds)*seconds
    now = np.searchsorted(leg.epoch, close, side="left") - 1
    before = np.searchsorted(leg.epoch, close-seconds, side="left") - 1
    valid = (before >= 0) & (now >= 0) & (close-seconds >= leg.formation)
    delta = np.full((len(close), leg.values.shape[1]), np.nan)
    delta[valid] = leg.values[now[valid]] - leg.values[before[valid]]
    return delta


def prefix_print_features(prints, epochs, formation, seconds, prepared=None):
    """Raw witnesses are inputs only; output contains derived prefix statistics."""
    prepared = prepared if prepared is not None else prepare_print_prefix(prints, formation)
    ts = prepared["epochs"]
    cadence = asof(ts, prepared["medians"], epochs)
    ends = np.floor(np.asarray(epochs)/seconds)*seconds
    first_end = (math.floor(formation/seconds)+1)*seconds
    positive_ends = positive_minute_endpoints(prepared, seconds)
    count = np.searchsorted(positive_ends, ends, side="right").astype(float)
    completed = np.floor((ends-first_end)/seconds)+1
    count[completed <= 0] = np.nan
    intensity = np.divide(count, completed, out=np.full(len(epochs), np.nan), where=completed > 0)
    return cadence, count, intensity


def field_registry():
    return [dict(name=f.name, block=f.block, kind=f.kind, source=f.source,
                 causal_definition=f.definition, leakage_exclusions=f.exclusion) for f in FIELDS]


def load_metadata(library):
    metadata = {}
    for row in iter_jsonl(library):
        if row["category"] in TOURS:
            row.pop("path")
            metadata[row["ticker"]] = row
    return metadata


def categorical_codes(metadata):
    return {name: {value: i for i, value in enumerate(sorted({r.get(name) for r in metadata.values() if r.get(name)}))}
            for name in CATEGORICAL}


def build_pair_panel(pair, metadata, sources, witnesses, contract, par, codebooks, evaluation_gates=None,
                     values_only=False):
    seconds = contract["minute_seconds"]
    atlas = np.asarray([g for g in contract["gates_minutes_to_bell"] if 0 < g <= pair.first_mtb])
    native = pair.grid()
    gates = (np.sort(np.union1d(native[(native > 0) & (native <= pair.first_mtb)], atlas))[::-1]
             if evaluation_gates is None else np.asarray(evaluation_gates, dtype=float))
    epochs = pair.bell-gates*seconds
    if np.any(~np.isfinite(gates)) or np.any(gates <= 0):
        raise ValueError("FEATURE_PHASE_MUST_BE_FINITE_AND_BEFORE_BELL")
    own = pair.levels(gates)
    matrix = np.full((len(epochs), len(pair.legs), len(MODEL_FIELDS)), np.nan)
    coverage = {}
    diagnostics = []
    diagnostic_arrays = {}
    for side, leg in enumerate(pair.legs):
        ticker = pair.event_id+"-"+leg.leg_id
        meta = metadata[ticker]
        source = sources.get(ticker, {})
        minutes, books = source.get("minute_features", []), source.get("books", [])
        vals = {}
        vals["formation_source"] = np.full(len(epochs), codebooks["formation_source"].get(meta.get("formation_source"), np.nan))
        publication = source.get("clock_provenance", {}).get("bell_publication_epoch")
        vals["bell_source"] = np.full(len(epochs), np.nan)
        if publication is not None and meta.get("bell_source") != "both_sides_trade_density":
            vals["bell_source"][epochs >= publication] = codebooks["bell_source"].get(meta.get("bell_source"), np.nan)
        wake = source.get("first_two_sided_book_epoch")
        wake = float(wake) if wake is not None else np.nan
        vals["book_wake_mtb"] = np.where(epochs >= wake, (pair.bell-wake)/seconds, np.nan)
        vals["book_awake_minutes"] = np.where(epochs >= wake, (epochs-wake)/seconds, np.nan)
        censored = source.get("first_source_book_was_two_sided")
        vals["wake_left_censored"] = np.where(epochs >= wake, float(censored) if censored is not None else np.nan, np.nan)
        tape = witnesses.get(ticker)
        if tape is None:
            for key in ("prefix_cadence_seconds", "positive_minutes_so_far", "causal_volume_intensity"):
                vals[key] = np.full(len(epochs), np.nan)
        else:
            cad, count, intensity = prefix_print_features(tape["prints"], epochs, leg.formation, seconds, tape.get("_prefix"))
            vals.update(prefix_cadence_seconds=cad, positive_minutes_so_far=count, causal_volume_intensity=intensity)
        bid, ask = own[:, side*3+1], own[:, side*3+2]
        spread = ask-bid
        vals["spread_cents"] = np.where(spread >= 0, spread, np.nan)
        delta = completed_closes(leg, epochs, seconds)
        vals.update(bid_consumption_velocity=delta[:, 1], ask_consumption_velocity=delta[:, 2])
        for target, source_name in (("taker_flow", "taker_flow_contracts"), ("taker_yes_contracts", "taker_yes_contracts"),
                                    ("taker_no_contracts", "taker_no_contracts"), ("distinct_levels_traded", "distinct_print_prices"),
                                    ("trade_clustering", "intertrade_gap_std_seconds")):
            vals[target] = source_column(minutes, source_name, epochs)
        for key in ("bid_depth_5", "ask_depth_5", "depth_ratio"):
            vals[key] = source_column(books, key, epochs)
        total_depth = vals["bid_depth_5"]+vals["ask_depth_5"]
        valid_depth = np.isfinite(total_depth) & (total_depth > 0) & (vals["bid_depth_5"] >= 0) & (vals["ask_depth_5"] >= 0)
        vals["depth_ratio"] = np.divide(vals["bid_depth_5"], total_depth,
            out=np.full(len(epochs), np.nan), where=valid_depth)
        oi_rows = source.get("open_interest", [])
        vals["open_interest"] = source_column(oi_rows, "open_interest", epochs)
        vals["open_interest_delta"] = source_column(oi_rows, "open_interest_delta", epochs)
        ends = np.floor(epochs/seconds)*seconds
        # Book minute close is strictly before end; machine epsilon changes only
        # the endpoint convention, never prices or an economic threshold.
        depth_now = source_column(books, "bid_depth_5", np.nextafter(ends, -np.inf))
        depth_before = source_column(books, "bid_depth_5", np.nextafter(ends-seconds, -np.inf))
        depth_change = depth_now-depth_before
        depth_change[ends-seconds < leg.formation] = np.nan
        vals["pressure_x_bid_response"] = vals["taker_flow"]*vals["bid_consumption_velocity"]
        vals["sell_pressure_x_replenishment"] = vals["taker_no_contracts"]*depth_change
        other = len(pair.legs)-1-side
        other_bid, other_ask = own[:, other*3+1], own[:, other*3+2]
        vals.update(partner_bid=other_bid, partner_ask=other_ask,
                    paired_bid_sum=bid+other_bid, paired_ask_sum=ask+other_ask,
                    paired_arb_gap_maker=par-bid-other_bid,
                    paired_arb_gap_taker=ask+other_ask-par,
                    pair_gap_abs=np.abs((bid+ask+other_bid+other_ask)/len(pair.legs)-par))
        for key, value in vals.items():
            matrix[:, side, FEATURE_INDEX[key]] = value
        matrix[epochs < pair.first_epoch, side, :] = np.nan
        if values_only:
            continue  # Same numeric model matrix; diagnostics do not feed it.
        snapshots = source.get("odds_snapshot_epochs")
        odds_known = np.searchsorted(np.asarray(snapshots), epochs, side="right") > 0 if snapshots is not None else None
        depth_intervals = source.get("ws_depth_valid_intervals")
        ws_known = None
        if depth_intervals is not None:
            ws_known = np.zeros(len(epochs), dtype=bool)
            for start, stop in depth_intervals:
                ws_known |= (epochs >= start) & (epochs < stop)
        spread_codes, spread_labels = filed_spread_bands(bid, ask, par)
        observations = source.get("book_observation_epochs")
        if observations is None:
            observed_age = np.full(len(epochs), np.nan)
        else:
            observation_epochs = np.asarray(observations, dtype=float)
            observed_age = epochs-asof(observation_epochs, observation_epochs, epochs)
        diagnostic_arrays[leg.leg_id] = dict(
            spread_band=spread_codes,
            odds_available=np.full(len(epochs), np.nan) if odds_known is None else odds_known.astype(float),
            ws_depth_available=np.full(len(epochs), np.nan) if ws_known is None else ws_known.astype(float),
            book_snapshot_age_seconds=observed_age)
        for values in diagnostic_arrays[leg.leg_id].values():
            values[epochs < pair.first_epoch] = np.nan
        diag = dict(ticker=ticker, book_wake_epoch=None if not np.isfinite(wake) else float(wake),
                    bell_source=meta.get("bell_source"), bell_source_publication_epoch=publication,
                    retrospective_cadence_s=meta.get("cadence_s"),
                    retrospective_cadence_excluded=True,
                    spread_band_labels=spread_labels,
                    book_snapshot_age="Seconds since latest actual source observation, not last change point; unknown if source observation clocks were not retained.",
                    odds_available_receipts=int(odds_known.sum()) if odds_known is not None else None,
                    ws_depth_available_receipts=int(ws_known.sum()) if ws_known is not None else None,
                    source_status=source.get("status", "SOURCE_EXTRACT" if source else "NO_EXTRACT"))
        diagnostics.append(diag)
        counts = {name: int(np.isfinite(matrix[:, side, index]).sum()) for name, index in FEATURE_INDEX.items()}
        counts.update(odds_available=diag["odds_available_receipts"], ws_depth_available=diag["ws_depth_available_receipts"])
        counts["spread_band"] = int(np.isfinite(spread_codes).sum())
        coverage[leg.leg_id] = dict(receipts=len(epochs), fields=counts)
    if values_only:
        return matrix
    return dict(event_id=pair.event_id, category=pair.category, month=pair.date[:7],
                formation=pair.formation, bell=pair.bell, date=pair.date,
                epochs=epochs, gates=gates, is_gate=np.isin(gates, atlas), values=matrix,
                fields=MODEL_FIELDS, legs=[l.leg_id for l in pair.legs], coverage=coverage,
                diagnostics=diagnostics, diagnostic_arrays=diagnostic_arrays)


def inventory(metadata, census):
    counts = defaultdict(Counter)
    for row in metadata.values():
        key = row["category"]+"/"+row["event_date"][:7]
        c = counts[key]
        c["library_legs"] += 1
        c["formation_source:"+row["formation_source"]] += 1
        c["bell_source:"+row["bell_source"]] += 1
        source_names = {s["src"] for s in row.get("source_rows", [])}
        for name in sorted(source_names):
            c["has_source:"+name] += 1
    return dict(status="LINEAGE_INVENTORY_ONLY_NOT_A_BLOCK_RESULT", fields=field_registry(),
                cohort_census=census, by_tour_month={k: dict(v) for k, v in sorted(counts.items())},
                restrictions=["Source provenance counts are not per-receipt feature availability.",
                              "No Foundation full-lifetime intensity or full-leg cadence enters the feature vector.",
                              "Native library spans and FIRST eligibility remain unchanged.",
                              "Bell clock is the filed replay ruler; inferred bell-source metadata is not causal evidence."])


def main():
    root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=root)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--sources", type=Path)
    p.add_argument("--witnesses", type=Path)
    p.add_argument("--supplemental", type=Path)
    p.add_argument("--inventory-only", action="store_true")
    args = p.parse_args()
    durable = args.root/"arb-executor/data/durable"
    library = durable/"RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz"
    counts = durable/"RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz"
    meta = load_metadata(library)
    pairs, census, _, count_proof = b.load_tick_library(library, {}, counts)
    pairs = [pair for pair in pairs if pair.category in TOURS]
    args.out.mkdir(parents=True, exist_ok=True)
    report = inventory(meta, census)
    report.update(library_sha256=sha256(library), print_counts_provenance=count_proof)
    if args.inventory_only:
        write_json(args.out/"LINEAGE_INVENTORY.json", report)
        print(json.dumps({"status": report["status"], "queries": len(pairs), "output": str(args.out)}), flush=True)
        return
    if not args.sources or not args.witnesses:
        raise ValueError("FULL_PANEL_REQUIRES_HASH_BOUND_SOURCES_AND_WITNESSES")
    sources = {r["ticker"]: r for r in iter_jsonl(args.sources)}
    witnesses = {r["ticker"]: r for r in iter_jsonl(args.witnesses)}
    if args.supplemental:
        for row in iter_jsonl(args.supplemental):
            sources.setdefault(row["ticker"], {}).update(row)
    prepare_sources(sources, witnesses)
    # Conduct constants read from the filed bench helper, never typed as model parameters.
    import conduct_scoreboard as conduct
    bound = conduct.bound_inputs(args.root)
    contract = bound["receipt"]["organ_contract"]
    codebooks = categorical_codes(meta)
    summaries = []
    for pair in pairs:
        panel = build_pair_panel(pair, meta, sources, witnesses, contract, bound["conduct"]["par"], codebooks)
        path = args.out/(pair.event_id+".npz")
        extra = {leg+"__"+key: values for leg, fields in panel.pop("diagnostic_arrays").items()
                 for key, values in fields.items()}
        np.savez_compressed(path, epoch=panel.pop("epochs"), gate=panel.pop("gates"),
                            is_gate=panel.pop("is_gate"), values=panel.pop("values"), **extra)
        panel.update(path=path.name, sha256=sha256(path))
        summaries.append(panel)
        print("PANEL "+json.dumps({"event": pair.event_id, "receipts": panel["coverage"][panel["legs"][0]]["receipts"]}), flush=True)
    report.update(status="PANEL_BUILT_NOT_A_BLOCK_RESULT", inputs={str(path):sha256(path) for path in (args.sources,args.witnesses)},
                  codebooks=codebooks, model_fields=MODEL_FIELDS, blocks=BLOCKS, events=summaries)
    write_json(args.out/"FEATURE_PANEL_RECEIPT.json", report)


if __name__ == "__main__":
    main()
