#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/five_exact_descent_verdict_v5_20260801")));
const libraryPath = path.join(output, "QUOTE_SHAPE_LIBRARY_LEAVE_FIVE_OUT_WITH_DESCENT_ORDINAL_V5.json");
const replayPath = path.join(output, "FIVE_GAME_DESCENT_VERDICT_V5_REPLAY.json");
const gatePath = path.join(output, "FIVE_GAME_HONEST_GATE.json");
const beforePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_stable_signer_v4_20260801/FIVE_GAME_HONEST_GATE.json");
const sourceFiles = [
  "arb-executor/analysis/build_window1_quote_shape_library_v1.js",
  "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js",
  "arb-executor/analysis/window1_quote_shape_descent_verdict_v5.js",
  "arb-executor/analysis/window1_quote_shape_stable_signer_v4.js",
  "arb-executor/analysis/window1_quote_shape_pair_wiring_v3.js",
  "arb-executor/analysis/build_window1_five_exact_honest_gate_v1.js",
  ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv",
  ".claude/window1_live_v4_replay/honest_fill_model_20260801/HONEST_FILL_MODEL_CONTRACT.json",
  ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/CEILING_CENSUS.json",
];

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileIdentity(file) { const bytes = fs.readFileSync(file); return { sha256: sha256(bytes), bytes: bytes.length }; }
function legMap(gate) { const out = new Map(); for (const event of gate.events) for (const leg of event.legs) out.set(`${event.event_id}|${leg.leg_id}`, { event, leg }); return out; }

