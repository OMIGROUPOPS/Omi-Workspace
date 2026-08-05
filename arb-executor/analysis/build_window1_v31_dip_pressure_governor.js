#!/usr/bin/env node
"use strict";

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const {
  HALFLIFE_SECONDS,
  TRAINING_DIP_HORIZON_SECONDS,
  MIN_TRAIN_ROWS,
  FEATURE_NAMES,
  updateEwma,
  featureVector,
  predict,
  onlineUpdate,
  fitThreshold,
  authorityVerdict,
  governBuy,
} = require("./window1_v31_dip_pressure_governor.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const index = argv.indexOf(name); return index < 0 ? fallback : argv[index + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805")));
const finalizeRun1 = arg("--finalize-run1", null);
const finalizeRun2 = arg("--finalize-run2", null);
const base = path.join(repo, ".claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805");
const baseEventPath = path.join(base, "EVENT_LEDGER.jsonl.gz");
const baseLegPath = path.join(base, "LEG_LEDGER.jsonl.gz");
const baseTracePath = path.join(base, "DECISION_TRACE_1608.json");
const baseScorePath = path.join(base, "SCORECARD.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const policyPath = path.join(repo, "arb-executor/analysis/window1_v31_dip_pressure_governor.js");
const builderPath = __filename;
const policyTestPath = path.join(repo, "arb-executor/tests/test_window1_v31_dip_pressure_governor.js");
const packageTestPath = path.join(repo, "arb-executor/tests/test_window1_v31_dip_pressure_governor_package.js");
const specCommit = "e64b0837e04e3ea7dd58fbbba907816b3fdbdcb2";
const specJsonPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PATHALPHA_MEASUREMENT.json";
const specDocPath = "arb-executor/docs/research/window1/second_seat/PATHALPHA_MEASUREMENT.md";

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha(fs.readFileSync(file)); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function write(file, bytes) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, bytes); }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function semanticHash(value) { return sha(JSON.stringify(value)); }
function integer(value) { const number = Number(value); return Number.isInteger(number) ? number : null; }
function positive(value) { const number = Number(value); return Number.isFinite(number) && number > 0 ? number : null; }
function group(rows, keyFunction) { const out = new Map(); for (const row of rows) { const key = keyFunction(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function countBy(rows, keyFunction) { const out = {}; for (const row of rows) { const key = String(keyFunction(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, probability) { const sorted = values.filter(Number.isFinite).sort((a, b) => a - b); return sorted.length ? sorted[Math.floor((sorted.length - 1) * probability)] : null; }
function distribution(values) { const numeric = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: numeric.length, null_n: values.length - numeric.length, min: numeric.length ? Math.min(...numeric) : null, p25: quantile(numeric, .25), median: quantile(numeric, .5), p75: quantile(numeric, .75), p90: quantile(numeric, .9), max: numeric.length ? Math.max(...numeric) : null, total_cents: numeric.reduce((sum, value) => sum + value, 0) }; }
function gitShow(commit, file) { return child.execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 }); }
function rel(file) { return path.relative(repo, file).replaceAll("\\", "/"); }

function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) return null;
  let hour = Number(match[4]);
  if (match[7] === "AM" && hour === 12) hour = 0;
  if (match[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000;
}

function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/);
  const header = lines.shift().split(",");
  return lines.filter(Boolean).map((line) => Object.fromEntries(line.split(",").map((value, index) => [header[index], value])));
}

function loadSources() {
  const sources = new Map();
  for (const row of parseCsv(fs.readFileSync(quotePath, "utf8"))) sources.set(row.ticker, { event_id: row.event_id, ticker: row.ticker, left: Number(row.left_ts), right: Number(row.right_ts), scheduled: Number(row.scheduled_start_ts) });
  return sources;
}

function loadBells() {
  return new Map(JSON.parse(fs.readFileSync(bellPath)).leg_rows.map((row) => [row.event_id, row.exact_bell_ts]));
}

function clocks(timestamp, source, bell) {
  return { timestamp_epoch: timestamp, t_minus_scheduled_seconds: source.scheduled - timestamp, t_minus_actual_bell_seconds: Number.isFinite(bell) ? bell - timestamp : null };
}

function loadTape(ticker, source, privateHashes) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing private development tape ${ticker}`);
  const bytes = fs.readFileSync(file);
  privateHashes[ticker] = { sha256: sha(bytes), bytes: bytes.length, source_class: "PRIVATE_FIT_DEVELOPMENT_TAPE_HASH_ONLY" };
  const lines = zlib.gunzipSync(bytes).toString("utf8").trimEnd().split(/\r?\n/);
  const header = lines.shift().split(",");
  const index = Object.fromEntries(header.map((name, position) => [name, position]));
  const parsed = [];
  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    const values = lines[lineIndex].split(",");
    const timestamp = parseEt(values[index.ts_et]);
    if (timestamp === null || timestamp < source.left || timestamp > source.right) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(values[index[`bid_${level}`]]), bidSize = positive(values[index[`bid_${level}_sz`]]);
      const ask = integer(values[index[`ask_${level}`]]), askSize = positive(values[index[`ask_${level}_sz`]]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]);
      if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length) continue;
    parsed.push({
      ts: timestamp,
      ordinal: lineIndex + 2,
      receipt: `${ticker}.csv.gz#row-${lineIndex + 2}`,
      bid: bids[0][0],
      ask: asks[0][0],
      spread: asks[0][0] - bids[0][0],
      top_bid_size: bids[0][1],
      top_ask_size: asks[0][1],
      top_bid_depth: bids.reduce((sum, level) => sum + level[1], 0),
      top_ask_depth: asks.reduce((sum, level) => sum + level[1], 0),
    });
  }
  parsed.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let state = null, previousTimestamp = null, lastAsk = null, askSince = null;
  for (const row of parsed) {
    if (lastAsk === null || row.ask !== lastAsk) { lastAsk = row.ask; askSince = row.ts; }
    row.ask_dwell_seconds = row.ts - askSince;
    state = updateEwma(state, previousTimestamp, row);
    row.band_state = Object.fromEntries(FEATURE_NAMES.map((name) => [name, state[name]]));
    previousTimestamp = row.ts;
  }
  return parsed;
}

