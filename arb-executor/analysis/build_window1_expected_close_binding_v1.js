#!/usr/bin/env node
"use strict";

// Score-free expected-close binding audit. Fits only July 12-17 and calibrates
// only July 18-20. It never invokes a policy replay or scorer.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const { fitExpectedCloseModel, predictExpectedClose, region } = require("./window1_expected_close_distribution_v1.js");

const POPULATION = 804;
const OUT_REL = ".claude/window1_live_v4_replay/expected_close_binding_20260801";
const QUOTE_REL = ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv";
const ENTRYMECH_REL = ".claude/entrymech_20260717/ENTRYMECH_CENSUS.md";
const MECHANISM_REL = ".claude/window1_range_attack_prerun_20260725/MECHANISM_RECOVERY_TABLE.json";
const AGGRESSOR_REL = ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/AGGRESSOR_SPLIT.json";
const CEILING_REL = ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/CEILING_CENSUS.json";
const COMMITMENT_REL = ".claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/COMMITMENT_GAP_CENSUS.json";
const MODEL_FEATURES = ["ask_net", "ask_dip", "mean_spread", "log_quote_rate", "log_ask_change_rate", "log_ask_dwell", "log_ask_size", "log_top5_ask_depth"];

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(data) { return crypto.createHash("sha256").update(data).digest("hex"); }
function fileHash(file) { return sha256(fs.readFileSync(file)); }
function parseCsv(file) { const lines = fs.readFileSync(file, "utf8").trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line) => Object.fromEntries(line.split(",").map((value, index) => [headers[index], value]))); }
function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!match) return null;
  let hour = Number(match[4]); if (match[7] === "AM" && hour === 12) hour = 0; if (match[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000;
}
function integer(value) { if (value === null || value === undefined || value === "" || typeof value === "boolean") return null; const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function finite(value) { const n = Number(value); return Number.isFinite(n) ? n : null; }
function quantile(values, q) { if (!values.length) return null; const sorted = [...values].sort((a, b) => a - b), x = (sorted.length - 1) * q, lo = Math.floor(x), hi = Math.ceil(x); return sorted[lo] + (sorted[hi] - sorted[lo]) * (x - lo); }
function distribution(values) { return { n: values.length, min: values.length ? Math.min(...values) : null, p10: quantile(values, 0.1), p25: quantile(values, 0.25), median: quantile(values, 0.5), p75: quantile(values, 0.75), p90: quantile(values, 0.9), max: values.length ? Math.max(...values) : null }; }
function edgeBand(value) { return value >= 15 ? "GE15" : value >= 5 ? "PLUS5_TO14" : value >= -4 ? "MINUS4_TO_PLUS4" : value >= -14 ? "MINUS14_TO_MINUS5" : "LE_MINUS15"; }
function gzipDeterministic(text) { return zlib.gzipSync(Buffer.from(text), { level: 9, mtime: 0 }); }

async function loadTicks(source, ticksRoot) {
  const file = path.join(ticksRoot, `${source.ticker}.csv.gz`), bytes = fs.readFileSync(file), input = fs.createReadStream(file);
  const lines = readline.createInterface({ input: input.pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let headers = null, ordinal = 0; const rows = [], left = Number(source.left_ts), right = Number(source.right_ts);
  for await (const line of lines) {
    ordinal += 1; if (!headers) { headers = line.replace(/\r$/, "").split(","); continue; }
    const values = line.replace(/\r$/, "").split(","); if (values.length !== headers.length) continue;
    const raw = Object.fromEntries(headers.map((name, index) => [name, values[index]])), ts = parseEt(raw.ts_et); if (ts === null || ts < left || ts > right) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(raw[`bid_${level}`]), bs = positive(raw[`bid_${level}_sz`]), ap = integer(raw[`ask_${level}`]), as = positive(raw[`ask_${level}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], ask_size: asks[0][1], top5_ask_depth: asks.reduce((sum, row) => sum + row[1], 0), receipt: `${path.basename(file)}#row-${ordinal}` });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return { rows, source: { path: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) } };
}
function truePrints(cacheLeg, left, right) {
  const seen = new Map();
  for (const raw of cacheLeg.prints || []) {
    const ts = finite(raw.ts), price = integer(raw.price), size = positive(raw.size), id = String(raw.trade_id || "");
    if (ts === null || ts < left || ts > right || price === null || size === null || !id) continue;
    const row = { ts, price, size, id, taker_side: String(raw.taker_side || "") }, prior = seen.get(id);
    if (prior && canonical(prior) !== canonical(row)) throw new Error(`conflicting print ${id}`); seen.set(id, row);
  }
  return [...seen.values()].sort((a, b) => a.ts - b.ts || a.id.localeCompare(b.id));
}
function enrich(rows, prints, source) {
  if (!rows.length) return [];
  const out = []; let firstAsk = rows[0].ask, minAsk = firstAsk, askStart = rows[0].ts, askChanges = 0, printIndex = 0, volume = 0, printCount = 0, latestPrint = null, spreadSum = 0;
  for (let index = 0; index < rows.length; index += 1) {
    const row = rows[index]; if (index && row.ask !== rows[index - 1].ask) { askChanges += 1; askStart = row.ts; }
    minAsk = Math.min(minAsk, row.ask); spreadSum += row.spread;
    while (printIndex < prints.length && prints[printIndex].ts < row.ts) { latestPrint = prints[printIndex]; volume += latestPrint.size; printCount += 1; printIndex += 1; }
    const elapsed = Math.max(1, row.ts - rows[0].ts), midpoint = (row.bid + row.ask) / 2;
    out.push({
      ...row,
      prefix: {
        ask_net: row.ask - firstAsk, ask_dip: minAsk - firstAsk, mean_spread: spreadSum / (index + 1),
        log_quote_rate: Math.log1p((index + 1) * 3600 / elapsed), log_ask_change_rate: Math.log1p(askChanges * 3600 / elapsed),
        log_ask_dwell: Math.log1p(row.ts - askStart), log_ask_size: Math.log1p(row.ask_size), log_top5_ask_depth: Math.log1p(row.top5_ask_depth),
      },
      causal: {
        quote_rate: (index + 1) * 3600 / elapsed, ask_change_rate: askChanges * 3600 / elapsed, ask_dwell: row.ts - askStart,
        latest_print: latestPrint, volume, print_rate: printCount * 3600 / elapsed,
        last_missing: latestPrint ? 0 : 1, last_minus_mid: latestPrint ? latestPrint.price - midpoint : 0,
        last_at_or_below_bid: latestPrint && latestPrint.price <= row.bid ? 1 : 0,
        last_at_or_above_ask: latestPrint && latestPrint.price >= row.ask ? 1 : 0,
      },
      scheduled_t_minus_seconds: Number(source.scheduled_start_ts) - row.ts,
    });
  }
  return out;
}
function latestStrictlyBefore(rows, ts) { let low = 0, high = rows.length; while (low < high) { const middle = (low + high) >> 1; if (rows[middle].ts < ts) low = middle + 1; else high = middle; } return low ? rows[low - 1] : null; }
function topology(rows) { if (!rows.length) return "UNAVAILABLE"; const first = rows[0].ask, last = rows[rows.length - 1].ask, floor = Math.min(...rows.map((row) => row.ask)), net = last - first, dip = floor - first; if (net < 0) return net === dip ? "DOWN_CONTINUATION" : "DOWN_REBOUND"; if (net > 0) return dip < 0 ? "UP_AFTER_DIP" : "UP_CONTINUATION"; return dip < 0 ? "FLAT_RECOVERED" : "FLAT_UNMOVED"; }
function selectHourly(rows) { const selected = new Map(); for (const row of rows) { const band = Math.floor(row.scheduled_t_minus_seconds / 3600); if (band < 0 || selected.has(band)) continue; selected.set(band, row); } return [...selected].sort((a, b) => b[0] - a[0]); }
function makeFeatures(own, sibling) {
  const s = sibling;
  return {
    bid: own.bid, ask: own.ask, spread: own.spread, log_ask_size: Math.log1p(own.ask_size), log_top5_ask_depth: Math.log1p(own.top5_ask_depth),
    log_ask_dwell: Math.log1p(own.causal.ask_dwell), log_quote_rate: Math.log1p(own.causal.quote_rate), log_ask_change_rate: Math.log1p(own.causal.ask_change_rate),
    last_missing: own.causal.last_missing, last_minus_mid: own.causal.last_minus_mid, last_at_or_below_bid: own.causal.last_at_or_below_bid, last_at_or_above_ask: own.causal.last_at_or_above_ask,
    log_executed_volume: Math.log1p(own.causal.volume), log_print_rate: Math.log1p(own.causal.print_rate), time_to_scheduled_hours: own.scheduled_t_minus_seconds / 3600,
    sibling_missing: s ? 0 : 1, sibling_bid: s?.bid || 0, sibling_ask: s?.ask || 0, sibling_spread: s?.spread || 0,
    sibling_log_ask_size: s ? Math.log1p(s.ask_size) : 0, sibling_log_top5_ask_depth: s ? Math.log1p(s.top5_ask_depth) : 0, sibling_log_ask_dwell: s ? Math.log1p(s.causal.ask_dwell) : 0,
    sibling_log_quote_rate: s ? Math.log1p(s.causal.quote_rate) : 0, sibling_last_missing: s ? s.causal.last_missing : 1, sibling_last_minus_mid: s ? s.causal.last_minus_mid : 0,
    sibling_log_executed_volume: s ? Math.log1p(s.causal.volume) : 0, pair_ask_sum: own.ask + (s?.ask || 0),
  };
}

async function scanEvent(sources, privateRoot) {
  const eventId = sources[0].event_id, cacheFile = path.join(privateRoot, "fit-local/guarded-cache-v3", `${eventId}.json.gz`), cacheBytes = fs.readFileSync(cacheFile), cache = JSON.parse(zlib.gunzipSync(cacheBytes));
  const loaded = [];
  for (const source of sources.sort((a, b) => a.leg.localeCompare(b.leg))) {
    const ticks = await loadTicks(source, path.join(privateRoot, "fit-local/ticks")), cacheLeg = cache.legs.find((leg) => leg.leg === source.leg && leg.ticker === source.ticker);
    if (!cacheLeg) throw new Error(`cache leg missing ${eventId}/${source.leg}`);
    const prints = truePrints(cacheLeg, Number(source.left_ts), Number(source.right_ts)), enriched = enrich(ticks.rows, prints, source);
    loaded.push({ source, rows: enriched, topology: topology(enriched), tick_source: ticks.source });
  }
  const samples = [];
  for (const leg of loaded) for (const [hourBand, own] of selectHourly(leg.rows)) {
    const siblingLeg = loaded.find((candidate) => candidate !== leg), sibling = latestStrictlyBefore(siblingLeg.rows, own.ts), close = integer(leg.source.window1_close_cents);
    samples.push({
      event_id: eventId, leg_id: leg.source.leg, ticker: leg.source.ticker, leg_identity: `${eventId}|${leg.source.leg}`, category: leg.source.category, slice: leg.source.slice,
      ts: own.ts, scheduled_t_minus_seconds: own.scheduled_t_minus_seconds, scheduled_hour_band: hourBand, bid_cents: own.bid, ask_cents: own.ask, price_region: region(own.ask),
      close_cents: close, close_status: close === null ? "REFERENCE_UNAVAILABLE" : "AVAILABLE", features: makeFeatures(own, sibling), prefix: own.prefix,
      true_last_trade: own.causal.latest_print ? { price_cents: own.causal.latest_print.price, ts: own.causal.latest_print.ts, receipt: own.causal.latest_print.id, position: own.causal.last_at_or_below_bid ? "AT_OR_BELOW_BID" : own.causal.last_at_or_above_ask ? "AT_OR_ABOVE_ASK" : "INSIDE_SPREAD" } : null,
      own_book_receipt: own.receipt, sibling_book_receipt: sibling?.receipt || null, sibling_book_ts: sibling?.ts || null, final_quote_topology: leg.topology,
    });
  }
  return { event_id: eventId, samples, legs: loaded.map((leg) => ({ event_id: eventId, leg_id: leg.source.leg, ticker: leg.source.ticker, category: leg.source.category, slice: leg.source.slice, topology: leg.topology, initial_price_region: leg.rows.length ? region(leg.rows[0].ask) : "UNKNOWN", tick_source: leg.tick_source })), cache_source: { path: `${eventId}.json.gz`, bytes: cacheBytes.length, sha256: sha256(cacheBytes) } };
}
async function workerMain() { const output = []; for (const sources of workerData.events) output.push(await scanEvent(sources, workerData.privateRoot)); parentPort.postMessage(output); }

function buildShapeLibrary(fitSamples, fitLegs) {
  const groups = {};
  for (const leg of fitLegs) { const key = `${leg.category}|${leg.initial_price_region}`; if (!groups[key]) groups[key] = {}; if (!groups[key][leg.topology]) groups[key][leg.topology] = { shape_id: `${key.replaceAll("|", "_")}_${leg.topology}`, topology: leg.topology, n_legs: 0, hours: {} }; groups[key][leg.topology].n_legs += 1; }
  for (const sample of fitSamples) {
    const leg = fitLegs.find((row) => row.event_id === sample.event_id && row.leg_id === sample.leg_id), key = `${sample.category}|${leg.initial_price_region}`, shape = groups[key][sample.final_quote_topology];
    const hour = String(sample.scheduled_hour_band); if (!shape.hours[hour]) shape.hours[hour] = [];
    shape.hours[hour].push(sample.prefix);
  }
  for (const topologies of Object.values(groups)) for (const shape of Object.values(topologies)) for (const [hour, rows] of Object.entries(shape.hours)) {
    shape.hours[hour] = Object.fromEntries(MODEL_FEATURES.map((name) => { const values = rows.map((row) => row[name]), mean = values.reduce((sum, value) => sum + value, 0) / values.length, sd = Math.max(1e-9, Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length)); return [name, { min: Math.min(...values), max: Math.max(...values), mean, sd }]; }));
  }
  return { schema_version: "WINDOW1_FIT_ONLY_QUOTE_SHAPE_LIBRARY_FOR_EXPECTED_CLOSE_V1", fit_slice_only: true, groups };
}
function bindSurvivors(samples, legs, library) {
  const legMap = new Map(legs.map((leg) => [`${leg.event_id}|${leg.leg_id}`, leg]));
  for (const sample of samples) {
    const leg = legMap.get(sample.leg_identity), group = library.groups[`${sample.category}|${leg.initial_price_region}`] || {}, candidates = [];
    for (const shape of Object.values(group)) {
      const hour = shape.hours[String(sample.scheduled_hour_band)]; if (!hour) continue;
      let distance = 0, inside = true;
      for (const name of MODEL_FEATURES) { const value = sample.prefix[name], bounds = hour[name]; if (value < bounds.min || value > bounds.max) inside = false; const z = (value - bounds.mean) / bounds.sd; distance += z * z; }
      candidates.push({ shape_id: shape.shape_id, inside, distance });
    }
    const inside = candidates.filter((row) => row.inside), minimum = candidates.length ? Math.min(...candidates.map((row) => row.distance)) : Infinity;
    sample.surviving_shapes = (inside.length ? inside : candidates.filter((row) => Math.abs(row.distance - minimum) < 1e-12)).map((row) => row.shape_id).sort();
    sample.shape_status = inside.length ? "EMPIRICAL_PREFIX_ENVELOPE" : candidates.length ? "NEAREST_FIT_SHAPE_NO_ENVELOPE_MATCH" : "NO_FIT_SHAPE_GROUP";
  }
}
function calibrationRows(predictions) {
  const map = new Map();
  for (const row of predictions) { const key = `${row.category}|${row.price_region}`; if (!map.has(key)) map.set(key, []); map.get(key).push(row); }
  return [...map].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => {
    const [category, price_region] = key.split("|"), uniqueLegs = new Set(rows.map((row) => row.leg_identity)).size, errors = rows.map((row) => row.median_close_cents - row.actual_close_cents), baseline = rows.map((row) => row.ask_cents - row.actual_close_cents), absolute = errors.map(Math.abs), baselineAbsolute = baseline.map(Math.abs);
    const edgeMap = new Map(); for (const row of rows) { const band = edgeBand(row.predicted_median_edge_cents); if (!edgeMap.has(band)) edgeMap.set(band, []); edgeMap.get(band).push(row); }
    return { category, price_region, prediction_rows: rows.length, unique_legs: uniqueLegs, unique_events: new Set(rows.map((row) => row.event_id)).size, thin: uniqueLegs < 30, thin_law: "unique post-fit legs <30; at n=30 the normal 95% half-width for nominal 90% coverage is approximately 10.7 percentage points", median_model_error_cents: distribution(errors), absolute_model_error_cents: distribution(absolute), absolute_current_ask_baseline_error_cents: distribution(baselineAbsolute), central_50_coverage: rows.filter((row) => row.actual_close_cents >= row.q25_close_cents && row.actual_close_cents <= row.q75_close_cents).length / rows.length, central_80_coverage: rows.filter((row) => row.actual_close_cents >= row.q10_close_cents && row.actual_close_cents <= row.q90_close_cents).length / rows.length, predicted_edge_calibration: [...edgeMap].sort(([a], [b]) => a.localeCompare(b)).map(([predicted_edge_band, values]) => ({ predicted_edge_band, reporting_band_only_not_decision_threshold: true, rows: values.length, unique_legs: new Set(values.map((row) => row.leg_identity)).size, predicted_median_edge_cents: distribution(values.map((row) => row.predicted_median_edge_cents)), actual_close_minus_ask_cents: distribution(values.map((row) => row.actual_close_cents - row.ask_cents)), prediction_error_cents: distribution(values.map((row) => row.median_close_cents - row.actual_close_cents)) })) };
  });
}
function markdown(binding, external, calibration, decisions) {
  return `# Window-1 expected-close binding audit\n\n` +
    `Score-free. Fit is July 12-17; calibration is disjoint July 18-20. No five-game or 804 policy replay was run.\n\n` +
    `## Binding result\n\n**${binding.status}** — ${binding.reason}\n\n` +
    `## External books\n\nFresh Pinnacle/Betfair/Matchbook decision-time reads: ${external.summary.fresh_legs}/${external.summary.population_legs}. External predictive comparison is ${external.summary.predictive_comparison}.\n\n` +
    `## Internal candidate\n\nThe candidate returns a weighted empirical distribution of own-close minus current ask. It consumes current bid/ask/spread/dwell, receipt-identified true last trade, executed volume/cadence, quote cadence, scheduled clock, sibling book, and fit-only surviving quote shapes. Every training leg contributes at most one closest residual per query.\n\n` +
    `Post-fit labeled legs: ${calibration.conservation.postfit_labeled_legs}; unlabeled: ${calibration.conservation.postfit_unlabeled_legs}. The model beats the current-ask baseline on median absolute error in ${calibration.comparison_to_current_ask_baseline.cells_better} of ${calibration.comparison_to_current_ask_baseline.cells_total} category/price-region cells; predicted-edge >=15c rows: ${calibration.comparison_to_current_ask_baseline.predicted_edge_ge15_rows}. Thin and non-thin cells are listed in the calibration artifact; no pooled performance metric is emitted.\n\n` +
    `## Decisions\n\n- Fee-aware take: ${decisions.fee_aware_take.status}.\n- First-leg commitment: ${decisions.commitment.status}.\n- Take versus rest: ${decisions.take_vs_rest.status}.\n`;
}

async function main() {
  const args = process.argv.slice(2), value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
  const repo = path.resolve(value("--repo", ".")), privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private")), out = path.resolve(value("--output", path.join(repo, OUT_REL))), workers = Number(value("--workers", "8"));
  const quoteFile = path.join(repo, QUOTE_REL), quoteRows = parseCsv(quoteFile); if (quoteRows.length !== 1608 || new Set(quoteRows.map((row) => row.event_id)).size !== POPULATION) throw new Error("population mismatch");
  const byEvent = new Map(); for (const row of quoteRows) { if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row); }
  const eventRows = [...byEvent].sort(([a], [b]) => a.localeCompare(b)).map(([, rows]) => rows), buckets = Array.from({ length: workers }, () => []); eventRows.forEach((rows, index) => buckets[index % workers].push(rows));
  const jobs = buckets.map((events) => new Promise((resolve, reject) => { const worker = new Worker(__filename, { workerData: { events, privateRoot } }); worker.once("message", resolve); worker.once("error", reject); worker.once("exit", (code) => { if (code) reject(new Error(`worker exit ${code}`)); }); }));
  const scanned = (await Promise.all(jobs)).flat().sort((a, b) => a.event_id.localeCompare(b.event_id)), allSamples = scanned.flatMap((row) => row.samples), allLegs = scanned.flatMap((row) => row.legs), fitSamples = allSamples.filter((row) => row.slice === "fit"), postSamples = allSamples.filter((row) => row.slice === "post_fit"), fitLegs = allLegs.filter((row) => row.slice === "fit"), postLegs = allLegs.filter((row) => row.slice === "post_fit");
  const shapeLibrary = buildShapeLibrary(fitSamples, fitLegs); bindSurvivors(allSamples, allLegs, shapeLibrary);
  const labeledFit = fitSamples.filter((row) => Number.isInteger(row.close_cents)), labeledPost = postSamples.filter((row) => Number.isInteger(row.close_cents)), model = fitExpectedCloseModel(labeledFit), predictions = [];
  for (const row of labeledPost) {
    const predicted = predictExpectedClose(model, row); if (!predicted.status.startsWith("DISTRIBUTION")) continue;
    predictions.push({ event_id: row.event_id, leg_id: row.leg_id, ticker: row.ticker, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, scheduled_hour_band: row.scheduled_hour_band, scheduled_t_minus_seconds: row.scheduled_t_minus_seconds, ts: row.ts, bid_cents: row.bid_cents, ask_cents: row.ask_cents, actual_close_cents: row.close_cents, surviving_shapes: row.surviving_shapes, shape_status: row.shape_status, independent_training_legs: predicted.independent_training_legs, effective_sample_size: predicted.effective_sample_size, q10_close_cents: predicted.close_quantiles_cents["0.1"], q25_close_cents: predicted.close_quantiles_cents["0.25"], median_close_cents: predicted.close_quantiles_cents["0.5"], q75_close_cents: predicted.close_quantiles_cents["0.75"], q90_close_cents: predicted.close_quantiles_cents["0.9"], predicted_median_edge_cents: predicted.close_quantiles_cents["0.5"] - row.ask_cents, own_book_receipt: row.own_book_receipt, sibling_book_receipt: row.sibling_book_receipt, true_last_trade: row.true_last_trade });
  }
  const cells = calibrationRows(predictions), thinCells = cells.filter((row) => row.thin).map((row) => `${row.category}|${row.price_region}`), comparison = { cells_total: cells.length, cells_better: cells.filter((row) => row.absolute_model_error_cents.median < row.absolute_current_ask_baseline_error_cents.median).length, cells_equal: cells.filter((row) => row.absolute_model_error_cents.median === row.absolute_current_ask_baseline_error_cents.median).length, cells_worse: cells.filter((row) => row.absolute_model_error_cents.median > row.absolute_current_ask_baseline_error_cents.median).length, predicted_edge_ge15_rows: predictions.filter((row) => row.predicted_median_edge_cents >= 15).length };
  const calibration = { schema_version: "WINDOW1_EXPECTED_CLOSE_CALIBRATION_V1", fit: { dates: "2026-07-12..2026-07-17", events: 525, legs: 1050, labeled_legs: new Set(labeledFit.map((row) => row.leg_identity)).size, sample_rows: labeledFit.length }, postfit: { dates: "2026-07-18..2026-07-20", events: 279, legs: 558, labeled_legs: new Set(labeledPost.map((row) => row.leg_identity)).size, sample_rows: labeledPost.length }, conservation: { population_events: 804, population_legs: 1608, close_unavailable_legs: allLegs.filter((row) => !quoteRows.find((source) => source.event_id === row.event_id && source.leg === row.leg_id)?.window1_close_cents).length, postfit_labeled_legs: new Set(labeledPost.map((row) => row.leg_identity)).size, postfit_unlabeled_legs: postLegs.length - new Set(labeledPost.map((row) => row.leg_identity)).size, predictions: predictions.length }, performance_partition_law: "category and current observable ask-price region; no pooled error statistic", comparison_to_current_ask_baseline: comparison, by_category_and_price_region: cells, thin_cells: thinCells };
  const entrymechFile = path.join(repo, ENTRYMECH_REL), mechanismFile = path.join(repo, MECHANISM_REL), mechanism = JSON.parse(fs.readFileSync(mechanismFile)), absent = mechanism.rows.filter((row) => ["Pinnacle", "authoritative_bookmaker_or_FV"].includes(row.mechanism)); if (absent.some((row) => row.classification !== "ABSENT")) throw new Error("external mechanism is not frozen absent");
  const externalCells = new Map(); for (const leg of allLegs) { const key = `${leg.category}|${leg.initial_price_region}`; if (!externalCells.has(key)) externalCells.set(key, new Set()); externalCells.get(key).add(`${leg.event_id}|${leg.leg_id}`); }
  const external = { schema_version: "WINDOW1_EXTERNAL_BOOK_COVERAGE_AUDIT_V1", population: { events: 804, legs: 1608 }, freshness_law: { pinnacle_betfair_matchbook_seconds: 1800, provenance: "existing FV overlap contract", betexplorer_seconds: 3600, betexplorer_not_in_sharp_books: true }, retained_july_source_truth: { odds_api_all_14_books_last_rows: "2026-07-10 13:00-13:42 ET", population_begins: "2026-07-12", external_rows_retained_in_frozen_window1_inputs: 0, mechanism_statuses: absent }, summary: { fresh_legs: 0, population_legs: 1608, fresh_rate: 0, predictive_comparison: "NOT_MEASURABLE_ZERO_FRESH_EXTERNAL_READS" }, by_category_and_starting_price_region: [...externalCells].sort(([a], [b]) => a.localeCompare(b)).map(([key, legs]) => { const [category, price_region] = key.split("|"); return { category, price_region, legs: legs.size, fresh_external_read_legs: 0, unavailable_legs: legs.size, coverage_rate: 0 }; }), forward_retention_required: ["append-only row per bookmaker poll and leg", "book key and raw odds", "de-vig fair value for both siblings", "provider source timestamp and local arrival timestamp", "event/ticker/player mapping plus mapping confidence", "raw response identity/hash", "poll failure and missing-tournament receipts", "freshness result at each consuming decision", "preserve complete history rather than latest value", "exclude circular 100-minus-Kalshi-price fallback from model authority"] };
  const binding = { schema_version: "WINDOW1_EXPECTED_CLOSE_CONTROL_BINDING_V1", status: "NOT_BOUND", reason: "The disjoint internal estimator beats the current-ask baseline in 0/16 category-price cells, 10 cells are thin, 301 legs lack close labels, and external-book predictive comparison is impossible because fresh July coverage is zero.", permitted_use: "DESCRIPTIVE_POSTFIT_CALIBRATION_ONLY", prohibited_use: ["fee-aware take authority", "first-leg commitment authority", "take-versus-rest authority", "five-game replay", "804 policy replay"], no_point_estimate_coercion: true, distribution_required: true, fit_test_disjoint: true, thin_cells: thinCells, comparison_to_current_ask_baseline: comparison };
  const aggressor = JSON.parse(fs.readFileSync(path.join(repo, AGGRESSOR_REL))), ceiling = JSON.parse(fs.readFileSync(path.join(repo, CEILING_REL))), commitment = JSON.parse(fs.readFileSync(path.join(repo, COMMITMENT_REL)));
  const decisions = { schema_version: "WINDOW1_EXPECTED_CLOSE_DECISION_UNLOCK_RECEIPT_V1", expected_close_binding: binding.status, fee_aware_take: { status: "BLOCKED_EXPECTED_CLOSE_NOT_BOUND", causal_516_clear_count: null, ex_post_5_of_516_not_promoted: true, rule: "sum(expected-close minus current ask) > sum exact five-lot taker fees" }, commitment: { status: "BLOCKED_JOINT_SIBLING_REACH_AND_OPERATOR_RISK_NOT_BOUND", observed_async_events: commitment.conservation.strict_first_leg_commitments, later_unaffordable_events: commitment.conservation.naked_or_never_completed_under_entry_cost_law, probability_spec: "P(first price + sibling reachable price + fees < pair budget | joint causal state)", threshold: null, threshold_reason: "requires operator-specified naked-risk utility/max holding loss plus a calibrated joint sibling-reach distribution; expected close alone is insufficient" }, take_vs_rest: { status: "BLOCKED_SELLER_PRINT_SHARE_IS_NOT_ORDER_FILL_PROBABILITY", aggressor_source: AGGRESSOR_REL, base_rate_partitions: { by_category_price_region: aggressor.by_category_and_starting_price_region, by_category_price_region_spread: aggressor.by_category_starting_price_region_and_spread }, required_model: "conditional seller-aggressed arrival hazard at-or-through proposed bid during intended residence, including queue-ahead and cancellation state", decision_spec: "rest only when expected maker value from calibrated fill hazard exceeds cross-now value net of fee; otherwise cross only when calibrated expected-close distribution clears fee/risk" }, policy_runs: { five_games: false, population_804: false, scorer_invocations: 0, performance_metrics: null }, frozen_take_ceiling: ceiling.controlling_take_ceiling };
  const requirements = { schema_version: "WINDOW1_EXPECTED_CLOSE_DATA_REQUIREMENTS_V1", current_blockers: binding, required_for_external_validation: external.forward_retention_required, required_for_commitment: ["calibrated joint distribution of sibling reachable ask and arrival time conditional on the first-leg state", "exact fee schedule", "operator-defined maximum naked duration/loss or utility threshold"], required_for_resting_fill_probability: ["order submission/cancel timestamps", "queue-ahead identity or bounded estimate", "seller-aggressed print at/through price", "displayed bid evolution", "order-specific resting interval", "honest maker/taker result"] };
  fs.mkdirSync(out, { recursive: true });
  const modelArtifact = { ...model, groups: Object.fromEntries(Object.entries(model.groups).map(([key, group]) => [key, { centers: group.centers, scales: group.scales, training_legs: group.training_legs, training_events: group.training_events, rows: group.rows.map(({ feature_vector, ...row }) => ({ ...row, feature_vector })) }])) };
  fs.writeFileSync(path.join(out, "EXPECTED_CLOSE_MODEL.json"), canonical(modelArtifact));
  fs.writeFileSync(path.join(out, "FIT_ONLY_QUOTE_SHAPE_LIBRARY.json"), canonical(shapeLibrary));
  fs.writeFileSync(path.join(out, "POSTFIT_CALIBRATION.json"), canonical(calibration));
  fs.writeFileSync(path.join(out, "POSTFIT_PREDICTIONS.jsonl.gz"), gzipDeterministic(predictions.map(JSON.stringify).join("\n") + "\n"));
  fs.writeFileSync(path.join(out, "EXTERNAL_BOOK_COVERAGE.json"), canonical(external));
  fs.writeFileSync(path.join(out, "CONTROL_BINDING.json"), canonical(binding));
  fs.writeFileSync(path.join(out, "DECISION_UNLOCK_RECEIPT.json"), canonical(decisions));
  fs.writeFileSync(path.join(out, "DATA_REQUIREMENTS.json"), canonical(requirements));
  fs.writeFileSync(path.join(out, "REPORT.md"), markdown(binding, external, calibration, decisions));
  const sourceManifest = { schema_version: "WINDOW1_EXPECTED_CLOSE_SOURCE_MANIFEST_V1", committed: Object.fromEntries([QUOTE_REL, ENTRYMECH_REL, MECHANISM_REL, AGGRESSOR_REL, CEILING_REL, COMMITMENT_REL].map((relative) => { const file = path.join(repo, relative); return [relative, { bytes: fs.statSync(file).size, sha256: fileHash(file) }]; })), private_tick_files: Object.fromEntries(scanned.flatMap((event) => event.legs.map((leg) => [leg.tick_source.path, { bytes: leg.tick_source.bytes, sha256: leg.tick_source.sha256 }]))), private_guarded_cache_v3: Object.fromEntries(scanned.map((event) => [event.cache_source.path, { bytes: event.cache_source.bytes, sha256: event.cache_source.sha256 }])) };
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical(sourceManifest));
  const artifactNames = ["CONTROL_BINDING.json", "DATA_REQUIREMENTS.json", "DECISION_UNLOCK_RECEIPT.json", "EXPECTED_CLOSE_MODEL.json", "EXTERNAL_BOOK_COVERAGE.json", "FIT_ONLY_QUOTE_SHAPE_LIBRARY.json", "POSTFIT_CALIBRATION.json", "POSTFIT_PREDICTIONS.jsonl.gz", "REPORT.md", "SOURCE_HASH_MANIFEST.json"], artifacts = { schema_version: "WINDOW1_EXPECTED_CLOSE_ARTIFACT_MANIFEST_V1", artifacts: Object.fromEntries(artifactNames.map((name) => [name, { bytes: fs.statSync(path.join(out, name)).size, sha256: fileHash(path.join(out, name)) }])) };
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical(artifacts));
  process.stdout.write(canonical({ status: binding.status, events: 804, legs: 1608, fit_labeled_legs: calibration.fit.labeled_legs, postfit_labeled_legs: calibration.postfit.labeled_legs, postfit_predictions: predictions.length, thin_cells: thinCells, external_fresh_legs: 0, output: path.relative(repo, out).replaceAll("\\", "/") }));
}

if (isMainThread) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }); else workerMain().catch((error) => { throw error; });
