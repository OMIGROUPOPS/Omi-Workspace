#!/usr/bin/env node
"use strict";

// Receipt-level maker/taker addendum for the four five-game replay credits.
// This is diagnostic only: no order is sent and no fill is reassigned.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const arg = (name, fallback) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
};
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_role_addendum_20260801")));
const replayPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/FIVE_GAME_REPLAY.json");
const summaryPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/FIVE_GAME_SUMMARY.json");
const frozenFivePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const v1AuditPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_insufficient_diagnosis_20260801/MAKER_TAKER_FILL_AUDIT.json");
const replayBuilderPath = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
const livePath = path.join(repo, "arb-executor/live_v4.py");
const DWELL_SECONDS = 10;
const QUANTITY = 5;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) throw new Error(`bad timestamp ${value}`);
  let hour = Number(match[4]);
  if (match[7] === "AM" && hour === 12) hour = 0;
  if (match[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map((line, index) => ({ raw: Object.fromEntries(line.split(",").map((value, column) => [headers[column], value])), ordinal: index + 2 }));
}
function clocks(ts, source) {
  return { timestamp_epoch: ts, t_minus_scheduled_seconds: source.scheduled - ts, t_minus_actual_bell_seconds: source.bell - ts };
}
function tMinus(seconds) {
  const sign = seconds >= 0 ? "T-" : "T+";
  const value = Math.abs(seconds);
  return `${sign}${Math.floor(value / 60)}:${String(value % 60).padStart(2, "0")}`;
}
function receiptOrdinal(receipt) {
  const match = String(receipt).match(/#row-(\d+)/);
  if (!match) throw new Error(`receipt lacks row ordinal: ${receipt}`);
  return Number(match[1]);
}

function loadRows(source) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  const bytes = fs.readFileSync(file);
  const rows = [];
  for (const { raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et);
    if (ts < source.left || ts > source.right) continue;
    const bids = [];
    const asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(raw[`bid_${level}`]);
      const bidSize = positive(raw[`bid_${level}_sz`]);
      const ask = integer(raw[`ask_${level}`]);
      const askSize = positive(raw[`ask_${level}_sz`]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]);
      if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    bids.sort((a, b) => b[0] - a[0]);
    asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({
      ts,
      ordinal,
      receipt: `${path.basename(file)}#row-${ordinal}`,
      bid: bids[0][0],
      ask: asks[0][0],
      last: integer(raw.last_trade),
      spread: asks[0][0] - bids[0][0],
      bids,
      asks,
      displayed_bid_size: bids[0][1],
      displayed_ask_size: asks[0][1],
      top_five_bid_depth: bids.reduce((sum, row) => sum + row[1], 0),
      top_five_ask_depth: asks.reduce((sum, row) => sum + row[1], 0),
    });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null;
  let askSince = null;
  for (const row of rows) {
    if (row.ask !== ask) { ask = row.ask; askSince = row.ts; }
    row.ask_dwell_seconds = row.ts - askSince;
  }
  return { rows, source: { file: path.basename(file), bytes: bytes.length, sha256: sha256(bytes) } };
}

function capacityAtOrBelow(row, limit) { return row.asks.filter(([price]) => price <= limit).reduce((sum, [, size]) => sum + size, 0); }
function sizeAtPrice(row, price) { return row.asks.filter(([level]) => level === price).reduce((sum, [, size]) => sum + size, 0); }
function compactRow(row, source, x) {
  return {
    ...clocks(row.ts, source),
    source_ordinal: row.ordinal,
    source_receipt: row.receipt,
    bid: row.bid,
    ask: row.ask,
    last_traded: row.last,
    spread: row.spread,
    ask_dwell_seconds: row.ask_dwell_seconds,
    displayed_ask_size_at_x: sizeAtPrice(row, x),
    displayed_ask_capacity_at_or_below_x: capacityAtOrBelow(row, x),
    displayed_best_ask_size: row.displayed_ask_size,
    top_five_ask_depth: row.top_five_ask_depth,
    ask_relation_to_x: row.ask < x ? "ASK_BELOW_X" : row.ask === x ? "ASK_EQUALS_X" : "ASK_ABOVE_X",
  };
}

function askEpisodes(rows, source) {
  const episodes = [];
  for (const row of rows) {
    const prior = episodes[episodes.length - 1];
    if (!prior || prior.ask_cents !== row.ask) {
      if (prior) {
        prior.end_ts_exclusive = row.ts;
        prior.state_interval_seconds_until_next_change = row.ts - prior.start_ts;
        prior.observed_receipt_span_seconds = prior.last_receipt_ts - prior.start_ts;
      }
      episodes.push({
        ask_cents: row.ask,
        start_ts: row.ts,
        start_clock: clocks(row.ts, source),
        start_receipt: row.receipt,
        last_receipt_ts: row.ts,
        end_ts_exclusive: null,
        end_receipt_inclusive: row.receipt,
        state_interval_seconds_until_next_change: 0,
        observed_receipt_span_seconds: 0,
        receipt_count: 1,
        bid_min: row.bid,
        bid_max: row.bid,
        last_values: Number.isInteger(row.last) ? [row.last] : [],
        displayed_ask_size_min: row.displayed_ask_size,
        displayed_ask_size_max: row.displayed_ask_size,
        top_five_ask_depth_min: row.top_five_ask_depth,
        top_five_ask_depth_max: row.top_five_ask_depth,
      });
    } else {
      prior.last_receipt_ts = row.ts;
      prior.end_receipt_inclusive = row.receipt;
      prior.receipt_count += 1;
      prior.bid_min = Math.min(prior.bid_min, row.bid);
      prior.bid_max = Math.max(prior.bid_max, row.bid);
      if (Number.isInteger(row.last) && !prior.last_values.includes(row.last)) prior.last_values.push(row.last);
      prior.displayed_ask_size_min = Math.min(prior.displayed_ask_size_min, row.displayed_ask_size);
      prior.displayed_ask_size_max = Math.max(prior.displayed_ask_size_max, row.displayed_ask_size);
      prior.top_five_ask_depth_min = Math.min(prior.top_five_ask_depth_min, row.top_five_ask_depth);
      prior.top_five_ask_depth_max = Math.max(prior.top_five_ask_depth_max, row.top_five_ask_depth);
    }
  }
  if (episodes.length) {
    const final = episodes[episodes.length - 1];
    final.end_ts_exclusive = source.right;
    final.state_interval_seconds_until_next_change = source.right - final.start_ts;
    final.observed_receipt_span_seconds = final.last_receipt_ts - final.start_ts;
  }
  return episodes;
}

function main() {
  const replay = JSON.parse(fs.readFileSync(replayPath));
  const summary = JSON.parse(fs.readFileSync(summaryPath));
  const frozenFive = JSON.parse(fs.readFileSync(frozenFivePath));
  const windows = Object.fromEntries(frozenFive.events.map((event) => [event.event_id, event.window]));
  const quoteLines = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/);
  const headers = quoteLines.shift().split(",");
  const quoteRows = quoteLines.map((line) => Object.fromEntries(line.split(",").map((value, index) => [headers[index], value])));
  const sources = {};
  for (const row of quoteRows) {
    const key = `${row.event_id}|${row.leg}`;
    sources[key] = {
      event_id: row.event_id,
      category: row.category,
      leg: row.leg,
      ticker: row.ticker,
      left: Number(row.left_ts),
      right: Number(row.right_ts),
      scheduled: Number(row.scheduled_start_ts),
      bell: Number(windows[row.event_id]?.actual_bell_ts),
    };
  }
  const rowsByTicker = {};
  const sourceHashes = {};
  const fills = [];
  const sequences = [];
  let bigProgression = null;
  for (const event of replay.events) {
    for (const [legId, leg] of Object.entries(event.legs)) {
      if (!leg.fill) continue;
      const source = sources[`${event.event_id}|${legId}`];
      if (!source || !Number.isFinite(source.bell)) throw new Error(`missing source ${event.event_id}/${legId}`);
      if (!rowsByTicker[source.ticker]) {
        const loaded = loadRows(source);
        rowsByTicker[source.ticker] = loaded.rows;
        sourceHashes[source.ticker] = loaded.source;
      }
      const rows = rowsByTicker[source.ticker];
      const ownActionOrdinal = receiptOrdinal(leg.placement.own_book_receipt_at_action);
      const fillOrdinal = receiptOrdinal(leg.fill.evidence_receipt);
      const ownActionRow = rows.find((row) => row.ordinal === ownActionOrdinal);
      const fillRow = rows.find((row) => row.ordinal === fillOrdinal);
      if (!ownActionRow || !fillRow) throw new Error(`missing action/fill row ${event.event_id}/${legId}`);
      const x = leg.placement.price_cents;
      const sequence = rows.filter((row) => row.ordinal >= ownActionOrdinal && row.ordinal <= fillOrdinal).map((row) => compactRow(row, source, x));
      const clamp = Math.max(1, ownActionRow.ask - 1);
      const laterRows = rows.filter((row) => row.ts > leg.placement.action_ts || (row.ts === leg.placement.action_ts && row.ordinal > ownActionOrdinal));
      const firstAskAtClamp = laterRows.find((row) => row.ask <= clamp) || null;
      const firstExecutableClamp = laterRows.find((row) => row.ask <= clamp && row.ask_dwell_seconds >= DWELL_SECONDS && capacityAtOrBelow(row, clamp) >= QUANTITY) || null;
      const minAskAfterAction = Math.min(...laterRows.map((row) => row.ask));
      const actionDisplayedSize = sizeAtPrice(ownActionRow, x);
      const sameReceiptCredit = leg.placement.own_book_receipt_at_action === leg.fill.evidence_receipt;
      fills.push({
        event_id: event.event_id,
        category: event.category,
        leg_id: legId,
        ticker: leg.ticker,
        x_cents: x,
        action_trigger_receipt: leg.placement.action_receipt,
        action_trigger_is_own_book_receipt: leg.placement.action_receipt === leg.placement.own_book_receipt_at_action,
        action_clock: clocks(leg.placement.action_ts, source),
        own_book_at_action: compactRow(ownActionRow, source, x),
        own_book_receipt_age_at_action_seconds: leg.placement.action_ts - ownActionRow.ts,
        exact_timestamp_own_book_snapshot_at_action: leg.placement.action_ts === ownActionRow.ts,
        displayed_external_ask_size_at_x_when_actioned: actionDisplayedSize,
        standing_external_offer_present_on_latest_lawful_snapshot: actionDisplayedSize > 0 && ownActionRow.ts <= leg.placement.action_ts,
        replay_same_receipt_credit: sameReceiptCredit,
        replay_credit_clock: clocks(leg.fill.evidence_ts, source),
        replay_credit_receipt: leg.fill.evidence_receipt,
        replay_action_to_credit_seconds: leg.fill.evidence_ts - leg.placement.action_ts,
        replay_modeled_order_as_pending_between_receipts: !sameReceiptCredit,
        exchange_order_submission_receipt_present: false,
        exchange_order_acknowledgement_present: false,
        exchange_liquidity_role_or_fee_receipt_present: false,
        receipt_proven_liquidity_role: "NOT_ESTABLISHED",
        receipt_proven_fee_treatment: "NOT_ESTABLISHED",
        marketability_if_submitted_unchanged_against_action_snapshot: x >= ownActionRow.ask ? "MARKETABLE_TAKER" : "NONMARKETABLE_MAKER",
        live_post_only_chokepoint_price_cents: clamp,
        live_post_only_relation: clamp < ownActionRow.bid ? "BELOW_BID" : clamp === ownActionRow.bid ? "JOINING_BID" : "INSIDE_SPREAD",
        raw_minimum_ask_after_action_cents: minAskAfterAction,
        raw_ask_ever_reached_live_clamp_after_action: Boolean(firstAskAtClamp),
        first_raw_ask_at_or_below_live_clamp: firstAskAtClamp ? compactRow(firstAskAtClamp, source, clamp) : null,
        ten_second_five_contract_ask_proof_at_or_below_live_clamp: firstExecutableClamp ? compactRow(firstExecutableClamp, source, clamp) : null,
        exact_action_through_credit_sequence_row_count: sequence.length,
      });
      sequences.push({ event_id: event.event_id, leg_id: legId, ticker: leg.ticker, x_cents: x, action_trigger_receipt: leg.placement.action_receipt, own_book_receipt_at_action: leg.placement.own_book_receipt_at_action, fill_receipt: leg.fill.evidence_receipt, rows: sequence });

      if (legId === "BIG") {
        const episodes = askEpisodes(rows, source);
        const actionEpisode = episodes.find((episode) => episode.start_ts <= leg.placement.action_ts && leg.placement.action_ts < episode.end_ts_exclusive);
        bigProgression = {
          event_id: event.event_id,
          leg_id: legId,
          ticker: leg.ticker,
          window: { left_ts: source.left, right_ts: source.right, scheduled_start_ts: source.scheduled, actual_bell_ts: source.bell },
          action_ts: leg.placement.action_ts,
          action_receipt: leg.placement.action_receipt,
          action_x_cents: x,
          valid_raw_book_receipts: rows.length,
          ask_episode_count: episodes.length,
          minimum_best_ask_entire_window_cents: Math.min(...rows.map((row) => row.ask)),
          minimum_best_ask_before_or_at_action_cents: Math.min(...rows.filter((row) => row.ts <= leg.placement.action_ts).map((row) => row.ask)),
          minimum_best_ask_strictly_after_action_cents: minAskAfterAction,
          ask_ever_below_55: rows.some((row) => row.ask < 55),
          ask_ever_below_action_x: rows.some((row) => row.ask < x),
          action_episode: actionEpisode,
          participant_identity_available: false,
          seller_count_at_55_establishable: false,
          episodes,
        };
      }
    }
  }
  if (fills.length !== 4 || !bigProgression) throw new Error("four-fill/BIG conservation failure");

  const byLeg = Object.fromEntries(fills.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const pairMakerAssessment = [
    { event_id: "KXATPCHALLENGERMATCH-26JUL19HURBIG", legs: ["HUR", "BIG"] },
    { event_id: "KXATPCHALLENGERMATCH-26JUL19NIKVRB", legs: ["NIK", "VRB"] },
  ].map(({ event_id, legs }) => {
    const rows = legs.map((leg) => byLeg[`${event_id}|${leg}`]);
    return {
      event_id,
      maker_clamped_legs_with_later_ten_second_five_contract_ask_proof: rows.filter((row) => row.ten_second_five_contract_ask_proof_at_or_below_live_clamp).map((row) => row.leg_id),
      maker_clamped_legs_without_later_ten_second_five_contract_ask_proof: rows.filter((row) => !row.ten_second_five_contract_ask_proof_at_or_below_live_clamp).map((row) => row.leg_id),
      maker_only_pair_completion_supported_by_replay_evidence: rows.every((row) => Boolean(row.ten_second_five_contract_ask_proof_at_or_below_live_clamp)),
      qualification: "Counterfactual replay evidence at the live post-only clamp, not an exchange fill receipt.",
    };
  });

  const receipt = {
    schema_version: "WINDOW1_QUOTE_SHAPE_MAKER_ROLE_ADDENDUM_V2",
    score_free: true,
    correction: {
      prior_blanket_role_claim: "All four replay credits are TAKER",
      corrected_receipt_claim: "All four prices were marketable against their action snapshots if submitted unchanged, but no exchange submission, acknowledgement, liquidity-role, or fee receipt exists. Receipt-proven maker/taker role is NOT_ESTABLISHED.",
      reason: "The strictly-later credit is a simulator chronology rule, not evidence of exchange resting status.",
      immediate_cross_law: "A buy at a displayed standing ask crosses that offer if submitted unchanged; it cannot join a sell queue at the same price.",
      live_maker_law: "The live never-marketable chokepoint changes a post-only buy at or above ask to ask-1 before submission.",
    },
    fill_count: fills.length,
    receipt_proven_maker_count: 0,
    receipt_proven_taker_count: 0,
    receipt_role_not_established_count: fills.length,
    marketable_if_submitted_unchanged_count: fills.filter((row) => row.marketability_if_submitted_unchanged_against_action_snapshot === "MARKETABLE_TAKER").length,
    replay_same_receipt_credit_count: fills.filter((row) => row.replay_same_receipt_credit).length,
    pair_maker_assessment: pairMakerAssessment,
    fills,
  };
  const progression = { schema_version: "WINDOW1_BIG_FULL_ASK_PROGRESSION_V1", score_free: true, ...bigProgression };
  const sequenceReceipt = { schema_version: "WINDOW1_FOUR_FILL_ACTION_TO_CREDIT_SEQUENCE_V1", score_free: true, fill_count: fills.length, sequences };
  const report = [
    "# Maker-role receipt addendum",
    "",
    "The previous blanket receipt-level TAKER ruling is retracted. All four actions were marketable if submitted unchanged, but the replay contains no exchange submission, acknowledgement, liquidity-role, or fee receipt. The receipt-proven role and fee treatment are NOT_ESTABLISHED. The delayed credit is imposed by the simulator and does not prove resting.",
    "",
    "| event | leg | action clocks scheduled/bell | bid/ask/last | own-book age | X | displayed ask size | replay credit delay/rows | receipt role/fee | unchanged submission | live maker clamp | ask later reached clamp? | 10s/5-lot proof at clamp? |",
    "|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|",
    ...fills.map((row) => `| ${row.event_id} | ${row.leg_id} | ${tMinus(row.action_clock.t_minus_scheduled_seconds)} / ${tMinus(row.action_clock.t_minus_actual_bell_seconds)} | ${row.own_book_at_action.bid}/${row.own_book_at_action.ask}/${row.own_book_at_action.last_traded ?? "NULL"} | ${row.own_book_receipt_age_at_action_seconds}s | ${row.x_cents} | ${row.displayed_external_ask_size_at_x_when_actioned} | ${row.replay_action_to_credit_seconds}s / ${row.exact_action_through_credit_sequence_row_count} | NOT_ESTABLISHED / NOT_ESTABLISHED | ${row.marketability_if_submitted_unchanged_against_action_snapshot} | ${row.live_post_only_chokepoint_price_cents} ${row.live_post_only_relation} | ${row.raw_ask_ever_reached_live_clamp_after_action ? "YES" : "NO"} | ${row.ten_second_five_contract_ask_proof_at_or_below_live_clamp ? "YES" : "NO"} |`),
    "",
    "A buy cannot join an existing sell queue at the same price: if sent unchanged while that ask remains, it crosses. Conversely, the simulator's distinct later credit receipt does not prove that an exchange order rested; the replay intentionally withholds same-receipt credit. HUR is additionally based on a 43-second-old own-book snapshot at the sibling-triggered action instant.",
    "",
    "At the live post-only clamp, only HUR has later 10-second/five-contract ask proof (37). BIG at 54, NIK at 17, and VRB at 67 do not. Therefore neither pair is maker-only complete under these replay receipts. That is a counterfactual replay classification, not an exchange liquidity-role receipt.",
    "",
    "## BIG ask path",
    "",
    `BIG's minimum best ask anywhere in the lawful window was ${bigProgression.minimum_best_ask_entire_window_cents}; it never went below 55. The 55 episode containing the action spans ${bigProgression.action_episode.observed_receipt_span_seconds} seconds from first to last observed 55 receipt and ${bigProgression.action_episode.state_interval_seconds_until_next_change} seconds until the first changed-ask receipt, across ${bigProgression.action_episode.receipt_count} raw book receipts. Displayed size at the best ask ranged from ${bigProgression.action_episode.displayed_ask_size_min} to ${bigProgression.action_episode.displayed_ask_size_max} contracts. Participant identities are absent, so the tape cannot establish whether one seller or many supplied that size.`,
    "",
    "| episode | start scheduled/bell | ask | observed receipt span | state until next change | receipts | bid range | last values | ask-size range |",
    "|---:|---|---:|---:|---:|---:|---|---|---|",
    ...bigProgression.episodes.map((episode, index) => `| ${index + 1} | ${tMinus(episode.start_clock.t_minus_scheduled_seconds)} / ${tMinus(episode.start_clock.t_minus_actual_bell_seconds)} | ${episode.ask_cents} | ${episode.observed_receipt_span_seconds}s | ${episode.state_interval_seconds_until_next_change}s | ${episode.receipt_count} | ${episode.bid_min}-${episode.bid_max} | ${episode.last_values.join(",") || "NULL"} | ${episode.displayed_ask_size_min}-${episode.displayed_ask_size_max} |`),
    "",
    "The complete ordered ask-episode ledger and every action-to-credit raw receipt are frozen beside this report.",
  ].join("\n") + "\n";
  const sourceManifest = {
    schema_version: "WINDOW1_MAKER_ROLE_ADDENDUM_SOURCE_MANIFEST_V1",
    committed: Object.fromEntries([replayPath, summaryPath, frozenFivePath, quotePath, v1AuditPath, replayBuilderPath, livePath, __filename].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])),
    private_ticks: Object.fromEntries(Object.entries(sourceHashes).map(([ticker, source]) => [ticker, source])),
  };
  const files = {
    "MAKER_ROLE_RECEIPT_AUDIT.json": canonical(receipt),
    "EXACT_ACTION_TO_CREDIT_SEQUENCE.json": canonical(sequenceReceipt),
    "BIG_FULL_ASK_PROGRESSION.json": canonical(progression),
    "SOURCE_HASH_MANIFEST.json": canonical(sourceManifest),
    "REPORT.md": report,
  };
  const artifacts = Object.entries(files).map(([name, content]) => ({ path: `.claude/window1_live_v4_replay/quote_shape_maker_role_addendum_20260801/${name}`, bytes: Buffer.byteLength(content), sha256: sha256(content) }));
  files["ARTIFACT_HASH_MANIFEST.json"] = canonical({ schema_version: "WINDOW1_MAKER_ROLE_ADDENDUM_ARTIFACT_MANIFEST_V1", artifacts });
  fs.mkdirSync(output, { recursive: true });
  for (const [name, content] of Object.entries(files)) fs.writeFileSync(path.join(output, name), content);
  process.stdout.write(canonical({ status: "BUILT", fill_count: fills.length, receipt_roles_not_established: fills.length, big_ask_episodes: bigProgression.ask_episode_count }));
}

main();
