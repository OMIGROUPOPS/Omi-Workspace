#!/usr/bin/env python3
"""Read-only, bell-clock survivorship bench; never opens the tick database.

The minute proof is an implementation check, not a trading ruling. Prior
artifacts are read by their pinned git revisions, never executed or rebuilt.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cached_property
from datetime import datetime
from pathlib import Path

import numpy as np

from tune_bench_floor_calls import (sha256_file, stable_json, distribution,
                                   inverse_weighted_quantile, ess)

GATES = (2880, 2160, 1440, 1080, 720, 480, 360, 240, 180, 120, 90, 60, 30, 15, 5)
QUANTILES = (.10, .25, .50, .75, .90)
CATEGORIES = ("ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL")
RULES = ("SOFT", "HARD", "STEP-FORECAST", "FIRST-TICK-ONLY", "BASE", "TAXONOMY-NULL")
SERIES = ("fav_last", "fav_bid", "fav_ask", "dog_last", "dog_bid", "dog_ask",
          "mirror_gap", "volume_cum_delta")
SIDES = ("favorite", "underdog")
LABEL = "PROOF RUN — STALE LIBRARY (ends 2026-05-01) — NOT A RULING"
AUDIT = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/"
PRIORS = {
    "trendpath_build.py": ("66b50db3", "arb-executor/analysis/trendpath_build.py"),
    "RECOGNITION_OPERATING_POINT": ("41c1f724", AUDIT + "RECOGNITION_OPERATING_POINT.json"),
    "SHAPE_TAXONOMY_BUILD1": ("e269779b", AUDIT + "SHAPE_TAXONOMY_BUILD1.json"),
    "GATE_POLICY_EVAL_LIVE_COORDS": ("71de534a", AUDIT + "GATE_POLICY_EVAL_LIVE_COORDS.json"),
    "PER_SHAPE_FLOOR_DEPTH_TABLES": ("8ab4f2d9", AUDIT + "PER_SHAPE_FLOOR_DEPTH_TABLES.json"),
    "V52p_ROLE_DOWN_DEPTH_AGGREGATE": ("020b775c",
        ".claude/window1_live_v4_replay/v52p_ripeness_gated_role_binding_20260817/ROLE_DOWN_DEPTH_AGGREGATE.json"),
}


def pinned(root, rev, path):
    return subprocess.check_output(["git", "show", f"{rev}:{path}"], cwd=root)


def bind_prior_art(root):
    receipts = {}
    for name, (rev, path) in PRIORS.items():
        data = pinned(root, rev, path)
        receipts[name] = dict(commit=rev, path=path, sha256=hashlib.sha256(data).hexdigest())
    data = pinned(root, "e269779b", AUDIT + "SHAPE_TAXONOMY_BUILD1.csv")
    labels = {(r["code"], r["leg"]): r["family_CANDIDATE"]
              for r in csv.DictReader(io.StringIO(data.decode("utf-8-sig")))}
    receipts["SHAPE_TAXONOMY_BUILD1"]["label_csv_sha256"] = hashlib.sha256(data).hexdigest()
    taxonomy = json.loads(pinned(root, "e269779b", AUDIT + "SHAPE_TAXONOMY_BUILD1.json"))
    receipts["SHAPE_TAXONOMY_BUILD1"]["signature_method_verbatim"] = taxonomy["signature_method"]
    return receipts, labels, sorted(taxonomy["families"])


def taxonomy_features(samples):
    """The filed 17-sample signature; zeros do not count as reversals."""
    values = np.asarray(samples, dtype=float)
    if values.shape != (17,) or not np.all(np.isfinite(values)):
        raise ValueError("TAXONOMY_REQUIRES_17_FINITE_LAST_TRUE_PRINT_SAMPLES")
    steps = np.diff(values)
    moving = np.sign(steps[steps != 0])
    net = float(values[-1] - values[0])
    maxstep = float(np.max(np.abs(steps)))
    return dict(net_cents=net, travel_cents=float(np.sum(np.abs(steps))),
                maxstep_cents=maxstep,
                bigstep_share=maxstep / abs(net) if net else None,
                early_net_cents=float(values[4] - values[0]),
                late_net_cents=float(values[-1] - values[12]),
                net_after_first_quarter_cents=float(values[-1] - values[4]),
                reversals=int(np.count_nonzero(moving[1:] != moving[:-1])),
                band_width_cents=float(np.max(values) - np.min(values)))


def family(samples, print_count, sleeper_threshold):
    """Inherited rule order, with the two operator-authorized bench choices."""
    features = taxonomy_features(samples)
    if print_count is None or sleeper_threshold is None:
        return None
    if not np.isfinite(print_count) or not np.isfinite(sleeper_threshold):
        return None
    if print_count < sleeper_threshold:
        return "SLEEPER"
    net = features["net_cents"]
    magnitude = abs(net)
    if magnitude < 5:
        return "ROUND_TRIP" if features["travel_cents"] >= 10 else "QUIET_WOBBLE"
    direction = "UP" if net > 0 else "DOWN"
    if features["late_net_cents"] / net >= .70:
        return "LATE_BREAK_" + direction
    if (features["early_net_cents"] / net >= .70
            and abs(features["net_after_first_quarter_cents"]) <= 2):
        return "EARLY_SET_" + direction
    if features["maxstep_cents"] >= .60 * magnitude:
        return "ONE_STEP_" + direction
    if features["reversals"] >= 4 and features["travel_cents"] >= 2 * magnitude:
        return "GRIND_WOBBLE_" + direction
    return "DRIFT_" + direction


def taxonomy_print_count(leg, stop_epoch=None):
    """Count actual trades only; a minute/change point is never a print count."""
    stop = leg.bell if stop_epoch is None else min(float(stop_epoch), leg.bell)
    count_epoch = getattr(leg, "count_epoch", None)
    cumulative = getattr(leg, "print_count_cum", None)
    if count_epoch is not None and cumulative is not None:
        count_epoch, cumulative = np.asarray(count_epoch), np.asarray(cumulative)
        if len(count_epoch) != len(cumulative):
            raise ValueError("TAXONOMY_PRINT_COUNT_COORDINATE_LENGTH_MISMATCH")
        valid = (count_epoch >= leg.formation) & (count_epoch < leg.bell) & (count_epoch <= stop)
        indices = np.flatnonzero(valid)
        return float(cumulative[indices[-1]]) if len(indices) else 0.0
    # Named inputs bind exchange print ids, while minute paths cannot use len().
    if getattr(leg, "trade_price", None) is not None:
        epochs = np.asarray(leg.trade_epoch)
        return float(np.count_nonzero((epochs >= leg.formation) & (epochs < leg.bell)
                                      & (epochs <= stop)))
    return None


def taxonomy_signature(leg, stop_epoch=None):
    """Full-span realized label or causal prefix; never project a prefix to bell."""
    stop = leg.bell if stop_epoch is None else min(float(stop_epoch), leg.bell)
    if stop < leg.formation or not np.isfinite(leg.open):
        return None
    grid = np.linspace(leg.formation, stop, 17)
    trade_epoch = np.asarray(leg.trade_epoch, dtype=float)
    valid = (trade_epoch >= leg.formation) & (trade_epoch < leg.bell) & (trade_epoch <= stop)
    epochs = trade_epoch[valid]
    prices = getattr(leg, "trade_price", None)
    if prices is not None:
        prices = np.asarray(prices, dtype=float)[valid]
    else:
        prices = leg.sample(epochs)[:, 0]
    finite = np.isfinite(prices)
    epochs, prices = epochs[finite], prices[finite]
    indices = np.searchsorted(epochs, grid, side="right") - 1
    samples = np.full(17, float(leg.open))
    present = indices >= 0
    samples[present] = prices[indices[present]]
    # The inherited leading sample is the filed post-formation open.
    samples[0] = leg.open
    return dict(samples_cents=samples, sample_epoch=grid,
                scope="REALIZED_VERIFIED_SPAN" if stop_epoch is None else "CAUSAL_OBSERVED_PREFIX",
                endpoint_epoch=float(stop), features=taxonomy_features(samples))


def classify_leg(leg, sleeper_threshold, stop_epoch=None):
    signature = taxonomy_signature(leg, stop_epoch)
    if signature is None:
        return dict(family=None, status="STORE_SILENT: no post-formation open or observed span")
    count = taxonomy_print_count(leg, stop_epoch)
    label = family(signature["samples_cents"], count, sleeper_threshold)
    signature.update(family=label, print_count=count,
                     sleeper_threshold=sleeper_threshold,
                     status="OK" if label else "STORE_SILENT: actual print count or category p10 missing")
    signature["quiet_wobble_prose_band_exception"] = bool(
        label == "QUIET_WOBBLE" and signature["features"]["band_width_cents"] > 5)
    return signature


def bind_numerical_null(root, receipts):
    """Read numerical priors verbatim; no refit, pooled-category fill, or clipping."""
    shape_rev, shape_path = PRIORS["PER_SHAPE_FLOOR_DEPTH_TABLES"]
    table = json.loads(pinned(root, shape_rev, shape_path))
    csv_bytes = pinned(root, shape_rev, AUDIT + "PER_SHAPE_FLOOR_DEPTH_TABLES.csv")
    receipts["PER_SHAPE_FLOOR_DEPTH_TABLES"]["csv_sha256"] = hashlib.sha256(csv_bytes).hexdigest()
    receipts["PER_SHAPE_FLOOR_DEPTH_TABLES"]["rows_including_ALL"] = len(table["rows"])
    receipts["PER_SHAPE_FLOOR_DEPTH_TABLES"]["scope_warning"] = (
        "Filed July taxonomy medians post-date the stale June proof and include named July games; "
        "this fixed null is a requested retrospective comparator, not out-of-sample evidence.")
    role_rev, role_path = PRIORS["V52p_ROLE_DOWN_DEPTH_AGGREGATE"]
    roles = json.loads(pinned(root, role_rev, role_path))
    model = dict(family_rows={(row["family"], row["category"]): row for row in table["rows"]},
                 faller_depth={row["category"]: float(row["depth_below_open_cents"])
                               for row in roles["rows"]})
    receipts["taxonomy_bench_choices"] = dict(
        sleeper="actual post-formation true-print count < category empirical p10; bench choice, not taxonomy law",
        flat_after="abs(net after first quarter) <= 2 cents; operator-authorized bench choice, not taxonomy law",
        rule_order=["SLEEPER", "ROUND_TRIP_OR_QUIET_WOBBLE", "LATE_BREAK", "EARLY_SET",
                    "ONE_STEP", "GRIND_WOBBLE", "DRIFT"],
        small_net_branch="abs(net)<5: ROUND_TRIP if travel>=10; otherwise QUIET_WOBBLE; no extra band filter",
        quiet_wobble_prose_caveat=("The inherited travel split does not mathematically guarantee the prose 5-cent band. "
                                    "quiet_wobble_prose_band_exception is exposed; no new cutoff is introduced."),
        causal_family_adaptation=("At a receipt only, normalize formation through the current gate into 17 samples; "
                                  "do not use or forward-fill into the unknown remainder. Realized labels use formation through bell."),
        direction="early/late shares are signed relative to net; reversals omit zero steps")
    receipts["numerical_null_rules"] = dict(
        called_family="exact family/category depth_below_open_c.med and floor_pos.med, never ALL fallback",
        level="post-formation open minus median depth (negative depths preserved, not clipped)",
        minutes_to_bell="(1 - median floor position) * verified span minutes; no gate clipping",
        missing_category="STORE_SILENT; no cross-category or ALL borrowing",
        role_only_faller="the filed V52p category down-depth aggregate, full precision",
        role_only_climber="zero depth as requested; no early-position scalar is stated in either cited file",
        role_only_timing="STORE_SILENT: qualitative early/late is not a numeric role-only timing predictor",
        negative_depth_row_count=sum(row["depth_below_open_c"]["med"] < 0 for row in table["rows"]),
        numerical_scope="floor point/timing only; no fabricated full path or prediction band")
    return model


def numerical_null(leg, category, gate, called_family, model):
    """Point null, with source identity and absent role-only timing explicit."""
    stop = leg.bell - float(gate) * 60
    current_last = float(leg.sample([stop])[0, 0])
    current_role = role(current_last - leg.open)
    result = dict(called_family=called_family, role=current_role,
                  source="PER_SHAPE_FLOOR_DEPTH_TABLES@8ab4f2d9",
                  retrospective_fixed_prior=True, full_path_status="NOT_SPECIFIED_BY_PRIOR")
    if called_family:
        row = model["family_rows"].get((called_family, category))
        if row is None:
            result.update(status="STORE_SILENT: exact family/category row absent", category=category,
                          level_cents=None, minutes_to_bell=None)
            return result
        depth = float(row["depth_below_open_c"]["med"])
        position = float(row["floor_pos"]["med"])
        result.update(status="OK", prior_row=f"{called_family}|{category}",
                      depth_below_open_cents=depth, floor_position=position,
                      level_cents=float(leg.open - depth),
                      minutes_to_bell=float((1-position) * (leg.bell-leg.formation) / 60))
        return result
    if current_role == "FALLER":
        depth = model["faller_depth"].get(category)
        result["source"] = "V52p_ROLE_DOWN_DEPTH_AGGREGATE@020b775c"
    elif current_role == "CLIMBER":
        depth = 0.0
        result["source"] = "OPERATOR_ROLE_ONLY_CLIMBER_ZERO_DEPTH"
    else:
        depth = None
    result.update(status="PARTIAL: role-only timing STORE_SILENT" if depth is not None
                  else "STORE_SILENT: no called family or directional role",
                  depth_below_open_cents=depth,
                  level_cents=float(leg.open-depth) if depth is not None else None,
                  minutes_to_bell=None, floor_position=None)
    return result


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [clean(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def role(drift):
    return "CLIMBER" if drift >= 2 else "FALLER" if drift <= -2 else "NOT_CALLABLE"


def date_key(event, explicit=None):
    if explicit:
        return str(explicit)[:10]
    return datetime.strptime(event.split("-")[-1][:7], "%y%b%d").date().isoformat()


@dataclass
class Leg:
    leg_id: str
    anchor: float
    formation: float
    bell: float
    epoch: np.ndarray
    values: np.ndarray
    volume: np.ndarray
    trade_epoch: np.ndarray
    low: np.ndarray
    family: str | None
    onset: float | None = None
    trade_count: np.ndarray | None = None
    postformation_open: float | None = None
    trade_price: np.ndarray | None = None
    count_epoch: np.ndarray | None = None
    print_count_cum: np.ndarray | None = None

    def sample(self, epoch):
        epoch = np.atleast_1d(epoch)
        index = np.searchsorted(self.epoch, epoch, side="right") - 1
        valid = index >= 0
        out = np.full((len(epoch), 4), np.nan)
        out[valid, :3] = self.values[index[valid]]
        out[valid, 3] = self.volume[index[valid]]
        return out

    @property
    def open(self):
        if self.postformation_open is not None:
            return self.postformation_open
        if not len(self.trade_epoch):
            return np.nan
        return self.sample([self.trade_epoch[0]])[0, 0]


@dataclass
class Pair:
    event_id: str
    category: str
    date: str
    legs: tuple[Leg, Leg]
    first_epoch: float
    grain: str

    @property
    def formation(self):
        return max(x.formation for x in self.legs)

    @property
    def bell(self):
        return self.legs[0].bell

    @property
    def first_mtb(self):
        return (self.bell - self.first_epoch) / 60

    @cached_property
    def first(self):
        return self.levels([self.first_mtb])[0]

    def grid(self):
        return self._grid

    @cached_property
    def _grid(self):
        ep = np.union1d(self.legs[0].epoch, self.legs[1].epoch)
        return (self.bell - ep[ep >= self.first_epoch]) / 60

    @cached_property
    def _cache(self):
        ep = np.union1d(self.legs[0].epoch, self.legs[1].epoch)
        sides = [leg.sample(ep) for leg in self.legs]
        out = np.column_stack((sides[0][:, :3], sides[1][:, :3],
                               sides[0][:, 0] + sides[1][:, 0],
                               sides[0][:, 3] + sides[1][:, 3]))
        first_vol = sum(leg.sample([self.first_epoch])[0, 3] for leg in self.legs)
        out[:, 7] -= first_vol
        return ep, out

    def levels(self, mtb):
        grid, values = self._cache
        indices = np.searchsorted((grid-self.bell)/60, -np.atleast_1d(mtb), side="right")-1
        result = values[np.maximum(indices, 0)].copy()
        result[indices < 0] = np.nan
        return result

    def roles(self, mtb):
        last = self.levels([mtb])[0, [0, 3]]
        return tuple(role(last[i] - self.legs[i].open) for i in range(2))

    def scorable(self, mtb):
        ep = self.bell - mtb * 60
        return (self.first_mtb >= mtb and all(
            np.any(leg.trade_epoch <= ep) and np.any(leg.trade_epoch > ep)
            for leg in self.legs))


def load_named_inputs(root, labels, tape_dir, prints_path):
    """Join real exchange trades with recorder books; snapshots never invent trades.

    Named truth coordinates/open anchors come from the filed ground-truth table.
    The first pool observation is the exact instant both legs have traded since
    formation, not a requirement that both traded within one simultaneous minute.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    root, tape_dir, prints_path = Path(root), Path(tape_dir), Path(prints_path)
    suffixes = ("ALTGAS", "GIUBAR", "URSPAL", "LAJSVA", "DANPRA")
    truth_path = root / AUDIT / "W1_GROUND_TRUTH_TABLE.json"
    truth_bytes = truth_path.read_bytes()
    truth = json.loads(truth_bytes)
    specs = {row["event_id"]: row for row in truth["rows"]
             if any(row["event_id"].endswith(suffix) for suffix in suffixes)}
    if len(specs) != len(suffixes):
        raise RuntimeError("NAMED_TRUTH_TABLE_MISSING_OR_AMBIGUOUS_EVENT")
    onset_path = (".claude/window1_live_v4_replay/"
                  "v52e_disposition_804_four_state_20260813/"
                  "POST_ONSET_OFFER_CAPTURE_LEDGER_804.jsonl.gz")
    onset_bytes = pinned(root, "4716657a", onset_path)
    onsets = {row["event_id"]: row.get("legs", {})
              for row in (json.loads(line) for line in gzip.decompress(onset_bytes).splitlines()
                          if line.strip()) if row["event_id"] in specs}
    tickers, leg_specs = set(), {}
    for event, spec in specs.items():
        formation, bell = spec.get("formation_end_game"), spec.get("bell_epoch")
        if formation is None or bell is None or formation >= bell:
            raise RuntimeError(f"NAMED_INVALID_TRUTH_SPAN {event}")
        for prefix in ("legA", "legB"):
            leg = spec[prefix]
            ticker = f"{event}-{leg}"
            opened = spec.get(f"{prefix}_open_postformation_c")
            if opened is None:
                raise RuntimeError(f"NAMED_POSTFORMATION_OPEN_MISSING {ticker}")
            tickers.add(ticker)
            leg_specs[ticker] = (event, leg, float(formation), float(bell), float(opened))
    needles = tuple(event.encode("utf-8") for event in specs)
    raw_trades = defaultdict(list)
    seen_ids, previous_epoch = {}, {}
    census = Counter()
    digest = hashlib.sha256()
    with prints_path.open("rb") as stream:
        for line_number, line in enumerate(stream, 1):
            digest.update(line)
            census["prints_file_lines"] += 1
            if not any(needle in line for needle in needles):
                continue
            row = json.loads(line)
            ticker = row.get("ticker")
            if ticker not in tickers:
                continue
            census["selected_print_rows"] += 1
            if row.get("true_print") is not True:
                raise RuntimeError(f"NAMED_NON_TRUE_PRINT {ticker} line={line_number}")
            trade_id = row.get("trade_id") or row.get("receipt_id")
            if not trade_id:
                raise RuntimeError(f"NAMED_TRADE_ID_MISSING {ticker} line={line_number}")
            epoch = datetime.fromisoformat(row["exchange_ts"].replace("Z", "+00:00")).timestamp()
            price, size = float(row["price_cents"]), float(row["size"])
            if not (math.isfinite(epoch) and math.isfinite(price) and math.isfinite(size)
                    and 0 <= price <= 100 and size > 0):
                raise RuntimeError(f"NAMED_INVALID_TRUE_PRINT {ticker} line={line_number}")
            signature = (ticker, epoch, price, size)
            if trade_id in seen_ids:
                if seen_ids[trade_id] != signature:
                    raise RuntimeError(f"NAMED_CONFLICTING_DUPLICATE_TRADE_ID {trade_id}")
                census["identical_duplicate_trade_ids_removed"] += 1
                continue
            seen_ids[trade_id] = signature
            if epoch < previous_epoch.get(ticker, -math.inf):
                census["source_order_timestamp_regressions_sorted"] += 1
            previous_epoch[ticker] = epoch
            if epoch >= leg_specs[ticker][3]:
                census["selected_trades_at_or_after_bell_excluded"] += 1
                continue
            raw_trades[ticker].append((epoch, line_number, price, size))
    sources = {
        "truth_table": dict(path=str(truth_path), bytes=len(truth_bytes),
                            sha256=hashlib.sha256(truth_bytes).hexdigest()),
        "canonical_onsets": dict(commit="4716657a", path=onset_path, bytes=len(onset_bytes),
                                  sha256=hashlib.sha256(onset_bytes).hexdigest()),
        "true_prints": dict(path=str(prints_path), bytes=prints_path.stat().st_size,
                            sha256=digest.hexdigest()),
        "book_tapes": {},
    }
    eastern = ZoneInfo("America/New_York")
    grouped = defaultdict(list)
    per_leg = {}
    for ticker in sorted(tickers):
        event, leg_id, formation, bell, opened = leg_specs[ticker]
        tape_path = tape_dir / f"{ticker}.csv.gz"
        tape_bytes = tape_path.read_bytes()
        sources["book_tapes"][ticker] = dict(path=str(tape_path), bytes=len(tape_bytes),
                                            sha256=hashlib.sha256(tape_bytes).hexdigest())
        books = {}
        rows = csv.DictReader(io.StringIO(gzip.decompress(tape_bytes).decode("utf-8-sig")))
        for row in rows:
            if row.get("ticker") != ticker:
                raise RuntimeError(f"NAMED_TAPE_TICKER_MISMATCH {tape_path}")
            epoch = datetime.strptime(row["ts_et"], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=eastern).timestamp()
            if epoch >= bell:
                continue
            values = []
            for field in ("bid_1", "ask_1"):
                text_value = row.get(field)
                value = float(text_value) if text_value not in (None, "", "None", "null", "NaN") else np.nan
                if math.isfinite(value) and not 0 <= value <= 100:
                    raise RuntimeError(f"NAMED_INVALID_BOOK_PRICE {ticker} {field}")
                values.append(value)
            books[epoch] = tuple(values)
        trades = sorted(raw_trades[ticker], key=lambda value: (value[0], value[1]))
        before_trades = [trade for trade in trades if trade[0] < formation]
        trades = [trade for trade in trades if trade[0] >= formation]
        if not trades:
            census["named_leg_no_postformation_true_trade"] += 1
            continue
        trade_at = defaultdict(list)
        for trade in trades:
            trade_at[trade[0]].append(trade)
        book_epochs = sorted(books)
        prior_book_index = int(np.searchsorted(book_epochs, formation, side="left")) - 1
        bid, ask = books[book_epochs[prior_book_index]] if prior_book_index >= 0 else (np.nan, np.nan)
        last = before_trades[-1][2] if before_trades else np.nan
        volume, count, low = 0.0, 0, np.nan
        epochs = sorted({formation} | {epoch for epoch in books if epoch >= formation} | set(trade_at))
        emitted_epochs, states, volumes, counts, lows = [], [], [], [], []
        previous_state = None
        for epoch in epochs:
            if epoch in books:
                bid, ask = books[epoch]
            for _, _, price, size in trade_at.get(epoch, ()):
                last = price
                volume += size
                count += 1
                low = price if not math.isfinite(low) else min(low, price)
            state = (last, bid, ask, volume, count, low)
            equal = previous_state is not None and all(
                left == right or (isinstance(left, float) and isinstance(right, float)
                                  and math.isnan(left) and math.isnan(right))
                for left, right in zip(state, previous_state))
            if equal:
                continue
            emitted_epochs.append(epoch)
            states.append((last, bid, ask))
            volumes.append(volume)
            counts.append(count)
            lows.append(low)
            previous_state = state
        onset = onsets.get(event, {}).get(leg_id, {}).get("onset_sel")
        group_leg = Leg(leg_id, opened, formation, bell, np.asarray(emitted_epochs),
                        np.asarray(states, dtype=float), np.asarray(volumes),
                        np.asarray([trade[0] for trade in trades]), np.asarray(lows),
                        labels.get((event.split("-")[-1], leg_id)), onset,
                        np.asarray(counts, dtype=np.int64), opened,
                        np.asarray([trade[2] for trade in trades], dtype=float))
        grouped[event].append(group_leg)
        per_leg[ticker] = dict(formation_end_epoch=formation, bell_epoch=bell,
                               verified_span_end_epoch=specs[event].get("span_end_epoch"),
                               filed_postformation_open_cents=opened, onset_epoch=onset,
                               first_postformation_trade_epoch=trades[0][0],
                               first_postformation_trade_cents=trades[0][2],
                               preformation_true_trade_count=len(before_trades),
                               postformation_prebell_true_trade_count=len(trades),
                               volume_cum=volume, native_change_points=len(emitted_epochs))
    pairs = []
    for event, spec in sorted(specs.items()):
        legs = grouped[event]
        if len(legs) != 2:
            census["named_pair_no_first_true_trade"] += 1
            continue
        first_epoch = max(leg.trade_epoch[0] for leg in legs)
        first_prices = [leg.sample([first_epoch])[0, 0] for leg in legs]
        if not all(math.isfinite(price) for price in first_prices):
            raise RuntimeError(f"NAMED_FIRST_TRADE_PRICE_MISSING {event}")
        if first_prices[0] == first_prices[1]:
            census["named_pair_first_tick_tie_STORE_SILENT"] += 1
            continue
        legs = tuple(sorted(legs, key=lambda leg: -leg.sample([first_epoch])[0, 0]))
        pairs.append(Pair(event, spec["category"], date_key(event), legs,
                          first_epoch, "NATIVE_TRUE_PRINT_AND_BOOK"))
        census["named_oriented_pairs"] += 1
    return pairs, dict(sources=sources, census=dict(sorted(census.items())), per_leg=per_leg,
                       rules={
                           "first_tick": "Exact instant both sides have a true trade since formation; first=minimal causal state with both traded, not simultaneous-minute trades.",
                           "true_trade": "true_print=true; exchange_ts, price_cents, size; identical trade_id rows deduplicated, conflicting identities fail; ties keep source order.",
                           "book": "Native recorder ts_et in America/New_York; bid_1/ask_1 only. Snapshot last_trade is never used.",
                           "volume": "Sum of true-print size since formation; exact trade count counts unique trade_id, not changed prices or minutes.",
                           "clock": "Filed W1_GROUND_TRUTH_TABLE formation_end_game and bell_epoch, not trace first-stage recorder-open time. Explicit verified span_end also recorded; no synthetic data to bell.",
                           "role_open": "Filed leg*_open_postformation_c, kept separately from first pool-observation prices.",
                           "missing": "No snapshot/anchor substitution for missing true prints; no first postformation trade excludes the pair."})


