#!/usr/bin/env node
"use strict";

// Corrects V7's overloaded "floor" label. Policy decisions remain frozen.
// This is a score-free evidence reconciliation over ask floors and true prints.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/trade_floor_correction_v8_20260802")));
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const askFloorPath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json");
const oldCeilingPath = path.join(repo, ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/CEILING_CENSUS.json");
const guardPath = path.join(repo, ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl");
const v7Dir = path.join(repo, ".claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801");
const v7LedgerPath = path.join(v7Dir, "EVENT_LEDGER.jsonl.gz");
const v7ConservationPath = path.join(v7Dir, "CONSERVATION_RECEIPT.json");
const testPath = path.join(repo, "arb-executor/tests/test_window1_trade_floor_correction_v8.js");
const cacheRoot = path.join(privateRoot, "fit-local/guarded-cache-v3");
const branchRaw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(item) { return `${JSON.stringify(item, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function relative(file) { return path.relative(repo, file).replace(/\\/g, "/"); }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function integer(item) { if (item === null || item === undefined || typeof item === "boolean" || String(item).trim() === "") return null; const number = Number(item); return Number.isInteger(number) ? number : null; }
function finite(item) { if (item === null || item === undefined || typeof item === "boolean" || String(item).trim() === "") return null; const number = Number(item); return Number.isFinite(number) ? number : null; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const headers = lines.shift().split(","); return lines.map((line) => Object.fromEntries(line.split(",").map((item, index) => [headers[index], item]))); }
function parseJsonl(text) { return text.trimEnd().split(/\r?\n/).filter(Boolean).map(JSON.parse); }
function gzipCanonicalJsonl(rows) { return zlib.gzipSync(Buffer.from(rows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9, mtime: 0 }); }
function quantile(values, probability) { const rows = [...values].sort((a, b) => a - b); return rows.length ? rows[Math.min(rows.length - 1, Math.floor(probability * (rows.length - 1)))] : null; }
function distribution(values) { return { n: values.length, min: values.length ? Math.min(...values) : null, p25: quantile(values, .25), median: quantile(values, .5), p75: quantile(values, .75), p90: quantile(values, .9), max: values.length ? Math.max(...values) : null, counts: Object.fromEntries([...new Set(values)].sort((a, b) => a - b).map((item) => [String(item), values.filter((value) => value === item).length])) }; }
function aggressor(raw) { return raw === "yes" ? "BUY" : raw === "no" ? "SELL" : "UNKNOWN"; }
function priceRegion(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function tminus(seconds) { if (!Number.isFinite(seconds)) return null; const sign = seconds >= 0 ? "T-" : "T+"; const total = Math.abs(seconds); return `${sign}${Math.floor(total / 60)}:${String(Math.floor(total % 60)).padStart(2, "0")}`; }
function minimumPrint(rows) { if (!rows.length) return null; return rows.reduce((best, row) => row.price_cents < best.price_cents || (row.price_cents === best.price_cents && (row.timestamp_epoch < best.timestamp_epoch || (row.timestamp_epoch === best.timestamp_epoch && row.receipt.localeCompare(best.receipt) < 0))) ? row : best); }
function floorRelation(floor, close, label) { if (!Number.isInteger(floor) || !Number.isInteger(close)) return `${label}_OR_CLOSE_UNAVAILABLE`; return floor < close ? `${label}_BELOW_W1_CLOSE` : floor === close ? `${label}_EQUALS_W1_CLOSE` : `${label}_ABOVE_W1_CLOSE`; }

function loadInputs() {
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8"));
  const askFloor = JSON.parse(fs.readFileSync(askFloorPath));
  const oldCeiling = JSON.parse(fs.readFileSync(oldCeilingPath));
  const guards = parseJsonl(fs.readFileSync(guardPath, "utf8"));
  const v7 = parseJsonl(zlib.gunzipSync(fs.readFileSync(v7LedgerPath)).toString("utf8"));
  const quoteByKey = Object.fromEntries(quoteRows.map((row) => [`${row.event_id}|${row.leg}`, row]));
  const askByKey = Object.fromEntries(askFloor.rows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const oldEventById = Object.fromEntries(oldCeiling.events.map((row) => [row.event_id, row]));
  const guardById = Object.fromEntries(guards.map((row) => [row.event_id, row]));
  ensure(v7.length === 804 && askFloor.rows.length === 1608 && quoteRows.length === 1608, "population identity mismatch");
  return { quoteByKey, askByKey, oldEventById, guardById, v7 };
}

function readPrints(eventId, legId, ticker, left, right, positiveBoundary, cacheManifest) {
  const file = path.join(cacheRoot, `${eventId}.json.gz`);
  const bytes = fs.readFileSync(file);
  cacheManifest[`${eventId}.json.gz`] = { bytes: bytes.length, sha256: sha256(bytes) };
  const cache = JSON.parse(zlib.gunzipSync(bytes));
  const leg = cache.legs.find((row) => row.leg === legId && row.ticker === ticker);
  ensure(leg, `missing cache leg ${eventId}/${legId}`);
  const seen = new Map();
  for (const raw of leg.prints || []) {
    const ts = finite(raw.ts), price = integer(raw.price), size = finite(raw.size), receipt = String(raw.trade_id || "");
    if (ts === null || ts < left || ts > right || price === null || !(size > 0) || !receipt) continue;
    const row = { timestamp_epoch: ts, price_cents: price, size, receipt, aggressor_side: aggressor(String(raw.taker_side || "")), aggressor_source_law: `taker_side=${String(raw.taker_side || "")}` };
    const prior = seen.get(receipt);
    ensure(!prior || canonical(prior) === canonical(row), `conflicting duplicate print ${receipt}`);
    seen.set(receipt, row);
  }
  if (!positiveBoundary) return { admitted: [], censored_count: seen.size };
  return { admitted: [...seen.values()].sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.receipt.localeCompare(b.receipt)), censored_count: 0 };
}

function summarizeLegCells(legs) {
  const map = new Map();
  for (const leg of legs) {
    const key = `${leg.category}|${leg.price_region}`;
    if (!map.has(key)) map.set(key, { category: leg.category, price_region: leg.price_region, leg_ids: [], legs: 0, ask_floor_available: 0, trade_floor_available: 0, trade_low_below_ask_low: 0, trade_low_equals_ask_low: 0, trade_low_above_ask_low: 0, ask_minus_trade_gaps: [], candidate_trade_gaps: [], trade_floor_below_close: 0, trade_floor_equals_close: 0, trade_floor_above_close: 0, trade_floor_unavailable: 0 });
    const cell = map.get(key); cell.leg_ids.push(leg.leg_identity); cell.legs += 1; cell.ask_floor_available += Number(Number.isInteger(leg.ask_capacity_floor_cents)); cell.trade_floor_available += Number(Number.isInteger(leg.lowest_traded_price_cents));
    if (Number.isInteger(leg.ask_capacity_floor_minus_traded_low_cents)) { const gap = leg.ask_capacity_floor_minus_traded_low_cents; cell.ask_minus_trade_gaps.push(gap); cell.trade_low_below_ask_low += Number(gap > 0); cell.trade_low_equals_ask_low += Number(gap === 0); cell.trade_low_above_ask_low += Number(gap < 0); }
    if (Number.isInteger(leg.candidate_entry_minus_traded_low_cents)) cell.candidate_trade_gaps.push(leg.candidate_entry_minus_traded_low_cents);
    cell.trade_floor_below_close += Number(leg.trade_floor_vs_close_class === "TRADED_LOW_BELOW_W1_CLOSE"); cell.trade_floor_equals_close += Number(leg.trade_floor_vs_close_class === "TRADED_LOW_EQUALS_W1_CLOSE"); cell.trade_floor_above_close += Number(leg.trade_floor_vs_close_class === "TRADED_LOW_ABOVE_W1_CLOSE"); cell.trade_floor_unavailable += Number(leg.trade_floor_vs_close_class === "TRADED_LOW_OR_CLOSE_UNAVAILABLE");
  }
  return [...map.values()].sort((a, b) => `${a.category}|${a.price_region}`.localeCompare(`${b.category}|${b.price_region}`)).map((cell) => ({ ...cell, ask_floor_minus_traded_low_distribution_cents: distribution(cell.ask_minus_trade_gaps), candidate_entry_minus_traded_low_distribution_cents: distribution(cell.candidate_trade_gaps), ask_minus_trade_gaps: undefined, candidate_trade_gaps: undefined }));
}

function summarizeFormerClass(legs, className) {
  const selected = legs.filter((leg) => leg.v7_ask_floor_vs_close_class === className);
  const cells = new Map();
  for (const leg of selected) {
    const key = `${leg.category}|${leg.price_region}`;
    if (!cells.has(key)) cells.set(key, { category: leg.category, price_region: leg.price_region, leg_ids: [], legs: 0, corrected_close_available: 0, v7_blank_close_coerced_to_zero: 0, traded_low_prices: [], traded_low_minus_close: [], exact_close_price_print_available: 0, exact_close_price_print_sell: 0, latest_print_equals_close: 0, latest_print_equals_close_and_sell: 0, close_price_print_seconds_before_right: [] });
    const cell = cells.get(key); cell.leg_ids.push(leg.leg_identity); cell.legs += 1;
    cell.corrected_close_available += Number(Number.isInteger(leg.own_window1_close_cents)); cell.v7_blank_close_coerced_to_zero += Number(leg.v7_close_binding_defect === "BLANK_CLOSE_COERCED_TO_ZERO");
    if (Number.isInteger(leg.lowest_traded_price_cents)) { cell.traded_low_prices.push(leg.lowest_traded_price_cents); if (Number.isInteger(leg.own_window1_close_cents)) cell.traded_low_minus_close.push(leg.lowest_traded_price_cents - leg.own_window1_close_cents); }
    cell.exact_close_price_print_available += Number(Boolean(leg.latest_print_at_frozen_close)); cell.exact_close_price_print_sell += Number(leg.latest_print_at_frozen_close?.aggressor_side === "SELL"); cell.latest_print_equals_close += Number(leg.latest_lawful_print?.price_cents === leg.own_window1_close_cents); cell.latest_print_equals_close_and_sell += Number(leg.latest_lawful_print?.price_cents === leg.own_window1_close_cents && leg.latest_lawful_print?.aggressor_side === "SELL"); if (Number.isFinite(leg.latest_print_at_frozen_close?.seconds_before_guarded_right_edge)) cell.close_price_print_seconds_before_right.push(leg.latest_print_at_frozen_close.seconds_before_guarded_right_edge);
  }
  return {
    class_name: className,
    legs: selected.length,
    corrected_close_available: selected.filter((leg) => Number.isInteger(leg.own_window1_close_cents)).length,
    v7_blank_close_coerced_to_zero: selected.filter((leg) => leg.v7_close_binding_defect === "BLANK_CLOSE_COERCED_TO_ZERO").length,
    traded_low_available: selected.filter((leg) => Number.isInteger(leg.lowest_traded_price_cents)).length,
    traded_low_price_distribution: distribution(selected.map((leg) => leg.lowest_traded_price_cents).filter(Number.isInteger)),
    traded_low_minus_close_distribution_cents: distribution(selected.map((leg) => Number.isInteger(leg.lowest_traded_price_cents) && Number.isInteger(leg.own_window1_close_cents) ? leg.lowest_traded_price_cents - leg.own_window1_close_cents : null).filter(Number.isInteger)),
    exact_close_price_print_available: selected.filter((leg) => leg.latest_print_at_frozen_close).length,
    exact_close_price_print_sell: selected.filter((leg) => leg.latest_print_at_frozen_close?.aggressor_side === "SELL").length,
    latest_print_equals_close: selected.filter((leg) => Number.isInteger(leg.own_window1_close_cents) && leg.latest_lawful_print?.price_cents === leg.own_window1_close_cents).length,
    latest_print_equals_close_and_sell: selected.filter((leg) => Number.isInteger(leg.own_window1_close_cents) && leg.latest_lawful_print?.price_cents === leg.own_window1_close_cents && leg.latest_lawful_print?.aggressor_side === "SELL").length,
    close_price_print_seconds_before_guarded_right_distribution: distribution(selected.map((leg) => leg.latest_print_at_frozen_close?.seconds_before_guarded_right_edge).filter(Number.isFinite)),
    by_category_and_price_region: [...cells.values()].sort((a, b) => `${a.category}|${a.price_region}`.localeCompare(`${b.category}|${b.price_region}`)).map((cell) => ({ ...cell, traded_low_price_distribution: distribution(cell.traded_low_prices), traded_low_minus_close_distribution_cents: distribution(cell.traded_low_minus_close), close_price_print_seconds_before_guarded_right_distribution: distribution(cell.close_price_print_seconds_before_right), traded_low_prices: undefined, traded_low_minus_close: undefined, close_price_print_seconds_before_right: undefined })),
  };
}

function aggregateLegFloorSummary(legs) {
  const comparable = legs.filter((leg) => Number.isInteger(leg.ask_capacity_floor_minus_traded_low_cents));
  const gaps = comparable.map((leg) => leg.ask_capacity_floor_minus_traded_low_cents);
  return {
    legs: legs.length,
    ask_floor_available: legs.filter((leg) => Number.isInteger(leg.ask_capacity_floor_cents)).length,
    trade_floor_available: legs.filter((leg) => Number.isInteger(leg.lowest_traded_price_cents)).length,
    directly_comparable_ask_and_trade_floors: comparable.length,
    trade_low_below_ask_low: comparable.filter((leg) => leg.ask_capacity_floor_minus_traded_low_cents > 0).length,
    trade_low_equals_ask_low: comparable.filter((leg) => leg.ask_capacity_floor_minus_traded_low_cents === 0).length,
    trade_low_above_ask_low: comparable.filter((leg) => leg.ask_capacity_floor_minus_traded_low_cents < 0).length,
    ask_floor_minus_traded_low_distribution_cents: distribution(gaps),
    blank_source_window1_close: legs.filter((leg) => !Number.isInteger(leg.own_window1_close_cents)).length,
    v7_blank_close_coerced_to_zero: legs.filter((leg) => leg.v7_close_binding_defect === "BLANK_CLOSE_COERCED_TO_ZERO").length,
  };
}

function ceilingSummary(events) {
  return { events: events.length, ask_capacity_take_ceiling: events.filter((event) => event.ask_capacity_take_ceiling_member).length, ask_target_seller_print_maker_ceiling: events.filter((event) => event.ask_target_seller_print_maker_ceiling_member).length, any_trade_low_price_ceiling: events.filter((event) => event.any_trade_low_price_ceiling_member).length, both_absolute_trade_lows_seller_aggressed_ceiling: events.filter((event) => event.both_absolute_trade_lows_seller_aggressed_ceiling_member).length, seller_aggressed_trade_floor_ceiling: events.filter((event) => event.seller_aggressed_trade_floor_ceiling_member).length, any_trade_size5_floor_ceiling: events.filter((event) => event.any_trade_size5_floor_ceiling_member).length, seller_aggressed_size5_trade_floor_ceiling: events.filter((event) => event.seller_aggressed_size5_trade_floor_ceiling_member).length };
}

function main() {
  const inputs = loadInputs(), cacheManifest = {}, legRows = [], eventRows = [];
  for (const event of inputs.v7) {
    const oldEvent = inputs.oldEventById[event.event_id];
    const guard = inputs.guardById[event.event_id];
    ensure(oldEvent && guard, `missing old event/guard ${event.event_id}`);
    const eventLegs = [];
    for (const [legId, v7Leg] of Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b))) {
      const identity = `${event.event_id}|${legId}`, source = inputs.quoteByKey[identity], ask = inputs.askByKey[identity];
      ensure(source && ask, `missing source ${identity}`);
      const left = finite(source.left_ts), right = finite(source.right_ts), scheduled = finite(source.scheduled_start_ts), positiveBoundary = String(source.evaluator_window_positive).toLowerCase() === "true" && guard.positive_window1_provable === true;
      const exactBell = guard.exact_start_utc ? Date.parse(guard.exact_start_utc) / 1000 : null;
      const printResult = readPrints(event.event_id, legId, source.ticker, left, right, positiveBoundary, cacheManifest), prints = printResult.admitted;
      const tradeLow = minimumPrint(prints), sellerFloor = minimumPrint(prints.filter((print) => print.aggressor_side === "SELL")), size5Floor = minimumPrint(prints.filter((print) => print.size >= 5)), sellerSize5Floor = minimumPrint(prints.filter((print) => print.aggressor_side === "SELL" && print.size >= 5));
      const close = integer(source.window1_close_cents), askFloor = ask.capacity_proven_floor?.limit_cents ?? null;
      const lowPrints = tradeLow ? prints.filter((print) => print.price_cents === tradeLow.price_cents) : [];
      const latestPrint = prints.length ? prints[prints.length - 1] : null;
      const exactClosePrints = close === null ? [] : prints.filter((print) => print.price_cents === close);
      const latestClosePrint = exactClosePrints.length ? exactClosePrints[exactClosePrints.length - 1] : null;
      const decorate = (print) => print ? { ...print, seconds_before_guarded_right_edge: right - print.timestamp_epoch, t_minus_scheduled_seconds: scheduled - print.timestamp_epoch, t_minus_scheduled: tminus(scheduled - print.timestamp_epoch), t_minus_exact_bell_seconds: exactBell === null ? null : exactBell - print.timestamp_epoch, t_minus_exact_bell: exactBell === null ? null : tminus(exactBell - print.timestamp_epoch) } : null;
      const row = {
        leg_identity: identity, event_id: event.event_id, category: event.category, price_region: v7Leg.price_region || priceRegion(integer(ask.window1_open_cents)), leg_id: legId, ticker: source.ticker,
        positive_window1_provable: positiveBoundary, guarded_left_ts: left, guarded_right_ts: right, scheduled_start_ts: scheduled, exact_bell_ts: exactBell, exact_bell_status: exactBell === null ? "NOT_EXACTLY_BOUND" : "V5_EXACT_START",
        own_window1_close_cents: close, frozen_close_raw: source.window1_close_cents, v7_close_cents: v7Leg.own_window1_close_cents, v7_close_binding_defect: close === null && v7Leg.own_window1_close_cents === 0 ? "BLANK_CLOSE_COERCED_TO_ZERO" : "NONE",
        ask_capacity_floor_cents: askFloor, ask_capacity_floor_proof: ask.capacity_proven_floor || null, v7_ask_floor_vs_close_class: v7Leg.market_ceiling_class,
        lowest_traded_price_cents: tradeLow?.price_cents ?? null,
        lowest_traded_price_proof: tradeLow ? { price_cents: tradeLow.price_cents, first_low_print: decorate(tradeLow), low_price_print_count: lowPrints.length, low_price_total_size: lowPrints.reduce((sum, print) => sum + print.size, 0), aggressor_counts: { BUY: lowPrints.filter((print) => print.aggressor_side === "BUY").length, SELL: lowPrints.filter((print) => print.aggressor_side === "SELL").length, UNKNOWN: lowPrints.filter((print) => print.aggressor_side === "UNKNOWN").length }, prints: lowPrints.map(decorate) } : null,
        seller_aggressed_trade_floor: decorate(sellerFloor), any_trade_size5_floor: decorate(size5Floor), seller_aggressed_size5_trade_floor: decorate(sellerSize5Floor),
        lawful_true_print_count: prints.length, censored_corridor_print_count: printResult.censored_count,
        latest_lawful_print: decorate(latestPrint), latest_lawful_print_matches_frozen_close: Boolean(latestPrint && latestPrint.price_cents === close),
        latest_print_at_frozen_close: decorate(latestClosePrint), frozen_close_print_binding: latestPrint && latestPrint.price_cents === close ? "LATEST_LAWFUL_TRUE_PRINT_EQUALS_FROZEN_CLOSE" : latestClosePrint ? "EARLIER_TRUE_PRINT_AT_FROZEN_CLOSE; LATEST_PRINT_DIFFERS" : "NO_TRUE_PRINT_AT_FROZEN_CLOSE",
        ask_capacity_floor_minus_traded_low_cents: Number.isInteger(askFloor) && tradeLow ? askFloor - tradeLow.price_cents : null,
        ask_floor_vs_close_class: floorRelation(askFloor, close, "ASK_CAPACITY_FLOOR"), trade_floor_vs_close_class: floorRelation(tradeLow?.price_cents ?? null, close, "TRADED_LOW"),
        candidate_entry_cents: v7Leg.honest_credited_entry_cents,
        candidate_entry_minus_ask_capacity_floor_cents: Number.isInteger(v7Leg.honest_credited_entry_cents) && Number.isInteger(askFloor) ? v7Leg.honest_credited_entry_cents - askFloor : null,
        candidate_entry_minus_traded_low_cents: Number.isInteger(v7Leg.honest_credited_entry_cents) && tradeLow ? v7Leg.honest_credited_entry_cents - tradeLow.price_cents : null,
        source_cache: { path: `fit-local/guarded-cache-v3/${event.event_id}.json.gz`, ...cacheManifest[`${event.event_id}.json.gz`] },
      };
      legRows.push(row); eventLegs.push(row);
    }
    const closes = eventLegs.map((leg) => leg.own_window1_close_cents), askFloors = eventLegs.map((leg) => leg.ask_capacity_floor_cents), tradeFloors = eventLegs.map((leg) => leg.lowest_traded_price_cents), sellerFloors = eventLegs.map((leg) => leg.seller_aggressed_trade_floor?.price_cents ?? null), size5Floors = eventLegs.map((leg) => leg.any_trade_size5_floor?.price_cents ?? null), sellerSize5Floors = eventLegs.map((leg) => leg.seller_aggressed_size5_trade_floor?.price_cents ?? null);
    const pairNegative = (floors) => floors.every(Number.isInteger) && closes.every(Number.isInteger) && floors[0] + floors[1] - closes[0] - closes[1] < 0;
    const absoluteLowSeller = eventLegs.every((leg) => leg.lowest_traded_price_proof && leg.lowest_traded_price_proof.aggressor_counts.SELL > 0);
    const askCapacityMember = pairNegative(askFloors);
    const makerTargetMember = askCapacityMember && eventLegs.every((leg) => Number.isInteger(leg.ask_capacity_floor_cents) && Number.isInteger(leg.seller_aggressed_trade_floor?.price_cents) && leg.seller_aggressed_trade_floor.price_cents <= leg.ask_capacity_floor_cents);
    const eventRow = { event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, closes, ask_capacity_floors: askFloors, absolute_trade_lows: tradeFloors, seller_aggressed_trade_floors: sellerFloors, any_trade_size5_floors: size5Floors, seller_aggressed_size5_trade_floors: sellerSize5Floors, ask_capacity_pair_delta_to_closes_cents: askFloors.every(Number.isInteger) && closes.every(Number.isInteger) ? askFloors[0] + askFloors[1] - closes[0] - closes[1] : null, absolute_trade_low_pair_delta_to_closes_cents: tradeFloors.every(Number.isInteger) && closes.every(Number.isInteger) ? tradeFloors[0] + tradeFloors[1] - closes[0] - closes[1] : null, seller_aggressed_trade_floor_pair_delta_to_closes_cents: sellerFloors.every(Number.isInteger) && closes.every(Number.isInteger) ? sellerFloors[0] + sellerFloors[1] - closes[0] - closes[1] : null, ask_capacity_take_ceiling_member: askCapacityMember, ask_capacity_take_ceiling_frozen_v7_member: oldEvent.controlling_516_member === true, ask_capacity_take_ceiling_reconciliation_match: askCapacityMember === (oldEvent.controlling_516_member === true), ask_target_seller_print_maker_ceiling_member: makerTargetMember, ask_target_seller_print_maker_ceiling_frozen_v7_member: oldEvent.maker_pair_combined_negative === true, ask_target_seller_print_maker_ceiling_reconciliation_match: makerTargetMember === (oldEvent.maker_pair_combined_negative === true), any_trade_low_price_ceiling_member: pairNegative(tradeFloors), both_absolute_trade_lows_seller_aggressed_ceiling_member: pairNegative(tradeFloors) && absoluteLowSeller, seller_aggressed_trade_floor_ceiling_member: pairNegative(sellerFloors), any_trade_size5_floor_ceiling_member: pairNegative(size5Floors), seller_aggressed_size5_trade_floor_ceiling_member: pairNegative(sellerSize5Floors), price_only_warning: "A traded price does not itself prove five-contract capacity; size>=5 variants are separate.", legs: Object.fromEntries(eventLegs.map((leg) => [leg.leg_id, leg.leg_identity])) };
    eventRows.push(eventRow);
  }
  ensure(legRows.length === 1608 && eventRows.length === 804, "output conservation failed");
  ensure(eventRows.every((event) => event.ask_capacity_take_ceiling_reconciliation_match), "independently recomputed ask ceiling differs from frozen 516 membership");
  ensure(eventRows.every((event) => event.ask_target_seller_print_maker_ceiling_reconciliation_match), "independently recomputed maker ceiling differs from frozen 253 membership");
  const partitions = new Map();
  for (const event of eventRows) { const key = `${event.category}|${event.starting_price_split}`; if (!partitions.has(key)) partitions.set(key, []); partitions.get(key).push(event); }
  const ceiling = { schema_version: "WINDOW1_DUAL_FLOOR_CEILING_RECOMPUTATION_V8", score_free: true, definitions: { ask_capacity_take_ceiling: "Both capacity-proven ask floors exist and pair delta to own W1 closes is negative; reproduces frozen 516.", ask_target_seller_print_maker_ceiling: "Frozen 253: both legs have a SELL print at/below the frozen ask target and the frozen ask pair is negative.", any_trade_low_price_ceiling: "Both true-print lows exist and pair delta to own W1 closes is negative; price-only, not five-contract capacity.", seller_aggressed_trade_floor_ceiling: "Both legs have a SELL-aggressed print floor and its pair delta is negative; price/observed-size only.", size5_variants: "Each leg has one qualifying true print with size >=5; no cumulative or queue fabrication." }, aggregate: ceilingSummary(eventRows), by_category_and_starting_price_split: [...partitions].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, starting_price_split] = key.split("|"); return { category, starting_price_split, ...ceilingSummary(rows), thin: rows.length < 10, event_ids: rows.map((row) => row.event_id) }; }), events: eventRows };
  ensure(ceiling.aggregate.ask_capacity_take_ceiling === 516, "failed to reproduce ask ceiling 516");
  ensure(ceiling.aggregate.ask_target_seller_print_maker_ceiling === 253, "failed to reproduce maker ceiling 253");
  const classes = { schema_version: "WINDOW1_V7_ASK_CLASS_TO_TRADE_FLOOR_RECONCILIATION_V8", former_ask_floor_above_close: summarizeFormerClass(legRows, "ASK_REACHABLE_FLOOR_ABOVE_W1_CLOSE"), former_ask_floor_equals_close: summarizeFormerClass(legRows, "EXACT_ASK_REACHABLE_FLOOR_EQUALS_W1_CLOSE") };
  ensure(classes.former_ask_floor_above_close.legs === 317 && classes.former_ask_floor_equals_close.legs === 477, "V7 class binding mismatch");
  const summary = { schema_version: "WINDOW1_DUAL_ASK_AND_TRADE_FLOOR_SUMMARY_V8", score_free: true, population: { events: 804, legs: 1608 }, floor_law: { objective_floor: "lowest lawful true public traded price inside the positively provable guarded Window-1 corridor", execution_floor: "lowest qualifying ask with >=10 seconds dwell and displayed capacity >=5", neither_substitutes_for_the_other: true }, clock_law: { prints: "exchange Unix epoch seconds", window_edges: "same Unix epoch-second basis", directly_comparable: true, exact_bell: "V5 exact_start_utc only; otherwise explicitly null" }, aggregate_leg_floor_census: aggregateLegFloorSummary(legRows), by_category_and_price_region: summarizeLegCells(legRows), v7_class_reconciliation: classes, metrics_and_performance_fields: { C: null, PC: null, IC: null, S: null, ranking: null, selection: null } };
  fs.mkdirSync(output, { recursive: true });
  fs.writeFileSync(path.join(output, "DUAL_FLOOR_LEG_LEDGER.jsonl.gz"), gzipCanonicalJsonl(legRows));
  fs.writeFileSync(path.join(output, "TRADE_FLOOR_EVENT_LEDGER.jsonl.gz"), gzipCanonicalJsonl(eventRows));
  fs.writeFileSync(path.join(output, "DUAL_FLOOR_SUMMARY.json"), canonical(summary));
  fs.writeFileSync(path.join(output, "ASK_FLOOR_CLASS_RECONCILIATION.json"), canonical(classes));
  fs.writeFileSync(path.join(output, "CEILING_RECOMPUTATION.json"), canonical(ceiling));
  fs.writeFileSync(path.join(output, "V7_SUPERSESSION_RECEIPT.json"), canonical({ schema_version: "WINDOW1_V7_FLOOR_SEMANTIC_SUPERSESSION_V8", v7_commit: "0ec177445c04709cb147617a6419c3ea981585e5", v7_event_ledger: { path: relative(v7LedgerPath), sha256: hashFile(v7LedgerPath) }, v7_conservation: { path: relative(v7ConservationPath), sha256: hashFile(v7ConservationPath) }, defects: [{ name: "ASK_FLOOR_OVERLOADED_AS_OBJECTIVE_TRADE_FLOOR", description: "V7 used the capacity-proven ask floor as both an execution-reach floor and the objective traded-price floor." }, { name: "BLANK_CLOSE_COERCED_TO_ZERO", description: "V7 converted blank source Window-1 closes through Number(blank), producing zero; 301 legs were affected, including 267 of the reported 317 above-close legs." }], preserved: "All V7 decisions, actions, fill classes, clocks and receipts remain byte-identical.", corrected: "V8 reports ask-capacity and true-trade floors side by side, binds blank closes as unavailable, and recomputes every gap and ceiling without changing policy behavior." }));
  const report = `# Window-1 dual ask/trade floor correction V8\n\nEvery per-leg floor, print, aggressor, size, receipt and clock: ${branchRaw}/${relative(path.join(output, "DUAL_FLOOR_LEG_LEDGER.jsonl.gz"))}\n\nEvery category / price-region number: ${branchRaw}/${relative(path.join(output, "DUAL_FLOOR_SUMMARY.json"))}\n\nThe former 317 above-close and 477 equals-close classes: ${branchRaw}/${relative(path.join(output, "ASK_FLOOR_CLASS_RECONCILIATION.json"))}\n\nAll ask- and trade-based ceiling definitions and counts: ${branchRaw}/${relative(path.join(output, "CEILING_RECOMPUTATION.json"))}\n\nV7 is preserved but its overloaded floor semantics and blank-close coercion are superseded: ${branchRaw}/${relative(path.join(output, "V7_SUPERSESSION_RECEIPT.json"))}\n\nA true print proves price and observed size. It does not silently prove five-contract capacity.\n`;
  fs.writeFileSync(path.join(output, "REPORT.md"), report);
  const committedSources = [quotePath, askFloorPath, oldCeilingPath, guardPath, v7LedgerPath, v7ConservationPath, __filename, testPath];
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_TRADE_FLOOR_CORRECTION_SOURCE_MANIFEST_V8", committed: Object.fromEntries(committedSources.map((file) => [relative(file), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), private_guarded_cache_v3: cacheManifest, forbidden_access: { holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false } }));
  const artifactNames = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_TRADE_FLOOR_CORRECTION_ARTIFACT_MANIFEST_V8", files: Object.fromEntries(artifactNames.map((name) => [name, { sha256: hashFile(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output: relative(output), aggregate: ceiling.aggregate, former_above: classes.former_ask_floor_above_close, former_equal: classes.former_ask_floor_equals_close }));
}

try { main(); } catch (error) { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }
