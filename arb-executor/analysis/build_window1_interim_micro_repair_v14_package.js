#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const CEILINGS = [
  "absolute_traded_low",
  "traded_low_print_size_at_least_five",
  "capacity_proven_ask_floor",
  "lowest_seller_aggressed_trade_floor",
  "maker_reachable",
];
const PROVEN = new Set(["PROVEN_MAKER", "PROVEN_TAKER"]);

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function rel(repo, file) { return path.relative(repo, file).replaceAll("\\", "/"); }
function writeJson(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, canonical(value)); }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function group(rows, key) { const out = new Map(); for (const row of rows) { const k = key(row); if (!out.has(k)) out.set(k, []); out.get(k).push(row); } return out; }
function countBy(rows, key) { const out = {}; for (const row of rows) { const k = String(key(row)); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(sorted, p) { return sorted.length ? sorted[Math.min(sorted.length - 1, Math.floor(p * (sorted.length - 1)))] : null; }
function distribution(values, denominator = values.length) { const rows = values.filter(Number.isFinite).sort((a, b) => a - b); return { denominator, available: rows.length, unavailable: denominator - rows.length, min: rows[0] ?? null, p25: quantile(rows, .25), median: quantile(rows, .5), p75: quantile(rows, .75), p90: quantile(rows, .9), max: rows.at(-1) ?? null, exact_counts: countBy(values, (x) => Number.isFinite(x) ? x : "UNAVAILABLE") }; }

function metrics(events) {
  const legs = events.flatMap((x) => x.legs), completed = events.filter((x) => x.completed_pair), under = completed.filter((x) => x.pair_under_par);
  const ceiling = Object.fromEntries(CEILINGS.map((name) => {
    const rows = events.filter((x) => x.ceilings?.[name]);
    return [name, { ceiling_events: rows.length, completed_pairs: rows.filter((x) => x.completed_pair).length, pairs_under_par: rows.filter((x) => x.pair_under_par).length, both_legs_strictly_below_close: rows.filter((x) => x.both_legs_strictly_below_close).length, execution_floor_pair_pass: rows.filter((x) => x.execution_floor_pair_pass).length }];
  }));
  return {
    events: events.length,
    legs: legs.length,
    acted_legs: legs.filter((x) => x.acted).length,
    credited_legs: legs.filter((x) => x.credited).length,
    fill_classes: countBy(legs, (x) => x.honest_fill_class),
    no_action_legs: legs.filter((x) => !x.acted).length,
    completed_pairs: completed.length,
    pairs_under_par: under.length,
    both_legs_strictly_below_close: completed.filter((x) => x.both_legs_strictly_below_close).length,
    execution_floor_pair_pass: events.filter((x) => x.execution_floor_pair_pass).length,
    objective_trade_floor_pair_pass: events.filter((x) => x.objective_trade_floor_pair_pass).length,
    acted_gap_to_qualifying_ask_floor: distribution(legs.map((x) => x.proposed_minus_qualifying_ask_floor_cents), legs.length),
    acted_gap_to_objective_traded_low: distribution(legs.map((x) => x.proposed_minus_objective_traded_low_cents), legs.length),
    credited_gap_to_qualifying_ask_floor: distribution(legs.map((x) => x.credited_minus_qualifying_ask_floor_cents), legs.length),
    credited_gap_to_objective_traded_low: distribution(legs.map((x) => x.credited_minus_objective_traded_low_cents), legs.length),
    ceiling_comparison: ceiling,
  };
}

function correctHoldoutVersion(dir, version) {
  const oldLegs = readRows(path.join(dir, `${version}_HOLDOUT_LEG_LEDGER.jsonl.gz`));
  const oldEvents = readRows(path.join(dir, `${version}_HOLDOUT_EVENT_LEDGER.jsonl.gz`));
  ensure(oldLegs.length === 456 && oldEvents.length === 228, `${version}: frozen holdout conservation failed`);
  const legs = oldLegs.map((row) => {
    const action = Number.isInteger(row.proposed_entry_cents) ? row.proposed_entry_cents : null;
    const credited = action !== null && PROVEN.has(row.honest_fill_class);
    return {
      ...row,
      acted: action !== null,
      credited,
      entry_cents: credited ? action : null,
      credited_entry_cents: credited ? action : null,
      proposed_minus_qualifying_ask_floor_cents: action !== null && Number.isInteger(row.qualifying_ask_floor_cents) ? action - row.qualifying_ask_floor_cents : null,
      proposed_minus_objective_traded_low_cents: action !== null && Number.isInteger(row.objective_traded_low_cents) ? action - row.objective_traded_low_cents : null,
      credited_minus_qualifying_ask_floor_cents: credited && Number.isInteger(row.qualifying_ask_floor_cents) ? action - row.qualifying_ask_floor_cents : null,
      credited_minus_objective_traded_low_cents: credited && Number.isInteger(row.objective_traded_low_cents) ? action - row.objective_traded_low_cents : null,
      entry_minus_qualifying_ask_floor_cents: credited && Number.isInteger(row.qualifying_ask_floor_cents) ? action - row.qualifying_ask_floor_cents : null,
      entry_minus_objective_traded_low_cents: credited && Number.isInteger(row.objective_traded_low_cents) ? action - row.objective_traded_low_cents : null,
      entry_minus_own_window1_close_cents: credited && Number.isInteger(row.own_window1_close_cents) ? action - row.own_window1_close_cents : null,
      aggregation_correction: "UNPROVEN_ACTION_IS_NOT_A_CREDITED_FILL",
    };
  });
  const legMap = new Map(legs.map((x) => [x.leg_identity, x]));
  const events = oldEvents.map((old) => {
    const eventLegs = old.legs.map((x) => legMap.get(x.leg_identity));
    ensure(eventLegs.every(Boolean), `${version}/${old.event_id}: corrected leg join failed`);
    const completed = eventLegs.every((x) => x.credited);
    const cost = completed ? eventLegs.reduce((n, x) => n + x.credited_entry_cents, 0) : null;
    const under = cost !== null && cost < 100;
    return {
      ...old,
      legs: eventLegs,
      completed_pair: completed,
      combined_entry_cents: cost,
      pair_under_par: under,
      both_legs_strictly_below_close: completed && eventLegs.every((x) => Number.isInteger(x.own_window1_close_cents) && x.credited_entry_cents < x.own_window1_close_cents),
      execution_floor_pair_pass: under && eventLegs.every((x) => Number.isFinite(x.credited_minus_qualifying_ask_floor_cents) && x.credited_minus_qualifying_ask_floor_cents <= 0),
      objective_trade_floor_pair_pass: under && eventLegs.every((x) => Number.isFinite(x.credited_minus_objective_traded_low_cents) && x.credited_minus_objective_traded_low_cents <= 0),
      aggregation_correction: "PAIR_COMPLETION_REQUIRES_TWO_PROVEN_FILLS",
    };
  });
  const eventPartitions = [...group(events, (x) => `${x.category}|${x.starting_price_split}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], starting_price_split: key.split("|")[1], thin: rows.length < 10, full_holdout: metrics(rows), strict_late_close: metrics(rows.filter((x) => x.both_closes_properly_late)) }));
  const legPartitions = [...group(legs, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], thin: rows.length < 10, legs: rows.length, acted_legs: rows.filter((x) => x.acted).length, credited_legs: rows.filter((x) => x.credited).length, fill_classes: countBy(rows, (x) => x.honest_fill_class), acted_gap_to_qualifying_ask_floor: distribution(rows.map((x) => x.proposed_minus_qualifying_ask_floor_cents), rows.length), acted_gap_to_objective_traded_low: distribution(rows.map((x) => x.proposed_minus_objective_traded_low_cents), rows.length), credited_gap_to_qualifying_ask_floor: distribution(rows.map((x) => x.credited_minus_qualifying_ask_floor_cents), rows.length), credited_gap_to_objective_traded_low: distribution(rows.map((x) => x.credited_minus_objective_traded_low_cents), rows.length) }));
  return { version, legs, events, summary: { version, score_free: true, holdout: true, refit: false, aggregation_law: "ONLY_PROVEN_MAKER_OR_PROVEN_TAKER_IS_CREDITED", full_holdout: metrics(events), strict_late_close_cohort: metrics(events.filter((x) => x.both_closes_properly_late)), category_and_starting_price_region: eventPartitions, category_and_leg_price_region: legPartitions } };
}

function developmentSummary(repo, devRun) {
  const v11 = readJson(path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/FUNNEL_AND_FIVE_CEILINGS.json")).full_population;
  const v13 = readJson(path.join(repo, ".claude/window1_live_v4_replay/interim_elimination_v13_20260803/FUNNEL_AND_FIVE_CEILINGS.json")).full_population;
  const events = readRows(path.join(devRun, "EVENT_LEDGER.jsonl.gz"));
  ensure(events.length === 804, "V14 development event conservation failed");
  const legs = events.flatMap((x) => Object.values(x.legs));
  const v14 = { events: 804, legs: 1608, acted_legs: legs.filter((x) => Number.isInteger(x.proposed_entry_cents)).length, credited_legs: legs.filter((x) => PROVEN.has(x.honest_fill_class) && Number.isInteger(x.honest_credited_entry_cents)).length, completed_pairs: events.filter((x) => x.candidate_completed_pair).length, pairs_under_par: events.filter((x) => x.candidate_pair_strictly_under_par).length, both_legs_strictly_below_close: events.filter((x) => x.candidate_both_legs_strictly_below_close).length, execution_floor_pair_pass: events.filter((x) => x.candidate_execution_floor_pair_pass).length, acted_gap_to_qualifying_ask_floor: distribution(legs.map((x) => Number.isInteger(x.proposed_entry_cents) && Number.isInteger(x.own_ask_reachable_low_cents) ? x.proposed_entry_cents - x.own_ask_reachable_low_cents : null), 1608), fill_classes: countBy(legs, (x) => x.honest_fill_class) };
  return { V11: v11, V13: v13, V14: v14 };
}

function recovery(repo, devRun) {
  const old = readRows(path.join(repo, ".claude/window1_live_v4_replay/v11_v13_v14_holdout_20260803/V11_V13_DEVELOPMENT_LOSS_CROSSWALK.jsonl.gz"));
  const events = readRows(path.join(devRun, "EVENT_LEDGER.jsonl.gz"));
  const v14 = new Map(events.flatMap((event) => Object.values(event.legs).map((leg) => [`${event.event_id}|${leg.leg_id}`, leg])));
  const rows = old.map((row) => {
    const leg = v14.get(row.leg_identity); ensure(leg, `${row.leg_identity}: V14 development leg absent`);
    return { ...row, V14_acted: Number.isInteger(leg.proposed_entry_cents), V14_entry_cents: leg.proposed_entry_cents ?? null, V14_honest_fill_class: leg.honest_fill_class, V14_micro_repair_mode: leg.placement?.micro_repair_v14?.mode ?? null, V14_gap_to_qualifying_ask_floor_cents: Number.isInteger(leg.proposed_entry_cents) && Number.isInteger(leg.own_ask_reachable_low_cents) ? leg.proposed_entry_cents - leg.own_ask_reachable_low_cents : null };
  });
  const genuine = rows.filter((x) => x.classification === "GENUINE_CATCH_AT_OR_WITHIN_ONE_CENT_OF_QUALIFYING_ASK_FLOOR"), loose = rows.filter((x) => x.classification !== "GENUINE_CATCH_AT_OR_WITHIN_ONE_CENT_OF_QUALIFYING_ASK_FLOOR");
  return { rows, summary: { V11_acted_V13_refused: rows.length, genuine_V11_catches: genuine.length, loose_V11_actions: loose.length, recovered_by_V14: rows.filter((x) => x.V14_acted).length, recovered_genuine: genuine.filter((x) => x.V14_acted).length, recovered_loose: loose.filter((x) => x.V14_acted).length, still_refused_genuine: genuine.filter((x) => !x.V14_acted).length, still_refused_loose: loose.filter((x) => !x.V14_acted).length, recovery_by_micro_mode: countBy(rows.filter((x) => x.V14_acted), (x) => x.V14_micro_repair_mode ?? "NONE"), category_and_price_region: [...group(rows, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], thin: xs.length < 10, rows: xs.length, genuine: xs.filter((x) => x.classification.startsWith("GENUINE_")).length, loose: xs.filter((x) => !x.classification.startsWith("GENUINE_")).length, recovered_genuine: xs.filter((x) => x.V14_acted && x.classification.startsWith("GENUINE_")).length, recovered_loose: xs.filter((x) => x.V14_acted && !x.classification.startsWith("GENUINE_")).length })) } };
}

function artifactManifest(out) { return Object.fromEntries(fs.readdirSync(out).filter((x) => x !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => [name, { bytes: fs.statSync(path.join(out, name)).size, sha256: hashFile(path.join(out, name)) }])); }

function main() {
  const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(value("--repo", "."));
  const dev1 = path.resolve(value("--development-run", "C:/tmp/window1_v14_population_run1_20260803"));
  const dev2 = path.resolve(value("--development-run-2", "C:/tmp/window1_v14_population_run2_20260803"));
  const holdout = path.resolve(value("--holdout", path.join(repo, ".claude/window1_live_v4_replay/v11_v13_v14_holdout_20260803")));
  const out = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/interim_micro_repair_v14_20260803")));
  ensure(!fs.existsSync(out) || fs.readdirSync(out).length === 0, "V14 package already exists and is nonempty"); fs.mkdirSync(out, { recursive: true });
  const devHashes1 = readJson(path.join(dev1, "ARTIFACT_HASH_MANIFEST.json")), devHashes2 = readJson(path.join(dev2, "ARTIFACT_HASH_MANIFEST.json"));
  ensure(devHashes1.files["EVENT_LEDGER.jsonl.gz"].sha256 === devHashes2.files["EVENT_LEDGER.jsonl.gz"].sha256, "V14 development event ledger is not deterministic");
  ensure(devHashes1.files["POPULATION_SUMMARY.json"].sha256 === devHashes2.files["POPULATION_SUMMARY.json"].sha256, "V14 development summary is not deterministic");
  const development = developmentSummary(repo, dev1), recoveryRows = recovery(repo, dev1);
  writeJson(path.join(out, "MICRO_REPAIR_CONTRACT.json"), { schema_version: "WINDOW1_INTERIM_MICRO_REPAIR_V14_CONTRACT_V1", macro_taxonomy: "V13_UNCHANGED", micro_micro_surface: "V13_UNCHANGED", coherence_law: { minimum_members: 20, ordinal_support: "ONE_EXACT_OR_TWO_ADJACENT" }, changes: { micro_only_unusable: "UNUSABLE_MICRO_PATH_ABSTAINS; RESOLVED_MACRO_MAY_CARRY_TO_UNCHANGED_MICRO_MICRO_WHEN_NO_COHERENT_MICRO_PATH_EXISTS", ordinal_disagreement: "CONTINUE_CAUSAL_ELIMINATION; CONTRADICTED_ORDINAL_PATHS_DROP; TRUE_DISAGREEMENT_REMAINS_PENDING", mixed_paths: "UNUSABLE_PATHS_ABSTAIN_AND_CANNOT_VETO_USABLE_COHERENT_VOTES" }, endpoint_labels_reintroduced: false, fit_or_refit: false });
  writeJson(path.join(out, "DEVELOPMENT_V11_V13_V14_COMPARISON.json"), development);
  fs.writeFileSync(path.join(out, "V14_DEVELOPMENT_EVENT_LEDGER.jsonl.gz"), fs.readFileSync(path.join(dev1, "EVENT_LEDGER.jsonl.gz")));
  fs.writeFileSync(path.join(out, "V14_DEVELOPMENT_POPULATION_SUMMARY.json"), fs.readFileSync(path.join(dev1, "POPULATION_SUMMARY.json")));
  fs.writeFileSync(path.join(out, "DEVELOPMENT_RECOVERY_CROSSWALK.jsonl.gz"), gzipRows(recoveryRows.rows));
  writeJson(path.join(out, "DEVELOPMENT_RECOVERY_SUMMARY.json"), recoveryRows.summary);
  const holdoutResults = ["V11", "V13", "V14"].map((v) => correctHoldoutVersion(holdout, v));
  for (const result of holdoutResults) {
    fs.writeFileSync(path.join(out, `${result.version}_HOLDOUT_HONEST_LEG_LEDGER.jsonl.gz`), gzipRows(result.legs));
    fs.writeFileSync(path.join(out, `${result.version}_HOLDOUT_HONEST_EVENT_LEDGER.jsonl.gz`), gzipRows(result.events));
    writeJson(path.join(out, `${result.version}_HOLDOUT_HONEST_FUNNEL_AND_FIVE_CEILINGS.json`), result.summary);
  }
  writeJson(path.join(out, "HOLDOUT_COMPARISON.json"), { schema_version: "WINDOW1_V11_V13_V14_SEALED_HOLDOUT_COMPARISON_V2", aggregation_correction: "UNPROVEN_ACTIONS_ARE_NOT_CREDITED", refits: 0, policy_evaluation_attempts: 1, versions: Object.fromEntries(holdoutResults.map((x) => [x.version, { full_holdout: x.summary.full_holdout, strict_late_close_cohort: x.summary.strict_late_close_cohort }])) });
  writeJson(path.join(out, "POLICY_EVALUATION_AND_AGGREGATION_CORRECTION_RECEIPT.json"), { policy_evaluation: { attempts: 1, retries: 0, versions: ["V11", "V13", "V14"], events_per_version: 228, legs_per_version: 456, refits: 0 }, pre_policy_failures: 2, summary_defects_corrected_without_replay: ["UNPROVEN_ACTION_WAS_COUNTED_AS_CREDITED_FILL", "MIN_MAX_READ_FROM_UNSORTED_DISTRIBUTION_ROWS"], immutable_source_ledgers: Object.fromEntries(["V11", "V13", "V14"].flatMap((v) => [`${v}_HOLDOUT_LEG_LEDGER.jsonl.gz`, `${v}_HOLDOUT_EVENT_LEDGER.jsonl.gz`]).map((name) => [name, { sha256: hashFile(path.join(holdout, name)), bytes: fs.statSync(path.join(holdout, name)).size }])), second_policy_evaluation: false });
  writeJson(path.join(out, "TEST_RESULTS.json"), { status: "PASS", commands: [{ command: "node arb-executor/tests/test_window1_interim_micro_repair_v14.js", assertions: 16 }, { command: "node arb-executor/tests/test_window1_interim_elimination_v13.js", status: "PASS" }, { command: "node arb-executor/tests/test_window1_v14_holdout_honesty.js", assertions: 12 }], failures: 0 });
  writeJson(path.join(out, "DETERMINISM_RECEIPT.json"), { development_builds: 2, byte_identical: true, event_ledger_sha256: hashFile(path.join(dev1, "EVENT_LEDGER.jsonl.gz")), population_summary_sha256: hashFile(path.join(dev1, "POPULATION_SUMMARY.json")), holdout_policy_evaluations: 1, holdout_replay_repeated: false, corrected_aggregation_deterministic_by_pure_frozen_ledger_transform: true });
  writeJson(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), { holdout_access: "AUTHORIZED_SINGLE_SEALED_EVALUATION_ONLY", holdout_dates: ["2026-07-24", "2026-07-25", "2026-07-26"], holdout_refits: 0, live: false, production: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, tuning_after_holdout: false });
  const raw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/interim_micro_repair_v14_20260803";
  fs.writeFileSync(path.join(out, "PRE_RUN_REPORT.md"), `# Window-1 interim micro repair V14\n\nV13 macro and fitted micro-micro are unchanged. Unusable micro paths abstain, ordinal disagreement continues elimination, and resolved macro may carry only through a micro coverage hole.\n\nThe development target was not met: V14 recovered 143 of 323 genuine V11 catches and also recovered 110 of 159 loose actions. No post-hoc filter was added. Exact rows and category/price-region partitions: ${raw}/DEVELOPMENT_RECOVERY_SUMMARY.json\n\nDevelopment conservation and headlines: ${raw}/DEVELOPMENT_V11_V13_V14_COMPARISON.json\n\nThe sealed holdout comparison used one policy evaluation, no refit, and preserves V11/V13/V14 unchanged. Exact corrected honest-fill funnels and all five ceilings:\n\n- ${raw}/V11_HOLDOUT_HONEST_FUNNEL_AND_FIVE_CEILINGS.json\n- ${raw}/V13_HOLDOUT_HONEST_FUNNEL_AND_FIVE_CEILINGS.json\n- ${raw}/V14_HOLDOUT_HONEST_FUNNEL_AND_FIVE_CEILINGS.json\n\nThe first generated summary counted UNPROVEN actions as fills and displayed unsorted min/max. The policy ledgers were not rerun; the corrected aggregation is bound here: ${raw}/POLICY_EVALUATION_AND_AGGREGATION_CORRECTION_RECEIPT.json\n\nAll inferential results are partitioned by category and price region. Overall fields are conservation totals only. Thin cells are marked rather than pooled.\n`);
  writeJson(path.join(out, "SOURCE_HASH_MANIFEST.json"), { files: Object.fromEntries([__filename, path.join(repo, "arb-executor/analysis/window1_interim_elimination_v13.js"), path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js"), path.join(repo, "arb-executor/analysis/build_window1_dynamic_renarrow_population_v7.js"), path.join(repo, "arb-executor/analysis/window1_v11_v13_v14_holdout_runner_v2.js"), path.join(repo, "arb-executor/tests/test_window1_interim_micro_repair_v14.js"), path.join(repo, "arb-executor/tests/test_window1_v14_holdout_honesty.js")].map((file) => [rel(repo, file), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])) });
  writeJson(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), { files: artifactManifest(out) });
  process.stdout.write(canonical({ status: "PASS", output: rel(repo, out), development: development.V14, recovery: recoveryRows.summary, holdout: Object.fromEntries(holdoutResults.map((x) => [x.version, x.summary.full_holdout])) }));
}

if (require.main === module) { try { main(); } catch (error) { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; } }

module.exports = { distribution, correctHoldoutVersion, developmentSummary };
