#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/naked_leg_disposition_v23_vs_a_20260804");
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
const ledger = () => zlib.gunzipSync(fs.readFileSync(path.join(dir, "NAKED_LEG_DISPOSITION_LEDGER.jsonl.gz"))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);

assert.ok(fs.existsSync(dir), "frozen census package missing");
const conservation = read("CONSERVATION_RECEIPT.json");
assert.deepStrictEqual(conservation.V23, { credited_legs: 920, legs_in_completed_pairs: 408, naked_credited_legs: 512, equation: "408+512=920", pass: true });
assert.deepStrictEqual(conservation.A_V20, { credited_legs: 1187, legs_in_completed_pairs: 942, naked_credited_legs: 245, equation: "942+245=1187", pass: true });
assert.strictEqual(conservation.disposition_rows, 757);
assert.strictEqual(conservation.exactly_one_disposition_row_per_naked_leg, true);
assert.deepStrictEqual(conservation.origin_class_counts.V23_PAIR_CAP_IMMEDIATE, { NEVER_COMPLETED_SIBLING: 352, CAP_ABSTENTION_SIBLING: 160 });

const rows = ledger();
assert.strictEqual(rows.length, 757);
assert.strictEqual(new Set(rows.map((x) => `${x.variant}|${x.leg_identity}`)).size, 757);
assert.ok(rows.every((x) => ["CAP_ABSTENTION_SIBLING", "NEVER_COMPLETED_SIBLING"].includes(x.origin_class)));
assert.ok(rows.every((x) => x.band_touch_law.includes("TRUE_PUBLIC_PRINT")));
assert.ok(rows.every((x) => x.band_target_cents === Math.min(98, x.entry_cents + x.band_x_cents)));
assert.ok(rows.every((x) => !x.band_touched || x.first_band_touch.price_cents >= x.band_target_cents));

const bands = read("BAND_AUTHORITY_RECEIPT.json");
assert.strictEqual(bands.status, "BOUND");
assert.strictEqual(bands.invented_band_or_touch_rule, false);
assert.strictEqual(bands.hold_cells, 0);
assert.ok(Object.values(bands.machine_readable_surfaces).every((x) => x.cells === 90));

const distributions = read("DISPOSITION_DISTRIBUTIONS.json");
assert.strictEqual(distributions.variants.V23_PAIR_CAP_IMMEDIATE.aggregate.legs, 512);
assert.strictEqual(distributions.variants.A_V20.aggregate.legs, 245);
assert.strictEqual(distributions.net_answer.full_V23_naked_book_sign, "UNRESOLVED_POST_FILL_EDGE_MARK_UNAVAILABLE");
assert.strictEqual(distributions.net_answer.no_imputation, true);

console.log("PASS test_window1_naked_leg_disposition_v23");
