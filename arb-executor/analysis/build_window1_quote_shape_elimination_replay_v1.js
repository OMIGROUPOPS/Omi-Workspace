#!/usr/bin/env node
"use strict";

// Cold two-game replay over the frozen quote-shape library. No scorer.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { evaluateMicroPositionEvidence } = require("./window1_quote_shape_micro_position_v2.js");
const { completePairTupleSupport, evaluatePairWiringEvidence } = require("./window1_quote_shape_pair_wiring_v3.js");
const { evaluateStableAskSigningSupport } = require("./window1_quote_shape_stable_signer_v4.js");
const { evaluateDescentVerdict } = require("./window1_quote_shape_descent_verdict_v5.js");

const args = process.argv.slice(2), value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(value("--repo", args[0] && !args[0].startsWith("--") ? args[0] : "."));
const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const outDir = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731")));
const libraryPath = path.resolve(value("--library", path.join(outDir, "QUOTE_SHAPE_LIBRARY.json")));
const stableSamePriceConfirmation = args.includes("--stable-same-price-confirmation");
const pairWiringV3 = args.includes("--pair-wiring-v3");
const stableSignerV4 = args.includes("--stable-signer-v4");
const descentVerdictV5 = args.includes("--descent-verdict-v5");
const dynamicRenarrowV6 = args.includes("--dynamic-renarrow-v6");
const compactPopulation = args.includes("--compact-population");
const noCharts = args.includes("--no-charts");
const excludeOwnTrainingMember = args.includes("--exclude-own-training-member");
const receiptName = value("--receipt-name", "TWO_GAME_REPLAY.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const refsPath = path.resolve(value("--references", path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/REPLAY_AND_REFERENCE_PANEL.json")));
const frozenFivePath = path.resolve(value("--windows", path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json")));
const DEFAULT_TARGETS = ["KXATPCHALLENGERMATCH-26JUL19NIKVRB", "KXATPCHALLENGERMATCH-26JUL19HURBIG"];
const targetFile = value("--target-file", null);
const TARGETS = new Set(targetFile ? JSON.parse(fs.readFileSync(path.resolve(targetFile))) : value("--targets", DEFAULT_TARGETS.join(",")).split(",").filter(Boolean));
const PREFIX_KEYS = ["ask_net", "ask_dip", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "ask_dwell_fraction", "mean_log_top_ask_size", "mean_log_top5_ask_depth"];
const DWELL_SECONDS = 10, QUANTITY = 5;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function parseEt(value) { const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line, index) => ({ raw: Object.fromEntries(line.split(",").map((v, i) => [headers[i], v])), ordinal: index + 2 })); }
function et(ts) { return new Date((ts - 4 * 3600) * 1000).toISOString().replace("T", " ").replace("Z", " ET"); }
function signed(value) { return Number.isInteger(value) ? `${value >= 0 ? "+" : ""}${value}` : "NULL"; }

