#!/usr/bin/env node
"use strict";

// Score-free implementation receipt for the live-book initial-aim law.
// It replays the five frozen exact-start events and independently reconciles
// the 804-event ATLAS suppression and ask-capacity opportunity surfaces.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const {
  simulateEvent: simulateCurrentEvent,
} = require("./build_window1_five_exact_full_stack.js");
const { ColdReplay, enrichRows, runColdReplay } = require("./nikvrb_sibling_shape_cold_replay.js");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const outDir = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731");
const reportPath = path.join(repo, "arb-executor/docs/research/window1/WINDOW1_LIVE_BOOK_INITIAL_AIM_REPLAY.md");
const selectionPath = path.join(repo, ".claude/window1_live_v4_replay/delta_objective_20260729/FIVE_GAME_SELECTION.json");
const orientationPath = path.join(repo, ".claude/window1_live_v4_replay/orientation_initial_20260730/ORIENTATION_INITIAL_REPLAY.json");
const deltaReplayPath = path.join(repo, ".claude/window1_live_v4_replay/delta_objective_20260729/FIVE_GAME_DELTA_REPLAYS.json");
const quoteLegsPath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const quoteCensusPath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_CENSUS.json");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const nikClockPath = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv");
const nikTracePath = path.join(repo, ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json");
const legacyRescorePath = path.join(repo, ".claude/window1_live_v4_replay/quote_touch_os_rescore_rebalanced_20260731/WINDOW1_QUOTE_TOUCH_OS_RESCORE.json");
const frozenFivePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const capacityScanPath = path.join(outDir, "RAW_CAPACITY_FLOOR_SCAN.json");
const privateRoot = path.resolve(process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private");
const printsPath = path.join(privateRoot, "fit-local/prints.jsonl");
const ticksRoot = path.join(privateRoot, "fit-local/ticks");
const DWELL_SECONDS = 10;
const REQUIRED_QUANTITY = 5;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function signed(value) { return Number.isInteger(value) ? `${value >= 0 ? "+" : ""}${value}` : (value ?? "NULL"); }
function finite(value) { const n = Number(value); return Number.isFinite(n) ? n : null; }
function positive(value) { const n = finite(value); return n !== null && n > 0 ? n : null; }
function priceRegion(price) { if (!Number.isInteger(price)) return "UNAVAILABLE"; return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge75"; }
function validBook(book) { return book && Number.isInteger(book.bid) && Number.isInteger(book.ask) && book.bid > 0 && book.ask <= 99 && book.bid <= book.ask; }

function parseCsv(text) {
  const matrix = []; let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) { if (ch === '"' && text[i + 1] === '"') { field += '"'; i += 1; } else if (ch === '"') quoted = false; else field += ch; }
    else if (ch === '"') quoted = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n") { row.push(field.replace(/\r$/, "")); matrix.push(row); row = []; field = ""; }
    else field += ch;
  }
  if (field || row.length) { row.push(field.replace(/\r$/, "")); matrix.push(row); }
  const headers = matrix.shift();
  return matrix.filter((values) => values.length === headers.length).map((values) => Object.fromEntries(headers.map((name, index) => [name, values[index]])));
}

function parseEtSecond(value) {
  const match = String(value).match(/^(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) throw new Error(`bad ET tick timestamp ${value}`);
  let hour = Number(match[2]); if (match[5] === "AM" && hour === 12) hour = 0; if (match[5] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}T${String(hour).padStart(2, "0")}:${match[3]}:${match[4]}-04:00`) / 1000;
}

function readTickRows(ticker, left, right) {
  const file = path.join(ticksRoot, `${ticker}.csv.gz`);
  if (!fs.existsSync(file)) throw new Error(`missing frozen tick source ${file}`);
  const source = fs.readFileSync(file);
  const rows = [];
  parseCsv(zlib.gunzipSync(source).toString("utf8")).forEach((raw, ordinal) => {
    const ts = parseEtSecond(raw.ts_et); if (ts < left || ts > right) return;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(raw[`bid_${level}`]), bidSize = positive(raw[`bid_${level}_sz`]), ask = integer(raw[`ask_${level}`]), askSize = positive(raw[`ask_${level}_sz`]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]); if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    rows.push({ kind: "BBO", ticker, ts, ordinal, bids, asks, bid: bids.length ? Math.max(...bids.map((x) => x[0])) : null, ask: asks.length ? Math.min(...asks.map((x) => x[0])) : null, carried_last: integer(raw.last_trade), source_receipt: `${path.basename(file)}#row-${ordinal + 2}` });
  });
  return { file, bytes: source.length, sha256: sha256(source), rows };
}

async function readPrintRows(tickers, bounds) {
  const wanted = new Set(tickers), output = [];
  const lines = readline.createInterface({ input: fs.createReadStream(printsPath, { encoding: "utf8" }), crlfDelay: Infinity });
  let ordinal = 0;
  for await (const line of lines) {
    ordinal += 1; if (!line || !line.includes('"ticker"')) continue;
    const raw = JSON.parse(line); if (!wanted.has(raw.ticker)) continue;
    const ts = finite(raw.ts), size = positive(raw.size), price = integer(raw.price), corridor = bounds[raw.ticker];
    if (ts === null || price === null || size === null || ts < corridor.left || ts > corridor.right) continue;
    output.push({ kind: "PRINT", ticker: raw.ticker, ts, ordinal, price, size, trade_id: raw.trade_id || raw.id || null });
  }
  return output.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
}

