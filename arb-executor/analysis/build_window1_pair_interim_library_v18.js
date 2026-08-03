#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const { scanOne, EXCLUDED_EVENTS, GRID, MIN_CLASS_N } = require("./build_window1_quote_shape_coherent_library_v12.js");
const { PAIR_ROLE_KEYS } = require("./window1_pair_interim_elimination_v18.js");

const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const ticksRoot = path.join(privateRoot, "fit-local/ticks");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const singleLibraryPath = path.resolve(value("--single-library", path.join(repo, ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json")));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/pair_interim_shape_v18_fit_20260803/INTERIM_PAIR_LIBRARY_V18.json")));
const workers = Math.max(1, Number(value("--workers", "4")));

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function countBy(rows, key) { const out = {}; for (const row of rows) { const k = String(key(row)); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => Number(a[0]) - Number(b[0]) || a[0].localeCompare(b[0]))); }
function group(rows, key) { const out = new Map(); for (const row of rows) { const k = key(row); if (!out.has(k)) out.set(k, []); out.get(k).push(row); } return out; }
function workerMain() { parentPort.postMessage(workerData.sources.map((source) => scanOne(source, workerData.ticksRoot, false))); }

function jointFeatures(high, low) {
  if (!high || !low) return null;
  const out = {};
  for (const [role, row] of [["high", high], ["low", low]]) for (const key of PAIR_ROLE_KEYS) out[`${role}_${key}`] = key === "current_ask" ? row.current_ask : row[key];
  out.ask_sum = high.current_ask + low.current_ask;
  out.ask_net_sum = high.ask_net + low.ask_net;
  out.spread_sum = high.mean_spread + low.mean_spread;
  return out;
}

