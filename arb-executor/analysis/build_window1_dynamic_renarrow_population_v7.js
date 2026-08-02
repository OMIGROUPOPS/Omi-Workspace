#!/usr/bin/env node
"use strict";

// Score-free 804-event diagnostic for the frozen V6 quote-shape decision tree.
// It replays policy decisions; it does not import or invoke a Window-1 scorer.

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801")));
const workers = Number(value("--workers", "8"));
const lagDiagnosticV10 = args.includes("--lag-diagnostic-v10");
const causalDescentOrdinalV10 = args.includes("--causal-descent-ordinal-v10");
const persistenceFloorV11 = args.includes("--persistence-floor-v11");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const capacityPath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const ceilingPath = path.join(repo, ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/CEILING_CENSUS.json");
const libraryPath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json");
const replayPath = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
const branchRaw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";
const DWELL_SECONDS = 10;
const QUANTITY = 5;

function canonical(item) { return `${JSON.stringify(item, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const headers = lines.shift().split(","); return lines.map((line) => Object.fromEntries(line.split(",").map((item, index) => [headers[index], item]))); }
function priceRegion(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function quantile(values, p) { const sorted = [...values].sort((a, b) => a - b); return sorted.length ? sorted[Math.min(sorted.length - 1, Math.floor(p * (sorted.length - 1)))] : null; }
function tminus(seconds) { if (!Number.isFinite(seconds)) return null; const sign = seconds >= 0 ? "T-" : "T+"; const total = Math.abs(seconds); return `${sign}${Math.floor(total / 60)}:${String(Math.floor(total % 60)).padStart(2, "0")}`; }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function relative(file) { return path.relative(repo, file).replace(/\\/g, "/"); }
function floorClass(floor, close) { if (!Number.isInteger(floor) || !Number.isInteger(close)) return "ASK_REACHABLE_FLOOR_OR_CLOSE_UNAVAILABLE"; if (floor < close) return "ASK_REACHABLE_FLOOR_BELOW_W1_CLOSE"; if (floor === close) return "EXACT_ASK_REACHABLE_FLOOR_EQUALS_W1_CLOSE"; return "ASK_REACHABLE_FLOOR_ABOVE_W1_CLOSE"; }

function prepareInputs(work) {
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8"));
  const capacity = JSON.parse(fs.readFileSync(capacityPath));
  const bell = JSON.parse(fs.readFileSync(bellPath));
  const ceiling = JSON.parse(fs.readFileSync(ceilingPath));
  const capacityByKey = Object.fromEntries(capacity.rows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const bellByKey = Object.fromEntries(bell.leg_rows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const quoteByEvent = {};
  for (const row of quoteRows) { if (!quoteByEvent[row.event_id]) quoteByEvent[row.event_id] = []; quoteByEvent[row.event_id].push(row); }
  const corrected = [];
  const windows = [];
  for (const event of ceiling.events) {
    const rows = quoteByEvent[event.event_id] || [];
    ensure(rows.length === 2, `expected two quote rows for ${event.event_id}`);
    const legs = {};
    for (const row of rows) {
      const cap = capacityByKey[`${event.event_id}|${row.leg}`];
      ensure(cap, `missing capacity row ${event.event_id}/${row.leg}`);
      const bellRow = bellByKey[`${event.event_id}|${row.leg}`];
      legs[row.leg] = {
        entry_cents: null,
        own_window1_close_cents: Number(cap.window1_close_cents),
        own_bell_price_cents: bellRow && Number.isInteger(Number(bellRow.close_price_cents)) ? Number(bellRow.close_price_cents) : null,
        own_ask_reachable_low_cents: cap.capacity_proven_floor?.limit_cents ?? null,
      };
    }
    corrected.push({ event_id: event.event_id, legs });
    const exactBells = rows.map((row) => bellByKey[`${event.event_id}|${row.leg}`]?.exact_bell_ts).filter(Number.isFinite);
    const actualBell = exactBells.length === 2 && exactBells[0] === exactBells[1] ? exactBells[0] : null;
    windows.push({ event_id: event.event_id, window: { actual_bell_ts: actualBell } });
  }
  const refsPath = path.join(work, "POPULATION_REFERENCES.json");
  const windowsPath = path.join(work, "POPULATION_WINDOWS.json");
  fs.writeFileSync(refsPath, canonical({ current_branch: corrected, corrected_branch: corrected }));
  fs.writeFileSync(windowsPath, canonical({ events: windows }));
  return { ceiling, capacityByKey, quoteByEvent, bellByKey, refsPath, windowsPath };
}

function launchShard(index, eventIds, work, refsPath, windowsPath) {
  const targetFile = path.join(work, `targets-${index}.json`);
  const shardDir = path.join(work, `shard-${index}`);
  fs.writeFileSync(targetFile, canonical(eventIds));
  fs.mkdirSync(shardDir, { recursive: true });
  const childArgs = [replayPath, "--repo", repo, "--private-root", privateRoot, "--library", libraryPath, "--references", refsPath, "--windows", windowsPath, "--target-file", targetFile, "--output", shardDir, "--receipt-name", "SHARD.json", "--stable-same-price-confirmation", "--pair-wiring-v3", "--stable-signer-v4", "--descent-verdict-v5", "--dynamic-renarrow-v6", "--compact-population", "--exclude-own-training-member", "--no-charts"];
  if (lagDiagnosticV10) childArgs.push("--lag-diagnostic-v10");
  if (causalDescentOrdinalV10) childArgs.push("--causal-descent-ordinal-v10");
  if (persistenceFloorV11) childArgs.push("--persistence-floor-v11");
  return new Promise((resolve, reject) => {
    const child = childProcess.spawn(process.execPath, childArgs, { cwd: repo, stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "", stderr = "";
    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });
    child.on("error", reject);
    child.on("exit", (code) => code === 0 ? resolve({ index, shardDir, stdout, stderr }) : reject(new Error(`shard ${index} failed (${code}): ${stderr}`)));
  });
}

function enrich(events, inputs) {
  const ceilingByEvent = Object.fromEntries(inputs.ceiling.events.map((event) => [event.event_id, event]));
  return events.map((event) => {
    const ceiling = ceilingByEvent[event.event_id];
    ensure(ceiling, `missing ceiling event ${event.event_id}`);
    const quoteRows = inputs.quoteByEvent[event.event_id];
    const legIds = quoteRows.map((row) => row.leg).sort();
    const legs = {};
    for (const legId of legIds) {
      const source = quoteRows.find((row) => row.leg === legId);
      const cap = inputs.capacityByKey[`${event.event_id}|${legId}`];
      const bell = inputs.bellByKey[`${event.event_id}|${legId}`];
      const replayLeg = event.legs?.[legId] || {};
      const entry = Number.isInteger(replayLeg.honest_credited_entry_cents) ? replayLeg.honest_credited_entry_cents : null;
      const floor = cap.capacity_proven_floor?.limit_cents ?? null;
      const close = Number(cap.window1_close_cents);
      const gap = entry !== null && Number.isInteger(floor) ? entry - floor : null;
      const actionTs = replayLeg.placement?.action_ts ?? null;
      const scheduled = Number(source.scheduled_start_ts);
      const actualBell = bell?.exact_bell_ts ?? null;
      legs[legId] = {
        leg_id: legId,
        ticker: source.ticker,
        price_region: replayLeg.price_region || priceRegion(Number(cap.window1_open_cents)),
        proposed_entry_cents: replayLeg.proposed_entry_cents ?? null,
        honest_fill_class: replayLeg.honest_fill_class || "UNPROVEN",
        honest_credited_entry_cents: entry,
        action_timestamp_epoch: actionTs,
        t_minus_scheduled_seconds: actionTs === null ? null : scheduled - actionTs,
        t_minus_scheduled: actionTs === null ? null : tminus(scheduled - actionTs),
        t_minus_actual_bell_seconds: actionTs === null || !Number.isFinite(actualBell) ? null : actualBell - actionTs,
        t_minus_actual_bell: actionTs === null || !Number.isFinite(actualBell) ? null : tminus(actualBell - actionTs),
        action_book: replayLeg.action_book || null,
        own_window1_close_cents: close,
        own_bell_price_cents: bell && Number.isInteger(Number(bell.close_price_cents)) ? Number(bell.close_price_cents) : null,
        own_ask_reachable_low_cents: floor,
        ask_reachable_low_proof: cap.capacity_proven_floor || null,
        delta_to_own_window1_close_cents: entry === null ? null : entry - close,
        delta_to_own_bell_price_cents: entry === null || !bell || !Number.isInteger(Number(bell.close_price_cents)) ? null : entry - Number(bell.close_price_cents),
        delta_to_own_ask_reachable_low_cents: gap,
        execution_floor_gate_pass: entry !== null && gap !== null && gap <= 0,
        execution_floor_gate_reason: entry === null ? "HONEST_FILL_NOT_PROVEN" : gap === null ? "ASK_REACHABLE_FLOOR_UNAVAILABLE" : gap <= 0 ? "ENTRY_AT_OR_BETTER_THAN_OWN_ASK_REACHABLE_LOW" : "ENTRY_ABOVE_OWN_ASK_REACHABLE_LOW",
        ask_reachable_floor_minus_own_window1_close_cents: Number.isInteger(floor) ? floor - close : null,
        market_ceiling_class: floorClass(floor, close),
        pair_reference_cents: "NOT_BOUND",
        delta_to_pair_reference_cents: "NOT_BOUND",
        predicates: replayLeg.placement ? ["DYNAMIC_MACRO_RENARROW", "PAIR_WIRING", "MICRO_POSITION", "ASK_DWELL_AT_LEAST_10_SECONDS", "DISPLAYED_ASK_CAPACITY_AT_LEAST_FIVE", "EXACT_ACTION_BOOK", replayLeg.honest_fill_class] : [replayLeg.terminal_reason || event.reason || "NO_ACTION"],
        placement: replayLeg.placement || null,
        lag_diagnostic_v10: replayLeg.lag_diagnostic_v10 || null,
        terminal_reason: replayLeg.terminal_reason || event.reason || null,
        replay_source: replayLeg.source || null,
      };
    }
    const values = Object.values(legs);
    const completed = values.every((leg) => leg.honest_credited_entry_cents !== null);
    const combined = completed ? values.reduce((sum, leg) => sum + leg.honest_credited_entry_cents, 0) : null;
    return {
      event_id: event.event_id,
      category: ceiling.category,
      starting_price_split: ceiling.starting_price_split,
      replay_status: event.replay_status,
      legs,
      candidate_completed_pair: completed,
      candidate_combined_entry_cents: combined,
      candidate_pair_strictly_under_par: combined !== null && combined < 100,
      candidate_both_legs_strictly_below_close: completed && values.every((leg) => leg.honest_credited_entry_cents < leg.own_window1_close_cents),
      candidate_execution_floor_pair_pass: completed && combined < 100 && values.every((leg) => leg.execution_floor_gate_pass),
      take_ceiling_member: ceiling.controlling_516_member,
      maker_ceiling_member: ceiling.maker_pair_combined_negative,
    };
  });
}

function summarize(ledger) {
  const eventMap = new Map();
  const legMap = new Map();
  for (const event of ledger) {
    const eventKey = `${event.category}|${event.starting_price_split}`;
    if (!eventMap.has(eventKey)) eventMap.set(eventKey, { category: event.category, starting_price_split: event.starting_price_split, event_ids: [], D: 0, take_ceiling: 0, maker_ceiling: 0, completed_pairs: 0, pairs_under_par: 0, both_legs_below_close: 0, execution_floor_pair_pass: 0 });
    const cell = eventMap.get(eventKey); cell.event_ids.push(event.event_id); cell.D += 1; cell.take_ceiling += Number(event.take_ceiling_member); cell.maker_ceiling += Number(event.maker_ceiling_member); cell.completed_pairs += Number(event.candidate_completed_pair); cell.pairs_under_par += Number(event.candidate_pair_strictly_under_par); cell.both_legs_below_close += Number(event.candidate_both_legs_strictly_below_close); cell.execution_floor_pair_pass += Number(event.candidate_execution_floor_pair_pass);
    for (const leg of Object.values(event.legs)) {
      const legKey = `${event.category}|${leg.price_region}`;
      if (!legMap.has(legKey)) legMap.set(legKey, { category: event.category, price_region: leg.price_region, leg_ids: [], legs: 0, acted: 0, honest_credited: 0, gaps: [], exact_floor: 0, within_one_cent_above_floor: 0, above_floor_by_two_or_more: 0, floor_below_close: 0, floor_equals_close: 0, floor_above_close: 0, floor_unavailable: 0 });
      const cellLeg = legMap.get(legKey); cellLeg.leg_ids.push(`${event.event_id}/${leg.leg_id}`); cellLeg.legs += 1; cellLeg.acted += Number(leg.proposed_entry_cents !== null); cellLeg.honest_credited += Number(leg.honest_credited_entry_cents !== null);
      if (Number.isInteger(leg.delta_to_own_ask_reachable_low_cents)) { cellLeg.gaps.push(leg.delta_to_own_ask_reachable_low_cents); cellLeg.exact_floor += Number(leg.delta_to_own_ask_reachable_low_cents === 0); cellLeg.within_one_cent_above_floor += Number(leg.delta_to_own_ask_reachable_low_cents === 1); cellLeg.above_floor_by_two_or_more += Number(leg.delta_to_own_ask_reachable_low_cents >= 2); }
      cellLeg.floor_below_close += Number(leg.market_ceiling_class === "ASK_REACHABLE_FLOOR_BELOW_W1_CLOSE"); cellLeg.floor_equals_close += Number(leg.market_ceiling_class === "EXACT_ASK_REACHABLE_FLOOR_EQUALS_W1_CLOSE"); cellLeg.floor_above_close += Number(leg.market_ceiling_class === "ASK_REACHABLE_FLOOR_ABOVE_W1_CLOSE"); cellLeg.floor_unavailable += Number(leg.market_ceiling_class === "ASK_REACHABLE_FLOOR_OR_CLOSE_UNAVAILABLE");
    }
  }
  const legCells = [...legMap.values()].map((cell) => ({ ...cell, gap_to_ask_reachable_low_distribution: { n: cell.gaps.length, min: cell.gaps.length ? Math.min(...cell.gaps) : null, p25: quantile(cell.gaps, .25), median: quantile(cell.gaps, .5), p75: quantile(cell.gaps, .75), p90: quantile(cell.gaps, .9), max: cell.gaps.length ? Math.max(...cell.gaps) : null, counts: Object.fromEntries([...new Set(cell.gaps)].sort((a, b) => a - b).map((gap) => [String(gap), cell.gaps.filter((item) => item === gap).length])) }, gaps: undefined }));
  return { event_cells: [...eventMap.values()].sort((a, b) => `${a.category}|${a.starting_price_split}`.localeCompare(`${b.category}|${b.starting_price_split}`)), leg_cells: legCells.sort((a, b) => `${a.category}|${a.price_region}`.localeCompare(`${b.category}|${b.price_region}`)) };
}

async function main() {
  ensure(workers >= 1 && workers <= 16, "workers must be in [1,16]");
  fs.mkdirSync(output, { recursive: true });
  const work = path.join(output, "_work");
  if (fs.existsSync(work)) fs.rmSync(work, { recursive: true, force: true });
  fs.mkdirSync(work, { recursive: true });
  const inputs = prepareInputs(work);
  const eventIds = inputs.ceiling.events.map((event) => event.event_id).sort();
  ensure(eventIds.length === 804 && new Set(eventIds).size === 804, "D must equal 804 unique events");
  const shards = Array.from({ length: workers }, () => []);
  eventIds.forEach((eventId, index) => shards[index % workers].push(eventId));
  const results = await Promise.all(shards.map((ids, index) => launchShard(index, ids, work, inputs.refsPath, inputs.windowsPath)));
  const replayEvents = results.flatMap((result) => JSON.parse(fs.readFileSync(path.join(result.shardDir, "SHARD.json"))).events);
  ensure(replayEvents.length === 804 && new Set(replayEvents.map((event) => event.event_id)).size === 804, "replay event conservation failed");
  const ledger = enrich(replayEvents, inputs).sort((a, b) => a.event_id.localeCompare(b.event_id));
  const summary = summarize(ledger);
  const allLegs = ledger.flatMap((event) => Object.values(event.legs));
  const conservation = {
    schema_version: "WINDOW1_DYNAMIC_RENARROW_POPULATION_CONSERVATION_V7",
    D: ledger.length,
    legs: allLegs.length,
    candidate_completed_pairs: ledger.filter((event) => event.candidate_completed_pair).length,
    candidate_pairs_under_par: ledger.filter((event) => event.candidate_pair_strictly_under_par).length,
    candidate_both_legs_strictly_below_close: ledger.filter((event) => event.candidate_both_legs_strictly_below_close).length,
    candidate_execution_floor_pair_pass: ledger.filter((event) => event.candidate_execution_floor_pair_pass).length,
    take_ceiling: ledger.filter((event) => event.take_ceiling_member).length,
    maker_ceiling: ledger.filter((event) => event.maker_ceiling_member).length,
    acted_legs: allLegs.filter((leg) => leg.proposed_entry_cents !== null).length,
    honest_credited_legs: allLegs.filter((leg) => leg.honest_credited_entry_cents !== null).length,
    exact_floor_legs: allLegs.filter((leg) => leg.delta_to_own_ask_reachable_low_cents === 0).length,
    one_cent_above_floor_legs: allLegs.filter((leg) => leg.delta_to_own_ask_reachable_low_cents === 1).length,
    floor_below_close_legs: allLegs.filter((leg) => leg.market_ceiling_class === "ASK_REACHABLE_FLOOR_BELOW_W1_CLOSE").length,
    floor_equals_close_legs: allLegs.filter((leg) => leg.market_ceiling_class === "EXACT_ASK_REACHABLE_FLOOR_EQUALS_W1_CLOSE").length,
    floor_above_close_legs: allLegs.filter((leg) => leg.market_ceiling_class === "ASK_REACHABLE_FLOOR_ABOVE_W1_CLOSE").length,
    floor_unavailable_legs: allLegs.filter((leg) => leg.market_ceiling_class === "ASK_REACHABLE_FLOOR_OR_CLOSE_UNAVAILABLE").length,
    unavailable_replays: ledger.filter((event) => event.replay_status === "SOURCE_UNAVAILABLE").length,
    event_partition_conservation: summary.event_cells.reduce((sum, cell) => sum + cell.D, 0),
    leg_partition_conservation: summary.leg_cells.reduce((sum, cell) => sum + cell.legs, 0),
    no_scorer_import_or_invocation: true,
  };
  ensure(conservation.D === 804 && conservation.legs === 1608 && conservation.take_ceiling === 516 && conservation.maker_ceiling === 253 && conservation.event_partition_conservation === 804 && conservation.leg_partition_conservation === 1608, "population conservation failed");
  const ledgerBytes = Buffer.from(ledger.map((row) => JSON.stringify(row)).join("\n") + "\n");
  fs.writeFileSync(path.join(output, "EVENT_LEDGER.jsonl.gz"), zlib.gzipSync(ledgerBytes, { level: 9, mtime: 0 }));
  fs.writeFileSync(path.join(output, "POPULATION_SUMMARY.json"), canonical({ schema_version: "WINDOW1_DYNAMIC_RENARROW_POPULATION_SUMMARY_V7", score_free: true, development_diagnostic: true, holdout_validation: false, ask_side_only: true, dwell_seconds: DWELL_SECONDS, exact_quantity: QUANTITY, pair_reference: "NOT_BOUND", ceilings: { take_reachable_combined_negative: 516, maker_reachable_combined_negative: 253 }, performance_fields: { C: null, PC: null, IC: null, S: null, ranking: null, selection: null }, ...summary }));
  fs.writeFileSync(path.join(output, "CONSERVATION_RECEIPT.json"), canonical(conservation));
  const fiveGatePath = path.join(output, "FIVE_GAME_EXECUTION_GATE_SPLIT_RECEIPT.json");
  const fiveSource = JSON.parse(fs.readFileSync(path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/FIVE_GAME_HONEST_GATE.json")));
  const fiveLegs = fiveSource.events.flatMap((event) => event.legs);
  fs.writeFileSync(fiveGatePath, canonical({ schema_version: "WINDOW1_FIVE_GAME_EXECUTION_GATE_SPLIT_V7", prior_receipt_sha256: hashFile(path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/FIVE_GAME_HONEST_GATE.json")), operator_claim: { exact_floor: 7, within_one_cent_above_floor: 3 }, independently_recomputed_from_frozen_capacity_floor: { exact_floor: fiveLegs.filter((leg) => leg.delta_to_own_ask_reachable_low_cents === 0).length, within_one_cent_above_floor: fiveLegs.filter((leg) => leg.delta_to_own_ask_reachable_low_cents === 1).length }, discrepancy_status: "RAW_LEDGER_CONTROLS; DO_NOT_FORCE OPERATOR HEADLINE", execution_gate_law: "entry <= own capacity-proven ask-reachable low; close relation separately classified", exact_floor_equals_close: fiveLegs.filter((leg) => leg.proposed_entry_cents === leg.own_ask_reachable_low_cents && leg.own_ask_reachable_low_cents === leg.own_window1_close_cents).map((leg) => `${leg.event_id}/${leg.leg_id}`) }));
  const report = `# Window-1 dynamic-renarrow V7 - 804 development diagnostic\n\nAll event and leg rows: ${branchRaw}/${relative(path.join(output, "EVENT_LEDGER.jsonl.gz"))}\n\nAll category / price-region partitions and every reported number: ${branchRaw}/${relative(path.join(output, "POPULATION_SUMMARY.json"))}\n\nConservation: ${branchRaw}/${relative(path.join(output, "CONSERVATION_RECEIPT.json"))}\n\nFive-game gate split and the 7/3 versus 8/2 reconciliation: ${branchRaw}/${relative(fiveGatePath)}\n\nThe execution gate is entry at or below the leg's own capacity-proven ask-reachable low. Floor-versus-close is a separate market-ceiling classification. Pair-reference is NOT_BOUND. This run is ask-side only, requires ${DWELL_SECONDS} seconds dwell and exact displayed capacity of at least ${QUANTITY}.\n\nThis is an in-sample development diagnostic. The target event was removed from causal nearest-member selection, but the aggregate library envelopes were fitted on the development population except the frozen five; no holdout claim is made.\n`;
  fs.writeFileSync(path.join(output, "REPORT.md"), report);
  const sourceFiles = [quotePath, capacityPath, bellPath, ceilingPath, libraryPath, replayPath, __filename];
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_DYNAMIC_RENARROW_POPULATION_SOURCE_MANIFEST_V7", committed: Object.fromEntries(sourceFiles.map((file) => [relative(file), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), private_tick_sources: Object.fromEntries(allLegs.filter((leg) => leg.replay_source).map((leg) => [leg.ticker, leg.replay_source])), prohibited_access: { holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false } }));
  fs.rmSync(work, { recursive: true, force: true });
  const artifactNames = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_DYNAMIC_RENARROW_POPULATION_ARTIFACT_MANIFEST_V7", files: Object.fromEntries(artifactNames.map((name) => [name, { sha256: hashFile(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output, conservation }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
