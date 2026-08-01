#!/usr/bin/env node
"use strict";

// Read-only diagnostic for the five-game quote-shape replay. It does not
// change a placement, assign a fill, or invoke a scorer.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { evaluateMicroPositionEvidence } = require("./window1_quote_shape_micro_position_v2.js");

const args = process.argv.slice(2);
const arg = (name, fallback) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
};
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const outDir = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_insufficient_diagnosis_20260801")));
const replayPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/FIVE_GAME_REPLAY.json");
const summaryPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/FIVE_GAME_SUMMARY.json");
const libraryPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/QUOTE_SHAPE_LIBRARY_LEAVE_FIVE_OUT.json");
const frozenFivePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const makerLawPath = path.join(repo, "arb-executor/analysis/window1_full_lawful_ceiling.py");
const takerLawPath = path.join(repo, "arb-executor/analysis/completion_census.py");
const replayBuilderPath = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
const microPositionPath = path.join(repo, "arb-executor/analysis/window1_quote_shape_micro_position_v2.js");
const DWELL_SECONDS = 10;
const QUANTITY = 5;
const PREFIX_KEYS = ["ask_net", "ask_dip", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "ask_dwell_fraction", "mean_log_top_ask_size", "mean_log_top5_ask_depth"];

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) throw new Error(`bad tick timestamp ${value}`);
  let hour = Number(m[4]);
  if (m[7] === "AM" && hour === 12) hour = 0;
  if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map((line, index) => ({ raw: Object.fromEntries(line.split(",").map((value, i) => [headers[i], value])), ordinal: index + 2 }));
}
function clocks(ts, source) {
  return {
    timestamp_epoch: ts,
    t_minus_scheduled_seconds: source.scheduled - ts,
    t_minus_actual_bell_seconds: source.bell - ts,
  };
}
function tMinus(seconds) {
  const sign = seconds >= 0 ? "T-" : "T+";
  const absolute = Math.abs(seconds);
  const minutes = Math.floor(absolute / 60);
  const remainder = absolute - minutes * 60;
  return `${sign}${minutes}:${String(remainder).padStart(2, "0")}`;
}

function loadRows(source) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  const bytes = fs.readFileSync(file);
  const rows = [];
  for (const { raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et);
    if (ts < source.left || ts > source.right) continue;
    const bids = [];
    const asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(raw[`bid_${level}`]);
      const bidSize = positive(raw[`bid_${level}_sz`]);
      const ask = integer(raw[`ask_${level}`]);
      const askSize = positive(raw[`ask_${level}_sz`]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]);
      if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    bids.sort((a, b) => b[0] - a[0]);
    asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({
      ts,
      ordinal,
      receipt: `${path.basename(file)}#row-${ordinal}`,
      bid: bids[0][0],
      ask: asks[0][0],
      spread: asks[0][0] - bids[0][0],
      top_bid_size: bids[0][1],
      top_ask_size: asks[0][1],
      top5_bid_depth: bids.reduce((sum, item) => sum + item[1], 0),
      top5_ask_depth: asks.reduce((sum, item) => sum + item[1], 0),
      bids,
      asks,
      carried_last: integer(raw.last_trade),
    });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  const formedIndex = rows.findIndex((row) => row.spread === 1);
  return {
    allRows: rows,
    shapeRows: formedIndex >= 0 ? rows.slice(formedIndex) : [],
    preformationRows: formedIndex < 0 ? rows.length : formedIndex,
    source: { file: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) },
  };
}

function prefixRows(rows, left, right) {
  let state = null;
  let firstAsk = null;
  let firstBookTs = null;
  let minAsk = null;
  let spreadMin = null;
  let spreadMax = null;
  let lastAskChange = null;
  let count = 0;
  let changes = 0;
  let askChangeAfterFirstTimestamp = false;
  let spreadIntegral = 0;
  let sizeIntegral = 0;
  let depthIntegral = 0;
  let observedDuration = 0;
  const output = [];
  function integrate(ts) {
    if (!state) return;
    const dt = Math.max(0, ts - state.integrated_to);
    spreadIntegral += state.spread * dt;
    sizeIntegral += Math.log1p(state.top_ask_size) * dt;
    depthIntegral += Math.log1p(state.top5_ask_depth) * dt;
    observedDuration += dt;
    state.integrated_to = ts;
  }
  for (const row of rows) {
    integrate(row.ts);
    if (!state) {
      firstAsk = row.ask;
      firstBookTs = row.ts;
      minAsk = row.ask;
      lastAskChange = row.ts;
      spreadMin = row.spread;
      spreadMax = row.spread;
    } else if (row.ask !== state.ask) {
      changes += 1;
      lastAskChange = row.ts;
      if (row.ts > firstBookTs) askChangeAfterFirstTimestamp = true;
    }
    minAsk = Math.min(minAsk, row.ask);
    spreadMin = Math.min(spreadMin, row.spread);
    spreadMax = Math.max(spreadMax, row.spread);
    count += 1;
    state = { ...row, integrated_to: row.ts };
    const elapsed = Math.max(1, row.ts - left);
    const observed = Math.max(1, observedDuration);
    const prefix = {
      ask_net: row.ask - firstAsk,
      ask_dip: minAsk - firstAsk,
      mean_spread: spreadIntegral / observed,
      spread_range: spreadMax - spreadMin,
      quote_rate: count * 3600 / elapsed,
      ask_change_rate: changes * 3600 / elapsed,
      ask_dwell_fraction: Math.max(0, row.ts - lastAskChange) / elapsed,
      mean_log_top_ask_size: sizeIntegral / observed,
      mean_log_top5_ask_depth: depthIntegral / observed,
    };
    output.push({
      ...row,
      prefix,
      ask_dwell_seconds: row.ts - lastAskChange,
      ask_change_after_first_timestamp: askChangeAfterFirstTimestamp,
      strictly_later_same_price_ask_receipt: row.ts > lastAskChange,
      raw_row_count: count,
      progress_bin: Math.max(0, Math.min(100, Math.floor((row.ts - left) / (right - left) * 100))),
    });
  }
  const collapsed = [];
  for (const row of output) {
    if (collapsed.length && collapsed[collapsed.length - 1].ts === row.ts) collapsed[collapsed.length - 1] = row;
    else collapsed.push(row);
  }
  return collapsed;
}

