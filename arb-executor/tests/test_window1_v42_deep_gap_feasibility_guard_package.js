#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v42_deep_gap_feasibility_guard_20260809");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
const market = read("MARKET_GRADE_SCORECARD.json");
const strict = read("STRICT_BUILD_VERIFICATION_SCORECARD.json");
const guard = read("DEEP_GAP_GUARD_RECEIPT.json");
const diff = read("DEEP_GAP_DIFFERENTIAL_RECEIPT.json");
const pnl = read("FULL_BOOK_PNL.json");
const acceptance = read("ACCEPTANCE_BAR.json");
const named = read("NAMED_V42_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.equal(control.schema_version, "window1-v42-deep-gap-feasibility-guard-control-v1");
assert.equal(control.parent, "96d33316b0c0020b46b71569fcdbadeaa97a64e3");
assert.equal(control.architecture.tolerance_cents, 10);
assert.equal(control.architecture.clocks_as_decision_inputs.length, 0);
assert.equal(market.score.D, 804);
assert.equal(strict.score.D, 804);
assert.equal(pnl.V41_reconstructed.completed_pairs, 243);
assert.equal(pnl.V41_reconstructed.completed_locked_cents, 732);
assert.equal(pnl.V41_reconstructed.true_book_net_cents, 782);
assert.equal(pnl.acceptance.pass, true);
assert.equal(acceptance.pass, true);
assert.equal(guard.controlling_census.T10.derived_net_cents, 73);
assert.equal(guard.tolerance_cents, 10);
assert.equal(diff.compared_leg_streams, 1608);
assert.equal(diff.conservation.pass, true);
assert.equal(named.assertions.PUTJEA_fingerprint_pass, true);
assert.equal(named.assertions.ROCBUE_touched, true);
assert.equal(named.assertions.KREZHE_touched, true);
assert.equal(named.assertions.BORDIM_DIM_not_withheld, true);
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

process.stdout.write(`${JSON.stringify({ package: root, tests: 32, passed: 32 })}\n`);
