#!/usr/bin/env node
"use strict";

// Freezes the score-free V6 five-game correction receipts. It never runs the 804.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const root = path.resolve(value("--root", path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801")));
const comparisonLibrary = path.resolve(value("--comparison-library", path.join(repo, ".claude/window1_live_v4_replay/QUOTE_SHAPE_LIBRARY_DYNAMIC_V6.tmp.json")));
const comparisonReplay = path.resolve(value("--comparison-replay", path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801.tmp/FIVE_GAME_DYNAMIC_RENARROW_V6_REPLAY.json")));
const comparisonGate = path.resolve(value("--comparison-gate", path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_gate_20260801.tmp/FIVE_GAME_HONEST_GATE.json")));
const testsPassed = args.includes("--tests-passed");
const branchRaw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function hash(file) { return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"); }
function bytes(file) { return fs.statSync(file).size; }
function write(name, value) { fs.writeFileSync(path.join(root, name), typeof value === "string" ? value : canonical(value)); }
function legMap(document) { return new Map(document.events.flatMap((event) => event.legs.map ? event.legs.map((leg) => [`${event.event_id}|${leg.leg_id}`, leg]) : Object.entries(event.legs).map(([leg, row]) => [`${event.event_id}|${leg}`, row]))); }
function tminus(seconds) { const sign = seconds >= 0 ? "T-" : "T+", n = Math.abs(Math.trunc(seconds)); return `${sign}${Math.floor(n / 60)}:${String(n % 60).padStart(2, "0")}`; }

const libraryPath = path.join(root, "QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json");
const replayPath = path.join(root, "FIVE_GAME_DYNAMIC_RENARROW_V6_REPLAY.json");
const gatePath = path.join(root, "FIVE_GAME_HONEST_GATE.json");
const v5ReplayPath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_descent_verdict_v5_20260801/FIVE_GAME_DESCENT_VERDICT_V5_REPLAY.json");
const v5GatePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_descent_verdict_v5_20260801/FIVE_GAME_HONEST_GATE.json");
const replay = JSON.parse(fs.readFileSync(replayPath));
const gate = JSON.parse(fs.readFileSync(gatePath));
const v5Replay = JSON.parse(fs.readFileSync(v5ReplayPath));
const v5Gate = JSON.parse(fs.readFileSync(v5GatePath));
const after = legMap(gate), before = legMap(v5Gate), replayLegs = legMap(replay), v5ReplayLegs = legMap(v5Replay);

const reclassifications = [...replayLegs].flatMap(([identity, leg]) => (leg.macro_reclassifications || []).map((row) => ({ identity, ...row })));
const beforeAfter = [...after].map(([identity, row]) => ({
  identity,
  category: row.category,
  price_region: row.price_region,
  before_entry_cents: before.get(identity)?.proposed_entry_cents ?? null,
  after_entry_cents: row.proposed_entry_cents,
  movement_cents: before.get(identity)?.proposed_entry_cents == null || row.proposed_entry_cents == null ? null : row.proposed_entry_cents - before.get(identity).proposed_entry_cents,
  honest_fill_class: row.honest_fill_class,
  own_window1_close_cents: row.own_window1_close_cents,
  delta_to_own_window1_close_cents: row.delta_to_own_window1_close_cents,
  own_bell_price_cents: row.own_bell_price_cents,
  delta_to_own_bell_price_cents: row.delta_to_own_bell_price_cents,
  own_ask_reachable_low_cents: row.own_ask_reachable_low_cents,
  delta_to_own_ask_reachable_low_cents: row.delta_to_own_ask_reachable_low_cents,
  pair_reference_cents: "NOT_BOUND",
  delta_to_pair_reference_cents: "NOT_BOUND",
  action_clock: row.action_clock,
  action_clock_labels: row.action_clock_labels,
  fired_predicates: row.fired_predicates,
}));

const beforeBra = v5ReplayLegs.get("KXWTACHALLENGERMATCH-26JUL16BRAVED|BRA");
const afterBra = replayLegs.get("KXWTACHALLENGERMATCH-26JUL16BRAVED|BRA");
const staleHold = beforeBra.decision_changes.find((row) => row.state === "HOLD" && row.book.ask === 40);
const lateFloor = beforeBra.decision_changes.find((row) => row.reason === "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW");
const correction = {
  schema_version: "WINDOW1_DYNAMIC_SHAPE_RENARROW_AND_TEMPORAL_VERDICT_V6",
  score_free: true,
  population_804_run: false,
  defect_1: {
    name: "STALE_SHAPE_CLASSIFICATION_NEVER_RENARROWED",
    law: "A witnessed new-low descent eliminates a surviving class when its fitted member support cannot contain the observed descent ordinal. Both macro legs reopen and re-narrow, current inverse path tuples are recomputed, and no lower layer is consulted until that macro pass completes.",
    reclassification_count: reclassifications.length,
    reclassifications,
  },
  defect_2: {
    name: "BRA_STATIC_MEDOID_TEMPORAL_LAG",
    before: {
      hold_timestamp_epoch: staleHold.ts,
      t_minus_scheduled: tminus(1784229600 - staleHold.ts),
      t_minus_actual_bell: tminus(1784232600 - staleHold.ts),
      ask_cents: staleHold.book.ask,
      ask_dwell_seconds: staleHold.book.ask_dwell_seconds,
      verdict: staleHold.surviving_shapes[0].verdict,
      authority: staleHold.surviving_shapes[0].temporal_authority,
      late_floor_timestamp_epoch: lateFloor.ts,
      late_floor_t_minus_scheduled: tminus(1784229600 - lateFloor.ts),
      late_floor_t_minus_actual_bell: tminus(1784232600 - lateFloor.ts),
      ask_when_static_medoid_flipped_cents: lateFloor.book.ask,
      observed_low_already_cents: 40,
      waited_for: "fixed static-medoid progress bin; the medoid future changed from -1 to 0 only after the reachable 40 ask disappeared",
    },
    after: {
      entry_cents: afterBra.entry_cents,
      action_timestamp_epoch: afterBra.placement.action_ts,
      t_minus_scheduled: tminus(1784229600 - afterBra.placement.action_ts),
      t_minus_actual_bell: tminus(1784232600 - afterBra.placement.action_ts),
      ask_cents: afterBra.placement.price_cents,
      authority: afterBra.placement.surviving_shapes[0].temporal_authority,
      selected_training_members: afterBra.placement.surviving_shapes[0].selected_training_members,
      selected_member_remaining_reachable_low_deltas: afterBra.placement.surviving_shapes[0].selected_member_remaining_min_deltas,
      proof: "the causally nearest fitted zero-descent member in the already-resolved DOWN_CONTINUATION class has zero remaining ask-reachable downside; raw asks lacking the inherited exact-five/10-second reach law cannot create lag",
    },
  },
  before_after_numeric_receipt: beforeAfter,
  acceptance: {
    honest_completed_pairs: gate.honest_completed_pair_count,
    objective_passes: gate.objective_gate_pass_count,
    objective_failures: beforeAfter.filter((row) => row.delta_to_own_window1_close_cents >= 0).map((row) => ({ identity: row.identity, entry_cents: row.after_entry_cents, close_cents: row.own_window1_close_cents, ask_reachable_low_cents: row.own_ask_reachable_low_cents, predicate: row.delta_to_own_ask_reachable_low_cents === 0 ? "EXACT_ASK_REACHABLE_FLOOR_EQUALS_W1_CLOSE; STRICT_BELOW_CLOSE_IS_UNATTAINABLE_ON_BOUND_ASK_EVIDENCE" : "ENTRY_ABOVE_REACHABLE_LOW" })),
    five_game_gate_passed: gate.five_game_gate_passed,
    population_804_authorized: gate.population_804_authorized_by_gate,
    population_804_run: gate.population_804_run,
  },
  constants: {
    dwell_seconds: { value: 10, provenance: `${branchRaw}/.claude/window1_live_v4_replay/honest_fill_model_20260801/HONEST_FILL_MODEL_CONTRACT.json` },
    quantity_contracts: { value: 5, provenance: `${branchRaw}/.claude/window1_live_v4_replay/honest_fill_model_20260801/HONEST_FILL_MODEL_CONTRACT.json` },
    invented_v6_numeric_thresholds: [],
  },
};
write("DYNAMIC_RENARROW_V6_CORRECTION_RECEIPT.json", correction);

const libraryHash = hash(libraryPath), comparisonLibraryHash = hash(comparisonLibrary), replayHash = hash(replayPath), comparisonReplayHash = hash(comparisonReplay), gateHash = hash(gatePath), comparisonGateHash = hash(comparisonGate);
if (libraryHash !== comparisonLibraryHash || replayHash !== comparisonReplayHash || gateHash !== comparisonGateHash) throw new Error("deterministic comparison mismatch");
write("DETERMINISM_AND_TEST_RECEIPT.json", {
  schema_version: "WINDOW1_DYNAMIC_RENARROW_V6_DETERMINISM_AND_TEST_RECEIPT",
  two_clean_builds: {
    library: { build_1_sha256: comparisonLibraryHash, build_2_sha256: libraryHash, byte_identical: true },
    replay: { build_1_sha256: comparisonReplayHash, build_2_sha256: replayHash, byte_identical: true },
    honest_gate: { build_1_sha256: comparisonGateHash, build_2_sha256: gateHash, byte_identical: true },
  },
  tests: { passed: testsPassed, commands: ["node arb-executor/tests/test_window1_quote_shape_dynamic_renarrow_v6.js", "node arb-executor/tests/test_window1_quote_shape_descent_verdict_v5.js", "node arb-executor/tests/test_window1_quote_shape_pair_wiring_v3.js", "node arb-executor/tests/test_window1_quote_shape_stable_ask_v2.js", "node arb-executor/tests/test_window1_quote_shape_stable_signer_v4.js"] },
  scorer_invocations: 0,
  population_804_run: false,
});

const sourceFiles = [
  "arb-executor/analysis/build_window1_quote_shape_library_v1.js",
  "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js",
  "arb-executor/analysis/build_window1_dynamic_renarrow_package_v6.js",
  "arb-executor/analysis/build_window1_five_exact_honest_gate_v1.js",
  "arb-executor/analysis/window1_quote_shape_descent_verdict_v5.js",
  "arb-executor/analysis/window1_quote_shape_pair_wiring_v3.js",
  "arb-executor/analysis/window1_quote_shape_stable_signer_v4.js",
  "arb-executor/tests/test_window1_quote_shape_dynamic_renarrow_v6.js",
  ".claude/window1_live_v4_replay/honest_fill_model_20260801/HONEST_FILL_MODEL_CONTRACT.json",
  ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv",
  ".claude/window1_live_v4_replay/five_exact_descent_verdict_v5_20260801/FIVE_GAME_DESCENT_VERDICT_V5_REPLAY.json",
  ".claude/window1_live_v4_replay/five_exact_descent_verdict_v5_20260801/FIVE_GAME_HONEST_GATE.json",
];
write("SOURCE_HASH_MANIFEST.json", { schema_version: "WINDOW1_DYNAMIC_RENARROW_V6_SOURCE_HASH_MANIFEST", files: Object.fromEntries(sourceFiles.map((relative) => { const file = path.join(repo, relative); return [relative, { sha256: hash(file), bytes: bytes(file) }]; })) });

const table = beforeAfter.map((row) => `| ${row.category} | ${row.price_region} | ${row.identity.split("|")[1]} | ${row.action_clock_labels.t_minus_scheduled} | ${row.action_clock_labels.t_minus_actual_bell} | ${row.after_entry_cents} | ${row.honest_fill_class} | ${row.own_window1_close_cents} | ${row.delta_to_own_window1_close_cents >= 0 ? "+" : ""}${row.delta_to_own_window1_close_cents} | ${row.own_bell_price_cents} | ${row.delta_to_own_bell_price_cents >= 0 ? "+" : ""}${row.delta_to_own_bell_price_cents} | ${row.own_ask_reachable_low_cents} | ${row.delta_to_own_ask_reachable_low_cents >= 0 ? "+" : ""}${row.delta_to_own_ask_reachable_low_cents} | NOT_BOUND | ${row.fired_predicates.join("; ")} | ${branchRaw}/.claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/FIVE_GAME_HONEST_GATE.json |`).join("\n");
write("REPORT.md", `# Window-1 five-game dynamic re-narrow V6\n\n| Category | Price region | Leg | T− scheduled | T− actual bell | Entry | Honest class | W1 close | Δ close | Bell | Δ bell | Ask-low | Δ ask-low | Pair ref / Δ | Predicates | Raw source |\n|---|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|---|\n${table}\n\nFive honest pair completions and three strict both-legs-below-close objective passes are recorded in ${branchRaw}/.claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/FIVE_GAME_HONEST_GATE.json. The gate is FAIL and the 804 was not run. LAJ and VED sit exactly at both their bound ask-reachable lows and their own W1 closes; the exact identities and predicates are in ${branchRaw}/.claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/DYNAMIC_RENARROW_V6_CORRECTION_RECEIPT.json.\n\nThe two named defects, BRA lag clocks, stale-class reclassification receipts, constant provenance, and before/after movements are in ${branchRaw}/.claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/DYNAMIC_RENARROW_V6_CORRECTION_RECEIPT.json. This remains a five-game cold validation only; population behavior is unvalidated.\n`);

const artifactFiles = fs.readdirSync(root).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
write("ARTIFACT_HASH_MANIFEST.json", { schema_version: "WINDOW1_DYNAMIC_RENARROW_V6_ARTIFACT_HASH_MANIFEST", files: Object.fromEntries(artifactFiles.map((name) => [name, { sha256: hash(path.join(root, name)), bytes: bytes(path.join(root, name)) }])) });
process.stdout.write(canonical({ status: "BUILT", library_sha256: libraryHash, replay_sha256: replayHash, gate_sha256: gateHash, honest_completed_pairs: gate.honest_completed_pair_count, objective_passes: gate.objective_gate_pass_count, five_game_gate_passed: gate.five_game_gate_passed, population_804_run: gate.population_804_run }));