function compatibleShapes(group, row, previous) {
  if (row.raw_row_count < 2) return previous;
  const profiles = previous.map((shapeId) => {
    const shape = group.shapes.find((candidate) => candidate.shape_id === shapeId);
    const support = shape.envelopes[row.progress_bin]?.empirical_support;
    return { shapeId, distances: support ? PREFIX_KEYS.map((key, index) => Math.abs((row.prefix[key] - support.means[index]) / support.sds[index])) : null };
  });
  const stagedMinimum = (candidates, indexes) => {
    const scored = candidates.map((candidate) => ({
      ...candidate,
      score: candidate.distances ? indexes.reduce((sum, index) => sum + candidate.distances[index] ** 2, 0) : Infinity,
    }));
    const minimum = Math.min(...scored.map((candidate) => candidate.score));
    return scored.filter((candidate) => candidate.score === minimum);
  };
  const micro = stagedMinimum(profiles, [0, 1]);
  return stagedMinimum(micro, [2, 3, 4, 5, 6, 7, 8]).map((candidate) => candidate.shapeId);
}
function directionOf(shapeId) {
  if (shapeId.includes("_UP_")) return "UP";
  if (shapeId.includes("_DOWN_")) return "DOWN";
  if (shapeId.includes("_FLAT_")) return "FLAT";
  return "UNKNOWN";
}
function inverseDirection(direction) { return direction === "UP" ? "DOWN" : direction === "DOWN" ? "UP" : direction; }
function shapeVerdict(group, shapeId, bin) {
  const shape = group.shapes.find((candidate) => candidate.shape_id === shapeId);
  const delta = shape.medoid_future[bin];
  return delta === null ? "UNKNOWN" : delta < 0 ? "LOWER" : "FLOOR";
}
function makerFee(price) { return Math.ceil(7 * QUANTITY * price * (100 - price) / 40000); }
function takerFee(price) { return Math.ceil(7 * QUANTITY * price * (100 - price) / 10000); }

