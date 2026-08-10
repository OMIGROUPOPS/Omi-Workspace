#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v46_pair_gated_gap_credit_20260810");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const control = read("CONTROL_BINDING.json"), score = read("ATTRIBUTION_SCORECARD.json"), gap = read("GAP_CREDIT_RECEIPT.json"), named = read("NAMED_V46_RECEIPT.json"), bar = read("COMPOSITION_ACCEPTANCE_BAR.json"), status = read("CONSTRUCTION_STATUS.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), determinism = read("DETERMINISM_RECEIPT.json"), manifest = read("ARTIFACT_HASH_MANIFEST.json"), bindings = read("V46_RECEIPT_BINDINGS.json"), differential = read("V45_V46_DIFFERENTIAL_RECEIPT.json");

assert.equal(control.schema_version, "window1-v46-pair-gated-gap-credit-control-v1");
assert.equal(control.base, "3bda0a5476c7fc845891928795f709feff8caabf");
assert.equal(control.architecture.additional_credit_event, "SINGLE_RECEIPT_ASK_GAP_GE_3_CENTS");
assert.equal(control.architecture.authorization, "OTHER_EXPRESSION_ALREADY_CREDITED");
assert.deepEqual(control.architecture.clocks_as_decision_inputs, []);
assert.deepEqual(score.order, ["V45_BASELINE", "V46_PAIR_GATED_GAP_CREDIT"]);
assert.equal(score.frozen_V45_reproduction.pass, true);
assert.equal(gap.conservation.pass, true);
assert.equal(gap.two_columns.new_exposure.events, 0);
assert.equal(named.assertions.no_new_exposure_from_pair_gated_gap_credit, true);
assert.equal(bar.pass, bar.baseline_reproduction.pass && bar.completed_pairs.pass && bar.true_book_net_cents.pass && bar.zero_bound_regressions.pass && bar.named_checks.pass);
assert.equal(status.status, bar.pass ? "PASS_OPERATIVE" : "BLOCKED_V45_REMAINS_OPERATIVE");
assert.equal(bindings.footprint.frozen_legs, 50);
assert.equal(bindings.footprint.L6_misstamped_legs, 42);
assert.equal(bindings.footprint.naked_knife_legs, 11);
assert.equal(bindings.footprint.naked_knife_median_adverse_cents, 44);
assert.equal(differential.compared_leg_streams, 1608);
assert.equal(differential.conservation.pass, true);
assert.equal(forbidden.live_accesses, 0);
assert.equal(forbidden.network_runtime_accesses, 0);
assert.equal(determinism.clean_builds, 2);
assert.equal(determinism.byte_identical, true);
for (const [name, meta] of Object.entries(manifest.files)) {
  const file = path.join(root, name);
  assert(fs.existsSync(file), name);
  assert.equal(hash(file), meta.sha256, name);
  assert.equal(fs.statSync(file).size, meta.bytes, name);
}

process.stdout.write(`${JSON.stringify({ package: root, tests: 31, passed: 31 })}\n`);
