#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v45_guard_release_sibling_credit_20260809");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const control = read("CONTROL_BINDING.json"), score = read("ATTRIBUTION_SCORECARD.json"), releases = read("RELEASED_REST_RECEIPT.json"), named = read("NAMED_V45_RECEIPT.json"), bar = read("COMPOSITION_ACCEPTANCE_BAR.json"), status = read("CONSTRUCTION_STATUS.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), determinism = read("DETERMINISM_RECEIPT.json"), manifest = read("ARTIFACT_HASH_MANIFEST.json"), bindings = read("V45_RECEIPT_BINDINGS.json");

assert.equal(control.schema_version, "window1-v45-guard-release-sibling-credit-control-v1");
assert.equal(control.base, "01a58334e90acffd4bb0fb17b6ceed17c4f51bbd");
assert.equal(control.architecture.pre_fill_deep_gap_guard, "V43_T10_REMAINS_ACTIVE_UNCHANGED");
assert.equal(control.architecture.release_trigger, "OTHER_EXPRESSION_CREDITED");
assert.deepEqual(control.architecture.clocks_as_decision_inputs, []);
assert.deepEqual(score.order, ["V43_BASELINE", "V45_GUARD_RELEASE_AT_SIBLING_CREDIT"]);
assert.equal(score.frozen_V43_reproduction.pass, true);
assert.equal(releases.conservation.pass, true);
assert.equal(releases.released_rests, releases.released_and_filled + releases.released_unfilled);
assert.equal(releases.two_columns.new_exposure.events, 0);
assert.equal(named.assertions.no_new_exposure_from_post_credit_release, true);
assert.equal(bar.pass, bar.baseline_reproduction.pass && bar.completed_pairs.pass && bar.true_book_net_cents.pass && bar.naked_pnl_cents.pass && bar.named_checks.pass);
assert.equal(status.status, bar.pass ? "PASS_OPERATIVE" : "BLOCKED_V43_REMAINS_OPERATIVE");
assert.equal(bindings.scoped_law.includes("PRE_FILL_DEEP_GAP_GUARD_STAYS"), true);
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

process.stdout.write(`${JSON.stringify({ package: root, tests: 24, passed: 24 })}\n`);
