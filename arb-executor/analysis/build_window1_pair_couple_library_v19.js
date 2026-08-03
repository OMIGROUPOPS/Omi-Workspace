#!/usr/bin/env node
"use strict";

const crypto = require("crypto"), fs = require("fs"), path = require("path");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
const { scanOne, EXCLUDED_EVENTS } = require("./build_window1_quote_shape_coherent_library_v12.js");
const { familyOf, exactKey } = require("./window1_pair_couple_elimination_v19.js");

const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const ticksRoot = path.join(privateRoot, "fit-local/ticks");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const singleLibraryPath = path.resolve(value("--single-library", path.join(repo, ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json")));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/pair_couple_v19_fit_20260803/PAIR_COUPLE_LIBRARY_V19.json")));
const workers = Math.max(1, Number(value("--workers", "8")));
const MIN_N = 30;

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function group(rows, key) { const out = new Map(); for (const row of rows) { const k = key(row); if (!out.has(k)) out.set(k, []); out.get(k).push(row); } return out; }
function countBy(rows, key) { const out = {}; for (const row of rows) { const k = String(key(row)); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => Number(a[0]) - Number(b[0]) || a[0].localeCompare(b[0]))); }
function support(rows, key) { return [...new Set(rows.map(key))].sort((a, b) => a - b); }
function coherent(values) { return values.length > 0 && values.at(-1) - values[0] <= 1; }
function workerMain() { parentPort.postMessage(workerData.sources.map((source) => scanOne(source, workerData.ticksRoot, false))); }

function receipt(rows, level, id) {
  const highSupport = support(rows, (row) => row.high_ordinal), lowSupport = support(rows, (row) => row.low_ordinal);
  const usableComponents = rows.every((row) => row.high_shape_usable && row.low_shape_usable);
  return {
    hypothesis_id: id,
    hierarchy_level: level,
    n: rows.length,
    minimum_n: MIN_N,
    hard_n_pass: rows.length >= MIN_N,
    component_single_leg_hypotheses_all_signable: usableComponents,
    high_leg_ordinal_counts: countBy(rows, (row) => row.high_ordinal),
    low_leg_ordinal_counts: countBy(rows, (row) => row.low_ordinal),
    high_leg_ordinal_support: highSupport,
    low_leg_ordinal_support: lowSupport,
    ordinal_coherence_pass: coherent(highSupport) && coherent(lowSupport),
    usable_for_signing: rows.length >= MIN_N && usableComponents && coherent(highSupport) && coherent(lowSupport),
    member_event_ids: rows.map((row) => row.event_id).sort(),
  };
}

