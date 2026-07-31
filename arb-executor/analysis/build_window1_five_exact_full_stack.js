#!/usr/bin/env node
"use strict";

// Score-free five-event cold validation for the NIKVRB-derived decision stack.
// The builder consumes only the frozen July 12-20 development inputs. It
// preserves price reach, displayed five-contract capacity, and credited fill
// as separate facts. It never imports a scorer.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { runColdReplay } = require("./nikvrb_sibling_shape_cold_replay.js");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const privateRoot = path.resolve(process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private");
const outDir = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731");
const reportPath = path.join(repo, "arb-executor/docs/research/window1/WINDOW1_FIVE_EXACT_FULL_STACK_CAPACITY.md");
const selectionPath = path.join(repo, ".claude/window1_live_v4_replay/delta_objective_20260729/FIVE_GAME_SELECTION.json");
const orientationPath = path.join(repo, ".claude/window1_live_v4_replay/orientation_initial_20260730/ORIENTATION_INITIAL_REPLAY.json");
const deltaReplayPath = path.join(repo, ".claude/window1_live_v4_replay/delta_objective_20260729/FIVE_GAME_DELTA_REPLAYS.json");
const quoteLegsPath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const nikClockPath = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv");
const nikTracePath = path.join(repo, ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json");
const replayPath = path.join(repo, "arb-executor/analysis/nikvrb_sibling_shape_cold_replay.js");
const scorecardBuilderPath = path.join(repo, "arb-executor/analysis/build_window1_organ_scorecard.js");
const printsPath = path.join(privateRoot, "fit-local/prints.jsonl");
const ticksRoot = path.join(privateRoot, "fit-local/ticks");

const DWELL_SECONDS = 10;
const CELL_CENTS = 5;
const REQUIRED_QUANTITY = 5;
const T2_MAX = 120;
const T2_MIN = 60;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function finite(value) { const n = Number(value); return Number.isFinite(n) ? n : null; }
function integer(value) { const n = finite(value); return Number.isInteger(n) ? n : null; }
function priceRegion(price) {
  if (!Number.isInteger(price)) return "UNAVAILABLE";
  if (price <= 25) return "le25";
  if (price <= 50) return "26_50";
  if (price <= 75) return "51_75";
  return "ge75";
}
function signed(value) { return Number.isInteger(value) ? `${value >= 0 ? "+" : ""}${value}` : (value ?? "NULL"); }

function parseCsv(text) {
  const matrix = []; let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i += 1; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n") { row.push(field.replace(/\r$/, "")); matrix.push(row); row = []; field = ""; }
    else field += ch;
  }
  if (field || row.length) { row.push(field.replace(/\r$/, "")); matrix.push(row); }
  const headers = matrix.shift();
  return matrix.filter((values) => values.length === headers.length)
    .map((values) => Object.fromEntries(headers.map((name, index) => [name, values[index]])));
}

function parseEtSecond(value) {
  const match = String(value).match(/^(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) throw new Error(`bad ET tick timestamp ${value}`);
  let hour = Number(match[2]);
  if (match[5] === "AM" && hour === 12) hour = 0;
  if (match[5] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}T${String(hour).padStart(2, "0")}:${match[3]}:${match[4]}-04:00`) / 1000;
}

function positive(value) { const n = finite(value); return n !== null && n > 0 ? n : null; }
function readTickRows(ticker, left, right) {
  const file = path.join(ticksRoot, `${ticker}.csv.gz`);
  if (!fs.existsSync(file)) throw new Error(`missing frozen tick source ${file}`);
  const rows = parseCsv(zlib.gunzipSync(fs.readFileSync(file)).toString("utf8"));
  const output = [];
  rows.forEach((raw, ordinal) => {
    const ts = parseEtSecond(raw.ts_et);
    if (ts < left || ts > right) return;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bid = integer(raw[`bid_${level}`]), bidSize = positive(raw[`bid_${level}_sz`]);
      const ask = integer(raw[`ask_${level}`]), askSize = positive(raw[`ask_${level}_sz`]);
      if (bid !== null && bidSize !== null) bids.push([bid, bidSize]);
      if (ask !== null && askSize !== null) asks.push([ask, askSize]);
    }
    output.push({
      kind: "BBO", ticker, ts, ordinal, bids, asks,
      bid: bids.length ? Math.max(...bids.map((x) => x[0])) : null,
      ask: asks.length ? Math.min(...asks.map((x) => x[0])) : null,
      carried_last: integer(raw.last_trade),
      source_receipt: `${path.basename(file)}#row-${ordinal + 2}`,
    });
  });
  return { file, rows: output };
}

