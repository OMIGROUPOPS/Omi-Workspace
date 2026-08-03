"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { evaluateLiveBookFloorAuthority, evaluateFittedPersistenceFloorAuthority } = require("../analysis/window1_quote_shape_live_book_persistence_v15.js");

const base = {
  unanimousFloor: true,
  ownMicroPositionObserved: true,
  inverseSiblingResolved: true,
  stableSigningSupported: true,
  freshOwnReceipt: true,
  askDwellSeconds: 10,
  dwellSeconds: 10,
  topAskSize: 5,
  quantity: 5,
};
const live = evaluateLiveBookFloorAuthority(base);
assert.strictEqual(live.supported, true);
assert.strictEqual(live.historical_low_equality_consulted, false);
assert.strictEqual(live.invented_thresholds, 0);
assert.strictEqual(evaluateLiveBookFloorAuthority({ ...base, freshOwnReceipt: false }).supported, false);

const persistence = {
  unanimousLower: true,
  currentAskAtObservedLow: true,
  freshOwnReceipt: true,
  strictlyLaterSamePriceAskReceipt: true,
  askDwellSeconds: 31,
  dwellSeconds: 10,
  topAskSize: 5,
  quantity: 5,
  ownMicroPositionObserved: true,
  inverseSiblingResolved: true,
  stableSigningSupported: true,
  persistenceProofs: [{ available: true, exhausted: true, median_wait_to_future_qualified_lower_seconds: 30 }],
};
const expired = evaluateFittedPersistenceFloorAuthority(persistence);
assert.strictEqual(expired.supported, true);
assert.strictEqual(expired.verdict, "FLOOR");
assert.strictEqual(expired.descent_ordinal_availability_is_not_a_veto, true);
assert.strictEqual(evaluateFittedPersistenceFloorAuthority({ ...persistence, persistenceProofs: [{ available: true, exhausted: false }] }).supported, false);
assert.strictEqual(evaluateFittedPersistenceFloorAuthority({ ...persistence, persistenceProofs: [] }).supported, false);
assert.throws(() => evaluateFittedPersistenceFloorAuthority({ ...persistence, askDwellSeconds: NaN }), /finite/);

const replay = fs.readFileSync(path.resolve(__dirname, "../analysis/build_window1_quote_shape_elimination_replay_v1.js"), "utf8");
assert.ok(replay.includes("!liveBookFloorV15 && row.prefix.ask_net !== row.prefix.ask_dip"));
assert.ok(replay.includes("evaluateFittedPersistenceFloorAuthority"));
assert.ok(replay.includes("price_cents: row.ask"));
assert.ok(replay.includes("const DWELL_SECONDS = 10, QUANTITY = 5"));
assert.ok(!replay.includes("liveBookFloorTolerance"));
assert.ok(replay.includes("--population-reference-ledger"));
assert.ok(replay.includes("for (const row of quoteRows) TARGETS.add(row.event_id)"));

process.stdout.write(`${JSON.stringify({ status: "PASS", assertions: 16, invented_thresholds: 0 })}\n`);
