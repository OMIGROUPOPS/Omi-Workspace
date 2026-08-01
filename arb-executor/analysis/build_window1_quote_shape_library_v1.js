#!/usr/bin/env node
"use strict";

// Quote-derived, leave-two-games-out shape library. No scorer or policy replay.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

const GRID = 100;
const DEFAULT_EXCLUDED_EVENTS = [
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
  "KXATPCHALLENGERMATCH-26JUL19HURBIG",
];
const PREFIX_KEYS = ["ask_net", "ask_dip", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "ask_dwell_fraction", "mean_log_top_ask_size", "mean_log_top5_ask_depth"];
const FINAL_KEYS = ["ask_net", "ask_dip", "ask_peak", "first_min_progress", "floor_dwell_fraction", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "median_ask_episode_dwell", "mean_log_top_ask_size", "mean_log_top5_ask_depth"];

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null;
  let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function median(values) { const s = [...values].sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : null; }

async function scanOne(source, ticksRoot) {
  const file = path.join(ticksRoot, `${source.ticker}.csv.gz`), stat = fs.statSync(file), hash = crypto.createHash("sha256");
  const input = fs.createReadStream(file); input.on("data", (chunk) => hash.update(chunk));
  const lines = readline.createInterface({ input: input.pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let headers = null, sourceRow = 0; const rows = [], left = Number(source.left_ts), right = Number(source.right_ts);
  for await (const line of lines) {
    sourceRow += 1; if (!headers) { headers = line.replace(/\r$/, "").split(","); continue; }
    const values = line.replace(/\r$/, "").split(","); if (values.length !== headers.length) continue;
    const raw = Object.fromEntries(headers.map((name, i) => [name, values[i]])), ts = parseEt(raw.ts_et); if (ts === null || ts < left || ts > right) continue;
    const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) {
      const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal: sourceRow, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1], top5_ask_depth: asks.reduce((s, x) => s + x[1], 0), carried_last: integer(raw.last_trade), receipt: `${path.basename(file)}#row-${sourceRow}` });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  if (!rows.length) return { event_id: source.event_id, leg_id: source.leg, ticker: source.ticker, category: source.category, status: "NO_LAWFUL_BBO", source: { file: path.basename(file), bytes: stat.size, sha256: hash.digest("hex") } };
  const formedIndex = rows.findIndex((row) => row.spread === 1);
  if (formedIndex < 0) return { event_id: source.event_id, leg_id: source.leg, ticker: source.ticker, category: source.category, status: "NO_ONE_TICK_FORMED_BOOK", source: { file: path.basename(file), bytes: stat.size, sha256: hash.digest("hex") } };
  rows.splice(0, formedIndex);
  const firstAsk = rows[0].ask, duration = right - left, grids = [], episodeDwells = [];
  let rowIndex = 0, state = null, rowCount = 0, askChanges = 0, minAsk = null, maxAsk = null, firstMinTs = null, lastAskChangeTs = null, observedStart = null;
  let spreadIntegral = 0, topSizeIntegral = 0, depthIntegral = 0, observedDuration = 0, spreadMin = null, spreadMax = null, floorDwell = 0;
  function integrate(toTs) {
    if (!state) return;
    const from = state.integrated_to, dt = Math.max(0, toTs - from); if (!dt) return;
    spreadIntegral += state.spread * dt; topSizeIntegral += Math.log1p(state.top_ask_size) * dt; depthIntegral += Math.log1p(state.top5_ask_depth) * dt; observedDuration += dt;
    if (state.ask === minAsk) floorDwell += dt; state.integrated_to = toTs;
  }
  for (let g = 0; g <= GRID; g += 1) {
    const cutoff = left + duration * g / GRID;
    while (rowIndex < rows.length && rows[rowIndex].ts <= cutoff) {
      const row = rows[rowIndex++]; integrate(row.ts);
      if (!state) { observedStart = row.ts; lastAskChangeTs = row.ts; minAsk = row.ask; maxAsk = row.ask; firstMinTs = row.ts; }
      else if (row.ask !== state.ask) { episodeDwells.push(row.ts - lastAskChangeTs); askChanges += 1; lastAskChangeTs = row.ts; }
      minAsk = Math.min(minAsk, row.ask); maxAsk = Math.max(maxAsk, row.ask); if (row.ask === minAsk && minAsk < (state?.min_seen ?? Infinity)) firstMinTs = row.ts;
      spreadMin = spreadMin === null ? row.spread : Math.min(spreadMin, row.spread); spreadMax = spreadMax === null ? row.spread : Math.max(spreadMax, row.spread);
      rowCount += 1; state = { ...row, min_seen: minAsk, integrated_to: row.ts };
    }
    integrate(cutoff);
    if (!state) { grids.push(null); continue; }
    const elapsed = Math.max(1, cutoff - left), obs = Math.max(1, observedDuration);
    grids.push({ ask_net: state.ask - firstAsk, ask_dip: minAsk - firstAsk, mean_spread: spreadIntegral / obs, spread_range: spreadMax - spreadMin, quote_rate: rowCount * 3600 / elapsed, ask_change_rate: askChanges * 3600 / elapsed, ask_dwell_fraction: Math.max(0, cutoff - lastAskChangeTs) / elapsed, mean_log_top_ask_size: topSizeIntegral / obs, mean_log_top5_ask_depth: depthIntegral / obs, current_ask: state.ask, current_bid: state.bid, remaining_min_delta: null });
  }
  integrate(right); if (state) episodeDwells.push(right - lastAskChangeTs);
  const suffixMin = Array(rows.length), suffix = []; let sm = Infinity; for (let i = rows.length - 1; i >= 0; i -= 1) { sm = Math.min(sm, rows[i].ask); suffixMin[i] = sm; }
  for (let g = 0; g <= GRID; g += 1) {
    if (!grids[g]) continue; const cutoff = left + duration * g / GRID; let lo = 0, hi = rows.length;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (rows[mid].ts < cutoff) lo = mid + 1; else hi = mid; }
    const futureMin = lo < rows.length ? Math.min(grids[g].current_ask, suffixMin[lo]) : grids[g].current_ask; grids[g].remaining_min_delta = futureMin - grids[g].current_ask;
  }
  const final = grids[GRID], finalFeatures = { ask_net: rows[rows.length - 1].ask - firstAsk, ask_dip: Math.min(...rows.map((r) => r.ask)) - firstAsk, ask_peak: Math.max(...rows.map((r) => r.ask)) - firstAsk, first_min_progress: (firstMinTs - left) / duration, floor_dwell_fraction: floorDwell / Math.max(1, observedDuration), mean_spread: final.mean_spread, spread_range: final.spread_range, quote_rate: rows.length * 3600 / duration, ask_change_rate: askChanges * 3600 / duration, median_ask_episode_dwell: median(episodeDwells), mean_log_top_ask_size: final.mean_log_top_ask_size, mean_log_top5_ask_depth: final.mean_log_top5_ask_depth };
  return { event_id: source.event_id, leg_id: source.leg, ticker: source.ticker, category: source.category, status: "AVAILABLE", price_region: region(rows[0].bid), first_ask: firstAsk, first_bid: rows[0].bid, final_features: finalFeatures, grid: grids, source: { file: path.basename(file), bytes: stat.size, sha256: hash.digest("hex") } };
}

