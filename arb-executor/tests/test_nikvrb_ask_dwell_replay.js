#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_ask_dwell_20260731");
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));

const run = child.spawnSync(
  process.execPath,
  ["arb-executor/analysis/build_nikvrb_ask_dwell_reference.js", ".", "--check"],
  { cwd: repo, encoding: "utf8" }
);
assert.strictEqual(run.status, 0, run.stderr || run.stdout);
const build = JSON.parse(run.stdout);
assert.deepStrictEqual(build.corrected_fills, { NIK: 18, VRB: 68 });
assert.strictEqual(build.ask_episodes, 154734);
assert.strictEqual(build.prior_598, 598);
assert.strictEqual(build.corrected_ask_only, 532);

const summary = readJson("REPLAY_SUMMARY.json");
const decisions = readJson("CORRECTED_MATERIAL_DECISIONS.json");
const orders = readJson("CORRECTED_ORDER_INTERVALS.json");
const corpus = readJson("ASK_ONLY_DIVOT_DWELL_CENSUS.json");
const opportunity = readJson("ASK_ONLY_OPPORTUNITY_RECONCILIATION.json");
const midwindow = readJson("NIK_MIDWINDOW_ASK_AUTHORITY_RECEIPT.json");
const capacityAbsent = readJson("EVIDENCE_ABSENT_CAPACITY_RECEIPT.json");
const referencePanel = readJson("REFERENCE_PANEL.json");
const packedRows = readJson("ARITHMETIC_DECISION_ROWS.json");
const rows = JSON.parse(zlib.gunzipSync(Buffer.from(packedRows.gzip_base64, "base64")));

assert.strictEqual(summary.threshold_seconds, 10);
assert.strictEqual(summary.reachability_side, "ask_only");
assert.strictEqual(summary.bid_side_entry_authority, false);
assert.deepStrictEqual(summary.prior_fills, { NIK: 19, VRB: 68 });
assert.deepStrictEqual(summary.corrected_fills, { NIK: 18, VRB: 68 });
assert.strictEqual(summary.independent_pair_reference, "NOT_BOUND");
assert.strictEqual(summary.evidence_absent_count, 0);
assert.ok(Object.values(summary.acceptance).every(Boolean));
assert.strictEqual(capacityAbsent.count, 0);
assert.strictEqual(referencePanel.pair_reference_cents, "NOT_BOUND");
assert.strictEqual(referencePanel.delta_to_pair_reference_cents, "NOT_BOUND");
assert.deepStrictEqual(referencePanel.legs.NIK, {
  entry_cents: 18,
  own_window1_close_cents: 19,
  delta_to_own_window1_close_cents: -1,
  own_bell_price_cents: 19,
  delta_to_own_bell_price_cents: -1,
  own_ask_reachable_low_cents: 18,
  delta_to_own_ask_reachable_low_cents: 0,
});

const vrb68 = orders.find((row) => row.leg === "VRB" && row.price === 68);
const vrbFill = decisions.find((row) => row.action === "CREDIT_VRB_FILL_68");
assert.strictEqual(vrb68.action_sequence, 263);
assert.strictEqual(vrbFill.sequence, 326);
assert.strictEqual(vrbFill.arithmetic, "ask 68 <= resting 68; dwell 32>=10; displayed capacity 110>=5; credit 5@68");
assert.strictEqual(vrbFill.joint_observation.VRB.ask_size, 110);
assert.ok(vrbFill.sequence > vrb68.action_sequence);

const nik18 = orders.find((row) => row.leg === "NIK" && row.price === 18);
const nikPlace = decisions.find((row) => row.action === "PLACE_NIK_18");
const nikFill = decisions.find((row) => row.action === "CREDIT_NIK_FILL_18");
assert.strictEqual(nik18.action_sequence, 3433);
assert.strictEqual(nikPlace.arithmetic, "arm ask 29-current ask 19=10>=5; dwell 11>=10; ask-1=18");
assert.strictEqual(nikFill.sequence, 4250);
assert.strictEqual(nikFill.arithmetic, "ask 18 <= resting 18; dwell 11>=10; displayed capacity 86>=5; credit 5@18");
assert.strictEqual(nikFill.joint_observation.NIK.ask_size, 86);
assert.ok(nikFill.sequence > nik18.action_sequence);

