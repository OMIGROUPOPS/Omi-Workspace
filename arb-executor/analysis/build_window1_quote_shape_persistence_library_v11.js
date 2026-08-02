#!/usr/bin/env node
"use strict";

// Fits a causal survival bound for a unanimous LOWER verdict from the same
// quote-only development corpus as the frozen shape library. The bound is the
// maximum observed wait from arrival at a qualified current low to a later
// qualified lower ask, partitioned by category, formed-book price region,
// exact shape, and observed new-low ordinal. Runtime uses it leave-one-leg-out.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private"));
const shapeLibraryPath = path.resolve(value("--shape-library", path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json")));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_v11_fit_20260802/PERSISTENCE_SURVIVAL_LIBRARY_V11.json")));
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const DWELL_SECONDS = 10;
const QUANTITY = 5;

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function integer(x) { const n = Number(x); return Number.isInteger(n) ? n : null; }
function positive(x) { const n = Number(x); return Number.isFinite(n) && n > 0 ? n : null; }
function parseEt(x) { const m = String(x).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line, i) => ({ raw: Object.fromEntries(line.split(",").map((v, j) => [headers[j], v])), ordinal: i + 2 })); }
function ensure(ok, message) { if (!ok) throw new Error(message); }

function loadEpisodes(source) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  const bytes = fs.readFileSync(file), rows = [];
  for (const { raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et); if (ts === null || ts < Number(source.left_ts) || ts > Number(source.right_ts)) continue;
    const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) { const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]); if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]); }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, bid: bids[0][0], ask: asks[0][0], top_ask_size: asks[0][1], spread: asks[0][0] - bids[0][0] });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  const formed = rows.findIndex((row) => row.spread === 1); if (formed < 0) return { episodes: [], source: { file: path.basename(file), sha256: sha256(bytes), bytes: bytes.length } };
  const lawful = rows.slice(formed), episodes = []; let current = null, low = null, descentOrdinal = 0;
  for (const row of lawful) {
    if (!current || row.ask !== current.ask) {
      if (current) { current.end_ts = row.ts; episodes.push(current); }
      if (low === null) low = row.ask; else if (row.ask < low) { low = row.ask; descentOrdinal += 1; }
      current = { ask: row.ask, start_ts: row.ts, end_ts: Number(source.right_ts), observed_low_at_start: low, descent_ordinal: descentOrdinal, first_qualifying_ts: null, first_qualifying_receipt_ordinal: null };
    }
    if (current.first_qualifying_ts === null && row.ts - current.start_ts >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) { current.first_qualifying_ts = row.ts; current.first_qualifying_receipt_ordinal = row.ordinal; }
  }
  if (current) episodes.push(current);
  return { episodes, source: { file: path.basename(file), sha256: sha256(bytes), bytes: bytes.length } };
}