async function workerMain() { const rows = []; for (const source of workerData.sources) rows.push(await scanOne(source, workerData.ticksRoot)); parentPort.postMessage(rows); }
function dist2(a, b) { let s = 0; for (let i = 0; i < a.length; i += 1) s += (a[i] - b[i]) ** 2; return s; }
function kmeans(points, k) {
  const cents = [points[0].slice()]; while (cents.length < k) { let best = 0, bestD = -1; for (let i = 0; i < points.length; i += 1) { const d = Math.min(...cents.map((c) => dist2(points[i], c))); if (d > bestD) { bestD = d; best = i; } } cents.push(points[best].slice()); }
  let assign = Array(points.length).fill(-1);
  for (let it = 0; it < 100; it += 1) {
    const next = points.map((p) => cents.reduce((best, c, i) => dist2(p, c) < dist2(p, cents[best]) ? i : best, 0)); if (next.every((x, i) => x === assign[i])) break; assign = next;
    for (let j = 0; j < k; j += 1) { const ids = points.map((_, i) => i).filter((i) => assign[i] === j); if (!ids.length) continue; cents[j] = points[0].map((_, d) => ids.reduce((s, i) => s + points[i][d], 0) / ids.length); }
  }
  return { cents, assign };
}
function silhouette(points, assign, k) {
  if (points.length < 3) return -1; let total = 0;
  for (let i = 0; i < points.length; i += 1) {
    const own = points.map((_, j) => j).filter((j) => j !== i && assign[j] === assign[i]); if (!own.length) continue; const a = own.reduce((s, j) => s + Math.sqrt(dist2(points[i], points[j])), 0) / own.length;
    let b = Infinity; for (let c = 0; c < k; c += 1) if (c !== assign[i]) { const ids = points.map((_, j) => j).filter((j) => assign[j] === c); if (ids.length) b = Math.min(b, ids.reduce((s, j) => s + Math.sqrt(dist2(points[i], points[j])), 0) / ids.length); }
    total += Number.isFinite(b) && Math.max(a, b) ? (b - a) / Math.max(a, b) : 0;
  }
  return total / points.length;
}
function topology(row) {
  const f = row.final_features;
  if (f.ask_net < 0) return f.ask_net === f.ask_dip ? "DOWN_CONTINUATION" : "DOWN_REBOUND";
  if (f.ask_net > 0) return f.ask_dip < 0 ? "UP_AFTER_DIP" : "UP_CONTINUATION";
  return f.ask_dip < 0 ? "FLAT_RECOVERED" : "FLAT_UNMOVED";
}
function clusterGroup(rows, groupKey) {
  const raw = rows.map((r) => FINAL_KEYS.map((k) => r.final_features[k])), means = raw[0].map((_, d) => raw.reduce((s, x) => s + x[d], 0) / raw.length), sds = means.map((m, d) => Math.max(1e-9, Math.sqrt(raw.reduce((s, x) => s + (x[d] - m) ** 2, 0) / raw.length))), z = raw.map((x) => x.map((v, d) => (v - means[d]) / sds[d])), byTopology = new Map();
  rows.forEach((row, i) => { const key = topology(row); if (!byTopology.has(key)) byTopology.set(key, []); byTopology.get(key).push(i); });
  const shapes = [], assignment = {};
  for (const [topologyName, ids] of [...byTopology].sort()) {
    const centroid = z[0].map((_, d) => ids.reduce((sum, i) => sum + z[i][d], 0) / ids.length), medoidId = ids.reduce((best, i) => dist2(z[i], centroid) < dist2(z[best], centroid) ? i : best, ids[0]), shapeId = `${groupKey.replace("|", "_")}_${topologyName}`;
    const envelopes = [];
    for (let g = 0; g <= GRID; g += 1) {
      const available = ids.map((i) => rows[i].grid[g]).filter(Boolean), env = {};
      for (const key of PREFIX_KEYS) env[key] = available.length ? [Math.min(...available.map((x) => x[key])), Math.max(...available.map((x) => x[key]))] : null;
      if (available.length) { const prefixMeans = PREFIX_KEYS.map((key) => available.reduce((sum, x) => sum + x[key], 0) / available.length), prefixSds = PREFIX_KEYS.map((key, d) => Math.max(1e-9, Math.sqrt(available.reduce((sum, x) => sum + (x[key] - prefixMeans[d]) ** 2, 0) / available.length))); env.empirical_support = { means: prefixMeans, sds: prefixSds }; } else env.empirical_support = null;
      envelopes.push(env);
    }
    const memberRows = ids.map((i) => rows[i]); shapes.push({ shape_id: shapeId, topology: topologyName, n: ids.length, centroid_z: centroid, medoid: { event_id: rows[medoidId].event_id, leg_id: rows[medoidId].leg_id, ticker: rows[medoidId].ticker }, medoid_future: rows[medoidId].grid.map((x) => x ? x.remaining_min_delta : null), feature_medians: Object.fromEntries(FINAL_KEYS.map((key) => [key, median(memberRows.map((r) => r.final_features[key]))])), envelopes });
    for (const i of ids) assignment[`${rows[i].event_id}|${rows[i].leg_id}`] = shapeId;
  }
  return { group_key: groupKey, n: rows.length, classified_n: rows.length, unclassified: [], selected_k: shapes.length, selection: "exact integer-cent ask-path topology; medoid and prefix support fitted on dwell, spread, cadence, displayed volume, and top-five depth", silhouette: null, feature_means: means, feature_sds: sds, shapes, assignment };
}

