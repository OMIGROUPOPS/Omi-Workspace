#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const sha256 = (body) => crypto.createHash("sha256").update(body).digest("hex");
let assertions = 0;
function check(condition, message) { assertions += 1; assert.ok(condition, message); }
function equal(actual, expected, message) { assertions += 1; assert.deepStrictEqual(actual, expected, message); }

const gap = read("COMMITMENT_GAP_CENSUS.json");
const sibling = read("SIBLING_FLOOR_CONDITIONAL_CENSUS.json");
const naked = read("NAKED_NONCOMPLETION_RECEIPT.json");
const rule = read("CAUSAL_COMMITMENT_RULE_SPEC.json");
const manifest = read("ARTIFACT_HASH_MANIFEST.json");
const source = fs.readFileSync(path.join(repo, "arb-executor/analysis/build_window1_first_leg_commitment_diagnostic_v1.js"), "utf8");
const ledger = zlib.gunzipSync(fs.readFileSync(path.join(out, "FIRST_LEG_COMMITMENT_EVENT_LEDGER.jsonl.gz"))).toString("utf8").trimEnd().split("\n").map(JSON.parse);

equal(gap.conservation.D, 804, "D remains 804");
equal(ledger.length, 804, "one event ledger row per event");
equal(gap.conservation.both_capacity_floors_available + gap.conservation.neither_capacity_floor_available, 804, "both/none floor conservation");
equal(gap.conservation.strict_first_leg_commitments + gap.conservation.simultaneous_floor_evidence + gap.conservation.neither_capacity_floor_available, 804, "commitment/tie/none conservation");
equal(gap.conservation.entry_cost_affordable_below_100 + gap.conservation.naked_or_never_completed_under_entry_cost_law, gap.conservation.strict_first_leg_commitments, "entry-cost conservation");
equal(gap.conservation.later_sibling_floor_available, gap.conservation.strict_first_leg_commitments, "all strict commitments have an independently rescanned later sibling floor on this tape");
equal(gap.conservation.capacity_reproduction_mismatches, 0, "raw floor scan reproduces frozen capacity floor");
equal(Object.values(gap.by_category_and_observable_starting_price_region).reduce((sum, cell) => sum + cell.events, 0), 804, "partition rows conserve to D");
equal(Object.values(sibling.by_category_starting_region_and_exact_first_x).reduce((sum, cell) => sum + cell.n, 0), gap.conservation.strict_first_leg_commitments, "exact-X conditionals conserve");
check(Object.values(gap.by_category_and_observable_starting_price_region).every((cell) => ["ATP_CHALL", "ATP_MAIN", "WTA_CHALL", "WTA_MAIN"].includes(cell.category)), "every summary retains category");
check(Object.values(gap.by_category_and_observable_starting_price_region).every((cell) => typeof cell.starting_price_region_pair === "string"), "every summary retains observable starting region");
check(Object.values(gap.by_category_and_observable_starting_price_region).every((cell) => cell.thin === (cell.events < 5)), "thin cells are labeled, never pooled");
check(ledger.every((row) => row.legs.length === 2), "two legs remain explicit");
check(ledger.every((row) => row.legs.every((leg) => !leg.global_floor || Number.isFinite(leg.global_floor.clock.tminus_scheduled_seconds))), "every floor has scheduled clock");
check(ledger.every((row) => row.legs.every((leg) => !leg.global_floor || Number.isFinite(leg.global_floor.clock.tminus_actual_bell_seconds) || leg.global_floor.clock.tminus_actual_bell_seconds === "NOT_BOUND")), "actual bell is numeric or explicitly NOT_BOUND");
check(ledger.filter((row) => row.first_leg_commitment).every((row) => row.later_sibling_floor && row.later_sibling_floor.evidence_ts > row.first_leg_commitment.evidence_ts), "sibling proof is strictly later");
check(ledger.filter((row) => row.first_leg_commitment && row.later_sibling_floor).every((row) => row.pair_entry_cost_cents === row.first_leg_commitment.price_cents + row.later_sibling_floor.limit_cents), "pair entry cost arithmetic exact");
check(ledger.every((row) => row.entry_cost_affordable_below_100 === null || row.entry_cost_affordable_below_100 === (row.pair_entry_cost_cents < 100)), "strict below-100 law exact");
equal(rule.status, "SPEC_ONLY_UNVALIDATED", "rule remains unvalidated");
equal(rule.provenance.independent_pair_value_reference.value, "NOT_BOUND", "no proxied pair reference");
equal(rule.provenance.naked_risk_probability_threshold.value, null, "no invented risk threshold");
equal(rule.provenance.maximum_naked_hold_seconds.value, null, "no invented naked-hold horizon");
check(!/require\([^)]*scor/i.test(source), "builder imports no scorer");
check(!source.includes("JUL24") && !source.includes("JUL25") && !source.includes("JUL26"), "builder contains no holdout identity");
equal(naked.fee_treatment, "NOT_INCLUDED; this is the existing entry-cost S diagnostic, not fee-aware PC", "fee fence explicit");

for (const [name, identity] of Object.entries(manifest.files)) {
  const body = fs.readFileSync(path.join(out, name));
  equal(body.length, identity.bytes, `${name} byte count`);
  equal(sha256(body), identity.sha256, `${name} hash`);
}

process.stdout.write(`${JSON.stringify({ status: "PASS", assertions, events: ledger.length, partitions: Object.keys(gap.by_category_and_observable_starting_price_region).length, exact_x_cells: Object.keys(sibling.by_category_starting_region_and_exact_first_x).length }, null, 2)}\n`);
