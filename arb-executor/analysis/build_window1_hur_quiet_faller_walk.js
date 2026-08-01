#!/usr/bin/env node
"use strict";

// Descriptive-only HUR ask walk. This does not alter or invoke a policy.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const repo = path.resolve(process.argv[2] || ".");
const privateRoot = path.resolve(process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private");
const outDir = path.join(repo, ".claude/window1_live_v4_replay/hur_quiet_faller_walk_20260731");
const reportPath = path.join(repo, "arb-executor/docs/research/window1/HUR_QUIET_FALLER_ASK_WALK.md");
const eventId = "KXATPCHALLENGERMATCH-26JUL19HURBIG";
const ticker = `${eventId}-HUR`;
const siblingTicker = `${eventId}-BIG`;
const leftTs = 1784471400;
const rightTs = 1784505540;
const scheduledTs = 1784500200;
const bellTs = 1784505600;
const actionTs = 1784471491;
const fillTs = 1784484959;
const orderPrice = 47;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) throw new Error(`bad ET timestamp ${value}`);
  let hour = Number(m[4]); if (m[7] === "AM" && hour === 12) hour = 0; if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function et(ts) { return new Date((ts - 4 * 3600) * 1000).toISOString().replace("T", " ").replace("Z", " ET"); }
function tminus(ts, reference) { return Math.round(((reference - ts) / 60) * 1000) / 1000; }
function parseCsv(text) {
  const rows = text.trimEnd().split(/\r?\n/), headers = rows.shift().split(",");
  return rows.map((line, index) => ({ raw: Object.fromEntries(line.split(",").map((v, i) => [headers[i], v])), sourceRow: index + 2 }));
}
function loadBooks(target) {
  const file = path.join(privateRoot, "fit-local/ticks", `${target}.csv.gz`), bytes = fs.readFileSync(file);
  const rows = [];
  for (const { raw, sourceRow } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et); if (ts < leftTs || ts > rightTs) continue;
    const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) {
      const bid = integer(raw[`bid_${i}`]), bidSize = positive(raw[`bid_${i}_sz`]);
      const ask = integer(raw[`ask_${i}`]), askSize = positive(raw[`ask_${i}_sz`]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]);
      if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    rows.push({ ts, sourceRow, receipt: `${path.basename(file)}#row-${sourceRow}`, bid: bids[0]?.[0] ?? null, bid_size: bids[0]?.[1] ?? null, ask: asks[0]?.[0] ?? null, ask_size: asks[0]?.[1] ?? null, spread: bids[0] && asks[0] ? asks[0][0] - bids[0][0] : null, top_five_ask_depth: asks.reduce((s, x) => s + x[1], 0), carried_last_trade: integer(raw.last_trade), asks });
  }
  return { file, bytes: bytes.length, sha256: sha256(bytes), rows };
}
function episodes(rows) {
  const output = []; let current = null;
  function close(endTs, endReceipt) {
    if (!current) return;
    current.end_ts = endTs; current.end_et = et(endTs); current.dwell_seconds = endTs - current.start_ts;
    current.tminus_scheduled_end_minutes = tminus(endTs, scheduledTs); current.tminus_bell_end_minutes = tminus(endTs, bellTs);
    current.end_receipt = endReceipt; output.push(current); current = null;
  }
  for (const row of rows) {
    if (!current || row.ask !== current.ask_cents) {
      if (current) close(row.ts, row.receipt);
      current = { episode: output.length + 1, ask_cents: row.ask, start_ts: row.ts, start_et: et(row.ts), tminus_scheduled_start_minutes: tminus(row.ts, scheduledTs), tminus_bell_start_minutes: tminus(row.ts, bellTs), start_receipt: row.receipt, raw_rows: 0, bid_start_cents: row.bid, bid_end_cents: row.bid, bid_min_cents: row.bid, bid_max_cents: row.bid, spread_start_cents: row.spread, spread_end_cents: row.spread, ask_size_start: row.ask_size, ask_size_end: row.ask_size, ask_size_min: row.ask_size, ask_size_max: row.ask_size, top_five_ask_depth_start: row.top_five_ask_depth, top_five_ask_depth_end: row.top_five_ask_depth, top_five_ask_depth_min: row.top_five_ask_depth, top_five_ask_depth_max: row.top_five_ask_depth, carried_last_start_cents: row.carried_last_trade, carried_last_end_cents: row.carried_last_trade, contains_action: false, contains_fill_evidence: false };
    }
    current.raw_rows += 1; current.bid_end_cents = row.bid; current.bid_min_cents = Math.min(current.bid_min_cents, row.bid); current.bid_max_cents = Math.max(current.bid_max_cents, row.bid); current.spread_end_cents = row.spread; current.ask_size_end = row.ask_size; current.ask_size_min = Math.min(current.ask_size_min, row.ask_size); current.ask_size_max = Math.max(current.ask_size_max, row.ask_size); current.top_five_ask_depth_end = row.top_five_ask_depth; current.top_five_ask_depth_min = Math.min(current.top_five_ask_depth_min, row.top_five_ask_depth); current.top_five_ask_depth_max = Math.max(current.top_five_ask_depth_max, row.top_five_ask_depth); current.carried_last_end_cents = row.carried_last_trade;
  }
  close(rightTs, "GUARDED_RIGHT_ENDPOINT");
  for (const episode of output) {
    episode.contains_action = episode.start_ts <= actionTs && actionTs < episode.end_ts;
    episode.contains_fill_evidence = episode.start_ts <= fillTs && fillTs < episode.end_ts;
    episode.relative_to_order = episode.ask_cents === null ? "ASK_UNAVAILABLE" : episode.ask_cents > orderPrice ? "ABOVE_ORDER" : episode.ask_cents === orderPrice ? "AT_ORDER" : "BELOW_ORDER";
  }
  return output;
}
async function firstPrint() {
  const file = path.join(privateRoot, "fit-local/prints.jsonl"), stream = fs.createReadStream(file, { encoding: "utf8" });
  const lines = readline.createInterface({ input: stream, crlfDelay: Infinity }); let ordinal = 0, first = null;
  for await (const line of lines) {
    ordinal += 1; if (!line.includes(ticker)) continue;
    const raw = JSON.parse(line), ts = raw.exchange_ts ? Date.parse(raw.exchange_ts) / 1000 : Number(raw.ts), size = positive(raw.size), price = integer(raw.price_cents ?? raw.price);
    if (!Number.isFinite(ts) || ts < leftTs || ts > rightTs || size === null || price === null) continue;
    const candidate = { ts, et: et(ts), tminus_scheduled_minutes: tminus(ts, scheduledTs), tminus_bell_minutes: tminus(ts, bellTs), price_cents: price, size, trade_id: raw.trade_id || raw.id || null, receipt_id: raw.receipt_id || null, source_ordinal: ordinal };
    if (!first || candidate.ts < first.ts || (candidate.ts === first.ts && candidate.source_ordinal < first.source_ordinal)) first = candidate;
  }
  return { file, first };
}
function latestAt(rows, ts) { let found = null; for (const row of rows) { if (row.ts > ts) break; found = row; } return found; }
async function main() {
  const hur = loadBooks(ticker), big = loadBooks(siblingTicker), askEpisodes = episodes(hur.rows), print = await firstPrint();
  const inheritedSourceManifestPath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/SOURCE_HASH_MANIFEST.json");
  const inheritedSourceManifest = JSON.parse(fs.readFileSync(inheritedSourceManifestPath));
  const atAction = latestAt(hur.rows, actionTs), siblingAtAction = latestAt(big.rows, actionTs);
  if (!atAction || atAction.ts !== actionTs) throw new Error("missing exact HUR action book");
  const placement = { action_ts: actionTs, action_et: et(actionTs), tminus_scheduled_minutes: tminus(actionTs, scheduledTs), tminus_bell_minutes: tminus(actionTs, bellTs), same_tick_observation: atAction, sibling_same_clock_observation: siblingAtAction, arithmetic: `min(bid ${atAction.bid}, ask ${atAction.ask}-1)=${Math.min(atAction.bid, atAction.ask - 1)}`, selected_price_cents: orderPrice, in_window_prior_book_rows: hur.rows.filter((row) => row.ts < actionTs).length, ask_dwell_at_action_seconds: 0, true_prints_observed_before_action: 0, dynamic_falling_evidence: "ABSENT", hold_support_verdict: "NO_OBSERVABLE_SUPPORT_AT_ACTION" };
  const result = { schema_version: "WINDOW1_HUR_QUIET_FALLER_ASK_WALK_V1", descriptive_only: true, policy_changed: false, event_id: eventId, ticker, corridor: { left_ts: leftTs, right_ts: rightTs, scheduled_start_ts: scheduledTs, actual_bell_ts: bellTs }, placement, first_lawful_true_print: print.first, corrected_fill: { price_cents: orderPrice, evidence_ts: fillTs, evidence_et: et(fillTs), tminus_scheduled_minutes: tminus(fillTs, scheduledTs), tminus_bell_minutes: tminus(fillTs, bellTs), source_receipt: "KXATPCHALLENGERMATCH-26JUL19HURBIG-HUR.csv.gz#row-1581", displayed_capacity_at_or_better: 7924 }, ask_episode_count: askEpisodes.length, zero_dwell_episodes: askEpisodes.filter((x) => x.dwell_seconds === 0).length, ask_episodes: askEpisodes, conclusion: { contemporaneous_hold_evidence: "NONE", reason: "The selected price was signed on the first in-window HUR BBO row. There was no prior in-window quote sequence and no lawful true print. Orientation labeled HUR FALLER but supplied no causal duration or continuation threshold. min(bid,ask-1) therefore had placement authority without a hold/patience condition.", required_design_class: "HOLD_CONDITION_BEFORE_PLACEMENT_AUTHORITY_NOT_ANOTHER_PRICE_CONSTANT" }, source: { hur_tick: { file: path.basename(hur.file), bytes: hur.bytes, sha256: hur.sha256 }, sibling_tick: { file: path.basename(big.file), bytes: big.bytes, sha256: big.sha256 }, private_development_prints: inheritedSourceManifest.private_development_prints, inherited_source_manifest: { path: path.relative(repo, inheritedSourceManifestPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(inheritedSourceManifestPath)) } } };
  const lines = ["# HUR quiet-book faller ask walk", "", "Descriptive only. No policy or scorer was changed or invoked.", "", `At ${placement.action_et} (T-${placement.tminus_scheduled_minutes} scheduled; T-${placement.tminus_bell_minutes} bell), the first in-window HUR book was ${atAction.bid}/${atAction.ask}, carried last ${atAction.carried_last_trade}, spread ${atAction.spread}. The corrected rule signed ${placement.arithmetic}. Ask dwell was zero; prior in-window book rows and lawful true prints were both zero.`, `On the same clock, the latest BIG book was ${siblingAtAction.bid}/${siblingAtAction.ask}, carried last ${siblingAtAction.carried_last_trade}, spread ${siblingAtAction.spread}. HUR's first lawful true print did not arrive until ${print.first.et} (T-${print.first.tminus_scheduled_minutes} scheduled; T-${print.first.tminus_bell_minutes} bell), ${Math.round(((print.first.ts - actionTs) / 60) * 1000) / 1000} minutes after placement.`, "", "There was no contemporaneous observable saying the leg was still falling. FALLER was a static orientation label, not a receipt-backed continuation or patience condition. The defect is placement authority without a hold condition; changing the price formula again would not repair that missing gate.", "", "| # | Start ET | T-sched | T-bell | Ask | Dwell s | Bid start-end (min-max) | Ask size min-max | Top-5 ask depth min-max | Last start-end | Relation to 47 |", "|---:|---|---:|---:|---:|---:|---|---|---|---|---|"];
  for (const x of askEpisodes) lines.push(`| ${x.episode} | ${x.start_et} | ${x.tminus_scheduled_start_minutes} | ${x.tminus_bell_start_minutes} | ${x.ask_cents ?? "NA"} | ${x.dwell_seconds} | ${x.bid_start_cents}-${x.bid_end_cents} (${x.bid_min_cents}-${x.bid_max_cents}) | ${x.ask_size_min}-${x.ask_size_max} | ${x.top_five_ask_depth_min}-${x.top_five_ask_depth_max} | ${x.carried_last_start_cents}-${x.carried_last_end_cents} | ${x.relative_to_order}${x.contains_action ? "; PLACE" : ""}${x.contains_fill_evidence ? "; FILL_EVIDENCE" : ""} |`);
  lines.push("", `Full machine receipt: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated/.claude/window1_live_v4_replay/hur_quiet_faller_walk_20260731/HUR_ASK_WALK.json`, "");
  const report = lines.join("\n"), files = { "HUR_ASK_WALK.json": canonical(result), "SOURCE_HASH_MANIFEST.json": canonical(result.source) };
  files["DETERMINISM_RECEIPT.json"] = canonical({ canonical_roundtrip_byte_identical: canonical(result) === canonical(JSON.parse(canonical(result))), artifact_sha256: sha256(Buffer.from(files["HUR_ASK_WALK.json"])) });
  fs.mkdirSync(outDir, { recursive: true }); for (const [name, content] of Object.entries(files)) fs.writeFileSync(path.join(outDir, name), content);
  fs.mkdirSync(path.dirname(reportPath), { recursive: true }); fs.writeFileSync(reportPath, report);
  process.stdout.write(canonical({ status: "BUILT", ask_episodes: askEpisodes.length, zero_dwell: result.zero_dwell_episodes, first_print: print.first, placement }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