def load_library(path, labels):
    grouped = defaultdict(list)
    census = Counter()
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            r = json.loads(line)
            grouped[r["event_id"]].append(r)
    pairs = []
    for event, rows in sorted(grouped.items()):
        cat = rows[0]["category"]
        census[f"{cat}:pair_events"] += 1
        reason = None
        if len(rows) != 2:
            reason = "not_two_legs"
        elif rows[0]["bell_epoch"] != rows[1]["bell_epoch"]:
            reason = "different_leg_bells_no_common_clock"
        if reason:
            census[f"{cat}:{reason}"] += 1
            continue
        legs = []
        for r in rows:
            p = r["path"]
            f, b = float(r["formation_end_epoch"]), float(r["bell_epoch"])
            ep = np.array([x.get("timestamp_epoch", f + x["window_fraction"] * (b-f)) for x in p])
            values = np.array([[x.get(k) for k in ("last_cents", "bid_cents", "ask_cents")] for x in p], dtype=float)
            volume = np.array([x.get("volume_cum") for x in p], dtype=float)
            if any("true_trade" in x for x in p):
                trade = np.array([bool(x.get("true_trade")) for x in p])
            else:
                trade = np.r_[volume[:1] > 0, np.diff(volume) > 0]
                if len(p) and p[0].get("seen_true_trade_high_cents") is not None:
                    trade[0] = True
            legs.append(Leg(r["leg_id"], float(r["anchor_cents"]), f, b, ep, values,
                            volume, ep[trade], np.array([x.get("seen_true_trade_low_cents") for x in p], dtype=float),
                            labels.get((event.split("-")[-1], r["leg_id"])), r.get("onset_epoch"),
                            postformation_open=float(r.get("postformation_open_cents", r["anchor_cents"]))))
        if any(not len(x.trade_epoch) for x in legs):
            census[f"{cat}:no_first_true_trade"] += 1
            continue
        first = max(x.trade_epoch[0] for x in legs)
        first_values = [x.sample([first])[0, 0] for x in legs]
        if not all(np.isfinite(first_values)):
            census[f"{cat}:no_first_true_trade"] += 1
            continue
        if first_values[0] == first_values[1]:
            census[f"{cat}:first_tick_tie_STORE_SILENT"] += 1
            continue
        legs = tuple(sorted(legs, key=lambda x: -x.sample([first])[0, 0]))
        date = date_key(event, rows[0].get("event_date"))
        pairs.append(Pair(event, cat, date, legs, first, rows[0].get("grain", "MINUTE")))
        census[f"{cat}:oriented_pairs"] += 1
    return pairs, dict(sorted(census.items()))


