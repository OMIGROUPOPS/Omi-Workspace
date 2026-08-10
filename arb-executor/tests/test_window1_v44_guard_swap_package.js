#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v44_guard_swap_20260809");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const control = read("CONTROL_BINDING.json");
const score = read("ATTRIBUTION_SCORECARD.json");
const bindings = read("GUARD_SWAP_BINDINGS.json");
const dry = read("DRY_SIBLING_WITHHOLD_RECEIPT.json");
const named = read("NAMED_V44_RECEIPT.json");
const bar = read("COMPOSITION_ACCEPTANCE_BAR.json");
const status = read("CONSTRUCTION_STATUS.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.equal(control.schema_version, "window1-v44-guard-swap-control-v1");
assert.equal(control.parent, "01a58334e90acffd4bb0fb17b6ceed17c4f51bbd");
assert.equal(control.architecture.clocks_as_decision_inputs.length, 0);
assert.equal(control.architecture.take_path, "DELETED_IN_V41");
assert.deepEqual(score.order, ["V43_BASELINE", "GUARD_REMOVED_ONLY", "DRY_SIBLING_ONLY", "V44_GUARD_SWAP"]);
assert.equal(score.rows.length, 4);
assert.equal(score.V43_baseline_reproduction.pass, true);
assert.equal(score.rows[0].MARKET_UNION_REACH.completed_pairs, 395);
assert.equal(score.rows[0].FULL_BOOK.true_book_net_cents, 1748);
assert.equal(bindings.removed_guard.status, "COMPOSITION_STALE_REMOVED_FROM_V44_COMBINED");
assert.equal(bindings.recalibration.role, "ANALYTICAL_ESTIMATE_NOT_EXECUTABLE_SCORE");
assert.equal(dry.threshold_cents, 3);
assert.equal(dry.analytical_estimate.controlling, false);
assert.equal(bar.pass, bar.baseline_reproduction.pass && bar.completed_pairs.pass && bar.naked_pnl_cents.pass && bar.true_book_net_cents.pass && bar.deep_gap_guard_removed.pass && bar.named_checks.pass);
assert.equal(status.status, bar.pass ? "PASS_OPERATIVE" : "BLOCKED_NOT_OPERATIVE");
assert.equal(Object.keys(named.assertions).length, 7);
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