function main() {
  const shapeLibraryBytes = fs.readFileSync(shapeLibraryPath), shapeLibrary = JSON.parse(shapeLibraryBytes);
  const shapeGroup = {};
  for (const [groupKey, group] of Object.entries(shapeLibrary.groups)) for (const shape of group.shapes) shapeGroup[shape.shape_id] = groupKey;
  const matrix = fs.readFileSync(quotePath, "utf8").trimEnd().split(/\r?\n/), headers = matrix.shift().split(",");
  const sources = matrix.map((line) => Object.fromEntries(line.split(",").map((v, i) => [headers[i], v]))).filter((r) => String(r.evaluator_window_positive).toLowerCase() === "true" && shapeLibrary.assignment[`${r.event_id}|${r.leg}`]);
  const cells = {}, sourceHashes = {}; let qualifiedEpisodes = 0, futureLowerEpisodes = 0, bottomedEpisodes = 0;
  for (const source of sources) {
    const identity = `${source.event_id}|${source.leg}`, shapeId = shapeLibrary.assignment[identity], groupKey = shapeGroup[shapeId]; ensure(groupKey, `missing group for shape ${shapeId}`); const [category, priceRegion] = groupKey.split("|"); ensure(category === source.category, `category mismatch for ${identity}`); const loaded = loadEpisodes(source); sourceHashes[source.ticker] = loaded.source;
    const qualified = loaded.episodes.filter((x) => x.first_qualifying_ts !== null && x.ask === x.observed_low_at_start);
    for (const episode of qualified) {
      qualifiedEpisodes += 1;
      const later = qualified.find((x) => x.first_qualifying_ts > episode.first_qualifying_ts && x.ask < episode.ask);
      const key = `${category}|${priceRegion}|${shapeId}|${episode.descent_ordinal}`;
      const cell = cells[key] ??= { category, price_region: priceRegion, shape_id: shapeId, observed_new_low_descents: episode.descent_ordinal, future_qualified_lower_examples: [], terminal_qualified_low_examples: [] };
      const base = { leg_identity: identity, event_id: source.event_id, leg_id: source.leg, ticker: source.ticker, ask_cents: episode.ask, episode_start_ts: episode.start_ts, first_qualifying_ts: episode.first_qualifying_ts, first_qualifying_receipt_ordinal: episode.first_qualifying_receipt_ordinal };
      if (later) { futureLowerEpisodes += 1; cell.future_qualified_lower_examples.push({ ...base, later_lower_ask_cents: later.ask, later_lower_first_qualifying_ts: later.first_qualifying_ts, wait_from_episode_start_seconds: later.first_qualifying_ts - episode.start_ts }); }
      else { bottomedEpisodes += 1; cell.terminal_qualified_low_examples.push(base); }
    }
  }
  for (const cell of Object.values(cells)) {
    cell.future_qualified_lower_examples.sort((a, b) => a.wait_from_episode_start_seconds - b.wait_from_episode_start_seconds || a.leg_identity.localeCompare(b.leg_identity));
    cell.terminal_qualified_low_examples.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity) || a.first_qualifying_ts - b.first_qualifying_ts);
    cell.future_qualified_lower_support_n = cell.future_qualified_lower_examples.length;
    cell.terminal_qualified_low_support_n = cell.terminal_qualified_low_examples.length;
    cell.max_wait_to_future_qualified_lower_seconds = cell.future_qualified_lower_examples.length ? Math.max(...cell.future_qualified_lower_examples.map((x) => x.wait_from_episode_start_seconds)) : null;
    const waits = cell.future_qualified_lower_examples.map((x) => x.wait_from_episode_start_seconds).sort((a, b) => a - b);
    cell.median_wait_to_future_qualified_lower_seconds = waits.length ? waits[Math.floor(waits.length / 2)] : null;
  }
  const result = { schema_version: "WINDOW1_QUOTE_SHAPE_PERSISTENCE_SURVIVAL_LIBRARY_V11", score_free: true, fit_population: { legs: sources.length, qualified_low_episodes: qualifiedEpisodes, future_qualified_lower_episodes: futureLowerEpisodes, terminal_qualified_low_episodes: bottomedEpisodes }, partition: "category + formed-book price region + exact quote-shape + observed new-low descent ordinal", causal_law: "At runtime, exclude the target leg. A qualified current low may override unanimous LOWER only after its same-price dwell strictly exceeds the empirical median wait to a later qualified lower ask among remaining fitted examples. This is the same upper-median estimator already frozen for the descent ordinal, not a new percentile. If remaining support contains terminal examples and no future-lower example, the fitted bound is zero. Missing support remains unavailable.", constants: { dwell_seconds: DWELL_SECONDS, exact_quantity_contracts: QUANTITY, wait_estimator: "leave-one-leg-out upper median, identical estimator class to the fitted descent ordinal", provenance: "inherited ask-reachability and descent-ordinal laws" }, cells: Object.fromEntries(Object.entries(cells).sort(([a], [b]) => a.localeCompare(b))), source: { shape_library: { path: path.relative(repo, shapeLibraryPath).replaceAll("\\", "/"), sha256: sha256(shapeLibraryBytes) }, quote_ledger: { path: path.relative(repo, quotePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(quotePath)) }, tick_files: sourceHashes }, forbidden_access: { holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false } };
  ensure(result.fit_population.legs > 0 && Object.keys(cells).length > 0, "empty persistence fit");
  fs.mkdirSync(path.dirname(output), { recursive: true }); fs.writeFileSync(output, canonical(result));
  process.stdout.write(canonical({ status: "BUILT", output: path.relative(repo, output).replaceAll("\\", "/"), fit_population: result.fit_population, cells: Object.keys(cells).length, sha256: sha256(fs.readFileSync(output)) }));
}

main();
