"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const root = path.resolve(__dirname, "../..");
const pkg = path.join(root, ".claude/window1_live_v4_replay/v48_trades_as_truth_20260810");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(pkg, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
assert.equal(control.schema_version, "window1-v48-trades-as-truth-control-v1");
assert.equal(control.base, "fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34");
assert.deepEqual(control.architecture.excluded_credit_filters, ["ASK", "QUOTE_TOUCH", "AGGRESSOR_SIDE", "DWELL", "SIZE", "ARRIVAL_DIRECTION", "CHANNEL_TAXONOMY"]);

const attribution = read("ATTRIBUTION_SCORECARD.json");
assert.equal(attribution.rows.length, 5);
assert.equal(attribution.frozen_V47_reproduction.pass, true);
assert.ok(["TRADE_TRUTH_BID_MINUS_ONE", "TRADE_TRUTH_BID", "TRADE_TRUTH_RECENT_TRADE"].includes(attribution.selected_ladder));
assert.equal(attribution.rows.find((row) => row.machine === "V47_BASELINE").MARKET.completed_pairs, 396);

const floors = read("TRADED_FLOOR_RE_SUM.json");
assert.equal(floors.conservation.games, 804);
assert.equal(floors.conservation.legs, 1608);
assert.equal(floors.conservation.pass, true);
assert.equal(rows("TRADED_FLOOR_GAME_LEDGER.jsonl.gz").length, 804);
assert.equal(rows("TRADED_FLOOR_LEG_LEDGER.jsonl.gz").length, 1608);

const named = read("NAMED_V48_RECEIPT.json");
assert.equal(named.LUZTSE_TSE.condition, "CREDIT_IFF_TRUE_TRADE_PRINT_AT_OR_BELOW_79_WHILE_THE_79_REST_STOOD");
assert.equal(named.LUZTSE_TSE.pass, true);
assert.equal(named.pass, true);

const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
for (const [key, value] of Object.entries(forbidden)) if (key.endsWith("_accesses") || key === "mutations") assert.equal(value, 0, key);

const determinism = read("DETERMINISM_RECEIPT.json");
assert.equal(determinism.clean_builds, 2);
assert.equal(determinism.byte_identical, true);

const manifest = read("ARTIFACT_HASH_MANIFEST.json");
for (const [name, receipt] of Object.entries(manifest.files)) {
  const file = path.join(pkg, name);
  assert.equal(fs.statSync(file).size, receipt.bytes, name);
  assert.equal(sha(file), receipt.sha256, name);
}

console.log("PASS test_window1_v48_trades_as_truth_package");
