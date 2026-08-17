#!/usr/bin/env node
"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v52m_macro_recognition.js");

const families = Object.fromEntries(policy.FAMILY_ORDER.map((family) => [family, 1]));
const confidence = Object.fromEntries(policy.FAMILY_ORDER.filter((family) => !policy.ABSTAIN_FAMILIES.has(family)).map((family) => [family, "95%"]));
const rows = policy.FAMILY_ORDER.flatMap((family, index) => [
  { family, category: "ALL", legs: 30, depth_below_open_c: { med: index % 5 }, floor_pos: { med: 0.5 } },
  ...(index < 13 ? [
    { family, category: "ATP_CHALL", legs: 30, depth_below_open_c: { med: index % 5 }, floor_pos: { med: 0.5 } },
    { family, category: "ATP_MAIN", legs: 30, depth_below_open_c: { med: index % 5 }, floor_pos: { med: 0.5 } },
    { family, category: "WTA_CHALL", legs: 30, depth_below_open_c: { med: index % 5 }, floor_pos: { med: 0.5 } },
  ] : []),
]).slice(0, 52);
while (rows.length < 52) rows.push({ family: policy.FAMILY_ORDER[rows.length % 13], category: `SYNTH_${rows.length}`, legs: 30, depth_below_open_c: { med: 1 }, floor_pos: { med: 0.5 } });
policy.configureShapeLibrary({
  taxonomy: { LABEL: "SHAPE_TAXONOMY_BUILD1", families, benchmark: { by_family_acc: confidence } },
  floor_tables: { LABEL: "PER_SHAPE_FLOOR_DEPTH_TABLES", rows },
  taxonomy_provenance: { commit: "e269779b0ec025d55f67d576e3cfb0cb575d5890", sha256: "a".repeat(64) },
  floor_table_provenance: { commit: "8ab4f2d9e8c831235dc7cb4570c88daa3caded50", sha256: "b".repeat(64) },
});

function classify(prices) {
  const state = policy.emptyShapeState();
  prices.forEach((price, index) => policy.observeTruePrint(state, { kind: "PRINT", ts: index * 60, ordinal: index, price, receipt: `R${index}` }));
  return policy.classifyShapeState(state, { timestamp_epoch: (prices.length - 1) * 60, receipt: "EVAL" });
}

assert.strictEqual(classify([50, 50]).family, "SLEEPER");
assert.strictEqual(classify([50, 52, 54, 52, 50]).family, "QUIET_WOBBLE");
assert.strictEqual(classify([50, 60, 50, 60, 50]).family, "ROUND_TRIP");
assert.ok(policy.FAMILY_ORDER.includes(classify([50, 49, 48, 47, 46, 45]).family));
const down = classify([50, 49, 48, 47, 46, 45]);
assert.ok(down.family.endsWith("_DOWN"));
assert.strictEqual(down.causal, true);
assert.strictEqual(down.right_edge_consumed, false);
assert.strictEqual(down.full_span_fit, false);
assert.ok(down.maximum_consumed_timestamp_epoch <= down.evaluation_timestamp_epoch);
assert.strictEqual(policy.FAMILY_ORDER.length, 13);
assert.strictEqual(policy.tableRowFor("DRIFT_DOWN", "NO_CELL").borrowed_from, "DRIFT_DOWN|ALL");
assert.strictEqual(policy.ABSTAIN_FAMILIES.has("SLEEPER"), true);
assert.strictEqual(policy.ABSTAIN_FAMILIES.has("DRIFT_DOWN"), false);
const replaced = policy.incumbentWithSelectedTarget(
  { target_cents: 46, reason: "V43_TRACKER", placement: { target_cents: 46, authority: "V43_TRACKER" }, unguarded_decision: { target_cents: 46, placement: { target_cents: 46 } } },
  { selected_target_cents: 85 },
);
assert.strictEqual(replaced.target_cents, 85);
assert.strictEqual(replaced.placement.target_cents, 85);
assert.strictEqual(Object.prototype.hasOwnProperty.call(replaced, "unguarded_decision"), false);
assert.strictEqual(replaced.reason, "V43_TRACKER");
assert.strictEqual(replaced.placement.authority, "V43_TRACKER");

process.stdout.write(`${JSON.stringify({ assertions: 18, failures: 0, causal: true, families: 13, stale_unguarded_pointer_removed: true, incumbent_signer_preserved: true })}\n`);
