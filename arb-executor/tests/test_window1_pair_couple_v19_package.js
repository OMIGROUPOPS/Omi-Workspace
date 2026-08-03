#!/usr/bin/env node
"use strict";

const assert = require("assert"), crypto = require("crypto"), fs = require("fs"), path = require("path");
const repo = path.resolve(__dirname, "../.."), root = path.join(repo, ".claude/window1_live_v4_replay/pair_couple_abstention_v19_20260803");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
for (const name of ["PAIR_COUPLE_LIBRARY_V19.json","PAIR_COUPLE_CENSUS.json","V11_COMPARISON.json","FRONTIER.json","REGRET_GAUGE.json","NON_ACTION_RESOLUTION_CENSUS.json","DETERMINISM_RECEIPT.json","FORBIDDEN_ACCESS_RECEIPT.json","ARTIFACT_HASH_MANIFEST.json"]) assert(fs.existsSync(path.join(root, name)), name);
const census = read("PAIR_COUPLE_CENSUS.json"), comparison = read("V11_COMPARISON.json"), trace = read("NON_ACTION_RESOLUTION_CENSUS.json"), regret = read("REGRET_GAUGE.json"), manifest = read("ARTIFACT_HASH_MANIFEST.json");
assert.strictEqual(census.architecture.minimum_n, 30); assert.strictEqual(comparison.V11.acted_legs, 712);
assert(comparison.V19.acted_legs >= 712); assert(comparison.V19.completed_pairs >= 185); assert(comparison.V19.pairs_under_par >= 94); assert(comparison.V19.both_legs_strictly_below_close >= 21);
assert.strictEqual(trace.denominator, 896); assert.strictEqual(trace.former_V18_joint_macro_veto_count, 0);
assert.strictEqual(regret.denominator_legs, 1608); assert.strictEqual(regret.numeric_completed_regret.denominator, 1608);
for (const [name, item] of Object.entries(manifest.files)) { const bytes = fs.readFileSync(path.join(root, name)); assert.strictEqual(bytes.length, item.bytes, name); assert.strictEqual(crypto.createHash("sha256").update(bytes).digest("hex"), item.sha256, name); }
console.log("test_window1_pair_couple_v19_package: PASS");