const VECTOR_BINS = [5, 10, 20, 35, 50, 65, 80, 100];
const VECTOR_ROLE_KEYS = ["ask_net", "ask_dip", "ask_peak", "ask_drawdown_from_peak", "mean_spread", "spread_range", "quote_rate", "ask_change_rate", "ask_dwell_fraction", "mean_log_top_ask_size", "mean_log_top5_ask_depth", "current_ask"];
function trajectoryVector(row) {
  const out = [];
  for (const bin of VECTOR_BINS) {
    const high = row.high.grid[bin], low = row.low.grid[bin];
    for (const side of [high, low]) for (const key of VECTOR_ROLE_KEYS) out.push(side ? side[key] : null);
    out.push(high && low ? high.current_ask + low.current_ask : null, high && low ? high.ask_net + low.ask_net : null, Number(!high), Number(!low));
  }
  return out;
}
function distance2(a, b) { let sum = 0; for (let i = 0; i < a.length; i += 1) sum += (a[i] - b[i]) ** 2; return sum; }
function meanVector(points, ids) { return points[0].map((_, d) => ids.reduce((sum, i) => sum + points[i][d], 0) / ids.length); }
function kmeans(points, eventIds, k) {
  const seeds = [eventIds.map((id, i) => [id, i]).sort((a, b) => a[0].localeCompare(b[0]))[0][1]];
  while (seeds.length < k) {
    let chosen = null;
    for (let i = 0; i < points.length; i += 1) if (!seeds.includes(i)) {
      const nearest = Math.min(...seeds.map((seed) => distance2(points[i], points[seed]))), candidate = { i, nearest, id: eventIds[i] };
      if (!chosen || candidate.nearest > chosen.nearest || (candidate.nearest === chosen.nearest && candidate.id < chosen.id)) chosen = candidate;
    }
    seeds.push(chosen.i);
  }
  let centers = seeds.map((i) => [...points[i]]), assignment = [];
  for (let iteration = 0; iteration < 100; iteration += 1) {
    const next = points.map((point) => centers.map((center, index) => ({ index, d: distance2(point, center) })).sort((a, b) => a.d - b.d || a.index - b.index)[0].index);
    const memberIds = centers.map((_, cluster) => next.map((value, i) => value === cluster ? i : null).filter((i) => i !== null));
    if (memberIds.some((ids) => !ids.length)) return null;
    const newCenters = memberIds.map((ids) => meanVector(points, ids));
    const stable = assignment.length && next.every((value, i) => value === assignment[i]); assignment = next; centers = newCenters; if (stable) break;
  }
  const clusters = centers.map((_, cluster) => assignment.map((value, i) => value === cluster ? i : null).filter((i) => i !== null));
  const sse = points.reduce((sum, point, i) => sum + distance2(point, centers[assignment[i]]), 0), observations = points.length * points[0].length;
  return { clusters, sse, bic: observations * Math.log(Math.max(Number.EPSILON, sse / observations)) + k * (points[0].length + 1) * Math.log(observations) };
}
function fitInterimClusters(rows) {
  const usableRows = rows;
  const raw = usableRows.map(trajectoryVector), dims = raw[0].length, means = Array.from({ length: dims }, (_, d) => { const values = raw.map((point) => point[d]).filter(Number.isFinite); return values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0; }), sds = Array.from({ length: dims }, (_, d) => { const values = raw.map((point) => point[d]).filter(Number.isFinite); return Math.max(1e-9, Math.sqrt(values.reduce((sum, value) => sum + (value - means[d]) ** 2, 0) / Math.max(1, values.length))); });
  const points = raw.map((point) => point.map((value, d) => (Number.isFinite(value) ? value - means[d] : 0) / sds[d])), eventIds = usableRows.map((row) => row.event_id);
  const candidates = [];
  for (let k = 1; k <= Math.max(1, Math.floor(points.length / MIN_CLASS_N)); k += 1) { const fit = kmeans(points, eventIds, k); if (fit && fit.clusters.every((ids) => ids.length >= MIN_CLASS_N)) candidates.push({ k, ...fit }); }
  candidates.sort((a, b) => a.bic - b.bic || a.k - b.k); const selected = candidates[0];
  return { rows: usableRows, clusters: selected.clusters, selection: { criterion: "MINIMUM_KMEANS_BIC_AMONG_TRAJECTORY_ONLY_FITS_WITH_EVERY_CLUSTER_N_GE_20", selected_k: selected.k, selected_bic: selected.bic, candidates: candidates.map((fit) => ({ k: fit.k, bic: fit.bic, cluster_sizes: fit.clusters.map((ids) => ids.length) })), vector_bins: VECTOR_BINS, vector_role_keys: VECTOR_ROLE_KEYS, missing_book_law: "MISSING VALUES IMPUTED TO CATEGORY FEATURE MEAN AFTER STANDARDIZATION PLUS EXPLICIT PER-ROLE MISSING INDICATORS; RUNTIME CANNOT MATCH UNTIL BOTH BOOKS EXIST", vector_dimensions: dims, outcome_or_ordinal_used_in_membership: false } };
}

