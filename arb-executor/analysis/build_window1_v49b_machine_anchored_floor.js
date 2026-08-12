#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const stream = require("stream/promises");
const zlib = require("zlib");
const child = require("child_process");
const floor = require("./window1_machine_anchored_floor.js");

const V47_COMMIT = "fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34";
const V49B_PACKAGE_COMMIT = "47b51fd20f3b0b821d27b63b15a576e36103562e";
const FLOOR_CONVICTION_COMMIT = "f36798fc84ea2fb466750212a69bed021d74a772";
const OLD_CAUSAL_TABLE_COMMIT = "d3db740f143646614bc10778c0b4e27fa519dcd8";
const CC_OVERPAY_CENSUS_COMMIT = "096241ae";
const V47_PACKAGE = ".claude/window1_live_v4_replay/v47_same_tick_arm_20260810";
const V49B_PACKAGE = ".claude/window1_live_v4_replay/v49b_faithful_stand_at_p_20260811";
const OUTPUT_REL = ".claude/window1_live_v4_replay/v49b_machine_anchored_floor_rebuild_20260812";

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const index = argv.indexOf(name); return index < 0 ? fallback : argv[index + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, OUTPUT_REL)));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return shaBytes(fs.readFileSync(file)); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function safeOutput(directory) {
  ensure(path.basename(directory).includes("machine_anchored_floor"), `unsafe output ${directory}`);
  ensure(directory !== repo && directory !== path.parse(directory).root, `unsafe output ${directory}`);
  fs.rmSync(directory, { recursive: true, force: true });
  fs.mkdirSync(directory, { recursive: true });
}
function gitShow(commit, file) { return child.execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 }); }
function validateCommit(commit) {
  const resolved = child.execFileSync("git", ["rev-parse", "--verify", `${commit}^{commit}`], { cwd: repo, encoding: "utf8" }).trim();
  child.execFileSync("git", ["cat-file", "-e", `${resolved}^{commit}`], { cwd: repo });
  return resolved;
}
function readGzipRows(file) {
  const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim();
  return text ? text.split(/\r?\n/).map(JSON.parse) : [];
}
async function writeGzipRows(file, rows) {
  async function* encode() { for (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encode(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file));
}
function writeManifest() {
  const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  write("ARTIFACT_HASH_MANIFEST.json", canonical({ files: Object.fromEntries(files.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
}
function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) return null;
  let hour = +match[4]; if (match[7] === "AM" && hour === 12) hour = 0; if (match[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/); const header = lines.shift().split(",");
  return { header, rows: lines.filter(Boolean).map((line) => line.split(",")) };
}
function integer(value) { const number = Number(value); return Number.isInteger(number) ? number : null; }
function positive(value) { const number = Number(value); return Number.isFinite(number) && number > 0 ? number : null; }
function loadTape(ticker, left, right) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing tape ${ticker}`);
  const bytes = fs.readFileSync(file), parsed = parseCsv(zlib.gunzipSync(bytes).toString("utf8"));
  const index = Object.fromEntries(parsed.header.map((value, position) => [value, position]));
  const rows = [];
  for (let n = 0; n < parsed.rows.length; n += 1) {
    const values = parsed.rows[n], ts = parseEt(values[index.ts_et]);
    if (!Number.isFinite(ts) || ts < left || ts > right) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(values[index[`bid_${level}`]]), bidSize = positive(values[index[`bid_${level}_sz`]]);
      const ask = integer(values[index[`ask_${level}`]]), askSize = positive(values[index[`ask_${level}_sz`]]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]);
      if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    rows.push({ kind: "BOOK", ticker, ts, ordinal: n + 2, receipt: `${ticker}.csv.gz#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1] });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, since = null;
  for (const row of rows) { if (row.ask !== ask) { ask = row.ask; since = row.ts; } row.ask_dwell_seconds = row.ts - since; }
  return { rows, sha256: shaBytes(bytes), bytes: bytes.length };
}
async function loadPrints(boundsByTicker) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), "missing private prints");
  const hash = crypto.createHash("sha256"), byTicker = new Map([...boundsByTicker].map(([ticker]) => [ticker, []])), seen = new Map([...boundsByTicker].map(([ticker]) => [ticker, new Set()]));
  let rawRows = 0, admitted = 0, duplicates = 0;
  const input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 }); input.on("data", (chunk) => hash.update(chunk));
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line) continue; rawRows += 1;
    const raw = JSON.parse(line), bound = boundsByTicker.get(raw.ticker);
    if (!bound || !raw.true_print) continue;
    const ts = Date.parse(raw.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right) continue;
    if (!raw.trade_id || seen.get(raw.ticker).has(raw.trade_id)) { duplicates += 1; continue; }
    seen.get(raw.ticker).add(raw.trade_id); admitted += 1;
    byTicker.get(raw.ticker).push({ kind: "PRINT", ticker: raw.ticker, ts, ordinal: admitted, receipt: raw.receipt_id, price: integer(raw.price_cents), size: positive(raw.size), taker_side: raw.taker_side, taker_book_side: raw.taker_book_side, trade_id: raw.trade_id });
  }
  for (const rows of byTicker.values()) rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return { byTicker, receipt: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: hash.digest("hex"), bytes: fs.statSync(file).size, raw_rows: rawRows, admitted_unique_window_prints: admitted, duplicate_trade_ids_rejected: duplicates } };
}
async function loadActions(file, machine, mode) {
  const byLeg = new Map(); let raw = 0, admitted = 0;
  const lines = readline.createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line) continue; raw += 1;
    const row = JSON.parse(line);
    if (row.machine !== machine || row.mode !== mode || !floor.transitionKind(row.kind)) continue;
    admitted += 1; row.trace_ordinal = raw;
    if (!byLeg.has(row.leg_identity)) byLeg.set(row.leg_identity, []);
    byLeg.get(row.leg_identity).push(row);
  }
  return { byLeg, receipt: { path: path.relative(repo, file).replaceAll("\\", "/"), sha256: fileHash(file), bytes: fs.statSync(file).size, raw_rows: raw, admitted_transition_rows: admitted, machine, mode } };
}
function legRows(events) {
  const rows = [];
  for (const event of events) for (const leg of Object.values(event.legs)) rows.push({ event, leg });
  return rows.sort((a, b) => a.leg.leg_identity.localeCompare(b.leg.leg_identity));
}
function summarize(rows, field) { return floor.distribution(rows.map((row) => row[field])); }
function grouped(rows, keyFn) {
  const groups = new Map(); for (const row of rows) { const key = keyFn(row); if (!groups.has(key)) groups.set(key, []); groups.get(key).push(row); }
  return [...groups].sort(([a], [b]) => a.localeCompare(b));
}