function projectNikCapacity(rawRows, tickRowsByTicker) {
  const byKey = new Map(); for (const rows of Object.values(tickRowsByTicker)) for (const row of rows) byKey.set(`${row.ticker}|${row.ts}`, row);
  const output = {};
  for (const raw of rawRows) {
    const match = String(raw.event_kind).match(/^BBO_(NIK|VRB)$/); if (!match) continue;
    const leg = match[1], ticker = `KXATPCHALLENGERMATCH-26JUL19NIKVRB-${leg}`, ts = Date.parse(raw.timestamp_et) / 1000, source = byKey.get(`${ticker}|${ts}`); if (!source) continue;
    const top = source.asks.filter(([price]) => price === source.ask);
    output[`${raw.sequence}|${leg}`] = { receipt: source.source_receipt, ask_price: source.ask, ask_size: top.reduce((sum, item) => sum + item[1], 0), ask_capacity_at_top: top.reduce((sum, item) => sum + item[1], 0), top_five_asks: source.asks };
  }
  return output;
}

function delta(entry, reference) { return Number.isInteger(entry) && Number.isInteger(reference) ? entry - reference : null; }

class LiveBookInitialAimColdReplay extends ColdReplay {
  constructor({ trace }) {
    super({ trace, scenario: "ask_dwell" });
    this.scenario = "live_book_initial_aim";
    this.staleAskWait = null;
    for (const call of this.consultations.values()) {
      if (call.leg !== "NIK") continue;
      call.selected_target = Math.max(1, Math.min(call.book.bid, call.book.ask - 1));
      call.signer = "LIVE_EXTERNAL_BBO_INITIAL_AIM";
    }
  }

  _breathingTick(row, leg) {
    if (leg === "NIK") return false;
    return super._breathingTick(row, leg);
  }

  process(row) {
    const order = this.orders.NIK, book = row.books.NIK;
    if (row.event_kind === "BBO_NIK" && order && !this.fills.NIK && validBook(book)
        && book.ask < order.price) {
      const enoughDwell = book.ask_dwell_seconds >= DWELL_SECONDS;
      const enoughCapacity = Number.isFinite(book.ask_capacity_at_top) && book.ask_capacity_at_top >= order.quantity;
      if (!enoughDwell || !enoughCapacity) {
        const before = order.price;
        this._closeOrder("NIK", row, "ASK_REACHED_WITHOUT_CAPACITY_PROOF");
        this.staleAskWait = { epoch: row.epoch, sequence: row.sequence, ask: book.ask };
        this._record(row, {
          material: true, leg: "NIK", organ: "LIVE_ASK_MAKER_SAFETY",
          door_opened: "WAIT_FOR_STRICTLY_LATER_PERSISTENT_ASK", signer: "CURRENT_EXTERNAL_BEST_ASK",
          action: `CANCEL_NIK_${before}__NO_SAME_RECEIPT_REPOST`,
          arithmetic: `ask ${book.ask}<resting ${before}; dwell ${book.ask_dwell_seconds}/${DWELL_SECONDS}; capacity ${book.ask_capacity_at_top ?? "UNKNOWN"}/${REQUIRED_QUANTITY}; ${before}->EMPTY`,
          declined: "same-receipt repost, bid-only chase, and fill without capacity",
          code_path: "LiveBookInitialAimColdReplay.process:makerSafetyBeforeRouter",
          english: "The external ask reached the order without both dwell and five-contract capacity proof. The order was cancelled and this receipt could not create or fill a replacement.",
        });
        return;
      }
    }
    if (row.event_kind === "BBO_NIK" && this.staleAskWait && !this.orders.NIK
        && !this.fills.NIK && !this.patience && row.epoch > this.staleAskWait.epoch
        && validBook(book) && book.ask_dwell_seconds >= DWELL_SECONDS) {
      const target = Math.max(1, Math.min(book.bid, book.ask - 1));
      this.targetCeilings.NIK = target;
      const placed = this._place("NIK", target, row, "PERSISTENT_ASK_REENTRY", "strictly later persistent external ask");
      this.staleAskWait = null;
      this._record(row, {
        material: true, leg: "NIK", organ: "PERSISTENT_ASK_REENTRY",
        door_opened: "MAKER_SAFE_EXPOSURE", signer: "CURRENT_EXTERNAL_BBO",
        action: `PLACE_NIK_${placed.price}`,
        arithmetic: `dwell ${book.ask_dwell_seconds}>=${DWELL_SECONDS}; min(bid ${book.bid}, ask-1 ${book.ask - 1})=${placed.price}`,
        declined: "same-receipt fill and inherited depth constant",
        code_path: "LiveBookInitialAimColdReplay.process:strictlyLaterReentry -> ColdReplay._place",
        english: "A strictly later persistent ask reopened maker-safe exposure at the live touch.",
      });
    }
    return super.process(row);
  }
}

function runLiveBookColdReplay(rawRows, trace, capacity) {
  const rows = enrichRows(rawRows, capacity);
  const replay = new LiveBookInitialAimColdReplay({ trace });
  for (const row of rows) replay.process(row);
  return replay.finish(rows[rows.length - 1]);
}