async function main() {
  const args = process.argv.slice(2), value = (name, fallback = null) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(value("--repo", ".")), privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private")), output = path.resolve(value("--output")), workerCount = Number(value("--workers", "8"));
  const excludedEvents = new Set(value("--exclude-events", DEFAULT_EXCLUDED_EVENTS.join(",")).split(",").filter(Boolean));
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const sourcePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv"), matrix = fs.readFileSync(sourcePath, "utf8").trimEnd().split(/\r?\n/), headers = matrix.shift().split(",");
  const sources = matrix.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v]))).filter((r) => String(r.evaluator_window_positive).toLowerCase() === "true" && !excludedEvents.has(r.event_id));
  const buckets = Array.from({ length: workerCount }, () => []); sources.forEach((s, i) => buckets[i % workerCount].push(s));
  const workers = buckets.map((bucket) => new Promise((resolve, reject) => { const worker = new Worker(__filename, { workerData: { sources: bucket, ticksRoot: path.join(privateRoot, "fit-local/ticks") } }); worker.once("message", resolve); worker.once("error", reject); worker.once("exit", (code) => { if (code) reject(new Error(`worker exit ${code}`)); }); }));
  const scanned = (await Promise.all(workers)).flat().sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id)), available = scanned.filter((r) => r.status === "AVAILABLE"), grouped = new Map();
  for (const row of available) { const key = `${row.category}|${row.price_region}`; if (!grouped.has(key)) grouped.set(key, []); grouped.get(key).push(row); }
  const groups = {}, assignment = {}; for (const [key, rows] of [...grouped].sort()) { const fit = clusterGroup(rows, key); groups[key] = { ...fit, assignment: undefined }; Object.assign(assignment, fit.assignment); }
  const byEvent = new Map(); for (const row of available) { if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row); }
  const pairTuples = {};
  for (const [eventId, legs] of byEvent) {
    if (legs.length !== 2) continue; legs.sort((a, b) => b.first_ask - a.first_ask || a.leg_id.localeCompare(b.leg_id)); const [high, low] = legs, highShape = assignment[`${eventId}|${high.leg_id}`], lowShape = assignment[`${eventId}|${low.leg_id}`]; if (!highShape || !lowShape) continue;
    const key = `${high.category}|${high.price_region}|${low.price_region}`; if (!pairTuples[key]) pairTuples[key] = {}; const tuple = `${highShape}|${lowShape}`; pairTuples[key][tuple] = (pairTuples[key][tuple] || 0) + 1;
  }
  const result = { schema_version: "WINDOW1_QUOTE_SHAPE_LIBRARY_V1", score_free: true, training_events: new Set(available.map((r) => r.event_id)).size, training_legs: available.length, excluded_cold_test_events: [...excludedEvents].sort(), price_band_key: "best bid on first one-tick-spread lawful book; prior unformed/wide books retain INSUFFICIENT_EVIDENCE", feature_contract: { full_path: FINAL_KEYS, tick_prefix: PREFIX_KEYS, displayed_volume: "time-weighted log1p top-ask displayed size", depth: "time-weighted log1p top-five ask depth", no_print_shape_dependency: true }, clustering: "per category and formed-book bid price band; exact integer-cent ask-path topology; within-shape medoids and prefix support fitted on quote dwell/spread/cadence/displayed-volume/depth", groups, assignment, pair_shape_tuples: pairTuples, source: { quote_ledger: { path: path.relative(repo, sourcePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(sourcePath)) }, tick_files: Object.fromEntries(scanned.map((r) => [r.ticker, r.source])) } };
  fs.writeFileSync(output, canonical(result)); process.stdout.write(canonical({ status: "BUILT", training_events: result.training_events, training_legs: result.training_legs, groups: Object.keys(groups).length, shapes: Object.values(groups).reduce((s, g) => s + g.shapes.length, 0), sha256: sha256(Buffer.from(canonical(result))) }));
}

if (isMainThread) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }); else workerMain().catch((error) => { throw error; });
