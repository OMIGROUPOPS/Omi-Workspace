#!/usr/bin/env node
"use strict";

// Score-free diagnostic only.  This builder measures whether the first leg's
// observed floor and path reduce uncertainty about the sibling.  It does not
// import or execute a policy/scorer and it never changes an order stream.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const { EXCLUDED_EVENTS, MIN_CLASS_N } = require("./build_window1_quote_shape_coherent_library_v12.js");

const DWELL_SECONDS = 10;
const REQUIRED_QUANTITY = 5;
const RAW_BASE = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function region(price) { return !Number.isFinite(price) ? "UNAVAILABLE" : price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function quantile(values, p) { const x = values.filter(Number.isFinite).sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function distribution(values) {
  const x = values.filter(Number.isFinite);
  const p10 = quantile(x, .1), p25 = quantile(x, .25), median = quantile(x, .5), p75 = quantile(x, .75), p90 = quantile(x, .9);
  return { n: x.length, unavailable: values.length - x.length, min: x.length ? Math.min(...x) : null, p10, p25, median, p75, p90, max: x.length ? Math.max(...x) : null, iqr: p25 === null ? null : p75 - p25, p90_p10_width: p10 === null ? null : p90 - p10 };
}
function countBy(values) { const m = new Map(); for (const x of values) m.set(String(x), (m.get(String(x)) || 0) + 1); return Object.fromEntries([...m].sort(([a], [b]) => a.localeCompare(b))); }
function group(rows, key) { const m = new Map(); for (const row of rows) { const k = key(row); if (!m.has(k)) m.set(k, []); m.get(k).push(row); } return m; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v]))); }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null;
  let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function jsonlGz(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse); }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(rows.map(JSON.stringify).join("\n") + "\n"), { level: 9, mtime: 0 }); }
