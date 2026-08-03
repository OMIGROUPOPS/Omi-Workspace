#!/usr/bin/env node
"use strict";

// Score-free quote-shape refit. Classes are supervised by the number of
// capacity-and-dwell-qualified ask descents before the final reachable low.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

const GRID = 100, DWELL_SECONDS = 10, QUANTITY = 5, MIN_CLASS_N = 20;
const EXCLUDED_EVENTS = [
  "KXATPCHALLENGERMATCH-26JUL19HURBIG",
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
  "KXATPMATCH-26JUL12LAJVAN",
  "KXWTACHALLENGERMATCH-26JUL16BRAVED",
  "KXWTAMATCH-26JUL20KORJIM",
];
const PREFIX_KEYS = ["ask_net", "ask_dip", "ask_peak", "ask_drawdown_from_peak", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "ask_dwell_fraction", "mean_log_top_ask_size", "mean_log_top5_ask_depth", "qualified_ask_descent_count", "qualified_ask_rise_count"];
const FINAL_KEYS = ["ask_net", "ask_dip", "ask_peak", "ask_drawdown_from_peak", "first_min_progress", "floor_dwell_fraction", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "median_ask_episode_dwell", "mean_log_top_ask_size", "mean_log_top5_ask_depth", "qualified_ask_descent_count", "qualified_ask_rise_count"];

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function median(values) { const s = [...values].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : null; }
function quantile(values, p) { const s = [...values].sort((a, b) => a - b); return s.length ? s[Math.min(s.length - 1, Math.floor(p * (s.length - 1)))] : null; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null;
  let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line, index) => ({ raw: Object.fromEntries(line.split(",").map((v, i) => [headers[i], v])), ordinal: index + 2 })); }
function oldTopology(row) {
  const f = row.final_features;
  if (f.ask_net < 0) return f.ask_net === f.ask_dip ? "DOWN_CONTINUATION" : "DOWN_REBOUND";
  if (f.ask_net > 0) return f.ask_dip < 0 ? "UP_AFTER_DIP" : "UP_CONTINUATION";
  return f.ask_dip < 0 ? "FLAT_RECOVERED" : "FLAT_UNMOVED";
}
function direction(row) { return row.final_features.ask_net < 0 ? "DOWN" : row.final_features.ask_net > 0 ? "UP" : "FLAT"; }

