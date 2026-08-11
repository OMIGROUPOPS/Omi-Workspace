"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../..");
const pkg = path.join(root, ".claude/window1_live_v4_replay/v49_evidenced_level_standing_20260810");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
assert.equal(control.schema_version, "window1-v49-evidenced-level-standing-control-v1");
assert.equal(control.base, "fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34");
assert.equal(control.architecture.inherited_standing_constant.seconds, 300);
assert.equal(control.architecture.historical_bid_sighting_alone, "NO_AUTHORITY");

const scorecard = read("ATTRIBUTION_SCORECARD.json");
assert.equal(scorecard.rows.length, 2);
assert.equal(scorecard.frozen_V47_reproduction.pass, true);
const baseline = scorecard.rows.find((row) => row.machine === "TRADE_TRUTH_V47_BASELINE");
const v49 = scorecard.rows.find((row) => row.machine === "V49_EVIDENCED_LEVEL_STANDING");
assert.equal(baseline.MARKET.completed_pairs, 396);
assert.equal(baseline.FULL_BOOK.true_book_net_cents, 1774);
assert.equal(v49.MARKET.completed_pairs, 393);
assert.equal(v49.STRICT_PRINT_CROSS.completed_pairs, 318);

const named = read("NAMED_V49_RECEIPT.json");
assert.equal(named.rows.HERKAZ.V49.completed, false);
assert.equal(named.assertions.HERKAZ_completes, false);
for (const label of ["ARNROM", "KIRSEK", "KRUFER", "BOSCOP", "PANFAL"]) {
  assert.equal(named.assertions[`${label}_no_regression`], true, label);
}

const status = read("CONSTRUCTION_STATUS.json");
assert.equal(status.status, "BLOCKED_V47_REMAINS_OPERATIVE");
assert.deepEqual(status.reasons, ["BOUND_REGRESSION"]);

const determinism = read("DETERMINISM_RECEIPT.json");
assert.equal(determinism.clean_builds, 2);
assert.equal(determinism.byte_identical, true);

const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
for (const [key, value] of Object.entries(forbidden)) {
  if (key.endsWith("_accesses") || key === "mutations") assert.equal(value, 0, key);
}

const manifest = read("ARTIFACT_HASH_MANIFEST.json");
for (const [name, receipt] of Object.entries(manifest.files)) {
  const file = path.join(pkg, name);
  assert.equal(fs.statSync(file).size, receipt.bytes, name);
  assert.equal(sha(file), receipt.sha256, name);
}

console.log("PASS test_window1_v49_evidenced_level_standing_package");