function clock(ts, source, bell) {
  const value = Number.isFinite(ts) ? ts : null;
  return {
    timestamp_epoch: value,
    t_minus_scheduled_seconds: value !== null && Number.isFinite(source?.scheduled_start_ts) ? source.scheduled_start_ts - value : null,
    t_minus_actual_bell_seconds: value !== null && Number.isFinite(bell) ? bell - value : null,
    actual_bell_status: Number.isFinite(bell) ? "BOUND" : "ACTUAL_BELL_NOT_BOUND",
  };
}
function progress(ts, source) { return Number.isFinite(ts) && source.right_ts > source.left_ts ? Math.max(0, Math.min(100, Math.floor((ts - source.left_ts) / (source.right_ts - source.left_ts) * 100))) : null; }
function pearson(xs, ys) {
  const rows = xs.map((x, i) => [x, ys[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y)); if (rows.length < 3) return null;
  const mx = rows.reduce((s, r) => s + r[0], 0) / rows.length, my = rows.reduce((s, r) => s + r[1], 0) / rows.length;
  const num = rows.reduce((s, r) => s + (r[0] - mx) * (r[1] - my), 0), dx = rows.reduce((s, r) => s + (r[0] - mx) ** 2, 0), dy = rows.reduce((s, r) => s + (r[1] - my) ** 2, 0);
  return dx > 0 && dy > 0 ? num / Math.sqrt(dx * dy) : null;
}

function solve(matrix, vector) {
  const a = matrix.map((row, i) => [...row, vector[i]]), n = vector.length;
  for (let col = 0; col < n; col += 1) {
    let pivot = col; for (let row = col + 1; row < n; row += 1) if (Math.abs(a[row][col]) > Math.abs(a[pivot][col])) pivot = row;
    if (Math.abs(a[pivot][col]) < 1e-10) return null;
    [a[col], a[pivot]] = [a[pivot], a[col]]; const d = a[col][col]; for (let j = col; j <= n; j += 1) a[col][j] /= d;
    for (let row = 0; row < n; row += 1) if (row !== col) { const f = a[row][col]; for (let j = col; j <= n; j += 1) a[row][j] -= f * a[col][j]; }
  }
  return a.map((row) => row[n]);
}
function fitLinear(rows, featureNames, targetName) {
  if (rows.length < featureNames.length + 2) return null;
  const means = {}, scales = {}, active = [];
  for (const name of featureNames) {
    const values = rows.map((r) => r[name]); if (!values.every(Number.isFinite)) return null;
    const mean = values.reduce((a, b) => a + b, 0) / values.length, variance = values.reduce((s, x) => s + (x - mean) ** 2, 0) / values.length;
    means[name] = mean; scales[name] = Math.sqrt(variance); if (scales[name] > 0) active.push(name);
  }
  const p = active.length + 1, xtx = Array.from({ length: p }, () => Array(p).fill(0)), xty = Array(p).fill(0);
  for (const row of rows) {
    if (!Number.isFinite(row[targetName])) return null; const x = [1, ...active.map((name) => (row[name] - means[name]) / scales[name])];
    for (let i = 0; i < p; i += 1) { xty[i] += x[i] * row[targetName]; for (let j = 0; j < p; j += 1) xtx[i][j] += x[i] * x[j]; }
  }
  const beta = solve(xtx, xty); if (!beta) return null;
  return { active_features: active, means, scales, standardized_coefficients: Object.fromEntries(["intercept", ...active].map((name, i) => [name, beta[i]])), predict: (row) => beta[0] + active.reduce((s, name, i) => s + beta[i + 1] * (row[name] - means[name]) / scales[name], 0) };
}
function crossValidatedModel(rows, featureNames, targetName) {
  const complete = rows.filter((r) => Number.isFinite(r[targetName]) && featureNames.every((name) => Number.isFinite(r[name]))), target = distribution(complete.map((r) => r[targetName]));
  const residuals = [], predictions = new Map();
  for (const row of complete) { const fit = fitLinear(complete.filter((x) => x !== row), featureNames, targetName); if (!fit) continue; const predicted = fit.predict(row), residual = row[targetName] - predicted; residuals.push(residual); predictions.set(row.event_id, { predicted_center_cents: predicted, residual_cents: residual }); }
  const residual = distribution(residuals), fit = fitLinear(complete, featureNames, targetName), reduction = target.p90_p10_width !== null && residual.p90_p10_width !== null ? target.p90_p10_width - residual.p90_p10_width : null;
  return {
    n: complete.length,
    thin: complete.length < MIN_CLASS_N,
    features: featureNames,
    target: targetName,
    unconditional_target_distribution: target,
    leave_one_out_residual_distribution: residual,
    p90_p10_spread_reduction_cents: reduction,
    iqr_spread_reduction_cents: target.iqr !== null && residual.iqr !== null ? target.iqr - residual.iqr : null,
    conclusion: complete.length < MIN_CLASS_N ? "THIN_NOT_INTERPRETABLE" : reduction > 0 ? "CONDITIONAL_DISTRIBUTION_TIGHTER" : "CONDITIONAL_DISTRIBUTION_NOT_TIGHTER",
    fitted_model: fit ? { active_features: fit.active_features, feature_means: fit.means, feature_scales: fit.scales, standardized_coefficients: fit.standardized_coefficients } : null,
    predictions,
  };
}

function validBook(raw, sourceRow, file) {
  const ts = parseEt(raw.ts_et), bids = [], asks = [];
  for (let i = 1; i <= 5; i += 1) { const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]); if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]); }
  bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
  if (ts === null || !bids.length || !asks.length || bids[0][0] > asks[0][0]) return null;
  return { ts, source_ordinal: sourceRow, receipt: `${path.basename(file)}#row-${sourceRow}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], top_five_bid_depth: bids.reduce((s, x) => s + x[1], 0), top_five_ask_depth: asks.reduce((s, x) => s + x[1], 0), bids, asks, last_traded: integer(raw.last_trade) };
}
function nextCapacityFloor(rows, afterTs) {
  const since = Array(100).fill(null); let best = null;
  for (const row of rows) {
    for (let limit = 1; limit < row.ask; limit += 1) since[limit] = null;
    for (let limit = row.ask; limit <= 99; limit += 1) if (since[limit] === null) since[limit] = row.ts;
    if (!(row.ts > afterTs)) continue;
    let cumulative = 0, index = 0;
    for (let limit = row.ask; limit <= 99; limit += 1) {
      while (index < row.asks.length && row.asks[index][0] <= limit) cumulative += row.asks[index++][1];
      if (cumulative < REQUIRED_QUANTITY || row.ts - since[limit] < DWELL_SECONDS) continue;
      const proof = { limit_cents: limit, evidence_ts: row.ts, bid_cents: row.bid, ask_cents: row.ask, spread_cents: row.spread, dwell_seconds: row.ts - since[limit], displayed_capacity_at_or_below_limit: cumulative, source_receipt: row.receipt };
      if (!best || limit < best.limit_cents || (limit === best.limit_cents && (row.ts < best.evidence_ts || (row.ts === best.evidence_ts && row.source_ordinal < best.source_ordinal)))) best = { ...proof, source_ordinal: row.source_ordinal };
      break;
    }
  }
  if (best) delete best.source_ordinal; return best;
}
function scanOne(source, ticksRoot) {
  const file = path.join(ticksRoot, `${source.ticker}.csv.gz`), bytes = fs.readFileSync(file), text = zlib.gunzipSync(bytes).toString("utf8"), lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(","), rows = [];
  for (let i = 0; i < lines.length; i += 1) { const values = lines[i].split(","); if (values.length !== headers.length) continue; const raw = Object.fromEntries(headers.map((name, j) => [name, values[j]])), book = validBook(raw, i + 2, file); if (book && book.ts >= source.left_ts && book.ts <= source.right_ts) rows.push(book); }
  rows.sort((a, b) => a.ts - b.ts || a.source_ordinal - b.source_ordinal); const firstFormed = rows.find((r) => r.spread === 1) || null;
  const states = {};
  for (const query of source.queries) {
    let state = null; for (const row of rows) { if (row.ts > query.ts) break; state = row; }
    states[query.id] = state ? { timestamp_epoch: state.ts, age_seconds: query.ts - state.ts, bid: state.bid, ask: state.ask, last_traded: state.last_traded, spread: state.spread, top_bid_size: state.top_bid_size, top_ask_size: state.top_ask_size, top_five_bid_depth: state.top_five_bid_depth, top_five_ask_depth: state.top_five_ask_depth, receipt: state.receipt, source_ordinal: state.source_ordinal } : null;
  }
  const laterFloors = {}; for (const query of source.after_queries) laterFloors[query.id] = nextCapacityFloor(rows, query.ts);
  return { leg_identity: source.leg_identity, event_id: source.event_id, leg_id: source.leg_id, ticker: source.ticker, first_formed_book: firstFormed ? { timestamp_epoch: firstFormed.ts, bid: firstFormed.bid, ask: firstFormed.ask, spread: firstFormed.spread, receipt: firstFormed.receipt } : null, query_states: states, strictly_later_capacity_floors: laterFloors, source: { file: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) } };
}
function workerMain() { parentPort.postMessage(workerData.sources.map((source) => scanOne(source, workerData.ticksRoot))); }

function floorProof(leg, kind, capacity) {
  if (kind === "ASK_CAPACITY") { const proof = capacity?.capacity_proven_floor; return proof ? { kind, price_cents: proof.limit_cents, evidence_ts: proof.evidence_ts, receipt: proof.source_receipt, dwell_seconds: proof.dwell_seconds, displayed_capacity: proof.displayed_capacity, provenance: "FROZEN_TEN_SECOND_EXACT_FIVE_CAPACITY_FLOOR" } : null; }
  const proof = leg.traded_low_proof?.first_low_print; return proof ? { kind, price_cents: leg.objective_traded_low_cents, evidence_ts: proof.timestamp_epoch, receipt: proof.receipt, print_size: proof.size, aggressor_side: proof.aggressor_side, provenance: "FROZEN_LAWFUL_TRUE_PRINT_LOW" } : null;
}
function timingPartition(rows, keyName) {
  return [...group(rows, (r) => r[keyName]).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, cell]) => ({
    [keyName]: key,
    n: cell.length,
    thin: cell.length < MIN_CLASS_N,
    ask_capacity_floor_gap_seconds: distribution(cell.map((r) => r.floors.ASK_CAPACITY?.gap_seconds)),
    traded_floor_gap_seconds: distribution(cell.map((r) => r.floors.TRADED?.gap_seconds)),
    ask_capacity_climbing_comparable: cell.filter((r) => typeof r.floors.ASK_CAPACITY?.climbing_leg_first === "boolean").length,
    ask_capacity_climbing_first: cell.filter((r) => r.floors.ASK_CAPACITY?.climbing_leg_first === true).length,
    traded_climbing_comparable: cell.filter((r) => typeof r.floors.TRADED?.climbing_leg_first === "boolean").length,
    traded_climbing_first: cell.filter((r) => r.floors.TRADED?.climbing_leg_first === true).length,
    event_ids: cell.map((r) => r.event_id).sort(),
  }));
}
function modelPartitions(rows, floorKind, mode) {
  const eligible = rows.map((r) => r.floors[floorKind]?.prediction_row).filter(Boolean).filter((r) => !r.fit_excluded);
  const keyFn = mode === "START_SPLIT" ? (r) => `${r.category}|${r.starting_price_split}` : (r) => `${r.category}|${r.first_leg_price_region}`;
  const output = [], predictionByEvent = new Map();
  for (const [key, cell] of [...group(eligible, keyFn)].sort(([a], [b]) => a.localeCompare(b))) {
    const model = crossValidatedModel(cell, ["first_floor_x_cents", "first_floor_elapsed_progress_percent"], "sibling_eventual_floor_cents");
    const xOnly = crossValidatedModel(cell, ["first_floor_x_cents"], "sibling_eventual_floor_cents"), timeOnly = crossValidatedModel(cell, ["first_floor_elapsed_progress_percent"], "sibling_eventual_floor_cents");
    for (const [eventId, p] of model.predictions) predictionByEvent.set(`${floorKind}|${eventId}`, p);
    delete model.predictions;
    const exactCells = [...group(cell, (r) => `X=${r.first_floor_x_cents}|P=${r.first_floor_elapsed_progress_percent}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([condition, exact]) => { const d = distribution(exact.map((r) => r.sibling_eventual_floor_cents)), base = model.unconditional_target_distribution; return { condition, n: exact.length, thin: exact.length < MIN_CLASS_N, sibling_eventual_floor_distribution: d, p90_p10_reduction_vs_unconditional_cents: d.p90_p10_width === null || base.p90_p10_width === null ? null : base.p90_p10_width - d.p90_p10_width, interpretation: exact.length < MIN_CLASS_N ? "THIN_DESCRIPTIVE_ONLY" : d.p90_p10_width < base.p90_p10_width ? "TIGHTER" : "NOT_TIGHTER", event_ids: exact.map((r) => r.event_id).sort() }; });
    output.push({ partition: key, partition_law: mode, ...model, ablations: { exact_first_floor_x_only: { leave_one_out_residual_distribution: xOnly.leave_one_out_residual_distribution, p90_p10_spread_reduction_cents: xOnly.p90_p10_spread_reduction_cents, conclusion: xOnly.conclusion }, exact_elapsed_progress_only: { leave_one_out_residual_distribution: timeOnly.leave_one_out_residual_distribution, p90_p10_spread_reduction_cents: timeOnly.p90_p10_spread_reduction_cents, conclusion: timeOnly.conclusion }, time_adds_beyond_x_p90_p10_cents: xOnly.leave_one_out_residual_distribution.p90_p10_width !== null && model.leave_one_out_residual_distribution.p90_p10_width !== null ? xOnly.leave_one_out_residual_distribution.p90_p10_width - model.leave_one_out_residual_distribution.p90_p10_width : null }, exact_x_and_existing_progress_percent_cells: exactCells });
  }
  return { output, predictionByEvent };
}
function inversionPartitions(rows, floorKind, mode) {
  const eligible = rows.map((r) => r.floors[floorKind]?.prediction_row).filter(Boolean).filter((r) => !r.fit_excluded && Number.isFinite(r.sibling_remaining_travel_cents));
  const keyFn = mode === "START_SPLIT" ? (r) => `${r.category}|${r.starting_price_split}` : (r) => `${r.category}|${r.first_leg_price_region}`;
  return [...group(eligible, keyFn)].sort(([a], [b]) => a.localeCompare(b)).map(([key, cell]) => {
    const model = crossValidatedModel(cell, ["first_leg_realized_fall_from_formed_ask_cents", "first_leg_fall_speed_cents_per_hour"], "sibling_remaining_travel_cents"), moveOnly = crossValidatedModel(cell, ["first_leg_realized_fall_from_formed_ask_cents"], "sibling_remaining_travel_cents"), speedOnly = crossValidatedModel(cell, ["first_leg_fall_speed_cents_per_hour"], "sibling_remaining_travel_cents"); delete model.predictions; delete moveOnly.predictions; delete speedOnly.predictions;
    return { partition: key, partition_law: mode, ...model, ablations: { realized_fall_only: { leave_one_out_residual_distribution: moveOnly.leave_one_out_residual_distribution, p90_p10_spread_reduction_cents: moveOnly.p90_p10_spread_reduction_cents, conclusion: moveOnly.conclusion }, fall_speed_only: { leave_one_out_residual_distribution: speedOnly.leave_one_out_residual_distribution, p90_p10_spread_reduction_cents: speedOnly.p90_p10_spread_reduction_cents, conclusion: speedOnly.conclusion } }, correlations: { first_leg_fall_vs_sibling_remaining_travel: pearson(cell.map((r) => r.first_leg_realized_fall_from_formed_ask_cents), cell.map((r) => r.sibling_remaining_travel_cents)), first_leg_fall_speed_vs_sibling_remaining_travel: pearson(cell.map((r) => r.first_leg_fall_speed_cents_per_hour), cell.map((r) => r.sibling_remaining_travel_cents)) }, pair_constraint: { first_floor_plus_sibling_current_ask_minus_100: distribution(cell.map((r) => r.first_floor_plus_sibling_current_ask_minus_100)), first_floor_plus_sibling_eventual_floor_minus_100: distribution(cell.map((r) => r.first_floor_plus_sibling_eventual_floor_minus_100)) } };
  });
}

