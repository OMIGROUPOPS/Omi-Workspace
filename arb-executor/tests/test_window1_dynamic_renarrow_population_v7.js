#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const population = path.join(repo, ".claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801");
const five = path.join(repo, ".claude/window1_live_v4_replay/five_exact_execution_gate_v7_20260801/FIVE_GAME_HONEST_GATE.json");

function test(name, fn) {
  try { fn(); process.stdout.write(`PASS ${name}\n`); }
  catch (error) { process.stderr.write(`FAIL ${name}: ${error.stack || error}\n`); process.exitCode = 1; }
}

test("five-game admission is separate from execution-floor quality", () => {
  const receipt = JSON.parse(fs.readFileSync(five));
  assert.strictEqual(receipt.five_game_gate_passed, true);
  assert.strictEqual(receipt.population_804_authorized_by_gate, true);
  assert.strictEqual(receipt.honest_completed_pair_count, 5);
  assert.strictEqual(receipt.execution_floor_gate_pass_count, 3);
  assert.strictEqual(receipt.objective_gate_pass_count, 3);
  const legs = receipt.events.flatMap((event) => event.legs);
  assert.strictEqual(legs.filter((leg) => leg.market_ceiling_class === "EXACT_ASK_REACHABLE_FLOOR_EQUALS_W1_CLOSE").length, 2);
  assert.strictEqual(legs.filter((leg) => leg.delta_to_own_ask_reachable_low_cents === 0).length, 8);
  assert.strictEqual(legs.filter((leg) => leg.delta_to_own_ask_reachable_low_cents === 1).length, 2);
});

test("population and both ceiling identities conserve", () => {
  const receipt = JSON.parse(fs.readFileSync(path.join(population, "CONSERVATION_RECEIPT.json")));
  assert.strictEqual(receipt.D, 804);
  assert.strictEqual(receipt.legs, 1608);
  assert.strictEqual(receipt.take_ceiling, 516);
  assert.strictEqual(receipt.maker_ceiling, 253);
  assert.strictEqual(receipt.event_partition_conservation, 804);
  assert.strictEqual(receipt.leg_partition_conservation, 1608);
  assert.strictEqual(receipt.no_scorer_import_or_invocation, true);
});

test("ledger contains every event and leg with separate ceiling and floor facts", () => {
  const bytes = zlib.gunzipSync(fs.readFileSync(path.join(population, "EVENT_LEDGER.jsonl.gz"))).toString("utf8").trim().split("\n");
  assert.strictEqual(bytes.length, 804);
  const rows = bytes.map(JSON.parse);
  assert.strictEqual(new Set(rows.map((row) => row.event_id)).size, 804);
  assert.strictEqual(rows.reduce((sum, row) => sum + Object.keys(row.legs).length, 0), 1608);
  for (const row of rows) for (const leg of Object.values(row.legs)) {
    assert.strictEqual(leg.pair_reference_cents, "NOT_BOUND");
    assert.ok(["ASK_REACHABLE_FLOOR_BELOW_W1_CLOSE", "EXACT_ASK_REACHABLE_FLOOR_EQUALS_W1_CLOSE", "ASK_REACHABLE_FLOOR_ABOVE_W1_CLOSE", "ASK_REACHABLE_FLOOR_OR_CLOSE_UNAVAILABLE"].includes(leg.market_ceiling_class));
  }
});

test("score and selection fields remain null", () => {
  const summary = JSON.parse(fs.readFileSync(path.join(population, "POPULATION_SUMMARY.json")));
  assert.deepStrictEqual(summary.performance_fields, { C: null, PC: null, IC: null, S: null, ranking: null, selection: null });
  assert.strictEqual(summary.ask_side_only, true);
  assert.strictEqual(summary.dwell_seconds, 10);
  assert.strictEqual(summary.exact_quantity, 5);
});
