#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_simultaneous_proxy_patch_20260804");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));

assert.ok(fs.existsSync(dir), "simultaneous patch package missing");
const patch = read("SIMULTANEOUS_OWN_AIM_PROXY_PATCH_RECEIPT.json");
assert.strictEqual(patch.scope, "EXACTLY_11_SAME-SECOND_A_PLACEMENT_EVENTS");
assert.strictEqual(patch.events.length, 11);
assert.strictEqual(patch.proxy_is_fill, false);
assert.strictEqual(patch.same_receipt_fill_forbidden, true);
assert.ok(patch.events.every((x) => x.first_leg_basis_type === "SIMULTANEOUS_LEXICALLY_FIRST_LEG_OWN_AIM_PRICE_PROXY_NOT_A_FILL"));

const comparison = read("V23_VS_A.json");
assert.strictEqual(comparison.simultaneous_own_aim_proxy_armed, 11);
assert.strictEqual(comparison.simultaneous_not_armed, 0);
assert.strictEqual(comparison.V23_PAIR_CAP_IMMEDIATE.D, 804);
assert.strictEqual(comparison.V23_PAIR_CAP_IMMEDIATE.completed_pairs, 194);
assert.strictEqual(comparison.V23_PAIR_CAP_IMMEDIATE.pairs_under_par, 194);
assert.strictEqual(comparison.V23_PAIR_CAP_IMMEDIATE.joint_objective_pairs, 45);
assert.strictEqual(comparison.V23_PAIR_CAP_IMMEDIATE.strict_carried_pairs, 83);

const control = read("CONTROL_BINDING.json");
assert.strictEqual(control.simultaneous_own_aim_proxy_patch, true);
assert.ok(control.simultaneous_patch_law.includes("NON-FILL PROXY"));

console.log("PASS test_window1_pair_cap_v23_simultaneous_patch");
