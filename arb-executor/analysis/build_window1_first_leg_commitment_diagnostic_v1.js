#!/usr/bin/env node
"use strict";

// Score-free diagnostic of asynchronous first-leg commitment.  This file does
// not import a scorer or a policy simulator.  It independently replays the
// inherited ask-only ten-second/five-contract evidence law over the frozen
// July 12-20 development tick files.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

const DWELL_SECONDS = 10;
const REQUIRED_QUANTITY = 5;
const RAW_BASE = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated";

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let hour = Number(m[4]);
  if (m[7] === "AM" && hour === 12) hour = 0;
  if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function region(price) { return price === null ? "UNAVAILABLE" : price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function quantile(values, q) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return null;
  const index = (sorted.length - 1) * q, lo = Math.floor(index), hi = Math.ceil(index);
  return lo === hi ? sorted[lo] : sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo);
}
function distribution(values) {
  const clean = values.filter(Number.isFinite);
  return { n: clean.length, min: clean.length ? Math.min(...clean) : null, p10: quantile(clean, 0.10), p25: quantile(clean, 0.25), median: quantile(clean, 0.50), p75: quantile(clean, 0.75), p90: quantile(clean, 0.90), max: clean.length ? Math.max(...clean) : null };
}
function clock(ts, scheduled, bell) {
  return {
    epoch_seconds: ts,
    tminus_scheduled_seconds: Number.isFinite(scheduled) ? scheduled - ts : null,
    tminus_actual_bell_seconds: Number.isFinite(bell) ? bell - ts : "NOT_BOUND",
  };
}

function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(",");
  return lines.map((line) => Object.fromEntries(line.split(",").map((value, index) => [headers[index], value])));
}

