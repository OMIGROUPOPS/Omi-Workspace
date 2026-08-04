"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../.."), root = path.join(repo, ".claude/window1_live_v4_replay/v29_mirror_armed_leg2_20260804"), v28 = path.join(repo, ".claude/window1_live_v4_replay/v28_anchor_cap_stack_20260804");
const read = (n) => JSON.parse(fs.readFileSync(path.join(root, n))), hash = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
const gunzip = (n) => zlib.gunzipSync(fs.readFileSync(path.join(root, n))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);

const score = read("SCORECARD.json"), authority = read("AUTHORITY_RECEIPT.json"), targets = read("TARGET_MASS_CONVERSION.json"), diff = read("DIFFERENTIAL_RECEIPT.json"), trace = read("TRACE_RECEIPT.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), det = read("DETERMINISM_RECEIPT.json"), artifacts = read("ARTIFACT_HASH_MANIFEST.json"), rows = gunzip("MIRROR_ARM_TARGET_MASS.jsonl.gz");
assert.strictEqual(score.V28_floor.joint_objective_pairs, 65);
assert.strictEqual(score.V29_score.joint_objective_pairs, 65);
assert.ok(Object.values(score.delta).every((x) => x === 0));
assert.strictEqual(authority.findings.numeric_decision_time_own_close_bar_authorized_cells, 0);
assert.strictEqual(authority.ruling, "OVERLAY_ABSTAINS_EVERYWHERE; V28 RUNS BYTE_IDENTICAL");
assert.strictEqual(targets.carried.target_mass, 144);
assert.strictEqual(targets.carried.structurally_eligible_before_authority_checks, 116);
assert.strictEqual(targets.carried.decision_reasons.SIBLING_CREDITED_DISCOUNT_AUTHORITY_NOT_BOUND, 116);
assert.strictEqual(targets.carried.decision_reasons.V28_ALREADY_HANDLES_LEG_BYTE_IDENTICAL, 28);
assert.strictEqual(targets.completion_mirror_false_negatives.target_mass, 237);
assert.strictEqual(targets.total.converted, 0);
assert.strictEqual(rows.length, 381);
assert.ok(rows.every((x) => x.decision.state === "ABSTAIN"));
assert.strictEqual(diff.changed_leg_streams, 0);
assert.strictEqual(diff.unchanged_leg_streams, 1608);
assert.ok(diff.artifact_identities.every((x) => x.equal));
assert.strictEqual(trace.rows, 1608);
assert.strictEqual(trace.byte_identical_because_overlay_has_zero_authorized_decisions, true);
for (const name of ["EVENT_LEDGER.jsonl.gz", "LEG_LEDGER.jsonl.gz", "DECISION_TRACE_1608.json", "FRONTIER.json", "REGRET_GAUGE.json", "REGRET_LEG_LEDGER.jsonl.gz"]) assert.strictEqual(hash(path.join(root, name)), hash(path.join(v28, name)), name);
assert.ok(Object.values(forbidden).every((x) => x === false));
assert.strictEqual(det.clean_builds, 2);
assert.strictEqual(det.byte_identical_payloads, true);
for (const [name, rec] of Object.entries(artifacts.files)) { const p = path.join(root, name === "DETERMINISM_RECEIPT" ? "DETERMINISM_RECEIPT.json" : name); assert.ok(fs.existsSync(p), name); assert.strictEqual(hash(p), rec.sha256, name); assert.strictEqual(fs.statSync(p).size, rec.bytes, name); }

process.stdout.write(`window1 V29 package tests: PASS (${Object.keys(artifacts.files).length} hashes; 23 invariants)\n`);
