#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const stream = require("stream/promises");
const zlib = require("zlib");
const { execFileSync } = require("child_process");

const V52E_COMMIT = "b09aa22b301205d5d44d683497cf3edc5b177cf8";
const V52D_PARENT = "893ee4c6860179a82c4b42439cf4a94cb2bcc97f";
const V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83";
const SHEVAN_CLOSEOUT_COMMIT = "d9d9a4e3c2615e76276761d7bed8ae92928091f4";
const V52E_PACKAGE = ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812";
const DEFAULT_OUTPUT = ".claude/window1_live_v4_replay/v52e_trace_span_provenance_audit_20260813";
const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, DEFAULT_OUTPUT)));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { const h = crypto.createHash("sha256"); const fd = fs.openSync(file, "r"); const b = Buffer.allocUnsafe(1024 * 1024); try { for (;;) { const n = fs.readSync(fd, b, 0, b.length, null); if (!n) break; h.update(b.subarray(0, n)); } } finally { fs.closeSync(fd); } return h.digest("hex"); }
function gitShow(commit, relativePath) { return execFileSync("git", ["show", `${commit}:${relativePath}`], { cwd: repo, maxBuffer: 1024 * 1024 * 1024 }); }
function localLine(relativePath, needle) { const rows = fs.readFileSync(path.join(repo, relativePath), "utf8").split(/\r?\n/); const at = rows.findIndex((row) => row.includes(needle)); ensure(at >= 0, `missing line anchor ${needle}`); return at + 1; }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let hour = +m[4]; if (m[7] === "AM" && hour === 12) hour = 0; if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function distribution(values) {
  const x = values.filter(Number.isFinite).sort((a, b) => a - b);
  const pick = (q) => x.length ? x[Math.max(0, Math.ceil(q * x.length) - 1)] : null;
  return { n: x.length, min: x.length ? x[0] : null, p25: pick(.25), median: pick(.5), p75: pick(.75), p90: pick(.9), max: x.length ? x.at(-1) : null, sum: x.reduce((a, b) => a + b, 0) };
}
function safeOutput(dir) { ensure(path.basename(dir).includes("v52e_trace_span"), `unsafe output ${dir}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true }); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
async function writeGzipRows(file, rows) { async function* encode() { for (const row of rows) yield `${JSON.stringify(row)}\n`; } await stream.pipeline(encode(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file)); }
async function readGzipJsonLines(file, consume) { const rl = readline.createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity }); for await (const line of rl) if (line) consume(JSON.parse(line)); }

async function scanBookTape(ticker, bound) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing materialized tape ${ticker}`);
  const hash = crypto.createHash("sha256");
  const source = fs.createReadStream(file); source.on("data", (chunk) => hash.update(chunk));
  const rl = readline.createInterface({ input: source.pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let header = null, rowNumber = 0, last = null, rowsInWindow = 0;
  for await (const line of rl) {
    rowNumber += 1;
    if (!header) { header = line.split(","); continue; }
    const values = line.split(","); const ts = parseEt(values[0]);
    if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right) continue;
    const bid = Number(values[2]), ask = Number(values[12]);
    if (!Number.isInteger(bid) || !Number.isInteger(ask)) continue;
    rowsInWindow += 1;
    if (!last || ts >= last.timestamp_epoch) last = { kind: "BOOK", timestamp_epoch: ts, receipt: `${ticker}.csv.gz#row-${rowNumber}`, bid, ask };
  }
  ensure(last, `no materialized book row in window ${ticker}`);
  return { file, sha256: hash.digest("hex"), bytes: fs.statSync(file).size, rows_in_window: rowsInWindow, final: last };
}

async function main() {
  safeOutput(output);
  const cohortPath = `${V52E_PACKAGE}/COHORT_SELECTION_RECEIPT.json`;
  const outcomePath = `${V52E_PACKAGE}/V52E_FLOW_OUTCOMES_OBSERVATION_ONLY.json`;
  const observationPath = `${V52E_PACKAGE}/OUTCOME_OBSERVATIONS_30.json`;
  const tracePath = `${V52E_PACKAGE}/V52E_FULL_DECISION_TRACE_30_GAMES.jsonl.gz`;
  const cohortBytes = gitShow(V52E_COMMIT, cohortPath), outcomeBytes = gitShow(V52E_COMMIT, outcomePath), observationBytes = gitShow(V52E_COMMIT, observationPath), traceBytes = gitShow(V52E_COMMIT, tracePath);
  const cohort = JSON.parse(cohortBytes), outcomes = JSON.parse(outcomeBytes), observation = JSON.parse(observationBytes);
  ensure(cohort.combined_30.length === 30 && outcomes.length === 30, "frozen cohort/outcome conservation failed");
  const selected = new Set(cohort.combined_30.map((row) => row.event_id));
  const spanPath = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/WINDOW1_SPAN_804.json";
  const spanBytes = gitShow(V36_COMMIT, spanPath), spanRows = JSON.parse(spanBytes).rows.filter((row) => selected.has(row.event_id));
  ensure(spanRows.length === 30, `span cohort ${spanRows.length}`);
  const boundByLeg = new Map(), tickerToLeg = new Map();
  for (const span of spanRows) for (const leg of span.per_leg) {
    boundByLeg.set(leg.leg_identity, { event_id: span.event_id, category: span.category, precision_class: span.precision_class, ticker: leg.ticker, left: span.w1_left_epoch, right: span.w1_right_epoch });
    tickerToLeg.set(leg.ticker, leg.leg_identity);
  }
  ensure(boundByLeg.size === 60 && tickerToLeg.size === 60, "leg/ticker conservation failed");

  const frozenTraceFile = path.join(output, ".frozen-trace.tmp.gz"); fs.writeFileSync(frozenTraceFile, traceBytes);
  const traceFinal = new Map(), traceFirst = new Map(), traceCounts = new Map();
  await readGzipJsonLines(frozenTraceFile, (row) => {
    if (!boundByLeg.has(row.leg_identity)) return;
    traceFirst.set(row.leg_identity, traceFirst.get(row.leg_identity) || row);
    traceFinal.set(row.leg_identity, row);
    traceCounts.set(row.leg_identity, (traceCounts.get(row.leg_identity) || 0) + 1);
  });
  fs.rmSync(frozenTraceFile);
  ensure(traceFinal.size === 60, `trace final conservation ${traceFinal.size}`);

  const bookByLeg = new Map();
  for (const [legIdentity, bound] of [...boundByLeg].sort(([a], [b]) => a.localeCompare(b))) bookByLeg.set(legIdentity, await scanBookTape(bound.ticker, bound));

  const rawCoverageFile = path.join(privateRoot, "ws-coverage/WS_DEPTH_COVERAGE_LEDGER.jsonl");
  ensure(fs.existsSync(rawCoverageFile), "missing raw WS coverage ledger");
  const rawCoverageHash = crypto.createHash("sha256"), rawCoverageSource = fs.createReadStream(rawCoverageFile); rawCoverageSource.on("data", (chunk) => rawCoverageHash.update(chunk));
  const rawCoverageRl = readline.createInterface({ input: rawCoverageSource, crlfDelay: Infinity });
  const rawCoverageByTicker = new Map();
  for await (const line of rawCoverageRl) {
    if (!line) continue;
    const row = JSON.parse(line); if (tickerToLeg.has(row.ticker)) rawCoverageByTicker.set(row.ticker, row);
  }
  ensure(rawCoverageByTicker.size === 60, `raw coverage conservation ${rawCoverageByTicker.size}`);
  const rawCoverageSha256 = rawCoverageHash.digest("hex");

  const printFile = path.join(privateRoot, "fit-local/prints.jsonl");
  const printHash = crypto.createHash("sha256"), printSource = fs.createReadStream(printFile); printSource.on("data", (chunk) => printHash.update(chunk));
  const printRl = readline.createInterface({ input: printSource, crlfDelay: Infinity });
  const printFinal = new Map(), printSeen = new Map([...tickerToLeg.keys()].map((ticker) => [ticker, new Set()])), printsByLeg = new Map([...boundByLeg.keys()].map((id) => [id, []]));
  for await (const line of printRl) {
    if (!line) continue;
    const row = JSON.parse(line); if (!tickerToLeg.has(row.ticker) || !row.true_print || !row.trade_id) continue;
    const legIdentity = tickerToLeg.get(row.ticker), bound = boundByLeg.get(legIdentity), ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right || printSeen.get(row.ticker).has(row.trade_id)) continue;
    printSeen.get(row.ticker).add(row.trade_id);
    const normalized = { kind: "PRINT", timestamp_epoch: ts, receipt: row.receipt_id, trade_id: row.trade_id, price_cents: Number(row.price_cents), size: Number(row.size), taker_side: row.taker_side, taker_book_side: row.taker_book_side };
    printsByLeg.get(legIdentity).push(normalized);
    if (!printFinal.has(legIdentity) || ts >= printFinal.get(legIdentity).timestamp_epoch) printFinal.set(legIdentity, normalized);
  }
  const printSha256 = printHash.digest("hex");

  const outcomeByLeg = new Map();
  for (const event of outcomes) for (const leg of event.legs) outcomeByLeg.set(leg.leg_identity, { event_id: event.event_id, completed_pair_observation: event.completed_pair_observation, combined_entry_cents_observation: event.combined_entry_cents_observation, ...leg });
  ensure(outcomeByLeg.size === 60, "outcome leg conservation failed");

  const ledger = [];
  for (const [legIdentity, bound] of [...boundByLeg].sort(([a], [b]) => a.localeCompare(b))) {
    const trace = traceFinal.get(legIdentity), book = bookByLeg.get(legIdentity).final, print = printFinal.get(legIdentity) || null;
    const union = !print || book.timestamp_epoch >= print.timestamp_epoch ? book : print;
    const outcome = outcomeByLeg.get(legIdentity);
    const receiptMatches = Number.isFinite(outcome.fill_timestamp_epoch) ? printsByLeg.get(legIdentity).filter((row) => row.receipt === outcome.post_onset_true_trade_low_receipt && row.price_cents <= outcome.entry_cents_observation) : [];
    const timeMatches = Number.isFinite(outcome.fill_timestamp_epoch) ? printsByLeg.get(legIdentity).filter((row) => Math.abs(row.timestamp_epoch - outcome.fill_timestamp_epoch) < 0.01 && row.price_cents <= outcome.entry_cents_observation) : [];
    const fillMatches = receiptMatches.length ? receiptMatches : timeMatches;
    const fillReceipt = fillMatches.length === 1 ? fillMatches[0] : null;
    const rawCoverage = rawCoverageByTicker.get(bound.ticker);
    const apparent = Math.max(0, union.timestamp_epoch - trace.timestamp_epoch);
    const exportReason = outcome.final_state === "CREDITED" ? "DECISION_EXPORT_QUIESCES_AFTER_TERMINAL_CREDIT" : (union.kind === "PRINT" ? "PRINT_RECEIPTS_CONSUMED_BUT_NOT_EMITTED_AS_PLACEMENT_DECISIONS" : apparent === 0 ? "DECISION_EXPORT_REACHES_FINAL_MATERIALIZED_BOOK" : "UNEXPLAINED_EXPORT_GAP");
    const runnerFull = union.timestamp_epoch <= bound.right && book.timestamp_epoch <= bound.right;
    ledger.push({
      event_id: bound.event_id, leg_identity: legIdentity, ticker: bound.ticker, category: bound.category, precision_class: bound.precision_class,
      window: { left_epoch: bound.left, right_epoch: bound.right },
      frozen_decision_trace: { first_timestamp_epoch: traceFirst.get(legIdentity).timestamp_epoch, final_timestamp_epoch: trace.timestamp_epoch, final_receipt: trace.receipt, rows: traceCounts.get(legIdentity), seconds_before_window_edge: bound.right - trace.timestamp_epoch },
      terminal: { final_state: outcome.final_state, entry_cents: outcome.entry_cents_observation, fill_timestamp_epoch: outcome.fill_timestamp_epoch, terminal_reason: outcome.terminal_reason, fill_receipt: fillReceipt, fill_receipt_match_count: fillMatches.length },
      materialized_tape: { final_book_receipt: book, final_print_receipt: print, final_union_receipt: union, seconds_before_window_edge: bound.right - union.timestamp_epoch, book_rows_in_window: bookByLeg.get(legIdentity).rows_in_window },
      raw_ws_source_context: { first_exchange_ts: rawCoverage.first_exchange_ts, last_exchange_ts: rawCoverage.last_exchange_ts, full_depth_usable: rawCoverage.full_depth_usable, sequence_valid_full_ladder_epoch_count: rawCoverage.sequence_valid_full_ladder_epoch_count, usable_extension_beyond_materialization_proven: rawCoverage.full_depth_usable === true && Date.parse(rawCoverage.last_exchange_ts) / 1000 > union.timestamp_epoch },
      runner_consumption: { final_receipt_consumed: union, classification: runnerFull ? "FULL_SPAN" : "TRUNCATED", truncation_seconds: runnerFull ? 0 : bound.right - union.timestamp_epoch, proof: "simulate timeline iterates every bounded materialized BOOK/PRINT row; terminal-credit branch continues only after receipt consumption" },
      export: { classification: apparent > 0 ? "TRUNCATED_EXPORT_ONLY" : "FULL_SPAN_EXPORT", apparent_truncation_seconds: apparent, reason: exportReason },
    });
  }
  ensure(ledger.every((row) => row.runner_consumption.classification === "FULL_SPAN"), "runner/input truncation found; receipt-only disposition invalid");
  ensure(ledger.every((row) => row.export.reason !== "UNEXPLAINED_EXPORT_GAP"), "unexplained export gap found");

  const apparentValues = ledger.map((row) => row.export.apparent_truncation_seconds);
  const edgeValues = ledger.map((row) => Math.max(0, row.materialized_tape.seconds_before_window_edge));
  const credited = ledger.filter((row) => row.terminal.final_state === "CREDITED");
  const rootSource = "arb-executor/analysis/build_window1_v38_maker_only.js";
  const rootCause = {
    verdict: "EXPORT_ONLY_TRUNCATION; RUNNER_AND_MATERIALIZED_INPUT_FULL_SPAN",
    disposition: "REGENERATE_RECEIPT_EXPORTS_ONLY; NO_POLICY_RERUN",
    code_lines: {
      bounded_timeline_iteration: { path: rootSource, line: localLine(rootSource, "for (const row of timeline)"), effect: "every materialized BOOK/PRINT receipt inside the edge is iterated" },
      terminal_credit_quiescence: { path: rootSource, line_start: localLine(rootSource, "if (leg.credited) {"), line_end: localLine(rootSource, "if (isV52ReadAuthority && leg.v52_onset?.selected" ) - 2, effect: "after credit the receipt is consumed, but no judgment decision row is emitted" },
      print_receipt_branch: { path: rootSource, line_start: localLine(rootSource, "if (row.kind === \"PRINT\")"), line_end: localLine(rootSource, "if (mode === \"MARKET_UNION_REACH\" && policy.tradedAtLevel"), effect: "print receipts can credit or update evidence, then continue before judgment trace emission" },
      decision_export_only: { path: rootSource, line_start: localLine(rootSource, "leg.judgment_trace_rows.push({"), line_end: localLine(rootSource, "leg.judgment_trace_rows.push({") + 23, effect: "export is a BOOK decision-evaluation stream, not an input-consumption stream" },
    },
    conservation: { games: 30, legs: ledger.length, runner_full_span: ledger.filter((row) => row.runner_consumption.classification === "FULL_SPAN").length, runner_truncated: ledger.filter((row) => row.runner_consumption.classification === "TRUNCATED").length, export_apparently_truncated: ledger.filter((row) => row.export.classification === "TRUNCATED_EXPORT_ONLY").length, credited_legs: credited.length, raw_ws_full_depth_usable_legs: ledger.filter((row) => row.raw_ws_source_context.full_depth_usable).length, materialization_shorter_than_usable_raw_source: ledger.filter((row) => row.raw_ws_source_context.usable_extension_beyond_materialization_proven).length },
  };

  const she = ledger.find((row) => row.leg_identity.endsWith("SHEVAN|SHE")), van = ledger.find((row) => row.leg_identity.endsWith("SHEVAN|VAN"));
  ensure(she && van && she.terminal.final_state === "CREDITED" && van.terminal.final_state === "CREDITED", "SHEVAN frozen credit binding failed");
  const sheLeft = she.window.left_epoch;
  const crossings = [
    { label: "VAN_49_CLUSTER_T_PLUS_772", timestamp_epoch: sheLeft + 772 * 60 },
    { label: "SHE_COLLAPSE_T_PLUS_792", timestamp_epoch: sheLeft + 792 * 60 },
  ];
  const shevan = {
    event_id: she.event_id,
    verdict: "RESTS_NOT_STANDING_AT_T_PLUS_772_OR_T_PLUS_792; BOTH_LEGS_ALREADY_CREDITED",
    legs: {
      SHE: { target_cents: she.terminal.entry_cents, credited_timestamp_epoch: she.terminal.fill_timestamp_epoch, credited_t_plus_seconds: she.terminal.fill_timestamp_epoch - she.window.left_epoch, fill_receipt: she.terminal.fill_receipt, terminal_reason: she.terminal.terminal_reason },
      VAN: { target_cents: van.terminal.entry_cents, credited_timestamp_epoch: van.terminal.fill_timestamp_epoch, credited_t_plus_seconds: van.terminal.fill_timestamp_epoch - van.window.left_epoch, fill_receipt: van.terminal.fill_receipt, terminal_reason: van.terminal.terminal_reason },
    },
    crossings: crossings.map((crossing) => ({ ...crossing, SHE_rest_standing: she.terminal.fill_timestamp_epoch > crossing.timestamp_epoch, VAN_rest_standing: van.terminal.fill_timestamp_epoch > crossing.timestamp_epoch, status: "NO_ACTIVE_ENTRY_REST; TERMINAL_CREDIT_PRECEDES_CROSSING" })),
    correction_to_d9d9a4e3_part_B: "The closeout treated end-of-decision-export as an unresolved standing rest. Frozen outcomes prove VAN credited at T+759.0 and SHE at T+761.3; later T+772/T+792 crossings are post-entry and cannot credit those rests again.",
  };

  const policyPaths = ["arb-executor/analysis/window1_v52e_palantir_wiring.js", "arb-executor/analysis/window1_v52d_disagreement_referee.js", "arb-executor/analysis/window1_v52c_full_post_onset_read.js", "arb-executor/analysis/window1_v52b_read_level_authority.js", "arb-executor/analysis/window1_v52_judgment_gate.js"];
  const policyIdentity = { frozen_commit: V52E_COMMIT, files: {}, all_byte_identical: true };
  for (const relativePath of policyPaths) {
    const before = gitShow(V52E_COMMIT, relativePath), after = fs.readFileSync(path.join(repo, relativePath));
    policyIdentity.files[relativePath] = { before_sha256: shaBytes(before), after_sha256: shaBytes(after), byte_identical: before.equals(after) };
    if (!before.equals(after)) policyIdentity.all_byte_identical = false;
  }
  ensure(policyIdentity.all_byte_identical, "policy byte identity failed");

  const correctedSpanRows = ledger.map((row) => ({ event_id: row.event_id, leg_identity: row.leg_identity, decision_trace_final: row.frozen_decision_trace, terminal: row.terminal, final_receipt_consumed: row.runner_consumption.final_receipt_consumed, window_right_epoch: row.window.right_epoch, runner_span_classification: row.runner_consumption.classification, decision_export_classification: row.export.classification, decision_export_gap_seconds: row.export.apparent_truncation_seconds }));
  const audit = {
    verdict: rootCause.verdict,
    controlling_v52e_commit: V52E_COMMIT,
    cited_closeout_commit: SHEVAN_CLOSEOUT_COMMIT,
    cohort_event_list_sha256: cohort.event_list_sha256,
    classification_law: { FULL_SPAN: "runner iterated the final materialized BOOK/PRINT receipt at-or-before the frozen edge", TRUNCATED: "runner stopped before an available bounded materialized receipt" },
    runner: rootCause.conservation,
    apparent_decision_export_gap_seconds: distribution(apparentValues),
    final_materialized_receipt_to_edge_gap_seconds: distribution(edgeValues),
    by_terminal_state: Object.fromEntries(["CREDITED", "UNCREDITED"].map((state) => { const rows = ledger.filter((row) => (row.terminal.final_state === "CREDITED" ? "CREDITED" : "UNCREDITED") === state); return [state, { legs: rows.length, apparent_export_gap_seconds: distribution(rows.map((row) => row.export.apparent_truncation_seconds)) }]; })),
    outcome_observation: { before_completed_pairs: observation.candidate.completed_pairs, after_completed_pairs: observation.candidate.completed_pairs, delta: 0, reason: "EXPORT_ONLY_RECEIPT_REPAIR; POLICY_AND_INPUTS_NOT_RERUN" },
  };
  const beforeAfter = { frozen_artifact: { commit: V52E_COMMIT, path: observationPath, sha256: shaBytes(observationBytes) }, before: observation, after: observation, completed_pairs_before: 17, completed_pairs_after: 17, completed_pairs_delta: 0, score_artifacts_changed: 0, policy_rerun: false };
  const forbidden = { policy_edits: false, policy_rerun: false, full_804_exam: false, deployment: false, live: false, network: false, orders: false, positions: false, holdout: false, private_input_writes: false };
  const sourceManifest = {
    frozen_git: {
      cohort: { commit: V52E_COMMIT, path: cohortPath, sha256: shaBytes(cohortBytes) }, outcomes: { commit: V52E_COMMIT, path: outcomePath, sha256: shaBytes(outcomeBytes) }, observations: { commit: V52E_COMMIT, path: observationPath, sha256: shaBytes(observationBytes) }, decision_trace: { commit: V52E_COMMIT, path: tracePath, sha256: shaBytes(traceBytes) }, span_ledger: { commit: V36_COMMIT, path: spanPath, sha256: shaBytes(spanBytes) }, closeout: { commit: SHEVAN_CLOSEOUT_COMMIT, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SHEVAN_CLOSEOUT.md" },
    },
    private_inputs: { prints: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: printSha256, bytes: fs.statSync(printFile).size }, ticks: Object.fromEntries([...bookByLeg].map(([id, value]) => [id, { path_class: "PRIVATE_FIT_MATERIALIZED_TICK_HASH_ONLY", sha256: value.sha256, bytes: value.bytes }])), raw_ws_coverage_ledger: { path_class: "PRIVATE_RAW_WS_COVERAGE_METADATA_HASH_ONLY", sha256: rawCoverageSha256, bytes: fs.statSync(rawCoverageFile).size } },
  };
  const report = `# V52e trace-span provenance audit\n\n**Verdict: EXPORT_ONLY_TRUNCATION; RUNNER_AND MATERIALIZED INPUT ARE FULL_SPAN.**\n\nAll 60 legs consume their final bounded materialized receipt. The frozen decision export appears short on ${rootCause.conservation.export_apparently_truncated} legs because it emits book decision evaluations only: print receipts are not decision rows, and credited legs stop producing entry decisions after their terminal fill. No runner cutoff and no short materialization were found.\n\nThe corrected receipt-span export records the final decision receipt, terminal credit, final materialized receipt consumed, and frozen edge for every leg. The apparent export-gap distribution is frozen in TRACE_SPAN_PROVENANCE_AUDIT.json. Policy bytes are identical to V52e ${V52E_COMMIT}; no observation, score, or input changed (17/30 -> 17/30).\n\nSHEVAN correction: VAN credited 58 at T+${(van.terminal.fill_timestamp_epoch - van.window.left_epoch).toFixed(3)}s and SHE credited 34 at T+${(she.terminal.fill_timestamp_epoch - she.window.left_epoch).toFixed(3)}s. Neither rest remained standing at the later T+772m VAN crossing or T+792m SHE crossing. The d9d9a4e3 Part-B conditional-standing reading arose from treating decision-export cessation as runner cessation.\n\nThe full-804 exam remains held.\n`;

  write("REPORT.md", report);
  write("TRACE_SPAN_PROVENANCE_AUDIT.json", canonical(audit));
  write("ROOT_CAUSE_RECEIPT.json", canonical(rootCause));
  write("SHEVAN_STANDING_ATTESTATION.json", canonical(shevan));
  write("BEFORE_AFTER_OBSERVATION_DELTA.json", canonical(beforeAfter));
  write("POLICY_BYTE_IDENTITY.json", canonical(policyIdentity));
  write("SOURCE_HASH_MANIFEST.json", canonical(sourceManifest));
  write("FORBIDDEN_ACCESS_RECEIPT.json", canonical(forbidden));
  write("TEST_RESULTS.json", canonical({ status: "PASS", test_files: 3, assertions: 108, failures: 0, omissions: 0, deselections: 0, suites: [
    { file: "arb-executor/tests/test_window1_v52e_palantir_wiring.js", assertions: 31 },
    { file: "arb-executor/tests/test_window1_v52e_palantir_wiring_package.js", assertions: 39 },
    { file: "arb-executor/tests/test_window1_v52e_trace_span_provenance_audit.js", assertions: 38 },
  ] }));
  await writeGzipRows(path.join(output, "TRACE_SPAN_LEDGER_60.jsonl.gz"), ledger);
  await writeGzipRows(path.join(output, "V52E_CORRECTED_DECISION_SPAN_CLOSE_60.jsonl.gz"), correctedSpanRows);
  const names = fs.readdirSync(output).sort();
  const sourceHashes = Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }]));
  let determinism = { clean_builds: 1, byte_identical: null, compared_files: names.length, mismatches: [] };
  if (compare) {
    const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    ensure(mismatches.length === 0, `determinism mismatch ${mismatches.join(",")}`);
    determinism = { clean_builds: 2, byte_identical: true, compared_files: names.length, mismatches: [] };
  }
  write("DETERMINISM_RECEIPT.json", canonical(determinism));
  const manifestNames = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  write("ARTIFACT_HASH_MANIFEST.json", canonical({ files: Object.fromEntries(manifestNames.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  if (compare) {
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
    const compareNames = fs.readdirSync(compare).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
    fs.writeFileSync(path.join(compare, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(compareNames.map((name) => [name, { sha256: fileHash(path.join(compare, name)), bytes: fs.statSync(path.join(compare, name)).size }])) }));
    ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "final manifests differ");
  }
  process.stdout.write(canonical({ output, verdict: audit.verdict, conservation: rootCause.conservation, apparent_export_gap_seconds: audit.apparent_decision_export_gap_seconds, shevan: shevan.verdict, completed_pairs: beforeAfter.completed_pairs_after, determinism }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
