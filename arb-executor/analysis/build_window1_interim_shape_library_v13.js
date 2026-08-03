#!/usr/bin/env node
"use strict";

// V13 fits causal interim-path hypotheses. Endpoint topology is retained only
// as an audit crosswalk; it is neither a feature nor a runtime lookup key.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const { scanOne, EXCLUDED_EVENTS, GRID, MIN_CLASS_N } = require("./build_window1_quote_shape_coherent_library_v12.js");
const { MACRO_KEYS, MICRO_MICRO_KEYS, macroState, traverseMicroModel } = require("./window1_interim_elimination_v13.js");

const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const ticksRoot = path.join(privateRoot, "fit-local/ticks");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json")));
const sampleOutput = path.resolve(value("--micro-samples", path.join(path.dirname(output), "MICRO_MICRO_FIT_SAMPLES_V13.jsonl.gz")));
const workers = Math.max(1, Number(value("--workers", "4")));
const FIT_LAST_DAY = 17;

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function dayOf(eventId) { const m = String(eventId).match(/-26JUL(\d+)/); return m ? Number(m[1]) : null; }
function countBy(xs) { const m = new Map(); for (const x of xs) m.set(String(x), (m.get(String(x)) || 0) + 1); return Object.fromEntries([...m].sort(([a], [b]) => a.localeCompare(b))); }
function median(xs) { const s = xs.filter(Number.isFinite).sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : null; }
function quantile(xs, p) { const s = xs.filter(Number.isFinite).sort((a, b) => a - b); return s.length ? s[Math.floor((s.length - 1) * p)] : null; }
function group(rows, fn) { const m = new Map(); for (const row of rows) { const k = fn(row); if (!m.has(k)) m.set(k, []); m.get(k).push(row); } return m; }
function gini(rows) { if (!rows.length) return 0; const p = rows.reduce((s, r) => s + r.label, 0) / rows.length; return 2 * p * (1 - p); }
function uniqueLegs(rows) { return new Set(rows.map((r) => `${r.event_id}|${r.leg_id}`)).size; }

function workerMain() { parentPort.postMessage(workerData.sources.map((source) => scanOne(source, workerData.ticksRoot, true))); }

function coherentSegments(rows) {
  const counts = new Map();
  for (const row of rows) { const n = row.qualified_descent_to_final_reachable_low?.descent_ordinal; if (Number.isInteger(n)) counts.set(n, (counts.get(n) || 0) + 1); }
  const values = [...counts].sort(([a], [b]) => a - b), memo = new Map();
  function better(a, b) { if (!b) return true; const ax = [a.usable_members, -a.usable_classes, -a.segments.length], bx = [b.usable_members, -b.usable_classes, -b.segments.length]; for (let i = 0; i < ax.length; i += 1) if (ax[i] !== bx[i]) return ax[i] > bx[i]; return JSON.stringify(a.segments) < JSON.stringify(b.segments); }
  function solve(i) {
    if (i >= values.length) return { usable_members: 0, usable_classes: 0, segments: [] };
    if (memo.has(i)) return memo.get(i);
    const options = [];
    for (const width of [1, 2]) {
      if (i + width > values.length) continue;
      const chosen = values.slice(i, i + width); if (width === 2 && chosen[1][0] !== chosen[0][0] + 1) continue;
      const n = chosen.reduce((s, x) => s + x[1], 0), tail = solve(i + width), usable = n >= MIN_CLASS_N;
      options.push({ usable_members: tail.usable_members + (usable ? n : 0), usable_classes: tail.usable_classes + Number(usable), segments: [{ ordinals: chosen.map((x) => x[0]), n, usable }, ...tail.segments] });
    }
    const best = options.reduce((a, b) => better(b, a) ? b : a, null); memo.set(i, best); return best;
  }
  return solve(0).segments;
}

function envelope(rows, bin) {
  const states = rows.map((r) => r.grid[bin]).filter(Boolean), out = { macro_states: [...new Set(states.map(macroState))].sort() };
  for (const key of MACRO_KEYS) out[key] = states.length ? [Math.min(...states.map((x) => x[key])), Math.max(...states.map((x) => x[key]))] : null;
  return out;
}