async function main() {
  safeOutput(output);
  const commits = Object.fromEntries(Object.entries({ V47_COMMIT, V49B_PACKAGE_COMMIT, FLOOR_CONVICTION_COMMIT, OLD_CAUSAL_TABLE_COMMIT, CC_OVERPAY_CENSUS_COMMIT }).map(([name, value]) => [name, validateCommit(value)]));
  const v47EventFile = path.join(repo, V47_PACKAGE, "MARKET_EVENT_LEDGER.jsonl.gz"), v49bEventFile = path.join(repo, V49B_PACKAGE, "MARKET_EVENT_LEDGER.jsonl.gz");
  const v47ActionFile = path.join(repo, V47_PACKAGE, "ACTION_TRACE.jsonl.gz"), v49bActionFile = path.join(repo, V49B_PACKAGE, "ACTION_TRACE.jsonl.gz");
  for (const file of [v47EventFile, v49bEventFile, v47ActionFile, v49bActionFile]) ensure(fs.existsSync(file), `missing frozen input ${file}`);
  const v47Events = readGzipRows(v47EventFile), v49bEvents = readGzipRows(v49bEventFile);
  ensure(v47Events.length === 804 && v49bEvents.length === 804, "event population must be 804 per machine");
  const v47Legs = legRows(v47Events), v49bLegs = legRows(v49bEvents);
  ensure(v47Legs.length === 1608 && v49bLegs.length === 1608, "leg population must be 1608 per machine");
  const bounds = new Map(v49bLegs.map(({ event, leg }) => [leg.ticker, { left: event.w1_left_epoch, right: event.w1_right_epoch }]));
  const prints = await loadPrints(bounds);
  const [v47Actions, v49bActions] = await Promise.all([
    loadActions(v47ActionFile, "V47_SAME_TICK_ARM", "MARKET_UNION_REACH"),
    loadActions(v49bActionFile, "V49B_FAITHFUL_STAND_AT_P", "MARKET_TRADES_AS_TRUTH"),
  ]);
  const tapeReceipts = [];
  function rebuildOne({ event, leg }, actionsByLeg, machine, tapeRows) {
      const actions = actionsByLeg.get(leg.leg_identity) ?? [], intervals = floor.buildStandingIntervals(actions, event.w1_right_epoch);
      const evidence = floor.evidenceFloor(intervals, tapeRows, prints.byTicker.get(leg.ticker) ?? []);
      const rebuilt = evidence.machine_floor?.price_cents ?? null;
      return { schema_version: "window1-machine-anchored-floor-v1", machine, event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, leg_id: leg.leg_id, category: event.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, w1_left_epoch: event.w1_left_epoch, w1_right_epoch: event.w1_right_epoch, credited: leg.credited, entry_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch, standing_interval_count: intervals.length, first_stand_timestamp_epoch: intervals[0]?.start_timestamp_epoch ?? null, last_stand_end_timestamp_epoch: intervals.at(-1)?.end_timestamp_epoch ?? null, rebuilt_machine_floor_cents: rebuilt, rebuilt_machine_floor_channel: evidence.machine_floor?.channel ?? null, rebuilt_machine_floor_receipt: evidence.machine_floor?.receipt ?? null, rebuilt_machine_trade_floor_cents: evidence.machine_trade_floor?.price_cents ?? null, rebuilt_machine_quote_floor_cents: evidence.machine_quote_floor?.price_cents ?? null, market_offered_true_trade_floor_cents: evidence.market_offered_trade_floor?.price_cents ?? null, entry_minus_machine_floor_cents: leg.credited && Number.isInteger(rebuilt) ? leg.entry_cents - rebuilt : null, entry_minus_market_offered_floor_cents: leg.credited && evidence.market_offered_trade_floor ? leg.entry_cents - evidence.market_offered_trade_floor.price_cents : null, presence_premium_cents: Number.isInteger(rebuilt) && evidence.market_offered_trade_floor ? rebuilt - evidence.market_offered_trade_floor.price_cents : null, impossible_entry_below_rebuilt_floor: Boolean(leg.credited && Number.isInteger(rebuilt) && leg.entry_cents < rebuilt), standing_intervals: intervals };
  }
  const rebuiltV47 = [], rebuiltV49b = [];
  for (let index = 0; index < v49bLegs.length; index += 1) {
    ensure(v47Legs[index].leg.leg_identity === v49bLegs[index].leg.leg_identity, `cross-machine identity mismatch at ${index}`);
    const { ticker } = v49bLegs[index].leg, bound = bounds.get(ticker), tape = loadTape(ticker, bound.left, bound.right);
    tapeReceipts.push({ ticker, sha256: tape.sha256, bytes: tape.bytes });
    rebuiltV47.push(rebuildOne(v47Legs[index], v47Actions.byLeg, "V47_SAME_TICK_ARM", tape.rows));
    rebuiltV49b.push(rebuildOne(v49bLegs[index], v49bActions.byLeg, "V49B_FAITHFUL_STAND_AT_P", tape.rows));
  }
  const oldTableBytes = gitShow(OLD_CAUSAL_TABLE_COMMIT, ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CAUSAL_LEG_TABLE.json"), oldTable = JSON.parse(oldTableBytes);
  const oldImpossible = rebuiltV47.filter((row) => row.credited && Number.isInteger(oldTable[row.ticker]?.causal_floor) && row.entry_cents < oldTable[row.ticker].causal_floor).map((row) => ({ leg_identity: row.leg_identity, ticker: row.ticker, entry_cents: row.entry_cents, old_causal_floor_cents: oldTable[row.ticker].causal_floor, gap_cents: oldTable[row.ticker].causal_floor - row.entry_cents, category: row.category }));
  const rebuiltV47Impossible = rebuiltV47.filter((row) => row.impossible_entry_below_rebuilt_floor), rebuiltV49bImpossible = rebuiltV49b.filter((row) => row.impossible_entry_below_rebuilt_floor);
  ensure(oldImpossible.length === 213, `failed to reproduce f36798fc impossible set: ${oldImpossible.length}`);
  ensure(rebuiltV47Impossible.length === 0 && rebuiltV49bImpossible.length === 0, "machine-anchored rebuild retained impossible credited legs");
  const completeEvents = new Set(v49bEvents.filter((event) => event.completed_pair).map((event) => event.event_id));
  const completed810 = rebuiltV49b.filter((row) => completeEvents.has(row.event_id));
  ensure(completeEvents.size === 405 && completed810.length === 810 && completed810.every((row) => row.credited), "V49b completion conservation failed");
  const premiumLedger = completed810.map((row) => ({ schema_version: "window1-v49b-presence-premium-v1", ...Object.fromEntries(Object.entries(row).filter(([key]) => !["standing_intervals"].includes(key))) }));
  ensure(premiumLedger.every((row) => Number.isInteger(row.entry_minus_machine_floor_cents) && row.entry_minus_machine_floor_cents >= 0), "machine premium must be fully bound and non-negative");
  ensure(premiumLedger.every((row) => Number.isInteger(row.entry_minus_market_offered_floor_cents) && Number.isInteger(row.presence_premium_cents)), "market floor and presence premium must be fully bound");
  ensure(premiumLedger.every((row) => row.entry_minus_market_offered_floor_cents === row.entry_minus_machine_floor_cents + row.presence_premium_cents), "presence premium arithmetic failed");
  const aggregate = { completed_pairs: completeEvents.size, credited_legs: premiumLedger.length, entry_minus_rebuilt_machine_floor_cents: summarize(premiumLedger, "entry_minus_machine_floor_cents"), entry_minus_market_offered_true_trade_floor_cents: summarize(premiumLedger, "entry_minus_market_offered_floor_cents"), presence_premium_cents: summarize(premiumLedger, "presence_premium_cents"), arithmetic: "ENTRY_MINUS_MARKET_OFFERED_FLOOR = ENTRY_MINUS_MACHINE_ANCHORED_FLOOR + MACHINE_FLOOR_MINUS_MARKET_OFFERED_FLOOR", conservation_pass: premiumLedger.length === 810 };
  const category = grouped(premiumLedger, (row) => row.category).map(([key, rows]) => ({ category: key, legs: rows.length, entry_minus_rebuilt_machine_floor_cents: summarize(rows, "entry_minus_machine_floor_cents"), entry_minus_market_offered_true_trade_floor_cents: summarize(rows, "entry_minus_market_offered_floor_cents"), presence_premium_cents: summarize(rows, "presence_premium_cents") }));
  const categoryPrice = grouped(premiumLedger, (row) => `${row.category}|${row.price_region}`).map(([key, rows]) => ({ cell: key, category: rows[0].category, price_region: rows[0].price_region, legs: rows.length, entry_minus_rebuilt_machine_floor_cents: summarize(rows, "entry_minus_machine_floor_cents"), entry_minus_market_offered_true_trade_floor_cents: summarize(rows, "entry_minus_market_offered_floor_cents"), presence_premium_cents: summarize(rows, "presence_premium_cents") }));
  const reconciliation = { controlling_spec: { commit: commits.FLOOR_CONVICTION_COMMIT, old_defect: "ANALYTIC_TRIGGER_EVENT_ANCHORED_INSTEAD_OF_EXECUTABLE_STAND; STRICT_AFTER_EXCLUDED_ANCHORING_FILL_PRINT", ordered_repair: "REGENERATE_CAUSAL_LEG_TABLE_ANCHORED_TO_EXECUTABLE_ACTUAL_STAND_TIMES", expected_old_impossible: 213 }, old_table: { commit: commits.OLD_CAUSAL_TABLE_COMMIT, sha256: shaBytes(oldTableBytes), V47_credited_legs: rebuiltV47.filter((row) => row.credited).length, with_old_floor: rebuiltV47.filter((row) => row.credited && Number.isInteger(oldTable[row.ticker]?.causal_floor)).length, impossible_entry_below_old_floor: oldImpossible.length, by_category: Object.fromEntries(grouped(oldImpossible, (row) => row.category).map(([key, rows]) => [key, rows.length])), gap_cents: floor.distribution(oldImpossible.map((row) => row.gap_cents)) }, rebuilt: { law: "MIN(TRUE_TRADE_AT_OR_BELOW_REST, QUALIFYING_ASK_AT_OR_BELOW_REST) STRICTLY_AFTER_ACTUAL_REST_STAND AND THROUGH FILL_OR_CANCEL", qualifying_ask_dwell_seconds: floor.QUALIFYING_ASK_DWELL_SECONDS, qualifying_ask_size_contracts: floor.QUALIFYING_ASK_SIZE_CONTRACTS, V47: { legs: rebuiltV47.length, credited_legs: rebuiltV47.filter((row) => row.credited).length, impossible_entry_below_rebuilt_floor: rebuiltV47Impossible.length }, V49b: { legs: rebuiltV49b.length, credited_legs: rebuiltV49b.filter((row) => row.credited).length, impossible_entry_below_rebuilt_floor: rebuiltV49bImpossible.length } }, killed_213: oldImpossible.length === 213 && rebuiltV47Impossible.length === 0, old_impossible_identities: oldImpossible };
  const presence = { stamp: "FIRST_MACHINE_ANCHORED_PRESENCE_PREMIUM_MEASUREMENT", machine: "V49B_FAITHFUL_STAND_AT_P", market_offer_ruler: "LOWEST_LAWFUL_TRUE_TRADE_ANYTIME_IN_FROZEN_W1_SPAN", machine_reach_ruler: "LOWEST_UNION_EVIDENCE_AT_OR_BELOW_AN_ACTUAL_EXECUTABLE_REST_WHILE_IT_STOOD", warning: "THIS IS COUNTERFACTUAL_REPLAY_REACH, NOT QUEUE_POSITION_OR LIVE_MARKET_IMPACT", CC_par_sheet_binding: { status: "BASIS_REPRODUCED_LOCALLY; NO SEPARATE SHA-PINNED V49B PAR SHEET WAS PRESENT", prior_CC_overpay_census_commit: commits.CC_OVERPAY_CENSUS_COMMIT }, aggregate, per_category: category, per_category_x_price_region: categoryPrice };
  tapeReceipts.sort((a, b) => a.ticker.localeCompare(b.ticker));
  await writeGzipRows(path.join(output, "V47_MACHINE_ANCHORED_FLOOR_TABLE_1608.jsonl.gz"), rebuiltV47);
  await writeGzipRows(path.join(output, "V49B_MACHINE_ANCHORED_FLOOR_TABLE_1608.jsonl.gz"), rebuiltV49b);
  await writeGzipRows(path.join(output, "V49B_COMPLETED_810_PRESENCE_PREMIUM_LEDGER.jsonl.gz"), premiumLedger);
  write("F36798FC_IMPOSSIBLE_SET_RECONCILIATION.json", canonical(reconciliation));
  write("PRESENCE_PREMIUM_SUMMARY.json", canonical(presence));
  write("CATEGORY_X_PRICE_REGION.json", canonical({ per_category: category, per_category_x_price_region: categoryPrice }));
  write("CONTROL_BINDING.json", canonical({ schema_version: "window1-v49b-machine-anchored-floor-control-v1", commits, frozen_inputs: { V47_event_ledger: { path: V47_PACKAGE + "/MARKET_EVENT_LEDGER.jsonl.gz", sha256: fileHash(v47EventFile) }, V47_action_trace: v47Actions.receipt, V49b_event_ledger: { path: V49B_PACKAGE + "/MARKET_EVENT_LEDGER.jsonl.gz", sha256: fileHash(v49bEventFile) }, V49b_action_trace: v49bActions.receipt, old_causal_leg_table: { commit: commits.OLD_CAUSAL_TABLE_COMMIT, sha256: shaBytes(oldTableBytes) }, private_prints: prints.receipt, private_tapes: { count: tapeReceipts.length, manifest_sha256: shaBytes(Buffer.from(canonical(tapeReceipts))) } }, policy_changes: 0, replay_changes: 0, scoring_changes: 0 }));
  write("SOURCE_HASH_MANIFEST.json", canonical({ builder: { path: "arb-executor/analysis/build_window1_v49b_machine_anchored_floor.js", sha256: fileHash(__filename) }, floor_module: { path: "arb-executor/analysis/window1_machine_anchored_floor.js", sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_machine_anchored_floor.js")) }, test: { path: "arb-executor/tests/test_window1_machine_anchored_floor.js", sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_machine_anchored_floor.js")) }, tape_manifest: tapeReceipts }));
  write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ holdout_access: 0, sealed_population_access: 0, live_access: 0, network_runtime: 0, orders: 0, positions: 0, exits: 0, settlement: 0, DCA: 0, deployment: 0, policy_mutation: 0, scope: "READ_ONLY_DEV_804_FROZEN_V47_AND_V49B_ARTIFACTS_PLUS_HASH_BOUND_PRIVATE_FIT_INPUTS" }));
  const report = `# V49b machine-anchored floor rebuild\n\nStatus: PASS. The staged f36798fc floor defect is removed: V47 reproduces the old 213 impossible credited-leg rows and the executable-stand rebuild contains zero; V49b also contains zero. No policy or replay behavior changed.\n\n## V49b completed pairs — 810 credited legs\n\n- Sum(entry - rebuilt machine floor): **${aggregate.entry_minus_rebuilt_machine_floor_cents.sum}c**; distribution min/p25/median/p75/p90/max ${aggregate.entry_minus_rebuilt_machine_floor_cents.min}/${aggregate.entry_minus_rebuilt_machine_floor_cents.p25}/${aggregate.entry_minus_rebuilt_machine_floor_cents.median}/${aggregate.entry_minus_rebuilt_machine_floor_cents.p75}/${aggregate.entry_minus_rebuilt_machine_floor_cents.p90}/${aggregate.entry_minus_rebuilt_machine_floor_cents.max}.\n- Sum(entry - market-offered true-trade floor): **${aggregate.entry_minus_market_offered_true_trade_floor_cents.sum}c**.\n- Presence premium, defined as the difference: **${aggregate.presence_premium_cents.sum}c**; distribution min/p25/median/p75/p90/max ${aggregate.presence_premium_cents.min}/${aggregate.presence_premium_cents.p25}/${aggregate.presence_premium_cents.median}/${aggregate.presence_premium_cents.p75}/${aggregate.presence_premium_cents.p90}/${aggregate.presence_premium_cents.max}.\n\nThe arithmetic conserves on all 810 rows. The market-offer ruler is the lowest lawful true trade in the frozen W1 span. The machine ruler is the lowest qualifying ask or true trade at-or-below an actual executable rest while that rest stood. This isolates the counterfactual replay presence premium; it still cannot measure real queue position or live market impact.\n\nPer-category and category-by-price-region distributions are frozen in PRESENCE_PREMIUM_SUMMARY.json and CATEGORY_X_PRICE_REGION.json.\n`;
  write("REPORT.md", report);
  const namesBeforeDeterminism = fs.readdirSync(output).sort();
  let determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
  if (compare) {
    const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extra.length, `determinism mismatch ${[...mismatches, ...extra].join(",")}`);
    determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
  }
  write("DETERMINISM_RECEIPT.json", canonical(determinism)); writeManifest();
  if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); const files = fs.readdirSync(compare).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(); fs.writeFileSync(path.join(compare, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(files.map((name) => [name, { sha256: fileHash(path.join(compare, name)), bytes: fs.statSync(path.join(compare, name)).size }])) })); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "final manifests differ"); }
  process.stdout.write(canonical({ output, reconciliation: reconciliation.rebuilt, killed_213: reconciliation.killed_213, presence_premium: aggregate, determinism }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