async function main() {
  const single = JSON.parse(fs.readFileSync(singleLibraryPath, "utf8")), excluded = new Set(EXCLUDED_EVENTS);
  const shapeById = new Map(Object.values(single.groups).flatMap((g) => g.shapes).map((shape) => [shape.shape_id, shape]));
  const lines = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/), headers = lines.shift().split(",");
  const sources = lines.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v])))
    .filter((row) => !excluded.has(row.event_id) && String(row.evaluator_window_positive).toLowerCase() === "true")
    .map((row) => ({ event_id: row.event_id, category: row.category, leg: row.leg, ticker: row.ticker, left_ts: Number(row.left_ts), right_ts: Number(row.right_ts) }));
  const buckets = Array.from({ length: workers }, () => []); sources.forEach((source, i) => buckets[i % workers].push(source));
  const scanned = (await Promise.all(buckets.map((bucket) => new Promise((resolve, reject) => { const worker = new Worker(__filename, { workerData: { sources: bucket, ticksRoot } }); worker.on("message", resolve); worker.on("error", reject); })))).flat().sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id));
  const pairs = [];
  for (const [eventId, legs] of group(scanned.filter((row) => row.status === "AVAILABLE"), (row) => row.event_id)) {
    if (legs.length !== 2) continue;
    const [high, low] = [...legs].sort((a, b) => b.first_ask - a.first_ask || a.leg_id.localeCompare(b.leg_id));
    const highShapeId = single.assignment[`${eventId}|${high.leg_id}`], lowShapeId = single.assignment[`${eventId}|${low.leg_id}`];
    const highShape = shapeById.get(highShapeId), lowShape = shapeById.get(lowShapeId);
    const highOrdinal = high.qualified_descent_to_final_reachable_low?.descent_ordinal, lowOrdinal = low.qualified_descent_to_final_reachable_low?.descent_ordinal;
    if (!highShape || !lowShape || !Number.isInteger(highOrdinal) || !Number.isInteger(lowOrdinal)) continue;
    pairs.push({ event_id: eventId, category: high.category, high_shape_id: highShapeId, low_shape_id: lowShapeId, high_shape_usable: highShape.usable_for_signing, low_shape_usable: lowShape.usable_for_signing, high_family: familyOf(highShapeId), low_family: familyOf(lowShapeId), high_ordinal: highOrdinal, low_ordinal: lowOrdinal });
  }
  const categories = {};
  for (const [category, rows] of [...group(pairs, (row) => row.category)].sort(([a], [b]) => a.localeCompare(b))) {
    const parents = new Map();
    for (const [key, members] of group(rows.filter((row) => row.high_family && row.low_family), (row) => `${row.high_family}|${row.low_family}`)) parents.set(key, receipt(members, "STRUCTURAL_PATH_FAMILY_COUPLE_PARENT", `${category}|PARENT|${key}`));
    const couples = [];
    for (const [key, members] of [...group(rows, (row) => exactKey(row.high_shape_id, row.low_shape_id))].sort(([a], [b]) => a.localeCompare(b))) {
      const direct = receipt(members, "EXACT_SINGLE_LEG_HYPOTHESIS_COUPLE", `${category}|EXACT|${key}`), sample = members[0], parentKey = sample.high_family && sample.low_family ? `${sample.high_family}|${sample.low_family}` : null, parent = parentKey ? parents.get(parentKey) : null;
      const authority = direct.usable_for_signing ? "DIRECT_EXACT_COUPLE" : parent?.usable_for_signing ? "EXPLICIT_STRUCTURAL_PARENT_BORROW" : "UNUSABLE_ABSTAIN";
      couples.push({
        pair_couple_id: direct.hypothesis_id,
        category,
        high_shape_id: sample.high_shape_id,
        low_shape_id: sample.low_shape_id,
        n: direct.n,
        direct_receipt: direct,
        borrowed_from: authority === "EXPLICIT_STRUCTURAL_PARENT_BORROW" ? parent.hypothesis_id : null,
        borrowed_parent_receipt: authority === "EXPLICIT_STRUCTURAL_PARENT_BORROW" ? parent : null,
        authority,
        usable_for_signing: authority !== "UNUSABLE_ABSTAIN",
        unusable_reason: authority === "UNUSABLE_ABSTAIN" ? "EXACT_COUPLE_FAILED_AND_NO_COHERENT_N_GE_30_STRUCTURAL_PARENT" : null,
        effective_ordinal_support: authority === "DIRECT_EXACT_COUPLE" ? { high: direct.high_leg_ordinal_support, low: direct.low_leg_ordinal_support } : authority === "EXPLICIT_STRUCTURAL_PARENT_BORROW" ? { high: parent.high_leg_ordinal_support, low: parent.low_leg_ordinal_support } : null,
      });
    }
    categories[category] = { category, hierarchy: ["EXACT_SINGLE_LEG_HYPOTHESIS_COUPLE", "STRUCTURAL_PATH_FAMILY_COUPLE_PARENT"], minimum_n: MIN_N, couples, parent_receipts: [...parents.values()].sort((a, b) => a.hypothesis_id.localeCompare(b.hypothesis_id)) };
  }
  const all = Object.values(categories).flatMap((g) => g.couples), signable = all.filter((row) => row.usable_for_signing), signableEvents = new Set(signable.flatMap((row) => row.direct_receipt.member_event_ids));
  const result = {
    schema_version: "WINDOW1_PAIR_COUPLE_LIBRARY_V19",
    score_free: true,
    fit_excludes_exact_start_games: true,
    excluded_exact_start_events: EXCLUDED_EVENTS,
    architecture: { single_leg_hypotheses: 39, pair_identity: "COMBINATION_OF_TWO_V13_INTERIM_SINGLE_LEG_HYPOTHESES", endpoint_labels: false, cells_or_price_buckets: false, hierarchy: "EXACT COUPLE THEN EXPLICIT STRUCTURAL PATH-FAMILY COUPLE PARENT", abstention: "NO SIGNABLE COUPLE LEAVES THE V11 PATH BYTE-IDENTICAL; PAIR COUPLES NEVER VETO", minimum_n: MIN_N, interpolation: "FORBIDDEN" },
    groups: single.groups,
    assignment: single.assignment,
    pair_shape_tuples: single.pair_shape_tuples,
    micro_micro_models: single.micro_micro_models,
    pair_couple_groups: categories,
    census: { pair_events_with_two_formed_books_and_both_ordinals: pairs.length, exact_pair_couples: all.length, direct_signable_couples: signable.filter((row) => row.authority === "DIRECT_EXACT_COUPLE").length, parent_borrowed_signable_couples: signable.filter((row) => row.authority === "EXPLICIT_STRUCTURAL_PARENT_BORROW").length, unusable_couples: all.length - signable.length, signable_event_members: signableEvents.size, signable_leg_identities: signableEvents.size * 2, denominator_available_single_leg_hypothesis_members: single.census.available_training_legs },
    source: { single_leg_library: { path: path.relative(repo, singleLibraryPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(singleLibraryPath)) }, quote_ledger: { path: path.relative(repo, quotePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(quotePath)) }, private_tick_files: Object.fromEntries(scanned.map((row) => [row.ticker, row.source])) },
  };
  fs.mkdirSync(path.dirname(output), { recursive: true }); const bytes = Buffer.from(canonical(result)); fs.writeFileSync(output, bytes); process.stdout.write(canonical({ status: "BUILT", output, sha256: sha256(bytes), census: result.census }));
}

if (!isMainThread) workerMain();
else if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = { receipt, coherent };
