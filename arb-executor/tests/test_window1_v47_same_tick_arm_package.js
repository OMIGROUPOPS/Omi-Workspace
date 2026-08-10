"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const root = path.resolve(__dirname, "../..");
const pkg = path.join(root, ".claude/window1_live_v4_replay/v47_same_tick_arm_20260810");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(pkg, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const status = read("CONSTRUCTION_STATUS.json");
assert.equal(status.status, "PASS_OPERATIVE");
assert.equal(status.gains_required, false);

const score = read("ATTRIBUTION_SCORECARD.json");
assert.equal(score.frozen_V45_reproduction.pass, true);
assert.deepEqual(score.delta_V47_minus_V45, { completed_pairs: 0, locked_cents: 0, true_book_net_cents: 0 });

const receipt = read("SEG_C_SAME_TICK_RECEIPT.json");
assert.equal(receipt.V47_positive_scheduler_latency_rows, 0);
assert.equal(receipt.outcome_changed_rows, 0);
assert.equal(receipt.conservation.pass, true);
assert.ok(receipt.SURECH.length > 0);
assert.ok(receipt.SURECH.every((row) => row.V47.positive_scheduler_latency_rows === 0));

const ledger = rows("SEG_C_SAME_TICK_FOOTPRINT.jsonl.gz");
assert.equal(ledger.length, receipt.deep_join_legs);
assert.equal(ledger.reduce((sum, row) => sum + row.qualification_rows, 0), receipt.qualification_rows);

const diff = read("V45_V47_DIFFERENTIAL_RECEIPT.json");
assert.equal(diff.compared_leg_streams, 1608);
assert.equal(diff.changed_leg_streams, 0);
assert.equal(diff.unchanged_leg_streams, 1608);
assert.equal(diff.conservation.pass, true);

const named = read("NAMED_V47_RECEIPT.json");
assert.equal(named.pass, true);
assert.equal(named.assertions.SURECH_causal_reach_null_remains_unfilled, true);

const manifest = read("ARTIFACT_HASH_MANIFEST.json");
for (const [name, meta] of Object.entries(manifest.files)) {
  const file = path.join(pkg, name);
  assert.ok(fs.existsSync(file), `missing ${name}`);
  assert.equal(sha(file), meta.sha256, `hash ${name}`);
  assert.equal(fs.statSync(file).size, meta.bytes, `bytes ${name}`);
}

console.log("PASS test_window1_v47_same_tick_arm_package");
