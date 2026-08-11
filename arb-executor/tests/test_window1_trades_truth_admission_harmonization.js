"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../..");
const policy = require("../analysis/window1_v48_trades_as_truth.js");
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

// A through-the-bid print is admitted when—and only when—the true trade and
// the active rest overlap at the same price. Book fields are deliberately
// present to prove that they are not consulted by the credit organ.
const rest35 = { target_cents: 35, action_ts: 1783839079 };
const genuine35 = {
  kind: "PRINT",
  ts: 1783854017.132571,
  trade_id: "synthetic-through-bid-35",
  price: 35,
  book_bid: 38,
  book_ask: 39,
};
assert.equal(policy.tradeTruthCredit(rest35, genuine35), true);

// The frozen FANBIG chronology contains two different receipts, neither of
// which meets the overlap law: 38 > active 35 at 11:00:17Z, then 35 > active
// 32 at 15:17:51Z. Joining the price from the latter to the timestamp/order
// from the former is forbidden.
const canonicalAtClaimedEpoch = {
  kind: "PRINT",
  ts: 1783854017.132571,
  trade_id: "54d11711-fb6b-5bb1-35cc-906d7014588e",
  price: 38,
  book_bid: 38,
  book_ask: 39,
};
assert.equal(policy.tradeTruthCredit(rest35, canonicalAtClaimedEpoch), false);

const rest32 = { target_cents: 32, action_ts: 1783869263 };
const canonicalFirst35 = {
  kind: "PRINT",
  ts: 1783869471.137727,
  trade_id: "9b39056f-f7c5-5ac7-9a31-b5b715efdccd",
  price: 35,
};
assert.equal(policy.tradeTruthCredit(rest32, canonicalFirst35), false);

const attribution = path.join(root, ".claude/window1_live_v4_replay/v48_trades_as_truth_20260810/ATTRIBUTION_SCORECARD.json");
assert.equal(sha(attribution), "59adad66bb6d5af1801e4c6cbdb95d3b98f5c5eebd639844017efeffeeb66075");
const rows = JSON.parse(fs.readFileSync(attribution, "utf8")).rows;
assert.equal(rows.find((row) => row.machine === "V47_BASELINE").MARKET.completed_pairs, 396);
assert.equal(rows.find((row) => row.machine === "TRADE_TRUTH_V47_INCUMBENT").MARKET.completed_pairs, 396);

const pkg = path.join(root, ".claude/window1_live_v4_replay/trades_truth_admission_harmonization_20260811");
const receipt = JSON.parse(fs.readFileSync(path.join(pkg, "ADMISSION_FORENSIC_RECEIPT.json"), "utf8"));
assert.equal(receipt.root_cause.class, "CROSS_RECEIPT_PRICE_TIMESTAMP_JOIN");
assert.equal(receipt.ruling.fanbig_fan_credited, false);
assert.equal(receipt.counterfactual_unit_proof.tradeTruthCredit, true);
const table = JSON.parse(fs.readFileSync(path.join(pkg, "HARMONIZATION_TABLE.json"), "utf8"));
assert.equal(table.rows[0].new_status, "DRIFT->FIXED");
assert.equal(table.rows[0].fixed_surface, "EVIDENCE_HARMONIZATION");
const identity = JSON.parse(fs.readFileSync(path.join(pkg, "POLICY_BYTE_IDENTITY.json"), "utf8"));
assert.equal(identity.policy_files_changed, 0);
assert.equal(identity.pass, true);

console.log("PASS test_window1_trades_truth_admission_harmonization");