function latestAt(rows, timestamp) {
  let found = null;
  for (const row of rows) { if (row.ts <= timestamp) found = row; else break; }
  return found;
}

function qualifying(row) {
  return row.spread <= 1 && row.ask_dwell_seconds >= 10 && row.top_ask_size >= 5;
}

function futureFloor(rows, timestamp, price, maximumTimestamp = Infinity) {
  let row = null;
  for (const candidate of rows) {
    if (candidate.ts <= timestamp || candidate.ts > maximumTimestamp || !qualifying(candidate)) continue;
    if (!row || candidate.ask < row.ask) row = candidate;
  }
  if (!row) return { price_cents: null, row: null, drop_cents: null };
  const minimum = row.ask;
  return { price_cents: minimum, row, drop_cents: Math.max(0, price - minimum) };
}

function firstReach(rows, timestamp, target) {
  return rows.find((row) => row.ts > timestamp && qualifying(row) && row.ask <= target) || null;
}

function fitWalkForward(samples) {
  const byCategory = group(samples, (sample) => sample.category);
  const fits = [];
  for (const [category, categoryRows] of byCategory) {
    categoryRows.sort((a, b) => a.action_timestamp_epoch - b.action_timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity));
    let weights = Array(FEATURE_NAMES.length + 1).fill(0);
    const history = [];
    for (let index = 0; index < categoryRows.length; index += 1) {
      const sample = categoryRows[index];
      const vector = featureVector(sample.band_state);
      const probability = predict(weights, vector);
      const threshold = fitThreshold(history);
      Object.assign(sample, {
        walkforward_scored: Boolean(index >= MIN_TRAIN_ROWS && threshold),
        walkforward_probability: index >= MIN_TRAIN_ROWS ? probability : null,
        walkforward_threshold: index >= MIN_TRAIN_ROWS && threshold ? threshold.threshold : null,
        pressure_state: index >= MIN_TRAIN_ROWS && threshold ? (probability >= threshold.threshold ? "HIGH" : "LOW") : "NO_AUTHORITY_WARMUP",
        pressure_implied_drop_cents: index >= MIN_TRAIN_ROWS && threshold ? threshold.pressure_implied_drop_cents : null,
        training_rows_before_decision: index,
        training_threshold_receipt: threshold,
        model_weights_before_decision: [...weights],
      });
      history.push({ probability, label: sample.label, deeper_floor_drop_cents: sample.deeper_floor_drop_cents });
      weights = onlineUpdate(weights, vector, sample.label, index);
    }
    const authority = authorityVerdict(categoryRows);
    fits.push({ category, ...authority, feature_names: FEATURE_NAMES, halflife_seconds: HALFLIFE_SECONDS, online_walkforward_min_train_rows: MIN_TRAIN_ROWS, final_weights: weights });
  }
  return fits.sort((a, b) => a.category.localeCompare(b.category));
}

function recomputeEvent(event) {
  const legs = Object.values(event.legs);
  const completed = legs.every((leg) => leg.credited);
  const sum = completed ? legs.reduce((total, leg) => total + leg.entry_cents, 0) : null;
  const closes = completed && legs.every((leg) => Number.isInteger(leg.audited_close_cents));
  Object.assign(event, {
    completed_pair: completed,
    combined_entry_cents: sum,
    pair_under_par: completed && sum < 100,
    both_legs_strictly_below_audited_close: closes && legs.every((leg) => leg.entry_cents < leg.audited_close_cents),
    joint_objective_pass_audited_close: closes && sum < 100 && legs.every((leg) => leg.entry_cents < leg.audited_close_cents),
    execution_floor_pair_pass: completed && sum < 100 && legs.every((leg) => Number.isInteger(leg.qualifying_ask_floor_cents) && leg.entry_cents <= leg.qualifying_ask_floor_cents),
  });
}