def attach_print_counts(pairs, cache_path, library_path):
    if not cache_path or not Path(cache_path).is_file():
        raise ValueError("EXACT_PRINT_COUNT_SOURCE_REQUIRED: do not use minute count or volume as print count")
    with gzip.open(cache_path, "rt", encoding="utf-8") as stream:
        data = json.load(stream)
    if data["library_sha256"] != sha256_file(library_path):
        raise ValueError("PRINT_COUNT_ADAPTER_LIBRARY_HASH_MISMATCH")
    by_category = defaultdict(list)
    for pair in pairs:
        for leg in pair.legs:
            ticker = pair.event_id + "-" + leg.leg_id
            r = data["legs"][ticker]
            if float(r["formation_end_epoch"]) != leg.formation or float(r["bell_epoch"]) != leg.bell:
                raise ValueError("PRINT_COUNT_SPAN_MISMATCH:"+ticker)
            values = np.asarray(r["cumulative"], dtype=float).reshape(-1, 2)
            leg.count_epoch = values[:, 0]
            leg.print_count_cum = values[:, 1]
            if len(values) and (np.any(np.diff(values[:, 0]) < 0) or np.any(np.diff(values[:, 1]) < 0)):
                raise ValueError("PRINT_COUNT_NONMONOTONE:"+ticker)
            total = taxonomy_print_count(leg)
            if total != r["total_count"]:
                raise ValueError("PRINT_COUNT_TOTAL_MISMATCH:"+ticker)
            by_category[pair.category].append(total)
    thresholds = {cat: inverse_weighted_quantile(np.asarray(counts), np.ones(len(counts)), .10)
                  for cat, counts in by_category.items()}
    receipt = {key: value for key, value in data.items() if key != "legs"}
    receipt.update(cache_path=str(cache_path), cache_sha256=sha256_file(cache_path),
        extract_row_count=sum(len(r["cumulative"]) for r in data["legs"].values()),
        extract_leg_count=len(data["legs"]), cache_bytes=Path(cache_path).stat().st_size,
        extract_row_definition="one (ticker, minute_ts, cumulative_trade_count) observation for every nonzero-trade minute within the filed library spans",
        sleeper_p10_by_category=thresholds,
        category_print_count_distributions={c: distribution(v) for c, v in by_category.items()},
        calibration_scope="All oriented library legs in category, no named games. Retrospective data-set scale, not per-query walk-forward calibration.")
    return thresholds, receipt


def label_pairs(pairs, thresholds):
    counts = Counter()
    for pair in pairs:
        for leg in pair.legs:
            leg.filed_family = leg.family
            leg.sleeper_threshold = thresholds[pair.category]
            result = classify_leg(leg, leg.sleeper_threshold)
            leg.family = result["family"]
            leg.family_audit = result
            counts[pair.category+":"+str(leg.family)] += 1
    return dict(sorted(counts.items()))


