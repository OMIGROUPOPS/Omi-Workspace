#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { askCapacity } = require("../analysis/build_window1_five_exact_full_stack.js");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));

const check = child.spawnSync(process.execPath,
  ["arb-executor/analysis/build_window1_five_exact_full_stack.js", ".", "--check"],
  { cwd: repo, encoding: "utf8", timeout: 120000 });
assert.strictEqual(check.status, 0, check.stderr || check.stdout);
assert.deepStrictEqual(JSON.parse(check.stdout), {
  status: "CHECK_PASS",
  event_count: 5,
  hold_gate_passed: false,
  population_804_run: false,
});

assert.deepStrictEqual(askCapacity(null, 50), { status: "EVIDENCE_ABSENT", quantity: null, levels: [] });
assert.deepStrictEqual(askCapacity({ asks: [[49, 4], [51, 100]] }, 50), {
  status: "EVIDENCE_ABSENT", quantity: 4, levels: [[49, 4]],
});
assert.deepStrictEqual(askCapacity({ asks: [[49, 4], [50, 1], [51, 100]] }, 50), {
  status: "PROVEN_FIVE_CONTRACT_CAPACITY", quantity: 5, levels: [[49, 4], [50, 1]],
});

const results = read("FIVE_GAME_FULL_STACK_RESULTS.json");
const packedLedger = read("PER_EVENT_DECISION_LEDGER.json");
const unpackedLedger = JSON.parse(zlib.gunzipSync(Buffer.from(packedLedger.gzip_base64, "base64")));
assert.strictEqual(packedLedger.encoding, "gzip+base64");
assert.strictEqual(unpackedLedger.length, 5);
const events = Object.fromEntries(results.events.map((row) => [row.event_id, row]));
assert.strictEqual(results.event_count, 5);
assert.strictEqual(results.hold_gate_passed, false);
assert.strictEqual(results.population_804_authorized_by_gate, false);
assert.strictEqual(results.population_804_run, false);
assert.strictEqual(results.pair_reference_law, "NOT_BOUND; no value or delta is proxied from either candidate fill");
assert.strictEqual(results.ceiling_reference.ask_only_10_second_event_ceiling, 532);
assert.strictEqual(results.ceiling_reference.capacity_adjustment, "NOT_PRECOMPUTED");
assert.ok(Object.values(results.category_price_region_partitions).every((cell) => cell.thin === true));
assert.strictEqual(Object.values(results.category_price_region_partitions).reduce((sum, cell) => sum + cell.leg_rows, 0), 10);

for (const event of results.events) for (const leg of Object.values(event.legs)) {
  assert.strictEqual(leg.pair_reference_cents, "NOT_BOUND");
  assert.strictEqual(leg.delta_to_pair_reference_cents, "NOT_BOUND");
  if (leg.fill) {
    const evidenceSize = leg.fill.evidence_size ?? leg.fill.evidence?.evidence_size;
    assert.strictEqual(leg.fill.quantity, 5);
    assert.ok(evidenceSize >= 5);
    assert.strictEqual(leg.accounting_status, "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN");
  }
}

const nikvrb = Object.values(events).find((row) => row.event_id.endsWith("NIKVRB"));
assert.strictEqual(nikvrb.integrity_hold, true);
assert.strictEqual(nikvrb.legs.NIK.entry_cents, 18);
assert.strictEqual(nikvrb.legs.NIK.fill.evidence.evidence_size, 86);
assert.strictEqual(nikvrb.legs.VRB.entry_cents, 68);
assert.strictEqual(nikvrb.legs.VRB.fill.evidence.evidence_size, 110);
assert.strictEqual(nikvrb.legs.NIK.change_status.orientation_conditioned_initial_tree, "FIRED");
assert.strictEqual(nikvrb.legs.VRB.change_status.orientation_conditioned_initial_tree, "FIRED");
assert.strictEqual(nikvrb.patience.sibling_recurrences, 66);

assert.deepStrictEqual(results.events.filter((row) => row.integrity_hold).map((row) => row.event_id), [nikvrb.event_id]);
assert.strictEqual(read("EVIDENCE_ABSENT_CAPACITY_RECEIPT.json").count, 0);
const defect = read("DEFECT_BEFORE_AFTER_RECEIPT.json");
assert.strictEqual(defect.pair_reference.after, "NOT_BOUND");
assert.ok(defect.capacity.number_moved.includes("null-sized NIKVRB credits 2->0"));
assert.ok(defect.recurrence_prose.after.includes("66 ask-side"));
assert.strictEqual(fs.existsSync(path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/POPULATION_804_RESULTS.json")), false);

const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
assert.ok(Object.values(forbidden).every((value) => value === false));

process.stdout.write("PASS test_window1_five_exact_full_stack_capacity (five-event gate FAIL; 804 not run)\n");