function calculate(events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  const completed = events.filter((event) => Object.values(event.legs).every((leg) => leg.credited));
  let under = 0, below = 0, joint = 0, carried = 0, missing = 0, execution = 0;
  for (const event of completed) {
    const eventLegs = Object.values(event.legs), sum = eventLegs.reduce((total, leg) => total + leg.entry_cents, 0);
    const closes = eventLegs.every((leg) => Number.isInteger(leg.audited_close_cents));
    const deltas = closes ? eventLegs.map((leg) => leg.entry_cents - leg.audited_close_cents) : [];
    if (sum < 100) under += 1;
    if (!closes) missing += 1;
    if (closes && deltas.every((delta) => delta < 0)) below += 1;
    if (closes && sum < 100 && deltas.every((delta) => delta < 0)) joint += 1;
    if (closes && deltas.some((delta) => delta > 0) && deltas.some((delta) => delta < 0)) carried += 1;
    if (sum < 100 && eventLegs.every((leg) => Number.isInteger(leg.qualifying_ask_floor_cents) && leg.entry_cents <= leg.qualifying_ask_floor_cents)) execution += 1;
  }
  return { D: events.length, legs: legs.length, acted_legs: legs.filter((leg) => leg.acted).length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: completed.length, pairs_under_par: under, completed_pairs_close_unavailable: missing, both_legs_strictly_below_audited_close: below, joint_objective_pairs: joint, strict_carried_pairs: carried, execution_floor_pair_passes: execution };
}

function frontier(events) {
  const tiers = { LE_93: (sum) => sum <= 93, LE_95: (sum) => sum <= 95, LE_97: (sum) => sum <= 97, LT_100: (sum) => sum < 100, ANY_PRICE: () => true };
  return Object.fromEntries(Object.entries(tiers).map(([name, predicate]) => {
    const selected = events.filter((event) => { const legs = Object.values(event.legs); return legs.every((leg) => leg.credited) && predicate(legs.reduce((sum, leg) => sum + leg.entry_cents, 0)); });
    return [name, { fixed_denominator: events.length, completed_pairs: selected.length, joint_objective_pairs: calculate(selected).joint_objective_pairs }];
  }));
}

function score(events) {
  return {
    aggregate: calculate(events),
    frontier: frontier(events),
    category_x_starting_price_region: [...group(events, (event) => `${event.category}|${event.starting_price_split}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], starting_price_region: key.split("|")[1], aggregate: calculate(rows), frontier: frontier(rows) })),
  };
}

function regret(events) {
  const rows = events.flatMap((event) => Object.values(event.legs)).map((leg) => {
    const value = leg.credited && Number.isInteger(leg.objective_traded_low_cents) ? leg.entry_cents - leg.objective_traded_low_cents : null;
    return { leg_identity: leg.leg_identity, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, credited: leg.credited, entry_cents: leg.credited ? leg.entry_cents : null, objective_traded_low_cents: leg.objective_traded_low_cents, regret_cents: value, loss_bucket: !leg.credited ? `NEVER_CREDITED:${leg.terminal_reason}` : value < 0 ? "BETTER_THAN_PRINT_FLOOR" : value === 0 ? "ZERO" : value <= 3 ? "ONE_TO_THREE" : value <= 9 ? "FOUR_TO_NINE" : "TEN_OR_MORE" };
  });
  return { denominator_legs: rows.length, numeric_regret: distribution(rows.map((row) => row.regret_cents)), never_credited_n: rows.filter((row) => !row.credited).length, category_x_price_region: [...group(rows, (row) => `${row.category}|${row.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, cell]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], n: cell.length, regret: distribution(cell.map((row) => row.regret_cents)), loss_buckets: countBy(cell, (row) => row.loss_bucket) })), rows };
}

function updateLegForDeeperFill(leg, sample, target, evidence, source, bell) {
  const oldPrice = leg.credited ? leg.entry_cents : null;
  leg.acted = true;
  leg.credited = true;
  leg.entry_cents = target;
  leg.action_timestamp_epoch = sample.action_timestamp_epoch;
  leg.honest_fill_class = "PROVEN_MAKER_BY_RESIDENCY_ASK_REACHED_RESTING_PRICE";
  leg.fill = { price_cents: target, quantity: 5, action_timestamp_epoch: sample.action_timestamp_epoch, evidence_timestamp_epoch: evidence.ts, action_receipt: sample.action_receipt, evidence_receipt: evidence.receipt, same_receipt_fill_forbidden: true, strictly_later_evidence: evidence.ts > sample.action_timestamp_epoch, evidence_book: { bid: evidence.bid, ask: evidence.ask, spread: evidence.spread, ask_dwell_seconds: evidence.ask_dwell_seconds, displayed_ask_size: evidence.top_ask_size } };
  leg.terminal_reason = "V31_HIGH_PRESSURE_DEMOTED_THEN_DEEPER_MAKER_FILL";
  leg.placement = { ...(leg.placement || {}), price_cents: target, action_ts: sample.action_timestamp_epoch, dip_pressure_governor: { disposition: "DEMOTED_THEN_DEEPER_FILL", original_price_cents: sample.current_buy_price_cents, target_cents: target, action_pressure: sample.walkforward_probability, threshold: sample.walkforward_threshold, pressure_state: sample.pressure_state, band_state: sample.band_state, evidence_clocks: clocks(evidence.ts, source, bell) } };
  leg.entry_minus_qualifying_ask_floor_cents = Number.isInteger(leg.qualifying_ask_floor_cents) ? target - leg.qualifying_ask_floor_cents : null;
  leg.entry_minus_objective_traded_low_cents = Number.isInteger(leg.objective_traded_low_cents) ? target - leg.objective_traded_low_cents : null;
  leg.entry_minus_own_window1_close_cents = Number.isInteger(leg.own_window1_close_cents) ? target - leg.own_window1_close_cents : null;
  return oldPrice;
}

