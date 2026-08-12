#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/v52_judgment_gate_20260812");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(out, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);

const status = read("CONSTRUCTION_STATUS.json");
const flow = read("STAGE1_FLOW_ASSERTIONS.json");
const posting = read("POSTING_AND_READ_DISTRIBUTIONS.json");
const states = read("THREE_STATE_CENSUS.json");
const market = read("MARKET_GRADE_SCORECARD.json");
const strict = read("STRICT_BUILD_VERIFICATION_SCORECARD.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");
const actions = rows("BIRTH_LICENSE_ACTION_LEDGER.jsonl.gz");
const onsets = rows("STABILITY_ONSET_LEDGER.jsonl.gz");
const decision = rows("DECISION_TRACE_1608.jsonl.gz");

assert.equal(flow.pass, true);
assert.equal(posting.REFLEX_POST, 0);
assert.equal(states.conservation.rows, 804);
assert.equal(states.conservation.assigned_once, true);
assert.equal(onsets.length, 1608);
assert.equal(decision.length, 1608);
assert.ok(actions.length > 0);
assert.ok(actions.every((row) => row.birth_license.onset.passed && row.birth_license.read.passed && row.birth_license.diary.passed));
assert.ok(actions.every((row) => row.birth_license.level.displayed_bid_consumed === false));
assert.equal(market.ruler, "CANON_TRADES_AS_TRUTH");
assert.equal(strict.role, "BUILD_VERIFICATION_ONLY_NOT_MARKET_VALUE");
assert.equal(status.no_deployment, true);
for (const [name, entry] of Object.entries(manifest.files)) {
  if (name === "ARTIFACT_HASH_MANIFEST.json") continue;
  const bytes = fs.readFileSync(path.join(out, name));
  assert.equal(crypto.createHash("sha256").update(bytes).digest("hex"), entry.sha256, name);
  assert.equal(bytes.length, entry.bytes, name);
}
console.log(JSON.stringify({ tests: 14, status: status.status, pass: true }));
