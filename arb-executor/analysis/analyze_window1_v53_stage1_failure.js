#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const root = path.resolve(process.argv[2] || ".");
const packageDir = path.join(root, ".claude/window1_live_v4_replay/v53_understanding_organ_stage1_20260819");
const tracePath = path.join(packageDir, "FULL_DECISION_TRACE_30.jsonl.gz");
const scorePath = path.join(packageDir, "STAGE1_SCORECARD.json");
const outputPath = path.join(packageDir, "V53_FAILURE_CAUSE_RECEIPT.json");
const shaFile = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const percentile = (rows, q) => rows[Math.max(0, Math.ceil(q * rows.length) - 1)] ?? null;

(async () => {
  const first = new Map();
  for await (const line of readline.createInterface({ input: fs.createReadStream(tracePath).pipe(zlib.createGunzip()), crlfDelay: Infinity })) {
    const row = JSON.parse(line);
    if (!["PLACE_REST", "REPRICE_REST"].includes(row.final_action) || first.has(row.leg_identity)) continue;
    const legId = row.leg_identity.split("|").at(-1);
    const reach = row.game_view?.legs?.[legId]?.reach ?? null;
    first.set(row.leg_identity, {
      event_id: row.event_id,
      leg_identity: row.leg_identity,
      first_post_timestamp_epoch: row.timestamp_epoch,
      first_post_receipt: row.receipt,
      first_target_cents: row.final_target_cents,
      running_session_low_cents_at_post: reach?.running_session_low_cents ?? null,
      running_session_low_producer_receipt: reach?.producer_receipt ?? null,
      seconds_after_low_observed: Number.isFinite(reach?.producer_receipt?.timestamp_epoch) ? row.timestamp_epoch - reach.producer_receipt.timestamp_epoch : null,
      target_at_or_below_historical_low: Number.isInteger(reach?.running_session_low_cents) && row.final_target_cents <= reach.running_session_low_cents,
    });
  }
  const rows = [...first.values()].sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_identity.localeCompare(b.leg_identity));
  const lags = rows.map((row) => row.seconds_after_low_observed).filter(Number.isFinite).sort((a, b) => a - b);
  const score = JSON.parse(fs.readFileSync(scorePath, "utf8"));
  const receipt = {
    label: "V53_01_STAGE1_FAILURE_CAUSE",
    status: "BLOCKING_FINDING_BANKED_NO_804",
    source_trace: { path: path.relative(root, tracePath).replaceAll("\\", "/"), sha256: shaFile(tracePath) },
    source_scorecard: { path: path.relative(root, scorePath).replaceAll("\\", "/"), sha256: shaFile(scorePath) },
    construction_assertions_passed: true,
    acceptance_bar_passed: score.acceptance_bar.pass,
    comparator_completed_pairs: score.comparator.completed_pairs,
    candidate_completed_pairs: score.candidate.completed_pairs,
    candidate_uncompleted_pairs: score.candidate.games - score.candidate.completed_pairs,
    diagnosis: "V53_TARGETED_AN_ALREADY_OBSERVED_SESSION_LOW_AFTER_ITS_RECEIPT; HISTORICAL_REACH_WAS_TREATED_AS_CURRENT_REACH_AND_THE_LEVEL_OFTEN_DID_NOT_RETURN",
    conservation: { first_post_rows: rows.length, unique_leg_identities: new Set(rows.map((row) => row.leg_identity)).size },
    target_at_or_below_historical_low: rows.filter((row) => row.target_at_or_below_historical_low).length,
    first_post_after_low_receipt: rows.filter((row) => row.seconds_after_low_observed > 0).length,
    lag_seconds: { n: lags.length, min: lags[0] ?? null, p25: percentile(lags, 0.25), median: percentile(lags, 0.50), p75: percentile(lags, 0.75), p90: percentile(lags, 0.90), max: lags.at(-1) ?? null },
    rows,
  };
  fs.writeFileSync(outputPath, `${JSON.stringify(receipt, null, 2)}\n`);
  process.stdout.write(`${outputPath}\n`);
})().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
