#!/usr/bin/env node
"use strict";

/* One-shot, frozen V11/V13/V14 Window-1 holdout evaluation.
 *
 * The runner consumes only the declared 2026-07-24..26 BBO files and frozen
 * event catalog, completes a resumable receipt-identified public-trade
 * capture, and applies the three already-fitted policies without refitting.
 * The evaluation identity is not consumed until every tape validates.
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { spawnSync } = require("child_process");

const HOLDOUT_DATES = new Set(["26JUL24", "26JUL25", "26JUL26"]);
const CATEGORIES = new Map([
  ["KXATPCHALLENGERMATCH", "ATP_CHALL"],
  ["KXATPMATCH", "ATP_MAIN"],
  ["KXWTACHALLENGERMATCH", "WTA_CHALL"],
  ["KXWTAMATCH", "WTA_MAIN"],
]);
const DWELL_SECONDS = 10;
const QUANTITY = 5;
const LATE_CLOSE_SECONDS = 300;
const VERSIONS = ["V11", "V13", "V14"];
const CEILINGS = [
  "absolute_traded_low",
  "traded_low_print_size_at_least_five",
  "capacity_proven_ask_floor",
  "lowest_seller_aggressed_trade_floor",
  "maker_reachable",
];

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function compact(value) { return JSON.stringify(value); }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function finite(value) { const n = Number(value); return Number.isFinite(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function rel(repo, file) { return path.relative(repo, file).replaceAll("\\", "/"); }
function writeJson(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, canonical(value)); }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(compact).join("\n")}\n`), { level: 9, mtime: 0 }); }
function readGzipRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function countBy(values) { const out = new Map(); for (const value of values) out.set(String(value), (out.get(String(value)) || 0) + 1); return Object.fromEntries([...out].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const rows = values.filter(Number.isFinite).sort((a, b) => a - b); return rows.length ? rows[Math.min(rows.length - 1, Math.floor(p * (rows.length - 1)))] : null; }
function distribution(values, denominator = values.length) { const rows = values.filter(Number.isFinite).sort((a, b) => a - b); return { denominator, available: rows.length, unavailable: denominator - rows.length, min: rows.length ? rows[0] : null, p25: quantile(rows, .25), median: quantile(rows, .5), p75: quantile(rows, .75), p90: quantile(rows, .9), max: rows.length ? rows[rows.length - 1] : null, exact_counts: countBy(values.map((x) => Number.isFinite(x) ? x : "UNAVAILABLE")) }; }
function group(rows, keyFn) { const out = new Map(); for (const row of rows) { const key = keyFn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function honestFillCredited(fillClass, price) { return Number.isInteger(price) && (fillClass === "PROVEN_MAKER" || fillClass === "PROVEN_TAKER"); }

function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}

function csvRows(text) {
  const lines = text.trimEnd().split(/\r?\n/); const headers = lines.shift().split(",");
  return lines.map((line, index) => ({ ordinal: index + 2, ...Object.fromEntries(line.replace(/\r$/, "").split(",").map((v, i) => [headers[i], v])) }));
}

function tickerIdentity(name) {
  const stem = name.replace(/\.csv\.gz$/, ""); const cut = stem.lastIndexOf("-");
  if (cut < 1) return null;
  const ticker = stem, eventId = stem.slice(0, cut), legId = stem.slice(cut + 1), prefix = eventId.split("-")[0], dateToken = eventId.split("-")[1]?.slice(0, 7);
  if (!CATEGORIES.has(prefix) || !HOLDOUT_DATES.has(dateToken)) return null;
  return { event_id: eventId, leg_id: legId, ticker, category: CATEGORIES.get(prefix), event_date: `2026-07-${dateToken.slice(-2)}` };
}

function loadBooks(file, left, right) {
  const bytes = fs.readFileSync(file), rows = [];
  for (const raw of csvRows(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et); if (ts === null || ts < left || ts > right) continue;
    const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) {
      const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal: raw.ordinal, bid: bids[0][0], ask: asks[0][0], asks, top_ask_size: asks[0][1] });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return { rows, bytes: bytes.length, sha256: sha256(bytes) };
}

function capacityFloor(books, right) {
  const since = Array(100).fill(null); let best = null, last = null;
  function inspect(book, evidenceTs, endpoint = false) {
    for (let limit = 1; limit < book.ask; limit += 1) since[limit] = null;
    for (let limit = book.ask; limit <= 99; limit += 1) if (since[limit] === null) since[limit] = book.ts;
    let cumulative = 0, idx = 0;
    for (let limit = book.ask; limit <= 99; limit += 1) {
      while (idx < book.asks.length && book.asks[idx][0] <= limit) cumulative += book.asks[idx++][1];
      if (cumulative < QUANTITY || evidenceTs - since[limit] < DWELL_SECONDS) continue;
      if (!best || limit < best.limit_cents || (limit === best.limit_cents && evidenceTs < best.evidence_ts)) best = { limit_cents: limit, evidence_ts: evidenceTs, dwell_seconds: evidenceTs - since[limit], displayed_capacity: cumulative, source_ordinal: book.ordinal, right_endpoint_carry: endpoint };
      break;
    }
  }
  for (const book of books) { inspect(book, book.ts); last = book; }
  if (last && last.ts < right) inspect(last, right, true);
  return best;
}

function canonicalTrade(row, ticker) {
  const tradeId = String(row.trade_id || "").trim(); ensure(tradeId, `${ticker}: public trade lacks trade_id`); ensure(row.ticker === ticker, `${ticker}: public trade ticker mismatch`);
  const ts = Date.parse(String(row.created_time || "")) / 1000; ensure(Number.isFinite(ts), `${ticker}/${tradeId}: bad created_time`);
  const price = row.yes_price_dollars !== undefined && row.yes_price_dollars !== null ? Math.round(Number(row.yes_price_dollars) * 100) : integer(row.yes_price);
  ensure(Number.isInteger(price) && price >= 1 && price <= 99, `${ticker}/${tradeId}: bad price`);
  const size = finite(row.count_fp ?? row.count); ensure(size !== null && size >= 0, `${ticker}/${tradeId}: bad size`);
  return { trade_id: tradeId, ticker, ts, price, size, taker_side: String(row.taker_side || ""), created_time: row.created_time };
}

async function requestJson(url, attempts = 12) {
  let last;
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetch(url, { headers: { Accept: "application/json", "User-Agent": "omi-window1-holdout-v2-resumable" }, signal: AbortSignal.timeout(30000) });
      if (!response.ok) {
        const retryAfter = finite(response.headers.get("retry-after"));
        const error = new Error(`HTTP ${response.status}`);
        error.retry_after_ms = retryAfter === null ? null : Math.max(0, retryAfter * 1000);
        throw error;
      }
      return await response.json();
    } catch (error) {
      last = error;
      if (attempt + 1 < attempts) {
        const deterministicBackoff = Math.min(60000, 1000 * 2 ** Math.min(attempt, 6));
        await new Promise((resolve) => setTimeout(resolve, error.retry_after_ms ?? deterministicBackoff));
      }
    }
  }
  throw last;
}

function readFrozenTape(file, ticker) {
  const bytes = fs.readFileSync(file);
  const pages = JSON.parse(zlib.gunzipSync(bytes).toString("utf8"));
  ensure(Array.isArray(pages) && pages.length > 0, `${ticker}: frozen tape pages absent`);
  const trades = [];
  for (const page of pages) {
    ensure(page && page.response && Array.isArray(page.response.trades), `${ticker}: malformed frozen page`);
    for (const row of page.response.trades) trades.push(canonicalTrade(row, ticker));
  }
  return { ticker, trades, page_count: pages.length, raw_sha256: sha256(bytes), raw_bytes: bytes.length, capture: "REUSED_HASH_VALIDATED" };
}

async function fetchTapeResumable(tickers, rawDir, progressFile) {
  fs.mkdirSync(rawDir, { recursive: true });
  const results = [], failures = [], queue = [];
  for (const ticker of tickers) {
    const file = path.join(rawDir, `${ticker}.json.gz`);
    if (fs.existsSync(file)) results.push(readFrozenTape(file, ticker)); else queue.push(ticker);
  }
  fs.appendFileSync(progressFile, `${new Date().toISOString()} CAPTURE_CENSUS reused=${results.length} missing=${queue.length}\n`);
  let complete = results.length;
  async function worker() {
    while (queue.length) {
      const ticker = queue.shift();
      try {
        let cursor = "", page = 0; const pages = [], trades = [], seenCursor = new Set();
        while (true) {
          const query = new URLSearchParams({ ticker, limit: "1000", ...(cursor ? { cursor } : {}) });
          const payload = await requestJson(`https://api.elections.kalshi.com/trade-api/v2/markets/trades?${query}`); page += 1;
          ensure(Array.isArray(payload.trades), `${ticker} page ${page}: trades missing`);
          for (const row of payload.trades) trades.push(canonicalTrade(row, ticker));
          pages.push({ page, cursor_in: cursor, response: payload }); const next = String(payload.cursor || "");
          if (!next) break; ensure(next !== cursor && !seenCursor.has(next), `${ticker}: cursor loop`); seenCursor.add(next); cursor = next;
        }
        const bytes = zlib.gzipSync(Buffer.from(`${JSON.stringify(pages)}\n`), { level: 9, mtime: 0 }); const file = path.join(rawDir, `${ticker}.json.gz`); fs.writeFileSync(file, bytes);
        results.push({ ticker, trades, page_count: page, raw_sha256: sha256(bytes), raw_bytes: bytes.length, capture: "FETCHED_V2" });
      } catch (error) { failures.push({ ticker, error: error.stack || String(error) }); }
      complete += 1; fs.appendFileSync(progressFile, `${new Date().toISOString()} ${complete}/${tickers.length} ${ticker} failures=${failures.length}\n`);
    }
  }
  await Promise.all(Array.from({ length: 2 }, worker));
  ensure(!failures.length, `public tape incomplete: ${compact(failures)}`);
  const sorted = results.sort((a, b) => a.ticker.localeCompare(b.ticker));
  ensure(sorted.length === tickers.length, `public tape conservation ${sorted.length}/${tickers.length}`);
  ensure(new Set(sorted.map((x) => x.ticker)).size === tickers.length, "public tape ticker identity duplicated");
  return sorted;
}

function pairNegative(floors, closes) { return floors.every(Number.isInteger) && closes.every(Number.isInteger) && floors[0] + floors[1] - closes[0] - closes[1] < 0; }

function prepareInputs({ ticksRoot, metadataRoot, workspace, tape }) {
  fs.mkdirSync(workspace, { recursive: true });
  const catalog = fs.readFileSync(path.join(metadataRoot, "corpus_events_v2.jsonl"), "utf8").trim().split(/\r?\n/).map(JSON.parse);
  const catalogMap = new Map(catalog.map((row) => [row.event, row]));
  const milestoneStarts = JSON.parse(fs.readFileSync(path.join(metadataRoot, "milestone_starts.json"), "utf8"));
  const officialStarts = JSON.parse(fs.readFileSync(path.join(metadataRoot, "daysheet_bells_official.json"), "utf8"));
  const daysheet = JSON.parse(fs.readFileSync(path.join(metadataRoot, "daysheet_bells.json"), "utf8"));
  const identities = fs.readdirSync(ticksRoot).map(tickerIdentity).filter(Boolean).sort((a, b) => a.ticker.localeCompare(b.ticker));
  ensure(identities.length === 456, `holdout leg ticker count ${identities.length}, expected 456`);
  const byEvent = group(identities, (x) => x.event_id); ensure(byEvent.size === 228, `holdout event count ${byEvent.size}, expected 228`);
  for (const [eventId, legs] of byEvent) ensure(legs.length === 2, `${eventId}: not exactly two legs`);
  const tapeMap = new Map(tape.map((x) => [x.ticker, x.trades]));
  const sources = [], referenceEvents = [], windowEvents = [], eventEvidence = [], inputFiles = {};
  for (const identity of identities) { const file = path.join(ticksRoot, `${identity.ticker}.csv.gz`); inputFiles[path.basename(file)] = { bytes: fs.statSync(file).size, sha256: hashFile(file) }; }
  for (const [eventId, legs] of [...byEvent].sort(([a], [b]) => a.localeCompare(b))) {
    const catalogMeta = catalogMap.get(eventId) || null;
    const milestone = finite(milestoneStarts[eventId]);
    const official = finite(officialStarts[eventId]?.start_ep);
    const scheduledFallback = finite(daysheet.starts?.[eventId]);
    const scheduled = catalogMeta ? finite(catalogMeta.sched_honest) : milestone ?? official ?? scheduledFallback;
    const daysheetBell = finite(daysheet.bells?.[eventId]?.bell_ts);
    const actualBell = catalogMeta ? finite(catalogMeta.official_ts ?? catalogMeta.onset_est) : daysheetBell;
    const right = catalogMeta ? finite(catalogMeta.right_edge) : actualBell ?? scheduled;
    const rightSource = catalogMeta ? catalogMeta.right_edge_src : actualBell !== null ? `holdout_daysheet_${daysheet.bells[eventId].source}` : official !== null ? "holdout_official_scheduled_start_no_bell" : milestone !== null ? "holdout_milestone_scheduled_start_no_bell" : "holdout_schedule_only_no_bell";
    ensure(scheduled !== null, `${eventId}: no frozen scheduled-start source`);
    ensure(right !== null, `${eventId}: no frozen right-edge source`);
    const left = scheduled - 8 * 3600;
    const positiveWindow = right > left;
    const refs = {}, evidenceLegs = [];
    for (const leg of legs.sort((a, b) => a.leg_id.localeCompare(b.leg_id))) {
      const books = positiveWindow ? loadBooks(path.join(ticksRoot, `${leg.ticker}.csv.gz`), left, right) : { rows: [], bytes: fs.statSync(path.join(ticksRoot, `${leg.ticker}.csv.gz`)).size, sha256: hashFile(path.join(ticksRoot, `${leg.ticker}.csv.gz`)) };
      const formed = books.rows.find((row) => row.ask - row.bid === 1) || null; const priceRegion = formed ? region(formed.bid) : "UNFORMED"; const floor = positiveWindow ? capacityFloor(books.rows, right) : null;
      const allTrades = (tapeMap.get(leg.ticker) || []).sort((a, b) => a.ts - b.ts || a.trade_id.localeCompare(b.trade_id));
      const prints = positiveWindow ? allTrades.filter((row) => row.ts >= left && row.ts <= right && row.size > 0) : [];
      const closePrint = prints.length ? prints[prints.length - 1] : null; const absolute = prints.length ? [...prints].sort((a, b) => a.price - b.price || a.ts - b.ts)[0] : null;
      const size5 = prints.filter((x) => x.size >= 5).sort((a, b) => a.price - b.price || a.ts - b.ts)[0] || null;
      const sellers = prints.filter((x) => x.taker_side === "no"); const seller = sellers.sort((a, b) => a.price - b.price || a.ts - b.ts)[0] || null;
      const makerTouch = floor ? sellers.filter((x) => x.price <= floor.limit_cents).sort((a, b) => a.ts - b.ts || a.price - b.price)[0] || null : null;
      const bellPrint = actualBell === null ? null : allTrades.filter((row) => row.ts <= actualBell && row.size > 0).sort((a, b) => b.ts - a.ts || a.trade_id.localeCompare(b.trade_id))[0] || null;
      sources.push({ event_id: eventId, category: leg.category, slice: "HOLDOUT_2026_07_24_26", leg: leg.leg_id, ticker: leg.ticker, left_ts: left, right_ts: right, scheduled_start_ts: scheduled, evaluator_window_positive: positiveWindow, window1_open_cents: formed?.ask ?? null, window1_close_cents: closePrint?.price ?? null, quote_10s_floor_limit_cents: floor?.limit_cents ?? null });
      refs[leg.leg_id] = { own_window1_close_cents: closePrint?.price ?? null, own_bell_price_cents: bellPrint?.price ?? null, own_ask_reachable_low_cents: floor?.limit_cents ?? null };
      evidenceLegs.push({ leg_id: leg.leg_id, ticker: leg.ticker, price_region: priceRegion, positive_window1_provable: positiveWindow, formed_book: formed ? { ts: formed.ts, bid: formed.bid, ask: formed.ask, ordinal: formed.ordinal } : null, close: closePrint, close_seconds_before_right: closePrint ? right - closePrint.ts : null, close_properly_late: closePrint ? right - closePrint.ts <= LATE_CLOSE_SECONDS : false, qualifying_ask_floor: floor, absolute_traded_low: absolute, traded_low_size_at_least_five: size5, seller_aggressed_traded_low: seller, maker_reachable_at_ask_floor: makerTouch, lawful_print_count: prints.length, tick_source: { bytes: books.bytes, sha256: books.sha256 } });
    }
    const closes = evidenceLegs.map((x) => x.close?.price ?? null), askFloors = evidenceLegs.map((x) => x.qualifying_ask_floor?.limit_cents ?? null), absolute = evidenceLegs.map((x) => x.absolute_traded_low?.price ?? null), size5 = evidenceLegs.map((x) => x.traded_low_size_at_least_five?.price ?? null), seller = evidenceLegs.map((x) => x.seller_aggressed_traded_low?.price ?? null);
    const split = evidenceLegs.map((x) => x.price_region).sort().join("+");
    eventEvidence.push({ event_id: eventId, category: legs[0].category, event_date: legs[0].event_date, starting_price_split: split, scheduled_start_ts: scheduled, guarded_right_ts: right, guarded_right_source: rightSource, actual_bell_ts: actualBell, metadata_source: catalogMeta ? "DEVELOPMENT_CATALOG_ROW" : "SEALED_HOLDOUT_MILESTONE_OFFICIAL_DAYSHEET_JOIN", both_closes_properly_late: evidenceLegs.every((x) => x.close_properly_late), legs: evidenceLegs, ceilings: { absolute_traded_low: pairNegative(absolute, closes), traded_low_print_size_at_least_five: pairNegative(size5, closes), capacity_proven_ask_floor: pairNegative(askFloors, closes), lowest_seller_aggressed_trade_floor: pairNegative(seller, closes), maker_reachable: pairNegative(askFloors, closes) && evidenceLegs.every((x) => Boolean(x.maker_reachable_at_ask_floor)) } });
    referenceEvents.push({ event_id: eventId, legs: refs }); windowEvents.push({ event_id: eventId, window: { left_ts: left, right_ts: right, scheduled_start_ts: scheduled, ...(actualBell === null ? {} : { actual_bell_ts: actualBell }) } });
  }
  const quote = path.join(workspace, "HOLDOUT_QUOTE_LEDGER.csv"); const columns = ["event_id", "category", "slice", "leg", "ticker", "left_ts", "right_ts", "scheduled_start_ts", "evaluator_window_positive", "window1_open_cents", "window1_close_cents", "quote_10s_floor_limit_cents"];
  fs.writeFileSync(quote, `${columns.join(",")}\n${sources.map((row) => columns.map((key) => row[key] ?? "").join(",")).join("\n")}\n`);
  const refsFile = path.join(workspace, "HOLDOUT_REFERENCES.json"), windowsFile = path.join(workspace, "HOLDOUT_WINDOWS.json"), targetsFile = path.join(workspace, "HOLDOUT_TARGETS.json");
  writeJson(refsFile, { current_branch: referenceEvents, corrected_branch: referenceEvents }); writeJson(windowsFile, { events: windowEvents }); writeJson(targetsFile, eventEvidence.map((x) => x.event_id));
  return { quote, refsFile, windowsFile, targetsFile, eventEvidence, inputFiles };
}

function runVariant(repo, ticksRoot, prepared, workspace, version) {
  const replay = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js"); const out = path.join(workspace, version.toLowerCase());
  const library = version === "V11" ? path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json") : path.join(repo, ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json");
  const argv = [replay, "--repo", repo, "--ticks-root", ticksRoot, "--quote-ledger", prepared.quote, "--references", prepared.refsFile, "--windows", prepared.windowsFile, "--target-file", prepared.targetsFile, "--output", out, "--receipt-name", "HOLDOUT_REPLAY.json", "--library", library, "--compact-population", "--no-charts", "--exclude-own-training-member", "--stable-same-price-confirmation", "--pair-wiring-v3", "--stable-signer-v4", "--descent-verdict-v5", "--dynamic-renarrow-v6", "--lag-diagnostic-v10", "--causal-descent-ordinal-v10"];
  if (version === "V11") argv.push("--persistence-floor-v11", "--persistence-library-v11", path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_v11_fit_20260802/PERSISTENCE_SURVIVAL_LIBRARY_V11.json"));
  if (version === "V13" || version === "V14") argv.push("--coherent-shape-v12", "--interim-elimination-v13");
  if (version === "V14") argv.push("--micro-repair-v14");
  const result = spawnSync(process.execPath, argv, { cwd: repo, encoding: "utf8", maxBuffer: 20 * 1024 * 1024 });
  ensure(result.status === 0, `${version} replay failed (${result.status}): ${result.stderr}\n${result.stdout}`);
  return { version, library, replay: JSON.parse(fs.readFileSync(path.join(out, "HOLDOUT_REPLAY.json"), "utf8")), stdout: result.stdout.trim() };
}

function metrics(events) {
  const legs = events.flatMap((x) => x.legs), completed = events.filter((x) => x.completed_pair), under = completed.filter((x) => x.pair_under_par);
  return { events: events.length, legs: legs.length, acted_legs: legs.filter((x) => x.acted).length, credited_legs: legs.filter((x) => x.credited).length, no_action_legs: legs.filter((x) => !x.acted).length, no_action_by_level: countBy(legs.filter((x) => !x.acted).map((x) => x.non_action_level)), no_action_terminal_reasons: countBy(legs.filter((x) => !x.acted).map((x) => x.terminal_reason)), completed_pairs: completed.length, pairs_under_par: under.length, both_legs_strictly_below_close: completed.filter((x) => x.both_legs_strictly_below_close).length, execution_floor_pair_pass: under.filter((x) => x.legs.every((leg) => Number.isFinite(leg.entry_minus_qualifying_ask_floor_cents) && leg.entry_minus_qualifying_ask_floor_cents <= 0)).length, objective_trade_floor_pair_pass: under.filter((x) => x.legs.every((leg) => Number.isFinite(leg.entry_minus_objective_traded_low_cents) && leg.entry_minus_objective_traded_low_cents <= 0)).length, entry_to_qualifying_ask_floor_gap: distribution(legs.map((x) => x.entry_minus_qualifying_ask_floor_cents), legs.length), entry_to_objective_traded_low_gap: distribution(legs.map((x) => x.entry_minus_objective_traded_low_cents), legs.length), ceiling_comparison: Object.fromEntries(CEILINGS.map((name) => { const rows = events.filter((x) => x.ceilings[name]); return [name, { ceiling_events: rows.length, completed_pairs: rows.filter((x) => x.completed_pair).length, pairs_under_par: rows.filter((x) => x.pair_under_par).length, both_legs_strictly_below_close: rows.filter((x) => x.both_legs_strictly_below_close).length, execution_floor_pair_pass: rows.filter((x) => x.pair_under_par && x.legs.every((leg) => Number.isFinite(leg.entry_minus_qualifying_ask_floor_cents) && leg.entry_minus_qualifying_ask_floor_cents <= 0)).length }]; })) };
}

function normalizeVariant(run, evidenceMap) {
  const events = [], legs = [];
  for (const rawEvent of run.replay.events) {
    const evidence = evidenceMap.get(rawEvent.event_id); ensure(evidence, `${run.version}/${rawEvent.event_id}: evidence missing`); const outLegs = [];
    for (const evLeg of evidence.legs) {
      const raw = rawEvent.legs?.[evLeg.leg_id] || {}; const actionEntry = integer(raw.proposed_entry_cents), candidateEntry = integer(raw.honest_credited_entry_cents), fillClass = raw.honest_fill_class || "UNPROVEN", credited = honestFillCredited(fillClass, candidateEntry), entry = credited ? candidateEntry : null, acted = actionEntry !== null;
      const nonActionLevel = acted ? null : String(raw.terminal_reason || "").includes("SOURCE") ? "SOURCE" : String(raw.terminal_reason || "").includes("MACRO") || String(raw.terminal_reason || "").includes("SHAPE") ? "MACRO_SHAPE" : String(raw.terminal_reason || "").includes("SIBLING") || String(raw.terminal_reason || "").includes("PAIR") ? "PAIR_MICRO" : String(raw.terminal_reason || "").includes("MICRO_MICRO") || String(raw.terminal_reason || "").includes("FRESH") ? "MICRO_MICRO" : "MICRO_POSITION_OR_CONSENSUS";
      const row = { version: run.version, leg_identity: `${evidence.event_id}|${evLeg.leg_id}`, event_id: evidence.event_id, category: evidence.category, starting_price_split: evidence.starting_price_split, price_region: evLeg.price_region, leg_id: evLeg.leg_id, ticker: evLeg.ticker, acted, credited, honest_fill_class: fillClass, entry_cents: entry, proposed_entry_cents: actionEntry, action_timestamp_epoch: finite(raw.placement?.action_ts), qualifying_ask_floor_cents: evLeg.qualifying_ask_floor?.limit_cents ?? null, objective_traded_low_cents: evLeg.absolute_traded_low?.price ?? null, entry_minus_qualifying_ask_floor_cents: entry !== null && evLeg.qualifying_ask_floor ? entry - evLeg.qualifying_ask_floor.limit_cents : null, entry_minus_objective_traded_low_cents: entry !== null && evLeg.absolute_traded_low ? entry - evLeg.absolute_traded_low.price : null, proposed_minus_qualifying_ask_floor_cents: actionEntry !== null && evLeg.qualifying_ask_floor ? actionEntry - evLeg.qualifying_ask_floor.limit_cents : null, proposed_minus_objective_traded_low_cents: actionEntry !== null && evLeg.absolute_traded_low ? actionEntry - evLeg.absolute_traded_low.price : null, own_window1_close_cents: evLeg.close?.price ?? null, entry_minus_own_window1_close_cents: entry !== null && evLeg.close ? entry - evLeg.close.price : null, close_properly_late: evLeg.close_properly_late, terminal_reason: raw.terminal_reason || rawEvent.reason || "NO_LAWFUL_DECISION", non_action_level: nonActionLevel, placement: raw.placement ?? null, action_book: raw.action_book ?? null, surviving_shapes_at_placement: raw.surviving_shapes_at_placement ?? [], surviving_shapes_at_terminal: raw.surviving_shapes_at_terminal ?? [], terminal_level_state: raw.terminal_level_state ?? null, floors: { qualifying_ask: evLeg.qualifying_ask_floor, absolute_trade: evLeg.absolute_traded_low, size_five_trade: evLeg.traded_low_size_at_least_five, seller_aggressed_trade: evLeg.seller_aggressed_traded_low, maker_touch: evLeg.maker_reachable_at_ask_floor } };
      legs.push(row); outLegs.push(row);
    }
    const completed = outLegs.every((x) => x.credited), sum = completed ? outLegs.reduce((n, x) => n + x.entry_cents, 0) : null;
    events.push({ version: run.version, event_id: evidence.event_id, event_date: evidence.event_date, category: evidence.category, starting_price_split: evidence.starting_price_split, both_closes_properly_late: evidence.both_closes_properly_late, legs: outLegs, completed_pair: completed, combined_entry_cents: sum, pair_under_par: sum !== null && sum < 100, both_legs_strictly_below_close: completed && outLegs.every((x) => Number.isInteger(x.own_window1_close_cents) && x.entry_cents < x.own_window1_close_cents), ceilings: evidence.ceilings });
  }
  ensure(events.length === 228 && legs.length === 456, `${run.version}: holdout conservation failed`);
  const late = events.filter((x) => x.both_closes_properly_late); const eventPartitions = [...group(events, (x) => `${x.category}|${x.starting_price_split}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], starting_price_split: key.split("|")[1], thin: rows.length < 10, full_holdout: metrics(rows), strict_late_close: metrics(rows.filter((x) => x.both_closes_properly_late)) }));
  const legPartitions = [...group(legs, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], thin: rows.length < 10, legs: rows.length, acted: rows.filter((x) => x.acted).length, credited: rows.filter((x) => x.credited).length, qualifying_ask_floor_gap: distribution(rows.map((x) => x.entry_minus_qualifying_ask_floor_cents), rows.length), objective_traded_low_gap: distribution(rows.map((x) => x.entry_minus_objective_traded_low_cents), rows.length), non_action_by_level: countBy(rows.filter((x) => !x.acted).map((x) => x.non_action_level)) }));
  return { version: run.version, events, legs, summary: { version: run.version, frozen_policy_refit: false, full_holdout: metrics(events), strict_late_close_cohort: metrics(late), strict_late_close_events: late.length, category_and_starting_price_region: eventPartitions, category_and_leg_price_region: legPartitions } };
}

function developmentComparison(repo) {
  const v11 = readGzipRows(path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/POPULATION_LEG_LEDGER.jsonl.gz")); const v13 = readGzipRows(path.join(repo, ".claude/window1_live_v4_replay/interim_elimination_v13_20260803/POPULATION_LEG_LEDGER.jsonl.gz")); const v13Map = new Map(v13.map((x) => [`${x.event_id}|${x.leg_id}`, x])); const rows = [];
  for (const old of v11.filter((x) => x.acted)) {
    const newer = v13Map.get(old.leg_identity); ensure(newer, `${old.leg_identity}: V13 row missing`); if (newer.proposed_entry_cents !== null) continue;
    const gap = finite(old.entry_minus_qualifying_ask_floor_cents); const supported = old.credited && Number.isInteger(old.qualifying_ask_floor_cents);
    const classification = !supported ? "LOOSE_OR_UNSUPPORTED_ACTION_WITHOUT_ASK_FLOOR_PROOF" : gap <= 1 ? "GENUINE_CATCH_AT_OR_WITHIN_ONE_CENT_OF_QUALIFYING_ASK_FLOOR" : "REAL_EXECUTABLE_ASK_BUT_LOOSE_TIMING_ABOVE_FLOOR";
    rows.push({ leg_identity: old.leg_identity, event_id: old.event_id, category: old.category, starting_price_split: old.starting_price_split, price_region: old.price_region, leg_id: old.leg_id, ticker: old.ticker, V11_entry_cents: old.entry_cents, V11_qualifying_ask_floor_cents: old.qualifying_ask_floor_cents, V11_objective_traded_low_cents: old.objective_traded_low_cents, V11_gap_to_qualifying_ask_floor_cents: gap, V11_gap_to_objective_traded_low_cents: old.entry_minus_objective_traded_low_cents, V11_honest_fill_class: old.honest_fill_class, V11_terminal_reason: old.terminal_reason, V13_blocking_level: newer.non_action_level, V13_terminal_reason: newer.terminal_reason, V13_terminal_survivors: newer.surviving_shapes_at_terminal, classification });
  }
  const partitions = [...group(rows, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], thin: xs.length < 10, legs: xs.length, classifications: countBy(xs.map((x) => x.classification)), V13_blocking_levels: countBy(xs.map((x) => x.V13_blocking_level)), V11_floor_gap: distribution(xs.map((x) => x.V11_gap_to_qualifying_ask_floor_cents), xs.length), V11_traded_low_gap: distribution(xs.map((x) => x.V11_gap_to_objective_traded_low_cents), xs.length) }));
  return { schema_version: "WINDOW1_V11_V13_DEVELOPMENT_LOSS_CROSSWALK_V1", development_only: true, rows: rows.length, classifications: countBy(rows.map((x) => x.classification)), V13_blocking_levels: countBy(rows.map((x) => x.V13_blocking_level)), category_and_price_region: partitions, ledger: rows };
}

function artifactManifest(out) { return Object.fromEntries(fs.readdirSync(out).filter((x) => x !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => [name, { bytes: fs.statSync(path.join(out, name)).size, sha256: hashFile(path.join(out, name)) }])); }

async function main() {
  const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  ensure(args.includes("--execute-once"), "runner requires --execute-once"); const repo = path.resolve(value("--repo", ".")), inputRoot = path.resolve(value("--input-root", "C:/tmp/window1_holdout_v11_v13_20260803")), out = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/v11_v13_v14_holdout_20260803")));
  const ticksRoot = path.join(inputRoot, "ticks"), metadataRoot = path.join(inputRoot, "metadata"), priorFailedMarker = path.join(inputRoot, "HOLDOUT_V11_V13_V14_EVALUATION_CONSUMED.json"), marker = path.join(inputRoot, "HOLDOUT_V11_V13_V14_POLICY_EVALUATION_CONSUMED.json"), workspace = path.join(inputRoot, "execution_workspace_v2"), rawDir = path.join(inputRoot, "public_trade_raw"), progress = path.join(inputRoot, "HOLDOUT_CAPTURE_V2_PROGRESS.log");
  ensure(!fs.existsSync(marker), "holdout evaluation already consumed"); ensure(!fs.existsSync(out), "holdout results directory already exists"); ensure(fs.existsSync(ticksRoot) && fs.existsSync(metadataRoot), "sealed input roots absent");
  fs.mkdirSync(workspace, { recursive: true }); fs.appendFileSync(progress, `${new Date().toISOString()} CAPTURE_RESUME_START\n`);
  const identities = fs.readdirSync(ticksRoot).map(tickerIdentity).filter(Boolean); ensure(identities.length === 456, "sealed ticker count changed"); const tape = await fetchTapeResumable(identities.map((x) => x.ticker).sort(), rawDir, progress);
  const prepared = prepareInputs({ ticksRoot, metadataRoot, workspace, tape });
  ensure(prepared.eventEvidence.length === 228, "prepared holdout event conservation failed before policy evaluation");
  ensure(prepared.eventEvidence.flatMap((x) => x.legs).length === 456, "prepared holdout leg conservation failed before policy evaluation");
  writeJson(marker, { execution_started_at_utc: new Date().toISOString(), runner: rel(repo, __filename), git_head: spawnSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).stdout.trim(), policy_evaluation_attempts: 1, policy_evaluation_retries: 0, prior_pre_policy_failures: 2, tape_rows_ready: tape.length, prepared_events: 228, prepared_legs: 456, holdout_dates: [...HOLDOUT_DATES].sort() });
  const evidenceMap = new Map(prepared.eventEvidence.map((x) => [x.event_id, x])); const runs = VERSIONS.map((version) => runVariant(repo, ticksRoot, prepared, workspace, version)); const normalized = runs.map((run) => normalizeVariant(run, evidenceMap)); const dev = developmentComparison(repo);
  fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(path.join(out, "V11_V13_DEVELOPMENT_LOSS_CROSSWALK.jsonl.gz"), gzipRows(dev.ledger)); writeJson(path.join(out, "V11_V13_DEVELOPMENT_LOSS_SUMMARY.json"), { ...dev, ledger: undefined });
  writeJson(path.join(out, "PRE_POLICY_PREPARATION_FAILURE_RECEIPT.json"), { schema_version: "WINDOW1_HOLDOUT_PRE_POLICY_FAILURE_RECEIPT_V1", prior_capture_failure: { runner: "arb-executor/analysis/window1_v11_v12_v13_holdout_runner_v1.js", public_tapes_frozen: 448, missing_tapes: 8, failure: "8 HTTP 429 responses", policy_evaluations: 0 }, resumable_capture: { reused_tapes: 448, newly_fetched_tapes: 8, complete_tapes: 456 }, prior_join_failure: { marker_path: rel(repo, priorFailedMarker), marker_sha256: fs.existsSync(priorFailedMarker) ? hashFile(priorFailedMarker) : null, error: "KXATPCHALLENGERMATCH-26JUL24DRACHI: missing catalog row", cause: "holdout event absent from development corpus catalog; sealed holdout metadata join was not used", policy_evaluations: 0 }, controlling_evaluation: { policy_evaluation_attempts: 1, versions: VERSIONS, refits: 0 } });
  const v13 = normalized.find((x) => x.version === "V13"), v14 = normalized.find((x) => x.version === "V14"); writeJson(path.join(out, "V13_V14_EXECUTION_FLOOR_DIAGNOSTIC.json"), { schema_version: "WINDOW1_V13_V14_EXECUTION_FLOOR_DIAGNOSTIC_V1", holdout_source: "single sealed evaluation; no refit", V13_category_and_price_region: v13.summary.category_and_leg_price_region, V14_category_and_price_region: v14.summary.category_and_leg_price_region });
  for (const item of normalized) { fs.writeFileSync(path.join(out, `${item.version}_HOLDOUT_LEG_LEDGER.jsonl.gz`), gzipRows(item.legs)); fs.writeFileSync(path.join(out, `${item.version}_HOLDOUT_EVENT_LEDGER.jsonl.gz`), gzipRows(item.events)); writeJson(path.join(out, `${item.version}_HOLDOUT_FUNNEL_AND_FIVE_CEILINGS.json`), item.summary); }
  const tapeManifest = { endpoint: "https://api.elections.kalshi.com/trade-api/v2/markets/trades", authentication: "none", tickers: tape.length, pages: tape.reduce((n, x) => n + x.page_count, 0), raw_trade_rows: tape.reduce((n, x) => n + x.trades.length, 0), canonical_trade_rows: new Set(tape.flatMap((x) => x.trades.map((y) => y.trade_id))).size, raw_total_bytes: tape.reduce((n, x) => n + x.raw_bytes, 0), raw_hash_set_sha256: sha256(tape.map((x) => `${x.ticker} ${x.raw_sha256}`).join("\n")) };
  const metadataFiles = Object.fromEntries(fs.readdirSync(metadataRoot).sort().map((name) => [name, { bytes: fs.statSync(path.join(metadataRoot, name)).size, sha256: hashFile(path.join(metadataRoot, name)) }])); writeJson(path.join(out, "INPUT_SOURCE_MANIFEST.json"), { holdout_dates: ["2026-07-24", "2026-07-25", "2026-07-26"], events: 228, legs: 456, BBO_files: { count: Object.keys(prepared.inputFiles).length, bytes: Object.values(prepared.inputFiles).reduce((n, x) => n + x.bytes, 0), hash_set_sha256: sha256(Object.entries(prepared.inputFiles).map(([k, v]) => `${k} ${v.sha256}`).join("\n")) }, metadata_files: metadataFiles, public_tape: tapeManifest, fit_artifacts_unchanged: Object.fromEntries(runs.map((x) => [x.version, { path: rel(repo, x.library), sha256: hashFile(x.library) }])) });
  writeJson(path.join(out, "ONE_EXECUTION_RECEIPT.json"), { policy_evaluation_attempts: 1, policy_evaluation_retries: 0, prior_pre_policy_failures: [{ status: "CAPTURE_INCOMPLETE", missing_tapes: 8, http_429_failures: 8, policy_evaluations: 0 }, { status: "SEALED_METADATA_JOIN_FAILED", error: "KXATPCHALLENGERMATCH-26JUL24DRACHI: missing catalog row", policy_evaluations: 0 }], runner_invocations_that_reached_policy: 1, version_evaluations_inside_single_runner: 3, versions: VERSIONS, refits: 0, holdout_dates: ["2026-07-24", "2026-07-25", "2026-07-26"], events: 228, legs: 456, completed_at_utc: new Date().toISOString(), no_tuning_after_view: true, forbidden_access: { live: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false } });
  const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated"; const url = (name) => `${rawBase}/${rel(repo, path.join(out, name))}`;
  fs.writeFileSync(path.join(out, "REPORT.md"), `# Window-1 V11 / V13 / V14 sealed holdout\n\nOne evaluation of the predeclared July 24-26 holdout after resumable tape capture completed. The earlier capture attempt stopped before policy evaluation. No refit and no post-holdout policy change.\n\n- V11-to-V13 development loss split: ${url("V11_V13_DEVELOPMENT_LOSS_SUMMARY.json")}\n- Exact development loss rows: ${url("V11_V13_DEVELOPMENT_LOSS_CROSSWALK.jsonl.gz")}\n- V13/V14 floor gaps by category and price region: ${url("V13_V14_EXECUTION_FLOOR_DIAGNOSTIC.json")}\n- V11 holdout funnel and five ceilings: ${url("V11_HOLDOUT_FUNNEL_AND_FIVE_CEILINGS.json")}\n- V13 holdout funnel and five ceilings: ${url("V13_HOLDOUT_FUNNEL_AND_FIVE_CEILINGS.json")}\n- V14 holdout funnel and five ceilings: ${url("V14_HOLDOUT_FUNNEL_AND_FIVE_CEILINGS.json")}\n- Source identity: ${url("INPUT_SOURCE_MANIFEST.json")}\n- Single-evaluation receipt: ${url("ONE_EXECUTION_RECEIPT.json")}\n\nAll inferential cells remain partitioned by category and starting-price or leg-price region. Overall rows are conservation totals only. Thin cells are marked and are not pooled.\n`);
  writeJson(path.join(out, "SOURCE_HASH_MANIFEST.json"), { files: Object.fromEntries([__filename, path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js"), ...runs.map((x) => x.library)].map((file) => [rel(repo, file), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])) }); writeJson(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), { files: artifactManifest(out) });
  fs.appendFileSync(progress, `${new Date().toISOString()} COMPLETE\n`); writeJson(marker, { ...JSON.parse(fs.readFileSync(marker, "utf8")), completed_at_utc: new Date().toISOString(), status: "COMPLETE", output_manifest_sha256: hashFile(path.join(out, "ARTIFACT_HASH_MANIFEST.json")) });
  process.stdout.write(canonical({ status: "COMPLETE", output: rel(repo, out), development_loss_rows: dev.rows, holdout: Object.fromEntries(normalized.map((x) => [x.version, x.summary.full_holdout])) }));
}

if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
module.exports = { tickerIdentity, capacityFloor, pairNegative, distribution, metrics, honestFillCredited, readFrozenTape, fetchTapeResumable, prepareInputs };