function buildShape(groupKey, rows, segment, index) {
  const ordinals = rows.map((r) => r.qualified_descent_to_final_reachable_low?.descent_ordinal).filter(Number.isInteger), usable = Boolean(segment.usable);
  return {
    shape_id: `${groupKey.replace("|", "_")}_INTERIM_PATH_${String(index + 1).padStart(2, "0")}_ORD_${segment.ordinals.join("_")}`,
    runtime_identity_law: "CAUSAL_INTERIM_ENVELOPES_ONLY; ENDPOINT_TOPOLOGY_FOR_AUDIT_CROSSWALK_ONLY",
    n: rows.length,
    usable_for_signing: usable,
    unusable_reason: usable ? null : "N_LT_20_FOR_EXACT_OR_ADJACENT_ORDINAL_SUPPORT",
    descent_to_final_reachable_low: { min: ordinals.length ? Math.min(...ordinals) : null, max: ordinals.length ? Math.max(...ordinals) : null, counts: countBy(ordinals), support_n: ordinals.length },
    coherence: { status: usable ? "PASS" : "UNUSABLE", minimum_members: MIN_CLASS_N, ordinal_support_width: ordinals.length ? Math.max(...ordinals) - Math.min(...ordinals) : null, required_support_width: "ONE_EXACT_COUNT_OR_TWO_ADJACENT_COUNTS" },
    interim_envelopes: Array.from({ length: GRID + 1 }, (_, bin) => envelope(rows, bin)),
    endpoint_classes_dissolved: countBy(rows.map((r) => r.old_topology)),
    member_identities: rows.map((r) => `${r.event_id}|${r.leg_id}`).sort(),
  };
}

function leaf(rows, leafId) {
  const positives = rows.reduce((s, r) => s + r.label, 0), negatives = rows.length - positives;
  return { type: "LEAF", leaf_id: leafId, samples: rows.length, unique_legs: uniqueLegs(rows), positives, negatives, fit_rate: rows.length ? positives / rows.length : null, verdict: positives > negatives ? "READY" : negatives > positives ? "NOT_READY" : "INSUFFICIENT_EVIDENCE" };
}

function fitTree(rows) {
  let nextLeaf = 1;
  function recurse(part) {
    if (!part.length || gini(part) === 0) return leaf(part, `L${nextLeaf++}`);
    let best = null;
    const parent = gini(part);
    for (const feature of MICRO_MICRO_KEYS) {
      const ordered = part.filter((r) => Number.isFinite(r.features[feature])).sort((a, b) => a.features[feature] - b.features[feature] || a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id));
      if (ordered.length !== part.length) continue;
      let leftPositive = 0, rightPositive = ordered.reduce((s, r) => s + r.label, 0);
      const leftLegs = new Map(), rightLegs = new Map();
      for (const row of ordered) { const id = `${row.event_id}|${row.leg_id}`; rightLegs.set(id, (rightLegs.get(id) || 0) + 1); }
      for (let i = 1; i < ordered.length; i += 1) {
        const moved = ordered[i - 1], movedId = `${moved.event_id}|${moved.leg_id}`;
        leftPositive += moved.label; rightPositive -= moved.label; leftLegs.set(movedId, (leftLegs.get(movedId) || 0) + 1);
        rightLegs.set(movedId, rightLegs.get(movedId) - 1); if (rightLegs.get(movedId) === 0) rightLegs.delete(movedId);
        if (ordered[i - 1].features[feature] === ordered[i].features[feature]) continue;
        if (leftLegs.size < MIN_CLASS_N || rightLegs.size < MIN_CLASS_N) continue;
        const leftRate = leftPositive / i, rightN = ordered.length - i, rightRate = rightPositive / rightN;
        const splitGini = (i * 2 * leftRate * (1 - leftRate) + rightN * 2 * rightRate * (1 - rightRate)) / ordered.length;
        const gain = parent - splitGini, threshold = (ordered[i - 1].features[feature] + ordered[i].features[feature]) / 2;
        const candidate = { feature, threshold, gain, splitIndex: i, ordered };
        if (!best || gain > best.gain || (gain === best.gain && (feature < best.feature || (feature === best.feature && threshold < best.threshold)))) best = candidate;
      }
    }
    if (!best || best.gain <= 0) return leaf(part, `L${nextLeaf++}`);
    const left = best.ordered.slice(0, best.splitIndex), right = best.ordered.slice(best.splitIndex);
    return { type: "SPLIT", feature: best.feature, threshold: best.threshold, gini_gain: best.gain, samples: part.length, unique_legs: uniqueLegs(part), left: recurse(left), right: recurse(right) };
  }
  return recurse(rows);
}