def build_print_count_cache(library_path, parquet_path, cache_path):
    """Optional local exact-count regeneration; no SSH or database access."""
    import pyarrow.parquet as pq
    if Path(cache_path).resolve() in (Path(library_path).resolve(), Path(parquet_path).resolve()):
        raise ValueError("PRINT_COUNT_CACHE_MUST_NOT_OVERWRITE_INPUT")
    with gzip.open(library_path, "rt", encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream]
    bounds = {r["ticker"]: r for r in rows}
    if len(bounds) != len(rows):
        raise ValueError("DUPLICATE_LIBRARY_TICKER")
    counts, matched = defaultdict(list), Counter()
    source = pq.ParquetFile(parquet_path)
    columns = ["ticker", "minute_ts", "trade_count_in_minute"]
    for batch in source.iter_batches(columns=columns):
        values = batch.to_pydict()
        for ticker, minute, count in zip(*(values[k] for k in columns)):
            bound = bounds.get(ticker)
            if not bound or not bound["formation_end_epoch"] <= minute < bound["bell_epoch"]:
                continue
            matched[ticker] += 1
            if count is None or count < 0 or count != int(count):
                raise ValueError("INVALID_TRADE_COUNT:"+ticker)
            if count:
                counts[ticker].append((minute, int(count)))
    legs = {}
    for ticker, bound in sorted(bounds.items()):
        if not matched[ticker]:
            raise ValueError("NO_SOURCE_ROWS_FOR_BOUND:"+ticker)
        total, cumulative, prior = 0, [], None
        for minute, count in sorted(counts[ticker]):
            if minute == prior:
                raise ValueError("DUPLICATE_COUNT_MINUTE:"+ticker)
            prior = minute
            total += count
            cumulative.append([minute, total])
        legs[ticker] = dict(category=bound["category"], formation_end_epoch=bound["formation_end_epoch"],
            bell_epoch=bound["bell_epoch"], total_count=total, cumulative=cumulative,
            source_minute_rows=matched[ticker], nonzero_minute_rows=len(cumulative))
    result = dict(schema="EXACT_PARQUET_TRADE_COUNT_ADAPTER_V1", library_sha256=sha256_file(library_path),
        source_path=str(parquet_path), source_sha256=sha256_file(parquet_path), source_rows=source.metadata.num_rows,
        source_columns={k: str(source.schema_arrow.field(k).type) for k in columns},
        count_rule="sum trade_count_in_minute over each filed formation<=minute<bell; exact sparse cumulative counts", legs=legs)
    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(cache_path).open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            zipped.write(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def relative_weights(logw):
    valid = np.isfinite(logw)
    w = np.zeros_like(logw)
    if np.any(valid):
        w[valid] = np.exp(logw[valid] - np.max(logw[valid]))
    return w


def initial_pool(query, pairs):
    members = [p for p in pairs if p.category == query.category and
               p.event_id != query.event_id and p.date != query.date and
               p.bell < query.formation]
    if not members:
        return [], np.array([])
    firsts = np.array([m.first for m in members])
    price_gap = np.abs(firsts[:, [0, 3]] - query.first[[0, 3]]).sum(axis=1)
    clock_gap = np.abs(np.array([m.first_mtb for m in members]) - query.first_mtb)
    w = 1 / (1 + price_gap) / (1 + clock_gap / query.first_mtb)
    return members, w


def quantile_cube(values, weights):
    """Exact inverse-CDF weighted quantiles; no cents rounding or volume bins."""
    shape = values.shape[1:]
    flat = values.reshape(len(weights), -1)
    valid = np.isfinite(flat)
    if np.any(valid) and np.all(flat[valid] == np.rint(flat[valid])):
        minimum, maximum = int(flat[valid].min()), int(flat[valid].max())
        span = maximum-minimum+1
        # Exact integer histogram when smaller than sorting the observation matrix.
        if span <= len(weights):
            out = {q: np.full(flat.shape[1], np.nan) for q in QUANTILES}
            for start in range(0, flat.shape[1], 256):
                block = flat[:, start:start+256]
                present = np.isfinite(block)
                columns = np.broadcast_to(np.arange(block.shape[1]), block.shape)
                keys = columns*span + np.where(present, block, minimum).astype(np.int64)-minimum
                w = np.broadcast_to(weights[:, None], block.shape)
                histogram = np.bincount(keys[present], weights=w[present], minlength=block.shape[1]*span).reshape(block.shape[1], span)
                cum = np.cumsum(histogram, axis=1)
                for q in QUANTILES:
                    found = np.argmax(cum >= q*cum[:, -1, None], axis=1).astype(float)+minimum
                    found[cum[:, -1] == 0] = np.nan
                    out[q][start:start+block.shape[1]] = found
            return {q: x.reshape(shape) for q, x in out.items()}
    order = np.argsort(flat, axis=0, kind="stable")
    sorted_values = np.take_along_axis(flat, order, axis=0)
    sorted_weights = weights[order] * np.isfinite(sorted_values)
    cumul = np.cumsum(sorted_weights, axis=0)
    total = cumul[-1]
    out = {}
    for q in QUANTILES:
        indices = np.argmax(cumul >= q * total, axis=0)
        result = sorted_values[indices, np.arange(flat.shape[1])]
        result[total == 0] = np.nan
        out[q] = result.reshape(shape)
    return out


def gate_coordinates(query, gate):
    epoch = query.bell - gate * 60
    output = {}
    for side, leg in zip(SIDES, query.legs):
        zero = max(leg.onset, query.formation) if leg.onset is not None else None
        output[side] = {
            "coordinate_zero_epoch": zero,
            "minutes_since_onset": (epoch-zero)/60 if zero is not None and epoch >= zero else None,
            "post_onset_trade_count": None,
            "cumulative_absolute_travel_cents": None,
            "status": "STORE_SILENT: index has no canonical onset or exact trade count",
        }
        if zero is None:
            continue
        if epoch < zero:
            output[side]["status"] = "NOT_YET_ONSET"
            continue
        if leg.trade_price is None:
            continue
        if len(leg.trade_price) != len(leg.trade_epoch) or np.any(np.diff(leg.trade_epoch) < 0):
            raise RuntimeError(f"TRUE_TRADE_COORDINATE_ARRAY_MISMATCH {query.event_id} {leg.leg_id}")
        start = int(np.searchsorted(leg.trade_epoch, zero, side="left"))
        end = int(np.searchsorted(leg.trade_epoch, epoch, side="right"))
        # Count [zero, gate] trades, including same-time distinct trade IDs. The
        # preceding known true price anchors the first post-zero price change;
        # absent one, no open/mid/book price is substituted for that missing gap.
        reference_available = start > 0
        prices = leg.trade_price[start - 1 if reference_available else start:end]
        if np.any(~np.isfinite(prices)):
            raise RuntimeError(f"TRUE_TRADE_COORDINATE_PRICE_MISSING {query.event_id} {leg.leg_id}")
        output[side].update(
            post_onset_trade_count=end-start,
            cumulative_absolute_travel_cents=float(np.abs(np.diff(prices)).sum()),
            travel_reference_available=reference_available,
            travel_reference=("last true trade strictly before coordinate zero" if reference_available else
                              "first true trade at/after coordinate zero; preceding gap unobserved"),
            status="READY_TRUE_TRADE_COORDINATES",
        )
    return output


def first_bind(query, gate):
    """Gate activates at g; score first subsequent directional call, never final hold."""
    out = {}
    for side, leg in zip(SIDES, query.legs):
        gate_epoch = query.bell - gate * 60
        epochs = np.r_[gate_epoch, leg.epoch[leg.epoch > gate_epoch]]
        calls = [role(v-leg.open) for v in leg.sample(epochs)[:, 0]]
        directional = [x for x in calls if x != "NOT_CALLABLE"]
        truth = role(leg.values[-1, 0]-leg.open)
        flips = sum(a != b for a, b in zip(directional, directional[1:]))
        current = calls[0]
        out[side] = dict(current_role=current, truth=truth,
                         first_bind=directional[0] if directional else None,
                         first_bind_called=bool(directional),
                         first_bind_correct=directional[0] == truth if directional else None,
                         flipped=bool(flips), flip_count=flips,
                         flip_rate_of_bound=bool(flips) if directional else None,
                         called_now=current != "NOT_CALLABLE",
                         correct_if_called_now=current == truth if current != "NOT_CALLABLE" else None,
                         held_at_end_correct=directional[-1] == truth if directional else None,
                         held_at_end_note="TAUTOLOGY when the final drift is directional; not first-bind accuracy")
    return out


def family_distribution(members, weights, families):
    total = float(weights.sum())
    counts = {name: 0.0 for name in families}
    for family, weight in zip(members, weights):
        if family in counts:
            counts[family] += float(weight)
    known = sum(counts.values())
    complete = total > 0 and all(f in counts for f, w in zip(members, weights) if w > 0)
    return dict(status="OK" if complete else "STORE_SILENT: unlabelled historical members",
                labelled_weight_share=known/total if total else None,
                probabilities={key: value/total if total else None for key, value in counts.items()},
                top=min(counts, key=lambda x: (-counts[x], x)) if complete else None)


def forecast_context(query, members, gate):
    grid = query.grid()
    grid = grid[grid < gate]
    current = query.levels([gate])[0]
    member_current = np.array([m.levels([gate])[0] for m in members])
    opens = np.array([[leg.open for leg in m.legs] for m in members])
    drifts = member_current[:, [0, 3]]-opens
    roles = query.roles(gate)
    member_roles = np.where(drifts >= 2, "CLIMBER", np.where(drifts <= -2, "FALLER", "NOT_CALLABLE"))
    masks = []
    for i in range(2):
        matching = (member_roles[:, i] == roles[i]) | (roles[i] == "NOT_CALLABLE")
        available = np.all(np.isfinite(member_current[:, i*3:i*3+3]), axis=1)
        available &= np.array([m.first_mtb for m in members]) >= gate
        masks.append(matching & available)
    return dict(grid=grid, current=current, actual=query.levels(grid),
                member_current=member_current, roles=roles, masks=masks)


def forecast(query, members, weights, gate, families, include_paths=False, context=None):
    effective = ess(weights) or 0
    result = dict(ess=effective, member_count=int(np.count_nonzero(weights)),
                  weight_sum=float(weights.sum()), sides={}, shared={})
    context = context or forecast_context(query, members, gate)
    grid = context["grid"]
    if not len(grid):
        result["status"] = "NO-CALL: no query remainder"
        return result
    current, actual = context["current"], context["actual"]
    roles, masks = context["roles"], context["masks"]
    def remainder_values(active, columns):
        if "remainder" not in context:
            context["remainder"] = np.stack([m.levels(grid)-context["member_current"][j] for j, m in enumerate(members)])
        return context["remainder"][active, :, columns]
    for i, side in enumerate(SIDES):
        start = i*3
        mask = masks[i]
        sw = weights * mask
        side_ess = ess(sw) or 0
        side_result = dict(ess=side_ess, member_count=int(np.count_nonzero(sw)),
                           role=roles[i], role_filter_bypassed=roles[i] == "NOT_CALLABLE",
                           family=family_distribution([m.legs[i].family for m in members], sw, families),
                           realized_family=query.legs[i].family)
        result["sides"][side] = side_result
        if side_ess < 10:
            side_result["status"] = "NO-CALL: ESS < 10"
            continue
        active = sw > 0
        quants = quantile_cube(remainder_values(active, slice(start, start+3)), sw[active])
        levels = {q: x + current[start:start+3] for q, x in quants.items()}
        last = actual[:, start]
        floor = float(np.nanmin(last))
        floor_mtb = float(grid[np.flatnonzero(last == floor)[0]])
        pred = {}
        for q in (.25, .50, .75):
            y = levels[q][:, 0]
            low = float(np.nanmin(y))
            pred[f"q{int(q*100)}"] = dict(level_cents=low, minutes_to_bell=float(grid[np.flatnonzero(y == low)[0]]))
        p = pred["q50"]
        side_result.update(status="OK", floors=pred, actual_floor_cents=floor,
                           actual_floor_mtb=floor_mtb,
                           floor_absolute_error_cents=abs(p["level_cents"]-floor),
                           floor_within_2_cents=abs(p["level_cents"]-floor) <= 2,
                           floor_timing_absolute_error_minutes=abs(p["minutes_to_bell"]-floor_mtb),
                           floor_timing_within_0_10_minutes=abs(p["minutes_to_bell"]-floor_mtb) <= .10,
                           floor_band_coverage=pred["q25"]["level_cents"] <= floor <= pred["q75"]["level_cents"],
                           path_last_mae_cents=float(np.nanmean(abs(levels[.50][:, 0]-last))),
                           coverage={}, reach={})
        for low, high, label in ((.25, .75, "q25_q75"), (.10, .90, "q10_q90")):
            inside = (actual[:, start:start+3] >= levels[low]) & (actual[:, start:start+3] <= levels[high])
            present = np.isfinite(actual[:, start:start+3]) & np.isfinite(levels[low]) & np.isfinite(levels[high])
            side_result["coverage"][label] = {name: float(np.mean(inside[present[:, j], j])) if np.any(present[:, j]) else None for j, name in enumerate(("last", "bid", "ask"))}
            side_result.setdefault("coverage_observations", {})[label] = dict(zip(("last", "bid", "ask"), present.sum(axis=0).tolist()))
            side_result["_inside_"+label] = inside[:, 0]
            side_result["_present_"+label] = present[:, 0]
        for q in ("q25", "q50"):
            px = pred[q]["level_cents"]
            postable = bool(np.isfinite(current[start+1]) and px < current[start+1])
            # Keep ORDER 4's diagnostic exactly, but expose the historical-low hazard.
            leg = query.legs[i]
            after = leg.epoch > query.bell - gate*60
            reached = postable and bool(np.any(leg.low[after] <= px))
            true_after = leg.trade_epoch[leg.trade_epoch > query.bell - gate*60]
            print_reach = postable and bool(np.any(leg.sample(true_after)[:, 0] <= px))
            side_result["reach"][q] = dict(postable=postable, reached=bool(reached),
                                          future_print_reached=bool(print_reach),
                                          level_cents=px,
                                          status="REACHED" if reached else "NOT_REACHED" if postable else "NOT_POSTABLE")
        if include_paths:
            side_result["predicted_remainder"] = dict(minutes_to_bell=grid,
                delta_from_now={f"q{int(q*100)}": values for q, values in quants.items()})
    pairmask = masks[0] & masks[1]
    pw = weights * pairmask
    paired_labels = [m.legs[0].family+"|"+m.legs[1].family for m in members]
    result["pair_family"] = family_distribution(paired_labels, pw, sorted(set(paired_labels)))
    result["pair_family"]["ess"] = ess(pw) or 0
    if (ess(pw) or 0) < 10:
        result["pair_family"].update(status="NO-CALL: pair-family ESS < 10", top=None)
    result["realized_pair_family"] = query.legs[0].family+"|"+query.legs[1].family
    result["shared"]["ess"] = ess(pw) or 0
    if (ess(pw) or 0) >= 10:
        active = pw > 0
        shared_quantiles = quantile_cube(remainder_values(active, slice(6, None)), pw[active])
        result["shared"]["coverage"] = {}
        for lo, hi, label in ((.25, .75, "q25_q75"), (.10, .90, "q10_q90")):
            observed = actual[:, 6:] - current[6:]
            valid = np.isfinite(observed) & np.isfinite(shared_quantiles[lo]) & np.isfinite(shared_quantiles[hi])
            coverage = []
            for j in range(2):
                coverage.append(float(np.mean((observed[valid[:, j], j] >= shared_quantiles[lo][valid[:, j], j]) &
                                              (observed[valid[:, j], j] <= shared_quantiles[hi][valid[:, j], j]))) if np.any(valid[:, j]) else None)
            result["shared"]["coverage"][label] = dict(zip(SERIES[6:], coverage))
        if include_paths:
            result["shared"]["predicted_remainder"] = dict(minutes_to_bell=grid,
                delta_from_now={f"q{int(q*100)}": x for q, x in shared_quantiles.items()})
    left, right = [result["sides"][s] for s in SIDES]
    if left["status"] == right["status"] == "OK":
        result["status"] = "OK"
        result["joint_floor_hit"] = left["floor_within_2_cents"] and right["floor_within_2_cents"]
        result["joint_floor_band_coverage"] = left["floor_band_coverage"] and right["floor_band_coverage"]
        result["joint_path_coverage"] = {}
        for label in ("q25_q75", "q10_q90"):
            present = left["_present_"+label] & right["_present_"+label]
            result["joint_path_coverage"][label] = float(np.mean((left["_inside_"+label] & right["_inside_"+label])[present])) if np.any(present) else None
        result["pair_reach"] = {}
        for q in ("q25", "q50"):
            reached = left["reach"][q]["reached"] and right["reach"][q]["reached"]
            discount = 100-left["reach"][q]["level_cents"]-right["reach"][q]["level_cents"]
            result["pair_reach"][q] = dict(reached=reached, discount_if_reached=discount if reached else None,
                expected_pair_discount_contribution=discount if reached else 0,
                not_postable=not(left["reach"][q]["postable"] and right["reach"][q]["postable"]))
    else:
        result["status"] = "NO-CALL: one or both role-filtered sides below ESS 10"
    for side_result in result["sides"].values():
        side_result.pop("_inside_q25_q75", None)
        side_result.pop("_inside_q10_q90", None)
        side_result.pop("_present_q25_q75", None)
        side_result.pop("_present_q10_q90", None)
    return clean(result)


def null_forecast(query, gate, model):
    result = dict(status="OK", retrospective_fixed_prior=True, sides={})
    for side, leg in zip(SIDES, query.legs):
        called = classify_leg(leg, leg.sleeper_threshold, query.bell-gate*60)
        point = numerical_null(leg, query.category, gate, called.get("family"), model)
        prior = model["family_rows"].get((called.get("family"), query.category), {})
        n = prior.get("legs", 0)
        row = dict(status=point["status"], ess=n, member_count=n, called_family=called,
                   null_point=point, realized_family=leg.family)
        if n and n < 10:
            row["status"] = "NO-CALL: prior row effective count < 10"
        grid = query.grid()
        grid = grid[grid < gate]
        if row["status"] == "OK" and len(grid):
            actual = leg.sample(query.bell-grid*60)[:, 0]
            floor = float(np.nanmin(actual))
            mtb = float(grid[np.flatnonzero(actual == floor)[0]])
            error = abs(point["level_cents"]-floor)
            time_error = abs(point["minutes_to_bell"]-mtb)
            row.update(floors={"q50": dict(level_cents=point["level_cents"], minutes_to_bell=point["minutes_to_bell"])},
                actual_floor_cents=floor, actual_floor_mtb=mtb,
                floor_absolute_error_cents=error, floor_within_2_cents=error <= 2,
                floor_timing_absolute_error_minutes=time_error,
                floor_timing_within_0_10_minutes=time_error <= .10,
                predicted_floor_already_past=point["minutes_to_bell"] > gate,
                family=dict(top=called.get("family"), probabilities={called.get("family"): 1.0}))
        else:
            result["status"] = "PARTIAL_OR_NO_CALL: numerical null unavailable on one or both sides"
        result["sides"][side] = row
    if all(row["status"] == "OK" for row in result["sides"].values()):
        result["joint_floor_hit"] = all(r["floor_within_2_cents"] for r in result["sides"].values())
    return clean(result)


def volume_likelihood(member_delta, query_delta):
    if np.any(np.isfinite(member_delta) & (member_delta < 0)) or (np.isfinite(query_delta) and query_delta < 0):
        raise ValueError("NEGATIVE_GATE_VOLUME: no clipping or invented size")
    return 1/(1+np.abs(np.log1p(member_delta)-np.log1p(query_delta)))


def simulate(query, pairs, families, volume_mode="separate-log1p", include_paths=False, model=None):
    members, w0 = initial_pool(query, pairs)
    output = dict(event_id=query.event_id, first_tick=dict(epoch=query.first_epoch,
        fav_first=query.first[0], dog_first=query.first[3], mtb_first=query.first_mtb,
        favorite=query.legs[0].leg_id, underdog=query.legs[1].leg_id,
        discovery_sides=["LEADER" if x >= 50 else "UNDERDOG" for x in query.first[[0, 3]]]),
        initial_count=len(members), initial_ess=ess(w0) or 0, gates={})
    if not members:
        for gate in GATES:
            output["gates"][str(gate)] = dict(status="SCORABLE" if query.scorable(gate) else "EXCLUDED: no true trade before and after on both sides",
                recognition=first_bind(query, gate),
                rules={rule: dict(status="NO-CALL: no walk-forward members", ess=0) for rule in RULES})
            if model and query.scorable(gate):
                output["gates"][str(gate)]["rules"]["TAXONOMY-NULL"] = null_forecast(query, gate, model)
        return clean(output)
    n = len(members)
    logs = {key: np.log(w0) for key in ("SOFT", "STEP-FORECAST")}
    hard = w0.copy()
    ticks = query.grid()
    tick_pos = 0
    previous = None
    volume_origin = query.first_mtb
    volume_query = query.first[7]
    volume_members = np.array([m.levels([volume_origin])[0, 7] for m in members])
    missing_updates = Counter()
    for gate in GATES:
        if gate > query.first_mtb:
            output["gates"][str(gate)] = dict(status="EXCLUDED: before first_tick")
            continue
        stop = int(np.searchsorted(-ticks, -gate, side="right"))
        gate_price_log = np.zeros(n)
        if volume_mode == "separate-log1p":
            # A memory block is only an execution detail, not a sampling grid.
            for lo in range(tick_pos, stop, 256):
                clock = ticks[lo:min(lo+256, stop)]
                q = query.levels(clock)
                m = np.array([p.levels(clock) for p in members])
                usable = np.all(np.isfinite(m), axis=2) & np.all(np.isfinite(q), axis=1)[None, :]
                usable &= np.array([p.first_mtb for p in members])[:, None] >= clock[None, :]
                distances = np.abs(m[:, :, :7]-q[None, :, :7]).mean(axis=2)
                # Sequential accumulation preserves tick order and bitwise determinism.
                for col in range(len(clock)):
                    present = usable[:, col]
                    d = distances[:, col]
                    logs["SOFT"][present] -= np.log1p(d[present])
                    gate_price_log[present] -= np.log1p(d[present])
                    active = present & (hard > 0)
                    if np.any(active):
                        median = inverse_weighted_quantile(d[active], hard[active], .50)
                        hard[active & (d > median)] = 0
                    missing_updates["member_tick_unavailable"] += int(np.count_nonzero(~present))
        tick_pos = stop
        current = query.levels([gate])[0]
        member_current = np.array([p.levels([gate])[0] for p in members])
        volume_available = np.isfinite(volume_members) & np.isfinite(member_current[:, 7])
        volume_available &= np.array([p.first_mtb for p in members]) >= volume_origin
        k_vol = np.ones(n)
        k_vol[volume_available] = volume_likelihood(member_current[volume_available, 7]-volume_members[volume_available], current[7]-volume_query)
        logs["SOFT"] += np.log(k_vol)
        hard *= k_vol
        validity = dict(status="NO_PREVIOUS_GATE", weighted_share=None)
        step_price = np.ones(n)
        if previous is not None and volume_mode == "separate-log1p":
            error = np.abs((member_current-previous["members"]) - (current-previous["query"]))
            valid = np.all(np.isfinite(error), axis=1) & previous["available"]
            prior_weights = previous["weights"] * valid
            good = (error[:, 0] <= 1) & (error[:, 3] <= 1)
            denominator = prior_weights.sum()
            validity = dict(status="OK" if denominator > 0 else "STORE_SILENT: no comparable forecasts",
                previous_gate=previous["gate"], weighted_share=float(prior_weights[good].sum()/denominator) if denominator > 0 else None,
                weight_sum=float(denominator), ess=ess(prior_weights) or 0,
                rule="pre-update forecast weights; both last-price move errors <= 1 cent")
            step_price[valid] = 1/(1+error[valid, :7].sum(axis=1))
            logs["STEP-FORECAST"][valid] += np.log(step_price[valid])
        logs["STEP-FORECAST"] += np.log(k_vol)
        base_sides = np.array([[(leg >= 50) for leg in p.first[[0, 3]]] for p in members])
        base_weights = np.all(base_sides == (query.first[[0, 3]] >= 50), axis=1).astype(float)
        weights = {"SOFT": relative_weights(logs["SOFT"]), "HARD": hard,
                   "STEP-FORECAST": relative_weights(logs["STEP-FORECAST"]),
                   "FIRST-TICK-ONLY": w0, "BASE": base_weights}
        roles = query.roles(gate)
        pair_available = np.array([p.first_mtb >= gate and all(roles[i] == "NOT_CALLABLE" or p.roles(gate)[i] == roles[i] for i in range(2)) for p in members])
        gate_result = dict(status="SCORABLE" if query.scorable(gate) else "EXCLUDED: no true trade before and after on both sides",
            minutes_to_bell=gate, live_coordinates=gate_coordinates(query, gate),
            recognition=first_bind(query, gate), validity=validity,
            hard_count=int(np.count_nonzero(hard)), hard_count_status="COMPUTED",
            likelihood_factors=dict(volume_interval_from_mtb=volume_origin,
                k_volume=distribution(k_vol[volume_available]), volume_members_observed=int(volume_available.sum()),
                soft_log_k_price=distribution(gate_price_log), step_k_price=distribution(step_price),
                hard_k_price="median-distance survival indicator; volume weights applied once per gate"), rules={})
        context = forecast_context(query, members, gate)
        for rule in RULES:
            if rule == "TAXONOMY-NULL":
                gate_result["rules"][rule] = null_forecast(query, gate, model) if model and gate_result["status"] == "SCORABLE" else dict(status=gate_result["status"])
                continue
            w = weights[rule]
            if gate_result["status"] != "SCORABLE":
                gate_result["rules"][rule] = dict(status=gate_result["status"], ess=ess(w) or 0)
                continue
            pred = forecast(query, members, w, gate, families, include_paths, context)
            pred["weight_normalization"] = dict(
                kind="relative to maximum log weight" if rule in logs else "absolute multiplicative weights",
                log_scale_removed=float(np.max(logs[rule])) if rule in logs else 0)
            if gate == 1440:
                ranking = sorted(range(n), key=lambda j: (-w[j], members[j].event_id))
                pred["top_20_survivors"] = [dict(event_id=members[j].event_id, weight=float(w[j]),
                    realized_families=[leg.family for leg in members[j].legs],
                    eligible_sides={side: bool(context["masks"][i][j]) for i, side in enumerate(SIDES)},
                    realized_floor_cents=[float(np.nanmin(leg.values[:, 0])) for leg in members[j].legs]) for j in ranking[:20] if w[j] > 0]
            gate_result["rules"][rule] = pred
        next_gates = [g for g in GATES if g < gate]
        if next_gates and volume_mode == "separate-log1p":
            next_gate = next_gates[0]
            moves = np.array([p.levels([next_gate])[0]-member_current[j] for j, p in enumerate(members)])
            sw = weights["STEP-FORECAST"] * pair_available
            available = np.all(np.isfinite(moves), axis=1) & (sw > 0)
            step_ess = ess(sw*available) or 0
            gate_result["next_step_forecast"] = dict(next_gate_minutes_to_bell=next_gate, ess=step_ess,
                status="OK" if step_ess >= 10 else "NO-CALL: ESS < 10",
                delta_quantiles={f"q{int(q*100)}": v.tolist() for q, v in quantile_cube(moves[available, None, :], sw[available]).items()} if step_ess >= 10 else None)
        output["gates"][str(gate)] = gate_result
        previous = dict(gate=gate, query=current, members=member_current,
                        weights=weights["STEP-FORECAST"]*pair_available,
                        available=np.all(np.isfinite(member_current), axis=1)&pair_available)
        volume_origin, volume_query, volume_members = gate, current[7], member_current[:, 7]
    output["availability_counts"] = dict(missing_updates)
    return clean(output)


def numeric_leaves(value, prefix=""):
    for key, item in value.items():
        name = f"{prefix}.{key}" if prefix else key
        if isinstance(item, dict):
            yield from numeric_leaves(item, name)
        elif isinstance(item, (int, float, bool)) and item is not None:
            yield name, float(item)


def new_cell():
    return dict(queries=0, statuses=Counter(), values=defaultdict(list),
                family_confusion={s: defaultdict(Counter) for s in (*SIDES, "pair")},
                family_log_loss={s: [] for s in (*SIDES, "pair")}, family_missing=Counter())


def add_cell(cell, result):
    cell["queries"] += 1
    cell["statuses"][result["status"]] += 1
    for name, value in numeric_leaves(result):
        if not any(key in name for key in ("family.probabilities", "floors.q", "actual_floor", "realized")):
            cell["values"][name].append(value)
    for side in (*SIDES, "pair"):
        row = result.get("sides", {}).get(side, {}) if side != "pair" else dict(status=result["status"], family=result.get("pair_family", {}), realized_family=result.get("realized_pair_family"))
        family = row.get("family", {})
        top, truth = family.get("top"), row.get("realized_family")
        if top and truth and row.get("status") == "OK":
            cell["family_confusion"][side][truth][top] += 1
            prob = family["probabilities"].get(truth, 0)
            cell["family_log_loss"][side].append(-math.log(prob) if prob > 0 else math.inf)
        else:
            cell["family_missing"][side] += 1


def finish_cell(cell):
    stats = {}
    for name, values in cell["values"].items():
        if not values:
            continue
        stats[name] = dict(n=len(values), mean=float(np.mean(values)), median=float(np.median(values)))
        if ".coverage.q25_q75." in name or name == "joint_path_coverage.q25_q75":
            stats[name]["gap_from_50_percent"] = stats[name]["mean"]-.50
        if ".coverage.q10_q90." in name or name == "joint_path_coverage.q10_q90":
            stats[name]["gap_from_80_percent"] = stats[name]["mean"]-.80
    families = {}
    for side in (*SIDES, "pair"):
        matrix = cell["family_confusion"][side]
        total = sum(sum(v.values()) for v in matrix.values())
        losses = cell["family_log_loss"][side]
        families[side] = dict(denominator=total, unscorable=cell["family_missing"][side],
            accuracy=sum(v.get(k, 0) for k, v in matrix.items())/total if total else None,
            log_loss="INF" if any(math.isinf(v) for v in losses) else float(np.mean(losses)) if losses else None,
            confusion={a: dict(b) for a, b in matrix.items()},
            status="OK" if total else "STORE_SILENT: no scored family calls")
    return dict(queries=cell["queries"], statuses=dict(cell["statuses"]), metrics=stats, family=families)


def score_denominators():
    return dict(
        errors="Path/floor errors and family accuracy use their own called-side or called-pair denominators; NO-CALL is not a zero prediction error.",
        conditional_utility="Existing pair_reach metrics retain their conditional-on-pair-call means and n.",
        eligible_utility="eligible_query_utility adds mean * called n / scorable_queries for pair reach and discount. A NO-CALL issues no bid and contributes zero reach/discount; it stays distinct from NOT_POSTABLE.",
        point_null="TAXONOMY-NULL has no evaluated bid/reach model, so its utility stays undefined rather than zero.")


def add_eligible_utility(scoreboard):
    """Reporting only: preserve all predictions and conditional metric values."""
    for category in scoreboard["categories"].values():
        for gate in category["gates"].values():
            eligible = gate["scorable_queries"]
            for rule, cell in gate.get("rules", {}).items():
                called = cell["statuses"].get("OK", 0)
                if not 0 <= called <= eligible:
                    raise ValueError("INVALID_CALLED_QUERY_DENOMINATOR")
                utility = dict(eligible_queries=eligible, called_pair_queries=called,
                    no_call_or_partial_queries=eligible-called,
                    status="OK" if eligible else "NO_SCORABLE_QUERIES")
                for quantile in ("q25", "q50"):
                    if rule == "TAXONOMY-NULL":
                        utility[quantile] = None
                        utility["status"] = "NOT_EVALUATED_FOR_POINT_NULL"
                        continue
                    prefix = "pair_reach."+quantile+"."
                    discount = cell["metrics"].get(prefix+"expected_pair_discount_contribution", {})
                    reach = cell["metrics"].get(prefix+"reached", {})
                    if discount.get("n", 0) != called or reach.get("n", 0) != called:
                        raise ValueError("UTILITY_CALL_DENOMINATOR_MISMATCH:"+rule)
                    discount_total = discount["mean"]*called if called else 0.0
                    reached_total = reach["mean"]*called if called else 0.0
                    utility[quantile] = dict(
                        discount_cents_per_called_pair=discount.get("mean"),
                        discount_cents_per_eligible_query=discount_total/eligible if eligible else None,
                        pair_reach_rate_per_called_pair=reach.get("mean"),
                        pair_reach_rate_per_eligible_query=reached_total/eligible if eligible else None,
                        formula="conditional mean * called_pair_queries / eligible_queries")
                cell["eligible_query_utility"] = utility
    return scoreboard


def summarize(scoreboard):
    def number(x):
        return "—" if x is None else f"{x:.3f}"
    def get(cell, key, stat="mean"):
        return cell.get("metrics", {}).get(key, {}).get(stat)
    out = ["# " + scoreboard["label"], "", "No selection, no trading ruling. Minute-book reach is diagnostic only.", "",
           "Error means are conditional on called sides. Utility shows both called-pair and all-eligible-query denominators; NO-CALL contributes zero only to reach/discount utility. These are not matched-cohort comparisons.", ""]
    for category, section in scoreboard["categories"].items():
        out += [f"## {category}", ""]
        for level, key in (("MACRO — favorite / underdog last-path MAE", "path_last_mae_cents"),
                           ("MICRO — floor MAE / median absolute error, favorite then underdog", "floor_absolute_error_cents"),
                           ("MICRO-MICRO — q50 pair reach × discount, per called pair / per eligible query", None)):
            out += [f"### {level}", "", "| Rule | " + " | ".join(map(str, GATES)) + " |",
                    "|---|" + "---|"*len(GATES)]
            for rule in RULES:
                cols = []
                for gate in GATES:
                    cell = section["gates"].get(str(gate), {}).get("rules", {}).get(rule, {})
                    if not cell:
                        cols.append("—")
                    elif key is None:
                        companion = (cell.get("eligible_query_utility", {}).get("q50") or {}).get("discount_cents_per_eligible_query")
                        cols.append(number(get(cell, "pair_reach.q50.expected_pair_discount_contribution"))+" / "+number(companion))
                    else:
                        vals = [number(get(cell, f"sides.{side}.{key}")) for side in SIDES]
                        if key == "floor_absolute_error_cents":
                            vals = [v+"/"+number(get(cell, f"sides.{side}.{key}", "median")) for side, v in zip(SIDES, vals)]
                        cols.append(" ; ".join(vals))
                out.append("| " + rule + " | " + " | ".join(cols) + " |")
            out.append("")
        out += ["### Call coverage / initial-pool ESS", "", "| Gate (minutes to bell) | Eligible | Initial ESS median | BASE pair calls |", "|---:|---:|---:|---:|"]
        for gate in GATES:
            row = section["gates"].get(str(gate), {})
            base = row.get("rules", {}).get("BASE", {})
            out.append(f"| {gate} | {row.get('scorable_queries', 0)} | {number(section['initial_ess']['q50'])} | {base.get('statuses', {}).get('OK', 0)} |")
        out.append("")
        out += ["### Per-side call denominators — favorite / underdog", "",
                "| Gate | Eligible pairs | " + " | ".join(RULES) + " |",
                "|---:|---:|" + "---|"*len(RULES)]
        for gate in GATES:
            row = section["gates"].get(str(gate), {})
            cells = []
            for rule in RULES:
                metrics = row.get("rules", {}).get(rule, {}).get("metrics", {})
                cells.append(" / ".join(str(metrics.get(f"sides.{side}.floor_absolute_error_cents", {}).get("n", 0)) for side in SIDES))
            out.append("| " + " | ".join([str(gate), str(row.get("scorable_queries", 0)), *cells]) + " |")
        out.append("")
    out += ["## Declared limits", ""] + ["- " + line for line in scoreboard["limitations"]]
    return "\n".join(out)+"\n"


_WORKER_DATA = None


def init_worker(pairs, families, volume_mode, model):
    global _WORKER_DATA
    _WORKER_DATA = (pairs, {p.event_id: p for p in pairs}, families, volume_mode, model)


def worker_query(event_id):
    pairs, lookup, families, mode, model = _WORKER_DATA
    return simulate(lookup[event_id], pairs, families, mode, model=model)


def build_outputs(args):
    root = Path(__file__).resolve().parents[2]
    prior_art, labels, families = bind_prior_art(root)
    pairs, census = load_library(args.library, labels)
    thresholds, count_receipt = attach_print_counts(pairs, args.print_count_cache, args.library)
    family_census = label_pairs(pairs, thresholds)
    model = bind_numerical_null(root, prior_art)
    started = time.monotonic()
    limitations = [
        "The supplied proof library ends 2026-05-01, so this is proof of execution, not evidence for a July trading ruling.",
        "Prior trendpath used first-hour-median discovery and flow onset; the operator explicitly replaces both with first true-traded pair discovery and bell slices, and replaces count thresholds with ESS < 10.",
        "The two taxonomy bench choices are operator-authorized: SLEEPER below category p10 actual trade counts; absolute net after first quarter <=2c for flat-after. Category p10 is retrospective full-library scale, not walk-forward calibration.",
        "The fixed July family/depth tables are a requested retrospective null, not out-of-sample calibration on the June-era proof. Its family call uses only the observed gate prefix, never the query's realized future family.",
        "Exact print counts are joined from the bound source parquet. June paths still lack canonical onsets; corresponding live coordinates stay null, never formation relabelled as onset.",
        "First_tick means the first causal state at which both legs have traded since formation, not a requirement for simultaneous trades. Orientation is by the two first_tick prices; equal prices are excluded.",
        "Role-open is separate from pool discovery: library postformation_open_cents when supplied, otherwise its filed anchor_cents; named checks use the filed truth-table postformation open. Neither is replaced by a later first-trade price.",
        "Member missing observations cause no weight update, not a fabricated tick or death; the member stays in the original pool and can forecast only when its clock is observed. Reported availability counts distinguish this.",
        "Seven price coordinates stay in cents. Volume is a separate log1p likelihood on pair contract-volume increments over each gate interval; no contracts enter the cents distance.",
        "SOFT updates the seven-price likelihood at every stored tick; volume is multiplied once per completed gate interval. HARD keeps its median-price kill rule (binary price factor) and applies the separate volume factor once per gate; no extra soft-price rule is added to HARD.",
        "The role-only null has filed depth but no unique numeric early/late timing scalar. Such timing stays silent; family-null rows use their exact published medians, even if that predicted floor lies before the query gate.",
        "Literal tau-to-minutes replacement retains ORDER4's 0.10 tolerance as 0.10 minutes; absolute timing errors in minutes are primary.",
        "ORDER4 reach uses the running low after placement, which can retain a past dip. A separate future_print_reached flag exposes that; neither minute path metric certifies a maker fill.",
        "No full-worktree OS, builder, shape-organ or face edits are made; this tool reads only explicit library and named-check inputs.",
    ]
    output = dict(label=LABEL if args.proof else "BELL-CLOCK SURVIVORSHIP BENCH — NOT A TRADING RULING",
                  categories={}, limitations=limitations, prior_art=prior_art)
    query_audit = {}
    for category in args.categories:
        queries = [p for p in pairs if p.category == category]
        cells = {str(g): {r: new_cell() for r in RULES} for g in GATES}
        status = {str(g): Counter() for g in GATES}
        recognition = {str(g): new_cell() for g in GATES}
        initials = []
        if args.limit_queries:
            queries = queries[:args.limit_queries]
        executor = None
        if args.workers > 1:
            executor = ProcessPoolExecutor(max_workers=args.workers, initializer=init_worker,
                initargs=(pairs, families, args.volume_mode, model))
            results = executor.map(worker_query, [q.event_id for q in queries], chunksize=1)
        else:
            results = (simulate(q, pairs, families, args.volume_mode, model=model) for q in queries)
        for j, (query, result) in enumerate(zip(queries, results)):
            initials.append(result["initial_ess"])
            audit = dict(initial_count=result["initial_count"], initial_ess=result["initial_ess"], gates={})
            for gate, row in result["gates"].items():
                status[gate][row["status"]] += 1
                audit["gates"][gate] = {rule: dict(status=pred["status"], ess=pred.get("ess"),
                    side_ess={s: p.get("ess") for s, p in pred.get("sides", {}).items()}) for rule, pred in row.get("rules", {}).items()}
                audit["gates"][gate]["likelihood_factors"] = row.get("likelihood_factors")
                if row["status"] == "SCORABLE":
                    for rule, pred in row["rules"].items():
                        add_cell(cells[gate][rule], pred)
                    rec = dict(status="OK", sides=row["recognition"])
                    add_cell(recognition[gate], rec)
            query_audit[query.event_id] = audit
            if (j+1) % 25 == 0 or j+1 == len(queries):
                print(f"{category} {j+1}/{len(queries)} queries; {time.monotonic()-started:.1f}s", flush=True)
        if executor:
            executor.shutdown(wait=True)
        category_output = dict(query_count=len(queries), initial_ess=distribution(initials), gates={})
        for gate in GATES:
            key = str(gate)
            scorable = status[key].get("SCORABLE", 0)
            wta_silent = category.startswith("WTA") and scorable < 200
            category_output["gates"][key] = dict(scorable_queries=scorable,
                exclusions=dict(status[key]),
                status="STORE_SILENT: WTA scorable count < 200" if wta_silent else "OK",
                recognition=finish_cell(recognition[key]),
                rules={r: finish_cell(cell) for r, cell in cells[key].items()} if not wta_silent else {})
        output["categories"][category] = category_output
    named = dict(label=output["label"], prior_art=prior_art, events={}, input_receipt={})
    if not args.skip_named:
        named_pairs, provenance = load_named_inputs(root, labels, args.tape_dir, args.prints)
        label_pairs(named_pairs, thresholds)
        named["input_receipt"] = provenance
        for q in named_pairs:
            print(f"named {q.event_id}", flush=True)
            named["events"][q.event_id.split("-")[-1]] = simulate(q, pairs, families, args.volume_mode, args.named_paths, model)
    receipt = dict(label=output["label"], prior_art=prior_art,
        input_library=dict(path=str(args.library), bytes=args.library.stat().st_size, sha256=sha256_file(args.library)),
        source_receipt=dict(path=str(args.library_receipt), sha256=sha256_file(args.library_receipt)),
        script_sha256=sha256_file(Path(__file__)),
        inherited_helpers=dict(path="arb-executor/analysis/tune_bench_floor_calls.py", sha256=sha256_file(Path(__file__).with_name("tune_bench_floor_calls.py")),
                               functions=["sha256_file", "stable_json", "distribution", "inverse_weighted_quantile", "ess"]),
        gates_minutes_to_bell=GATES, series=SERIES, categories=args.categories,
        selected_query_limit=args.limit_queries, volume_mode=args.volume_mode,
        census=census, family_census=family_census, exact_print_counts=count_receipt,
        walk_forward="member.bell_epoch < query.formation_end_epoch; leave-self-out; exclude same event_date; category separate; no distance/count cutoff. Fixed retrospective taxonomy-scale/null calibration is disclosed separately, not claimed walk-forward.",
        clock="Reconstruct each leg's epoch from its own formation/bell fraction, align both by their common bell; reject discordant bells. Sample largest member epoch <= bell - minutes_to_bell*60.",
        units=dict(price="cents; seven-series price likelihood only", volume="log1p(pair contracts accumulated over gate)",
            engine_transform=dict(field="volume_log1p", declaration="SIMILARITY_DECLARATION",
                path="arb-executor/analysis/window1_v54_functionable_os.js", sha256=sha256_file(root/"arb-executor/analysis/window1_v54_functionable_os.js")),
            k_price_soft="1/(1+mean absolute seven-price level difference), multiplied in tick order",
            k_price_step="1/(1+sum absolute errors of seven-price gate-to-next-gate moves)",
            k_volume="1/(1+abs(log1p(delta_volume_member)-log1p(delta_volume_query)))",
            application="SOFT and STEP weights multiply distinct k_price and k_volume factors; HARD price gate is its inherited binary median-distance selector; no engine similarity weight/scale is copied into either formula"),
        w0="1/(1+abs(delta_fav_first)+abs(delta_dog_first)) * 1/(1+abs(delta_mtb_first)/query.mtb_first)",
        rules=dict(SOFT="seven-price tick likelihood product times separate gate-volume factor",
                   HARD="drop if contemporaneous mean seven-price distance exceeds weighted median among available surviving members; ties stay; w0 times prior gate-volume factors",
                   STEP_FORECAST="at next gate multiply seven-price move-error likelihood and separate log-volume likelihood; VALIDITY uses frozen pre-update forecast weights and both lasts within 1 cent",
                   FIRST_TICK_ONLY="w0 unchanged", BASE="all category+discovery-oriented eligible members weight 1; same role gate",
                   role="last - postformation_open >=2 CLIMBER, <=-2 FALLER; otherwise NOT_CALLABLE and bypass role filter"),
        no_call="ESS < 10 after role/availability filter, counted explicitly with separate denominators; never replace with a different pool",
        score_denominators=score_denominators(),
        determinism="fixed event_id/timestamp order; exact inverse weighted CDF; no randomness or runtime stamps in artifacts; --verify-repeat byte-compares both builds",
        limitations=limitations)
    output["query_set_audit"] = query_audit
    add_eligible_utility(output)
    args.out.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, data in (("SCOREBOARD", output), ("RECEIPT", receipt), ("NAMED_CHECKS", named)):
        path = args.out/f"TUNE_BENCH_{name}.json"
        if name == "SCOREBOARD":
            # Compact serialization keeps the full per-query audit below repository file limits.
            path.write_text(json.dumps(clean(data), sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n", encoding="utf-8", newline="\n")
        else:
            stable_json(path, clean(data))
        paths[name] = path
    summary = args.out/"TUNE_BENCH_SUMMARY.md"
    summary.write_text(summarize(output), encoding="utf-8", newline="\n")
    paths["SUMMARY"] = summary
    return paths


def self_test():
    values = np.array([[[0, 12.5]], [[2, 80000]], [[1, 4.0]]])
    w = np.array([1., 2., 1.])
    for q, vals in quantile_cube(values, w).items():
        for col in range(2):
            assert vals[0, col] == inverse_weighted_quantile(values[:, 0, col], w, q)
    integer = np.arange(800).reshape(20, 20, 2) % 7
    for q, vals in quantile_cube(integer, np.ones(20)).items():
        for i in range(20):
            for j in range(2):
                assert vals[i, j] == inverse_weighted_quantile(integer[:, i, j], np.ones(20), q)
    assert role(2) == "CLIMBER" and role(-2) == "FALLER" and role(1) == "NOT_CALLABLE"
    assert ess(np.ones(10)) == 10
    np.testing.assert_allclose(relative_weights(np.array([-10000., -10001.])), [1, math.exp(-1)])
    # Synthetic fixtures exercise mechanics, never filed-game calibration.
    from datetime import timedelta, timezone
    def fixture(event, start_date, future_shift=0, volume_scale=1):
        formation = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc).timestamp()
        offsets = np.array([0, 100, 560, 920, 1280, 1640, 1760, 1880,
                            1940, 1970, 1985, 1995, 1999], dtype=float)
        epoch = formation + offsets * 60
        favorite = np.array([60, 60, 62, 64, 61, 63, 65, 64, 66, 65, 67, 66, 65], dtype=float)
        favorite[offsets > 560] += future_shift
        legs = []
        for i, prices in enumerate((favorite, 100-favorite)):
            counts = np.arange(1, len(epoch)+1, dtype=float)
            leg = Leg(str(i), float(prices[0]), formation, formation+2000*60,
                      epoch.copy(), np.column_stack((prices, prices-1, prices+1)),
                      counts*volume_scale, epoch.copy(), np.minimum.accumulate(prices),
                      "DRIFT_UP" if i == 0 else "DRIFT_DOWN", onset=formation,
                      trade_count=counts.copy(), postformation_open=float(prices[0]),
                      trade_price=prices.copy(), count_epoch=epoch.copy(),
                      print_count_cum=counts.copy())
            leg.sleeper_threshold = 0.0
            legs.append(leg)
        return Pair(event, "ATP_MAIN", start_date, tuple(legs), formation,
                    "SYNTHETIC_TRUE_PRINT_AND_BOOK")
    query = fixture("SYNTHETIC-QUERY", "2026-08-01")
    members = [fixture(f"SYNTHETIC-MEMBER-{i:02d}",
                       (datetime(2026, 7, 1)+timedelta(days=i)).date().isoformat())
               for i in range(24)]
    test_families = ["SLEEPER", "ROUND_TRIP", "QUIET_WOBBLE"] + [
        name+"_"+direction for name in ("LATE_BREAK", "EARLY_SET", "ONE_STEP",
                                      "GRIND_WOBBLE", "DRIFT")
        for direction in ("UP", "DOWN")]
    gate = 1440
    # Count identities, not changed prices: the second true print repeats 60.
    assert taxonomy_print_count(query.legs[0]) == 13
    assert taxonomy_print_count(query.legs[0], query.formation+100*60) == 2
    assert taxonomy_print_count(query.legs[0], query.formation-1) == 0
    coordinates = gate_coordinates(query, gate)
    assert coordinates["favorite"]["post_onset_trade_count"] == 3
    assert coordinates["favorite"]["cumulative_absolute_travel_cents"] == 2
    # The call boundary applies to family scores, not only path forecasts.
    below = forecast(query, members[:9], np.ones(9), gate, test_families)
    cell = new_cell()
    add_cell(cell, below)
    summary = finish_cell(cell)
    assert below["status"].startswith("NO-CALL")
    assert all(summary["family"][side]["denominator"] == 0 for side in (*SIDES, "pair"))
    boundary = forecast(query, members[:10], np.ones(10), gate, test_families)
    cell = new_cell()
    add_cell(cell, boundary)
    summary = finish_cell(cell)
    assert boundary["status"] == "OK"
    assert all(summary["family"][side]["denominator"] == 1 for side in (*SIDES, "pair"))

    # Two callable side pools can still have a non-callable intersection.
    split_members = [fixture(f"SYNTHETIC-SPLIT-{i:02d}", member.date)
                     for i, member in enumerate(members)]
    for i, member in enumerate(split_members[:20]):
        side, shift = (1, 1) if i < 10 else (0, -1)
        member.legs[side].values[2] += shift
        member.legs[side].trade_price[2] += shift
    split = forecast(query, split_members, np.ones(24), gate, test_families)
    assert all(split["sides"][side]["ess"] == 14 for side in SIDES)
    assert split["shared"]["ess"] == 4
    cell = new_cell()
    add_cell(cell, split)
    summary = finish_cell(cell)
    assert all(summary["family"][side]["denominator"] == 1 for side in SIDES)
    assert summary["family"]["pair"]["denominator"] == 0

    # A shared immutable gate context is identical to fresh sampling.
    weights = np.linspace(1, 2, len(members))
    fresh = forecast(query, members, weights, gate, test_families, include_paths=True)
    context = forecast_context(query, members, gate)
    cached = forecast(query, members, weights, gate, test_families,
                      include_paths=True, context=context)
    assert cached == fresh
    remainder_identity = id(context["remainder"])
    assert forecast(query, members, weights, gate, test_families,
                    include_paths=True, context=context) == fresh
    assert id(context["remainder"]) == remainder_identity

    # Volume is an independent dimensionless likelihood, never a cents term.
    deltas = np.array([0.0, 3.0, 8.0])
    expected = 1/(1+np.abs(np.log1p(deltas)-math.log1p(3.0)))
    np.testing.assert_allclose(volume_likelihood(deltas, 3.0), expected, rtol=0, atol=0)
    assert volume_likelihood(np.array([3.0]), 3.0)[0] == 1
    for member_delta, query_delta in ((np.array([-1.0]), 0.0), (np.array([0.0]), -1.0)):
        try:
            volume_likelihood(member_delta, query_delta)
        except ValueError as error:
            assert "NEGATIVE_GATE_VOLUME" in str(error)
        else:
            raise AssertionError("negative gate volume must fail, never clip")

    model = dict(family_rows={(name, "ATP_MAIN"): dict(
        legs=24, depth_below_open_c=dict(med=5.0), floor_pos=dict(med=.5))
        for name in test_families}, faller_depth={"ATP_MAIN": 8.67})
    original = simulate(query, members, test_families, model=model)
    changed = fixture("SYNTHETIC-QUERY", "2026-08-01", future_shift=-8)
    mutated = simulate(changed, members, test_families, model=model)
    original_gate = original["gates"][str(gate)]
    mutated_gate = mutated["gates"][str(gate)]
    # Future prints may change realized evaluation, but no frozen forecast,
    # gate likelihood, membership, role or causal called family at this gate.
    assert original["first_tick"] == mutated["first_tick"]
    assert original_gate["likelihood_factors"] == mutated_gate["likelihood_factors"]
    assert original_gate["validity"] == mutated_gate["validity"]
    assert original_gate["hard_count"] == mutated_gate["hard_count"]
    assert original_gate["next_step_forecast"] == mutated_gate["next_step_forecast"]
    for rule in RULES:
        for side in SIDES:
            before = original_gate["rules"][rule]["sides"][side]
            after = mutated_gate["rules"][rule]["sides"][side]
            assert before["ess"] == after["ess"]
            assert before["floors"] == after["floors"]
            if rule == "TAXONOMY-NULL":
                assert before["called_family"] == after["called_family"]
                assert before["null_point"] == after["null_point"]
            else:
                assert before["role"] == after["role"]
                assert before["family"] == after["family"]
    assert (original_gate["rules"]["BASE"]["sides"]["favorite"]["actual_floor_cents"]
            != mutated_gate["rules"]["BASE"]["sides"]["favorite"]["actual_floor_cents"])

    extra_volume = fixture("SYNTHETIC-QUERY", "2026-08-01", volume_scale=2)
    volume_run = simulate(extra_volume, members, test_families, model=model)
    factors = volume_run["gates"][str(gate)]["likelihood_factors"]
    assert factors["soft_log_k_price"]["mean"] == 0
    assert factors["step_k_price"]["mean"] == 1
    expected_volume = float(volume_likelihood(np.array([4.0]), 8.0)[0])
    assert math.isclose(factors["k_volume"]["mean"], expected_volume, rel_tol=1e-14)
    assert factors["k_volume"]["mean"] < 1

    # Same-day, same-event, future-bell and cross-category members never leak in.
    same_day = fixture("SYNTHETIC-SAME-DAY", "2026-07-01")
    same_day.date = query.date
    future = fixture("SYNTHETIC-FUTURE", "2026-08-02")
    other_category = fixture("SYNTHETIC-OTHER-CATEGORY", "2026-07-01")
    other_category.category = "ATP_CHALL"
    selected, initial_weights = initial_pool(query, members+[query, same_day, future, other_category])
    assert [member.event_id for member in selected] == [member.event_id for member in members]
    np.testing.assert_array_equal(initial_weights, np.ones(len(members)))
    # Windows spawn and worker-count changes preserve deterministic output bytes.
    worker_pairs = members+[query]
    direct = simulate(query, worker_pairs, test_families, model=model)
    direct_bytes = json.dumps(direct, sort_keys=True, separators=(",", ":")).encode("utf-8")
    for worker_count in (1, 2):
        with ProcessPoolExecutor(max_workers=worker_count, initializer=init_worker,
                initargs=(worker_pairs, test_families, "separate-log1p", model)) as executor:
            worker_results = list(executor.map(worker_query, [query.event_id, query.event_id]))
        for result in worker_results:
            result_bytes = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
            assert result_bytes == direct_bytes
    utility_metrics = {}
    for q in ("q25", "q50"):
        utility_metrics[f"pair_reach.{q}.expected_pair_discount_contribution"] = dict(n=24, mean=7/6)
        utility_metrics[f"pair_reach.{q}.reached"] = dict(n=24, mean=.5)
    utility_board = dict(categories=dict(ATP_MAIN=dict(gates={"2160": dict(scorable_queries=427, rules={
        "SOFT": dict(statuses=dict(OK=24), metrics=utility_metrics),
        "HARD": dict(statuses={}, metrics={}),
        "TAXONOMY-NULL": dict(statuses={}, metrics={})})})))
    add_eligible_utility(utility_board)
    utility_rows = utility_board["categories"]["ATP_MAIN"]["gates"]["2160"]["rules"]
    assert math.isclose(utility_rows["SOFT"]["eligible_query_utility"]["q50"]["discount_cents_per_eligible_query"], 28/427)
    assert utility_rows["SOFT"]["metrics"] == utility_metrics
    assert utility_rows["HARD"]["eligible_query_utility"]["q50"]["discount_cents_per_eligible_query"] == 0
    assert utility_rows["HARD"]["eligible_query_utility"]["q50"]["discount_cents_per_called_pair"] is None
    assert utility_rows["TAXONOMY-NULL"]["eligible_query_utility"]["q50"] is None
    print("SELF-TEST PASS: quantiles; exact counts; ESS/no-call family boundary; cached forecasts; separate price/volume factors; future-mutation causality; walk-forward exclusions; direct/1-worker/2-worker byte equality; eligible-query utility denominators", flush=True)


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=root/"arb-executor/data/durable/RANGE_OVERLAP_LIBRARY.jsonl.gz")
    parser.add_argument("--library-receipt", type=Path, default=root/"arb-executor/data/durable/RANGE_OVERLAP_LIBRARY_RECEIPT.json")
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("tune_bench_v2"))
    parser.add_argument("--categories", nargs="+", choices=CATEGORIES, default=list(CATEGORIES))
    parser.add_argument("--proof", action="store_true")
    parser.add_argument("--volume-mode", choices=("separate-log1p",), default="separate-log1p")
    parser.add_argument("--print-count-cache", type=Path, default=Path(r"C:\tmp\tune_bench_v2_print_counts.json.gz"))
    parser.add_argument("--minute-parquet", type=Path, help="local parquet to regenerate exact-count cache; requires pyarrow")
    parser.add_argument("--workers", type=int, default=1, help="execution parallelism only; aggregation remains event-id ordered")
    parser.add_argument("--tape-dir", type=Path, default=Path(r"C:\Users\omigr\OMI-Window1-private\fit-local\ticks"))
    parser.add_argument("--prints", type=Path, default=Path(r"C:\Users\omigr\OMI-Window1-private\fit-local\prints.jsonl"))
    parser.add_argument("--skip-named", action="store_true")
    parser.add_argument("--named-paths", action="store_true")
    parser.add_argument("--limit-queries", type=int, help="explicit smoke-test only, always disclosed; not the formal proof")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--verify-repeat", action="store_true")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    if args.self_test:
        self_test()
        return
    if args.proof and sha256_file(args.library) != "019d84b0500a79c5d762d95ae7f481c3ae9a5bd5f0818f81aea9207a27fdd76e":
        raise SystemExit("PROOF_LIBRARY_HASH_MISMATCH")
    if args.minute_parquet:
        build_print_count_cache(args.library, args.minute_parquet, args.print_count_cache)
    paths = build_outputs(args)
    first = {name: path.read_bytes() for name, path in paths.items()}
    for name, data in first.items():
        print(f"RUN1 {name} sha256 {hashlib.sha256(data).hexdigest()}", flush=True)
    if args.verify_repeat:
        repeated = build_outputs(args)
        for name, path in repeated.items():
            data = path.read_bytes()
            if data != first[name]:
                raise SystemExit(f"NONDETERMINISTIC {name}")
            print(f"RUN2 {name} sha256 {hashlib.sha256(data).hexdigest()} BYTE_IDENTICAL", flush=True)


if __name__ == "__main__":
    main()