function evaluateTick({ leg, sibling, tuples, high, ts, tickIndex, changedThisTick }) {
  const elapsedSinceOwnTick = ts - leg.last.ts;
  const row = {
    ...leg.last,
    ts,
    ask_dwell_seconds: leg.last.ask_dwell_seconds + elapsedSinceOwnTick,
    progress_bin: Math.max(0, Math.min(100, Math.floor((ts - leg.left) / (leg.right - leg.left) * 100))),
  };
  const role = leg === high ? "highShape" : "lowShape";
  const shapes = [...new Set(tuples.map((tuple) => tuple[role]))];
  const verdicts = shapes.map((shapeId) => ({ shape_id: shapeId, direction: directionOf(shapeId), verdict: shapeVerdict(leg.group, shapeId, row.progress_bin) }));
  let state = "INSUFFICIENT_EVIDENCE";
  let reason = "SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP";
  let micro = { own_micro_position_observed: false, evidence_type: null, stable_same_price_receipt: false, inverse_sibling_resolved: false };
  if (row.raw_row_count < 2) reason = "NO_PRIOR_IN_WINDOW_BOOK";
  else if (shapes.length && verdicts.every((candidate) => candidate.verdict === "LOWER")) {
    state = "HOLD";
    reason = "ALL_SURVIVING_SHAPES_SAY_LOWER";
  } else if (shapes.length && verdicts.every((candidate) => candidate.verdict === "FLOOR")) {
    micro = evaluateMicroPositionEvidence({ leg, sibling, dwellSeconds: DWELL_SECONDS });
    if (!micro.own_micro_position_observed) reason = "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED";
    else if (!micro.inverse_sibling_resolved) reason = "FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED";
    else if (row.prefix.ask_net !== row.prefix.ask_dip) reason = "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW";
    else if (row.ask_dwell_seconds >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) {
      state = "PLACE";
      reason = micro.stable_same_price_receipt && !leg.last.ask_change_after_first_timestamp
        ? "ALL_SURVIVING_PAIR_CONSTRAINED_SHAPES_SAY_FLOOR_AND_STABLE_SAME_PRICE_ASK_IS_EXECUTABLE"
        : "ALL_SURVIVING_PAIR_CONSTRAINED_SHAPES_SAY_FLOOR_AND_ASK_IS_EXECUTABLE";
    } else reason = "FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY";
  }
  const checks = {
    prior_in_window_book: row.raw_row_count >= 2,
    pair_constrained_shape_present: shapes.length > 0,
    floor_consensus: shapes.length > 0 && verdicts.every((candidate) => candidate.verdict === "FLOOR"),
    lower_consensus: shapes.length > 0 && verdicts.every((candidate) => candidate.verdict === "LOWER"),
    own_micro_position_observed: micro.own_micro_position_observed,
    inverse_sibling_resolved: micro.inverse_sibling_resolved,
    current_ask_is_observed_low: row.prefix.ask_net === row.prefix.ask_dip,
    dwell_at_least_10_seconds: row.ask_dwell_seconds >= DWELL_SECONDS,
    top_ask_size_at_least_five: row.top_ask_size >= QUANTITY,
  };
  return {
    event_id: leg.event_id,
    category: leg.category,
    price_region: leg.price_region,
    leg_id: leg.leg,
    joint_tick_index: tickIndex,
    own_evaluation_index: ++leg.evaluationCount,
    own_book_changed_this_joint_tick: changedThisTick,
    ...clocks(ts, leg),
    source_receipt: leg.last.receipt,
    source_row_timestamp_epoch: leg.last.ts,
    state,
    reason,
    book: {
      bid: row.bid,
      ask: row.ask,
      carried_last: row.carried_last,
      spread: row.spread,
      ask_dwell_seconds: row.ask_dwell_seconds,
      top_ask_size: row.top_ask_size,
      top5_ask_depth: row.top5_ask_depth,
      ask_net: row.prefix.ask_net,
      ask_dip: row.prefix.ask_dip,
    },
    library_partition: { key: leg.group.group_key, n: leg.group.n, selected_k: leg.group.selected_k },
    leg_surviving_shapes: leg.survivor_shapes.map((shapeId) => ({ shape_id: shapeId, direction: directionOf(shapeId) })),
    pair_constrained_surviving_shapes: verdicts,
    surviving_pair_tuple_count: tuples.length,
    checks,
    micro_position_evidence_type: micro.evidence_type,
  };
}

function diagnoseEvent(eventId, sources, library) {
  const legs = sources.map((source) => {
    const loaded = loadRows(source);
    if (!loaded.shapeRows.length) throw new Error(`no formed one-tick book for ${source.ticker}`);
    return {
      ...source,
      allRows: loaded.allRows,
      rows: prefixRows(loaded.shapeRows, source.left, source.right),
      source: loaded.source,
      preformationRows: loaded.preformationRows,
      firstAsk: loaded.shapeRows[0].ask,
      firstBid: loaded.shapeRows[0].bid,
      price_region: region(loaded.shapeRows[0].bid),
      last: null,
      evaluationCount: 0,
    };
  }).sort((a, b) => a.leg.localeCompare(b.leg));
  const high = [...legs].sort((a, b) => b.firstAsk - a.firstAsk || a.leg.localeCompare(b.leg))[0];
  const low = legs.find((leg) => leg !== high);
  const pairKey = `${high.category}|${high.price_region}|${low.price_region}`;
  const tupleObject = library.pair_shape_tuples[pairKey] || {};
  const allTuples = Object.entries(tupleObject).map(([key, n]) => {
    const [highShape, lowShape] = key.split("|");
    return { highShape, lowShape, n };
  });
  for (const leg of legs) {
    const group = library.groups[`${leg.category}|${leg.price_region}`];
    if (!group) throw new Error(`missing group ${leg.category}|${leg.price_region}`);
    leg.group = group;
    leg.survivorShapes = group.shapes.map((shape) => shape.shape_id);
    leg.survivor_shapes = leg.survivorShapes;
    leg.resolved_direction = null;
    leg.independent_direction = null;
  }
  let tuples = allTuples;
  const indices = Object.fromEntries(legs.map((leg) => [leg.leg, 0]));
  const clock = [...new Set(legs.flatMap((leg) => leg.rows.map((row) => row.ts)))].sort((a, b) => a - b);
  const traces = Object.fromEntries(legs.map((leg) => [leg.leg, []]));
  for (let clockIndex = 0; clockIndex < clock.length; clockIndex += 1) {
    const ts = clock[clockIndex];
    const changed = {};
    for (const leg of legs) {
      let didChange = false;
      while (indices[leg.leg] < leg.rows.length && leg.rows[indices[leg.leg]].ts <= ts) {
        leg.last = leg.rows[indices[leg.leg]++];
        didChange = true;
      }
      changed[leg.leg] = didChange;
      if (didChange && (leg === high || high.last)) {
        leg.survivorShapes = compatibleShapes(leg.group, leg.last, leg.survivorShapes);
        leg.survivor_shapes = leg.survivorShapes;
        const ownDirections = [...new Set(leg.survivorShapes.map(directionOf))];
        if (!leg.independent_direction && ownDirections.length === 1 && ownDirections[0] !== "UNKNOWN") leg.independent_direction = ownDirections[0];
      }
      const directions = [...new Set(leg.survivorShapes.map(directionOf))];
      if (!leg.resolved_direction && directions.length === 1 && directions[0] !== "UNKNOWN") leg.resolved_direction = directions[0];
    }
    for (const sourceLeg of legs) {
      if (!sourceLeg.resolved_direction) continue;
      const sibling = legs.find((leg) => leg !== sourceLeg);
      if (sibling.resolved_direction) continue;
      const required = inverseDirection(sourceLeg.resolved_direction);
      const constrained = sibling.survivorShapes.filter((shapeId) => directionOf(shapeId) === required);
      if (constrained.length) {
        sibling.survivorShapes = constrained;
        sibling.survivor_shapes = constrained;
      }
    }
    tuples = tuples.filter((tuple) => high.survivorShapes.includes(tuple.highShape) && low.survivorShapes.includes(tuple.lowShape));
    for (const leg of legs) {
      if (!leg.last) continue;
      const sibling = legs.find((candidate) => candidate !== leg);
      traces[leg.leg].push(evaluateTick({ leg, sibling, tuples, high, ts, tickIndex: clockIndex + 1, changedThisTick: changed[leg.leg] }));
    }
  }
  return { event_id: eventId, pair_key: pairKey, initial_pair_tuple_count: allTuples.length, final_pair_tuple_count: tuples.length, legs, traces };
}

