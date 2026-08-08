#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v41_maker_machine_20260808");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
const market = read("MARKET_GRADE_SCORECARD.json");
const strict = read("STRICT_BUILD_VERIFICATION_SCORECARD.json");
const deletion = read("TAKE_PATH_DELETION_RECEIPT.json");
const persistence = read("PERSISTENCE_ONLY_JOIN_RECEIPT.json");
const causal = read("CAUSAL_REACH_BINDING.json");
const comparison = read("V36_COMPARISON.json");
const named = read("NAMED_V41_RECEIPT.json");
const sanity = read("REST_SANITY.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.equal(control.schema_version, "window1-v41-maker-machine-control-v1");
assert.equal(control.base, "bfde0d8d1135f5c5f48a5f3d619ab30050efab83");
assert.equal(control.architecture.take_path, "DELETED_NOT_GATED");
assert.equal(control.architecture.clocks_as_decision_inputs.length, 0);
assert.equal(deletion.forbidden_action_literal_TAKE_count, 0);
assert.equal(deletion.take_named_function_count, 0);
assert.equal(deletion.market_taker_fills, 0);
assert.equal(deletion.strict_taker_fills, 0);
assert.equal(deletion.maker_fees_cents, 0);
assert.equal(persistence.seller_hit_gate_removed, true);
assert.equal(persistence.join_overrides_tracker, true);
assert.equal(causal.CAUSAL_REACH.under_par, 504);
assert.equal(causal.CAUSAL_REACH.locked, 3319);
assert.equal(market.score.D, 804);
assert.equal(strict.score.D, 804);
assert.equal(comparison.frozen_net_of_taker_fee_score.aggregate.taker_legs_charged, 882);
assert.equal(comparison.V41_maker_fee.total_entry_fees_cents, 0);
assert(named.ARNROM && named.BOSCOP && named.NIKVRB && named.WESPAA && named.KRUFER);
assert.equal(named.ARNROM.no_fabricated_target_credit, true);
assert.equal(sanity.post_decision_rest_at_or_above_ask_violations, 0);
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