function loadRows(source) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`), bytes = fs.readFileSync(file), rows = [];
  for (const { raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et); if (ts === null || ts < source.left || ts > source.right) continue; const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) { const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]); if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]); }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, receipt: `${path.basename(file)}#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1], top5_ask_depth: asks.reduce((s, x) => s + x[1], 0), asks, carried_last: integer(raw.last_trade) });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal); const formedIndex = rows.findIndex((row) => row.spread === 1); const shapeRows = formedIndex >= 0 ? rows.slice(formedIndex) : [];
  return { rows: shapeRows, preformation_rows: formedIndex < 0 ? rows.length : formedIndex, source: { file: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) } };
}
function prefixRows(rows, left, right) {
  let state = null, firstAsk = null, firstBid = null, firstBookTs = null, firstTopAskSize = null, firstSpread = null, minAsk = null, maxAsk = null, spreadMin = null, spreadMax = null, lastAskChange = null, count = 0, secondCount = 0, changes = 0, askDescents = 0, newLowDescents = 0, askRises = 0, askChangeAfterFirstTimestamp = false, topAskSizeEverChanged = false, spreadIntegral = 0, sizeIntegral = 0, depthIntegral = 0, observedDuration = 0;
  const distinctBbo = new Set(), distinctAsks = new Set();
  const output = [];
  function integrate(ts) { if (!state) return; const dt = Math.max(0, ts - state.integrated_to); spreadIntegral += state.spread * dt; sizeIntegral += Math.log1p(state.top_ask_size) * dt; depthIntegral += Math.log1p(state.top5_ask_depth) * dt; observedDuration += dt; state.integrated_to = ts; }
  for (const row of rows) {
    integrate(row.ts); if (!state) { firstAsk = row.ask; firstBid = row.bid; firstBookTs = row.ts; firstTopAskSize = row.top_ask_size; firstSpread = row.spread; minAsk = row.ask; maxAsk = row.ask; lastAskChange = row.ts; spreadMin = row.spread; spreadMax = row.spread; }
    if (!state || row.ts !== state.ts) secondCount += 1;
    if (state && row.ask !== state.ask) { changes += 1; if (row.ask < state.ask) askDescents += 1; else askRises += 1; if (row.ask < minAsk) newLowDescents += 1; lastAskChange = row.ts; if (row.ts > firstBookTs) askChangeAfterFirstTimestamp = true; }
    if (row.top_ask_size !== firstTopAskSize) topAskSizeEverChanged = true;
    minAsk = Math.min(minAsk, row.ask); maxAsk = Math.max(maxAsk, row.ask); spreadMin = Math.min(spreadMin, row.spread); spreadMax = Math.max(spreadMax, row.spread); distinctBbo.add(`${row.bid}/${row.ask}`); distinctAsks.add(row.ask); count += 1; state = { ...row, integrated_to: row.ts };
    const elapsed = Math.max(1, row.ts - left), obs = Math.max(1, observedDuration), prefix = { ask_net: row.ask - firstAsk, ask_dip: minAsk - firstAsk, mean_spread: spreadIntegral / obs, spread_range: spreadMax - spreadMin, quote_rate: count * 3600 / elapsed, ask_change_rate: changes * 3600 / elapsed, ask_dwell_fraction: Math.max(0, row.ts - lastAskChange) / elapsed, mean_log_top_ask_size: sizeIntegral / obs, mean_log_top5_ask_depth: depthIntegral / obs };
    output.push({ ...row, prefix, ask_dwell_seconds: row.ts - lastAskChange, ask_change_after_first_timestamp: askChangeAfterFirstTimestamp, strictly_later_same_price_ask_receipt: row.ts > lastAskChange, top_ask_size_ever_changed: topAskSizeEverChanged, ask_peak_cents: maxAsk - firstAsk, confirmation_spread_cents: Math.max(firstSpread, row.spread), raw_row_count: count, second_distinct_receipt_count: secondCount, distinct_bbo_state_count: distinctBbo.size, distinct_ask_count: distinctAsks.size, ask_change_count: changes, ask_descent_count: askDescents, new_low_descent_count: newLowDescents, ask_rise_count: askRises, first_book: { timestamp_epoch: firstBookTs, bid: firstBid, ask: firstAsk, top_ask_size: firstTopAskSize, spread: firstSpread }, progress_bin: Math.max(0, Math.min(100, Math.floor((row.ts - left) / (right - left) * 100))) });
  }
  const collapsed = []; for (const row of output) { if (collapsed.length && collapsed[collapsed.length - 1].ts === row.ts) collapsed[collapsed.length - 1] = row; else collapsed.push(row); } return collapsed;
}
function compatibleShapes(group, row, previous) {
  if (row.raw_row_count < 2) return previous;
  const profiles = previous.map((shapeId) => {
    const shape = group.shapes.find((s) => s.shape_id === shapeId), support = shape.envelopes[row.progress_bin]?.empirical_support;
    return { shapeId, distances: support ? PREFIX_KEYS.map((key, d) => Math.abs((row.prefix[key] - support.means[d]) / support.sds[d])) : null };
  });
  // The tree is deliberately ordered. Ask-path position is the micro layer;
  // dwell/spread/cadence/visible size/depth can only resolve ties left by it.
  // Exact empirical minima are a fitted ordering, not a hand-set tolerance.
  const stagedMinimum = (candidates, indexes) => {
    const scored = candidates.map((candidate) => ({ ...candidate, score: candidate.distances ? indexes.reduce((sum, i) => sum + candidate.distances[i] ** 2, 0) : Infinity }));
    const minimum = Math.min(...scored.map((candidate) => candidate.score));
    return scored.filter((candidate) => candidate.score === minimum);
  };
  const micro = stagedMinimum(profiles, [0, 1]);
  return stagedMinimum(micro, [2, 3, 4, 5, 6, 7, 8]).map((x) => x.shapeId);
}
function nearestMemberFuture(shape, row, requiredDescentOrdinal = null, excludedEventId = null) {
  const support = shape.envelopes[row.progress_bin]?.empirical_support, members = (shape.member_paths || []).filter((member) => member.event_id !== excludedEventId && member.bins[row.progress_bin] && (requiredDescentOrdinal === null || member.descent_ordinal_to_final_reachable_low === requiredDescentOrdinal));
  if (!support || !members.length) return { verdict: "UNKNOWN", selected_members: [], remaining_min_deltas: [] };
  const scored = members.map((member) => {
    const bin = member.bins[row.progress_bin], distances = PREFIX_KEYS.map((key, index) => Math.abs((row.prefix[key] - bin.prefix[index]) / support.sds[index]));
    return { member, bin, micro: distances[0] ** 2 + distances[1] ** 2, tie: distances.slice(2).reduce((sum, value) => sum + value ** 2, 0) };
  });
  const microMin = Math.min(...scored.map((item) => item.micro)), micro = scored.filter((item) => item.micro === microMin), tieMin = Math.min(...micro.map((item) => item.tie)), nearest = micro.filter((item) => item.tie === tieMin), deltas = nearest.map((item) => item.bin.remaining_reachable_low_delta);
  const verdict = !deltas.length || deltas.some((delta) => !Number.isFinite(delta)) ? "UNKNOWN" : deltas.every((delta) => delta < 0) ? "LOWER" : deltas.every((delta) => delta >= 0) ? "FLOOR" : "UNKNOWN";
  return { verdict, selected_members: nearest.map((item) => ({ event_id: item.member.event_id, leg_id: item.member.leg_id, ticker: item.member.ticker })), remaining_min_deltas: deltas };
}
function shapeVerdict(group, shapeId, bin, row, excludedEventId = null) {
  const shape = group.shapes.find((s) => s.shape_id === shapeId), delta = shape.medoid_future[bin], medoidVerdict = delta === null ? "UNKNOWN" : delta < 0 ? "LOWER" : "FLOOR", fitted = shape.descent_to_final_reachable_low ?? null;
  const zeroDescentSupport = Number(fitted?.counts?.["0"] || 0), useZeroDescentMember = dynamicRenarrowV6 && shape.topology.startsWith("DOWN_") && medoidVerdict === "LOWER" && row.new_low_descent_count === 0 && zeroDescentSupport > 0, memberVerdict = useZeroDescentMember ? nearestMemberFuture(shape, row, 0, excludedEventId) : null, baseVerdict = useZeroDescentMember ? memberVerdict.verdict : medoidVerdict;
  const adjusted = descentVerdictV5 ? evaluateDescentVerdict({ baseVerdict, observedNewLowDescents: row.new_low_descent_count, fittedDistribution: fitted }) : { verdict: baseVerdict, descent_adjustment: "NOT_APPLICABLE", observed_new_low_descents: row.new_low_descent_count };
  return { ...adjusted, base_verdict: baseVerdict, fitted_descent_distribution: fitted, temporal_authority: useZeroDescentMember ? "CAUSALLY_NEAREST_ZERO_DESCENT_MEMBER" : "STATIC_SHAPE_MEDOID", selected_training_members: memberVerdict?.selected_members ?? [], selected_member_remaining_min_deltas: memberVerdict?.remaining_min_deltas ?? [] };
}
function permitsObservedDescent(shape, observedNewLowDescents) { return observedNewLowDescents === 0 || Number(shape.descent_to_final_reachable_low?.max) >= observedNewLowDescents; }
function directionOf(shapeId) { if (shapeId.includes("_UP_")) return "UP"; if (shapeId.includes("_DOWN_")) return "DOWN"; if (shapeId.includes("_FLAT_")) return "FLAT"; return "UNKNOWN"; }
function inverseDirection(direction) { return direction === "UP" ? "DOWN" : direction === "DOWN" ? "UP" : direction; }
function currentPathDirection(leg) { if (!leg?.last) return "UNKNOWN"; return leg.last.prefix.ask_net < 0 ? "DOWN" : leg.last.prefix.ask_net > 0 ? "UP" : "FLAT"; }
function directionObserved(leg, direction) { if (!leg.last || !leg.last.ask_change_after_first_timestamp) return false; const net = leg.last.prefix.ask_net; return direction === "UP" ? net > 0 : direction === "DOWN" ? net < 0 : direction === "FLAT" ? net === 0 : false; }
function evaluateDynamicPairWiringEvidence({ leg, sibling, dwellSeconds, survivingTuples, legRole }) {
  const inherited = evaluatePairWiringEvidence({ leg, sibling, dwellSeconds, survivingTuples, legRole });
  if (inherited.inverse_sibling_resolved || survivingTuples.length !== 1 || survivingTuples[0].support_class !== "CURRENT_PREFIX_INVERSE_CLOSURE_AFTER_MACRO_RECLASSIFICATION") return inherited;
  const tuple = survivingTuples[0], siblingRole = legRole === "highShape" ? "lowShape" : "highShape", ownShapeStillAlive = leg.survivor_shapes.includes(tuple[legRole]), siblingShapeStillAlive = sibling.survivor_shapes.includes(tuple[siblingRole]), ownDirection = currentPathDirection(leg), siblingDirection = currentPathDirection(sibling), siblingMicro = evaluateMicroPositionEvidence({ leg: sibling, sibling: null, dwellSeconds });
  const proven = ownShapeStillAlive && siblingShapeStillAlive && ownDirection !== "FLAT" && inverseDirection(ownDirection) === siblingDirection && siblingMicro.own_micro_position_observed;
  return { ...inherited, inverse_sibling_resolved: proven, inverse_sibling_proof_type: proven ? "CURRENT_PREFIX_INVERSE_PAIR_WITH_SIBLING_OWN_MICRO_RECEIPT" : null };
}
function capacityAtOrBelow(row, limit) { return row.asks.filter(([price]) => price <= limit).reduce((sum, x) => sum + x[1], 0); }
function preActionEvidence(leg) {
  const row = leg?.last;
  if (!row) return null;
  return {
    first_book: row.first_book,
    current_book: { timestamp_epoch: row.ts, bid: row.bid, ask: row.ask, last_traded: row.carried_last, spread: row.spread, top_ask_size: row.top_ask_size, top_five_ask_depth: row.top5_ask_depth, receipt: row.receipt },
    seconds_since_first_formed_book: row.ts - row.first_book.timestamp_epoch,
    raw_receipt_rows: row.raw_row_count,
    second_distinct_receipts: row.second_distinct_receipt_count,
    distinct_bbo_states: row.distinct_bbo_state_count,
    distinct_ask_prices: row.distinct_ask_count,
    ask_changes: row.ask_change_count,
    ask_descents: row.ask_descent_count,
    new_low_descents: row.new_low_descent_count,
    ask_rises: row.ask_rise_count,
    ask_net_cents: row.prefix.ask_net,
    ask_dip_cents: row.prefix.ask_dip,
    ask_peak_cents: row.ask_peak_cents,
    top_ask_size_ever_changed: row.top_ask_size_ever_changed,
  };
}
function downsample(rows, max = 1400) { if (rows.length <= max) return rows; const step = (rows.length - 1) / (max - 1), out = []; for (let i = 0; i < max; i += 1) out.push(rows[Math.round(i * step)]); return out; }