const patience = decisions.find((row) => row.organ === "SIBLING_REALIZED_SHAPE");
assert.strictEqual(patience.arithmetic, "VRB ask recurrences 66>0; VRB bid 73>fill 68; cancel 21->EMPTY");
assert.ok(patience.english.includes("66 completed ask-side quote recurrences"));
assert.ok(!patience.english.includes("97 completed"));

assert.deepStrictEqual(midwindow.ask_values, [29]);
assert.deepStrictEqual(midwindow.last_trade_values, [28]);
assert.strictEqual(midwindow.source_clock_rows, 910);
assert.strictEqual(midwindow.NIK_BBO_receipts, 841);
assert.strictEqual(midwindow.bid_changes, 240);
assert.strictEqual(midwindow.true_print_receipts, 0);
assert.strictEqual(corpus.nik_midwindow.bid_side_episodes, 63);
assert.strictEqual(corpus.nik_midwindow.ask_side_episodes, 0);
assert.deepStrictEqual(corpus.nik_midwindow.bid_dwell_counts, { "0": 59, "1": 2, "13": 1, "25": 1 });
assert.strictEqual(decisions.filter((row) => row.leg === "NIK" && row.sequence >= 1700 && row.sequence <= 2703
  && ["LIVE_ASK_TOUCH", "ASK_DWELL_PATIENCE_RELEASE"].includes(row.organ)).length, 0);

assert.strictEqual(corpus.source_episode_rows, 392282);
assert.deepStrictEqual(corpus.total, { episodes: 154734, unique_events: 583, unique_legs: 981 });
assert.strictEqual(corpus.dwell_bands.ZERO_SECONDS.episodes, 74391);
assert.strictEqual(corpus.dwell_bands.ONE_TO_NINE_SECONDS.episodes, 69363);
assert.strictEqual(corpus.dwell_bands.TEN_TO_TWENTY_NINE_SECONDS.episodes, 3785);
assert.strictEqual(corpus.dwell_bands.THIRTY_TO_FIFTY_NINE_SECONDS.episodes, 2646);
assert.strictEqual(corpus.dwell_bands.SIXTY_TO_299_SECONDS.episodes, 1799);
assert.strictEqual(corpus.dwell_bands.AT_LEAST_300_SECONDS.episodes, 2750);
assert.deepStrictEqual(corpus.at_or_above_thresholds["10_seconds"], { episodes: 10980, unique_events: 573, unique_legs: 952 });

assert.strictEqual(opportunity.primary_prior_denominator, 598);
assert.strictEqual(opportunity.primary_corrected_denominator, 532);
assert.strictEqual(opportunity.threshold_rows["10_seconds"].removed_count, 66);
assert.strictEqual(opportunity.threshold_rows["30_seconds"].corrected_ask_only_negative_pair_opportunities, 531);
assert.strictEqual(opportunity.threshold_rows["60_seconds"].corrected_ask_only_negative_pair_opportunities, 525);
assert.strictEqual(opportunity.threshold_rows["300_seconds"].corrected_ask_only_negative_pair_opportunities, 503);

assert.ok(rows.length > 26000);
assert.ok(rows.every((row) => row.input_value && row.operation && Object.hasOwn(row, "output_value")));
const html = fs.readFileSync(path.join(repo, "arb-executor/docs/research/window1/NIKVRB_ASK_DWELL_TABLE_CHARTS.html"), "utf8");
for (const token of ["prior_bid_reactive", "corrected_ask_dwell", "best bid", "best ask", "last traded", "our resting bid"]) assert.ok(html.includes(token));
assert.strictEqual((html.match(/chart\(b,l\)/g) || []).length, 1);

const forbidden = readJson("FORBIDDEN_ACCESS_RECEIPT.json");
assert.ok(Object.values(forbidden).filter((value) => typeof value === "boolean").every((value) => value === false));
const liveHash = crypto.createHash("sha256").update(fs.readFileSync(path.join(repo, "arb-executor/live_v4.py"))).digest("hex");
assert.strictEqual(liveHash, "f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760");

process.stdout.write("PASS test_nikvrb_ask_dwell_replay (ask-only dwell replay; descriptive corpus recut; no live/population scoring)\n");
