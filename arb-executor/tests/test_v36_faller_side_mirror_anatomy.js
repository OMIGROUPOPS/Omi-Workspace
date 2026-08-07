#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const crypto = require("crypto");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v36_faller_side_mirror_anatomy_20260807");
const read = name => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const rows = name => zlib.gunzipSync(fs.readFileSync(path.join(root, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const tests = [];
const test = (name, fn) => { fn(); tests.push(name); process.stdout.write(`ok - ${name}\n`); };

test("population conserves 511 V36-FALLING sides and 399 issues", () => {
  const s = read("FALLER_POPULATION_AND_TAXONOMY.json");
  assert.strictEqual(s.population.faller_sides_with_union_reach, 511);
  assert.strictEqual(s.population.issue_sides, 399);
  assert.strictEqual(s.population.captured_controls, 112);
  assert.strictEqual(s.population.measured_issue_cents, 1567);
});

test("every issue side has one taxonomy", () => {
  const issue = rows("FALLER_ISSUE_ANATOMY_399.jsonl.gz");
  assert.strictEqual(issue.length, 399);
  assert(issue.every(r => r.miss_taxonomy && r.miss_taxonomy.class));
  assert.strictEqual(new Set(issue.map(r => r.ticker)).size, 399);
});

test("candidate slate contains both books and both pressure reads", () => {
  const all = rows("FALLER_SIDE_ANATOMY_511.jsonl.gz");
  assert.strictEqual(all.length, 511);
  for (const row of all) {
    assert(Object.hasOwn(row.signals, "own_pressure_state"));
    assert(Object.hasOwn(row.signals, "sibling_pressure_state"));
    assert(Object.hasOwn(row.signals, "own_spread_dwell"));
    assert(Object.hasOwn(row.signals, "sibling_spread_dwell"));
    assert(Object.hasOwn(row.signals, "pair_cap_room"));
  }
});

test("lift reports category and category x price region", () => {
  const lift = read("CANDIDATE_SIGNAL_LIFT.json");
  assert(lift.category_rows.length > 0);
  assert(lift.category_x_price_region_rows.length > 0);
  assert(lift.category_x_price_region_rows.every(r => Object.hasOwn(r.group_keys, "price_region")));
});

test("named GANJAN KRALOR WESPAA rows exist", () => {
  const named = read("NAMED_GAMES.json");
  for (const key of ["GANJAN", "KRALOR", "WESPAA"]) {
    assert.strictEqual(named[key].finding, "FALLER_SIDE_FOUND");
    assert(named[key].rows.length >= 1);
  }
});

test("full trace reconstruction is exact", () => {
  const receipt = read("TRACE_RECONSTRUCTION_RECEIPT.json");
  assert.strictEqual(receipt.full_trace_rows_parsed, 3631920);
  assert.deepStrictEqual(receipt.snapshot_reconstruction_mismatches, []);
});

test("forbidden accesses and mutations are zero", () => {
  const receipt = read("FORBIDDEN_ACCESS_RECEIPT.json");
  for (const [key, value] of Object.entries(receipt)) if (key !== "scope") assert.strictEqual(value, 0, key);
});

test("two clean builds are byte-identical", () => {
  const receipt = read("DETERMINISM_RECEIPT.json");
  assert.strictEqual(receipt.byte_identical, true);
  assert.deepStrictEqual(receipt.mismatches, []);
});

test("artifact manifest verifies", () => {
  const manifest = read("ARTIFACT_HASH_MANIFEST.json");
  for (const row of manifest.files) {
    const file = path.join(root, row.path);
    const hash = crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
    assert.strictEqual(hash, row.sha256, row.path);
    assert.strictEqual(fs.statSync(file).size, row.bytes, row.path);
  }
});

process.stdout.write(`${tests.length} tests passed\n`);
