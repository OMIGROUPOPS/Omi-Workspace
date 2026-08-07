"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../..");
const pack = path.join(root, ".claude/window1_live_v4_replay/v38_maker_only_machine_20260807");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pack, name), "utf8"));
let tests = 0;
function test(name, fn) { fn(); tests += 1; process.stdout.write(`ok - ${name}\n`); }

test("package exists and take deletion passes", () => {
  assert(fs.statSync(pack).isDirectory());
  const receipt = read("TAKE_PATH_DELETION_RECEIPT.json");
  assert.strictEqual(receipt.forbidden_action_literal_TAKE_count, 0);
  assert.strictEqual(receipt.take_named_function_count, 0);
  assert.strictEqual(receipt.pass, true);
});

test("market answer key conserves 637 games and 5253 cents", () => {
  const score = read("MARKET_GRADE_SCORECARD.json");
  assert.strictEqual(score.reach_grade.answer_key_games, 637);
  assert.strictEqual(score.reach_grade.answer_key_locked_cents, 5253);
});

test("strict ruler is labeled build verification only", () => {
  assert.strictEqual(read("STRICT_BUILD_VERIFICATION_SCORECARD.json").role, "BUILD_VERIFICATION_ONLY_NOT_MARKET_VALUE");
});

test("category and bell-confidence partition conserves", () => {
  const cells = read("CATEGORY_X_BELL_CONFIDENCE.json");
  assert.strictEqual(cells.conservation.pass, true);
});

test("all residual sides have exactly one layer owner", () => {
  const bind = read("LAYER_BIND_RANKING.json");
  assert.strictEqual(bind.conservation.pass, true);
});

test("named reach identities remain frozen", () => {
  const named = read("NAMED_GAMES.json").games;
  assert.strictEqual(named.ARNROM.reach_combined_cents, 88);
  assert.strictEqual(named.BOSCOP.reach_combined_cents, 75);
  assert.strictEqual(named.NIKVRB.reach_combined_cents, 86);
  assert(named.GANJAN);
});

test("forbidden access receipt is zero", () => {
  const receipt = read("FORBIDDEN_ACCESS_RECEIPT.json");
  for (const [key, value] of Object.entries(receipt)) if (key.endsWith("_accesses") || key === "mutations") assert.strictEqual(value, 0, key);
});

test("determinism and manifest pass", () => {
  assert.strictEqual(read("DETERMINISM_RECEIPT.json").byte_identical, true);
  assert(Object.keys(read("ARTIFACT_HASH_MANIFEST.json").files).length >= 18);
});

process.stdout.write(`${tests} tests passed\n`);
