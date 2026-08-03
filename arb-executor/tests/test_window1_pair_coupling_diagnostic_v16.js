#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { crossValidatedModel, nextCapacityFloor } = require("../analysis/build_window1_pair_coupling_diagnostic_v16.js");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/pair_coupling_diagnostic_v16_20260803");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name)));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(out, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);

const events = rows("PAIR_FLOOR_COUPLING_EVENT_LEDGER.jsonl.gz"), carried = rows("STRICT_CARRIED_PAIR_COUPLING_LEDGER.jsonl.gz"), timing = read("FLOOR_TIMING_CENSUS.json"), conditional = read("CONDITIONAL_SIBLING_FLOOR_DISTRIBUTIONS.json"), inversion = read("PAIR_INVERSION_LAW_RECEIPT.json"), cf = read("STRICT_CARRIED_PAIR_COUNTERFACTUAL.json"), control = read("CONTROL_BINDING.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
assert.equal(events.length, 804); assert.equal(events.filter((r) => r.fit_excluded).length, 5); assert.equal(carried.length, 52);
assert.deepEqual(new Set(events.filter((r) => r.fit_excluded).map((r) => r.event_id)), new Set(conditional.fit_population.excluded_exact_start_events));
assert.equal(timing.population.events, 804); assert.equal(timing.population.fitted_events, 799);
for (const event of events) for (const kind of ["ASK_CAPACITY", "TRADED"]) if (event.floors[kind]?.status === "STRICTLY_ASYNCHRONOUS") { assert(event.floors[kind].gap_seconds > 0); assert(event.floors[kind].first.clock.t_minus_scheduled_seconds !== null); assert(event.floors[kind].second.clock.t_minus_scheduled_seconds !== null); assert(event.floors[kind].first.proof.receipt); assert(event.floors[kind].second.proof.receipt); }
for (const kind of ["ASK_CAPACITY", "TRADED"]) { assert(Array.isArray(conditional.by_category_and_starting_price_split[kind])); assert(Array.isArray(conditional.by_category_and_first_floor_price_region[kind])); assert(Array.isArray(inversion.by_category_and_starting_price_split[kind])); }
for (const row of carried) { assert(row.counterfactual.causal_policy_claim === false); if (row.chronological_status === "STRICT_FIRST_THEN_SECOND" && row.counterfactual.available) assert(row.second_leg.next_strictly_later_qualifying_ask_floor.evidence_ts > row.second_leg.action_clock.timestamp_epoch); }
assert.equal(cf.baseline.completed_pairs, 185); assert.equal(cf.baseline.pairs_under_par, 94); assert.equal(cf.baseline.strict_one_above_one_below_pairs, 52);
assert.equal(control.behavior_changed, false); assert.equal(control.scorer_invocations, 0); assert.equal(forbidden.holdout_july_24_26_accessed, false); assert.equal(forbidden.behavior_changes, 0);

const modelRows = Array.from({ length: 24 }, (_, i) => ({ event_id: `E${i}`, x: i, t: i % 4, y: 2 * i + (i % 2) }));
const model = crossValidatedModel(modelRows, ["x", "t"], "y"); assert.equal(model.n, 24); assert.equal(model.thin, false); assert(model.leave_one_out_residual_distribution.n === 24);
const books = [{ ts: 0, ask: 50, bid: 49, spread: 1, asks: [[50, 5]], receipt: "r0", source_ordinal: 1 }, { ts: 10, ask: 50, bid: 49, spread: 1, asks: [[50, 5]], receipt: "r1", source_ordinal: 2 }, { ts: 11, ask: 49, bid: 48, spread: 1, asks: [[49, 5]], receipt: "r2", source_ordinal: 3 }, { ts: 21, ask: 49, bid: 48, spread: 1, asks: [[49, 5]], receipt: "r3", source_ordinal: 4 }];
assert.equal(nextCapacityFloor(books, 10).limit_cents, 49); assert.equal(nextCapacityFloor(books, 10).evidence_ts, 21);

process.stdout.write(`${JSON.stringify({ status: "PASS", assertions: 30, events: events.length, carried_rows: carried.length })}\n`);