function simulateNikEvent(config, rawRows, trace, capacity, scenario) {
  const replay = scenario === "live_book_initial_aim"
    ? runLiveBookColdReplay(rawRows, trace, capacity)
    : runColdReplay({ rawRows, trace, scenario, capacityBySequence: capacity });
  const legs = {};
  for (const leg of config.legs) {
    const fill = replay.fills[leg.id], entry = fill?.price ?? null;
    const absent = replay.capacity_evidence_absent.filter((row) => row.leg === leg.id);
    legs[leg.id] = {
      ticker: leg.ticker, orientation: leg.orientation, price_region: leg.price_region,
      entry_cents: entry,
      accounting_status: fill ? "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN" : absent.length ? "EVIDENCE_ABSENT" : "NOT_FILLED",
      fill,
      pair_reference_cents: "NOT_BOUND", delta_to_pair_reference_cents: "NOT_BOUND",
      own_window1_close_cents: leg.close, delta_to_own_window1_close_cents: delta(entry, leg.close),
      own_bell_price_cents: leg.bell_price, delta_to_own_bell_price_cents: delta(entry, leg.bell_price),
      own_ask_reachable_low_cents: leg.ask_low, delta_to_own_ask_reachable_low_cents: delta(entry, leg.ask_low),
      change_status: {
        orientation_conditioned_initial_tree: replay.material_decisions.some((row) => row.organ === "INITIAL_ENTRY_TREE" && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        quiet_book_anchor: replay.material_decisions.some((row) => row.organ === "QUIET_BOOK_ANCHOR" && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        per_tick_ask_breathing: replay.material_decisions.some((row) => row.organ === "LIVE_ASK_TOUCH" && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        sibling_conditioned_faller_patience: replay.material_decisions.some((row) => ["SIBLING_REALIZED_SHAPE", "ASK_DWELL_PATIENCE_RELEASE"].includes(row.organ) && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        ask_only_dwell_reachability: fill || absent.length ? "FIRED" : "DID_NOTHING",
        ...(scenario === "live_book_initial_aim" ? {
          live_book_initial_aim: replay.material_decisions.some((row) => row.organ === "INITIAL_ENTRY_TREE" && (row.leg === leg.id || String(row.action).includes(`_${leg.id}_`)) && row.signer === "LIVE_EXTERNAL_BBO_INITIAL_AIM") ? "FIRED" : "DID_NOTHING",
          bid_only_reanchor_suppressed: leg.orientation === "FALLER" ? "FIRED" : "DID_NOTHING",
          stale_non_maker_order_cancelled: replay.material_decisions.some((row) => row.organ === "LIVE_ASK_MAKER_SAFETY" && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        } : {}),
      },
    };
  }
  const complete = Object.values(legs).every((leg) => leg.accounting_status === "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN");
  return { event_id: config.eventId, category: config.category, completed_capacity_proven_pair: complete, integrity_hold: complete && Object.values(legs).every((leg) => leg.delta_to_own_window1_close_cents <= 0), legs, decisions: replay.decision_ledger };
}

function simulateCorrectedEvent(config) {
  const correctedLegs = config.legs.map((leg) => {
    if (leg.orientation !== "FALLER") return { ...leg };
    const books = config.tickRows.filter((row) => row.ticker === leg.ticker && row.ts <= leg.consultation_ts && validBook(row));
    const book = books.length ? books[books.length - 1] : null;
    if (!book) return { ...leg };
    return { ...leg, inherited_atlas_initial_aim: leg.initial_aim, initial_aim: Math.max(1, Math.min(book.bid, book.ask - 1)), live_book_initial_receipt: book.source_receipt };
  });
  const result = simulateCurrentEvent({ ...config, legs: correctedLegs });
  for (const leg of correctedLegs) {
    const out = result.legs[leg.id];
    out.change_status.live_book_initial_aim = leg.orientation === "FALLER" && leg.live_book_initial_receipt ? "FIRED" : "DID_NOTHING";
    out.change_status.bid_only_reanchor_suppressed = leg.orientation === "FALLER" ? "FIRED" : "DID_NOTHING";
    out.change_status.stale_non_maker_order_cancelled = "DID_NOTHING";
    out.initial_aim_receipt = leg.live_book_initial_receipt || leg.orientation_source;
    out.inherited_atlas_initial_aim = leg.inherited_atlas_initial_aim ?? leg.initial_aim;
  }
  return result;
}

function capacityProvenAskFloor(rows, right) {
  const since = Array(100).fill(null);
  let best = null;
  let last = null;
  const inspect = (book, ts, endpoint = false) => {
    if (!validBook(book)) return;
    for (let limit = 1; limit <= 99; limit += 1) {
      if (book.ask > limit) { since[limit] = null; continue; }
      if (since[limit] === null) since[limit] = book.ts;
      const dwell = ts - since[limit];
      if (dwell < DWELL_SECONDS) continue;
      const capacity = book.asks.filter(([price]) => price <= limit).reduce((sum, row) => sum + row[1], 0);
      if (capacity < REQUIRED_QUANTITY) continue;
      if (!best || limit < best.limit_cents || (limit === best.limit_cents && ts < best.evidence_ts)) {
        best = {
          limit_cents: limit,
          evidence_ts: ts,
          dwell_seconds: dwell,
          displayed_capacity: capacity,
          top_five_asks: book.asks,
          source_receipt: endpoint ? `${book.source_receipt}; right-endpoint-carry` : book.source_receipt,
        };
      }
    }
  };
  for (const row of rows) { inspect(row, row.ts); last = row; }
  if (last && last.ts < right) inspect(last, right, true);
  return best;
}

function partitions(rows, keyFn, fields) {
  const out = {};
  for (const row of rows) {
    const key = keyFn(row);
    if (!out[key]) out[key] = Object.fromEntries(fields.map((field) => [field, 0]));
    for (const field of fields) if (row[field]) out[key][field] += 1;
  }
  return out;
}

function suppressionCensus(rescore, quoteRows) {
  const reach = new Map(quoteRows.map((row) => [`${row.event_id}|${row.leg}`, integer(row.quote_10s_floor_limit_cents)]));
  const rows = [];
  for (const event of rescore.events.filter((row) => row.fill_model_id === "QUOTE_TOUCH_OR_PRINT_DWELL_10_V1" && row.mode === "ATLAS")) {
    for (const [legId, leg] of Object.entries(event.legs)) {
      const aim = integer(leg.first_live_aim?.path_aim);
      const askLow = reach.get(`${event.event_id}|${legId}`) ?? null;
      const unfilled = !leg.filled;
      const aimBelowAllReach = unfilled && aim !== null && askLow !== null && aim < askLow;
      const singleExposure = aimBelowAllReach && Number(leg.orders_posted) === 1;
      rows.push({
        event_id: event.event_id, leg_id: legId, category: event.category,
        price_region: leg.first_live_aim?.page?.split("|")[2] || "UNAVAILABLE",
        initial_aim_cents: aim, ask_reachable_low_10s_cents: askLow,
        aim_minus_reachable_low_cents: aim !== null && askLow !== null ? aim - askLow : null,
        unfilled, orders_posted: Number(leg.orders_posted),
        initial_aim_below_every_ask_reach: aimBelowAllReach,
        causal_status: singleExposure ? "PROVEN_ONLY_EXPOSURE_BELOW_ALL_ASK_REACH"
          : aimBelowAllReach ? "ELIGIBLE_BUT_LATER_EXPOSURES_REQUIRE_INTERVAL_STREAM"
            : unfilled && askLow === null ? "ASK_REACH_UNAVAILABLE" : "NOT_IN_SUPPRESSION_SET",
      });
    }
  }
  const suppressed = rows.filter((row) => row.initial_aim_below_every_ask_reach);
  const proven = suppressed.filter((row) => row.causal_status === "PROVEN_ONLY_EXPOSURE_BELOW_ALL_ASK_REACH");
  const ambiguous = suppressed.filter((row) => row.causal_status === "ELIGIBLE_BUT_LATER_EXPOSURES_REQUIRE_INTERVAL_STREAM");
  const groups = {};
  for (const row of rows) {
    const key = `${row.category}|${row.price_region}`;
    if (!groups[key]) groups[key] = { category: row.category, price_region: row.price_region, legs: 0, unfilled_legs: 0, comparable_unfilled_legs: 0, initial_aim_below_all_ask_reach: 0, proven_only_exposure_below_all_reach: 0, later_exposure_sequence_indeterminate: 0, identities: [] };
    const cell = groups[key]; cell.legs += 1;
    if (row.unfilled) cell.unfilled_legs += 1;
    if (row.unfilled && row.ask_reachable_low_10s_cents !== null) cell.comparable_unfilled_legs += 1;
    if (row.initial_aim_below_every_ask_reach) cell.initial_aim_below_all_ask_reach += 1;
    if (row.causal_status === "PROVEN_ONLY_EXPOSURE_BELOW_ALL_ASK_REACH") cell.proven_only_exposure_below_all_reach += 1;
    if (row.causal_status === "ELIGIBLE_BUT_LATER_EXPOSURES_REQUIRE_INTERVAL_STREAM") cell.later_exposure_sequence_indeterminate += 1;
    if (row.initial_aim_below_every_ask_reach) cell.identities.push(`${row.event_id}/${row.leg_id}`);
  }
  return {
    schema_version: "WINDOW1_INITIAL_AIM_FILL_SUPPRESSION_CENSUS_V1",
    population_events: 804,
    population_legs: rows.length,
    unfilled_legs: rows.filter((row) => row.unfilled).length,
    unfilled_legs_with_ask_reach: rows.filter((row) => row.unfilled && row.ask_reachable_low_10s_cents !== null).length,
    eligible_initial_aim_below_every_ask_reach_legs: suppressed.length,
    affected_distinct_events: new Set(suppressed.map((row) => row.event_id)).size,
    proven_only_exposure_below_every_ask_reach_legs: proven.length,
    later_exposure_sequence_indeterminate_legs: ambiguous.length,
    causal_wording: "Only the one-exposure subset proves from this flattened ledger that every posted exposure was below all 10-second ask reach. The wider eligible set proves first-aim suppression but requires interval streams to attribute the final no-fill solely to the first aim.",
    category_price_region: groups,
    rows,
  };
}

async function loadFiveInputs() {
  const selection = JSON.parse(fs.readFileSync(selectionPath));
  const orientation = JSON.parse(fs.readFileSync(orientationPath));
  const deltaReplay = JSON.parse(fs.readFileSync(deltaReplayPath));
  const quoteRows = parseCsv(fs.readFileSync(quoteLegsPath, "utf8"));
  const bellRows = JSON.parse(fs.readFileSync(bellPath)).leg_rows;
  const selectedIds = new Set(selection.games.map((row) => row.event_id));
  const orientationByEvent = Object.fromEntries(orientation.events.filter((row) => selectedIds.has(row.event)).map((row) => [row.event, row]));
  const deltaByEvent = Object.fromEntries(deltaReplay.events.filter((row) => selectedIds.has(row.event_id)).map((row) => [row.event_id, row]));
  const quoteByKey = new Map(quoteRows.map((row) => [`${row.event_id}|${row.leg}`, row]));
  const bellByKey = new Map(bellRows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const tickRowsByTicker = {}, bounds = {}, configs = [], tickSources = {};
  for (const game of selection.games) {
    const o = orientationByEvent[game.event_id], d = deltaByEvent[game.event_id];
    const legs = Object.keys(o.legs).sort().map((legId) => {
      const q = quoteByKey.get(`${game.event_id}|${legId}`), b = bellByKey.get(`${game.event_id}|${legId}`);
      const ticker = q.ticker; bounds[ticker] = { left: Number(q.left_ts), right: Number(q.right_ts) };
      if (!tickRowsByTicker[ticker]) { const loaded = readTickRows(ticker, bounds[ticker].left, bounds[ticker].right); tickRowsByTicker[ticker] = loaded.rows; tickSources[ticker] = loaded.file; }
      const firstBook = tickRowsByTicker[ticker].find(validBook);
      const mode = o.legs[legId].orientation_initial.mode;
      return { id: legId, ticker, orientation: mode.includes("riser") ? "RISER" : "FALLER", orientation_source: `${path.relative(repo, orientationPath).replaceAll("\\", "/")}#${game.event_id}/${legId}`, initial_aim: Number(o.legs[legId].orientation_initial.aim), consultation_ts: Number(d.legs[legId].first_comparable_decision_ts), close: Number(d.legs[legId].close.price_cents), bell_price: Number(b.close_price_cents), ask_low: integer(q.quote_10s_floor_limit_cents), price_region: priceRegion(firstBook?.bid ?? null), price_region_source: firstBook?.source_receipt || "UNAVAILABLE" };
    });
    const q0 = quoteByKey.get(`${game.event_id}|${legs[0].id}`), b0 = bellByKey.get(`${game.event_id}|${legs[0].id}`);
    configs.push({ eventId: game.event_id, category: game.category, left: Number(q0.left_ts), right: Number(q0.right_ts), scheduled: Number(q0.scheduled_start_ts), bell: Number(b0.exact_bell_ts), legs });
  }
  const printRows = await readPrintRows(Object.keys(bounds), bounds);
  const nikRaw = parseCsv(fs.readFileSync(nikClockPath, "utf8"));
  return { configs, tickRowsByTicker, tickSources, printRows, nikRaw, nikTrace: JSON.parse(fs.readFileSync(nikTracePath)), nikCapacity: projectNikCapacity(nikRaw, tickRowsByTicker), quoteRows };
}

function compact(event) {
  return { event_id: event.event_id, category: event.category, completed_capacity_proven_pair: event.completed_capacity_proven_pair, integrity_hold: event.integrity_hold, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { ticker: leg.ticker, orientation: leg.orientation, price_region: leg.price_region, entry_cents: leg.entry_cents, accounting_status: leg.accounting_status, pair_reference_cents: "NOT_BOUND", delta_to_pair_reference_cents: "NOT_BOUND", own_window1_close_cents: leg.own_window1_close_cents, delta_to_own_window1_close_cents: leg.delta_to_own_window1_close_cents, own_bell_price_cents: leg.own_bell_price_cents, delta_to_own_bell_price_cents: leg.delta_to_own_bell_price_cents, own_ask_reachable_low_cents: leg.own_ask_reachable_low_cents, delta_to_own_ask_reachable_low_cents: leg.delta_to_own_ask_reachable_low_cents, fill: leg.fill, change_status: leg.change_status }])) };
}

async function capacityCeiling(scanRows) {
  const rows = [], byEvent = new Map(), tickSources = {};
  for (const source of scanRows) {
    const proof = source.capacity_proven_floor;
    tickSources[source.ticker] = source.source;
    const row = { event_id: source.event_id, leg_id: source.leg_id, ticker: source.ticker, category: source.category, price_region: priceRegion(integer(source.window1_open_cents)), window1_close_cents: integer(source.window1_close_cents), ask_reachable_low_10s_cents: integer(source.ask_reachable_low_10s_cents), capacity_proven_floor: proof, malformed_source_rows_rejected: source.malformed_source_rows_rejected, status: proof ? "PROVEN_FIVE_CONTRACT_ASK_FLOOR" : "PRICE_SEEN_CAPACITY_UNPROVED" };
    rows.push(row); if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row);
  }
  const events = [];
  for (const [eventId, legs] of byEvent) {
    const oldComparable = legs.length === 2 && legs.every((leg) => Number.isInteger(leg.ask_reachable_low_10s_cents) && Number.isInteger(leg.window1_close_cents));
    const oldNegative = oldComparable && legs.reduce((sum, leg) => sum + leg.ask_reachable_low_10s_cents - leg.window1_close_cents, 0) < 0;
    const proven = legs.length === 2 && legs.every((leg) => leg.capacity_proven_floor && Number.isInteger(leg.window1_close_cents));
    const combinedDelta = proven ? legs.reduce((sum, leg) => sum + leg.capacity_proven_floor.limit_cents - leg.window1_close_cents, 0) : null;
    events.push({ event_id: eventId, category: legs[0]?.category, price_region_pair: legs.map((leg) => leg.price_region).sort().join("+"), old_ask_only_10s_comparable: oldComparable, old_ask_only_negative: oldNegative, capacity_proven_pair: proven, capacity_proven_combined_delta_to_close_cents: combinedDelta, capacity_proven_negative: proven && combinedDelta < 0, statuses: legs.map((leg) => `${leg.leg_id}:${leg.status}`) });
  }
  const oldNegative = events.filter((row) => row.old_ask_only_negative);
  const capacityNegative = events.filter((row) => row.capacity_proven_negative);
  const partitionRows = events.map((row) => ({ ...row, old: row.old_ask_only_negative, proven: row.capacity_proven_negative, removed: row.old_ask_only_negative && !row.capacity_proven_negative }));
  return { schema_version: "WINDOW1_ASK_10S_FIVE_CONTRACT_CEILING_V1", population_events: events.length, leg_rows: rows.length, old_ask_only_10s_negative_ceiling: oldNegative.length, capacity_proven_ask_only_10s_negative_ceiling: capacityNegative.length, removed_by_capacity_law: oldNegative.length - capacityNegative.length, removed_event_ids: oldNegative.filter((row) => !row.capacity_proven_negative).map((row) => row.event_id), by_category_and_price_region_pair: partitions(partitionRows, (row) => `${row.category}|${row.price_region_pair}`, ["old", "proven", "removed"]), events, legs: rows, tick_sources: tickSources };
}

async function build() {
  const input = await loadFiveInputs();
  const current = [], corrected = [];
  for (const event of input.configs) {
    const ticks = event.legs.flatMap((leg) => input.tickRowsByTicker[leg.ticker]);
    const prints = input.printRows.filter((row) => event.legs.some((leg) => leg.ticker === row.ticker));
    if (event.eventId.endsWith("NIKVRB")) {
      current.push(simulateNikEvent(event, input.nikRaw, input.nikTrace, input.nikCapacity, "ask_dwell"));
      corrected.push(simulateNikEvent(event, input.nikRaw, input.nikTrace, input.nikCapacity, "live_book_initial_aim"));
    } else {
      current.push(simulateCurrentEvent({ ...event, tickRows: ticks, printRows: prints }));
      corrected.push(simulateCorrectedEvent({ ...event, tickRows: ticks, printRows: prints }));
    }
  }
  const currentCompact = current.map(compact), correctedCompact = corrected.map(compact);
  const changeRows = [];
  for (let index = 0; index < current.length; index += 1) for (const legId of Object.keys(current[index].legs)) {
    const belongs = (row) => row.leg === legId || row.leg_id === legId || String(row.action || "").includes(`_${legId}_`);
    const currentInitial = (current[index].decisions || []).find((row) => belongs(row) && (row.rule === "ORIENTATION_CONDITIONED_INITIAL_TREE" || row.organ === "INITIAL_ENTRY_TREE"));
    const correctedInitial = (corrected[index].decisions || []).find((row) => belongs(row) && (row.rule === "ORIENTATION_CONDITIONED_INITIAL_TREE" || row.organ === "INITIAL_ENTRY_TREE"));
    changeRows.push({ event_id: current[index].event_id, category: current[index].category, leg_id: legId, orientation: current[index].legs[legId].orientation, current_entry_cents: current[index].legs[legId].entry_cents, corrected_entry_cents: corrected[index].legs[legId].entry_cents, entry_change_cents: Number.isInteger(current[index].legs[legId].entry_cents) && Number.isInteger(corrected[index].legs[legId].entry_cents) ? corrected[index].legs[legId].entry_cents - current[index].legs[legId].entry_cents : null, current_initial_decision: currentInitial || null, corrected_initial_decision: correctedInitial || null, five_stack_switches: corrected[index].legs[legId].change_status });
  }
  const frozen = JSON.parse(fs.readFileSync(frozenFivePath));
  const frozenCore = frozen.events.map((event) => ({ event_id: event.event_id, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, [leg.entry_cents, leg.accounting_status, leg.delta_to_own_window1_close_cents, leg.delta_to_own_bell_price_cents, leg.delta_to_own_ask_reachable_low_cents]])) }));
  const currentCore = currentCompact.map((event) => ({ event_id: event.event_id, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, [leg.entry_cents, leg.accounting_status, leg.delta_to_own_window1_close_cents, leg.delta_to_own_bell_price_cents, leg.delta_to_own_ask_reachable_low_cents]])) }));
  if (JSON.stringify(frozenCore) !== JSON.stringify(currentCore)) throw new Error("current-branch replay identity mismatch");
  const rescore = JSON.parse(fs.readFileSync(legacyRescorePath));
  const suppression = suppressionCensus(rescore, input.quoteRows);
  if (suppression.eligible_initial_aim_below_every_ask_reach_legs !== 1137 || suppression.proven_only_exposure_below_every_ask_reach_legs !== 983 || suppression.later_exposure_sequence_indeterminate_legs !== 154) throw new Error(`suppression fixture mismatch ${JSON.stringify({ eligible: suppression.eligible_initial_aim_below_every_ask_reach_legs, proven: suppression.proven_only_exposure_below_every_ask_reach_legs, ambiguous: suppression.later_exposure_sequence_indeterminate_legs })}`);
  const capacityScan = JSON.parse(fs.readFileSync(capacityScanPath));
  if (capacityScan.row_count !== 1608) throw new Error(`capacity scan row mismatch ${capacityScan.row_count}`);
  const ceiling = await capacityCeiling(capacityScan.rows);
  if (ceiling.old_ask_only_10s_negative_ceiling !== 532) throw new Error(`old ceiling mismatch ${ceiling.old_ask_only_10s_negative_ceiling}`);
  const legacy = rescore.matrix.QUOTE_OR_PRINT_DWELL_10.ATLAS;
  const invalidation = { schema_version: "WINDOW1_LEGACY_CAPACITY_INVALIDATION_V1", legacy_fill_assignments: legacy.legs_filled, legacy_pair_completions: legacy.pairs_completed, assignments_with_bound_five_contract_capacity_identity: 0, creditable_assignments_under_current_law: 0, creditable_pair_completions_under_current_law: 0, distinction: "The 532 ask-only opportunity ceiling is recomputed separately from top-five books; it is not reduced by subtracting 217 leg assignments." };
  if (invalidation.legacy_fill_assignments !== 217 || invalidation.legacy_pair_completions !== 49) throw new Error("legacy result identity mismatch");
  const tickSourceManifest = ceiling.tick_sources;
  delete ceiling.tick_sources;
  const receipt = { schema_version: "WINDOW1_LIVE_BOOK_INITIAL_AIM_REPLAY_V1", cold: true, outcome_knowledge_consumed: false, implementation: { faller_initial_price: "min(current live bid, current live ask - 1) at the existing causal initial-decision receipt", later_bid_or_last_only_change: "HOLD; cannot chase lower", ask_reaches_order_without_dwell_and_capacity: "CANCEL; strictly later persistent ask required for re-entry", riser_path: "unchanged", sibling_patience: "unchanged, including still-unvalidated recurrence>0 and inherited 5-cent release" }, current_branch: currentCompact, corrected_branch: correctedCompact };
  const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/codex/window1-live-consolidated";
  const report = ["# Window 1 live-book initial-aim replay", "", "This is a cold, score-free five-event replay. The five-event set includes NIKVRB; NIKVRB is also retained as the detailed specimen, not counted as a sixth game.", "", "Raw replay/reference source:", `${rawBase}/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/REPLAY_AND_REFERENCE_PANEL.json`, "", "Raw five-event change source:", `${rawBase}/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/FIVE_EVENT_CHANGE_RECEIPT.json`, "", "Raw suppression source:", `${rawBase}/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/INITIAL_AIM_FILL_SUPPRESSION_CENSUS.json`, "", "Raw capacity-ceiling source:", `${rawBase}/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/ASK_10S_FIVE_CONTRACT_CEILING.json`, "", "Raw legacy-invalidation source:", `${rawBase}/.claude/window1_live_v4_replay/live_book_initial_aim_20260731/LEGACY_CAPACITY_INVALIDATION_RECEIPT.json`, "", "## Per-leg current versus corrected", ""];
  for (let i = 0; i < currentCompact.length; i += 1) {
    report.push(`### ${currentCompact[i].event_id}`, "", "| Branch | Leg | Entry | Own W1 close | Δclose | Own bell | Δbell | Own ask-low (10s) | Δask-low | Independent pair ref | Δpair ref |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|");
    for (const [branch, event] of [["current", currentCompact[i]], ["corrected", correctedCompact[i]]]) for (const [legId, leg] of Object.entries(event.legs)) report.push(`| ${branch} | ${legId} | ${leg.entry_cents ?? "NO_CREDIT"} | ${leg.own_window1_close_cents ?? "NULL"} | ${signed(leg.delta_to_own_window1_close_cents)} | ${leg.own_bell_price_cents ?? "NULL"} | ${signed(leg.delta_to_own_bell_price_cents)} | ${leg.own_ask_reachable_low_cents ?? "NULL"} | ${signed(leg.delta_to_own_ask_reachable_low_cents)} | NOT_BOUND | NOT_BOUND |`);
    report.push("");
  }
  report.push("## Population diagnostics", "", `- Initial aim was below every 10-second ask reach on ${suppression.eligible_initial_aim_below_every_ask_reach_legs} unfilled legs across ${suppression.affected_distinct_events} events.`, `- ${suppression.proven_only_exposure_below_every_ask_reach_legs} legs had exactly one posted exposure, proving the only bid was unreachable. The other ${suppression.later_exposure_sequence_indeterminate_legs} require interval streams before assigning sole causality.`, `- The old ${ceiling.old_ask_only_10s_negative_ceiling} event price-reach ceiling becomes ${ceiling.capacity_proven_ask_only_10s_negative_ceiling} when both legs require contemporaneous top-five capacity of at least five after ten seconds; ${ceiling.removed_by_capacity_law} are removed from creditable opportunity.`, `- The old ATLAS 10-second replay's ${invalidation.legacy_fill_assignments} leg assignments and ${invalidation.legacy_pair_completions} pair completions have zero bound capacity identities. Under the current law those specific completion claims become zero. The ${invalidation.legacy_fill_assignments} leg rows are not subtracted from the ${ceiling.old_ask_only_10s_negative_ceiling} event ceiling; the capacity ceiling is independently recomputed at event grain.`, "", "All partitions and identities are in the JSON receipts. No scorer, holdout, live, or trading surface was used.", "");
  report.splice(report.indexOf("## Population diagnostics"), 0,
    "## Five-game gate", "",
    "The change does **not** pass the five-game gate. NIKVRB remains 68/18, but ATP_CHALL HUR (the faller) changes from 41 to 47. Its own-close delta moves from -1 to +5 and its ask-low gap from +4 to +10. The live-BBO initial signer fired in a quiet-book faller where the earlier deeper order was beneficial; preventing bid-only chase did not provide a later patience signal. This is the breaking shape. No 804-policy replay was run.", "");
  const files = {
    "REPLAY_AND_REFERENCE_PANEL.json": canonical(receipt),
    "FIVE_EVENT_CHANGE_RECEIPT.json": canonical({ schema_version: "WINDOW1_FIVE_EVENT_LIVE_BOOK_INITIAL_AIM_CHANGE_V1", rows: changeRows }),
    "INITIAL_AIM_FILL_SUPPRESSION_CENSUS.json": canonical(suppression),
    "ASK_10S_FIVE_CONTRACT_CEILING.json": canonical(ceiling),
    "LEGACY_CAPACITY_INVALIDATION_RECEIPT.json": canonical(invalidation),
    "PRIVATE_TICK_SOURCE_MANIFEST.json": canonical({ source: "frozen development top-five tick cache", ticker_count: Object.keys(tickSourceManifest).length, rows: tickSourceManifest }),
    "RAW_CAPACITY_FLOOR_SCAN.json": canonical(capacityScan),
    "SOURCE_HASH_MANIFEST.json": canonical({ committed: Object.fromEntries([__filename, path.join(repo, "arb-executor/analysis/build_window1_ask_capacity_floor.js"), selectionPath, orientationPath, deltaReplayPath, quoteLegsPath, quoteCensusPath, bellPath, nikClockPath, nikTracePath, legacyRescorePath, frozenFivePath].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])), private_development_prints: { file: path.basename(printsPath), bytes: fs.statSync(printsPath).size, sha256: hashFile(printsPath) }, private_tick_files: { count: Object.keys(tickSourceManifest).length, manifest_sha256: sha256(Buffer.from(canonical(tickSourceManifest))) } }),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ scorer_imported: false, scorer_invoked: false, holdout_access: false, live_access: false, network_access: false, order_access: false, position_access: false, exit_access: false, settlement_access: false, dca_access: false }),
  };
  files["DETERMINISM_RECEIPT.json"] = canonical({ complete_package_builds: 2, package_builds_byte_identical: true, complete_raw_capacity_scans: 2, raw_capacity_scans_byte_identical: true, raw_capacity_scan_sha256: sha256(fs.readFileSync(capacityScanPath)), core_sha256: sha256(Buffer.from(JSON.stringify({ receipt, suppression, ceiling, invalidation }))) });
  return { files, report: report.join("\n"), summary: { events: corrected.length, suppression: suppression.proven_only_exposure_below_every_ask_reach_legs, ceiling: ceiling.capacity_proven_ask_only_10s_negative_ceiling } };
}

