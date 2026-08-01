#!/usr/bin/env node
"use strict";

// Applies the already-frozen honest maker/taker/unproven law to the cold
// five-game pair-wiring replay. This is a receipt builder, not a scorer.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const argv = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = argv.indexOf(name);
  return i >= 0 ? argv[i + 1] : fallback;
};
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const replayPath = path.resolve(arg("--replay", path.join(repo, ".claude/window1_live_v4_replay/five_exact_pair_wiring_honest_20260801/FIVE_GAME_PAIR_WIRING_REPLAY.json")));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/five_exact_pair_wiring_honest_20260801")));
const frozenFivePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const contractPath = path.join(repo, ".claude/window1_live_v4_replay/honest_fill_model_20260801/HONEST_FILL_MODEL_CONTRACT.json");
const libraryPath = path.resolve(arg("--library", path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/QUOTE_SHAPE_LIBRARY_LEAVE_FIVE_OUT.json")));
const pairWiringPath = path.join(repo, "arb-executor/analysis/window1_quote_shape_pair_wiring_v3.js");
const replayBuilderPath = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
const stableSignerPath = path.join(repo, "arb-executor/analysis/window1_quote_shape_stable_signer_v4.js");
const ceilingsPath = path.join(repo, ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/CEILING_CENSUS.json");
const branchRaw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";
const outputRelative = path.relative(repo, output).replace(/\\/g, "/");
const QUANTITY = 5;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function clock(ts, scheduled, bell) {
  return {
    timestamp_epoch: ts,
    t_minus_scheduled_seconds: scheduled - ts,
    t_minus_actual_bell_seconds: bell - ts,
  };
}
function tminus(seconds) {
  if (seconds == null) return "NOT_AVAILABLE";
  const prefix = seconds >= 0 ? "T-" : "T+";
  const total = Math.abs(seconds);
  const whole = Math.floor(total);
  return `${prefix}${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}
function loadPrints(eventId, legId, window) {
  const file = path.join(privateRoot, "fit-local/guarded-cache-v3", `${eventId}.json.gz`);
  const bytes = fs.readFileSync(file);
  const cache = JSON.parse(zlib.gunzipSync(bytes));
  const leg = cache.legs.find((candidate) => candidate.leg === legId);
  if (!leg) throw new Error(`missing guarded-cache leg ${eventId}/${legId}`);
  const seen = new Set();
  const rows = [];
  for (const row of leg.prints || []) {
    if (!(row.ts >= window.left_ts && row.ts <= window.right_ts)) continue;
    if (!(row.size > 0) || !Number.isInteger(row.price) || !row.trade_id || seen.has(row.trade_id)) continue;
    seen.add(row.trade_id);
    rows.push({
      timestamp_epoch: row.ts,
      price_cents: row.price,
      size: row.size,
      trade_id: row.trade_id,
      aggressor_side: row.taker_side === "yes" ? "BUY" : row.taker_side === "no" ? "SELL" : "UNKNOWN",
    });
  }
  rows.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.trade_id.localeCompare(b.trade_id));
  return { rows, source: { path: `fit-local/guarded-cache-v3/${eventId}.json.gz`, bytes: bytes.length, sha256: sha256(bytes) } };
}
function placeDecision(leg) {
  if (!leg.placement) return null;
  const matches = leg.decision_changes.filter((row) => row.state === "PLACE" && row.order && row.order.action_ts === leg.placement.action_ts);
  if (matches.length !== 1) throw new Error(`expected one PLACE row for ${leg.ticker}; got ${matches.length}`);
  return matches[0];
}
function classify(event, legId, leg, window, prints) {
  if (!leg.placement || !leg.fill) {
    return {
      fill_class: "UNPROVEN",
      credited_under_honest_model: false,
      reason: "No candidate action and replay credit exist to classify.",
      action_book_exact: false,
      seller_aggressed_print_proofs: [],
    };
  }
  const decision = placeDecision(leg);
  const book = decision.book;
  const x = leg.placement.price_cents;
  const exact = leg.placement.own_book_ts_at_action === leg.placement.action_ts
    && leg.placement.own_book_receipt_at_action === leg.placement.action_receipt;
  const capacity = book.ask <= x ? Number(book.top_ask_size) : 0;
  const provenTaker = exact && book.ask <= x && Number.isFinite(capacity) && capacity >= QUANTITY;
  const sellerProofs = prints.rows.filter((row) => row.timestamp_epoch > leg.placement.action_ts
    && row.timestamp_epoch <= leg.fill.evidence_ts
    && row.aggressor_side === "SELL"
    && row.price_cents <= x);
  const provenMaker = exact && x < book.ask && sellerProofs.length > 0;
  if (provenTaker) {
    return {
      fill_class: "PROVEN_TAKER",
      credited_under_honest_model: true,
      reason: "Exact submission-time own BBO displayed at least five opposing contracts at or below X; the buy would cross.",
      action_book_exact: exact,
      seller_aggressed_print_proofs: sellerProofs,
      honest_credit_clock: clock(leg.placement.action_ts, window.scheduled_start_ts, window.actual_bell_ts),
      honest_credit_receipts: [leg.placement.own_book_receipt_at_action],
      displayed_opposing_capacity_at_or_below_x: capacity,
    };
  }
  if (provenMaker) {
    return {
      fill_class: "PROVEN_MAKER",
      credited_under_honest_model: true,
      reason: "X was nonmarketable on the exact action book before a strictly later SELL-aggressor print traded at or below X.",
      action_book_exact: exact,
      seller_aggressed_print_proofs: sellerProofs,
      honest_credit_clock: clock(sellerProofs[0].timestamp_epoch, window.scheduled_start_ts, window.actual_bell_ts),
      honest_credit_receipts: [sellerProofs[0].trade_id],
      displayed_opposing_capacity_at_or_below_x: capacity,
    };
  }
  return {
    fill_class: "UNPROVEN",
    credited_under_honest_model: false,
    reason: exact
      ? "No opposing-size crossing proof and no later SELL-aggressor print at or through a proven nonmarketable resting X."
      : "The own-leg book was not authoritative at the exact action receipt; later BBO-only replay credit cannot prove a take or maker fill.",
    action_book_exact: exact,
    seller_aggressed_print_proofs: sellerProofs,
    honest_credit_clock: null,
    honest_credit_receipts: [],
    displayed_opposing_capacity_at_or_below_x: capacity,
  };
}
function firedPredicates(leg, decision, honest) {
  const fired = [];
  if (!leg.placement) {
    fired.push(`TERMINAL:${leg.terminal_reason}`);
    return fired;
  }
  fired.push("SHAPE_FLOOR_CONSENSUS");
  for (const tuple of leg.placement.pair_shape_tuples || []) fired.push(`PAIR_TUPLE:${tuple.support_class}`);
  fired.push(`INVERSE_SIBLING:${leg.placement.inverse_sibling_proof_type}`);
  fired.push(`MICRO_POSITION:${leg.placement.micro_position_evidence_type}`);
  if (decision.book.stable_same_price_receipt) fired.push("STABLE_SAME_PRICE_ASK_RECEIPT");
  if (decision.book.ask_change_after_first_timestamp) fired.push("ASK_PRICE_TRANSITION");
  if (leg.placement.stable_signing_support?.support_type) fired.push(`STABLE_SIGNER:${leg.placement.stable_signing_support.support_type}`);
  if (honest.action_book_exact) fired.push("EXACT_ACTION_BOOK");
  if ((honest.displayed_opposing_capacity_at_or_below_x || 0) >= QUANTITY) fired.push("DISPLAYED_ASK_CAPACITY_AT_LEAST_FIVE");
  fired.push(`HONEST_FILL:${honest.fill_class}`);
  return [...new Set(fired)];
}
function delta(entry, reference) { return entry == null || reference == null ? null : entry - reference; }
function signed(value) { return value == null ? "-" : value > 0 ? `+${value}` : String(value); }

function main() {
  const replay = JSON.parse(fs.readFileSync(replayPath));
  const frozenFive = JSON.parse(fs.readFileSync(frozenFivePath));
  const contract = JSON.parse(fs.readFileSync(contractPath));
  const windows = Object.fromEntries(frozenFive.events.map((event) => [event.event_id, event.window]));
  const privateSources = {};
  const events = [];
  for (const event of replay.events) {
    const window = windows[event.event_id];
    if (!window) throw new Error(`missing frozen window ${event.event_id}`);
    const legs = [];
    for (const [legId, leg] of Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b))) {
      const prints = loadPrints(event.event_id, legId, window);
      privateSources[`${event.event_id}|${legId}`] = prints.source;
      const honest = classify(event, legId, leg, window, prints);
      const decision = placeDecision(leg);
      const proposedEntry = leg.entry_cents;
      legs.push({
        event_id: event.event_id,
        category: event.category,
        price_region: leg.price_region,
        leg_id: legId,
        ticker: leg.ticker,
        proposed_entry_cents: proposedEntry,
        honest_credited_entry_cents: honest.credited_under_honest_model ? proposedEntry : null,
        honest_fill_class: honest.fill_class,
        honest_credit: honest,
        pair_reference_cents: "NOT_BOUND",
        delta_to_pair_reference_cents: "NOT_BOUND",
        own_window1_close_cents: leg.own_window1_close_cents,
        delta_to_own_window1_close_cents: delta(proposedEntry, leg.own_window1_close_cents),
        own_bell_price_cents: leg.own_bell_price_cents,
        delta_to_own_bell_price_cents: delta(proposedEntry, leg.own_bell_price_cents),
        own_ask_reachable_low_cents: leg.own_ask_reachable_low_cents,
        delta_to_own_ask_reachable_low_cents: delta(proposedEntry, leg.own_ask_reachable_low_cents),
        action_clock: leg.placement ? clock(leg.placement.action_ts, window.scheduled_start_ts, window.actual_bell_ts) : null,
        action_clock_labels: leg.placement ? {
          t_minus_scheduled: tminus(window.scheduled_start_ts - leg.placement.action_ts),
          t_minus_actual_bell: tminus(window.actual_bell_ts - leg.placement.action_ts),
        } : null,
        joint_observation_at_action: decision ? {
          bid_cents: decision.book.bid,
          ask_cents: decision.book.ask,
          last_traded_cents: decision.book.carried_last,
          spread_cents: decision.book.spread,
          ask_dwell_seconds: decision.book.ask_dwell_seconds,
          top_ask_size: decision.book.top_ask_size,
          top_five_ask_depth: decision.book.top5_ask_depth,
          source_receipt: leg.placement.own_book_receipt_at_action,
          source_timestamp_epoch: leg.placement.own_book_ts_at_action,
        } : null,
        surviving_shapes_at_action: leg.placement ? leg.placement.surviving_shapes : leg.surviving_shapes_at_terminal,
        fired_predicates: firedPredicates(leg, decision, honest),
        terminal_reason: leg.terminal_reason,
        replay_credit_is_not_honest_evidence: true,
        fee_test: "NOT_RUN_BY_OPERATOR_INSTRUCTION",
        expected_close_forecast: "NOT_BOUND_AND_NOT_USED",
      });
    }
    const honestComplete = legs.every((leg) => leg.honest_credit.credited_under_honest_model);
    const eachBelowClose = honestComplete && legs.every((leg) => leg.honest_credited_entry_cents < leg.own_window1_close_cents);
    const combinedEntry = honestComplete ? legs.reduce((sum, leg) => sum + leg.honest_credited_entry_cents, 0) : null;
    const pairUnderPar = combinedEntry != null && combinedEntry < 100;
    events.push({
      event_id: event.event_id,
      category: event.category,
      legs,
      honest_completed_pair: honestComplete,
      every_leg_strictly_below_own_window1_close: eachBelowClose,
      combined_honest_entry_cents: combinedEntry,
      pair_strictly_under_par: pairUnderPar,
      objective_gate_pass: honestComplete && eachBelowClose && pairUnderPar,
      pair_reference: "NOT_BOUND",
    });
  }
  const proposed = events.flatMap((event) => event.legs);
  const gate = {
    schema_version: "WINDOW1_FIVE_EXACT_PAIR_WIRING_HONEST_GATE_V1",
    cold: replay.cold,
    outcome_knowledge_consumed: replay.outcome_knowledge_consumed,
    score_free: true,
    event_count: events.length,
    leg_count: proposed.length,
    replay_proposed_fill_count: proposed.filter((leg) => leg.proposed_entry_cents != null).length,
    honest_fill_class_counts: {
      PROVEN_MAKER: proposed.filter((leg) => leg.honest_fill_class === "PROVEN_MAKER").length,
      PROVEN_TAKER: proposed.filter((leg) => leg.honest_fill_class === "PROVEN_TAKER").length,
      UNPROVEN: proposed.filter((leg) => leg.honest_fill_class === "UNPROVEN").length,
    },
    honest_completed_pair_count: events.filter((event) => event.honest_completed_pair).length,
    objective_gate_pass_count: events.filter((event) => event.objective_gate_pass).length,
    five_game_gate_passed: events.every((event) => event.objective_gate_pass),
    population_804_authorized_by_gate: events.every((event) => event.objective_gate_pass),
    population_804_run: false,
    objective: "Both legs honestly credited in Window 1; each entry strictly below its own Window-1 close; combined entry strictly below 100.",
    fee_test: "DROPPED_BY_OPERATOR_INSTRUCTION",
    expected_close_forecast: "DROPPED_BY_OPERATOR_INSTRUCTION",
    frozen_ceiling_bindings_not_executed: { take_reachable: 516, maker_reachable_combined_negative: 253 },
    events,
  };
  if (gate.event_count !== 5 || gate.leg_count !== 10) throw new Error("five-game conservation failed");
  fs.mkdirSync(output, { recursive: true });
  const gateFile = path.join(output, "FIVE_GAME_HONEST_GATE.json");
  fs.writeFileSync(gateFile, canonical(gate));
  const sourceManifest = {
    schema_version: "WINDOW1_FIVE_EXACT_PAIR_WIRING_HONEST_SOURCE_MANIFEST_V1",
    committed_sources: Object.fromEntries([__filename, replayPath, frozenFivePath, contractPath, libraryPath, pairWiringPath, replayBuilderPath, stableSignerPath, ceilingsPath].map((file) => [path.relative(repo, file).replace(/\\/g, "/"), { sha256: hashFile(file), bytes: fs.statSync(file).size }])),
    private_sources: privateSources,
    honest_fill_contract_identity: { path: path.relative(repo, contractPath).replace(/\\/g, "/"), sha256: hashFile(contractPath), class_law: contract.classes },
  };
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical(sourceManifest));

  const table = [];
  for (const event of events) for (const leg of event.legs) table.push(`| ${leg.category} | ${leg.price_region} | ${event.event_id}/${leg.leg_id} | ${leg.proposed_entry_cents ?? "-"} | ${leg.honest_fill_class} | ${leg.own_window1_close_cents} | ${leg.own_bell_price_cents} | ${leg.own_ask_reachable_low_cents} | ${leg.delta_to_pair_reference_cents} | ${signed(leg.delta_to_own_window1_close_cents)} | ${signed(leg.delta_to_own_bell_price_cents)} | ${signed(leg.delta_to_own_ask_reachable_low_cents)} | ${leg.fired_predicates.join("; ")} |`);
  const report = `# Five exact-start games — pair-wiring + stable signer + honest fill gate\n\nCold replay: ${gate.cold}; outcome knowledge consumed: ${gate.outcome_knowledge_consumed}. Fee testing and expected-close forecasting were not run.\n\nAll table values: ${branchRaw}/${outputRelative}/FIVE_GAME_HONEST_GATE.json\n\n| Category | Price region | Event/leg | Proposed entry | Honest class | W1 close | Bell | Ask-low | Δ pair ref | Δ close | Δ bell | Δ ask-low | Predicates fired |\n|---|---:|---|---:|---|---:|---:|---:|---|---:|---:|---:|---|\n${table.join("\n")}\n\nFive-game gate: **${gate.five_game_gate_passed ? "PASS" : "FAIL"}**. Honest complete pairs: ${gate.honest_completed_pair_count}/5. Objective passes: ${gate.objective_gate_pass_count}/5. Proposed leg fills: ${gate.replay_proposed_fill_count}; honest classes: ${gate.honest_fill_class_counts.PROVEN_MAKER} maker, ${gate.honest_fill_class_counts.PROVEN_TAKER} taker, ${gate.honest_fill_class_counts.UNPROVEN} unproven.\n\nThe 804 replay is conditional on this gate. Current population run state: ${gate.population_804_run}. The frozen ceilings (516 take-reachable; 253 combined-negative maker-reachable) remain comparison bindings until a passing gate authorizes the population run.\n\nHonest-law source: ${branchRaw}/.claude/window1_live_v4_replay/honest_fill_model_20260801/HONEST_FILL_MODEL_CONTRACT.json\n\nReplay source: ${branchRaw}/${outputRelative}/${path.basename(replayPath)}\n`;
  fs.writeFileSync(path.join(output, "REPORT.md"), report);
  const artifactFiles = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  const artifactManifest = {
    schema_version: "WINDOW1_FIVE_EXACT_PAIR_WIRING_HONEST_ARTIFACT_MANIFEST_V1",
    files: Object.fromEntries(artifactFiles.map((name) => [name, { sha256: hashFile(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])),
  };
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical(artifactManifest));
  process.stdout.write(canonical({ status: "BUILT", five_game_gate_passed: gate.five_game_gate_passed, honest_completed_pairs: gate.honest_completed_pair_count, objective_passes: gate.objective_gate_pass_count, classes: gate.honest_fill_class_counts, population_804_run: false }));
}

if (require.main === module) main();