function calibration(model, samples) {
  const rows = samples.map((s) => ({ ...s, prediction: traverseMicroModel(model, s.features) })), scored = rows.filter((r) => r.prediction.verdict !== "INSUFFICIENT_EVIDENCE");
  return { samples: rows.length, unique_legs: uniqueLegs(rows), predicted_ready: rows.filter((r) => r.prediction.verdict === "READY").length, predicted_not_ready: rows.filter((r) => r.prediction.verdict === "NOT_READY").length, insufficient: rows.length - scored.length, accuracy: scored.length ? scored.filter((r) => Number(r.prediction.verdict === "READY") === r.label).length / scored.length : null, brier: scored.length ? scored.reduce((sum, r) => sum + (r.prediction.fit_rate - r.label) ** 2, 0) / scored.length : null, by_leaf: Object.fromEntries([...group(rows, (r) => r.prediction.leaf_id || "UNAVAILABLE")].sort(([a], [b]) => a.localeCompare(b)).map(([k, x]) => [k, { n: x.length, observed_next_receipt_executable_rate: x.reduce((s, r) => s + r.label, 0) / x.length }])) };
}

async function main() {
  const raw = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/), headers = raw.shift().split(","), excluded = new Set(EXCLUDED_EVENTS);
  const sources = raw.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v]))).filter((r) => !excluded.has(r.event_id) && String(r.evaluator_window_positive).toLowerCase() === "true").map((r) => ({ event_id: r.event_id, category: r.category, leg: r.leg, ticker: r.ticker, left_ts: Number(r.left_ts), right_ts: Number(r.right_ts) }));
  const buckets = Array.from({ length: workers }, () => []); sources.forEach((s, i) => buckets[i % workers].push(s));
  const results = isMainThread ? (await Promise.all(buckets.map((bucket) => new Promise((resolve, reject) => { const w = new Worker(__filename, { workerData: { sources: bucket, ticksRoot } }); w.on("message", resolve); w.on("error", reject); })))).flat() : [];
  const available = results.filter((r) => r.status === "AVAILABLE"), groups = {}, assignment = {};
  for (const [key, rows] of [...group(available, (r) => `${r.category}|${r.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const shapes = [];
    const segments = coherentSegments(rows), assigned = new Set();
    for (const [index, segment] of segments.filter((item) => item.usable).entries()) {
      const members = rows.filter((r) => segment.ordinals.includes(r.qualified_descent_to_final_reachable_low?.descent_ordinal));
      const shape = buildShape(key, members, segment, index); shapes.push(shape); for (const id of shape.member_identities) { assignment[id] = shape.shape_id; assigned.add(id); }
    }
    const remainder = rows.filter((r) => !assigned.has(`${r.event_id}|${r.leg_id}`));
    if (remainder.length) { const ordinals = [...new Set(remainder.map((r) => r.qualified_descent_to_final_reachable_low?.descent_ordinal).filter(Number.isInteger))].sort((a, b) => a - b), shape = buildShape(key, remainder, { ordinals, n: remainder.length, usable: false }, shapes.length); shape.shape_id = `${key.replace("|", "_")}_INTERIM_PATH_UNUSABLE_REMAINDER`; shape.unusable_reason = "NO_N_GE_20_EXACT_OR_ADJACENT_ORDINAL_COHORT_OR_ORDINAL_CENSORED"; shapes.push(shape); for (const id of shape.member_identities) assignment[id] = shape.shape_id; }
    groups[key] = { category: key.split("|")[0], price_region: key.split("|")[1], shapes };
  }
  const pairShapeTuples = {};
  for (const [eventId, rows] of group(available, (r) => r.event_id)) if (rows.length === 2) {
    const sorted = [...rows].sort((a, b) => b.first_ask - a.first_ask || a.leg_id.localeCompare(b.leg_id)), high = sorted[0], low = sorted[1], h = assignment[`${eventId}|${high.leg_id}`], l = assignment[`${eventId}|${low.leg_id}`];
    if (h && l) { const k = `${high.category}|${high.price_region}|${low.price_region}`; if (!pairShapeTuples[k]) pairShapeTuples[k] = {}; pairShapeTuples[k][`${h}|${l}`] = (pairShapeTuples[k][`${h}|${l}`] || 0) + 1; }
  }
  const samples = available.flatMap((r) => r.micro_micro_samples || []).filter((r) => r.label !== null).sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id) || a.timestamp_epoch - b.timestamp_epoch || a.receipt.localeCompare(b.receipt));
  const microModels = {};
  for (const [key, rows] of [...group(samples, (r) => `${r.category}|${r.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b))) {
    const fit = rows.filter((r) => dayOf(r.event_id) <= FIT_LAST_DAY), post = rows.filter((r) => dayOf(r.event_id) > FIT_LAST_DAY), model = { group_key: key, fit_dates: "2026-07-12..2026-07-17", calibration_dates: "2026-07-18..2026-07-20", label: "next strictly-later chronological BBO has ask<=current ask and displayed top-five ask capacity at/below current ask >=5", minimum_unique_legs_per_split_child: MIN_CLASS_N, features: MICRO_MICRO_KEYS, tree: fitTree(fit) };
    model.fit_calibration = calibration(model, fit); model.post_fit_calibration = calibration(model, post); microModels[key] = model;
  }
  const shapes = Object.values(groups).flatMap((g) => g.shapes), signable = shapes.filter((s) => s.usable_for_signing), endpointDissolution = {};
  for (const row of available) { const old = `${row.category}|${row.price_region}|${row.old_topology}`, now = assignment[`${row.event_id}|${row.leg_id}`]; if (!endpointDissolution[old]) endpointDissolution[old] = {}; endpointDissolution[old][now] = (endpointDissolution[old][now] || 0) + 1; }
  const library = { schema_version: "WINDOW1_INTERIM_ELIMINATION_LIBRARY_V13", score_free: true, fit_excludes_exact_start_games: true, excluded_exact_start_events: EXCLUDED_EVENTS, fit_universe: { requested_positive_window_legs: sources.length, available_formed_book_legs: available.length, events: new Set(available.map((r) => r.event_id)).size }, architecture: { window_open: "ALL_SHAPES_LIVE", macro: "ELIMINATE_ONLY_ON_CAUSAL_INTERIM_ASK_PATH_ENVELOPES", micro: "UNANIMOUS_COHERENT_QUALIFIED_DESCENT_ORDINAL", micro_micro: "FITTED_NEXT_STRICTLY_LATER_RECEIPT_EXECUTABILITY_TREE", ordering: "MACRO_THEN_PAIR_MICRO_THEN_MICRO_POSITION_THEN_MICRO_MICRO; UNRESOLVED_LEVEL_BLOCKS_ALL_LEVELS_BELOW" }, endpoint_labels_runtime_role: "NONE", outcome_role: "QUALIFIED_DESCENT_ORDINAL_USED_ONLY_FOR_POST_FIT_COHERENCE_CERTIFICATION", groups, assignment, pair_shape_tuples: pairShapeTuples, micro_micro_models: microModels, endpoint_class_dissolution: endpointDissolution, census: { shapes: shapes.length, signable_shapes: signable.length, unusable_shapes: shapes.length - signable.length, signable_members: signable.reduce((s, x) => s + x.n, 0), unusable_members: shapes.filter((x) => !x.usable_for_signing).reduce((s, x) => s + x.n, 0), available_training_legs: available.length, micro_micro_samples: samples.length, fit_samples: samples.filter((x) => dayOf(x.event_id) <= FIT_LAST_DAY).length, post_fit_samples: samples.filter((x) => dayOf(x.event_id) > FIT_LAST_DAY).length }, source_contract: { quote_ledger: path.relative(repo, quotePath).replaceAll("\\", "/"), raw_tick_root: "PRIVATE_HASH_BOUND_FIT_LOCAL_TICKS", ask_side_only: true, grid_bins: GRID, minimum_members: MIN_CLASS_N, endpoint_labels_excluded_from_features_and_runtime: true } };
  fs.mkdirSync(path.dirname(output), { recursive: true }); const bytes = Buffer.from(canonical(library)); fs.writeFileSync(output, bytes); fs.writeFileSync(sampleOutput, zlib.gzipSync(Buffer.from(samples.map(JSON.stringify).join("\n") + "\n"), { level: 9, mtime: 0 }));
  process.stdout.write(canonical({ status: "BUILT", output, sha256: sha256(bytes), sample_output: sampleOutput, sample_sha256: sha256(fs.readFileSync(sampleOutput)), census: library.census }));
}

if (require.main === module) {
  if (!isMainThread) { try { workerMain(); } catch (error) { throw error; } }
  else main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
}

module.exports = { coherentSegments, buildShape, fitTree, calibration };
