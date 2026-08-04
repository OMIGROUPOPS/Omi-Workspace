#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const variant = value("--variant", null);
if (!new Set(["FIX_A", "FIX_C"]).has(variant)) throw new Error("--variant must be FIX_A or FIX_C");
const run1 = path.resolve(value("--run1", ""));
const run2 = path.resolve(value("--run2", ""));
const artifactRel = variant === "FIX_A"
  ? ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804"
  : ".claude/window1_live_v4_replay/isolated_fix_c_shape_settlement_v20_20260804";
const out = path.resolve(value("--output", path.join(repo, artifactRel)));
const baseDir = path.join(repo, ".claude/window1_live_v4_replay/pair_couple_abstention_v19_20260803");
const baseEventPath = path.join(baseDir, "POPULATION_EVENT_LEDGER.jsonl.gz");
const baseLegPath = path.join(baseDir, "POPULATION_LEG_LEDGER.jsonl.gz");
const baseFrontierPath = path.join(baseDir, "FRONTIER.json");
const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function ensure(x, message) { if (!x) throw new Error(message); }
function rel(file) { return path.relative(repo, file).replaceAll("\\", "/"); }
function readRows(file) { const s = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return s ? s.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function group(rows, key) { const map = new Map(); for (const row of rows) { const k = key(row); if (!map.has(k)) map.set(k, []); map.get(k).push(row); } return map; }
function countBy(rows, key) { const out = {}; for (const row of rows) { const k = String(key(row)); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const xs = values.filter(Number.isFinite).sort((a, b) => a - b); return xs.length ? xs[Math.floor((xs.length - 1) * p)] : null; }
function distribution(values) { const xs = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: xs.length, null_n: values.length - xs.length, min: xs.length ? Math.min(...xs) : null, p25: quantile(xs, .25), median: quantile(xs, .5), p75: quantile(xs, .75), p90: quantile(xs, .9), max: xs.length ? Math.max(...xs) : null, total_numeric_cents: xs.reduce((a, b) => a + b, 0) }; }

function repairReceipt(candidate) {
  return variant === "FIX_A" ? candidate.placement?.fix_a_anchor_freshness_v20 : candidate.placement?.fix_c_shape_verdict_settlement_v20;
}

function addCandidate(base, candidate) {
  const entry = candidate.honest_credited_entry_cents;
  return {
    ...base,
    acted: candidate.proposed_entry_cents !== null,
    credited: entry !== null,
    honest_fill_class: candidate.honest_fill_class,
    entry_cents: entry,
    action_timestamp_epoch: candidate.action_timestamp_epoch,
    entry_minus_qualifying_ask_floor_cents: entry === null || !Number.isInteger(base.qualifying_ask_floor_cents) ? null : entry - base.qualifying_ask_floor_cents,
    entry_minus_objective_traded_low_cents: entry === null || !Number.isInteger(base.objective_traded_low_cents) ? null : entry - base.objective_traded_low_cents,
    entry_minus_own_window1_close_cents: entry === null || !Number.isInteger(base.own_window1_close_cents) ? null : entry - base.own_window1_close_cents,
    terminal_reason: candidate.terminal_reason,
    placement: candidate.placement,
    source_lane: `${variant}_ISOLATED_ADDITION_TO_FROZEN_V19_NON_ACTION`,
    isolated_repair_added: true,
    isolated_repair_receipt: repairReceipt(candidate),
  };
}

function metrics(events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  const completed = events.filter((event) => event.completed_pair);
  return {
    D: events.length,
    legs: legs.length,
    acted_legs: legs.filter((leg) => leg.acted).length,
    credited_legs: legs.filter((leg) => leg.credited).length,
    completed_pairs: completed.length,
    pairs_under_par: events.filter((event) => event.pair_under_par).length,
    both_legs_strictly_below_close: events.filter((event) => event.both_legs_strictly_below_close).length,
    joint_objective_pairs: events.filter((event) => event.joint_objective_pass).length,
    execution_floor_pair_pass: events.filter((event) => event.execution_floor_pair_pass).length,
    strict_carried_pairs: completed.filter((event) => { const ds = Object.values(event.legs).map((leg) => leg.entry_minus_own_window1_close_cents); return ds.some((x) => x > 0) && ds.some((x) => x < 0); }).length,
  };
}

function frontier(events) {
  const tiers = { LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true };
  const out = {};
  for (const [name, predicate] of Object.entries(tiers)) {
    const rows = events.filter((event) => event.completed_pair && predicate(event.combined_entry_cents));
    out[name] = {
      denominator: events.length,
      completed_pairs: rows.length,
      raw_rate: `${rows.length}/${events.length}`,
      pairs_both_legs_strictly_below_close: rows.filter((event) => event.both_legs_strictly_below_close).length,
      joint_objective_pairs: rows.filter((event) => event.joint_objective_pass).length,
    };
  }
  out.any_price_reference_ceiling = { denominator: events.length, count: events.filter((event) => event.take_ceiling_member).length, law: "FROZEN_516_TAKE_REACHABLE_REFERENCE_CEILING; NOT A POLICY FILL" };
  return out;
}

function regretRow(leg) {
  const numeric = leg.credited && Number.isInteger(leg.objective_traded_low_cents) ? leg.entry_cents - leg.objective_traded_low_cents : null;
  let bucket = "PRINT_BACKED_FLOOR_UNAVAILABLE";
  if (!leg.credited) bucket = "NEVER_PLACED_FULL_REGRET";
  else if (numeric < 0) bucket = "BETTER_THAN_PRINT_FLOOR";
  else if (numeric === 0) bucket = "ZERO";
  else if (numeric <= 3) bucket = "ONE_TO_THREE";
  else if (numeric <= 9) bucket = "FOUR_TO_NINE";
  else bucket = "TEN_OR_MORE";
  return {
    leg_identity: leg.leg_identity,
    event_id: leg.event_id,
    category: leg.category,
    price_region: leg.price_region,
    source_lane: leg.source_lane || "FROZEN_V19_BASE",
    credited_fill_cents: leg.credited ? leg.entry_cents : null,
    achievable_print_backed_floor_cents: leg.objective_traded_low_cents,
    regret_cents: numeric,
    never_placed_carries_full_regret: !leg.credited,
    full_regret_representation: !leg.credited ? "CATEGORICAL_FULL_LOSS_WITH_FLOOR_PRESERVED; NO_FABRICATED_FILL_PRICE" : null,
    loss_bucket: bucket,
    loss_attribution: leg.credited ? (leg.source_lane || "FROZEN_V19_BASE") : `NEVER_PLACED:${leg.terminal_reason || "NO_ACTION"}`,
  };
}

function main() {
  for (const file of [run1, run2, baseEventPath, baseLegPath, baseFrontierPath]) ensure(fs.existsSync(file), `missing ${file}`);
  ensure(hashFile(run1) === hashFile(run2), `${variant} raw population builds differ`);
  const candidateEvents = readRows(run1);
  const candidateLegs = new Map(candidateEvents.flatMap((event) => Object.values(event.legs).map((leg) => [`${event.event_id}|${leg.leg_id}`, leg])));
  const baseEvents = readRows(baseEventPath);
  const baseLegs = readRows(baseLegPath);
  ensure(candidateEvents.length === 804 && baseEvents.length === 804 && baseLegs.length === 1608, "population conservation");
  const baseByEvent = new Map(baseEvents.map((event) => [event.event_id, event]));
  const finalLegs = baseLegs.map((base) => {
    const candidate = candidateLegs.get(base.leg_identity);
    ensure(candidate, `missing candidate ${base.leg_identity}`);
    return !base.acted && candidate.proposed_entry_cents !== null && repairReceipt(candidate)
      ? addCandidate(base, candidate)
      : { ...base, source_lane: base.source_lane || "FROZEN_V19_BASE", isolated_repair_added: false, isolated_repair_receipt: null };
  });
  const finalByKey = new Map(finalLegs.map((leg) => [leg.leg_identity, leg]));
  const finalEvents = candidateEvents.map((candidateEvent) => {
    const baseEvent = baseByEvent.get(candidateEvent.event_id);
    ensure(baseEvent, `missing base event ${candidateEvent.event_id}`);
    const legs = Object.fromEntries(Object.keys(candidateEvent.legs).sort().map((legId) => [legId, finalByKey.get(`${candidateEvent.event_id}|${legId}`)]));
    const xs = Object.values(legs), completed = xs.every((leg) => leg.credited), combined = completed ? xs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const bothBelow = completed && xs.every((leg) => Number.isInteger(leg.own_window1_close_cents) && leg.entry_cents < leg.own_window1_close_cents);
    const underPar = completed && combined < 100;
    return {
      event_id: candidateEvent.event_id,
      category: candidateEvent.category,
      starting_price_split: candidateEvent.starting_price_split,
      legs,
      completed_pair: completed,
      combined_entry_cents: combined,
      pair_under_par: underPar,
      both_legs_strictly_below_close: bothBelow,
      joint_objective_pass: underPar && bothBelow,
      execution_floor_pair_pass: underPar && xs.every((leg) => Number.isInteger(leg.qualifying_ask_floor_cents) && leg.entry_cents <= leg.qualifying_ask_floor_cents),
      take_ceiling_member: baseEvent.take_ceiling_member,
      maker_ceiling_member: baseEvent.maker_ceiling_member,
      isolated_repair_added_legs: xs.filter((leg) => leg.isolated_repair_added).map((leg) => leg.leg_id),
    };
  }).sort((a, b) => a.event_id.localeCompare(b.event_id));
  const baseMetrics = metrics(baseEvents.map((event) => ({ ...event, joint_objective_pass: event.pair_under_par && event.both_legs_strictly_below_close })));
  const currentMetrics = metrics(finalEvents);
  ensure(baseMetrics.D === 804 && baseMetrics.legs === 1608 && baseMetrics.joint_objective_pairs === 19, "frozen V19 floor identity mismatch");
  for (const key of ["acted_legs", "credited_legs", "completed_pairs", "pairs_under_par", "both_legs_strictly_below_close", "joint_objective_pairs", "execution_floor_pair_pass"]) ensure(currentMetrics[key] >= baseMetrics[key], `V19 floor regressed: ${key}`);
  const baseFrontier = frontier(baseEvents.map((event) => ({ ...event, joint_objective_pass: event.pair_under_par && event.both_legs_strictly_below_close })));
  const currentFrontier = frontier(finalEvents);
  for (const tier of ["LE_93", "LE_95", "LE_97", "LT_100", "ANY_PRICE"]) {
    ensure(currentFrontier[tier].completed_pairs >= baseFrontier[tier].completed_pairs, `${tier} completion regressed`);
    ensure(currentFrontier[tier].joint_objective_pairs >= baseFrontier[tier].joint_objective_pairs, `${tier} JOINT regressed`);
  }
  const partitionRows = [...group(finalEvents, (event) => `${event.category}|${event.starting_price_split}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], starting_price_region: key.split("|")[1], D: rows.length, metrics: metrics(rows), frontier: frontier(rows) }));
  const regrets = finalLegs.map(regretRow);
  const regretCells = [...group(regrets, (row) => `${row.category}|${row.price_region}|${row.loss_bucket}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], loss_bucket: key.split("|")[2], n: rows.length, regret_distribution: distribution(rows.map((row) => row.regret_cents)), loss_attribution: countBy(rows, (row) => row.loss_attribution), never_placed_full_regret_n: rows.filter((row) => row.never_placed_carries_full_regret).length }));
  const additions = finalLegs.filter((leg) => leg.isolated_repair_added);
  const receipt = {
    schema_version: `WINDOW1_${variant}_ISOLATED_CAUSAL_ADDITION_V20`,
    base: "FROZEN_PAIR_COUPLE_ABSTENTION_V19",
    stacking: false,
    repair: variant === "FIX_A" ? "REARM_OBSERVED_LOW_WITHIN_ONE_CENT_ON_FRESH_OWN_BOOK_RECEIPT; PLACE_AT_CURRENT_LIVE_ASK" : "REASK_UNANIMOUS_LOWER_AFTER_LATER_QUALIFIED_OWN_ASK_AT_OR_ABOVE_REFUSED_FLOOR_SETTLEMENT_RECEIPT",
    provenance: variant === "FIX_A" ? "ONE_CENT_STARTING_TOLERANCE_EXPLICITLY_AUTHORIZED_FROM_FROZEN_2026_08_03_HOLDOUT_GATE_LAG_DIAGNOSTIC" : "INHERITED_10_SECOND_DWELL_AND_EXACT_FIVE_CAPACITY; NO_NEW_NUMERIC_CONSTANT",
    added_legs: additions.length,
    added_leg_identities: additions.map((leg) => leg.leg_identity).sort(),
    source_receipts_complete: additions.every((leg) => leg.isolated_repair_receipt),
  };
  fs.mkdirSync(out, { recursive: true });
  fs.copyFileSync(run1, path.join(out, "RAW_ISOLATED_REPLAY_EVENT_LEDGER.jsonl.gz"));
  fs.writeFileSync(path.join(out, "POPULATION_EVENT_LEDGER.jsonl.gz"), gzipRows(finalEvents));
  fs.writeFileSync(path.join(out, "POPULATION_LEG_LEDGER.jsonl.gz"), gzipRows(finalLegs));
  fs.writeFileSync(path.join(out, "REGRET_LEG_LEDGER.jsonl.gz"), gzipRows(regrets));
  fs.writeFileSync(path.join(out, "FRONTIER.json"), canonical({ fixed_denominator: 804, JOINT_law: "PAIR_STRICTLY_UNDER_PAR_AND_BOTH_LEGS_STRICTLY_BELOW_OWN_W1_CLOSE", tiers: currentFrontier, category_and_starting_price_region: partitionRows.map((row) => ({ category: row.category, starting_price_region: row.starting_price_region, D: row.D, frontier: row.frontier })) }));
  fs.writeFileSync(path.join(out, "REGRET_GAUGE.json"), canonical({ law: "REGRET = CREDITED FILL - ACHIEVABLE PRINT-BACKED FLOOR", denominator_legs: 1608, numeric_completed_regret: distribution(regrets.map((row) => row.regret_cents)), never_placed_full_regret_n: regrets.filter((row) => row.never_placed_carries_full_regret).length, category_price_region_loss_buckets: regretCells }));
  fs.writeFileSync(path.join(out, "V19_NON_REGRESSION_COMPARISON.json"), canonical({ score_free: false, replay_scored: true, variant, V19: baseMetrics, isolated_variant: currentMetrics, delta: Object.fromEntries(Object.keys(baseMetrics).filter((key) => Number.isInteger(baseMetrics[key])).map((key) => [key, currentMetrics[key] - baseMetrics[key]])), V19_floor_pass: true, category_and_starting_price_region: partitionRows }));
  fs.writeFileSync(path.join(out, "CAUSAL_ADDITION_RECEIPT.json"), canonical(receipt));
  fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical({ population_builds: 2, run1_sha256: hashFile(run1), run2_sha256: hashFile(run2), byte_identical: true, isolated_overlay_deterministic: true }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, stacking: false }));
  const url = (name) => `${rawBase}/${artifactRel}/${name}`;
  fs.writeFileSync(path.join(out, "REPORT.md"), `# ${variant} isolated V20 replay\n\n- V19 non-regression and category x price-region partitions: ${url("V19_NON_REGRESSION_COMPARISON.json")}\n- FRONTIER and JOINT: ${url("FRONTIER.json")}\n- REGRET: ${url("REGRET_GAUGE.json")}\n- Exact causal additions: ${url("CAUSAL_ADDITION_RECEIPT.json")}\n- Raw isolated replay: ${url("RAW_ISOLATED_REPLAY_EVENT_LEDGER.jsonl.gz")}\n- Event ledger: ${url("POPULATION_EVENT_LEDGER.jsonl.gz")}\n- Leg ledger: ${url("POPULATION_LEG_LEDGER.jsonl.gz")}\n`);
  const sources = [
    [`${artifactRel}/RAW_ISOLATED_REPLAY_EVENT_LEDGER.jsonl.gz`, path.join(out, "RAW_ISOLATED_REPLAY_EVENT_LEDGER.jsonl.gz")],
    [rel(baseEventPath), baseEventPath],
    [rel(baseLegPath), baseLegPath],
    [rel(baseFrontierPath), baseFrontierPath],
    ["arb-executor/analysis/window1_isolated_repair_predicates_v20.js", path.join(repo, "arb-executor/analysis/window1_isolated_repair_predicates_v20.js")],
    ["arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js", path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js")],
    ["arb-executor/analysis/build_window1_dynamic_renarrow_population_v7.js", path.join(repo, "arb-executor/analysis/build_window1_dynamic_renarrow_population_v7.js")],
    ["arb-executor/analysis/build_window1_isolated_repair_v20_package.js", __filename],
  ];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sources.map(([name, file]) => [name, { sha256: hashFile(file), bytes: fs.statSync(file).size }])) }));
  const names = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", variant, metrics: currentMetrics, delta: Object.fromEntries(Object.keys(baseMetrics).filter((key) => Number.isInteger(baseMetrics[key])).map((key) => [key, currentMetrics[key] - baseMetrics[key]])), additions: additions.length }));
}

main();