function main() {
  const library = JSON.parse(fs.readFileSync(libraryPath));
  const replay = JSON.parse(fs.readFileSync(replayPath));
  const gate = JSON.parse(fs.readFileSync(gatePath));
  const before = JSON.parse(fs.readFileSync(beforePath));
  const cells = [];
  let shapeCount = 0, supportN = 0, censoredN = 0;
  for (const [groupKey, group] of Object.entries(library.groups).sort(([a], [b]) => a.localeCompare(b))) {
    const [category, priceRegion] = groupKey.split("|");
    for (const shape of group.shapes) {
      const distribution = shape.descent_to_final_reachable_low;
      shapeCount += 1; supportN += distribution.support_n; censoredN += distribution.censored_n;
      cells.push({ category, price_region: priceRegion, shape_id: shape.shape_id, topology: shape.topology, shape_members: shape.n, distribution });
    }
  }
  const distributionReceipt = {
    schema_version: "WINDOW1_QUOTE_SHAPE_DESCENT_TO_FINAL_REACHABLE_LOW_V5",
    score_free: true,
    fit_population: "all positive-evaluator Window-1 quote legs except the five exact-start validation games",
    training_events: library.training_events,
    training_legs: library.training_legs,
    excluded_events: library.excluded_cold_test_events,
    group_count: Object.keys(library.groups).length,
    shape_count: shapeCount,
    reachable_support_legs: supportN,
    censored_legs: censoredN,
    grain: "category + formed-book price region + exact surviving quote-shape class",
    event_measure: "number of strictly lower new-low ask transitions through the first exact-five, ten-second occurrence of the final ask-reachable low",
    verdict_statistic: "within-cell empirical median among members with at least one observed new-low descent; zero-descent members are excluded only after a descent is causally observed",
    invented_numeric_thresholds: [],
    cells,
  };
  fs.writeFileSync(path.join(output, "DESCENT_TO_FINAL_REACHABLE_LOW_DISTRIBUTIONS.json"), canonical(distributionReceipt));

  const beforeMap = legMap(before), afterMap = legMap(gate), changes = [];
  for (const [key, afterRow] of [...afterMap].sort(([a], [b]) => a.localeCompare(b))) {
    const beforeRow = beforeMap.get(key); if (!beforeRow) throw new Error(`missing before row ${key}`);
    changes.push({
      event_id: afterRow.event.event_id,
      category: afterRow.leg.category,
      price_region: afterRow.leg.price_region,
      leg_id: afterRow.leg.leg_id,
      before_entry_cents: beforeRow.leg.proposed_entry_cents,
      after_entry_cents: afterRow.leg.proposed_entry_cents,
      movement_cents: beforeRow.leg.proposed_entry_cents == null || afterRow.leg.proposed_entry_cents == null ? null : afterRow.leg.proposed_entry_cents - beforeRow.leg.proposed_entry_cents,
      before_terminal_reason: beforeRow.leg.terminal_reason,
      after_terminal_reason: afterRow.leg.terminal_reason,
      after_fill_class: afterRow.leg.honest_fill_class,
      own_close_cents: afterRow.leg.own_window1_close_cents,
      ask_reachable_low_cents: afterRow.leg.own_ask_reachable_low_cents,
      after_gap_to_close_cents: afterRow.leg.delta_to_own_window1_close_cents,
      after_gap_to_ask_reachable_low_cents: afterRow.leg.delta_to_own_ask_reachable_low_cents,
    });
  }
  const correction = {
    schema_version: "WINDOW1_DESCENT_VERDICT_V5_BEFORE_AFTER_RECEIPT",
    defect_before: "the medoid future verdict could call FLOOR on the first new-low descent without consulting the fitted number of descents to the final reachable low",
    defect_after: "every post-descent FLOOR verdict consumes the leave-five-out within-cell descent ordinal; below the fitted median remains LOWER and zero matching support is UNKNOWN",
    numeric_movement: changes,
    five_game_gate: {
      passed: gate.five_game_gate_passed,
      honest_completed_pairs: gate.honest_completed_pair_count,
      objective_passes: gate.objective_gate_pass_count,
      fill_classes: gate.honest_fill_class_counts,
    },
    population_804_run: false,
    population_stop_reason: gate.five_game_gate_passed ? null : "FIVE_GAME_GATE_FAILED",
  };
  fs.writeFileSync(path.join(output, "DESCENT_VERDICT_V5_CORRECTION_RECEIPT.json"), canonical(correction));

  const report = `# Window-1 fitted descent verdict V5\n\nThis is a score-free, cold five-game gate. The five games were excluded from the fit.\n\nFit: ${library.training_events} events / ${library.training_legs} legs, ${Object.keys(library.groups).length} category-region groups, ${shapeCount} quote-shape cells. Reachable support: ${supportN}; censored: ${censoredN}.\n\nThe fitted quantity is the count of new-low ask descents at which the final ten-second, exact-five ask-reachable low first becomes established. After a descent is observed, the verdict uses the empirical within-cell median among descending training members. No numeric threshold was invented.\n\nFive-game gate: ${gate.five_game_gate_passed ? "PASS" : "FAIL"}. Honest completed pairs: ${gate.honest_completed_pair_count}/5. Objective passes: ${gate.objective_gate_pass_count}/5. Fill classes: ${gate.honest_fill_class_counts.PROVEN_MAKER} maker, ${gate.honest_fill_class_counts.PROVEN_TAKER} taker, ${gate.honest_fill_class_counts.UNPROVEN} unproven.\n\nThe 804 was ${gate.population_804_run ? "run" : "not run"}. The frozen 516 take-reachable and 253 maker-reachable ceilings were not exercised because the five-game gate failed.\n`;
  fs.writeFileSync(path.join(output, "REPORT.md"), report);
  const sourceManifest = { schema_version: "WINDOW1_DESCENT_VERDICT_V5_SOURCE_MANIFEST", sources: Object.fromEntries(sourceFiles.map((relative) => [relative, fileIdentity(path.join(repo, relative))])), fitted_library: fileIdentity(libraryPath), replay: fileIdentity(replayPath), before_gate: fileIdentity(beforePath) };
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical(sourceManifest));
  const artifacts = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_DESCENT_VERDICT_V5_ARTIFACT_MANIFEST", files: Object.fromEntries(artifacts.map((name) => [name, fileIdentity(path.join(output, name))])) }));
  process.stdout.write(canonical({ status: "BUILT", training_events: library.training_events, training_legs: library.training_legs, shapes: shapeCount, gate_passed: gate.five_game_gate_passed, objective_passes: gate.objective_gate_pass_count, population_804_run: false }));
}

main();