function scanOne(source, ticksRoot) {
  const file = path.join(ticksRoot, `${source.ticker}.csv.gz`), bytes = fs.readFileSync(file), rows = [];
  for (const { raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et); if (ts === null || ts < Number(source.left_ts) || ts > Number(source.right_ts)) continue;
    const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) {
      const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1], top5_ask_depth: asks.reduce((sum, x) => sum + x[1], 0), receipt: `${path.basename(file)}#row-${ordinal}` });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  const formed = rows.findIndex((row) => row.spread === 1);
  if (formed < 0) return { event_id: source.event_id, leg_id: source.leg, ticker: source.ticker, category: source.category, status: rows.length ? "NO_ONE_TICK_FORMED_BOOK" : "NO_LAWFUL_BBO", source: { file: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) } };
  rows.splice(0, formed);
  const left = Number(source.left_ts), right = Number(source.right_ts), duration = right - left, firstAsk = rows[0].ask;
  let state = null, rowIndex = 0, rowCount = 0, askChanges = 0, minAsk = null, maxAsk = null, firstMinTs = null, lastAskChange = null, observedDuration = 0, spreadIntegral = 0, sizeIntegral = 0, depthIntegral = 0, spreadMin = null, spreadMax = null, floorDwell = 0;
  let qualifiedAsk = null, qualifiedStart = null, qualifiedRecorded = false, previousQualifiedAsk = null, qualifiedDescents = 0, qualifiedRises = 0;
  const episodeDwells = [], qualifiedWitnesses = [], grids = [];
  function integrate(ts) { if (!state) return; const dt = Math.max(0, ts - state.integrated_to); spreadIntegral += state.spread * dt; sizeIntegral += Math.log1p(state.top_ask_size) * dt; depthIntegral += Math.log1p(state.top5_ask_depth) * dt; observedDuration += dt; if (state.ask === minAsk) floorDwell += dt; state.integrated_to = ts; }
  function consume(row) {
    integrate(row.ts);
    if (!state) { minAsk = maxAsk = row.ask; firstMinTs = lastAskChange = row.ts; }
    if (qualifiedAsk === null || row.ask !== qualifiedAsk) { qualifiedAsk = row.ask; qualifiedStart = row.ts; qualifiedRecorded = false; }
    if (state && row.ask !== state.ask) { episodeDwells.push(row.ts - lastAskChange); askChanges += 1; lastAskChange = row.ts; }
    if (!qualifiedRecorded && row.ts - qualifiedStart >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) {
      if (previousQualifiedAsk !== null) { if (row.ask < previousQualifiedAsk) qualifiedDescents += 1; else if (row.ask > previousQualifiedAsk) qualifiedRises += 1; }
      previousQualifiedAsk = row.ask; qualifiedRecorded = true;
      qualifiedWitnesses.push({ ask_cents: row.ask, descent_ordinal: qualifiedDescents, timestamp_epoch: row.ts, receipt: row.receipt, top_ask_size: row.top_ask_size });
    }
    const previousMin = minAsk; minAsk = Math.min(minAsk, row.ask); maxAsk = Math.max(maxAsk, row.ask); if (row.ask < previousMin) firstMinTs = row.ts;
    spreadMin = spreadMin === null ? row.spread : Math.min(spreadMin, row.spread); spreadMax = spreadMax === null ? row.spread : Math.max(spreadMax, row.spread); rowCount += 1; state = { ...row, integrated_to: row.ts };
  }
  for (let g = 0; g <= GRID; g += 1) {
    const cutoff = left + duration * g / GRID; while (rowIndex < rows.length && rows[rowIndex].ts <= cutoff) consume(rows[rowIndex++]); integrate(cutoff);
    if (!state) { grids.push(null); continue; }
    const elapsed = Math.max(1, cutoff - left), obs = Math.max(1, observedDuration);
    grids.push({ ask_net: state.ask - firstAsk, ask_dip: minAsk - firstAsk, ask_peak: maxAsk - firstAsk, ask_drawdown_from_peak: maxAsk - state.ask, mean_spread: spreadIntegral / obs, spread_range: spreadMax - spreadMin, quote_rate: rowCount * 3600 / elapsed, ask_change_rate: askChanges * 3600 / elapsed, ask_dwell_fraction: Math.max(0, cutoff - lastAskChange) / elapsed, mean_log_top_ask_size: sizeIntegral / obs, mean_log_top5_ask_depth: depthIntegral / obs, qualified_ask_descent_count: qualifiedDescents, qualified_ask_rise_count: qualifiedRises, current_ask: state.ask, remaining_qualified_low_delta: null });
  }
  while (rowIndex < rows.length) consume(rows[rowIndex++]); integrate(right); if (state) episodeDwells.push(right - lastAskChange);
  const finalLow = qualifiedWitnesses.length ? Math.min(...qualifiedWitnesses.map((x) => x.ask_cents)) : null, floorWitness = finalLow === null ? null : qualifiedWitnesses.find((x) => x.ask_cents === finalLow);
  for (let g = 0; g <= GRID; g += 1) if (grids[g]) { const cutoff = left + duration * g / GRID, future = qualifiedWitnesses.filter((x) => x.timestamp_epoch >= cutoff); grids[g].remaining_qualified_low_delta = future.length ? Math.min(...future.map((x) => x.ask_cents)) - grids[g].current_ask : null; }
  const final = grids[GRID], finalFeatures = { ask_net: rows[rows.length - 1].ask - firstAsk, ask_dip: Math.min(...rows.map((r) => r.ask)) - firstAsk, ask_peak: Math.max(...rows.map((r) => r.ask)) - firstAsk, ask_drawdown_from_peak: Math.max(...rows.map((r) => r.ask)) - rows[rows.length - 1].ask, first_min_progress: (firstMinTs - left) / duration, floor_dwell_fraction: floorDwell / Math.max(1, observedDuration), mean_spread: final.mean_spread, spread_range: final.spread_range, quote_rate: rows.length * 3600 / duration, ask_change_rate: askChanges * 3600 / duration, median_ask_episode_dwell: median(episodeDwells), mean_log_top_ask_size: final.mean_log_top_ask_size, mean_log_top5_ask_depth: final.mean_log_top5_ask_depth, qualified_ask_descent_count: qualifiedDescents, qualified_ask_rise_count: qualifiedRises };
  return { event_id: source.event_id, leg_id: source.leg, ticker: source.ticker, category: source.category, status: "AVAILABLE", price_region: region(rows[0].bid), first_ask: firstAsk, first_bid: rows[0].bid, final_features: finalFeatures, old_topology: oldTopology({ final_features: finalFeatures }), direction: finalFeatures.ask_net < 0 ? "DOWN" : finalFeatures.ask_net > 0 ? "UP" : "FLAT", qualified_descent_to_final_reachable_low: floorWitness ? { status: "AVAILABLE", ask_reachable_low_cents: finalLow, descent_ordinal: floorWitness.descent_ordinal, witness_timestamp_epoch: floorWitness.timestamp_epoch, witness_receipt: floorWitness.receipt, dwell_seconds: DWELL_SECONDS, quantity_contracts: QUANTITY } : { status: "NO_QUALIFIED_ASK_REACHABLE_LOW", dwell_seconds: DWELL_SECONDS, quantity_contracts: QUANTITY }, grid: grids, source: { file: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) } };
}

