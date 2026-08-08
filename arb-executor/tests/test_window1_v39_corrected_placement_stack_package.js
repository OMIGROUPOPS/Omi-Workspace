#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v39_corrected_placement_stack_20260807");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json"), market = read("MARKET_GRADE_SCORECARD.json"), strict = read("STRICT_BUILD_VERIFICATION_SCORECARD.json"), telemetry = read("CAUSAL_DIRECTION_CLASSIFIER_TELEMETRY.json"), sanity = read("REST_SANITY.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), determinism = read("DETERMINISM_RECEIPT.json"), manifest = read("ARTIFACT_HASH_MANIFEST.json"), named = read("NAMED_GAMES.json"), recovery = read("MISLABEL_RECOVERY_RECEIPT.json");

assert.equal(control.schema_version, "window1-v39-corrected-placement-stack-control-v1");
assert.equal(control.base, "bfde0d8d1135f5c5f48a5f3d619ab30050efab83");
assert.equal(control.architecture.take_path, "V36_MATURE_FLOOR_TAKE_INTACT");
assert.equal(market.score.D, 804); assert.equal(market.score.legs, 1608);
assert.equal(strict.score.D, 804); assert.equal(strict.score.legs, 1608);
assert.equal(market.reach_grade.answer_key_games, 637); assert.equal(market.reach_grade.answer_key_locked_cents, 5253);
assert.equal(sanity.post_decision_rest_at_or_above_ask_violations, 0);
assert.equal(telemetry.telemetry_only_ex_post_direction_not_consumed_by_policy, true);
assert.equal(recovery.controlling_counterfactual_denominator, 115);
assert.match(recovery.identity_binding_status, /NOT_BOUND/);
assert.equal(forbidden.holdout_accesses, 0); assert.equal(forbidden.live_accesses, 0); assert.equal(forbidden.network_runtime_accesses, 0);
assert.equal(determinism.byte_identical, true); assert.equal(determinism.clean_builds, 2);
for (const label of ["ARNROM", "BOSCOP", "WESPAA", "NIKVRB", "GANJAN"]) assert(named.games[label]);
for (const [name, meta] of Object.entries(manifest.files)) { const file = path.join(root, name); assert(fs.existsSync(file), name); assert.equal(hash(file), meta.sha256, name); assert.equal(fs.statSync(file).size, meta.bytes, name); }

process.stdout.write(`${JSON.stringify({ package: root, tests: 22, passed: 22 }, null, 2)}\n`);