function replayGame(eventId, sources, library, refs) {
  const legs = sources.map((source) => { const loaded = loadRows(source); return { ...source, source_receipt: loaded.source, rows: prefixRows(loaded.rows, source.left, source.right), first_book_ts: loaded.rows[0].ts, first_book_receipt: loaded.rows[0].receipt, first_ask: loaded.rows[0].ask, first_bid: loaded.rows[0].bid, price_region: region(loaded.rows[0].bid), order: null, fill: null, last: null, survivor_shapes: null, decisions: [] }; });
  legs.sort((a, b) => a.leg.localeCompare(b.leg)); const high = [...legs].sort((a, b) => b.first_ask - a.first_ask || a.leg.localeCompare(b.leg))[0], low = legs.find((x) => x !== high), pairKey = `${high.category}|${high.price_region}|${low.price_region}`, tuplesObject = library.pair_shape_tuples[pairKey] || {};
  const observedTuples = Object.keys(tuplesObject).map((key) => { const [highShape, lowShape] = key.split("|"); return { highShape, lowShape, n: tuplesObject[key], support_class: "EMPIRICALLY_OBSERVED_PAIR_TUPLE" }; });
  const allTuples = pairWiringV3 ? completePairTupleSupport({ observedTupleObject: tuplesObject, highShapes: library.groups[`${high.category}|${high.price_region}`].shapes.map((shape) => shape.shape_id), lowShapes: library.groups[`${low.category}|${low.price_region}`].shapes.map((shape) => shape.shape_id) }) : observedTuples;
  for (const leg of legs) { const group = library.groups[`${leg.category}|${leg.price_region}`]; if (!group) throw new Error(`missing shape group ${leg.category}|${leg.price_region}`); leg.group = group; leg.all_shape_ids = group.shapes.map((s) => s.shape_id); leg.survivor_shapes = [...leg.all_shape_ids]; leg.resolved_direction = null; leg.independent_direction = null; leg.macro_reclassifications = []; }
  let tuples = allTuples, indices = Object.fromEntries(legs.map((l) => [l.leg, 0])); const dynamicPairClosures = [], clock = [...new Set(legs.flatMap((l) => l.rows.map((r) => r.ts)))].sort((a, b) => a - b);
  for (const ts of clock) {
    const changedThisTick = {}, contradictions = [];
    for (const leg of legs) {
      let changed = false; while (indices[leg.leg] < leg.rows.length && leg.rows[indices[leg.leg]].ts <= ts) { leg.last = leg.rows[indices[leg.leg]++]; changed = true; }
      changedThisTick[leg.leg] = changed;
      // Do not let a low/sibling leg collapse before the other book exists.
      // The first resolved direction is then an exact inverse constraint on its sibling.
      if (changed && (leg === high || high.last)) {
        leg.survivor_shapes = compatibleShapes(leg.group, leg.last, leg.survivor_shapes);
        const descentCapable = dynamicRenarrowV6 && leg.last.new_low_descent_count > 0 ? leg.all_shape_ids.filter((shapeId) => permitsObservedDescent(leg.group.shapes.find((shape) => shape.shape_id === shapeId), leg.last.new_low_descent_count)) : [];
        if (descentCapable.length && !leg.survivor_shapes.some((shapeId) => permitsObservedDescent(leg.group.shapes.find((shape) => shape.shape_id === shapeId), leg.last.new_low_descent_count))) {
          contradictions.push({ leg, staleShapes: [...leg.survivor_shapes], descentCapable });
        }
      }
    }
    if (contradictions.length) {
      for (const leg of legs) {
        leg.resolved_direction = null; leg.independent_direction = null;
        if (!leg.last) { leg.survivor_shapes = [...leg.all_shape_ids]; continue; }
        const contradicted = contradictions.find((item) => item.leg === leg), candidates = contradicted ? contradicted.descentCapable : leg.all_shape_ids;
        leg.survivor_shapes = compatibleShapes(leg.group, leg.last, candidates);
      }
      for (const item of contradictions) {
        item.leg.macro_reclassifications.push({ timestamp_epoch: item.leg.last.ts, receipt: item.leg.last.receipt, observed_new_low_descents: item.leg.last.new_low_descent_count, eliminated_stale_shapes: item.staleShapes, reopened_candidate_shapes: item.descentCapable, re_narrowed_shapes: [...item.leg.survivor_shapes], joint_re_narrowed_shapes: Object.fromEntries(legs.map((leg) => [leg.leg, [...leg.survivor_shapes]])), joint_current_path_directions: Object.fromEntries(legs.map((leg) => [leg.leg, currentPathDirection(leg)])), sibling_macro_reopened_before_lower_layers: true, reason: "OBSERVED_DESCENT_ORDINAL_EXCEEDED_EVERY_SURVIVING_SHAPE" });
      }
    }
    for (const leg of legs) {
      const directions = [...new Set(leg.survivor_shapes.map(directionOf))];
      if (!leg.independent_direction && directions.length === 1 && directions[0] !== "UNKNOWN") leg.independent_direction = directions[0];
      if (!leg.resolved_direction && directions.length === 1 && directions[0] !== "UNKNOWN") leg.resolved_direction = directions[0];
    }
    for (const sourceLeg of legs) {
      if (!sourceLeg.resolved_direction) continue; const sibling = legs.find((leg) => leg !== sourceLeg); if (sibling.resolved_direction) continue;
      const required = inverseDirection(sourceLeg.resolved_direction), constrained = sibling.survivor_shapes.filter((shapeId) => directionOf(shapeId) === required); if (constrained.length) sibling.survivor_shapes = constrained;
    }
    tuples = (dynamicRenarrowV6 ? allTuples : tuples).filter((t) => high.survivor_shapes.includes(t.highShape) && low.survivor_shapes.includes(t.lowShape));
    if (dynamicRenarrowV6 && !tuples.length && high.last && low.last && currentPathDirection(high) !== "FLAT" && inverseDirection(currentPathDirection(high)) === currentPathDirection(low)) {
      tuples = high.survivor_shapes.flatMap((highShape) => low.survivor_shapes.map((lowShape) => ({ highShape, lowShape, n: 0, support_class: "CURRENT_PREFIX_INVERSE_CLOSURE_AFTER_MACRO_RECLASSIFICATION", high_current_path_direction: currentPathDirection(high), low_current_path_direction: currentPathDirection(low), high_receipt: high.last.receipt, low_receipt: low.last.receipt })));
      dynamicPairClosures.push({ timestamp_epoch: ts, high_leg: high.leg, low_leg: low.leg, high_current_path_direction: currentPathDirection(high), low_current_path_direction: currentPathDirection(low), high_shapes: [...high.survivor_shapes], low_shapes: [...low.survivor_shapes], tuple_count: tuples.length, high_receipt: high.last.receipt, low_receipt: low.last.receipt });
    }
    for (const leg of legs) {
      if (!leg.last || leg.fill) continue; const elapsedSinceOwnTick = ts - leg.last.ts, row = { ...leg.last, ts, ask_dwell_seconds: leg.last.ask_dwell_seconds + elapsedSinceOwnTick, progress_bin: Math.max(0, Math.min(100, Math.floor((ts - leg.left) / (leg.right - leg.left) * 100))), macro_reclassified: leg.macro_reclassifications.length > 0 };
      const fillRow = stableSamePriceConfirmation ? leg.last : row;
      const distinctStrictlyLaterFillReceipt = stableSamePriceConfirmation ? fillRow.ts > leg.order?.action_ts && fillRow.receipt !== leg.order?.own_book_receipt_at_action : row.ts > leg.order?.action_ts;
      if (leg.order && distinctStrictlyLaterFillReceipt && fillRow.ask <= leg.order.price_cents && fillRow.ask_dwell_seconds >= DWELL_SECONDS && capacityAtOrBelow(fillRow, leg.order.price_cents) >= QUANTITY) { leg.fill = { price_cents: leg.order.price_cents, quantity: QUANTITY, evidence_ts: fillRow.ts, evidence_receipt: fillRow.receipt, evidence_type: "STRICTLY_LATER_ASK_DWELL_AND_DISPLAYED_CAPACITY", ask_cents: fillRow.ask, ask_dwell_seconds: fillRow.ask_dwell_seconds, capacity: capacityAtOrBelow(fillRow, leg.order.price_cents) }; leg.decisions.push({ ts: fillRow.ts, state: "FILLED", receipt: fillRow.receipt, order: leg.order, fill: leg.fill }); continue; }
      if (leg.order) continue;
      const role = leg === high ? "highShape" : "lowShape", shapes = [...new Set(tuples.map((t) => t[role]))], verdicts = shapes.map((id) => ({ shape_id: id, ...shapeVerdict(leg.group, id, row.progress_bin, row, excludeOwnTrainingMember ? eventId : null) })); let state = "INSUFFICIENT_EVIDENCE", reason = "SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP";
      if (row.raw_row_count < 2) reason = "NO_PRIOR_IN_WINDOW_BOOK";
      else if (shapes.length && verdicts.some((x) => x.descent_adjustment === "OBSERVED_DESCENT_OUTSIDE_SHAPE_TRAINING_SUPPORT")) reason = "OBSERVED_DESCENT_OUTSIDE_SURVIVING_SHAPE_TRAINING_SUPPORT";
      else if (shapes.length && verdicts.every((x) => x.verdict === "LOWER")) { state = "HOLD"; reason = "ALL_SURVIVING_SHAPES_SAY_LOWER"; }
      else if (shapes.length && verdicts.every((x) => x.verdict === "FLOOR")) {
        const sibling = legs.find((candidate) => candidate !== leg);
        const legRole = leg === high ? "highShape" : "lowShape";
        const microEvidence = pairWiringV3 ? dynamicRenarrowV6 ? evaluateDynamicPairWiringEvidence({ leg, sibling, dwellSeconds: DWELL_SECONDS, survivingTuples: tuples, legRole }) : evaluatePairWiringEvidence({ leg, sibling, dwellSeconds: DWELL_SECONDS, survivingTuples: tuples, legRole }) : stableSamePriceConfirmation ? evaluateMicroPositionEvidence({ leg, sibling, dwellSeconds: DWELL_SECONDS }) : { own_micro_position_observed: leg.last.ask_change_after_first_timestamp, evidence_type: leg.last.ask_change_after_first_timestamp ? "ASK_PRICE_TRANSITION" : null, stable_same_price_receipt: false, inverse_sibling_resolved: Boolean(leg.resolved_direction && sibling.independent_direction && inverseDirection(leg.resolved_direction) === sibling.independent_direction && directionObserved(sibling, sibling.independent_direction)) };
        const inverseSiblingResolved = microEvidence.inverse_sibling_resolved, stableSamePriceReceipt = microEvidence.stable_same_price_receipt, ownMicroPositionObserved = microEvidence.own_micro_position_observed, microPositionEvidenceType = microEvidence.evidence_type;
        const stableSigningSupport = stableSignerV4 ? evaluateStableAskSigningSupport({ leg, sibling, inverseSiblingResolved }) : { required: false, supported: true, support_type: "V4_DISABLED", predicates: {} };
        if (!ownMicroPositionObserved) reason = "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED";
        else if (!inverseSiblingResolved) reason = "FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED";
        else if (!stableSigningSupport.supported) reason = "FLOOR_CONSENSUS_BUT_STABLE_SAME_PRICE_ASK_LACKS_SIGNING_SUPPORT";
        else if (row.prefix.ask_net !== row.prefix.ask_dip) reason = "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW";
        else if (row.ask_dwell_seconds >= DWELL_SECONDS && row.top_ask_size >= QUANTITY && stableSignerV4 && !changedThisTick[leg.leg]) reason = "FLOOR_CONSENSUS_AWAITING_FRESH_OWN_BOOK_RECEIPT";
        else if (row.ask_dwell_seconds >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) { state = "PLACE"; reason = stableSamePriceReceipt && !leg.last.ask_change_after_first_timestamp ? "ALL_SURVIVING_PAIR_CONSTRAINED_SHAPES_SAY_FLOOR_AND_STABLE_SAME_PRICE_ASK_IS_EXECUTABLE" : "ALL_SURVIVING_PAIR_CONSTRAINED_SHAPES_SAY_FLOOR_AND_ASK_IS_EXECUTABLE"; }
        else reason = "FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY";
        row.micro_position_evidence_type = microPositionEvidenceType;
        row.stable_same_price_receipt = stableSamePriceReceipt;
        row.inverse_sibling_resolved = inverseSiblingResolved;
        row.inverse_sibling_proof_type = microEvidence.inverse_sibling_proof_type ?? null;
        row.stable_signing_support = stableSigningSupport;
      }
      if (state === "PLACE") { const sibling = legs.find((candidate) => candidate !== leg), baseOrder = { price_cents: row.ask, quantity: QUANTITY, action_ts: ts, action_receipt: row.receipt, same_receipt_fill_forbidden: true, surviving_shapes: verdicts, pair_shape_tuples: tuples.map((t) => ({ ...t })), inverse_sibling_proof_type: row.inverse_sibling_proof_type ?? null, stable_signing_support: row.stable_signing_support ?? null, pre_action_evidence: { own: preActionEvidence(leg), sibling: preActionEvidence(sibling) } }; leg.order = stableSamePriceConfirmation ? { ...baseOrder, action_receipt: changedThisTick[leg.leg] ? leg.last.receipt : sibling.last?.receipt, own_book_receipt_at_action: leg.last.receipt, own_book_ts_at_action: leg.last.ts, sibling_book_receipt_at_action: sibling.last?.receipt ?? null, sibling_book_ts_at_action: sibling.last?.ts ?? null, micro_position_evidence_type: row.micro_position_evidence_type ?? "ASK_PRICE_TRANSITION" } : baseOrder; }
      const prior = leg.decisions[leg.decisions.length - 1]; if (!prior || prior.state !== state || prior.reason !== reason || state === "PLACE") leg.decisions.push({ ts, state, reason, book: { bid: row.bid, ask: row.ask, spread: row.spread, carried_last: row.carried_last, ask_dwell_seconds: row.ask_dwell_seconds, ask_net: row.prefix.ask_net, ask_dip: row.prefix.ask_dip, ask_change_after_first_timestamp: row.ask_change_after_first_timestamp, ...(stableSamePriceConfirmation ? { strictly_later_same_price_ask_receipt: leg.last.strictly_later_same_price_ask_receipt, stable_same_price_receipt: row.stable_same_price_receipt ?? false, stable_signing_support: row.stable_signing_support ?? null, micro_position_evidence_type: row.micro_position_evidence_type ?? null, inverse_sibling_resolved: row.inverse_sibling_resolved ?? false, inverse_sibling_proof_type: row.inverse_sibling_proof_type ?? null } : {}), top_ask_size: row.top_ask_size, top5_ask_depth: row.top5_ask_depth }, surviving_shapes: verdicts, surviving_pair_tuple_count: tuples.length, receipt: row.receipt, order: leg.order });
    }
  }
  const current = refs.current_branch.find((x) => x.event_id === eventId), corrected = refs.corrected_branch.find((x) => x.event_id === eventId);
  return { event_id: eventId, category: legs[0].category, pair_constraint: { identity: "two outcomes sum to 100", training_pair_key: pairKey, observed_pair_shape_tuples: observedTuples.length, structural_closure_enabled: pairWiringV3, initial_pair_shape_tuples: allTuples.length, final_pair_shape_tuples: tuples.length, dynamic_current_path_inverse_closures: dynamicPairClosures }, legs: Object.fromEntries(legs.map((leg) => { const ref = corrected.legs[leg.leg], entry = leg.fill?.price_cents ?? null; return [leg.leg, { ticker: leg.ticker, price_region: leg.price_region, status: leg.fill ? "CREDITED" : "INSUFFICIENT_EVIDENCE", entry_cents: entry, baseline_entry_cents: current?.legs?.[leg.leg]?.entry_cents ?? null, own_window1_close_cents: ref.own_window1_close_cents, delta_to_own_window1_close_cents: entry === null || !Number.isInteger(ref.own_window1_close_cents) ? null : entry - ref.own_window1_close_cents, own_bell_price_cents: ref.own_bell_price_cents, delta_to_own_bell_price_cents: entry === null || !Number.isInteger(ref.own_bell_price_cents) ? null : entry - ref.own_bell_price_cents, own_ask_reachable_low_cents: ref.own_ask_reachable_low_cents, delta_to_own_ask_reachable_low_cents: entry === null || !Number.isInteger(ref.own_ask_reachable_low_cents) ? null : entry - ref.own_ask_reachable_low_cents, pair_reference_cents: "NOT_BOUND", delta_to_pair_reference_cents: "NOT_BOUND", placement: leg.order, fill: leg.fill, macro_reclassifications: leg.macro_reclassifications, surviving_shapes_at_placement: leg.order?.surviving_shapes || [], surviving_shapes_at_terminal: leg.survivor_shapes.map((shape_id) => ({ shape_id, direction: directionOf(shape_id) })), terminal_reason: leg.fill ? "CREDITED_ON_STRICTLY_LATER_EXECUTABLE_ASK" : leg.decisions[leg.decisions.length - 1]?.reason || "NO_LAWFUL_DECISION", decision_changes: leg.decisions, chart_rows: downsample(leg.rows.map((r) => ({ ts: r.ts, bid: r.bid, ask: r.ask, last: r.carried_last }))), source: leg.source_receipt }]; })) };
}