function workerMain() { parentPort.postMessage(workerData.sources.map((source) => scanOne(source, workerData.ticksRoot))); }
function scorePlan(plan) { return [plan.usable_members, -plan.usable_classes, -plan.segments.length]; }
function better(a, b) { if (!b) return true; const x = scorePlan(a), y = scorePlan(b); for (let i = 0; i < x.length; i += 1) if (x[i] !== y[i]) return x[i] > y[i]; return JSON.stringify(a.segments) < JSON.stringify(b.segments); }
function coherentSegments(rows) {
  const counts = new Map(); for (const row of rows) { const ordinal = row.qualified_descent_to_final_reachable_low?.descent_ordinal; if (Number.isInteger(ordinal)) counts.set(ordinal, (counts.get(ordinal) || 0) + 1); }
  const values = [...counts].sort(([a], [b]) => a - b), memo = new Map();
  function solve(i) {
    if (i >= values.length) return { usable_members: 0, usable_classes: 0, segments: [] }; if (memo.has(i)) return memo.get(i);
    const options = [];
    for (const width of [1, 2]) {
      if (i + width > values.length) continue; const chosen = values.slice(i, i + width); if (width === 2 && chosen[1][0] !== chosen[0][0] + 1) continue;
      const n = chosen.reduce((sum, x) => sum + x[1], 0), tail = solve(i + width), usable = n >= MIN_CLASS_N;
      options.push({ usable_members: tail.usable_members + (usable ? n : 0), usable_classes: tail.usable_classes + Number(usable), segments: [{ ordinals: chosen.map((x) => x[0]), n, usable }, ...tail.segments] });
    }
    const best = options.reduce((chosen, candidate) => better(candidate, chosen) ? candidate : chosen, null); memo.set(i, best); return best;
  }
  return solve(0).segments;
}
function distribution(values, total, usable) {
  const counts = Object.fromEntries([...new Set(values)].sort((a, b) => a - b).map((value) => [String(value), values.filter((x) => x === value).length])), min = values.length ? Math.min(...values) : null, max = values.length ? Math.max(...values) : null;
  return { status: usable ? "FITTED_USABLE" : "UNUSABLE_THIN_OR_HETEROGENEOUS", grain: "category + formed-book bid price region + final quote direction + coherent qualified-ask descent ordinal support", ordinal_definition: "number of capacity>=5 and dwell>=10s qualified ask-to-ask downward transitions before the first qualified occurrence of the final reachable ask low", support_n: values.length, censored_n: total - values.length, min, p25: quantile(values, .25), median: median(values), p75: quantile(values, .75), p90: quantile(values, .9), max, counts, signing_ordinal_after_a_descent_is_observed: usable ? max : null };
}
function buildShape(groupKey, directionName, memberRows, usable, suffix) {
  const shapeId = `${groupKey.replace("|", "_")}_${directionName}_COHERENT_${suffix}`, ordinalValues = memberRows.map((row) => row.qualified_descent_to_final_reachable_low?.descent_ordinal).filter(Number.isInteger), dist = distribution(ordinalValues, memberRows.length, usable);
  const envelopes = [];
  for (let g = 0; g <= GRID; g += 1) {
    const available = memberRows.map((row) => row.grid[g]).filter(Boolean), env = {};
    for (const key of PREFIX_KEYS) env[key] = available.length ? [Math.min(...available.map((x) => x[key])), Math.max(...available.map((x) => x[key]))] : null;
    if (available.length) { const means = PREFIX_KEYS.map((key) => available.reduce((sum, x) => sum + x[key], 0) / available.length), sds = PREFIX_KEYS.map((key, d) => Math.max(1e-9, Math.sqrt(available.reduce((sum, x) => sum + (x[key] - means[d]) ** 2, 0) / available.length))); env.empirical_support = { means, sds }; } else env.empirical_support = null;
    envelopes.push(env);
  }
  const medians = Object.fromEntries(FINAL_KEYS.map((key) => [key, median(memberRows.map((r) => r.final_features[key]))]));
  const medoid = memberRows.reduce((best, row) => { const score = FINAL_KEYS.reduce((sum, key) => sum + Math.abs(row.final_features[key] - medians[key]), 0), bestScore = FINAL_KEYS.reduce((sum, key) => sum + Math.abs(best.final_features[key] - medians[key]), 0); return score < bestScore ? row : best; }, memberRows[0]);
  const oldCounts = {}; for (const row of memberRows) oldCounts[`${groupKey.replace("|", "_")}_${row.old_topology}`] = (oldCounts[`${groupKey.replace("|", "_")}_${row.old_topology}`] || 0) + 1;
  return { shape_id: shapeId, topology: `${directionName}_COHERENT_QUALIFIED_ASK_DESCENT`, n: memberRows.length, usable_for_signing: usable, unusable_reason: usable ? null : memberRows.length < MIN_CLASS_N ? "SUPPORT_BELOW_20" : "ORDINAL_SUPPORT_WIDER_THAN_TWO_ADJACENT_COUNTS", old_classes_merged: oldCounts, coherence: { definition: "all signable members bottom on one exact qualified descent count or two adjacent counts", min_class_n: MIN_CLASS_N, ordinal_support_width: dist.min === null ? null : dist.max - dist.min, internally_coherent: usable && dist.max - dist.min <= 1, status: usable ? "PASS" : "UNUSABLE" }, medoid: { event_id: medoid.event_id, leg_id: medoid.leg_id, ticker: medoid.ticker }, medoid_future: medoid.grid.map((x) => x ? x.remaining_qualified_low_delta : null), member_paths: [], descent_to_final_reachable_low: dist, feature_medians: medians, envelopes };
}
function buildGroup(rows, groupKey) {
  const shapes = [], assignment = {}, byDirection = new Map(); for (const row of rows) { if (!byDirection.has(row.direction)) byDirection.set(row.direction, []); byDirection.get(row.direction).push(row); }
  for (const [directionName, directionRows] of [...byDirection].sort()) {
    const segments = coherentSegments(directionRows), claimed = new Set();
    for (const segment of segments.filter((x) => x.usable)) {
      const members = directionRows.filter((row) => segment.ordinals.includes(row.qualified_descent_to_final_reachable_low?.descent_ordinal)), suffix = `ORD_${segment.ordinals.join("_")}`, shape = buildShape(groupKey, directionName, members, true, suffix); shapes.push(shape); for (const row of members) { claimed.add(`${row.event_id}|${row.leg_id}`); assignment[`${row.event_id}|${row.leg_id}`] = shape.shape_id; }
    }
    const remainder = directionRows.filter((row) => !claimed.has(`${row.event_id}|${row.leg_id}`));
    if (remainder.length) { const shape = buildShape(groupKey, directionName, remainder, false, "UNUSABLE_REMAINDER"); shapes.push(shape); for (const row of remainder) assignment[`${row.event_id}|${row.leg_id}`] = shape.shape_id; }
  }
  const priorClassBehavior = {};
  for (const row of rows) {
    const classId = `${groupKey.replace("|", "_")}_${row.old_topology}`, ordinal = row.qualified_descent_to_final_reachable_low?.descent_ordinal, key = Number.isInteger(ordinal) ? String(ordinal) : "UNAVAILABLE";
    if (!priorClassBehavior[classId]) priorClassBehavior[classId] = { members: 0, qualified_descent_positive: 0, ordinal_counts: {} };
    priorClassBehavior[classId].members += 1; priorClassBehavior[classId].qualified_descent_positive += Number(Number.isInteger(ordinal) && ordinal > 0); priorClassBehavior[classId].ordinal_counts[key] = (priorClassBehavior[classId].ordinal_counts[key] || 0) + 1;
  }
  return { group_key: groupKey, n: rows.length, classified_n: rows.length, selected_k: shapes.length, selection: "supervised quote-direction plus exact/adjacent capacity-and-dwell-qualified ask-descent ordinal; dynamic programming maximizes members in n>=20 coherent classes, then minimizes signable class count", prefix_keys: PREFIX_KEYS, prior_class_behavior: priorClassBehavior, shapes, assignment };
}