function reasonIntervals(rows) {
  const intervals = [];
  for (const row of rows) {
    const key = JSON.stringify([row.state, row.reason, row.leg_surviving_shapes, row.pair_constrained_surviving_shapes, row.surviving_pair_tuple_count]);
    const prior = intervals[intervals.length - 1];
    if (prior && prior.key === key) {
      prior.evaluation_count += 1;
      prior.last = row;
    } else intervals.push({ key, evaluation_count: 1, first: row, last: row });
  }
  return intervals.map(({ key, ...interval }) => interval);
}

function disagreementClass(row) {
  if (row.reason !== "SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP") return "NOT_THE_ACTIVE_PREDICATE";
  if (!row.pair_constrained_surviving_shapes.length && row.leg_surviving_shapes.length) return "PAIR_TUPLE_LIBRARY_GAP";
  if (!row.leg_surviving_shapes.length) return "LEG_SHAPE_LIBRARY_GAP";
  const verdicts = new Set(row.pair_constrained_surviving_shapes.map((shape) => shape.verdict));
  if (verdicts.size > 1) return "PAIR_CONSTRAINED_LIBRARY_DISAGREEMENT";
  return "UNRESOLVED_LIBRARY_PREDICATE";
}
function blockerClass(row) {
  if (row.reason === "SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP") return disagreementClass(row) === "PAIR_TUPLE_LIBRARY_GAP" ? "LIBRARY_FITTING_PAIR_TUPLE_COVERAGE_DEFECT" : "LIBRARY_FITTING_DISAGREEMENT_OR_GAP";
  if (row.reason === "FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED") return "PAIR_EVIDENCE_PREDICATE_UNPROVEN";
  if (row.reason === "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW") return "MICRO_POSITION_NO_LONGER_AT_LOW";
  if (row.reason === "NO_PRIOR_IN_WINDOW_BOOK") return "BOOK_SEQUENCE_EVIDENCE_UNPROVEN";
  return "OTHER_NAMED_PREDICATE";
}

function scanCapacityFloor(source, rows) {
  const since = Array(100).fill(null);
  let best = null;
  let last = null;
  const inspect = (book, evidenceTs, endpoint = false) => {
    if (!Number.isInteger(book.bid) || !Number.isInteger(book.ask) || book.bid <= 0 || book.ask > 99 || book.bid > book.ask) return;
    for (let limit = 1; limit < book.ask; limit += 1) since[limit] = null;
    for (let limit = book.ask; limit <= 99; limit += 1) if (since[limit] === null) since[limit] = book.ts;
    let cumulative = 0;
    let levelIndex = 0;
    for (let limit = book.ask; limit <= 99; limit += 1) {
      while (levelIndex < book.asks.length && book.asks[levelIndex][0] <= limit) cumulative += book.asks[levelIndex++][1];
      const dwell = evidenceTs - since[limit];
      if (cumulative < QUANTITY || dwell < DWELL_SECONDS) continue;
      if (!best || limit < best.limit_cents || (limit === best.limit_cents && evidenceTs < best.evidence_ts)) {
        best = {
          limit_cents: limit,
          ...clocks(evidenceTs, source),
          dwell_seconds_at_first_proof: dwell,
          displayed_capacity_at_or_below_limit: cumulative,
          best_ask_at_proof: book.ask,
          best_bid_at_proof: book.bid,
          carried_last_at_proof: book.carried_last,
          spread_at_proof: book.spread,
          top_five_asks: book.asks,
          source_receipt: `${book.receipt}${endpoint ? "; right-endpoint-carry" : ""}`,
        };
      }
      break;
    }
  };
  for (const row of rows) { inspect(row, row.ts); last = row; }
  if (last && last.ts < source.right) inspect(last, source.right, true);
  return best;
}

