"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const output = process.argv[2] ? path.resolve(process.argv[2]) : path.join(repo, ".claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805");
const json = (name) => JSON.parse(fs.readFileSync(path.join(output, name)));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(output, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const score = json("SCORECARD.json");
assert.strictEqual(score.V32_score.D, 804);
assert.strictEqual(score.V32_score.legs, 1608);
assert.strictEqual(score.R3_floor.joint_objective_pairs, 68);
assert.strictEqual(score.V32_score.proven_maker_legs + score.V32_score.proven_taker_legs, score.V32_score.credited_legs);
assert.strictEqual(score.model_free_comparison_ceiling.joint_pairs, 201);
assert.strictEqual(score.model_free_comparison_ceiling.executable_gap_is_execution_price, 201 - score.V32_score.joint_objective_pairs);
const legs = rows("LEG_LEDGER.jsonl.gz");
assert.strictEqual(legs.length, 1608);
for (const leg of legs) {
  if (leg.honest_fill_class?.startsWith("PROVEN_MAKER")) assert(leg.fill_timestamp_epoch > leg.action_timestamp_epoch, leg.leg_identity);
  if (leg.honest_fill_class?.startsWith("PROVEN_TAKER")) assert.strictEqual(leg.fill_timestamp_epoch, leg.action_timestamp_epoch, leg.leg_identity);
  if (leg.credited) assert(Number.isInteger(leg.entry_cents));
}
const events = rows("EVENT_LEDGER.jsonl.gz");
assert.strictEqual(events.length, 804);
assert(events.every((event) => !event.completed_pair || event.combined_entry_cents < 100));
const trace = json("DECISION_TRACE_1608.json");
assert.strictEqual(trace.rows.length, 1608);
assert.strictEqual(trace.conservation.actual, 1608);
const disagreement = json("STATE_DISAGREEMENT_RECEIPT.json");
assert(!Object.prototype.hasOwnProperty.call(disagreement.by_category, "undefined"));
for (const category of ["ATP_CHALL", "ATP_MAIN", "WTA_CHALL", "WTA_MAIN"]) assert(disagreement.by_category[category]);
const arn = json("ARNROM_REGRESSION_RECEIPT.json");
assert(arn.event_id.includes("ARNROM"));
assert(arn.result);
const forbidden = json("FORBIDDEN_ACCESS_RECEIPT.json");
for (const [key, value] of Object.entries(forbidden)) if (key.endsWith("_accesses")) assert.strictEqual(value, 0, key);
const det = json("DETERMINISM_RECEIPT.json");
assert.strictEqual(det.byte_identical_core_artifacts, true);
const manifest = json("ARTIFACT_HASH_MANIFEST.json");
for (const [name, receipt] of Object.entries(manifest.files)) { const file = path.join(output, name); assert(fs.existsSync(file), name); assert.strictEqual(hash(file), receipt.sha256, name); assert.strictEqual(fs.statSync(file).size, receipt.bytes, name); }
assert(!fs.existsSync(path.join(output, ".print-spool")));
process.stdout.write("window1 V32 no-chase package tests: PASS\n");