function buildHypothesis(category, members, ordinals, index, usable) {
  const featureNames = [
    ...["high", "low"].flatMap((role) => PAIR_ROLE_KEYS.map((key) => `${role}_${key}`)),
    "ask_sum", "ask_net_sum", "spread_sum",
  ];
  const envelopes = Array.from({ length: GRID + 1 }, (_, bin) => {
    const features = members.map((row) => jointFeatures(row.high.grid[bin], row.low.grid[bin])).filter(Boolean), envelope = {};
    for (const key of featureNames) envelope[key] = features.length ? [Math.min(...features.map((r) => r[key])), Math.max(...features.map((r) => r[key]))] : null;
    return envelope;
  });
  const shapePairs = [...group(members, (row) => `${row.high_shape_id}|${row.low_shape_id}`)].map(([key, xs]) => { const [highShape, lowShape] = key.split("|"); return { high_shape_id: highShape, low_shape_id: lowShape, n: xs.length }; }).sort((a, b) => b.n - a.n || a.high_shape_id.localeCompare(b.high_shape_id) || a.low_shape_id.localeCompare(b.low_shape_id));
  const highCounts = countBy(members, (r) => r.high_ordinal), lowCounts = countBy(members, (r) => r.low_ordinal);
  const highSupport = Object.keys(highCounts).map(Number), lowSupport = Object.keys(lowCounts).map(Number);
  return {
    pair_hypothesis_id: `${category}_PAIR_INTERIM_${usable ? String(index + 1).padStart(2, "0") : "UNUSABLE_REMAINDER"}`,
    category,
    runtime_lookup_key: "CATEGORY_ONLY; NO_PRICE_REGION; NO_CELL; NO_BUCKET",
    n: members.length,
    usable_for_signing: usable,
    unusable_reason: usable ? null : "N_LT_20_OR_PAIR_ORDINAL_SUPPORT_NOT_EXACT_OR_ADJACENT",
    coherence: {
      minimum_event_members: MIN_CLASS_N,
      high_leg_ordinal_counts: highCounts,
      low_leg_ordinal_counts: lowCounts,
      high_leg_support_width: highSupport.length ? Math.max(...highSupport) - Math.min(...highSupport) : null,
      low_leg_support_width: lowSupport.length ? Math.max(...lowSupport) - Math.min(...lowSupport) : null,
      requirement: "N>=20 EVENTS; EACH LEG ONE EXACT DESCENT COUNT OR TWO ADJACENT COUNTS",
      status: usable ? "PASS" : "UNUSABLE",
    },
    ordinal_support: ordinals,
    joint_interim_envelopes: envelopes,
    member_single_shape_pairs: shapePairs,
    member_event_ids: members.map((r) => r.event_id).sort(),
    member_leg_identities: members.flatMap((r) => [`${r.event_id}|${r.high.leg_id}`, `${r.event_id}|${r.low.leg_id}`]).sort(),
  };
}

