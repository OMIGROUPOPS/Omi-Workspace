"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/live_book_ordinal_root_repair_v15_20260803");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name)));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(root, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

const census = read("CURRENT_V11_SIX_GATE_NON_ACTION_CENSUS.json");
const compare = read("V11_TO_V15_COMPARISON.json");
const above = read("ABOVE_OBSERVED_LOW_REMOVAL_RECEIPT.json");
const persistence = read("UNANIMOUS_LOWER_PERSISTENCE_ROOT_RECEIPT.json");
const carried = read("CARRIED_PAIR_RECONCILIATION.json");
const constants = read("CONSTANT_PROVENANCE.json");
const deterministic = read("DETERMINISM_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const combinedLegs = rows("V15_COMBINED_LEG_LEDGER.jsonl.gz");
const combinedEvents = rows("V15_COMBINED_EVENT_LEDGER.jsonl.gz");
const carriedRows = rows("STRICT_CARRIED_PAIR_DIAGNOSTIC.jsonl.gz");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.deepStrictEqual(census.population, { events: 804, legs: 1608, acted: 712, no_action: 896 });
assert.strictEqual(Object.values(census.six_gates).reduce((a, b) => a + b, 0), 806);
assert.strictEqual(census.source_unavailable, 90);
assert.strictEqual(census.six_gates.HISTORICAL_LOW_ANCHOR, 283);
assert.strictEqual(census.six_gates.UNANIMOUS_LOWER_PERSISTENCE, 183);
assert.strictEqual(above.baseline_above_observed_low_legs, 283);
assert.strictEqual(above.tolerance_cents, null);
assert.strictEqual(above.invented_thresholds, 0);
assert.strictEqual(persistence.baseline_unanimous_lower_legs, 183);
assert.strictEqual(persistence.all_fitted_waits_exhausted_and_all_other_predicates_satisfied, 34);
assert.ok(persistence.fitted_persistence_only_new_actions_from_baseline_lower >= 34);
assert.ok(persistence.fitted_persistence_only_actions_with_exact_authority_receipt >= 34);
assert.strictEqual(combinedLegs.length, 1608);
assert.strictEqual(combinedEvents.length, 804);
assert.strictEqual(compare.variants.combined.overall.events, 804);
assert.strictEqual(carried.completed_pairs, 185);
assert.strictEqual(carried.strict_one_above_one_below_rows_diagnosed, 52);
assert.strictEqual(carried.requested_approximate_73_reconciliation.exact_73_cohort_exists, false);
assert.strictEqual(carried.requested_approximate_73_reconciliation.under_par_not_both_below, 78);
assert.strictEqual(carriedRows.length, 52);
assert.ok(carriedRows.every((x) => ["FIRST", "SECOND", "SAME_TIMESTAMP"].includes(x.positive_leg_fill_order)));
assert.ok(carriedRows.every((x) => x.positive_leg.action_clock && x.sibling_leg.action_clock));
assert.strictEqual(constants.inherited_and_unchanged.find((x) => x.constant === "dwell_seconds").value, 10);
assert.strictEqual(constants.inherited_and_unchanged.find((x) => x.constant === "exact_quantity_contracts").value, 5);
assert.strictEqual(constants.above_low_tolerance.value, null);
assert.strictEqual(deterministic.byte_identical, true);
assert.strictEqual(forbidden.holdout_access, false);
assert.strictEqual(forbidden.scorer_invocations, 0);
assert.strictEqual(Object.entries(manifest.files).every(([name, item]) => hash(fs.readFileSync(path.join(root, name))) === item.sha256), true);

process.stdout.write(`${JSON.stringify({ status: "PASS", assertions: 30, events: 804, legs: 1608, strict_carried_pairs: 52 })}\n`);