function svgChart(event, sources) {
  const W = 1200, H = 720, left = 64, right = 25, top = 42, panelH = 270, gap = 75, plotW = W - left - right, colors = { bid: "#2563eb", ask: "#f59e0b", last: "#64748b", order: "#dc2626" };
  const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); let body = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="100%" height="100%" fill="white"/><style>text{font-family:Arial,sans-serif;fill:#111827}.axis{stroke:#9ca3af;stroke-width:1}.grid{stroke:#e5e7eb;stroke-width:1}.bid{stroke:${colors.bid}}.ask{stroke:${colors.ask}}.last{stroke:${colors.last}}.order{stroke:${colors.order};stroke-width:2}.line{fill:none;stroke-width:1.3}</style><text x="${left}" y="24" font-size="17" font-weight="bold">${esc(event.event_id)} -- quote-shape elimination replay</text>`;
  const legs = Object.entries(event.legs).sort();
  legs.forEach(([legId, leg], index) => { const y0 = top + index * (panelH + gap), rows = leg.chart_rows, source = sources.find((x) => x.leg === legId), minTs = source.left, maxTs = source.right, vals = rows.flatMap((r) => [r.bid, r.ask, r.last]).filter(Number.isFinite), minP = Math.max(0, Math.min(...vals) - 2), maxP = Math.min(100, Math.max(...vals) + 2), x = (ts) => left + (ts - minTs) / (maxTs - minTs) * plotW, y = (p) => y0 + panelH - (p - minP) / Math.max(1, maxP - minP) * panelH;
    for (let p = Math.ceil(minP / 10) * 10; p <= maxP; p += 10) { body += `<line class="grid" x1="${left}" y1="${y(p)}" x2="${W-right}" y2="${y(p)}"/><text x="${left-9}" y="${y(p)+4}" font-size="11" text-anchor="end">${p}</text>`; }
    body += `<line class="axis" x1="${left}" y1="${y0+panelH}" x2="${W-right}" y2="${y0+panelH}"/><text x="${left}" y="${y0-10}" font-size="15" font-weight="bold">${legId}: ${leg.status}; entry ${leg.entry_cents ?? "n/a"}; low ${leg.own_ask_reachable_low_cents}</text>`;
    for (const [key, cls] of [["bid","bid"],["ask","ask"],["last","last"]]) body += `<polyline class="line ${cls}" points="${rows.filter((r) => Number.isFinite(r[key])).map((r) => `${x(r.ts).toFixed(1)},${y(r[key]).toFixed(1)}`).join(" ")}"/>`;
    if (leg.placement) { const end = leg.fill?.evidence_ts || maxTs; body += `<line class="order" x1="${x(leg.placement.action_ts)}" y1="${y(leg.placement.price_cents)}" x2="${x(end)}" y2="${y(leg.placement.price_cents)}"/><circle cx="${x(leg.placement.action_ts)}" cy="${y(leg.placement.price_cents)}" r="4" fill="${colors.order}"/>`; }
    for (let m = 0; m <= 4; m += 1) { const ts = minTs + (maxTs-minTs)*m/4, sched = Math.round((source.scheduled-ts)/60), bell = Math.round((source.bell-ts)/60); body += `<text x="${x(ts)}" y="${y0+panelH+18}" font-size="10" text-anchor="middle">T-${sched}s / T-${bell}b</text>`; }
  });
  body += `<g transform="translate(${left},${H-28})"><line class="bid" x1="0" y1="0" x2="28" y2="0"/><text x="34" y="4" font-size="11">bid</text><line class="ask" x1="80" y1="0" x2="108" y2="0"/><text x="114" y="4" font-size="11">ask</text><line class="last" x1="160" y1="0" x2="188" y2="0"/><text x="194" y="4" font-size="11">carried last</text><line class="order" x1="285" y1="0" x2="313" y2="0"/><text x="319" y="4" font-size="11">our order</text></g></svg>`; return body;
}

