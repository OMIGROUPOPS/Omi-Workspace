#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const repo = path.resolve(__dirname, "../..");
const temp = fs.mkdtempSync(path.join(os.tmpdir(), "w1-initial-aim-audit-"));
const temp2 = fs.mkdtempSync(path.join(os.tmpdir(), "w1-initial-aim-audit-"));
try {
  const run = spawnSync("node", [
    path.join(repo, "arb-executor/analysis/build_window1_initial_aim_constant_audit.js"),
    "--repo", repo,
    "--output", temp,
  ], { encoding: "utf8" });
  assert.strictEqual(run.status, 0, run.stderr);
  const run2 = spawnSync("node", [
    path.join(repo, "arb-executor/analysis/build_window1_initial_aim_constant_audit.js"),
    "--repo", repo,
    "--output", temp2,
  ], { encoding: "utf8" });
  assert.strictEqual(run2.status, 0, run2.stderr);
  const names1 = fs.readdirSync(temp).sort();
  const names2 = fs.readdirSync(temp2).sort();
  assert.deepStrictEqual(names1, names2);
  for (const name of names1) {
    assert.deepStrictEqual(fs.readFileSync(path.join(temp, name)), fs.readFileSync(path.join(temp2, name)), `non-deterministic ${name}`);
  }

  const atlas = JSON.parse(fs.readFileSync(path.join(temp, "ATLAS_P75_CATEGORY_PRICE_DISTRIBUTIONS.json"), "utf8"));
  assert.strictEqual(atlas.conservation.population_events, 804);
  assert.strictEqual(atlas.conservation.population_legs, 1608);
  assert.strictEqual(atlas.conservation.comparable_rows, 1338);
  assert.strictEqual(atlas.conservation.predicted_too_shallow_negative, 19);
  assert.strictEqual(atlas.conservation.exact_zero, 12);
  assert.strictEqual(atlas.conservation.predicted_too_deep_positive, 1307);
  assert.strictEqual(atlas.nik_control.reconstructed_anchor_cents, 33);
  assert.strictEqual(atlas.nik_control.ask_10s_reachable_low_cents, 18);
  assert.strictEqual(atlas.nik_control.actual_travel_cents, 15);
  assert.strictEqual(atlas.nik_control.signed_error_cents, -8);

  const chase = JSON.parse(fs.readFileSync(path.join(temp, "CHASE_AND_FILLABLE_LOW_CENSUS.json"), "utf8"));
  assert.strictEqual(chase.conservation.legacy_fill_assignments, 217);
  assert.strictEqual(chase.conservation.legacy_fill_assignments_credited_under_current_capacity_law, 0);
  assert.strictEqual(chase.conservation.proven_net_down_placement_paths_lower_bound, 44);
  assert.strictEqual(chase.conservation.net_down_distinct_events_lower_bound, 41);
  assert.strictEqual(chase.conservation.ask_10s_low_comparable_legacy_fills, 101);
  assert.strictEqual(chase.conservation.above_reachable_low, 41);
  assert.strictEqual(chase.conservation.at_reachable_low, 24);
  assert.strictEqual(chase.conservation.below_ask_only_low_via_other_evidence, 36);
  assert.strictEqual(chase.conservation.exact_downward_cancel_repost_transition_count, null);

  const nik = JSON.parse(fs.readFileSync(path.join(temp, "NIK_ANCHOR_PROVENANCE_RECEIPT.json"), "utf8"));
  assert.deepStrictEqual(nik.decisions.map((row) => row.anchor.side), ["OFFER_LIFT", "NOT_A_PRINT", "BID_HIT"]);
  assert.deepStrictEqual(nik.decisions.map((row) => row.arithmetic), ["33 - 7 = 26", "30 - 7 = 23", "28 - 7 = 21"]);

  const spec = JSON.parse(fs.readFileSync(path.join(temp, "INITIAL_AIM_REPLACEMENT_SPEC.json"), "utf8"));
  assert.strictEqual(spec.status, "SPEC_ONLY_NOT_IMPLEMENTED_NOT_REPLAYED_NOT_VALIDATED");
  assert.deepStrictEqual(spec.nik_counterfactual_at_requested_calls.map((row) => row.replacement_action), [
    "PLACE 23 from min(23,33-1)",
    "HOLD 23; bid/mid change cannot re-anchor",
    "HOLD 23; bid/last change cannot re-anchor and ask 27 remains above X",
  ]);
  assert.ok(spec.unvalidated.some((item) => item.includes("recurrence>0")));

  const report = fs.readFileSync(path.join(temp, "REPORT.md"), "utf8");
  assert.ok(report.includes("ATLAS_PRE_DATES_HONEST_CLOCK_MIGRATION") || report.includes("pre-migration"));
  assert.ok(report.includes("raw.githubusercontent.com"));
  assert.ok(report.includes("not recoverable"));
  assert.ok(report.includes("SPEC_ONLY") || report.includes("specification"));

  console.log(`PASS test_window1_initial_aim_constant_audit: two builds, ${names1.length} files byte-identical, 25 semantic assertions`);
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
  fs.rmSync(temp2, { recursive: true, force: true });
}
