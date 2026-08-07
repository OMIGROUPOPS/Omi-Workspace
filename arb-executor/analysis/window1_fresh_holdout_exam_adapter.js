#!/usr/bin/env node
"use strict";

/*
 * Binding-only adapter for the sealed-171 V35/V36 exam.
 *
 * The frozen builders are compiled from their exact source bytes after one
 * ephemeral change: their terminal causalMain() invocation is replaced by an
 * export of the already-defined loader, simulation, scoring, and trace
 * functions. No policy source is edited. DEV-804 parity is required before
 * the single-use exam mode can create a results directory.
 */

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const Module = require("module");
const path = require("path");
const { Writable } = require("stream");
const stream = require("stream/promises");
const zlib = require("zlib");
const { writeGzipRowsFile } = require("./window1_streaming_gzip_jsonl.js");

const argv = process.argv.slice(2);
const arg = (name, fallback = null) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const required = (name) => { const value = arg(name); if (!value) throw new Error(`${name} required`); return value; };
const repo = path.resolve(arg("--repo", path.join(__dirname, "../..")));
const mode = required("--mode");
const privateRoot = path.resolve(arg("--private-root", "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(required("--output"));

const BRAINS = {
  V36: {
    commit: "bfde0d8d1135f5c5f48a5f3d619ab30050efab83",
    builder: "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js",
    policy: "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js",
    builderSha256: "5e8ba40af9fc85986fc921e79ffda582272b48f6ff522c40d3fba4509ffbb2bf",
    policySha256: "5db3922d5749e11548bca0c301abec19da5e2dfb993ffc17a44ec90989e34f73",
    frozen: ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806",
    scoreSchema: "window1-v36-state-directional-rest-mature-floor-close-free-score-v1",
  },
  V35: {
    commit: "0799fba887f1d1e84f9c0ef3e73096fd9d76019e",
    builder: "arb-executor/analysis/build_window1_v35_living_rest_evidence_gate.js",
    policy: "arb-executor/analysis/window1_v35_living_rest_evidence_gate.js",
    builderSha256: "ffff1aa3027f8bee17dba77905eaa13edd3e12292f6b849d733afe75652735c6",
    policySha256: "14d237ccfcda4c716a43c6c455ad0f4a8c8994835f770bd3ff18ce4d7d79a54f",
    frozen: ".claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806",
    scoreSchema: "window1-v35-living-rest-evidence-gate-close-free-score-v1",
  },
};
const START_COMMIT = "224417da642a9f378a0d83f76edffe9890cb4a6f";
const START_PATH = ".claude/window1_start_recovery_20260724/REAL_START_LEDGER_V3.jsonl";
const CLEAN_DEEP_COMMIT = "03bac97b12777d751fbb334fa6ae0f605445498a";
const CLEAN_DEEP_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DEEP_PAIR_HYGIENE_CENSUS.json";
const SEALED_SHA256 = "06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313";
const BOUNDARY_SHA256 = "70f8b28749d8e1fd60e64af6e3ced41e556b2a20e5898ec692f0e4f7081b7c0a";

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha(fs.readFileSync(file)); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function readJsonl(file) { const text = fs.readFileSync(file, "utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function gitShow(commit, rel) { return child.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 512 * 1024 * 1024 }); }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function group(rows, fn) { const out = new Map(); for (const row of rows) { const key = fn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function priceRegion(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function writeJson(dir, name, value) { fs.writeFileSync(path.join(dir, name), canonical(value)); }

function compileFrozenBrain(name, privateRootValue, scratchOutput) {
  const brain = BRAINS[name];
  const builderFile = path.join(repo, brain.builder);
  const policyFile = path.join(repo, brain.policy);
  const builderBytes = fs.readFileSync(builderFile);
  const policyBytes = fs.readFileSync(policyFile);
  ensure(sha(builderBytes) === brain.builderSha256, `${name} builder hash drift`);
  ensure(sha(policyBytes) === brain.policySha256, `${name} policy hash drift`);
  ensure(sha(gitShow(brain.commit, brain.builder)) === brain.builderSha256, `${name} pinned builder mismatch`);
  ensure(sha(gitShow(brain.commit, brain.policy)) === brain.policySha256, `${name} pinned policy mismatch`);
  let source = builderBytes.toString("utf8").replace(/^#![^\n]*\n/, "");
  const terminal = "causalMain().catch((error) => { process.stderr.write(`${error.stack || error}\\n`); process.exitCode = 1; });";
  ensure(source.includes(terminal), `${name} terminal invocation not found`);
  const exportSource = "module.exports = { loadBaseEvents, loadSources, loadFullTape, condenseTape, buildPrintSpool, w1Boundary, w1Clock, evidenceInsideWindow, simulateW1Mode, scoreW1Column, frontierW1, regretW1, fillSplit, compactW1Trace, restSanity, gradeDigest, stripCloseTelemetry, parseEt, integer, positive };";
  source = source.replace(terminal, exportSource);
  const priorArgv = process.argv;
  try {
    process.argv = [priorArgv[0], builderFile, "--repo", repo, "--private-root", privateRootValue, "--output", scratchOutput];
    const instance = new Module(builderFile, module);
    instance.filename = builderFile;
    instance.paths = Module._nodeModulePaths(path.dirname(builderFile));
    instance._compile(source, builderFile);
    return instance.exports;
  } finally {
    process.argv = priorArgv;
  }
}

function normalizedBoundary(row) {
  return {
    event_id: row.event_id,
    right_edge_epoch: Number(row.right_edge_epoch),
    edge_source_field: row.right_edge_source_field,
    precision_class: row.precision_class,
    selected_source: row.selected_source,
    selected_source_family: row.selected_source,
    selected_timestamp_precision: row.selected_timestamp_precision,
    conflict_status: "FROZEN_STAGE12_NO_CONFLICT_FIELD",
    interval_contradiction: false,
  };
}

function loadTapeWithApi(api, file, ticker) {
  const bytes = fs.readFileSync(file);
  const lines = zlib.gunzipSync(bytes).toString("utf8").trimEnd().split(/\r?\n/);
  const header = lines.shift().split(",");
  const ix = Object.fromEntries(header.map((value, index) => [value, index]));
  const out = [];
  for (let n = 0; n < lines.length; n += 1) {
    const value = lines[n].split(","), ts = api.parseEt(value[ix.ts_et]);
    if (!Number.isFinite(ts)) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = api.integer(value[ix[`bid_${level}`]]), bs = api.positive(value[ix[`bid_${level}_sz`]]), ap = api.integer(value[ix[`ask_${level}`]]), as = api.positive(value[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    out.push({ kind: "BOOK", ticker, ts, ordinal: n + 2, receipt: `${ticker}.csv.gz#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bids.reduce((sum, row) => sum + row[1], 0), ask_depth_5: asks.reduce((sum, row) => sum + row[1], 0), last_trade: api.integer(value[ix.last_trade]) });
  }
  out.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, since = null;
  for (const row of out) { if (row.ask !== ask) { ask = row.ask; since = row.ts; } row.ask_dwell_seconds = row.ts - since; row.depth_ratio = row.bid_depth_5 / (row.bid_depth_5 + row.ask_depth_5); }
  out.rawReceiptCount = out.length;
  return out;
}

function loadSealedPrints(file) {
  const byTicker = new Map();
  for (const row of readJsonl(file)) {
    const ts = Date.parse(row.exchange_ts) / 1000;
    ensure(Number.isFinite(ts) && row.true_print === true && row.trade_id, "invalid sealed print");
    if (!byTicker.has(row.ticker)) byTicker.set(row.ticker, []);
    byTicker.get(row.ticker).push({ kind: "PRINT", ticker: row.ticker, ts, ordinal: 1, receipt: row.trade_id, price: Number(row.price_cents), size: Number(row.size), taker_side: row.taker_side, trade_id: row.trade_id });
  }
  for (const rows of byTicker.values()) {
    rows.sort((a, b) => a.ts - b.ts || a.trade_id.localeCompare(b.trade_id));
    rows.forEach((row, index) => { row.ordinal = index + 1; });
  }
  return byTicker;
}

function createSealedBinding(api, declarationFile, eventListFile, boundaryFile, tapeRoot, printsFile) {
  const listBytes = fs.readFileSync(eventListFile);
  ensure(sha(listBytes) === SEALED_SHA256, "sealed list hash mismatch");
  ensure(hashFile(boundaryFile) === BOUNDARY_SHA256, "boundary ledger hash mismatch");
  const ids = listBytes.toString("utf8").trim().split(/\r?\n/);
  const declaration = readJson(declarationFile);
  const byId = new Map(declaration.events.map((row) => [row.event_id, row]));
  const rawBoundaryRows = readJsonl(boundaryFile);
  const rawBoundaries = new Map(rawBoundaryRows.map((row) => [row.event_id, row]));
  const boundaries = new Map(rawBoundaryRows.map((row) => [row.event_id, normalizedBoundary(row)]));
  const prints = loadSealedPrints(printsFile);
  const rawTapes = new Map(), tapeHashes = {};
  const baseEvents = [];
  const sources = new Map(), bells = new Map();
  for (const eventId of ids) {
    const sourceEvent = byId.get(eventId), boundary = boundaries.get(eventId);
    ensure(sourceEvent && boundary && sourceEvent.legs.length === 2, `missing sealed binding ${eventId}`);
    const legs = {};
    const firstBids = [];
    for (const sourceLeg of sourceEvent.legs) {
      const ticker = sourceLeg.ticker, legId = sourceLeg.leg_id;
      const file = path.join(tapeRoot, path.basename(sourceLeg.remote_path));
      ensure(fs.existsSync(file), `missing tape ${ticker}`);
      ensure(hashFile(file) === sourceLeg.sha256 && fs.statSync(file).size === sourceLeg.bytes, `tape identity mismatch ${ticker}`);
      const raw = loadTapeWithApi(api, file, ticker);
      ensure(raw.length > 0, `no formed book ${ticker}`);
      rawTapes.set(ticker, raw); tapeHashes[ticker] = { sha256: hashFile(file), bytes: fs.statSync(file).size };
      firstBids.push(raw[0].bid);
      const region = priceRegion(raw[0].bid);
      legs[legId] = { leg_identity: `${eventId}|${legId}`, event_id: eventId, category: sourceEvent.category, price_region: region, leg_id: legId, ticker, R3: null };
      const scheduleCandidate = (rawBoundaries.get(eventId)?.candidate_sources || []).find((row) => row.direction === "schedule_bound");
      sources.set(ticker, { event_id: eventId, ticker, scheduled: scheduleCandidate?.timestamp_epoch ?? boundary.right_edge_epoch });
    }
    const orderedRegions = firstBids.slice().sort((a, b) => a - b).map(priceRegion);
    const split = orderedRegions.join("+");
    for (const leg of Object.values(legs)) leg.starting_price_split = split;
    baseEvents.push({ event_id: eventId, category: sourceEvent.category, starting_price_split: split, legs });
    if (boundary.precision_class === "exact") bells.set(eventId, boundary.right_edge_epoch);
  }
  ensure(baseEvents.length === 171 && rawTapes.size === 342 && prints.size <= 342, "sealed input conservation failed");
  return { baseEvents, boundaries, sources, bells, rawTapes, prints, tapeHashes };
}

function timelineFor(baseEvent, tapes, prints) {
  const timeline = [];
  for (const [legId, leg] of Object.entries(baseEvent.legs)) {
    for (const row of tapes.get(leg.ticker)) timeline.push({ ...row, leg_id: legId });
    for (const row of prints.get(leg.ticker) || []) timeline.push({ ...row, leg_id: legId });
  }
  timeline.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
  return timeline;
}

function runPopulation(api, binding, brainName) {
  const strictEvents = [], censusEvents = [], actions = [], decisions = [], spans = [];
  const expected = binding.baseEvents.length;
  for (let eventIndex = 0; eventIndex < binding.baseEvents.length; eventIndex += 1) {
    const baseEvent = binding.baseEvents[eventIndex], boundary = binding.boundaries.get(baseEvent.event_id);
    const tapes = new Map(), prints = new Map();
    for (const leg of Object.values(baseEvent.legs)) {
      const printRows = binding.prints.get(leg.ticker) || [];
      prints.set(leg.ticker, printRows);
      const raw = binding.rawTapes ? binding.rawTapes.get(leg.ticker) : binding.loadTape(leg.ticker);
      tapes.set(leg.ticker, api.condenseTape(raw, printRows));
    }
    const left = Math.min(...[...tapes.values()].map((rows) => rows[0]?.ts).filter(Number.isFinite));
    ensure(Number.isFinite(left), `no left edge ${baseEvent.event_id}`);
    const span = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, w1_left_epoch: left, w1_right_epoch: boundary.right_edge_epoch, edge_source_field: boundary.edge_source_field, precision_class: boundary.precision_class, selected_source: boundary.selected_source, selected_source_family: boundary.selected_source_family, selected_timestamp_precision: boundary.selected_timestamp_precision, conflict_status: boundary.conflict_status, interval_contradiction: boundary.interval_contradiction, non_positive_span: boundary.right_edge_epoch < left, span_seconds: Math.max(0, boundary.right_edge_epoch - left) };
    spans.push(span);
    const timeline = timelineFor(baseEvent, tapes, prints);
    const strictDecisions = [], censusDecisions = [];
    strictEvents.push(api.simulateW1Mode(baseEvent, tapes, prints, binding.sources, binding.bells, "STRICT_LAW", actions, strictDecisions, span, timeline, boundary));
    censusEvents.push(api.simulateW1Mode(baseEvent, tapes, prints, binding.sources, binding.bells, "CENSUS_PRICED", actions, censusDecisions, span, timeline, boundary));
    for (const row of strictDecisions) decisions.push(row);
    for (const row of censusDecisions) decisions.push(row);
    if ((eventIndex + 1) % 25 === 0 || eventIndex + 1 === expected) process.stderr.write(`${brainName}_ADAPTER events=${eventIndex + 1}/${expected}\n`);
  }
  return {
    strictEvents, censusEvents, actions, decisions, spans,
    strictTrace: api.compactW1Trace(strictEvents), censusTrace: api.compactW1Trace(censusEvents),
    strictScore: api.scoreW1Column(strictEvents, "STRICT_LAW"),
    censusScore: api.scoreW1Column(censusEvents, "CENSUS_PRICED_ONE_CENT_RESIDENCY"),
    strictFrontier: api.frontierW1(strictEvents), censusFrontier: api.frontierW1(censusEvents),
    strictRegret: api.regretW1(strictEvents), censusRegret: api.regretW1(censusEvents),
    strictFillSplit: api.fillSplit(strictEvents), censusFillSplit: api.fillSplit(censusEvents),
  };
}

function devBinding(api, brainName, scratch) {
  const startRows = gitShow(START_COMMIT, START_PATH).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
  const printLoad = api.buildPrintSpool(new Set(api.loadBaseEvents().flatMap((event) => Object.values(event.legs).map((leg) => leg.ticker))));
  const loadTape = (ticker) => api.loadFullTape(ticker, {});
  return {
    baseEvents: api.loadBaseEvents(),
    boundaries: new Map(startRows.map((row) => [row.event_id, api.w1Boundary(row)])),
    sources: api.loadSources(),
    bells: new Map(readJson(path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json")).leg_rows.map((row) => [row.event_id, row.exact_bell_ts])),
    prints: { get: (ticker) => printLoad.load(ticker) },
    loadTape,
    cleanup: () => printLoad.cleanup(),
    scratch,
  };
}

function byteEqualObject(left, right) { return Buffer.from(canonical(left)).equals(Buffer.from(canonical(right))); }

function orderedJsonlDigest(rows) {
  const digest = crypto.createHash("sha256"); let bytes = 0;
  for (const row of rows) { const line = `${JSON.stringify(row)}\n`; digest.update(line); bytes += Buffer.byteLength(line); }
  return { rows: rows.length, bytes, sha256: digest.digest("hex") };
}

async function frozenFullTraceDigest(directory) {
  const parts = fs.readdirSync(directory).filter((name) => /^FULL_DECISION_TRACE\.jsonl\.gz\.part\d+$/.test(name)).sort();
  ensure(parts.length > 0, `frozen full-trace parts absent: ${directory}`);
  async function* compressedParts() { for (const name of parts) for await (const chunk of fs.createReadStream(path.join(directory, name))) yield chunk; }
  const digest = crypto.createHash("sha256"); let bytes = 0;
  const sink = new Writable({ write(chunk, _encoding, callback) { digest.update(chunk); bytes += chunk.length; callback(); } });
  await stream.pipeline(compressedParts(), zlib.createGunzip(), sink);
  return { parts: parts.length, bytes, sha256: digest.digest("hex") };
}

function fullScorecardForParity(name, result) {
  const frozen = readJson(path.join(repo, BRAINS[name].frozen, "SCORECARD_TWO_COLUMN.json"));
  frozen.STRICT_LAW = result.strictScore;
  frozen.CENSUS_PRICED = result.censusScore;
  frozen.conservation = { D_each_column: [result.strictScore.aggregate.D, result.censusScore.aggregate.D], expected_D: 804, pass: result.strictScore.aggregate.D === 804 && result.censusScore.aggregate.D === 804 };
  if (name === "V36") {
    const v35s = frozen.comparison_floor.V35_STRICT, v35c = frozen.comparison_floor.V35_CENSUS;
    frozen.delta_vs_V35 = { STRICT_completed_pairs: result.strictScore.aggregate.completed_pairs - v35s.completed_pairs, STRICT_under_par_pairs: result.strictScore.aggregate.pairs_under_par - v35s.pairs_under_par, CENSUS_completed_pairs: result.censusScore.aggregate.completed_pairs - v35c.completed_pairs, CENSUS_under_par_pairs: result.censusScore.aggregate.pairs_under_par - v35c.pairs_under_par };
    const v34s = frozen.comparison_floor.V34_W1_STRICT, v34c = frozen.comparison_floor.V34_W1_CENSUS;
    frozen.delta_vs_V34_W1 = { STRICT_completed_pairs: result.strictScore.aggregate.completed_pairs - v34s.completed_pairs, STRICT_under_par_pairs: result.strictScore.aggregate.pairs_under_par - v34s.pairs_under_par, CENSUS_completed_pairs: result.censusScore.aggregate.completed_pairs - v34c.completed_pairs, CENSUS_under_par_pairs: result.censusScore.aggregate.pairs_under_par - v34c.pairs_under_par };
  } else {
    const v34s = frozen.comparison_floor.V34_W1_STRICT, v34c = frozen.comparison_floor.V34_W1_CENSUS;
    frozen.delta_vs_V34_W1 = { STRICT_completed_pairs: result.strictScore.aggregate.completed_pairs - v34s.completed_pairs, STRICT_under_par_pairs: result.strictScore.aggregate.pairs_under_par - v34s.pairs_under_par, CENSUS_completed_pairs: result.censusScore.aggregate.completed_pairs - v34c.completed_pairs, CENSUS_under_par_pairs: result.censusScore.aggregate.pairs_under_par - v34c.pairs_under_par };
  }
  return frozen;
}

async function runDevInertness() {
  ensure(!fs.existsSync(output), "DEV inertness output must be absent");
  fs.mkdirSync(output, { recursive: true });
  const rows = {};
  for (const name of ["V36", "V35"]) {
    const scratch = path.join(output, `.scratch-${name.toLowerCase()}`);
    fs.mkdirSync(scratch, { recursive: true });
    const api = compileFrozenBrain(name, privateRoot, scratch);
    const binding = devBinding(api, name, scratch);
    let result;
    try { result = runPopulation(api, binding, name + "_DEV804"); } finally { binding.cleanup(); }
    const frozenStrictTrace = readJson(path.join(repo, BRAINS[name].frozen, "STRICT_DECISION_TRACE_1608.json"));
    const frozenCensusTrace = readJson(path.join(repo, BRAINS[name].frozen, "CENSUS_PRICED_DECISION_TRACE_1608.json"));
    const frozenScorecard = readJson(path.join(repo, BRAINS[name].frozen, "SCORECARD_TWO_COLUMN.json"));
    const candidateScorecard = fullScorecardForParity(name, result);
    const candidateFullTrace = orderedJsonlDigest(result.decisions);
    const frozenFullTrace = await frozenFullTraceDigest(path.join(repo, BRAINS[name].frozen));
    const checks = {
      strict_trace_byte_identical: byteEqualObject({ rows: result.strictTrace, conservation: { rows: result.strictTrace.length, expected: 1608, pass: result.strictTrace.length === 1608 } }, frozenStrictTrace),
      census_trace_byte_identical: byteEqualObject({ rows: result.censusTrace, conservation: { rows: result.censusTrace.length, expected: 1608, pass: result.censusTrace.length === 1608 } }, frozenCensusTrace),
      full_scorecard_byte_identical: byteEqualObject(candidateScorecard, frozenScorecard),
      strict_frontier_byte_identical: byteEqualObject(result.strictFrontier, readJson(path.join(repo, BRAINS[name].frozen, "STRICT_FRONTIER.json"))),
      census_frontier_byte_identical: byteEqualObject(result.censusFrontier, readJson(path.join(repo, BRAINS[name].frozen, "CENSUS_PRICED_FRONTIER.json"))),
      full_decision_trace_jsonl_byte_identical: candidateFullTrace.bytes === frozenFullTrace.bytes && candidateFullTrace.sha256 === frozenFullTrace.sha256,
    };
    rows[name] = { commit: BRAINS[name].commit, checks, pass: Object.values(checks).every(Boolean), decisions_inspected: result.decisions.length, full_decision_trace_jsonl: { candidate: candidateFullTrace, frozen: frozenFullTrace }, strict_events: result.strictEvents.length, census_events: result.censusEvents.length };
    fs.rmSync(scratch, { recursive: true, force: true });
    ensure(rows[name].pass, `${name} DEV inertness mismatch`);
  }
  writeJson(output, "DEV_INERTNESS_RECEIPT.json", { schema_version: "window1-sealed-exam-dev-inertness-v1", brains: rows, pass: Object.values(rows).every((row) => row.pass), scorer_or_policy_mutations: 0, sealed_exam_invocations: 0 });
  const names = fs.readdirSync(output).sort();
  writeJson(output, "ARTIFACT_HASH_MANIFEST.json", { files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) });
  process.stdout.write(canonical({ status: "PASS", brains: rows }));
}

function terminalCollapseReceipt(leg, trades) {
  if (!leg.credited || !Number.isInteger(leg.entry_cents) || leg.entry_cents > 9 || !Number.isFinite(leg.fill_timestamp_epoch)) return { terminal_collapse: false, reason: "ENTRY_NOT_SINGLE_DIGIT_OR_NOT_CREDITED", evidence: [] };
  const rows = trades.filter((row) => row.taker_side === "no" && Number.isFinite(row.size) && row.size > 0 && Math.abs(row.ts - leg.fill_timestamp_epoch) <= 1800).sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let best = [];
  for (let i = 0; i < rows.length; i += 1) {
    const run = [rows[i]];
    for (let j = i + 1; j < rows.length; j += 1) { if (rows[j].ts - run[0].ts > 1800) break; if (rows[j].price < run.at(-1).price) run.push(rows[j]); }
    if (run.length > best.length || (run.length === best.length && run[0].price - run.at(-1).price > (best[0]?.price ?? 0) - (best.at(-1)?.price ?? 0))) best = run;
  }
  const span = best.length ? best[0].price - best.at(-1).price : 0;
  const terminal = best.length >= 3 && span >= 10 && best.at(-1).price <= 9;
  return { terminal_collapse: terminal, reason: terminal ? "MONOTONE_SELLER_DUMP_GE3_SPAN_GE10_INTO_SINGLE_DIGITS_WITHIN_30M_OF_FILL" : "NO_QUALIFYING_TERMINAL_COLLAPSE", evidence: best.map((row) => ({ timestamp_epoch: row.ts, ordinal: row.ordinal, receipt: row.receipt, price_cents: row.price, size: row.size, aggressor_side: "SELLER" })) };
}

function cleanDeep(events, prints, mode) {
  const rows = events.filter((event) => event.completed_pair && event.combined_entry_cents <= 95).map((event) => {
    const receipts = Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, terminalCollapseReceipt(leg, prints.get(leg.ticker) || [])]));
    const any = Object.values(receipts).some((row) => row.terminal_collapse);
    return { event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, bell_confidence: event.bell_confidence, combined_entry_cents: event.combined_entry_cents, exact_bell: event.bell_confidence === "exact", any_terminal_collapse: any, exact_bell_collapse_clean: event.bell_confidence === "exact" && !any, leg_receipts: receipts };
  });
  return { mode, deep_definition: "COMPLETED_PAIR_COMBINED_ENTRY_LE_95", terminal_collapse_method: "03bac97b: credited single-digit leg inside monotone seller-aggressed run of >=3 descending prints spanning >=10c into single digits within 30 minutes", deep_pairs: rows.length, by_bell_confidence: countBy(rows, (row) => row.bell_confidence), with_terminal_collapse: rows.filter((row) => row.any_terminal_collapse).length, exact_bell: rows.filter((row) => row.exact_bell).length, exact_bell_collapse_clean: rows.filter((row) => row.exact_bell_collapse_clean).length, schedule_only_collapse_clean: rows.filter((row) => row.bell_confidence === "schedule_only" && !row.any_terminal_collapse).length, rows };
}

function dynamicRestSanity(api, events, actions, mode) {
  const value = api.restSanity(events, actions, mode);
  const expected = events.length * 2;
  value.conservation = { rows: value.rows.length, expected_legs: expected, cell_legs: value.category_x_price_region_x_bell_confidence.reduce((sum, row) => sum + row.legs, 0), pass: value.rows.length === expected && value.category_x_price_region_x_bell_confidence.reduce((sum, row) => sum + row.legs, 0) === expected };
  return value;
}

function buildBrainArtifacts(name, api, result, binding) {
  const strictClean = cleanDeep(result.strictEvents, binding.prints, "STRICT_LAW");
  const censusClean = cleanDeep(result.censusEvents, binding.prints, "CENSUS_PRICED");
  const devScore = readJson(path.join(repo, BRAINS[name].frozen, "SCORECARD_TWO_COLUMN.json"));
  const scorecard = {
    schema_version: `window1-fresh-holdout-${name.toLowerCase()}-score-v1`,
    brain_commit: BRAINS[name].commit,
    R3_excluded_context_only: { commit: "49f6501561c5d99a7f36c68ec41e0ea7250680e5", original_joint_reference_only: 68, reason: "TRANSITIVE_INPUT_BLOCKER_4f4d546" },
    development_context: { STRICT_LAW: devScore.STRICT_LAW.aggregate, CENSUS_PRICED: devScore.CENSUS_PRICED.aggregate },
    STRICT_LAW: result.strictScore,
    CENSUS_PRICED: result.censusScore,
    clean_deep: { STRICT_LAW: { ...strictClean, rows: undefined }, CENSUS_PRICED: { ...censusClean, rows: undefined } },
    conservation: { D_each_column: [result.strictScore.aggregate.D, result.censusScore.aggregate.D], expected_D: 171, pass: result.strictScore.aggregate.D === 171 && result.censusScore.aggregate.D === 171 },
  };
  return {
    "SCORECARD_TWO_COLUMN.json": canonical(scorecard),
    "STRICT_FRONTIER.json": canonical(result.strictFrontier),
    "CENSUS_PRICED_FRONTIER.json": canonical(result.censusFrontier),
    "STRICT_REGRET_GAUGE.json": canonical({ ...result.strictRegret, rows: undefined }),
    "CENSUS_PRICED_REGRET_GAUGE.json": canonical({ ...result.censusRegret, rows: undefined }),
    "STRICT_REGRET_LEDGER.jsonl.gz": gzipRows(result.strictRegret.rows),
    "CENSUS_PRICED_REGRET_LEDGER.jsonl.gz": gzipRows(result.censusRegret.rows),
    "STRICT_EVENT_LEDGER.jsonl.gz": gzipRows(result.strictEvents),
    "CENSUS_PRICED_EVENT_LEDGER.jsonl.gz": gzipRows(result.censusEvents),
    "STRICT_DECISION_TRACE_342.json": canonical({ rows: result.strictTrace, conservation: { rows: result.strictTrace.length, expected: 342, pass: result.strictTrace.length === 342 } }),
    "CENSUS_PRICED_DECISION_TRACE_342.json": canonical({ rows: result.censusTrace, conservation: { rows: result.censusTrace.length, expected: 342, pass: result.censusTrace.length === 342 } }),
    "ACTION_AND_FILL_TRACE.jsonl.gz": gzipRows(result.actions),
    "WINDOW1_SPAN_171.json": canonical({ rows: result.spans, precision_class_counts: countBy(result.spans, (row) => row.precision_class), conservation: { rows: result.spans.length, expected: 171, pass: result.spans.length === 171 } }),
    "STRICT_FILL_SPLIT.json": canonical(result.strictFillSplit),
    "CENSUS_PRICED_FILL_SPLIT.json": canonical(result.censusFillSplit),
    "STRICT_REST_SANITY.json": canonical(dynamicRestSanity(api, result.strictEvents, result.actions, "STRICT_LAW")),
    "CENSUS_PRICED_REST_SANITY.json": canonical(dynamicRestSanity(api, result.censusEvents, result.actions, "CENSUS_PRICED")),
    "STRICT_CLEAN_DEEP.json": canonical(strictClean),
    "CENSUS_PRICED_CLEAN_DEEP.json": canonical(censusClean),
  };
}

async function runExam() {
  const inertnessFile = path.resolve(required("--dev-inertness-receipt"));
  const declarationFile = path.resolve(required("--sealed-declaration"));
  const eventListFile = path.resolve(required("--event-list"));
  const boundaryFile = path.resolve(required("--boundary-ledger"));
  const tapeRoot = path.resolve(required("--tape-root"));
  const printsFile = path.resolve(required("--prints"));
  const printsReceiptFile = path.resolve(required("--prints-receipt"));
  ensure(!fs.existsSync(output), "exam results directory already exists: authorization single-use guard");
  const inertness = readJson(inertnessFile);
  ensure(inertness.pass === true && inertness.sealed_exam_invocations === 0, "DEV inertness gate not PASS");
  ensure(readJson(printsReceiptFile).nightly_method_spot_reconciliation.pass === true, "print re-pull receipt not PASS");
  fs.mkdirSync(output, { recursive: true });
  writeJson(output, "EXECUTION_START_RECEIPT.json", { schema_version: "window1-fresh-holdout-exam-start-v2", authorization: "OPERATOR_PROMPT_SERIALIZER_REPAIR_FRESH_EXAM_20260807", authorization_consumed: true, invocation_count: 1, retries: 0, prior_consumed_failure_commit: "a746d17582284736f9b3a9e6c8db2bf61e9204e1", brains: ["V36", "V35"], R3_excluded: true, event_N: 171, event_list_sha256: hashFile(eventListFile), boundary_sha256: hashFile(boundaryFile), prints_sha256: hashFile(printsFile), started_at_utc: new Date().toISOString() });
  const policyBefore = Object.fromEntries(Object.entries(BRAINS).map(([name, brain]) => [name, { builder_sha256: hashFile(path.join(repo, brain.builder)), policy_sha256: hashFile(path.join(repo, brain.policy)) }]));
  const results = {}, artifactBuilds = {};
  for (const name of ["V36", "V35"]) {
    const scratch = path.join(output, `.scratch-${name.toLowerCase()}`); fs.mkdirSync(scratch);
    const api = compileFrozenBrain(name, privateRoot, scratch);
    const binding = createSealedBinding(api, declarationFile, eventListFile, boundaryFile, tapeRoot, printsFile);
    const result = runPopulation(api, binding, name + "_SEALED171");
    results[name] = { result, binding };
    artifactBuilds[name] = buildBrainArtifacts(name, api, result, binding);
    fs.rmSync(scratch, { recursive: true, force: true });
  }
  const policyAfter = Object.fromEntries(Object.entries(BRAINS).map(([name, brain]) => [name, { builder_sha256: hashFile(path.join(repo, brain.builder)), policy_sha256: hashFile(path.join(repo, brain.policy)) }]));
  ensure(JSON.stringify(policyBefore) === JSON.stringify(policyAfter), "policy bytes changed during exam");
  for (const [name, artifacts] of Object.entries(artifactBuilds)) {
    const brainDir = path.join(output, name); fs.mkdirSync(brainDir);
    const serializationScratch = path.join(output, `.scratch-serialize-${name.toLowerCase()}`); fs.mkdirSync(serializationScratch, { recursive: true });
    const build2 = buildBrainArtifacts(name, compileFrozenBrain(name, privateRoot, serializationScratch), results[name].result, results[name].binding);
    const names = Object.keys(artifacts).sort();
    const mismatch = names.filter((artifact) => !Buffer.from(artifacts[artifact]).equals(Buffer.from(build2[artifact])));
    for (const artifact of names) fs.writeFileSync(path.join(brainDir, artifact), artifacts[artifact]);
    const traceName = "FULL_DECISION_TRACE.jsonl.gz";
    const traceFile = path.join(brainDir, traceName), traceCheck = path.join(serializationScratch, traceName);
    await writeGzipRowsFile(traceFile, results[name].result.decisions);
    await writeGzipRowsFile(traceCheck, results[name].result.decisions);
    if (hashFile(traceFile) !== hashFile(traceCheck) || fs.statSync(traceFile).size !== fs.statSync(traceCheck).size) mismatch.push(traceName);
    ensure(mismatch.length === 0, `${name} artifact serialization determinism mismatch`);
    fs.rmSync(serializationScratch, { recursive: true, force: true });
    writeJson(brainDir, "DETERMINISM_RECEIPT.json", { builds_from_single_authorized_in_memory_replay: 2, replay_invocations: 1, byte_identical: true, compared_files: names.length + 1, streaming_full_trace: true, mismatches: [] });
    const files = fs.readdirSync(brainDir).sort();
    writeJson(brainDir, "ARTIFACT_HASH_MANIFEST.json", { files: Object.fromEntries(files.map((file) => [file, { sha256: hashFile(path.join(brainDir, file)), bytes: fs.statSync(path.join(brainDir, file)).size }])) });
  }
  const bellRows = [];
  for (const name of ["V36", "V35"]) {
    for (const column of ["STRICT_LAW", "CENSUS_PRICED"]) {
      const events = column === "STRICT_LAW" ? results[name].result.strictEvents : results[name].result.censusEvents;
      for (const confidence of ["exact", "live_by_only", "schedule_only"]) {
        const subset = events.filter((event) => event.bell_confidence === confidence);
        const completed = subset.filter((event) => event.completed_pair);
        const deep = cleanDeep(subset, results[name].binding.prints, column);
        bellRows.push({ brain: name, column, bell_confidence: confidence, headline: confidence === "exact", D: subset.length, completed_pairs: completed.length, under_par_pairs: completed.filter((event) => event.pair_under_par).length, frontier: { LE_93: completed.filter((event) => event.combined_entry_cents <= 93).length, LE_95: completed.filter((event) => event.combined_entry_cents <= 95).length, LE_97: completed.filter((event) => event.combined_entry_cents <= 97).length, LT_100: completed.filter((event) => event.combined_entry_cents < 100).length, ANY_PRICE: completed.length }, collapse_clean_LE95: confidence === "exact" ? deep.exact_bell_collapse_clean : confidence === "schedule_only" ? deep.schedule_only_collapse_clean : deep.deep_pairs - deep.with_terminal_collapse });
      }
    }
  }
  writeJson(output, "BELL_CONFIDENCE_SCORECARD.json", { exact_bell_headline_D: 11, schedule_only_D: 146, rows: bellRows, conservation: { rows: bellRows.length, expected: 12, pass: bellRows.length === 12 } });
  writeJson(output, "POLICY_BYTE_IDENTITY_RECEIPT.json", { before: policyBefore, after: policyAfter, byte_identical: JSON.stringify(policyBefore) === JSON.stringify(policyAfter), ephemeral_adapter_operation: "TERMINAL_RUNNER_INVOCATION_REPLACED_BY_INTERNAL_FUNCTION_EXPORT_IN_MEMORY_ONLY", policy_files_modified: 0 });
  writeJson(output, "CONTROL_BINDING.json", { event_N: 171, legs: 342, event_list_sha256: hashFile(eventListFile), boundary_sha256: hashFile(boundaryFile), prints_sha256: hashFile(printsFile), brains: Object.fromEntries(Object.entries(BRAINS).map(([name, brain]) => [name, brain.commit])), R3: { status: "EXCLUDED", dev_context_only: true, blocker_commit: "4f4d546421043f187bc73e2d9ad1eca0b9cf7f36" }, clean_deep: { commit: CLEAN_DEEP_COMMIT, path: CLEAN_DEEP_PATH, sha256: sha(gitShow(CLEAN_DEEP_COMMIT, CLEAN_DEEP_PATH)) }, one_run: { invocations: 1, retries: 0, authorization_consumed: true } });
  writeJson(output, "FORBIDDEN_ACCESS_RECEIPT.json", { exam_replay_network_access: 0, live_engine_access: 0, account_access: 0, order_access: 0, position_access: 0, trading_access: 0, tuning: 0, policy_edits: 0, R3_invocations: 0, input_network_access_before_exam: "PUBLIC_TRADE_REPULL_AND_N20_CAPTURE_RECONCILIATION_ONLY" });
  writeJson(output, "EXECUTION_COMPLETE_RECEIPT.json", { status: "COMPLETE", invocation_count: 1, retries: 0, brain_invocations: { V36: 1, V35: 1, R3: 0 }, score_rows: bellRows.length, authorization_consumed: true, completed_at_utc: new Date().toISOString() });
  const reportLines = ["# Sealed-171 Window-1 generalization exam", "", "The exact-bell core (11 games) is the headline partition. Schedule-only (146 games) is shown separately with the 03bac97b terminal-collapse hygiene method. V36 and V35 ran once after byte-identical DEV-804 traces and scorecards passed. R3 is excluded and its development number is context only.", ""];
  for (const row of bellRows.filter((row) => row.headline)) reportLines.push(`- ${row.brain} ${row.column} exact: D=${row.D}; completed=${row.completed_pairs}; under_par=${row.under_par_pairs}; <=93/<=95/<=97/<100/any=${row.frontier.LE_93}/${row.frontier.LE_95}/${row.frontier.LE_97}/${row.frontier.LT_100}/${row.frontier.ANY_PRICE}; clean-deep<=95=${row.collapse_clean_LE95}.`);
  reportLines.push("", "No retry, tuning, live engine, account, order, position, or trading access occurred.", "");
  fs.writeFileSync(path.join(output, "REPORT.md"), reportLines.join("\n"));
  const manifestFiles = [];
  for (const entry of fs.readdirSync(output, { withFileTypes: true })) {
    if (entry.name.startsWith(".scratch") || entry.name === "ARTIFACT_HASH_MANIFEST.json") continue;
    if (entry.isFile()) manifestFiles.push(entry.name);
    if (entry.isDirectory()) for (const file of fs.readdirSync(path.join(output, entry.name))) manifestFiles.push(`${entry.name}/${file}`);
  }
  writeJson(output, "ARTIFACT_HASH_MANIFEST.json", { files: Object.fromEntries(manifestFiles.sort().map((rel) => [rel.replaceAll("\\", "/"), { sha256: hashFile(path.join(output, rel)), bytes: fs.statSync(path.join(output, rel)).size }])) });
  process.stdout.write(canonical({ status: "COMPLETE", invocation_count: 1, retries: 0, exact_headline: bellRows.filter((row) => row.headline) }));
}

async function main() {
  if (mode === "dev-inertness") await runDevInertness();
  else if (mode === "exam-execute") await runExam();
  else throw new Error(`unsupported mode ${mode}`);
}

main().catch((error) => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
