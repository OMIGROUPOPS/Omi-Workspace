#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { resolveQuietBookAnchor } = require("../analysis/nikvrb_sibling_shape_cold_replay.js");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_live_book_breathing_20260731");
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));

const run = child.spawnSync(
  process.execPath,
  ["arb-executor/analysis/build_nikvrb_live_book_breathing_reference.js", ".", "--check"],
  { cwd: repo, encoding: "utf8" }
);
assert.strictEqual(run.status, 0, run.stderr || run.stdout);
const build = JSON.parse(run.stdout);
assert.strictEqual(build.status, "CHECK_PASS");
assert.strictEqual(build.source_rows, 13123);
assert.strictEqual(build.decision_rows, 26244);
assert.deepStrictEqual(build.current, { NIK: 21, VRB: 69 });
assert.deepStrictEqual(build.corrected, { NIK: 19, VRB: 68 });

const summary = readJson("REPLAY_SUMMARY.json");
const audit = readJson("CODE_PATH_AUDIT.json");
const orders = readJson("CORRECTED_ORDER_INTERVALS.json");
const decisions = readJson("CORRECTED_MATERIAL_DECISIONS.json");
const packedRows = readJson("ARITHMETIC_DECISION_ROWS.json");
const rows = JSON.parse(zlib.gunzipSync(Buffer.from(packedRows.gzip_base64, "base64")).toString("utf8"));
assert.strictEqual(packedRows.row_count, 26244);
assert.strictEqual(summary.population_run, false);
assert.strictEqual(summary.live_execution, false);
assert.strictEqual(summary.external_sharp_receipts_on_specimen, 0);
assert.strictEqual(summary.quiet_anchors.VRB.anchor_cents, 68);
assert.strictEqual(summary.quiet_anchors.VRB.raw_anchor_cents, 67.5);
assert.strictEqual(summary.quiet_anchors.VRB.sequence, 256);
assert.strictEqual(summary.acceptance.VRB_fill_68_or_better, true);
assert.strictEqual(summary.acceptance.NIK_fill_at_live_touch_19, true);

const vrb67 = orders.find((row) => row.leg === "VRB" && row.price === 67);
const vrb68 = orders.find((row) => row.leg === "VRB" && row.price === 68);
assert.strictEqual(vrb67.action_sequence, 256);
assert.strictEqual(vrb67.end_sequence, 278);
assert.strictEqual(vrb68.action_sequence, 278);
assert.strictEqual(vrb68.end_sequence, 326);
assert.strictEqual(vrb68.end_reason, "FILLED_ACTIVE_ASK_LIFT_CONFIRMATION");
const arm = decisions.find((row) => row.action === "ARM_VRB_ASK_LIFT_68");
const vrbFill = decisions.find((row) => row.action === "CREDIT_VRB_FILL_68");
assert.strictEqual(arm.sequence, 325);
assert.strictEqual(vrbFill.sequence, 326);
assert.ok(vrbFill.sequence > arm.sequence);
assert.ok(vrbFill.timestamp_et > arm.timestamp_et);

const nikRelease = decisions.find((row) => row.action === "PLACE_NIK_19");
const nikFill = decisions.find((row) => row.action === "CREDIT_NIK_FILL_19");
assert.strictEqual(nikRelease.sequence, 2975);
assert.strictEqual(nikFill.sequence, 3361);
assert.ok(nikFill.sequence > nikRelease.sequence);
const correctedNik = rows.filter((row) => row.branch === "corrected" && row.leg === "NIK"
  && row.what_fired.startsWith("LIVE_BOOK_TOUCH") && row.order_after !== null);
assert.ok(correctedNik.length > 0);
assert.ok(correctedNik.every((row) => row.order_after <= row.best_bid));
assert.ok(rows.some((row) => row.branch === "current" && row.leg === "NIK"
  && row.order_after === 21 && row.best_bid === 19));
assert.ok(rows.some((row) => row.branch === "current" && row.leg === "VRB"
  && row.order_before === 69 && row.best_ask === 68));
assert.ok(rows.every((row) => row.input_value && row.operation && "output_value" in row));

assert.strictEqual(audit.fv_anchor_placement_config, false);
assert.strictEqual(audit.exact_gate.actual_source.includes("true-print"), true);
assert.deepStrictEqual(audit.exact_gate.not_sources, ["Pinnacle", "Betfair", "Matchbook", "own BBO"]);
assert.strictEqual(audit.external_sharp_path.specimen_result.includes("own lawful 67/68 BBO"), true);
assert.strictEqual(audit.stale_order_paths.length, 6);

const external = resolveQuietBookAnchor({
  book: { bid: 67, ask: 68 },
  externalSharp: {
    sources: ["matchbook", "pinnacle", "betfair_ex_eu"],
    fv_cents: 68.25,
    age_seconds: 15,
    receipts: ["p", "b", "m"],
  },
});
assert.strictEqual(external.anchor_cents, 68);
assert.strictEqual(external.source, "EXTERNAL_SHARP_BLEND__PINNACLE_BETFAIR_MATCHBOOK");
const incompleteExternal = resolveQuietBookAnchor({
  book: { bid: 67, ask: 68 },
  externalSharp: { sources: ["pinnacle"], fv_cents: 72, age_seconds: 15 },
});
assert.strictEqual(incompleteExternal.anchor_cents, 68);
assert.strictEqual(incompleteExternal.source, "OWN_LAWFUL_BBO_MID");
assert.strictEqual(resolveQuietBookAnchor({ book: { bid: 67, ask: 75 } }), null);

const html = fs.readFileSync(
  path.join(repo, "arb-executor/docs/research/window1/NIKVRB_LIVE_BOOK_BREATHING_TABLE_CHARTS.html"), "utf8"
);
for (const token of ["chart('current',leg)", "chart('corrected',leg)",
  "input value", "operation", "order before", "order after"]) assert.ok(html.includes(token));
const htmlPayloadMatch = html.match(/const DATA_GZIP_BASE64="([A-Za-z0-9+/=]+)"/);
assert.ok(htmlPayloadMatch);
const htmlPayload = JSON.parse(zlib.gunzipSync(Buffer.from(htmlPayloadMatch[1], "base64")).toString("utf8"));
assert.strictEqual(htmlPayload.rows.length, 26244);
assert.strictEqual(htmlPayload.series.corrected.VRB.length, 13122);
assert.strictEqual(htmlPayload.series.corrected.NIK.length, 13122);
const forbidden = readJson("FORBIDDEN_ACCESS_RECEIPT.json");
assert.ok(Object.values(forbidden).filter((value) => typeof value === "boolean").every((value) => value === false));
const liveHash = crypto.createHash("sha256").update(fs.readFileSync(path.join(repo, "arb-executor/live_v4.py"))).digest("hex");
assert.strictEqual(liveHash, "f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760");

process.stdout.write("PASS test_nikvrb_live_book_breathing_replay (focused assertions; one cold game; no population/live execution)\n");