async function main() {
  const args = process.argv.slice(2), value = (name, fallback = null) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(value("--repo", ".")), privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private")), output = path.resolve(value("--output")), workersN = Number(value("--workers", "8")), exclude = new Set(value("--exclude-events", EXCLUDED_EVENTS.join(",")).split(",").filter(Boolean));
  const sourcePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv"), lines = fs.readFileSync(sourcePath, "utf8").trimEnd().split(/\r?\n/), headers = lines.shift().split(","), sources = lines.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v]))).filter((row) => String(row.evaluator_window_positive).toLowerCase() === "true" && !exclude.has(row.event_id));
  const buckets = Array.from({ length: workersN }, () => []); sources.forEach((source, index) => buckets[index % workersN].push(source));
  const scanned = (await Promise.all(buckets.map((bucket) => new Promise((resolve, reject) => { const worker = new Worker(__filename, { workerData: { sources: bucket, ticksRoot: path.join(privateRoot, "fit-local/ticks") } }); worker.once("message", resolve); worker.once("error", reject); worker.once("exit", (code) => { if (code) reject(new Error(`worker exit ${code}`)); }); })))).flat().sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id));
  const available = scanned.filter((row) => row.status === "AVAILABLE"), grouped = new Map(); for (const row of available) { const key = `${row.category}|${row.price_region}`; if (!grouped.has(key)) grouped.set(key, []); grouped.get(key).push(row); }
  const groups = {}, assignment = {}; for (const [key, rows] of [...grouped].sort()) { const group = buildGroup(rows, key); groups[key] = { ...group, assignment: undefined }; Object.assign(assignment, group.assignment); }
  const pairShapeTuples = {}, byEvent = new Map(); for (const row of available) { if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row); }
  for (const [eventId, legs] of byEvent) { if (legs.length !== 2) continue; legs.sort((a, b) => b.first_ask - a.first_ask || a.leg_id.localeCompare(b.leg_id)); const [high, low] = legs, highShape = assignment[`${eventId}|${high.leg_id}`], lowShape = assignment[`${eventId}|${low.leg_id}`]; if (!highShape || !lowShape) continue; const key = `${high.category}|${high.price_region}|${low.price_region}`, tuple = `${highShape}|${lowShape}`; if (!pairShapeTuples[key]) pairShapeTuples[key] = {}; pairShapeTuples[key][tuple] = (pairShapeTuples[key][tuple] || 0) + 1; }
  const allShapes = Object.values(groups).flatMap((group) => group.shapes), usable = allShapes.filter((shape) => shape.usable_for_signing), oldTopologySpan = {};
  for (const row of available) { if (!oldTopologySpan[row.old_topology]) oldTopologySpan[row.old_topology] = { members: 0, qualified_descent_positive: 0, ordinal_counts: {} }; const cell = oldTopologySpan[row.old_topology], ordinal = row.qualified_descent_to_final_reachable_low?.descent_ordinal; cell.members += 1; cell.qualified_descent_positive += Number(Number.isInteger(ordinal) && ordinal > 0); const key = Number.isInteger(ordinal) ? String(ordinal) : "UNAVAILABLE"; cell.ordinal_counts[key] = (cell.ordinal_counts[key] || 0) + 1; }
  const result = { schema_version: "WINDOW1_COHERENT_QUOTE_SHAPE_LIBRARY_V12", score_free: true, training_events: new Set(available.map((row) => row.event_id)).size, training_legs: available.length, excluded_exact_start_events: [...exclude].sort(), fit_contract: { minimum_signable_class_members: MIN_CLASS_N, coherence: "one exact ordinal or two adjacent integer ordinals only", ordinal: "all capacity>=5, dwell>=10-second qualified ask-to-ask downward transitions before first qualified final reachable low", no_future_data_at_runtime: true, no_print_shape_dependency: true }, price_band_key: "best bid on first one-tick-spread lawful book", feature_contract: { full_path: FINAL_KEYS, tick_prefix: PREFIX_KEYS, ask_side_only: true, dwell_seconds: DWELL_SECONDS, displayed_capacity_contracts: QUANTITY }, groups, assignment, pair_shape_tuples: pairShapeTuples, taxonomy_span: { prior_topology_behavior: oldTopologySpan, finding: "FLAT_UNMOVED and UP_CONTINUATION can contain qualified downward transitions because final net/dip labels erase an interim fall from a prior peak; qualified transition ordinal and rise count are required separating features" }, census: { groups: Object.keys(groups).length, classes_total: allShapes.length, signable_classes: usable.length, unusable_classes: allShapes.length - usable.length, signable_members: usable.reduce((sum, shape) => sum + shape.n, 0), unusable_members: allShapes.filter((shape) => !shape.usable_for_signing).reduce((sum, shape) => sum + shape.n, 0), all_signable_classes_n_at_least_20: usable.every((shape) => shape.n >= MIN_CLASS_N), all_signable_classes_ordinal_width_at_most_one: usable.every((shape) => shape.coherence.ordinal_support_width <= 1) }, source: { quote_ledger: { path: path.relative(repo, sourcePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(sourcePath)) }, tick_files: Object.fromEntries(scanned.map((row) => [row.ticker, row.source])) } };
  fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, canonical(result)); process.stdout.write(canonical({ status: "BUILT", output, sha256: sha256(Buffer.from(canonical(result))), training_events: result.training_events, training_legs: result.training_legs, census: result.census }));
}

if (isMainThread) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }); else { try { workerMain(); } catch (error) { throw error; } }