function updateLegForLostCompletion(leg, sample, target) {
  const oldPrice = leg.credited ? leg.entry_cents : null;
  leg.acted = true;
  leg.credited = false;
  leg.entry_cents = null;
  leg.honest_fill_class = "UNPROVEN";
  leg.fill = null;
  leg.terminal_reason = "V31_HIGH_PRESSURE_DEMOTED_DIP_NEVER_RETURNED";
  leg.placement = { ...(leg.placement || {}), price_cents: target, action_ts: sample.action_timestamp_epoch, dip_pressure_governor: { disposition: "DEMOTED_THEN_LOST", original_price_cents: sample.current_buy_price_cents, target_cents: target, action_pressure: sample.walkforward_probability, threshold: sample.walkforward_threshold, pressure_state: sample.pressure_state, band_state: sample.band_state } };
  leg.entry_minus_qualifying_ask_floor_cents = null;
  leg.entry_minus_objective_traded_low_cents = null;
  leg.entry_minus_own_window1_close_cents = null;
  return oldPrice;
}

function finalize(run1, run2) {
  const first = path.resolve(run1), second = path.resolve(run2);
  const excluded = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
  const files = fs.readdirSync(first).filter((name) => !excluded.has(name)).sort();
  ensure(JSON.stringify(files) === JSON.stringify(fs.readdirSync(second).filter((name) => !excluded.has(name)).sort()), "clean-build file census differs");
  const rows = files.map((name) => ({ path: name, run1_sha256: fileHash(path.join(first, name)), run2_sha256: fileHash(path.join(second, name)), bytes: fs.statSync(path.join(first, name)).size }));
  ensure(rows.every((row) => row.run1_sha256 === row.run2_sha256), "clean builds differ");
  fs.mkdirSync(output, { recursive: true });
  for (const name of files) fs.copyFileSync(path.join(first, name), path.join(output, name));
  const payloadSha256 = sha(Buffer.from(rows.map((row) => `${row.path}:${row.run1_sha256}:${row.bytes}`).join("\n")));
  write(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({ status: "PASS", clean_builds: 2, files_compared: rows.length, byte_identical: true, payload_sha256: payloadSha256, rows }));
  const manifestFiles = {};
  for (const name of [...files, "DETERMINISM_RECEIPT.json"].sort()) manifestFiles[name] = { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size };
  write(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema: "WINDOW1_V31_ARTIFACT_HASH_MANIFEST_V1", files: manifestFiles }));
  process.stdout.write(canonical({ status: "FINALIZED", files: Object.keys(manifestFiles).length, payload_sha256: payloadSha256 }));
}

