#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_fresh_holdout_seal_20260806");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

const remote = read("REMOTE_TAPE_CENSUS.json");
const audit = read("GIT_TOUCH_AUDIT.json");
const seal = read("SEALED_DECLARATION.json");
const gate = read("ONE_RUN_GATE_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.strictEqual(remote.event_count, 172);
assert.strictEqual(remote.leg_file_count, 344);
assert.strictEqual(remote.paired_event_count, 172);
assert.strictEqual(remote.floor_pass_admissible_event_count, 172);
assert.strictEqual(audit.candidate_events, 172);
assert.strictEqual(audit.excluded_touched + audit.sealed_untouched, 172);
assert.strictEqual(seal.sealed_N, audit.sealed_untouched);
assert.ok(seal.sealed_N < 60);
assert.strictEqual(seal.status, "STOPPED_N_LT_60_STAGE2_FORBIDDEN");
assert.strictEqual(gate.stage_2.status, "NOT_INVOKED_CONDITIONAL_AUTHORIZATION_UNSATISFIED");
assert.deepStrictEqual(gate.stage_2.brain_runner_invocations, { V36: 0, V35: 0, R3: 0, total: 0 });
assert.strictEqual(gate.stage_2.performance_fields, null);
assert.strictEqual(forbidden.scorer_invocations, 0);
assert.strictEqual(forbidden.result_rows, 0);
const list = fs.readFileSync(path.join(out, "SEALED_EVENT_LIST.txt"));
assert.strictEqual(sha(list), seal.event_list_sha256);
assert.strictEqual(list.toString("utf8").trim().split(/\r?\n/).filter(Boolean).length, seal.sealed_N);
for (const [name, receipt] of Object.entries(manifest.files)) {
  const bytes = fs.readFileSync(path.join(out, name));
  assert.strictEqual(bytes.length, receipt.bytes, `${name} bytes`);
  assert.strictEqual(sha(bytes), receipt.sha256, `${name} hash`);
}
console.log(JSON.stringify({ pass: true, tests: 23, sealed_N: seal.sealed_N, scorer_invocations: 0 }));
