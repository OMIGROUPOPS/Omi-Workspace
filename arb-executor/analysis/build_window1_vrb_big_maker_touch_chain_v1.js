#!/usr/bin/env node
"use strict";

// Exact quote/print trace for the VRB 67 maker touch and BIG 55 ask floor.
// Diagnostic only: no replay decision, fill, score, or live surface is changed.

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
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/vrb_big_maker_touch_chain_20260801")));
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const fivePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const makerPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_role_addendum_20260801/MAKER_ROLE_RECEIPT_AUDIT.json");
const livePath = path.join(repo, "arb-executor/live_v4.py");

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) throw new Error(`bad ET timestamp ${value}`);
  let hour = Number(match[4]);
  if (match[7] === "AM" && hour === 12) hour = 0;
  if (match[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map((line, index) => ({ ordinal: index + 2, row: Object.fromEntries(line.split(",").map((value, column) => [headers[column], value])) }));
}
function finite(value) { const number = Number(value); return Number.isFinite(number) ? number : null; }
function integer(value) { const number = Number(value); return Number.isInteger(number) ? number : null; }
function tMinus(seconds) {
  const sign = seconds >= 0 ? "T-" : "T+";
  const value = Math.abs(seconds);
  return `${sign}${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, "0")}`;
}
function clocks(ts, source) {
  return { timestamp_epoch: ts, t_minus_scheduled_seconds: source.scheduled - ts, t_minus_actual_bell_seconds: source.bell - ts };
}
function compactBook(row, source) {
  return {
    ...clocks(row.ts, source),
    source_ordinal: row.ordinal,
    source_receipt: row.receipt,
    bid: row.bid,
    bid_size: row.bidSize,
    ask: row.ask,
    ask_size: row.askSize,
    last_traded_carried: row.last,
    spread: row.ask - row.bid,
    top_five_bid_depth: row.bidDepth,
    top_five_ask_depth: row.askDepth,
  };
}
function loadBooks(source) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  const bytes = fs.readFileSync(file);
  const rows = [];
  for (const { ordinal, row } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(row.ts_et);
    if (ts < source.left || ts > source.right) continue;
    const bid = integer(row.bid_1);
    const ask = integer(row.ask_1);
    const bidSize = finite(row.bid_1_sz);
    const askSize = finite(row.ask_1_sz);
    if (!bid || !ask || bid > ask || !(bidSize > 0) || !(askSize > 0)) continue;
    rows.push({
      ts,
      ordinal,
      receipt: `${path.basename(file)}#row-${ordinal}`,
      bid,
      ask,
      bidSize,
      askSize,
      last: integer(row.last_trade) || null,
      bidDepth: finite(row.bid_depth_5),
      askDepth: finite(row.ask_depth_5),
    });
  }
  rows.sort((left, right) => left.ts - right.ts || left.ordinal - right.ordinal);
  return { rows, source: { path: `fit-local/ticks/${path.basename(file)}`, bytes: bytes.length, sha256: sha256(bytes) } };
}
function loadPrints(source) {
  const file = path.join(privateRoot, "fit-local/guarded-cache-v3", `${source.event_id}.json.gz`);
  const bytes = fs.readFileSync(file);
  const cache = JSON.parse(zlib.gunzipSync(bytes));
  const leg = cache.legs.find((row) => row.leg === source.leg);
  if (!leg) throw new Error(`missing guarded print leg ${source.event_id}/${source.leg}`);
  const seen = new Set();
  const prints = [];
  for (const row of leg.prints) {
    if (row.ts < source.left || row.ts > source.right || !(row.size > 0) || !Number.isInteger(row.price) || !row.trade_id || seen.has(row.trade_id)) continue;
    seen.add(row.trade_id);
    prints.push({
      ...clocks(row.ts, source),
      price: row.price,
      size: row.size,
      taker_side: row.taker_side,
      aggressor_side: row.taker_side === "yes" ? "BUY" : row.taker_side === "no" ? "SELL" : "UNKNOWN",
      trade_id: row.trade_id,
    });
  }
  prints.sort((left, right) => left.timestamp_epoch - right.timestamp_epoch || left.trade_id.localeCompare(right.trade_id));
  return { prints, source: { path: `fit-local/guarded-cache-v3/${path.basename(file)}`, bytes: bytes.length, sha256: sha256(bytes), cache_key: cache.cache_key, cache_version: cache.cache_version } };
}
function episodes(rows, key, source) {
  const result = [];
  for (const row of rows) {
    const value = key(row);
    const prior = result.at(-1);
    if (!prior || prior.value !== value) {
      if (prior) {
        prior.end_ts_exclusive = row.ts;
        prior.state_interval_seconds_until_next_change = row.ts - prior.start_ts;
        prior.observed_receipt_span_seconds = prior.last_ts - prior.start_ts;
      }
      result.push({
        value,
        start_ts: row.ts,
        last_ts: row.ts,
        start_clock: clocks(row.ts, source),
        start_receipt: row.receipt,
        end_receipt_inclusive: row.receipt,
        end_ts_exclusive: null,
        observed_receipt_span_seconds: 0,
        state_interval_seconds_until_next_change: null,
        receipt_count: 1,
      });
    } else {
      prior.last_ts = row.ts;
      prior.end_receipt_inclusive = row.receipt;
      prior.receipt_count += 1;
    }
  }
  if (result.length) {
    const final = result.at(-1);
    final.observed_receipt_span_seconds = final.last_ts - final.start_ts;
  }
  return result;
}
function gzipJsonl(rows) {
  const text = rows.map((row) => JSON.stringify(row)).join("\n") + "\n";
  return zlib.gzipSync(Buffer.from(text), { level: 9, mtime: 0 });
}

function main() {
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8")).map(({ row }) => row);
  const five = JSON.parse(fs.readFileSync(fivePath));
  const maker = JSON.parse(fs.readFileSync(makerPath));
  const bells = Object.fromEntries(five.events.map((event) => [event.event_id, event.window.actual_bell_ts]));
  const sourceFor = (leg) => {
    const row = quoteRows.find((candidate) => candidate.leg === leg && (leg === "VRB" ? candidate.event_id.includes("NIKVRB") : candidate.event_id.includes("HURBIG")));
    if (!row) throw new Error(`missing source row ${leg}`);
    return { event_id: row.event_id, category: row.category, leg, ticker: row.ticker, left: Number(row.left_ts), right: Number(row.right_ts), scheduled: Number(row.scheduled_start_ts), bell: Number(bells[row.event_id]) };
  };
  const vrbSource = sourceFor("VRB");
  const bigSource = sourceFor("BIG");
  const vrbBooks = loadBooks(vrbSource);
  const bigBooks = loadBooks(bigSource);
  const vrbPrints = loadPrints(vrbSource);
  const bigPrints = loadPrints(bigSource);
  const vrbMaker = maker.fills.find((row) => row.leg_id === "VRB");
  const bigMaker = maker.fills.find((row) => row.leg_id === "BIG");
  if (!vrbMaker || !bigMaker) throw new Error("maker action bindings absent");

  const vrbAskEpisodes = episodes(vrbBooks.rows, (row) => row.ask, vrbSource);
  const vrbBidEpisodes = episodes(vrbBooks.rows, (row) => row.bid, vrbSource);
  const vrbPairEpisodes = episodes(vrbBooks.rows, (row) => `${row.bid}/${row.ask}`, vrbSource);
  const creditOrdinal = Number(String(vrbMaker.replay_credit_receipt).match(/#row-(\d+)/)[1]);
  const creditRow = vrbBooks.rows.find((row) => row.ordinal === creditOrdinal);
  const containingBid67 = vrbBidEpisodes.find((episode) => episode.value === 67 && episode.start_ts <= creditRow.ts && (episode.end_ts_exclusive === null || creditRow.ts < episode.end_ts_exclusive));
  if (!containingBid67 || containingBid67.state_interval_seconds_until_next_change !== 1128) throw new Error("VRB 1128-second bid-67 episode not reproduced");
  const firstAsk68 = vrbBooks.rows.find((row) => row.ask === 68);
  const earlyAsk68Episodes = vrbAskEpisodes.filter((episode) => episode.value === 68 && episode.start_ts <= containingBid67.last_ts);
  if (earlyAsk68Episodes.length !== 9) throw new Error(`VRB early ask-68 episode mismatch ${earlyAsk68Episodes.length}`);
  const earlyPair67x68 = vrbPairEpisodes.filter((episode) => episode.value === "67/68" && episode.start_ts >= firstAsk68.ts && episode.start_ts <= containingBid67.last_ts);
  const pairStateSeconds = earlyPair67x68.reduce((sum, episode) => sum + episode.state_interval_seconds_until_next_change, 0);
  if (pairStateSeconds !== 641) throw new Error(`VRB 67/68 state mismatch ${pairStateSeconds}`);
  const vrbRelevantRows = vrbBooks.rows.filter((row) => row.ts <= containingBid67.last_ts);
  const vrbBid67Rows = vrbRelevantRows.filter((row) => row.bid === 67).map((row) => ({ schema_version: "VRB_BID67_TICK_V1", ...compactBook(row, vrbSource), ask_at_same_tick: row.ask, bid_67: true, ask_68: row.ask === 68 }));
  const vrbAsk68Rows = vrbRelevantRows.filter((row) => row.ask === 68).map((row) => ({ schema_version: "VRB_ASK68_TICK_V1", ...compactBook(row, vrbSource), bid_at_same_tick: row.bid, bid_67: row.bid === 67, ask_68: true }));
  const preFirst68Episodes = vrbPairEpisodes.filter((episode) => episode.start_ts <= firstAsk68.ts);
  const vrbEarlyPrints = vrbPrints.prints.filter((row) => row.timestamp_epoch >= vrbBooks.rows[0].ts && row.timestamp_epoch <= containingBid67.last_ts);
  const vrbSellerExecutionsAtOrBelow67 = vrbEarlyPrints.filter((row) => row.aggressor_side === "SELL" && row.price <= 67);

  const bigAsk55RowsRaw = bigBooks.rows.filter((row) => row.ask === 55);
  const bigAsk55Rows = bigAsk55RowsRaw.map((row) => ({ schema_version: "BIG_ASK55_TICK_V1", ...compactBook(row, bigSource), ask_55: true }));
  const bigBidEpisodesWithinAsk55 = episodes(bigAsk55RowsRaw, (row) => row.bid, bigSource);
  const bigAsk55Start = bigAsk55RowsRaw[0].ts;
  const bigAsk55End = bigAsk55RowsRaw.at(-1).ts;
  const bigNextBookAfter55 = bigBooks.rows.find((row) => row.ts > bigAsk55End || (row.ts === bigAsk55End && row.ordinal > bigAsk55RowsRaw.at(-1).ordinal));
  if (!bigNextBookAfter55) throw new Error("BIG next book after ask-55 episode absent");
  const finalBigBidEpisode = bigBidEpisodesWithinAsk55.at(-1);
  finalBigBidEpisode.end_ts_exclusive = bigNextBookAfter55.ts;
  finalBigBidEpisode.state_interval_seconds_until_next_change = bigNextBookAfter55.ts - finalBigBidEpisode.start_ts;
  const bigPrintsDuring55 = bigPrints.prints.filter((row) => row.timestamp_epoch >= bigAsk55Start && row.timestamp_epoch <= bigAsk55End);
  const bigSellerExecutionsAtOrBelow54 = bigPrintsDuring55.filter((row) => row.aggressor_side === "SELL" && row.price <= 54);
  const bigPrintsAfterActionDuring55 = bigPrintsDuring55.filter((row) => row.timestamp_epoch > bigMaker.action_clock.timestamp_epoch);
  const bigBid55Rows = bigAsk55RowsRaw.filter((row) => row.bid === 55);

  const receipt = {
    schema_version: "WINDOW1_VRB_BIG_MAKER_TOUCH_CHAIN_V1",
    score_free: true,
    fill_law_distinctions: {
      at_touch: "A resting buy equals the external best bid.",
      maker_execution_proof: "A positive-size true print at or below the resting bid with taker_side=no (SELL aggressor), subject to queue uncertainty.",
      ask_visit_one_cent_above_bid: "Shows the order was at touch in a one-cent spread; does not prove a seller hit the bid.",
      carried_last_trade: "Context only; never promoted to a true print.",
    },
    vrb: {
      source: vrbSource,
      first_valid_book: compactBook(vrbBooks.rows[0], vrbSource),
      first_bid_67: compactBook(vrbBooks.rows.find((row) => row.bid === 67), vrbSource),
      first_ask_68: compactBook(firstAsk68, vrbSource),
      bid_67_episode_containing_credit: containingBid67,
      early_ask_68_episode_count: earlyAsk68Episodes.length,
      early_ask_68_episodes: earlyAsk68Episodes,
      early_67x68_episode_count: earlyPair67x68.length,
      early_67x68_state_seconds: pairStateSeconds,
      early_67x68_observed_receipt_span_seconds: earlyPair67x68.reduce((sum, episode) => sum + episode.observed_receipt_span_seconds, 0),
      bid_67_tick_count_through_1128_episode: vrbBid67Rows.length,
      ask_68_tick_count_through_1128_episode: vrbAsk68Rows.length,
      every_early_ask_68_tick_had_bid_67: vrbAsk68Rows.every((row) => row.bid === 67),
      pre_first_68_pair_episodes: preFirst68Episodes,
      seconds_from_first_bid_67_to_first_ask_68: firstAsk68.ts - vrbBooks.rows.find((row) => row.bid === 67).ts,
      true_prints_from_first_book_through_1128_episode: vrbEarlyPrints,
      seller_aggressor_true_prints_at_or_below_67: vrbSellerExecutionsAtOrBelow67,
      resting_67_fill_proven_in_early_chain: vrbSellerExecutionsAtOrBelow67.length > 0,
    },
    big: {
      source: bigSource,
      ask_55_tick_count: bigAsk55Rows.length,
      ask_55_first: compactBook(bigAsk55RowsRaw[0], bigSource),
      ask_55_last: compactBook(bigAsk55RowsRaw.at(-1), bigSource),
      ask_55_observed_receipt_span_seconds: bigAsk55End - bigAsk55Start,
      ask_55_state_seconds_until_next_changed_ask_receipt: bigNextBookAfter55.ts - bigAsk55Start,
      first_changed_ask_after_55: compactBook(bigNextBookAfter55, bigSource),
      bid_episodes_while_ask_55: bigBidEpisodesWithinAsk55,
      bid_55_tick_count_while_ask_55: bigBid55Rows.length,
      bid_55_first_tick: bigBid55Rows.length ? compactBook(bigBid55Rows[0], bigSource) : null,
      true_prints_while_ask_55: bigPrintsDuring55,
      true_prints_after_replay_action_while_ask_55: bigPrintsAfterActionDuring55,
      seller_aggressor_true_prints_at_or_below_54: bigSellerExecutionsAtOrBelow54,
      resting_54_fill_proven: bigSellerExecutionsAtOrBelow54.length > 0,
    },
  };

  const report = [
    "# VRB/BIG maker-touch chain",
    "",
    "## VRB early chain",
    "",
    `VRB was 67/68 in ${earlyPair67x68.length} early episodes totaling ${pairStateSeconds} state-seconds. Every one of the ${vrbAsk68Rows.length} raw ask-68 ticks in those nine episodes had bid 67. The bid-67 episode containing the replay credit lasted ${containingBid67.state_interval_seconds_until_next_change} seconds across ${containingBid67.receipt_count} raw ticks.`,
    "",
    "| visit | start scheduled/bell | last observed scheduled/bell | bid/ask | state seconds | receipts |",
    "|---:|---|---|---|---:|---:|",
    ...earlyPair67x68.map((episode, index) => `| ${index + 1} | ${tMinus(episode.start_clock.t_minus_scheduled_seconds)} / ${tMinus(episode.start_clock.t_minus_actual_bell_seconds)} | ${tMinus(vrbSource.scheduled - episode.last_ts)} / ${tMinus(vrbSource.bell - episode.last_ts)} | 67/68 | ${episode.state_interval_seconds_until_next_change} | ${episode.receipt_count} |`),
    "",
    `The first lawful bid 67 appeared ${firstAsk68.ts - vrbBooks.rows.find((row) => row.bid === 67).ts} seconds before the first ask 68. Before 68, the complete pair-state chain is:`,
    "",
    ...preFirst68Episodes.map((episode) => `- ${tMinus(episode.start_clock.t_minus_scheduled_seconds)} scheduled / ${tMinus(episode.start_clock.t_minus_actual_bell_seconds)} bell: ${episode.value}; ${episode.state_interval_seconds_until_next_change ?? 0}s to next state; ${episode.receipt_count} receipts.`),
    "",
    `True-print check: ${vrbEarlyPrints.length} print(s) occurred from the first book through the 1,128-second bid episode; ${vrbSellerExecutionsAtOrBelow67.length} were SELL-aggressor prints at or below 67. A resting 67 bid was at touch during every 67/68 visit, but an early maker fill is not proven.`,
    "",
    "## BIG ask-55 chain",
    "",
    `BIG's ask was 55 for ${bigAsk55End - bigAsk55Start} observed seconds across ${bigAsk55Rows.length} raw ticks. The bid underneath it followed:`,
    "",
    "| start scheduled/bell | bid/ask | observed span | state to next bid | receipts |",
    "|---|---|---:|---:|---:|",
    ...bigBidEpisodesWithinAsk55.map((episode) => `| ${tMinus(episode.start_clock.t_minus_scheduled_seconds)} / ${tMinus(episode.start_clock.t_minus_actual_bell_seconds)} | ${episode.value}/55 | ${episode.observed_receipt_span_seconds}s | ${episode.state_interval_seconds_until_next_change ?? 0}s | ${episode.receipt_count} |`),
    "",
    `The bid reached 55 only on ${bigBid55Rows.length} same-second raw ticks at the end of the 55-ask episode and the locked state lasted ${finalBigBidEpisode.state_interval_seconds_until_next_change} seconds until the next book changed to ${bigNextBookAfter55.bid}/${bigNextBookAfter55.ask}. The guarded true-print tape contains ${bigPrintsDuring55.length} prints while ask 55 was displayed: ${bigPrintsDuring55.filter((row) => row.price === 55).length} at 55, ${bigPrintsDuring55.filter((row) => row.price === 56).length} at 56, and ${bigPrintsDuring55.filter((row) => row.price === 57).length} at 57; all were BUY aggressors. There were ${bigSellerExecutionsAtOrBelow54.length} SELL-aggressor prints at or below the maker-clamped 54. A resting 54 fill is not proven.`,
    "",
    "The compressed JSONL ledgers contain every requested raw tick with both clocks and the same-tick bid, ask, carried last trade, spread, size, and top-five depth.",
  ].join("\n") + "\n";

  const sourceManifest = {
    schema_version: "WINDOW1_VRB_BIG_MAKER_TOUCH_SOURCE_MANIFEST_V1",
    committed: Object.fromEntries([quotePath, fivePath, makerPath, livePath, __filename].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])),
    private: { vrb_books: vrbBooks.source, vrb_guarded_prints: vrbPrints.source, big_books: bigBooks.source, big_guarded_prints: bigPrints.source },
  };
  const files = {
    "MAKER_TOUCH_EXECUTION_RECEIPT.json": Buffer.from(canonical(receipt)),
    "VRB_BID67_TICKS.jsonl.gz": gzipJsonl(vrbBid67Rows),
    "VRB_ASK68_TICKS.jsonl.gz": gzipJsonl(vrbAsk68Rows),
    "BIG_ASK55_TICKS.jsonl.gz": gzipJsonl(bigAsk55Rows),
    "REPORT.md": Buffer.from(report),
    "SOURCE_HASH_MANIFEST.json": Buffer.from(canonical(sourceManifest)),
  };
  const artifacts = Object.entries(files).map(([name, bytes]) => ({ path: `.claude/window1_live_v4_replay/vrb_big_maker_touch_chain_20260801/${name}`, bytes: bytes.length, sha256: sha256(bytes) }));
  files["ARTIFACT_HASH_MANIFEST.json"] = Buffer.from(canonical({ schema_version: "WINDOW1_VRB_BIG_MAKER_TOUCH_ARTIFACT_MANIFEST_V1", artifacts }));
  fs.mkdirSync(output, { recursive: true });
  for (const [name, bytes] of Object.entries(files)) fs.writeFileSync(path.join(output, name), bytes);
  process.stdout.write(canonical({ status: "BUILT", vrb_bid67_ticks: vrbBid67Rows.length, vrb_ask68_ticks: vrbAsk68Rows.length, vrb_67x68_seconds: pairStateSeconds, big_ask55_ticks: bigAsk55Rows.length }));
}

main();
