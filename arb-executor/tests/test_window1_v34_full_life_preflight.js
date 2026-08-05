#!/usr/bin/env node
"use strict";

const assert = require("assert");
const cp = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const BUILDER = path.join(ROOT, "arb-executor", "analysis", "build_window1_v34_full_life_preflight.js");

function files(dir) {
  return fs.readdirSync(dir).sort().map((name) => [name, fs.readFileSync(path.join(dir, name))]);
}

const root = fs.mkdtempSync(path.join(os.tmpdir(), "v34-preflight-"));
const a = path.join(root, "a");
const b = path.join(root, "b");
cp.execFileSync(process.execPath, [BUILDER, "--out", a], { cwd: ROOT, stdio: "inherit" });
cp.execFileSync(process.execPath, [BUILDER, "--out", b], { cwd: ROOT, stdio: "inherit" });

const af = files(a);
const bf = files(b);
assert.deepStrictEqual(af.map(([n]) => n), bf.map(([n]) => n));
for (let i = 0; i < af.length; i += 1) assert.ok(af[i][1].equals(bf[i][1]), af[i][0]);

const coverage = JSON.parse(fs.readFileSync(path.join(a, "ACTUAL_BELL_COVERAGE_RECEIPT.json"), "utf8"));
const blocked = JSON.parse(fs.readFileSync(path.join(a, "CONSTRUCTION_BLOCK_RECEIPT.json"), "utf8"));
const forbidden = JSON.parse(fs.readFileSync(path.join(a, "FORBIDDEN_ACCESS_RECEIPT.json"), "utf8"));
assert.strictEqual(coverage.population_events, 804);
assert.strictEqual(coverage.exact_actual_bell_events, 234);
assert.strictEqual(coverage.events_without_exact_actual_bell, 570);
assert.strictEqual(blocked.status, "BLOCKED_BEFORE_VARIANT_CONSTRUCTION");
assert.strictEqual(blocked.effects.V34_policy_code_created, false);
assert.strictEqual(blocked.effects.replay_executed, false);
assert.strictEqual(forbidden.accesses.scorer_invocations, 0);
assert.strictEqual(forbidden.accesses.replay_invocations, 0);
assert.strictEqual(forbidden.accesses.live, 0);
assert.strictEqual(forbidden.accesses.holdout, 0);

fs.rmSync(root, { recursive: true, force: true });
console.log("PASS test_window1_v34_full_life_preflight (2 byte-identical builds; fail-closed coverage gate)");
