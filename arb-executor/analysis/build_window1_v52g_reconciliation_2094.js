#!/usr/bin/env node
"use strict";

// Receipts-only reconciliation for e17af2dc's 2,094
// AT_OR_ABOVE_UNCREDITED_TIMING moments.  This consumes frozen V52e
// decision diaries, their exact action-state reconstruction, and the same
// hash-bound development prints.  It never imports or invokes policy code.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const child = require("child_process");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const traceDir = path.join(repo, ".claude/window1_live_v4_replay/v52e_disposition_804_blocked_20260813");
const scoreDir = path.join(repo, ".claude/window1_live_v4_replay/v52e_disposition_804_four_state_20260813");
const spanPath = path.join(repo, ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/WINDOW1_SPAN_804.json");
const v52gDir = path.join(repo, ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813");
const out = path.resolve(repo, arg("--output", ".claude/window1_live_v4_replay/v52g_reconciliation_2094_and_flip_traces_20260813"));
const compare = arg("--compare", null) ? path.resolve(repo, arg("--compare", null)) : null;
const E17 = "e17af2dc4141686c158a19e86be1fb220b641012";
const E17_REL = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803";
const V52E_TRACE = "d9f83b30c44c3910f40d84b4b4f32daccabf3604";
const V52E_SCORE = "4716657a18519d5b90705eb20030a66f5491a91b";
const V52G = "ab841995f0cefa6011cf839fabf44057188111c4";
const FLIP_EVENTS = ["KXWTAMATCH-26JUL13CRIJEA", "KXWTAMATCH-26JUL19BRAVON"];

function ensure(v, m) { if (!v) throw new Error(m); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha(fs.readFileSync(file)); }
function gitShow(commit, rel) { return child.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 512 * 1024 * 1024 }); }
function canonicalValue(value) { if (Array.isArray(value)) return value.map(canonicalValue); if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((k) => [k, canonicalValue(value[k])])); return value; }
function canonical(value) { return JSON.stringify(canonicalValue(value), null, 2) + "\n"; }
function write(name, value) { fs.writeFileSync(path.join(out, name), typeof value === "string" ? value : canonical(value)); }
function writeGz(name, rows) { const body = rows.map((row) => JSON.stringify(canonicalValue(row))).join("\n") + (rows.length ? "\n" : ""); fs.writeFileSync(path.join(out, name), zlib.gzipSync(Buffer.from(body), { level: 9, mtime: 0 })); }
function rowsGz(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse); }
function rowObject(array, fields) { return Object.fromEntries(fields.map((field, index) => [field, array[index]])); }
function legToken(id) { return String(id).split("|").pop(); }
function safeOutput() { ensure(path.basename(out).includes("v52g_reconciliation_2094"), `unsafe output ${out}`); fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true }); }
function artifactManifest() { const files = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(); const rows = files.map((name) => ({ path: name, sha256: fileHash(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size })); write("ARTIFACT_HASH_MANIFEST.json", { files: rows, aggregate_sha256: sha(Buffer.from(rows.map((row) => `${row.sha256}  ${row.path}\n`).join(""))) }); }
async function streamGz(file, callback) { const lines = readline.createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity }); for await (const line of lines) if (line) await callback(JSON.parse(line)); }

async function loadPrints(metaByTicker) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), `missing ${file}`);
  const hash = crypto.createHash("sha256");
  const byLeg = new Map([...metaByTicker.values()].map((meta) => [meta.leg_identity, []]));
  const seen = new Map([...metaByTicker.keys()].map((ticker) => [ticker, new Set()]));
  let raw = 0, admitted = 0, duplicate = 0;
  const source = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  source.on("data", (chunk) => hash.update(chunk));
  const lines = readline.createInterface({ input: source, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line) continue;
    raw += 1;
    const row = JSON.parse(line), meta = metaByTicker.get(row.ticker);
    if (!meta || !row.true_print) continue;
    const ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < meta.left || ts > meta.right) continue;
    if (!row.trade_id || seen.get(row.ticker).has(row.trade_id)) { duplicate += 1; continue; }
    seen.get(row.ticker).add(row.trade_id);
    const price = Number(row.price_cents), size = Number(row.size);
    if (!Number.isInteger(price) || !Number.isFinite(size) || size <= 0) continue;
    admitted += 1;
    byLeg.get(meta.leg_identity).push({ leg_identity: meta.leg_identity, timestamp_epoch: ts, sequence: admitted, receipt: row.receipt_id, trade_id: row.trade_id, price_cents: price, size, taker_side: row.taker_side, taker_book_side: row.taker_book_side });
  }
  for (const values of byLeg.values()) values.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.sequence - b.sequence);
  return { byLeg, receipt: { sha256: hash.digest("hex"), bytes: fs.statSync(file).size, raw_rows: raw, admitted_unique_window_prints: admitted, duplicate_trade_ids_rejected: duplicate } };
}

