#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const os = require("os");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { execFileSync } = require("child_process");
const {
  lawfulCent,
  enumerateTrueDivots,
  classifyDeadSibling,
} = require("./window1_v53_dead_sibling_divot_census.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v53_05_dead_sibling_divot_census_20260821")));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const v36Root = path.resolve(arg("--v36-root", "C:/tmp/omi-v36-frozen-bfde"));
const spanPath = path.join(v36Root, ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/WINDOW1_SPAN_804.json");
const findingsPath = "arb-executor/docs/research/window1/FINDINGS_V53.md";
const truthCommit = "c0056976c446afcb4d9603796a2e06c068ee94d6";
const truthPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
const priorSweepCommit = "1e428ff108a94d778a6e949d09fcbabc5ce080d3";
const parentCommit = "077b8c807743a6d25c5e5182da3870391b18a513";
const packages = [
  {
    iteration: "V53_02",
    package: ".claude/window1_live_v4_replay/v53_02_understanding_bounds_stage1_20260820",
    traceName: "FULL_DECISION_TRACE_30.jsonl.gz",
    traceRole: "CANDIDATE_STATE_MACHINE_TRACE",
  },
  {
    iteration: "V53_03",
    package: ".claude/window1_live_v4_replay/v53_03_read_licensed_bound_stage1_20260820",
    traceName: "FULL_DECISION_TRACE_30.jsonl.gz",
    traceRole: "CANDIDATE_STATE_MACHINE_TRACE",
  },
  {
    iteration: "V53_04B",
    package: ".claude/window1_live_v4_replay/v53_04b_engine_selected_stage1_20260820",
    traceName: "V52L_COMPARATOR_TRACE_30.jsonl.gz",
    traceRole: "BYTE_EQUAL_A0_CONTROL_BEHAVIOR_TRACE_WITH_RISER_ARM_RECOMPUTED_FROM_VERIFIED_BOOK",
  },
];

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return shaBytes(fs.readFileSync(file)); }
function gitShow(commit, relative) { return execFileSync("git", ["show", `${commit}:${relative}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 }); }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function write(name, value) { fs.writeFileSync(path.join(output, name), typeof value === "string" || Buffer.isBuffer(value) ? value : canonical(value)); }
function cleanOutput(dir) {
  ensure(path.basename(dir).includes("v53_05"), `unsafe output ${dir}`);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
}
function writeManifest(dir) {
  const names = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  const files = Object.fromEntries(names.map((name) => {
    const file = path.join(dir, name), bytes = fs.statSync(file).size;
    ensure(bytes <= 50 * 1024 * 1024, `L22 file cap exceeded ${name} ${bytes}`);
    return [name, { sha256: fileHash(file), bytes }];
  }));
  fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files }));
}
function readGzipRows(file) {
  return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
}
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let hour = +m[4];
  if (m[7] === "AM" && hour === 12) hour = 0;
  if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/);
  const header = lines.shift().split(",");
  return { header, rows: lines.filter(Boolean).map((line) => line.split(",")) };
}
function loadTape(ticker, bounds) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing verified tape ${ticker}`);
  const bytes = fs.readFileSync(file), parsed = parseCsv(zlib.gunzipSync(bytes).toString("utf8"));
  const ix = Object.fromEntries(parsed.header.map((value, index) => [value, index]));
  const rows = [];
  for (let n = 0; n < parsed.rows.length; n += 1) {
    const values = parsed.rows[n], timestamp = parseEt(values[ix.ts_et]);
    if (!Number.isFinite(timestamp) || timestamp < bounds.left || timestamp > bounds.right) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(values[ix[`bid_${level}`]]), bidSize = positive(values[ix[`bid_${level}_sz`]]);
      const ask = integer(values[ix[`ask_${level}`]]), askSize = positive(values[ix[`ask_${level}_sz`]]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]);
      if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    rows.push({
      timestamp_epoch: timestamp,
      receipt: `${ticker}.csv.gz#row-${n + 2}`,
      bid_cents: bids[0][0],
      ask_cents: asks[0][0],
      last_traded_cents: integer(values[ix.last_trade]),
      spread_cents: asks[0][0] - bids[0][0],
      top_bid_size: bids[0][1],
      top_ask_size: asks[0][1],
    });
  }
  rows.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.receipt.localeCompare(b.receipt));
  return { rows, source: { path_class: "PRIVATE_VERIFIED_TICK_TAPE_HASH_ONLY", ticker, sha256: shaBytes(bytes), bytes: bytes.length, rows_in_replay_span: rows.length } };
}
function traceRowState(row) {
  return {
    event_id: row.event_id,
    leg_identity: row.leg_identity,
    price_region: row.price_region ?? null,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    observation: row.observation,
    read: row.read ? { state: row.read.state, quote_path_state: row.read.quote_path_state, pressure_state: row.read.pressure_state } : null,
    order_before_cents: row.order_before_cents,
    final_action: row.final_action,
    final_target_cents: row.final_target_cents,
    reason: row.reason,
    joint_license: row.joint_license ? { complete: row.joint_license.complete } : null,
  };
}
async function loadRelevantTrace(file, eventIds, expectedHash) {
  ensure(fs.existsSync(file), `missing custody trace ${file}`);
  const compressedHash = crypto.createHash("sha256"), input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  input.on("data", (chunk) => compressedHash.update(chunk));
  const lines = readline.createInterface({ input: input.pipe(zlib.createGunzip()), crlfDelay: Infinity });
  const byLeg = new Map();
  let rawRows = 0, selectedRows = 0;
  for await (const line of lines) {
    if (!line) continue;
    rawRows += 1;
    const match = line.match(/^\{"event_id":"([^"]+)"/);
    if (!match || !eventIds.has(match[1])) continue;
    const row = JSON.parse(line), slim = traceRowState(row);
    if (!byLeg.has(row.leg_identity)) byLeg.set(row.leg_identity, []);
    byLeg.get(row.leg_identity).push(slim);
    selectedRows += 1;
  }
  for (const rows of byLeg.values()) rows.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.receipt.localeCompare(b.receipt));
  const actualHash = compressedHash.digest("hex");
  ensure(actualHash === expectedHash, `custody hash mismatch ${file}`);
  return { byLeg, receipt: { custody_location: file.replaceAll("\\", "/"), sha256: actualHash, bytes: fs.statSync(file).size, raw_rows: rawRows, selected_rows: selectedRows } };
}
async function loadPrints(tickerBounds) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), "missing private canonical prints");
  const byTicker = new Map([...tickerBounds].map(([ticker]) => [ticker, []]));
  const seen = new Map([...tickerBounds].map(([ticker]) => [ticker, new Set()]));
  const wanted = new Set(tickerBounds.keys()), digest = crypto.createHash("sha256");
  const input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  input.on("data", (chunk) => digest.update(chunk));
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let rawRows = 0, selectedRows = 0, duplicateIds = 0;
  for await (const line of lines) {
    if (!line) continue;
    rawRows += 1;
    const match = line.match(/"ticker":"([^"]+)"/);
    if (!match || !wanted.has(match[1])) continue;
    const row = JSON.parse(line), bounds = tickerBounds.get(row.ticker);
    if (row.true_print !== true) continue;
    const timestamp = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(timestamp) || timestamp < bounds.left || timestamp > bounds.right) continue;
    if (!row.trade_id || seen.get(row.ticker).has(row.trade_id)) { duplicateIds += 1; continue; }
    seen.get(row.ticker).add(row.trade_id);
    byTicker.get(row.ticker).push({ timestamp_epoch: timestamp, receipt: row.receipt_id, trade_id: row.trade_id, price_cents: integer(row.price_cents), size: positive(row.size), taker_side: row.taker_side, taker_book_side: row.taker_book_side });
    selectedRows += 1;
  }
  for (const rows of byTicker.values()) rows.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
  return { byTicker, receipt: { path_class: "PRIVATE_CANONICAL_TRUE_PRINTS_HASH_ONLY", sha256: digest.digest("hex"), bytes: fs.statSync(file).size, raw_rows: rawRows, selected_unique_rows: selectedRows, duplicate_trade_ids_rejected: duplicateIds } };
}
function deadSiblingRows(packagePath, iteration) {
  const perGame = readJson(path.join(repo, packagePath, "PER_GAME_L1_L8.json")).rows;
  const market = new Map(readGzipRows(path.join(repo, packagePath, "MARKET_EVENT_LEDGER_30.jsonl.gz")).map((row) => [row.event_id, row]));
  const dead = [], exclusions = [];
  for (const row of perGame) {
    const credits = Object.entries(row.L7_CREDIT.why);
    const credited = credits.filter(([, value]) => value.credited === true), uncredited = credits.filter(([, value]) => value.credited !== true);
    if (credited.length === 1 && uncredited.length === 1) {
      const [deadIdentity] = uncredited[0], [creditedIdentity, creditedView] = credited[0], event = market.get(row.event_id);
      const deadLegId = deadIdentity.split("|").at(-1), creditedLegId = creditedIdentity.split("|").at(-1);
      ensure(event?.legs?.[creditedLegId]?.credited === true, `market ledger disagrees ${iteration} ${row.event_id}`);
      dead.push({
        run_instance_id: `${iteration}|${deadIdentity}`,
        iteration,
        event_id: row.event_id,
        category: row.category,
        dead_leg_identity: deadIdentity,
        dead_leg_id: deadLegId,
        credited_sibling_identity: creditedIdentity,
        credited_sibling_leg_id: creditedLegId,
        sibling_credit: {
          entry_cents: creditedView.entry_cents,
          fill_timestamp_epoch: event.legs[creditedLegId].fill_timestamp_epoch,
          fill_class: event.legs[creditedLegId].fill_class,
        },
      });
    } else if (!row.L8_OUTCOME.candidate.completed) {
      exclusions.push({ iteration, event_id: row.event_id, credited_legs: credited.length, uncredited_legs: uncredited.length, reason: "NOT_A_SINGLE_CREDITED_PAIR" });
    }
  }
  return { dead, exclusions, eventRows: perGame };
}
function a0ArmFunction(books) {
  let priorAsk = null, firstArm = null;
  const visits = [];
  for (const row of books) {
    if (row.ask_cents !== priorAsk) {
      visits.push({ timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, ask_cents: row.ask_cents });
      while (visits.length && visits[0].timestamp_epoch < row.timestamp_epoch - 300) visits.shift();
      const matching = visits.filter((visit) => visit.ask_cents === row.ask_cents);
      if (!firstArm && matching.length >= 2) firstArm = { armed: true, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, ask_cents: row.ask_cents, visits: matching.length, law: "A0_CONTROL_PROXY_SECOND_VISIT_OBSERVATIONAL_ONLY" };
    }
    priorAsk = row.ask_cents;
  }
  return (timestampEpoch) => firstArm && firstArm.timestamp_epoch < timestampEpoch ? firstArm : { armed: false, law: "A0_CONTROL_PROXY_SECOND_VISIT_OBSERVATIONAL_ONLY" };
}
function verifyTraceAgainstTape(traceRows, tapeRows, legIdentity) {
  const tape = new Map(tapeRows.map((row) => [row.receipt, row]));
  let compared = 0;
  for (const row of traceRows) {
    const raw = tape.get(row.receipt);
    ensure(raw, `trace receipt absent from tape ${legIdentity} ${row.receipt}`);
    ensure(raw.timestamp_epoch === row.timestamp_epoch
      && raw.bid_cents === row.observation.bid
      && raw.ask_cents === row.observation.ask
      && raw.last_traded_cents === row.observation.last_traded
      && raw.spread_cents === row.observation.spread,
    `trace/tape observation mismatch ${legIdentity} ${row.receipt}`);
    compared += 1;
  }
  return compared;
}
function rollup(rows) {
  const classes = ["DIVOTS_EXISTED_REST_ELSEWHERE", "ZERO_TRUE_DIVOTS", "DIVOTS_EXISTED_SLIDE_WOULD_NOT_TRADE"];
  const totals = Object.fromEntries(classes.map((name) => [name, rows.filter((row) => row.classification === name).length]));
  const byCategory = {};
  for (const category of [...new Set(rows.map((row) => row.category))].sort()) {
    const subset = rows.filter((row) => row.category === category);
    byCategory[category] = { total: subset.length, ...Object.fromEntries(classes.map((name) => [name, subset.filter((row) => row.classification === name).length])) };
  }
  const winner = classes.slice().sort((a, b) => totals[b] - totals[a] || a.localeCompare(b))[0];
  const strictMajority = totals[winner] > rows.length / 2 ? winner : null;
  return { dead_sibling_run_instances: rows.length, class_totals: totals, by_category: byCategory, strict_majority: strictMajority, strict_majority_count: strictMajority ? totals[strictMajority] : 0 };
}

