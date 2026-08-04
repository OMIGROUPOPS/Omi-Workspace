"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/v28_anchor_cap_stack_20260804");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(root, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
const hash = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");

assert.ok(fs.existsSync(root));
const control = read("CONTROL_SUMMARY.json"), score = read("SCORECARD.json"), trace = read("DECISION_TRACE_1608.json"), cap = read("CAP_REARM_RECEIPTS.json"), shelves = read("RATIFICATION_AND_SHELVING_RECEIPT.json"), diff = read("DIFFERENTIAL_RECEIPT.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), deterministic = read("DETERMINISM_RECEIPT.json"), artifacts = read("ARTIFACT_HASH_MANIFEST.json"), fn = read("F1_VS_V28_FN_TABLE.json");
const events = rows("EVENT_LEDGER.jsonl.gz"), legs = rows("LEG_LEDGER.jsonl.gz"), regrets = rows("REGRET_LEG_LEDGER.jsonl.gz");

assert.strictEqual(control.baseline.joint, 62);
assert.strictEqual(score.F1_floor.joint_objective_pairs, 62);
assert.ok(score.V28_score.joint_objective_pairs > 62);
assert.strictEqual(score.disposition, "V28_SURVIVES_F1_JOINT_FLOOR_PENDING_OPERATOR_RATIFICATION");
assert.deepStrictEqual(shelves.stacked_candidate.components, ["FIX1_ANCHOR_REARM", "FIX2_CAP_REARM"]);
assert.strictEqual(shelves.shelved_not_deleted.length, 2);
assert.deepStrictEqual(shelves.excluded_from_V28, ["FIX3_VERDICT_FALSIFIABILITY", "FIX4_ADMISSION_REASK"]);
assert.strictEqual(cap.targeted_F1_cap_stops, 188);
assert.strictEqual(cap.frozen_no_return_receipts_reused + cap.freshly_scanned_F1_induced_cap_stops, 188);
assert.strictEqual(cap.rearmed_legs + cap.no_return_legs, 188);
assert.ok(cap.receipts.filter((x) => x.rearm).every((x) => x.rearm.ask <= x.cap_cents && x.rearm.spread === 1 && x.rearm.ask_dwell_seconds >= 10 && x.rearm.top_ask_size >= 5));
assert.strictEqual(events.length, 804);
assert.strictEqual(legs.length, 1608);
assert.strictEqual(regrets.length, 1608);
assert.strictEqual(trace.rows.length, 1608);
assert.strictEqual(new Set(trace.rows.map((x) => x.leg_identity)).size, 1608);
assert.strictEqual(diff.changed_leg_streams, cap.rearmed_legs);
assert.ok(diff.rows.filter((x) => !x.changed).every((x) => x.F1_semantic_sha256 === x.V28_semantic_sha256));
assert.strictEqual(fn.comparison.find((x) => x.layer === "PLACEMENT_CAP").stopped_delta, -cap.rearmed_legs);
assert.strictEqual(score.V28_score.D, 804);
assert.strictEqual(score.V28_score.completed_pairs - score.F1_floor.completed_pairs, cap.rearmed_legs);
assert.ok(Object.values(forbidden).filter((x) => typeof x === "boolean").every((x) => x === false));
assert.strictEqual(deterministic.clean_builds, 2);
assert.strictEqual(deterministic.byte_identical_payloads, true);
for (const [name, receipt] of Object.entries(artifacts.files)) { const p = path.join(root, name); assert.ok(fs.existsSync(p), name); assert.strictEqual(hash(p), receipt.sha256, name); assert.strictEqual(fs.statSync(p).size, receipt.bytes, name); }

process.stdout.write(`window1 V28 package tests: PASS (${Object.keys(artifacts.files).length} artifact hashes; 23 invariants)\n`);