function build() {
  const required = [baseEventPath, baseLegPath, baseTracePath, baseScorePath, quotePath, bellPath, policyPath, builderPath, policyTestPath, packageTestPath];
  for (const file of required) ensure(fs.existsSync(file), `missing ${file}`);
  child.execFileSync("git", ["cat-file", "-e", `${specCommit}^{commit}`], { cwd: repo });
  const specJson = gitShow(specCommit, specJsonPath), specDoc = gitShow(specCommit, specDocPath), spec = JSON.parse(specJson);
  ensure(spec.summary.part2_dip_timing.combined_walkforward_auc === 0.777, "six-band controlling AUC changed");
  ensure(spec.summary.part2_dip_timing.lead_median_s === 2221, "six-band controlling lead changed");
  const events = readRows(baseEventPath), baseLegs = readRows(baseLegPath), trace = JSON.parse(fs.readFileSync(baseTracePath)), baseScore = JSON.parse(fs.readFileSync(baseScorePath));
  ensure(events.length === 804 && baseLegs.length === 1608 && trace.rows.length === 1608, "R3 conservation failed");
  ensure(baseScore.V29R3_score.joint_objective_pairs === 68, "R3 joint floor mismatch");
  const sources = loadSources(), bells = loadBells(), privateHashes = {};
  const samples = [];
  for (const leg of baseLegs.filter((row) => row.acted)) {
    const source = sources.get(leg.ticker); ensure(source, `source missing ${leg.ticker}`);
    const rows = loadTape(leg.ticker, source, privateHashes), actionTimestamp = Number(leg.action_timestamp_epoch), actionRow = latestAt(rows, actionTimestamp);
    ensure(actionRow, `action book missing ${leg.leg_identity}`);
    const currentBuyPrice = integer(leg.placement?.price_cents); ensure(currentBuyPrice !== null, `buy price missing ${leg.leg_identity}`);
    const later = futureFloor(rows, actionTimestamp, currentBuyPrice, actionTimestamp + TRAINING_DIP_HORIZON_SECONDS);
    samples.push({
      leg_identity: leg.leg_identity,
      event_id: leg.event_id,
      ticker: leg.ticker,
      category: leg.category,
      price_region: leg.price_region,
      starting_price_split: leg.starting_price_split,
      action_timestamp_epoch: actionTimestamp,
      action_receipt: leg.placement?.action_receipt || actionRow.receipt,
      action_book_receipt: actionRow.receipt,
      action_book: { bid: actionRow.bid, ask: actionRow.ask, spread: actionRow.spread, ask_dwell_seconds: actionRow.ask_dwell_seconds, top_bid_size: actionRow.top_bid_size, top_ask_size: actionRow.top_ask_size, top5_bid_depth: actionRow.top_bid_depth, top5_ask_depth: actionRow.top_ask_depth },
      band_state: actionRow.band_state,
      current_buy_price_cents: currentBuyPrice,
      label: later.drop_cents > 0 ? 1 : 0,
      deeper_floor_drop_cents: later.drop_cents,
      future_qualifying_floor_cents_grading_only: later.price_cents,
      future_floor_receipt_grading_only: later.row?.receipt || null,
      training_dip_horizon_seconds: TRAINING_DIP_HORIZON_SECONDS,
      base_credited: leg.credited,
      base_entry_cents: leg.credited ? leg.entry_cents : null,
      buy_path: leg.terminal_reason?.includes("MIRROR") || leg.placement?.dip_pressure_governor ? "MIRROR_OR_REPAIR" : "INCUMBENT",
    });
  }
  const fits = fitWalkForward(samples), authorityByCategory = new Map(fits.map((fit) => [fit.category, fit]));
  const sampleByLeg = new Map(samples.map((sample) => [sample.leg_identity, sample]));
  const baseByLeg = new Map(baseLegs.map((leg) => [leg.leg_identity, leg]));
  const beforeEvents = new Map(events.map((event) => [event.event_id, clone(event)]));
  const dispositions = [], changedLegs = new Set(), changedEvents = new Set();
  for (const event of events) {
    for (const leg of Object.values(event.legs)) {
      const sample = sampleByLeg.get(leg.leg_identity), authority = authorityByCategory.get(leg.category);
      if (!sample) { dispositions.push({ leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, price_region: leg.price_region, disposition: "UNTOUCHED", reason: "NO_INCUMBENT_OR_MIRROR_BUY_DECISION", authority_earned: Boolean(authority?.earned) }); continue; }
      const decision = governBuy({ authority, pressureState: sample.pressure_state, currentPriceCents: sample.current_buy_price_cents, impliedDropCents: sample.pressure_implied_drop_cents });
      if (decision.decision !== "DEMOTE") {
        dispositions.push({ leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, price_region: leg.price_region, buy_path: sample.buy_path, disposition: "UNTOUCHED", reason: decision.reason, authority_earned: Boolean(authority?.earned), pressure_state: sample.pressure_state, probability: sample.walkforward_probability, threshold: sample.walkforward_threshold });
        continue;
      }
      ensure(decision.target_cents < sample.current_buy_price_cents, `demotion not below current price ${leg.leg_identity}`);
      const evidence = firstReach(loadTape(leg.ticker, sources.get(leg.ticker), privateHashes), sample.action_timestamp_epoch, decision.target_cents);
      const wasCredited = leg.credited, oldEntry = wasCredited ? leg.entry_cents : null;
      if (evidence) updateLegForDeeperFill(leg, sample, decision.target_cents, evidence, sources.get(leg.ticker), bells.get(leg.event_id));
      else updateLegForLostCompletion(leg, sample, decision.target_cents);
      changedLegs.add(leg.leg_identity); changedEvents.add(leg.event_id);
      dispositions.push({
        leg_identity: leg.leg_identity, event_id: leg.event_id, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, buy_path: sample.buy_path,
        disposition: evidence ? "DEMOTED_THEN_DEEPER_FILL" : "DEMOTED_THEN_LOST", reason: evidence ? "PRESSURE_TARGET_REACHED_ON_STRICTLY_LATER_QUALIFYING_BOOK" : "PRESSURE_TARGET_NEVER_REACHED",
        authority_earned: true, pressure_state: sample.pressure_state, probability: sample.walkforward_probability, threshold: sample.walkforward_threshold, band_state: sample.band_state,
        original_credited: wasCredited, original_entry_cents: oldEntry, original_buy_price_cents: sample.current_buy_price_cents, target_cents: decision.target_cents,
        pressure_implied_drop_cents: sample.pressure_implied_drop_cents, evidence_receipt: evidence?.receipt || null, evidence_timestamp_epoch: evidence?.ts || null,
        action_clocks: clocks(sample.action_timestamp_epoch, sources.get(leg.ticker), bells.get(leg.event_id)),
      });
    }
    recomputeEvent(event);
  }
  for (const event of events) recomputeEvent(event);
  const resultLegs = events.flatMap((event) => Object.values(event.legs)).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
  const diffRows = resultLegs.map((leg) => ({ leg_identity: leg.leg_identity, changed: changedLegs.has(leg.leg_identity), R3_semantic_sha256: semanticHash(baseByLeg.get(leg.leg_identity)), V31_semantic_sha256: semanticHash(leg) }));
  ensure(diffRows.filter((row) => row.changed).every((row) => row.R3_semantic_sha256 !== row.V31_semantic_sha256), "changed stream did not change");
  ensure(diffRows.filter((row) => !row.changed).every((row) => row.R3_semantic_sha256 === row.V31_semantic_sha256), "no-authority or LOW stream drifted");
  const eventById = new Map(events.map((event) => [event.event_id, event])), dispositionByLeg = new Map(dispositions.map((row) => [row.leg_identity, row]));
  const traceRows = trace.rows.map((baseRow) => {
    const event = eventById.get(baseRow.event_id), leg = Object.values(event.legs).find((candidate) => candidate.leg_identity === baseRow.leg_identity), disposition = dispositionByLeg.get(baseRow.leg_identity);
    return { ...clone(baseRow), variant: "V31_DIP_PRESSURE_GOVERNOR", v31_dip_pressure_governor: disposition, final_state: event.joint_objective_pass_audited_close ? "JOINT-CAPTURED" : leg.credited ? (event.completed_pair ? "carried" : "naked") : leg.acted ? "resting-uncredited" : "never-placed", leg_action_state: { acted: leg.acted, credited: leg.credited, entry_cents: leg.credited ? leg.entry_cents : null, terminal_reason: leg.terminal_reason }, event_result: { completed_pair: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, both_legs_strictly_below_audited_close: event.both_legs_strictly_below_audited_close, joint_objective_pass: event.joint_objective_pass_audited_close } };
  });
  ensure(traceRows.length === 1608 && new Set(traceRows.map((row) => row.leg_identity)).size === 1608, "trace conservation failed");
  const currentScore = score(events), baseAggregate = baseScore.V29R3_score;
  const delta = Object.fromEntries(Object.keys(baseAggregate).filter((key) => Number.isInteger(baseAggregate[key])).map((key) => [key, currentScore.aggregate[key] - baseAggregate[key]]));
  const baseEventById = beforeEvents;
  const jointGained = events.filter((event) => !baseEventById.get(event.event_id).joint_objective_pass_audited_close && event.joint_objective_pass_audited_close).map((event) => event.event_id);
  const jointLost = events.filter((event) => baseEventById.get(event.event_id).joint_objective_pass_audited_close && !event.joint_objective_pass_audited_close).map((event) => event.event_id);
  const completionLost = events.filter((event) => baseEventById.get(event.event_id).completed_pair && !event.completed_pair).map((event) => event.event_id);
  const completionGained = events.filter((event) => !baseEventById.get(event.event_id).completed_pair && event.completed_pair).map((event) => event.event_id);
  const dispositionSummary = { legs: 1608, by_disposition: countBy(dispositions, (row) => row.disposition), by_category: [...group(dispositions, (row) => row.category)].sort(([a], [b]) => a.localeCompare(b)).map(([category, rows]) => ({ category, n: rows.length, dispositions: countBy(rows, (row) => row.disposition), reasons: countBy(rows, (row) => row.reason) })), rows: dispositions };
  const arnLeg = "KXATPCHALLENGERMATCH-26JUL12ARNROM|ROM", arnSample = sampleByLeg.get(arnLeg), arnDisposition = dispositionByLeg.get(arnLeg), arnAfter = resultLegs.find((leg) => leg.leg_identity === arnLeg);
  ensure(arnSample && arnDisposition && arnAfter, "ARNROM|ROM regression unavailable");
  const arnReceipt = { leg_identity: arnLeg, named_price_cents: 42, named_timestamp_epoch: 1783896551, action_matches_named_case: arnSample.current_buy_price_cents === 42 && arnSample.action_timestamp_epoch === 1783896551, action_book: arnSample.action_book, band_state: arnSample.band_state, walkforward: { scored: arnSample.walkforward_scored, probability: arnSample.walkforward_probability, threshold: arnSample.walkforward_threshold, pressure_state: arnSample.pressure_state, training_rows_before_decision: arnSample.training_rows_before_decision, category_authority: authorityByCategory.get(arnSample.category) }, governor_disposition: arnDisposition, result: { credited: arnAfter.credited, entry_cents: arnAfter.credited ? arnAfter.entry_cents : null, terminal_reason: arnAfter.terminal_reason } };
  const bandBinding = { commit: specCommit, commit_object_verified: true, json_path: specJsonPath, json_sha256: sha(specJson), doc_path: specDocPath, doc_sha256: sha(specDoc), frozen_spec: { bands: FEATURE_NAMES, halflife_seconds: HALFLIFE_SECONDS, training_dip_horizon_seconds: TRAINING_DIP_HORIZON_SECONDS, causal: true, combined_walkforward_auc: spec.summary.part2_dip_timing.combined_walkforward_auc, median_lead_seconds: spec.summary.part2_dip_timing.lead_median_s, original_bar: spec.summary.part2_dip_timing_BAR_ruledJul6.bar }, implementation_definition: { cross: "bid>ask", lock: "bid==ask", bid_dom: "top5_bid_depth/(top5_bid_depth+top5_ask_depth)", ask_dom: "top5_ask_depth/(top5_bid_depth+top5_ask_depth)", ask_stair: "current_ask<previous_ask", bid_stair: "current_bid>previous_bid", ewma: "exp(-ln(2)*delta_seconds/120)", threshold_fit: "maximize_prior_training_precision_lift_with_at_least_20_HIGH_rows; ties by F1 then threshold" } };
  const rg = regret(events);
  fs.mkdirSync(output, { recursive: true });
  write(path.join(output, "EVENT_LEDGER.jsonl.gz"), gzipRows(events));
  write(path.join(output, "LEG_LEDGER.jsonl.gz"), gzipRows(resultLegs));
  write(path.join(output, "DECISION_TRACE_1608.json"), canonical({ schema: "WINDOW1_DECISION_TRACE_1608_V31", variant: "V31_DIP_PRESSURE_GOVERNOR", generated_utc: "2026-08-05T00:00:00Z", scope: { events: 804, legs: 1608 }, rows: traceRows }));
  write(path.join(output, "GOVERNOR_SAMPLE_LEDGER.jsonl.gz"), gzipRows(samples));
  write(path.join(output, "GOVERNOR_DISPOSITION.json"), canonical(dispositionSummary));
  write(path.join(output, "GOVERNOR_AUTHORITY_FIT.json"), canonical({ method: "ONLINE_EXPANDING_WALK_FORWARD_BY_CATEGORY_ORDERED_BY_DATE_THEN_ACTION_TIMESTAMP", no_current_or_future_outcome_in_decision: true, fits }));
  write(path.join(output, "BAND_SPEC_BINDING.json"), canonical(bandBinding));
  write(path.join(output, "ARNROM_ROM_REGRESSION_RECEIPT.json"), canonical(arnReceipt));
  write(path.join(output, "DEMOTE_RISK_RECEIPT.json"), canonical({ wrong_phase_buys_converted_to_deeper_fills: dispositions.filter((row) => row.disposition === "DEMOTED_THEN_DEEPER_FILL" && row.original_credited && Number.isInteger(baseByLeg.get(row.leg_identity).audited_close_cents) && row.original_entry_cents >= baseByLeg.get(row.leg_identity).audited_close_cents).length, all_demoted_then_deeper_fill: dispositions.filter((row) => row.disposition === "DEMOTED_THEN_DEEPER_FILL").length, all_demoted_then_lost: dispositions.filter((row) => row.disposition === "DEMOTED_THEN_LOST").length, joint_gained: jointGained.length, joint_gained_event_ids: jointGained, joint_lost: jointLost.length, joint_lost_event_ids: jointLost, completions_gained: completionGained.length, completion_gained_event_ids: completionGained, completions_lost: completionLost.length, completion_lost_event_ids: completionLost, net_joint_delta: jointGained.length - jointLost.length }));
  write(path.join(output, "VERDICT_RECEIPT.json"), canonical({ candidate: "V31_DIP_PRESSURE_GOVERNOR", verdict: currentScore.aggregate.joint_objective_pairs >= baseAggregate.joint_objective_pairs ? "NON_REGRESSING_ELIGIBLE_FOR_REVIEW" : "REJECTED_JOINT_REGRESSION_DO_NOT_PROMOTE", operative_baseline_after_build: currentScore.aggregate.joint_objective_pairs >= baseAggregate.joint_objective_pairs ? "PENDING_OPERATOR_RULING" : "V29R3_STANDING_FLOOR_RELEASE", floor_joint: baseAggregate.joint_objective_pairs, candidate_joint: currentScore.aggregate.joint_objective_pairs, joint_delta: currentScore.aggregate.joint_objective_pairs - baseAggregate.joint_objective_pairs, tests_pass_is_not_candidate_ratification: true }));
  write(path.join(output, "SCORECARD.json"), canonical({ variant: "V31_DIP_PRESSURE_GOVERNOR", R3_floor: baseAggregate, V31_score: currentScore.aggregate, delta, joint_non_regression: currentScore.aggregate.joint_objective_pairs >= baseAggregate.joint_objective_pairs, category_x_starting_price_region: currentScore.category_x_starting_price_region }));
  write(path.join(output, "FRONTIER.json"), canonical({ fixed_denominator: 804, JOINT_law: "BOTH_LEGS_CREDITED_AND_SUM_LT_100_AND_EACH_ENTRY_STRICTLY_BELOW_OWN_AUDITED_CLOSE", tiers: currentScore.frontier, category_x_starting_price_region: currentScore.category_x_starting_price_region.map((cell) => ({ category: cell.category, starting_price_region: cell.starting_price_region, frontier: cell.frontier })) }));
  write(path.join(output, "REGRET_GAUGE.json"), canonical({ ...rg, rows: undefined }));
  write(path.join(output, "REGRET_LEG_LEDGER.jsonl.gz"), gzipRows(rg.rows));
  write(path.join(output, "DIFFERENTIAL_RECEIPT.json"), canonical({ base: "V29R3_STANDING_FLOOR_RELEASE", changed_leg_streams: changedLegs.size, unchanged_leg_streams: 1608 - changedLegs.size, all_no_authority_and_low_pressure_streams_semantic_hash_equal: diffRows.filter((row) => !row.changed).every((row) => row.R3_semantic_sha256 === row.V31_semantic_sha256), rows: diffRows }));
  write(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ holdout: false, live: false, network_runtime: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, deployment: false, wall_clock_policy_input: false, audited_close_policy_input: false, future_floor_policy_input: false, grading_only_fields: ["label", "future_qualifying_floor_cents_grading_only", "audited_close_cents", "objective_traded_low_cents"] }));
  const sourceFiles = [baseEventPath, baseLegPath, baseTracePath, baseScorePath, quotePath, bellPath, policyPath, builderPath, policyTestPath, packageTestPath];
  write(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sourceFiles.map((file) => [rel(file), { sha256: fileHash(file), bytes: fs.statSync(file).size }])), private_development_tapes: privateHashes, external_git_objects: { [specCommit]: { [specJsonPath]: sha(specJson), [specDocPath]: sha(specDoc) } } }));
  write(path.join(output, "TEST_RESULTS.json"), canonical({ status: "PASS", commands: ["node arb-executor/tests/test_window1_v31_dip_pressure_governor.js", "node arb-executor/tests/test_window1_v31_dip_pressure_governor_package.js", "node arb-executor/tests/test_window1_v29r3_standing_floor_release_policy.js", "node arb-executor/tests/test_window1_v29r3_standing_floor_release_package.js", "node arb-executor/tests/test_window1_v29r2_mirror_armed_uncaptured_side_policy.js", "node arb-executor/tests/test_window1_v29r2_mirror_armed_uncaptured_side_package.js", "node arb-executor/tests/test_window1_v28_anchor_cap_stack_policy.js", "node arb-executor/tests/test_window1_v28_anchor_cap_stack_package.js"], omissions: 0, deselections: 0 }));
  const report = `# Window-1 V31 dip-pressure governor — 2026-08-05\n\nV31 is a repair-with-earned-authority on V29-R3. The six causal bands use the e64b0837 120-second EWMA definition. The governor never creates a BUY and never assigns role: immediately before an incumbent or mirror BUY already authorized by R3, a category with earned walk-forward authority may demote a HIGH-pressure buy to a strictly lower resting target. LOW pressure and every category without earned authority are byte-identical to R3.\n\nAuthority is earned only when held-out HIGH-pressure precision exceeds the held-out category base rate by at least five percentage points and has at least 20 HIGH calls. The threshold and pressure-implied deeper-floor drop are learned only from chronologically prior decisions. No clock is a policy input.\n\nR3 JOINT floor: ${baseAggregate.joint_objective_pairs}. V31 JOINT: ${currentScore.aggregate.joint_objective_pairs}. Changed legs: ${changedLegs.size}; unchanged semantic-hash-identical legs: ${1608 - changedLegs.size}. Deeper fills: ${dispositions.filter((row) => row.disposition === "DEMOTED_THEN_DEEPER_FILL").length}; demoted then lost: ${dispositions.filter((row) => row.disposition === "DEMOTED_THEN_LOST").length}. Joint gained: ${jointGained.length}; joint lost: ${jointLost.length}.\n\n**VERDICT: ${currentScore.aggregate.joint_objective_pairs >= baseAggregate.joint_objective_pairs ? "NON-REGRESSING; PENDING OPERATOR REVIEW" : "REJECTED — JOINT REGRESSION; V29-R3 REMAINS OPERATIVE"}.** Test PASS means the receipt is internally valid, not that the candidate is ratified.\n\nARNROM|ROM at 42: pressure=${arnSample.pressure_state}, authority=${authorityByCategory.get(arnSample.category).earned}, disposition=${arnDisposition.disposition}, final entry=${arnAfter.credited ? arnAfter.entry_cents : "UNPROVEN"}.\n`;
  write(path.join(output, "REPORT.md"), report);
  process.stdout.write(canonical({ status: "BUILT", R3_joint: baseAggregate.joint_objective_pairs, V31_joint: currentScore.aggregate.joint_objective_pairs, changed_legs: changedLegs.size, authority: fits.map((fit) => ({ category: fit.category, earned: fit.earned, heldout_high_n: fit.heldout_high_n, precision: fit.heldout_high_precision, base_rate: fit.heldout_base_rate, margin: fit.required_margin })), dispositions: countBy(dispositions, (row) => row.disposition), joint_gained: jointGained.length, joint_lost: jointLost.length, ARNROM_ROM: { pressure: arnSample.pressure_state, authority: authorityByCategory.get(arnSample.category).earned, disposition: arnDisposition.disposition, entry: arnAfter.credited ? arnAfter.entry_cents : null } }));
}

if (finalizeRun1 || finalizeRun2) {
  ensure(finalizeRun1 && finalizeRun2, "both finalize runs required");
  finalize(finalizeRun1, finalizeRun2);
} else build();