function compactEvent(event) {
  if (event.replay_status === "SOURCE_UNAVAILABLE") return event;
  return {
    event_id: event.event_id,
    category: event.category,
    replay_status: "AVAILABLE",
    pair_constraint: event.pair_constraint,
    legs: Object.fromEntries(Object.entries(event.legs).map(([legId, leg]) => {
      const place = (leg.decision_changes || []).find((row) => row.state === "PLACE" && row.order?.action_ts === leg.placement?.action_ts) || null;
      const actionBook = place?.book || null;
      const exactActionBook = Boolean(leg.placement && leg.placement.own_book_ts_at_action === leg.placement.action_ts && leg.placement.own_book_receipt_at_action === leg.placement.action_receipt);
      const displayedCapacity = actionBook && actionBook.ask <= leg.placement?.price_cents ? Number(actionBook.top_ask_size) : 0;
      const provenTakerAtAction = exactActionBook && Number.isFinite(displayedCapacity) && displayedCapacity >= QUANTITY;
      return [legId, {
        ticker: leg.ticker,
        price_region: leg.price_region,
        replay_status: leg.status,
        proposed_entry_cents: leg.placement?.price_cents ?? null,
        replay_later_receipt_entry_cents: leg.entry_cents,
        honest_fill_class: provenTakerAtAction ? "PROVEN_TAKER" : "UNPROVEN",
        honest_credited_entry_cents: provenTakerAtAction ? leg.placement.price_cents : null,
        action_book_exact: exactActionBook,
        displayed_opposing_capacity_at_or_below_x: displayedCapacity,
        own_window1_close_cents: leg.own_window1_close_cents,
        own_bell_price_cents: leg.own_bell_price_cents,
        own_ask_reachable_low_cents: leg.own_ask_reachable_low_cents,
        delta_to_own_window1_close_cents: provenTakerAtAction && Number.isInteger(leg.own_window1_close_cents) ? leg.placement.price_cents - leg.own_window1_close_cents : null,
        delta_to_own_bell_price_cents: provenTakerAtAction && Number.isInteger(leg.own_bell_price_cents) ? leg.placement.price_cents - leg.own_bell_price_cents : null,
        delta_to_own_ask_reachable_low_cents: provenTakerAtAction && Number.isInteger(leg.own_ask_reachable_low_cents) ? leg.placement.price_cents - leg.own_ask_reachable_low_cents : null,
        pair_reference_cents: "NOT_BOUND",
        delta_to_pair_reference_cents: "NOT_BOUND",
        placement: leg.placement,
        replay_later_receipt_fill: leg.fill,
        action_book: actionBook,
        macro_reclassifications: leg.macro_reclassifications,
        surviving_shapes_at_placement: leg.surviving_shapes_at_placement,
        surviving_shapes_at_terminal: leg.surviving_shapes_at_terminal,
        terminal_reason: leg.terminal_reason,
        source: leg.source,
      }];
    })),
  };
}

