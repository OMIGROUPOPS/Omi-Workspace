#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const argv = process.argv.slice(2);
const arg = (name, fallback = null) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const required = (name) => { const value = arg(name); if (!value) throw new Error(`${name} required`); return value; };
const repo = path.resolve(arg("--repo", path.join(__dirname, "../..")));
const results = path.resolve(required("--results"));
const declarationFile = path.resolve(required("--population-declaration"));
const boundaryFile = path.resolve(required("--boundary-ledger"));
const printsFile = path.resolve(required("--prints"));
const oldTapeRoot = path.resolve(required("--old-tape-root"));
const newTapeRoot = path.resolve(required("--new-tape-root"));
const output = path.resolve(required("--output"));

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha(fs.readFileSync(file)); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function readJsonl(file) { const text = fs.readFileSync(file, "utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function readGzipRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function parseEt(value) { const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = +m[4]; if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function csv(value) { if (value === null || value === undefined) return ""; const text = typeof value === "object" ? JSON.stringify(value) : String(value); return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text; }
function walkFiles(root) { const files = {}; const walk = (dir) => { for (const item of fs.readdirSync(dir, { withFileTypes: true })) { const full = path.join(dir, item.name); if (item.isDirectory()) walk(full); else { const rel = path.relative(root, full).replaceAll("\\", "/"); files[rel] = { sha256: hashFile(full), bytes: fs.statSync(full).size }; } } }; walk(root); return files; }

function tapeRoot(leg) {
  if (leg.private_root_class === "HOLDOUT_EXAM_20260807_TAPES") return oldTapeRoot;
  if (leg.private_root_class === "V47_EXAM_NEW_CAPTURE_TAPES") return newTapeRoot;
  throw new Error(`unknown tape class ${leg.private_root_class}`);
}

function loadTape(leg) {
  const file = path.join(tapeRoot(leg), leg.path_basename);
  ensure(fs.existsSync(file), `missing tape ${leg.ticker}`);
  ensure(hashFile(file) === leg.sha256 && fs.statSync(file).size === leg.bytes, `tape mismatch ${leg.ticker}`);
  const lines = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trimEnd().split(/\r?\n/);
  const header = lines.shift().split(","), ix = Object.fromEntries(header.map((value, index) => [value, index]));
  const rows = [];
  for (let n = 0; n < lines.length; n += 1) {
    const cells = lines[n].split(","), ts = parseEt(cells[ix.ts_et]);
    if (!Number.isFinite(ts) || ts < leg.authoritative_from_epoch || ts > leg.authoritative_through_epoch) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(cells[ix[`bid_${level}`]]), bs = positive(cells[ix[`bid_${level}_sz`]]), ap = integer(cells[ix[`ask_${level}`]]), as = positive(cells[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    const bidDepth = bids.reduce((sum, row) => sum + row[1], 0), askDepth = asks.reduce((sum, row) => sum + row[1], 0);
    rows.push({ ticker: leg.ticker, ts, ordinal: n + 2, receipt: `${leg.path_basename}#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], last_traded: integer(cells[ix.last_trade]), spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bidDepth, ask_depth_5: askDepth, depth_ratio: bidDepth / (bidDepth + askDepth) });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let priorAsk = null, askSince = null;
  for (const row of rows) { if (row.ask !== priorAsk) { priorAsk = row.ask; askSince = row.ts; } row.ask_dwell_seconds = row.ts - askSince; }
  return rows;
}

function atOrBefore(rows, ts) {
  let low = 0, high = rows.length - 1, found = null;
  while (low <= high) { const mid = (low + high) >> 1; if (rows[mid].ts <= ts) { found = rows[mid]; low = mid + 1; } else high = mid - 1; }
  return found;
}

function observation(row) {
  if (!row) return null;
  return { receipt: row.receipt, timestamp_epoch: row.ts, bid: row.bid, ask: row.ask, last_traded: row.last_traded, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_bid_size: row.top_bid_size, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5, depth_ratio: row.depth_ratio };
}

async function selectedPrints(tickers) {
  const result = new Map([...tickers].map((ticker) => [ticker, []]));
  const input = fs.createReadStream(printsFile, { highWaterMark: 1024 * 1024 });
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line) continue;
    const row = JSON.parse(line);
    if (!result.has(row.ticker)) continue;
    result.get(row.ticker).push(row);
  }
  for (const rows of result.values()) rows.sort((a, b) => Date.parse(a.exchange_ts) - Date.parse(b.exchange_ts) || String(a.trade_id).localeCompare(String(b.trade_id)));
  return result;
}

function outcome(event) { return Object.values(event.legs).filter((leg) => leg.credited).length; }
function reachGap(leg) { return Number.isInteger(leg.resting_target_at_edge_cents) && Number.isInteger(leg.union_reach_cents) ? leg.union_reach_cents - leg.resting_target_at_edge_cents : null; }

function selectGames(events, actions, declarations) {
  const byId = new Map(declarations.events.map((event) => [event.event_id, event]));
  const guardCount = (event) => actions.filter((row) => row.event_id === event.event_id && ["DEEP_GAP_WITHHOLD_START", "DEEP_GAP_WITHHOLD_LIFT", "CANCEL_REST"].includes(row.kind)).length;
  const used = new Set(), take = (role, rows) => { const event = rows.find((row) => !used.has(row.event_id)); ensure(event, `no selection ${role}`); used.add(event.event_id); return { role, event_id: event.event_id }; };
  const completed = events.filter((event) => outcome(event) === 2);
  const oneLeg = events.filter((event) => outcome(event) === 1);
  const zero = events.filter((event) => outcome(event) === 0);
  const picks = [];
  picks.push(take("COMPLETED_DEEP_EXACT", completed.filter((event) => event.bell_confidence === "exact").sort((a, b) => a.combined_entry_cents - b.combined_entry_cents || a.event_id.localeCompare(b.event_id))));
  picks.push(take("COMPLETED_MAX_GUARD_LIFECYCLE", completed.slice().sort((a, b) => guardCount(b) - guardCount(a) || a.event_id.localeCompare(b.event_id))));
  picks.push(take("ONE_LEG_EXACT", oneLeg.filter((event) => event.bell_confidence === "exact").sort((a, b) => a.event_id.localeCompare(b.event_id))));
  picks.push(take("ONE_LEG_CAPTURE_STREAM", oneLeg.filter((event) => byId.get(event.event_id)?.source_partition === "STAGE_B_CAPTURE_ONLY_STREAM").sort((a, b) => a.event_id.localeCompare(b.event_id))));
  const far = zero.slice().sort((a, b) => {
    const score = (event) => Object.values(event.legs).reduce((sum, leg) => sum + Math.max(0, reachGap(leg) ?? 0), 0);
    return score(b) - score(a) || a.event_id.localeCompare(b.event_id);
  });
  picks.push(take("SKIP_FAR_FROM_REACH", far));
  const near = zero.filter((event) => Object.values(event.legs).every((leg) => Number.isInteger(reachGap(leg)) && Math.abs(reachGap(leg)) <= 2)).sort((a, b) => Object.values(a.legs).reduce((sum, leg) => sum + Math.abs(reachGap(leg)), 0) - Object.values(b.legs).reduce((sum, leg) => sum + Math.abs(reachGap(leg)), 0) || a.event_id.localeCompare(b.event_id));
  picks.push(take("NEAR_MISS", near));
  return picks;
}

function actionObservation(action, ownReceipts, allReceipts) {
  const direct = ownReceipts.get(action.receipt) || allReceipts.get(action.receipt);
  if (direct) return observation(direct);
  if (action.own_book) return { receipt: action.own_book_receipt || action.receipt, timestamp_epoch: action.timestamp_epoch, ...action.own_book };
  if (action.evidence) return { receipt: action.receipt, timestamp_epoch: action.timestamp_epoch, trade: action.evidence };
  return null;
}

function buildLegChain(event, leg, eventDeclaration, boundary, eventActions, eventJoins, tapes, prints) {
  const ownRows = tapes.get(leg.leg_id), siblingId = Object.keys(event.legs).find((id) => id !== leg.leg_id), siblingRows = tapes.get(siblingId), allRows = [...ownRows, ...siblingRows];
  const ownReceipts = new Map(ownRows.map((row) => [row.receipt, row])), allReceipts = new Map(allRows.map((row) => [row.receipt, row]));
  const actions = eventActions.filter((row) => row.leg_identity === leg.leg_identity).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.kind).localeCompare(String(b.kind)));
  const joins = eventJoins.filter((row) => row.leg_identity === leg.leg_identity).sort((a, b) => a.qualification_timestamp_epoch - b.qualification_timestamp_epoch);
  let priorTarget = null;
  const marks = actions.map((action, index) => {
    const own = actionObservation(action, ownReceipts, allReceipts), sibling = observation(atOrBefore(siblingRows, action.timestamp_epoch));
    const nextTarget = Number.isInteger(action.target_cents) ? action.target_cents : action.kind === "FILL" ? action.entry_cents : null;
    const row = { sequence: index + 1, layer: action.kind === "FILL" ? "L6_OUTCOME" : action.kind === "PAIR_ARM" || action.kind === "PAIR_CAP_REPRICE" ? "L3_PAIR_CAP" : action.kind === "PLACE_REST" ? "L4_POST" : ["REPRICE_REST", "CANCEL_REST"].includes(action.kind) ? "L5_WALK" : "L2_READ", kind: action.kind, timestamp_epoch: action.timestamp_epoch, t_minus_scheduled_seconds: action.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: action.t_minus_actual_bell_seconds, receipt: action.receipt, state_call: action.state ?? "SILENT_NOT_EMITTED_ON_THIS_ACTION", state_evidence: own ?? "SILENT_RECEIPT_NOT_BOOK_OR_PRINT", sibling_observation: sibling ?? "SILENT_NO_PRIOR_SIBLING_BOOK", prior_target_cents: priorTarget, target_cents: nextTarget, why: action.reason ?? action.guard?.reason ?? action.fill_class ?? action.kind, target_law: action.reason ?? action.guard?.reason ?? null, pair_cap_cents: action.pair_cap_cents ?? action.guard?.implied_sibling_cap_cents ?? null, fill_evidence: action.evidence ?? null, raw_action_receipt: action };
    if (["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE"].includes(action.kind) && Number.isInteger(nextTarget)) priorTarget = nextTarget;
    if (action.kind === "CANCEL_REST" || action.kind === "FILL") priorTarget = null;
    return row;
  });
  const finalAction = actions.find((row) => row.kind === "FILL") || null;
  const l1 = { layer: "L1_ADMIT", status: "PASS", why: "FROZEN_STAGE1_POPULATION_ADMISSION", event_id: event.event_id, ticker: leg.ticker, source_partition: eventDeclaration.source_partition, touch_classification: eventDeclaration.touch_classification, tape_sha256: eventDeclaration.legs.find((row) => row.ticker === leg.ticker).sha256, authoritative_from_epoch: eventDeclaration.legs.find((row) => row.ticker === leg.ticker).authoritative_from_epoch, authoritative_through_epoch: eventDeclaration.legs.find((row) => row.ticker === leg.ticker).authoritative_through_epoch, hard_right_edge_epoch: boundary.right_edge_epoch, precision_class: boundary.precision_class, edge_source_field: boundary.right_edge_source_field };
  const l2 = { layer: "L2_READ", mark_sequences: marks.filter((row) => row.layer !== "L6_OUTCOME").map((row) => row.sequence), constituent_quote_path_and_pressure_receipts: "SILENT_NOT_EMITTED_SEPARATELY_BY_FROZEN_V47_EXAM_TRACE", why: "combined state is carried on emitted action receipts; bid/ask/last/spread/dwell/depth are joined to the exact named tape receipt" };
  const l3 = { layer: "L3_TARGET", mark_sequences: marks.filter((row) => ["L3_PAIR_CAP", "L4_POST", "L5_WALK"].includes(row.layer) && Number.isInteger(row.target_cents)).map((row) => row.sequence), why: "target and named placement/cap law are copied from emitted action receipts" };
  const l4 = { layer: "L4_POST", mark_sequences: marks.filter((row) => row.kind === "PLACE_REST").map((row) => row.sequence), join_qualifications: joins, why: joins.length || marks.some((row) => row.kind === "PLACE_REST") ? "post and arming receipts emitted" : "SILENT_NO_POST_RECEIPT" };
  const l5 = { layer: "L5_WALK", mark_sequences: marks.filter((row) => ["REPRICE_REST", "PAIR_CAP_REPRICE", "CANCEL_REST"].includes(row.kind)).map((row) => row.sequence), why: marks.some((row) => ["REPRICE_REST", "PAIR_CAP_REPRICE", "CANCEL_REST"].includes(row.kind)) ? "every emitted reprice/cancel is preserved in execution order" : "SILENT_NO_REPRICE" };
  const l6 = { layer: "L6_OUTCOME", credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, fill_receipt: finalAction?.receipt ?? null, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_evidence: finalAction?.evidence ?? null, terminal_state: leg.final_state, terminal_reason: leg.terminal_reason, resting_target_at_edge_cents: leg.resting_target_at_edge_cents, union_reach_cents: leg.union_reach_cents, reach_gap_cents: reachGap(leg), true_print_receipts_for_leg: prints.length, why: leg.credited ? "emitted fill receipt" : "frozen terminal event row" };
  const silent = [];
  if (!l4.mark_sequences.length) silent.push("L4_POST");
  if (!l5.mark_sequences.length) silent.push("L5_WALK");
  if (!finalAction && leg.credited) silent.push("L6_FILL_RECEIPT_INCONSISTENT");
  if (l2.constituent_quote_path_and_pressure_receipts.startsWith("SILENT")) silent.push("L2_CONSTITUENT_DIRECTION_READS");
  return { leg_identity: leg.leg_identity, ticker: leg.ticker, L1: l1, L2: l2, L3: l3, L4: l4, L5: l5, L6: l6, execution_order_marks: marks, silent_layers_or_fields: silent };
}

async function build(root) {
  ensure(!fs.existsSync(root), `output exists ${root}`);
  fs.mkdirSync(root, { recursive: true });
  const complete = readJson(path.join(results, "EXECUTION_COMPLETE_RECEIPT.json"));
  ensure(complete.status === "COMPLETE_FINAL" && complete.score_emitting_runs === 1 && complete.population_N === 238, "frozen exam not complete");
  const declaration = readJson(declarationFile), boundaries = new Map(readJsonl(boundaryFile).map((row) => [row.event_id, row]));
  const eventLedgerFile = path.join(results, "SCORES/V47/MARKET_EVENT_LEDGER.jsonl.gz"), actionFile = path.join(results, "SCORES/V47/ACTION_TRACE.jsonl.gz"), joinFile = path.join(results, "SCORES/V47/JOIN_QUALIFICATION_TRACE.jsonl.gz");
  const events = readGzipRows(eventLedgerFile), actions = readGzipRows(actionFile).filter((row) => row.mode === "MARKET_TRADES_TRUTH"), joins = readGzipRows(joinFile).filter((row) => row.mode === "MARKET_UNION_REACH");
  ensure(events.length === 238, "event ledger conservation");
  const picks = selectGames(events, actions, declaration), selected = new Set(picks.map((row) => row.event_id));
  const tickers = new Set(declaration.events.filter((event) => selected.has(event.event_id)).flatMap((event) => event.legs.map((leg) => leg.ticker)));
  const prints = await selectedPrints(tickers), eventMap = new Map(events.map((event) => [event.event_id, event])), declarationMap = new Map(declaration.events.map((event) => [event.event_id, event]));
  const auditRows = [];
  for (const pick of picks) {
    const event = eventMap.get(pick.event_id), eventDeclaration = declarationMap.get(pick.event_id), boundary = boundaries.get(pick.event_id);
    ensure(event && eventDeclaration && boundary, `missing binding ${pick.event_id}`);
    const tapes = new Map(); for (const leg of eventDeclaration.legs) tapes.set(leg.leg_id, loadTape(leg));
    const eventActions = actions.filter((row) => row.event_id === event.event_id), eventJoins = joins.filter((row) => row.event_id === event.event_id);
    const chains = Object.fromEntries(Object.values(event.legs).sort((a, b) => a.leg_id.localeCompare(b.leg_id)).map((leg) => [leg.leg_id, buildLegChain(event, leg, eventDeclaration, boundary, eventActions, eventJoins, tapes, prints.get(leg.ticker) || [])]));
    const pack = { schema_version: "window1-v47-sealed-exam-why-chain-v1", role: pick.role, event: { event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, edge_source_field: event.edge_source_field, completed_pair: event.completed_pair, combined_entry_cents: event.combined_entry_cents, credited_legs: outcome(event), outcome_class: outcome(event) === 2 ? "COMPLETED" : outcome(event) === 1 ? "ONE_LEG" : pick.role === "NEAR_MISS" ? "NEAR_MISS" : "SKIP" }, chains, receipts_only: true, policy_rerun: false };
    const dir = path.join(root, event.event_id); fs.mkdirSync(dir, { recursive: true }); fs.writeFileSync(path.join(dir, "DECISION_MARKS.json"), canonical(pack));
    const columns = ["sequence", "event_id", "leg_identity", "layer", "kind", "timestamp_epoch", "t_minus_scheduled_seconds", "t_minus_actual_bell_seconds", "receipt", "state_call", "prior_target_cents", "target_cents", "why", "own_bid", "own_ask", "own_last", "own_spread", "own_dwell", "own_bid_depth_5", "own_ask_depth_5", "sibling_bid", "sibling_ask", "sibling_last", "sibling_spread", "sibling_dwell"];
    const timeline = Object.values(chains).flatMap((chain) => chain.execution_order_marks.map((mark) => ({ sequence: mark.sequence, event_id: event.event_id, leg_identity: chain.leg_identity, layer: mark.layer, kind: mark.kind, timestamp_epoch: mark.timestamp_epoch, t_minus_scheduled_seconds: mark.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: mark.t_minus_actual_bell_seconds, receipt: mark.receipt, state_call: mark.state_call, prior_target_cents: mark.prior_target_cents, target_cents: mark.target_cents, why: mark.why, own_bid: mark.state_evidence?.bid, own_ask: mark.state_evidence?.ask, own_last: mark.state_evidence?.last_traded, own_spread: mark.state_evidence?.spread, own_dwell: mark.state_evidence?.ask_dwell_seconds, own_bid_depth_5: mark.state_evidence?.bid_depth_5, own_ask_depth_5: mark.state_evidence?.ask_depth_5, sibling_bid: mark.sibling_observation?.bid, sibling_ask: mark.sibling_observation?.ask, sibling_last: mark.sibling_observation?.last_traded, sibling_spread: mark.sibling_observation?.spread, sibling_dwell: mark.sibling_observation?.ask_dwell_seconds }))).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_identity.localeCompare(b.leg_identity) || a.sequence - b.sequence);
    fs.writeFileSync(path.join(dir, "DUAL_TIMELINE_V2.csv"), `${columns.join(",")}\n${timeline.map((row) => columns.map((column) => csv(row[column])).join(",")).join("\n")}\n`);
    auditRows.push({ role: pick.role, event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, outcome_class: pack.event.outcome_class, credited_legs: pack.event.credited_legs, combined_entry_cents: event.combined_entry_cents, action_receipts: eventActions.length, join_receipts: eventJoins.length, L5_reprices: Object.values(chains).reduce((sum, chain) => sum + chain.L5.mark_sequences.length, 0), silent_fields: Object.fromEntries(Object.entries(chains).map(([id, chain]) => [id, chain.silent_layers_or_fields])) });
  }
  ensure(auditRows.filter((row) => row.outcome_class === "COMPLETED").length === 2, "completed selection");
  ensure(auditRows.filter((row) => row.outcome_class === "ONE_LEG").length === 2, "one-leg selection");
  ensure(auditRows.filter((row) => row.outcome_class === "SKIP").length === 1, "skip selection");
  ensure(auditRows.filter((row) => row.outcome_class === "NEAR_MISS").length === 1, "near-miss selection");
  const receipt = { schema_version: "window1-v47-sealed-exam-why-chain-audit-v1", frozen_exam: { V47: "fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34", population_N: 238, score_emitting_runs: 1, results_root_sha_scope: "FROZEN_STAGE3_ONE_RUN_FINAL_RETRY2" }, selection_law: ["lowest-combined exact-bell completion", "completed game with maximum emitted guard lifecycle", "first exact-bell one-leg outcome", "first capture-stream one-leg outcome", "zero-credit game farthest below union reach", "zero-credit game nearest union reach"], rows: auditRows, sources: { event_ledger: { path: path.relative(repo, eventLedgerFile).replaceAll("\\", "/"), sha256: hashFile(eventLedgerFile) }, action_trace: { path: path.relative(repo, actionFile).replaceAll("\\", "/"), sha256: hashFile(actionFile) }, join_trace: { path: path.relative(repo, joinFile).replaceAll("\\", "/"), sha256: hashFile(joinFile) }, population_declaration: { path: path.relative(repo, declarationFile).replaceAll("\\", "/"), sha256: hashFile(declarationFile) }, boundary_ledger: { path: path.relative(repo, boundaryFile).replaceAll("\\", "/"), sha256: hashFile(boundaryFile) }, prints: { path_class: "FROZEN_PRIVATE_EXAM_PRINTS", sha256: hashFile(printsFile) } }, limitations: { "un-emitted_hold_only_decisions": "SILENT", quote_path_and_pressure_constituents: "SILENT_UNLESS_PRESENT_ON_FROZEN_EVENT_SNAPSHOT", no_reconstruction_claim: true, no_policy_rerun: true }, conservation: { packs: auditRows.length, completed: 2, one_leg: 2, skip: 1, near_miss: 1, pass: auditRows.length === 6 } };
  fs.writeFileSync(path.join(root, "WHY_CHAIN_AUDIT.json"), canonical(receipt));
  fs.writeFileSync(path.join(root, "REPORT.md"), `# V47 sealed exam WHY-chain audit\n\nSix post-score, receipt-only walkthrough packs: two completed, two one-leg, one skip, and one near-miss. No policy replay occurred. Each DECISION_MARKS file binds L1 through L6; every emitted reprice appears in L5. Frozen traces did not separately emit every HOLD-only direction constituent, so those fields are explicitly SILENT rather than reconstructed.\n`);
  return walkFiles(root);
}

(async () => {
  ensure(!fs.existsSync(output), "output already exists");
  const second = `${output}.determinism-2`;
  ensure(!fs.existsSync(second), "determinism output exists");
  const firstManifest = await build(output), secondManifest = await build(second);
  const names = [...new Set([...Object.keys(firstManifest), ...Object.keys(secondManifest)])].sort();
  const mismatches = names.filter((name) => !firstManifest[name] || !secondManifest[name] || firstManifest[name].sha256 !== secondManifest[name].sha256 || firstManifest[name].bytes !== secondManifest[name].bytes);
  ensure(!mismatches.length && Object.keys(firstManifest).length === Object.keys(secondManifest).length, `determinism mismatch ${mismatches.join(",")}`);
  fs.rmSync(second, { recursive: true, force: true });
  fs.writeFileSync(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({ builds: 2, compared_files: names.length, byte_identical: true, mismatches: [] }));
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: walkFiles(output) }));
  process.stdout.write(canonical({ status: "PASS", packs: 6, compared_files: names.length }));
})().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