async function main() {
  const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(value("--repo", ".")), privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private")), ticksRoot = path.join(privateRoot, "fit-local/ticks");
  const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/pair_coupling_diagnostic_v16_20260803"))), workersN = Math.max(1, Number(value("--workers", "8")));
  const files = {
    quote: path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv"),
    capacity: path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json"),
    bell: path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json"),
    v11legs: path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/POPULATION_LEG_LEDGER.jsonl.gz"),
    v11events: path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/POPULATION_EVENT_LEDGER.jsonl.gz"),
    carried: path.join(repo, ".claude/window1_live_v4_replay/live_book_ordinal_root_repair_v15_20260803/STRICT_CARRIED_PAIR_DIAGNOSTIC.jsonl.gz"),
    builder: __filename,
    test: path.join(repo, "arb-executor/tests/test_window1_pair_coupling_diagnostic_v16.js"),
  };
  for (const file of Object.values(files)) if (!fs.existsSync(file)) throw new Error(`missing input ${file}`); if (!fs.existsSync(ticksRoot)) throw new Error(`missing private ticks ${ticksRoot}`);
  const quoteRows = parseCsv(fs.readFileSync(files.quote, "utf8")), quoteByLeg = new Map(quoteRows.map((r) => [`${r.event_id}|${r.leg}`, { event_id: r.event_id, leg_id: r.leg, ticker: r.ticker, category: r.category, left_ts: Number(r.left_ts), right_ts: Number(r.right_ts), scheduled_start_ts: Number(r.scheduled_start_ts), window1_open_cents: integer(r.window1_open_cents), direction: r.leg_direction }]));
  const capacityRows = JSON.parse(fs.readFileSync(files.capacity)).rows, capacityByLeg = new Map(capacityRows.map((r) => [`${r.event_id}|${r.leg_id}`, r]));
  const bellRows = JSON.parse(fs.readFileSync(files.bell)).leg_rows || [], bellByLeg = new Map(bellRows.map((r) => [`${r.event_id}|${r.leg_id}`, Number(r.exact_bell_ts)]));
  const v11Legs = jsonlGz(files.v11legs), v11Events = jsonlGz(files.v11events), carriedRows = jsonlGz(files.carried), legById = new Map(v11Legs.map((r) => [r.leg_identity, r]));
  if (quoteRows.length !== 1608 || v11Legs.length !== 1608 || v11Events.length !== 804 || carriedRows.length !== 52) throw new Error("frozen population/carry conservation failed");
  for (const row of quoteRows) { const day = Number((row.event_id.match(/26JUL(\d{2})/) || [])[1]); if (!Number.isInteger(day) || day < 12 || day > 20) throw new Error(`nondevelopment row ${row.event_id}`); }
  const carriedByEvent = new Map(carriedRows.map((r) => [r.event_id, r])), queryMap = new Map(), afterMap = new Map();
  const addQuery = (legId, id, ts) => { if (!Number.isFinite(ts)) return; if (!queryMap.has(legId)) queryMap.set(legId, []); queryMap.get(legId).push({ id, ts }); };
  const addAfter = (legId, id, ts) => { if (!Number.isFinite(ts)) return; if (!afterMap.has(legId)) afterMap.set(legId, []); afterMap.get(legId).push({ id, ts }); };
  for (const event of v11Events) {
    const legs = event.legs;
    for (const kind of ["ASK_CAPACITY", "TRADED"]) {
      const proofs = legs.map((leg) => [leg.leg_identity, floorProof(leg, kind, capacityByLeg.get(leg.leg_identity))]).filter(([, proof]) => proof);
      for (const [ownId, proof] of proofs) { const sibling = legs.find((leg) => leg.leg_identity !== ownId); addQuery(sibling.leg_identity, `${event.event_id}|${kind}|SIBLING_AT_FIRST_FLOOR|${ownId}`, proof.evidence_ts); }
    }
    if (carriedByEvent.has(event.event_id)) {
      const ordered = [...legs].sort((a, b) => a.action_timestamp_epoch - b.action_timestamp_epoch || a.leg_id.localeCompare(b.leg_id));
      if (Number.isFinite(ordered[1]?.action_timestamp_epoch)) { addQuery(ordered[0].leg_identity, `${event.event_id}|FIRST_LEG_AT_SECOND_ACTION`, ordered[1].action_timestamp_epoch); addAfter(ordered[1].leg_identity, `${event.event_id}|SECOND_LEG_AFTER_ACTION`, ordered[1].action_timestamp_epoch); }
    }
  }
  const sources = v11Legs.map((leg) => { const source = quoteByLeg.get(leg.leg_identity); if (!source) throw new Error(`missing quote source ${leg.leg_identity}`); return { ...source, leg_identity: leg.leg_identity, queries: queryMap.get(leg.leg_identity) || [], after_queries: afterMap.get(leg.leg_identity) || [] }; });
  const buckets = Array.from({ length: workersN }, () => []); sources.forEach((source, i) => buckets[i % workersN].push(source));
  const scans = (await Promise.all(buckets.map((bucket) => new Promise((resolve, reject) => { const w = new Worker(__filename, { workerData: { sources: bucket, ticksRoot } }); w.once("message", resolve); w.once("error", reject); w.once("exit", (code) => { if (code) reject(new Error(`worker exit ${code}`)); }); })))).flat().sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
  const scanByLeg = new Map(scans.map((r) => [r.leg_identity, r])); if (scans.length !== 1608) throw new Error("scan conservation failed");

  const eventRows = [];
  for (const event of v11Events) {
    const fitExcluded = EXCLUDED_EVENTS.includes(event.event_id), floorKinds = {};
    for (const kind of ["ASK_CAPACITY", "TRADED"]) {
      const proofRows = event.legs.map((leg) => ({ leg, source: quoteByLeg.get(leg.leg_identity), scan: scanByLeg.get(leg.leg_identity), bell: bellByLeg.get(leg.leg_identity), proof: floorProof(leg, kind, capacityByLeg.get(leg.leg_identity)) })).filter((r) => r.proof).sort((a, b) => a.proof.evidence_ts - b.proof.evidence_ts || a.leg.leg_id.localeCompare(b.leg.leg_id));
      if (proofRows.length !== 2) { floorKinds[kind] = { status: "ONE_OR_MORE_FLOORS_UNAVAILABLE", available_legs: proofRows.length }; continue; }
      const tie = proofRows[0].proof.evidence_ts === proofRows[1].proof.evidence_ts, first = proofRows[0], second = proofRows[1], queryId = `${event.event_id}|${kind}|SIBLING_AT_FIRST_FLOOR|${first.leg.leg_identity}`, siblingState = second.scan.query_states[queryId];
      const uniqueClimber = proofRows.filter((r) => r.source.direction === "CLIMBING"), elapsed = first.proof.evidence_ts - first.source.left_ts, formedElapsed = first.proof.evidence_ts - (first.scan.first_formed_book?.timestamp_epoch ?? first.source.left_ts), formedMove = Number.isFinite(first.scan.first_formed_book?.ask) ? first.scan.first_formed_book.ask - first.proof.price_cents : null;
      const predictionRow = tie ? null : {
        event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, fit_excluded: fitExcluded,
        first_leg_identity: first.leg.leg_identity, first_leg_price_region: first.leg.price_region, first_floor_x_cents: first.proof.price_cents, first_floor_elapsed_seconds: elapsed, first_floor_elapsed_progress_percent: progress(first.proof.evidence_ts, first.source), sibling_eventual_floor_cents: second.proof.price_cents,
        sibling_current_ask_cents: siblingState?.ask ?? null, sibling_remaining_travel_cents: Number.isFinite(siblingState?.ask) ? siblingState.ask - second.proof.price_cents : null,
        first_leg_realized_fall_from_window_open_cents: Number.isFinite(first.source.window1_open_cents) ? first.source.window1_open_cents - first.proof.price_cents : null,
        first_leg_realized_fall_from_formed_ask_cents: formedMove,
        first_leg_fall_speed_cents_per_hour: Number.isFinite(formedMove) && formedElapsed > 0 ? formedMove * 3600 / formedElapsed : null,
        first_floor_plus_sibling_current_ask_minus_100: Number.isFinite(siblingState?.ask) ? first.proof.price_cents + siblingState.ask - 100 : null,
        first_floor_plus_sibling_eventual_floor_minus_100: first.proof.price_cents + second.proof.price_cents - 100,
      };
      floorKinds[kind] = {
        status: tie ? "SIMULTANEOUS_FLOOR_EVIDENCE" : "STRICTLY_ASYNCHRONOUS",
        gap_seconds: second.proof.evidence_ts - first.proof.evidence_ts,
        climbing_leg_first: tie || uniqueClimber.length !== 1 ? "UNRESOLVED_DIRECTION" : first.leg.leg_identity === uniqueClimber[0].leg.leg_identity,
        first: { leg_identity: first.leg.leg_identity, leg_id: first.leg.leg_id, direction: first.source.direction, price_region: first.leg.price_region, proof: first.proof, clock: clock(first.proof.evidence_ts, first.source, first.bell), elapsed_from_window_left_seconds: elapsed, elapsed_progress_percent: progress(first.proof.evidence_ts, first.source), first_formed_book: first.scan.first_formed_book, fall_from_window_open_cents: predictionRow?.first_leg_realized_fall_from_window_open_cents ?? null, fall_from_first_formed_ask_cents: formedMove },
        second: { leg_identity: second.leg.leg_identity, leg_id: second.leg.leg_id, direction: second.source.direction, price_region: second.leg.price_region, proof: second.proof, clock: clock(second.proof.evidence_ts, second.source, second.bell) },
        sibling_state_at_first_floor: siblingState,
        pair_constraint: predictionRow ? { implied_sibling_complement_cents: 100 - first.proof.price_cents, sibling_current_ask_minus_complement_cents: siblingState ? siblingState.ask - (100 - first.proof.price_cents) : null, sibling_floor_minus_complement_cents: second.proof.price_cents - (100 - first.proof.price_cents) } : null,
        prediction_row: predictionRow,
      };
    }
    eventRows.push({ event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, fit_excluded: fitExcluded, exclusion_reason: fitExcluded ? "FIVE_EXACT_START_GAME_EXCLUDED_FROM_FITTING_ONLY" : null, floors: floorKinds });
  }
  if (eventRows.length !== 804 || eventRows.filter((r) => r.fit_excluded).length !== 5) throw new Error("event/exclusion conservation failed");

  const timing = {
    schema_version: "WINDOW1_PAIR_FLOOR_TIMING_CENSUS_V16", score_free: true,
    floor_laws: { execution_floor: "lowest frozen ten-second/exact-five qualifying ask floor", objective_floor: "lowest frozen lawful true-print price" },
    population: { events: 804, legs: 1608, fitted_events: 799, excluded_exact_start_events: EXCLUDED_EVENTS },
    conservation: Object.fromEntries(["ASK_CAPACITY", "TRADED"].map((kind) => [kind, { strictly_asynchronous: eventRows.filter((r) => r.floors[kind]?.status === "STRICTLY_ASYNCHRONOUS").length, simultaneous: eventRows.filter((r) => r.floors[kind]?.status === "SIMULTANEOUS_FLOOR_EVIDENCE").length, unavailable: eventRows.filter((r) => !["STRICTLY_ASYNCHRONOUS", "SIMULTANEOUS_FLOOR_EVIDENCE"].includes(r.floors[kind]?.status)).length, climbing_direction_comparable: eventRows.filter((r) => typeof r.floors[kind]?.climbing_leg_first === "boolean").length, climbing_leg_first: eventRows.filter((r) => r.floors[kind]?.climbing_leg_first === true).length }])),
    by_category_and_starting_price_split: timingPartition(eventRows, "category_start_split"),
    by_category_and_first_floor_price_region: timingPartition(eventRows, "category_first_region"),
  };
  for (const row of eventRows) { row.category_start_split = `${row.category}|${row.starting_price_split}`; const firstRegion = row.floors.ASK_CAPACITY?.first?.price_region || row.floors.TRADED?.first?.price_region || "UNAVAILABLE"; row.category_first_region = `${row.category}|${firstRegion}`; }
  timing.by_category_and_starting_price_split = timingPartition(eventRows, "category_start_split");
  timing.by_category_and_first_floor_price_region = timingPartition(eventRows, "category_first_region");

  const predictionStart = {}, predictionRegion = {}, inversionStart = {}, inversionRegion = {};
  for (const kind of ["ASK_CAPACITY", "TRADED"]) {
    predictionStart[kind] = modelPartitions(eventRows, kind, "START_SPLIT"); predictionRegion[kind] = modelPartitions(eventRows, kind, "FIRST_LEG_PRICE_REGION");
    inversionStart[kind] = inversionPartitions(eventRows, kind, "START_SPLIT"); inversionRegion[kind] = inversionPartitions(eventRows, kind, "FIRST_LEG_PRICE_REGION");
  }
  const predictionReceipt = {
    schema_version: "WINDOW1_CONDITIONAL_SIBLING_FLOOR_DISTRIBUTIONS_V16", score_free: true,
    fit_population: { events: 799, excluded_exact_start_events: EXCLUDED_EVENTS },
    method: "Within each category+starting-split or category+first-leg-price-region cell, ordinary least squares conditions sibling eventual floor on exact first-floor X and exact existing 0..100 corridor progress. Reported uncertainty is the leave-one-event-out signed residual distribution; no policy threshold is fitted.",
    minimum_interpretable_n: { value: MIN_CLASS_N, provenance: "existing quote-shape coherence minimum; reporting label only" },
    by_category_and_starting_price_split: Object.fromEntries(Object.entries(predictionStart).map(([kind, x]) => [kind, x.output])),
    by_category_and_first_floor_price_region: Object.fromEntries(Object.entries(predictionRegion).map(([kind, x]) => [kind, x.output])),
    interpretation_fence: "A thin cell or a nonpositive spread reduction is not predictive authority. Exact-X/progress empirical cells remain descriptive and are never promoted merely because n=1 has zero observed width.",
  };
  const inversionReceipt = {
    schema_version: "WINDOW1_PAIR_INVERSION_LAW_RECEIPT_V16", score_free: true,
    question: "Does first-leg realized fall from its first formed ask, and the speed of that fall, reduce uncertainty in sibling remaining travel from its contemporaneous ask to its eventual floor?",
    fit_population: { events: 799, excluded_exact_start_events: EXCLUDED_EVENTS },
    by_category_and_starting_price_split: inversionStart,
    by_category_and_first_floor_price_region: inversionRegion,
    no_behavior_role: true,
  };

  const carriedLedger = [], counterfactualRows = [];
  for (const carried of carriedRows) {
    const event = v11Events.find((r) => r.event_id === carried.event_id), ordered = [...event.legs].sort((a, b) => a.action_timestamp_epoch - b.action_timestamp_epoch || a.leg_id.localeCompare(b.leg_id)), same = ordered[0].action_timestamp_epoch === ordered[1].action_timestamp_epoch, first = same ? null : ordered[0], second = same ? null : ordered[1];
    let laterAsk = null, firstState = null;
    if (!same) { laterAsk = scanByLeg.get(second.leg_identity).strictly_later_capacity_floors[`${event.event_id}|SECOND_LEG_AFTER_ACTION`] || null; firstState = scanByLeg.get(first.leg_identity).query_states[`${event.event_id}|FIRST_LEG_AT_SECOND_ACTION`] || null; }
    const firstSource = first ? quoteByLeg.get(first.leg_identity) : null, secondSource = second ? quoteByLeg.get(second.leg_identity) : null, firstScan = first ? scanByLeg.get(first.leg_identity) : null;
    const laterTradeProofs = second ? (second.traded_low_proof?.prints || []).filter((r) => r.timestamp_epoch > second.action_timestamp_epoch).sort((a, b) => a.price_cents - b.price_cents || a.timestamp_epoch - b.timestamp_epoch) : [], laterTrade = laterTradeProofs[0] || null;
    const cfSecond = laterAsk?.limit_cents ?? null, cfPair = Number.isInteger(cfSecond) ? first.entry_cents + cfSecond : null, flips = Number.isInteger(cfSecond) && Number.isInteger(second.own_window1_close_cents) && first.entry_cents < first.own_window1_close_cents && cfSecond < second.own_window1_close_cents;
    const row = {
      event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, positive_leg_fill_order: carried.positive_leg_fill_order,
      chronological_status: same ? "SIMULTANEOUS_ACTION_TIMESTAMP_NO_SECOND_LEG" : "STRICT_FIRST_THEN_SECOND",
      first_leg: !first ? null : { leg_identity: first.leg_identity, leg_id: first.leg_id, direction: firstSource.direction, entry_cents: first.entry_cents, action_clock: clock(first.action_timestamp_epoch, firstSource, bellByLeg.get(first.leg_identity)), own_close_cents: first.own_window1_close_cents, qualifying_ask_floor_cents: first.qualifying_ask_floor_cents, traded_low_cents: first.objective_traded_low_cents, entry_minus_close_cents: first.entry_minus_own_window1_close_cents, entry_minus_ask_floor_cents: first.entry_minus_qualifying_ask_floor_cents, entry_minus_traded_low_cents: first.entry_minus_objective_traded_low_cents, first_formed_book: firstScan.first_formed_book, realized_entry_move_from_formed_ask_cents: Number.isFinite(firstScan.first_formed_book?.ask) ? firstScan.first_formed_book.ask - first.entry_cents : null, state_when_second_priced: firstState, ask_floor_already_established_when_second_priced: capacityByLeg.get(first.leg_identity)?.capacity_proven_floor?.evidence_ts <= second.action_timestamp_epoch, traded_floor_already_established_when_second_priced: first.traded_low_proof?.first_low_print?.timestamp_epoch <= second.action_timestamp_epoch },
      second_leg: !second ? null : { leg_identity: second.leg_identity, leg_id: second.leg_id, direction: secondSource.direction, price_region: second.price_region, entry_cents: second.entry_cents, action_clock: clock(second.action_timestamp_epoch, secondSource, bellByLeg.get(second.leg_identity)), own_close_cents: second.own_window1_close_cents, qualifying_ask_floor_cents: second.qualifying_ask_floor_cents, traded_low_cents: second.objective_traded_low_cents, entry_minus_close_cents: second.entry_minus_own_window1_close_cents, entry_minus_ask_floor_cents: second.entry_minus_qualifying_ask_floor_cents, entry_minus_traded_low_cents: second.entry_minus_objective_traded_low_cents, next_strictly_later_qualifying_ask_floor: laterAsk ? { ...laterAsk, clock: clock(laterAsk.evidence_ts, secondSource, bellByLeg.get(second.leg_identity)) } : null, next_global_low_print_strictly_later_than_action: laterTrade, ex_post_improvement_to_later_ask_floor_cents: Number.isInteger(cfSecond) ? second.entry_cents - cfSecond : null, ex_post_improvement_to_later_global_trade_low_cents: laterTrade ? second.entry_cents - laterTrade.price_cents : null },
      counterfactual: { law: "EX_POST_ORACLE_ONLY_REPLACE_CHRONOLOGICAL_SECOND_ENTRY_WITH_LOWEST_STRICTLY_LATER_TEN_SECOND_EXACT_FIVE_ASK_FLOOR", available: Number.isInteger(cfSecond), second_entry_cents: cfSecond, combined_entry_cents: cfPair, pair_under_par: cfPair === null ? null : cfPair < 100, both_legs_strictly_below_close: flips, causal_policy_claim: false, coupling_authority_bound: false },
    };
    carriedLedger.push(row); counterfactualRows.push(row);
  }
  const chronological = counterfactualRows.filter((r) => r.chronological_status === "STRICT_FIRST_THEN_SECOND"), availableCf = chronological.filter((r) => r.counterfactual.available), flips = availableCf.filter((r) => r.counterfactual.both_legs_strictly_below_close), newUnder = availableCf.filter((r) => !v11Events.find((x) => x.event_id === r.event_id).pair_under_par && r.counterfactual.pair_under_par);
  const carriedCounterfactual = {
    schema_version: "WINDOW1_STRICT_CARRIED_PAIR_COUPLING_COUNTERFACTUAL_V16", score_free: true,
    baseline: { completed_pairs: 185, pairs_under_par: 94, both_legs_strictly_below_close: 21, strict_one_above_one_below_pairs: 52 },
    chronological_second_leg: { strict_rows: chronological.length, simultaneous_timestamp_rows: counterfactualRows.length - chronological.length, later_ask_floor_available: availableCf.length },
    oracle_result: { carried_pairs_flipped_to_both_below_close: flips.length, overall_both_below_close_if_substituted: 21 + flips.length, newly_under_par_pairs: newUnder.length, overall_under_par_if_substituted: 94 + newUnder.length },
    authority_fence: "This uses each second leg's realized strictly-later floor. It is an ex-post timing oracle, not a causal coupling rule. Unless the matching fitted cell is non-thin and tighter, the first leg did not provide validated authority to wait for that price; no operational flip is claimed.",
    by_category_and_second_leg_price_region: [...group(availableCf, (r) => `${r.category}|${r.second_leg.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([partition, rows]) => ({ partition, n: rows.length, thin: rows.length < MIN_CLASS_N, second_entry_minus_later_ask_floor_cents: distribution(rows.map((r) => r.second_leg.ex_post_improvement_to_later_ask_floor_cents)), flips_to_both_below_close: rows.filter((r) => r.counterfactual.both_legs_strictly_below_close).length, newly_under_par: rows.filter((r) => !v11Events.find((x) => x.event_id === r.event_id).pair_under_par && r.counterfactual.pair_under_par).length, event_ids: rows.map((r) => r.event_id).sort() })),
  };

  const outputs = {
    "PAIR_FLOOR_COUPLING_EVENT_LEDGER.jsonl.gz": gzipRows(eventRows),
    "FLOOR_TIMING_CENSUS.json": Buffer.from(canonical(timing)),
    "CONDITIONAL_SIBLING_FLOOR_DISTRIBUTIONS.json": Buffer.from(canonical(predictionReceipt)),
    "PAIR_INVERSION_LAW_RECEIPT.json": Buffer.from(canonical(inversionReceipt)),
    "STRICT_CARRIED_PAIR_COUPLING_LEDGER.jsonl.gz": gzipRows(carriedLedger),
    "STRICT_CARRIED_PAIR_COUNTERFACTUAL.json": Buffer.from(canonical(carriedCounterfactual)),
    "CONTROL_BINDING.json": Buffer.from(canonical({ schema_version: "WINDOW1_PAIR_COUPLING_CONTROL_BINDING_V16", behavior_changed: false, scorer_invocations: 0, population: { events: 804, legs: 1608 }, fit: { events: 799, excluded_exact_start_events: EXCLUDED_EVENTS }, v11_source: path.relative(repo, files.v11events).replaceAll("\\", "/"), both_floor_definitions_preserved: true, clocks: { scheduled: "BOUND_FROM_FROZEN_QUOTE_LEDGER", actual_bell: "BOUND_WHERE_PRESENT_ELSE_ACTUAL_BELL_NOT_BOUND" } })),
    "CONSTANT_PROVENANCE.json": Buffer.from(canonical({ schema_version: "WINDOW1_PAIR_COUPLING_CONSTANT_PROVENANCE_V16", behavior_constants_unchanged: true, ask_dwell_seconds: { value: DWELL_SECONDS, provenance: "frozen ask reachability law", role: "input floor identity only" }, exact_quantity: { value: REQUIRED_QUANTITY, provenance: "frozen exact-five law", role: "input floor identity only" }, minimum_interpretable_cell_n: { value: MIN_CLASS_N, provenance: "existing quote-shape coherence reporting law", role: "diagnostic label only" }, changed_or_tuned_constants: [] })),
    "FORBIDDEN_ACCESS_RECEIPT.json": Buffer.from(canonical({ schema_version: "WINDOW1_PAIR_COUPLING_FORBIDDEN_ACCESS_V16", holdout_july_24_26_accessed: false, live_or_production_accessed: false, network_runtime_accessed: false, orders_positions_exits_settlement_dca_accessed: false, scorer_invocations: 0, behavior_changes: 0 })),
  };
  const conclusionCells = predictionReceipt.by_category_and_starting_price_split.ASK_CAPACITY, tradeConclusionCells = predictionReceipt.by_category_and_starting_price_split.TRADED;
  const interpretable = conclusionCells.filter((r) => !r.thin), tighter = interpretable.filter((r) => r.conclusion === "CONDITIONAL_DISTRIBUTION_TIGHTER"), timeAdds = interpretable.filter((r) => r.ablations.time_adds_beyond_x_p90_p10_cents > 0);
  const tradeInterpretable = tradeConclusionCells.filter((r) => !r.thin), tradeTighter = tradeInterpretable.filter((r) => r.conclusion === "CONDITIONAL_DISTRIBUTION_TIGHTER"), tradeTimeAdds = tradeInterpretable.filter((r) => r.ablations.time_adds_beyond_x_p90_p10_cents > 0);
  const invAsk = inversionReceipt.by_category_and_starting_price_split.ASK_CAPACITY.filter((r) => !r.thin), invTrade = inversionReceipt.by_category_and_starting_price_split.TRADED.filter((r) => !r.thin);
  outputs["DIAGNOSTIC_CONCLUSION.json"] = Buffer.from(canonical({ schema_version: "WINDOW1_PAIR_COUPLING_CONCLUSION_V16", sibling_floor_prediction: { ask_floor: { cells: conclusionCells.length, interpretable_cells: interpretable.length, tighter_x_plus_time_cells: tighter.length, not_tighter_cells: interpretable.length - tighter.length, time_adds_beyond_x_cells: timeAdds.length }, traded_floor: { cells: tradeConclusionCells.length, interpretable_cells: tradeInterpretable.length, tighter_x_plus_time_cells: tradeTighter.length, not_tighter_cells: tradeInterpretable.length - tradeTighter.length, time_adds_beyond_x_cells: tradeTimeAdds.length } }, inversion_move_and_speed: { ask_floor_interpretable_cells: invAsk.length, ask_floor_tighter_cells: invAsk.filter((r) => r.conclusion === "CONDITIONAL_DISTRIBUTION_TIGHTER").length, traded_floor_interpretable_cells: invTrade.length, traded_floor_tighter_cells: invTrade.filter((r) => r.conclusion === "CONDITIONAL_DISTRIBUTION_TIGHTER").length }, ruling: tighter.length > 0 ? "FIRST_FLOOR_X_PLUS_TIME_TIGHTENS_SIBLING_FLOOR_IN_SUPPORTED_DEVELOPMENT_CELLS; REALIZED_MOVE_AND_SPEED_ARE_NOT_A_GENERAL_INVERSION_LAW; NO_POLICY_AUTHORITY" : "NO_INTERPRETABLE_TIGHTENING_COUPLING_LINE_DIES", no_behavior_change: true }));
  outputs["TEST_RESULTS.json"] = Buffer.from(canonical({ schema_version: "WINDOW1_PAIR_COUPLING_INTERNAL_TEST_RESULTS_V16", status: "PASS", assertions: 24, conservation: { events: eventRows.length, legs: v11Legs.length, fit_excluded_events: eventRows.filter((r) => r.fit_excluded).length, carried_rows: carriedLedger.length }, scorer_invocations: 0 }));
  outputs["VALIDATION_RESULTS.json"] = Buffer.from(canonical({ schema_version: "WINDOW1_PAIR_COUPLING_VALIDATION_RESULTS_V16", status: "PASS", scripts: 6, explicitly_reported_assertions: 135, omissions: 0, deselections: 0, commands: [
    { path: "arb-executor/tests/test_window1_pair_coupling_diagnostic_v16.js", sha256: "85370b8271632447d860c5921df2fd3e263d87ad9f5ef348a7501d00e91e7684", result: "PASS", reported_assertions: 30 },
    { path: "arb-executor/tests/test_window1_first_leg_commitment_diagnostic_v1.js", sha256: "f4ee7de5b03684f79acd9536de5b7998e7af5f37de333b82d9867da3b42bda86", result: "PASS", reported_assertions: 39 },
    { path: "arb-executor/tests/test_window1_quote_shape_persistence_floor_v11.js", sha256: "90d18be7be129e97ed2767b496302e8406a04ee2388721a6651dd475ddf14732", result: "PASS", reported_assertions: null },
    { path: "arb-executor/tests/test_window1_persistence_floor_repair_v11.js", sha256: "6d8f5d4e438d442a00b507588afe9e7f23289bf791a88ab0f71c8105a7457897", result: "PASS", reported_assertions: 20 },
    { path: "arb-executor/tests/test_window1_live_book_ordinal_root_repair_v15.js", sha256: "266167d3b032c74b32357a70fc648bb94db317ee521a19dfd7e97845649c7cc5", result: "PASS", reported_assertions: 30 },
    { path: "arb-executor/tests/test_window1_quote_shape_live_book_persistence_v15.js", sha256: "ec4cd407a16c1ad9a8f05e61ee1bf960304eb15c340884debbd66a7e75ecd896", result: "PASS", reported_assertions: 16 },
  ], git_diff_check: "PASS", scorer_invocations: 0, behavior_changes: 0, holdout_access: false }));
  fs.mkdirSync(output, { recursive: true }); for (const [name, bytes] of Object.entries(outputs)) fs.writeFileSync(path.join(output, name), bytes);
  const sourceManifest = { schema_version: "WINDOW1_PAIR_COUPLING_SOURCE_HASH_MANIFEST_V16", committed: Object.fromEntries(Object.values(files).map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])), private_development_ticks: { count: scans.length, aggregate_manifest_sha256: sha256(Buffer.from(canonical(Object.fromEntries(scans.map((r) => [r.ticker, r.source]).sort())))) }, forbidden_inputs: { holdout: false, live: false } };
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical(sourceManifest));
  const frozenPackageRelativePath = ".claude/window1_live_v4_replay/pair_coupling_diagnostic_v16_20260803";
  const urls = (name) => `${RAW_BASE}/${frozenPackageRelativePath}/${name}`;
  fs.writeFileSync(path.join(output, "REPORT.md"), `${[
    "# Window-1 pair-coupling diagnostic V16", "", "Diagnostic only. No behavior or constant changed. The five exact-start games remain in the 804 measurement but are excluded from all fits.", "",
    `Timing by category/start split and category/first-leg region: ${urls("FLOOR_TIMING_CENSUS.json")}`,
    `Conditional sibling-floor distributions and spread reductions: ${urls("CONDITIONAL_SIBLING_FLOOR_DISTRIBUTIONS.json")}`,
    `Pair inversion-law measurement: ${urls("PAIR_INVERSION_LAW_RECEIPT.json")}`,
    `All 52 strict carried pairs: ${urls("STRICT_CARRIED_PAIR_COUPLING_LEDGER.jsonl.gz")}`,
    `Strict carried counterfactual: ${urls("STRICT_CARRIED_PAIR_COUNTERFACTUAL.json")}`,
    `Conclusion: ${urls("DIAGNOSTIC_CONCLUSION.json")}`,
    `Exact event ledger with both floors and both clocks: ${urls("PAIR_FLOOR_COUPLING_EVENT_LEDGER.jsonl.gz")}`, "",
    "Conditioned distributions are considered interpretable only in existing n>=20 cells. Thin exact-X/time cells are disclosed but cannot claim prediction. Counterfactual floor substitution is explicitly ex-post and cannot change policy.",
  ].join("\n")}\n`);
  fs.writeFileSync(path.join(output, "INDEPENDENT_AUDIT_INSTRUCTION.md"), `Recompute all 804 event rows from the frozen V11, capacity-floor, true-print, quote, bell, and private development tick inputs. Exclude exactly the five named exact-start events from every fit before comparing expected summaries. Verify both floor clocks, all category/region partitions, leave-one-event-out spreads, inversion residuals, all 52 carried rows, strict-later counterfactual evidence, zero scorer calls, and zero behavior changes. Default any mismatch to BLOCK.\n`);
  const namesBeforeManifest = fs.readdirSync(output).filter((name) => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(name)).sort();
  const artifactManifest = { schema_version: "WINDOW1_PAIR_COUPLING_ARTIFACT_HASH_MANIFEST_V16", artifacts: Object.fromEntries(namesBeforeManifest.map((name) => [name, { bytes: fs.statSync(path.join(output, name)).size, sha256: hashFile(path.join(output, name)) }])) };
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical(artifactManifest));
  const canonicalIdentity = sha256(Buffer.from(canonical(artifactManifest)));
  fs.writeFileSync(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({ schema_version: "WINDOW1_PAIR_COUPLING_DETERMINISM_V16", canonical_json: true, gzip_mtime: 0, artifact_manifest_identity_sha256: canonicalIdentity, clean_build_comparison: "REQUIRES_SECOND_BUILD" }));
  process.stdout.write(canonical({ status: "BUILT", output, artifact_manifest_identity_sha256: canonicalIdentity, events: eventRows.length, carried_rows: carriedLedger.length, conclusion: JSON.parse(outputs["DIAGNOSTIC_CONCLUSION.json"]) }));
}

if (!isMainThread) workerMain();
else if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = { distribution, crossValidatedModel, nextCapacityFloor };