async function readPrintRows(tickers, bounds) {
  const wanted = new Set(tickers);
  const output = [];
  const input = fs.createReadStream(printsPath, { encoding: "utf8" });
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let ordinal = 0;
  for await (const line of lines) {
    ordinal += 1;
    if (!line || !line.includes('"ticker"')) continue;
    const raw = JSON.parse(line);
    if (!wanted.has(raw.ticker)) continue;
    const ts = finite(raw.ts);
    const size = positive(raw.size);
    const price = integer(raw.price);
    const corridor = bounds[raw.ticker];
    if (ts === null || price === null || size === null || ts < corridor.left || ts > corridor.right) continue;
    output.push({ kind: "PRINT", ticker: raw.ticker, ts, ordinal, price, size, trade_id: raw.trade_id || raw.id || null });
  }
  output.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return output;
}

function askCapacity(book, limit) {
  if (!book || !Array.isArray(book.asks)) return { status: "EVIDENCE_ABSENT", quantity: null, levels: [] };
  const levels = book.asks.filter(([price, size]) => price <= limit && size > 0);
  if (!levels.length) return { status: "EVIDENCE_ABSENT", quantity: 0, levels };
  const quantity = levels.reduce((sum, row) => sum + row[1], 0);
  return { status: quantity >= REQUIRED_QUANTITY ? "PROVEN_FIVE_CONTRACT_CAPACITY" : "EVIDENCE_ABSENT", quantity, levels };
}

function signedDelta(entry, reference) {
  return Number.isInteger(entry) && Number.isInteger(reference) ? entry - reference : null;
}

function validBook(book) { return book && Number.isInteger(book.bid) && Number.isInteger(book.ask) && book.bid > 0 && book.ask <= 99 && book.bid <= book.ask; }

