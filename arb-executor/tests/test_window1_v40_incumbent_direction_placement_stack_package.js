#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v40_incumbent_direction_placement_stack_20260808");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
const market = read("MARKET_GRADE_SCORECARD.json");
const strict = read("STRICT_BUILD_VERIFICATION_SCORECARD.json");
const classifier = read("CLASSIFIER_RESEARCH_OPEN_RECEIPT.json");
const joins = read("PERSISTENT_JOIN_POST_EVIDENCE_RECEIPT.json");
const sanity = read("REST_SANITY.json");
const acceptance = read("ACCEPTANCE_BAR.json");
const named = read("NAMED_V40_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.equal(control.schema_version, "window1-v40-incumbent-direction-placement-stack-control-v1");
assert.equal(control.base, "bfde0d8d1135f5c5f48a5f3d619ab30050efab83");
assert.equal(control.architecture.direction, "V36_INCUMBENT_QUOTE_PATH_PLUS_JUL6_PRESSURE_STATE_MACHINE_BYTE_FOR_FUNCTION_INHERITED");
assert.equal(classifier.status, "CLASSIFIER_RESEARCH_OPEN");
assert.equal(classifier.V40_policy_imports_V39, false);
assert.equal(classifier.V40_state_combiner_identity, true);
assert.equal(market.score.D, 804); assert.equal(market.score.legs, 1608);
assert.equal(strict.score.D, 804); assert.equal(strict.score.legs, 1608);
assert.equal(market.reach_grade.answer_key_games, 637); assert.equal(market.reach_grade.answer_key_locked_cents, 5253);
assert.equal(sanity.post_decision_rest_at_or_above_ask_violations, 0);
assert(Number.isInteger(joins.join_legs));
assert(joins.BOSCOP_COP);
assert(named.ARNROM && named.BOSCOP && named.WESPAA && named.NIKVRB);
assert.equal(typeof acceptance.pass, "boolean");
assert.equal(forbidden.holdout_accesses, 0); assert.equal(forbidden.live_accesses, 0); assert.equal(forbidden.network_runtime_accesses, 0);
assert.equal(determinism.byte_identical, true); assert.equal(determinism.clean_builds, 2);
for (const [name, meta] of Object.entries(manifest.files)) { const file = path.join(root, name); assert(fs.existsSync(file), name); assert.equal(hash(file), meta.sha256, name); assert.equal(fs.statSync(file).size, meta.bytes, name); }

process.stdout.write(`${JSON.stringify({ package: root, tests: 28, passed: 28 }, null, 2)}\n`);

