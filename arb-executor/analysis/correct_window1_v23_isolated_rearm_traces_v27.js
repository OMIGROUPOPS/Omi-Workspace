#!/usr/bin/env node
"use strict";

// Fast, deterministic trace-normalization stage.  It consumes only the two
// already-built payloads and the frozen V23 trace; it never opens a tape.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const argv = process.argv.slice(2);
const at = (n, d) => { const i = argv.indexOf(n); return i < 0 ? d : argv[i + 1]; };
const repo = path.resolve(at("--repo", "."));
const root = path.resolve(at("--root", ""));
const baselineTracePath = path.join(repo, ".claude/window1_live_v4_replay/decision_trace_v23_20260804/DECISION_TRACE_1608.json");
const builderPath = path.join(repo, "arb-executor/analysis/build_window1_v23_isolated_rearms_v27.js");
const correctorPath = __filename;
const policyTestPath = path.join(repo, "arb-executor/tests/test_window1_v23_isolated_rearm_policies_v27.js");
const packageTestPath = path.join(repo, "arb-executor/tests/test_window1_v23_isolated_rearms_v27_package.js");
const variants = ["fix1_anchor_residual", "fix2_cap_rearm", "fix3_verdict_falsifiability", "fix4_admission_reask"];
const layers = ["ADMISSION", "BOOK", "IDENTITY", "FLOOR", "VERDICT", "ANCHOR", "SIBLING_PAIR", "PLACEMENT_CAP", "FILL", "COMPLETION"];
const canonical = (x) => `${JSON.stringify(x, null, 2)}\n`;
const sha = (x) => crypto.createHash("sha256").update(x).digest("hex");
const readRows = (p) => zlib.gunzipSync(fs.readFileSync(p)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
function group(rows, fn) { const m = new Map(); for (const row of rows) { const k = fn(row); if (!m.has(k)) m.set(k, []); m.get(k).push(row); } return m; }
function countBy(rows, fn) { const o = {}; for (const row of rows) { const k = String(fn(row)); o[k] = (o[k] || 0) + 1; } return Object.fromEntries(Object.entries(o).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function layerRows(first) { return layers.map((layer, i) => { if (!first) return { order: i + 1, layer, result: "PASS" }; const j = layers.indexOf(first.layer); return i < j ? { order: i + 1, layer, result: "PASS" } : i === j ? { order: i + 1, layer, result: "FLAG", predicate: first.predicate } : { order: i + 1, layer, result: "FLAG", predicate: "NOT_REACHED_AFTER_UPSTREAM_FLAG", upstream_layer: first.layer }; }); }
function rollup(rows) { return [...group(rows.filter((x) => x.first_flag), (x) => x.first_flag.layer)].sort(([a], [b]) => a.localeCompare(b)).map(([layer, xs]) => ({ layer, stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) })); }

const baseline = JSON.parse(fs.readFileSync(baselineTracePath));
const baseByLeg = new Map(baseline.rows.map((x) => [x.leg_identity, x]));
const controlPath = path.join(root, "CONTROL_SUMMARY.json");
const control = JSON.parse(fs.readFileSync(controlPath));
for (const slug of variants) {
  const dir = path.join(root, slug), events = readRows(path.join(dir, "EVENT_LEDGER.jsonl.gz"));
  const byLeg = new Map(events.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, { leg, event }])));
  const tracePath = path.join(dir, "DECISION_TRACE_1608.json"), trace = JSON.parse(fs.readFileSync(tracePath));
  const changedEvents = new Set(trace.rows.filter((row) => row.repair_effect).map((row) => row.event_id));
  for (const row of trace.rows) {
    const base = baseByLeg.get(row.leg_identity), { leg, event } = byLeg.get(row.leg_identity), outcome = row.repair_effect;
    let first = null, tape = row.tape_offered_afterward;
    if (!outcome && !changedEvents.has(row.event_id)) { first = base.first_flag; tape = base.tape_offered_afterward; }
    else if (leg.credited && event.completed_pair && event.combined_entry_cents < 100) { first = null; tape = row.tape_offered_afterward; }
    else if (leg.credited && event.completed_pair && event.combined_entry_cents >= 100) {
      first = row.first_flag?.source_layer?.startsWith("V27_") ? row.first_flag : { ...(base.first_flag || row.first_flag), layer: "COMPLETION", source_layer: `V27_${trace.variant}`, predicate: "COMPLETED_PAIR_NOT_STRICTLY_UNDER_PAR", values_compared: { combined_entry_cents: event.combined_entry_cents } };
      tape = { evaluated_ticker: row.ticker, best_qualifying_ask_floor_cents_after_flag: null, own_audited_close_cents: leg.audited_close_cents, negative_delta_available_past_flag: "NO", floor_status: "PAIR_ALREADY_COMPLETED_AT_OR_ABOVE_PAR" };
    } else if (outcome) { first = row.first_flag; }
    else { first = base.first_flag; tape = base.tape_offered_afterward; }
    row.first_flag = first;
    row.layer_results_in_execution_order = layerRows(first);
    row.tape_offered_afterward = tape;
  }
  trace.rollup.layer_totals = rollup(trace.rows);
  trace.rollup.layer_x_category = [...group(trace.rows.filter((x) => x.first_flag), (x) => `${x.first_flag.layer}|${x.category}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ layer: key.split("|")[0], category: key.split("|")[1], stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) }));
  fs.writeFileSync(tracePath, canonical(trace));
  const key = Object.keys(control.variants).find((name) => control.variants[name].directory === slug);
  control.variants[key].first_flag_totals = trace.rollup.layer_totals;
  const base = control.baseline.score, current = control.variants[key].score;
  const fullFloor = ["completed_pairs", "pairs_under_par", "both_legs_strictly_below_audited_close", "joint_objective_pairs", "execution_floor_pair_passes"].every((name) => current[name] >= base[name]);
  Object.assign(control.variants[key], { V23_multimetric_floor_nonregression: fullFloor, stacking_eligible: false, stacking_requires_separate_operator_ratification: true });
  const scorePath = path.join(dir, "SCORECARD.json"), score = JSON.parse(fs.readFileSync(scorePath)); Object.assign(score, { V23_multimetric_floor_nonregression: fullFloor, stacking_eligible: false, stacking_requires_separate_operator_ratification: true }); fs.writeFileSync(scorePath, canonical(score));
  const repairPath = path.join(dir, "REPAIR_RECEIPT.json"), repair = JSON.parse(fs.readFileSync(repairPath)); Object.assign(repair, { V23_multimetric_floor_nonregression: fullFloor, stacking_requires_separate_operator_ratification: true }); fs.writeFileSync(repairPath, canonical(repair));
}
fs.writeFileSync(controlPath, canonical(control));
const sourcePath = path.join(root, "SOURCE_HASH_MANIFEST.json"), source = JSON.parse(fs.readFileSync(sourcePath));
source.committed["arb-executor/analysis/build_window1_v23_isolated_rearms_v27.js"] = { sha256: sha(fs.readFileSync(builderPath)), bytes: fs.statSync(builderPath).size };
source.committed["arb-executor/analysis/correct_window1_v23_isolated_rearm_traces_v27.js"] = { sha256: sha(fs.readFileSync(correctorPath)), bytes: fs.statSync(correctorPath).size };
source.committed["arb-executor/tests/test_window1_v23_isolated_rearm_policies_v27.js"] = { sha256: sha(fs.readFileSync(policyTestPath)), bytes: fs.statSync(policyTestPath).size };
source.committed["arb-executor/tests/test_window1_v23_isolated_rearms_v27_package.js"] = { sha256: sha(fs.readFileSync(packageTestPath)), bytes: fs.statSync(packageTestPath).size };
fs.writeFileSync(sourcePath, canonical(source));
process.stdout.write(canonical({ status: "TRACE_NORMALIZED", root, variants: variants.length }));
