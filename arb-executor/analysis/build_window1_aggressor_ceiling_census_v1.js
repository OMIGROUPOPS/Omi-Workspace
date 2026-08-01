#!/usr/bin/env node
"use strict";

// Score-free aggressor-flow and maker-vs-take opportunity census.
// The builder reads only the frozen July 12-20 D=804 development artifacts.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const POPULATION = 804;
const DWELL_SECONDS = 10;
const DISPLAYED_QUANTITY = 5;
const CONTROL_TAKE_CEILING = 516;
const OUT_REL = ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801";
const QUOTE_REL = ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv";
const GUARD_REL = ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl";
const FLOOR_SCAN_REL = ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json";
const CONTROL_CEILING_REL = ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/ASK_10S_FIVE_CONTRACT_CEILING.json";

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(data) { return crypto.createHash("sha256").update(data).digest("hex"); }
function fileHash(file) { return sha256(fs.readFileSync(file)); }
function parseCsv(file) {
  const lines = fs.readFileSync(file, "utf8").trimEnd().split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map((line) => Object.fromEntries(line.split(",").map((value, index) => [headers[index], value])));
}
function readJsonl(file) {
  return fs.readFileSync(file, "utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
}
function int(value) { if (value === null || value === undefined || value === "" || typeof value === "boolean") return null; const n = Number(value); return Number.isInteger(n) ? n : null; }
function finite(value) { if (value === null || value === undefined || value === "" || typeof value === "boolean") return null; const n = Number(value); return Number.isFinite(n) ? n : null; }
function region(price) {
  if (!Number.isInteger(price)) return "UNKNOWN";
  return price <= 25 ? "LE25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "GE76";
}
function timeBand(seconds) {
  if (!Number.isFinite(seconds)) return "NOT_BOUND";
  if (seconds < 0) return "POST_REFERENCE";
  if (seconds <= 600) return "T_MINUS_0_10M";
  if (seconds <= 1800) return "T_MINUS_10_30M";
  if (seconds <= 3600) return "T_MINUS_30_60M";
  if (seconds <= 7200) return "T_MINUS_60_120M";
  if (seconds <= 14400) return "T_MINUS_120_240M";
  return "T_MINUS_GT_240M";
}
function counter() { return { prints: 0, buyer_aggressed: 0, seller_aggressed: 0, unknown_aggressor: 0 }; }
function addCounter(map, key, side) {
  if (!map.has(key)) map.set(key, counter());
  const row = map.get(key); row.prints += 1;
  row[side === "BUY" ? "buyer_aggressed" : side === "SELL" ? "seller_aggressed" : "unknown_aggressor"] += 1;
}
function rowsFromCounter(map, dimensions) {
  return [...map].sort(([a], [b]) => a.localeCompare(b)).map(([key, values]) => {
    const parts = key.split("|");
    return { ...Object.fromEntries(dimensions.map((name, index) => [name, parts[index]])), ...values, buyer_rate: values.prints ? values.buyer_aggressed / values.prints : null, seller_rate: values.prints ? values.seller_aggressed / values.prints : null, unknown_rate: values.prints ? values.unknown_aggressor / values.prints : null };
  });
}
function asksAtOrBelow(snapshot, price) {
  return (snapshot.asks || []).reduce((sum, level) => {
    const p = int(level[0]), size = finite(level[1]);
    return p !== null && size !== null && size > 0 && p <= price ? sum + size : sum;
  }, 0);
}
function validSnapshot(raw, ordinal, left, right) {
  const ts = finite(raw.ts), bid = int(raw.best_bid), ask = int(raw.best_ask);
  if (ts === null || ts < left || ts > right || bid === null || ask === null || bid <= 0 || ask > 99 || bid > ask) return null;
  const bidSize = (raw.bids || []).filter((x) => int(x[0]) === bid).reduce((s, x) => s + Math.max(0, finite(x[1]) || 0), 0);
  const askSize = (raw.asks || []).filter((x) => int(x[0]) === ask).reduce((s, x) => s + Math.max(0, finite(x[1]) || 0), 0);
  if (!(bidSize > 0) || !(askSize > 0)) return null;
  return { ...raw, ts, bid, ask, ordinal, spread: ask - bid, bid_size: bidSize, ask_size: askSize };
}
function takeFloor(snapshots, right, strictLaterCapacity = false) {
  let best = null;
  for (let start = 0; start < snapshots.length;) {
    const ask = snapshots[start].ask;
    let end = start + 1;
    while (end < snapshots.length && snapshots[end].ask === ask) end += 1;
    const nextTs = end < snapshots.length ? snapshots[end].ts : right;
    const episodeEnd = Math.min(right, nextTs);
    let proof = null;
    for (let i = start; i < end; i += 1) {
      const row = snapshots[i];
      if (strictLaterCapacity && row.ts - snapshots[start].ts < DWELL_SECONDS) continue;
      const capacity = asksAtOrBelow(row, ask);
      if (capacity >= DISPLAYED_QUANTITY) { proof = { row, capacity }; break; }
    }
    if (proof && episodeEnd - snapshots[start].ts >= DWELL_SECONDS) {
      const candidate = {
        price_cents: ask,
        episode_start_ts: snapshots[start].ts,
        proof_ts: proof.row.ts,
        episode_dwell_seconds: episodeEnd - snapshots[start].ts,
        capacity_receipt_offset_seconds: proof.row.ts - snapshots[start].ts,
        displayed_ask_capacity_at_or_below_x: proof.capacity,
        proof_snapshot_ordinal: proof.row.ordinal,
      };
      if (!best || candidate.price_cents < best.price_cents || (candidate.price_cents === best.price_cents && candidate.proof_ts < best.proof_ts)) best = candidate;
    }
    start = end;
  }
  return best;
}
function latestBookAtPrint(snapshots, printTs) {
  let low = 0, high = snapshots.length;
  while (low < high) { const mid = (low + high) >> 1; if (snapshots[mid].ts <= printTs) low = mid + 1; else high = mid; }
  if (!low) return { status: "NO_PRIOR_LAWFUL_BBO", row: null };
  const row = snapshots[low - 1];
  if (row.ts === printTs) return { status: "EQUAL_TIMESTAMP_CROSS_STREAM_ORDER_UNBOUND", row: null };
  return { status: "LATEST_LAWFUL_BBO_AT_OR_BEFORE_PRINT", row };
}
function gzipDeterministic(text) {
  return zlib.gzipSync(Buffer.from(text), { level: 9, mtime: 0 });
}
function markdown(result) {
  const c = result.ceiling_census;
  return `# Window-1 ask-side aggressor and ceiling census\n\n` +
    `Score-free descriptive census over the frozen July 12-20 D=${POPULATION}. Holdout is not read.\n\n` +
    `## Law\n\n` +
    `- BUY means \`taker_side=yes\`: an aggressor lifted the ask.\n` +
    `- SELL means \`taker_side=no\`: an aggressor hit the bid.\n` +
    `- Maker-reachable is ex-post only: at least one positive-size SELL print exists on the leg. Its floor is the lowest such print. It does not prove queue priority or five-lot capacity.\n` +
    `- The controlling take ceiling uses the frozen raw-tick ask floor: a same-price ask episode with dwell >=${DWELL_SECONDS}s and displayed ask capacity >=${DISPLAYED_QUANTITY} at or below X. The stricter requirement that the capacity receipt itself arrive >=${DWELL_SECONDS}s later is disclosed separately and does not rewrite the frozen 516.\n` +
    `- Pair ceiling requires both legs reachable, both independent Window-1 closes available, and combined floor-minus-close delta <0.\n` +
    `- Exact time-to-bell partitions use only V5 \`exact_start_utc\`. Proxy clocks are not promoted to actual bells. Scheduled-clock partitions are separate.\n\n` +
    `## Conservation\n\n` +
    `- Events: ${result.population.events}; legs: ${result.population.legs}.\n` +
    `- Lawful admitted prints: ${result.print_conservation.lawful_admitted_prints}; BUY ${result.print_conservation.buyer_aggressed}; SELL ${result.print_conservation.seller_aggressed}; UNKNOWN ${result.print_conservation.unknown_aggressor}.\n` +
    `- Spread bound: ${result.print_conservation.spread_bound}; no prior BBO: ${result.print_conservation.no_prior_bbo}; exact equal-timestamp ambiguity: ${result.print_conservation.equal_timestamp_cross_stream_ambiguous}.\n\n` +
    `## Ex-post opportunity ceilings\n\n` +
    `| Measure | Events |\n|---|---:|\n` +
    `| Controlling take ceiling | ${CONTROL_TAKE_CEILING} |\n` +
    `| Reproduced take ceiling | ${c.summary.take_pair_combined_negative} |\n` +
    `| Both legs take-reachable | ${c.summary.take_both_legs_reachable} |\n` +
    `| Maker pair combined-negative | ${c.summary.maker_pair_combined_negative} |\n` +
    `| Both legs maker-reachable | ${c.summary.maker_both_legs_reachable} |\n` +
    `| Missing independent close blocks comparison | ${c.summary.reference_missing_events} |\n\n` +
    `The maker pair count ${c.summary.maker_pair_combined_negative} is the subset of the frozen 516 pair-floor events where both targets have a SELL print at or below X. The broader ${c.summary.maker_both_legs_reachable} count spans D=804 and is not itself a combined-negative ceiling.\n\n` +
    `Raw-tick 516 reconciliation: guarded-cache same-law reconstruction ${c.guarded_cache_floor_reconciliation.guarded_cache_same_law_rederived_ceiling}; stricter later-capacity-receipt variant ${c.guarded_cache_floor_reconciliation.guarded_cache_strict_later_capacity_ceiling}. Exact identities and source-grain explanation are frozen in \`CEILING_CENSUS.json\`.\n\n` +
    `All headline totals have mandatory category and starting-price-split partitions in \`CEILING_CENSUS.json\`. All flow results are partitioned in \`AGGRESSOR_SPLIT.json\`; no pooled median is emitted.\n`;
}

function main() {
  const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(value("--repo", "."));
  const privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private"));
  const out = path.resolve(value("--output", path.join(repo, OUT_REL)));
  const quoteFile = path.join(repo, QUOTE_REL), guardFile = path.join(repo, GUARD_REL), floorFile = path.join(repo, FLOOR_SCAN_REL), controlFile = path.join(repo, CONTROL_CEILING_REL), cacheRoot = path.join(privateRoot, "fit-local/guarded-cache-v3");
  const quoteRows = parseCsv(quoteFile), guards = readJsonl(guardFile), guardMap = new Map(guards.map((row) => [row.event_id, row]));
  const floorScan = JSON.parse(fs.readFileSync(floorFile, "utf8")), controlCeiling = JSON.parse(fs.readFileSync(controlFile, "utf8"));
  if (floorScan.row_count !== POPULATION * 2 || floorScan.rows.length !== POPULATION * 2) throw new Error("frozen floor scan is not 1,608 legs");
  if (controlCeiling.population_events !== POPULATION || controlCeiling.capacity_proven_ask_only_10s_negative_ceiling !== CONTROL_TAKE_CEILING) throw new Error("frozen controlling ceiling is not 516/804");
  const floorMap = new Map(floorScan.rows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const controlEventMap = new Map(controlCeiling.events.map((row) => [row.event_id, row]));
  if (quoteRows.length !== POPULATION * 2 || new Set(quoteRows.map((row) => row.event_id)).size !== POPULATION) throw new Error("quote ledger is not D=804 x two legs");
  if (guards.length !== POPULATION || guardMap.size !== POPULATION) throw new Error("V5 guard ledger is not D=804");
  const byEvent = new Map();
  for (const row of quoteRows) { if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row); }

  const maps = {
    category_leg_region: new Map(), category_print_region: new Map(), category_leg_region_spread: new Map(),
    category_leg_region_schedule: new Map(), category_leg_region_exact_bell: new Map(),
  };
  const legRows = [], eventRows = [], cacheManifest = {};
  let admitted = 0, buy = 0, sell = 0, unknown = 0, spreadBound = 0, noPrior = 0, equalTs = 0, rawInCorridorCensored = 0;

  for (const [eventId, sourceLegs] of [...byEvent].sort(([a], [b]) => a.localeCompare(b))) {
    if (sourceLegs.length !== 2) throw new Error(`event leg count mismatch: ${eventId}`);
    const guard = guardMap.get(eventId); if (!guard) throw new Error(`missing V5 row: ${eventId}`);
    const flags = new Set(sourceLegs.map((row) => String(row.evaluator_window_positive).toLowerCase() === "true"));
    if (flags.size !== 1 || ([...flags][0] && !Boolean(guard.positive_window1_provable))) throw new Error(`boundary status mismatch: ${eventId}`);
    const cacheFile = path.join(cacheRoot, `${eventId}.json.gz`), bytes = fs.readFileSync(cacheFile), cache = JSON.parse(zlib.gunzipSync(bytes));
    if (cache.event_id !== eventId || !Array.isArray(cache.legs) || cache.legs.length !== 2) throw new Error(`cache identity mismatch: ${eventId}`);
    cacheManifest[`${eventId}.json.gz`] = { bytes: bytes.length, sha256: sha256(bytes), cache_key: cache.cache_key, cache_version: cache.cache_version };
    const perEvent = [];
    for (const source of sourceLegs.sort((a, b) => a.leg.localeCompare(b.leg))) {
      const left = finite(source.left_ts), right = finite(source.right_ts), scheduled = finite(source.scheduled_start_ts);
      if (left === null || right === null || scheduled === null) throw new Error(`invalid source corridor: ${eventId}/${source.leg}`);
      const cacheLeg = cache.legs.find((row) => row.leg === source.leg && row.ticker === source.ticker);
      if (!cacheLeg) throw new Error(`cache leg mismatch: ${eventId}/${source.leg}`);
      const snapshots = (cacheLeg.snapshots || []).map((row, ordinal) => validSnapshot(row, ordinal, left, right)).filter(Boolean).sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
      const frozenFloorRow = floorMap.get(`${eventId}|${source.leg}`); if (!frozenFloorRow || frozenFloorRow.ticker !== source.ticker) throw new Error(`frozen floor identity mismatch: ${eventId}/${source.leg}`);
      const formed = snapshots.find((row) => row.spread === 1), legRegion = String(frozenFloorRow.price_region || region(formed?.bid ?? null)), positiveBoundary = String(source.evaluator_window_positive).toLowerCase() === "true";
      const exactBell = guard.exact_start_utc ? Date.parse(guard.exact_start_utc) / 1000 : null;
      const seen = new Map(), prints = [];
      for (const raw of cacheLeg.prints || []) {
        const ts = finite(raw.ts), price = int(raw.price), size = finite(raw.size), receipt = String(raw.trade_id || "");
        if (ts === null || ts < left || ts > right || price === null || !(size > 0) || !receipt) continue;
        const normalized = { ts, price, size, receipt, taker_side: String(raw.taker_side || "") };
        const prior = seen.get(receipt); if (prior && canonical(prior) !== canonical(normalized)) throw new Error(`conflicting duplicate print: ${receipt}`);
        seen.set(receipt, normalized);
      }
      for (const row of seen.values()) prints.push(row);
      prints.sort((a, b) => a.ts - b.ts || a.receipt.localeCompare(b.receipt));
      if (!positiveBoundary) rawInCorridorCensored += prints.length;
      const digest = crypto.createHash("sha256"), sideCounts = counter(), sellerPrints = [];
      if (positiveBoundary) for (const print of prints) {
        const side = print.taker_side === "yes" ? "BUY" : print.taker_side === "no" ? "SELL" : "UNKNOWN";
        const book = latestBookAtPrint(snapshots, print.ts), spreadClass = book.row ? String(book.row.spread) : book.status;
        const scheduleBand = timeBand(scheduled - print.ts), bellBand = exactBell === null ? "BELL_NOT_EXACTLY_BOUND" : timeBand(exactBell - print.ts);
        admitted += 1; sideCounts.prints += 1;
        if (side === "BUY") { buy += 1; sideCounts.buyer_aggressed += 1; }
        else if (side === "SELL") { sell += 1; sideCounts.seller_aggressed += 1; sellerPrints.push(print); }
        else { unknown += 1; sideCounts.unknown_aggressor += 1; }
        if (book.row) spreadBound += 1; else if (book.status.startsWith("EQUAL")) equalTs += 1; else noPrior += 1;
        addCounter(maps.category_leg_region, `${source.category}|${legRegion}`, side);
        addCounter(maps.category_print_region, `${source.category}|${region(print.price)}`, side);
        addCounter(maps.category_leg_region_spread, `${source.category}|${legRegion}|${spreadClass}`, side);
        addCounter(maps.category_leg_region_schedule, `${source.category}|${legRegion}|${scheduleBand}`, side);
        addCounter(maps.category_leg_region_exact_bell, `${source.category}|${legRegion}|${bellBand}`, side);
        digest.update(`${print.receipt}|${print.ts}|${print.price}|${print.size}|${side}|${spreadClass}|${scheduleBand}|${bellBand}\n`);
      }
      const makerFloor = sellerPrints.length ? sellerPrints.reduce((best, row) => row.price < best.price || (row.price === best.price && row.ts < best.ts) ? row : best) : null;
      const cacheDerivedTakerFloor = positiveBoundary ? takeFloor(snapshots, right) : null;
      const cacheStrictLaterTakerFloor = positiveBoundary ? takeFloor(snapshots, right, true) : null;
      const takerFloor = frozenFloorRow.capacity_proven_floor || null;
      const makerTargetTouch = takerFloor ? sellerPrints.filter((row) => row.price <= takerFloor.limit_cents).sort((a, b) => a.ts - b.ts || a.receipt.localeCompare(b.receipt))[0] || null : null;
      const close = int(source.window1_close_cents), publishedFloor = int(source.quote_10s_floor_limit_cents);
      const legRow = {
        event_id: eventId, category: source.category, period: source.slice, leg: source.leg, ticker: source.ticker,
        positive_window1_provable: positiveBoundary, left_ts: left, guarded_right_ts: right, scheduled_start_ts: scheduled,
        exact_bell_ts: exactBell, exact_bell_status: exactBell === null ? "NOT_EXACTLY_BOUND" : "V5_EXACT_START",
        starting_price_region: legRegion, window1_close_cents: close,
        lawful_prints: positiveBoundary ? prints.length : 0, censored_corridor_prints: positiveBoundary ? 0 : prints.length,
        aggressor_counts: sideCounts, classified_print_stream_sha256: digest.digest("hex"),
        seller_aggressed_floor: makerFloor ? { price_cents: makerFloor.price, ts: makerFloor.ts, receipt: makerFloor.receipt, size: makerFloor.size, aggressor_side: "SELL", aggressor_source_law: "taker_side=no" } : null,
        frozen_516_target_price_cents: takerFloor?.limit_cents ?? null,
        maker_reachable_at_frozen_target: makerTargetTouch ? { target_price_cents: takerFloor.limit_cents, print_price_cents: makerTargetTouch.price, ts: makerTargetTouch.ts, receipt: makerTargetTouch.receipt, size: makerTargetTouch.size, aggressor_side: "SELL", aggressor_source_law: "taker_side=no" } : null,
        take_reachable_floor: takerFloor,
        guarded_cache_rederived_take_floor: cacheDerivedTakerFloor,
        guarded_cache_strict_later_capacity_floor: cacheStrictLaterTakerFloor,
        frozen_floor_vs_guarded_cache_rederivation: takerFloor === null && cacheDerivedTakerFloor === null ? "BOTH_ABSENT" : takerFloor !== null && cacheDerivedTakerFloor !== null && takerFloor.limit_cents === cacheDerivedTakerFloor.price_cents ? "IDENTICAL_PRICE" : "DIFFERENT_SOURCE_OR_FLOOR",
        published_ask_only_10s_floor_cents: publishedFloor,
        capacity_floor_vs_published: !positiveBoundary ? "BOUNDARY_CENSORED" : takerFloor === null ? (publishedFloor === null ? "BOTH_ABSENT" : "CAPACITY_PROOF_ABSENT") : publishedFloor === null ? "CAPACITY_FLOOR_ONLY" : takerFloor.limit_cents === publishedFloor ? "IDENTICAL" : takerFloor.limit_cents > publishedFloor ? "CAPACITY_RAISED_FLOOR" : "CAPACITY_LOWER_THAN_PUBLISHED_BLOCK",
      };
      if (legRow.capacity_floor_vs_published.endsWith("BLOCK")) throw new Error(`capacity floor lower than published ask floor: ${eventId}/${source.leg}`);
      legRows.push(legRow); perEvent.push(legRow);
    }
    const controlEvent = controlEventMap.get(eventId); if (!controlEvent) throw new Error(`missing frozen ceiling event: ${eventId}`);
    const category = perEvent[0].category, regionSplit = controlEvent.price_region_pair;
    const closes = perEvent.map((row) => row.window1_close_cents), takeFloors = perEvent.map((row) => row.frozen_516_target_price_cents), makerTouches = perEvent.map((row) => row.maker_reachable_at_frozen_target), cacheFloors = perEvent.map((row) => row.guarded_cache_rederived_take_floor?.price_cents ?? null), strictCacheFloors = perEvent.map((row) => row.guarded_cache_strict_later_capacity_floor?.price_cents ?? null);
    const referenceAvailable = closes.every(Number.isInteger), makerBoth = makerTouches.every(Boolean), takeBoth = takeFloors.every(Number.isInteger);
    eventRows.push({
      event_id: eventId, category, period: perEvent[0].period, starting_price_split: regionSplit,
      positive_window1_provable: perEvent.every((row) => row.positive_window1_provable),
      reference_available_both_legs: referenceAvailable, closes, frozen_take_floor_targets: takeFloors,
      controlling_516_member: controlEvent.capacity_proven_negative === true,
      maker_target_touches: makerTouches,
      guarded_cache_rederived_take_floors: cacheFloors,
      guarded_cache_rederived_negative: cacheFloors.every(Number.isInteger) && referenceAvailable ? cacheFloors[0] + cacheFloors[1] - closes[0] - closes[1] < 0 : false,
      guarded_cache_strict_later_take_floors: strictCacheFloors,
      guarded_cache_strict_later_negative: strictCacheFloors.every(Number.isInteger) && referenceAvailable ? strictCacheFloors[0] + strictCacheFloors[1] - closes[0] - closes[1] < 0 : false,
      maker_both_legs_reachable: makerBoth, take_both_legs_reachable: takeBoth,
      take_combined_delta_cents: takeBoth && referenceAvailable ? takeFloors[0] + takeFloors[1] - closes[0] - closes[1] : null,
      maker_pair_combined_negative: makerBoth && controlEvent.capacity_proven_negative === true,
      take_pair_combined_negative: controlEvent.capacity_proven_negative === true,
    });
  }

  function ceilingSummary(rows) {
    return {
      events: rows.length,
      maker_both_legs_reachable: rows.filter((r) => r.maker_both_legs_reachable).length,
      maker_both_legs_reachable_event_ids: rows.filter((r) => r.maker_both_legs_reachable).map((r) => r.event_id),
      take_both_legs_reachable: rows.filter((r) => r.take_both_legs_reachable).length,
      take_both_legs_reachable_event_ids: rows.filter((r) => r.take_both_legs_reachable).map((r) => r.event_id),
      maker_pair_combined_negative: rows.filter((r) => r.maker_pair_combined_negative === true).length,
      maker_pair_combined_negative_event_ids: rows.filter((r) => r.maker_pair_combined_negative === true).map((r) => r.event_id),
      take_pair_combined_negative: rows.filter((r) => r.take_pair_combined_negative === true).length,
      take_pair_combined_negative_event_ids: rows.filter((r) => r.take_pair_combined_negative === true).map((r) => r.event_id),
      reference_missing_events: rows.filter((r) => !r.reference_available_both_legs).length,
      reference_missing_event_ids: rows.filter((r) => !r.reference_available_both_legs).map((r) => r.event_id),
      boundary_censored_events: rows.filter((r) => !r.positive_window1_provable).length,
      boundary_censored_event_ids: rows.filter((r) => !r.positive_window1_provable).map((r) => r.event_id),
    };
  }
  const summary = ceilingSummary(eventRows);
  if (summary.take_pair_combined_negative !== CONTROL_TAKE_CEILING) throw new Error(`controlling 516 take ceiling mismatch: ${summary.take_pair_combined_negative}`);
  const partitions = [];
  const partMap = new Map();
  for (const row of eventRows) { const key = `${row.category}|${row.starting_price_split}`; if (!partMap.has(key)) partMap.set(key, []); partMap.get(key).push(row); }
  for (const [key, rows] of [...partMap].sort(([a], [b]) => a.localeCompare(b))) { const [category, starting_price_split] = key.split("|"); partitions.push({ category, starting_price_split, ...ceilingSummary(rows), thin: rows.length < 10 }); }

  const aggressor = {
    schema_version: "WINDOW1_ASK_SIDE_AGGRESSOR_CENSUS_V1", score_free: true,
    population: { events: POPULATION, legs: POPULATION * 2, dates: ["2026-07-12", "2026-07-20"], holdout_dates: ["2026-07-24", "2026-07-26"], holdout_accessed: false },
    print_conservation: { lawful_admitted_prints: admitted, buyer_aggressed: buy, seller_aggressed: sell, unknown_aggressor: unknown, spread_bound: spreadBound, no_prior_bbo: noPrior, equal_timestamp_cross_stream_ambiguous: equalTs, censored_corridor_prints_not_admitted: rawInCorridorCensored },
    clock_law: { common_numeric_basis: "Unix epoch seconds", prints: "subsecond exchange timestamp", books: "whole-second raw snapshot timestamp plus preserved source-list ordinal", equal_timestamp_cross_stream_order: "UNBOUND; spread is unavailable rather than selected", exact_bell: "V5 exact_start_utc only", schedule: "frozen occurrence schedule" },
    by_category_and_starting_price_region: rowsFromCounter(maps.category_leg_region, ["category", "starting_price_region"]),
    by_category_and_print_price_region: rowsFromCounter(maps.category_print_region, ["category", "print_price_region"]),
    by_category_starting_price_region_and_spread: rowsFromCounter(maps.category_leg_region_spread, ["category", "starting_price_region", "spread_width_cents_or_status"]),
    by_category_starting_price_region_and_scheduled_clock: rowsFromCounter(maps.category_leg_region_schedule, ["category", "starting_price_region", "time_to_scheduled_band"]),
    by_category_starting_price_region_and_exact_bell_clock: rowsFromCounter(maps.category_leg_region_exact_bell, ["category", "starting_price_region", "time_to_exact_bell_band"]),
  };
  const cacheReproducedIds = eventRows.filter((row) => row.guarded_cache_rederived_negative).map((row) => row.event_id);
  const strictCacheIds = eventRows.filter((row) => row.guarded_cache_strict_later_negative).map((row) => row.event_id);
  const controlIds = summary.take_pair_combined_negative_event_ids;
  const cacheSet = new Set(cacheReproducedIds), controlSet = new Set(controlIds);
  const strictCacheSet = new Set(strictCacheIds);
  const ceiling = { schema_version: "WINDOW1_MAKER_TAKE_CEILING_CENSUS_V1", score_free: true, ex_post_oracle_only: true, controlling_take_ceiling: CONTROL_TAKE_CEILING, summary, partitions, guarded_cache_floor_reconciliation: { status: "SOURCE_GRAIN_DIFFERENCE_DISCLOSED", frozen_raw_tick_ceiling: CONTROL_TAKE_CEILING, guarded_cache_same_law_rederived_ceiling: cacheReproducedIds.length, frozen_only_event_ids: controlIds.filter((id) => !cacheSet.has(id)), guarded_cache_only_event_ids: cacheReproducedIds.filter((id) => !controlSet.has(id)), guarded_cache_strict_later_capacity_ceiling: strictCacheIds.length, strict_later_missing_from_frozen_event_ids: controlIds.filter((id) => !strictCacheSet.has(id)), strict_later_extra_event_ids: strictCacheIds.filter((id) => !controlSet.has(id)), controlling_source: FLOOR_SCAN_REL, explanation: "The 516 target prices and capacity receipts are frozen from the raw per-ticker top-five tick files. Guarded-cache snapshots are a distinct normalized source and are not permitted to overwrite those targets. Requiring the capacity receipt itself to arrive only after ten seconds is a stricter non-controlling law and is reported separately." }, events: eventRows };
  const result = { population: aggressor.population, print_conservation: aggressor.print_conservation, ceiling_census: ceiling };
  fs.mkdirSync(out, { recursive: true });
  const legText = legRows.map((row) => JSON.stringify(row)).join("\n") + "\n";
  fs.writeFileSync(path.join(out, "PER_LEG_AGGRESSOR_CENSUS.jsonl.gz"), gzipDeterministic(legText));
  fs.writeFileSync(path.join(out, "AGGRESSOR_SPLIT.json"), canonical(aggressor));
  fs.writeFileSync(path.join(out, "CEILING_CENSUS.json"), canonical(ceiling));
  const sources = { schema_version: "WINDOW1_AGGRESSOR_CEILING_SOURCE_MANIFEST_V1", sources: { [QUOTE_REL]: { sha256: fileHash(quoteFile), bytes: fs.statSync(quoteFile).size }, [GUARD_REL]: { sha256: fileHash(guardFile), bytes: fs.statSync(guardFile).size }, [FLOOR_SCAN_REL]: { sha256: fileHash(floorFile), bytes: fs.statSync(floorFile).size }, [CONTROL_CEILING_REL]: { sha256: fileHash(controlFile), bytes: fs.statSync(controlFile).size }, private_guarded_cache_v3: cacheManifest } };
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical(sources));
  fs.writeFileSync(path.join(out, "REPORT.md"), markdown(result));
  const names = ["AGGRESSOR_SPLIT.json", "CEILING_CENSUS.json", "PER_LEG_AGGRESSOR_CENSUS.jsonl.gz", "REPORT.md", "SOURCE_HASH_MANIFEST.json"];
  const artifacts = { schema_version: "WINDOW1_AGGRESSOR_CEILING_ARTIFACT_MANIFEST_V1", artifacts: Object.fromEntries(names.map((name) => [name, { bytes: fs.statSync(path.join(out, name)).size, sha256: fileHash(path.join(out, name)) }])) };
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical(artifacts));
  process.stdout.write(canonical({ status: "BUILT", prints: admitted, buy, sell, unknown, take_ceiling: summary.take_pair_combined_negative, maker_ceiling: summary.maker_pair_combined_negative, maker_both_legs: summary.maker_both_legs_reachable, output: path.relative(repo, out).replaceAll("\\", "/") }));
}

try { main(); } catch (error) { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }
