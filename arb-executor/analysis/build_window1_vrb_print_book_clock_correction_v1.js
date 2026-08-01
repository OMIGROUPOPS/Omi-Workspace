#!/usr/bin/env node
"use strict";

// Corrects the scope of the VRB early-chain print statement by intersecting
// true prints with each exact 67/68 interval and auditing cross-stream clocks.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const arg = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/vrb_print_book_clock_correction_20260801")));
const chainPath = path.join(repo, ".claude/window1_live_v4_replay/vrb_big_maker_touch_chain_20260801/MAKER_TOUCH_EXECUTION_RECEIPT.json");
const priorReportPath = path.join(repo, ".claude/window1_live_v4_replay/vrb_big_maker_touch_chain_20260801/REPORT.md");

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function round6(value) { return Math.round(value * 1e6) / 1e6; }
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
  return lines.map((line, index) => ({ ordinal: index + 2, row: Object.fromEntries(line.split(",").map((value, column) => [headers[column], value])) }));
}
function clocks(ts, source) { return { timestamp_epoch: ts, t_minus_scheduled_seconds: source.scheduled - ts, t_minus_actual_bell_seconds: source.bell - ts }; }
function tMinus(seconds) {
  const sign = seconds >= 0 ? "T-" : "T+";
  const value = Math.abs(seconds);
  return `${sign}${Math.floor(value / 60)}:${String(Math.floor(value % 60)).padStart(2, "0")}.${String(Math.round((value % 1) * 1e6)).padStart(6, "0")}`;
}
function compactBook(row, source) {
  return { ...clocks(row.ts, source), source_ordinal: row.ordinal, source_receipt: row.receipt, source_ts_et: row.tsEt, bid: row.bid, bid_size: row.bidSize, ask: row.ask, ask_size: row.askSize, last_traded_carried: row.last, spread: row.ask - row.bid };
}