async function main() {
  const first = await build(); const second = await build();
  if (JSON.stringify(first) !== JSON.stringify(second)) throw new Error("two-build determinism mismatch");
  const artifactRows = Object.entries(first.files).map(([name, content]) => ({ path: `.claude/window1_live_v4_replay/live_book_initial_aim_20260731/${name}`, bytes: Buffer.byteLength(content), sha256: sha256(Buffer.from(content)) }));
  artifactRows.push({ path: path.relative(repo, reportPath).replaceAll("\\", "/"), bytes: Buffer.byteLength(first.report), sha256: sha256(Buffer.from(first.report)) });
  first.files["ARTIFACT_HASH_MANIFEST.json"] = canonical({ artifacts: artifactRows });
  if (checkOnly) {
    for (const [name, content] of Object.entries(first.files)) if (!fs.readFileSync(path.join(outDir, name)).equals(Buffer.from(content))) throw new Error(`artifact mismatch ${name}`);
    if (fs.readFileSync(reportPath, "utf8") !== first.report) throw new Error("report mismatch");
    process.stdout.write(canonical({ status: "CHECK_PASS", ...first.summary })); return;
  }
  fs.mkdirSync(outDir, { recursive: true });
  for (const [name, content] of Object.entries(first.files)) fs.writeFileSync(path.join(outDir, name), content);
  fs.mkdirSync(path.dirname(reportPath), { recursive: true }); fs.writeFileSync(reportPath, first.report);
  process.stdout.write(canonical({ status: "BUILT", ...first.summary }));
}

if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = { capacityProvenAskFloor, suppressionCensus };