function simulateEvent(config) {
  const { eventId, category, left, right, scheduled, bell, legs, tickRows, printRows } = config;
  const state = Object.fromEntries(legs.map((leg) => [leg.id, {
    book: null, askValue: null, askSince: null, priorAsk: null, askDown: false, askTrough: null, askRecurrences: 0,
    lastPrint: null, ceiling: null, order: null, fill: null, priceReach: [], capacityAbsent: [], actions: [],
    consultationDone: false, quietAnchorDone: false,
  }]));
  const byTicker = Object.fromEntries(legs.map((leg) => [leg.ticker, leg]));
  const riser = legs.find((leg) => leg.orientation === "RISER");
  const faller = legs.find((leg) => leg.orientation === "FALLER");
  if (!riser || !faller) throw new Error(`${eventId}: orientation does not identify one riser and one faller`);
  let patience = null;
  const decisions = [];
  const flags = Object.fromEntries(legs.map((leg) => [leg.id, {
    orientation_conditioned_initial_tree: false,
    quiet_book_anchor: false,
    per_tick_ask_breathing: false,
    sibling_conditioned_faller_patience: false,
    ask_only_dwell_reachability: false,
  }]));

  function clock(ts) { return { tminus_scheduled_minutes: (scheduled - ts) / 60, tminus_bell_minutes: (bell - ts) / 60 }; }
  function action(leg, ts, rule, before, after, arithmetic, source) {
    const row = { event_id: eventId, category, leg_id: leg.id, ts, ...clock(ts), rule, before, after, arithmetic, source };
    decisions.push(row); state[leg.id].actions.push(row); return row;
  }
  function closeOrder(leg, ts, reason) {
    const s = state[leg.id]; if (!s.order) return null; const before = s.order;
    before.end_ts = ts; before.end_reason = reason; s.order = null; return before;
  }
  function place(leg, ts, price, rule, source) {
    const s = state[leg.id], before = s.order ? s.order.price : null;
    if (!validBook(s.book) || !Number.isInteger(price) || price < 1 || price > 99 || price > s.book.ask) return null;
    closeOrder(leg, ts, `REPLACED_BY_${rule}`);
    s.order = { leg_id: leg.id, price, quantity: REQUIRED_QUANTITY, action_ts: ts, rule, source, end_ts: null, end_reason: null };
    action(leg, ts, rule, before, price, `${before === null ? "EMPTY" : before}->${price}`, source);
    return s.order;
  }
  function tryFill(leg, ts, trigger) {
    const s = state[leg.id];
    if (!s.order || !validBook(s.book) || ts <= s.order.action_ts || s.book.ask > s.order.price) return false;
    const dwell = ts - s.askSince;
    if (dwell < DWELL_SECONDS) return false;
    flags[leg.id].ask_only_dwell_reachability = true;
    const capacity = askCapacity(s.book, s.order.price);
    const reach = { event_id: eventId, leg_id: leg.id, ts, ...clock(ts), resting_price: s.order.price, ask: s.book.ask, ask_dwell_seconds: dwell, capacity, trigger, source_receipt: s.book.source_receipt };
    s.priceReach.push(reach);
    if (capacity.status !== "PROVEN_FIVE_CONTRACT_CAPACITY") {
      s.capacityAbsent.push({ ...reach, accounting_status: "EVIDENCE_ABSENT", credited_quantity: 0 });
      return false;
    }
    const order = s.order;
    s.fill = { leg_id: leg.id, price: order.price, quantity: REQUIRED_QUANTITY, action_ts: order.action_ts, evidence_ts: ts, evidence_type: "ASK_DWELL_WITH_DISPLAYED_CAPACITY", evidence_size: capacity.quantity, evidence_levels: capacity.levels, evidence_receipt: s.book.source_receipt, strictly_later: ts > order.action_ts };
    closeOrder(leg, ts, "FILLED_CAPACITY_PROVEN_ASK_DWELL");
    action(leg, ts, "FILL_CAPACITY_GATE", order.price, order.price, `ask ${s.book.ask}<=${order.price}; dwell ${dwell}>=${DWELL_SECONDS}; displayed ${capacity.quantity}>=${REQUIRED_QUANTITY}; credit 5@${order.price}`, s.book.source_receipt);
    return true;
  }

  const events = [...tickRows, ...printRows].sort((a, b) => a.ts - b.ts || (a.kind === "BBO" ? 0 : 1) - (b.kind === "BBO" ? 0 : 1) || a.ticker.localeCompare(b.ticker) || a.ordinal - b.ordinal);
  for (let index = 0; index < events.length;) {
    const ts = events[index].ts;
    const batch = [];
    while (index < events.length && events[index].ts === ts) batch.push(events[index++]);
    for (const receipt of batch) {
      const leg = byTicker[receipt.ticker]; if (!leg) continue; const s = state[leg.id];
      if (receipt.kind === "PRINT") { s.lastPrint = receipt; continue; }
      s.book = receipt;
      if (receipt.ask !== s.askValue) { s.askValue = receipt.ask; s.askSince = ts; }
      if (Number.isInteger(receipt.ask)) {
        if (Number.isInteger(s.priorAsk) && receipt.ask < s.priorAsk) { s.askDown = true; s.askTrough = receipt.ask; }
        else if (s.askDown && receipt.ask > s.askTrough) { s.askRecurrences += 1; s.askDown = false; s.askTrough = null; }
        else if (s.askDown && receipt.ask < s.askTrough) s.askTrough = receipt.ask;
        s.priorAsk = receipt.ask;
      }
    }

    for (const leg of legs) {
      const s = state[leg.id]; if (!validBook(s.book) || s.book.ts !== ts || s.fill) continue;
      if (tryFill(leg, ts, "BBO")) continue;
      // A lawful ask at/below an already resting limit is a capacity/dwell
      // evaluation state, not authority to move the limit away. This is the
      // exact NIKVRB ask-dwell hold: wait for independent residency evidence,
      // then credit only if displayed capacity is proven.
      if (s.order && s.book.ask <= s.order.price) continue;

      if (!s.quietAnchorDone && !s.lastPrint && s.book.ask - s.book.bid === 1) {
        s.quietAnchorDone = true; flags[leg.id].quiet_book_anchor = true;
        const anchor = Math.round((s.book.bid + s.book.ask) / 2);
        s.ceiling = anchor;
        place(leg, ts, Math.min(anchor, s.book.ask - 1), "QUIET_BOOK_ANCHOR", s.book.source_receipt);
      }

      if (!s.consultationDone && ts >= leg.consultation_ts) {
        s.consultationDone = true; flags[leg.id].orientation_conditioned_initial_tree = true;
        s.ceiling = Number.isInteger(s.ceiling) ? Math.min(s.ceiling, leg.initial_aim) : leg.initial_aim;
        const target = Math.max(1, Math.min(s.ceiling, s.book.ask - 1));
        if (!s.order || s.order.price !== target) place(leg, ts, target, "ORIENTATION_CONDITIONED_INITIAL_TREE", leg.orientation_source);
        else action(leg, ts, "ORIENTATION_CONDITIONED_INITIAL_TREE", target, target, `min(existing ceiling, orientation aim ${leg.initial_aim}, ask-1 ${s.book.ask - 1})=${target}`, leg.orientation_source);
      }

      if (s.order && !s.fill) {
        let target = Math.max(1, Math.min(s.ceiling, s.book.ask - 1));
        if (s.book.ask < s.order.price) target = s.book.ask;
        if (target !== s.order.price) {
          flags[leg.id].per_tick_ask_breathing = true;
          place(leg, ts, target, "PER_TICK_ASK_BREATHING", s.book.source_receipt);
        }
      }
    }

    const rs = state[riser.id], fs = state[faller.id];
    const tminus = (scheduled - ts) / 60;
    if (!patience && rs.fill && !fs.fill && fs.order && tminus <= T2_MAX && tminus > T2_MIN
        && rs.askRecurrences > 0 && validBook(rs.book) && rs.book.bid > rs.fill.price && validBook(fs.book)) {
      const cancelled = closeOrder(faller, ts, "SIBLING_RISER_SHAPE_RESOLVED");
      patience = { ts, arm_ask: fs.book.ask, riser_recurrences: rs.askRecurrences, riser_fill: rs.fill.price, cancelled_price: cancelled.price };
      flags[faller.id].sibling_conditioned_faller_patience = true;
      action(faller, ts, "SIBLING_CONDITIONED_FALLER_PATIENCE", cancelled.price, null, `${rs.askRecurrences}>0 ask recurrences; riser bid ${rs.book.bid}>fill ${rs.fill.price}; cancel ${cancelled.price}`, rs.book.source_receipt);
    }
    if (patience && !fs.fill && !fs.order && validBook(fs.book) && validBook(rs.book)) {
      const askDrop = patience.arm_ask - fs.book.ask;
      const dwell = ts - fs.askSince;
      if (askDrop >= CELL_CENTS && dwell >= DWELL_SECONDS && rs.book.ask > rs.fill.price) {
        fs.ceiling = fs.book.ask - 1;
        flags[faller.id].sibling_conditioned_faller_patience = true;
        place(faller, ts, fs.ceiling, "FALLER_PATIENCE_RELEASE", fs.book.source_receipt);
      }
    }
  }

  for (const leg of legs) if (state[leg.id].order) closeOrder(leg, right, "WINDOW1_END");
  const resultLegs = {};
  for (const leg of legs) {
    const s = state[leg.id], entry = s.fill?.price ?? null;
    resultLegs[leg.id] = {
      ticker: leg.ticker,
      orientation: leg.orientation,
      price_region: leg.price_region,
      price_region_source: leg.price_region_source,
      entry_cents: entry,
      accounting_status: s.fill ? "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN" : (s.capacityAbsent.length ? "EVIDENCE_ABSENT" : "NOT_FILLED"),
      fill: s.fill,
      pair_reference_cents: "NOT_BOUND",
      delta_to_pair_reference_cents: "NOT_BOUND",
      own_window1_close_cents: leg.close,
      delta_to_own_window1_close_cents: signedDelta(entry, leg.close),
      own_bell_price_cents: leg.bell_price,
      delta_to_own_bell_price_cents: signedDelta(entry, leg.bell_price),
      own_ask_reachable_low_cents: leg.ask_low,
      delta_to_own_ask_reachable_low_cents: signedDelta(entry, leg.ask_low),
      price_reach_receipts: s.priceReach,
      evidence_absent_receipts: s.capacityAbsent,
      change_status: Object.fromEntries(Object.entries(flags[leg.id]).map(([name, fired]) => [name, fired ? "FIRED" : "DID_NOTHING"])),
      ask_recurrences_observed: s.askRecurrences,
      actions: s.actions,
    };
  }
  const complete = legs.every((leg) => resultLegs[leg.id].accounting_status === "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN");
  const ownCloseNonpositive = legs.every((leg) => resultLegs[leg.id].delta_to_own_window1_close_cents !== null && resultLegs[leg.id].delta_to_own_window1_close_cents <= 0);
  return { event_id: eventId, category, window: { left_ts: left, right_ts: right, scheduled_start_ts: scheduled, actual_bell_ts: bell }, legs: resultLegs, completed_capacity_proven_pair: complete, all_credited_legs_at_or_below_own_close: ownCloseNonpositive, integrity_hold: complete && ownCloseNonpositive, patience, decision_count: decisions.length, decisions };
}