async function main() {
  cleanOutput(output);
  ensure(fs.existsSync(spanPath), `missing frozen span ${spanPath}`);
  const implementationCommit = execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim();
  const findings = fs.readFileSync(path.join(repo, findingsPath), "utf8");
  for (const id of ["F-V53-028", "F-V53-033", "F-V53-034", "F-V53-035"]) ensure(findings.includes(id), `missing filed finding ${id}`);
  const spansBytes = fs.readFileSync(spanPath), spans = JSON.parse(spansBytes).rows, spanByEvent = new Map(spans.map((row) => [row.event_id, row]));
  ensure(spans.length === 804, "frozen stage span must contain 804 events");
  const truthBytes = gitShow(truthCommit, truthPath), truth = JSON.parse(truthBytes), truthByEvent = new Map(truth.rows.map((row) => [row.event_id, row]));
  const allDead = [], allExclusions = [], packageInputs = [];
  for (const spec of packages) {
    const packagePath = path.join(repo, spec.package), manifest = readJson(path.join(packagePath, "EXTERNAL_CUSTODY_MANIFEST.json"));
    const artifact = manifest.artifacts.find((row) => row.path.endsWith(`/${spec.traceName}`));
    ensure(artifact, `missing custody trace declaration ${spec.iteration} ${spec.traceName}`);
    const found = deadSiblingRows(packagePath, spec.iteration);
    allDead.push(...found.dead.map((row) => ({ ...row, trace_spec: spec })));
    allExclusions.push(...found.exclusions);
    packageInputs.push({ iteration: spec.iteration, package: spec.package, trace_role: spec.traceRole, trace: artifact, dead_siblings: found.dead.length, non_single_uncompleted_exclusions: found.exclusions.length });
  }
  ensure(packageInputs.find((row) => row.iteration === "V53_04B").dead_siblings === 7, "V53-04B seven dead-sibling pattern did not reproduce");
  const tickerBounds = new Map();
  for (const dead of allDead) {
    const span = spanByEvent.get(dead.event_id);
    ensure(span, `missing replay span ${dead.event_id}`);
    for (const leg of span.per_leg) tickerBounds.set(leg.ticker, { left: span.w1_left_epoch, right: span.w1_right_epoch });
  }
  const printLoad = await loadPrints(tickerBounds);
  const rows = [], tapeSources = {}, traceSources = [];
  for (const spec of packages) {
    const packageInput = packageInputs.find((row) => row.iteration === spec.iteration), eventIds = new Set(allDead.filter((row) => row.iteration === spec.iteration).map((row) => row.event_id));
    const trace = await loadRelevantTrace(packageInput.trace.custody_location, eventIds, packageInput.trace.sha256);
    traceSources.push({ iteration: spec.iteration, role: spec.traceRole, ...trace.receipt });
    for (const dead of allDead.filter((row) => row.iteration === spec.iteration)) {
      const span = spanByEvent.get(dead.event_id), spanLegById = new Map(span.per_leg.map((row) => [row.leg_identity.split("|").at(-1), row]));
      const deadMeta = spanLegById.get(dead.dead_leg_id), siblingMeta = spanLegById.get(dead.credited_sibling_leg_id);
      ensure(deadMeta && siblingMeta, `span leg binding failed ${dead.run_instance_id}`);
      const deadTape = loadTape(deadMeta.ticker, { left: span.w1_left_epoch, right: span.w1_right_epoch });
      const siblingTape = loadTape(siblingMeta.ticker, { left: span.w1_left_epoch, right: span.w1_right_epoch });
      tapeSources[deadMeta.ticker] = deadTape.source; tapeSources[siblingMeta.ticker] = siblingTape.source;
      const deadTrace = trace.byLeg.get(dead.dead_leg_identity) || [], siblingTrace = trace.byLeg.get(dead.credited_sibling_identity) || [];
      ensure(deadTrace.length && siblingTrace.length, `dead event trace missing ${dead.run_instance_id}`);
      const traceTapeRowsVerified = verifyTraceAgainstTape(deadTrace, deadTape.rows, dead.dead_leg_identity)
        + verifyTraceAgainstTape(siblingTrace, siblingTape.rows, dead.credited_sibling_identity);
      const divots = enumerateTrueDivots({
        prints: printLoad.byTicker.get(deadMeta.ticker) || [],
        ownBooks: deadTape.rows,
        siblingBooks: siblingTape.rows,
        decisionRows: deadTrace,
        siblingCredit: dead.sibling_credit,
        observationalArmAt: spec.iteration === "V53_04B" ? a0ArmFunction(deadTape.rows) : () => ({ armed: null, law: "NOT_PRESENT_IN_VARIANT" }),
      });
      const classification = classifyDeadSibling(divots);
      rows.push({
        ...dead,
        trace_spec: undefined,
        ticker: deadMeta.ticker,
        sibling_ticker: siblingMeta.ticker,
        price_region: deadTrace.at(-1)?.price_region ?? null,
        replay_span: { left_epoch: span.w1_left_epoch, right_epoch: span.w1_right_epoch, precision_class: span.precision_class, edge_source_field: span.edge_source_field },
        truth_table_telemetry: (() => {
          const truthRow = truthByEvent.get(dead.event_id), index = truthRow?.legA === dead.dead_leg_id ? "A" : truthRow?.legB === dead.dead_leg_id ? "B" : null;
          return { verified_span: truthRow?.verified_span ?? null, own_w1_close_cents: index ? truthRow[`leg${index}_close_c`] : null };
        })(),
        trace_tape_rows_verified: traceTapeRowsVerified,
        true_divot_count: divots.length,
        classification,
        true_divots: divots,
      });
    }
  }
  rows.sort((a, b) => a.iteration.localeCompare(b.iteration) || a.event_id.localeCompare(b.event_id) || a.dead_leg_identity.localeCompare(b.dead_leg_identity));
  const summary = rollup(rows), unique = new Set(rows.map((row) => row.dead_leg_identity));
  const perIteration = Object.fromEntries(packages.map((spec) => {
    const subset = rows.filter((row) => row.iteration === spec.iteration);
    return [spec.iteration, rollup(subset)];
  }));
  const f24 = readJson(path.join(repo, packages[2].package, "F24_SCOREBOARD.json"));
  const offeredLadder = {
    source: { path: `${packages[2].package}/F24_SCOREBOARD.json`, sha256: fileHash(path.join(repo, packages[2].package, "F24_SCOREBOARD.json")), law: f24.law },
    candidate: {
      games: f24.candidate.games,
      offered_games: f24.candidate.offered_games,
      percent_of_offered_completed_under_par: f24.candidate.percent_of_offered_completed_under_par,
      margin_ladder: f24.candidate.margin_ladder,
    },
  };
  const census = {
    label: "V53_05_DEAD_SIBLING_TRUE_DIVOT_CENSUS",
    scope: "FRESH_30_RUN_INSTANCES_V53_02_V53_03_V53_04B_SINGLE_CREDITED_PAIRS_ONLY",
    measurement_only: true,
    full_804_run: false,
    implementation_commit: implementationCommit,
    law_binding: {
      F_V53_028: "TRUE_DIVOT_REQUIRES_STRENGTHENING_RISING_READ_PLUS_JOINT_BOOK_PLUS_TRUE_PRINT_AT_OR_BELOW_BID_AND_IS_CAUSALLY_RECOGNIZED_ON_LATER_HIGHER_PRINT",
      credit: "STRICTLY_LATER_DISTINCT_TRUE_TRADE_AT_OR_BELOW_POSTED_BEST_BID; NO_AGGRESSOR_DWELL_SIZE_OR_ASK_FILTER",
      pair_arm: "CREDITED_SIBLING_FILL_PRECEDES_DIVOT_RECOGNITION",
      post_only: "TARGET_BEST_BID_STRICTLY_BELOW_CURRENT_ASK",
      pair_cap: "TARGET_BEST_BID_AT_OR_BELOW_99_MINUS_CREDITED_SIBLING_ENTRY",
    },
    conservation: {
      run_instances: rows.length,
      unique_dead_sibling_identities: unique.size,
      classified_once: rows.length,
      class_sum: Object.values(summary.class_totals).reduce((sum, value) => sum + value, 0),
      non_single_uncompleted_exclusions: allExclusions.length,
      V53_04B_dead_sibling_count: rows.filter((row) => row.iteration === "V53_04B").length,
      V53_04B_expected_seven_confirmed: rows.filter((row) => row.iteration === "V53_04B").length === 7,
    },
    summary,
    by_iteration: perIteration,
    conditional_build_gate: {
      required_class: "DIVOTS_EXISTED_REST_ELSEWHERE",
      required_relation: "STRICT_MAJORITY_OF_DEAD_SIBLING_RUN_INSTANCES",
      pass: summary.strict_majority === "DIVOTS_EXISTED_REST_ELSEWHERE",
      disposition: summary.strict_majority === "DIVOTS_EXISTED_REST_ELSEWHERE" ? "V53_05_BUILD_PERMITTED" : "STOP_AFTER_T1_BANK_CLASS_TOTALS_NO_BUILD_NO_PINS_NO_FRESH25_NO_804",
    },
    offered_ladder_V53_04B: offeredLadder,
    exclusions: allExclusions,
    rows,
  };
  write("DEAD_SIBLING_DIVOT_CENSUS.json", census);
  write("CLASS_TOTALS.json", { summary, by_iteration: perIteration, conservation: census.conservation, conditional_build_gate: census.conditional_build_gate });
  write("OFFERED_LADDER_V53_04B.json", offeredLadder);
  write("SOURCE_HASH_MANIFEST.json", {
    sources: {
      parent: parentCommit,
      prior_sweep: priorSweepCommit,
      findings: { path: findingsPath, sha256: fileHash(path.join(repo, findingsPath)) },
      frozen_replay_spans: { path: spanPath.replaceAll("\\", "/"), sha256: shaBytes(spansBytes), rows: spans.length },
      truth_table_telemetry_only: { commit: truthCommit, path: truthPath, sha256: shaBytes(truthBytes), scoring_consumption: false },
      packages: packageInputs,
      selected_trace_streams: traceSources,
      canonical_prints: printLoad.receipt,
      verified_tapes: Object.fromEntries(Object.entries(tapeSources).sort(([a], [b]) => a.localeCompare(b))),
    },
  });
  write("FORBIDDEN_ACCESS_RECEIPT.json", { policy_change: false, full_804: false, fresh_25: false, pins_sweep: false, sealed: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, deployment: false });
  write("REPORT.md", `# V53-05 dead-sibling true-divot census\n\nT1 classified ${rows.length} single-credited dead-sibling run instances (${unique.size} unique leg identities): ${Object.entries(summary.class_totals).map(([key, value]) => `${key} ${value}`).join("; ")}. V53-04B's seven misses reproduced as seven single-credited dead siblings.\n\nThe strict majority is ${summary.strict_majority ?? "NONE"}. Conditional gate: ${census.conditional_build_gate.pass ? "PASS — V53-05 build permitted" : "STOP — no V53-05 build, pins sweep, fresh 25, Stage-1 #5, or full 804"}.\n\nEvery divot is the F-V53-028 joint observation and is recognized only on its later resume. A counterfactual slide credits only on a strictly later distinct true-trade receipt at-or-below the posted best bid; same-receipt credit is forbidden.\n\nV53-04B offered ladder: ${offeredLadder.candidate.offered_games} offered games; ${JSON.stringify(offeredLadder.candidate.margin_ladder)}.\n`);
  const baseNames = fs.readdirSync(output).sort();
  let determinism;
  if (compare) {
    const ignored = new Set(["DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"]), compareNames = fs.readdirSync(compare).sort();
    const names = [...new Set([...baseNames, ...compareNames])].filter((name) => !ignored.has(name)).sort();
    const mismatches = names.filter((name) => !fs.existsSync(path.join(output, name)) || !fs.existsSync(path.join(compare, name)) || fileHash(path.join(output, name)) !== fileHash(path.join(compare, name)));
    ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`);
    determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [] };
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
    writeManifest(compare);
  } else {
    determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_CLEAN_BUILD" };
  }
  write("DETERMINISM_RECEIPT.json", determinism);
  writeManifest(output);
  if (compare) ensure(fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")), "final manifests differ");
  process.stdout.write(canonical({ output, summary, conditional_build_gate: census.conditional_build_gate, determinism }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error.message}\n`); process.exitCode = 1; });
