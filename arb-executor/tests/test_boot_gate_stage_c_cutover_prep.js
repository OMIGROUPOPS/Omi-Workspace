"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const pkg = path.join(repo, ".claude/boot_gate_stage_c_v36_cutover_prep_20260807");
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const drift = readJson("DRIFT_DISPOSITION.json");
assert.equal(drift.hunks.length, 31);
assert.equal(drift.hunks.filter((row) => row.disposition === "RETIRE").length, 31);
assert.equal(drift.summary.KEEP, 0);
assert.equal(drift.summary.unclassified, 0);

const identity = readJson("POLICY_BYTE_IDENTITY.json");
assert.equal(identity.files.length, 5);
for (const row of identity.files) assert.equal(sha(path.join(repo, row.path)), row.sha256);

const sources = readJson("SOURCE_HASH_MANIFEST.json");
for (const row of sources.files) {
  const file = path.join(repo, row.path);
  assert.equal(fs.statSync(file).size, row.bytes, row.path);
  assert.equal(sha(file), row.sha256, row.path);
}

const artifacts = readJson("ARTIFACT_HASH_MANIFEST.json");
for (const row of artifacts.files) {
  const file = path.join(pkg, row.path);
  assert.equal(fs.statSync(file).size, row.bytes, row.path);
  assert.equal(sha(file), row.sha256, row.path);
}

const shadow = fs.readFileSync(path.join(repo, "arb-executor/v36_shadow_brain.py"), "utf8");
for (const token of ["api_post", "api_delete", "place_order", "cancel_order"])
  assert(!shadow.includes(token), token);
const live = fs.readFileSync(path.join(repo, "arb-executor/live_v4.py"), "utf8");
assert(live.includes("V36ShadowBrain(self._log)"));
assert(!live.includes('return (15, "exit")'));

const ready = readJson("RUNTIME_READINESS_RECEIPT.json");
assert.equal(ready.stage_c_prep_verdict, "PREPARED_SOURCE_ONLY_ENGINE_PARKED");
assert.equal(ready.launch_verdict, "NO_GO");
const forbidden = readJson("FORBIDDEN_ACCESS_RECEIPT.json");
assert.equal(forbidden.engine_starts, 0);
assert.equal(forbidden.order_mutations, 0);
assert.equal(forbidden.position_mutations, 0);

console.log("boot gate Stage-C package tests: PASS (31 drift hunks, 5 frozen policies, manifests, NO-GO launch fence)");