function placementRelation(price, book) {
  if (price < book.bid) return "RESTING_BELOW_BID";
  if (price === book.bid) return "JOINING_BID";
  if (price < book.ask) return "RESTING_INSIDE_SPREAD";
  if (price === book.ask) return "SITTING_AT_ASK_MARKETABLE_BUY";
  return "THROUGH_ASK_MARKETABLE_BUY";
}

function main() {
  const replay = JSON.parse(fs.readFileSync(replayPath));
  const summary = JSON.parse(fs.readFileSync(summaryPath));
  const library = JSON.parse(fs.readFileSync(libraryPath));
  const frozenFive = JSON.parse(fs.readFileSync(frozenFivePath));
  const frozenWindows = Object.fromEntries(frozenFive.events.map((event) => [event.event_id, event.window]));
  const quoteLines = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/);
  const quoteHeaders = quoteLines.shift().split(",");
  const quoteRows = quoteLines.map((line) => Object.fromEntries(line.split(",").map((value, index) => [quoteHeaders[index], value])));
  const targets = new Set(summary.events.map((event) => event.event_id));
  const sourcesByEvent = {};
  for (const row of quoteRows) {
    if (!targets.has(row.event_id)) continue;
    if (!sourcesByEvent[row.event_id]) sourcesByEvent[row.event_id] = [];
    sourcesByEvent[row.event_id].push({
      event_id: row.event_id,
      category: row.category,
      leg: row.leg,
      ticker: row.ticker,
      left: Number(row.left_ts),
      right: Number(row.right_ts),
      scheduled: Number(row.scheduled_start_ts),
      bell: Number(frozenWindows[row.event_id].actual_bell_ts),
      quote_10s_floor_limit_cents: integer(row.quote_10s_floor_limit_cents),
      window1_close_cents: integer(row.window1_close_cents),
    });
  }

  const fillRows = [];
  for (const event of replay.events) {
    for (const [legId, leg] of Object.entries(event.legs)) {
      if (!leg.fill) continue;
      const place = leg.decision_changes.find((decision) => decision.state === "PLACE");
      if (!place) throw new Error(`missing PLACE for ${event.event_id}/${legId}`);
      const relation = placementRelation(leg.placement.price_cents, place.book);
      const makerOnlyClampedPrice = Math.max(1, place.book.ask - 1);
      const makerOnlyRelation = placementRelation(makerOnlyClampedPrice, place.book);
      const source = sourcesByEvent[event.event_id].find((candidate) => candidate.leg === legId);
      fillRows.push({
        event_id: event.event_id,
        category: event.category,
        price_region: leg.price_region,
        leg_id: legId,
        ticker: leg.ticker,
        action_clock: clocks(leg.placement.action_ts, source),
        action_receipt: leg.placement.action_receipt,
        own_book_receipt_at_action: leg.placement.own_book_receipt_at_action,
        action_book: {
          bid: place.book.bid,
          ask: place.book.ask,
          carried_last: place.book.carried_last,
          spread: place.book.spread,
          ask_dwell_seconds: place.book.ask_dwell_seconds,
          top_ask_size: place.book.top_ask_size,
          top5_ask_depth: place.book.top5_ask_depth,
        },
        order_price_cents: leg.placement.price_cents,
        placement_relation: relation,
        execution_role: relation.includes("MARKETABLE") ? "TAKER" : "MAKER",
        maker_only_live_chokepoint_price_cents: makerOnlyClampedPrice,
        maker_only_live_chokepoint_relation: makerOnlyRelation,
        maker_only_post_outcome: relation.includes("MARKETABLE") ? "LIVE_NEVER_MARKETABLE_CHOKEPOINT_CLAMPS_TO_ASK_MINUS_ONE_BEFORE_POST_ONLY_SUBMISSION" : "LAWFUL_MAKER_RESTING_ORDER",
        original_fill_receipt_reaches_clamped_maker_price: leg.fill.ask_cents <= makerOnlyClampedPrice,
        delayed_fill_receipt_does_not_change_action_role: true,
        fill_evidence_clock: clocks(leg.fill.evidence_ts, source),
        fill_evidence_receipt: leg.fill.evidence_receipt,
        fill_evidence_ask_cents: leg.fill.ask_cents,
        fill_evidence_capacity: leg.fill.capacity,
        quantity: leg.fill.quantity,
        maker_fee_total_cents_for_five_contract_order: makerFee(leg.placement.price_cents),
        taker_fee_total_cents_for_five_contract_order: takerFee(leg.placement.price_cents),
        replay_fee_treatment: "NO_FEE_APPLIED_PRICE_ONLY_DIAGNOSTIC",
      });
    }
  }
  const pairFeeRows = summary.events.filter((event) => event.completed_pair).map((event) => {
    const fills = fillRows.filter((row) => row.event_id === event.event_id);
    const maker = fills.reduce((sum, row) => sum + row.maker_fee_total_cents_for_five_contract_order, 0);
    const taker = fills.reduce((sum, row) => sum + row.taker_fee_total_cents_for_five_contract_order, 0);
    return {
      event_id: event.event_id,
      price_only_combined_delta_to_own_closes_cents_per_contract: event.combined_delta_to_own_window1_closes_cents,
      maker_fee_total_cents_for_five_contract_pair: maker,
      taker_fee_total_cents_for_five_contract_pair: taker,
      maker_fee_adjusted_delta_cents_per_contract: event.combined_delta_to_own_window1_closes_cents + maker / QUANTITY,
      taker_fee_adjusted_delta_cents_per_contract: event.combined_delta_to_own_window1_closes_cents + taker / QUANTITY,
      maker_only_completion_valid: fills.every((row) => row.execution_role === "MAKER"),
      ruling: "PRICE_DELTA_IS_OBSERVED_COUNTERFACTUAL_ARITHMETIC_BUT_NOT_A_MAKER_ONLY_COMPLETION",
    };
  });
  const makerAudit = {
    schema_version: "WINDOW1_FIVE_GAME_MAKER_TAKER_FILL_AUDIT_V1",
    score_free: true,
    quantity: QUANTITY,
    doctrine: "ENTRY_BUYS_ARE_MAKER_ONLY_POST_ONLY",
    fee_law: {
      maker: "ceil(1.75% * quantity * p * (1-p)) dollars, expressed here as ceil(7*q*price*(100-price)/40000) cents",
      taker: "ceil(7% * quantity * p * (1-p)) dollars, expressed here as ceil(7*q*price*(100-price)/10000) cents",
      underlying_rate_multiple: 4,
    },
    credited_fill_count: fillRows.length,
    placement_relation_counts: Object.fromEntries([...new Set(fillRows.map((row) => row.placement_relation))].map((key) => [key, fillRows.filter((row) => row.placement_relation === key).length])),
    maker_only_creditable_fill_count: fillRows.filter((row) => row.execution_role === "MAKER").length,
    taker_or_marketable_fill_count: fillRows.filter((row) => row.execution_role === "TAKER").length,
    fills: fillRows,
    completed_pairs: pairFeeRows,
  };

  const allTickRows = [];
  const insufficiencyRows = [];
  const floorRows = [];
  for (const eventSummary of summary.events.filter((event) => !event.completed_pair)) {
    const diagnostic = diagnoseEvent(eventSummary.event_id, sourcesByEvent[eventSummary.event_id], library);
    for (const legSummary of eventSummary.legs) {
      const leg = diagnostic.legs.find((candidate) => candidate.leg === legSummary.leg_id);
      const trace = diagnostic.traces[leg.leg];
      if (trace.some((row) => row.state === "PLACE")) throw new Error(`diagnostic unexpectedly placed ${eventSummary.event_id}/${leg.leg}`);
      allTickRows.push(...trace);
      const terminal = trace[trace.length - 1];
      const firstTerminalPredicate = trace.find((row) => row.reason === terminal.reason);
      const minimumPairShapeCount = Math.min(...trace.map((row) => row.pair_constrained_surviving_shapes.length));
      const maximumPairShapeCount = Math.max(...trace.map((row) => row.pair_constrained_surviving_shapes.length));
      const minimumLegShapeCount = Math.min(...trace.map((row) => row.leg_surviving_shapes.length));
      const everPairCollapsedToOne = trace.some((row) => row.pair_constrained_surviving_shapes.length === 1);
      const everLegCollapsedToOne = trace.some((row) => row.leg_surviving_shapes.length === 1);
      insufficiencyRows.push({
        event_id: eventSummary.event_id,
        category: eventSummary.category,
        leg_id: leg.leg,
        ticker: leg.ticker,
        price_region: leg.price_region,
        library_partition: { key: leg.group.group_key, n: leg.group.n, selected_k: leg.group.selected_k },
        shape_partition_is_the_226_leg_partition: leg.group.n === 226,
        joint_clock_tick_count: Math.max(...Object.values(diagnostic.traces).flat().map((row) => row.joint_tick_index)),
        own_decision_evaluation_count: trace.length,
        pair_shape_tuple_context: {
          key: diagnostic.pair_key,
          initial_tuple_count: diagnostic.initial_pair_tuple_count,
          terminal_tuple_count: diagnostic.final_pair_tuple_count,
        },
        terminal_predicate_first_occurrence: firstTerminalPredicate,
        terminal_evaluation: terminal,
        terminal_library_disagreement_class: disagreementClass(terminal),
        terminal_blocker_class: blockerClass(terminal),
        ever_leg_shape_set_collapsed_to_one: everLegCollapsedToOne,
        ever_pair_constrained_shape_set_collapsed_to_one: everPairCollapsedToOne,
        minimum_leg_survivor_count: minimumLegShapeCount,
        minimum_pair_constrained_survivor_count: minimumPairShapeCount,
        maximum_pair_constrained_survivor_count: maximumPairShapeCount,
        reason_counts: Object.fromEntries([...new Set(trace.map((row) => row.reason))].sort().map((reason) => [reason, trace.filter((row) => row.reason === reason).length])),
        reason_and_shape_intervals: reasonIntervals(trace),
        stale_v2_terminal_reason: legSummary.terminal_reason,
        stale_reason_matches_recomputed_terminal: legSummary.terminal_reason === terminal.reason,
      });

      const floor = scanCapacityFloor(leg, leg.allRows);
      if (!floor) throw new Error(`missing capacity floor ${eventSummary.event_id}/${leg.leg}`);
      if (floor.limit_cents !== legSummary.own_ask_reachable_low_cents) throw new Error(`floor mismatch ${eventSummary.event_id}/${leg.leg}: ${floor.limit_cents} != ${legSummary.own_ask_reachable_low_cents}`);
      floorRows.push({
        event_id: eventSummary.event_id,
        category: eventSummary.category,
        price_region: leg.price_region,
        leg_id: leg.leg,
        ticker: leg.ticker,
        own_window1_close_cents: legSummary.own_window1_close_cents,
        ask_reachable_low_cents: floor.limit_cents,
        signed_low_minus_close_cents: floor.limit_cents - legSummary.own_window1_close_cents,
        discount_left_unharvested_cents: legSummary.own_window1_close_cents - floor.limit_cents,
        proof: floor,
      });
    }
  }
  const insufficiency = {
    schema_version: "WINDOW1_FIVE_GAME_INSUFFICIENT_PREDICATE_DIAGNOSIS_V1",
    score_free: true,
    warning: "The V2 replay decision_changes ledger compresses only on state changes, not predicate changes. stale_v2_terminal_reason is retained but the recomputed terminal_evaluation is controlling here.",
    event_count: 3,
    leg_count: insufficiencyRows.length,
    rows: insufficiencyRows,
  };
  const floorLedger = {
    schema_version: "WINDOW1_THREE_INSUFFICIENT_EVENTS_ASK_LOW_DWELL_CAPACITY_V1",
    side: "ASK_ONLY",
    dwell_seconds: DWELL_SECONDS,
    required_displayed_contracts: QUANTITY,
    row_count: floorRows.length,
    rows: floorRows,
    event_pairs: [...new Set(floorRows.map((row) => row.event_id))].sort().map((eventId) => {
      const rows = floorRows.filter((row) => row.event_id === eventId);
      const floorSum = rows.reduce((sum, row) => sum + row.ask_reachable_low_cents, 0);
      const closeSum = rows.reduce((sum, row) => sum + row.own_window1_close_cents, 0);
      return {
        event_id: eventId,
        capacity_proven_ask_floor_sum_cents: floorSum,
        own_window1_close_sum_cents: closeSum,
        signed_floor_sum_minus_close_sum_cents: floorSum - closeSum,
        discount_left_unharvested_cents: closeSum - floorSum,
      };
    }),
  };

  const sourceManifest = {
    schema_version: "WINDOW1_MAKER_INSUFFICIENT_SOURCE_HASH_MANIFEST_V1",
    committed: Object.fromEntries([replayPath, summaryPath, libraryPath, frozenFivePath, quotePath, makerLawPath, takerLawPath, replayBuilderPath, microPositionPath, __filename].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])),
    private_tick_files: Object.fromEntries(Object.values(sourcesByEvent).flat().map((source) => {
      const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
      return [path.basename(file), { bytes: fs.statSync(file).size, sha256: hashFile(file) }];
    })),
  };
  const report = [
    "# Five-game maker/taker and insufficiency diagnosis",
    "",
    "This is a cold-input, score-free diagnostic. It changes no placement or fill.",
    "",
    "## Maker versus taker",
    "",
    "| category | region | event | leg | action BBO/last | dwell | replay X | replay relation | role | live maker clamp X/relation | maker fee / 5 | taker fee / 5 |",
    "|---|---|---|---|---|---:|---:|---|---|---|---:|---:|",
    ...fillRows.map((row) => `| ${row.category} | ${row.price_region} | ${row.event_id} | ${row.leg_id} | ${row.action_book.bid}/${row.action_book.ask}/${row.action_book.carried_last ?? "NULL"} (spread ${row.action_book.spread}) | ${row.action_book.ask_dwell_seconds}s | ${row.order_price_cents} | ${row.placement_relation} | ${row.execution_role} | ${row.maker_only_live_chokepoint_price_cents}/${row.maker_only_live_chokepoint_relation} | ${row.maker_fee_total_cents_for_five_contract_order}c | ${row.taker_fee_total_cents_for_five_contract_order}c |`),
    "",
    "All four credited prices equal the contemporaneous external ask. They are marketable taker actions. The live post-only chokepoint would clamp each one-cent-spread action to ask-1, which equals the bid, before submission. The later external ask receipt reaches none of those clamped prices. It proves the replay's delayed capacity rule; it does not retroactively turn the ask-priced action into maker liquidity.",
    "",
    "| event | price-only delta/contract | maker fees/pair | taker fees/pair | maker-adjusted delta/contract | taker-adjusted delta/contract | maker-only valid |",
    "|---|---:|---:|---:|---:|---:|---|",
    ...pairFeeRows.map((row) => `| ${row.event_id} | ${row.price_only_combined_delta_to_own_closes_cents_per_contract} | ${row.maker_fee_total_cents_for_five_contract_pair}c | ${row.taker_fee_total_cents_for_five_contract_pair}c | ${row.maker_fee_adjusted_delta_cents_per_contract.toFixed(1)} | ${row.taker_fee_adjusted_delta_cents_per_contract.toFixed(1)} | NO |`),
    "",
    "The -9 and -16 remain price-only arithmetic, and remain negative after counterfactual taker fees. They are not maker-only completed-pair results because none of the four actions could lawfully rest post-only at its action BBO.",
    "",
    "## Insufficient legs",
    "",
    "| category | region | partition n | event | leg | first terminal-predicate tick (sched/bell) | BBO/last, spread, dwell | recomputed terminal predicate | own surviving shapes | pair-constrained shapes | blocker class | low | dwell | capacity | low-close |",
    "|---|---|---:|---|---|---|---|---|---|---|---|---:|---:|---:|---:|",
    ...insufficiencyRows.map((row) => {
      const floor = floorRows.find((candidate) => candidate.event_id === row.event_id && candidate.leg_id === row.leg_id);
      const first = row.terminal_predicate_first_occurrence;
      const ownShapes = row.terminal_evaluation.leg_surviving_shapes.map((shape) => shape.shape_id).join("; ") || "EMPTY";
      const pairShapes = row.terminal_evaluation.pair_constrained_surviving_shapes.map((shape) => `${shape.shape_id}:${shape.verdict}`).join("; ") || "EMPTY";
      const book = first.book;
      return `| ${row.category} | ${row.price_region} | ${row.library_partition.n} | ${row.event_id} | ${row.leg_id} | #${first.joint_tick_index} (${tMinus(first.t_minus_scheduled_seconds)} / ${tMinus(first.t_minus_actual_bell_seconds)}) | ${book.bid}/${book.ask}/${book.carried_last ?? "NULL"}, ${book.spread}c, ${book.ask_dwell_seconds}s | ${row.terminal_evaluation.reason} | ${ownShapes} | ${pairShapes} | ${row.terminal_blocker_class} | ${floor.ask_reachable_low_cents} | ${floor.proof.dwell_seconds_at_first_proof}s | ${floor.proof.displayed_capacity_at_or_below_limit} | ${floor.signed_low_minus_close_cents >= 0 ? "+" : ""}${floor.signed_low_minus_close_cents} |`;
    }),
    "",
    "The 226-leg ATP_CHALL 51_75 partition belongs to BIG and resolved successfully. None of the six insufficient legs is in that partition. LAJ/VAN are ATP_MAIN 26_50 (n=96); their pair-constrained tuple set is exhausted. That is a pair-library coverage/fitting defect, not missing market evidence. The other four failures retain their exact named evidence predicates above.",
    "",
    "| event | capacity-proven ask-floor pair | own-close pair | signed floor-close | discount left unharvested |",
    "|---|---:|---:|---:|---:|",
    ...floorLedger.event_pairs.map((row) => `| ${row.event_id} | ${row.capacity_proven_ask_floor_sum_cents} | ${row.own_window1_close_sum_cents} | ${row.signed_floor_sum_minus_close_sum_cents} | ${row.discount_left_unharvested_cents}c |`),
  ].join("\n") + "\n";

  const files = {
    "MAKER_TAKER_FILL_AUDIT.json": canonical(makerAudit),
    "INSUFFICIENT_PREDICATE_DIAGNOSIS.json": canonical(insufficiency),
    "ASK_LOW_DWELL_CAPACITY_LEDGER.json": canonical(floorLedger),
    "PER_TICK_INSUFFICIENCY_TRACE.jsonl.gz": zlib.gzipSync(Buffer.from(allTickRows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { mtime: 0 }),
    "SOURCE_HASH_MANIFEST.json": canonical(sourceManifest),
    "REPORT.md": report,
  };
  const artifactRows = Object.entries(files).map(([name, content]) => ({ path: `.claude/window1_live_v4_replay/quote_shape_maker_insufficient_diagnosis_20260801/${name}`, bytes: Buffer.byteLength(content), sha256: sha256(content) }));
  files["ARTIFACT_HASH_MANIFEST.json"] = canonical({ schema_version: "WINDOW1_MAKER_INSUFFICIENT_ARTIFACT_HASH_MANIFEST_V1", artifacts: artifactRows });
  fs.mkdirSync(outDir, { recursive: true });
  for (const [name, content] of Object.entries(files)) fs.writeFileSync(path.join(outDir, name), content);
  process.stdout.write(canonical({ status: "BUILT", credited_fills: fillRows.length, taker_fills: fillRows.filter((row) => row.execution_role === "TAKER").length, insufficient_legs: insufficiencyRows.length, per_tick_rows: allTickRows.length }));
}

main();
