#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function load(file) { return JSON.parse(fs.readFileSync(file)); }

function main() {
  const args = process.argv.slice(2), get = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(get("--repo", "."));
  const root = path.join(repo, ".claude/window1_live_v4_replay");
  const sources = {
    fill: path.join(root, "honest_fill_model_20260801/FOUR_FILL_CLASSIFICATION.json"),
    pairs: path.join(root, "honest_fill_model_20260801/PAIR_COMPLETION_RESCORING.json"),
    aggressor: path.join(root, "aggressor_ceiling_census_20260801/AGGRESSOR_SPLIT.json"),
    ceilings: path.join(root, "aggressor_ceiling_census_20260801/CEILING_CENSUS.json"),
    fee: path.join(root, "fee_aware_take_census_20260801/FEE_AWARE_TAKE_CENSUS.json"),
    commitment: path.join(root, "first_leg_commitment_diagnostic_20260801/COMMITMENT_GAP_CENSUS.json"),
    conditional: path.join(root, "first_leg_commitment_diagnostic_20260801/SIBLING_FLOOR_CONDITIONAL_CENSUS.json"),
    wiring: path.join(root, "pair_wiring_correction_20260801/PAIR_WIRING_CORRECTION_RECEIPT.json"),
  };
  for (const file of Object.values(sources)) if (!fs.existsSync(file)) throw new Error(`missing dependency ${file}`);
  const fill = load(sources.fill), pairs = load(sources.pairs), aggressor = load(sources.aggressor), ceilings = load(sources.ceilings), fee = load(sources.fee), commitment = load(sources.commitment), wiring = load(sources.wiring);
  if (fill.PROVEN_MAKER !== 0 || fill.PROVEN_TAKER !== 3 || fill.UNPROVEN !== 1) throw new Error("honest fill identity mismatch");
  if (aggressor.population.events !== 804 || ceilings.controlling_take_ceiling !== 516 || fee.rows.length !== 516 || commitment.conservation.D !== 804) throw new Error("population identity mismatch");
  const gate = {
    schema_version: "WINDOW1_ENTRY_HONESTY_DEPENDENCY_GATE_V1",
    score_free: true,
    dependencies: {
      honest_fill_model: "LANDED",
      aggressor_split: "LANDED_DESCRIPTIVE",
      fee_aware_take_rule: "BLOCKED_EXPECTED_CLOSE_NOT_BOUND",
      first_leg_commitment_measurement: "LANDED_DESCRIPTIVE_RULE_REMAINS_INSUFFICIENT_EVIDENCE",
      pair_wiring_correction: "SPECIFIED_AND_SYNTHETICALLY_TESTED_NOT_FIVE_GAME_VALIDATED",
    },
    five_game_replay_run: false,
    five_game_gate_passed: false,
    five_game_blocker: "No independently bound decision-time expected-close input exists for the fee-aware take authority.",
    population_804_policy_run: false,
    population_gate_passed: false,
    scorer_invocations: 0,
    performance_metrics: null,
  };
  const outDir = path.resolve(get("--output", path.join(root, "entry_honesty_dependency_20260801")));
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "DECISION_GATE_RECEIPT.json"), canonical(gate));
  const raw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay";
  const report = [
    "# Window 1 entry-honesty dependency report",
    "",
    "Score-free. Ask-side only. No five-game rerun and no 804 policy replay were run because the decision-time expected-close authority is not bound.",
    "",
    "## 1. Honest fill truth",
    "",
    `Source: ${raw}/honest_fill_model_20260801/FOUR_FILL_CLASSIFICATION.json`,
    "",
    `The four replay credits classify as ${fill.PROVEN_MAKER} PROVEN_MAKER, ${fill.PROVEN_TAKER} PROVEN_TAKER, and ${fill.UNPROVEN} UNPROVEN. NIKVRB is the only honest-model completion (${pairs.completed_pair_count_under_honest_model}/2), and it is a two-taker pair. HUR is UNPROVEN because its exact submission-time own book is absent.`,
    "",
    "## 2. Aggressor split and ceilings",
    "",
    `Flow source: ${raw}/aggressor_ceiling_census_20260801/AGGRESSOR_SPLIT.json`,
    "",
    `Ceiling source: ${raw}/aggressor_ceiling_census_20260801/CEILING_CENSUS.json`,
    "",
    `The ${aggressor.print_conservation.lawful_admitted_prints} lawful prints partition into ${aggressor.print_conservation.buyer_aggressed} buyer-aggressed, ${aggressor.print_conservation.seller_aggressed} seller-aggressed, and ${aggressor.print_conservation.unknown_aggressor} unknown. At the frozen 516 target prices, ${ceilings.summary.maker_both_legs_reachable} events have both legs maker-reachable and ${ceilings.summary.maker_pair_combined_negative} have a combined-negative maker floor; the take ceiling remains ${ceilings.controlling_take_ceiling}. All category, price-region, spread, and both-clock cells are in the linked raw files.`,
    "",
    "## 3. Fee-aware take rule",
    "",
    `Source: ${raw}/fee_aware_take_census_20260801/FEE_AWARE_TAKE_CENSUS.json`,
    "",
    `Using actual W1 closes only as an ex-post oracle, ${fee.ex_post_clearing_count}/516 clear the operator-specified fee comparison. The executable count is NOT_BOUND because expected close at decision time has no bound source. NIKVRB is 16 cents of ex-post pair edge versus 14 cents of five-lot taker fees; the HURBIG floor oracle fails, and HUR itself is unproven in the replay.`,
    "",
    "## 4. First-leg commitment",
    "",
    `Gap source: ${raw}/first_leg_commitment_diagnostic_20260801/COMMITMENT_GAP_CENSUS.json`,
    "",
    `Conditional source: ${raw}/first_leg_commitment_diagnostic_20260801/SIBLING_FLOOR_CONDITIONAL_CENSUS.json`,
    "",
    `Both floors exist for ${commitment.conservation.both_capacity_floors_available}/804 events. ${commitment.conservation.strict_first_leg_commitments} are strictly asynchronous and ${commitment.conservation.simultaneous_floor_evidence} tie. A strictly later sibling floor exists in all ${commitment.conservation.later_sibling_floor_available} asynchronous cases, but ${commitment.conservation.naked_or_never_completed_under_entry_cost_law} finish at combined cost >=100; only ${commitment.conservation.entry_cost_affordable_below_100} are below 100. No causal commitment threshold is validated.`,
    "",
    "## 5. Pair wiring",
    "",
    `Source: ${raw}/pair_wiring_correction_20260801/PAIR_WIRING_CORRECTION_RECEIPT.json`,
    "",
    `Four candidate rows can use the single surviving inverse tuple when each side has its own micro receipt. LAJ/VAN lacked ${wiring.defect_two.missing_terminal_tuple}; V3 adds it as ${wiring.defect_two.tuple_support_class} with empirical n=${wiring.defect_two.tuple_empirical_count}. This is not a validation fill.`,
    "",
    "## 6. Gate",
    "",
    `Source: ${raw}/entry_honesty_dependency_20260801/DECISION_GATE_RECEIPT.json`,
    "",
    "The five-game gate did not run: item 3 cannot make a causal take decision without an expected-close authority. Consequently the 804 policy run was not run. That is the blocking dependency, not an adverse replay result.",
    "",
  ].join("\n");
  fs.writeFileSync(path.join(outDir, "DEPENDENCY_REPORT.md"), report);
  const sourceManifest = Object.fromEntries(Object.entries(sources).map(([key, file]) => [key, { path: path.relative(repo, file).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(file)) }]));
  fs.writeFileSync(path.join(outDir, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_ENTRY_HONESTY_SOURCE_MANIFEST_V1", sources: sourceManifest }));
  const artifacts = fs.readdirSync(outDir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => { const bytes = fs.readFileSync(path.join(outDir, name)); return { path: name, bytes: bytes.length, sha256: sha256(bytes) }; });
  fs.writeFileSync(path.join(outDir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_ENTRY_HONESTY_ARTIFACT_MANIFEST_V1", artifacts }));
  process.stdout.write(canonical({ status: "BUILT", gate, report_sha256: sha256(fs.readFileSync(path.join(outDir, "DEPENDENCY_REPORT.md"))) }));
}

main();