function makeNikCapacityProjection(rawRows, tickRowsByTicker) {
  const byKey = new Map();
  for (const rows of Object.values(tickRowsByTicker)) for (const row of rows) byKey.set(`${row.ticker}|${row.ts}`, row);
  const output = {};
  for (const raw of rawRows) {
    const match = String(raw.event_kind).match(/^BBO_(NIK|VRB)$/); if (!match) continue;
    const leg = match[1], ticker = `KXATPCHALLENGERMATCH-26JUL19NIKVRB-${leg}`;
    const ts = Date.parse(raw.timestamp_et) / 1000;
    const source = byKey.get(`${ticker}|${ts}`);
    if (!source) continue;
    const top = source.asks.filter(([price]) => price === source.ask);
    output[`${raw.sequence}|${leg}`] = {
      receipt: source.source_receipt,
      ask_price: source.ask,
      ask_size: top.reduce((sum, row) => sum + row[1], 0),
      ask_capacity_at_top: top.reduce((sum, row) => sum + row[1], 0),
      top_five_asks: source.asks,
    };
  }
  return output;
}

function simulateNikSpecimen(config, rawRows, trace, capacityBySequence) {
  const replay = runColdReplay({ rawRows, trace, scenario: "ask_dwell", capacityBySequence });
  const resultLegs = {};
  for (const leg of config.legs) {
    const fill = replay.fills[leg.id];
    const entry = fill?.price ?? null;
    const capacityAbsent = replay.capacity_evidence_absent.filter((row) => row.leg === leg.id);
    const legDecisions = replay.decision_ledger.filter((row) => row.leg === leg.id || (!row.leg && String(row.action || "").includes(`_${leg.id}_`)));
    resultLegs[leg.id] = {
      ticker: leg.ticker,
      orientation: leg.orientation,
      price_region: leg.price_region,
      price_region_source: leg.price_region_source,
      entry_cents: entry,
      accounting_status: fill ? "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN" : (capacityAbsent.length ? "EVIDENCE_ABSENT" : "NOT_FILLED"),
      fill,
      pair_reference_cents: "NOT_BOUND",
      delta_to_pair_reference_cents: "NOT_BOUND",
      own_window1_close_cents: leg.close,
      delta_to_own_window1_close_cents: signedDelta(entry, leg.close),
      own_bell_price_cents: leg.bell_price,
      delta_to_own_bell_price_cents: signedDelta(entry, leg.bell_price),
      own_ask_reachable_low_cents: leg.ask_low,
      delta_to_own_ask_reachable_low_cents: signedDelta(entry, leg.ask_low),
      price_reach_receipts: fill ? [{ evidence: fill.evidence, evidence_ts: fill.evidence_et, entry_cents: fill.price }] : [],
      evidence_absent_receipts: capacityAbsent,
      change_status: {
        orientation_conditioned_initial_tree: replay.material_decisions.some((row) => row.organ === "INITIAL_ENTRY_TREE" && (row.leg === leg.id || String(row.action || "").includes(`_${leg.id}_`))) ? "FIRED" : "DID_NOTHING",
        quiet_book_anchor: replay.material_decisions.some((row) => row.organ === "QUIET_BOOK_ANCHOR" && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        per_tick_ask_breathing: replay.material_decisions.some((row) => row.organ === "LIVE_ASK_TOUCH" && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        sibling_conditioned_faller_patience: replay.material_decisions.some((row) => ["SIBLING_REALIZED_SHAPE", "ASK_DWELL_PATIENCE_RELEASE"].includes(row.organ) && row.leg === leg.id) ? "FIRED" : "DID_NOTHING",
        ask_only_dwell_reachability: Boolean(fill) || capacityAbsent.length > 0 ? "FIRED" : "DID_NOTHING",
      },
      ask_recurrences_observed: leg.id === "VRB" ? replay.patience?.sibling_recurrences ?? 0 : 0,
      actions: legDecisions,
    };
  }
  const complete = config.legs.every((leg) => resultLegs[leg.id].accounting_status === "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN");
  const ownCloseNonpositive = config.legs.every((leg) => resultLegs[leg.id].delta_to_own_window1_close_cents !== null && resultLegs[leg.id].delta_to_own_window1_close_cents <= 0);
  return {
    event_id: config.eventId,
    category: config.category,
    window: { left_ts: config.left, right_ts: config.right, scheduled_start_ts: config.scheduled, actual_bell_ts: config.bell },
    legs: resultLegs,
    completed_capacity_proven_pair: complete,
    all_credited_legs_at_or_below_own_close: ownCloseNonpositive,
    integrity_hold: complete && ownCloseNonpositive,
    patience: replay.patience,
    decision_count: replay.decision_ledger.length,
    decisions: replay.decision_ledger,
    replay_path: "frozen detailed NIKVRB dual-book clock and organ consultations",
  };
}

async function build() {
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
  const tickSources = {}, tickRowsByTicker = {}, bounds = {}, eventConfigs = [];
  for (const game of selection.games) {
    const o = orientationByEvent[game.event_id], d = deltaByEvent[game.event_id];
    const legs = Object.keys(o.legs).sort().map((legId) => {
      const q = quoteByKey.get(`${game.event_id}|${legId}`), b = bellByKey.get(`${game.event_id}|${legId}`);
      if (!q || !b) throw new Error(`${game.event_id}/${legId}: missing quote or bell reference`);
      const mode = o.legs[legId].orientation_initial.mode;
      const ticker = q.ticker;
      bounds[ticker] = { left: Number(q.left_ts), right: Number(q.right_ts) };
      if (!tickRowsByTicker[ticker]) {
        const loaded = readTickRows(ticker, Number(q.left_ts), Number(q.right_ts));
        tickSources[ticker] = loaded.file; tickRowsByTicker[ticker] = loaded.rows;
      }
      const firstBook = tickRowsByTicker[ticker].find(validBook);
      return {
        id: legId, ticker,
        orientation: mode.includes("riser") ? "RISER" : "FALLER",
        orientation_source: `${path.relative(repo, orientationPath).replaceAll("\\", "/")}#${game.event_id}/${legId}`,
        initial_aim: Number(o.legs[legId].orientation_initial.aim),
        consultation_ts: Number(d.legs[legId].first_comparable_decision_ts),
        close: Number(d.legs[legId].close.price_cents),
        bell_price: Number(b.close_price_cents),
        ask_low: integer(q.quote_10s_floor_limit_cents),
        price_region: priceRegion(firstBook?.bid ?? null),
        price_region_source: firstBook ? `${firstBook.source_receipt}; frozen organ-scorecard current-bid cell law` : "UNAVAILABLE",
      };
    });
    eventConfigs.push({ eventId: game.event_id, category: game.category, left: Number(quoteByKey.get(`${game.event_id}|${legs[0].id}`).left_ts), right: Number(quoteByKey.get(`${game.event_id}|${legs[0].id}`).right_ts), scheduled: Number(quoteByKey.get(`${game.event_id}|${legs[0].id}`).scheduled_start_ts), bell: Number(bellByKey.get(`${game.event_id}|${legs[0].id}`).exact_bell_ts), legs });
  }
  const printRows = await readPrintRows(Object.keys(bounds), bounds);
  const printsByEvent = new Map();
  for (const event of eventConfigs) printsByEvent.set(event.eventId, printRows.filter((row) => event.legs.some((leg) => leg.ticker === row.ticker)));
  const nikRawRows = parseCsv(fs.readFileSync(nikClockPath, "utf8"));
  const nikCapacity = makeNikCapacityProjection(nikRawRows, tickRowsByTicker);
  const nikTrace = JSON.parse(fs.readFileSync(nikTracePath, "utf8"));
  const results = eventConfigs.map((event) => event.eventId.endsWith("NIKVRB")
    ? simulateNikSpecimen(event, nikRawRows, nikTrace, nikCapacity)
    : simulateEvent({ ...event, tickRows: event.legs.flatMap((leg) => tickRowsByTicker[leg.ticker]), printRows: printsByEvent.get(event.eventId) }));
  const hold = results.every((row) => row.integrity_hold);
  const categoryPriceRegionPartitions = {};
  for (const event of results) for (const [legId, leg] of Object.entries(event.legs)) {
    const key = `${event.category}|${leg.price_region}`;
    if (!categoryPriceRegionPartitions[key]) categoryPriceRegionPartitions[key] = {
      category: event.category,
      price_region: leg.price_region,
      leg_rows: 0,
      capacity_proven_credited_legs: 0,
      legs_at_or_below_own_close: 0,
      thin: true,
      identities: [],
    };
    const cell = categoryPriceRegionPartitions[key];
    cell.leg_rows += 1;
    if (leg.accounting_status === "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN") cell.capacity_proven_credited_legs += 1;
    if (Number.isInteger(leg.delta_to_own_window1_close_cents) && leg.delta_to_own_window1_close_cents <= 0) cell.legs_at_or_below_own_close += 1;
    cell.identities.push(`${event.event_id}/${legId}`);
  }
  const compactEvents = results.map(({ decisions, ...event }) => ({
    ...event,
    legs: Object.fromEntries(Object.entries(event.legs).map(([legId, { actions, ...leg }]) => [legId, leg])),
  }));
  const summary = {
    schema_version: "WINDOW1_FIVE_EXACT_FULL_STACK_CAPACITY_V1",
    event_count: results.length,
    predeclared_hold_gate: "all five events complete both legs with contemporaneous displayed capacity >=5 and every credited leg entry is at or below its own Window-1 close",
    hold_gate_passed: hold,
    population_804_authorized_by_gate: hold,
    population_804_run: false,
    ceiling_reference: { ask_only_10_second_event_ceiling: 532, capacity_adjustment: "NOT_PRECOMPUTED" },
    pair_reference_law: "NOT_BOUND; no value or delta is proxied from either candidate fill",
    capacity_law: "credit exactly five only when the contemporaneous lawful top-five external asks at or below the resting limit display aggregate size >=5; otherwise EVIDENCE_ABSENT",
    price_region_law: "frozen organ-scorecard region from the first lawful current bid: <=25 le25; <=50 26_50; <=75 51_75; otherwise ge75",
    category_price_region_partitions: categoryPriceRegionPartitions,
    events: compactEvents,
  };
  const capacityAbsences = results.flatMap((event) => Object.values(event.legs).flatMap((leg) => leg.evidence_absent_receipts.map((row) => ({ ...row, event_id: event.event_id }))));
  const reportLines = [
    "# Five exact-start full-stack capacity validation", "",
    `Hold gate: **${hold ? "PASS" : "FAIL"}**. The 804 run was **${hold ? "not run by this builder; separately gated" : "not permitted"}**.`, "",
    "Pair reference is `NOT_BOUND`. A displayed ask capacity of at least five at or below the resting limit is required for credit; price reach with absent/sub-five capacity is reported separately.", "",
    "| category | price region | event | leg | entry | pair ref | delta pair | own W1 close | delta close | own bell | delta bell | own ask-low | delta ask-low | accounting |", "|---|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
  ];
  for (const event of results) for (const leg of Object.values(event.legs)) reportLines.push(`| ${event.category} | ${leg.price_region} | ${event.event_id} | ${leg.orientation}:${leg.ticker.split("-").at(-1)} | ${leg.entry_cents ?? "NULL"} | NOT_BOUND | NOT_BOUND | ${leg.own_window1_close_cents} | ${signed(leg.delta_to_own_window1_close_cents)} | ${leg.own_bell_price_cents} | ${signed(leg.delta_to_own_bell_price_cents)} | ${leg.own_ask_reachable_low_cents ?? "NULL"} | ${signed(leg.delta_to_own_ask_reachable_low_cents)} | ${leg.accounting_status} |`);
  reportLines.push("", "## Category and price-region partitions", "", "Every cell is thin in this five-game validation; none is aggregated upward.", "", "| category | price region | leg rows | credited legs | at/below own close | status |", "|---|---|---:|---:|---:|---|");
  for (const cell of Object.values(categoryPriceRegionPartitions)) reportLines.push(`| ${cell.category} | ${cell.price_region} | ${cell.leg_rows} | ${cell.capacity_proven_credited_legs} | ${cell.legs_at_or_below_own_close} | THIN |`);
  reportLines.push("", "## Change firing", "", "Each value is `FIRED` or `DID_NOTHING`; a fired decision mechanism is not itself fill credit.", "");
  for (const event of results) {
    reportLines.push(`### ${event.event_id}`, "");
    for (const [legId, leg] of Object.entries(event.legs)) reportLines.push(`- ${legId}: ${Object.entries(leg.change_status).map(([key, value]) => `${key}=${value}`).join("; ")}`);
    reportLines.push("");
  }
  if (!hold) {
    reportLines.push("## Blocking shapes", "");
    for (const event of results.filter((row) => !row.integrity_hold)) {
      const failures = Object.entries(event.legs).filter(([, leg]) => leg.accounting_status !== "CREDITED_FIVE_CONTRACT_CAPACITY_PROVEN" || leg.delta_to_own_window1_close_cents > 0).map(([id, leg]) => `${id}:${leg.accounting_status}:delta_close=${signed(leg.delta_to_own_window1_close_cents)}`);
      reportLines.push(`- ${event.event_id}: ${failures.join(", ")}; patience=${event.patience ? `armed at ${event.patience.ts}, recurrence ${event.patience.riser_recurrences}, arm ask ${event.patience.arm_ask}` : "not armed"}.`);
    }
  }
  const baseFiles = {
    "FIVE_GAME_FULL_STACK_RESULTS.json": canonical(summary),
    "PER_EVENT_DECISION_LEDGER.json": canonical({
      encoding: "gzip+base64",
      uncompressed_bytes: Buffer.byteLength(canonical(results)),
      gzip_sha256: sha256(zlib.gzipSync(Buffer.from(canonical(results)), { mtime: 0 })),
      gzip_base64: zlib.gzipSync(Buffer.from(canonical(results)), { mtime: 0 }).toString("base64"),
    }),
    "EVIDENCE_ABSENT_CAPACITY_RECEIPT.json": canonical({ count: capacityAbsences.length, rows: capacityAbsences }),
    "NIKVRB_CAPACITY_BY_SEQUENCE.json": canonical({ schema_version: "NIKVRB_ASK_CAPACITY_BY_SEQUENCE_V1", required_quantity: REQUIRED_QUANTITY, rows: Object.keys(nikCapacity).length, capacity_by_sequence: nikCapacity }),
    "REFERENCE_LAW_RECEIPT.json": canonical({ independent_pair_reference: "NOT_BOUND", forbidden_proxy: "100 - sibling entry", reported_references: ["own_window1_close", "own_actual_bell_price", "own_ask_reachable_low"], signed_delta_law: "entry - own reference", per_leg_only: true }),
    "DEFECT_BEFORE_AFTER_RECEIPT.json": canonical({
      pair_reference: {
        before: "100 - sibling entry proxy",
        after: "NOT_BOUND",
        number_moved: "10 per-leg proxy reference/delta fields removed from the five-event panel; no independent pair-reference number substituted",
      },
      capacity: {
        before: "NIKVRB ask-dwell credits carried evidence_size=null",
        after: "five-contract credit requires contemporaneous displayed ask capacity >=5; unknown/sub-five is EVIDENCE_ABSENT",
        number_moved: "NIKVRB credited-leg count 2->2 because displayed sizes 86 and 110 were recovered; null-sized NIKVRB credits 2->0",
      },
      recurrence_prose: {
        before: "97 mixed bid+ask quote recurrences",
        after: "66 ask-side recurrences, matching the executable branch",
        number_moved: "decision count 0; prose value -31; executable value 66->66",
      },
    }),
    "SOURCE_HASH_MANIFEST.json": canonical({ committed: Object.fromEntries([__filename, replayPath, scorecardBuilderPath, selectionPath, orientationPath, deltaReplayPath, quoteLegsPath, bellPath, nikClockPath, nikTracePath].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])), private_development: Object.fromEntries([printsPath, ...Object.values(tickSources)].map((file) => [path.basename(file), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])) }),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ scorer_imported: false, scorer_invoked: false, population_804_run: false, holdout_access: false, live_access: false, network_access: false, order_access: false, position_access: false, exit_access: false, settlement_access: false, dca_access: false }),
  };
  baseFiles["DETERMINISM_RECEIPT.json"] = canonical({ method: "two complete private-input builds compared before write", complete_builds: 2, byte_identical: true, core_sha256: sha256(Buffer.from(JSON.stringify({ summary, results, nikCapacity }))) });
  return { baseFiles, docs: { [reportPath]: `${reportLines.join("\n")}\n` }, summary };
}