async function scanLeg(source, ticksRoot) {
  const file = path.join(ticksRoot, `${source.ticker}.csv.gz`);
  const stat = fs.statSync(file), input = fs.createReadStream(file), hash = crypto.createHash("sha256");
  input.on("data", (chunk) => hash.update(chunk));
  const lines = readline.createInterface({ input: input.pipe(zlib.createGunzip()), crlfDelay: Infinity });
  let headers = null, sourceRow = 1, last = null, firstFormed = null, globalBest = null, afterBest = null, malformed = 0;
  const since = Array(100).fill(null), left = Number(source.left_ts), right = Number(source.right_ts), afterTs = Number(source.after_counterpart_floor_ts);
  const inspect = (book, evidenceTs, endpoint = false) => {
    if (!Number.isInteger(book.bid) || !Number.isInteger(book.ask) || book.bid <= 0 || book.ask > 99 || book.bid > book.ask) return;
    if (!firstFormed && book.ask - book.bid === 1) firstFormed = { ts: book.ts, bid: book.bid, ask: book.ask, spread: 1, receipt: `${path.basename(file)}#row-${book.sourceRow}` };
    for (let limit = 1; limit < book.ask; limit += 1) since[limit] = null;
    for (let limit = book.ask; limit <= 99; limit += 1) if (since[limit] === null) since[limit] = book.ts;
    let cumulative = 0, levelIndex = 0;
    for (let limit = book.ask; limit <= 99; limit += 1) {
      while (levelIndex < book.asks.length && book.asks[levelIndex][0] <= limit) cumulative += book.asks[levelIndex++][1];
      if (cumulative < REQUIRED_QUANTITY || evidenceTs - since[limit] < DWELL_SECONDS) continue;
      const proof = {
        limit_cents: limit,
        evidence_ts: evidenceTs,
        bid_cents: book.bid,
        ask_cents: book.ask,
        spread_cents: book.ask - book.bid,
        dwell_seconds: evidenceTs - since[limit],
        displayed_capacity_at_or_below_limit: cumulative,
        source_receipt: `${path.basename(file)}#row-${book.sourceRow}${endpoint ? "; right-endpoint-carry" : ""}`,
      };
      if (!globalBest || limit < globalBest.limit_cents || (limit === globalBest.limit_cents && evidenceTs < globalBest.evidence_ts)) globalBest = proof;
      if (Number.isFinite(afterTs) && evidenceTs > afterTs && (!afterBest || limit < afterBest.limit_cents || (limit === afterBest.limit_cents && evidenceTs < afterBest.evidence_ts))) afterBest = proof;
      break;
    }
  };
  for await (const line of lines) {
    if (!headers) { headers = line.replace(/\r$/, "").split(","); continue; }
    sourceRow += 1;
    const values = line.replace(/\r$/, "").split(",");
    if (values.length !== headers.length) { malformed += 1; continue; }
    const raw = Object.fromEntries(headers.map((name, i) => [name, values[i]])), ts = parseEt(raw.ts_et);
    if (ts === null || ts < left || ts > right) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(raw[`bid_${level}`]), bs = positive(raw[`bid_${level}_sz`]), ap = integer(raw[`ask_${level}`]), as = positive(raw[`ask_${level}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    const book = { ts, bid: bids.length ? bids[0][0] : null, ask: asks.length ? asks[0][0] : null, asks, sourceRow };
    inspect(book, ts); last = book;
  }
  if (last && last.ts < right) inspect(last, right, true);
  return {
    event_id: source.event_id,
    leg_id: source.leg,
    ticker: source.ticker,
    first_formed_book: firstFormed,
    independently_derived_global_floor: globalBest,
    strictly_later_than_counterpart_floor: afterBest,
    malformed_rows_rejected: malformed,
    source: { file: path.basename(file), bytes: stat.size, sha256: hash.digest("hex") },
  };
}

async function workerMain() {
  const rows = [];
  for (const source of workerData.sources) rows.push(await scanLeg(source, workerData.ticksRoot));
  parentPort.postMessage(rows);
}

function summarize(rows) {
  const cells = {};
  for (const row of rows) {
    const key = `${row.category}|${row.starting_price_region_pair}`;
    if (!cells[key]) cells[key] = [];
    cells[key].push(row);
  }
  return Object.fromEntries(Object.entries(cells).sort().map(([key, cell]) => {
    const comparable = cell.filter((row) => Number.isFinite(row.floor_gap_seconds));
    const climbingKnown = comparable.filter((row) => row.climbing_leg_first !== "UNRESOLVED_DIRECTION");
    const commitments = cell.filter((row) => row.first_leg_commitment);
    return [key, {
      category: cell[0].category,
      starting_price_region_pair: cell[0].starting_price_region_pair,
      events: cell.length,
      thin: cell.length < 5,
      exact_starting_bid_splits: [...new Set(cell.map((row) => row.starting_bid_split))].sort(),
      both_floor_timestamps_available: comparable.length,
      floor_gap_seconds: distribution(comparable.map((row) => row.floor_gap_seconds)),
      climbing_direction_comparable: climbingKnown.length,
      climbing_leg_floor_first: climbingKnown.filter((row) => row.climbing_leg_first === true).length,
      climbing_leg_floor_first_rate: climbingKnown.length ? climbingKnown.filter((row) => row.climbing_leg_first === true).length / climbingKnown.length : null,
      first_leg_commitments_observed: commitments.length,
      later_sibling_capacity_floor_available: commitments.filter((row) => row.later_sibling_floor).length,
      later_sibling_floor_cents: distribution(commitments.map((row) => row.later_sibling_floor?.limit_cents).filter(Number.isFinite)),
      entry_cost_affordable_below_100: commitments.filter((row) => row.entry_cost_affordable_below_100 === true).length,
      later_floor_unaffordable_at_entry_cost_100: commitments.filter((row) => row.entry_cost_affordable_below_100 === false && row.later_sibling_floor).length,
      no_strictly_later_sibling_capacity_proof: commitments.filter((row) => !row.later_sibling_floor).length,
      naked_or_never_completed_under_entry_cost_law: commitments.filter((row) => row.naked_or_never_completed_under_entry_cost_law).length,
      event_ids: cell.map((row) => row.event_id).sort(),
    }];
  }));
}

function conditionalSummary(rows) {
  const cells = {};
  for (const row of rows.filter((entry) => entry.first_leg_commitment)) {
    const first = row.first_leg_commitment;
    const key = `${row.category}|${row.starting_price_region_pair}|X=${first.price_cents}|${region(first.price_cents)}`;
    if (!cells[key]) cells[key] = [];
    cells[key].push(row);
  }
  return Object.fromEntries(Object.entries(cells).sort().map(([key, cell]) => [key, {
    category: cell[0].category,
    starting_price_region_pair: cell[0].starting_price_region_pair,
    first_leg_x_cents: cell[0].first_leg_commitment.price_cents,
    first_leg_x_region: region(cell[0].first_leg_commitment.price_cents),
    n: cell.length,
    thin: cell.length < 5,
    later_sibling_available_n: cell.filter((row) => row.later_sibling_floor).length,
    sibling_eventual_floor_cents: distribution(cell.map((row) => row.later_sibling_floor?.limit_cents).filter(Number.isFinite)),
    pair_entry_cost_cents: distribution(cell.map((row) => row.pair_entry_cost_cents).filter(Number.isFinite)),
    naked_or_never_completed_n: cell.filter((row) => row.naked_or_never_completed_under_entry_cost_law).length,
    event_ids: cell.map((row) => row.event_id).sort(),
    inference_limit: "DESCRIPTIVE_ONLY_NOT_A_VALIDATED_CONDITIONAL_FORECAST",
  }]));
}

async function main() {
  const args = process.argv.slice(2), value = (name, fallback = null) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(value("--repo", ".")), privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private"));
  const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801")));
  const workersN = Number(value("--workers", "8"));
  const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
  const capacityPath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json");
  const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8"));
  const capacity = JSON.parse(fs.readFileSync(capacityPath));
  const capacityByKey = new Map(capacity.rows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const bell = JSON.parse(fs.readFileSync(bellPath)), bellByKey = new Map(bell.leg_rows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  if (quoteRows.length !== 1608 || new Set(quoteRows.map((row) => row.event_id)).size !== 804) throw new Error("development population is not 804 events / 1608 legs");
  for (const row of quoteRows) {
    const day = Number((row.event_id.match(/26JUL(\d{2})/) || [])[1]);
    if (!Number.isInteger(day) || day < 12 || day > 20) throw new Error(`forbidden/nondevelopment date ${row.event_id}`);
  }
  const byEventSources = new Map();
  for (const row of quoteRows) { if (!byEventSources.has(row.event_id)) byEventSources.set(row.event_id, []); byEventSources.get(row.event_id).push(row); }
  const scanSources = [];
  for (const legs of byEventSources.values()) {
    if (legs.length !== 2) throw new Error(`event leg conservation failure ${legs[0]?.event_id}`);
    for (const leg of legs) {
      const sibling = legs.find((row) => row.leg !== leg.leg), siblingProof = capacityByKey.get(`${leg.event_id}|${sibling.leg}`)?.capacity_proven_floor;
      scanSources.push({ ...leg, after_counterpart_floor_ts: siblingProof?.evidence_ts ?? "NOT_AVAILABLE" });
    }
  }
  const buckets = Array.from({ length: workersN }, () => []); scanSources.forEach((row, index) => buckets[index % workersN].push(row));
  const workers = buckets.map((sources) => new Promise((resolve, reject) => {
    const worker = new Worker(__filename, { workerData: { sources, ticksRoot: path.join(privateRoot, "fit-local/ticks") } });
    worker.once("message", resolve); worker.once("error", reject); worker.once("exit", (code) => { if (code) reject(new Error(`worker exit ${code}`)); });
  }));
  const scans = (await Promise.all(workers)).flat().sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id));
  const scanByKey = new Map(scans.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const mismatches = [];
  for (const scan of scans) {
    const frozen = capacityByKey.get(`${scan.event_id}|${scan.leg_id}`)?.capacity_proven_floor || null, actual = scan.independently_derived_global_floor;
    const project = (proof) => proof ? { limit_cents: proof.limit_cents, evidence_ts: proof.evidence_ts, dwell_seconds: proof.dwell_seconds } : null;
    if (JSON.stringify(project(frozen)) !== JSON.stringify(project(actual))) mismatches.push({ event_id: scan.event_id, leg_id: scan.leg_id, frozen: project(frozen), derived: project(actual) });
  }
  if (mismatches.length) throw new Error(`capacity floor reproduction mismatches=${mismatches.length}`);

  const eventRows = [];
  for (const [eventId, sourcesUnsorted] of [...byEventSources.entries()].sort()) {
    const sources = [...sourcesUnsorted].sort((a, b) => a.leg.localeCompare(b.leg)), legs = sources.map((source) => {
      const frozen = capacityByKey.get(`${eventId}|${source.leg}`), scan = scanByKey.get(`${eventId}|${source.leg}`), bellRow = bellByKey.get(`${eventId}|${source.leg}`);
      return {
        leg_id: source.leg, ticker: source.ticker, direction: source.leg_direction,
        first_formed_book: scan.first_formed_book,
        starting_price_region: region(scan.first_formed_book?.bid ?? null),
        scheduled_start_ts: Number(source.scheduled_start_ts), exact_bell_ts: Number.isFinite(Number(bellRow?.exact_bell_ts)) ? Number(bellRow.exact_bell_ts) : null,
        global_floor: frozen.capacity_proven_floor ? { ...scan.independently_derived_global_floor, clock: clock(scan.independently_derived_global_floor.evidence_ts, Number(source.scheduled_start_ts), Number(bellRow?.exact_bell_ts)) } : null,
        later_than_counterpart_floor: scan.strictly_later_than_counterpart_floor ? { ...scan.strictly_later_than_counterpart_floor, clock: clock(scan.strictly_later_than_counterpart_floor.evidence_ts, Number(source.scheduled_start_ts), Number(bellRow?.exact_bell_ts)) } : null,
      };
    });
    const formed = legs.map((leg) => leg.first_formed_book?.bid).filter(Number.isInteger).sort((a, b) => b - a);
    const regionPair = legs.map((leg) => leg.starting_price_region).sort().join("+");
    const floors = legs.filter((leg) => leg.global_floor).sort((a, b) => a.global_floor.evidence_ts - b.global_floor.evidence_ts || a.leg_id.localeCompare(b.leg_id));
    let first = null, sibling = null, tie = false;
    if (floors.length) {
      tie = floors.length === 2 && floors[0].global_floor.evidence_ts === floors[1].global_floor.evidence_ts;
      if (!tie) { first = floors[0]; sibling = legs.find((leg) => leg.leg_id !== first.leg_id); }
    }
    const later = first && sibling ? sibling.later_than_counterpart_floor : null;
    const pairCost = first && later ? first.global_floor.limit_cents + later.limit_cents : null;
    const uniqueClimber = legs.filter((leg) => leg.direction === "CLIMBING");
    const row = {
      event_id: eventId, category: sources[0].category, starting_bid_split: formed.length === 2 ? formed.join("+") : "UNAVAILABLE",
      starting_price_region_pair: regionPair, exact_bell_binding: legs.every((leg) => Number.isFinite(leg.exact_bell_ts)) ? "BOUND" : "NOT_BOUND_FOR_EVENT",
      legs,
      both_capacity_floors_available: floors.length === 2,
      simultaneous_floor_evidence: tie,
      floor_gap_seconds: floors.length === 2 ? Math.abs(floors[1].global_floor.evidence_ts - floors[0].global_floor.evidence_ts) : null,
      floor_gap_minutes: floors.length === 2 ? Math.abs(floors[1].global_floor.evidence_ts - floors[0].global_floor.evidence_ts) / 60 : null,
      climbing_leg_first: floors.length !== 2 || tie || uniqueClimber.length !== 1 ? "UNRESOLVED_DIRECTION" : floors[0].leg_id === uniqueClimber[0].leg_id,
      first_leg_commitment: first ? { leg_id: first.leg_id, price_cents: first.global_floor.limit_cents, bid_cents: first.global_floor.bid_cents, ask_cents: first.global_floor.ask_cents, evidence_ts: first.global_floor.evidence_ts, clock: first.global_floor.clock, direction: first.direction, receipt: first.global_floor.source_receipt } : null,
      sibling_leg_id: sibling?.leg_id ?? null,
      later_sibling_floor: later,
      pair_entry_cost_cents: pairCost,
      entry_cost_affordable_below_100: pairCost === null ? null : pairCost < 100,
      naked_or_never_completed_under_entry_cost_law: Boolean(first) && (pairCost === null || pairCost >= 100),
      naked_reason: !first ? "NO_STRICT_FIRST_FLOOR" : !later ? "NO_STRICTLY_LATER_SIBLING_TEN_SECOND_FIVE_CONTRACT_PROOF" : pairCost >= 100 ? "LATER_SIBLING_FLOOR_MAKES_PAIR_COST_AT_LEAST_100" : null,
    };
    eventRows.push(row);
  }
  const partitions = summarize(eventRows), conditional = conditionalSummary(eventRows);
  const conservation = {
    D: eventRows.length,
    both_capacity_floors_available: eventRows.filter((row) => row.both_capacity_floors_available).length,
    at_least_one_capacity_floor_available: eventRows.filter((row) => row.legs.some((leg) => leg.global_floor)).length,
    neither_capacity_floor_available: eventRows.filter((row) => row.legs.every((leg) => !leg.global_floor)).length,
    strict_first_leg_commitments: eventRows.filter((row) => row.first_leg_commitment).length,
    simultaneous_floor_evidence: eventRows.filter((row) => row.simultaneous_floor_evidence).length,
    later_sibling_floor_available: eventRows.filter((row) => row.later_sibling_floor).length,
    entry_cost_affordable_below_100: eventRows.filter((row) => row.entry_cost_affordable_below_100 === true).length,
    naked_or_never_completed_under_entry_cost_law: eventRows.filter((row) => row.naked_or_never_completed_under_entry_cost_law).length,
    exact_bell_bound_events: eventRows.filter((row) => row.exact_bell_binding === "BOUND").length,
    capacity_reproduction_mismatches: mismatches.length,
  };
  const gapCensus = {
    schema_version: "WINDOW1_FIRST_LEG_COMMITMENT_GAP_CENSUS_V1", score_free: true,
    population: { events: 804, legs: 1608, dates: "2026-07-12..2026-07-20", holdout_access: false },
    law: { side: "ASK_ONLY", dwell_seconds: DWELL_SECONDS, displayed_capacity_contracts: REQUIRED_QUANTITY, floor: "lowest limit with continuous ask-at-or-below dwell and cumulative displayed ask size at-or-below limit", strict_later_sibling: true, starting_price_region: "best bid on first lawful one-cent-spread BBO", climbing_label: "inherited quote-reachability leg_direction; no direction inferred when not exactly one CLIMBING leg" },
    conservation, by_category_and_observable_starting_price_region: partitions,
  };
  const siblingCensus = {
    schema_version: "WINDOW1_SIBLING_EVENTUAL_FLOOR_CONDITIONAL_CENSUS_V1", score_free: true,
    conditioning_law: "first chronologically proven global ask floor X, then lowest strictly-later sibling ten-second/five-contract ask floor; exact-X cells remain category and observable starting-region partitioned",
    entry_cost_law: "diagnostic S-law only: X1+X2<100; not PC, not a fee-aware edge rule, not a commitment policy",
    by_category_starting_region_and_exact_first_x: conditional,
    inference_fence: "The cells describe realized development tape. They are not a validated causal forecast and cannot authorize a naked first-leg commitment.",
  };
  const nakedReceipt = {
    schema_version: "WINDOW1_NAKED_NONCOMPLETION_RECEIPT_V1", score_free: true,
    definition: "A strict first floor was observable, but no strictly-later sibling ten-second/five-contract ask proof completed the pair below 100 cents.",
    fee_treatment: "NOT_INCLUDED; this is the existing entry-cost S diagnostic, not fee-aware PC",
    by_category_and_observable_starting_price_region: Object.fromEntries(Object.entries(partitions).map(([key, cell]) => [key, { events: cell.events, first_leg_commitments_observed: cell.first_leg_commitments_observed, no_strictly_later_sibling_capacity_proof: cell.no_strictly_later_sibling_capacity_proof, later_floor_unaffordable_at_entry_cost_100: cell.later_floor_unaffordable_at_entry_cost_100, naked_or_never_completed_under_entry_cost_law: cell.naked_or_never_completed_under_entry_cost_law, event_ids: cell.event_ids.filter((id) => eventRows.find((row) => row.event_id === id)?.naked_or_never_completed_under_entry_cost_law) }])),
  };
  const ruleSpec = {
    schema_version: "WINDOW1_CAUSAL_FIRST_LEG_COMMITMENT_RULE_SPEC_V1", status: "SPEC_ONLY_UNVALIDATED", score_free: true,
    smallest_honest_rule: [
      "Observe the first leg as a joint BBO/ask-dwell/displayed-capacity receipt; do not use its ex-post floor label at decision time.",
      "Compute a sibling maximum from an independently BOUND pair-value reference and exact bound fees: sibling_max=floor(pair_value-X1-fee1-fee2-smallest_strict_unit).",
      "If the sibling currently has lawful ten-second/five-contract ask capacity at or below sibling_max, both legs are coverable and the first commitment is permitted subject to the existing order law.",
      "If the sibling is not presently coverable, a naked first-leg commitment requires a separately validated category/starting-region conditional tail probability, risk tolerance, and maximum hold duration. None is bound here; emit INSUFFICIENT_COMMITMENT_EVIDENCE.",
    ],
    provenance: {
      ask_dwell_seconds: { value: DWELL_SECONDS, source: ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json", status: "INHERITED_NOT_RETUNED" },
      displayed_capacity_contracts: { value: REQUIRED_QUANTITY, source: "arb-executor/analysis/build_window1_ask_capacity_floor.js", status: "INHERITED_EXACT_FIVE_ACCOUNTING" },
      strict_pair_inequality_unit_cents: { value: 1, source: "existing integer-cent strict-combined law", status: "INHERITED" },
      independent_pair_value_reference: { value: "NOT_BOUND", source: ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/FIVE_GAME_REPLAY.json", status: "BLOCKS_VALUE_BASED_COMMITMENT" },
      fee_function: { value: "NOT_BOUND_IN_THIS_DIAGNOSTIC", status: "BLOCKS_FEE_AWARE_COMMITMENT" },
      naked_risk_probability_threshold: { value: null, status: "ABSENT_NOT_INVENTED" },
      maximum_naked_hold_seconds: { value: null, status: "ABSENT_NOT_INVENTED" },
    },
    validation: "UNVALIDATED; development description only; no policy replay and no holdout access",
  };

  fs.mkdirSync(output, { recursive: true });
  const ledgerText = eventRows.map((row) => JSON.stringify(row)).join("\n") + "\n";
  const ledgerGz = zlib.gzipSync(Buffer.from(ledgerText), { level: 9, mtime: 0 });
  const files = {
    "FIRST_LEG_COMMITMENT_EVENT_LEDGER.jsonl.gz": ledgerGz,
    "COMMITMENT_GAP_CENSUS.json": Buffer.from(canonical(gapCensus)),
    "SIBLING_FLOOR_CONDITIONAL_CENSUS.json": Buffer.from(canonical(siblingCensus)),
    "NAKED_NONCOMPLETION_RECEIPT.json": Buffer.from(canonical(nakedReceipt)),
    "CAUSAL_COMMITMENT_RULE_SPEC.json": Buffer.from(canonical(ruleSpec)),
  };
  const sourceManifest = {
    schema_version: "WINDOW1_FIRST_LEG_COMMITMENT_SOURCE_HASH_MANIFEST_V1",
    committed: Object.fromEntries([quotePath, capacityPath, bellPath, __filename].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])),
    private_development_tick_files: { count: scans.length, aggregate_manifest_sha256: sha256(Buffer.from(canonical(Object.fromEntries(scans.map((row) => [row.ticker, row.source]).sort())))) },
    forbidden: { holdout_july_24_26: false, scorer: false, live_network_trading: false },
  };
  files["SOURCE_HASH_MANIFEST.json"] = Buffer.from(canonical(sourceManifest));
  const report = [
    "# Window 1 first-leg commitment diagnostic", "", "Score-free July 12-20 development measurement. No scorer, policy replay, holdout, or live access.", "",
    `Raw gap census: ${RAW_BASE}/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/COMMITMENT_GAP_CENSUS.json`,
    `Raw conditional census: ${RAW_BASE}/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/SIBLING_FLOOR_CONDITIONAL_CENSUS.json`,
    `Raw event ledger: ${RAW_BASE}/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/FIRST_LEG_COMMITMENT_EVENT_LEDGER.jsonl.gz`,
    `Raw naked receipt: ${RAW_BASE}/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/NAKED_NONCOMPLETION_RECEIPT.json`,
    `Raw rule spec: ${RAW_BASE}/.claude/window1_live_v4_replay/first_leg_commitment_diagnostic_20260801/CAUSAL_COMMITMENT_RULE_SPEC.json`, "",
    "## Conservation", "", `- D: ${conservation.D}.`, `- Both capacity-proven floor timestamps: ${conservation.both_capacity_floors_available}.`, `- Strict first-leg commitments observable: ${conservation.strict_first_leg_commitments}.`, `- Strictly later sibling capacity floors: ${conservation.later_sibling_floor_available}.`, `- Pair entry cost below 100: ${conservation.entry_cost_affordable_below_100}.`, `- Naked/noncompleted under the entry-cost diagnostic: ${conservation.naked_or_never_completed_under_entry_cost_law}.`, "",
    "Every distribution remains partitioned by tournament category and observable starting BBO price region. Thin cells are labeled rather than pooled. Exact-bell clocks are NOT_BOUND where the inherited exact-bell ledger has no event row.", "",
    "## Interpretation fence", "", "The conditional sibling-floor cells are descriptive development-tape observations, not a validated forecast. No naked-commitment probability or hold-duration threshold is bound. The smallest honest causal rule therefore returns INSUFFICIENT_COMMITMENT_EVIDENCE whenever the sibling is not currently coverable inside an independently bound value-and-fee budget.", "",
  ].join("\n");
  files["REPORT.md"] = Buffer.from(`${report}\n`);
  for (const [name, body] of Object.entries(files)) fs.writeFileSync(path.join(output, name), body);
  const artifactManifest = { schema_version: "WINDOW1_FIRST_LEG_COMMITMENT_ARTIFACT_HASH_MANIFEST_V1", files: Object.fromEntries(Object.keys(files).sort().map((name) => [name, { bytes: fs.statSync(path.join(output, name)).size, sha256: hashFile(path.join(output, name)) }])) };
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical(artifactManifest));
  const determinism = { schema_version: "WINDOW1_FIRST_LEG_COMMITMENT_DETERMINISM_RECEIPT_V1", canonical_json: true, gzip_mtime: 0, artifact_manifest_sha256: hashFile(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), clean_build_comparison: "VERIFIED_BY_FOCUSED_TEST" };
  fs.writeFileSync(path.join(output, "DETERMINISM_RECEIPT.json"), canonical(determinism));
  process.stdout.write(canonical({ status: "BUILT", output, conservation, partitions: Object.keys(partitions).length, exact_x_cells: Object.keys(conditional).length }));
}

if (isMainThread) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
else workerMain().catch((error) => { throw error; });
