"use strict";

const assert = require("assert");
const guard = require("../analysis/window1_named_subset_guard.js");

const A = "KXWTAMATCH-26JUL13CRIJEA";
const B = "KXATPCHALLENGERMATCH-26JUL12POLKUH";
const C = "KXATPMATCH-26JUL18DANPRA";

const spec = guard.parseExactNamedSubset(`${A},${B}`, "2");
assert.deepEqual(spec.event_ids, [A, B]);
assert.equal(spec.expected_games, 2);
assert.throws(() => guard.parseExactNamedSubset(`${A},${B}`, "3"), /named count 2 != expected 3/);
assert.throws(() => guard.parseExactNamedSubset(`${A},${A}`, "2"), /duplicate named game/);

const exact = guard.createExecutionGuard(spec);
exact.record(A);
exact.record(B);
assert.deepEqual(exact.finalize(), {
  mode: "EXACT_N_NAMED_GAMES",
  expected_games: 2,
  named_event_ids: [A, B],
  executed_event_ids: [A, B],
  total_games_executed: 2,
  other_games_executed: 0,
  missing_named_games: [],
  exact_identity_and_count: true,
});

const foreign = guard.createExecutionGuard(spec);
assert.throws(() => foreign.record(C), /unrequested execution/);
const duplicate = guard.createExecutionGuard(spec);
duplicate.record(A);
assert.throws(() => duplicate.record(A), /duplicate execution/);
const short = guard.createExecutionGuard(spec);
short.record(A);
assert.throws(() => short.finalize(), /executed count 1 != expected 2/);

console.log("window1_named_subset_guard: PASS");