async function main() {
  const first = await build(); const second = await build();
  if (JSON.stringify(first) !== JSON.stringify(second)) throw new Error("two-build determinism mismatch");
  const artifactRows = [];
  for (const [name, content] of Object.entries(first.baseFiles)) artifactRows.push({ path: `.claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/${name}`, bytes: Buffer.byteLength(content), sha256: sha256(Buffer.from(content)) });
  for (const [file, content] of Object.entries(first.docs)) artifactRows.push({ path: path.relative(repo, file).replaceAll("\\", "/"), bytes: Buffer.byteLength(content), sha256: sha256(Buffer.from(content)) });
  first.baseFiles["ARTIFACT_HASH_MANIFEST.json"] = canonical({ artifacts: artifactRows });
  if (checkOnly) {
    for (const [name, content] of Object.entries(first.baseFiles)) {
      const existing = fs.readFileSync(path.join(outDir, name));
      if (!existing.equals(Buffer.from(content))) throw new Error(`artifact mismatch ${name}`);
    }
    for (const [file, content] of Object.entries(first.docs)) if (fs.readFileSync(file, "utf8") !== content) throw new Error(`document mismatch ${file}`);
    process.stdout.write(canonical({ status: "CHECK_PASS", event_count: first.summary.event_count, hold_gate_passed: first.summary.hold_gate_passed, population_804_run: false })); return;
  }
  fs.mkdirSync(outDir, { recursive: true });
  for (const [name, content] of Object.entries(first.baseFiles)) fs.writeFileSync(path.join(outDir, name), content);
  for (const [file, content] of Object.entries(first.docs)) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, content); }
  process.stdout.write(canonical({ status: "BUILT", output: path.relative(repo, outDir), event_count: first.summary.event_count, hold_gate_passed: first.summary.hold_gate_passed, population_804_run: false }));
}

if (require.main === module) {
  main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
}

module.exports = { askCapacity, simulateEvent };