async function main() {
  const singleLibrary = JSON.parse(fs.readFileSync(singleLibraryPath, "utf8")), excluded = new Set(EXCLUDED_EVENTS);
  const raw = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/), headers = raw.shift().split(",");
  const sources = raw.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v]))).filter((r) => !excluded.has(r.event_id) && String(r.evaluator_window_positive).toLowerCase() === "true").map((r) => ({ event_id: r.event_id, category: r.category, leg: r.leg, ticker: r.ticker, left_ts: Number(r.left_ts), right_ts: Number(r.right_ts) }));
  const buckets = Array.from({ length: workers }, () => []); sources.forEach((source, i) => buckets[i % workers].push(source));
  const scanned = (await Promise.all(buckets.map((bucket) => new Promise((resolve, reject) => { const worker = new Worker(__filename, { workerData: { sources: bucket, ticksRoot } }); worker.on("message", resolve); worker.on("error", reject); })))).flat().sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id));
  const available = scanned.filter((row) => row.status === "AVAILABLE"), pairs = [];
  for (const [eventId, legs] of group(available, (row) => row.event_id)) {
    if (legs.length !== 2) continue;
    const sorted = [...legs].sort((a, b) => b.first_ask - a.first_ask || a.leg_id.localeCompare(b.leg_id)), [high, low] = sorted;
    const highShape = singleLibrary.assignment[`${eventId}|${high.leg_id}`], lowShape = singleLibrary.assignment[`${eventId}|${low.leg_id}`];
    const highOrdinal = high.qualified_descent_to_final_reachable_low?.descent_ordinal, lowOrdinal = low.qualified_descent_to_final_reachable_low?.descent_ordinal;
    if (!highShape || !lowShape || !Number.isInteger(highOrdinal) || !Number.isInteger(lowOrdinal)) continue;
    pairs.push({ event_id: eventId, category: high.category, high, low, high_shape_id: highShape, low_shape_id: lowShape, high_ordinal: highOrdinal, low_ordinal: lowOrdinal });
  }
  const groups = {};
  for (const [category, rows] of [...group(pairs, (row) => row.category)].sort(([a], [b]) => a.localeCompare(b))) {
    const fit = fitInterimClusters(rows), hypotheses = fit.clusters.map((ids, index) => {
      const members = ids.map((i) => fit.rows[i]), high = [...new Set(members.map((row) => row.high_ordinal))].sort((a, b) => a - b), low = [...new Set(members.map((row) => row.low_ordinal))].sort((a, b) => a - b), usable = members.length >= MIN_CLASS_N && high.length > 0 && low.length > 0 && high.at(-1) - high[0] <= 1 && low.at(-1) - low[0] <= 1;
      return buildHypothesis(category, members, { high, low }, index, usable);
    });
    groups[category] = { category, lookup_dimensions: ["category"], price_region_or_cell_used: false, trajectory_only_fit: fit.selection, hypotheses };
  }
  const hypotheses = Object.values(groups).flatMap((group) => group.hypotheses), signable = hypotheses.filter((row) => row.usable_for_signing), signableLegs = new Set(signable.flatMap((row) => row.member_leg_identities));
  const result = {
    schema_version: "WINDOW1_SYNCHRONIZED_PAIR_INTERIM_LIBRARY_V18",
    score_free: true,
    fit_excludes_exact_start_games: true,
    excluded_exact_start_events: EXCLUDED_EVENTS,
    single_leg_library: { path: path.relative(repo, singleLibraryPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(singleLibraryPath)), hypotheses: singleLibrary.census.shapes, available_training_legs: singleLibrary.census.available_training_legs },
    architecture: { leg_library: "V13 CAUSAL INTERIM SINGLE-BOOK HYPOTHESES RETAINED", pair_library: "SYNCHRONIZED BOTH-BOOK INTERIM HYPOTHESES", mutual_narrowing: "LEG SURVIVORS REMOVE INCONSISTENT PAIR HYPOTHESES; PAIR SURVIVORS REMOVE INCONSISTENT LEG HYPOTHESES; FIXED POINT", signing: "ALL RESOLVED SURVIVORS MUST AGREE; UNUSABLE HYPOTHESES ABSTAIN; NO SIGNABLE PAIR SURVIVOR IS INSUFFICIENT_EVIDENCE", level_order: "SOURCE -> LEG_MACRO_AND_PAIR_MACRO_MUTUAL_FIXED_POINT -> MICRO_ORDINAL -> FITTED_MICRO_MICRO" },
    fit_contract: { observations: "BOTH BOOKS AT THE SAME GUARDED WINDOW PROGRESS CUTOFF", features: "BOTH ASKS, ASK PATHS, SPREADS, DWELLS, CADENCE, DISPLAYED ASK SIZE, TOP-FIVE ASK DEPTH", category_only: true, price_region_cells: false, endpoint_labels: false, minimum_event_members: MIN_CLASS_N, membership_fit: "DETERMINISTIC KMEANS ON STANDARDIZED SYNCHRONIZED INTERIM TRAJECTORIES; K CHOSEN BY MINIMUM BIC WITH EVERY CLUSTER N>=20", ordinal_role: "POST-FIT COHERENCE CERTIFICATION ONLY; NEVER MEMBERSHIP", ordinal_coherence: "EACH LEG EXACT OR TWO ADJACENT COUNTS" },
    groups: singleLibrary.groups,
    assignment: singleLibrary.assignment,
    pair_shape_tuples: singleLibrary.pair_shape_tuples,
    micro_micro_models: singleLibrary.micro_micro_models,
    pair_hypothesis_groups: groups,
    census: { pair_events_with_two_formed_books_and_both_ordinals: pairs.length, pair_hypotheses: hypotheses.length, signable_pair_hypotheses: signable.length, unusable_pair_hypotheses: hypotheses.length - signable.length, signable_pair_event_members: signable.reduce((sum, row) => sum + row.n, 0), pair_signable_leg_identities: signableLegs.size, denominator_available_single_leg_hypothesis_members: singleLibrary.census.available_training_legs, pair_signable_share_of_1343: signableLegs.size / singleLibrary.census.available_training_legs },
    source: { quote_ledger: { path: path.relative(repo, quotePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(quotePath)) }, private_tick_files: Object.fromEntries(scanned.map((row) => [row.ticker, row.source])) },
  };
  fs.mkdirSync(path.dirname(output), { recursive: true }); const bytes = Buffer.from(canonical(result)); fs.writeFileSync(output, bytes);
  process.stdout.write(canonical({ status: "BUILT", output, sha256: sha256(bytes), census: result.census }));
}

if (!isMainThread) workerMain();
else if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = { jointFeatures, trajectoryVector, kmeans, fitInterimClusters, buildHypothesis };
