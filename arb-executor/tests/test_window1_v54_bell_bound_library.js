"use strict";

const assert = require("assert/strict");
const bell = require("../analysis/window1_v54_bell_bound_library.js");

const bindings = {
  analysis_commit: "15955e44",
  actual_bell_path: "ACTUAL.json",
  named_neighbor_path: "NEIGHBOR.json",
  range_receipt: "range#row-1",
};
const authorities = bell.buildAuthorities({
  actualBellTable: {
    "26JUL12AAAEEE": { source: "MACHINE_RECEIPT", bell_epoch: 125 },
    "26APR01BBBFFF": { source: "BELL_UNRESOLVED", bell_epoch: null },
  },
  namedNeighborCheck: {
    neighbors: [{ neighbor: "KXATPMATCH-26MAY01CCCDDD", inplay_signature_epoch: 115, legs: { CCC: { prebell_low_by_signature: 39 }, DDD: { prebell_low_by_signature: 59 } } }],
  },
  bindings,
});

const ticks = (prices) => prices.map(([timestamp, price]) => [timestamp, price - 1, price + 1, price]);
const official = bell.rematerializeRangeRow({
  event: "KXATPMATCH-26JUL12AAAEEE", cat: "ATP_MAIN", edge_src: "onset_snapshot_est", right_edge: 999,
  legs: { AAA: { anchor: 40, low: 1, close: 2, ticks: ticks([[100, 40], [120, 38], [130, 1]]) }, EEE: { anchor: 60, low: 1, close: 99, ticks: ticks([[100, 60], [120, 62], [130, 99]]) } },
}, authorities, "range#row-2");
assert.equal(official.span.method, "OFFICIAL_ACTUAL_MACHINE_RECEIPT");
assert.equal(official.legs.find((row) => row.leg_id === "AAA").low_cents, 38);
assert.equal(official.legs.find((row) => row.leg_id === "EEE").close_cents, 62);

const named = bell.rematerializeRangeRow({
  event: "KXATPMATCH-26MAY01CCCDDD", cat: "ATP_MAIN", edge_src: "onset_snapshot_est", right_edge: 999,
  legs: { CCC: { anchor: 40, low: 1, close: 1, ticks: ticks([[100, 40], [110, 39], [115, 1]]) }, DDD: { anchor: 60, low: 1, close: 99, ticks: ticks([[100, 60], [110, 59], [115, 99]]) } },
}, authorities, "range#row-3");
assert.equal(named.span.method, "IN_PLAY_SIGNATURE_NAMED_NEIGHBOR_FVS050");
assert.equal(named.legs.find((row) => row.leg_id === "CCC").low_cents, 39);
assert.equal(named.legs.find((row) => row.leg_id === "DDD").low_cents, 59);

const unbounded = bell.rematerializeRangeRow({
  event: "KXATPMATCH-26APR01BBBFFF", cat: "ATP_MAIN", edge_src: "onset_snapshot_est", right_edge: 999,
  legs: { BBB: { anchor: 40, low: 1, ticks: ticks([[100, 40], [130, 1]]) }, FFF: { anchor: 60, low: 1, ticks: ticks([[100, 60], [130, 99]]) } },
}, authorities, "range#row-4");
assert.equal(unbounded.span.status, "UNBOUNDED");
assert.equal(unbounded.legs[0].low_cents, null);
assert.equal(unbounded.vector.leg0_travel_cents, null);
assert.notEqual(unbounded.span.right_edge_epoch, 0, "null bell may never coerce to epoch zero");

console.log("window1_v54_bell_bound_library: PASS");