function main() {
  const chain = JSON.parse(fs.readFileSync(chainPath));
  const source = chain.vrb.source;
  const tickFile = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  const cacheFile = path.join(privateRoot, "fit-local/guarded-cache-v3", `${source.event_id}.json.gz`);
  const tickBytes = fs.readFileSync(tickFile);
  const cacheBytes = fs.readFileSync(cacheFile);
  const books = parseCsv(zlib.gunzipSync(tickBytes).toString("utf8")).map(({ ordinal, row }) => ({
    ts: parseEt(row.ts_et),
    tsEt: row.ts_et,
    ordinal,
    receipt: `${path.basename(tickFile)}#row-${ordinal}`,
    bid: Number(row.bid_1),
    ask: Number(row.ask_1),
    bidSize: Number(row.bid_1_sz),
    askSize: Number(row.ask_1_sz),
    last: Number(row.last_trade) || null,
  })).filter((row) => row.ts >= source.left && row.ts <= source.right && row.bid > 0 && row.ask > 0 && row.bid <= row.ask && row.bidSize > 0 && row.askSize > 0).sort((left, right) => left.ts - right.ts || left.ordinal - right.ordinal);
  const cache = JSON.parse(zlib.gunzipSync(cacheBytes));
  const leg = cache.legs.find((row) => row.leg === "VRB");
  const seen = new Set();
  const prints = leg.prints.filter((row) => row.ts >= source.left && row.ts <= source.right && row.size > 0 && row.trade_id && !seen.has(row.trade_id) && seen.add(row.trade_id)).map((row) => ({
    ...clocks(row.ts, source),
    price: row.price,
    size: row.size,
    taker_side: row.taker_side,
    aggressor_side: row.taker_side === "yes" ? "BUY" : row.taker_side === "no" ? "SELL" : "UNKNOWN",
    trade_id: row.trade_id,
  })).sort((left, right) => left.timestamp_epoch - right.timestamp_epoch || left.trade_id.localeCompare(right.trade_id));

  const visits = chain.vrb.early_ask_68_episodes.map((episode, index) => {
    const inside = prints.filter((row) => row.timestamp_epoch >= episode.start_ts && row.timestamp_epoch < episode.end_ts_exclusive);
    return {
      visit: index + 1,
      interval_semantics: "[start_ts,end_ts_exclusive)",
      start: { ...clocks(episode.start_ts, source), receipt: episode.start_receipt },
      end_exclusive: { ...clocks(episode.end_ts_exclusive, source) },
      last_observed: { ...clocks(episode.last_ts, source), receipt: episode.end_receipt_inclusive },
      book: { bid: 67, ask: 68 },
      state_seconds: episode.state_interval_seconds_until_next_change,
      book_receipt_count: episode.receipt_count,
      print_count: inside.length,
      prints: inside,
    };
  });
  const visitPrints = visits.flatMap((row) => row.prints);
  if (visits.length !== 9 || visitPrints.length !== 0) throw new Error(`visit/print conservation ${visits.length}/${visitPrints.length}`);

  const earlyStart = chain.vrb.first_valid_book.timestamp_epoch;
  const earlyEnd = chain.vrb.bid_67_episode_containing_credit.last_ts;
  const contextualPrints = prints.filter((row) => row.timestamp_epoch >= earlyStart && row.timestamp_epoch <= earlyEnd);
  if (contextualPrints.length !== 1) throw new Error(`contextual print count ${contextualPrints.length}`);
  const print = contextualPrints[0];
  const sameSecond = books.filter((row) => row.ts === Math.floor(print.timestamp_epoch));
  const distinctPrior = books.filter((row) => row.ts < Math.floor(print.timestamp_epoch)).at(-1);
  const latestAtOrBefore = books.filter((row) => row.ts <= print.timestamp_epoch).at(-1);
  const containingVisit = visits.find((visit) => print.timestamp_epoch >= visit.start.timestamp_epoch && print.timestamp_epoch < visit.end_exclusive.timestamp_epoch) || null;
  const priorVisit = [...visits].reverse().find((visit) => visit.end_exclusive.timestamp_epoch <= print.timestamp_epoch) || null;
  const nextVisit = visits.find((visit) => visit.start.timestamp_epoch > print.timestamp_epoch) || null;
  const askAgreement = distinctPrior.ask === 70 && sameSecond.length > 0 && sameSecond.every((row) => row.ask === 70) && latestAtOrBefore.ask === 70;
  if (!askAgreement || containingVisit !== null) throw new Error("print/book correction invariant failed");

  const receipt = {
    schema_version: "WINDOW1_VRB_PRINT_BOOK_CLOCK_CORRECTION_V1",
    score_free: true,
    correction: {
      prior_statement: "One true print occurred from the first valid book through the end of the 1,128-second bid-67 episode.",
      status: "TRUE_BUT_MISLEADING_SCOPE",
      corrected_statement: "That print occurred between the first and second 67/68 visits while the contemporaneous book was 69/70. No true print occurred inside any of the nine 67/68 intervals.",
    },
    print: {
      ...print,
      timestamp_et: "2026-07-19 07:13:56.179481 AM EDT",
      containing_67x68_visit: containingVisit,
      seconds_after_prior_visit_end: round6(print.timestamp_epoch - priorVisit.end_exclusive.timestamp_epoch),
      seconds_before_next_visit_start: round6(nextVisit.start.timestamp_epoch - print.timestamp_epoch),
      latest_distinct_prior_second_book: compactBook(distinctPrior, source),
      same_second_book_rows: sameSecond.map((row) => compactBook(row, source)),
      latest_book_at_or_before_print: compactBook(latestAtOrBefore, source),
      ask_at_print_cents: 70,
      ask_at_print_established_despite_cross_stream_subsecond_ambiguity: askAgreement,
    },
    visits,
    conservation: { visit_count: visits.length, prints_inside_visits: visitPrints.length, all_nine_print_empty: visits.every((visit) => visit.print_count === 0) },
    clock_binding: {
      print_clock: "Guarded-cache true-print Unix epoch seconds with microsecond precision; source UTC normalized.",
      book_clock: "Tick CSV America/New_York timestamp converted to Unix epoch seconds; source precision is one second; equal-second book rows ordered by preserved source ordinal.",
      same_epoch_basis: true,
      directly_comparable_across_distinct_seconds: true,
      authoritative_cross_stream_order_within_same_second: false,
      conclusion_reliability_here: "RELIABLE: the latest distinct-prior-second book and every same-second book row all agree on 69/70, so unavailable subsecond cross-stream ordering cannot change the ask-at-print conclusion.",
    },
  };
  const report = [
    "# VRB print/book clock correction",
    "",
    `The 70-cent print occurred at 2026-07-19 07:13:56.179481 AM EDT (epoch ${print.timestamp_epoch}; ${tMinus(print.t_minus_scheduled_seconds)} scheduled / ${tMinus(print.t_minus_actual_bell_seconds)} bell). The latest distinct-prior-second book was ${distinctPrior.bid}/${distinctPrior.ask} at ${distinctPrior.tsEt}; both book rows stamped 07:13:56 were also ${sameSecond[0].bid}/${sameSecond[0].ask}. The ask was 70, not 68.`,
    "",
    `The print was ${round6(print.timestamp_epoch - priorVisit.end_exclusive.timestamp_epoch)} seconds after visit 1 ended and ${round6(nextVisit.start.timestamp_epoch - print.timestamp_epoch)} seconds before visit 2 began. It was outside every 67/68 interval.`,
    "",
    "| visit | exact half-open interval epoch | scheduled/bell start | bid/ask | prints |",
    "|---:|---|---|---|---|",
    ...visits.map((visit) => `| ${visit.visit} | [${visit.start.timestamp_epoch}, ${visit.end_exclusive.timestamp_epoch}) | ${tMinus(visit.start.t_minus_scheduled_seconds)} / ${tMinus(visit.start.t_minus_actual_bell_seconds)} | 67/68 | NONE |`),
    "",
    "The streams share a normalized Unix-epoch basis and are directly comparable across distinct seconds. The book source has only one-second precision, so cross-stream order inside one second is not authoritative. Here that limitation is immaterial: the 07:13:52 book and both 07:13:56 book rows all show 69/70.",
  ].join("\n") + "\n";
  const sourceManifest = {
    schema_version: "WINDOW1_VRB_PRINT_BOOK_CLOCK_SOURCE_MANIFEST_V1",
    committed: Object.fromEntries([chainPath, priorReportPath, __filename].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])),
    private: {
      tick_csv_gz: { path: `fit-local/ticks/${path.basename(tickFile)}`, bytes: tickBytes.length, sha256: sha256(tickBytes) },
      guarded_cache_gz: { path: `fit-local/guarded-cache-v3/${path.basename(cacheFile)}`, bytes: cacheBytes.length, sha256: sha256(cacheBytes), cache_key: cache.cache_key, cache_version: cache.cache_version },
    },
  };
  const files = {
    "PRINT_BOOK_CLOCK_RECEIPT.json": canonical(receipt),
    "NINE_VISIT_PRINT_INTERSECTION.json": canonical({ schema_version: "WINDOW1_VRB_NINE_VISIT_PRINT_INTERSECTION_V1", visits }),
    "REPORT.md": report,
    "SOURCE_HASH_MANIFEST.json": canonical(sourceManifest),
  };
  const artifacts = Object.entries(files).map(([name, content]) => ({ path: `.claude/window1_live_v4_replay/vrb_print_book_clock_correction_20260801/${name}`, bytes: Buffer.byteLength(content), sha256: sha256(content) }));
  files["ARTIFACT_HASH_MANIFEST.json"] = canonical({ schema_version: "WINDOW1_VRB_PRINT_BOOK_CLOCK_ARTIFACT_MANIFEST_V1", artifacts });
  fs.mkdirSync(output, { recursive: true });
  for (const [name, content] of Object.entries(files)) fs.writeFileSync(path.join(output, name), content);
  process.stdout.write(canonical({ status: "BUILT", print_epoch: print.timestamp_epoch, ask_at_print: 70, visits: visits.length, prints_inside_visits: visitPrints.length }));
}

main();
