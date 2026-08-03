#!/usr/bin/env node
"use strict";

const assert = require("assert"), crypto = require("crypto"), fs = require("fs"), path = require("path"), zlib = require("zlib");
const repo = path.resolve(__dirname, "../..");
const fitPath = path.join(repo, ".claude/window1_live_v4_replay/pair_interim_shape_v18_fit_20260803/INTERIM_PAIR_LIBRARY_V18.json");
const out = path.join(repo, ".claude/window1_live_v4_replay/pair_interim_elimination_v18_20260803");
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const rows = (file) => zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);

assert.ok(fs.existsSync(fitPath));
const fit = JSON.parse(fs.readFileSync(fitPath));
assert.strictEqual(fit.census.denominator_available_single_leg_hypothesis_members, 1343);
assert.strictEqual(fit.fit_contract.price_region_cells, false);
assert.strictEqual(fit.fit_contract.endpoint_labels, false);
assert.match(fit.fit_contract.membership_fit, /SYNCHRONIZED INTERIM TRAJECTORIES/);
for (const group of Object.values(fit.pair_hypothesis_groups)) {
  assert.deepStrictEqual(group.lookup_dimensions, ["category"]);
  assert.strictEqual(group.price_region_or_cell_used, false);
  assert.strictEqual(group.trajectory_only_fit.outcome_or_ordinal_used_in_membership, false);
  for (const hypothesis of group.hypotheses) if (hypothesis.usable_for_signing) {
    assert.ok(hypothesis.n >= 20);
    assert.ok(hypothesis.coherence.high_leg_support_width <= 1);
    assert.ok(hypothesis.coherence.low_leg_support_width <= 1);
  }
}

if (fs.existsSync(out)) {
  const comparison = JSON.parse(fs.readFileSync(path.join(out, "V11_COMPARISON.json")));
  assert.strictEqual(comparison.V11.acted_legs, 712);
  assert.strictEqual(comparison.V11.completed_pairs, 185);
  assert.strictEqual(comparison.V11.pairs_under_par, 94);
  assert.strictEqual(comparison.V11.both_legs_strictly_below_close, 21);
  assert.strictEqual(comparison.V11.execution_floor_pair_pass, 29);
  assert.strictEqual(comparison.V11.strict_carried_pairs, 52);
  const trace = rows(path.join(out, "V11_896_NON_ACTION_PAIR_RESOLUTION_TRACE.jsonl.gz"));
  assert.strictEqual(trace.length, 896);
  const manifest = JSON.parse(fs.readFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json")));
  for (const [name, receipt] of Object.entries(manifest.files)) assert.strictEqual(hash(path.join(out, name)), receipt.sha256);
}
console.log("test_window1_pair_interim_v18_package: PASS");