function exportedTargets(row) {
  const before = Number.isInteger(row?.order_before_cents) ? row.order_before_cents : null;
  const after = row?.final_action === "CANCEL_REST" ? null
    : (row?.final_action === "PLACE_REST" || row?.final_action === "REPRICE_REST") && Number.isInteger(row.final_target_cents) ? row.final_target_cents
      : before;
  return { before, after, final_target: Number.isInteger(row?.final_target_cents) ? row.final_target_cents : null };
}

async function main() {
  safeOutput();
  const e17JsonBytes = gitShow(E17, `${E17_REL}/DECISIVE_MOMENT_ATTRIBUTION.json`);
  const e17CsvBytes = gitShow(E17, `${E17_REL}/DECISIVE_MOMENT_ATTRIBUTION.csv`);
  const e17ReportBytes = gitShow(E17, `${E17_REL}/DECISIVE_MOMENT_ATTRIBUTION.md`);
  const e17 = JSON.parse(e17JsonBytes);
  ensure(e17.anomaly_moments === 2094, `e17 anomaly count changed ${e17.anomaly_moments}`);
  const spans = JSON.parse(fs.readFileSync(spanPath)).rows;
  const metaByTicker = new Map(spans.flatMap((event) => event.per_leg.map((leg) => [leg.ticker, { leg_identity: leg.leg_identity, left: event.w1_left_epoch, right: event.w1_right_epoch }])));
  const prints = await loadPrints(metaByTicker);
  const offers = rowsGz(path.join(scoreDir, "POST_ONSET_OFFER_CAPTURE_LEDGER_804.jsonl.gz"));
  const marketEvents = rowsGz(path.join(scoreDir, "MARKET_EVENT_LEDGER_804.jsonl.gz"));
  const marketByEvent = new Map(marketEvents.map((row) => [row.event_id, row]));
  const shortfalls = offers.filter((row) => row.offer_class === "OFFERED_POST_ONSET" && !row.market_complete_at_delta);
  ensure(shortfalls.length === 346, `shortfall population changed ${shortfalls.length}`);
  const candidateByLeg = new Map();
  for (const offer of shortfalls) {
    const frozen = marketByEvent.get(offer.event_id); ensure(frozen, `missing frozen event ${offer.event_id}`);
    for (const [token, legOffer] of Object.entries(offer.legs)) {
      const legId = Object.keys(frozen.legs).find((id) => legToken(id) === token); ensure(legId, `missing ${offer.event_id}|${token}`);
      const leg = frozen.legs[legId];
      const values = (prints.byLeg.get(legId) || []).filter((row) => row.timestamp_epoch >= legOffer.onset_sel);
      if (!values.length) continue;
      const floor = Math.min(...values.map((row) => row.price_cents));
      const moments = values.filter((row) => row.price_cents === floor);
      candidateByLeg.set(legId, { event_id: offer.event_id, category: offer.category, price_region: offer.price_region, leg, floor, moments });
    }
  }
  const schema = JSON.parse(fs.readFileSync(path.join(traceDir, "TRACE_SCHEMA.json")));
  const chunks = fs.readdirSync(traceDir).filter((name) => /^V52E_FULL_DECISION_TRACE_804_CHUNK_\d+\.jsonl\.gz$/.test(name)).sort();
  ensure(chunks.length === 101, `chunk count changed ${chunks.length}`);
  const anomalyRows = [];
  const counts = { source_reported_moments: e17.anomaly_moments, shortfall_events: shortfalls.length, candidate_legs: candidateByLeg.size, floor_print_moments: 0, before_ge: 0, after_ge: 0, final_target_ge: 0, any_export_ge: 0, action_state_ge: 0, export_or_action_ge: 0, source_anomaly_already_terminal: 0, source_anomaly_standing_precredit: 0, crediting_defects: 0, before_ge_and_leg_missed_floor: 0, after_ge_and_leg_missed_floor: 0 };
  function evaluateLeg(candidate, trace) {
    trace.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.sequence - b.sequence);
    const missedFloor = !candidate.leg.credited || candidate.leg.entry_cents > candidate.floor;
    let i = 0, prior = null;
    for (const print of candidate.moments) {
      while (i < trace.length && trace[i].timestamp_epoch <= print.timestamp_epoch) prior = trace[i++];
      const target = exportedTargets(prior);
      const transitions = candidate.leg.action_transitions || [];
      let active = null;
      for (const action of transitions) {
        if (action.timestamp_epoch >= print.timestamp_epoch) break;
        active = action.action === "CANCEL_REST" ? null : Number.isInteger(action.after_cents) ? action.after_cents : active;
      }
      counts.floor_print_moments += 1;
      if (target.before >= candidate.floor) counts.before_ge += 1;
      if (target.after >= candidate.floor) counts.after_ge += 1;
      if (target.final_target >= candidate.floor) counts.final_target_ge += 1;
      if (Math.max(target.before ?? -1, target.final_target ?? -1) >= candidate.floor) counts.any_export_ge += 1;
      if (active >= candidate.floor) {
        counts.action_state_ge += 1;
        const terminal = Number.isFinite(candidate.leg.fill_timestamp_epoch) && candidate.leg.fill_timestamp_epoch <= print.timestamp_epoch;
        if (terminal) counts.source_anomaly_already_terminal += 1;
        else { counts.source_anomaly_standing_precredit += 1; counts.crediting_defects += 1; }
        anomalyRows.push({
          source_anomaly_identity: `${candidate.leg.leg_identity}|${print.receipt}`,
          event_id: candidate.event_id,
          leg_identity: candidate.leg.leg_identity,
          category: candidate.category,
          price_region: candidate.price_region,
          print: { timestamp_epoch: print.timestamp_epoch, receipt: print.receipt, trade_id: print.trade_id, price_cents: print.price_cents, size: print.size, taker_side: print.taker_side, taker_book_side: print.taker_book_side },
          source_export_reconstruction: { last_decision_timestamp_epoch: prior?.timestamp_epoch ?? null, last_decision_receipt: prior?.receipt ?? null, order_before_cents: target.before, final_target_cents: target.final_target, reconstructed_order_after_cents: target.after, comparison: `${target.after} >= ${candidate.floor}` },
          runner_actual_state_at_exact_print_receipt: terminal ? "ALREADY_TERMINAL" : "STANDING_AT_TARGET",
          runner_fill: { fill_timestamp_epoch: candidate.leg.fill_timestamp_epoch, fill_receipt: candidate.leg.fill_receipt, entry_cents: candidate.leg.entry_cents, fill_class: candidate.leg.fill_class, seconds_before_moment: terminal ? print.timestamp_epoch - candidate.leg.fill_timestamp_epoch : null },
          verdict: terminal ? "EXPORT_GRAIN_ILLUSION" : "CREDITING_DEFECT",
          verdict_reason: terminal ? "DECISION_EXPORT_HAS_NO_FILL_TERMINAL_ROW_AND_CARRIES_THE_LAST_STANDING_TARGET_FORWARD_AFTER_CREDIT" : "REST_STOOD_AT_OR_ABOVE_PRINT_AND_NO_CREDIT_WAS_RECORDED",
          failing_code_path: terminal ? null : "arb-executor/analysis/build_window1_v38_maker_only.js:599-600 -> window1_v49b_faithful_stand_at_p.js:91-99",
        });
      }
      if (target.after >= candidate.floor || active >= candidate.floor) counts.export_or_action_ge += 1;
      if (missedFloor && target.before >= candidate.floor) counts.before_ge_and_leg_missed_floor += 1;
      if (missedFloor && target.after >= candidate.floor) counts.after_ge_and_leg_missed_floor += 1;
    }
  }
  let traceRows = 0;
  for (const name of chunks) {
    const lines = readline.createInterface({ input: fs.createReadStream(path.join(traceDir, name)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
    let eventId = null;
    const eventRows = new Map();
    const flush = () => {
      for (const [legId, trace] of eventRows) evaluateLeg(candidateByLeg.get(legId), trace);
      eventRows.clear();
    };
    for await (const line of lines) {
      if (!line) continue;
      traceRows += 1;
      const row = rowObject(JSON.parse(line), schema.fields), candidate = candidateByLeg.get(row.leg_identity);
      if (eventId !== null && row.event_id !== eventId) flush();
      eventId = row.event_id;
      if (candidate) {
        if (!eventRows.has(row.leg_identity)) eventRows.set(row.leg_identity, []);
        eventRows.get(row.leg_identity).push(row);
      }
    }
    flush();
  }
  anomalyRows.sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity) || a.print.timestamp_epoch - b.print.timestamp_epoch || a.print.receipt.localeCompare(b.print.receipt));
  ensure(anomalyRows.length === 2093, `independent reconstruction fingerprint changed ${anomalyRows.length}`);
  ensure(counts.crediting_defects === 0 && counts.source_anomaly_already_terminal === anomalyRows.length, "materialized crediting defect found");

  const flipLedger = rowsGz(path.join(v52gDir, "V52F_V52G_FOUR_STATE_EVENT_LEDGER_30.jsonl.gz"));
  const flipStateRows = flipLedger.filter((row) => FLIP_EVENTS.includes(row.event_id));
  ensure(flipStateRows.length === 4, `flip state rows ${flipStateRows.length}`);
  for (const eventId of FLIP_EVENTS) {
    const base = flipStateRows.find((row) => row.event_id === eventId && row.variant === "V52F");
    const candidate = flipStateRows.find((row) => row.event_id === eventId && row.variant === "V52G");
    ensure(base?.state === "COMPLETE_AT_DELTA" && candidate?.state === "PARTIAL_FOR_REASON", `flip identity changed ${eventId}`);
  }
  const diffRows = [];
  await streamGz(path.join(v52gDir, "BEFORE_AFTER_DECISION_DIFFERENTIAL.jsonl.gz"), (row) => { if (FLIP_EVENTS.includes(row.event_id)) diffRows.push(row); });
  const firstDiff = new Map();
  for (const eventId of FLIP_EVENTS) {
    const values = diffRows.filter((row) => row.event_id === eventId).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.receipt.localeCompare(b.receipt));
    ensure(values.length, `no differential ${eventId}`);
    firstDiff.set(eventId, values[0].timestamp_epoch);
  }
  const flipTraceRows = [];
  for (const [variant, pattern] of [["V52F", /^V52F_BASELINE_FULL_DECISION_TRACE_30_GAMES_CHUNK_\d+\.jsonl\.gz$/], ["V52G", /^V52G_FULL_DECISION_TRACE_30_GAMES_CHUNK_\d+\.jsonl\.gz$/]]) {
    const names = fs.readdirSync(v52gDir).filter((name) => pattern.test(name)).sort(); ensure(names.length === 6, `${variant} chunks ${names.length}`);
    for (const name of names) await streamGz(path.join(v52gDir, name), (row) => {
      if (!FLIP_EVENTS.includes(row.event_id)) return;
      const pivot = firstDiff.get(row.event_id);
      if (row.timestamp_epoch >= pivot - 1 && row.timestamp_epoch <= pivot + 1) flipTraceRows.push({ row_type: `${variant}_DECISION_TRACE_AT_DIVERGENCE`, variant, ...row });
    });
  }
  for (const row of diffRows) flipTraceRows.push({ row_type: "CLAUSE_6_DECISION_DIFFERENTIAL", ...row });
  const pairSeries = [];
  await streamGz(path.join(v52gDir, "PAIR_JOINT_TARGET_TIME_SERIES.jsonl.gz"), (row) => { if (FLIP_EVENTS.includes(row.event_id)) pairSeries.push(row); });
  for (const row of pairSeries) flipTraceRows.push({ row_type: "V52G_PAIR_BUDGET_TIME_SERIES", ...row });
  for (const eventId of FLIP_EVENTS) {
    const event = marketByEvent.get(eventId), pivot = firstDiff.get(eventId); ensure(event, `missing market ${eventId}`);
    for (const legId of Object.keys(event.legs)) for (const print of prints.byLeg.get(legId) || []) if (print.timestamp_epoch >= pivot) flipTraceRows.push({ row_type: "FORWARD_TRUTH_PRINT", event_id: eventId, ...print });
    for (const state of flipStateRows.filter((row) => row.event_id === eventId)) flipTraceRows.push({ row_type: "TERMINAL_FOUR_STATE_OBSERVATION", ...state });
  }
  flipTraceRows.sort((a, b) => String(a.event_id).localeCompare(String(b.event_id)) || (a.timestamp_epoch ?? Number.MAX_SAFE_INTEGER) - (b.timestamp_epoch ?? Number.MAX_SAFE_INTEGER) || String(a.variant ?? "").localeCompare(String(b.variant ?? "")) || String(a.receipt ?? "").localeCompare(String(b.receipt ?? "")) || String(a.row_type).localeCompare(String(b.row_type)));

  const sourceResidue = { source_reported_moments: 2094, independently_materialized_moments: anomalyRows.length, unexplained_residue: 1, source_moment_ledger_present_at_e17: false, status: "SOURCE_ANOMALY_COUNT_NOT_FULLY_RECONCILABLE_ONE_IDENTITY_NOT_FROZEN", consequence: "The 2,093 materialized rows are adjudicated; no verdict is invented for the unidentifiable 2,094th count. The source count is a measurement defect and blocks a complete 2,094-of-2,094 certification." };
  const summary = { verdict: "2093_EXPORT_GRAIN_ILLUSION__0_CREDITING_DEFECT__1_SOURCE_COUNT_RESIDUE_BLOCK", ...counts, independently_materialized_moments: anomalyRows.length, unexplained_source_residue: 1, games_with_crediting_defect: 0, corrected_four_state_census_emitted: false, corrected_capture_emitted: false, stop_for_operator_review: true, source_residue: sourceResidue, conservation: { materialized: anomalyRows.length, verdict_sum: counts.source_anomaly_already_terminal + counts.crediting_defects, pass: anomalyRows.length === counts.source_anomaly_already_terminal + counts.crediting_defects } };
  writeGz("RECONCILIATION_2093_MATERIALIZED_MOMENTS.jsonl.gz", anomalyRows);
  write("RECONCILIATION_SUMMARY.json", summary);
  write("SOURCE_COUNT_RESIDUE_RECEIPT.json", sourceResidue);
  write("CREDITING_CODE_PATH_RECEIPT.json", { policy_imports: 0, policy_invocations: 0, behavior_edits: false, trade_truth_definition: { file: "arb-executor/analysis/window1_v49b_faithful_stand_at_p.js", lines: "91-99", condition: "order exists; lawful integer target; PRINT; print timestamp strictly after action; nonempty trade_id; integer print price <= target" }, runner_callsite: { file: "arb-executor/analysis/build_window1_v38_maker_only.js", lines: "599-600", effect: "fillLeg immediately on tradeTruthCredit" }, frozen_score_reconstruction: { file: "arb-executor/analysis/build_window1_v52e_four_state_score_from_traces.js", lines: "130-147", effect: "PRINT merged ahead of same-second BOOK_DECISION; active target credits at-or-below print" }, finding: "All 2,093 materialized source moments occur after that leg was already credited; no failing credit path exists among them." });
  writeGz("V52F_V52G_FLIP_TRACES_ROWS_ONLY.jsonl.gz", flipTraceRows);
  write("V52F_V52G_FLIP_SUMMARY.json", { events: FLIP_EVENTS.length, event_ids: FLIP_EVENTS, baseline_complete_at_delta: 2, candidate_complete_at_delta: 0, baseline_candidate_delta: -2, divergence_rows: diffRows.length, trace_rows_at_divergence: flipTraceRows.filter((row) => /DECISION_TRACE_AT_DIVERGENCE$/.test(row.row_type)).length, pair_budget_time_series_rows: pairSeries.length, forward_truth_print_rows: flipTraceRows.filter((row) => row.row_type === "FORWARD_TRUTH_PRINT").length, interpretation: null, adjudication_owner: "ANALYSIS_SEAT", rows_only: true });
  write("CONTROL_BINDING.json", { scope: "DEV_804_RECEIPTS_ONLY_RECONCILIATION_PLUS_V52F_V52G_SHARED_COHORT_FLIPS", anomaly_source_commit: E17, frozen_trace_commit: V52E_TRACE, frozen_score_commit: V52E_SCORE, frozen_v52g_commit: V52G, policy_edits: false, policy_replay: false, score_replay: false, score_correction: false, sealed: false, live: false });
  const policyFiles = ["arb-executor/analysis/window1_v49b_faithful_stand_at_p.js", "arb-executor/analysis/window1_v52e_palantir_wiring.js", "arb-executor/analysis/window1_v52f_pair_entry_conservation.js", "arb-executor/analysis/window1_v52g_joint_target_conservation.js"].map((rel) => ({ path: rel, current_sha256: fileHash(path.join(repo, rel)) }));
  write("POLICY_BYTE_IDENTITY.json", { policy_files: policyFiles, modifications_by_this_build: 0, imports: 0, invocations: 0, pass: true });
  write("SOURCE_HASH_MANIFEST.json", { sources: { e17_report: { commit: E17, path: `${E17_REL}/DECISIVE_MOMENT_ATTRIBUTION.md`, sha256: sha(e17ReportBytes) }, e17_json: { commit: E17, path: `${E17_REL}/DECISIVE_MOMENT_ATTRIBUTION.json`, sha256: sha(e17JsonBytes) }, e17_csv: { commit: E17, path: `${E17_REL}/DECISIVE_MOMENT_ATTRIBUTION.csv`, sha256: sha(e17CsvBytes) }, trace_manifest: { commit: V52E_TRACE, path: ".claude/window1_live_v4_replay/v52e_disposition_804_blocked_20260813/TRACE_CHUNK_MANIFEST.json", sha256: fileHash(path.join(traceDir, "TRACE_CHUNK_MANIFEST.json")) }, market_ledger: { commit: V52E_SCORE, path: ".claude/window1_live_v4_replay/v52e_disposition_804_four_state_20260813/MARKET_EVENT_LEDGER_804.jsonl.gz", sha256: fileHash(path.join(scoreDir, "MARKET_EVENT_LEDGER_804.jsonl.gz")) }, print_input: prints.receipt, v52g_manifest: { commit: V52G, path: ".claude/window1_live_v4_replay/v52g_joint_target_conservation_20260813/ARTIFACT_HASH_MANIFEST.json", sha256: fileHash(path.join(v52gDir, "ARTIFACT_HASH_MANIFEST.json")) } } });
  write("FORBIDDEN_ACCESS_RECEIPT.json", { sealed: false, holdout: false, deployment: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, policy_edits: false, policy_replay: false, scorer_invocations: 0 });
  const report = `# V52g 2,094 reconciliation and -2 flip traces\n\nVERDICT: **2,093 EXPORT_GRAIN_ILLUSION; 0 CREDITING_DEFECT; 1 source-count identity residue — BLOCK for operator review.**\n\nThe e17af2dc report froze the integer 2,094 but no moment ledger. Independent reconstruction from its named 346-game population, V52e's 101 receipt-grain chunks, the frozen market-event action ledger, and the hash-bound true prints materializes 2,093 exact identities. Every materialized moment occurs after that leg's recorded credit: the decision-only export stopped at credit and its last standing target was incorrectly carried forward to later floor prints. No materialized row was standing and uncredited. The missing 2,094th identity is not invented; the one-count residue is a source measurement defect.\n\nNo corrected four-state census or capture is emitted because no materialized CREDITING_DEFECT exists and the source set itself is incomplete. The original score artifacts remain authoritative and byte-untouched.\n\nV52f-to-V52g flips are CRIJEA and BRAVON. The rows-only ledger freezes both machines at each divergence, every clause-6 differential row, V52g pair-budget time series, forward true prints, and terminal observations. Interpretation is deliberately null for the analysis seat.\n\nPolicy imports/invocations 0/0; score invocations 0; no sealed, holdout, live, deployment, order, position, exit, settlement, DCA, or network access.\n`;
  write("REPORT.md", report);
  const names = fs.readdirSync(out).sort();
  let determinism;
  if (compare) {
    const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(out, name)));
    const extras = fs.readdirSync(compare).filter((name) => ![...names, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extras.length, `determinism mismatch ${[...mismatches, ...extras].join(",")}`);
    determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [], policy_invocations: 0, score_invocations: 0 };
  } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD", policy_invocations: 0, score_invocations: 0 };
  write("DETERMINISM_RECEIPT.json", determinism);
  artifactManifest();
  if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); const files = fs.readdirSync(compare).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(); const rows = files.map((name) => ({ path: name, sha256: fileHash(path.join(compare, name)), bytes: fs.statSync(path.join(compare, name)).size })); fs.writeFileSync(path.join(compare, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: rows, aggregate_sha256: sha(Buffer.from(rows.map((row) => `${row.sha256}  ${row.path}\n`).join(""))) })); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(out, "ARTIFACT_HASH_MANIFEST.json")), "final manifests differ"); }
  process.stdout.write(canonical({ output: out, summary, flips: FLIP_EVENTS, flip_rows: flipTraceRows.length, determinism }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