function unavailableEvent(eventId, sources, error) {
  return {
    event_id: eventId,
    category: sources?.[0]?.category ?? null,
    replay_status: "SOURCE_UNAVAILABLE",
    reason: error instanceof Error ? error.message : String(error),
    legs: Object.fromEntries((sources || []).map((source) => [source.leg, {
      ticker: source.ticker,
      price_region: null,
      replay_status: "SOURCE_UNAVAILABLE",
      proposed_entry_cents: null,
      honest_fill_class: "UNPROVEN",
      honest_credited_entry_cents: null,
      pair_reference_cents: "NOT_BOUND",
      delta_to_pair_reference_cents: "NOT_BOUND",
      own_window1_close_cents: source.own_window1_close_cents ?? null,
      own_bell_price_cents: source.own_bell_price_cents ?? null,
      own_ask_reachable_low_cents: source.own_ask_reachable_low_cents ?? null,
      delta_to_own_window1_close_cents: null,
      delta_to_own_bell_price_cents: null,
      delta_to_own_ask_reachable_low_cents: null,
      terminal_reason: "SOURCE_UNAVAILABLE",
    }])),
  };
}

function main() {
  const library = JSON.parse(fs.readFileSync(libraryPath));
  const refs = JSON.parse(fs.readFileSync(refsPath));
  const windowsReceipt = JSON.parse(fs.readFileSync(frozenFivePath));
  const windows = Object.fromEntries(windowsReceipt.events.map((event) => [event.event_id, event.window]));
  const raw = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/);
  const headers = raw.shift().split(",");
  const quoteRows = raw.map((line) => Object.fromEntries(line.split(",").map((item, index) => [headers[index], item])));
  const refByEvent = Object.fromEntries((refs.corrected_branch || []).map((event) => [event.event_id, event]));
  const sourcesByEvent = {};
  for (const row of quoteRows) if (TARGETS.has(row.event_id)) {
    const ref = refByEvent[row.event_id]?.legs?.[row.leg] || {};
    if (!sourcesByEvent[row.event_id]) sourcesByEvent[row.event_id] = [];
    sourcesByEvent[row.event_id].push({ event_id: row.event_id, category: row.category, leg: row.leg, ticker: row.ticker, left: Number(row.left_ts), right: Number(row.right_ts), scheduled: Number(row.scheduled_start_ts), bell: Number.isFinite(Number(windows[row.event_id]?.actual_bell_ts)) ? Number(windows[row.event_id].actual_bell_ts) : null, own_window1_close_cents: ref.own_window1_close_cents ?? null, own_bell_price_cents: ref.own_bell_price_cents ?? null, own_ask_reachable_low_cents: ref.own_ask_reachable_low_cents ?? null });
  }
  const fullEvents = [...TARGETS].sort().map((eventId) => {
    try { return replayGame(eventId, sourcesByEvent[eventId], library, refs); }
    catch (error) { return unavailableEvent(eventId, sourcesByEvent[eventId], error); }
  });
  const events = compactPopulation ? fullEvents.map(compactEvent) : fullEvents;
  const receipt = {
    schema_version: dynamicRenarrowV6 ? "WINDOW1_QUOTE_SHAPE_DYNAMIC_RENARROW_REPLAY_V6" : "WINDOW1_QUOTE_SHAPE_REPLAY",
    cold: true,
    outcome_knowledge_consumed: false,
    score_free: true,
    library_sha256: sha256(fs.readFileSync(libraryPath)),
    descent_verdict_v5: descentVerdictV5,
    dynamic_renarrow_v6: dynamicRenarrowV6,
    compact_population: compactPopulation,
    own_training_member_excluded_from_causal_nearest_member_selection: excludeOwnTrainingMember,
    aggregate_library_fit_disclosure: compactPopulation ? "The aggregate quote-shape library was fitted on the development population except the frozen five. The target event is excluded from causal nearest-member selection, but aggregate envelopes remain in-sample for non-five rows; this 804 diagnostic is not holdout validation." : null,
    decision_law: { states: ["PLACE", "HOLD", "INSUFFICIENT_EVIDENCE"], dwell_seconds: DWELL_SECONDS, exact_quantity: QUANTITY, macro: "dynamic contradiction-driven re-narrowing before lower layers", pair: "inverse pair wiring and current-prefix closure", micro: "causal prefix position within surviving shapes", micro_micro: "fresh ask receipt, dwell and displayed ask capacity", fill: "replay later-receipt credit is retained separately; honest PROVEN_TAKER is derived from exact action-time opposing ask capacity in the compact population receipt" },
    events,
  };
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, receiptName), canonical(receipt));
  if (!noCharts) for (const event of fullEvents.filter((item) => item.replay_status !== "SOURCE_UNAVAILABLE")) {
    const shortName = stableSamePriceConfirmation ? event.event_id.replace(/^KX(?:ATP|WTA)(?:CHALLENGER)?MATCH-26JUL\d+/, "") : event.event_id.includes("NIKVRB") ? "NIKVRB" : "HURBIG";
    fs.writeFileSync(path.join(outDir, `${shortName}_QUOTE_SHAPE_REPLAY.svg`), svgChart(event, sourcesByEvent[event.event_id]));
  }
  process.stdout.write(canonical({ status: "BUILT", event_count: events.length, unavailable: events.filter((event) => event.replay_status === "SOURCE_UNAVAILABLE").length, receipt: path.join(outDir, receiptName) }));
}

main();
