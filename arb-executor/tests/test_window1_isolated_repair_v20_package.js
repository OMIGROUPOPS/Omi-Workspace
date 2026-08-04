"use strict";

const assert = require("assert"), fs = require("fs"), path = require("path"), zlib = require("zlib");
const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay");
function json(file) { return JSON.parse(fs.readFileSync(file)); }
function rows(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse); }
function test(name, fn) { try { fn(); process.stdout.write(`PASS ${name}\n`); } catch (error) { process.stderr.write(`FAIL ${name}: ${error.stack}\n`); process.exitCode = 1; } }

const a = path.join(root, "isolated_fix_a_anchor_freshness_v20_20260804");
const c = path.join(root, "isolated_fix_c_shape_settlement_v20_20260804");

for (const [name, dir] of [["FIX_A", a], ["FIX_C", c]]) {
  test(`${name} preserves D=804 and V19 JOINT floor`, () => {
    const comparison = json(path.join(dir, "V19_NON_REGRESSION_COMPARISON.json"));
    assert.strictEqual(comparison.V19.D, 804);
    assert.strictEqual(comparison.V19.joint_objective_pairs, 19);
    assert.ok(comparison.isolated_variant.joint_objective_pairs >= 19);
    assert.strictEqual(comparison.V19_floor_pass, true);
  });
  test(`${name} is isolated and every addition has its exact receipt`, () => {
    const receipt = json(path.join(dir, "CAUSAL_ADDITION_RECEIPT.json"));
    assert.strictEqual(receipt.stacking, false);
    assert.strictEqual(receipt.source_receipts_complete, true);
    const ledger = rows(path.join(dir, "POPULATION_LEG_LEDGER.jsonl.gz"));
    assert.strictEqual(ledger.length, 1608);
    assert.strictEqual(ledger.filter((row) => row.isolated_repair_added).length, receipt.added_legs);
    assert.ok(ledger.filter((row) => row.isolated_repair_added).every((row) => row.isolated_repair_receipt));
  });
  test(`${name} frontier and regret preserve partition denominators`, () => {
    const frontier = json(path.join(dir, "FRONTIER.json"));
    const regret = json(path.join(dir, "REGRET_GAUGE.json"));
    assert.strictEqual(frontier.fixed_denominator, 804);
    assert.strictEqual(frontier.category_and_starting_price_region.reduce((sum, row) => sum + row.D, 0), 804);
    assert.strictEqual(regret.denominator_legs, 1608);
    assert.strictEqual(regret.numeric_completed_regret.denominator, 1608);
  });
}

test("Fix A improves JOINT and Fix C does not regress it", () => {
  const ac = json(path.join(a, "V19_NON_REGRESSION_COMPARISON.json"));
  const cc = json(path.join(c, "V19_NON_REGRESSION_COMPARISON.json"));
  assert.deepStrictEqual([ac.V19.joint_objective_pairs, ac.isolated_variant.joint_objective_pairs], [19, 27]);
  assert.deepStrictEqual([cc.V19.joint_objective_pairs, cc.isolated_variant.joint_objective_pairs], [19, 19]);
});

test("sibling source is its own book and contains no 100-p mirror", () => {
  const receipt = json(path.join(root, "sibling_source_read_20260804/SIBLING_SOURCE_RECEIPT.json"));
  assert.strictEqual(receipt.conclusion, "FALSE; THEORY_DIES; NO_FIX_B_BUILT");
  assert.strictEqual(receipt.mirror_expression_found, false);
  const source = fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_quote_shape_micro_position_v2.js"), "utf8");
  assert.match(source, /directionObserved\(sibling, sibling\.independent_direction\)/);
  assert.doesNotMatch(source, /100\s*-\s*p/);
});

test("WTA_MAIN death trace conserves 152 events and has zero JOINT", () => {
  const census = json(path.join(root, "wta_main_v19_death_trace_20260804/WTA_MAIN_DEATH_CENSUS.json"));
  assert.strictEqual(census.D, 152);
  assert.strictEqual(census.conservation, 152);
  assert.strictEqual(census.joint_objective_pairs, 0);
  assert.strictEqual(census.category_and_starting_price_region.reduce((sum, row) => sum + row.D, 0), 152);
});

if (process.exitCode) process.exit(process.exitCode);
